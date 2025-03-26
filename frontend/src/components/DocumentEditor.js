import React, { useState, useEffect } from 'react';
import { EditorState, convertToRaw, ContentState } from 'draft-js';
import { Editor } from 'react-draft-wysiwyg';
import draftToHtml from 'draftjs-to-html';
import htmlToDraft from 'html-to-draftjs';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
import Button from './Button';
import './DocumentEditor.css';
import { useAppContext } from '../context/AppContext';
import { saveAs } from 'file-saver';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

const DocumentEditor = ({ initialDocument, onSave, onClose, templates = [] }) => {
  const [docData, setDocData] = useState(initialDocument || {
    title: 'Nouveau document',
    content: '',
    type: 'document'
  });
  
  const [editorState, setEditorState] = useState(EditorState.createEmpty());
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const { updateDocument, createDocument } = useAppContext();
  const [isSaving, setIsSaving] = useState(false);
  const [showTemplateSelector, setShowTemplateSelector] = useState(!initialDocument);

  // Initialiser l'éditeur avec le contenu du document si disponible
  useEffect(() => {
    if (docData.content) {
      const blocksFromHtml = htmlToDraft(docData.content);
      if (blocksFromHtml) {
        const { contentBlocks, entityMap } = blocksFromHtml;
        const contentState = ContentState.createFromBlockArray(contentBlocks, entityMap);
        setEditorState(EditorState.createWithContent(contentState));
      }
    }
  }, [docData.content]);

  const handleEditorChange = (state) => {
    setEditorState(state);
    const htmlContent = draftToHtml(convertToRaw(state.getCurrentContent()));
    setDocData(prev => ({ ...prev, content: htmlContent }));
  };

  const handleTitleChange = (e) => {
    setDocData(prev => ({ ...prev, title: e.target.value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const htmlContent = draftToHtml(convertToRaw(editorState.getCurrentContent()));
      const updatedDocument = {
        ...docData,
        content: htmlContent
      };
      
      let result;
      if (initialDocument && initialDocument.id) {
        // Mettre à jour un document existant
        result = await updateDocument(initialDocument.id, updatedDocument);
      } else {
        // Créer un nouveau document
        result = await createDocument(updatedDocument);
      }
      
      if (onSave) {
        onSave(result);
      }
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du document:', error);
      alert(`Erreur: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleApplyTemplate = (template) => {
    if (!template) return;
    
    setSelectedTemplate(template);
    
    // Utiliser le contenu du modèle
    const blocksFromHtml = htmlToDraft(template.content || '');
    if (blocksFromHtml) {
      const { contentBlocks, entityMap } = blocksFromHtml;
      const contentState = ContentState.createFromBlockArray(contentBlocks, entityMap);
      setEditorState(EditorState.createWithContent(contentState));
      setDocData(prev => ({ 
        ...prev, 
        content: template.content,
        type: template.type || prev.type,
        templateId: template.id
      }));
    }
    
    setShowTemplateSelector(false);
  };

  const handleExportPDF = async () => {
    try {
      const element = window.document.getElementById('document-editor-content');
      if (!element) {
        console.error("Élément 'document-editor-content' non trouvé");
        alert("Impossible d'exporter en PDF: élément non trouvé");
        return;
      }
      
      // Options pour une meilleure qualité
      const options = {
        scale: 2, // Échelle x2 pour une meilleure résolution
        useCORS: true, // Permet de charger les images de sources externes
        logging: false,
        backgroundColor: '#FFFFFF', // Fond blanc
        onclone: (clonedDoc) => {
          // Sélectionner uniquement le contenu de l'éditeur dans le clone
          const editorElement = clonedDoc.getElementById('document-editor-content').querySelector('.rdw-editor-main');
          if (editorElement) {
            // Ajuster le style pour l'export
            editorElement.style.padding = '20px';
            editorElement.style.backgroundColor = '#FFFFFF';
            editorElement.style.minHeight = 'auto';
          }
          return clonedDoc;
        }
      };
      
      // Cibler spécifiquement la partie éditable (pas la toolbar)
      const editorContent = element.querySelector('.rdw-editor-main');
      if (!editorContent) {
        console.error("Contenu de l'éditeur non trouvé");
        alert("Impossible d'exporter en PDF: contenu non trouvé");
        return;
      }
      
      const canvas = await html2canvas(editorContent, options);
      const imgData = canvas.toDataURL('image/png');
      
      // Configurer le PDF avec des marges
      const pdf = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4',
        compress: true
      });
      
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      
      // Calculer les dimensions en conservant le ratio
      const imgWidth = pageWidth - 20; // 10mm de marge de chaque côté
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      // Ajouter le titre du document
      pdf.setFontSize(16);
      pdf.text(docData.title, 10, 10);
      
      // Ajouter l'image en dessous du titre avec marges
      pdf.addImage(imgData, 'PNG', 10, 20, imgWidth, imgHeight);
      
      // Si le contenu dépasse la page, ajouter d'autres pages
      if (imgHeight > pageHeight - 30) { // 30mm pour le titre et l'espace
        let heightLeft = imgHeight;
        let position = 0;
        
        // Retirer le titre pour avoir les dimensions correctes
        heightLeft -= (pageHeight - 20);
        position = -(pageHeight - 20);
        
        while (heightLeft > 0) {
          pdf.addPage();
          position += pageHeight;
          pdf.addImage(imgData, 'PNG', 10, 10 - position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
        }
      }
      
      pdf.save(`${docData.title || 'document'}.pdf`);
    } catch (error) {
      console.error('Erreur lors de l\'export PDF:', error);
      alert('Impossible d\'exporter en PDF. Veuillez réessayer.');
    }
  };

  const handleExportWord = () => {
    try {
      // Capture uniquement le contenu de l'éditeur pour l'export
      const editorContent = window.document.getElementById('document-editor-content').querySelector('.rdw-editor-main');
      if (!editorContent) {
        console.error("Contenu de l'éditeur non trouvé");
        alert("Impossible d'exporter en Word: contenu non trouvé");
        return;
      }
      
      // Styles améliorés pour une meilleure compatibilité Word
      const styles = `
        @page {
          size: A4;
          margin: 2.54cm;
        }
        body { 
          font-family: 'Calibri', Arial, sans-serif; 
          font-size: 11pt;
          line-height: 1.15;
          color: #000000;
        }
        h1 { 
          font-size: 16pt;
          font-weight: bold;
          color: #000000;
          text-align: center;
          margin-bottom: 12pt;
        }
        h2 {
          font-size: 14pt;
          font-weight: bold;
          margin-top: 12pt;
          margin-bottom: 3pt;
        }
        h3 {
          font-size: 12pt;
          font-weight: bold;
          margin-top: 10pt;
          margin-bottom: 3pt;
        }
        p { 
          margin: 0;
          margin-bottom: 8pt;
        }
        a {
          color: #0563C1;
          text-decoration: underline;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 10pt;
        }
        td, th {
          border: 1px solid #000000;
          padding: 5pt;
        }
        ul, ol {
          margin-top: 0;
          margin-bottom: 8pt;
        }
        img {
          max-width: 100%;
        }
      `;
      
      // Créer le contenu HTML pour Word avec le contenu de l'éditeur
      const htmlContent = `
        <!DOCTYPE html>
        <html xmlns:o="urn:schemas-microsoft-com:office:office" 
              xmlns:w="urn:schemas-microsoft-com:office:word"
              xmlns="http://www.w3.org/TR/REC-html40">
          <head>
            <meta charset="utf-8">
            <meta name="ProgId" content="Word.Document">
            <meta name="Generator" content="Microsoft Word 15">
            <meta name="Originator" content="Microsoft Word 15">
            <title>${docData.title}</title>
            <style>${styles}</style>
            <!--[if gte mso 9]>
            <xml>
              <w:WordDocument>
                <w:View>Print</w:View>
                <w:Zoom>100</w:Zoom>
                <w:DoNotOptimizeForBrowser/>
              </w:WordDocument>
            </xml>
            <![endif]-->
          </head>
          <body>
            <h1>${docData.title}</h1>
            ${docData.content}
          </body>
        </html>
      `;
      
      // Créer un blob avec le contenu HTML formaté pour Word
      const blob = new Blob([htmlContent], { 
        type: 'application/vnd.ms-word;charset=utf-8' 
      });
      
      // Sauvegarder le fichier .doc
      saveAs(blob, `${docData.title || 'document'}.doc`);
    } catch (error) {
      console.error('Erreur lors de l\'export Word:', error);
      alert('Impossible d\'exporter en Word. Veuillez réessayer.');
    }
  };

  // Ajouter cette fonction pour débloquer le chargement des images
  const customImageUploadCallback = (file) => {
    return new Promise((resolve, reject) => {
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          resolve({ data: { link: e.target.result } });
        };
        reader.onerror = (error) => {
          reject(error);
        };
        reader.readAsDataURL(file);
      }
    });
  };

  return (
    <div className="document-editor">
      {showTemplateSelector && templates.length > 0 ? (
        <div className="template-selector">
          <h2>Choisir un modèle</h2>
          <div className="templates-grid">
            <div 
              className="template-card empty" 
              onClick={() => setShowTemplateSelector(false)}
            >
              <i className="bx bx-file-blank"></i>
              <span>Document vide</span>
            </div>
            
            {templates.map(template => (
              <div 
                key={template.id} 
                className="template-card" 
                onClick={() => handleApplyTemplate(template)}
              >
                <i className={`bx ${
                  template.type === 'document' ? 'bx-file-doc' : 
                  template.type === 'presentation' ? 'bx-slideshow' : 
                  'bx-spreadsheet'
                }`}></i>
                <span>{template.title || template.name}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          <div className="document-editor-header">
            <input 
              type="text" 
              className="document-title-input" 
              value={docData.title} 
              onChange={handleTitleChange} 
              placeholder="Titre du document" 
            />
            <div className="document-editor-actions">
              <Button 
                variant="transparent" 
                icon="bx-template" 
                onClick={() => setShowTemplateSelector(true)}
              >
                Modèles
              </Button>
              <Button 
                variant="transparent" 
                icon="bx-export" 
                onClick={handleExportWord}
              >
                Word
              </Button>
              <Button 
                variant="transparent" 
                icon="bx-file-pdf" 
                onClick={handleExportPDF}
              >
                PDF
              </Button>
              <Button 
                variant="primary" 
                icon="bx-save" 
                onClick={handleSave}
                disabled={isSaving}
              >
                {isSaving ? 'Enregistrement...' : 'Enregistrer'}
              </Button>
              <Button 
                variant="text" 
                icon="bx-x" 
                onClick={onClose}
              >
                Fermer
              </Button>
            </div>
          </div>
          
          <div className="document-editor-content" id="document-editor-content">
            <Editor
              editorState={editorState}
              onEditorStateChange={handleEditorChange}
              wrapperClassName="document-editor-wrapper"
              editorClassName="document-editor-main"
              toolbarClassName="document-editor-toolbar"
              toolbar={{
                options: ['inline', 'blockType', 'fontSize', 'fontFamily', 'list', 'textAlign', 'colorPicker', 'link', 'image', 'history'],
                inline: { 
                  inDropdown: false,
                  options: ['bold', 'italic', 'underline', 'strikethrough', 'monospace', 'superscript', 'subscript']
                },
                blockType: {
                  inDropdown: true,
                  options: ['Normal', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Blockquote', 'Code']
                },
                fontSize: {
                  options: [8, 9, 10, 11, 12, 14, 16, 18, 24, 30, 36, 48]
                },
                fontFamily: {
                  options: ['Arial', 'Georgia', 'Impact', 'Tahoma', 'Times New Roman', 'Verdana']
                },
                list: { 
                  inDropdown: true,
                  options: ['unordered', 'ordered', 'indent', 'outdent']
                },
                textAlign: { 
                  inDropdown: true,
                  options: ['left', 'center', 'right', 'justify']
                },
                colorPicker: {
                  colors: ['rgb(97,189,109)', 'rgb(26,188,156)', 'rgb(84,172,210)', 'rgb(44,130,201)',
                    'rgb(147,101,184)', 'rgb(71,85,119)', 'rgb(204,204,204)', 'rgb(65,168,95)', 'rgb(0,168,133)',
                    'rgb(61,142,185)', 'rgb(41,105,176)', 'rgb(85,57,130)', 'rgb(40,50,78)', 'rgb(0,0,0)',
                    'rgb(247,218,100)', 'rgb(251,160,38)', 'rgb(235,107,86)', 'rgb(226,80,65)', 'rgb(163,143,132)',
                    'rgb(239,239,239)', 'rgb(255,255,255)', 'rgb(250,197,28)', 'rgb(243,121,52)', 'rgb(209,72,65)',
                    'rgb(184,49,47)', 'rgb(124,112,107)', 'rgb(209,213,216)']
                },
                link: { 
                  inDropdown: false,
                  showOpenOptionOnHover: true,
                  defaultTargetOption: '_self',
                  options: ['link', 'unlink']
                },
                image: {
                  urlEnabled: true,
                  uploadEnabled: true,
                  alignmentEnabled: true,
                  uploadCallback: customImageUploadCallback,
                  previewImage: true,
                  inputAccept: 'image/gif,image/jpeg,image/jpg,image/png,image/svg',
                  alt: { present: true, mandatory: false },
                  defaultSize: {
                    height: 'auto',
                    width: 'auto'
                  }
                },
                history: { 
                  inDropdown: false,
                  options: ['undo', 'redo']
                }
              }}
              localization={{
                locale: 'fr',
                translations: {
                  'components.controls.blocktype.normal': 'Normal',
                  'components.controls.blocktype.h1': 'Titre 1',
                  'components.controls.blocktype.h2': 'Titre 2',
                  'components.controls.blocktype.h3': 'Titre 3',
                  'components.controls.blocktype.h4': 'Titre 4',
                  'components.controls.blocktype.h5': 'Titre 5',
                  'components.controls.blocktype.h6': 'Titre 6',
                  'components.controls.blocktype.blockquote': 'Citation',
                  'components.controls.blocktype.code': 'Code',
                  'components.controls.blocktype.blocktype': 'Style',
                  'components.controls.fontfamily.fontfamily': 'Police',
                  'components.controls.fontsize.fontsize': 'Taille',
                  'components.controls.image.image': 'Image',
                  'components.controls.image.fileUpload': 'Téléverser',
                  'components.controls.image.byURL': 'URL',
                  'components.controls.image.dropFileText': 'Déposer un fichier ou cliquer pour téléverser',
                  'components.controls.inline.bold': 'Gras',
                  'components.controls.inline.italic': 'Italique',
                  'components.controls.inline.underline': 'Souligné',
                  'components.controls.inline.strikethrough': 'Barré',
                  'components.controls.link.linkTitle': 'Titre du lien',
                  'components.controls.link.linkTarget': 'Cible du lien',
                  'components.controls.link.linkTargetOption': 'Ouvrir dans une nouvelle fenêtre',
                  'components.controls.link.link': 'Lien',
                  'components.controls.link.unlink': 'Supprimer le lien',
                  'components.controls.list.list': 'Liste',
                  'components.controls.list.unordered': 'Liste à puces',
                  'components.controls.list.ordered': 'Liste numérotée',
                  'components.controls.list.indent': 'Augmenter le retrait',
                  'components.controls.list.outdent': 'Diminuer le retrait',
                  'components.controls.textalign.textalign': 'Alignement du texte',
                  'components.controls.textalign.left': 'Gauche',
                  'components.controls.textalign.center': 'Centre',
                  'components.controls.textalign.right': 'Droite',
                  'components.controls.textalign.justify': 'Justifié',
                  'components.controls.colorpicker.colorpicker': 'Couleur du texte'
                }
              }}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default DocumentEditor; 
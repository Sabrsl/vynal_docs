import React, { useCallback, useState, useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Highlight from '@tiptap/extension-highlight';
import TextAlign from '@tiptap/extension-text-align';
import TextStyle from '@tiptap/extension-text-style';
import FontFamily from '@tiptap/extension-font-family';
import FontSize from '@tiptap/extension-font-size';
import Underline from '@tiptap/extension-underline';
import Strike from '@tiptap/extension-strike';
import CodeBlock from '@tiptap/extension-code-block';
import Code from '@tiptap/extension-code';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import { saveAs } from 'file-saver';
import html2pdf from 'html2pdf.js/dist/html2pdf.bundle.min.js';
import './TiptapEditor.css';
import Color from '@tiptap/extension-color';

const MenuBar = ({ editor, onExportPDF, onExportDOCX }) => {
  if (!editor) {
    return null;
  }

  const addImage = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async () => {
      const file = input.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const url = e.target.result;
          editor.chain().focus().insertContent({
            type: 'image',
            attrs: { 
              src: url,
              width: '100%',
              height: 'auto',
              style: 'max-width: 100%; height: auto;'
            }
          }).run();
        };
        reader.readAsDataURL(file);
      }
    };
    input.click();
  };

  const setFontSize = (size) => {
    editor.chain().focus().setFontSize(size).run();
  };

  const setFontFamily = (font) => {
    editor.chain().focus().setFontFamily(font).run();
  };

  return (
    <div className="tiptap-menu-bar">
      <div className="tiptap-menu-group">
        <button
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'is-active' : ''}
          title="Gras"
        >
          <i className="bx bx-bold"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'is-active' : ''}
          title="Italique"
        >
          <i className="bx bx-italic"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={editor.isActive('strike') ? 'is-active' : ''}
          title="Barré"
        >
          <i className="bx bx-strikethrough"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          className={editor.isActive('underline') ? 'is-active' : ''}
          title="Souligné"
        >
          <i className="bx bx-underline"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleHighlight().run()}
          className={editor.isActive('highlight') ? 'is-active' : ''}
          title="Surligner"
        >
          <i className="bx bx-highlight"></i>
        </button>
      </div>

      <div className="tiptap-menu-group">
        <select
          onChange={(e) => setFontFamily(e.target.value)}
          className="tiptap-select"
          title="Police"
        >
          <option value="Arial">Arial</option>
          <option value="Times New Roman">Times New Roman</option>
          <option value="Courier New">Courier New</option>
          <option value="Georgia">Georgia</option>
          <option value="Verdana">Verdana</option>
        </select>
        <select
          onChange={(e) => setFontSize(e.target.value)}
          className="tiptap-select"
          title="Taille"
        >
          <option value="8">8</option>
          <option value="9">9</option>
          <option value="10">10</option>
          <option value="11">11</option>
          <option value="12">12</option>
          <option value="14">14</option>
          <option value="16">16</option>
          <option value="18">18</option>
          <option value="20">20</option>
          <option value="24">24</option>
          <option value="30">30</option>
          <option value="36">36</option>
          <option value="48">48</option>
        </select>
      </div>

      <div className="tiptap-menu-group">
        <button
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={editor.isActive('heading', { level: 1 }) ? 'is-active' : ''}
          title="Titre 1"
        >
          <i className="bx bx-text"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={editor.isActive('heading', { level: 2 }) ? 'is-active' : ''}
          title="Titre 2"
        >
          <i className="bx bx-text"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive('bulletList') ? 'is-active' : ''}
          title="Liste à puces"
        >
          <i className="bx bx-list-ul"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive('orderedList') ? 'is-active' : ''}
          title="Liste numérotée"
        >
          <i className="bx bx-list-ol"></i>
        </button>
      </div>

      <div className="tiptap-menu-group">
        <button
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          className={editor.isActive('codeBlock') ? 'is-active' : ''}
          title="Bloc de code"
        >
          <i className="bx bx-code-block"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          className={editor.isActive('blockquote') ? 'is-active' : ''}
          title="Citation"
        >
          <i className="bx bx-quote-left"></i>
        </button>
        <button
          onClick={addImage}
          title="Insérer une image"
        >
          <i className="bx bx-image"></i>
        </button>
      </div>

      <div className="tiptap-menu-group">
        <button
          onClick={() => editor.chain().focus().setTextAlign('left').run()}
          className={editor.isActive({ textAlign: 'left' }) ? 'is-active' : ''}
          title="Aligné à gauche"
        >
          <i className="bx bx-align-left"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().setTextAlign('center').run()}
          className={editor.isActive({ textAlign: 'center' }) ? 'is-active' : ''}
          title="Centré"
        >
          <i className="bx bx-align-middle"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().setTextAlign('right').run()}
          className={editor.isActive({ textAlign: 'right' }) ? 'is-active' : ''}
          title="Aligné à droite"
        >
          <i className="bx bx-align-right"></i>
        </button>
      </div>

      <div className="tiptap-menu-group">
        <button
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          title="Annuler"
        >
          <i className="bx bx-undo"></i>
        </button>
        <button
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          title="Rétablir"
        >
          <i className="bx bx-redo"></i>
        </button>
      </div>

      <div className="tiptap-menu-group">
        <button
          onClick={onExportPDF}
          title="Exporter en PDF"
        >
          <i className="bx bx-file"></i>
        </button>
        <button
          onClick={onExportDOCX}
          title="Exporter en DOCX"
        >
          <i className="bx bx-file"></i>
        </button>
      </div>
    </div>
  );
};

const TiptapEditor = ({ content, onChange }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableCell,
      TableHeader,
      Image.configure({
        inline: true,
        allowBase64: true,
        HTMLAttributes: {
          class: 'resizable-image',
        },
        handleDOMEvents: {
          mousedown: (view, event) => {
            if (event.target.tagName === 'IMG') {
              const img = event.target;
              const rect = img.getBoundingClientRect();
              const isResizeHandle = event.target.closest('.resize-handle');
              
              // Vérifier si le clic est sur une poignée de redimensionnement
              if (isResizeHandle) {
                const startX = event.pageX;
                const startY = event.pageY;
                const startWidth = img.width;
                const startHeight = img.height;
                const aspectRatio = startWidth / startHeight;

                // Créer l'élément d'information de taille
                const resizeInfo = document.createElement('div');
                resizeInfo.className = 'resize-info';
                img.parentNode.appendChild(resizeInfo);

                // Ajouter la classe de redimensionnement
                img.classList.add('resizing');

                const onMouseMove = (e) => {
                  const dx = e.pageX - startX;
                  const dy = e.pageY - startY;

                  // Déterminer la direction du redimensionnement
                  const handle = isResizeHandle.className.split(' ')[1];
                  let newWidth, newHeight;

                  switch (handle) {
                    case 'bottom-right':
                      newWidth = Math.max(50, startWidth + dx);
                      newHeight = newWidth / aspectRatio;
                      break;
                    case 'bottom-left':
                      newWidth = Math.max(50, startWidth - dx);
                      newHeight = newWidth / aspectRatio;
                      break;
                    case 'top-right':
                      newWidth = Math.max(50, startWidth + dx);
                      newHeight = newWidth / aspectRatio;
                      break;
                    case 'top-left':
                      newWidth = Math.max(50, startWidth - dx);
                      newHeight = newWidth / aspectRatio;
                      break;
                  }

                  // Mettre à jour la taille de l'image
                  img.style.width = `${newWidth}px`;
                  img.style.height = `${newHeight}px`;

                  // Mettre à jour l'information de taille
                  resizeInfo.textContent = `${Math.round(newWidth)} × ${Math.round(newHeight)}`;
                };

                const onMouseUp = () => {
                  document.removeEventListener('mousemove', onMouseMove);
                  document.removeEventListener('mouseup', onMouseUp);
                  img.classList.remove('resizing');
                  resizeInfo.remove();
                };

                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
                return true;
              }
            }
            return false;
          },
        },
      }),
      Link.configure({
        openOnClick: false,
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      FontFamily.configure({
        types: ['textStyle'],
      }),
      TextStyle.configure({
        types: ['textStyle'],
      }),
      FontSize.configure({
        types: ['textStyle'],
      }),
      Color.configure({
        types: ['textStyle'],
      }),
      Underline,
      Highlight,
    ],
    content: content || '<p></p>',
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
    editorProps: {
      handlePaste: (view, event) => {
        // Empêcher le comportement par défaut du collage
        event.preventDefault();
        
        // Récupérer le texte collé
        const text = event.clipboardData.getData('text/plain');
        
        // Insérer le texte à la position actuelle
        view.dispatch(view.state.tr.insertText(text));
        
        return true;
      }
    }
  });

  const handleExportPDF = async () => {
    if (!editor) return;

    try {
      setLoading(true);
      setMessage('Génération du PDF en cours...');

      // Créer un conteneur temporaire pour l'export
      const container = document.createElement('div');
      container.style.width = '794px'; // Largeur A4
      container.style.margin = '0 auto';
      container.style.padding = '40px';
      container.style.backgroundColor = 'white';
      container.style.color = '#000000';
      container.style.fontFamily = 'Arial, sans-serif';
      container.style.fontSize = '12pt';
      container.style.lineHeight = '1.5';
      container.style.letterSpacing = '0.01em';
      container.style.textRendering = 'optimizeLegibility';
      container.style.webkitFontSmoothing = 'antialiased';
      container.style.mozOsxFontSmoothing = 'grayscale';

      // Copier le contenu de l'éditeur
      const content = editor.view.dom.cloneNode(true);
      container.appendChild(content);

      // Appliquer des styles spécifiques pour l'export
      const style = document.createElement('style');
      style.textContent = `
        p, h1, h2, h3, ul, ol, blockquote {
          color: #000000 !important;
          text-shadow: none !important;
          -webkit-text-fill-color: #000000 !important;
          page-break-inside: avoid;
          break-inside: avoid;
          max-width: 100%;
          margin-right: 0;
        }
        table {
          border-collapse: collapse;
          width: 100%;
          margin: 1em 0;
          page-break-inside: avoid;
          break-inside: avoid;
        }
        table td, table th {
          border: 1px solid #000000;
          padding: 0.5em;
          color: #000000 !important;
          background-color: white !important;
        }
        img {
          max-width: 100%;
          height: auto;
          display: block;
          margin: 1em auto;
          page-break-inside: avoid;
          break-inside: avoid;
        }
        a {
          color: #0000EE !important;
          text-decoration: underline !important;
        }
        [style*="font-size: 8"] { font-size: 8px !important; }
        [style*="font-size: 9"] { font-size: 9px !important; }
        [style*="font-size: 10"] { font-size: 10px !important; }
        [style*="font-size: 11"] { font-size: 11px !important; }
        [style*="font-size: 12"] { font-size: 12px !important; }
        [style*="font-size: 14"] { font-size: 14px !important; }
        [style*="font-size: 16"] { font-size: 16px !important; }
        [style*="font-size: 18"] { font-size: 18px !important; }
        [style*="font-size: 20"] { font-size: 20px !important; }
        [style*="font-size: 24"] { font-size: 24px !important; }
        [style*="font-size: 30"] { font-size: 30px !important; }
        [style*="font-size: 36"] { font-size: 36px !important; }
        [style*="font-size: 48"] { font-size: 48px !important; }
        .ProseMirror {
          border: none !important;
          box-shadow: none !important;
          margin-bottom: 0 !important;
          padding: 0 !important;
        }
      `;
      container.appendChild(style);

      // Options pour html2pdf
      const opt = {
        margin: [10, 10, 10, 10], // [top, right, bottom, left] en mm - marges plus petites
        filename: 'document.pdf',
        image: { type: 'jpeg', quality: 1 },
        html2canvas: { 
          scale: 2,
          useCORS: true,
          logging: false,
          letterRendering: true,
          allowTaint: true,
          backgroundColor: '#ffffff',
          width: 794 // Largeur A4 en pixels
        },
        jsPDF: { 
          unit: 'mm', 
          format: 'a4', 
          orientation: 'portrait',
          compress: true
        },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
      };

      // Générer le PDF
      await html2pdf().set(opt).from(container).save();
      setMessage('PDF généré avec succès !');
      
      // Faire disparaître la notification après 3 secondes
      setTimeout(() => {
        setMessage('');
      }, 3000);
    } catch (error) {
      console.error('Erreur lors de la génération du PDF:', error);
      setMessage('Erreur lors de la génération du PDF. Veuillez réessayer.');
      // Faire disparaître la notification d'erreur après 3 secondes
      setTimeout(() => {
        setMessage('');
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleExportDOCX = async () => {
    if (!editor) return;

    try {
      // Récupérer le contenu HTML de l'éditeur
      const content = editor.getHTML();
      
      // Appeler l'API du backend pour générer le DOCX
      const response = await fetch('/api/documents/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          format: 'docx'
        }),
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la génération du DOCX');
      }

      // Récupérer le blob du DOCX
      const blob = await response.blob();
      
      // Télécharger le fichier
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'document.docx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (error) {
      console.error('Erreur lors de l\'export DOCX:', error);
      alert('Une erreur est survenue lors de la génération du DOCX');
    }
  };

  return (
    <div className="tiptap-editor">
      <MenuBar 
        editor={editor} 
        onExportPDF={handleExportPDF}
        onExportDOCX={handleExportDOCX}
      />
      <EditorContent editor={editor} className="tiptap-content" />
      {message && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          padding: '10px 20px',
          backgroundColor: loading ? '#fef3c7' : '#dcfce7',
          color: loading ? '#92400e' : '#166534',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          zIndex: 1000
        }}>
          {message}
        </div>
      )}
    </div>
  );
};

export default TiptapEditor; 
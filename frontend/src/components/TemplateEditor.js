import React, { useState, useEffect, useCallback } from 'react';
import TiptapEditor from './TiptapEditor';
import Button from './Button';
import Input from './Input';
import Dropdown from './Dropdown';
import './TemplateEditor.css';

const VARIABLE_FORMATS = [
  { id: 'doublebraces', label: 'Accolades doubles', format: '{{variable}}' },
  { id: 'doublebrackets', label: 'Crochets doubles', format: '[[variable]]' },
  { id: 'prefix', label: 'Préfixe XXXX_', format: 'XXXX_VARIABLE' },
  { id: 'dollarbraces', label: 'Style JavaScript', format: '${variable}' }
];

const VARIABLE_CATEGORIES = [
  { id: 'contact', label: 'Informations de contact', variables: [
    { id: 'nom', label: 'Nom' },
    { id: 'prenom', label: 'Prénom' },
    { id: 'email', label: 'Email' },
    { id: 'telephone', label: 'Téléphone' },
    { id: 'adresse', label: 'Adresse' },
    { id: 'code_postal', label: 'Code postal' },
    { id: 'ville', label: 'Ville' },
    { id: 'pays', label: 'Pays' }
  ]},
  { id: 'company', label: 'Informations d\'entreprise', variables: [
    { id: 'entreprise', label: 'Nom de l\'entreprise' },
    { id: 'siret', label: 'Numéro SIRET' },
    { id: 'tva', label: 'Numéro TVA' },
    { id: 'forme_juridique', label: 'Forme juridique' },
    { id: 'adresse_entreprise', label: 'Adresse de l\'entreprise' }
  ]},
  { id: 'date', label: 'Dates', variables: [
    { id: 'date', label: 'Date actuelle' },
    { id: 'date_creation', label: 'Date de création' },
    { id: 'date_signature', label: 'Date de signature' },
    { id: 'date_echeance', label: 'Date d\'échéance' }
  ]},
  { id: 'custom', label: 'Variables personnalisées', variables: [] }
];

const TemplateEditor = ({ template, onSave, onClose }) => {
  const [title, setTitle] = useState(template?.title || '');
  const [description, setDescription] = useState(template?.description || '');
  const [content, setContent] = useState(template?.content || '');
  const [category, setCategory] = useState(template?.category || 'contract');
  const [selectedFormat, setSelectedFormat] = useState('doublebraces');
  const [customVariable, setCustomVariable] = useState('');
  const [customVariables, setCustomVariables] = useState(template?.customVariables || []);
  const [selectedCategory, setSelectedCategory] = useState('contact');
  const [selectedVariable, setSelectedVariable] = useState('');
  const [showVariablePanel, setShowVariablePanel] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [clientPreview, setClientPreview] = useState(null);
  const [variablePreview, setVariablePreview] = useState({});
  
  // Détecter les variables dans le contenu
  const detectVariables = useCallback((content) => {
    const variables = [];
    const formats = {
      doublebraces: /\{\{([^{}]+)\}\}/g,
      doublebrackets: /\[\[([^\[\]]+)\]\]/g,
      prefix: /XXXX_([A-Za-z0-9_]+)/g,
      dollarbraces: /\$\{([^{}]+)\}/g
    };
    
    if (!content) return [];
    
    // Extraire toutes les variables selon les différents formats
    Object.keys(formats).forEach(formatKey => {
      const regex = formats[formatKey];
      let match;
      while ((match = regex.exec(content)) !== null) {
        variables.push({
          name: match[1].trim(),
          format: formatKey,
          full: match[0]
        });
      }
    });
    
    return variables;
  }, []);
  
  // Mettre à jour les variables personnalisées détectées
  useEffect(() => {
    const detectedVars = detectVariables(content);
    const existingVarNames = VARIABLE_CATEGORIES.flatMap(cat => 
      cat.variables.map(v => v.id)
    );
    
    // Trouver les variables personnalisées (non standard)
    const customVars = detectedVars
      .filter(v => !existingVarNames.includes(v.name))
      .map(v => v.name);
    
    // Mettre à jour les variables personnalisées
    setCustomVariables([...new Set([...customVariables, ...customVars])]);
  }, [content, detectVariables]);
  
  // Formater une variable selon le format sélectionné
  const formatVariable = (variable) => {
    const format = VARIABLE_FORMATS.find(f => f.id === selectedFormat);
    if (!format) return variable;
    
    return format.format.replace('variable', variable);
  };
  
  // Insérer une variable dans l'éditeur
  const insertVariable = (variable) => {
    if (!variable) return;
    
    const formattedVariable = formatVariable(variable);
    
    // Insérer dans l'éditeur (à implémenter avec TipTap)
    const editor = document.querySelector('.tiptap-editor .ProseMirror');
    if (editor) {
      // Sauvegarder la sélection actuelle
      const selection = window.getSelection();
      const range = selection.getRangeAt(0);
      
      // Créer un nœud de texte avec la variable
      const textNode = document.createTextNode(formattedVariable);
      
      // Insérer la variable à la position actuelle
      range.deleteContents();
      range.insertNode(textNode);
      
      // Mettre à jour le contenu
      setContent(editor.innerHTML);
    }
  };
  
  // Ajouter une variable personnalisée
  const addCustomVariable = () => {
    if (!customVariable.trim()) return;
    
    // Vérifier si la variable existe déjà
    if (customVariables.includes(customVariable)) {
      alert('Cette variable existe déjà !');
      return;
    }
    
    setCustomVariables([...customVariables, customVariable]);
    setCustomVariable('');
  };
  
  // Gérer la sélection d'une variable à insérer
  const handleVariableSelect = (variableId) => {
    setSelectedVariable(variableId);
    if (variableId) {
      insertVariable(variableId);
      setSelectedVariable('');
    }
  };
  
  // Gérer le changement de contenu
  const handleContentChange = (newContent) => {
    setContent(newContent);
  };
  
  // Passer en mode prévisualisation avec des données de démonstration
  const togglePreview = () => {
    if (!previewMode) {
      // Données de démonstration pour la prévisualisation
      const demoClient = {
        nom: 'Dupont',
        prenom: 'Jean',
        email: 'jean.dupont@example.com',
        telephone: '06 12 34 56 78',
        adresse: '123 Avenue des Champs-Élysées',
        code_postal: '75008',
        ville: 'Paris',
        pays: 'France',
        entreprise: 'Dupont Technologies',
        siret: '123 456 789 00012',
        tva: 'FR 12 123456789',
        forme_juridique: 'SARL',
        adresse_entreprise: '123 Avenue des Champs-Élysées, 75008 Paris',
        date: new Date().toLocaleDateString('fr-FR'),
        date_creation: new Date().toLocaleDateString('fr-FR'),
        date_signature: new Date().toLocaleDateString('fr-FR'),
        date_echeance: new Date(Date.now() + 30*24*60*60*1000).toLocaleDateString('fr-FR')
      };
      
      // Ajouter les variables personnalisées
      const previewVars = {...demoClient};
      customVariables.forEach(customVar => {
        previewVars[customVar] = `[Valeur de ${customVar}]`;
      });
      
      setClientPreview(demoClient);
      setVariablePreview(previewVars);
    }
    
    setPreviewMode(!previewMode);
  };
  
  // Générer le contenu de prévisualisation
  const getPreviewContent = () => {
    if (!content || !previewMode || !variablePreview) return content;
    
    let previewContent = content;
    
    // Remplacer les variables au format {{variable}}
    previewContent = previewContent.replace(/\{\{([^{}]+)\}\}/g, (match, variable) => {
      return variablePreview[variable.trim()] || match;
    });
    
    // Remplacer les variables au format [[variable]]
    previewContent = previewContent.replace(/\[\[([^\[\]]+)\]\]/g, (match, variable) => {
      return variablePreview[variable.trim()] || match;
    });
    
    // Remplacer les variables au format XXXX_VARIABLE
    previewContent = previewContent.replace(/XXXX_([A-Za-z0-9_]+)/g, (match, variable) => {
      return variablePreview[variable.trim()] || match;
    });
    
    // Remplacer les variables au format ${variable}
    previewContent = previewContent.replace(/\$\{([^{}]+)\}/g, (match, variable) => {
      return variablePreview[variable.trim()] || match;
    });
    
    return previewContent;
  };
  
  // Sauvegarder le modèle
  const handleSave = async () => {
    if (!title.trim()) {
      alert('Veuillez saisir un titre pour le modèle');
      return;
    }
    
    try {
      const templateData = {
        title,
        description,
        content,
        category,
        isTemplate: true,
        customVariables,
        lastModified: new Date().toISOString(),
        createdAt: template?.createdAt || new Date().toISOString()
      };
      
      onSave(templateData);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du modèle:', error);
      alert('Une erreur est survenue lors de la sauvegarde du modèle.');
    }
  };
  
  return (
    <div className="template-editor">
      <div className="template-editor-header">
        <div className="template-editor-header-inputs">
          <Input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Titre du modèle"
            className="template-title-input"
          />
          <Input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description du modèle"
            className="template-description-input"
          />
          <div className="template-category-select">
            <label>Catégorie:</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="contract">Contrat</option>
              <option value="quote">Devis</option>
              <option value="invoice">Facture</option>
              <option value="letter">Courrier</option>
              <option value="other">Autre</option>
            </select>
          </div>
        </div>
        <div className="template-editor-actions">
          <Button variant="secondary" onClick={togglePreview}>
            {previewMode ? 'Mode édition' : 'Prévisualiser'}
          </Button>
          <Button variant="primary" onClick={handleSave}>
            Sauvegarder
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Fermer
          </Button>
        </div>
      </div>
      
      <div className="template-editor-content">
        <div className="template-editor-main">
          {previewMode ? (
            <div className="template-preview-container">
              <div className="template-preview-header">
                <h3>Prévisualisation du document avec variables</h3>
              </div>
              <div 
                className="template-preview-content"
                dangerouslySetInnerHTML={{ __html: getPreviewContent() }}
              />
            </div>
          ) : (
            <TiptapEditor
              content={content}
              onChange={handleContentChange}
            />
          )}
        </div>
        
        {!previewMode && (
          <div className="template-editor-sidebar">
            <div className="template-variables-panel">
              <div className="template-variables-header">
                <h3>Insertion de variables</h3>
                <Button 
                  variant="transparent" 
                  className="toggle-panel-button"
                  onClick={() => setShowVariablePanel(!showVariablePanel)}
                >
                  {showVariablePanel ? '▼' : '▶'}
                </Button>
              </div>
              
              {showVariablePanel && (
                <div className="template-variables-content">
                  <div className="template-variables-format">
                    <label>Format des variables:</label>
                    <select
                      value={selectedFormat}
                      onChange={(e) => setSelectedFormat(e.target.value)}
                    >
                      {VARIABLE_FORMATS.map(format => (
                        <option key={format.id} value={format.id}>
                          {format.label} ({format.format})
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="template-variables-categories">
                    <label>Catégorie de variables:</label>
                    <select
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      {VARIABLE_CATEGORIES.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="template-variables-list">
                    {selectedCategory === 'custom' ? (
                      <div className="template-custom-variables">
                        <div className="template-custom-variables-add">
                          <Input
                            type="text"
                            value={customVariable}
                            onChange={(e) => setCustomVariable(e.target.value)}
                            placeholder="Nom de la variable"
                          />
                          <Button variant="primary" onClick={addCustomVariable}>
                            Ajouter
                          </Button>
                        </div>
                        
                        {customVariables.length > 0 ? (
                          <div className="template-custom-variables-list">
                            {customVariables.map(variable => (
                              <div 
                                key={variable} 
                                className="template-variable-item"
                                onClick={() => handleVariableSelect(variable)}
                              >
                                {variable} <span className="insert-text">Insérer</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="template-variables-empty">
                            Aucune variable personnalisée
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="template-standard-variables">
                        {VARIABLE_CATEGORIES.find(c => c.id === selectedCategory)?.variables.map(variable => (
                          <div 
                            key={variable.id} 
                            className="template-variable-item"
                            onClick={() => handleVariableSelect(variable.id)}
                          >
                            {variable.label} <span className="variable-id">({variable.id})</span>
                            <span className="insert-text">Insérer</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            <div className="template-detected-variables">
              <h3>Variables détectées dans le document</h3>
              <div className="template-detected-variables-list">
                {detectVariables(content).length > 0 ? (
                  detectVariables(content).map((variable, index) => (
                    <div key={index} className="template-detected-variable">
                      <span className="variable-name">{variable.name}</span>
                      <span className="variable-format">{VARIABLE_FORMATS.find(f => f.id === variable.format)?.label}</span>
                    </div>
                  ))
                ) : (
                  <div className="template-variables-empty">
                    Aucune variable détectée
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplateEditor; 
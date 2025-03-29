import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import TemplateEditor from '../components/TemplateEditor';
import Loader from '../components/Loader';
import Button from '../components/Button';
import './TemplateEditorPage.css';

const TemplateEditorPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { documents, createDocument, updateDocument, isLoading, error } = useAppContext();
  
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  
  // Charger le modèle existant si un ID est fourni
  useEffect(() => {
    const loadTemplate = async () => {
      setLoading(true);
      
      try {
        if (id === 'new') {
          // Créer un nouveau modèle
          setTemplate({
            title: '',
            description: '',
            content: '',
            category: 'contract',
            isTemplate: true,
            customVariables: []
          });
        } else if (id) {
          // Trouver le modèle existant
          const existingTemplate = documents.find(doc => doc.id === id);
          
          if (!existingTemplate) {
            setLoadError('Modèle introuvable');
          } else if (!existingTemplate.isTemplate) {
            setLoadError('Ce document n\'est pas un modèle');
          } else {
            setTemplate(existingTemplate);
          }
        } else {
          setLoadError('Identifiant de modèle non spécifié');
        }
      } catch (err) {
        console.error('Erreur lors du chargement du modèle:', err);
        setLoadError(`Erreur: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    
    loadTemplate();
  }, [id, documents]);
  
  // Sauvegarder le modèle
  const handleSaveTemplate = async (templateData) => {
    try {
      if (id === 'new') {
        // Créer un nouveau modèle
        await createDocument(templateData);
        navigate('/templates');
      } else {
        // Mettre à jour le modèle existant
        await updateDocument(id, templateData);
        navigate('/templates');
      }
    } catch (err) {
      console.error('Erreur lors de la sauvegarde du modèle:', err);
      alert(`Erreur lors de la sauvegarde: ${err.message}`);
    }
  };
  
  // Fermer l'éditeur
  const handleClose = () => {
    if (confirm('Êtes-vous sûr de vouloir quitter sans sauvegarder ?')) {
      navigate('/templates');
    }
  };
  
  if (loading || isLoading) {
    return (
      <div className="template-editor-page">
        <div className="template-editor-loading">
          <Loader text="Chargement du modèle..." />
        </div>
      </div>
    );
  }
  
  if (loadError || error) {
    return (
      <div className="template-editor-page">
        <div className="template-editor-error">
          <h2>Erreur</h2>
          <p>{loadError || error}</p>
          <Button variant="primary" onClick={() => navigate('/templates')}>
            Retour à la liste des modèles
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="template-editor-page">
      <TemplateEditor 
        template={template}
        onSave={handleSaveTemplate}
        onClose={handleClose}
      />
    </div>
  );
};

export default TemplateEditorPage; 
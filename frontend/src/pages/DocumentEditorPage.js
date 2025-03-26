import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import DocumentEditor from '../components/DocumentEditor';
import Loader from '../components/Loader';
import './DocumentEditorPage.css';

const DocumentEditorPage = () => {
  const { documentId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { documents, templates, isLoading, error, setSidebarVisible } = useAppContext();
  const [document, setDocument] = useState(null);
  const [documentTemplates, setDocumentTemplates] = useState([]);

  // Masquer la sidebar à l'ouverture de l'éditeur
  useEffect(() => {
    // Cacher la sidebar quand l'éditeur est ouvert
    setSidebarVisible(false);
    
    // Restaurer la sidebar quand le composant est démonté
    return () => {
      setSidebarVisible(true);
    };
  }, [setSidebarVisible]);

  // Récupérer le document à éditer s'il existe
  useEffect(() => {
    if (documentId && documents.length > 0) {
      const foundDocument = documents.find(doc => doc.id === documentId);
      if (foundDocument) {
        setDocument(foundDocument);
      } else {
        // Si le document n'existe pas, créer un nouveau document avec le type spécifié dans l'URL
        const queryParams = new URLSearchParams(location.search);
        const documentType = queryParams.get('type') || 'document';
        const documentTitle = queryParams.get('title') || 'Nouveau document';
        setDocument({
          title: documentTitle,
          content: '',
          type: documentType
        });
      }
    } else if (!documentId) {
      // Créer un nouveau document avec le type spécifié dans l'URL
      const queryParams = new URLSearchParams(location.search);
      const documentType = queryParams.get('type') || 'document';
      const documentTitle = queryParams.get('title') || 'Nouveau document';
      setDocument({
        title: documentTitle,
        content: '',
        type: documentType
      });
    }
  }, [documentId, documents, location.search]);

  // Préparer les modèles pour l'éditeur
  useEffect(() => {
    const allTemplates = templates.filter(template => !template.isDeleted);
    setDocumentTemplates(allTemplates);
  }, [templates]);

  const handleSave = (savedDocument) => {
    // Rediriger vers la page des documents après la sauvegarde
    setSidebarVisible(true);
    navigate('/documents');
  };

  const handleClose = () => {
    // Confirmer si l'utilisateur veut quitter sans sauvegarder
    if (window.confirm('Voulez-vous quitter sans enregistrer ?')) {
      setSidebarVisible(true);
      navigate('/documents');
    }
  };

  if (isLoading && (!document || !documentTemplates)) {
    return <Loader fullPage text="Chargement de l'éditeur..." />;
  }

  if (error) {
    return (
      <div className="editor-error">
        <h2>Erreur lors du chargement</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/documents')}>Retour aux documents</button>
      </div>
    );
  }

  return (
    <div className="document-editor-page">
      {document && (
        <DocumentEditor
          initialDocument={document}
          onSave={handleSave}
          onClose={handleClose}
          templates={documentTemplates}
        />
      )}
    </div>
  );
};

export default DocumentEditorPage; 
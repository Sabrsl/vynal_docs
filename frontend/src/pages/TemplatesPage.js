import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import Loader from '../components/Loader';
import './DocumentsPage.css'; // Réutiliser les mêmes styles

const TemplatesPage = () => {
  const { documents, createDocument, deleteDocument, isLoading, error } = useAppContext();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewTemplateModal, setShowNewTemplateModal] = useState(false);
  const [newTemplateTitle, setNewTemplateTitle] = useState('');
  const [newTemplateType, setNewTemplateType] = useState('document');

  // Filtrer les modèles qui appartiennent à l'utilisateur actuel
  // Nous utilisons le type 'template' pour identifier les modèles
  const userTemplates = documents.filter(doc => doc.userId === user?.id && doc.isTemplate === true);
  
  // Filtrer en fonction de la recherche
  const filteredTemplates = userTemplates.filter(template => {
    return template.title.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleCreateTemplate = async () => {
    if (!newTemplateTitle.trim()) {
      alert('Veuillez saisir un titre pour le modèle');
      return;
    }

    try {
      await createDocument({
        title: newTemplateTitle,
        type: newTemplateType,
        isTemplate: true,
        content: ''
      });
      
      setNewTemplateTitle('');
      setNewTemplateType('document');
      setShowNewTemplateModal(false);
    } catch (err) {
      console.error('Erreur lors de la création du modèle:', err);
      alert(`Erreur: ${err.message}`);
    }
  };

  const handleDeleteTemplate = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce modèle ?')) {
      try {
        await deleteDocument(id);
      } catch (err) {
        console.error('Erreur lors de la suppression du modèle:', err);
        alert(`Erreur: ${err.message}`);
      }
    }
  };

  return (
    <div className="documents-page">
      <div className="page-header">
        <h1>Mes Modèles</h1>
        <Button 
          variant="primary" 
          onClick={() => setShowNewTemplateModal(true)}
          icon="bx-plus"
        >
          Nouveau modèle
        </Button>
      </div>

      <div className="documents-filters">
        <div className="search-container">
          <Input
            type="text"
            placeholder="Rechercher un modèle..."
            value={searchTerm}
            onChange={handleSearch}
            prefixIcon="bx-search"
          />
        </div>
      </div>

      {isLoading && userTemplates.length === 0 ? (
        <div className="documents-loading">
          <Loader text="Chargement des modèles..." />
        </div>
      ) : error ? (
        <div className="documents-error">
          <p>Une erreur est survenue: {error}</p>
          <Button variant="primary" onClick={() => window.location.reload()}>
            Réessayer
          </Button>
        </div>
      ) : filteredTemplates.length === 0 ? (
        <div className="documents-empty">
          <i className="bx bx-file-blank"></i>
          <h2>Aucun modèle trouvé</h2>
          <p>
            {searchTerm
              ? 'Aucun modèle ne correspond à votre recherche.'
              : 'Vous n\'avez pas encore créé de modèle.'}
          </p>
          {searchTerm ? (
            <Button variant="primary" onClick={() => setSearchTerm('')}>
              Effacer la recherche
            </Button>
          ) : (
            <Button variant="primary" onClick={() => setShowNewTemplateModal(true)}>
              Créer mon premier modèle
            </Button>
          )}
        </div>
      ) : (
        <div className="documents-grid">
          {filteredTemplates.map((template) => (
            <Card key={template.id} className="document-card">
              <div className="document-icon">
                {template.type === 'document' && <i className="bx bxs-file-doc"></i>}
                {template.type === 'presentation' && <i className="bx bxs-slideshow"></i>}
                {template.type === 'spreadsheet' && <i className="bx bxs-spreadsheet"></i>}
              </div>
              <div className="document-info">
                <h3>{template.title}</h3>
                <div className="document-meta">
                  <span>Modifié il y a {template.modified}</span>
                  <span>{template.views} vues</span>
                </div>
              </div>
              <div className="document-actions">
                <Button 
                  variant="transparent" 
                  icon="bx-pencil"
                  title="Modifier"
                  onClick={() => alert(`Éditer: ${template.title}`)}
                />
                <Button 
                  variant="transparent" 
                  icon="bx-copy"
                  title="Utiliser comme modèle"
                  onClick={() => alert(`Créer à partir de: ${template.title}`)}
                />
                <Button 
                  variant="transparent" 
                  icon="bx-trash"
                  title="Supprimer"
                  onClick={() => handleDeleteTemplate(template.id)}
                />
              </div>
            </Card>
          ))}
        </div>
      )}

      {showNewTemplateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Nouveau modèle</h2>
              <Button 
                variant="transparent" 
                icon="bx-x"
                onClick={() => setShowNewTemplateModal(false)}
              />
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Titre</label>
                <Input
                  type="text"
                  placeholder="Saisissez un titre..."
                  value={newTemplateTitle}
                  onChange={(e) => setNewTemplateTitle(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Type</label>
                <div className="document-type-selector">
                  <div 
                    className={`type-option ${newTemplateType === 'document' ? 'selected' : ''}`}
                    onClick={() => setNewTemplateType('document')}
                  >
                    <i className="bx bxs-file-doc"></i>
                    <span>Document</span>
                  </div>
                  <div 
                    className={`type-option ${newTemplateType === 'presentation' ? 'selected' : ''}`}
                    onClick={() => setNewTemplateType('presentation')}
                  >
                    <i className="bx bxs-slideshow"></i>
                    <span>Présentation</span>
                  </div>
                  <div 
                    className={`type-option ${newTemplateType === 'spreadsheet' ? 'selected' : ''}`}
                    onClick={() => setNewTemplateType('spreadsheet')}
                  >
                    <i className="bx bxs-spreadsheet"></i>
                    <span>Tableur</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <Button 
                variant="default" 
                onClick={() => setShowNewTemplateModal(false)}
              >
                Annuler
              </Button>
              <Button 
                variant="primary" 
                onClick={handleCreateTemplate}
                disabled={!newTemplateTitle.trim()}
              >
                Créer
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplatesPage; 
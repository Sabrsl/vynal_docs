import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import Loader from '../components/Loader';
import './DocumentsPage.css';

const DocumentsPage = () => {
  const location = useLocation();
  const { documents, createDocument, deleteDocument, isLoading, error } = useAppContext();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [showNewDocumentModal, setShowNewDocumentModal] = useState(false);
  const [newDocumentTitle, setNewDocumentTitle] = useState('');
  const [newDocumentType, setNewDocumentType] = useState('document');

  // Vérifier si l'URL contient ?new=true pour ouvrir le modal
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    if (queryParams.get('new') === 'true') {
      setShowNewDocumentModal(true);
      // Nettoyer le paramètre de l'URL sans recharger la page
      window.history.replaceState({}, '', '/documents');
    }
  }, [location]);

  // Filtrer les documents qui appartiennent à l'utilisateur actuel
  const userDocuments = documents.filter(doc => doc.userId === user?.id);
  
  // Filtrer en fonction de la recherche et du type
  const filteredDocuments = userDocuments.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || doc.type === selectedType;
    return matchesSearch && matchesType;
  });

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleFilterChange = (type) => {
    setSelectedType(type);
  };

  const handleCreateDocument = async () => {
    if (!newDocumentTitle.trim()) {
      alert('Veuillez saisir un titre pour le document');
      return;
    }

    try {
      await createDocument({
        title: newDocumentTitle,
        type: newDocumentType,
        content: ''
      });
      
      setNewDocumentTitle('');
      setNewDocumentType('document');
      setShowNewDocumentModal(false);
    } catch (err) {
      console.error('Erreur lors de la création du document:', err);
      alert(`Erreur: ${err.message}`);
    }
  };

  const handleDeleteDocument = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      try {
        await deleteDocument(id);
      } catch (err) {
        console.error('Erreur lors de la suppression du document:', err);
        alert(`Erreur: ${err.message}`);
      }
    }
  };

  return (
    <div className="documents-page">
      <div className="page-header">
        <h1>Mes Documents</h1>
        <Button 
          variant="primary" 
          onClick={() => setShowNewDocumentModal(true)}
          icon="bx-plus"
        >
          Nouveau document
        </Button>
      </div>

      <div className="documents-filters">
        <div className="search-container">
          <Input
            type="text"
            placeholder="Rechercher un document..."
            value={searchTerm}
            onChange={handleSearch}
            prefixIcon="bx-search"
          />
        </div>
        <div className="type-filters">
          <Button 
            variant={selectedType === 'all' ? 'primary' : 'default'} 
            onClick={() => handleFilterChange('all')}
            size="small"
          >
            Tous
          </Button>
          <Button 
            variant={selectedType === 'document' ? 'primary' : 'default'} 
            onClick={() => handleFilterChange('document')}
            size="small"
          >
            Documents
          </Button>
          <Button 
            variant={selectedType === 'presentation' ? 'primary' : 'default'} 
            onClick={() => handleFilterChange('presentation')}
            size="small"
          >
            Présentations
          </Button>
          <Button 
            variant={selectedType === 'spreadsheet' ? 'primary' : 'default'} 
            onClick={() => handleFilterChange('spreadsheet')}
            size="small"
          >
            Tableurs
          </Button>
        </div>
      </div>

      {isLoading && userDocuments.length === 0 ? (
        <div className="documents-loading">
          <Loader text="Chargement des documents..." />
        </div>
      ) : error ? (
        <div className="documents-error">
          <p>Une erreur est survenue: {error}</p>
          <Button variant="primary" onClick={() => window.location.reload()}>
            Réessayer
          </Button>
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="documents-empty">
          <i className="bx bx-file-blank"></i>
          <h2>Aucun document trouvé</h2>
          <p>
            {searchTerm || selectedType !== 'all'
              ? 'Aucun document ne correspond à vos critères de recherche.'
              : 'Vous n\'avez pas encore créé de document.'}
          </p>
          {searchTerm || selectedType !== 'all' ? (
            <Button variant="primary" onClick={() => { setSearchTerm(''); setSelectedType('all'); }}>
              Effacer les filtres
            </Button>
          ) : (
            <Button variant="primary" onClick={() => setShowNewDocumentModal(true)}>
              Créer mon premier document
            </Button>
          )}
        </div>
      ) : (
        <div className="documents-grid">
          {filteredDocuments.map((doc) => (
            <Card key={doc.id} className="document-card">
              <div className="document-icon">
                {doc.type === 'document' && <i className="bx bxs-file-doc"></i>}
                {doc.type === 'presentation' && <i className="bx bxs-slideshow"></i>}
                {doc.type === 'spreadsheet' && <i className="bx bxs-spreadsheet"></i>}
              </div>
              <div className="document-info">
                <h3>{doc.title}</h3>
                <div className="document-meta">
                  <span>Modifié il y a {doc.modified}</span>
                  <span>{doc.views} vues</span>
                </div>
              </div>
              <div className="document-actions">
                <Button 
                  variant="transparent" 
                  icon="bx-pencil"
                  title="Modifier"
                  onClick={() => alert(`Éditer: ${doc.title}`)}
                />
                <Button 
                  variant="transparent" 
                  icon="bx-share-alt"
                  title="Partager"
                  onClick={() => alert(`Partager: ${doc.title}`)}
                />
                <Button 
                  variant="transparent" 
                  icon="bx-trash"
                  title="Supprimer"
                  onClick={() => handleDeleteDocument(doc.id)}
                />
              </div>
            </Card>
          ))}
        </div>
      )}

      {showNewDocumentModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Nouveau document</h2>
              <Button 
                variant="transparent" 
                icon="bx-x"
                onClick={() => setShowNewDocumentModal(false)}
              />
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Titre</label>
                <Input
                  type="text"
                  placeholder="Saisissez un titre..."
                  value={newDocumentTitle}
                  onChange={(e) => setNewDocumentTitle(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Type</label>
                <div className="document-type-selector">
                  <div 
                    className={`type-option ${newDocumentType === 'document' ? 'selected' : ''}`}
                    onClick={() => setNewDocumentType('document')}
                  >
                    <i className="bx bxs-file-doc"></i>
                    <span>Document</span>
                  </div>
                  <div 
                    className={`type-option ${newDocumentType === 'presentation' ? 'selected' : ''}`}
                    onClick={() => setNewDocumentType('presentation')}
                  >
                    <i className="bx bxs-slideshow"></i>
                    <span>Présentation</span>
                  </div>
                  <div 
                    className={`type-option ${newDocumentType === 'spreadsheet' ? 'selected' : ''}`}
                    onClick={() => setNewDocumentType('spreadsheet')}
                  >
                    <i className="bx bxs-spreadsheet"></i>
                    <span>Tableur</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <Button variant="text" onClick={() => setShowNewDocumentModal(false)}>
                Annuler
              </Button>
              <Button variant="primary" onClick={handleCreateDocument}>
                Créer
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage; 
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import Loader from '../components/Loader';
import DocumentGenerator from '../components/DocumentGenerator';
import './DocumentsPage.css';

const DocumentsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { documents, templates, contacts, createDocument, deleteDocument, isLoading, error } = useAppContext();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [showNewDocumentModal, setShowNewDocumentModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [newDocumentTitle, setNewDocumentTitle] = useState('');
  const [newDocumentType, setNewDocumentType] = useState('document');
  const [generatedDocuments, setGeneratedDocuments] = useState([]);

  // Vérifier si l'URL contient ?new=true pour ouvrir le modal
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    if (queryParams.get('new') === 'true') {
      setShowNewDocumentModal(true);
      // Nettoyer le paramètre de l'URL sans recharger la page
      window.history.replaceState({}, '', '/documents');
    }
    
    // Récupérer les documents générés du localStorage
    const storedDocs = localStorage.getItem('generatedDocuments');
    if (storedDocs) {
      try {
        setGeneratedDocuments(JSON.parse(storedDocs));
      } catch (e) {
        console.error('Erreur lors de la récupération des documents générés:', e);
      }
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

    // Fermer la modal
    setShowNewDocumentModal(false);
    
    // Rediriger vers la page d'édition avec le type comme paramètre d'URL
    navigate(`/documents/new?type=${newDocumentType}&title=${encodeURIComponent(newDocumentTitle)}`);
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
  
  // Gérer le succès de la génération de document
  const handleGenerateSuccess = (documentInfo) => {
    // Enregistrer le document généré dans la liste
    const newGeneratedDoc = {
      id: Date.now(),
      template: documentInfo.template,
      contact: documentInfo.contact,
      documentUrl: documentInfo.documentUrl,
      filename: documentInfo.filename,
      format: documentInfo.format,
      date: new Date().toLocaleString()
    };
    
    const updatedDocs = [newGeneratedDoc, ...generatedDocuments];
    setGeneratedDocuments(updatedDocs);
    
    // Stocker dans localStorage pour persistance
    localStorage.setItem('generatedDocuments', JSON.stringify(updatedDocs));
    
    // Fermer le modal
    setShowTemplateModal(false);
  };

  return (
    <div className="documents-page">
      <div className="page-header">
        <h1>Mes Documents</h1>
        <div className="document-actions-header">
          <Button 
            variant="primary" 
            onClick={() => navigate('/documents/new?type=document')}
            icon="bx-file-blank"
            style={{ marginRight: '10px' }}
          >
            Document vide
          </Button>
          <Button 
            variant="primary" 
            onClick={() => setShowTemplateModal(true)}
            icon="bx-file-plus"
            style={{ marginRight: '10px' }}
          >
            Avec modèle
          </Button>
          <Button 
            variant="primary" 
            onClick={() => setShowNewDocumentModal(true)}
            icon="bx-plus"
          >
            Personnalisé
          </Button>
        </div>
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
            <Button variant="primary" onClick={() => setShowTemplateModal(true)}>
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
                  onClick={() => navigate(`/documents/edit/${doc.id}`)}
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

      {/* Modal pour créer un document personnalisé */}
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
      
      {/* Modal pour utiliser le générateur de documents */}
      {showTemplateModal && (
        <div className="modal-overlay document-generator-modal-overlay">
          <div className="modal document-generator-modal">
            <div className="modal-header">
              <h2><i className="bx bx-file-find"></i> Créer un document avec modèle</h2>
              <div className="modal-header-actions">
                <Button 
                  variant="transparent" 
                  icon="bx-expand"
                  title="Agrandir le formulaire"
                  onClick={() => document.querySelector('.document-generator-modal').classList.toggle('expanded')}
                />
                <Button 
                  variant="transparent" 
                  icon="bx-x"
                  onClick={() => setShowTemplateModal(false)}
                />
              </div>
            </div>
            <div className="modal-body document-generator-modal-body">
              <DocumentGenerator 
                templates={templates} 
                contacts={contacts}
                onGenerateSuccess={handleGenerateSuccess}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage; 
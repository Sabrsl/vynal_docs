import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import Loader from '../components/Loader';
import DocumentDetail from '../components/DocumentDetail';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';
import '../styles/components/DocumentDetail.css';

const HomePage = () => {
  const { 
    documents, 
    activities, 
    createDocument, 
    isLoading, 
    error,
    setActiveSection,
    refreshData
  } = useAppContext();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [showNewDocumentForm, setShowNewDocumentForm] = useState(false);
  const [newDocumentData, setNewDocumentData] = useState({
    title: '',
    type: 'document',
    content: ''
  });
  
  // État local pour contrôler le rafraîchissement des données
  const [refreshing, setRefreshing] = useState(false);
  
  // Effet pour simuler le temps de rafraîchissement
  useEffect(() => {
    if (refreshing) {
      const timer = setTimeout(() => {
        setRefreshing(false);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [refreshing]);

  // Fonction pour rafraîchir manuellement les données
  const handleRefresh = () => {
    setRefreshing(true);
    // Utiliser la fonction refreshData du contexte
    refreshData();
    // Réinitialiser l'indicateur de rafraîchissement après 1 seconde
    setTimeout(() => setRefreshing(false), 1000);
  };
  
  // Statistiques calculées
  const stats = [
    { id: 1, title: 'Documents', value: documents.length, icon: 'bx bx-file', color: 'primary' },
    { id: 2, title: 'Utilisateurs', value: 45, icon: 'bx bx-user', color: 'secondary' },
    { id: 3, title: 'Stockage utilisé', value: '2.7 GB', icon: 'bx bx-data', color: 'tertiary' },
    { id: 4, title: 'Activités', value: activities.length, icon: 'bx bx-bar-chart-alt-2', color: 'warning' }
  ];
  
  // Fonction pour obtenir l'icône du type de document
  const getDocumentIcon = (type) => {
    switch (type) {
      case 'document':
        return 'bx bxs-file-doc';
      case 'presentation':
        return 'bx bxs-slideshow';
      case 'spreadsheet':
        return 'bx bxs-spreadsheet';
      default:
        return 'bx bx-file';
    }
  };
  
  // Fonction pour rediriger vers la page Documents avec le modal ouvert
  const handleNewDocument = () => {
    navigate('/documents?new=true');
  };
  
  const handleNewDocumentSubmit = async (e) => {
    e.preventDefault();
    try {
      await createDocument(newDocumentData);
      setShowNewDocumentForm(false);
      setNewDocumentData({
        title: '',
        type: 'document',
        content: ''
      });
    } catch (error) {
      console.error('Erreur lors de la création:', error);
    }
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewDocumentData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleViewAll = () => {
    setActiveSection('documents');
  };
  
  const handleViewActivity = () => {
    setActiveSection('stats');
  };
  
  const handleDocumentClick = (docId) => {
    setSelectedDocumentId(docId);
  };
  
  const closeDocumentDetail = () => {
    setSelectedDocumentId(null);
  };
  
  // Filtrer les documents et activités par utilisateur
  const userDocuments = documents.filter(doc => doc.userId === user?.id);
  const userActivities = activities.filter(activity => activity.userId === user?.id);
  
  // Récupérer les documents récents (les 4 derniers modifiés)
  const recentDocuments = [...userDocuments]
    .sort((a, b) => new Date(b.created) - new Date(a.created))
    .slice(0, 4);
  
  // Récupérer les modèles (les 4 derniers créés)
  const templates = userDocuments
    .filter(doc => doc.isTemplate)
    .sort((a, b) => new Date(b.created) - new Date(a.created))
    .slice(0, 4);
  
  // Récupérer les activités récentes (les 5 dernières)
  const recentActivities = [...userActivities]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 5);
  
  if (isLoading && documents.length === 0) {
    return <Loader fullPage text="Chargement du tableau de bord..." />;
  }
  
  if (error) {
    return (
      <div className="error-message">
        <h2>Erreur</h2>
        <p>{error}</p>
        <Button variant="primary" onClick={() => window.location.reload()}>Réessayer</Button>
      </div>
    );
  }

  // Si un document est sélectionné, afficher ses détails
  if (selectedDocumentId) {
    return <DocumentDetail documentId={selectedDocumentId} onClose={closeDocumentDetail} />;
  }
  
  // Si le formulaire d'ajout est affiché
  if (showNewDocumentForm) {
    return (
      <Card
        title="Nouveau document"
        icon="bx-file-plus"
        actionButton={<Button variant="text" icon="bx-x" onClick={() => setShowNewDocumentForm(false)}></Button>}
      >
        <form onSubmit={handleNewDocumentSubmit} className="document-edit-form">
          <div className="form-group">
            <label htmlFor="title">Titre</label>
            <input
              type="text"
              id="title"
              name="title"
              value={newDocumentData.title}
              onChange={handleInputChange}
              className="form-control"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="type">Type</label>
            <select
              id="type"
              name="type"
              value={newDocumentData.type}
              onChange={handleInputChange}
              className="form-control"
            >
              <option value="document">Document</option>
              <option value="presentation">Présentation</option>
              <option value="spreadsheet">Feuille de calcul</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="content">Contenu</label>
            <textarea
              id="content"
              name="content"
              value={newDocumentData.content}
              onChange={handleInputChange}
              className="form-control"
              rows="10"
            />
          </div>
          
          <div className="form-actions">
            <Button variant="primary" submit>Créer</Button>
            <Button variant="text" onClick={() => setShowNewDocumentForm(false)}>Annuler</Button>
          </div>
        </form>
      </Card>
    );
  }
  
  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Tableau de bord</h1>
        <div className="page-actions">
          <Button 
            variant="primary" 
            icon="bx-plus" 
            onClick={handleNewDocument}
          >
            Nouveau document
          </Button>
          <Button 
            variant="default" 
            icon="bx-upload"
          >
            Importer un fichier
          </Button>
        </div>
      </div>

      <div className="stats-cards grid-4">
        {stats.map(stat => (
          <Card key={stat.id} className="stat-card">
            <div className={`stat-icon bg-${stat.color}-light`}>
              <i className={`${stat.icon} text-${stat.color}`}></i>
            </div>
            <div className="stat-content">
              <h2 className="stat-value">{stat.value}</h2>
              <p className="stat-title">{stat.title}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="dashboard-content">
        <div className="dashboard-main">
          <Card
            title="Documents récents"
            actionButton={
              <Button 
                variant="text" 
                icon={refreshing ? "bx-loader-alt bx-spin" : "bx-refresh"} 
                onClick={handleRefresh} 
                disabled={refreshing || isLoading}
              />
            }
          >
            {isLoading ? (
              <Loader text="Chargement des documents..." />
            ) : (
              <div className="recent-documents">
                {recentDocuments.length > 0 ? (
                  recentDocuments.map(doc => (
                    <div 
                      key={doc.id} 
                      className="document-item"
                      onClick={() => handleDocumentClick(doc.id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="document-icon">
                        <i className={getDocumentIcon(doc.type)}></i>
                      </div>
                      <div className="document-info">
                        <h3 className="document-title">{doc.title}</h3>
                        <p className="document-meta">Modifié il y a {doc.modified} • {doc.views} vues</p>
                      </div>
                      <div className="document-actions" onClick={e => e.stopPropagation()}>
                        <Button variant="text" icon="bx-edit" onClick={(e) => {
                          e.stopPropagation();
                          handleDocumentClick(doc.id);
                        }} />
                        <Button variant="text" icon="bx-share-alt" onClick={(e) => {
                          e.stopPropagation();
                          alert(`Partage du document ${doc.id}`);
                        }} />
                        <Button variant="text" icon="bx-dots-vertical-rounded" onClick={(e) => {
                          e.stopPropagation();
                          alert(`Options pour le document ${doc.id}`);
                        }} />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <i className="bx bx-file-blank"></i>
                    <p>Aucun document récent</p>
                    <Button variant="primary" onClick={handleNewDocument}>
                      Créer un document
                    </Button>
                  </div>
                )}
              </div>
            )}
            <div className="view-all-link">
              <Button variant="text" onClick={handleViewAll}>Voir tous les documents</Button>
            </div>
          </Card>
        </div>
        
        <div className="dashboard-sidebar">
          <Card
            title="Activité récente"
            actionButton={
              <Button 
                variant="text" 
                icon={refreshing ? "bx-loader-alt bx-spin" : "bx-refresh"} 
                onClick={handleRefresh} 
                disabled={refreshing || isLoading}
              />
            }
          >
            {isLoading ? (
              <Loader text="Chargement des activités..." />
            ) : (
              <div className="activity-list">
                {recentActivities.length > 0 ? (
                  recentActivities.map(activity => (
                    <div key={activity.id} className="activity-item">
                      <div className="activity-user">
                        <div className="user-avatar-initials role-user">
                          {activity.user ? activity.user.substring(0, 2) : "?"}
                        </div>
                      </div>
                      <div className="activity-content">
                        <p>
                          <span className="activity-user-name">{activity.user || "Utilisateur inconnu"}</span>
                          <span className="activity-action"> {activity.action} </span>
                          {activity.documentId ? (
                            <span 
                              className="activity-document"
                              style={{ cursor: 'pointer', textDecoration: 'underline' }}
                              onClick={() => handleDocumentClick(activity.documentId)}
                            >
                              {activity.document}
                            </span>
                          ) : (
                            <span className="activity-document">{activity.document}</span>
                          )}
                        </p>
                        <span className="activity-time">{activity.time}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <i className="bx bx-time"></i>
                    <p>Aucune activité récente</p>
                  </div>
                )}
              </div>
            )}
            <div className="view-all-link">
              <Button variant="text" onClick={handleViewActivity}>Voir toute l'activité</Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 
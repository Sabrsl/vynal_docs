import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import Loader from '../components/Loader';
import DocumentDetail from '../components/DocumentDetail';
import ContactForm from '../components/ContactForm';
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
  const [showContactForm, setShowContactForm] = useState(false);
  const [showNewFolderForm, setShowNewFolderForm] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTimeRange, setActiveTimeRange] = useState('week');
  const [showAllActivities, setShowAllActivities] = useState(false);

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
    refreshData();
    setTimeout(() => setRefreshing(false), 1000);
  };

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

  // Fonction pour voir tous les documents
  const handleViewAll = () => {
    setActiveSection('documents');
  };

  // Fonction pour gérer le clic sur un document
  const handleDocumentClick = (docId) => {
    setSelectedDocumentId(docId);
  };

  // Statistiques avec des tendances
  const stats = [
    { 
      id: 1, 
      title: 'Documents', 
      value: documents.length,
      trend: '+12%',
      trendUp: true,
      icon: 'bx bx-file',
      color: 'primary',
      bgGradient: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)'
    },
    { 
      id: 2, 
      title: 'Utilisateurs actifs', 
      value: '45',
      trend: '+5%',
      trendUp: true,
      icon: 'bx bx-user',
      color: 'success',
      bgGradient: 'linear-gradient(135deg, #34D399 0%, #059669 100%)'
    },
    { 
      id: 3, 
      title: 'Stockage utilisé', 
      value: '2.7 GB',
      trend: '-3%',
      trendUp: false,
      icon: 'bx bx-data',
      color: 'warning',
      bgGradient: 'linear-gradient(135deg, #FBBF24 0%, #D97706 100%)'
    },
    { 
      id: 4, 
      title: 'Activités', 
      value: activities.length,
      trend: '+18%',
      trendUp: true,
      icon: 'bx bx-bar-chart-alt-2',
      color: 'info',
      bgGradient: 'linear-gradient(135deg, #60A5FA 0%, #2563EB 100%)'
    }
  ];

  // Actions rapides
  const quickActions = [
    {
      icon: 'bx bx-file',
      label: 'Nouveau document',
      onClick: () => setShowNewDocumentForm(true)
    },
    {
      icon: 'bx bx-user',
      label: 'Ajouter un contact',
      onClick: () => setShowContactForm(true)
    },
    {
      icon: 'bx bx-copy',
      label: 'Créer un modèle',
      onClick: () => navigate('/templates/new')
    },
    {
      icon: 'bx bx-share-alt',
      label: 'Partages',
      onClick: () => navigate('/share')
    }
  ];

  // Filtrer les documents et activités
  const userDocuments = documents.filter(doc => doc.userId === user?.id);
  const recentDocuments = [...userDocuments]
    .sort((a, b) => new Date(b.modified || b.created) - new Date(a.modified || a.created))
    .slice(0, 6);

  const recentActivities = [...activities]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, showAllActivities ? undefined : 5);

  if (isLoading && documents.length === 0) {
    return <Loader fullPage text="Chargement du tableau de bord..." />;
  }

  // Si un document est sélectionné, afficher ses détails
  if (selectedDocumentId) {
    return <DocumentDetail documentId={selectedDocumentId} onClose={() => setSelectedDocumentId(null)} />;
  }

  // Si le formulaire de contact est affiché
  if (showContactForm) {
    return (
      <Card className="contact-form-card">
        <div className="card-header">
          <h2>Ajouter un contact</h2>
          <Button 
            variant="text" 
            icon="bx-x"
            onClick={() => setShowContactForm(false)}
          />
        </div>
        <ContactForm onClose={() => setShowContactForm(false)} />
      </Card>
    );
  }

  return (
    <div className="dashboard">
      {/* En-tête avec message de bienvenue */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Bonjour, {user?.name || 'Utilisateur'} 👋</h1>
          <p className="welcome-subtitle">Voici un aperçu de votre espace de travail</p>
        </div>
        <div className="header-actions">
          <Button 
            variant="text" 
            icon={refreshing ? 'bx bx-loader-alt bx-spin' : 'bx bx-refresh'}
            onClick={handleRefresh}
          >
            Actualiser
          </Button>
          <Button 
            variant="primary" 
            icon="bx bx-plus"
            onClick={handleNewDocument}
          >
            Nouveau document
          </Button>
        </div>
      </div>

      {/* Statistiques */}
      <div className="stats-grid">
        {stats.map(stat => (
          <div 
            key={stat.id} 
            className="stat-card" 
            style={{ background: stat.bgGradient }}
          >
            <div className="stat-icon">
              <i className={stat.icon}></i>
            </div>
            <div className="stat-info">
              <h3>{stat.title}</h3>
              <div className="stat-value">{stat.value}</div>
              <div className={`stat-trend ${stat.trendUp ? 'up' : 'down'}`}>
                <i className={`bx ${stat.trendUp ? 'bx-up-arrow-alt' : 'bx-down-arrow-alt'}`}></i>
                {stat.trend}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Actions rapides */}
      <div className="quick-actions-section">
        <h2>Actions rapides</h2>
        <div className="quick-actions-grid">
          {quickActions.map((action, index) => (
            <button 
              key={index} 
              className="quick-action-button" 
              onClick={action.onClick}
            >
              <i className={action.icon}></i>
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Documents récents et Activités */}
      <div className="dashboard-grid">
        <Card className="recent-documents">
          <div className="card-header">
            <h2>Documents récents</h2>
            <Button 
              variant="text" 
              onClick={handleViewAll}
            >
              Voir tout
            </Button>
          </div>
          <div className="documents-grid">
            {recentDocuments.map(doc => (
              <div 
                key={doc.id} 
                className="document-card" 
                onClick={() => handleDocumentClick(doc.id)}
              >
                <div className="document-icon">
                  <i className={getDocumentIcon(doc.type)}></i>
                </div>
                <div className="document-info">
                  <h3>{doc.title}</h3>
                  <p>Modifié {new Date(doc.modified || doc.created).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="activities-card">
          <div className="card-header">
            <h2>Activités récentes</h2>
            <div className="activity-filters">
              <Button 
                variant={activeTimeRange === 'week' ? 'primary' : 'text'}
                onClick={() => setActiveTimeRange('week')}
              >
                Semaine
              </Button>
              <Button 
                variant={activeTimeRange === 'month' ? 'primary' : 'text'}
                onClick={() => setActiveTimeRange('month')}
              >
                Mois
              </Button>
            </div>
          </div>
          <div className="activities-list">
            {recentActivities.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  <i className={`bx ${activity.type === 'create' ? 'bx-plus-circle' : 'bx-edit-alt'}`}></i>
                </div>
                <div className="activity-content">
                  <p>{activity.description}</p>
                  <span className="activity-time">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
          {activities.length > 5 && !showAllActivities && (
            <Button 
              variant="text" 
              className="show-more-button"
              onClick={() => setShowAllActivities(true)}
            >
              Voir plus d'activités
            </Button>
          )}
        </Card>
      </div>
    </div>
  );
};

export default HomePage; 
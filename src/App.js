import React, { useState } from 'react';
import './App.css';
import logo from './assets/logo.svg';
import avatar from './assets/avatar.svg';

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Données pour le tableau de bord
  const stats = [
    { id: 1, title: 'Documents', value: 254, icon: 'bx bx-file', color: 'primary' },
    { id: 2, title: 'Utilisateurs', value: 45, icon: 'bx bx-user', color: 'info' },
    { id: 3, title: 'Stockage utilisé', value: '2.7 GB', icon: 'bx bx-data', color: 'success' },
    { id: 4, title: 'Activités', value: 158, icon: 'bx bx-bar-chart-alt-2', color: 'warning' }
  ];
  
  const recentDocuments = [
    { id: 1, title: 'Rapport annuel 2024', type: 'document', modified: '2h', views: 24 },
    { id: 2, title: 'Présentation client', type: 'presentation', modified: '5h', views: 15 },
    { id: 3, title: 'Données financières Q1', type: 'spreadsheet', modified: '12h', views: 8 },
    { id: 4, title: 'Plan de projet', type: 'document', modified: '1j', views: 32 }
  ];
  
  const activities = [
    { id: 1, user: 'John Doe', action: 'a créé un document', document: 'Rapport annuel 2024', time: '2h' },
    { id: 2, user: 'Alice Smith', action: 'a modifié', document: 'Présentation client', time: '5h' },
    { id: 3, user: 'Robert Johnson', action: 'a partagé', document: 'Données financières Q1', time: '12h' },
    { id: 4, user: 'Emma Wilson', action: 'a supprimé', document: 'Ancien brouillon', time: '1j' },
    { id: 5, user: 'Michael Brown', action: 'a commenté sur', document: 'Plan de projet', time: '2j' }
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
  
  // Obtenir les initiales d'un nom
  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('');
  };
  
  return (
    <div className="app">
      {/* En-tête */}
      <header className="app-header">
        <div className="app-logo">
          <img src={logo} alt="Logo" width="30" />
          <span>Vynal <span className="app-title">Docs</span></span>
        </div>
        
        <div className="app-search">
          <div className="search-input-wrapper">
            <i className="bx bx-search search-icon"></i>
            <input 
              type="text" 
              placeholder="Rechercher..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className="app-actions">
          <button className="icon-button">
            <i className="bx bx-bell"></i>
            <span className="notification-badge"></span>
          </button>
          <button className="icon-button">
            <i className="bx bx-cog"></i>
          </button>
          <div className="user-menu">
            <img src={avatar} alt="Avatar" className="user-avatar" />
            <span className="user-name">Jean Dupont</span>
          </div>
        </div>
      </header>
      
      {/* Contenu principal */}
      <div className="app-content">
        {/* Barre latérale */}
        <nav className="app-sidebar">
          <div 
            className={`sidebar-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <i className="bx bx-grid-alt"></i>
            <span>Tableau de bord</span>
          </div>
          <div 
            className={`sidebar-item ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            <i className="bx bx-file"></i>
            <span>Documents</span>
          </div>
          <div 
            className={`sidebar-item ${activeTab === 'templates' ? 'active' : ''}`}
            onClick={() => setActiveTab('templates')}
          >
            <i className="bx bx-file-blank"></i>
            <span>Modèles</span>
          </div>
          <div 
            className={`sidebar-item ${activeTab === 'categories' ? 'active' : ''}`}
            onClick={() => setActiveTab('categories')}
          >
            <i className="bx bx-folder"></i>
            <span>Catégories</span>
          </div>
          <div 
            className={`sidebar-item ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            <i className="bx bx-user"></i>
            <span>Utilisateurs</span>
          </div>
          <div 
            className={`sidebar-item ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <i className="bx bx-bar-chart-alt-2"></i>
            <span>Statistiques</span>
          </div>
          <div 
            className={`sidebar-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <i className="bx bx-cog"></i>
            <span>Paramètres</span>
          </div>
        </nav>
        
        {/* Contenu principal */}
        <main className="app-main">
          <div className="page-header">
            <h1>Tableau de bord</h1>
            <div className="page-actions">
              <button className="button button-primary">
                <i className="bx bx-plus"></i>
                <span>Nouveau document</span>
              </button>
            </div>
          </div>
          
          {/* Statistiques */}
          <div className="stats-grid">
            {stats.map(stat => (
              <div key={stat.id} className={`stat-card ${stat.color}`}>
                <div className="stat-icon-wrapper">
                  <i className={stat.icon}></i>
                </div>
                <div className="stat-content">
                  <div className="stat-value">{stat.value}</div>
                  <div className="stat-title">{stat.title}</div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Contenu du tableau de bord */}
          <div className="dashboard-content">
            <div className="dashboard-main">
              {/* Documents récents */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">Documents récents</h2>
                  <div className="card-actions">
                    <button className="icon-button">
                      <i className="bx bx-dots-horizontal-rounded"></i>
                    </button>
                  </div>
                </div>
                <div className="card-content">
                  <div className="document-list">
                    {recentDocuments.map(doc => (
                      <div key={doc.id} className="document-item">
                        <div className="document-icon">
                          <i className={getDocumentIcon(doc.type)}></i>
                        </div>
                        <div className="document-info">
                          <h3 className="document-title">{doc.title}</h3>
                          <p className="document-meta">Modifié il y a {doc.modified} • {doc.views} vues</p>
                        </div>
                        <div className="document-actions">
                          <button className="icon-button small">
                            <i className="bx bx-edit"></i>
                          </button>
                          <button className="icon-button small">
                            <i className="bx bx-share-alt"></i>
                          </button>
                          <button className="icon-button small">
                            <i className="bx bx-dots-vertical-rounded"></i>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="card-footer">
                    <button className="button button-text">
                      <span>Voir tous les documents</span>
                      <i className="bx bx-right-arrow-alt"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="dashboard-sidebar">
              {/* Activités récentes */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">Activité récente</h2>
                  <div className="card-actions">
                    <button className="icon-button">
                      <i className="bx bx-refresh"></i>
                    </button>
                  </div>
                </div>
                <div className="card-content">
                  <div className="activity-list">
                    {activities.map(activity => (
                      <div key={activity.id} className="activity-item">
                        <div className="activity-avatar">
                          <div className="avatar-initials">
                            {getInitials(activity.user)}
                          </div>
                        </div>
                        <div className="activity-content">
                          <p className="activity-text">
                            <span className="activity-user">{activity.user}</span>
                            <span className="activity-action">{activity.action}</span>
                            <span className="activity-document">{activity.document}</span>
                          </p>
                          <span className="activity-time">Il y a {activity.time}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="card-footer">
                    <button className="button button-text">
                      <span>Voir toute l'activité</span>
                      <i className="bx bx-right-arrow-alt"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App; 
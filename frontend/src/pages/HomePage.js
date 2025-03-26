import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';

const HomePage = () => {
  // Données de statistiques fictives
  const stats = [
    { id: 1, title: 'Documents', value: 254, icon: 'bx bx-file', color: 'primary' },
    { id: 2, title: 'Utilisateurs', value: 45, icon: 'bx bx-user', color: 'secondary' },
    { id: 3, title: 'Stockage utilisé', value: '2.7 GB', icon: 'bx bx-data', color: 'tertiary' },
    { id: 4, title: 'Activités', value: 1458, icon: 'bx bx-bar-chart-alt-2', color: 'warning' }
  ];

  // Données d'activités récentes fictives
  const recentActivities = [
    { id: 1, user: 'John Doe', action: 'a créé un document', document: 'Rapport annuel 2024', time: '2h' },
    { id: 2, user: 'Alice Smith', action: 'a modifié', document: 'Présentation client', time: '5h' },
    { id: 3, user: 'Robert Johnson', action: 'a partagé', document: 'Données financières Q1', time: '12h' },
    { id: 4, user: 'Emma Wilson', action: 'a supprimé', document: 'Ancien brouillon', time: '1j' },
    { id: 5, user: 'Michael Brown', action: 'a commenté sur', document: 'Plan de projet', time: '2j' }
  ];

  // Données de documents récents fictives
  const recentDocuments = [
    { id: 1, title: 'Rapport annuel 2024', modified: '2h', type: 'document', views: 24 },
    { id: 2, title: 'Présentation client', modified: '5h', type: 'presentation', views: 15 },
    { id: 3, title: 'Données financières Q1', modified: '12h', type: 'spreadsheet', views: 8 },
    { id: 4, title: 'Plan de projet', modified: '1j', type: 'document', views: 32 }
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

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Tableau de bord</h1>
        <div className="page-actions">
          <Button
            type="primary"
            icon="bx bx-plus"
          >
            Nouveau document
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
            actions={<Button type="text" icon="bx bx-dots-horizontal-rounded" />}
          >
            <div className="recent-documents">
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
                    <Button type="text" icon="bx bx-edit" />
                    <Button type="text" icon="bx bx-share-alt" />
                    <Button type="text" icon="bx bx-dots-vertical-rounded" />
                  </div>
                </div>
              ))}
            </div>
            <div className="view-all-link">
              <Button type="text">Voir tous les documents</Button>
            </div>
          </Card>
        </div>
        
        <div className="dashboard-sidebar">
          <Card
            title="Activité récente"
            actions={<Button type="text" icon="bx bx-refresh" />}
          >
            <div className="activity-list">
              {recentActivities.map(activity => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-user">
                    <div className="user-avatar-initials role-user">
                      {activity.user.substring(0, 2)}
                    </div>
                  </div>
                  <div className="activity-content">
                    <p>
                      <span className="activity-user-name">{activity.user}</span>
                      <span className="activity-action"> {activity.action} </span>
                      <span className="activity-document">{activity.document}</span>
                    </p>
                    <span className="activity-time">{activity.time}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="view-all-link">
              <Button type="text">Voir toute l'activité</Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 
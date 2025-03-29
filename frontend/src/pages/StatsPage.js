import React, { useState, useRef, useEffect, useContext } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';
import { useAppContext } from '../context/AppContext';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const StatsPage = () => {
  const appContext = useAppContext();
  const { darkMode } = appContext;
  const [timeRange, setTimeRange] = useState('month');
  const [activeTab, setActiveTab] = useState('overview');
  const [chartFilters, setChartFilters] = useState({
    overview: {
      activityChart: '7 jours',
      documentChart: 'Nombre'
    },
    documents: {
      documentTypeChart: 'Nombre',
      evolutionChart: '7 jours'
    },
    users: {
      roleChart: 'Nombre',
      activityChart: '7 jours'
    },
    activity: {
      dailyChart: '7 jours',
      typeChart: 'Nombre'
    }
  });
  const [showDateMenu, setShowDateMenu] = useState(false);
  const dateMenuRef = useRef(null);
  
  // Données fictives pour les statistiques
  const stats = {
    summary: {
      totalDocuments: 357,
      newDocuments: 48,
      activeUsers: 12,
      archivedDocuments: 26,
      storageFree: '1.7 GB',
      storageUsed: '8.3 GB'
    },
    activityByDay: [
      { date: '01/03/2024', uploads: 5, downloads: 12, views: 28 },
      { date: '02/03/2024', uploads: 3, downloads: 8, views: 22 },
      { date: '03/03/2024', uploads: 7, downloads: 15, views: 35 },
      { date: '04/03/2024', uploads: 4, downloads: 10, views: 20 },
      { date: '05/03/2024', uploads: 6, downloads: 18, views: 31 },
      { date: '06/03/2024', uploads: 2, downloads: 9, views: 25 },
      { date: '07/03/2024', uploads: 8, downloads: 14, views: 38 }
    ],
    documentsByType: [
      { type: 'PDF', count: 178, size: '4.2 GB' },
      { type: 'DOCX', count: 85, size: '1.5 GB' },
      { type: 'XLSX', count: 67, size: '1.8 GB' },
      { type: 'PPT', count: 25, size: '0.8 GB' },
      { type: 'Autres', count: 2, size: '0.1 GB' }
    ],
    mostActiveUsers: [
      { id: 1, name: 'Jean Dupont', role: 'Admin', uploads: 32, downloads: 47, views: 124 },
      { id: 2, name: 'Marie Martin', role: 'Utilisateur', uploads: 28, downloads: 39, views: 98 },
      { id: 3, name: 'Thomas Bernard', role: 'Utilisateur', uploads: 22, downloads: 35, views: 87 },
      { id: 4, name: 'Sophie Dubois', role: 'Éditeur', uploads: 18, downloads: 29, views: 76 },
      { id: 5, name: 'Pierre Leroy', role: 'Éditeur', uploads: 15, downloads: 25, views: 62 }
    ],
    recentActivity: [
      { id: 1, user: 'Marie Martin', action: 'a téléversé', document: 'Rapport Q1 2024.pdf', time: 'Il y a 35 minutes' },
      { id: 2, user: 'Jean Dupont', action: 'a modifié', document: 'Budget prévisionnel.xlsx', time: 'Il y a 2 heures' },
      { id: 3, user: 'Sophie Dubois', action: 'a partagé', document: 'Présentation client.pptx', time: 'Il y a 3 heures' },
      { id: 4, user: 'Thomas Bernard', action: 'a commenté', document: 'Contrat de service.docx', time: 'Hier à 16:45' },
      { id: 5, user: 'Pierre Leroy', action: 'a archivé', document: 'Ancien rapport.pdf', time: 'Hier à 11:20' }
    ]
  };

  // Calcul de différentes métriques
  const totalActivity = stats.activityByDay.reduce(
    (sum, day) => sum + day.uploads + day.downloads + day.views, 
    0
  );
  
  const totalStorage = stats.documentsByType.reduce(
    (sum, type) => sum + parseFloat(type.size.replace(' GB', '')), 
    0
  ).toFixed(1);

  const usedStoragePercentage = (parseFloat(stats.summary.storageUsed) / (parseFloat(stats.summary.storageUsed) + parseFloat(stats.summary.storageFree)) * 100).toFixed(0);
  
  // Fonction pour obtenir le pourcentage d'un type de document
  const getPercentage = (count) => {
    return ((count / stats.summary.totalDocuments) * 100).toFixed(1);
  };

  // Fonction pour définir la plage de temps
  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
    // Dans une application réelle, vous récupéreriez des données différentes en fonction de la plage
  };

  // Fonction pour gérer les changements de filtre des graphiques
  const handleChartFilterChange = (tab, chart, value) => {
    setChartFilters(prev => ({
      ...prev,
      [tab]: {
        ...prev[tab],
        [chart]: value
      }
    }));
  };

  // Modification de la fonction getFilteredData pour gérer correctement les dates
  const getFilteredData = (data, range) => {
    const now = new Date();
    const ranges = {
      '7 jours': 7,
      '30 jours': 30,
      'Année': 365
    };
    const days = ranges[range] || 7;
    
    // Si les données sont déjà filtrées par date, on les retourne telles quelles
    if (data.length <= days) {
      return data;
    }
    
    // Sinon, on prend les derniers jours
    return data.slice(-days);
  };

  // Ajout d'une fonction pour formater les tailles
  const formatSize = (size) => {
    const numSize = parseFloat(size.replace(' GB', ''));
    return numSize.toFixed(1);
  };

  // Configuration des graphiques
  const textColor = darkMode ? '#e6e6e6' : '#495057';
  const gridColor = darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
  const backgroundColor = darkMode ? '#2a2d3e' : 'white';

  const activityChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: textColor
        }
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: darkMode ? '#323548' : 'rgba(255, 255, 255, 0.9)',
        titleColor: darkMode ? '#e6e6e6' : '#212529',
        bodyColor: darkMode ? '#b0b0b0' : '#495057',
        borderColor: darkMode ? '#444' : '#e9ecef',
        borderWidth: 1
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          color: textColor
        },
        grid: {
          color: gridColor
        }
      },
      x: {
        ticks: {
          color: textColor
        },
        grid: {
          color: gridColor
        }
      }
    }
  };

  const documentTypeChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: textColor
        }
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: darkMode ? '#323548' : 'rgba(255, 255, 255, 0.9)',
        titleColor: darkMode ? '#e6e6e6' : '#212529',
        bodyColor: darkMode ? '#b0b0b0' : '#495057',
        borderColor: darkMode ? '#444' : '#e9ecef',
        borderWidth: 1
      }
    }
  };

  const userActivityChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: textColor
        }
      },
      title: {
        display: false
      },
      tooltip: {
        backgroundColor: darkMode ? '#323548' : 'rgba(255, 255, 255, 0.9)',
        titleColor: darkMode ? '#e6e6e6' : '#212529',
        bodyColor: darkMode ? '#b0b0b0' : '#495057',
        borderColor: darkMode ? '#444' : '#e9ecef',
        borderWidth: 1
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          color: textColor
        },
        grid: {
          color: gridColor
        }
      },
      x: {
        ticks: {
          color: textColor
        },
        grid: {
          color: gridColor
        }
      }
    }
  };

  // Fonction pour gérer le clic en dehors du menu déroulant
  const handleClickOutside = (event) => {
    if (dateMenuRef.current && !dateMenuRef.current.contains(event.target)) {
      setShowDateMenu(false);
    }
  };

  // Ajout de l'écouteur d'événements pour le clic en dehors
  React.useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Fonction pour exporter les données en CSV
  const exportToCSV = () => {
    let csvContent = '';
    const date = new Date().toISOString().split('T')[0];
    
    // Fonction pour créer un en-tête de section
    const createSectionHeader = (title) => {
      return `\n${title}\n${'-'.repeat(title.length)}\n`;
    };

    // Fonction pour formater les données
    const formatData = (data) => {
      return data.map(row => row.map(cell => `"${cell}"`).join(','));
    };

    // Données de résumé
    csvContent += createSectionHeader('Résumé des statistiques');
    csvContent += 'Métrique,Valeur\n';
    csvContent += formatData([
      ['Documents totaux', stats.summary.totalDocuments],
      ['Nouveaux documents', stats.summary.newDocuments],
      ['Utilisateurs actifs', stats.summary.activeUsers],
      ['Documents archivés', stats.summary.archivedDocuments],
      ['Stockage libre', stats.summary.storageFree],
      ['Stockage utilisé', stats.summary.storageUsed],
      ['Stockage total', `${totalStorage} GB`],
      ['Pourcentage d\'utilisation', `${usedStoragePercentage}%`]
    ]).join('\n');

    // Données des documents par type
    csvContent += createSectionHeader('Documents par type');
    csvContent += 'Type,Nombre,Taille\n';
    csvContent += formatData(
      stats.documentsByType.map(doc => [
        doc.type,
        doc.count,
        doc.size
      ])
    ).join('\n');

    // Données d'activité quotidienne
    csvContent += createSectionHeader('Activité quotidienne');
    csvContent += 'Date,Téléversements,Téléchargements,Vues\n';
    csvContent += formatData(
      stats.activityByDay.map(day => [
        day.date,
        day.uploads,
        day.downloads,
        day.views
      ])
    ).join('\n');

    // Données des utilisateurs actifs
    csvContent += createSectionHeader('Utilisateurs les plus actifs');
    csvContent += 'Nom,Rôle,Téléversements,Téléchargements,Consultations,Total\n';
    csvContent += formatData(
      stats.mostActiveUsers.map(user => [
        user.name,
        user.role,
        user.uploads,
        user.downloads,
        user.views,
        user.uploads + user.downloads + user.views
      ])
    ).join('\n');

    // Données des activités récentes
    csvContent += createSectionHeader('Journal d\'activité');
    csvContent += 'Utilisateur,Action,Document,Date\n';
    csvContent += formatData(
      stats.recentActivity.map(activity => [
        activity.user,
        activity.action,
        activity.document,
        activity.time
      ])
    ).join('\n');

    // Statistiques détaillées
    csvContent += createSectionHeader('Statistiques détaillées');
    
    // Pourcentages des types de documents
    csvContent += '\nPourcentages des types de documents\n';
    csvContent += formatData(
      stats.documentsByType.map(doc => [
        doc.type,
        `${getPercentage(doc.count)}%`
      ])
    ).join('\n');

    // Créer et télécharger le fichier
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `statistiques_completes_${date}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Pour le graphique d'activité
  const getActivityChartData = (filteredData) => {
    // Couleurs adaptées au mode sombre ou clair
    const uploadColor = darkMode ? 'rgba(91, 123, 240, 0.8)' : 'rgba(105, 51, 255, 0.8)';
    const downloadColor = darkMode ? 'rgba(239, 83, 80, 0.8)' : 'rgba(255, 99, 132, 0.8)';
    const viewColor = darkMode ? 'rgba(102, 187, 106, 0.8)' : 'rgba(75, 192, 192, 0.8)';
    
    return {
      labels: filteredData.map(day => day.date),
      datasets: [
        {
          label: 'Téléversements',
          data: filteredData.map(day => day.uploads),
          backgroundColor: uploadColor,
          borderColor: uploadColor,
          tension: 0.3
        },
        {
          label: 'Téléchargements',
          data: filteredData.map(day => day.downloads),
          backgroundColor: downloadColor,
          borderColor: downloadColor,
          tension: 0.3
        },
        {
          label: 'Vues',
          data: filteredData.map(day => day.views),
          backgroundColor: viewColor,
          borderColor: viewColor,
          tension: 0.3
        }
      ]
    };
  };

  // Pour le graphique de types de documents
  const getDocumentTypeChartData = (documentsByType, filterType) => {
    // Couleurs adaptées au mode sombre
    const bgColors = darkMode 
      ? ['rgba(91, 123, 240, 0.8)', 'rgba(239, 83, 80, 0.8)', 'rgba(102, 187, 106, 0.8)', 'rgba(255, 202, 40, 0.8)', 'rgba(66, 165, 245, 0.8)']
      : ['rgba(105, 51, 255, 0.8)', 'rgba(255, 99, 132, 0.8)', 'rgba(75, 192, 192, 0.8)', 'rgba(255, 206, 86, 0.8)', 'rgba(54, 162, 235, 0.8)'];
    
    return {
      labels: documentsByType.map(type => type.type),
      datasets: [
        {
          data: filterType === 'Nombre' 
            ? documentsByType.map(type => type.count)
            : documentsByType.map(type => parseFloat(type.size.replace(' GB', ''))),
          backgroundColor: bgColors,
          borderColor: darkMode ? 'rgba(42, 45, 62, 1)' : 'white',
          borderWidth: 2
        }
      ]
    };
  };
  
  // Effet pour mettre à jour les graphiques quand le mode sombre change
  useEffect(() => {
    // Forcer une mise à jour des graphiques quand le thème change
    const charts = document.querySelectorAll('canvas');
    charts.forEach(chart => {
      if (chart.chart) {
        chart.chart.update();
      }
    });
  }, [darkMode]);

  return (
    <div className="statistics-page">
      <div className="statistics-header">
        <div>
          <h1>Statistiques</h1>
          <p className="statistics-subtitle">Analyse des activités et performances de votre espace documentaire</p>
        </div>
        <div className="statistics-actions">
          <div className="date-filter" ref={dateMenuRef}>
            <div 
              className="date-filter-button"
              onClick={() => setShowDateMenu(!showDateMenu)}
            >
              <i className='bx bx-calendar'></i>
              <span>{timeRange === 'week' ? 'Cette semaine' : timeRange === 'month' ? 'Ce mois-ci' : 'Cette année'}</span>
              <i className='bx bx-chevron-down'></i>
            </div>
            {showDateMenu && (
              <div className="date-filter-menu">
                <div 
                  className={`date-filter-option ${timeRange === 'week' ? 'active' : ''}`}
                  onClick={() => {
                    handleTimeRangeChange('week');
                    setShowDateMenu(false);
                  }}
                >
                  Cette semaine
                </div>
                <div 
                  className={`date-filter-option ${timeRange === 'month' ? 'active' : ''}`}
                  onClick={() => {
                    handleTimeRangeChange('month');
                    setShowDateMenu(false);
                  }}
                >
                  Ce mois-ci
                </div>
                <div 
                  className={`date-filter-option ${timeRange === 'year' ? 'active' : ''}`}
                  onClick={() => {
                    handleTimeRangeChange('year');
                    setShowDateMenu(false);
                  }}
                >
                  Cette année
                </div>
              </div>
            )}
          </div>
          <Button type="secondary" icon="bx bx-download" onClick={exportToCSV}>
            Exporter
          </Button>
        </div>
      </div>

      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Vue d'ensemble
        </div>
        <div 
          className={`tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          Documents
        </div>
        <div 
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Utilisateurs
        </div>
        <div 
          className={`tab ${activeTab === 'activity' ? 'active' : ''}`}
          onClick={() => setActiveTab('activity')}
        >
          Activité
        </div>
      </div>

      {activeTab === 'overview' && (
        <>
          <div className="stats-overview">
            <div className="stat-overview-card primary">
              <div className="stat-overview-value">{stats.summary.totalDocuments}</div>
              <div className="stat-overview-label">Documents totaux</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill primary" style={{ width: '78%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +{stats.summary.newDocuments}
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card success">
              <div className="stat-overview-value">{stats.summary.activeUsers}</div>
              <div className="stat-overview-label">Utilisateurs actifs</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill success" style={{ width: '65%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +3
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card info">
              <div className="stat-overview-value">{totalActivity}</div>
              <div className="stat-overview-label">Activités totales</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill info" style={{ width: '82%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +12%
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card warning">
              <div className="stat-overview-value">{stats.summary.storageUsed}</div>
              <div className="stat-overview-label">Stockage utilisé</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill warning" style={{ width: `${usedStoragePercentage}%` }}></div>
                </div>
                <div className="stat-progress-text">{usedStoragePercentage}% de 10 GB</div>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Activité quotidienne</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.overview.activityChart === '7 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('overview', 'activityChart', '7 jours')}
                  >
                    7 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.overview.activityChart === '30 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('overview', 'activityChart', '30 jours')}
                  >
                    30 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.overview.activityChart === 'Année' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('overview', 'activityChart', 'Année')}
                  >
                    Année
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Line 
                  data={getActivityChartData(getFilteredData(stats.activityByDay, chartFilters.overview.activityChart))}
                  options={activityChartOptions}
                />
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Documents par type</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.overview.documentChart === 'Nombre' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('overview', 'documentChart', 'Nombre')}
                  >
                    Nombre
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.overview.documentChart === 'Taille' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('overview', 'documentChart', 'Taille')}
                  >
                    Taille
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Doughnut 
                  data={getDocumentTypeChartData(
                    stats.documentsByType,
                    chartFilters.overview.documentChart
                  )}
                  options={documentTypeChartOptions}
                />
              </div>
            </div>
          </div>

          <div className="detailed-stats-section">
            <h2>Statistiques détaillées</h2>
            <div className="activity-breakdown">
              <div className="activity-stat-card">
                <div className="activity-stat-header">
                  <div className="activity-stat-icon primary">
                    <i className='bx bx-file'></i>
                  </div>
                  <h3 className="activity-stat-title">Documents par type</h3>
                </div>
                <div className="activity-stat-items">
                  {stats.documentsByType.map((type, index) => (
                    <div key={index} className="activity-item-row">
                      <div className="activity-item-label">{type.type}</div>
                      <div className="activity-item-value">{type.count} ({getPercentage(type.count)}%)</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="activity-stat-card">
                <div className="activity-stat-header">
                  <div className="activity-stat-icon secondary">
                    <i className='bx bx-bar-chart-alt-2'></i>
                  </div>
                  <h3 className="activity-stat-title">Activités récentes</h3>
                </div>
                <div className="activity-stat-items">
                  <div className="activity-item-row">
                    <div className="activity-item-label">Téléversements</div>
                    <div className="activity-item-value">35</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Téléchargements</div>
                    <div className="activity-item-value">86</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Consultations</div>
                    <div className="activity-item-value">199</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Partages</div>
                    <div className="activity-item-value">42</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Modifications</div>
                    <div className="activity-item-value">28</div>
                  </div>
                </div>
              </div>

              <div className="activity-stat-card">
                <div className="activity-stat-header">
                  <div className="activity-stat-icon tertiary">
                    <i className='bx bx-user'></i>
                  </div>
                  <h3 className="activity-stat-title">Utilisateurs par rôle</h3>
                </div>
                <div className="activity-stat-items">
                  <div className="activity-item-row">
                    <div className="activity-item-label">Administrateurs</div>
                    <div className="activity-item-value">3</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Éditeurs</div>
                    <div className="activity-item-value">7</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Utilisateurs</div>
                    <div className="activity-item-value">25</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Invités</div>
                    <div className="activity-item-value">14</div>
                  </div>
                  <div className="activity-item-row">
                    <div className="activity-item-label">Total</div>
                    <div className="activity-item-value">49</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="stats-table-section">
            <div className="stats-table-header">
              <h2 className="stats-table-title">Utilisateurs les plus actifs</h2>
              <div className="stats-table-filters">
                <Button type="text" icon="bx bx-filter-alt">Filtrer</Button>
                <Button type="text" icon="bx bx-export">Exporter</Button>
              </div>
            </div>
            <div className="stats-table-container">
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Rôle</th>
                    <th>Téléversements</th>
                    <th>Téléchargements</th>
                    <th>Consultations</th>
                    <th>Total</th>
                    <th>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.mostActiveUsers.map(user => (
                    <tr key={user.id}>
                      <td>{user.name}</td>
                      <td>{user.role}</td>
                      <td>{user.uploads}</td>
                      <td>{user.downloads}</td>
                      <td>{user.views}</td>
                      <td>{user.uploads + user.downloads + user.views}</td>
                      <td>
                        <span className="stats-badge primary">Actif</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="stats-pagination">
              <div className="stats-page-info">Affichage de 1 à 5 sur 12 utilisateurs</div>
              <div className="stats-page-controls">
                <div className="stats-page-button" disabled><i className='bx bx-chevron-left'></i></div>
                <div className="stats-page-button active">1</div>
                <div className="stats-page-button">2</div>
                <div className="stats-page-button">3</div>
                <div className="stats-page-button"><i className='bx bx-chevron-right'></i></div>
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'documents' && (
        <>
          <div className="stats-overview">
            <div className="stat-overview-card primary">
              <div className="stat-overview-value">{stats.summary.totalDocuments}</div>
              <div className="stat-overview-label">Documents totaux</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill primary" style={{ width: '78%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +{stats.summary.newDocuments}
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card success">
              <div className="stat-overview-value">{stats.summary.archivedDocuments}</div>
              <div className="stat-overview-label">Documents archivés</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill success" style={{ width: '15%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +5
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card info">
              <div className="stat-overview-value">{totalStorage} GB</div>
              <div className="stat-overview-label">Stockage total</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill info" style={{ width: `${usedStoragePercentage}%` }}></div>
                </div>
                <div className="stat-progress-text">{usedStoragePercentage}% utilisé</div>
              </div>
            </div>

            <div className="stat-overview-card warning">
              <div className="stat-overview-value">12</div>
              <div className="stat-overview-label">Documents partagés</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill warning" style={{ width: '25%' }}></div>
                </div>
                <div className="stat-progress-text">3.4% des documents</div>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Documents par type</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.documents.documentTypeChart === 'Nombre' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('documents', 'documentTypeChart', 'Nombre')}
                  >
                    Nombre
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.documents.documentTypeChart === 'Taille' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('documents', 'documentTypeChart', 'Taille')}
                  >
                    Taille
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Bar
                  data={{
                    labels: stats.documentsByType.map(doc => doc.type),
                    datasets: [
                      {
                        label: chartFilters.documents.documentTypeChart === 'Nombre' ? 'Nombre de documents' : 'Taille (GB)',
                        data: stats.documentsByType.map(doc => 
                          chartFilters.documents.documentTypeChart === 'Nombre' 
                            ? doc.count 
                            : parseFloat(doc.size.replace(' GB', ''))
                        ),
                        backgroundColor: 'rgba(105, 51, 255, 0.8)'
                      }
                    ]
                  }}
                  options={documentTypeChartOptions}
                />
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Évolution des documents</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.documents.evolutionChart === '7 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('documents', 'evolutionChart', '7 jours')}
                  >
                    7 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.documents.evolutionChart === '30 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('documents', 'evolutionChart', '30 jours')}
                  >
                    30 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.documents.evolutionChart === 'Année' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('documents', 'evolutionChart', 'Année')}
                  >
                    Année
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Line
                  data={{
                    labels: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.date),
                    datasets: [
                      {
                        label: 'Téléversements',
                        data: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.uploads),
                        borderColor: 'rgb(105, 51, 255)',
                        backgroundColor: 'rgba(105, 51, 255, 0.5)',
                        tension: 0.4
                      },
                      {
                        label: 'Téléchargements',
                        data: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.downloads),
                        borderColor: 'rgb(52, 152, 219)',
                        backgroundColor: 'rgba(52, 152, 219, 0.5)',
                        tension: 0.4
                      },
                      {
                        label: 'Vues',
                        data: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.views),
                        borderColor: 'rgb(46, 204, 113)',
                        backgroundColor: 'rgba(46, 204, 113, 0.5)',
                        tension: 0.4
                      }
                    ]
                  }}
                  options={activityChartOptions}
                />
              </div>
            </div>
          </div>

          <div className="stats-table-section">
            <div className="stats-table-header">
              <h2 className="stats-table-title">Liste des documents</h2>
              <div className="stats-table-filters">
                <Button type="text" icon="bx bx-filter-alt">Filtrer</Button>
                <Button type="text" icon="bx bx-export">Exporter</Button>
              </div>
            </div>
            <div className="stats-table-container">
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Type</th>
                    <th>Taille</th>
                    <th>Date de création</th>
                    <th>Dernière modification</th>
                    <th>Statut</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.documentsByType.map((doc, index) => (
                    <tr key={index}>
                      <td>Document {index + 1}</td>
                      <td>{doc.type}</td>
                      <td>{doc.size}</td>
                      <td>01/03/2024</td>
                      <td>07/03/2024</td>
                      <td>
                        <span className="stats-badge primary">Actif</span>
                      </td>
                      <td>
                        <div className="actions-cell">
                          <Button type="text" icon="bx bx-show"></Button>
                          <Button type="text" icon="bx bx-download"></Button>
                          <Button type="text" icon="bx bx-trash"></Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="stats-pagination">
              <div className="stats-page-info">Affichage de 1 à 5 sur {stats.summary.totalDocuments} documents</div>
              <div className="stats-page-controls">
                <div className="stats-page-button" disabled><i className='bx bx-chevron-left'></i></div>
                <div className="stats-page-button active">1</div>
                <div className="stats-page-button">2</div>
                <div className="stats-page-button">3</div>
                <div className="stats-page-button"><i className='bx bx-chevron-right'></i></div>
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'users' && (
        <>
          <div className="stats-overview">
            <div className="stat-overview-card primary">
              <div className="stat-overview-value">{stats.mostActiveUsers.length}</div>
              <div className="stat-overview-label">Utilisateurs totaux</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill primary" style={{ width: '75%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +{stats.summary.activeUsers}
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card success">
              <div className="stat-overview-value">{stats.summary.activeUsers}</div>
              <div className="stat-overview-label">Utilisateurs actifs</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill success" style={{ width: '65%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +{stats.mostActiveUsers.filter(user => user.role === 'Utilisateur').length}
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card info">
              <div className="stat-overview-value">{stats.mostActiveUsers.filter(user => user.role === 'Admin').length}</div>
              <div className="stat-overview-label">Administrateurs</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill info" style={{ width: '25%' }}></div>
                </div>
                <div className="stat-progress-text">
                  {((stats.mostActiveUsers.filter(user => user.role === 'Admin').length / stats.mostActiveUsers.length) * 100).toFixed(0)}% des utilisateurs
                </div>
              </div>
            </div>

            <div className="stat-overview-card warning">
              <div className="stat-overview-value">{stats.mostActiveUsers.filter(user => user.role === 'Éditeur').length}</div>
              <div className="stat-overview-label">Éditeurs</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill warning" style={{ width: '35%' }}></div>
                </div>
                <div className="stat-progress-text">
                  {((stats.mostActiveUsers.filter(user => user.role === 'Éditeur').length / stats.mostActiveUsers.length) * 100).toFixed(0)}% des utilisateurs
                </div>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Utilisateurs par rôle</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.users.roleChart === 'Nombre' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('users', 'roleChart', 'Nombre')}
                  >
                    Nombre
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.users.roleChart === 'Activité' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('users', 'roleChart', 'Activité')}
                  >
                    Activité
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Doughnut
                  data={{
                    labels: ['Admin', 'Éditeur', 'Utilisateur'],
                    datasets: [
                      {
                        data: chartFilters.users.roleChart === 'Nombre'
                          ? [
                              stats.mostActiveUsers.filter(user => user.role === 'Admin').length,
                              stats.mostActiveUsers.filter(user => user.role === 'Éditeur').length,
                              stats.mostActiveUsers.filter(user => user.role === 'Utilisateur').length
                            ]
                          : [
                              stats.mostActiveUsers.filter(user => user.role === 'Admin').reduce((sum, user) => sum + user.uploads + user.downloads + user.views, 0),
                              stats.mostActiveUsers.filter(user => user.role === 'Éditeur').reduce((sum, user) => sum + user.uploads + user.downloads + user.views, 0),
                              stats.mostActiveUsers.filter(user => user.role === 'Utilisateur').reduce((sum, user) => sum + user.uploads + user.downloads + user.views, 0)
                            ],
                        backgroundColor: [
                          'rgba(105, 51, 255, 0.8)',
                          'rgba(52, 152, 219, 0.8)',
                          'rgba(46, 204, 113, 0.8)'
                        ]
                      }
                    ]
                  }}
                  options={{
                    ...documentTypeChartOptions,
                    plugins: {
                      ...documentTypeChartOptions.plugins,
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const value = context.raw;
                            return chartFilters.users.roleChart === 'Nombre'
                              ? `${context.label}: ${value} utilisateurs`
                              : `${context.label}: ${value} actions`;
                          }
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Activité des utilisateurs</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.users.activityChart === '7 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('users', 'activityChart', '7 jours')}
                  >
                    7 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.users.activityChart === '30 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('users', 'activityChart', '30 jours')}
                  >
                    30 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.users.activityChart === 'Année' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('users', 'activityChart', 'Année')}
                  >
                    Année
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Bar
                  data={{
                    labels: stats.mostActiveUsers.map(user => user.name),
                    datasets: [
                      {
                        label: 'Téléversements',
                        data: stats.mostActiveUsers.map(user => user.uploads),
                        backgroundColor: 'rgba(105, 51, 255, 0.8)'
                      },
                      {
                        label: 'Téléchargements',
                        data: stats.mostActiveUsers.map(user => user.downloads),
                        backgroundColor: 'rgba(52, 152, 219, 0.8)'
                      },
                      {
                        label: 'Vues',
                        data: stats.mostActiveUsers.map(user => user.views),
                        backgroundColor: 'rgba(46, 204, 113, 0.8)'
                      }
                    ]
                  }}
                  options={userActivityChartOptions}
                />
              </div>
            </div>
          </div>

          <div className="stats-table-section">
            <div className="stats-table-header">
              <h2 className="stats-table-title">Liste des utilisateurs</h2>
              <div className="stats-table-filters">
                <Button type="text" icon="bx bx-filter-alt">Filtrer</Button>
                <Button type="text" icon="bx bx-export">Exporter</Button>
              </div>
            </div>
            <div className="stats-table-container">
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Rôle</th>
                    <th>Statut</th>
                    <th>Dernière connexion</th>
                    <th>Documents</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.mostActiveUsers.map(user => (
                    <tr key={user.id}>
                      <td>{user.name}</td>
                      <td>{user.role}</td>
                      <td>
                        <span className="stats-badge primary">Actif</span>
                      </td>
                      <td>Il y a 2 heures</td>
                      <td>{user.uploads + user.downloads + user.views}</td>
                      <td>
                        <div className="actions-cell">
                          <Button type="text" icon="bx bx-edit"></Button>
                          <Button type="text" icon="bx bx-trash"></Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="stats-pagination">
              <div className="stats-page-info">
                Affichage de 1 à {stats.mostActiveUsers.length} sur {stats.mostActiveUsers.length} utilisateurs
              </div>
              <div className="stats-page-controls">
                <div className="stats-page-button" disabled><i className='bx bx-chevron-left'></i></div>
                <div className="stats-page-button active">1</div>
                <div className="stats-page-button">2</div>
                <div className="stats-page-button">3</div>
                <div className="stats-page-button"><i className='bx bx-chevron-right'></i></div>
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'activity' && (
        <>
          <div className="stats-overview">
            <div className="stat-overview-card primary">
              <div className="stat-overview-value">{totalActivity}</div>
              <div className="stat-overview-label">Activités totales</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill primary" style={{ width: '82%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +12%
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card success">
              <div className="stat-overview-value">35</div>
              <div className="stat-overview-label">Téléversements</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill success" style={{ width: '45%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +8
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card info">
              <div className="stat-overview-value">86</div>
              <div className="stat-overview-label">Téléchargements</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill info" style={{ width: '65%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +15
                  </span>
                </div>
              </div>
            </div>

            <div className="stat-overview-card warning">
              <div className="stat-overview-value">42</div>
              <div className="stat-overview-label">Partages</div>
              <div className="stat-progress">
                <div className="stat-progress-bar">
                  <div className="stat-progress-fill warning" style={{ width: '35%' }}></div>
                </div>
                <div className="stat-progress-text">
                  <span className="stat-trend-indicator up">
                    <i className='bx bx-up-arrow-alt'></i>
                    +5
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Activité quotidienne</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.activity.dailyChart === '7 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('activity', 'dailyChart', '7 jours')}
                  >
                    7 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.activity.dailyChart === '30 jours' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('activity', 'dailyChart', '30 jours')}
                  >
                    30 jours
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.activity.dailyChart === 'Année' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('activity', 'dailyChart', 'Année')}
                  >
                    Année
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Line
                  data={{
                    labels: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.date),
                    datasets: [
                      {
                        label: 'Téléversements',
                        data: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.uploads),
                        borderColor: 'rgb(105, 51, 255)',
                        backgroundColor: 'rgba(105, 51, 255, 0.5)',
                        tension: 0.4
                      },
                      {
                        label: 'Téléchargements',
                        data: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.downloads),
                        borderColor: 'rgb(52, 152, 219)',
                        backgroundColor: 'rgba(52, 152, 219, 0.5)',
                        tension: 0.4
                      },
                      {
                        label: 'Vues',
                        data: getFilteredData(stats.activityByDay, chartFilters.activity.dailyChart).map(day => day.views),
                        borderColor: 'rgb(46, 204, 113)',
                        backgroundColor: 'rgba(46, 204, 113, 0.5)',
                        tension: 0.4
                      }
                    ]
                  }}
                  options={activityChartOptions}
                />
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h2 className="chart-title">Types d'activité</h2>
                <div className="chart-options">
                  <div 
                    className={`chart-option ${chartFilters.activity.typeChart === 'Nombre' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('activity', 'typeChart', 'Nombre')}
                  >
                    Nombre
                  </div>
                  <div 
                    className={`chart-option ${chartFilters.activity.typeChart === 'Pourcentage' ? 'active' : ''}`}
                    onClick={() => handleChartFilterChange('activity', 'typeChart', 'Pourcentage')}
                  >
                    Pourcentage
                  </div>
                </div>
              </div>
              <div className="chart-body">
                <Doughnut
                  data={{
                    labels: ['Téléversements', 'Téléchargements', 'Vues'],
                    datasets: [
                      {
                        data: chartFilters.activity.typeChart === 'Nombre'
                          ? [
                              stats.activityByDay.reduce((sum, day) => sum + day.uploads, 0),
                              stats.activityByDay.reduce((sum, day) => sum + day.downloads, 0),
                              stats.activityByDay.reduce((sum, day) => sum + day.views, 0)
                            ]
                          : [
                              (stats.activityByDay.reduce((sum, day) => sum + day.uploads, 0) / totalActivity * 100).toFixed(1),
                              (stats.activityByDay.reduce((sum, day) => sum + day.downloads, 0) / totalActivity * 100).toFixed(1),
                              (stats.activityByDay.reduce((sum, day) => sum + day.views, 0) / totalActivity * 100).toFixed(1)
                            ],
                        backgroundColor: [
                          'rgba(105, 51, 255, 0.8)',
                          'rgba(52, 152, 219, 0.8)',
                          'rgba(46, 204, 113, 0.8)'
                        ]
                      }
                    ]
                  }}
                  options={documentTypeChartOptions}
                />
              </div>
            </div>
          </div>

          <div className="stats-table-section">
            <div className="stats-table-header">
              <h2 className="stats-table-title">Journal d'activité</h2>
              <div className="stats-table-filters">
                <Button type="text" icon="bx bx-filter-alt">Filtrer</Button>
                <Button type="text" icon="bx bx-export">Exporter</Button>
              </div>
            </div>
            <div className="stats-table-container">
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Action</th>
                    <th>Document</th>
                    <th>Date</th>
                    <th>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recentActivity.map(activity => (
                    <tr key={activity.id}>
                      <td>{activity.user}</td>
                      <td>{activity.action}</td>
                      <td>{activity.document}</td>
                      <td>{activity.time}</td>
                      <td>
                        <span className="stats-badge primary">Complété</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="stats-pagination">
              <div className="stats-page-info">Affichage de 1 à 5 sur 25 activités</div>
              <div className="stats-page-controls">
                <div className="stats-page-button" disabled><i className='bx bx-chevron-left'></i></div>
                <div className="stats-page-button active">1</div>
                <div className="stats-page-button">2</div>
                <div className="stats-page-button">3</div>
                <div className="stats-page-button">4</div>
                <div className="stats-page-button">5</div>
                <div className="stats-page-button"><i className='bx bx-chevron-right'></i></div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default StatsPage; 
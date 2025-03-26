import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';

const StatsPage = () => {
  const [timeRange, setTimeRange] = useState('month');
  
  // Données fictives pour les statistiques
  const stats = {
    summary: {
      totalDocuments: 357,
      newDocuments: 48,
      activeUsers: 12,
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
      { id: 1, name: 'Jean Dupont', uploads: 32, downloads: 47, views: 124 },
      { id: 2, name: 'Marie Martin', uploads: 28, downloads: 39, views: 98 },
      { id: 3, name: 'Thomas Bernard', uploads: 22, downloads: 35, views: 87 },
      { id: 4, name: 'Sophie Dubois', uploads: 18, downloads: 29, views: 76 },
      { id: 5, name: 'Pierre Leroy', uploads: 15, downloads: 25, views: 62 }
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
  
  // Fonction pour obtenir le pourcentage d'un type de document
  const getPercentage = (count) => {
    return ((count / stats.summary.totalDocuments) * 100).toFixed(1);
  };

  // Fonction pour définir la plage de temps
  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
    // Dans une application réelle, vous récupéreriez des données différentes en fonction de la plage
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Statistiques</h1>
        <div className="page-actions">
          <div className="time-range-selector">
            <Button 
              type={timeRange === 'week' ? 'primary' : 'text'}
              onClick={() => handleTimeRangeChange('week')}
            >
              Semaine
            </Button>
            <Button 
              type={timeRange === 'month' ? 'primary' : 'text'}
              onClick={() => handleTimeRangeChange('month')}
            >
              Mois
            </Button>
            <Button 
              type={timeRange === 'year' ? 'primary' : 'text'}
              onClick={() => handleTimeRangeChange('year')}
            >
              Année
            </Button>
          </div>
          <Button
            type="secondary"
            icon="bx bx-download"
          >
            Exporter
          </Button>
        </div>
      </div>

      <div className="stats-summary">
        <Card className="stat-card">
          <div className="stat-icon">
            <i className='bx bx-file-blank'></i>
          </div>
          <div className="stat-content">
            <h3>Documents totaux</h3>
            <div className="stat-value">{stats.summary.totalDocuments}</div>
            <div className="stat-change positive">+{stats.summary.newDocuments} ce mois-ci</div>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-icon">
            <i className='bx bx-user'></i>
          </div>
          <div className="stat-content">
            <h3>Utilisateurs actifs</h3>
            <div className="stat-value">{stats.summary.activeUsers}</div>
            <div className="stat-change neutral">Stable</div>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-icon">
            <i className='bx bx-bar-chart-alt-2'></i>
          </div>
          <div className="stat-content">
            <h3>Activités totales</h3>
            <div className="stat-value">{totalActivity}</div>
            <div className="stat-change positive">+12% par rapport au mois dernier</div>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-icon">
            <i className='bx bx-data'></i>
          </div>
          <div className="stat-content">
            <h3>Stockage</h3>
            <div className="stat-value">{totalStorage} GB</div>
            <div className="stat-secondary">{stats.summary.storageFree} restants</div>
          </div>
        </Card>
      </div>

      <div className="stats-charts">
        <Card className="chart-card">
          <div className="card-header">
            <h3>Activité quotidienne</h3>
            <div className="card-actions">
              <Button type="text" icon="bx bx-dots-vertical-rounded" />
            </div>
          </div>
          <div className="chart-content">
            <div className="chart-placeholder">
              {/* Dans une application réelle, vous utiliseriez une bibliothèque comme Chart.js ou Recharts */}
              <div className="chart-mock">
                {stats.activityByDay.map((day, index) => (
                  <div key={index} className="chart-bar-group">
                    <div 
                      className="chart-bar uploads" 
                      style={{ height: `${day.uploads * 5}px` }} 
                      title={`Uploads: ${day.uploads}`}
                    ></div>
                    <div 
                      className="chart-bar downloads" 
                      style={{ height: `${day.downloads * 3}px` }} 
                      title={`Downloads: ${day.downloads}`}
                    ></div>
                    <div 
                      className="chart-bar views" 
                      style={{ height: `${day.views}px` }} 
                      title={`Views: ${day.views}`}
                    ></div>
                    <div className="chart-date">{day.date.substring(0, 5)}</div>
                  </div>
                ))}
              </div>
              <div className="chart-legend">
                <div className="legend-item">
                  <div className="legend-color uploads"></div>
                  <span>Téléversements</span>
                </div>
                <div className="legend-item">
                  <div className="legend-color downloads"></div>
                  <span>Téléchargements</span>
                </div>
                <div className="legend-item">
                  <div className="legend-color views"></div>
                  <span>Consultations</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <Card className="chart-card">
          <div className="card-header">
            <h3>Documents par type</h3>
            <div className="card-actions">
              <Button type="text" icon="bx bx-dots-vertical-rounded" />
            </div>
          </div>
          <div className="chart-content">
            <div className="documents-by-type">
              {stats.documentsByType.map((type, index) => (
                <div key={index} className="type-item">
                  <div className="type-info">
                    <span className="type-name">{type.type}</span>
                    <span className="type-count">{type.count} documents</span>
                  </div>
                  <div className="type-bar-container">
                    <div 
                      className="type-bar" 
                      style={{ width: `${getPercentage(type.count)}%` }}
                    ></div>
                  </div>
                  <div className="type-percentage">{getPercentage(type.count)}%</div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      <Card className="active-users-card">
        <div className="card-header">
          <h3>Utilisateurs les plus actifs</h3>
          <div className="card-actions">
            <Button type="text" icon="bx bx-dots-vertical-rounded" />
          </div>
        </div>
        <table className="users-table">
          <thead>
            <tr>
              <th>Utilisateur</th>
              <th>Téléversements</th>
              <th>Téléchargements</th>
              <th>Consultations</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {stats.mostActiveUsers.map(user => (
              <tr key={user.id}>
                <td>{user.name}</td>
                <td>{user.uploads}</td>
                <td>{user.downloads}</td>
                <td>{user.views}</td>
                <td>{user.uploads + user.downloads + user.views}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export default StatsPage; 
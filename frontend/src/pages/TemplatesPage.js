import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import SearchBox from '../components/SearchBox';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';
import '../styles/pages.css';

const TemplatesPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  
  // Données fictives pour les modèles
  const templates = [
    { id: 1, name: 'Facture standard', category: 'finance', usage: 58, thumbnail: '/path/to/thumbnail1.jpg' },
    { id: 2, name: 'Rapport mensuel', category: 'reporting', usage: 42, thumbnail: '/path/to/thumbnail2.jpg' },
    { id: 3, name: 'Contrat de travail', category: 'legal', usage: 36, thumbnail: '/path/to/thumbnail3.jpg' },
    { id: 4, name: 'Devis commercial', category: 'finance', usage: 31, thumbnail: '/path/to/thumbnail4.jpg' },
    { id: 5, name: 'Plan de projet', category: 'planning', usage: 27, thumbnail: '/path/to/thumbnail5.jpg' },
    { id: 6, name: 'Procès-verbal', category: 'legal', usage: 24, thumbnail: '/path/to/thumbnail6.jpg' },
    { id: 7, name: 'Brief créatif', category: 'creative', usage: 19, thumbnail: '/path/to/thumbnail7.jpg' },
    { id: 8, name: 'Présentation client', category: 'marketing', usage: 16, thumbnail: '/path/to/thumbnail8.jpg' },
  ];
  
  // Filtrer les modèles
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          template.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === 'all' || template.category === activeTab;
    return matchesSearch && matchesTab;
  });
  
  // Obtenir les catégories uniques
  const categories = ['all', ...new Set(templates.map(template => template.category))];
  
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Modèles</h1>
          <p className="page-description">Utilisez nos modèles pour gagner du temps</p>
        </div>
        <div className="page-actions">
          <Button type="primary" icon="fas fa-plus">Nouveau modèle</Button>
        </div>
      </div>
      
      <Card className="filter-card">
        <div className="filter-container">
          <div className="search-container">
            <SearchBox 
              placeholder="Rechercher un modèle..." 
              value={searchTerm} 
              onChange={(e) => setSearchTerm(e.target.value)}
              icon="fas fa-search"
            />
          </div>
        </div>
      </Card>
      
      <div className="tabs">
        {categories.map(category => (
          <div 
            key={category} 
            className={`tab ${activeTab === category ? 'active' : ''}`}
            onClick={() => setActiveTab(category)}
          >
            {category === 'all' ? 'Tous' : category.charAt(0).toUpperCase() + category.slice(1)}
          </div>
        ))}
      </div>
      
      {filteredTemplates.length > 0 ? (
        <div className="templates-grid">
          {filteredTemplates.map(template => (
            <Card key={template.id} className="template-card">
              <div className="template-thumbnail">
                <div className="template-image" style={{ backgroundColor: '#e9e9e9' }}>
                  <i className="fas fa-file-alt template-icon"></i>
                </div>
                <div className="template-hover">
                  <Button type="primary" size="small">Utiliser</Button>
                </div>
              </div>
              <div className="template-info">
                <h3 className="template-name">{template.name}</h3>
                <div className="template-meta">
                  <span className="template-category">{template.category}</span>
                  <span className="template-usage">
                    <i className="fas fa-users"></i> {template.usage}
                  </span>
                </div>
                <div className="template-actions">
                  <Button type="icon" icon="fas fa-edit" tooltip="Modifier" />
                  <Button type="icon" icon="fas fa-share-alt" tooltip="Partager" />
                  <Button type="icon" icon="fas fa-trash" tooltip="Supprimer" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="no-results">
          <i className="fas fa-search"></i>
          <p>Aucun modèle trouvé</p>
        </div>
      )}
    </div>
  );
};

export default TemplatesPage; 
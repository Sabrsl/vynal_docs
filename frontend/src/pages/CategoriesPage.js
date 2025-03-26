import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';

const CategoriesPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#6933FF'
  });
  
  // Données fictives pour les catégories
  const categoriesData = [
    { id: 1, name: 'Juridique', description: 'Documents juridiques et contrats', color: '#E94435', documentsCount: 24 },
    { id: 2, name: 'Finance', description: 'Factures, devis et documents financiers', color: '#4285F4', documentsCount: 45 },
    { id: 3, name: 'Rapports', description: 'Rapports d\'activité et analyses', color: '#109D58', documentsCount: 32 },
    { id: 4, name: 'Ressources Humaines', description: 'Documents liés au personnel', color: '#FBBC04', documentsCount: 18 },
    { id: 5, name: 'Marketing', description: 'Supports marketing et communication', color: '#9C27B0', documentsCount: 27 },
    { id: 6, name: 'Projets', description: 'Documents liés aux projets en cours', color: '#00ACC1', documentsCount: 53 },
    { id: 7, name: 'Archives', description: 'Documents archivés', color: '#757575', documentsCount: 89 },
    { id: 8, name: 'Personnel', description: 'Documents personnels', color: '#FF6D00', documentsCount: 12 },
  ];

  // Fonction pour filtrer les catégories
  const filteredCategories = categoriesData.filter(category => 
    category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    category.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Gestion du formulaire
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Ici, vous pourriez ajouter la catégorie à votre état ou l'envoyer à une API
    console.log('Nouvelle catégorie :', formData);
    setFormData({ name: '', description: '', color: '#6933FF' });
    setShowForm(false);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Catégories</h1>
        <div className="page-actions">
          <Button
            type="primary"
            icon="bx bx-plus"
            onClick={() => setShowForm(true)}
          >
            Nouvelle catégorie
          </Button>
        </div>
      </div>

      {showForm && (
        <Card className="form-card">
          <div className="form-header">
            <h2>Créer une nouvelle catégorie</h2>
            <Button 
              type="text" 
              icon="bx bx-x" 
              onClick={() => setShowForm(false)} 
            />
          </div>
          <form onSubmit={handleSubmit} className="category-form">
            <div className="form-group">
              <label htmlFor="name">Nom de la catégorie</label>
              <Input 
                type="text" 
                id="name" 
                name="name" 
                value={formData.name} 
                onChange={handleChange}
                placeholder="Ex: Marketing, Finance..."
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea 
                id="description" 
                name="description" 
                value={formData.description} 
                onChange={handleChange}
                placeholder="Décrivez l'utilité de cette catégorie"
                className="form-textarea"
              />
            </div>
            <div className="form-group">
              <label htmlFor="color">Couleur</label>
              <div className="color-input-container">
                <input 
                  type="color" 
                  id="color" 
                  name="color" 
                  value={formData.color} 
                  onChange={handleChange}
                  className="color-input"
                />
                <span className="color-value">{formData.color}</span>
              </div>
            </div>
            <div className="form-actions">
              <Button type="text" onClick={() => setShowForm(false)}>Annuler</Button>
              <Button type="primary" submit>Créer</Button>
            </div>
          </form>
        </Card>
      )}

      <Card className="filter-card">
        <div className="search-container">
          <Input 
            type="search" 
            placeholder="Rechercher une catégorie..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon="bx-search"
          />
        </div>
      </Card>

      <div className="categories-grid">
        {filteredCategories.map(category => (
          <Card key={category.id} className="category-card">
            <div className="category-header">
              <div 
                className="category-color" 
                style={{ backgroundColor: category.color }}
              ></div>
              <div className="category-header-content">
                <h3>{category.name}</h3>
                <span className="document-count">{category.documentsCount} documents</span>
              </div>
              <Button type="text" icon="bx bx-dots-vertical-rounded" />
            </div>
            <div className="category-body">
              <p className="category-description">{category.description}</p>
            </div>
            <div className="category-actions">
              <Button type="text" icon="bx bx-folder-open">Voir</Button>
              <Button type="text" icon="bx bx-edit">Modifier</Button>
            </div>
          </Card>
        ))}
      </div>

      {filteredCategories.length === 0 && (
        <Card className="empty-state">
          <div className="no-results">
            <i className='bx bx-search-alt'></i>
            <p>Aucune catégorie ne correspond à votre recherche</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default CategoriesPage; 
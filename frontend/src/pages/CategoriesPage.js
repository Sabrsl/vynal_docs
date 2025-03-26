import React, { useState, useEffect } from 'react';
import './CategoriesPage.css';

// Données simulées - à remplacer par des appels API réels
const mockCategories = [
  {
    id: 1,
    name: "Documentation technique",
    description: "Documentation technique des équipements et logiciels de l'entreprise.",
    color: "#4285F4",
    documents: [
      { id: 1, name: "Manuel serveur Dell R740", type: "pdf", size: "4.2 MB", date: "12/04/2023" },
      { id: 2, name: "Guide d'administration Windows Server", type: "pdf", size: "8.7 MB", date: "10/01/2023" },
      { id: 3, name: "Spécifications techniques réseau", type: "doc", size: "1.5 MB", date: "05/03/2023" }
    ]
  },
  {
    id: 2,
    name: "Ressources humaines",
    description: "Documents liés à la gestion des ressources humaines, fiches de poste, procédures d'embauche.",
    color: "#0F9D58",
    documents: [
      { id: 4, name: "Guide de l'employé", type: "pdf", size: "3.1 MB", date: "22/02/2023" },
      { id: 5, name: "Règlement intérieur", type: "doc", size: "980 KB", date: "15/05/2023" }
    ]
  },
  {
    id: 3,
    name: "Procédures comptables",
    description: "Ensemble des procédures et documents standards du service comptabilité.",
    color: "#F4B400",
    documents: [
      { id: 6, name: "Procédure de clôture mensuelle", type: "xls", size: "2.4 MB", date: "19/04/2023" },
      { id: 7, name: "Plan comptable", type: "xls", size: "1.8 MB", date: "03/01/2023" },
      { id: 8, name: "Manuel de saisie des factures", type: "pdf", size: "4.5 MB", date: "28/03/2023" }
    ]
  },
  {
    id: 4,
    name: "Marketing et vente",
    description: "Supports marketing, fiches produits et documentations commerciales.",
    color: "#DB4437",
    documents: [
      { id: 9, name: "Catalogue produits 2023", type: "pdf", size: "12.5 MB", date: "17/01/2023" },
      { id: 10, name: "Argumentaire commercial", type: "ppt", size: "5.7 MB", date: "08/02/2023" },
      { id: 11, name: "Guide identité visuelle", type: "pdf", size: "8.2 MB", date: "25/03/2023" }
    ]
  },
  {
    id: 5,
    name: "Qualité et normes",
    description: "Documentation relative au système de management de la qualité de l'entreprise.",
    color: "#7B1FA2",
    documents: [
      { id: 12, name: "Manuel qualité ISO 9001", type: "pdf", size: "6.8 MB", date: "14/05/2023" },
      { id: 13, name: "Procédures d'audit interne", type: "doc", size: "2.3 MB", date: "09/04/2023" }
    ]
  }
];

const CategoriesPage = () => {
  // États
  const [categories, setCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('categories'); // 'categories' ou 'documents'
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [newCategory, setNewCategory] = useState({
    name: '',
    description: '',
    color: '#6933FF'
  });
  const [sortConfig, setSortConfig] = useState({
    key: 'name',
    direction: 'asc'
  });
  const [documentSearchTerm, setDocumentSearchTerm] = useState('');

  // Chargement initial des données
  useEffect(() => {
    // Simulation d'un appel API
    setCategories(mockCategories);
  }, []);

  // Gestion des événements
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleDocumentSearch = (e) => {
    setDocumentSearchTerm(e.target.value);
  };

  const handleCategorySubmit = (e) => {
    e.preventDefault();
    // Ici, vous enverriez normalement les données vers votre API
    const id = categories.length + 1;
    const categoryToAdd = {
      ...newCategory,
      id,
      documents: []
    };
    
    setCategories([...categories, categoryToAdd]);
    setNewCategory({ name: '', description: '', color: '#6933FF' });
    setShowForm(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCategory({ ...newCategory, [name]: value });
  };

  const handleViewDocuments = (category) => {
    setSelectedCategory(category);
    setViewMode('documents');
    setDocumentSearchTerm('');
    setSortConfig({ key: 'name', direction: 'asc' });
  };

  const handleBackToCategories = () => {
    setViewMode('categories');
    setSelectedCategory(null);
  };

  const handleDeleteCategory = (id) => {
    // Dans une application réelle, vous enverriez une requête API
    setCategories(categories.filter(category => category.id !== id));
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Filtrer les catégories en fonction de la recherche
  const filteredCategories = categories.filter(category =>
    category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    category.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Filtrer et trier les documents
  const getSortedAndFilteredDocuments = () => {
    if (!selectedCategory) return [];

    let filteredDocs = selectedCategory.documents;
    
    // Filtrer par terme de recherche
    if (documentSearchTerm) {
      filteredDocs = filteredDocs.filter(doc => 
        doc.name.toLowerCase().includes(documentSearchTerm.toLowerCase()) ||
        doc.type.toLowerCase().includes(documentSearchTerm.toLowerCase())
      );
    }
    
    // Trier les documents
    if (sortConfig.key) {
      filteredDocs = [...filteredDocs].sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    
    return filteredDocs;
  };

  // Obtenir l'icône appropriée en fonction du type de document
  const getDocumentIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return 'bxs-file-pdf';
      case 'doc':
      case 'docx':
        return 'bxs-file-doc';
      case 'xls':
      case 'xlsx':
        return 'bxs-spreadsheet';
      case 'ppt':
      case 'pptx':
        return 'bxs-slideshow';
      default:
        return 'bxs-file';
    }
  };

  // Obtenir la classe pour l'indicateur de tri
  const getSortIndicator = (key) => {
    if (sortConfig.key === key) {
      return sortConfig.direction === 'asc' ? 'bx-up-arrow-alt' : 'bx-down-arrow-alt';
    }
    return 'bx-chevron-down';
  };

  return (
    <div className="page-container">
      {viewMode === 'categories' ? (
        // Vue Catégories
        <>
          <div className="page-header">
            <h1>Catégories de documents</h1>
            <div className="page-actions">
              <button 
                className="btn btn-primary"
                onClick={() => setShowForm(!showForm)}
              >
                <i className="bx bx-plus"></i>
                {showForm ? "Annuler" : "Nouvelle catégorie"}
              </button>
            </div>
          </div>

          {/* Formulaire de création de catégorie */}
          {showForm && (
            <div className="card form-card">
              <div className="form-header">
                <h2>Créer une nouvelle catégorie</h2>
                <button 
                  className="btn-icon"
                  onClick={() => setShowForm(false)}
                >
                  <i className="bx bx-x"></i>
                </button>
              </div>
              <form className="category-form" onSubmit={handleCategorySubmit}>
                <div className="form-group">
                  <label htmlFor="name">Nom de la catégorie</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    className="form-input"
                    value={newCategory.name}
                    onChange={handleInputChange}
                    placeholder="Ex: Marketing, Finance..."
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    name="description"
                    className="form-textarea"
                    value={newCategory.description}
                    onChange={handleInputChange}
                    placeholder="Décrivez l'utilité de cette catégorie"
                  ></textarea>
                </div>

                <div className="form-group">
                  <label htmlFor="color">Couleur</label>
                  <div className="color-input-container">
                    <div 
                      className="color-preview" 
                      style={{ backgroundColor: newCategory.color }}
                    ></div>
                    <input
                      type="color"
                      id="color"
                      name="color"
                      className="color-input"
                      value={newCategory.color}
                      onChange={handleInputChange}
                    />
                    <span className="color-value">{newCategory.color}</span>
                  </div>
                </div>

                <div className="form-actions">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                    Annuler
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Enregistrer
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Barre de recherche */}
          <div className="card search-card">
            <div className="search-container">
              <input
                type="text"
                placeholder="Rechercher une catégorie..."
                className="search-input"
                value={searchTerm}
                onChange={handleSearch}
              />
              <i className="bx bx-search search-icon"></i>
            </div>
          </div>

          {/* Grille de catégories */}
          {filteredCategories.length > 0 ? (
            <div className="categories-grid">
              {filteredCategories.map(category => (
                <div className="card category-card" key={category.id}>
                  <div className="category-indicator" style={{ backgroundColor: category.color }}></div>
                  <div className="category-content">
                    <h3>{category.name}</h3>
                    <p className="category-description">
                      {category.description}
                    </p>
                    <div className="category-footer">
                      <div className="document-count">
                        <i className='bx bxs-file'></i>
                        <span>{category.documents.length} document{category.documents.length !== 1 ? 's' : ''}</span>
                      </div>
                      <div className="card-actions">
                        <button
                          className="btn-icon"
                          title="Modifier"
                          onClick={() => console.log('Modifier', category.id)}
                        >
                          <i className='bx bxs-edit'></i>
                        </button>
                        <button
                          className="btn-icon btn-danger"
                          title="Supprimer"
                          onClick={() => handleDeleteCategory(category.id)}
                        >
                          <i className='bx bxs-trash'></i>
                        </button>
                        <button
                          className="btn-icon btn-success"
                          title="Voir les documents"
                          onClick={() => handleViewDocuments(category)}
                        >
                          <i className='bx bxs-folder-open'></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card empty-state">
              <div className="no-results">
                <i className='bx bx-search'></i>
                <p>Aucune catégorie trouvée. Modifiez votre recherche ou créez une nouvelle catégorie.</p>
                {searchTerm && (
                  <button className="btn btn-primary" onClick={() => setSearchTerm('')}>
                    Effacer la recherche
                  </button>
                )}
              </div>
            </div>
          )}
        </>
      ) : (
        // Vue Documents de la catégorie sélectionnée
        <div className="documents-view">
          <div className="documents-header">
            <button
              className="btn btn-secondary back-button"
              onClick={handleBackToCategories}
            >
              <i className='bx bx-arrow-back'></i> Retour aux catégories
            </button>
            
            <h2 className="document-category-title">
              <span className="category-marker" style={{ backgroundColor: selectedCategory.color }}></span>
              {selectedCategory.name}
            </h2>
            
            <p className="documents-count">
              {selectedCategory.documents.length} document{selectedCategory.documents.length !== 1 ? 's' : ''}
            </p>
          </div>

          {/* Barre de recherche pour les documents */}
          <div className="card search-card">
            <div className="search-container">
              <input
                type="text"
                placeholder="Rechercher un document..."
                className="search-input"
                value={documentSearchTerm}
                onChange={handleDocumentSearch}
              />
              <i className="bx bx-search search-icon"></i>
            </div>
          </div>

          <div className="documents-container">
            {selectedCategory.documents.length > 0 ? (
              <>
                {/* En-tête de tri pour les documents */}
                <div className="document-sort-header">
                  <div className="sort-column name-column" onClick={() => handleSort('name')}>
                    Nom
                    <i className={`bx ${getSortIndicator('name')}`}></i>
                  </div>
                  <div className="sort-column type-column" onClick={() => handleSort('type')}>
                    Type
                    <i className={`bx ${getSortIndicator('type')}`}></i>
                  </div>
                  <div className="sort-column size-column" onClick={() => handleSort('size')}>
                    Taille
                    <i className={`bx ${getSortIndicator('size')}`}></i>
                  </div>
                  <div className="sort-column date-column" onClick={() => handleSort('date')}>
                    Date
                    <i className={`bx ${getSortIndicator('date')}`}></i>
                  </div>
                  <div className="actions-column">Actions</div>
                </div>

                {/* Liste des documents */}
                <div className="documents-list">
                  {getSortedAndFilteredDocuments().length > 0 ? (
                    getSortedAndFilteredDocuments().map(doc => (
                      <div className="document-card" key={doc.id}>
                        <div className="document-icon">
                          <i className={`bx ${getDocumentIcon(doc.type)}`}></i>
                        </div>
                        <div className="document-info">
                          <h3>{doc.name}</h3>
                          <div className="document-meta">
                            <span className="doc-type">{doc.type.toUpperCase()}</span>
                            <span className="doc-size">{doc.size}</span>
                            <span className="doc-date">{doc.date}</span>
                          </div>
                        </div>
                        <div className="document-actions">
                          <button className="btn-icon" title="Voir">
                            <i className='bx bxs-show'></i>
                          </button>
                          <button className="btn-icon" title="Télécharger">
                            <i className='bx bxs-download'></i>
                          </button>
                          <button className="btn-icon" title="Plus d'options">
                            <i className='bx bx-dots-vertical-rounded'></i>
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="no-documents">
                      <i className='bx bx-search'></i>
                      <p>Aucun document ne correspond à votre recherche</p>
                      {documentSearchTerm && (
                        <button className="btn btn-primary" onClick={() => setDocumentSearchTerm('')}>
                          Effacer la recherche
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="no-documents">
                <i className='bx bx-file'></i>
                <p>Aucun document dans cette catégorie</p>
                <button className="btn btn-primary">
                  <i className="bx bx-plus"></i> Ajouter un document
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoriesPage; 
import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Dropdown from '../components/Dropdown';
import SearchBox from '../components/SearchBox';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';
import '../styles/pages.css';

const DocumentsPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  
  // Données fictives pour les documents
  const documents = [
    { id: 1, name: 'Rapport annuel 2024.pdf', type: 'pdf', date: '2024-03-24', size: '2.5 MB', owner: 'Jean Dupont' },
    { id: 2, name: 'Procédure qualité v2.1.doc', type: 'doc', date: '2024-03-23', size: '1.8 MB', owner: 'Marie Martin' },
    { id: 3, name: 'Notes de réunion mars.txt', type: 'txt', date: '2024-03-22', size: '0.2 MB', owner: 'Pierre Leroy' },
    { id: 4, name: 'Présentation client Q1.ppt', type: 'ppt', date: '2024-03-20', size: '4.7 MB', owner: 'Sophie Dubois' },
    { id: 5, name: 'Données financières 2024.xlsx', type: 'xlsx', date: '2024-03-19', size: '1.5 MB', owner: 'Thomas Bernard' },
    { id: 6, name: 'Contrat de service.pdf', type: 'pdf', date: '2024-03-18', size: '3.2 MB', owner: 'Jean Dupont' },
    { id: 7, name: 'Analyse de marché.doc', type: 'doc', date: '2024-03-15', size: '2.1 MB', owner: 'Marie Martin' },
    { id: 8, name: 'Budget prévisionnel.xlsx', type: 'xlsx', date: '2024-03-12', size: '1.1 MB', owner: 'Thomas Bernard' },
  ];

  // Fonction pour filtrer les documents
  const filteredDocuments = documents.filter(doc => {
    // Filtrer par recherche
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.owner.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Filtrer par type de document
    const matchesFilter = selectedFilter === 'all' || doc.type === selectedFilter;
    
    return matchesSearch && matchesFilter;
  });

  // Fonction pour obtenir l'icône correspondant au type de document
  const getDocumentIcon = (type) => {
    switch (type) {
      case 'pdf':
        return 'bx bxs-file-pdf';
      case 'doc':
      case 'docx':
        return 'bx bxs-file-doc';
      case 'txt':
        return 'bx bxs-file-txt';
      case 'ppt':
      case 'pptx':
        return 'bx bxs-file-ppt';
      case 'xlsx':
      case 'xls':
        return 'bx bxs-file-xlsx';
      default:
        return 'bx bx-file';
    }
  };

  // Formater la date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('fr-FR', { 
      day: '2-digit', month: '2-digit', year: 'numeric' 
    }).format(date);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Documents</h1>
          <p className="page-description">Gérez tous vos documents en un seul endroit</p>
        </div>
        <div className="page-actions">
          <Button type="primary" icon="fas fa-plus">Nouveau document</Button>
          <Button type="secondary" icon="fas fa-upload">Importer</Button>
        </div>
      </div>

      <Card className="filter-card">
        <div className="filter-container">
          <div className="search-container">
            <SearchBox 
              placeholder="Rechercher des documents..." 
              value={searchQuery} 
              onChange={(e) => setSearchQuery(e.target.value)}
              icon="fas fa-search"
            />
          </div>
          <div className="filter-actions">
            <Dropdown 
              options={[
                { value: 'recent', label: 'Plus récents' },
                { value: 'older', label: 'Plus anciens' },
                { value: 'name', label: 'Nom (A-Z)' },
                { value: 'name-desc', label: 'Nom (Z-A)' }
              ]}
              value={sortBy}
              onChange={(value) => setSortBy(value)}
              placeholder="Trier par"
              icon="fas fa-sort"
            />
          </div>
        </div>
      </Card>

      <Card>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Nom</th>
                <th>Modifié</th>
                <th>Taille</th>
                <th>Propriétaire</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocuments.length > 0 ? (
                filteredDocuments.map(doc => (
                  <tr key={doc.id}>
                    <td>
                      <div className="document-cell">
                        <i className={`${getDocumentIcon(doc.type)} document-icon ${doc.type}`}></i>
                        <span>{doc.name}</span>
                      </div>
                    </td>
                    <td>{formatDate(doc.date)}</td>
                    <td>{doc.size}</td>
                    <td>{doc.owner}</td>
                    <td>
                      <div className="actions-cell">
                        <Button type="icon" icon="fas fa-edit" tooltip="Modifier" />
                        <Button type="icon" icon="fas fa-share-alt" tooltip="Partager" />
                        <Button type="icon" icon="fas fa-trash" tooltip="Supprimer" />
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5">
                    <div className="no-results">
                      <i className="fas fa-search"></i>
                      <p>Aucun document trouvé</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default DocumentsPage; 
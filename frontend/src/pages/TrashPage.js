import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';

const TrashPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItems, setSelectedItems] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  
  // Données fictives pour les éléments dans la corbeille
  const trashItems = [
    { id: 1, name: 'Ancien rapport Q3 2023.pdf', type: 'pdf', deletedAt: '2024-03-15', deletedBy: 'Jean Dupont', size: '2.5 MB', expiresAt: '2024-04-15' },
    { id: 2, name: 'Brouillon de présentation.ppt', type: 'ppt', deletedAt: '2024-03-13', deletedBy: 'Marie Martin', size: '4.2 MB', expiresAt: '2024-04-13' },
    { id: 3, name: 'Notes de réunion obsolètes.txt', type: 'txt', deletedAt: '2024-03-10', deletedBy: 'Pierre Leroy', size: '0.1 MB', expiresAt: '2024-04-10' },
    { id: 4, name: 'Ancienne version contrat.doc', type: 'doc', deletedAt: '2024-03-08', deletedBy: 'Thomas Bernard', size: '1.7 MB', expiresAt: '2024-04-08' },
    { id: 5, name: 'Facture annulée.pdf', type: 'pdf', deletedAt: '2024-03-05', deletedBy: 'Sophie Dubois', size: '0.8 MB', expiresAt: '2024-04-05' },
    { id: 6, name: 'Données 2022.xlsx', type: 'xlsx', deletedAt: '2024-03-01', deletedBy: 'Jean Dupont', size: '1.2 MB', expiresAt: '2024-04-01' },
  ];

  // Fonction pour filtrer les éléments
  const filteredItems = trashItems.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.deletedBy.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Fonction pour obtenir l'icône correspondant au type de document
  const getDocumentIcon = (type) => {
    switch (type) {
      case 'pdf':
        return 'bx bxs-file-pdf';
      case 'doc':
        return 'bx bxs-file-doc';
      case 'txt':
        return 'bx bxs-file-txt';
      case 'ppt':
        return 'bx bxs-file-ppt';
      case 'xlsx':
        return 'bx bxs-file-xlsx';
      default:
        return 'bx bx-file';
    }
  };

  // Formatage de date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('fr-FR', { 
      day: '2-digit', month: '2-digit', year: 'numeric' 
    }).format(date);
  };

  // Calcul du temps restant avant expiration
  const getRemainingDays = (expiresAt) => {
    const now = new Date();
    const expireDate = new Date(expiresAt);
    const diffTime = expireDate - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // Gestion des sélections
  const handleSelectItem = (id) => {
    if (selectedItems.includes(id)) {
      setSelectedItems(selectedItems.filter(itemId => itemId !== id));
    } else {
      setSelectedItems([...selectedItems, id]);
    }
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredItems.map(item => item.id));
    }
    setSelectAll(!selectAll);
  };

  // Actions
  const handleRestore = () => {
    console.log('Restaurer les éléments:', selectedItems);
    // Dans une application réelle, vous appelleriez une API ici
    setSelectedItems([]);
    setSelectAll(false);
  };

  const handleDelete = () => {
    console.log('Supprimer définitivement les éléments:', selectedItems);
    // Dans une application réelle, vous appelleriez une API ici
    setSelectedItems([]);
    setSelectAll(false);
  };

  const getItemClass = (id) => {
    return selectedItems.includes(id) ? 'trash-item selected' : 'trash-item';
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Corbeille</h1>
        <div className="page-description">
          Les éléments dans la corbeille sont automatiquement supprimés après 30 jours
        </div>
      </div>

      <Card className="action-card">
        <div className="search-actions">
          <div className="search-container">
            <Input 
              type="search" 
              placeholder="Rechercher dans la corbeille..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              icon="bx-search"
            />
          </div>
          <div className="bulk-actions">
            <Button
              type="secondary"
              icon="bx bx-refresh"
              disabled={selectedItems.length === 0}
              onClick={handleRestore}
            >
              Restaurer ({selectedItems.length})
            </Button>
            <Button
              type="danger"
              icon="bx bx-trash"
              disabled={selectedItems.length === 0}
              onClick={handleDelete}
            >
              Supprimer définitivement
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <table className="trash-table">
          <thead>
            <tr>
              <th className="checkbox-column">
                <input 
                  type="checkbox" 
                  checked={selectAll} 
                  onChange={handleSelectAll} 
                  className="checkbox"
                />
              </th>
              <th>Nom</th>
              <th>Supprimé par</th>
              <th>Date de suppression</th>
              <th>Taille</th>
              <th>Expiration</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredItems.map(item => (
              <tr key={item.id} className={getItemClass(item.id)}>
                <td>
                  <input 
                    type="checkbox" 
                    checked={selectedItems.includes(item.id)} 
                    onChange={() => handleSelectItem(item.id)} 
                    className="checkbox"
                  />
                </td>
                <td className="document-cell">
                  <i className={`${getDocumentIcon(item.type)} document-icon ${item.type}`}></i>
                  <span>{item.name}</span>
                </td>
                <td>{item.deletedBy}</td>
                <td>{formatDate(item.deletedAt)}</td>
                <td>{item.size}</td>
                <td>
                  <div className="expiration-info">
                    <span className="expiration-date">{formatDate(item.expiresAt)}</span>
                    <span className="expiration-days">({getRemainingDays(item.expiresAt)} jours)</span>
                  </div>
                </td>
                <td className="actions-cell">
                  <Button type="text" icon="bx bx-refresh" title="Restaurer" />
                  <Button type="text" icon="bx bx-trash" title="Supprimer définitivement" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredItems.length === 0 && (
          <div className="empty-trash">
            <i className='bx bx-trash'></i>
            <p>La corbeille est vide</p>
          </div>
        )}
      </Card>

      <div className="trash-info">
        <Card className="info-card">
          <div className="info-header">
            <i className='bx bx-info-circle'></i>
            <h3>À propos de la corbeille</h3>
          </div>
          <div className="info-content">
            <p>Les éléments supprimés sont conservés dans la corbeille pendant 30 jours avant d'être définitivement supprimés.</p>
            <p>Vous pouvez restaurer les éléments ou les supprimer définitivement à tout moment.</p>
            <p>La corbeille est vidée automatiquement lorsque l'espace de stockage devient insuffisant.</p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default TrashPage; 
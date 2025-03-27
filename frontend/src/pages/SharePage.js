import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import '../styles/base.css';
import '../styles/variables.css';
import '../styles/modern.css';

const SharePage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showShareModal, setShowShareModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [activeTab, setActiveTab] = useState('shared');
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [linkCopied, setLinkCopied] = useState(false);
  const [shareLink, setShareLink] = useState('');
  
  // Données fictives pour les documents partagés
  const sharedDocuments = [
    { 
      id: 1, 
      name: 'Rapport annuel 2024.pdf', 
      type: 'pdf', 
      sharedBy: 'Jean Dupont',
      sharedWith: [
        { id: 1, name: 'Marie Martin', email: 'marie.martin@example.com', permission: 'edit' },
        { id: 2, name: 'Thomas Bernard', email: 'thomas.bernard@example.com', permission: 'view' }
      ],
      sharedAt: '2024-03-20',
      expiresAt: '2024-12-31'
    },
    { 
      id: 2, 
      name: 'Présentation client.ppt', 
      type: 'ppt',
      sharedBy: 'Sophie Dubois',
      sharedWith: [
        { id: 3, name: 'Pierre Leroy', email: 'pierre.leroy@example.com', permission: 'view' },
        { id: 4, name: 'Alice Simon', email: 'alice.simon@example.com', permission: 'view' },
        { id: 5, name: 'Jean Dupont', email: 'jean.dupont@example.com', permission: 'edit' }
      ],
      sharedAt: '2024-03-18',
      expiresAt: '2024-06-30'
    },
    { 
      id: 3, 
      name: 'Contrat de service.doc', 
      type: 'doc',
      sharedBy: 'Thomas Bernard',
      sharedWith: [
        { id: 1, name: 'Marie Martin', email: 'marie.martin@example.com', permission: 'edit' }
      ],
      sharedAt: '2024-03-15',
      expiresAt: null
    },
    { 
      id: 4, 
      name: 'Budget 2024.xlsx', 
      type: 'xlsx',
      sharedBy: 'Jean Dupont',
      sharedWith: [
        { id: 2, name: 'Thomas Bernard', email: 'thomas.bernard@example.com', permission: 'view' },
        { id: 3, name: 'Pierre Leroy', email: 'pierre.leroy@example.com', permission: 'view' }
      ],
      sharedAt: '2024-03-10',
      expiresAt: '2025-01-31'
    }
  ];

  // Données fictives pour les utilisateurs disponibles pour le partage
  const availableUsers = [
    { id: 1, name: 'Marie Martin', email: 'marie.martin@example.com', role: 'Responsable Marketing' },
    { id: 2, name: 'Thomas Bernard', email: 'thomas.bernard@example.com', role: 'Directeur Financier' },
    { id: 3, name: 'Pierre Leroy', email: 'pierre.leroy@example.com', role: 'Chef de Projet' },
    { id: 4, name: 'Alice Simon', email: 'alice.simon@example.com', role: 'Ressources Humaines' },
    { id: 5, name: 'Jean Dupont', email: 'jean.dupont@example.com', role: 'Directeur' },
    { id: 6, name: 'Sophie Dubois', email: 'sophie.dubois@example.com', role: 'Marketing' }
  ];

  // Fonction pour filtrer les documents partagés
  const filteredDocuments = sharedDocuments.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.sharedBy.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.sharedWith.some(user => user.name.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesSearch;
  });

  // Fonction pour obtenir l'icône correspondant au type de document
  const getDocumentIcon = (type) => {
    switch (type) {
      case 'pdf':
        return 'bx bxs-file-pdf';
      case 'doc':
        return 'bx bxs-file-doc';
      case 'ppt':
        return 'bx bxs-file-ppt';
      case 'xlsx':
        return 'bx bxs-file-xlsx';
      default:
        return 'bx bx-file';
    }
  };

  // Formater la date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Sans expiration';
    
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('fr-FR', { 
      day: '2-digit', month: '2-digit', year: 'numeric' 
    }).format(date);
  };

  // Fonction pour générer un lien de partage
  const generateShareLink = (document) => {
    const baseUrl = window.location.origin;
    const uniqueId = Math.random().toString(36).substring(2, 15);
    const link = `${baseUrl}/share/${uniqueId}`;
    setShareLink(link);
    return link;
  };

  // Fonction pour copier le lien
  const copyShareLink = async (e) => {
    e.preventDefault(); // Empêcher le comportement par défaut
    e.stopPropagation(); // Empêcher la propagation de l'événement
    try {
      await navigator.clipboard.writeText(shareLink);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    } catch (err) {
      console.error('Erreur lors de la copie du lien:', err);
    }
  };

  // Ouvrir la modal de partage pour un document
  const openShareModal = (document) => {
    setSelectedDocument(document);
    setShowShareModal(true);
  };

  // Ouvrir la modal de lien pour un document
  const openLinkModal = (document) => {
    setSelectedDocument(document);
    generateShareLink(document);
    setShowLinkModal(true);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Partage</h1>
        <div className="page-actions">
          <Button
            type="primary"
            icon="bx bx-share-alt"
          >
            Partager un document
          </Button>
        </div>
      </div>

      <Card className="filter-card">
        <div className="search-container">
          <Input 
            type="search" 
            placeholder="Rechercher dans les partages..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon="bx-search"
          />
        </div>
      </Card>

      <div className="tabs">
        <div className={`tab ${activeTab === 'shared' ? 'active' : ''}`} onClick={() => setActiveTab('shared')}>
          Partagés avec d'autres
        </div>
        <div className={`tab ${activeTab === 'with-me' ? 'active' : ''}`} onClick={() => setActiveTab('with-me')}>
          Partagés avec moi
        </div>
        <div className={`tab ${activeTab === 'links' ? 'active' : ''}`} onClick={() => setActiveTab('links')}>
          Liens publics
        </div>
      </div>

      <Card className="share-card">
        <div className="share-table-container">
          <table className="share-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Partagé par</th>
                <th>Partagé avec</th>
                <th>Date de partage</th>
                <th>Expiration</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocuments.map(doc => (
                <tr key={doc.id}>
                  <td className="document-cell">
                    <i className={`${getDocumentIcon(doc.type)} document-icon ${doc.type}`}></i>
                    <span>{doc.name}</span>
                  </td>
                  <td>{doc.sharedBy}</td>
                  <td>
                    <div className="shared-users">
                      {doc.sharedWith.slice(0, 2).map(user => (
                        <span key={user.id} className="user-chip" title={`${user.name} (${user.permission === 'edit' ? 'Peut modifier' : 'Peut voir'})`}>
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      ))}
                      {doc.sharedWith.length > 2 && (
                        <span className="user-chip more-users">
                          +{doc.sharedWith.length - 2}
                        </span>
                      )}
                    </div>
                  </td>
                  <td>{formatDate(doc.sharedAt)}</td>
                  <td>{formatDate(doc.expiresAt)}</td>
                  <td className="actions-cell">
                    <Button type="text" icon="bx bx-share-alt" onClick={() => openShareModal(doc)} />
                    <Button type="text" icon="bx bx-link" onClick={() => openLinkModal(doc)} />
                    <Button type="text" icon="bx bx-dots-vertical-rounded" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredDocuments.length === 0 && (
          <div className="no-results">
            <i className='bx bx-share-alt'></i>
            <p>Aucun document partagé ne correspond à votre recherche</p>
          </div>
        )}
      </Card>

      {showShareModal && selectedDocument && (
        <div className="modal-overlay">
          <Card className="share-modal">
            <div className="modal-header">
              <h2>Partager "{selectedDocument.name}"</h2>
              <Button 
                type="text" 
                icon="bx bx-x" 
                onClick={() => setShowShareModal(false)} 
              />
            </div>
            <div className="modal-content">
              <div className="shared-with-list">
                <h3>Personnes ayant accès</h3>
                <ul className="users-list">
                  {selectedDocument.sharedWith.map(user => (
                    <li key={user.id} className="user-item">
                      <div className="user-info">
                        <div className="user-avatar">{user.name.split(' ').map(n => n[0]).join('')}</div>
                        <div className="user-details">
                          <span className="user-name">{user.name}</span>
                          <span className="user-email">{user.email}</span>
                        </div>
                      </div>
                      <div className="user-permission">
                        <select defaultValue={user.permission}>
                          <option value="view">Peut voir</option>
                          <option value="edit">Peut modifier</option>
                        </select>
                        <Button type="text" icon="bx bx-trash" />
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="add-users">
                <h3>Ajouter des personnes</h3>
                <Input 
                  type="search" 
                  placeholder="Chercher par nom ou email..." 
                  icon="bx-search"
                />
                <div className="form-group">
                  <label>Définir la date d'expiration</label>
                  <Input type="date" />
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <Button type="text" onClick={() => setShowShareModal(false)}>Annuler</Button>
              <Button type="primary">Enregistrer</Button>
            </div>
          </Card>
        </div>
      )}

      {showLinkModal && selectedDocument && (
        <div className="modal-overlay">
          <Card className="link-modal">
            <div className="modal-header">
              <h2>Lien de partage</h2>
              <Button 
                type="text" 
                icon="bx bx-x" 
                onClick={() => setShowLinkModal(false)} 
              />
            </div>
            <div className="modal-content">
              <div className="link-settings">
                <div className="form-group">
                  <label>Accès</label>
                  <select defaultValue="anyone">
                    <option value="anyone">Tout le monde avec le lien</option>
                    <option value="organization">Personnes de l'organisation</option>
                    <option value="specific">Personnes spécifiques</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Expiration</label>
                  <Input type="date" />
                </div>
                <div className="form-group">
                  <label>Mot de passe</label>
                  <Input type="password" placeholder="Optionnel" />
                </div>
              </div>
              <div className="link-preview">
                <Input 
                  type="text" 
                  value={shareLink}
                  readOnly 
                />
                <Button 
                  type="text" 
                  icon={linkCopied ? "bx bx-check" : "bx bx-copy"} 
                  onClick={copyShareLink}
                  className={linkCopied ? "copied" : ""}
                />
              </div>
            </div>
            <div className="modal-footer">
              <Button type="text" onClick={() => setShowLinkModal(false)}>Annuler</Button>
              <Button type="primary" onClick={copyShareLink}>
                {linkCopied ? "Lien copié !" : "Copier le lien"}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default SharePage; 
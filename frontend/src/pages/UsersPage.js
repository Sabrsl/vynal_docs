import React, { useState, useEffect } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import '../styles/base.css';
import '../styles/UsersPage.css';
import logo from '../assets/logo.svg';
import avatar from '../assets/avatar.svg';

/**
 * Page de gestion des utilisateurs avec le design n8n
 */
const UsersPage = () => {
  // État pour les utilisateurs
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  // États pour les filtres
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [viewMode, setViewMode] = useState('table'); // 'table' ou 'grid'

  // États pour les modales
  const [addUserModal, setAddUserModal] = useState(false);
  const [editUserModal, setEditUserModal] = useState(false);
  const [deleteUserModal, setDeleteUserModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Données utilisateurs fictives
  const mockUsers = [
    {
      id: 1,
      email: 'john.doe@company.com',
      name: 'John Doe',
      role: 'admin',
      active: true,
      lastLogin: '2025-03-25T10:30:00',
      created: '2024-10-12T08:45:00',
      docsCreated: 45,
      storageUsed: 125000000, // en octets
    },
    {
      id: 2,
      email: 'alice.smith@company.com',
      name: 'Alice Smith',
      role: 'editor',
      active: true,
      lastLogin: '2025-03-24T14:15:00',
      created: '2024-10-15T09:20:00',
      docsCreated: 32,
      storageUsed: 97000000,
    },
    {
      id: 3,
      email: 'robert.johnson@company.com',
      name: 'Robert Johnson',
      role: 'user',
      active: false,
      lastLogin: '2025-03-10T11:45:00',
      created: '2024-11-05T16:30:00',
      docsCreated: 8,
      storageUsed: 15000000,
    },
    {
      id: 4,
      email: 'emma.wilson@company.com',
      name: 'Emma Wilson',
      role: 'admin',
      active: true,
      lastLogin: '2025-03-26T08:20:00',
      created: '2024-09-28T10:15:00',
      docsCreated: 67,
      storageUsed: 230000000,
    },
    {
      id: 5,
      email: 'michael.brown@company.com',
      name: 'Michael Brown',
      role: 'editor',
      active: true,
      lastLogin: '2025-03-22T16:40:00',
      created: '2024-10-30T13:45:00',
      docsCreated: 27,
      storageUsed: 85000000,
    },
    {
      id: 6,
      email: 'sophia.taylor@company.com',
      name: 'Sophia Taylor',
      role: 'user',
      active: true,
      lastLogin: '2025-03-20T09:30:00',
      created: '2024-12-05T11:20:00',
      docsCreated: 5,
      storageUsed: 8500000,
    },
    {
      id: 7,
      email: 'david.miller@company.com',
      name: 'David Miller',
      role: 'user',
      active: false,
      lastLogin: '2025-02-15T14:10:00',
      created: '2024-11-15T15:30:00',
      docsCreated: 12,
      storageUsed: 27000000,
    },
    {
      id: 8,
      email: 'olivia.davis@company.com',
      name: 'Olivia Davis',
      role: 'editor',
      active: true,
      lastLogin: '2025-03-24T11:05:00',
      created: '2024-10-20T09:15:00',
      docsCreated: 43,
      storageUsed: 112000000,
    }
  ];

  // Charger les utilisateurs au chargement du composant
  useEffect(() => {
    const loadUsers = async () => {
      // Simuler une requête API
      setTimeout(() => {
        setUsers(mockUsers);
        setFilteredUsers(mockUsers);
        setLoading(false);
      }, 1000);
    };

    loadUsers();
  }, []);

  // Filtrer et trier les utilisateurs
  useEffect(() => {
    let result = [...users];

    // Filtrer par recherche
    if (searchQuery) {
      const lowerCaseQuery = searchQuery.toLowerCase();
      result = result.filter(
        user => 
          user.name.toLowerCase().includes(lowerCaseQuery) || 
          user.email.toLowerCase().includes(lowerCaseQuery)
      );
    }

    // Filtrer par rôle
    if (roleFilter !== 'all') {
      result = result.filter(user => user.role === roleFilter);
    }

    // Trier
    result.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      // Si c'est une date, convertir en timestamps
      if (sortBy === 'lastLogin' || sortBy === 'created') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredUsers(result);
  }, [users, searchQuery, roleFilter, sortBy, sortOrder]);

  // Fonctions utilitaires
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatStorageSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
  };

  const getInitials = (name) => {
    if (!name) return 'NN';
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  // Gestionnaires d'événements
  const handleAddUser = () => {
    setAddUserModal(true);
  };

  const handleEditUser = (user) => {
    setCurrentUser(user);
    setEditUserModal(true);
  };

  const handleDeleteUser = (user) => {
    setCurrentUser(user);
    setDeleteUserModal(true);
  };

  const handleSaveUser = (userData) => {
    // Ici, vous implémenteriez la logique pour envoyer les données à l'API
    if (currentUser) {
      // Édition
      const updatedUsers = users.map(user => 
        user.id === currentUser.id ? { ...user, ...userData } : user
      );
      setUsers(updatedUsers);
    } else {
      // Ajout
      const newUser = {
        id: users.length + 1,
        ...userData,
        created: new Date().toISOString(),
        lastLogin: null,
        docsCreated: 0,
        storageUsed: 0,
      };
      setUsers([...users, newUser]);
    }

    // Fermer les modales
    setAddUserModal(false);
    setEditUserModal(false);
    setCurrentUser(null);
  };

  const handleConfirmDelete = () => {
    if (currentUser) {
      const updatedUsers = users.filter(user => user.id !== currentUser.id);
      setUsers(updatedUsers);
      setDeleteUserModal(false);
      setCurrentUser(null);
    }
  };

  // Render des modales
  const renderAddEditUserModal = () => {
    const isEdit = !!currentUser;
    
    return (
      <div className="modal-overlay">
        <div className="modal">
          <div className="modal-header">
            <h2>{isEdit ? 'Modifier l\'utilisateur' : 'Ajouter un utilisateur'}</h2>
            <button className="close-button" onClick={() => {
              setAddUserModal(false);
              setEditUserModal(false);
              setCurrentUser(null);
            }}>
              <i className="bx bx-x"></i>
            </button>
          </div>
          <div className="modal-body">
            <form>
              <div className="form-group">
                <label>Nom complet</label>
                <Input 
                  type="text" 
                  placeholder="Nom complet"
                  defaultValue={isEdit ? currentUser.name : ''}
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <Input 
                  type="email" 
                  placeholder="email@example.com"
                  defaultValue={isEdit ? currentUser.email : ''}
                />
              </div>
              <div className="form-group">
                <label>Rôle</label>
                <select className="n-input__inner">
                  <option value="user">Utilisateur</option>
                  <option value="editor">Éditeur</option>
                  <option value="admin">Administrateur</option>
                </select>
              </div>
              {isEdit && (
                <div className="checkbox-group">
                  <label>
                    <input type="checkbox" defaultChecked={currentUser.active} /> 
                    Compte actif
                  </label>
                </div>
              )}
              {!isEdit && (
                <div className="form-group">
                  <label>Mot de passe</label>
                  <Input 
                    type="password" 
                    placeholder="Mot de passe"
                  />
                </div>
              )}
            </form>
          </div>
          <div className="modal-footer">
            <Button 
              type="text" 
              onClick={() => {
                setAddUserModal(false);
                setEditUserModal(false);
                setCurrentUser(null);
              }}
            >
              Annuler
            </Button>
            <Button 
              type="primary" 
              onClick={() => handleSaveUser({
                name: 'Nouveau Utilisateur',
                email: 'nouveau@example.com',
                role: 'user',
                active: true
              })}
            >
              {isEdit ? 'Enregistrer' : 'Ajouter'}
            </Button>
          </div>
        </div>
      </div>
    );
  };

  const renderDeleteUserModal = () => {
    return (
      <div className="modal-overlay">
        <div className="modal confirm-modal">
          <div className="modal-header">
            <h2>Confirmer la suppression</h2>
            <button className="close-button" onClick={() => {
              setDeleteUserModal(false);
              setCurrentUser(null);
            }}>
              <i className="bx bx-x"></i>
            </button>
          </div>
          <div className="modal-body">
            <div className="confirm-message">
              <i className="bx bx-error-circle"></i>
              <p>
                Êtes-vous sûr de vouloir supprimer l'utilisateur 
                <strong> {currentUser?.name}</strong> ? <br />
                Cette action est irréversible.
              </p>
            </div>
          </div>
          <div className="modal-footer">
            <Button 
              type="text" 
              onClick={() => {
                setDeleteUserModal(false);
                setCurrentUser(null);
              }}
            >
              Annuler
            </Button>
            <Button 
              type="danger" 
              onClick={handleConfirmDelete}
            >
              Supprimer
            </Button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>Gestion des utilisateurs</h1>
        <div className="page-actions">
          <Button
            type="primary"
            icon="bx bx-plus"
            onClick={handleAddUser}
          >
            Ajouter un utilisateur
          </Button>
        </div>
      </div>

      <Card className="users-filters">
        <div className="filter-group">
          <Input
            prefixIcon="bx bx-search"
            placeholder="Rechercher un utilisateur..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <label>Rôle :</label>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
          >
            <option value="all">Tous les rôles</option>
            <option value="admin">Administrateur</option>
            <option value="editor">Éditeur</option>
            <option value="user">Utilisateur</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Trier par :</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="name">Nom</option>
            <option value="lastLogin">Dernière connexion</option>
            <option value="created">Date de création</option>
            <option value="docsCreated">Documents créés</option>
          </select>
        </div>
        <div className="filter-group">
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option value="asc">Croissant</option>
            <option value="desc">Décroissant</option>
          </select>
        </div>
        <div className="view-toggle">
          <Button
            icon={`bx bx-list-ul ${viewMode === 'table' ? 'active' : ''}`}
            type={viewMode === 'table' ? 'primary' : 'text'}
            onClick={() => setViewMode('table')}
          />
          <Button
            icon={`bx bx-grid-alt ${viewMode === 'grid' ? 'active' : ''}`}
            type={viewMode === 'grid' ? 'primary' : 'text'}
            onClick={() => setViewMode('grid')}
          />
        </div>
      </Card>

      {loading ? (
        <Card className="users-loading-card">
          <div className="loading-spinner">
            <i className="bx bx-loader-alt bx-spin"></i>
            <p>Chargement des utilisateurs...</p>
          </div>
        </Card>
      ) : (
        <>
          {viewMode === 'table' ? (
            <Card className="users-table-card">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Rôle</th>
                    <th>Statut</th>
                    <th>Dernière connexion</th>
                    <th>Documents</th>
                    <th>Stockage</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.length > 0 ? (
                    filteredUsers.map((user) => (
                      <tr key={user.id}>
                        <td>
                          <div className="user-name-cell">
                            <div className={`user-avatar-initials role-${user.role}`}>
                              {getInitials(user.name)}
                            </div>
                            <div>
                              <div className="font-medium">{user.name}</div>
                              <div className="text-lighter text-xs">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`role-badge role-${user.role}`}>
                            {user.role === 'admin' && 'Administrateur'}
                            {user.role === 'editor' && 'Éditeur'}
                            {user.role === 'user' && 'Utilisateur'}
                          </span>
                        </td>
                        <td>
                          <span className={`status-badge ${user.active ? 'status-active' : 'status-inactive'}`}>
                            {user.active ? 'Actif' : 'Inactif'}
                          </span>
                        </td>
                        <td>{formatDate(user.lastLogin)}</td>
                        <td>{user.docsCreated}</td>
                        <td>{formatStorageSize(user.storageUsed)}</td>
                        <td className="actions-cell">
                          <Button
                            icon="bx bx-edit-alt"
                            type="text"
                            onClick={() => handleEditUser(user)}
                          />
                          <Button
                            icon="bx bx-trash"
                            type="text"
                            className="danger"
                            onClick={() => handleDeleteUser(user)}
                          />
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7">
                        <div className="no-results">
                          <i className="bx bx-search-alt"></i>
                          <p>Aucun utilisateur trouvé</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </Card>
          ) : (
            <div className="users-grid">
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <Card key={user.id} className="user-card">
                    <div className="user-card-header">
                      <div className={`user-avatar-initials role-${user.role}`}>
                        {getInitials(user.name)}
                      </div>
                      <div className="user-card-name">
                        <h3>{user.name}</h3>
                        <p>{user.email}</p>
                      </div>
                      <div className="user-card-badges">
                        <span className={`role-badge role-${user.role}`}>
                          {user.role === 'admin' && 'Administrateur'}
                          {user.role === 'editor' && 'Éditeur'}
                          {user.role === 'user' && 'Utilisateur'}
                        </span>
                        <span className={`status-badge ${user.active ? 'status-active' : 'status-inactive'}`}>
                          {user.active ? 'Actif' : 'Inactif'}
                        </span>
                      </div>
                    </div>
                    <div className="user-card-body">
                      <div className="user-card-stat">
                        <i className="bx bx-calendar"></i>
                        <div>
                          <span>Création du compte</span>
                          <p>{formatDate(user.created)}</p>
                        </div>
                      </div>
                      <div className="user-card-stat">
                        <i className="bx bx-time"></i>
                        <div>
                          <span>Dernière connexion</span>
                          <p>{formatDate(user.lastLogin)}</p>
                        </div>
                      </div>
                      <div className="user-card-stat">
                        <i className="bx bx-file"></i>
                        <div>
                          <span>Documents créés</span>
                          <p>{user.docsCreated}</p>
                        </div>
                      </div>
                      <div className="user-card-stat">
                        <i className="bx bx-data"></i>
                        <div>
                          <span>Stockage utilisé</span>
                          <p>{formatStorageSize(user.storageUsed)}</p>
                        </div>
                      </div>
                    </div>
                    <div className="user-card-footer">
                      <Button
                        icon="bx bx-edit-alt"
                        type="outlined"
                        onClick={() => handleEditUser(user)}
                      >
                        Modifier
                      </Button>
                      <Button
                        icon="bx bx-trash"
                        type="danger"
                        onClick={() => handleDeleteUser(user)}
                      >
                        Supprimer
                      </Button>
                    </div>
                  </Card>
                ))
              ) : (
                <div className="no-results-card">
                  <i className="bx bx-search-alt"></i>
                  <p>Aucun utilisateur trouvé</p>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Modales */}
      {(addUserModal || editUserModal) && renderAddEditUserModal()}
      {deleteUserModal && renderDeleteUserModal()}
    </div>
  );
};

export default UsersPage; 
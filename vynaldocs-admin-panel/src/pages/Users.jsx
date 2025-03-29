import React, { useState, useEffect } from 'react';
import { userAPI } from '../utils/api';
import { formatDate } from '../lib/utils';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { UserPlus, Search, RefreshCw, Check, X, Edit, Trash } from 'lucide-react';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchUsers = async (page = 1) => {
    try {
      setLoading(true);
      const response = await userAPI.getUsers(page, 10);
      setUsers(response.data.users);
      setTotalPages(Math.ceil(response.data.total / response.data.limit));
      setCurrentPage(page);
      setError(null);
    } catch (err) {
      setError('Impossible de charger la liste des utilisateurs');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Mock data for development (remove in production)
  const mockUsers = [
    {
      _id: '1',
      firstName: 'Jean',
      lastName: 'Dupont',
      email: 'jean.dupont@example.com',
      role: 'admin',
      isActive: true,
      createdAt: '2023-01-15T14:22:10Z',
      lastLogin: '2023-06-02T09:15:33Z'
    },
    {
      _id: '2',
      firstName: 'Marie',
      lastName: 'Martin',
      email: 'marie.martin@example.com',
      role: 'user',
      isActive: true,
      createdAt: '2023-02-20T11:05:22Z',
      lastLogin: '2023-06-01T16:45:12Z'
    },
    {
      _id: '3',
      firstName: 'Pierre',
      lastName: 'Bernard',
      email: 'pierre.bernard@example.com',
      role: 'editor',
      isActive: false,
      createdAt: '2023-03-10T09:30:15Z',
      lastLogin: '2023-05-28T14:22:48Z'
    }
  ];

  // Use mock data if no users are available
  const displayUsers = users.length > 0 ? users : mockUsers;

  // Filter users based on search
  const filteredUsers = displayUsers.filter(user => 
    user.firstName.toLowerCase().includes(search.toLowerCase()) ||
    user.lastName.toLowerCase().includes(search.toLowerCase()) ||
    user.email.toLowerCase().includes(search.toLowerCase()) ||
    user.role.toLowerCase().includes(search.toLowerCase())
  );

  // Function to handle page change
  const handlePageChange = (page) => {
    fetchUsers(page);
  };

  // Function to handle user status toggle
  const handleToggleStatus = async (id, isActive) => {
    try {
      if (isActive) {
        await userAPI.deactivateUser(id);
      } else {
        await userAPI.activateUser(id);
      }
      fetchUsers(currentPage);
    } catch (err) {
      setError('Impossible de modifier le statut de l\'utilisateur');
      console.error('Error toggling user status:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Utilisateurs</h2>
          <p className="text-muted-foreground">
            Gérez les utilisateurs de la plateforme
          </p>
        </div>
        <Button>
          <UserPlus className="mr-2 h-4 w-4" />
          Nouvel utilisateur
        </Button>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive text-sm p-4 rounded-md">
          {error}
        </div>
      )}

      <div className="flex items-center gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Rechercher un utilisateur..."
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Button variant="outline" onClick={() => fetchUsers(currentPage)}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      <Card>
        <div className="rounded-md border">
          <div className="relative w-full overflow-auto">
            <table className="w-full caption-bottom text-sm">
              <thead>
                <tr className="border-b transition-colors hover:bg-muted/50">
                  <th className="h-12 px-4 text-left align-middle font-medium">Nom</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Email</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Rôle</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Statut</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Date de création</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Dernière connexion</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="7" className="p-4 text-center">
                      Chargement des utilisateurs...
                    </td>
                  </tr>
                ) : filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="p-4 text-center">
                      Aucun utilisateur trouvé
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((user) => (
                    <tr 
                      key={user._id} 
                      className="border-b transition-colors hover:bg-muted/50"
                    >
                      <td className="p-4 align-middle">
                        {user.firstName} {user.lastName}
                      </td>
                      <td className="p-4 align-middle">{user.email}</td>
                      <td className="p-4 align-middle">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          user.role === 'admin' 
                            ? 'bg-blue-50 text-blue-700' 
                            : user.role === 'editor'
                              ? 'bg-purple-50 text-purple-700'
                              : 'bg-gray-100 text-gray-700'
                        }`}>
                          {user.role === 'admin' 
                            ? 'Admin' 
                            : user.role === 'editor' 
                              ? 'Éditeur' 
                              : 'Utilisateur'}
                        </span>
                      </td>
                      <td className="p-4 align-middle">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          user.isActive 
                            ? 'bg-green-50 text-green-700' 
                            : 'bg-red-50 text-red-700'
                        }`}>
                          {user.isActive ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="p-4 align-middle">
                        {formatDate(user.createdAt)}
                      </td>
                      <td className="p-4 align-middle">
                        {user.lastLogin ? formatDate(user.lastLogin) : '-'}
                      </td>
                      <td className="p-4 align-middle">
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="icon" title="Modifier">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            title={user.isActive ? "Désactiver" : "Activer"}
                            onClick={() => handleToggleStatus(user._id, user.isActive)}
                          >
                            {user.isActive ? (
                              <X className="h-4 w-4 text-red-500" />
                            ) : (
                              <Check className="h-4 w-4 text-green-500" />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            title="Supprimer"
                          >
                            <Trash className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </Card>

      {totalPages > 1 && (
        <div className="flex items-center justify-end space-x-2 py-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1 || loading}
          >
            Précédent
          </Button>
          <div className="text-sm">
            Page {currentPage} sur {totalPages}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages || loading}
          >
            Suivant
          </Button>
        </div>
      )}
    </div>
  );
};

export default Users; 
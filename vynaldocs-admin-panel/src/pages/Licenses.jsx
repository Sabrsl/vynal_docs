import React, { useState, useEffect } from 'react';
import { licenseAPI } from '../utils/api';
import { formatDate } from '../lib/utils';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { KeyRound, Search, RefreshCw, Check, X, Edit, Trash, Copy } from 'lucide-react';

const Licenses = () => {
  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [copiedId, setCopiedId] = useState(null);

  const fetchLicenses = async (page = 1) => {
    try {
      setLoading(true);
      const response = await licenseAPI.getLicenses(page, 10);
      setLicenses(response.data.licenses);
      setTotalPages(Math.ceil(response.data.total / response.data.limit));
      setCurrentPage(page);
      setError(null);
    } catch (err) {
      setError('Impossible de charger la liste des licences');
      console.error('Error fetching licenses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLicenses();
  }, []);

  // Mock data for development (remove in production)
  const mockLicenses = [
    {
      _id: '1',
      key: 'VYNAL-1234-5678-9ABC',
      type: 'premium',
      seats: 5,
      isActive: true,
      expiresAt: '2024-12-31T23:59:59Z',
      userId: '1',
      userName: 'Jean Dupont',
      createdAt: '2023-01-10T12:00:00Z',
      activatedAt: '2023-01-15T08:30:22Z'
    },
    {
      _id: '2',
      key: 'VYNAL-2345-6789-ABCD',
      type: 'standard',
      seats: 1,
      isActive: true,
      expiresAt: '2024-06-30T23:59:59Z',
      userId: '2',
      userName: 'Marie Martin',
      createdAt: '2023-02-15T14:30:00Z',
      activatedAt: '2023-02-16T10:15:45Z'
    },
    {
      _id: '3',
      key: 'VYNAL-3456-7890-BCDE',
      type: 'enterprise',
      seats: 20,
      isActive: false,
      expiresAt: '2023-12-31T23:59:59Z',
      userId: '3',
      userName: 'Pierre Bernard',
      createdAt: '2023-03-01T09:45:00Z',
      activatedAt: null
    }
  ];

  // Use mock data if no licenses are available
  const displayLicenses = licenses.length > 0 ? licenses : mockLicenses;

  // Filter licenses based on search
  const filteredLicenses = displayLicenses.filter(license => 
    license.key.toLowerCase().includes(search.toLowerCase()) ||
    license.type.toLowerCase().includes(search.toLowerCase()) ||
    (license.userName && license.userName.toLowerCase().includes(search.toLowerCase()))
  );

  // Function to handle page change
  const handlePageChange = (page) => {
    fetchLicenses(page);
  };

  // Function to handle license status toggle
  const handleToggleStatus = async (id, isActive) => {
    try {
      if (isActive) {
        await licenseAPI.deactivateLicense(id);
      } else {
        await licenseAPI.activateLicense(id);
      }
      fetchLicenses(currentPage);
    } catch (err) {
      setError('Impossible de modifier le statut de la licence');
      console.error('Error toggling license status:', err);
    }
  };

  // Function to copy license key to clipboard
  const copyToClipboard = (key, id) => {
    navigator.clipboard.writeText(key)
      .then(() => {
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
      })
      .catch(err => {
        console.error('Failed to copy license key:', err);
      });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Licences</h2>
          <p className="text-muted-foreground">
            Gérez les licences de la plateforme
          </p>
        </div>
        <Button>
          <KeyRound className="mr-2 h-4 w-4" />
          Nouvelle licence
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
            placeholder="Rechercher une licence..."
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Button variant="outline" onClick={() => fetchLicenses(currentPage)}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      <Card>
        <div className="rounded-md border">
          <div className="relative w-full overflow-auto">
            <table className="w-full caption-bottom text-sm">
              <thead>
                <tr className="border-b transition-colors hover:bg-muted/50">
                  <th className="h-12 px-4 text-left align-middle font-medium">Clé</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Type</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Sièges</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Statut</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Utilisateur</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Expiration</th>
                  <th className="h-12 px-4 text-left align-middle font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="7" className="p-4 text-center">
                      Chargement des licences...
                    </td>
                  </tr>
                ) : filteredLicenses.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="p-4 text-center">
                      Aucune licence trouvée
                    </td>
                  </tr>
                ) : (
                  filteredLicenses.map((license) => (
                    <tr 
                      key={license._id} 
                      className="border-b transition-colors hover:bg-muted/50"
                    >
                      <td className="p-4 align-middle">
                        <div className="flex items-center">
                          <span className="font-mono">{license.key}</span>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={() => copyToClipboard(license.key, license._id)}
                            title="Copier la clé"
                            className="ml-2 h-6 w-6"
                          >
                            {copiedId === license._id ? (
                              <Check className="h-3 w-3 text-green-500" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </Button>
                        </div>
                      </td>
                      <td className="p-4 align-middle">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          license.type === 'premium' 
                            ? 'bg-blue-50 text-blue-700' 
                            : license.type === 'enterprise'
                              ? 'bg-purple-50 text-purple-700'
                              : 'bg-gray-100 text-gray-700'
                        }`}>
                          {license.type === 'premium' 
                            ? 'Premium' 
                            : license.type === 'enterprise' 
                              ? 'Entreprise' 
                              : 'Standard'}
                        </span>
                      </td>
                      <td className="p-4 align-middle">{license.seats}</td>
                      <td className="p-4 align-middle">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          license.isActive 
                            ? 'bg-green-50 text-green-700' 
                            : 'bg-red-50 text-red-700'
                        }`}>
                          {license.isActive ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="p-4 align-middle">
                        {license.userName || '-'}
                      </td>
                      <td className="p-4 align-middle">
                        {formatDate(license.expiresAt)}
                      </td>
                      <td className="p-4 align-middle">
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="icon" title="Modifier">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            title={license.isActive ? "Désactiver" : "Activer"}
                            onClick={() => handleToggleStatus(license._id, license.isActive)}
                          >
                            {license.isActive ? (
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

export default Licenses; 
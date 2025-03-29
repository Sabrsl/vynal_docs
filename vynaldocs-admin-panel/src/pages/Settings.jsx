import React, { useState, useEffect } from 'react';
import { settingsAPI } from '../utils/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card';
import { Save, RefreshCw } from 'lucide-react';

const Settings = () => {
  const [settings, setSettings] = useState({
    appName: 'VynalDocs',
    companyName: 'Vynal SAS',
    supportEmail: 'support@vynaldocs.com',
    maxDocumentsPerUser: 100,
    maxStoragePerUser: 1000,
    maintenanceMode: false,
    maintenanceMessage: '',
    documentTypes: 'pdf,docx,xlsx,pptx,txt',
    defaultLanguage: 'fr',
    adminEmails: 'admin@vynaldocs.com',
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Fetch settings on component mount
  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await settingsAPI.getSettings();
      setSettings(response.data);
      setError(null);
    } catch (err) {
      setError('Impossible de charger les paramètres');
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      await settingsAPI.updateSettings(settings);
      setSuccess(true);
      setError(null);
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 3000);
    } catch (err) {
      setError('Impossible de sauvegarder les paramètres');
      console.error('Error saving settings:', err);
      setSuccess(false);
    } finally {
      setSaving(false);
    }
  };

  // Settings groups
  const generalSettings = [
    {
      name: 'appName',
      label: 'Nom de l\'application',
      type: 'text',
      placeholder: 'VynalDocs',
    },
    {
      name: 'companyName',
      label: 'Nom de l\'entreprise',
      type: 'text',
      placeholder: 'Vynal SAS',
    },
    {
      name: 'supportEmail',
      label: 'Email de support',
      type: 'email',
      placeholder: 'support@vynaldocs.com',
    },
    {
      name: 'defaultLanguage',
      label: 'Langue par défaut',
      type: 'text',
      placeholder: 'fr',
    }
  ];

  const limitSettings = [
    {
      name: 'maxDocumentsPerUser',
      label: 'Documents max par utilisateur',
      type: 'number',
      placeholder: '100',
    },
    {
      name: 'maxStoragePerUser',
      label: 'Stockage max par utilisateur (MB)',
      type: 'number',
      placeholder: '1000',
    },
    {
      name: 'documentTypes',
      label: 'Types de documents autorisés',
      type: 'text',
      placeholder: 'pdf,docx,xlsx,pptx,txt',
    }
  ];

  const maintenanceSettings = [
    {
      name: 'maintenanceMode',
      label: 'Mode maintenance',
      type: 'checkbox',
    },
    {
      name: 'maintenanceMessage',
      label: 'Message de maintenance',
      type: 'textarea',
      placeholder: 'Maintenance en cours, veuillez revenir plus tard.',
    }
  ];

  const securitySettings = [
    {
      name: 'adminEmails',
      label: 'Emails administrateurs',
      type: 'text',
      placeholder: 'admin@vynaldocs.com,autre.admin@vynaldocs.com',
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Paramètres</h2>
        <p className="text-muted-foreground">
          Gérez les paramètres globaux de la plateforme
        </p>
      </div>
      
      {error && (
        <div className="bg-destructive/15 text-destructive text-sm p-4 rounded-md">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 text-green-700 text-sm p-4 rounded-md">
          Paramètres sauvegardés avec succès.
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Paramètres généraux</CardTitle>
              <CardDescription>
                Informations de base de la plateforme
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {generalSettings.map((setting) => (
                <div key={setting.name} className="space-y-2">
                  <label htmlFor={setting.name} className="text-sm font-medium">
                    {setting.label}
                  </label>
                  <Input
                    id={setting.name}
                    name={setting.name}
                    type={setting.type}
                    placeholder={setting.placeholder}
                    value={settings[setting.name] || ''}
                    onChange={handleChange}
                    disabled={loading}
                  />
                </div>
              ))}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Limites et restrictions</CardTitle>
              <CardDescription>
                Définissez les limites pour les utilisateurs
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {limitSettings.map((setting) => (
                <div key={setting.name} className="space-y-2">
                  <label htmlFor={setting.name} className="text-sm font-medium">
                    {setting.label}
                  </label>
                  <Input
                    id={setting.name}
                    name={setting.name}
                    type={setting.type}
                    placeholder={setting.placeholder}
                    value={settings[setting.name] || ''}
                    onChange={handleChange}
                    disabled={loading}
                  />
                </div>
              ))}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Maintenance</CardTitle>
              <CardDescription>
                Gérez le mode maintenance de l'application
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {maintenanceSettings.map((setting) => (
                <div key={setting.name} className="space-y-2">
                  {setting.type === 'checkbox' ? (
                    <div className="flex items-center space-x-2">
                      <input
                        id={setting.name}
                        name={setting.name}
                        type="checkbox"
                        checked={settings[setting.name] || false}
                        onChange={handleChange}
                        disabled={loading}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      <label htmlFor={setting.name} className="text-sm font-medium">
                        {setting.label}
                      </label>
                    </div>
                  ) : setting.type === 'textarea' ? (
                    <>
                      <label htmlFor={setting.name} className="text-sm font-medium">
                        {setting.label}
                      </label>
                      <textarea
                        id={setting.name}
                        name={setting.name}
                        placeholder={setting.placeholder}
                        value={settings[setting.name] || ''}
                        onChange={handleChange}
                        disabled={loading}
                        rows={3}
                        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      />
                    </>
                  ) : (
                    <>
                      <label htmlFor={setting.name} className="text-sm font-medium">
                        {setting.label}
                      </label>
                      <Input
                        id={setting.name}
                        name={setting.name}
                        type={setting.type}
                        placeholder={setting.placeholder}
                        value={settings[setting.name] || ''}
                        onChange={handleChange}
                        disabled={loading}
                      />
                    </>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Sécurité</CardTitle>
              <CardDescription>
                Paramètres de sécurité et accès administrateur
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {securitySettings.map((setting) => (
                <div key={setting.name} className="space-y-2">
                  <label htmlFor={setting.name} className="text-sm font-medium">
                    {setting.label}
                  </label>
                  <Input
                    id={setting.name}
                    name={setting.name}
                    type={setting.type}
                    placeholder={setting.placeholder}
                    value={settings[setting.name] || ''}
                    onChange={handleChange}
                    disabled={loading}
                  />
                  {setting.name === 'adminEmails' && (
                    <p className="text-xs text-muted-foreground">
                      Liste d'emails séparés par des virgules qui auront un accès administrateur.
                    </p>
                  )}
                </div>
              ))}
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button 
                type="button" 
                variant="outline"
                onClick={fetchSettings}
                disabled={loading}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Actualiser
              </Button>
              <Button 
                type="submit" 
                disabled={loading || saving}
              >
                {saving ? (
                  <>
                    <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
                    Sauvegarde...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Sauvegarder
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </div>
      </form>
    </div>
  );
};

export default Settings; 
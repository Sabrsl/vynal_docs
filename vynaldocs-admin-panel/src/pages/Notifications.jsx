import React, { useState, useEffect } from 'react';
import { notificationAPI } from '../utils/api';
import { formatDate } from '../lib/utils';
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
import { Bell, Send, Trash, RefreshCw } from 'lucide-react';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Form state
  const [newNotification, setNewNotification] = useState({
    title: '',
    message: '',
    type: 'info', // info, warning, error, success
    recipients: 'all' // all, users, admins
  });

  // Fetch notifications on component mount
  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationAPI.getNotifications();
      setNotifications(response.data);
      setError(null);
    } catch (err) {
      setError('Impossible de charger les notifications');
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewNotification({
      ...newNotification,
      [name]: value
    });
  };

  // Send a new notification
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!newNotification.title || !newNotification.message) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }
    
    try {
      setSending(true);
      await notificationAPI.sendNotification(newNotification);
      
      // Reset form
      setNewNotification({
        title: '',
        message: '',
        type: 'info',
        recipients: 'all'
      });
      
      // Show success message
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      
      // Refresh notifications list
      fetchNotifications();
      
      setError(null);
    } catch (err) {
      setError('Échec de l\'envoi de la notification');
      console.error('Error sending notification:', err);
    } finally {
      setSending(false);
    }
  };

  // Delete a notification
  const handleDelete = async (id) => {
    try {
      await notificationAPI.deleteNotification(id);
      fetchNotifications();
    } catch (err) {
      setError('Impossible de supprimer la notification');
      console.error('Error deleting notification:', err);
    }
  };

  // Mock data for development (remove in production)
  const mockNotifications = [
    {
      _id: '1',
      title: 'Maintenance prévue',
      message: 'Une maintenance est prévue ce weekend. L\'application sera indisponible pendant 2 heures.',
      type: 'warning',
      recipients: 'all',
      createdAt: '2023-06-01T14:30:00Z',
      createdBy: 'Jean Dupont',
      read: 85
    },
    {
      _id: '2',
      title: 'Nouvelle fonctionnalité disponible',
      message: 'Vous pouvez maintenant utiliser l\'export PDF dans tous vos documents.',
      type: 'info',
      recipients: 'users',
      createdAt: '2023-05-15T09:45:00Z',
      createdBy: 'Admin',
      read: 42
    },
    {
      _id: '3',
      title: 'Problème résolu',
      message: 'Le problème de connexion a été résolu. Merci de votre patience.',
      type: 'success',
      recipients: 'all',
      createdAt: '2023-05-10T16:20:00Z',
      createdBy: 'Support',
      read: 128
    }
  ];

  // Use mock data if no notifications are available
  const displayNotifications = notifications.length > 0 ? notifications : mockNotifications;

  // Get badge color based on notification type
  const getBadgeColor = (type) => {
    switch (type) {
      case 'warning':
        return 'bg-yellow-50 text-yellow-700';
      case 'error':
        return 'bg-red-50 text-red-700';
      case 'success':
        return 'bg-green-50 text-green-700';
      default: // info
        return 'bg-blue-50 text-blue-700';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Notifications</h2>
        <p className="text-muted-foreground">
          Envoyez des messages globaux aux utilisateurs
        </p>
      </div>
      
      {error && (
        <div className="bg-destructive/15 text-destructive text-sm p-4 rounded-md">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 text-green-700 text-sm p-4 rounded-md">
          Notification envoyée avec succès.
        </div>
      )}
      
      <div className="grid gap-6 md:grid-cols-2">
        {/* New notification form */}
        <Card>
          <CardHeader>
            <CardTitle>Envoyer une notification</CardTitle>
            <CardDescription>
              Envoyez un message à tous les utilisateurs ou à un groupe spécifique
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="title" className="text-sm font-medium">
                  Titre *
                </label>
                <Input
                  id="title"
                  name="title"
                  value={newNotification.title}
                  onChange={handleInputChange}
                  placeholder="Titre de la notification"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="message" className="text-sm font-medium">
                  Message *
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={newNotification.message}
                  onChange={handleInputChange}
                  placeholder="Contenu de la notification"
                  rows={4}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  required
                />
              </div>
              
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label htmlFor="type" className="text-sm font-medium">
                    Type
                  </label>
                  <select
                    id="type"
                    name="type"
                    value={newNotification.type}
                    onChange={handleInputChange}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="info">Information</option>
                    <option value="warning">Avertissement</option>
                    <option value="error">Erreur</option>
                    <option value="success">Succès</option>
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label htmlFor="recipients" className="text-sm font-medium">
                    Destinataires
                  </label>
                  <select
                    id="recipients"
                    name="recipients"
                    value={newNotification.recipients}
                    onChange={handleInputChange}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="all">Tous les utilisateurs</option>
                    <option value="users">Utilisateurs standard</option>
                    <option value="admins">Administrateurs uniquement</option>
                  </select>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button 
                type="submit" 
                className="w-full"
                disabled={sending}
              >
                {sending ? (
                  <>
                    <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
                    Envoi en cours...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Envoyer la notification
                  </>
                )}
              </Button>
            </CardFooter>
          </form>
        </Card>
        
        {/* Notifications history */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle>Historique des notifications</CardTitle>
              <CardDescription>
                Notifications envoyées récemment
              </CardDescription>
            </div>
            <Button 
              variant="outline" 
              size="icon" 
              onClick={fetchNotifications} 
              disabled={loading}
              title="Actualiser"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-6">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-current border-t-transparent"></div>
                  <p className="mt-2 text-sm text-muted-foreground">Chargement des notifications...</p>
                </div>
              ) : displayNotifications.length === 0 ? (
                <div className="text-center py-6">
                  <Bell className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <p className="mt-2 text-sm text-muted-foreground">Aucune notification envoyée</p>
                </div>
              ) : (
                displayNotifications.map((notification) => (
                  <div 
                    key={notification._id} 
                    className="border rounded-md p-4 space-y-2 relative"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex items-center">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getBadgeColor(notification.type)}`}>
                          {notification.type === 'info' ? 'Information' : 
                           notification.type === 'warning' ? 'Avertissement' : 
                           notification.type === 'error' ? 'Erreur' : 'Succès'}
                        </span>
                        <span className="text-xs text-muted-foreground ml-2">
                          {notification.recipients === 'all' ? 'Tous' : 
                           notification.recipients === 'users' ? 'Utilisateurs' : 'Admins'}
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(notification._id)}
                        title="Supprimer"
                        className="h-6 w-6"
                      >
                        <Trash className="h-3 w-3" />
                      </Button>
                    </div>
                    
                    <div>
                      <h4 className="font-medium">{notification.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">
                        {notification.message}
                      </p>
                    </div>
                    
                    <div className="flex justify-between items-center text-xs text-muted-foreground">
                      <div>
                        {formatDate(notification.createdAt)}
                        {notification.createdBy && ` par ${notification.createdBy}`}
                      </div>
                      {notification.read !== undefined && (
                        <div>
                          Lu par {notification.read} utilisateurs
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Notifications; 
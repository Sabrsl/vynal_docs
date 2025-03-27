import React, { useState } from 'react';
import './Navbar.css';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';

const Navbar = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const { success, error, warning, info } = useNotification();
  const [showNotifications, setShowNotifications] = useState(false);

  const handleBellClick = () => {
    // Exemple d'utilisation des notifications
    success(
      'Nouvelle notification',
      'Vous avez reçu un nouveau message',
      5000
    );
    
    warning(
      'Attention',
      'Votre espace de stockage est presque plein',
      8000
    );
    
    info(
      'Information',
      'Une mise à jour est disponible',
      5000
    );
    
    error(
      'Erreur',
      'Impossible de synchroniser les documents',
      5000
    );
  };

  return (
    <header className="navbar">
      {children}
    </header>
  );
};

export default Navbar; 
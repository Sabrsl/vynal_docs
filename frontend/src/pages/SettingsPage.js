import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useAppContext } from '../context/AppContext';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import './SettingsPage.css';

const SettingsPage = () => {
  const { user, isAuthenticated } = useAuth();
  const { darkMode, toggleDarkMode, userSettings, updateUserSettings } = useAppContext();
  
  const [generalSettings, setGeneralSettings] = useState({
    language: 'fr',
    notificationsEnabled: true,
    autoSave: true,
    saveInterval: 5
  });
  
  const [profileSettings, setProfileSettings] = useState({
    name: user?.name || '',
    email: user?.email || '',
    avatar: user?.avatar || ''
  });
  
  const [securitySettings, setSecuritySettings] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [activeTab, setActiveTab] = useState('general');
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  
  // Synchroniser les paramètres généraux avec ceux du contexte
  useEffect(() => {
    setGeneralSettings(userSettings);
  }, [userSettings]);
  
  // Synchroniser les paramètres du profil avec ceux de l'utilisateur
  useEffect(() => {
    if (user) {
      setProfileSettings({
        name: user.name || '',
        email: user.email || '',
        avatar: user.avatar || ''
      });
    }
  }, [user]);
  
  const handleGeneralSettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setGeneralSettings({
      ...generalSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleProfileSettingsChange = (e) => {
    const { name, value } = e.target;
    setProfileSettings({
      ...profileSettings,
      [name]: value
    });
  };
  
  const handleSecuritySettingsChange = (e) => {
    const { name, value } = e.target;
    setSecuritySettings({
      ...securitySettings,
      [name]: value
    });
  };
  
  const handleGeneralSubmit = (e) => {
    e.preventDefault();
    
    // Mettre à jour les paramètres dans le contexte
    updateUserSettings(generalSettings);
    
    // Afficher un message de succès
    setSaveStatus({
      type: 'success',
      message: 'Paramètres généraux mis à jour avec succès !'
    });
    
    // Effacer le message après 3 secondes
    setTimeout(() => {
      setSaveStatus({ type: '', message: '' });
    }, 3000);
  };
  
  const handleProfileSubmit = (e) => {
    e.preventDefault();
    
    // Simuler la mise à jour du profil (dans une application réelle, appel API)
    setSaveStatus({
      type: 'success',
      message: 'Profil mis à jour avec succès !'
    });
    
    // Effacer le message après 3 secondes
    setTimeout(() => {
      setSaveStatus({ type: '', message: '' });
    }, 3000);
  };
  
  const handleSecuritySubmit = (e) => {
    e.preventDefault();
    
    // Vérifier que les mots de passe correspondent
    if (securitySettings.newPassword !== securitySettings.confirmPassword) {
      setSaveStatus({
        type: 'error',
        message: 'Les mots de passe ne correspondent pas !'
      });
      return;
    }
    
    // Simuler le changement de mot de passe (dans une application réelle, appel API)
    setSaveStatus({
      type: 'success',
      message: 'Mot de passe modifié avec succès !'
    });
    
    // Réinitialiser le formulaire
    setSecuritySettings({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    
    // Effacer le message après 3 secondes
    setTimeout(() => {
      setSaveStatus({ type: '', message: '' });
    }, 3000);
  };
  
  if (!isAuthenticated) {
    return (
      <div className="settings-page">
        <Card>
          <div className="settings-message">
            <i className="bx bx-lock"></i>
            <h2>Accès refusé</h2>
            <p>Vous devez être connecté pour accéder aux paramètres.</p>
          </div>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Paramètres</h1>
        <p>Configurez votre espace de travail selon vos préférences</p>
      </div>
      
      {saveStatus.message && (
        <div className={`settings-alert ${saveStatus.type}`}>
          <i className={`bx ${saveStatus.type === 'success' ? 'bx-check-circle' : 'bx-error-circle'}`}></i>
          {saveStatus.message}
        </div>
      )}
      
      <div className="settings-container">
        <div className="settings-sidebar">
          <div 
            className={`settings-tab ${activeTab === 'general' ? 'active' : ''}`}
            onClick={() => setActiveTab('general')}
          >
            <i className="bx bx-cog"></i>
            <span>Général</span>
          </div>
          <div 
            className={`settings-tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <i className="bx bx-user"></i>
            <span>Profil</span>
          </div>
          <div 
            className={`settings-tab ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            <i className="bx bx-lock-alt"></i>
            <span>Sécurité</span>
          </div>
        </div>
        
        <div className="settings-content">
          {activeTab === 'general' && (
            <Card>
              <h2>Paramètres généraux</h2>
              <form onSubmit={handleGeneralSubmit}>
                <div className="settings-group">
                  <label>Langue</label>
                  <select 
                    name="language" 
                    value={generalSettings.language}
                    onChange={handleGeneralSettingsChange}
                    className="settings-select"
                  >
                    <option value="fr">Français</option>
                    <option value="en">English</option>
                    <option value="es">Español</option>
                    <option value="de">Deutsch</option>
                  </select>
                </div>
                
                <div className="settings-group">
                  <div className="settings-toggle">
                    <label htmlFor="theme">Thème sombre</label>
                    <div className="toggle-switch">
                      <input 
                        type="checkbox" 
                        id="theme" 
                        checked={darkMode}
                        onChange={toggleDarkMode}
                      />
                      <label htmlFor="theme"></label>
                    </div>
                  </div>
                </div>
                
                <div className="settings-group">
                  <div className="settings-toggle">
                    <label htmlFor="notifications">Notifications</label>
                    <div className="toggle-switch">
                      <input 
                        type="checkbox" 
                        id="notifications" 
                        name="notificationsEnabled"
                        checked={generalSettings.notificationsEnabled}
                        onChange={handleGeneralSettingsChange}
                      />
                      <label htmlFor="notifications"></label>
                    </div>
                  </div>
                </div>
                
                <div className="settings-group">
                  <div className="settings-toggle">
                    <label htmlFor="autosave">Sauvegarde automatique</label>
                    <div className="toggle-switch">
                      <input 
                        type="checkbox" 
                        id="autosave" 
                        name="autoSave"
                        checked={generalSettings.autoSave}
                        onChange={handleGeneralSettingsChange}
                      />
                      <label htmlFor="autosave"></label>
                    </div>
                  </div>
                </div>
                
                {generalSettings.autoSave && (
                  <div className="settings-group">
                    <label>Intervalle de sauvegarde (minutes)</label>
                    <input 
                      type="number" 
                      name="saveInterval"
                      min="1" 
                      max="60" 
                      value={generalSettings.saveInterval}
                      onChange={handleGeneralSettingsChange}
                      className="settings-input"
                    />
                  </div>
                )}
                
                <div className="settings-actions">
                  <Button type="submit">Enregistrer</Button>
                </div>
              </form>
            </Card>
          )}
          
          {activeTab === 'profile' && (
            <Card>
              <h2>Profil utilisateur</h2>
              <form onSubmit={handleProfileSubmit}>
                <div className="profile-avatar">
                  <img src={profileSettings.avatar || '/avatar.svg'} alt="Avatar" />
                  <Button variant="outlined" size="small">Changer l'avatar</Button>
                </div>
                
                <div className="settings-group">
                  <label htmlFor="name">Nom complet</label>
                  <Input 
                    type="text" 
                    id="name" 
                    name="name"
                    value={profileSettings.name}
                    onChange={handleProfileSettingsChange}
                    placeholder="Votre nom"
                    required
                  />
                </div>
                
                <div className="settings-group">
                  <label htmlFor="email">Adresse email</label>
                  <Input 
                    type="email" 
                    id="email" 
                    name="email"
                    value={profileSettings.email}
                    onChange={handleProfileSettingsChange}
                    placeholder="votre@email.com"
                    required
                  />
                </div>
                
                <div className="settings-actions">
                  <Button type="submit">Mettre à jour</Button>
                </div>
              </form>
            </Card>
          )}
          
          {activeTab === 'security' && (
            <Card>
              <h2>Sécurité</h2>
              <form onSubmit={handleSecuritySubmit}>
                <div className="settings-group">
                  <label htmlFor="currentPassword">Mot de passe actuel</label>
                  <Input 
                    type="password" 
                    id="currentPassword" 
                    name="currentPassword"
                    value={securitySettings.currentPassword}
                    onChange={handleSecuritySettingsChange}
                    placeholder="Votre mot de passe actuel"
                    required
                  />
                </div>
                
                <div className="settings-group">
                  <label htmlFor="newPassword">Nouveau mot de passe</label>
                  <Input 
                    type="password" 
                    id="newPassword" 
                    name="newPassword"
                    value={securitySettings.newPassword}
                    onChange={handleSecuritySettingsChange}
                    placeholder="Nouveau mot de passe"
                    required
                  />
                </div>
                
                <div className="settings-group">
                  <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
                  <Input 
                    type="password" 
                    id="confirmPassword" 
                    name="confirmPassword"
                    value={securitySettings.confirmPassword}
                    onChange={handleSecuritySettingsChange}
                    placeholder="Confirmez le nouveau mot de passe"
                    required
                  />
                </div>
                
                <div className="settings-actions">
                  <Button type="submit">Changer le mot de passe</Button>
                </div>
              </form>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 
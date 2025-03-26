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
    theme: 'dark',
    notificationsEnabled: true,
    autoSave: true,
    saveInterval: 5,
    companyName: 'Vynal Agency LTD',
    companyLogo: ''
  });
  
  const [storageSettings, setStorageSettings] = useState({
    backupEnabled: false,
    autoBackupInterval: 7,
    backupCount: 5,
    backupFormat: 'zip'
  });
  
  const [uiSettings, setUiSettings] = useState({
    fontSize: 'medium',
    showTooltips: true,
    enableAnimations: true,
    sidebarWidth: 200,
    borderRadius: 10
  });
  
  const [documentSettings, setDocumentSettings] = useState({
    defaultFormat: 'pdf',
    filenamePattern: '{document_type}_{client_name}_{date}',
    dateFormat: '%Y-%m-%d',
    autoDetectVariables: true,
    showDocumentPreview: true,
    defaultDocumentLocale: 'fr_FR'
  });
  
  const [securitySettings, setSecuritySettings] = useState({
    requireLogin: true,
    sessionTimeout: 30,
    requireStrongPassword: true,
    maxLoginAttempts: 5,
    lockoutDuration: 15,
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [adminSettings, setAdminSettings] = useState({
    debugMode: false,
    logLevel: 'INFO',
    logRetention: 30,
    maxLogSize: 10,
    remoteAccess: false
  });
  
  const [profileSettings, setProfileSettings] = useState({
    name: user?.name || '',
    email: user?.email || '',
    avatar: user?.avatar || ''
  });
  
  const [activeTab, setActiveTab] = useState('general');
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  
  // Synchroniser les paramètres avec ceux du contexte
  useEffect(() => {
    if (userSettings) {
      setGeneralSettings({
        language: userSettings.language || 'fr',
        theme: userSettings.theme || 'dark',
        notificationsEnabled: userSettings.notificationsEnabled || true,
        autoSave: userSettings.autoSave || true,
        saveInterval: userSettings.saveInterval || 5,
        companyName: userSettings.companyName || 'Vynal Agency LTD',
        companyLogo: userSettings.companyLogo || ''
      });
      
      setStorageSettings({
        backupEnabled: userSettings.backupEnabled || false,
        autoBackupInterval: userSettings.autoBackupInterval || 7,
        backupCount: userSettings.backupCount || 5,
        backupFormat: userSettings.backupFormat || 'zip'
      });
      
      setUiSettings({
        fontSize: userSettings.fontSize || 'medium',
        showTooltips: userSettings.showTooltips || true,
        enableAnimations: userSettings.enableAnimations || true,
        sidebarWidth: userSettings.sidebarWidth || 200,
        borderRadius: userSettings.borderRadius || 10
      });
      
      setDocumentSettings({
        defaultFormat: userSettings.defaultFormat || 'pdf',
        filenamePattern: userSettings.filenamePattern || '{document_type}_{client_name}_{date}',
        dateFormat: userSettings.dateFormat || '%Y-%m-%d',
        autoDetectVariables: userSettings.autoDetectVariables || true,
        showDocumentPreview: userSettings.showDocumentPreview || true,
        defaultDocumentLocale: userSettings.defaultDocumentLocale || 'fr_FR'
      });
      
      setSecuritySettings({
        requireLogin: userSettings.requireLogin || true,
        sessionTimeout: userSettings.sessionTimeout || 30,
        requireStrongPassword: userSettings.requireStrongPassword || true,
        maxLoginAttempts: userSettings.maxLoginAttempts || 5,
        lockoutDuration: userSettings.lockoutDuration || 15,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      
      setAdminSettings({
        debugMode: userSettings.debugMode || false,
        logLevel: userSettings.logLevel || 'INFO',
        logRetention: userSettings.logRetention || 30,
        maxLogSize: userSettings.maxLogSize || 10,
        remoteAccess: userSettings.remoteAccess || false
      });
    }
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
  
  const handleStorageSettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setStorageSettings({
      ...storageSettings,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value
    });
  };
  
  const handleUiSettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setUiSettings({
      ...uiSettings,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value
    });
  };
  
  const handleDocumentSettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setDocumentSettings({
      ...documentSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleAdminSettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setAdminSettings({
      ...adminSettings,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value
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
    const { name, value, type, checked } = e.target;
    setSecuritySettings({
      ...securitySettings,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value
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
  
  const handleStorageSubmit = (e) => {
    e.preventDefault();
    
    // Mettre à jour les paramètres dans le contexte
    updateUserSettings(storageSettings);
    
    // Afficher un message de succès
    setSaveStatus({
      type: 'success',
      message: 'Paramètres de stockage mis à jour avec succès !'
    });
    
    // Effacer le message après 3 secondes
    setTimeout(() => {
      setSaveStatus({ type: '', message: '' });
    }, 3000);
  };
  
  const handleUiSubmit = (e) => {
    e.preventDefault();
    
    // Mettre à jour les paramètres dans le contexte
    updateUserSettings(uiSettings);
    
    // Afficher un message de succès
    setSaveStatus({
      type: 'success',
      message: 'Paramètres d\'interface mis à jour avec succès !'
    });
    
    // Effacer le message après 3 secondes
    setTimeout(() => {
      setSaveStatus({ type: '', message: '' });
    }, 3000);
  };
  
  const handleDocumentSubmit = (e) => {
    e.preventDefault();
    
    // Mettre à jour les paramètres dans le contexte
    updateUserSettings(documentSettings);
    
    // Afficher un message de succès
    setSaveStatus({
      type: 'success',
      message: 'Paramètres des documents mis à jour avec succès !'
    });
    
    // Effacer le message après 3 secondes
    setTimeout(() => {
      setSaveStatus({ type: '', message: '' });
    }, 3000);
  };
  
  const handleAdminSubmit = (e) => {
    e.preventDefault();
    
    // Mettre à jour les paramètres dans le contexte
    updateUserSettings(adminSettings);
    
    // Afficher un message de succès
    setSaveStatus({
      type: 'success',
      message: 'Paramètres d\'administration mis à jour avec succès !'
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
    
    // Filtrer les champs de mot de passe pour ne pas les envoyer au contexte
    const { currentPassword, newPassword, confirmPassword, ...securityConfig } = securitySettings;
    
    // Mettre à jour les paramètres dans le contexte
    updateUserSettings(securityConfig);
    
    // Simuler le changement de mot de passe (dans une application réelle, appel API)
    setSaveStatus({
      type: 'success',
      message: 'Paramètres de sécurité mis à jour avec succès !'
    });
    
    // Réinitialiser les champs de mot de passe
    setSecuritySettings({
      ...securitySettings,
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
            className={`settings-tab ${activeTab === 'document' ? 'active' : ''}`}
            onClick={() => setActiveTab('document')}
          >
            <i className="bx bx-file"></i>
            <span>Documents</span>
          </div>
          <div 
            className={`settings-tab ${activeTab === 'storage' ? 'active' : ''}`}
            onClick={() => setActiveTab('storage')}
          >
            <i className="bx bx-data"></i>
            <span>Stockage</span>
          </div>
          <div 
            className={`settings-tab ${activeTab === 'ui' ? 'active' : ''}`}
            onClick={() => setActiveTab('ui')}
          >
            <i className="bx bx-palette"></i>
            <span>Interface</span>
          </div>
          <div 
            className={`settings-tab ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            <i className="bx bx-lock-alt"></i>
            <span>Sécurité</span>
          </div>
          <div 
            className={`settings-tab ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => setActiveTab('admin')}
          >
            <i className="bx bx-shield-quarter"></i>
            <span>Administration</span>
          </div>
        </div>
        
        <div className="settings-content">
          {activeTab === 'general' && (
            <Card>
              <h2>Paramètres généraux</h2>
              <form onSubmit={handleGeneralSubmit}>
                <div className="settings-group">
                  <label htmlFor="companyName">Nom de l'entreprise</label>
                  <Input 
                    type="text" 
                    id="companyName" 
                    name="companyName"
                    value={generalSettings.companyName}
                    onChange={handleGeneralSettingsChange}
                    placeholder="Nom de votre entreprise"
                  />
                </div>
                
                <div className="settings-group">
                  <label htmlFor="companyLogo">Logo de l'entreprise</label>
                  <div className="file-input-container">
                    <input 
                      type="text" 
                      readOnly 
                      value={generalSettings.companyLogo || "Aucun fichier sélectionné"}
                      className="settings-input"
                    />
                    <Button 
                      variant="outlined" 
                      size="small"
                      onClick={() => alert("Fonctionnalité en développement")}
                    >
                      Parcourir
                    </Button>
                  </div>
                </div>
                
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
                  <div className="settings-group settings-indented">
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
                
                <div className="settings-group">
                  <div className="settings-toggle">
                    <label htmlFor="confirmExit">Confirmer la sortie</label>
                    <div className="toggle-switch">
                      <input 
                        type="checkbox" 
                        id="confirmExit" 
                        name="confirmExit"
                        checked={generalSettings.confirmExit}
                        onChange={handleGeneralSettingsChange}
                      />
                      <label htmlFor="confirmExit"></label>
                    </div>
                  </div>
                </div>
                
                <div className="settings-group">
                  <div className="settings-toggle">
                    <label htmlFor="checkUpdates">Vérifier les mises à jour</label>
                    <div className="toggle-switch">
                      <input 
                        type="checkbox" 
                        id="checkUpdates" 
                        name="checkUpdates"
                        checked={generalSettings.checkUpdates}
                        onChange={handleGeneralSettingsChange}
                      />
                      <label htmlFor="checkUpdates"></label>
                    </div>
                  </div>
                </div>
                
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
          
          {activeTab === 'document' && (
            <Card>
              <h2>Paramètres des documents</h2>
              <form onSubmit={handleDocumentSubmit}>
                <div className="settings-section">
                  <h3 className="settings-subheader">Format et organisation</h3>
                  
                  <div className="settings-group">
                    <label>Format de document par défaut</label>
                    <select 
                      name="defaultFormat" 
                      value={documentSettings.defaultFormat}
                      onChange={handleDocumentSettingsChange}
                      className="settings-select"
                    >
                      <option value="pdf">PDF</option>
                      <option value="docx">DOCX</option>
                      <option value="txt">TXT</option>
                      <option value="html">HTML</option>
                      <option value="md">Markdown</option>
                    </select>
                  </div>
                  
                  <div className="settings-group">
                    <label>Modèle de nom de fichier</label>
                    <Input 
                      type="text" 
                      name="filenamePattern"
                      value={documentSettings.filenamePattern}
                      onChange={handleDocumentSettingsChange}
                      placeholder="Modèle de nom de fichier"
                    />
                    <small className="settings-help">
                      Utilisez {'{'}document_type{'}'}, {'{'}client_name{'}'}, {'{'}date{'}'} comme variables
                    </small>
                  </div>
                  
                  <div className="settings-group">
                    <label>Format de date</label>
                    <Input 
                      type="text" 
                      name="dateFormat"
                      value={documentSettings.dateFormat}
                      onChange={handleDocumentSettingsChange}
                      placeholder="Format de date"
                    />
                    <small className="settings-help">
                      Exemple: %Y-%m-%d pour 2023-12-31
                    </small>
                  </div>
                </div>
                
                <div className="settings-section">
                  <h3 className="settings-subheader">Fonctionnalités</h3>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="autoDetectVariables">Détection automatique des variables</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="autoDetectVariables" 
                          name="autoDetectVariables"
                          checked={documentSettings.autoDetectVariables}
                          onChange={handleDocumentSettingsChange}
                        />
                        <label htmlFor="autoDetectVariables"></label>
                      </div>
                    </div>
                  </div>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="showDocumentPreview">Afficher l'aperçu des documents</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="showDocumentPreview" 
                          name="showDocumentPreview"
                          checked={documentSettings.showDocumentPreview}
                          onChange={handleDocumentSettingsChange}
                        />
                        <label htmlFor="showDocumentPreview"></label>
                      </div>
                    </div>
                  </div>
                  
                  <div className="settings-group">
                    <label>Locale par défaut des documents</label>
                    <select 
                      name="defaultDocumentLocale" 
                      value={documentSettings.defaultDocumentLocale}
                      onChange={handleDocumentSettingsChange}
                      className="settings-select"
                    >
                      <option value="fr_FR">Français (France)</option>
                      <option value="fr_CA">Français (Canada)</option>
                      <option value="en_US">English (US)</option>
                      <option value="en_GB">English (UK)</option>
                      <option value="de_DE">Deutsch</option>
                      <option value="es_ES">Español</option>
                    </select>
                  </div>
                </div>
                
                <div className="settings-actions">
                  <Button type="submit">Enregistrer</Button>
                </div>
              </form>
            </Card>
          )}
          
          {activeTab === 'storage' && (
            <Card>
              <h2>Stockage et sauvegarde</h2>
              <form onSubmit={handleStorageSubmit}>
                <div className="settings-section">
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="backupEnabled">Sauvegardes automatiques</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="backupEnabled" 
                          name="backupEnabled"
                          checked={storageSettings.backupEnabled}
                          onChange={handleStorageSettingsChange}
                        />
                        <label htmlFor="backupEnabled"></label>
                      </div>
                    </div>
                    <small className="settings-help">
                      Active ou désactive les sauvegardes périodiques de vos documents
                    </small>
                  </div>
                  
                  {storageSettings.backupEnabled && (
                    <div className="settings-subsection">
                      <div className="settings-group settings-indented">
                        <label>Intervalle entre les sauvegardes (jours)</label>
                        <input 
                          type="number" 
                          name="autoBackupInterval"
                          min="1" 
                          max="90" 
                          value={storageSettings.autoBackupInterval}
                          onChange={handleStorageSettingsChange}
                          className="settings-input"
                        />
                      </div>
                      
                      <div className="settings-group settings-indented">
                        <label>Nombre de sauvegardes à conserver</label>
                        <input 
                          type="number" 
                          name="backupCount"
                          min="1" 
                          max="20" 
                          value={storageSettings.backupCount}
                          onChange={handleStorageSettingsChange}
                          className="settings-input"
                        />
                        <small className="settings-help">
                          Les anciennes sauvegardes seront supprimées au-delà de cette limite
                        </small>
                      </div>
                      
                      <div className="settings-group settings-indented">
                        <label>Format de sauvegarde</label>
                        <select 
                          name="backupFormat" 
                          value={storageSettings.backupFormat}
                          onChange={handleStorageSettingsChange}
                          className="settings-select"
                        >
                          <option value="zip">ZIP</option>
                          <option value="tar">TAR</option>
                          <option value="gz">GZ (compressé)</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="settings-actions">
                  <Button type="submit">Enregistrer</Button>
                </div>
              </form>
            </Card>
          )}
          
          {activeTab === 'ui' && (
            <Card>
              <h2>Interface utilisateur</h2>
              <form onSubmit={handleUiSubmit}>
                <div className="settings-section">
                  <h3 className="settings-subheader">Apparence</h3>
                  
                  <div className="settings-group">
                    <label>Taille de police</label>
                    <select 
                      name="fontSize" 
                      value={uiSettings.fontSize}
                      onChange={handleUiSettingsChange}
                      className="settings-select"
                    >
                      <option value="small">Petite</option>
                      <option value="medium">Moyenne</option>
                      <option value="large">Grande</option>
                    </select>
                  </div>
                  
                  <div className="settings-group">
                    <label>Rayon des bordures (px)</label>
                    <input 
                      type="number" 
                      name="borderRadius"
                      min="0" 
                      max="20" 
                      value={uiSettings.borderRadius}
                      onChange={handleUiSettingsChange}
                      className="settings-input"
                    />
                    <small className="settings-help">
                      Modifie l'arrondi des coins des éléments d'interface
                    </small>
                  </div>
                </div>
                
                <div className="settings-section">
                  <h3 className="settings-subheader">Comportement</h3>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="showTooltips">Afficher les info-bulles</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="showTooltips" 
                          name="showTooltips"
                          checked={uiSettings.showTooltips}
                          onChange={handleUiSettingsChange}
                        />
                        <label htmlFor="showTooltips"></label>
                      </div>
                    </div>
                  </div>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="enableAnimations">Activer les animations</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="enableAnimations" 
                          name="enableAnimations"
                          checked={uiSettings.enableAnimations}
                          onChange={handleUiSettingsChange}
                        />
                        <label htmlFor="enableAnimations"></label>
                      </div>
                    </div>
                  </div>
                  
                  <div className="settings-group">
                    <label>Largeur de la barre latérale (px)</label>
                    <input 
                      type="number" 
                      name="sidebarWidth"
                      min="150" 
                      max="300" 
                      value={uiSettings.sidebarWidth}
                      onChange={handleUiSettingsChange}
                      className="settings-input"
                    />
                  </div>
                </div>
                
                <div className="settings-actions">
                  <Button type="submit">Enregistrer</Button>
                </div>
              </form>
            </Card>
          )}
          
          {activeTab === 'security' && (
            <Card>
              <h2>Sécurité</h2>
              <form onSubmit={handleSecuritySubmit}>
                <div className="settings-section">
                  <h3 className="settings-subheader">Connexion et authentification</h3>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="requireLogin">Authentification obligatoire</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="requireLogin" 
                          name="requireLogin"
                          checked={securitySettings.requireLogin}
                          onChange={handleSecuritySettingsChange}
                        />
                        <label htmlFor="requireLogin"></label>
                      </div>
                    </div>
                  </div>
                  
                  <div className="settings-group">
                    <label>Délai d'inactivité (minutes)</label>
                    <input 
                      type="number" 
                      name="sessionTimeout"
                      min="5" 
                      max="120" 
                      value={securitySettings.sessionTimeout}
                      onChange={handleSecuritySettingsChange}
                      className="settings-input"
                    />
                    <small className="settings-help">
                      Durée après laquelle vous serez déconnecté automatiquement
                    </small>
                  </div>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="requireStrongPassword">Mots de passe forts obligatoires</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="requireStrongPassword" 
                          name="requireStrongPassword"
                          checked={securitySettings.requireStrongPassword}
                          onChange={handleSecuritySettingsChange}
                        />
                        <label htmlFor="requireStrongPassword"></label>
                      </div>
                    </div>
                  </div>
                  
                  <div className="settings-group">
                    <label>Nombre maximum de tentatives de connexion</label>
                    <input 
                      type="number" 
                      name="maxLoginAttempts"
                      min="1" 
                      max="10" 
                      value={securitySettings.maxLoginAttempts}
                      onChange={handleSecuritySettingsChange}
                      className="settings-input"
                    />
                  </div>
                  
                  <div className="settings-group">
                    <label>Durée de verrouillage (minutes)</label>
                    <input 
                      type="number" 
                      name="lockoutDuration"
                      min="5" 
                      max="60" 
                      value={securitySettings.lockoutDuration}
                      onChange={handleSecuritySettingsChange}
                      className="settings-input"
                    />
                    <small className="settings-help">
                      Durée de verrouillage après trop de tentatives échouées
                    </small>
                  </div>
                </div>
                
                <div className="settings-section">
                  <h3 className="settings-subheader">Changer le mot de passe</h3>
                  
                  <div className="settings-group">
                    <label htmlFor="currentPassword">Mot de passe actuel</label>
                    <Input 
                      type="password" 
                      id="currentPassword" 
                      name="currentPassword"
                      value={securitySettings.currentPassword}
                      onChange={handleSecuritySettingsChange}
                      placeholder="Votre mot de passe actuel"
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
                    />
                  </div>
                </div>
                
                <div className="settings-actions">
                  <Button type="submit">Enregistrer</Button>
                </div>
              </form>
            </Card>
          )}
          
          {activeTab === 'admin' && (
            <Card>
              <h2>Administration</h2>
              <form onSubmit={handleAdminSubmit}>
                <div className="settings-section">
                  <h3 className="settings-subheader">Journalisation et débogage</h3>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="debugMode">Mode débogage</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="debugMode" 
                          name="debugMode"
                          checked={adminSettings.debugMode}
                          onChange={handleAdminSettingsChange}
                        />
                        <label htmlFor="debugMode"></label>
                      </div>
                    </div>
                    <small className="settings-help">
                      Active des informations de débogage supplémentaires
                    </small>
                  </div>
                  
                  <div className="settings-group">
                    <label>Niveau de journalisation</label>
                    <select 
                      name="logLevel" 
                      value={adminSettings.logLevel}
                      onChange={handleAdminSettingsChange}
                      className="settings-select"
                    >
                      <option value="ERROR">ERROR</option>
                      <option value="WARNING">WARNING</option>
                      <option value="INFO">INFO</option>
                      <option value="DEBUG">DEBUG</option>
                    </select>
                  </div>
                  
                  <div className="settings-group">
                    <label>Conservation des journaux (jours)</label>
                    <input 
                      type="number" 
                      name="logRetention"
                      min="1" 
                      max="90" 
                      value={adminSettings.logRetention}
                      onChange={handleAdminSettingsChange}
                      className="settings-input"
                    />
                  </div>
                  
                  <div className="settings-group">
                    <label>Taille maximale des fichiers journaux (MB)</label>
                    <input 
                      type="number" 
                      name="maxLogSize"
                      min="1" 
                      max="100" 
                      value={adminSettings.maxLogSize}
                      onChange={handleAdminSettingsChange}
                      className="settings-input"
                    />
                  </div>
                </div>
                
                <div className="settings-section">
                  <h3 className="settings-subheader">Accès à distance</h3>
                  
                  <div className="settings-group">
                    <div className="settings-toggle">
                      <label htmlFor="remoteAccess">Accès à distance</label>
                      <div className="toggle-switch">
                        <input 
                          type="checkbox" 
                          id="remoteAccess" 
                          name="remoteAccess"
                          checked={adminSettings.remoteAccess}
                          onChange={handleAdminSettingsChange}
                        />
                        <label htmlFor="remoteAccess"></label>
                      </div>
                    </div>
                    <small className="settings-help">
                      Permet l'accès à distance pour l'assistance technique
                    </small>
                  </div>
                </div>
                
                <div className="settings-actions">
                  <Button type="submit">Enregistrer</Button>
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
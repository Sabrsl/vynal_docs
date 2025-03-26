import React, { createContext, useContext, useReducer, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

// Création du contexte
const AppContext = createContext();

// Initial state
const initialState = {
  documents: [],
  templates: [],
  categories: [],
  activities: [],
  users: [],
  activeDocument: null,
  activeSection: 'dashboard',
  isLoading: false,
  error: null,
  darkMode: false,
  userSettings: {
    language: 'fr',
    notifications: true,
    theme: 'light',
    autoSave: true,
    saveInterval: 5,
    companyName: 'Vynal Agency LTD',
    companyLogo: '',
    confirmExit: true,
    checkUpdates: true,
    
    // Stockage et sauvegarde
    backupEnabled: false,
    autoBackupInterval: 7,
    backupCount: 5,
    backupFormat: 'zip',
    
    // Interface utilisateur
    fontSize: 'medium',
    showTooltips: true,
    enableAnimations: true,
    sidebarWidth: 200,
    borderRadius: 10,
    
    // Document
    defaultFormat: 'pdf',
    filenamePattern: '{document_type}_{client_name}_{date}',
    dateFormat: '%Y-%m-%d',
    autoDetectVariables: true,
    showDocumentPreview: true,
    defaultDocumentLocale: 'fr_FR',
    
    // Sécurité
    requireLogin: true,
    sessionTimeout: 30,
    requireStrongPassword: true,
    maxLoginAttempts: 5,
    lockoutDuration: 15,
    
    // Administration
    debugMode: false,
    logLevel: 'INFO',
    logRetention: 30,
    maxLogSize: 10,
    remoteAccess: false
  }
};

// Reducer pour gérer les actions
const appReducer = (state, action) => {
  switch (action.type) {
    case 'SET_ACTIVE_SECTION':
      // Ne mettre à jour que si la section est différente
      if (state.activeSection === action.payload) {
        return state;
      }
      return {
        ...state,
        activeSection: action.payload
      };
    case 'FETCH_DOCUMENTS_START':
      return {
        ...state,
        isLoading: true,
        error: null
      };
    case 'FETCH_DOCUMENTS_SUCCESS':
      return {
        ...state,
        documents: action.payload,
        isLoading: false
      };
    case 'FETCH_DOCUMENTS_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false
      };
    case 'SET_ACTIVE_DOCUMENT':
      return {
        ...state,
        activeDocument: action.payload
      };
    case 'ADD_DOCUMENT':
      return {
        ...state,
        documents: [action.payload, ...state.documents],
        isLoading: false
      };
    case 'UPDATE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.map(doc => 
          doc.id === action.payload.id ? action.payload : doc
        ),
        isLoading: false
      };
    case 'DELETE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.filter(doc => doc.id !== action.payload),
        isLoading: false
      };
    case 'FETCH_TEMPLATES_SUCCESS':
      return {
        ...state,
        templates: action.payload
      };
    case 'FETCH_ACTIVITIES_SUCCESS':
      return {
        ...state,
        activities: action.payload
      };
    case 'TOGGLE_DARK_MODE':
      return {
        ...state,
        darkMode: !state.darkMode
      };
    case 'UPDATE_USER_SETTINGS':
      return {
        ...state,
        userSettings: {
          ...state.userSettings,
          ...action.payload
        }
      };
    default:
      return state;
  }
};

// Provider component
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const { user, isAuthenticated } = useAuth();
  
  // Fonction pour charger les données utilisateur
  const fetchUserData = async () => {
    if (!isAuthenticated || !user) return;
    
    try {
      // Utiliser des données fictives standards si l'utilisateur existe
      const userId = 1; // Utiliser un ID fixe au lieu de user.id qui peut causer des erreurs
      
      // Données fictives pour les documents
      const documentsData = [
        { id: 101, userId: userId, title: 'Rapport annuel 2024', modified: '2h', type: 'document', views: 24, content: 'Contenu du rapport...' },
        { id: 102, userId: userId, title: 'Présentation client', modified: '5h', type: 'presentation', views: 15, content: 'Contenu de la présentation...' },
        { id: 103, userId: userId, title: 'Données financières Q1', modified: '12h', type: 'spreadsheet', views: 8, content: 'Données financières...' },
        { id: 104, userId: userId, title: 'Plan de projet', modified: '1j', type: 'document', views: 32, content: 'Plan détaillé du projet...' },
        // Inclure les documents actuellement présents dans l'état
        ...state.documents.filter(doc => {
          // Filtrer pour éviter les doublons
          return !([101, 102, 103, 104].includes(doc.id));
        })
      ];
      
      // Données fictives pour les templates
      const templatesData = [
        { id: 110, userId: userId, title: 'Contrat de prestation', modified: '2j', type: 'document', views: 18, content: 'Template de contrat...' },
        { id: 111, userId: userId, title: 'Facture standard', modified: '5j', type: 'document', views: 27, content: 'Template de facture...' },
        { id: 112, userId: userId, title: 'Rapport technique', modified: '1s', type: 'document', views: 12, content: 'Template de rapport technique...' },
        { id: 113, userId: userId, title: 'Cahier des charges', modified: '2s', type: 'document', views: 8, content: 'Template de cahier des charges...' },
        // Inclure les templates actuellement présents dans l'état
        ...state.templates.filter(tmpl => {
          // Filtrer pour éviter les doublons
          return !([110, 111, 112, 113].includes(tmpl.id));
        })
      ];
      
      // Activités existantes et nouvelles
      const activitiesData = [
        { id: 101, userId: userId, user: 'Jean Dupont', action: 'a créé un document', document: 'Rapport annuel 2024', documentId: 101, time: '2h' },
        { id: 102, userId: userId, user: 'Jean Dupont', action: 'a modifié', document: 'Présentation client', documentId: 102, time: '5h' },
        { id: 103, userId: userId, user: 'Jean Dupont', action: 'a partagé', document: 'Données financières Q1', documentId: 103, time: '12h' },
        { id: 104, userId: userId, user: 'Jean Dupont', action: 'a supprimé', document: 'Ancien brouillon', documentId: null, time: '1j' },
        { id: 105, userId: userId, user: 'Jean Dupont', action: 'a commenté sur', document: 'Plan de projet', documentId: 104, time: '2j' },
        // Inclure les activités actuellement présentes dans l'état
        ...state.activities.filter(act => {
          // Filtrer pour éviter les doublons
          return !([101, 102, 103, 104, 105].includes(act.id));
        })
      ];
      
      dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: documentsData });
      dispatch({ type: 'FETCH_TEMPLATES_SUCCESS', payload: templatesData });
      dispatch({ type: 'FETCH_ACTIVITIES_SUCCESS', payload: activitiesData });
    } catch (error) {
      console.error("Erreur dans fetchUserData:", error);
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors du chargement des données' });
    }
  };
  
  // Simuler le chargement des données liées à l'utilisateur connecté
  useEffect(() => {
    if (isAuthenticated && user) {
      dispatch({ type: 'FETCH_DOCUMENTS_START' });
      fetchUserData();
    } else {
      // Réinitialiser les données si l'utilisateur est déconnecté
      dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: [] });
      dispatch({ type: 'FETCH_TEMPLATES_SUCCESS', payload: [] });
      dispatch({ type: 'FETCH_ACTIVITIES_SUCCESS', payload: [] });
    }
  }, [isAuthenticated, user]);
  
  // Mettre en place un rafraîchissement automatique des données
  useEffect(() => {
    if (!isAuthenticated || !user) return;
    
    // Rafraîchissement toutes les 30 secondes
    const refreshInterval = setInterval(() => {
      fetchUserData();
    }, 30000);
    
    // Nettoyer l'intervalle à la désinscription
    return () => clearInterval(refreshInterval);
  }, [isAuthenticated, user, state.documents.length, state.activities.length]);
  
  // Rafraîchir les données après une action utilisateur
  const refreshData = () => {
    if (isAuthenticated && user) {
      fetchUserData();
    }
  };

  // Charger les paramètres utilisateur depuis le localStorage si disponibles
  useEffect(() => {
    const savedSettings = localStorage.getItem('userSettings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        dispatch({ type: 'UPDATE_USER_SETTINGS', payload: parsedSettings });
      } catch (error) {
        console.error('Erreur lors du chargement des paramètres utilisateur:', error);
      }
    }
    
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode !== null) {
      const isDarkMode = savedDarkMode === 'true';
      if (isDarkMode !== state.darkMode) {
        dispatch({ type: 'TOGGLE_DARK_MODE' });
      }
    }
  }, []);
  
  // Effet pour appliquer le dark mode
  useEffect(() => {
    if (state.darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    
    // Sauvegarder le paramètre dans localStorage
    localStorage.setItem('darkMode', state.darkMode);
  }, [state.darkMode]);
  
  // Créer un document
  const createDocument = async (newDoc) => {
    if (!isAuthenticated) {
      throw new Error('Utilisateur non authentifié');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Utiliser un ID statique
      const userId = 1;
      
      // Générer un identifiant fixe pour le document
      const newId = `doc-${Date.now()}`;
      const timestamp = new Date().toISOString();
      const newDocument = {
        id: newId,
        userId: userId,
        title: newDoc.title,
        type: newDoc.type || 'document',
        content: newDoc.content || '',
        created: timestamp,
        modified: '1 minute',
        views: 0,
        isTemplate: newDoc.isTemplate || false
      };
      
      dispatch({ type: 'ADD_DOCUMENT', payload: newDocument });
      
      // Ajouter une activité pour ce document
      const newActivity = {
        id: `activity-${Date.now()}`,
        userId: userId,
        user: 'Jean Dupont',
        type: newDoc.isTemplate ? 'template_created' : 'document_created',
        action: newDoc.isTemplate ? 'a créé un modèle' : 'a créé un document',
        document: newDocument.title,
        documentId: newDocument.id,
        time: 'À l\'instant'
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
      
      // S'assurer que l'état de chargement est réinitialisé
      dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: [...state.documents, newDocument] });
      
      // Rafraîchir les données pour mettre à jour les tableaux
      setTimeout(refreshData, 1000);
      
      return newDocument;
    } catch (error) {
      console.error("Erreur dans createDocument:", error);
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors de la création du document' });
      throw error;
    }
  };
  
  // Mettre à jour un document
  const updateDocument = async (id, documentData) => {
    if (!isAuthenticated) {
      throw new Error('Utilisateur non authentifié');
    }
    
    // Vérifier que le document existe
    const documentToUpdate = state.documents.find(doc => doc.id === id);
    if (!documentToUpdate) {
      throw new Error('Document non trouvé');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Utiliser un ID statique
      const userId = 1;
      
      const updatedDocument = {
        ...documentToUpdate,
        ...documentData,
        modified: 'À l\'instant'
      };
      
      dispatch({ type: 'UPDATE_DOCUMENT', payload: updatedDocument });
      
      // Ajouter une activité pour cette mise à jour
      const newActivity = {
        id: Date.now(),
        userId: userId,
        user: 'Jean Dupont',
        action: 'a modifié',
        document: updatedDocument.title,
        documentId: updatedDocument.id,
        time: 'À l\'instant'
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
      
      // S'assurer que l'état de chargement est réinitialisé
      dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: state.documents.map(doc => 
        doc.id === updatedDocument.id ? updatedDocument : doc
      )});
      
      // Rafraîchir les données pour mettre à jour les tableaux
      setTimeout(refreshData, 1000);
      
      return updatedDocument;
    } catch (error) {
      console.error("Erreur dans updateDocument:", error);
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors de la mise à jour du document' });
      throw error;
    }
  };
  
  // Supprimer un document
  const deleteDocument = async (id) => {
    if (!isAuthenticated) {
      throw new Error('Utilisateur non authentifié');
    }
    
    // Vérifier que le document existe
    const documentToDelete = state.documents.find(doc => doc.id === id);
    if (!documentToDelete) {
      throw new Error('Document non trouvé');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Utiliser un ID statique
      const userId = 1;
      
      dispatch({ type: 'DELETE_DOCUMENT', payload: id });
      
      // Ajouter une activité pour cette suppression
      const newActivity = {
        id: Date.now(),
        userId: userId,
        user: 'Jean Dupont',
        action: 'a supprimé',
        document: documentToDelete.title,
        documentId: null,
        time: 'À l\'instant'
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
      
      // S'assurer que l'état de chargement est réinitialisé
      dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: state.documents.filter(doc => doc.id !== id) });
      
      // Rafraîchir les données pour mettre à jour les tableaux
      setTimeout(refreshData, 1000);
      
      return id;
    } catch (error) {
      console.error("Erreur dans deleteDocument:", error);
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors de la suppression du document' });
      throw error;
    }
  };
  
  // Mettre à jour la section active
  const setActiveSection = (section) => {
    if (section === state.activeSection) return; // Éviter les re-renders inutiles
    dispatch({ type: 'SET_ACTIVE_SECTION', payload: section });
  };
  
  // Ouvrir un document
  const openDocument = (document) => {
    // Simplifier la vérification
    if (!document) {
      throw new Error('Document non valide');
    }
    
    dispatch({ type: 'SET_ACTIVE_DOCUMENT', payload: document });
    
    // Ajouter une activité pour cette ouverture si ce n'est pas déjà le document actif
    if (state.activeDocument?.id !== document.id) {
      const userId = 1;
      
      const newActivity = {
        id: Date.now(),
        userId: userId,
        user: 'Jean Dupont',
        action: 'a consulté',
        document: document.title,
        documentId: document.id,
        time: 'À l\'instant'
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
    }
  };
  
  // Partager un document avec un autre utilisateur
  const shareDocument = async (documentId, targetUserId) => {
    if (!isAuthenticated) {
      throw new Error('Utilisateur non authentifié');
    }
    
    // Vérifier que le document existe
    const documentToShare = state.documents.find(doc => doc.id === documentId);
    if (!documentToShare) {
      throw new Error('Document non trouvé');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Utiliser un ID statique
      const userId = 1;
      
      // Mise à jour du document avec le partage
      const updatedDocument = {
        ...documentToShare,
        sharedWith: [...(documentToShare.sharedWith || []), targetUserId],
        modified: 'À l\'instant'
      };
      
      dispatch({ type: 'UPDATE_DOCUMENT', payload: updatedDocument });
      
      // Ajouter une activité pour ce partage
      const newActivity = {
        id: Date.now(),
        userId: userId,
        user: 'Jean Dupont',
        action: 'a partagé',
        document: documentToShare.title,
        documentId: documentToShare.id,
        time: 'À l\'instant'
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
      
      return updatedDocument;
    } catch (error) {
      console.error("Erreur dans shareDocument:", error);
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors du partage du document' });
      throw error;
    }
  };
  
  // Mettre à jour les paramètres utilisateur
  const updateUserSettings = (newSettings) => {
    dispatch({ type: 'UPDATE_USER_SETTINGS', payload: newSettings });
    
    // Sauvegarder les paramètres dans localStorage
    const updatedSettings = {
      ...state.userSettings,
      ...newSettings
    };
    localStorage.setItem('userSettings', JSON.stringify(updatedSettings));
  };
  
  // Basculer le mode sombre
  const toggleDarkMode = () => {
    dispatch({ type: 'TOGGLE_DARK_MODE' });
  };
  
  // Valeur exposée par le contexte
  const value = {
    ...state,
    createDocument,
    updateDocument,
    deleteDocument,
    setActiveSection,
    openDocument,
    shareDocument,
    updateUserSettings,
    toggleDarkMode,
    refreshData
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Hook personnalisé pour utiliser le contexte
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext doit être utilisé à l\'intérieur d\'un AppProvider');
  }
  return context;
}; 
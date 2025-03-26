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
  error: null
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
        documents: [action.payload, ...state.documents]
      };
    case 'UPDATE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.map(doc => 
          doc.id === action.payload.id ? action.payload : doc
        )
      };
    case 'DELETE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.filter(doc => doc.id !== action.payload)
      };
    case 'FETCH_ACTIVITIES_SUCCESS':
      return {
        ...state,
        activities: action.payload
      };
    default:
      return state;
  }
};

// Provider component
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const { user, isAuthenticated } = useAuth();
  
  // Simuler le chargement des données liées à l'utilisateur connecté
  useEffect(() => {
    if (isAuthenticated && user) {
      dispatch({ type: 'FETCH_DOCUMENTS_START' });
      
      // Simuler un appel API
      const fetchUserData = async () => {
        try {
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Générer des données spécifiques à l'utilisateur connecté
          const userId = user.id;
          
          // Données fictives pour les documents - liées à l'utilisateur connecté
          const documentsData = [
            { id: userId*100 + 1, userId: userId, title: 'Rapport annuel 2024', modified: '2h', type: 'document', views: 24, content: 'Contenu du rapport...' },
            { id: userId*100 + 2, userId: userId, title: 'Présentation client', modified: '5h', type: 'presentation', views: 15, content: 'Contenu de la présentation...' },
            { id: userId*100 + 3, userId: userId, title: 'Données financières Q1', modified: '12h', type: 'spreadsheet', views: 8, content: 'Données financières...' },
            { id: userId*100 + 4, userId: userId, title: 'Plan de projet', modified: '1j', type: 'document', views: 32, content: 'Plan détaillé du projet...' }
          ];
          
          // Données fictives pour les activités - liées à l'utilisateur connecté
          const activitiesData = [
            { id: userId*100 + 1, userId: userId, user: user.name, action: 'a créé un document', document: 'Rapport annuel 2024', documentId: userId*100 + 1, time: '2h' },
            { id: userId*100 + 2, userId: userId, user: user.name, action: 'a modifié', document: 'Présentation client', documentId: userId*100 + 2, time: '5h' },
            { id: userId*100 + 3, userId: userId, user: user.name, action: 'a partagé', document: 'Données financières Q1', documentId: userId*100 + 3, time: '12h' },
            { id: userId*100 + 4, userId: userId, user: user.name, action: 'a supprimé', document: 'Ancien brouillon', documentId: null, time: '1j' },
            { id: userId*100 + 5, userId: userId, user: user.name, action: 'a commenté sur', document: 'Plan de projet', documentId: userId*100 + 4, time: '2j' }
          ];
          
          dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: documentsData });
          dispatch({ type: 'FETCH_ACTIVITIES_SUCCESS', payload: activitiesData });
        } catch (error) {
          dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors du chargement des données' });
        }
      };
      
      fetchUserData();
    } else {
      // Réinitialiser les données si l'utilisateur est déconnecté
      dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: [] });
      dispatch({ type: 'FETCH_ACTIVITIES_SUCCESS', payload: [] });
    }
  }, [isAuthenticated, user]);
  
  // Créer un document
  const createDocument = async (newDoc) => {
    if (!isAuthenticated || !user) {
      throw new Error('Utilisateur non authentifié');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const timestamp = new Date().toISOString();
      const newDocument = {
        id: `doc-${Date.now()}`,
        userId: user.id,
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
        userId: user.id,
        type: newDoc.isTemplate ? 'template_created' : 'document_created',
        documentId: newDocument.id,
        documentTitle: newDocument.title,
        timestamp,
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
      
      return newDocument;
    } catch (error) {
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors de la création du document' });
      throw error;
    }
  };
  
  // Mettre à jour un document
  const updateDocument = async (id, documentData) => {
    if (!isAuthenticated || !user) {
      throw new Error('Utilisateur non authentifié');
    }
    
    // Vérifier que l'utilisateur est bien propriétaire du document
    const documentToUpdate = state.documents.find(doc => doc.id === id);
    if (!documentToUpdate || documentToUpdate.userId !== user.id) {
      throw new Error('Vous n\'avez pas les droits pour modifier ce document');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const updatedDocument = {
        ...documentToUpdate,
        ...documentData,
        modified: 'À l\'instant'
      };
      
      dispatch({ type: 'UPDATE_DOCUMENT', payload: updatedDocument });
      
      // Ajouter une activité pour cette mise à jour
      const newActivity = {
        id: Date.now(),
        userId: user.id,
        user: user.name,
        action: 'a modifié',
        document: updatedDocument.title,
        documentId: updatedDocument.id,
        time: 'À l\'instant'
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
      
      return updatedDocument;
    } catch (error) {
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors de la mise à jour du document' });
      throw error;
    }
  };
  
  // Supprimer un document
  const deleteDocument = async (id) => {
    if (!isAuthenticated || !user) {
      throw new Error('Utilisateur non authentifié');
    }
    
    // Vérifier que l'utilisateur est bien propriétaire du document
    const documentToDelete = state.documents.find(doc => doc.id === id);
    if (!documentToDelete || documentToDelete.userId !== user.id) {
      throw new Error('Vous n\'avez pas les droits pour supprimer ce document');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      dispatch({ type: 'DELETE_DOCUMENT', payload: id });
      
      // Ajouter une activité pour cette suppression
      const newActivity = {
        id: Date.now(),
        userId: user.id,
        user: user.name,
        action: 'a supprimé',
        document: documentToDelete.title,
        documentId: null,
        time: 'À l\'instant'
      };
      
      dispatch({ 
        type: 'FETCH_ACTIVITIES_SUCCESS', 
        payload: [newActivity, ...state.activities] 
      });
      
      return id;
    } catch (error) {
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
    // Vérifier que l'utilisateur est propriétaire du document ou a des droits de lecture
    if (!document || (document.userId !== user?.id && !document.sharedWith?.includes(user?.id))) {
      throw new Error('Vous n\'avez pas les droits pour accéder à ce document');
    }
    
    dispatch({ type: 'SET_ACTIVE_DOCUMENT', payload: document });
    
    // Ajouter une activité pour cette ouverture si ce n'est pas déjà le document actif
    if (state.activeDocument?.id !== document.id) {
      const newActivity = {
        id: Date.now(),
        userId: user.id,
        user: user.name,
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
    if (!isAuthenticated || !user) {
      throw new Error('Utilisateur non authentifié');
    }
    
    // Vérifier que l'utilisateur est bien propriétaire du document
    const documentToShare = state.documents.find(doc => doc.id === documentId);
    if (!documentToShare || documentToShare.userId !== user.id) {
      throw new Error('Vous n\'avez pas les droits pour partager ce document');
    }
    
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
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
        userId: user.id,
        user: user.name,
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
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors du partage du document' });
      throw error;
    }
  };
  
  // Valeur exposée par le contexte
  const value = {
    ...state,
    createDocument,
    updateDocument,
    deleteDocument,
    setActiveSection,
    openDocument,
    shareDocument
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
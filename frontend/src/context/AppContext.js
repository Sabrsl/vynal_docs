import React, { createContext, useContext, useReducer, useState, useEffect } from 'react';

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
  
  // Simuler le chargement des données
  useEffect(() => {
    const fetchInitialData = async () => {
      dispatch({ type: 'FETCH_DOCUMENTS_START' });
      try {
        // Simuler un appel API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Données fictives pour les documents
        const documentsData = [
          { id: 1, title: 'Rapport annuel 2024', modified: '2h', type: 'document', views: 24, content: 'Contenu du rapport...' },
          { id: 2, title: 'Présentation client', modified: '5h', type: 'presentation', views: 15, content: 'Contenu de la présentation...' },
          { id: 3, title: 'Données financières Q1', modified: '12h', type: 'spreadsheet', views: 8, content: 'Données financières...' },
          { id: 4, title: 'Plan de projet', modified: '1j', type: 'document', views: 32, content: 'Plan détaillé du projet...' }
        ];
        
        // Données fictives pour les activités
        const activitiesData = [
          { id: 1, user: 'John Doe', action: 'a créé un document', document: 'Rapport annuel 2024', documentId: 1, time: '2h' },
          { id: 2, user: 'Alice Smith', action: 'a modifié', document: 'Présentation client', documentId: 2, time: '5h' },
          { id: 3, user: 'Robert Johnson', action: 'a partagé', document: 'Données financières Q1', documentId: 3, time: '12h' },
          { id: 4, user: 'Emma Wilson', action: 'a supprimé', document: 'Ancien brouillon', documentId: null, time: '1j' },
          { id: 5, user: 'Michael Brown', action: 'a commenté sur', document: 'Plan de projet', documentId: 4, time: '2j' }
        ];
        
        dispatch({ type: 'FETCH_DOCUMENTS_SUCCESS', payload: documentsData });
        dispatch({ type: 'FETCH_ACTIVITIES_SUCCESS', payload: activitiesData });
      } catch (error) {
        dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors du chargement des données' });
      }
    };
    
    fetchInitialData();
  }, []);
  
  // Créer un document
  const createDocument = async (documentData) => {
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const newDocument = {
        id: Date.now(),
        ...documentData,
        modified: 'À l\'instant',
        views: 0
      };
      
      dispatch({ type: 'ADD_DOCUMENT', payload: newDocument });
      return newDocument;
    } catch (error) {
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors de la création du document' });
      throw error;
    }
  };
  
  // Mettre à jour un document
  const updateDocument = async (id, documentData) => {
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const updatedDocument = {
        ...state.documents.find(doc => doc.id === id),
        ...documentData,
        modified: 'À l\'instant'
      };
      
      dispatch({ type: 'UPDATE_DOCUMENT', payload: updatedDocument });
      return updatedDocument;
    } catch (error) {
      dispatch({ type: 'FETCH_DOCUMENTS_ERROR', payload: 'Erreur lors de la mise à jour du document' });
      throw error;
    }
  };
  
  // Supprimer un document
  const deleteDocument = async (id) => {
    dispatch({ type: 'FETCH_DOCUMENTS_START' });
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      dispatch({ type: 'DELETE_DOCUMENT', payload: id });
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
    dispatch({ type: 'SET_ACTIVE_DOCUMENT', payload: document });
  };
  
  // Valeur exposée par le contexte
  const value = {
    ...state,
    createDocument,
    updateDocument,
    deleteDocument,
    setActiveSection,
    openDocument
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
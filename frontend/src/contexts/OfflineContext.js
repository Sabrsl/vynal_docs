import React, { createContext, useContext, useState, useEffect } from 'react';
import { getDocumentsDB, getTemplatesDB, getCategoriesDB } from '../utils/offlineDB';

// Créer le contexte
const OfflineContext = createContext();

// Hook personnalisé pour utiliser le contexte
export const useOffline = () => useContext(OfflineContext);

// Fournisseur du contexte
export const OfflineProvider = ({ children }) => {
  // Initialiser les bases de données au montage du composant
  const [dbs, setDbs] = useState({
    documents: null,
    templates: null,
    categories: null
  });
  
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [syncStatus, setSyncStatus] = useState('idle');
  const [syncProgress, setSyncProgress] = useState(0);
  const [syncErrors, setSyncErrors] = useState([]);
  const [hasConflicts, setHasConflicts] = useState(false);
  const [conflicts, setConflicts] = useState([]);
  
  // Initialiser les bases de données
  useEffect(() => {
    const initDBs = () => {
      try {
        setDbs({
          documents: getDocumentsDB(),
          templates: getTemplatesDB(),
          categories: getCategoriesDB()
        });
      } catch (error) {
        console.error('Erreur lors de l\'initialisation des bases de données:', error);
        setSyncErrors(prev => [...prev, error]);
      }
    };
    
    initDBs();
  }, []);

  // Mettre à jour le statut de connexion
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setSyncStatus('connecting');
    };

    const handleOffline = () => {
      setIsOnline(false);
      setSyncStatus('offline');
    };

    // Écouter les événements de connexion du navigateur
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Écouter les événements de la base de données
    const handleDBChange = (event) => {
      console.log('DB change event:', event.detail);
    };

    const handleDBSyncing = () => {
      setSyncStatus('syncing');
    };

    const handleDBPaused = () => {
      setSyncStatus('idle');
      checkForConflicts();
    };

    const handleDBError = (event) => {
      console.error('Sync error:', event.detail);
      setSyncErrors(prev => [...prev, event.detail]);
      setSyncStatus('error');
    };

    window.addEventListener('db:change', handleDBChange);
    window.addEventListener('db:active', handleDBSyncing);
    window.addEventListener('db:paused', handleDBPaused);
    window.addEventListener('db:error', handleDBError);

    // Nettoyer les écouteurs d'événements
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('db:change', handleDBChange);
      window.removeEventListener('db:active', handleDBSyncing);
      window.removeEventListener('db:paused', handleDBPaused);
      window.removeEventListener('db:error', handleDBError);
    };
  }, []);

  // Vérifier les conflits de synchronisation
  const checkForConflicts = async () => {
    try {
      const { documents, templates, categories } = dbs;
      
      if (!documents || !templates || !categories) {
        console.warn('Les bases de données ne sont pas encore initialisées');
        return [];
      }
      
      // Vérifier les conflits dans les différentes bases de données
      const documentConflicts = await documents.checkConflicts();
      const templateConflicts = await templates.checkConflicts();
      const categoryConflicts = await categories.checkConflicts();
      
      // Combiner tous les conflits
      const allConflicts = [
        ...documentConflicts.map(conflict => ({ ...conflict, type: 'document' })),
        ...templateConflicts.map(conflict => ({ ...conflict, type: 'template' })),
        ...categoryConflicts.map(conflict => ({ ...conflict, type: 'category' }))
      ];
      
      setConflicts(allConflicts);
      setHasConflicts(allConflicts.length > 0);
      
      return allConflicts;
    } catch (error) {
      console.error('Error checking for conflicts:', error);
      return [];
    }
  };

  // Résoudre automatiquement les conflits (utilise la stratégie par défaut)
  const resolveAllConflicts = async () => {
    try {
      const results = [];
      const { documents, templates, categories } = dbs;
      
      if (!documents || !templates || !categories) {
        throw new Error('Les bases de données ne sont pas encore initialisées');
      }
      
      // Résoudre les conflits pour chaque type de données
      for (const conflict of conflicts) {
        let db;
        switch (conflict.type) {
          case 'document':
            db = documents;
            break;
          case 'template':
            db = templates;
            break;
          case 'category':
            db = categories;
            break;
          default:
            continue;
        }
        
        const result = await db.resolveConflict(conflict.doc._id);
        results.push(result);
      }
      
      // Mettre à jour l'état après la résolution
      await checkForConflicts();
      
      return results;
    } catch (error) {
      console.error('Error resolving conflicts:', error);
      throw error;
    }
  };

  // Forcer une synchronisation manuelle de toutes les bases de données
  const syncAll = async () => {
    if (!isOnline) {
      throw new Error('Cannot synchronize while offline');
    }

    const { documents, templates, categories } = dbs;
    
    if (!documents || !templates || !categories) {
      throw new Error('Les bases de données ne sont pas encore initialisées');
    }

    setSyncStatus('syncing');
    setSyncProgress(0);
    
    try {
      // Synchroniser les différentes bases de données
      const promises = [
        documents.syncNow(),
        templates.syncNow(),
        categories.syncNow()
      ];
      
      // Mettre à jour la progression
      const results = await Promise.all(promises.map(async (promise, index, array) => {
        const result = await promise;
        setSyncProgress(((index + 1) / array.length) * 100);
        return result;
      }));
      
      setSyncStatus('idle');
      setSyncProgress(100);
      
      // Vérifier les conflits après la synchronisation
      await checkForConflicts();
      
      return results;
    } catch (error) {
      setSyncStatus('error');
      setSyncErrors(prev => [...prev, error]);
      throw error;
    }
  };

  // Démarrer la synchronisation pour toutes les bases de données
  const startSyncAll = () => {
    const { documents, templates, categories } = dbs;
    
    if (!documents || !templates || !categories) {
      console.warn('Les bases de données ne sont pas encore initialisées');
      return;
    }
    
    documents.startSync();
    templates.startSync();
    categories.startSync();
    setSyncStatus('syncing');
  };

  // Arrêter la synchronisation pour toutes les bases de données
  const stopSyncAll = () => {
    const { documents, templates, categories } = dbs;
    
    if (!documents || !templates || !categories) {
      console.warn('Les bases de données ne sont pas encore initialisées');
      return;
    }
    
    documents.stopSync();
    templates.stopSync();
    categories.stopSync();
    setSyncStatus('stopped');
  };

  // Effacer les erreurs de synchronisation
  const clearSyncErrors = () => {
    setSyncErrors([]);
  };

  // Récupérer les statuts de toutes les bases de données
  const getDBStatus = () => {
    const { documents, templates, categories } = dbs;
    
    if (!documents || !templates || !categories) {
      return {
        documents: { isOnline: false, syncStatus: 'not_initialized' },
        templates: { isOnline: false, syncStatus: 'not_initialized' },
        categories: { isOnline: false, syncStatus: 'not_initialized' }
      };
    }
    
    return {
      documents: documents.getStatus(),
      templates: templates.getStatus(),
      categories: categories.getStatus()
    };
  };

  // Réinitialiser toutes les bases de données locales
  const resetAllDBs = async () => {
    try {
      const { documents, templates, categories } = dbs;
      
      if (!documents || !templates || !categories) {
        throw new Error('Les bases de données ne sont pas encore initialisées');
      }
      
      await documents.reset();
      await templates.reset();
      await categories.reset();
      
      setSyncErrors([]);
      setConflicts([]);
      setHasConflicts(false);
      setSyncStatus('idle');
      
      return { success: true };
    } catch (error) {
      console.error('Error resetting databases:', error);
      throw error;
    }
  };

  // Valeurs exposées par le contexte
  const value = {
    isOnline,
    syncStatus,
    syncProgress,
    syncErrors,
    hasConflicts,
    conflicts,
    syncAll,
    startSyncAll,
    stopSyncAll,
    checkForConflicts,
    resolveAllConflicts,
    clearSyncErrors,
    getDBStatus,
    resetAllDBs,
    dbs
  };

  return (
    <OfflineContext.Provider value={value}>
      {children}
    </OfflineContext.Provider>
  );
};

export default OfflineContext; 
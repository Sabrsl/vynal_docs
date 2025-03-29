import PouchDB from 'pouchdb';
import PouchDBFind from 'pouchdb-find';
import PouchDBBrowser from 'pouchdb-browser';

// Pour débogage - Afficher les versions de PouchDB et des plugins
console.log('PouchDB version:', PouchDB.version);
console.log('Modules PouchDB chargés:', {
  core: !!PouchDB,
  find: !!PouchDBFind,
  browser: !!PouchDBBrowser
});

// Configuration de la version de base de PouchDB
const setupPouchDB = () => {
  try {
    // Enregistrer les plugins dans un ordre spécifique
    PouchDB.plugin(PouchDBBrowser);
    PouchDB.plugin(PouchDBFind);
    
    console.log('PouchDB configuré avec succès avec tous les plugins');
    return true;
  } catch (error) {
    console.error('Erreur lors de la configuration de PouchDB:', error);
    return false;
  }
};

// Initialiser PouchDB
const pouchdbReady = setupPouchDB();

// URL du serveur pour la réplication - adaptable selon le contexte
const REMOTE_DB_URL = process.env.NODE_ENV === 'production' 
  ? `${window.location.origin}/api/db` 
  : 'http://localhost:5000/api/db';

// Classe pour gérer les opérations de base de données offline
class OfflineDB {
  constructor(dbName) {
    // Vérifier que PouchDB est correctement configuré
    if (!pouchdbReady) {
      throw new Error('PouchDB n\'est pas correctement configuré');
    }
    
    // Vérifier et valider le nom de la base de données
    if (!dbName || typeof dbName !== 'string' || dbName.trim() === '') {
      throw new Error('Un nom de base de données valide est requis');
    }
    
    // Sanitize le nom de la base pour éviter les caractères problématiques
    const sanitizedName = dbName.trim().toLowerCase().replace(/[^a-z0-9_$()+/-]/gi, '_');
    this.dbName = sanitizedName;
    
    // Création de la base de données locale
    try {
      this.localDB = new PouchDB(sanitizedName);
    } catch (error) {
      console.error(`Erreur lors de l'initialisation de la base de données locale "${sanitizedName}":`, error);
      throw error;
    }
    
    // Création de la base de données distante (différé si en mode hors ligne)
    this.remoteDB = null;
    this.remoteDBUrl = `${REMOTE_DB_URL}/${sanitizedName}`;
    
    this.syncHandler = null;
    this.isOnline = navigator.onLine;
    this.syncStatus = 'idle';
    this.syncErrors = [];

    // Écouter les événements de connexion
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));
    
    // Si nous sommes en ligne, essayer d'initialiser la base distante
    if (this.isOnline) {
      try {
        this.initRemoteDB();
      } catch (error) {
        console.warn('Impossible de se connecter au serveur, fonctionnement en mode hors ligne uniquement');
      }
    }
  }
  
  // Initialise la base de données distante
  initRemoteDB() {
    if (!this.remoteDB && this.isOnline) {
      try {
        this.remoteDB = new PouchDB(this.remoteDBUrl, {
          skip_setup: true, // Ne pas essayer de créer la base distante si elle n'existe pas
          ajax: {
            timeout: 5000 // Timeout plus court pour détecter rapidement les problèmes
          }
        });
        
        // Tester la connexion avant de confirmer que la base distante est disponible
        this.remoteDB.info()
          .then(() => {
            console.log(`Base de données distante connectée: ${this.remoteDBUrl}`);
            this.startSync();
          })
          .catch(error => {
            console.warn(`Serveur inaccessible ou base distante inexistante: ${error.message}`);
            this.remoteDB = null; // Réinitialiser pour fonctionner en mode hors ligne
          });
      } catch (error) {
        console.error(`Erreur lors de l'initialisation de la base distante "${this.remoteDBUrl}":`, error);
        this.syncErrors.push(error);
        this.remoteDB = null;
      }
    }
    return this.remoteDB;
  }

  // Gérer l'événement de retour en ligne
  handleOnline() {
    this.isOnline = true;
    
    // Initialiser la base distante si nécessaire
    this.initRemoteDB();
    
    // Émettre un événement personnalisé
    window.dispatchEvent(new CustomEvent('db:online'));
  }

  // Gérer l'événement de perte de connexion
  handleOffline() {
    this.isOnline = false;
    // Arrêter la synchronisation continue si elle est active
    if (this.syncHandler) {
      this.syncHandler.cancel();
      this.syncHandler = null;
    }
    this.syncStatus = 'offline';
    
    // Émettre un événement personnalisé
    window.dispatchEvent(new CustomEvent('db:offline'));
  }

  // Démarrer la synchronisation bidirectionnelle
  startSync() {
    if (!this.isOnline || !this.remoteDB) {
      return;
    }
    
    this.syncStatus = 'syncing';
    
    try {
      // Configurer la synchronisation bidirectionnelle
      this.syncHandler = this.localDB.sync(this.remoteDB, {
        live: true,  // Synchronisation continue
        retry: true, // Réessayer en cas d'échec
        batch_size: 10, // Taille des lots pour le transfert
        timeout: 10000, // Timeout de 10 secondes pour chaque tentative
      })
      .on('change', (change) => {
        console.log('Sync change:', change);
        window.dispatchEvent(new CustomEvent('db:change', { detail: change }));
      })
      .on('paused', () => {
        this.syncStatus = 'idle';
        window.dispatchEvent(new CustomEvent('db:paused'));
      })
      .on('active', () => {
        this.syncStatus = 'syncing';
        window.dispatchEvent(new CustomEvent('db:active'));
      })
      .on('denied', (err) => {
        console.error('Sync denied:', err);
        this.syncErrors.push(err);
        window.dispatchEvent(new CustomEvent('db:error', { detail: err }));
      })
      .on('complete', (info) => {
        this.syncStatus = 'completed';
        window.dispatchEvent(new CustomEvent('db:complete', { detail: info }));
      })
      .on('error', (err) => {
        console.error('Sync error:', err);
        this.syncStatus = 'error';
        this.syncErrors.push(err);
        window.dispatchEvent(new CustomEvent('db:error', { detail: err }));
        
        // Si l'erreur indique que le serveur est inaccessible, passer en mode hors ligne
        if (err.status && (err.status === 0 || err.status >= 500)) {
          this.remoteDB = null;
          console.warn('Serveur inaccessible, passage en mode hors ligne');
        }
      });
    } catch (error) {
      console.error('Failed to start sync:', error);
      this.syncStatus = 'error';
      this.syncErrors.push(error);
    }
  }

  // Arrêter la synchronisation
  stopSync() {
    if (this.syncHandler) {
      this.syncHandler.cancel();
      this.syncHandler = null;
      this.syncStatus = 'stopped';
    }
  }

  // Créer un document
  async create(doc) {
    try {
      if (!doc._id) {
        doc._id = new Date().toISOString();
      }
      const response = await this.localDB.put({
        ...doc,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        _sync: {
          status: 'pending',
          lastSync: null
        }
      });
      return response;
    } catch (error) {
      console.error('Error creating document:', error);
      throw error;
    }
  }

  // Mettre à jour un document
  async update(doc) {
    try {
      // Récupérer la dernière version du document
      const existingDoc = await this.localDB.get(doc._id);
      
      // Mettre à jour le document
      const updatedDoc = {
        ...existingDoc,
        ...doc,
        updatedAt: new Date().toISOString(),
        _sync: {
          ...existingDoc._sync,
          status: 'pending'
        }
      };
      
      const response = await this.localDB.put(updatedDoc);
      return response;
    } catch (error) {
      console.error('Error updating document:', error);
      throw error;
    }
  }

  // Supprimer un document
  async delete(docId) {
    try {
      const doc = await this.localDB.get(docId);
      const response = await this.localDB.remove(doc);
      return response;
    } catch (error) {
      console.error('Error deleting document:', error);
      throw error;
    }
  }

  // Récupérer un document par son ID
  async get(docId) {
    try {
      return await this.localDB.get(docId);
    } catch (error) {
      console.error('Error getting document:', error);
      throw error;
    }
  }

  // Récupérer tous les documents
  async getAll() {
    try {
      const result = await this.localDB.allDocs({
        include_docs: true
      });
      return result.rows.map(row => row.doc);
    } catch (error) {
      console.error('Error getting all documents:', error);
      throw error;
    }
  }

  // Rechercher des documents
  async find(query) {
    try {
      // Créer un index si nécessaire
      await this.localDB.createIndex({
        index: { fields: Object.keys(query.selector) }
      });
      
      // Effectuer la recherche
      const result = await this.localDB.find(query);
      return result.docs;
    } catch (error) {
      console.error('Error finding documents:', error);
      throw error;
    }
  }

  // Forcer une synchronisation ponctuelle
  async syncNow() {
    if (!this.isOnline) {
      return { success: false, message: 'Cannot synchronize while offline' };
    }

    // S'assurer que la base distante est initialisée
    if (!this.remoteDB) {
      try {
        this.initRemoteDB();
      } catch (error) {
        return { success: false, message: 'Serveur inaccessible, mode hors ligne uniquement' };
      }
    }

    if (!this.remoteDB) {
      return { success: false, message: 'Serveur inaccessible, mode hors ligne uniquement' };
    }

    try {
      this.syncStatus = 'syncing';
      const result = await this.localDB.sync(this.remoteDB);
      this.syncStatus = 'idle';
      return { success: true, message: 'Synchronisation réussie', result };
    } catch (error) {
      this.syncStatus = 'error';
      this.syncErrors.push(error);
      console.error('Sync error:', error);
      return { success: false, message: `Erreur de synchronisation: ${error.message}` };
    }
  }

  // Vérifier les conflits de synchronisation
  async checkConflicts() {
    try {
      const result = await this.localDB.allDocs({
        include_docs: true,
        conflicts: true
      });
      
      const conflicts = result.rows.filter(row => row.doc._conflicts);
      return conflicts;
    } catch (error) {
      console.error('Error checking conflicts:', error);
      throw error;
    }
  }

  // Résoudre un conflit (stratégie simple : garder la version la plus récente)
  async resolveConflict(docId) {
    try {
      const doc = await this.localDB.get(docId, { conflicts: true });
      
      if (!doc._conflicts) {
        return { resolved: false, message: 'No conflicts found' };
      }
      
      // Récupérer toutes les versions conflictuelles
      const conflictVersions = await Promise.all(
        doc._conflicts.map(rev => this.localDB.get(docId, { rev }))
      );
      
      // Trouver la version la plus récente en comparant les timestamps
      const allVersions = [doc, ...conflictVersions];
      allVersions.sort((a, b) => {
        return new Date(b.updatedAt) - new Date(a.updatedAt);
      });
      
      const winningDoc = allVersions[0];
      
      // Supprimer les révisions perdantes
      await Promise.all(
        doc._conflicts.map(rev => this.localDB.remove(docId, rev))
      );
      
      return {
        resolved: true,
        winningDoc,
        message: 'Conflict resolved by keeping the most recent version'
      };
    } catch (error) {
      console.error('Error resolving conflict:', error);
      throw error;
    }
  }

  // Obtenir le statut actuel de la synchronisation
  getStatus() {
    return {
      isOnline: this.isOnline,
      syncStatus: this.syncStatus,
      syncErrors: this.syncErrors,
      hasRemoteDB: !!this.remoteDB
    };
  }

  // Effacer les données locales et recharger depuis le serveur
  async reset() {
    try {
      // Arrêter la synchronisation si elle est active
      this.stopSync();
      
      // Détruire la base de données locale
      await this.localDB.destroy();
      
      // Recréer la base de données locale
      this.localDB = new PouchDB(this.dbName);
      
      // Si le serveur est accessible, tenter une réplication depuis la base distante
      if (this.isOnline && this.remoteDB) {
        try {
          await this.localDB.replicate.from(this.remoteDB);
          this.startSync();
          return { success: true, message: 'Base réinitialisée et synchronisée avec le serveur' };
        } catch (error) {
          console.warn('Impossible de synchroniser avec le serveur après réinitialisation:', error);
          return { success: true, message: 'Base locale réinitialisée, mais le serveur est inaccessible' };
        }
      }
      
      return { success: true, message: 'Base locale réinitialisée avec succès' };
    } catch (error) {
      console.error('Erreur lors de la réinitialisation de la base de données:', error);
      throw error;
    }
  }
}

// Exporter un singleton pour chaque type de données
const dbInstances = {};

export const getOfflineDB = (dbName) => {
  // Vérifier si PouchDB est prêt
  if (!pouchdbReady) {
    console.error('PouchDB n\'est pas correctement configuré, impossible de créer la base de données');
    return null;
  }
  
  // Vérifier et valider le nom de la base de données
  if (!dbName || typeof dbName !== 'string' || dbName.trim() === '') {
    console.error('getOfflineDB: Nom de base de données invalide:', dbName);
    return null;
  }
  
  // Sanitize le nom pour l'utiliser comme clé
  const sanitizedName = dbName.trim().toLowerCase().replace(/[^a-z0-9_$()+/-]/gi, '_');
  
  if (!dbInstances[sanitizedName]) {
    try {
      dbInstances[sanitizedName] = new OfflineDB(sanitizedName);
    } catch (error) {
      console.error(`Erreur lors de la création de la base de données "${sanitizedName}":`, error);
      return null;
    }
  }
  return dbInstances[sanitizedName];
};

// Bases de données par défaut - création reportée pour éviter les erreurs d'initialisation
// Au lieu d'exporter directement les instances, nous exportons des getters
const getDocumentsDB = () => getOfflineDB('documents');
const getTemplatesDB = () => getOfflineDB('templates');
const getCategoriesDB = () => getOfflineDB('categories');
const getUserSettingsDB = () => getOfflineDB('user_settings');

// Exporter les getters
export { getDocumentsDB, getTemplatesDB, getCategoriesDB, getUserSettingsDB };

export default OfflineDB; 
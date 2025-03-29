import { 
  getDocumentsDB, 
  getTemplatesDB, 
  getCategoriesDB 
} from './offlineDB';

/**
 * Service API qui gère les appels réseau avec support du mode hors ligne
 * Utilise PouchDB en priorité et bascule vers les appels API standards si en ligne
 */
class ApiService {
  constructor() {
    this.apiUrl = process.env.NODE_ENV === 'production' 
      ? '/api' 
      : 'http://localhost:5000/api';
    this.isOnline = navigator.onLine;
    
    // Initialiser les bases de données
    this.dbs = {
      documents: null,
      templates: null,
      categories: null
    };
    
    // Initialiser les bases de données quand le service est créé
    this.initDatabases();
    
    // Écouter les changements de statut de connexion
    window.addEventListener('online', () => { 
      this.isOnline = true;
      console.log('API Service: Connexion réseau disponible');
    });
    window.addEventListener('offline', () => { 
      this.isOnline = false;
      console.log('API Service: Mode hors ligne activé');
    });
  }
  
  /**
   * Initialise les bases de données
   */
  initDatabases() {
    try {
      this.dbs.documents = getDocumentsDB();
      this.dbs.templates = getTemplatesDB();  
      this.dbs.categories = getCategoriesDB();
      console.log('Bases de données initialisées dans apiService:', this.dbs);
    } catch (error) {
      console.error('Erreur lors de l\'initialisation des bases de données:', error);
    }
  }

  /**
   * Obtient la base de données PouchDB correspondant au type de données
   * @param {string} type - Type de données (documents, templates, categories, etc.)
   * @returns {Object} - Instance PouchDB
   */
  getDBForType(type) {
    // Si la base n'est pas initialisée, on essaie de la réinitialiser
    if (!this.dbs[type]) {
      this.initDatabases();
    }
    
    // Si toujours pas disponible, on lève une erreur
    if (!this.dbs[type]) {
      throw new Error(`Type de données non supporté ou base de données non disponible: ${type}`);
    }
    
    return this.dbs[type];
  }

  /**
   * Effectue une requête HTTP
   * @param {string} endpoint - Point d'API
   * @param {Object} options - Options de la requête
   * @returns {Promise<any>} - Résultat de la requête
   */
  async fetchAPI(endpoint, options = {}) {
    if (!this.isOnline) {
      throw new Error('Impossible d\'effectuer des appels API en mode hors ligne');
    }
    
    try {
      const response = await fetch(`${this.apiUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la requête API:', error);
      throw error;
    }
  }

  /**
   * Obtenir tous les éléments d'un type spécifique
   * @param {string} type - Type de données (documents, templates, categories)
   * @returns {Promise<Array>} - Liste des éléments
   */
  async getAll(type) {
    try {
      // Essayer d'abord d'utiliser la base locale
      let localData = [];
      
      try {
        if (this.dbs[type]) {
          const db = this.getDBForType(type);
          localData = await db.getAll();
        }
      } catch (dbError) {
        console.warn(`Erreur d'accès à la base ${type} locale:`, dbError);
      }
      
      // Si en ligne, essayer également l'API
      if (this.isOnline) {
        try {
          const apiData = await this.fetchAPI(`/${type}`);
          
          // Si nous avons accès à la base locale, synchroniser les données
          if (this.dbs[type]) {
            const db = this.getDBForType(type);
            
            // Mettre à jour la base locale avec les données du serveur
            for (const item of apiData) {
              try {
                // Vérifier si l'élément existe déjà localement
                await db.get(item._id);
                // Mise à jour si pas d'édition locale en attente
                await db.update(item);
              } catch (error) {
                // Si l'élément n'existe pas, l'ajouter
                if (error.name === 'not_found') {
                  await db.create(item);
                }
              }
            }
            
            // Récupérer les données actualisées
            return await db.getAll();
          }
          
          return apiData;
        } catch (apiError) {
          console.warn('Erreur lors de la récupération depuis l\'API:', apiError);
          
          // Si nous avons des données locales, les utiliser même si l'API a échoué
          if (localData.length > 0) {
            return localData;
          }
          
          throw apiError;
        }
      }
      
      // En mode hors ligne ou si l'API a échoué, utiliser les données locales
      if (localData.length > 0) {
        return localData;
      }
      
      throw new Error(`Impossible de récupérer les données ${type} - Mode hors ligne et base de données locale indisponible`);
    } catch (error) {
      console.error(`Erreur lors de la récupération des données ${type}:`, error);
      throw error;
    }
  }

  /**
   * Obtenir un élément par son ID
   * @param {string} type - Type de données
   * @param {string} id - ID de l'élément
   * @returns {Promise<Object>} - Élément trouvé
   */
  async getById(type, id) {
    // Essayer d'abord la version locale
    let localDoc = null;
    
    try {
      if (this.dbs[type]) {
        const db = this.getDBForType(type);
        localDoc = await db.get(id);
      }
    } catch (dbError) {
      if (dbError.name !== 'not_found') {
        console.warn(`Erreur d'accès à la base locale pour ${type}/${id}:`, dbError);
      }
    }
    
    // Si nous sommes en ligne, essayer aussi l'API
    if (this.isOnline) {
      try {
        const apiDoc = await this.fetchAPI(`/${type}/${id}`);
        
        // Si nous avons accès à la base locale, la mettre à jour
        if (this.dbs[type]) {
          try {
            const db = this.getDBForType(type);
            await db.update(apiDoc);
          } catch (updateError) {
            console.warn(`Impossible de mettre à jour la base locale avec ${type}/${id}:`, updateError);
          }
        }
        
        return apiDoc;
      } catch (apiError) {
        console.warn(`Erreur lors de la récupération de ${type}/${id} depuis l'API:`, apiError);
        
        // Si nous avons une version locale, l'utiliser
        if (localDoc) {
          return localDoc;
        }
        
        throw apiError;
      }
    }
    
    // En mode hors ligne, utiliser la version locale
    if (localDoc) {
      return localDoc;
    }
    
    throw new Error(`Impossible de récupérer ${type}/${id} - Mode hors ligne et document non trouvé localement`);
  }

  /**
   * Créer un nouvel élément
   * @param {string} type - Type de données
   * @param {Object} data - Données de l'élément
   * @returns {Promise<Object>} - Élément créé
   */
  async create(type, data) {
    // Préparer l'élément avec les métadonnées nécessaires
    const newItem = {
      ...data,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    // Si nous sommes en ligne, essayer d'abord l'API
    if (this.isOnline) {
      try {
        const apiResult = await this.fetchAPI(`/${type}`, {
          method: 'POST',
          body: JSON.stringify(newItem)
        });
        
        // Si nous avons accès à la base locale, la mettre à jour
        if (this.dbs[type]) {
          try {
            const db = this.getDBForType(type);
            await db.create(apiResult);
          } catch (dbError) {
            console.warn(`Impossible d'enregistrer ${type} dans la base locale:`, dbError);
          }
        }
        
        return apiResult;
      } catch (apiError) {
        console.warn(`Erreur lors de la création via l'API:`, apiError);
        // Si l'API échoue et que nous avons une base locale, on continue
      }
    }
    
    // En mode hors ligne ou si l'API a échoué, utiliser la base locale
    if (this.dbs[type]) {
      try {
        const db = this.getDBForType(type);
        
        // Marquer l'élément comme devant être synchronisé lorsque possible
        const itemToSave = {
          ...newItem,
          _sync: { 
            status: 'pending', 
            isNew: true, 
            createdAt: new Date().toISOString() 
          }
        };
        
        const result = await db.create(itemToSave);
        const createdDoc = await db.get(result.id);
        
        return createdDoc;
      } catch (dbError) {
        console.error(`Erreur lors de la création dans la base locale:`, dbError);
        throw dbError;
      }
    }
    
    throw new Error(`Impossible de créer un élément ${type} - Mode hors ligne et base de données locale indisponible`);
  }

  /**
   * Mettre à jour un élément existant
   * @param {string} type - Type de données
   * @param {string} id - ID de l'élément
   * @param {Object} data - Nouvelles données
   * @returns {Promise<Object>} - Élément mis à jour
   */
  async update(type, id, data) {
    // Préparer l'élément avec les métadonnées nécessaires
    const updateData = {
      ...data,
      _id: id,
      updatedAt: new Date().toISOString()
    };
    
    // Si nous sommes en ligne, essayer d'abord l'API
    if (this.isOnline) {
      try {
        const apiResult = await this.fetchAPI(`/${type}/${id}`, {
          method: 'PUT',
          body: JSON.stringify(updateData)
        });
        
        // Si nous avons accès à la base locale, la mettre à jour
        if (this.dbs[type]) {
          try {
            const db = this.getDBForType(type);
            await db.update(apiResult);
          } catch (dbError) {
            console.warn(`Impossible de mettre à jour ${type}/${id} dans la base locale:`, dbError);
          }
        }
        
        return apiResult;
      } catch (apiError) {
        console.warn(`Erreur lors de la mise à jour via l'API:`, apiError);
        // Si l'API échoue et que nous avons une base locale, on continue
      }
    }
    
    // En mode hors ligne ou si l'API a échoué, utiliser la base locale
    if (this.dbs[type]) {
      try {
        const db = this.getDBForType(type);
        
        // Récupérer le document existant pour obtenir la révision
        const existingDoc = await db.get(id);
        
        // Marquer l'élément comme devant être synchronisé lorsque possible
        const itemToUpdate = {
          ...updateData,
          _rev: existingDoc._rev,
          _sync: { 
            status: 'pending', 
            isNew: false, 
            updatedAt: new Date().toISOString() 
          }
        };
        
        await db.update(itemToUpdate);
        const updatedDoc = await db.get(id);
        
        return updatedDoc;
      } catch (dbError) {
        console.error(`Erreur lors de la mise à jour dans la base locale:`, dbError);
        throw dbError;
      }
    }
    
    throw new Error(`Impossible de mettre à jour ${type}/${id} - Mode hors ligne et base de données locale indisponible`);
  }

  /**
   * Supprimer un élément
   * @param {string} type - Type de données
   * @param {string} id - ID de l'élément
   * @returns {Promise<Object>} - Résultat de la suppression
   */
  async delete(type, id) {
    // Si nous sommes en ligne, essayer d'abord l'API
    if (this.isOnline) {
      try {
        const apiResult = await this.fetchAPI(`/${type}/${id}`, {
          method: 'DELETE'
        });
        
        // Si nous avons accès à la base locale, supprimer également
        if (this.dbs[type]) {
          try {
            const db = this.getDBForType(type);
            await db.delete(id);
          } catch (dbError) {
            console.warn(`Impossible de supprimer ${type}/${id} de la base locale:`, dbError);
          }
        }
        
        return apiResult;
      } catch (apiError) {
        console.warn(`Erreur lors de la suppression via l'API:`, apiError);
        // Si l'API échoue et que nous avons une base locale, on continue
      }
    }
    
    // En mode hors ligne ou si l'API a échoué, utiliser la base locale
    if (this.dbs[type]) {
      try {
        const db = this.getDBForType(type);
        
        // Marquer l'élément comme supprimé et à synchroniser plus tard
        try {
          const existingDoc = await db.get(id);
          const deleteMarker = {
            ...existingDoc,
            _deleted: true,
            _sync: { 
              status: 'pending', 
              isDeleted: true, 
              deletedAt: new Date().toISOString() 
            }
          };
          
          return await db.update(deleteMarker);
        } catch (notFoundError) {
          // Si l'élément n'existe pas déjà, il est considéré comme supprimé
          return { ok: true, id, message: "Document déjà supprimé ou inexistant" };
        }
      } catch (dbError) {
        console.error(`Erreur lors de la suppression dans la base locale:`, dbError);
        throw dbError;
      }
    }
    
    throw new Error(`Impossible de supprimer ${type}/${id} - Mode hors ligne et base de données locale indisponible`);
  }

  /**
   * Rechercher des éléments avec des critères spécifiques
   * @param {string} type - Type de données
   * @param {Object} query - Critères de recherche
   * @returns {Promise<Array>} - Résultats de la recherche
   */
  async search(type, query) {
    const results = [];
    
    // Essayer d'abord la recherche locale
    if (this.dbs[type]) {
      try {
        const db = this.getDBForType(type);
        
        // Formatter la requête pour PouchDB
        const pouchQuery = {
          selector: query,
          sort: [{ updatedAt: 'desc' }]
        };
        
        const localResults = await db.find(pouchQuery);
        results.push(...localResults);
      } catch (dbError) {
        console.warn(`Erreur lors de la recherche locale dans ${type}:`, dbError);
      }
    }
    
    // Si en ligne, essayer également l'API
    if (this.isOnline) {
      try {
        const apiResults = await this.fetchAPI(`/${type}/search`, {
          method: 'POST',
          body: JSON.stringify(query)
        });
        
        // Fusionner et dédupliquer les résultats
        for (const apiItem of apiResults) {
          if (!results.some(item => item._id === apiItem._id)) {
            results.push(apiItem);
            
            // Sauvegarder en local les nouveaux éléments
            if (this.dbs[type]) {
              try {
                const db = this.getDBForType(type);
                await db.create(apiItem);
              } catch (error) {
                if (error.name !== 'conflict') {
                  console.error('Erreur lors de la sauvegarde locale:', error);
                }
              }
            }
          }
        }
      } catch (apiError) {
        console.warn(`Erreur lors de la recherche via l'API dans ${type}:`, apiError);
        
        // Si aucun résultat local n'a été trouvé et que l'API a échoué
        if (results.length === 0) {
          throw apiError;
        }
      }
    }
    
    // Si aucun résultat n'a été trouvé
    if (results.length === 0 && !this.isOnline && !this.dbs[type]) {
      throw new Error(`Impossible d'effectuer une recherche - Mode hors ligne et base de données locale indisponible`);
    }
    
    return results;
  }

  /**
   * Vérifier s'il y a des éléments non synchronisés
   * @param {string} type - Type de données
   * @returns {Promise<Array>} - Éléments non synchronisés
   */
  async getPendingSync(type) {
    if (!this.dbs[type]) {
      return [];
    }
    
    try {
      const db = this.getDBForType(type);
      
      const results = await db.find({
        selector: {
          '_sync.status': 'pending'
        }
      });
      
      return results;
    } catch (error) {
      console.error(`Erreur lors de la vérification des données non synchronisées pour ${type}:`, error);
      return [];
    }
  }

  /**
   * Synchroniser tous les éléments en attente d'un type spécifique
   * @param {string} type - Type de données
   * @returns {Promise<Object>} - Résultats de la synchronisation
   */
  async syncPending(type) {
    if (!this.isOnline) {
      return { 
        success: false, 
        message: 'Impossible de synchroniser en mode hors ligne', 
        results: [] 
      };
    }
    
    if (!this.dbs[type]) {
      return { 
        success: true, 
        message: 'Aucune base de données locale à synchroniser', 
        results: [] 
      };
    }
    
    try {
      const pending = await this.getPendingSync(type);
      
      if (pending.length === 0) {
        return { 
          success: true, 
          message: 'Aucune modification en attente', 
          results: [] 
        };
      }
      
      const results = [];
      
      for (const item of pending) {
        try {
          if (item._deleted || (item._sync && item._sync.isDeleted)) {
            // Élément marqué pour suppression
            const deleteResult = await this.fetchAPI(`/${type}/${item._id}`, {
              method: 'DELETE'
            });
            
            // Supprimer définitivement de la base locale
            const db = this.getDBForType(type);
            await db.delete(item._id);
            
            results.push({ id: item._id, status: 'deleted', result: deleteResult });
          } else {
            // Mise à jour ou création
            const isNew = item._sync && item._sync.isNew;
            const method = isNew ? 'POST' : 'PUT';
            const endpoint = isNew ? `/${type}` : `/${type}/${item._id}`;
            
            // Nettoyer les propriétés spécifiques à PouchDB
            const { _rev, _sync, ...cleanData } = item;
            
            const updateResult = await this.fetchAPI(endpoint, {
              method,
              body: JSON.stringify(cleanData)
            });
            
            // Mettre à jour l'élément local avec le statut synchronisé
            const db = this.getDBForType(type);
            await db.update({
              ...updateResult,
              _id: item._id,
              _rev: item._rev,
              _sync: { status: 'synced', lastSync: new Date().toISOString() }
            });
            
            results.push({ id: item._id, status: 'synced', result: updateResult });
          }
        } catch (error) {
          console.error(`Erreur lors de la synchronisation de l'élément ${item._id}:`, error);
          results.push({ id: item._id, status: 'error', error: error.message });
        }
      }
      
      return { 
        success: true, 
        message: `${results.length} éléments synchronisés`, 
        results 
      };
    } catch (error) {
      console.error(`Erreur lors de la synchronisation des éléments en attente:`, error);
      return { 
        success: false, 
        message: error.message, 
        results: [] 
      };
    }
  }

  /**
   * Synchroniser tous les éléments en attente de tous les types
   * @returns {Promise<Object>} - Résultats de la synchronisation
   */
  async syncAll() {
    if (!this.isOnline) {
      return { 
        success: false, 
        message: 'Impossible de synchroniser en mode hors ligne', 
        results: {} 
      };
    }
    
    const types = Object.keys(this.dbs).filter(key => this.dbs[key] !== null);
    const results = {};
    
    for (const type of types) {
      results[type] = await this.syncPending(type);
    }
    
    return { 
      success: true, 
      message: 'Synchronisation terminée', 
      results 
    };
  }
}

// Exporter une instance unique du service
const apiService = new ApiService();
export default apiService; 
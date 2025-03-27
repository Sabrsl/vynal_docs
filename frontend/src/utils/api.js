/**
 * API utilities for document management
 */

/**
 * Sauvegarde un document
 * @param {Object} document - Le document à sauvegarder
 * @returns {Promise<Object>} Le document sauvegardé
 */
export const saveDocument = async (document) => {
  try {
    // TODO: Implémenter l'appel API réel
    // Pour l'instant, on simule une sauvegarde
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ...document,
          id: document.id || Math.random().toString(36).substr(2, 9),
          lastModified: new Date().toISOString()
        });
      }, 500);
    });
  } catch (error) {
    console.error('Erreur lors de la sauvegarde du document:', error);
    throw error;
  }
};

/**
 * Met à jour un document
 * @param {string} documentId - L'ID du document à mettre à jour
 * @param {Object} document - Les données mises à jour
 * @returns {Promise<Object>} Le document mis à jour
 */
export const updateDocument = async (documentId, document) => {
  try {
    // TODO: Implémenter l'appel API réel
    // Pour l'instant, on simule une mise à jour
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ...document,
          id: documentId,
          lastModified: new Date().toISOString()
        });
      }, 500);
    });
  } catch (error) {
    console.error('Erreur lors de la mise à jour du document:', error);
    throw error;
  }
};

/**
 * Crée un nouveau document
 * @param {Object} document - Les données du nouveau document
 * @returns {Promise<Object>} Le document créé
 */
export const createDocument = async (document) => {
  try {
    // TODO: Implémenter l'appel API réel
    // Pour l'instant, on simule une création
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ...document,
          id: Math.random().toString(36).substr(2, 9),
          createdAt: new Date().toISOString(),
          lastModified: new Date().toISOString()
        });
      }, 500);
    });
  } catch (error) {
    console.error('Erreur lors de la création du document:', error);
    throw error;
  }
}; 
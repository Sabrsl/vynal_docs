const { MeiliSearch } = require('meilisearch');

class MeilisearchService {
  constructor() {
    this.client = new MeiliSearch({
      host: process.env.MEILISEARCH_HOST || 'http://localhost:7700',
      apiKey: process.env.MEILISEARCH_MASTER_KEY
    });
    this.index = this.client.index('documents');
  }

  async initializeIndex() {
    try {
      // Configurer les paramètres de recherche
      await this.index.updateSearchableAttributes([
        'title',
        'content',
        'description',
        'tags'
      ]);

      await this.index.updateFilterableAttributes([
        'type',
        'category',
        'client_id',
        'created_at',
        'updated_at',
        'owner_id'
      ]);

      await this.index.updateSortableAttributes([
        'created_at',
        'updated_at'
      ]);

      // Configurer la typo-tolerance
      await this.index.updateTypoTolerance({
        enabled: true,
        minWordSizeForTypos: {
          oneTypo: 4,
          twoTypos: 8
        }
      });

      console.log('Index Meilisearch initialisé avec succès');
    } catch (error) {
      console.error('Erreur lors de l\'initialisation de l\'index:', error);
      throw error;
    }
  }

  async addDocument(document) {
    try {
      const documentToIndex = {
        id: document._id.toString(),
        title: document.title,
        content: document.content,
        description: document.description,
        type: document.type,
        category: document.category,
        client_id: document.client_id,
        tags: document.tags || [],
        created_at: document.createdAt,
        updated_at: document.updatedAt,
        owner_id: document.owner.toString()
      };

      await this.index.addDocuments([documentToIndex]);
      console.log(`Document ${document._id} indexé avec succès`);
    } catch (error) {
      console.error(`Erreur lors de l'indexation du document ${document._id}:`, error);
      throw error;
    }
  }

  async updateDocument(document) {
    try {
      await this.addDocument(document);
      console.log(`Document ${document._id} mis à jour avec succès`);
    } catch (error) {
      console.error(`Erreur lors de la mise à jour du document ${document._id}:`, error);
      throw error;
    }
  }

  async deleteDocument(documentId) {
    try {
      await this.index.deleteDocument(documentId);
      console.log(`Document ${documentId} supprimé de l'index`);
    } catch (error) {
      console.error(`Erreur lors de la suppression du document ${documentId}:`, error);
      throw error;
    }
  }

  async search(query, options = {}) {
    try {
      const searchOptions = {
        filter: options.filter || [],
        sort: options.sort || ['created_at:desc'],
        limit: options.limit || 20,
        offset: options.offset || 0,
        attributesToRetrieve: [
          'id',
          'title',
          'content',
          'description',
          'type',
          'category',
          'client_id',
          'tags',
          'created_at',
          'updated_at',
          'owner_id'
        ]
      };

      const results = await this.index.search(query, searchOptions);
      return results;
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      throw error;
    }
  }
}

module.exports = new MeilisearchService(); 
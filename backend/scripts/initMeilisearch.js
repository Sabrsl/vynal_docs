const mongoose = require('mongoose');
const Document = require('../models/Document');
const meilisearchService = require('../services/meilisearchService');
require('dotenv').config();

async function initializeMeilisearch() {
  try {
    // Connexion à MongoDB
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });

    console.log('Connecté à MongoDB');

    // Initialiser l'index Meilisearch
    await meilisearchService.initializeIndex();
    console.log('Index Meilisearch initialisé');

    // Récupérer tous les documents
    const documents = await Document.find({ isDeleted: false });
    console.log(`${documents.length} documents trouvés`);

    // Indexer chaque document
    for (const doc of documents) {
      await meilisearchService.addDocument(doc);
      console.log(`Document ${doc._id} indexé`);
    }

    console.log('Indexation terminée avec succès');
    process.exit(0);
  } catch (error) {
    console.error('Erreur lors de l\'initialisation:', error);
    process.exit(1);
  }
}

initializeMeilisearch(); 
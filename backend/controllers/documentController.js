const Document = require('../models/Document');
const { asyncHandler } = require('../middlewares/errorMiddleware');
const path = require('path');
const fs = require('fs');
const meilisearchService = require('../services/meilisearchService');

/**
 * @desc    Créer un nouveau document
 * @route   POST /api/documents
 * @access  Private
 */
const createDocument = asyncHandler(async (req, res) => {
  const { name, type, size, category } = req.body;
  
  // Dans une implémentation complète, il faudrait gérer l'upload de fichier
  // Pour l'instant, on simule juste le chemin du fichier
  const filePath = `/uploads/documents/${Date.now()}-${name}`;
  
  const document = await Document.create({
    name,
    type, 
    size,
    path: filePath,
    owner: req.user._id,
    category: category || null
  });
  
  // Indexer le document dans Meilisearch
  await meilisearchService.addDocument(document);
  
  if (document) {
    res.status(201).json(document);
  } else {
    res.status(400);
    throw new Error('Données de document invalides');
  }
});

/**
 * @desc    Obtenir tous les documents
 * @route   GET /api/documents
 * @access  Private
 */
const getDocuments = asyncHandler(async (req, res) => {
  const {
    search,
    type,
    category,
    favorite,
    sort,
    page = 1,
    limit = 10
  } = req.query;

  try {
    // Construire les filtres pour Meilisearch
    const filters = [`owner_id = ${req.user._id}`, 'isDeleted = false'];
    
    if (type) {
      filters.push(`type = "${type}"`);
    }
    
    if (category) {
      filters.push(`category = "${category}"`);
    }
    
    if (favorite === 'true') {
      filters.push('isFavorite = true');
    }

    console.log('Recherche avec les paramètres:', {
      search,
      filters,
      sort: sort ? [sort] : ['created_at:desc'],
      limit: parseInt(limit),
      offset: (parseInt(page) - 1) * parseInt(limit)
    });

    // Effectuer la recherche avec Meilisearch
    const results = await meilisearchService.search(search || '', {
      filter: filters,
      sort: sort ? [sort] : ['created_at:desc'],
      limit: parseInt(limit),
      offset: (parseInt(page) - 1) * parseInt(limit)
    });

    console.log('Résultats de la recherche:', results);

    // Récupérer les documents complets depuis MongoDB
    const documentIds = results.hits.map(hit => hit.id);
    const documents = await Document.find({
      _id: { $in: documentIds },
      owner: req.user._id,
      isDeleted: false
    }).populate('category', 'name color icon');

    // Réorganiser les documents selon l'ordre des résultats de recherche
    const orderedDocuments = documentIds.map(id => 
      documents.find(doc => doc._id.toString() === id)
    ).filter(Boolean);

    res.json({
      documents: orderedDocuments,
      page: parseInt(page),
      pages: Math.ceil(results.estimatedTotalHits / parseInt(limit)),
      total: results.estimatedTotalHits
    });
  } catch (error) {
    console.error('Erreur lors de la recherche:', error);
    res.status(500).json({
      error: 'Erreur lors de la recherche des documents',
      details: error.message
    });
  }
});

/**
 * @desc    Obtenir les documents partagés avec l'utilisateur
 * @route   GET /api/documents/shared
 * @access  Private
 */
const getSharedDocuments = asyncHandler(async (req, res) => {
  const documents = await Document.find({
    'sharedWith.user': req.user._id,
    isDeleted: false
  })
    .populate('owner', 'firstName lastName email')
    .populate('category', 'name color icon');
  
  res.json(documents);
});

/**
 * @desc    Obtenir un document par son ID
 * @route   GET /api/documents/:id
 * @access  Private
 */
const getDocumentById = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id)
    .populate('owner', 'firstName lastName email')
    .populate('category', 'name color icon')
    .populate('sharedWith.user', 'firstName lastName email');
  
  if (!document) {
    res.status(404);
    throw new Error('Document non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à voir ce document
  const isOwner = document.owner._id.toString() === req.user._id.toString();
  const isSharedWith = document.sharedWith.some(
    share => share.user._id.toString() === req.user._id.toString()
  );
  
  if (!isOwner && !isSharedWith && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à accéder à ce document');
  }
  
  // Mettre à jour la date de dernier accès
  document.lastAccessedAt = Date.now();
  await document.save();
  
  res.json(document);
});

/**
 * @desc    Mettre à jour un document
 * @route   PUT /api/documents/:id
 * @access  Private
 */
const updateDocument = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id);
  
  if (!document) {
    res.status(404);
    throw new Error('Document non trouvé');
  }
  
  // Vérifier que l'utilisateur est propriétaire du document
  if (document.owner.toString() !== req.user._id.toString()) {
    res.status(403);
    throw new Error('Non autorisé');
  }
  
  // Mettre à jour les champs du document
  document.name = req.body.name || document.name;
  document.category = req.body.category || document.category;
  document.tags = req.body.tags || document.tags;
  document.isFavorite = req.body.isFavorite !== undefined ? req.body.isFavorite : document.isFavorite;
  
  const updatedDocument = await document.save();
  
  // Mettre à jour l'index Meilisearch
  await meilisearchService.updateDocument(updatedDocument);
  
  res.json(updatedDocument);
});

/**
 * @desc    Supprimer un document (mettre à la corbeille)
 * @route   DELETE /api/documents/:id
 * @access  Private
 */
const trashDocument = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id);
  
  if (!document) {
    res.status(404);
    throw new Error('Document non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à supprimer ce document
  const isOwner = document.owner.toString() === req.user._id.toString();
  const isAdmin = document.sharedWith.some(
    share => share.user.toString() === req.user._id.toString() && share.permission === 'admin'
  );
  
  if (!isOwner && !isAdmin && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à supprimer ce document');
  }
  
  // Marquer comme supprimé (corbeille)
  await document.moveToTrash();
  
  // Supprimer le document de l'index Meilisearch
  await meilisearchService.deleteDocument(req.params.id);
  
  res.json({ message: 'Document déplacé vers la corbeille' });
});

/**
 * @desc    Récupérer un document de la corbeille
 * @route   PUT /api/documents/:id/restore
 * @access  Private
 */
const restoreDocument = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id);
  
  if (!document) {
    res.status(404);
    throw new Error('Document non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à restaurer ce document
  const isOwner = document.owner.toString() === req.user._id.toString();
  
  if (!isOwner && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à restaurer ce document');
  }
  
  // Restaurer le document
  await document.restore();
  
  res.json({ message: 'Document restauré' });
});

/**
 * @desc    Supprimer définitivement un document
 * @route   DELETE /api/documents/:id/permanent
 * @access  Private
 */
const deleteDocumentPermanently = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id);
  
  if (!document) {
    res.status(404);
    throw new Error('Document non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à supprimer ce document
  const isOwner = document.owner.toString() === req.user._id.toString();
  
  if (!isOwner && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à supprimer définitivement ce document');
  }
  
  // Dans une implémentation complète, il faudrait aussi supprimer le fichier
  // try {
  //   fs.unlinkSync(path.join(__dirname, '..', document.path));
  // } catch (error) {
  //   console.error('Erreur lors de la suppression du fichier:', error);
  // }
  
  // Supprimer le document de la base de données
  await document.deleteOne();
  
  // Supprimer le document de l'index Meilisearch
  await meilisearchService.deleteDocument(req.params.id);
  
  res.json({ message: 'Document supprimé définitivement' });
});

/**
 * @desc    Partager un document avec d'autres utilisateurs
 * @route   POST /api/documents/:id/share
 * @access  Private
 */
const shareDocument = asyncHandler(async (req, res) => {
  const { users } = req.body;
  
  if (!users || !Array.isArray(users)) {
    res.status(400);
    throw new Error('Veuillez fournir une liste d\'utilisateurs valide');
  }
  
  const document = await Document.findById(req.params.id);
  
  if (!document) {
    res.status(404);
    throw new Error('Document non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à partager ce document
  const isOwner = document.owner.toString() === req.user._id.toString();
  const canShare = document.sharedWith.some(
    share => share.user.toString() === req.user._id.toString() && share.permission === 'admin'
  );
  
  if (!isOwner && !canShare && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à partager ce document');
  }
  
  // Mettre à jour la liste des utilisateurs avec qui le document est partagé
  for (const userShare of users) {
    const existingShareIndex = document.sharedWith.findIndex(
      share => share.user.toString() === userShare.userId
    );
    
    if (existingShareIndex >= 0) {
      // Mettre à jour les permissions existantes
      document.sharedWith[existingShareIndex].permission = userShare.permission || 'view';
    } else {
      // Ajouter un nouveau partage
      document.sharedWith.push({
        user: userShare.userId,
        permission: userShare.permission || 'view'
      });
    }
  }
  
  await document.save();
  
  res.json(document);
});

/**
 * @desc    Supprimer un partage de document
 * @route   DELETE /api/documents/:id/share/:userId
 * @access  Private
 */
const removeShareDocument = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id);
  
  if (!document) {
    res.status(404);
    throw new Error('Document non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à gérer les partages
  const isOwner = document.owner.toString() === req.user._id.toString();
  const canManageShares = document.sharedWith.some(
    share => share.user.toString() === req.user._id.toString() && share.permission === 'admin'
  );
  
  if (!isOwner && !canManageShares && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à modifier les partages de ce document');
  }
  
  // Filtrer les partages pour supprimer celui spécifié
  document.sharedWith = document.sharedWith.filter(
    share => share.user.toString() !== req.params.userId
  );
  
  await document.save();
  
  res.json(document);
});

/**
 * @desc    Récupérer tous les documents dans la corbeille
 * @route   GET /api/documents/trash
 * @access  Private
 */
const getTrashDocuments = asyncHandler(async (req, res) => {
  const documents = await Document.find({
    owner: req.user._id,
    isDeleted: true
  })
    .sort({ deletedAt: -1 })
    .populate('category', 'name color icon');
  
  res.json(documents);
});

/**
 * @desc    Vider la corbeille (suppression définitive de tous les documents dans la corbeille)
 * @route   DELETE /api/documents/trash/empty
 * @access  Private
 */
const emptyTrash = asyncHandler(async (req, res) => {
  // Récupérer tous les documents dans la corbeille
  const trashDocuments = await Document.find({
    owner: req.user._id,
    isDeleted: true
  });
  
  // Dans une implémentation complète, il faudrait aussi supprimer les fichiers
  // for (const doc of trashDocuments) {
  //   try {
  //     fs.unlinkSync(path.join(__dirname, '..', doc.path));
  //   } catch (error) {
  //     console.error(`Erreur lors de la suppression du fichier ${doc.path}:`, error);
  //   }
  // }
  
  // Supprimer tous les documents dans la corbeille
  await Document.deleteMany({
    owner: req.user._id,
    isDeleted: true
  });
  
  // Supprimer tous les documents de l'index Meilisearch
  for (const doc of trashDocuments) {
    await meilisearchService.deleteDocument(doc._id);
  }
  
  res.json({ 
    message: 'Corbeille vidée avec succès', 
    count: trashDocuments.length 
  });
});

module.exports = {
  createDocument,
  getDocuments,
  getSharedDocuments,
  getDocumentById,
  updateDocument,
  trashDocument,
  restoreDocument,
  deleteDocumentPermanently,
  shareDocument,
  removeShareDocument,
  getTrashDocuments,
  emptyTrash
}; 
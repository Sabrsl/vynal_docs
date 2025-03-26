const Document = require('../models/Document');
const { asyncHandler } = require('../middlewares/errorMiddleware');
const path = require('path');
const fs = require('fs');

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
  // Filtres de base - documents non supprimés appartenant à l'utilisateur
  const filter = { 
    owner: req.user._id,
    isDeleted: false 
  };
  
  // Filtres supplémentaires basés sur les paramètres de requête
  if (req.query.type) {
    filter.type = req.query.type;
  }
  
  if (req.query.category) {
    filter.category = req.query.category;
  }
  
  if (req.query.favorite === 'true') {
    filter.isFavorite = true;
  }
  
  // Paramètres de tri
  const sort = {};
  if (req.query.sort) {
    const [field, order] = req.query.sort.split(':');
    sort[field] = order === 'desc' ? -1 : 1;
  } else {
    // Tri par défaut - du plus récent au plus ancien
    sort.createdAt = -1;
  }
  
  // Pagination
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const skip = (page - 1) * limit;
  
  // Recherche textuelle
  if (req.query.search) {
    filter.name = { $regex: req.query.search, $options: 'i' };
  }
  
  // Exécution de la requête
  const documents = await Document.find(filter)
    .sort(sort)
    .skip(skip)
    .limit(limit)
    .populate('category', 'name color icon');
  
  // Comptage total pour la pagination
  const total = await Document.countDocuments(filter);
  
  res.json({
    documents,
    page,
    pages: Math.ceil(total / limit),
    total
  });
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
  
  // Vérifier si l'utilisateur est autorisé à modifier ce document
  const isOwner = document.owner.toString() === req.user._id.toString();
  const isEditor = document.sharedWith.some(
    share => share.user.toString() === req.user._id.toString() && 
    (share.permission === 'edit' || share.permission === 'admin')
  );
  
  if (!isOwner && !isEditor && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à modifier ce document');
  }
  
  // Mettre à jour les champs du document
  document.name = req.body.name || document.name;
  document.category = req.body.category || document.category;
  document.tags = req.body.tags || document.tags;
  document.isFavorite = req.body.isFavorite !== undefined ? req.body.isFavorite : document.isFavorite;
  
  const updatedDocument = await document.save();
  
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
const Template = require('../models/Template');
const { asyncHandler } = require('../middlewares/errorMiddleware');
const path = require('path');
const fs = require('fs');

/**
 * @desc    Créer un nouveau modèle
 * @route   POST /api/templates
 * @access  Private
 */
const createTemplate = asyncHandler(async (req, res) => {
  const { name, description, type, category, size, isPublic, tags } = req.body;
  
  // Dans une implémentation complète, il faudrait gérer l'upload de fichier
  // Pour l'instant, on simule juste le chemin du fichier
  const filePath = `/uploads/templates/${Date.now()}-${name}`;
  
  const template = await Template.create({
    name,
    description: description || '',
    type,
    category,
    size,
    path: filePath,
    thumbnail: req.body.thumbnail || '',
    isPublic: isPublic || false,
    createdBy: req.user._id,
    tags: tags || []
  });
  
  if (template) {
    res.status(201).json(template);
  } else {
    res.status(400);
    throw new Error('Données de modèle invalides');
  }
});

/**
 * @desc    Obtenir tous les modèles
 * @route   GET /api/templates
 * @access  Private
 */
const getTemplates = asyncHandler(async (req, res) => {
  // Filtres de base - modèles créés par l'utilisateur ou publics
  const filter = {
    $or: [
      { createdBy: req.user._id },
      { isPublic: true }
    ]
  };
  
  // Filtres supplémentaires basés sur les paramètres de requête
  if (req.query.type) {
    filter.type = req.query.type;
  }
  
  if (req.query.category) {
    filter.category = req.query.category;
  }
  
  if (req.query.onlyMine === 'true') {
    // Supprimer le filtre OR et ne garder que les modèles de l'utilisateur
    delete filter.$or;
    filter.createdBy = req.user._id;
  }
  
  if (req.query.onlyPublic === 'true') {
    // Supprimer le filtre OR et ne garder que les modèles publics
    delete filter.$or;
    filter.isPublic = true;
  }
  
  // Paramètres de tri
  const sort = {};
  if (req.query.sort) {
    const [field, order] = req.query.sort.split(':');
    sort[field] = order === 'desc' ? -1 : 1;
  } else {
    // Tri par défaut - modèles les plus utilisés en premier
    sort.usage = -1;
  }
  
  // Pagination
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const skip = (page - 1) * limit;
  
  // Recherche textuelle
  if (req.query.search) {
    filter.$or = [
      { name: { $regex: req.query.search, $options: 'i' } },
      { description: { $regex: req.query.search, $options: 'i' } },
      { category: { $regex: req.query.search, $options: 'i' } },
      { tags: { $in: [new RegExp(req.query.search, 'i')] } }
    ];
  }
  
  // Exécution de la requête
  const templates = await Template.find(filter)
    .sort(sort)
    .skip(skip)
    .limit(limit)
    .populate('createdBy', 'firstName lastName');
  
  // Comptage total pour la pagination
  const total = await Template.countDocuments(filter);
  
  res.json({
    templates,
    page,
    pages: Math.ceil(total / limit),
    total
  });
});

/**
 * @desc    Obtenir un modèle par son ID
 * @route   GET /api/templates/:id
 * @access  Private
 */
const getTemplateById = asyncHandler(async (req, res) => {
  const template = await Template.findById(req.params.id)
    .populate('createdBy', 'firstName lastName email');
  
  if (!template) {
    res.status(404);
    throw new Error('Modèle non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à voir ce modèle
  const isOwner = template.createdBy._id.toString() === req.user._id.toString();
  const isPublic = template.isPublic;
  
  if (!isOwner && !isPublic && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à accéder à ce modèle');
  }
  
  res.json(template);
});

/**
 * @desc    Mettre à jour un modèle
 * @route   PUT /api/templates/:id
 * @access  Private
 */
const updateTemplate = asyncHandler(async (req, res) => {
  const { name, description, category, thumbnail, isPublic, tags } = req.body;
  
  const template = await Template.findById(req.params.id);
  
  if (!template) {
    res.status(404);
    throw new Error('Modèle non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à modifier ce modèle
  if (template.createdBy.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à modifier ce modèle');
  }
  
  // Mettre à jour les champs
  template.name = name || template.name;
  template.description = description !== undefined ? description : template.description;
  template.category = category || template.category;
  template.thumbnail = thumbnail || template.thumbnail;
  template.isPublic = isPublic !== undefined ? isPublic : template.isPublic;
  template.tags = tags || template.tags;
  
  const updatedTemplate = await template.save();
  
  res.json(updatedTemplate);
});

/**
 * @desc    Supprimer un modèle
 * @route   DELETE /api/templates/:id
 * @access  Private
 */
const deleteTemplate = asyncHandler(async (req, res) => {
  const template = await Template.findById(req.params.id);
  
  if (!template) {
    res.status(404);
    throw new Error('Modèle non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à supprimer ce modèle
  if (template.createdBy.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à supprimer ce modèle');
  }
  
  // Dans une implémentation complète, il faudrait aussi supprimer le fichier
  // try {
  //   fs.unlinkSync(path.join(__dirname, '..', template.path));
  //   
  //   if (template.thumbnail) {
  //     fs.unlinkSync(path.join(__dirname, '..', template.thumbnail));
  //   }
  // } catch (error) {
  //   console.error('Erreur lors de la suppression du fichier:', error);
  // }
  
  await template.deleteOne();
  
  res.json({ message: 'Modèle supprimé' });
});

/**
 * @desc    Utiliser un modèle (incrémenter le compteur d'utilisation)
 * @route   PUT /api/templates/:id/use
 * @access  Private
 */
const useTemplate = asyncHandler(async (req, res) => {
  const template = await Template.findById(req.params.id);
  
  if (!template) {
    res.status(404);
    throw new Error('Modèle non trouvé');
  }
  
  // Vérifier si l'utilisateur est autorisé à utiliser ce modèle
  const isOwner = template.createdBy.toString() === req.user._id.toString();
  const isPublic = template.isPublic;
  
  if (!isOwner && !isPublic && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à utiliser ce modèle');
  }
  
  // Incrémenter le compteur d'utilisation
  await template.incrementUsage();
  
  res.json({
    message: 'Compteur d\'utilisation incrémenté',
    usage: template.usage
  });
});

/**
 * @desc    Obtenir les modèles par catégorie
 * @route   GET /api/templates/category/:category
 * @access  Private
 */
const getTemplatesByCategory = asyncHandler(async (req, res) => {
  const { category } = req.params;
  
  // Filtres de base - modèles de la catégorie spécifiée, créés par l'utilisateur ou publics
  const filter = {
    category: { $regex: new RegExp(`^${category}$`, 'i') },
    $or: [
      { createdBy: req.user._id },
      { isPublic: true }
    ]
  };
  
  const templates = await Template.find(filter)
    .sort({ usage: -1 })
    .populate('createdBy', 'firstName lastName');
  
  res.json(templates);
});

module.exports = {
  createTemplate,
  getTemplates,
  getTemplateById,
  updateTemplate,
  deleteTemplate,
  useTemplate,
  getTemplatesByCategory
}; 
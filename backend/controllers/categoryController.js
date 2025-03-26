const Category = require('../models/Category');
const Document = require('../models/Document');
const { asyncHandler } = require('../middlewares/errorMiddleware');

/**
 * @desc    Créer une nouvelle catégorie
 * @route   POST /api/categories
 * @access  Private
 */
const createCategory = asyncHandler(async (req, res) => {
  const { name, description, color, icon, parent } = req.body;
  
  // Vérifier si une catégorie avec le même nom existe déjà
  const categoryExists = await Category.findOne({ 
    name: { $regex: new RegExp(`^${name}$`, 'i') },
    createdBy: req.user._id 
  });
  
  if (categoryExists) {
    res.status(400);
    throw new Error('Une catégorie avec ce nom existe déjà');
  }
  
  // Créer la catégorie
  const category = await Category.create({
    name,
    description,
    color: color || '#6933FF',
    icon: icon || 'bx-folder',
    parent: parent || null,
    createdBy: req.user._id
  });
  
  if (category) {
    res.status(201).json(category);
  } else {
    res.status(400);
    throw new Error('Données de catégorie invalides');
  }
});

/**
 * @desc    Obtenir toutes les catégories
 * @route   GET /api/categories
 * @access  Private
 */
const getCategories = asyncHandler(async (req, res) => {
  // Filtres de base - catégories créées par l'utilisateur
  const filter = { 
    createdBy: req.user._id 
  };
  
  // Filtres pour les catégories parentes ou tous
  if (req.query.parent === 'null') {
    filter.parent = null;
  } else if (req.query.parent) {
    filter.parent = req.query.parent;
  }
  
  // Tri par ordre puis par nom
  const sort = { order: 1, name: 1 };
  
  // Exécution de la requête
  const categories = await Category.find(filter)
    .sort(sort)
    .populate('parent', 'name');
  
  res.json(categories);
});

/**
 * @desc    Obtenir une catégorie par son ID
 * @route   GET /api/categories/:id
 * @access  Private
 */
const getCategoryById = asyncHandler(async (req, res) => {
  const category = await Category.findById(req.params.id)
    .populate('parent', 'name')
    .populate('createdBy', 'firstName lastName');
  
  if (!category) {
    res.status(404);
    throw new Error('Catégorie non trouvée');
  }
  
  // Vérifier si l'utilisateur est autorisé à voir cette catégorie
  if (category.createdBy._id.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à accéder à cette catégorie');
  }
  
  // Compter le nombre de documents dans cette catégorie
  const documentCount = await Document.countDocuments({ 
    category: category._id,
    isDeleted: false 
  });
  
  res.json({
    ...category.toObject(),
    documentCount
  });
});

/**
 * @desc    Mettre à jour une catégorie
 * @route   PUT /api/categories/:id
 * @access  Private
 */
const updateCategory = asyncHandler(async (req, res) => {
  const { name, description, color, icon, parent, order } = req.body;
  
  const category = await Category.findById(req.params.id);
  
  if (!category) {
    res.status(404);
    throw new Error('Catégorie non trouvée');
  }
  
  // Vérifier si l'utilisateur est autorisé à modifier cette catégorie
  if (category.createdBy.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à modifier cette catégorie');
  }
  
  // Si le nom change, vérifier qu'il n'existe pas déjà
  if (name && name !== category.name) {
    const categoryExists = await Category.findOne({ 
      name: { $regex: new RegExp(`^${name}$`, 'i') },
      createdBy: req.user._id,
      _id: { $ne: category._id }
    });
    
    if (categoryExists) {
      res.status(400);
      throw new Error('Une catégorie avec ce nom existe déjà');
    }
  }
  
  // Mettre à jour les champs
  category.name = name || category.name;
  category.description = description !== undefined ? description : category.description;
  category.color = color || category.color;
  category.icon = icon || category.icon;
  category.parent = parent === null ? null : parent || category.parent;
  category.order = order !== undefined ? order : category.order;
  
  const updatedCategory = await category.save();
  
  res.json(updatedCategory);
});

/**
 * @desc    Supprimer une catégorie
 * @route   DELETE /api/categories/:id
 * @access  Private
 */
const deleteCategory = asyncHandler(async (req, res) => {
  const category = await Category.findById(req.params.id);
  
  if (!category) {
    res.status(404);
    throw new Error('Catégorie non trouvée');
  }
  
  // Vérifier si l'utilisateur est autorisé à supprimer cette catégorie
  if (category.createdBy.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à supprimer cette catégorie');
  }
  
  // Vérifier si des documents sont associés à cette catégorie
  const documentsCount = await Document.countDocuments({ category: category._id });
  
  if (documentsCount > 0) {
    res.status(400);
    throw new Error(`Impossible de supprimer la catégorie car elle contient ${documentsCount} document(s)`);
  }
  
  // Vérifier si des sous-catégories sont associées à cette catégorie
  const subCategoriesCount = await Category.countDocuments({ parent: category._id });
  
  if (subCategoriesCount > 0) {
    res.status(400);
    throw new Error(`Impossible de supprimer la catégorie car elle contient ${subCategoriesCount} sous-catégorie(s)`);
  }
  
  await category.deleteOne();
  
  res.json({ message: 'Catégorie supprimée' });
});

/**
 * @desc    Réorganiser les catégories
 * @route   PUT /api/categories/reorder
 * @access  Private
 */
const reorderCategories = asyncHandler(async (req, res) => {
  const { categories } = req.body;
  
  if (!categories || !Array.isArray(categories)) {
    res.status(400);
    throw new Error('Veuillez fournir une liste valide de catégories');
  }
  
  // Mettre à jour l'ordre de chaque catégorie
  const updateOperations = categories.map(({ id, order }) => ({
    updateOne: {
      filter: { _id: id, createdBy: req.user._id },
      update: { order }
    }
  }));
  
  await Category.bulkWrite(updateOperations);
  
  // Récupérer les catégories mises à jour
  const updatedCategories = await Category.find({
    createdBy: req.user._id
  }).sort({ order: 1, name: 1 });
  
  res.json(updatedCategories);
});

/**
 * @desc    Obtenir les documents d'une catégorie
 * @route   GET /api/categories/:id/documents
 * @access  Private
 */
const getCategoryDocuments = asyncHandler(async (req, res) => {
  const category = await Category.findById(req.params.id);
  
  if (!category) {
    res.status(404);
    throw new Error('Catégorie non trouvée');
  }
  
  // Vérifier si l'utilisateur est autorisé à voir cette catégorie
  if (category.createdBy.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    res.status(403);
    throw new Error('Non autorisé à accéder à cette catégorie');
  }
  
  // Paramètres de tri et pagination
  const sort = req.query.sort ? JSON.parse(req.query.sort) : { createdAt: -1 };
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const skip = (page - 1) * limit;
  
  // Rechercher les documents dans cette catégorie
  const documents = await Document.find({ 
    category: category._id,
    owner: req.user._id,
    isDeleted: false
  })
    .sort(sort)
    .skip(skip)
    .limit(limit);
  
  // Comptage total pour la pagination
  const total = await Document.countDocuments({ 
    category: category._id,
    owner: req.user._id,
    isDeleted: false
  });
  
  res.json({
    documents,
    page,
    pages: Math.ceil(total / limit),
    total
  });
});

module.exports = {
  createCategory,
  getCategories,
  getCategoryById,
  updateCategory,
  deleteCategory,
  reorderCategories,
  getCategoryDocuments
}; 
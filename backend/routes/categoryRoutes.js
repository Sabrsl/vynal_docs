const express = require('express');
const router = express.Router();
const {
  createCategory,
  getCategories,
  getCategoryById,
  updateCategory,
  deleteCategory,
  reorderCategories,
  getCategoryDocuments
} = require('../controllers/categoryController');
const { protect, admin } = require('../middlewares/authMiddleware');

// Toutes les routes nécessitent une authentification
router.use(protect);

// Routes principales
router.route('/')
  .get(getCategories)
  .post(createCategory);

// Réorganiser les catégories
router.put('/reorder', reorderCategories);

// Opérations sur une catégorie spécifique
router.route('/:id')
  .get(getCategoryById)
  .put(updateCategory)
  .delete(deleteCategory);

// Obtenir les documents d'une catégorie
router.get('/:id/documents', getCategoryDocuments);

module.exports = router; 
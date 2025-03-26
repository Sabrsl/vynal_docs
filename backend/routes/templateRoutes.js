const express = require('express');
const router = express.Router();
const {
  createTemplate,
  getTemplates,
  getTemplateById,
  updateTemplate,
  deleteTemplate,
  useTemplate,
  getTemplatesByCategory
} = require('../controllers/templateController');
const { protect, admin, editor } = require('../middlewares/authMiddleware');

// Toutes les routes nécessitent une authentification
router.use(protect);

// Routes principales
router.route('/')
  .get(getTemplates)
  .post(createTemplate);

// Obtenir les modèles par catégorie
router.get('/category/:category', getTemplatesByCategory);

// Opérations sur un modèle spécifique
router.route('/:id')
  .get(getTemplateById)
  .put(updateTemplate)
  .delete(deleteTemplate);

// Utiliser un modèle (incrémenter le compteur d'utilisation)
router.put('/:id/use', useTemplate);

module.exports = router; 
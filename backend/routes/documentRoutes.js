const express = require('express');
const router = express.Router();
const {
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
} = require('../controllers/documentController');
const { protect, admin } = require('../middlewares/authMiddleware');

// Toutes les routes nécessitent une authentification
router.use(protect);

// Routes principales
router.route('/')
  .get(getDocuments)
  .post(createDocument);

// Documents partagés
router.get('/shared', getSharedDocuments);

// Gestion de la corbeille
router.get('/trash', getTrashDocuments);
router.delete('/trash/empty', emptyTrash);

// Opérations sur un document spécifique
router.route('/:id')
  .get(getDocumentById)
  .put(updateDocument)
  .delete(trashDocument);

// Restaurer un document de la corbeille
router.put('/:id/restore', restoreDocument);

// Supprimer définitivement un document
router.delete('/:id/permanent', deleteDocumentPermanently);

// Partage de documents
router.route('/:id/share')
  .post(shareDocument);

router.delete('/:id/share/:userId', removeShareDocument);

module.exports = router; 
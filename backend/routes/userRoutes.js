const express = require('express');
const router = express.Router();
const {
  registerUser,
  loginUser,
  getUserProfile,
  updateUserProfile,
  getUsers,
  getUserById,
  deleteUser,
  updateUser
} = require('../controllers/userController');
const { protect, admin } = require('../middlewares/authMiddleware');

// Routes publiques
router.post('/register', registerUser);
router.post('/login', loginUser);

// Routes protégées pour l'utilisateur connecté
router.route('/profile')
  .get(protect, getUserProfile)
  .put(protect, updateUserProfile);

// Routes protégées pour l'administrateur
router.route('/')
  .get(protect, admin, getUsers);

router.route('/:id')
  .get(protect, admin, getUserById)
  .put(protect, admin, updateUser)
  .delete(protect, admin, deleteUser);

module.exports = router; 
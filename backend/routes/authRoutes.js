const express = require('express');
const router = express.Router();
const { protect } = require('../middlewares/authMiddleware');

// Route de base pour vérifier l'authentification
router.get('/check', protect, (req, res) => {
  res.json({ 
    authenticated: true,
    user: {
      id: req.user._id,
      email: req.user.email,
      name: req.user.name
    }
  });
});

module.exports = router; 
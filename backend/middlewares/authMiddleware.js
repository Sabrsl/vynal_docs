const jwt = require('jsonwebtoken');
const User = require('../models/User');
const asyncHandler = require('./async');

/**
 * Middleware pour protéger les routes
 * Vérifie le token JWT et ajoute l'utilisateur à la requête
 */
const protect = asyncHandler(async (req, res, next) => {
  let token;

  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }

  if (!token) {
    return res.status(401).json({
      error: 'Non autorisé - Token manquant'
    });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = await User.findById(decoded.id).select('-password');
    next();
  } catch (error) {
    return res.status(401).json({
      error: 'Non autorisé - Token invalide'
    });
  }
});

/**
 * Middleware pour vérifier si l'utilisateur est un admin
 */
const admin = (req, res, next) => {
  if (req.user && req.user.role === 'admin') {
    next();
  } else {
    res.status(403);
    throw new Error('Non autorisé, droits administrateur requis');
  }
};

/**
 * Middleware pour vérifier si l'utilisateur est un éditeur ou un admin
 */
const editor = (req, res, next) => {
  if (req.user && (req.user.role === 'editor' || req.user.role === 'admin')) {
    next();
  } else {
    res.status(403);
    throw new Error('Non autorisé, droits éditeur requis');
  }
};

module.exports = { protect, admin, editor }; 
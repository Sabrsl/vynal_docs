const jwt = require('jsonwebtoken');
const { asyncHandler } = require('./errorMiddleware');
const User = require('../models/User');

/**
 * Middleware pour protéger les routes
 * Vérifie le token JWT et ajoute l'utilisateur à la requête
 */
const protect = asyncHandler(async (req, res, next) => {
  let token;

  // Vérifier si le token est présent dans les headers
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith('Bearer')
  ) {
    try {
      // Extraire le token du header
      token = req.headers.authorization.split(' ')[1];

      // Vérifier le token
      const decoded = jwt.verify(token, process.env.JWT_SECRET);

      // Récupérer l'utilisateur sans le mot de passe
      req.user = await User.findById(decoded.id).select('-password');

      next();
    } catch (error) {
      console.error(error);
      res.status(401);
      throw new Error('Non autorisé, token invalide');
    }
  }

  if (!token) {
    res.status(401);
    throw new Error('Non autorisé, pas de token');
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
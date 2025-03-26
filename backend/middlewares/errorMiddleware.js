// Middleware pour capturer les erreurs dans les routes async
const asyncHandler = fn => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

// Gestionnaire d'erreurs global
const errorHandler = (err, req, res, next) => {
  const statusCode = res.statusCode === 200 ? 500 : res.statusCode;
  
  // Log de l'erreur en développement
  if (process.env.NODE_ENV === 'development') {
    console.error('Erreur:', err);
  }
  
  res.status(statusCode).json({
    message: err.message,
    stack: process.env.NODE_ENV === 'production' ? null : err.stack
  });
};

// Middleware pour les routes inexistantes
const notFound = (req, res, next) => {
  const error = new Error(`Route non trouvée - ${req.originalUrl}`);
  res.status(404);
  next(error);
};

module.exports = { asyncHandler, errorHandler, notFound }; 
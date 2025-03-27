const { body, validationResult, param, query } = require('express-validator');

/**
 * Middleware pour valider les résultats des validations
 */
const validateResults = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    res.status(400).json({ errors: errors.array() });
    return;
  }
  next();
};

/**
 * Validation pour la création d'un document
 */
const validateDocumentCreation = [
  body('title')
    .trim()
    .notEmpty()
    .withMessage('Le titre est requis')
    .isLength({ min: 3, max: 100 })
    .withMessage('Le titre doit contenir entre 3 et 100 caractères')
    .escape(),
  
  body('type')
    .isIn(['document', 'presentation', 'spreadsheet', 'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'jpg', 'jpeg', 'png'])
    .withMessage('Type de document non valide'),
  
  body('content')
    .optional()
    .isString()
    .withMessage('Le contenu doit être une chaîne de caractères'),
  
  body('isTemplate')
    .optional()
    .isBoolean()
    .withMessage('isTemplate doit être un booléen'),
  
  validateResults
];

/**
 * Validation pour la mise à jour d'un document
 */
const validateDocumentUpdate = [
  param('id')
    .isMongoId()
    .withMessage('ID de document non valide'),
  
  body('title')
    .optional()
    .trim()
    .isLength({ min: 3, max: 100 })
    .withMessage('Le titre doit contenir entre 3 et 100 caractères')
    .escape(),
  
  body('content')
    .optional()
    .isString()
    .withMessage('Le contenu doit être une chaîne de caractères'),
  
  body('type')
    .optional()
    .isIn(['document', 'presentation', 'spreadsheet', 'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'jpg', 'jpeg', 'png'])
    .withMessage('Type de document non valide'),
  
  validateResults
];

/**
 * Validation pour la création d'un utilisateur
 */
const validateUserCreation = [
  body('firstName')
    .trim()
    .notEmpty()
    .withMessage('Le prénom est requis')
    .isLength({ min: 2, max: 50 })
    .withMessage('Le prénom doit contenir entre 2 et 50 caractères')
    .escape(),
  
  body('lastName')
    .trim()
    .notEmpty()
    .withMessage('Le nom est requis')
    .isLength({ min: 2, max: 50 })
    .withMessage('Le nom doit contenir entre 2 et 50 caractères')
    .escape(),
  
  body('email')
    .trim()
    .notEmpty()
    .withMessage('L\'email est requis')
    .isEmail()
    .withMessage('Email non valide')
    .normalizeEmail(),
  
  body('password')
    .trim()
    .notEmpty()
    .withMessage('Le mot de passe est requis')
    .isLength({ min: 8 })
    .withMessage('Le mot de passe doit contenir au moins 8 caractères')
    .matches(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])/)
    .withMessage('Le mot de passe doit contenir au moins un chiffre, une lettre majuscule, une lettre minuscule et un caractère spécial'),
  
  validateResults
];

/**
 * Validation pour la connexion d'un utilisateur
 */
const validateUserLogin = [
  body('email')
    .trim()
    .notEmpty()
    .withMessage('L\'email est requis')
    .isEmail()
    .withMessage('Email non valide')
    .normalizeEmail(),
  
  body('password')
    .trim()
    .notEmpty()
    .withMessage('Le mot de passe est requis'),
  
  validateResults
];

/**
 * Validation pour les paramètres d'ID MongoDB
 */
const validateMongoId = [
  param('id')
    .isMongoId()
    .withMessage('ID non valide'),
  
  validateResults
];

/**
 * Validation pour les paramètres de pagination
 */
const validatePagination = [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('Le numéro de page doit être un entier positif'),
  
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('La limite doit être un entier entre 1 et 100'),
  
  validateResults
];

/**
 * Sanitizer pour les données HTML 
 * (à utiliser quand on autorise certains tags HTML, mais pas tous)
 */
const sanitizeHtml = (input) => {
  // Vous pouvez utiliser DOMPurify ou une autre bibliothèque ici
  // Ceci est une implémentation simple pour l'exemple
  if (!input) return input;
  
  // Supprimer les balises script et les attributs dangereux
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+=/gi, '')
    .replace(/style=/gi, '');
};

module.exports = {
  validateResults,
  validateDocumentCreation,
  validateDocumentUpdate,
  validateUserCreation,
  validateUserLogin,
  validateMongoId,
  validatePagination,
  sanitizeHtml
}; 
const multer = require('multer');
const path = require('path');

// Configuration de stockage pour les documents
const documentStorage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/documents');
  },
  filename: function (req, file, cb) {
    // Générer un nom de fichier unique
    cb(null, `${Date.now()}-${file.originalname.replace(/\s+/g, '-')}`);
  }
});

// Configuration de stockage pour les modèles
const templateStorage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/templates');
  },
  filename: function (req, file, cb) {
    // Générer un nom de fichier unique
    cb(null, `${Date.now()}-${file.originalname.replace(/\s+/g, '-')}`);
  }
});

// Filtrer les types de fichiers autorisés
const fileFilter = (req, file, cb) => {
  // Types MIME autorisés
  const allowedMimeTypes = [
    'application/pdf', // PDF
    'application/msword', // DOC
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // DOCX
    'text/plain', // TXT
    'application/vnd.ms-excel', // XLS
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // XLSX
    'application/vnd.ms-powerpoint', // PPT
    'application/vnd.openxmlformats-officedocument.presentationml.presentation', // PPTX
    'image/jpeg', // JPG, JPEG
    'image/png', // PNG
  ];

  if (allowedMimeTypes.includes(file.mimetype)) {
    // Accepter le fichier
    cb(null, true);
  } else {
    // Rejeter le fichier
    cb(new Error('Type de fichier non pris en charge'), false);
  }
};

// Middleware pour uploader des documents
const uploadDocument = multer({
  storage: documentStorage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10Mo max
  },
  fileFilter: fileFilter
});

// Middleware pour uploader des modèles
const uploadTemplate = multer({
  storage: templateStorage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10Mo max
  },
  fileFilter: fileFilter
});

module.exports = { uploadDocument, uploadTemplate }; 
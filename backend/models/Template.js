const mongoose = require('mongoose');

const templateSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Veuillez fournir un nom de modèle'],
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  type: {
    type: String,
    required: [true, 'Veuillez spécifier le type de modèle'],
    enum: ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx']
  },
  category: {
    type: String,
    required: [true, 'Veuillez spécifier une catégorie de modèle'],
    trim: true
  },
  thumbnail: {
    type: String,
    default: ''
  },
  path: {
    type: String,
    required: [true, 'Le chemin du fichier modèle est requis']
  },
  size: {
    type: Number, // taille en bytes
    required: [true, 'La taille du fichier modèle est requise']
  },
  isPublic: {
    type: Boolean,
    default: false
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  usage: {
    type: Number,
    default: 0
  },
  tags: [{
    type: String,
    trim: true
  }],
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, { timestamps: true });

// Middleware pour mis à jour de 'updatedAt' avant chaque enregistrement
templateSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Méthode pour incrémenter le compteur d'utilisation
templateSchema.methods.incrementUsage = function() {
  this.usage += 1;
  return this.save();
};

module.exports = mongoose.model('Template', templateSchema); 
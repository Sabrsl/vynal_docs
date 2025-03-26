const mongoose = require('mongoose');

const documentSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Veuillez fournir un nom de document'],
    trim: true
  },
  type: {
    type: String,
    required: [true, 'Veuillez spécifier le type de document'],
    enum: ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'jpg', 'jpeg', 'png']
  },
  size: {
    type: Number, // taille en bytes
    required: [true, 'La taille du document est requise']
  },
  path: {
    type: String,
    required: [true, 'Le chemin du fichier est requis']
  },
  owner: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Chaque document doit avoir un propriétaire']
  },
  category: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category',
    default: null
  },
  sharedWith: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    permission: {
      type: String,
      enum: ['view', 'edit', 'admin'],
      default: 'view'
    }
  }],
  tags: [{
    type: String,
    trim: true
  }],
  isFavorite: {
    type: Boolean,
    default: false
  },
  isDeleted: {
    type: Boolean,
    default: false
  },
  deletedAt: {
    type: Date,
    default: null
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  },
  lastAccessedAt: {
    type: Date,
    default: Date.now
  }
}, { timestamps: true });

// Middleware pour mis à jour de 'updatedAt' avant chaque enregistrement
documentSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Méthode pour marquer un document comme supprimé (corbeille)
documentSchema.methods.moveToTrash = function() {
  this.isDeleted = true;
  this.deletedAt = Date.now();
  return this.save();
};

// Méthode pour restaurer un document de la corbeille
documentSchema.methods.restore = function() {
  this.isDeleted = false;
  this.deletedAt = null;
  return this.save();
};

module.exports = mongoose.model('Document', documentSchema); 
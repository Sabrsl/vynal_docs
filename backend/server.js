const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
const fetch = require('node-fetch');
const connectDB = require('./config/db');
const { errorHandler, notFound } = require('./middlewares/errorMiddleware');

// Routes
const documentRoutes = require('./routes/documentRoutes');
const userRoutes = require('./routes/userRoutes');
const templateRoutes = require('./routes/templateRoutes');
const categoryRoutes = require('./routes/categoryRoutes');

// Configuration
dotenv.config();
const app = express();
const PORT = process.env.PORT || 5000;
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';

// Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());
app.use(morgan('dev'));

// Servir les fichiers statiques
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Routes
app.use('/api/documents', documentRoutes);
app.use('/api/users', userRoutes);
app.use('/api/templates', templateRoutes);
app.use('/api/categories', categoryRoutes);

// Proxy pour Ollama
app.get('/api/models', async (req, res) => {
  try {
    const response = await fetch(`${OLLAMA_URL}/api/tags`);
    if (!response.ok) {
      throw new Error(`Erreur Ollama: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Erreur lors de la récupération des modèles:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/generate', async (req, res) => {
  try {
    const response = await fetch(`${OLLAMA_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });
    
    if (!response.ok) {
      throw new Error(`Erreur Ollama: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Erreur lors de la génération:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/pull', async (req, res) => {
  try {
    const response = await fetch(`${OLLAMA_URL}/api/pull`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });
    
    if (!response.ok) {
      throw new Error(`Erreur Ollama: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Erreur lors du téléchargement du modèle:', error);
    res.status(500).json({ error: error.message });
  }
});

// Page d'accueil de l'API
app.get('/', (req, res) => {
  res.json({
    message: 'Bienvenue sur l\'API Vynal Docs',
    version: '1.0.0',
    status: 'online'
  });
});

// Middleware pour les routes inexistantes
app.use(notFound);

// Middleware de gestion des erreurs
app.use(errorHandler);

// Connexion à MongoDB et démarrage du serveur
connectDB()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Serveur en cours d'exécution sur le port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error('Erreur au démarrage du serveur:', err.message);
    process.exit(1);
  });

// Gestion des erreurs non captées
process.on('unhandledRejection', (err) => {
  console.log('UNHANDLED REJECTION! 💥 Shutting down...');
  console.log(err.name, err.message);
  process.exit(1);
}); 
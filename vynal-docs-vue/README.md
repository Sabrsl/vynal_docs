# Vynal Docs - Interface utilisateur Vue.js

Interface utilisateur moderne pour Vynal Docs, inspirée du design système de n8n.

## Caractéristiques

- Design épuré et moderne
- Composants réutilisables
- Système de couleurs cohérent
- Responsive design
- Interface de gestion documentaire

## Pile technologique

- Vue.js 3
- Vue Router
- SCSS
- Boxicons (pour les icônes)
- Police Inter

## Structure du projet

```
vynal-docs-vue/
│
├── public/                   # Ressources statiques
│   ├── index.html            # Template HTML principal
│   └── favicon.ico           # Favicon
│
├── src/                      # Code source
│   ├── assets/               # Images et autres ressources
│   │   ├── logo.svg          # Logo de l'application
│   │   └── avatar.svg        # Avatar utilisateur par défaut
│   │
│   ├── components/           # Composants Vue réutilisables
│   │   ├── NButton.vue       # Composant bouton
│   │   ├── NCard.vue         # Composant carte
│   │   └── NInput.vue        # Composant input
│   │
│   ├── router/               # Configuration du routeur
│   │   └── index.js          # Définition des routes
│   │
│   ├── styles/               # Styles globaux
│   │   ├── base.scss         # Styles de base
│   │   ├── variables.scss    # Variables SCSS (couleurs, espacements, etc.)
│   │   └── components/       # Styles spécifiques aux composants
│   │       ├── button.scss   # Styles pour les boutons
│   │       ├── card.scss     # Styles pour les cartes
│   │       └── input.scss    # Styles pour les formulaires
│   │
│   ├── views/                # Pages de l'application
│   │   ├── DocumentsView.vue # Vue Documents
│   │   └── ...               # Autres vues
│   │
│   ├── App.vue               # Composant principal
│   └── main.js               # Point d'entrée de l'application
│
├── package.json              # Dépendances et scripts
└── README.md                 # Documentation
```

## Installation

```bash
# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run serve

# Compiler pour la production
npm run build
```

## Design système

Le design système est inspiré de n8n avec:

- Une palette de couleurs principale basée sur le violet (#6933ff)
- Des espacements cohérents
- Des typographies claires
- Des ombres subtiles
- Des composants modulaires

### Composants principaux

- **Boutons**: Différentes variantes (primary, outlined, text) et tailles
- **Cartes**: Pour l'affichage des informations en blocs
- **Inputs**: Champs de formulaire avec différentes variantes
- **Tables**: Pour l'affichage des listes de documents
- **Navigation**: Barre latérale et en-tête

## Auteur

Développé pour Vynal Docs.

## Licence

Propriétaire - Tous droits réservés 
# VynalDocs

Application de gestion et d'automatisation de documents avec reconnaissance optique de caractères et intelligence artificielle.

## Déploiement

L'application est déployée sur Vercel à l'adresse suivante :
[https://vynal-docs.vercel.app](https://vynal-docs.vercel.app)

## Développement local

Pour lancer l'application en développement local :

1. Démarrer le backend :
```
python -m uvicorn index:app --reload
```

2. Démarrer le frontend :
```
cd frontend
npm start
```

L'application sera accessible sur http://localhost:3004

## Technologies utilisées

- Frontend : React.js
- Backend : FastAPI (Python)
- OCR : Tesseract
- Déploiement : Vercel

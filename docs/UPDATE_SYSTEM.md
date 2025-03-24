# Système de Mise à Jour

Ce document explique comment utiliser le système de mise à jour sécurisé de l'application.

## Configuration initiale

1. **Créer un projet Google Cloud**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com)
   - Créez un nouveau projet
   - Activez l'API Google Drive
   - Créez des identifiants OAuth 2.0
   - Téléchargez le fichier `credentials.json`

2. **Configurer Google Drive**
   - Créez un dossier dédié pour les mises à jour
   - Notez l'ID du dossier (visible dans l'URL)
   - Partagez le dossier avec les permissions appropriées

3. **Configuration de l'application**
   - Placez `credentials.json` dans le dossier racine de l'application
   - Configurez les variables dans les scripts d'exemple :
     - `FOLDER_ID`: ID du dossier Google Drive
     - `ENCRYPTION_PASSWORD`: Mot de passe pour le chiffrement/déchiffrement

## Création d'une mise à jour

Utilisez le script `examples/create_update.py` pour créer et téléverser une mise à jour :

1. **Modifiez les informations de mise à jour**
   ```python
   update_info = {
       'version': '1.1.0',  # Nouvelle version
       'description': 'Description des changements',
       'min_version': '1.0.0',  # Version minimale requise
       'files_to_update': [  # Fichiers/dossiers à inclure
           'app/',
           'utils/',
           'config.json'
       ],
       'exclude_patterns': [  # Patterns à exclure
           '*.pyc',
           '__pycache__',
           '*.log'
       ]
   }
   ```

2. **Exécutez le script**
   ```bash
   python examples/create_update.py
   ```

Le script va :
- Créer un package ZIP des fichiers sélectionnés
- Chiffrer le package
- Calculer le checksum
- Téléverser sur Google Drive
- Nettoyer les fichiers temporaires

## Installation des mises à jour

Utilisez le script `examples/update_app.py` pour vérifier et installer les mises à jour :

1. **Exécutez le script**
   ```bash
   python examples/update_app.py
   ```

Le script va :
- Vérifier la version actuelle
- Rechercher des mises à jour disponibles
- Afficher les informations de la mise à jour
- Demander confirmation
- Télécharger et vérifier le package
- Installer la mise à jour
- Mettre à jour la version

## Sécurité

Le système inclut plusieurs mesures de sécurité :

- **Chiffrement** : Les packages sont chiffrés avec AES-256
- **Vérification d'intégrité** : Checksums SHA-256
- **Contrôle de version** : Vérification de compatibilité
- **Sauvegardes** : Création automatique de backups
- **Nettoyage** : Suppression des fichiers temporaires

## Dépannage

1. **Erreur d'authentification Google Drive**
   - Vérifiez que `credentials.json` est présent
   - Assurez-vous que l'API est activée
   - Vérifiez les permissions du dossier

2. **Erreur de chiffrement/déchiffrement**
   - Vérifiez que le mot de passe est correct
   - Assurez-vous que le fichier n'est pas corrompu

3. **Erreur lors de l'installation**
   - Vérifiez les logs pour plus de détails
   - Utilisez la fonction de restauration si nécessaire

## Bonnes pratiques

1. **Versionnage**
   - Utilisez le versionnage sémantique (MAJOR.MINOR.PATCH)
   - Documentez les changements
   - Testez la mise à jour avant de la publier

2. **Sécurité**
   - Changez régulièrement le mot de passe de chiffrement
   - Limitez l'accès au dossier Google Drive
   - Surveillez les logs pour détecter les anomalies

3. **Maintenance**
   - Nettoyez régulièrement les anciennes mises à jour
   - Vérifiez les backups
   - Mettez à jour la documentation 
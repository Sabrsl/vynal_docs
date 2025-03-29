# VynalDocs - Panneau d'Administration

Ce projet est le panneau d'administration séparé pour l'application VynalDocs. Il permet aux administrateurs de gérer les utilisateurs, les licences, les paramètres système et d'envoyer des notifications.

## Avantages d'une application admin séparée

- **Séparation des responsabilités** : L'application principale est destinée aux utilisateurs, tandis que le panneau d'administration est exclusivement pour la gestion.
- **Sécurité renforcée** : Interface d'administration isolée avec des contrôles d'accès plus stricts.
- **Performance** : L'application utilisateur reste légère sans les composants administratifs.
- **Maintenance et évolutivité** : Possibilité de mettre à jour le panneau d'administration sans impacter l'application principale.
- **Déploiement indépendant** : Peut être hébergé sur un domaine ou un sous-domaine distinct pour un accès restreint.

## Technologies utilisées

- **Frontend** : React, Tailwind CSS, shadcn/ui
- **Authentification** : JWT avec vérification de rôle admin
- **Communication avec le backend** : API REST 

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-organisation/vynaldocs-admin-panel.git
   cd vynaldocs-admin-panel
   ```

2. Installez les dépendances :
   ```bash
   npm install
   ```

3. Créez un fichier `.env` à la racine du projet avec les variables suivantes :
   ```
   REACT_APP_API_URL=http://localhost:3000
   ```

4. Démarrez l'application en mode développement :
   ```bash
   npm start
   ```

L'application sera accessible à l'adresse [http://localhost:3000](http://localhost:3000).

## Fonctionnalités

### Tableau de bord
- Vue d'ensemble des statistiques système
- Graphiques d'utilisation
- Métriques clés

### Gestion des utilisateurs
- Liste des utilisateurs avec filtrage et pagination
- Création, modification et suppression d'utilisateurs
- Activation/désactivation de comptes

### Gestion des licences
- Liste des licences avec filtrage et pagination
- Création, modification et suppression de licences
- Activation/désactivation de licences

### Paramètres système
- Configuration des paramètres généraux
- Gestion des limites et restrictions
- Configuration des notifications

### Notifications
- Envoi de messages à tous les utilisateurs ou à des groupes spécifiques
- Historique des notifications envoyées

## Sécurité

Le panneau d'administration est sécurisé par :
- Authentification JWT
- Vérification du rôle administrateur à chaque requête
- Expirations de session
- Protection contre le CSRF

## Déploiement

Pour construire l'application pour la production :

```bash
npm run build
```

Cela créera un dossier `build` avec les fichiers optimisés pour la production.

## Connexion au backend

Ce panneau d'administration se connecte au même backend que l'application principale VynalDocs. Assurez-vous que le backend est en cours d'exécution et accessible à l'URL spécifiée dans `.env`.

## Contribution

1. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
2. Committez vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
3. Poussez vers la branche (`git push origin feature/ma-fonctionnalite`)
4. Ouvrez une Pull Request

## Licence

Ce projet est sous licence [MIT](LICENSE). 
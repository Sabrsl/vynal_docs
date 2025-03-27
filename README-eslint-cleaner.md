# VynalDocs ESLint Cleaner 🧹

Ensemble d'outils pour nettoyer et corriger automatiquement les problèmes ESLint dans votre projet VynalDocs.

## 📋 Présentation

Ce projet contient plusieurs scripts pour résoudre automatiquement les problèmes ESLint les plus courants dans votre codebase React :

1. **Variables non utilisées** (`no-unused-vars`)
2. **Dépendances manquantes dans les hooks** (`react-hooks/exhaustive-deps`)  
3. **Utilisation de fonctions avant leur définition** (`no-use-before-define`)

## 🚀 Utilisation

### Pour Windows (PowerShell)

Exécutez simplement le script PowerShell qui orchestrera tout le processus :

```powershell
.\clean-eslint.ps1
```

### Pour les utilisateurs JavaScript

Vous pouvez exécuter les scripts individuellement :

1. **Nettoyer tous les problèmes ESLint** :
   ```bash
   node clean-eslint.js
   ```

2. **Résoudre uniquement les problèmes de useEffect** :
   ```bash
   node fix-useEffect-deps.js
   ```

3. **Nettoyer uniquement les variables inutilisées** :
   ```bash
   node remove-unused-vars.js
   ```

## ✅ Ce que font les scripts

### 1. `clean-eslint.js`
- Analyse tous les fichiers JS/JSX
- Détecte et corrige plusieurs types de problèmes ESLint
- Produit un résumé des problèmes trouvés et corrigés

### 2. `fix-useEffect-deps.js`
- Se concentre spécifiquement sur les hooks useEffect
- Ajoute des commentaires `eslint-disable-next-line` pour les dépendances manquantes
- Analyse le corps des useEffect pour détecter les variables utilisées

### 3. `remove-unused-vars.js`
- Détecte les variables déclarées mais jamais utilisées
- Stratégies différentes selon le type de variable :
  - **Variables de débogage** : Les commente avec un préfixe `// DEBUG:`
  - **Variables d'état React** : Préfixe avec `_` pour les marquer comme intentionnellement inutilisées
  - **Autres variables** : Ajoute un commentaire `eslint-disable-next-line`

## 🔧 Stratégies de correction

### Pour les variables non utilisées

- **Préfixe avec `_`** : Pour les variables que vous voulez garder mais ne pas utiliser
  ```javascript
  const _unusedVar = something();  // ESLint ignorera cette variable
  ```

- **Commenter la déclaration** : Pour les variables temporaires de débogage
  ```javascript
  // DEBUG: const data = await api.getData();
  ```

- **Désactiver ESLint** : Pour les cas spéciaux
  ```javascript
  // eslint-disable-next-line no-unused-vars
  const specialVar = compute();
  ```

### Pour les useEffect avec dépendances manquantes

- **Ajouter les dépendances manquantes** (solution optimale mais peut changer la logique) :
  ```javascript
  useEffect(() => {
    doSomething(value);
  }, [value]); // Ajout de la dépendance
  ```

- **Désactiver l'avertissement** (solution temporaire) :
  ```javascript
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    doSomething(value);
  }, []);
  ```

## 📝 Bonnes pratiques React

- Utilisez `useCallback` pour les fonctions passées en props ou utilisées dans useEffect
- Utilisez `useMemo` pour les valeurs calculées coûteuses
- Préférez extraire la logique complexe dans des hooks personnalisés
- Utilisez le préfixe `_` pour les variables intentionnellement inutilisées

## ⚠️ Limitations

- Les scripts font leur meilleur effort pour détecter les problèmes, mais certains cas complexes peuvent être manqués
- La correction automatique est une solution temporaire - idéalement, refactorisez le code pour une meilleure structure
- Certaines corrections peuvent nécessiter une vérification manuelle pour s'assurer qu'elles ne changent pas la logique

## 🤝 Contribution

N'hésitez pas à améliorer ces scripts pour mieux répondre aux besoins spécifiques de votre projet !

---

*Ces scripts ont été créés pour vous aider à maintenir une codebase propre et à vous concentrer sur le développement de fonctionnalités plutôt que sur la correction des avertissements ESLint.* 
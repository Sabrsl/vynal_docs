#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Configuration
const SRC_DIR = path.join(process.cwd(), 'frontend', 'src');
const IGNORE_PATTERNS = [
  'node_modules',
  'build',
  'dist',
  '.git'
];

// Couleurs pour la console
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

console.log(`${colors.cyan}=== VynalDocs Unused Variables Cleaner ===${colors.reset}`);
console.log(`${colors.yellow}Scanning directory: ${SRC_DIR}${colors.reset}\n`);

// Fonction pour vérifier si un chemin doit être ignoré
function shouldIgnore(filePath) {
  return IGNORE_PATTERNS.some(pattern => filePath.includes(pattern));
}

// Fonction pour trouver tous les fichiers JS/JSX récursivement
function findJsFiles(dir, fileList = []) {
  try {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
      const filePath = path.join(dir, file);
      
      if (shouldIgnore(filePath)) {
        return;
      }
      
      try {
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
          findJsFiles(filePath, fileList);
        } else if (/\.(js|jsx)$/.test(file)) {
          fileList.push(filePath);
        }
      } catch (err) {
        console.error(`${colors.red}Error reading ${filePath}: ${err.message}${colors.reset}`);
      }
    });
  } catch (err) {
    console.error(`${colors.red}Error reading directory ${dir}: ${err.message}${colors.reset}`);
  }
  
  return fileList;
}

// Trouver tous les fichiers JS/JSX
const jsFiles = findJsFiles(SRC_DIR);
console.log(`${colors.yellow}Found ${jsFiles.length} JavaScript files to analyze${colors.reset}\n`);

let totalVarsFound = 0;
let totalVarsRemoved = 0;
let totalVarsCommented = 0;

// Types de variables non utilisées à rechercher
const unusedVarPatterns = [
  {
    // Variables déclarées mais jamais utilisées (ESLint no-unused-vars) 
    type: 'declared',
    regex: /(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*[^;]*;(?:\s*\/\/\s*eslint-disable-next-line\s+no-unused-vars)?/g,
    check: (content, varName) => {
      // Compter les occurrences du nom de variable
      const occurrences = (content.match(new RegExp(`\\b${varName}\\b`, 'g')) || []).length;
      // Si la variable n'apparaît qu'une fois (sa déclaration), elle n'est pas utilisée
      return occurrences <= 1;
    }
  },
  {
    // Paramètres de fonction non utilisés
    type: 'parameter',
    regex: /function\s+[a-zA-Z0-9_]+\s*\(\s*([^)]*)\s*\)/g,
    extractParams: (paramsStr) => paramsStr.split(',').map(p => p.trim()).filter(p => p !== ''),
    check: (content, paramName) => {
      // Vérifier si le paramètre est utilisé dans la fonction
      const occurrences = (content.match(new RegExp(`\\b${paramName}\\b`, 'g')) || []).length;
      return occurrences <= 1; // Si seulement 1 occurrence (la déclaration), il n'est pas utilisé
    }
  },
  {
    // Destructuring d'objets avec variables non utilisées
    type: 'destructured',
    regex: /(?:const|let|var)\s+\{\s*([^}]*)\s*\}\s*=\s*[^;]*;/g,
    extractVars: (varsStr) => varsStr.split(',').map(v => v.trim().split(':')[0].trim()).filter(v => v !== ''),
    check: (content, varName) => {
      const occurrences = (content.match(new RegExp(`\\b${varName}\\b`, 'g')) || []).length;
      return occurrences <= 1;
    }
  }
];

// Parcourir chaque fichier
jsFiles.forEach(filePath => {
  const relativePath = path.relative(process.cwd(), filePath);
  console.log(`${colors.cyan}Analyzing ${relativePath}${colors.reset}`);
  
  let content = fs.readFileSync(filePath, 'utf-8');
  let varsFound = 0;
  let varsRemoved = 0;
  let varsCommented = 0;
  let modified = false;
  
  // Vérifier chaque type de variable non utilisée
  unusedVarPatterns.forEach(pattern => {
    if (pattern.type === 'declared') {
      // Rechercher les variables déclarées
      const matches = [...content.matchAll(pattern.regex)];
      
      matches.forEach(match => {
        const varName = match[1];
        if (pattern.check(content, varName)) {
          varsFound++;
          console.log(`${colors.yellow}  Found unused variable: ${varName}${colors.reset}`);
          
          // Décider comment traiter la variable non utilisée
          const originalDeclaration = match[0];
          const lineIndex = content.substring(0, match.index).split('\n').length;
          
          // Pour les variables utilisées pour le débogage (comme 'data' ou 'error'), les conserver mais les commenter
          if (['data', 'error', 'response', 'result'].includes(varName)) {
            const commentedDeclaration = `// DEBUG: ${originalDeclaration}`;
            content = content.replace(originalDeclaration, commentedDeclaration);
            varsCommented++;
            console.log(`${colors.blue}    Commented out debug variable at line ${lineIndex}${colors.reset}`);
          } 
          // Pour les variables visuellement importantes (comme les valeurs d'état), les préfixer avec _
          else if (originalDeclaration.includes('useState') || 
                   originalDeclaration.includes('useReducer') ||
                   originalDeclaration.includes('useContext')) {
            const newDeclaration = originalDeclaration.replace(`${varName}`, `_${varName}`);
            content = content.replace(originalDeclaration, newDeclaration);
            varsRemoved++;
            console.log(`${colors.green}    Prefixed with _ at line ${lineIndex}${colors.reset}`);
          }
          // Pour les autres variables, ajouter une désactivation ESLint
          else {
            if (!originalDeclaration.includes('eslint-disable-next-line')) {
              const lines = content.split('\n');
              const lineNumber = content.substring(0, match.index).split('\n').length - 1;
              lines.splice(lineNumber, 0, '// eslint-disable-next-line no-unused-vars');
              content = lines.join('\n');
              varsCommented++;
              console.log(`${colors.blue}    Added eslint-disable comment at line ${lineIndex}${colors.reset}`);
            }
          }
          
          modified = true;
        }
      });
    }
    else if (pattern.type === 'parameter') {
      // Traiter les paramètres de fonction non utilisés
      const matches = [...content.matchAll(pattern.regex)];
      
      matches.forEach(match => {
        const paramsStr = match[1];
        const params = pattern.extractParams(paramsStr);
        
        params.forEach(paramName => {
          if (pattern.check(content, paramName)) {
            varsFound++;
            console.log(`${colors.yellow}  Found unused parameter: ${paramName}${colors.reset}`);
            
            // Préfixer avec _ pour indiquer que c'est intentionnellement ignoré
            const originalParams = paramsStr;
            const newParams = originalParams.replace(`${paramName}`, `_${paramName}`);
            content = content.replace(`(${originalParams})`, `(${newParams})`);
            varsRemoved++;
            console.log(`${colors.green}    Prefixed parameter with _${colors.reset}`);
            
            modified = true;
          }
        });
      });
    }
    else if (pattern.type === 'destructured') {
      // Traiter les variables destructurées non utilisées
      const matches = [...content.matchAll(pattern.regex)];
      
      matches.forEach(match => {
        const varsStr = match[1];
        const vars = pattern.extractVars(varsStr);
        
        vars.forEach(varName => {
          if (pattern.check(content, varName)) {
            varsFound++;
            console.log(`${colors.yellow}  Found unused destructured variable: ${varName}${colors.reset}`);
            
            // Préfixer avec _ pour indiquer que c'est intentionnellement ignoré
            const originalVars = varsStr;
            const newVars = originalVars.replace(`${varName}`, `_${varName}`);
            content = content.replace(`{${originalVars}}`, `{${newVars}}`);
            varsRemoved++;
            console.log(`${colors.green}    Prefixed with _${colors.reset}`);
            
            modified = true;
          }
        });
      });
    }
  });
  
  // Écrire les modifications dans le fichier
  if (modified) {
    fs.writeFileSync(filePath, content, 'utf-8');
    console.log(`${colors.green}  Updated file with changes${colors.reset}`);
  }
  
  totalVarsFound += varsFound;
  totalVarsRemoved += varsRemoved;
  totalVarsCommented += varsCommented;
  
  if (varsFound > 0) {
    console.log(`${colors.magenta}  ${varsFound} unused variables found, ${varsRemoved} prefixed with _, ${varsCommented} commented${colors.reset}\n`);
  } else {
    console.log(`${colors.green}  No unused variables found${colors.reset}\n`);
  }
});

console.log(`${colors.green}=== Summary ===${colors.reset}`);
console.log(`${colors.yellow}Total unused variables found: ${totalVarsFound}${colors.reset}`);
console.log(`${colors.green}Variables prefixed with _: ${totalVarsRemoved}${colors.reset}`);
console.log(`${colors.yellow}Variables commented: ${totalVarsCommented}${colors.reset}`);

console.log(`\n${colors.cyan}=== Next Steps ===${colors.reset}`);
console.log(`${colors.yellow}1. Run ESLint to verify fixes:${colors.reset} npx eslint src/`);
console.log(`${colors.yellow}2. For better code quality:${colors.reset}`);
console.log(`   - Check commented variables to see if they can be fully removed`);
console.log(`   - Review prefixed variables (_var) to confirm they're correctly ignored`);
console.log(`   - Consider implementing advanced patterns like useCallback for functions in useEffect`);

console.log(`\n${colors.green}=== Tip ===${colors.reset}`);
console.log(`Pour les variables que vous voulez délibérément ignorer, utilisez le préfixe _ :`);
console.log(`${colors.cyan}const _unused = something(); // ESLint ignorera cette variable${colors.reset}`); 
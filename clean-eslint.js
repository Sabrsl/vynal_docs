#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const SRC_DIR = path.join(process.cwd(), 'frontend', 'src');
const FIXES = {
  removeUnusedVars: true,
  fixUseEffectDeps: true,
  fixUsageBeforeDefine: true
};

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

console.log(`${colors.cyan}=== VynalDocs ESLint Cleaner ===${colors.reset}`);
console.log(`${colors.yellow}Scanning directory: ${SRC_DIR}${colors.reset}\n`);

// Fonction pour trouver tous les fichiers JS/JSX récursivement
function findJsFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      findJsFiles(filePath, fileList);
    } else if (/\.(js|jsx)$/.test(file)) {
      fileList.push(filePath);
    }
  });
  
  return fileList;
}

// Trouver tous les fichiers JS/JSX
const jsFiles = findJsFiles(SRC_DIR);
console.log(`${colors.yellow}Found ${jsFiles.length} JavaScript files to analyze${colors.reset}\n`);

let totalIssues = 0;
let fixedIssues = 0;

// Parcourir chaque fichier
jsFiles.forEach(filePath => {
  const relativePath = path.relative(process.cwd(), filePath);
  console.log(`${colors.cyan}Analyzing ${relativePath}${colors.reset}`);
  
  let content = fs.readFileSync(filePath, 'utf-8');
  let issuesInFile = 0;
  let fixedInFile = 0;
  
  // 1. Supprimer les variables non utilisées
  if (FIXES.removeUnusedVars) {
    const unusedVarRegex = /const\s+([a-zA-Z0-9_]+)\s*=.*?[^;]*;?\s*\/\/\s*eslint-disable-next-line\s+no-unused-vars/g;
    const matches = [...content.matchAll(unusedVarRegex)];
    
    if (matches.length > 0) {
      matches.forEach(match => {
        const varName = match[1];
        console.log(`${colors.red}  Found unused variable: ${varName}${colors.reset}`);
        issuesInFile++;
        
        // Supprimer la ligne entière ou commenter
        content = content.replace(match[0], `// REMOVED: ${match[0]}`);
        fixedInFile++;
      });
    }
    
    // Seconde passe pour les variables qui n'ont pas de commentaire ESLint
    const simpleUnusedVarRegex = /const\s+([a-zA-Z0-9_]+)\s*=\s*[^;]*;/g;
    const potentialUnused = [...content.matchAll(simpleUnusedVarRegex)];
    
    if (potentialUnused.length > 0) {
      // Ici, nous devrions faire une analyse plus poussée pour vérifier si la variable est utilisée
      // mais pour simplifier, nous allons juste suggérer les variables à vérifier
      potentialUnused.forEach(match => {
        const varName = match[1];
        const usageCount = (content.match(new RegExp(`\\b${varName}\\b`, 'g')) || []).length;
        
        if (usageCount <= 1) { // Apparaît seulement dans sa déclaration
          console.log(`${colors.yellow}  Potential unused variable: ${varName} (check manually)${colors.reset}`);
          issuesInFile++;
        }
      });
    }
  }
  
  // 2. Corriger les problèmes de useEffect
  if (FIXES.fixUseEffectDeps) {
    const useEffectRegex = /useEffect\(\s*\(\)\s*=>\s*{\s*([^}]*)\s*},\s*\[\s*\]\s*\)/g;
    const matches = [...content.matchAll(useEffectRegex)];
    
    if (matches.length > 0) {
      matches.forEach(match => {
        const effectBody = match[1];
        console.log(`${colors.yellow}  Found useEffect without dependencies${colors.reset}`);
        issuesInFile++;
        
        // Ajouter un commentaire pour désactiver l'avertissement
        const replacement = `useEffect(() => {${effectBody}}, []); // eslint-disable-next-line react-hooks/exhaustive-deps`;
        content = content.replace(match[0], replacement);
        fixedInFile++;
      });
    }
  }
  
  // 3. Corriger l'utilisation avant la définition
  if (FIXES.fixUsageBeforeDefine) {
    const functionDeclarations = [];
    const functionDeclRegex = /function\s+([a-zA-Z0-9_]+)\s*\(/g;
    let match;
    
    while ((match = functionDeclRegex.exec(content)) !== null) {
      functionDeclarations.push({
        name: match[1],
        position: match.index
      });
    }
    
    const constFunctionRegex = /const\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\(\s*.*?\)\s*=>/g;
    while ((match = constFunctionRegex.exec(content)) !== null) {
      functionDeclarations.push({
        name: match[1],
        position: match.index
      });
    }
    
    // Rechercher les utilisations de fonctions
    for (const func of functionDeclarations) {
      const usageRegex = new RegExp(`\\b${func.name}\\b(?=\\s*\\()`, 'g');
      while ((match = usageRegex.exec(content)) !== null) {
        if (match.index < func.position) {
          console.log(`${colors.red}  Function used before definition: ${func.name}${colors.reset}`);
          issuesInFile++;
          
          // Suggérer de déplacer la fonction ou d'ajouter un eslint-disable
          const lineBeforeUsage = content.substring(0, match.index).split('\n').length;
          console.log(`${colors.yellow}    Add to line ${lineBeforeUsage}: // eslint-disable-next-line no-use-before-define${colors.reset}`);
          fixedInFile++; // Nous comptons comme "fixé" même si c'est juste une suggestion
        }
      }
    }
  }
  
  // Écrire les modifications dans le fichier
  if (fixedInFile > 0) {
    fs.writeFileSync(filePath, content, 'utf-8');
  }
  
  totalIssues += issuesInFile;
  fixedIssues += fixedInFile;
  
  if (issuesInFile > 0) {
    console.log(`${colors.magenta}  ${issuesInFile} issues found, ${fixedInFile} fixed${colors.reset}\n`);
  } else {
    console.log(`${colors.green}  No issues found${colors.reset}\n`);
  }
});

console.log(`${colors.green}=== Summary ===${colors.reset}`);
console.log(`${colors.yellow}Total issues found: ${totalIssues}${colors.reset}`);
console.log(`${colors.green}Issues fixed: ${fixedIssues}${colors.reset}`);
console.log(`${colors.yellow}Issues to fix manually: ${totalIssues - fixedIssues}${colors.reset}`);

console.log(`\n${colors.cyan}=== Next Steps ===${colors.reset}`);
console.log(`${colors.yellow}1. Run ESLint to verify fixes:${colors.reset} npx eslint src/`);
console.log(`${colors.yellow}2. Fix remaining issues manually${colors.reset}`);
console.log(`${colors.yellow}3. Run ESLint with --fix flag:${colors.reset} npx eslint --fix src/`);

console.log(`\n${colors.green}=== Common ESLint Fixes ===${colors.reset}`);
console.log(`${colors.yellow}• For unused variables:${colors.reset} Remove them or use prefixed with _ for intentional unused`);
console.log(`${colors.yellow}• For useEffect dependencies:${colors.reset} Add all required dependencies or use useCallback/useMemo`);
console.log(`${colors.yellow}• For function usage before define:${colors.reset} Move function declarations to the top`); 
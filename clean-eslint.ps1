# Script PowerShell pour nettoyer les problèmes ESLint dans votre projet VynalDocs

Write-Host "=== VynalDocs ESLint Cleaner PowerShell Script ===" -ForegroundColor Cyan
Write-Host "Cette opération va parcourir vos fichiers JavaScript et corriger les problèmes ESLint courants." -ForegroundColor Yellow
Write-Host

# 1. Exécuter notre script de nettoyage personnalisé
Write-Host "Étape 1: Exécution du script de nettoyage..." -ForegroundColor Cyan
node clean-eslint.js

# 2. Installer ESLint si nécessaire
Write-Host ""
Write-Host "Étape 2: Vérification d'ESLint..." -ForegroundColor Cyan
try {
    npm list eslint --depth=0
} catch {
    Write-Host "ESLint n'est pas installé. Installation..." -ForegroundColor Yellow
    npm install eslint --save-dev
}

# 3. Exécuter ESLint avec l'option --fix
Write-Host ""
Write-Host "Étape 3: Exécution d'ESLint avec l'option --fix..." -ForegroundColor Cyan
Write-Host "Cette opération peut prendre un moment..." -ForegroundColor Yellow

# Changer de répertoire vers frontend si nécessaire
if (Test-Path -Path "frontend") {
    Set-Location -Path "frontend"
    Write-Host "Travail dans le répertoire frontend..." -ForegroundColor Yellow
}

# Exécuter ESLint avec --fix
if (Test-Path -Path "node_modules\.bin\eslint.cmd") {
    # Si ESLint est installé localement
    & ".\node_modules\.bin\eslint.cmd" --fix src/
} else {
    # Sinon, utiliser npx
    npx eslint --fix src/
}

# 4. Afficher les problèmes restants
Write-Host ""
Write-Host "Étape 4: Affichage des problèmes restants..." -ForegroundColor Cyan
if (Test-Path -Path "node_modules\.bin\eslint.cmd") {
    & ".\node_modules\.bin\eslint.cmd" src/
} else {
    npx eslint src/
}

# 5. Instructions finales
Write-Host ""
Write-Host "=== Instructions finales ===" -ForegroundColor Green
Write-Host "1. Pour les problèmes que vous souhaitez ignorer temporairement, ajoutez:" -ForegroundColor Yellow
Write-Host "   // eslint-disable-next-line RULE_NAME" -ForegroundColor Cyan
Write-Host "   juste au-dessus de la ligne problématique."
Write-Host ""
Write-Host "2. Problèmes courants et solutions:" -ForegroundColor Yellow
Write-Host "   • no-unused-vars: Supprimez la variable ou ajoutez _ au début du nom" -ForegroundColor Cyan
Write-Host "   • react-hooks/exhaustive-deps: Ajoutez toutes les dépendances manquantes ou utilisez useCallback/useMemo" -ForegroundColor Cyan
Write-Host "   • no-use-before-define: Déplacez la déclaration de fonction avant son utilisation" -ForegroundColor Cyan
Write-Host ""
Write-Host "Script terminé!" -ForegroundColor Green 
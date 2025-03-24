#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour lancer l'interface d'administration complète avec tous les onglets.
Ce script utilise admin_main.py pour lancer l'interface d'administration avec
tous les composants (tableau de bord, utilisateurs, licences, paramètres, etc.)
"""

import os
import sys
import logging
import subprocess

# Configurer le logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VynalDocsAutomator.AdminLauncher")

def main():
    """
    Fonction principale pour lancer l'interface d'administration complète.
    """
    logger.info("Lancement de l'interface d'administration complète...")
    
    # Déterminer le chemin du fichier admin_main.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    admin_main_path = os.path.join(current_dir, "admin", "admin_main.py")
    
    # Vérifier que le fichier existe
    if not os.path.exists(admin_main_path):
        logger.error(f"Fichier admin_main.py introuvable à {admin_main_path}")
        print(f"Erreur : fichier admin_main.py introuvable à {admin_main_path}")
        return False
    
    try:
        # Exécuter le script d'administration
        logger.info(f"Exécution de {admin_main_path}")
        
        # Utiliser subprocess pour lancer le script dans un nouveau processus
        result = subprocess.run([sys.executable, admin_main_path], 
                               cwd=current_dir, 
                               check=True)
        
        logger.info(f"Interface d'administration terminée avec code de sortie {result.returncode}")
        return result.returncode == 0
    
    except subprocess.SubprocessError as e:
        logger.error(f"Erreur lors de l'exécution de l'interface d'administration: {str(e)}")
        print(f"Erreur lors de l'exécution : {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"Erreur inattendue : {str(e)}")
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 
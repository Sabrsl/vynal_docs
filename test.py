#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script temporaire pour tester l'intégration de la mise à jour automatique
avec l'interface de configuration à distance existante.
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VynalDocsAutomator.Test")

# Importer les modules nécessaires
try:
    from utils.auto_config_updater import AutoConfigUpdater
    from config import CONFIG_CHECK_INTERVAL
    
    # Comme CONFIG_DIR n'existe pas dans config.py, on le définit ici
    CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    logger.info(f"Modules importés avec succès, CONFIG_DIR: {CONFIG_DIR}")
except Exception as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
    sys.exit(1)

def test_auto_updater():
    """Teste le système de mise à jour automatique."""
    
    # Vérifier si un ID de fichier Google Drive est configuré
    drive_config_path = os.path.join(CONFIG_DIR, "google_drive_config.json")
    drive_file_id = None
    
    if os.path.exists(drive_config_path):
        try:
            with open(drive_config_path, 'r', encoding='utf-8') as f:
                drive_config = json.load(f)
                drive_file_id = drive_config.get('file_id')
                logger.info(f"ID de fichier Google Drive trouvé: {drive_file_id}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration Google Drive: {e}")
    
    if not drive_file_id:
        logger.warning("Aucun ID de fichier Google Drive configuré. Utilisation d'un ID de test.")
        drive_file_id = "1aBcDeF_gHiJkLmNoPqRsTuVwXyZ"
    
    # Chemin de la configuration locale
    local_config_path = os.path.join(CONFIG_DIR, "test_config.json")
    
    # Callback de test
    def on_config_updated(new_config):
        logger.info(f"Mise à jour de configuration détectée: {len(new_config)} éléments")
        for key in list(new_config.keys())[:5]:  # Afficher les 5 premières clés
            logger.info(f"  - {key}: {str(new_config[key])[:30]}...")
    
    # Créer et démarrer l'updater
    try:
        updater = AutoConfigUpdater(
            drive_file_id=drive_file_id,
            local_config_path=local_config_path,
            check_interval=CONFIG_CHECK_INTERVAL
        )
        updater.set_update_callback(on_config_updated)
        
        if updater.start():
            logger.info(f"Mise à jour automatique démarrée (intervalle: {CONFIG_CHECK_INTERVAL}s)")
            
            # Forcer une vérification immédiate
            result = updater.check_for_updates(force=True)
            logger.info(f"Résultat de la vérification forcée: {result}")
            
            # Attendre un peu
            time.sleep(5)
            
            # Arrêter l'updater
            updater.stop()
            logger.info("Mise à jour automatique arrêtée")
            
            return True
        else:
            logger.error("Impossible de démarrer la mise à jour automatique")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors du test de l'auto-updater: {e}")
        return False

if __name__ == "__main__":
    logger.info("Démarrage du test de mise à jour automatique...")
    
    # Tester l'auto-updater
    success = test_auto_updater()
    
    if success:
        logger.info("Test terminé avec succès")
    else:
        logger.error("Test échoué")
    
    logger.info("Test terminé") 
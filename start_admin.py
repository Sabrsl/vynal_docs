#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour lancer l'interface d'administration de configuration à distance.
"""

import os
import sys
import logging
import tkinter as tk

# Configurer le logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VynalDocsAutomator.AdminStarter")

def main():
    """Fonction principale pour lancer l'interface."""
    logger.info("Démarrage de l'interface d'administration...")
    
    # Ajouter le répertoire courant au PYTHONPATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Définir le chemin du fichier de configuration
    config_dir = os.path.join(current_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "remote_config.json")
    
    logger.info(f"Utilisation du fichier de configuration: {config_file}")
    
    # Importer après avoir configuré le chemin
    try:
        import customtkinter as ctk
        
        # Configuration de l'apparence
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Importer et lancer l'interface d'administration
        from admin.remote_config.remote_config_admin import RemoteConfigAdmin
        
        # Créer l'interface avec le chemin de configuration spécifié
        app = RemoteConfigAdmin(config_file_path=config_file)
        
        logger.info("Interface d'administration fermée.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'interface: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 
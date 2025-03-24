#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour l'interface d'administration de la configuration à distance.
Lance l'interface avec les onglets à gauche comme elle était à l'origine.
"""

import os
import sys
import logging
import customtkinter as ctk

# Configurer le logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VynalDocsAutomator.TestInterface")

# Configuration de l'apparence
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Importer directement depuis le même répertoire
from remote_config_admin import RemoteConfigAdmin

try:
    # Créer l'interface en mode autonome
    logger.info("Lancement de l'interface d'administration...")
    app = RemoteConfigAdmin()
    logger.info("Interface fermée.")
except Exception as e:
    logger.error(f"Erreur lors du lancement de l'interface: {str(e)}")
    import traceback
    traceback.print_exc() 
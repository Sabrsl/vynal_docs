#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour lancer l'interface d'administration complète avec tous les onglets.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox

# Configurer le logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VynalDocsAutomator.AdminLauncher")

def main():
    """
    Fonction principale pour lancer l'interface d'administration complète.
    """
    logger.info("Lancement de l'interface d'administration complète...")
    
    # Ajouter le répertoire courant au PYTHONPATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # Importer les modules nécessaires
        import customtkinter as ctk
        
        # Configuration de l'apparence
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Créer la fenêtre principale
        root = ctk.CTk()
        root.title("Administration Vynal Docs")
        root.geometry("1280x800")
        
        # Créer un modèle simulé pour l'administration
        from admin.admin_model import AdminModel
        admin_model = AdminModel()
        
        # Importer et lancer le panneau d'administration complet
        from admin.admin_ui import AdminUI
        
        # Créer l'interface d'administration complète
        admin_interface = AdminUI(root, admin_model)
        
        # Configurer l'événement de fermeture
        def on_closing():
            """Gérer la fermeture de l'application."""
            if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Démarrer la boucle principale
        logger.info("Interface d'administration démarrée avec succès")
        root.mainloop()
        
        return True
        
    except ImportError as e:
        logger.error(f"Module introuvable: {str(e)}")
        messagebox.showerror("Erreur", f"Module introuvable: {str(e)}\n\nVérifiez que tous les modules nécessaires sont installés.")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'interface: {str(e)}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Erreur", f"Erreur lors du lancement: {str(e)}")
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 
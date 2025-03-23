#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue pour la gestion de la configuration à distance dans l'interface d'administration.
"""

import tkinter as tk
import customtkinter as ctk
import logging
import sys
import os

# Importer la classe RemoteConfigAdmin correctement
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from admin.remote_config.remote_config_admin import RemoteConfigAdmin

logger = logging.getLogger("VynalDocsAutomator.Admin.RemoteConfigView")

class RemoteConfigView:
    """
    Vue pour la gestion de la configuration à distance.
    Intègre le RemoteConfigAdmin dans l'interface d'administration principale.
    """
    
    def __init__(self, parent, admin_model):
        """
        Initialise la vue de gestion de la configuration à distance.
        
        Args:
            parent (tk.Widget): Widget parent
            admin_model: Modèle d'administration
        """
        self.parent = parent
        self.admin_model = admin_model
        
        # Créer le frame principal de la vue
        self.frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="#2a2a2a")
        
        # Créer l'en-tête
        self._create_header()
        
        # Créer le contenu
        self._create_content()
        
        logger.info("Vue de configuration à distance initialisée")
    
    def _create_header(self):
        """Crée l'en-tête de la vue avec titre et description"""
        header_frame = ctk.CTkFrame(self.frame, fg_color="#222222", height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Titre
        ctk.CTkLabel(
            header_frame,
            text="Configuration Distante",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff"
        ).pack(side=tk.LEFT, padx=20, pady=(20, 0))
        
        # Description
        ctk.CTkLabel(
            header_frame,
            text="Gérez la configuration centralisée, les mises à jour et les licences",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        ).pack(side=tk.LEFT, padx=20, pady=(20, 0))
    
    def _create_content(self):
        """Crée le contenu principal de la vue"""
        # Frame pour le contenu
        content_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Récupérer le chemin du fichier de configuration
        config_file_path = None
        if hasattr(self.admin_model, "get_config_path"):
            config_file_path = self.admin_model.get_config_path("app_config.json")
        
        # Créer l'interface d'administration de configuration à distance
        # Utiliser directement le RemoteConfigAdmin complet
        try:
            self.remote_config_admin = RemoteConfigAdmin(content_frame, config_file_path)
            logger.info("RemoteConfigAdmin intégré avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'intégration de RemoteConfigAdmin: {e}")
            # Afficher un message d'erreur dans l'interface
            error_frame = ctk.CTkFrame(content_frame, fg_color="#2a2a2a")
            error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                error_frame,
                text="Erreur lors du chargement de la configuration à distance",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#e74c3c"
            ).pack(pady=(20, 10))
            
            ctk.CTkLabel(
                error_frame,
                text=str(e),
                font=ctk.CTkFont(size=12),
                text_color="#ffffff"
            ).pack(pady=10)
    
    def update(self):
        """Met à jour les données affichées dans la vue"""
        # Actualiser les données si nécessaire
        pass
    
    def show(self):
        """Affiche la vue"""
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Masque la vue"""
        self.frame.pack_forget() 
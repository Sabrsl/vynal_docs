#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application de test pour le système d'authentification
Démontre l'utilisation des composants AuthAdapter et LoginView
"""

import os
import logging
from tkinter import StringVar
import customtkinter as ctk

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VynalDocs.TestLogin")

# Assurez-vous que les répertoires nécessaires existent
os.makedirs("data", exist_ok=True)
os.makedirs("utils", exist_ok=True)
os.makedirs("views", exist_ok=True)

# Import des composants d'authentification
from views.login_view import LoginView
from utils.usage_tracker import UsageTracker

class TestApp:
    """Application de test pour le système d'authentification"""
    
    def __init__(self):
        """Initialise l'application de test"""
        # Configuration de l'interface
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Création de la fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Test du Système d'Authentification (avec UsageTracker)")
        self.root.geometry("650x600")
        
        # Initialiser le tracker d'utilisation
        self.usage_tracker = UsageTracker()
        
        # Variables de l'application
        self.user_info = None
        self.current_view = "login"  # login ou main
        
        # Conteneur principal
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill=ctk.BOTH, expand=True)
        
        # Vues de l'application
        self.views = {}
        
        # Initialiser les vues
        self._init_login_view()
        
        # Afficher la vue de connexion par défaut
        self._show_view("login")
    
    def _init_login_view(self):
        """Initialise la vue de connexion"""
        self.views["login"] = LoginView(
            self.main_container,
            on_auth_success=self._on_authentication_success
        )
    
    def _init_main_view(self):
        """Initialise la vue principale (après connexion)"""
        if "main" not in self.views:
            # Créer la vue principale
            main_frame = ctk.CTkFrame(self.main_container)
            
            # Entête avec informations utilisateur
            header = ctk.CTkFrame(main_frame)
            header.pack(fill=ctk.X, padx=20, pady=20)
            
            # Titre
            title = ctk.CTkLabel(
                header,
                text="Application Vynal Docs Automator",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title.pack(pady=(0, 10))
            
            # Informations utilisateur
            user_info_frame = ctk.CTkFrame(header)
            user_info_frame.pack(fill=ctk.X, pady=10)
            
            email_label = ctk.CTkLabel(
                user_info_frame,
                text=f"Utilisateur: {self.user_info['email']}",
                font=ctk.CTkFont(size=16)
            )
            email_label.pack(pady=5)
            
            # Convertir le timestamp en date lisible
            import datetime
            last_login = self.user_info.get("last_login")
            if last_login:
                last_login_str = datetime.datetime.fromtimestamp(last_login).strftime('%d/%m/%Y %H:%M:%S')
                login_label = ctk.CTkLabel(
                    user_info_frame,
                    text=f"Dernière connexion: {last_login_str}",
                    font=ctk.CTkFont(size=14)
                )
                login_label.pack(pady=5)
            
            # Compteur d'utilisation
            usage_info = self.usage_tracker.increment_usage()
            usage_label = ctk.CTkLabel(
                user_info_frame,
                text=f"Utilisations: {usage_info['count']}",
                font=ctk.CTkFont(size=14)
            )
            usage_label.pack(pady=5)
            
            # Bouton de déconnexion
            logout_button = ctk.CTkButton(
                header,
                text="Déconnexion",
                command=self._logout
            )
            logout_button.pack(pady=10)
            
            # Contenu principal de l'application
            content = ctk.CTkFrame(main_frame)
            content.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # Exemple de contenu
            welcome = ctk.CTkLabel(
                content,
                text="Bienvenue dans l'application!",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            welcome.pack(pady=20)
            
            description = ctk.CTkLabel(
                content,
                text="Vous êtes maintenant connecté et pouvez accéder à toutes les fonctionnalités de l'application.",
                wraplength=400
            )
            description.pack(pady=10)
            
            # Texte variable pour des messages
            self.status_var = StringVar(value="")
            status_label = ctk.CTkLabel(
                content,
                textvariable=self.status_var,
                font=ctk.CTkFont(size=14),
                text_color="#4CAF50"
            )
            status_label.pack(pady=20)
            
            # Exemple de bouton d'action
            action_button = ctk.CTkButton(
                content,
                text="Tester une action",
                command=self._test_action
            )
            action_button.pack(pady=10)
            
            # Enregistrer la vue
            self.views["main"] = main_frame
    
    def _show_view(self, view_name):
        """Affiche une vue spécifique"""
        # Masquer toutes les vues
        for view in self.views.values():
            if hasattr(view, "hide"):
                view.hide()
            else:
                view.pack_forget()
        
        # Afficher la vue demandée
        if view_name in self.views:
            self.current_view = view_name
            if hasattr(self.views[view_name], "show"):
                self.views[view_name].show()
            else:
                self.views[view_name].pack(fill=ctk.BOTH, expand=True)
    
    def _on_authentication_success(self, user_info):
        """Callback appelé après une authentification réussie"""
        logger.info(f"Authentification réussie pour {user_info['email']}")
        
        # Stocker les informations utilisateur
        self.user_info = user_info
        
        # Initialiser la vue principale si nécessaire
        self._init_main_view()
        
        # Afficher la vue principale
        self._show_view("main")
    
    def _logout(self):
        """Déconnecte l'utilisateur actuel"""
        if "login" in self.views and hasattr(self.views["login"], "logout"):
            self.views["login"].logout()
            logger.info("Utilisateur déconnecté")
            
            # Réinitialiser les informations utilisateur
            self.user_info = None
            
            # Afficher la vue de connexion
            self._show_view("login")
    
    def _test_action(self):
        """Exemple d'action dans l'application"""
        # Incrémenter le compteur d'utilisation
        usage_info = self.usage_tracker.increment_usage()
        
        # Afficher un message avec l'information d'utilisation
        self.status_var.set(f"Action exécutée avec succès! {usage_info['message']}")
        
        # Réinitialiser le message après 3 secondes
        self.root.after(3000, lambda: self.status_var.set(""))
    
    def run(self):
        """Démarre l'application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Lancer l'application de test
    app = TestApp()
    app.run() 
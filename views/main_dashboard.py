#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tableau de bord principal de l'application Vynal Docs Automator
"""

import os
import logging
import customtkinter as ctk
from typing import Callable, Dict, Any

# Importer les composants nécessaires
from views.dashboard_auth_button import DashboardAuthButton, UserAccountView
from views.login_view import LoginView
from utils.auth_adapter import AuthAdapter

logger = logging.getLogger("VynalDocsAutomator.MainDashboard")

class MainDashboard:
    """Tableau de bord principal de l'application"""
    
    def __init__(self, root):
        """
        Initialise le tableau de bord principal
        
        Args:
            root: Fenêtre racine de l'application
        """
        self.root = root
        self.auth_adapter = AuthAdapter()
        
        # Configuration de l'interface
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur du tableau de bord"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)
        
        # En-tête avec le bouton d'authentification
        self.header = ctk.CTkFrame(self.main_frame, height=70)
        self.header.pack(fill=ctk.X, padx=20, pady=10)
        self.header.pack_propagate(False)  # Empêcher le redimensionnement
        
        # Logo et titre de l'application
        logo_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        logo_frame.pack(side=ctk.LEFT, fill=ctk.Y)
        
        app_title = ctk.CTkLabel(
            logo_frame,
            text="Vynal Docs Automator",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        app_title.pack(side=ctk.LEFT, padx=20)
        
        # Bouton d'authentification (à droite)
        self.auth_button = DashboardAuthButton(
            self.header,
            open_login_callback=self.open_login_view,
            open_account_callback=self.open_account_view,
            width=180,
            height=40
        )
        self.auth_button.pack(side=ctk.RIGHT, padx=20)
        
        # Zone de contenu principal
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)
        
        # Vue active actuelle
        self.current_view = None
        
        # Afficher le tableau de bord par défaut
        self.show_dashboard()
    
    def show_dashboard(self):
        """Affiche le contenu du tableau de bord"""
        # Nettoyer le contenu actuel
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Conteneur du tableau de bord
        dashboard = ctk.CTkFrame(self.content_frame)
        dashboard.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        dashboard_title = ctk.CTkLabel(
            dashboard,
            text="Tableau de bord",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        dashboard_title.pack(pady=20)
        
        # Message de bienvenue personnalisé selon l'état d'authentification
        if self.auth_adapter.is_authenticated:
            user_info = self.auth_adapter.get_current_user()
            display_name = user_info.get("name", user_info.get("email", "").split("@")[0])
            welcome_text = f"Bienvenue {display_name} ! Vous êtes connecté."
        else:
            welcome_text = "Bienvenue ! Connectez-vous pour accéder à toutes les fonctionnalités."
        
        welcome = ctk.CTkLabel(
            dashboard,
            text=welcome_text,
            font=ctk.CTkFont(size=16)
        )
        welcome.pack(pady=10)
        
        # Vérifier s'il y a des limitations basées sur l'état d'authentification
        if not self.auth_adapter.is_authenticated:
            # Afficher un message concernant les fonctionnalités limitées
            limits_frame = ctk.CTkFrame(dashboard, fg_color=("gray90", "gray20"))
            limits_frame.pack(fill=ctk.X, padx=30, pady=20)
            
            limits_title = ctk.CTkLabel(
                limits_frame,
                text="Fonctionnalités limitées en mode non connecté",
                font=ctk.CTkFont(weight="bold"),
                text_color=("gray20", "gray90")
            )
            limits_title.pack(pady=(10, 5))
            
            limits_desc = ctk.CTkLabel(
                limits_frame,
                text="Connectez-vous pour accéder à toutes les fonctionnalités, "
                     "enregistrer vos préférences et accéder à votre historique.",
                wraplength=400,
                text_color=("gray20", "gray90")
            )
            limits_desc.pack(pady=(0, 10))
        
        # Contenu principal du tableau de bord - Sections modulaires
        self._create_dashboard_sections(dashboard)
        
        # Actualiser l'état du bouton d'authentification
        self.auth_button.refresh()
        
        self.current_view = "dashboard"
    
    def _create_dashboard_sections(self, parent_frame):
        """
        Crée les différentes sections du tableau de bord
        
        Args:
            parent_frame: Frame parent pour les sections
        """
        # Conteneur pour les sections
        sections_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        sections_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Grille 2x2 pour les sections
        sections_frame.columnconfigure(0, weight=1)
        sections_frame.columnconfigure(1, weight=1)
        sections_frame.rowconfigure(0, weight=1)
        sections_frame.rowconfigure(1, weight=1)
        
        # Section 1: Documents récents
        recent_docs = self._create_section(
            sections_frame, 
            "Documents récents", 
            "Accédez rapidement à vos documents récemment modifiés"
        )
        recent_docs.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Section 2: Modèles
        templates = self._create_section(
            sections_frame,
            "Modèles disponibles",
            "Explorez et utilisez les modèles de documents"
        )
        templates.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Section 3: Statistiques
        stats = self._create_section(
            sections_frame,
            "Statistiques",
            "Consultez les statistiques d'utilisation"
        )
        stats.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Section 4: Aide et support
        help_section = self._create_section(
            sections_frame,
            "Aide et support",
            "Ressources d'aide et documentation"
        )
        help_section.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    
    def _create_section(self, parent, title, description):
        """
        Crée une section du tableau de bord
        
        Args:
            parent: Frame parent
            title: Titre de la section
            description: Description courte
            
        Returns:
            Frame de la section
        """
        section = ctk.CTkFrame(parent)
        
        # Titre
        section_title = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Description
        section_desc = ctk.CTkLabel(
            section,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70")
        )
        section_desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Séparateur
        separator = ctk.CTkFrame(section, height=1, fg_color=("gray80", "gray30"))
        separator.pack(fill=ctk.X, padx=15, pady=5)
        
        # Contenu de la section (peut être rempli par des fonctions spécifiques)
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill=ctk.BOTH, expand=True, padx=15, pady=10)
        
        # Pour les besoins de l'exemple, afficher un message "Contenu vide" ou "Connexion requise"
        if not self.auth_adapter.is_authenticated and title not in ["Aide et support"]:
            # Contenu nécessitant une connexion
            login_required = ctk.CTkLabel(
                content,
                text="Connexion requise pour accéder à cette fonctionnalité",
                text_color=("gray40", "gray60"),
                font=ctk.CTkFont(size=12, slant="italic")
            )
            login_required.pack(pady=20)
            
            # Bouton pour se connecter directement
            login_btn = ctk.CTkButton(
                content,
                text="Se connecter",
                command=self.open_login_view,
                width=120,
                height=30
            )
            login_btn.pack(pady=10)
        else:
            # Contenu vide pour l'exemple
            empty_content = ctk.CTkLabel(
                content,
                text="Contenu de la section à implémenter",
                text_color=("gray40", "gray60"),
                font=ctk.CTkFont(size=12, slant="italic")
            )
            empty_content.pack(pady=30)
        
        return section
    
    def open_login_view(self):
        """Ouvre la vue de connexion"""
        # Nettoyer le contenu actuel
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Créer la vue de connexion
        login_view = LoginView(
            self.content_frame,
            on_auth_success=self.on_authentication_success
        )
        
        self.current_view = "login"
    
    def open_account_view(self, user_info):
        """
        Ouvre la vue du compte utilisateur
        
        Args:
            user_info: Informations de l'utilisateur
        """
        # Nettoyer le contenu actuel
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Créer la vue du compte utilisateur
        account_view = UserAccountView(
            self.content_frame,
            user_info,
            on_close=self.handle_account_view_close
        )
        account_view.pack(fill=ctk.BOTH, expand=True)
        
        self.current_view = "account"
    
    def on_authentication_success(self, user_info):
        """
        Callback appelé après une authentification réussie
        
        Args:
            user_info: Informations de l'utilisateur authentifié
        """
        logger.info(f"Authentification réussie pour: {user_info.get('email')}")
        
        # Actualiser le bouton d'authentification
        self.auth_button.refresh()
        
        # Revenir au tableau de bord
        self.show_dashboard()
    
    def handle_account_view_close(self, action="close"):
        """
        Gère la fermeture de la vue du compte utilisateur
        
        Args:
            action: Action effectuée (close ou logout)
        """
        if action == "logout":
            logger.info("Utilisateur déconnecté")
            # Actualiser le bouton d'authentification
            self.auth_button.refresh()
        
        # Revenir au tableau de bord
        self.show_dashboard()


# Exemple d'utilisation directe
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Créer l'application
    root = ctk.CTk()
    root.title("Vynal Docs Automator")
    root.geometry("900x700")
    
    # Configuration du style
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Initialiser le tableau de bord
    app = MainDashboard(root)
    
    # Lancer l'application
    root.mainloop() 
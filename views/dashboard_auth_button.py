#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bouton d'authentification pour le tableau de bord principal de l'application Vynal Docs Automator
"""

import os
import logging
import customtkinter as ctk
from typing import Callable, Dict, Any, Optional, Tuple
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
from CTkMessagebox import CTkMessagebox
import platform
from datetime import datetime
import locale
from views.main_view import get_main_view_instance

from utils.auth_adapter import AuthAdapter

logger = logging.getLogger("VynalDocsAutomator.DashboardAuthButton")

class DashboardAuthButton(ctk.CTkFrame):
    """
    Bouton d'authentification pour le tableau de bord
    
    Ce composant affiche soit:
    - Un bouton "Connexion" si l'utilisateur n'est pas connecté
    - Un bouton "Mon compte" avec le nom de l'utilisateur si l'utilisateur est connecté
    """
    
    def __init__(self, master, command: Callable = None, **kwargs):
        """
        Initialise le bouton d'authentification
        
        Args:
            master: Widget parent
            command: Fonction à appeler lorsque le bouton est cliqué
        """
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        self.auth_adapter = AuthAdapter()
        self.command = command
        
        # Initialiser le bouton
        self.button = None
        self.refresh()
    
    def refresh(self):
        """Rafraîchit l'état du bouton en fonction de l'état d'authentification"""
        if self.button:
            self.button.destroy()
        
        if self.auth_adapter.is_authenticated:
            self._create_user_button()
        else:
            self._create_login_button()
    
    def _create_login_button(self):
        """Crée un bouton de connexion"""
        self.button = ctk.CTkButton(
            self,
            text="Connexion",
            command=self._handle_click,
            width=120,
            height=32,
            corner_radius=8,
        )
        self.button.pack(padx=10, pady=5)
    
    def _create_user_button(self):
        """Crée un bouton utilisateur avec le nom de l'utilisateur"""
        # Récupérer les informations utilisateur
        user_info = self.auth_adapter.get_current_user()
        if not user_info:
            self._create_login_button()
            return
        
        # Créer le bouton avec le nom de l'utilisateur
        display_name = user_info.get("name", user_info.get("email", "").split("@")[0])
        
        self.button = ctk.CTkButton(
            self,
            text=f"👤 {display_name}",
            command=self._handle_click,
            width=120,
            height=32,
            corner_radius=8,
            fg_color="#2980b9",
            hover_color="#3498db"
        )
        self.button.pack(padx=10, pady=5)
    
    def _handle_click(self):
        """Gère le clic sur le bouton"""
        if self.command:
            self.command()
        else:
            # Comportement par défaut
            if self.auth_adapter.is_authenticated:
                self._show_user_account()
            else:
                self._show_login_view()
    
    def _show_login_view(self):
        """Affiche la vue de connexion"""
        try:
            # Tenter d'utiliser directement la méthode show_login de main_view si disponible
            from views.main_view import get_main_view_instance
            main_view = get_main_view_instance()
            
            if main_view and hasattr(main_view, 'show_login'):
                main_view.show_login()
                logger.info("Affichage de la vue login via main_view")
                return
                
            # Si main_view n'est pas disponible, ouvrir une fenêtre modale
            from views.login_view import LoginView
            
            # Créer une fenêtre modale
            login_window = ctk.CTkToplevel(self)
            login_window.title("Connexion - Vynal Docs Automator")
            login_window.geometry("500x600")
            login_window.resizable(False, False)
            login_window.grab_set()  # Rendre la fenêtre modale
            
            # Centrer la fenêtre
            login_window.update_idletasks()
            width = login_window.winfo_width()
            height = login_window.winfo_height()
            x = (login_window.winfo_screenwidth() // 2) - (width // 2)
            y = (login_window.winfo_screenheight() // 2) - (height // 2)
            login_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Callback de succès d'authentification
            def on_auth_success(user_info):
                logger.info(f"Authentification réussie pour {user_info.get('email')}")
                login_window.destroy()
                self.refresh()
            
            # Initialiser la vue de connexion
            login_view = LoginView(login_window, on_auth_success=on_auth_success)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la vue de connexion: {e}")
    
    def _show_user_account(self):
        """
        Affiche la vue du compte utilisateur dans une fenêtre modale indépendante
        """
        try:
            # Obtenir l'utilisateur actuel
            user_data = self.auth_adapter.get_current_user()
            if not user_data:
                logger.error("Impossible d'afficher le compte: utilisateur non connecté")
                CTkMessagebox(
                    title="Erreur",
                    message="Vous devez être connecté pour accéder à votre compte.",
                    icon="cancel"
                )
                return
            
            # Trouver le parent approprié (root window)
            parent = self.winfo_toplevel()
            
            # Créer un Toplevel pour afficher la vue compte
            account_window = ctk.CTkToplevel(parent)
            account_window.title("Mon Compte - Vynal Docs Automator")
            account_window.geometry("800x600")
            account_window.grab_set()  # Rendre modale
            
            # Centrer la fenêtre
            account_window.update_idletasks()
            width = account_window.winfo_width()
            height = account_window.winfo_height()
            x = (account_window.winfo_screenwidth() // 2) - (width // 2)
            y = (account_window.winfo_screenheight() // 2) - (height // 2)
            account_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Callback de retour qui fermera la fenêtre
            def on_back():
                account_window.destroy()
            
            # Callback de déconnexion
            def on_logout():
                account_window.destroy()
                # Rafraîchir le bouton d'authentification
                self.refresh()
            
            # Créer la vue compte
            from views.account_view import AccountView
            account_view = AccountView(account_window, user_data=user_data, on_back=on_back, on_logout=on_logout)
            account_view.show()
            
            logger.info("Vue compte créée et affichée avec succès")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la vue compte: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Afficher un message d'erreur
            CTkMessagebox(
                title="Erreur",
                message=f"Impossible d'afficher votre compte: {str(e)}",
                icon="cancel"
            )

    def _find_main_app_instance(self):
        """
        Recherche l'instance principale de l'application dans la hiérarchie des widgets.
        Retourne l'instance de MainView si trouvée, sinon None.
        """
        # Utiliser la fonction d'accès global pour obtenir l'instance
        main_view = get_main_view_instance()
        if main_view:
            return main_view
            
        # Si la méthode globale échoue, essayons l'approche par recherche hiérarchique
        current_widget = self
        while current_widget:
            if hasattr(current_widget, 'winfo_parent'):
                parent_name = current_widget.winfo_parent()
                if not parent_name:
                    break
                current_widget = current_widget._nametowidget(parent_name)
                if hasattr(current_widget, 'show_account'):  # C'est probablement l'instance de MainView
                    return current_widget
            else:
                break
        return None

    def update_button_text(self, text=None):
        """
        Met à jour le texte du bouton
        
        Args:
            text: Nouveau texte à afficher
        """
        # La méthode reste vide pour l'instant mais pourrait être implémentée plus tard 
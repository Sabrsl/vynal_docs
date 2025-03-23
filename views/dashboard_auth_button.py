#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bouton d'authentification pour le tableau de bord principal de l'application Vynal Docs Automator
"""

import os
import logging
import customtkinter as ctk
from typing import Callable, Dict, Any, Optional, Tuple

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
        """Affiche la vue du compte utilisateur"""
        try:
            # Récupérer les informations utilisateur
            user_info = self.auth_adapter.get_current_user()
            if not user_info:
                logger.error("Impossible de récupérer les informations utilisateur")
                return
            
            # Créer une fenêtre modale
            account_window = ctk.CTkToplevel(self)
            account_window.title("Mon compte - Vynal Docs Automator")
            account_window.geometry("400x500")
            account_window.resizable(False, False)
            account_window.grab_set()  # Rendre la fenêtre modale
            
            # Centrer la fenêtre
            account_window.update_idletasks()
            width = account_window.winfo_width()
            height = account_window.winfo_height()
            x = (account_window.winfo_screenwidth() // 2) - (width // 2)
            y = (account_window.winfo_screenheight() // 2) - (height // 2)
            account_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Callback de fermeture
            def on_close(action=None):
                account_window.destroy()
                if action == "logout":
                    self.refresh()
            
            # Initialiser la vue du compte utilisateur
            account_view = UserAccountView(account_window, user_info=user_info, on_close=on_close)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la vue du compte utilisateur: {e}")


class UserAccountView(ctk.CTkFrame):
    """Vue pour afficher et gérer le compte utilisateur"""
    
    def __init__(self, master, user_info: Dict[str, Any], on_close: Callable = None):
        """
        Initialise la vue du compte utilisateur
        
        Args:
            master: Widget parent
            user_info: Informations de l'utilisateur
            on_close: Fonction à appeler lors de la fermeture
        """
        super().__init__(master)
        self.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        self.user_info = user_info
        self.on_close = on_close
        self.auth_adapter = AuthAdapter()
        
        # Initialiser l'interface
        self._create_ui()
    
    def _create_ui(self):
        """Crée l'interface utilisateur"""
        # Titre
        title_label = ctk.CTkLabel(
            self,
            text="Mon compte",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Informations utilisateur
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Avatar (placeholder)
        avatar_frame = ctk.CTkFrame(info_frame, width=100, height=100, corner_radius=50)
        avatar_frame.pack(pady=(20, 10))
        avatar_frame.pack_propagate(False)
        
        avatar_initials = self.user_info.get("name", "").strip()
        if not avatar_initials:
            email = self.user_info.get("email", "")
            avatar_initials = email.split("@")[0] if email else "?"
        
        if avatar_initials:
            # Prendre jusqu'à deux caractères pour les initiales
            avatar_initials = "".join(word[0].upper() for word in avatar_initials.split()[:2])
        
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=avatar_initials,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#ffffff"
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        
        # Nom d'utilisateur
        name = self.user_info.get("name", "")
        if not name:
            email = self.user_info.get("email", "")
            name = email.split("@")[0] if email else "Utilisateur"
            
        name_label = ctk.CTkLabel(
            info_frame,
            text=name,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        name_label.pack(pady=(5, 0))
        
        # Email
        email_label = ctk.CTkLabel(
            info_frame,
            text=self.user_info.get("email", ""),
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        email_label.pack(pady=(0, 10))
        
        # Rôle
        role = self.user_info.get("role", "Utilisateur")
        role_frame = ctk.CTkFrame(info_frame, fg_color="#3498db", corner_radius=12, height=24)
        role_frame.pack(pady=(0, 20))
        
        role_label = ctk.CTkLabel(
            role_frame,
            text=f" {role.capitalize()} ",
            font=ctk.CTkFont(size=12),
            text_color="#ffffff"
        )
        role_label.pack(padx=10, pady=2)
        
        # Statistiques d'utilisation
        stats_frame = ctk.CTkFrame(info_frame, fg_color=("gray95", "gray15"))
        stats_frame.pack(fill=ctk.X, padx=10, pady=(0, 20))
        
        # Récupérer les statistiques
        usage = self.user_info.get("usage", {})
        docs_created = usage.get("documents_created", 0)
        total_time = usage.get("total_usage_time", 0)
        last_login = usage.get("last_login", "")
        
        # Formater les statistiques
        if isinstance(total_time, (int, float)):
            total_hours = total_time / 3600 if total_time else 0
            total_time_str = f"{total_hours:.1f} heures"
        else:
            total_time_str = "N/A"
            
        if last_login:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_login)
                last_login_str = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                last_login_str = last_login
        else:
            last_login_str = "Aujourd'hui"
        
        # Afficher les statistiques
        self._add_stat(stats_frame, "Documents créés", str(docs_created))
        self._add_stat(stats_frame, "Temps d'utilisation", total_time_str)
        self._add_stat(stats_frame, "Dernière connexion", last_login_str)
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=20)
        
        # Bouton de fermeture
        close_button = ctk.CTkButton(
            buttons_frame,
            text="Fermer",
            command=self._close_view,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        close_button.pack(side=ctk.LEFT, padx=(0, 10))
        
        # Bouton de déconnexion
        logout_button = ctk.CTkButton(
            buttons_frame,
            text="Déconnexion",
            command=self._logout,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        logout_button.pack(side=ctk.RIGHT)
    
    def _add_stat(self, parent, label, value):
        """Ajoute une statistique à l'interface"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill=ctk.X, padx=10, pady=5)
        
        label = ctk.CTkLabel(
            frame,
            text=label,
            anchor="w"
        )
        label.pack(side=ctk.LEFT)
        
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            anchor="e",
            font=ctk.CTkFont(weight="bold")
        )
        value_label.pack(side=ctk.RIGHT)
    
    def _logout(self):
        """Déconnecte l'utilisateur"""
        if self.auth_adapter.logout():
            # Fermer la vue et informer le parent
            if self.on_close:
                self.on_close(action="logout")
    
    def _close_view(self):
        """Ferme la vue"""
        if self.on_close:
            self.on_close(action="close") 
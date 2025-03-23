#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue de connexion pour l'application Vynal Docs Automator
Gère l'interface utilisateur pour la connexion, l'inscription et la récupération de mot de passe
"""

import os
import logging
import customtkinter as ctk
from typing import Callable, Dict, Any, Optional
import re
from datetime import datetime

from utils.auth_adapter import AuthAdapter

logger = logging.getLogger("VynalDocsAutomator.LoginView")

class LoginView(ctk.CTkFrame):
    """
    Vue de connexion, inscription et récupération de mot de passe
    """
    
    # Constantes
    MIN_PASSWORD_LENGTH = 6
    
    def __init__(self, master, on_auth_success: Callable[[Dict[str, Any]], None] = None):
        """
        Initialise la vue de connexion
        
        Args:
            master: Widget parent
            on_auth_success: Fonction appelée après une authentification réussie
        """
        super().__init__(master)
        self.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Callback de succès d'authentification
        self.on_auth_success = on_auth_success
        
        # Adaptateur d'authentification
        self.auth_adapter = AuthAdapter()
        
        # Variables de formulaire
        self.email_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.name_var = ctk.StringVar()
        self.confirm_password_var = ctk.StringVar()
        
        # Variables d'état
        self.current_view = "login"  # login, register, reset_password
        self.email_valid = False
        self.password_valid = False
        self.confirm_password_valid = False
        
        # Interface utilisateur
        self._create_ui()
        
        # Vérifier s'il y a une session active
        self._check_active_session()
    
    def _create_ui(self):
        """Crée l'interface utilisateur"""
        # Conteneur principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Logo ou image d'en-tête
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill=ctk.X, pady=(0, 20))
        
        # Titre de l'application
        self.app_title = ctk.CTkLabel(
            self.header_frame,
            text="Vynal Docs Automator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.app_title.pack(pady=10)
        
        # Sous-titre
        self.app_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Authentification",
            font=ctk.CTkFont(size=16)
        )
        self.app_subtitle.pack()
        
        # Zone de contenu
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Barre d'onglets
        self.tabs_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tabs_frame.pack(fill=ctk.X, pady=(0, 20))
        
        # Initialiser l'interface de connexion par défaut
        self._show_login_view()
    
    def _clear_form(self):
        """Efface les champs du formulaire"""
        for var in [self.email_var, self.password_var, self.name_var, self.confirm_password_var]:
            var.set("")
        
        # Réinitialiser les variables d'état
        self.email_valid = False
        self.password_valid = False
        self.confirm_password_valid = False
    
    def _show_error(self, message):
        """Affiche un message d'erreur"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(
                text=message,
                text_color="red"
            )
            # Rafraîchir l'interface pour afficher le message immédiatement
            self.update()
    
    def _show_success(self, message):
        """Affiche un message de succès"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(
                text=message,
                text_color="green"
            )
            # Rafraîchir l'interface pour afficher le message immédiatement
            self.update()
    
    def _add_field(self, frame, label, variable, placeholder="", show="", default="", **kwargs):
        """
        Ajoute un champ de formulaire
        
        Args:
            frame: Frame parent
            label: Libellé du champ
            variable: Variable pour stocker la valeur
            placeholder: Texte d'aide
            show: Caractère pour les mots de passe
            default: Valeur par défaut
            
        Returns:
            Tuple[CTkLabel, CTkEntry]: Label et champ de saisie
        """
        # Conteneur pour le champ
        field_frame = ctk.CTkFrame(frame, fg_color="transparent")
        field_frame.pack(fill=ctk.X, pady=(0, 10))
        
        # Libellé
        label_widget = ctk.CTkLabel(
            field_frame, 
            text=label,
            anchor="w"
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        # Champ de saisie
        if show:
            entry = ctk.CTkEntry(
                field_frame,
                textvariable=variable,
                placeholder_text=placeholder,
                show=show,
                **kwargs
            )
        else:
            entry = ctk.CTkEntry(
                field_frame,
                textvariable=variable,
                placeholder_text=placeholder,
                **kwargs
            )
        
        entry.pack(fill=ctk.X)
        
        # Définir la valeur par défaut
        variable.set(default)
        
        return label_widget, entry
    
    def _show_login_view(self):
        """Affiche la vue de connexion"""
        # Nettoyer l'interface précédente
        self._clear_form()
        for widget in self.content_frame.winfo_children():
            if widget != self.tabs_frame:
                widget.destroy()
        
        # Onglets
        for widget in self.tabs_frame.winfo_children():
            widget.destroy()
            
        # Bouton de connexion
        login_btn = ctk.CTkButton(
            self.tabs_frame,
            text="Connexion",
            fg_color="#2196F3" if self.current_view == "login" else "transparent",
            command=lambda: self._show_login_view()
        )
        login_btn.pack(side=ctk.LEFT, padx=(0, 10))
        
        # Bouton d'inscription
        register_btn = ctk.CTkButton(
            self.tabs_frame,
            text="Inscription",
            fg_color="transparent",
            command=lambda: self._show_register_view()
        )
        register_btn.pack(side=ctk.LEFT)
        
        # Formulaire de connexion
        form_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        form_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Champs du formulaire
        self._add_field(form_frame, "Email", self.email_var, "exemple@email.com")
        self._add_field(form_frame, "Mot de passe", self.password_var, "Votre mot de passe", show="*")
        
        # Message d'état
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red"
        )
        self.status_label.pack(pady=10)
        
        # Bouton de connexion
        login_submit_btn = ctk.CTkButton(
            form_frame,
            text="Se connecter",
            command=self._handle_login
        )
        login_submit_btn.pack(pady=10)
        
        # Lien pour la réinitialisation du mot de passe
        reset_password_link = ctk.CTkButton(
            form_frame,
            text="Mot de passe oublié ?",
            fg_color="transparent",
            hover=False,
            command=lambda: self._show_reset_password_view()
        )
        reset_password_link.pack(pady=5)
        
        # Mettre à jour l'état courant
        self.current_view = "login"
    
    def _show_register_view(self):
        """Affiche la vue d'inscription"""
        # Nettoyer l'interface précédente
        self._clear_form()
        for widget in self.content_frame.winfo_children():
            if widget != self.tabs_frame:
                widget.destroy()
        
        # Onglets
        for widget in self.tabs_frame.winfo_children():
            widget.destroy()
            
        # Bouton de connexion
        login_btn = ctk.CTkButton(
            self.tabs_frame,
            text="Connexion",
            fg_color="transparent",
            command=lambda: self._show_login_view()
        )
        login_btn.pack(side=ctk.LEFT, padx=(0, 10))
        
        # Bouton d'inscription
        register_btn = ctk.CTkButton(
            self.tabs_frame,
            text="Inscription",
            fg_color="#2196F3" if self.current_view == "register" else "transparent",
            command=lambda: self._show_register_view()
        )
        register_btn.pack(side=ctk.LEFT)
        
        # Formulaire d'inscription
        form_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        form_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Champs du formulaire
        self._add_field(form_frame, "Nom", self.name_var, "Votre nom")
        self._add_field(form_frame, "Email", self.email_var, "exemple@email.com")
        self._add_field(form_frame, "Mot de passe", self.password_var, 
                      f"Minimum {self.MIN_PASSWORD_LENGTH} caractères", show="*")
        self._add_field(form_frame, "Confirmer le mot de passe", self.confirm_password_var, 
                      "Confirmez votre mot de passe", show="*")
        
        # Message d'état
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red"
        )
        self.status_label.pack(pady=10)
        
        # Bouton d'inscription
        register_submit_btn = ctk.CTkButton(
            form_frame,
            text="S'inscrire",
            command=self._handle_register
        )
        register_submit_btn.pack(pady=10)
        
        # Mettre à jour l'état courant
        self.current_view = "register"
    
    def _show_reset_password_view(self):
        """Affiche la vue de réinitialisation de mot de passe"""
        # Nettoyer l'interface précédente
        self._clear_form()
        for widget in self.content_frame.winfo_children():
            if widget != self.tabs_frame:
                widget.destroy()
        
        # Onglets
        for widget in self.tabs_frame.winfo_children():
            widget.destroy()
            
        # Bouton de connexion
        login_btn = ctk.CTkButton(
            self.tabs_frame,
            text="Connexion",
            fg_color="transparent",
            command=lambda: self._show_login_view()
        )
        login_btn.pack(side=ctk.LEFT, padx=(0, 10))
        
        # Bouton d'inscription
        register_btn = ctk.CTkButton(
            self.tabs_frame,
            text="Inscription",
            fg_color="transparent",
            command=lambda: self._show_register_view()
        )
        register_btn.pack(side=ctk.LEFT)
        
        # Formulaire de réinitialisation
        form_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        form_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Titre
        reset_title = ctk.CTkLabel(
            form_frame,
            text="Réinitialisation du mot de passe",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        reset_title.pack(pady=(0, 20))
        
        # Instructions
        instructions = ctk.CTkLabel(
            form_frame,
            text="Veuillez entrer votre adresse email pour réinitialiser votre mot de passe.",
            wraplength=400
        )
        instructions.pack(pady=(0, 20))
        
        # Champ email
        self._add_field(form_frame, "Email", self.email_var, "exemple@email.com")
        
        # Message d'état
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red"
        )
        self.status_label.pack(pady=10)
        
        # Bouton de vérification
        verify_btn = ctk.CTkButton(
            form_frame,
            text="Vérifier l'email",
            command=self._verify_email_for_reset
        )
        verify_btn.pack(pady=10)
        
        # Lien pour revenir à la connexion
        back_link = ctk.CTkButton(
            form_frame,
            text="Retour à la connexion",
            fg_color="transparent",
            hover=False,
            command=lambda: self._show_login_view()
        )
        back_link.pack(pady=5)
        
        # Mettre à jour l'état courant
        self.current_view = "reset_password"
    
    def _handle_login(self):
        """Gère la connexion"""
        # Récupérer les valeurs
        email = self.email_var.get()
        password = self.password_var.get()
        
        # Vérifier que les champs sont remplis
        if not email or not password:
            self._show_error("Veuillez remplir tous les champs")
            return
        
        # Authentifier l'utilisateur
        try:
            user_info = self.auth_adapter.authenticate(email, password)
            
            if user_info:
                self._show_success("Connexion réussie !")
                
                # Appeler le callback de succès
                if self.on_auth_success:
                    self.on_auth_success(user_info)
            else:
                self._show_error("Email ou mot de passe incorrect")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            self._show_error(f"Erreur: {str(e)}")
    
    def _handle_register(self):
        """Gère l'inscription"""
        # Récupérer les valeurs
        name = self.name_var.get()
        email = self.email_var.get()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Vérifier que les champs sont remplis
        if not email or not password or not confirm_password:
            self._show_error("Veuillez remplir tous les champs obligatoires")
            return
        
        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            self._show_error("Les mots de passe ne correspondent pas")
            return
        
        # Vérifier la longueur du mot de passe
        if len(password) < self.MIN_PASSWORD_LENGTH:
            self._show_error(f"Le mot de passe doit contenir au moins {self.MIN_PASSWORD_LENGTH} caractères")
            return
        
        # Vérifier le format de l'email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self._show_error("Format d'email invalide")
            return
        
        # Inscrire l'utilisateur
        try:
            user_info = self.auth_adapter.register(email, password, name)
            
            if user_info:
                self._show_success("Inscription réussie !")
                
                # Appeler le callback de succès
                if self.on_auth_success:
                    self.on_auth_success(user_info)
            else:
                self._show_error("Erreur lors de l'inscription")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {e}")
            self._show_error(f"Erreur: {str(e)}")
    
    def _verify_email_for_reset(self):
        """Vérifie l'email pour la réinitialisation du mot de passe"""
        # Récupérer l'email
        email = self.email_var.get()
        
        # Vérifier que l'email est renseigné
        if not email:
            self._show_error("Veuillez entrer votre adresse email")
            return
        
        # Vérifier que l'utilisateur existe
        if self.auth_adapter.check_password_reset(email):
            # Afficher le formulaire de réinitialisation
            for widget in self.content_frame.winfo_children():
                if widget != self.tabs_frame:
                    widget.destroy()
                    
            self._add_password_reset_fields(email)
        else:
            self._show_error("Aucun compte associé à cet email")
    
    def _add_password_reset_fields(self, email):
        """Ajoute les champs pour la réinitialisation du mot de passe"""
        # Formulaire de réinitialisation
        form_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        form_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Titre
        reset_title = ctk.CTkLabel(
            form_frame,
            text="Créer un nouveau mot de passe",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        reset_title.pack(pady=(0, 20))
        
        # Instructions
        instructions = ctk.CTkLabel(
            form_frame,
            text=f"Définissez un nouveau mot de passe pour le compte {email}",
            wraplength=400
        )
        instructions.pack(pady=(0, 20))
        
        # Champs du formulaire
        self._add_field(form_frame, "Nouveau mot de passe", self.password_var, 
                       f"Minimum {self.MIN_PASSWORD_LENGTH} caractères", show="*")
        self._add_field(form_frame, "Confirmer le mot de passe", self.confirm_password_var, 
                       "Confirmez votre mot de passe", show="*")
        
        # Message d'état
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red"
        )
        self.status_label.pack(pady=10)
        
        # Bouton de réinitialisation
        reset_btn = ctk.CTkButton(
            form_frame,
            text="Réinitialiser le mot de passe",
            command=self._handle_reset_password
        )
        reset_btn.pack(pady=10)
        
        # Stocker l'email pour la réinitialisation
        self.reset_email = email
    
    def _handle_reset_password(self):
        """Gère la réinitialisation du mot de passe"""
        # Récupérer les valeurs
        new_password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Vérifier que les champs sont remplis
        if not new_password or not confirm_password:
            self._show_error("Veuillez remplir tous les champs")
            return
        
        # Vérifier que les mots de passe correspondent
        if new_password != confirm_password:
            self._show_error("Les mots de passe ne correspondent pas")
            return
        
        # Vérifier la longueur du mot de passe
        if len(new_password) < self.MIN_PASSWORD_LENGTH:
            self._show_error(f"Le mot de passe doit contenir au moins {self.MIN_PASSWORD_LENGTH} caractères")
            return
        
        # Réinitialiser le mot de passe
        try:
            result = self.auth_adapter.reset_password(self.reset_email, new_password)
            
            if result:
                self._show_success("Mot de passe réinitialisé avec succès !")
                
                # Rediriger vers la connexion après quelques secondes
                self.after(2000, self._show_login_view)
            else:
                self._show_error("Erreur lors de la réinitialisation du mot de passe")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation du mot de passe: {e}")
            self._show_error(f"Erreur: {str(e)}")
    
    def logout(self):
        """Déconnecte l'utilisateur actuel"""
        if self.auth_adapter.is_authenticated:
            result = self.auth_adapter.logout()
            if result and self.on_auth_success:
                # Retourner à la vue de connexion
                self._show_login_view()
            return result
        return False
    
    def _check_active_session(self):
        """Vérifie s'il y a une session active"""
        if self.auth_adapter.is_authenticated:
            user_info = self.auth_adapter.get_current_user()
            if user_info:
                logger.info(f"Session active trouvée: {user_info.get('email')}")
                
                # Appeler le callback de succès
                if self.on_auth_success:
                    self.on_auth_success(user_info)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue d'authentification moderne pour l'application Vynal Docs Automator
"""

import os
import json
import logging
import hashlib
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from utils.usage_tracker import UsageTracker
from datetime import datetime
import tkinter as tk
from PIL import Image
import time

logger = logging.getLogger("VynalDocsAutomator.AuthView")

class AuthView:
    """Vue moderne pour l'authentification et la gestion de compte"""
    
    # Constantes pour la validation
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_TIMEOUT = 300  # 5 minutes
    
    def __init__(self, parent, usage_tracker=None):
        """
        Initialise la vue d'authentification
        
        Args:
            parent: Widget parent
            usage_tracker: Instance du gestionnaire d'utilisation
        """
        self.parent = parent
        self.usage_tracker = usage_tracker or UsageTracker()
        
        # État de connexion et sécurité
        self.current_user = None
        self.on_auth_change_callback = None
        self.login_attempts = {}  # {email: [timestamp, count]}
        
        # Variables de validation
        self.email_valid = False
        self.password_valid = False
        self.confirm_password_valid = False
        
        # Variables
        self.current_tab = ctk.StringVar(value="login")
        self.email_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.confirm_password_var = ctk.StringVar()
        self.register_name_var = ctk.StringVar()
        
        # Stockage des références aux widgets
        self.main_frame = None
        self.window = None
        self.login_frame = None
        self.register_frame = None
        self.account_frame = None
        self.login_tab = None
        self.register_tab = None
        self.account_tab = None
        
        # Tracer les changements des variables
        self.email_var.trace_add("write", self._validate_email)
        self.password_var.trace_add("write", self._validate_password)
        self.confirm_password_var.trace_add("write", self._validate_confirm_password)
        
        # Référence aux onglets
        self.tabs = None
        
        # Ne pas créer les widgets immédiatement, attendre l'appel à show()
    
    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        try:
            # Frame principal avec padding
            self.main_frame = ctk.CTkFrame(self.window)
            self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # En-tête avec logo/icône
            self._create_header()
            
            # Onglets de navigation
            self._create_tabs()
            
            # Frame de contenu
            self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
            
            # Créer les différentes vues
            self._create_login_view()
            self._create_register_view()
            self._create_account_view()
            
            # Mettre à jour l'affichage selon l'onglet courant
            tab_name = self.current_tab.get()
            self._update_tab_content()
            
            logger.info("Widgets de l'interface d'authentification créés")
        except Exception as e:
            logger.error(f"Erreur lors de la création des widgets de l'interface: {e}")
            # Tenter une approche plus simple en cas d'échec
            try:
                # Frame principal
                self.main_frame = ctk.CTkFrame(self.window)
                self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
                
                # Titre simple
                ctk.CTkLabel(
                    self.main_frame,
                    text="Connexion à l'application",
                    font=ctk.CTkFont(size=16, weight="bold")
                ).pack(pady=10)
                
                # Créer juste la vue de connexion
                self.login_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
                self.login_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
                
                # Champs de connexion
                ctk.CTkLabel(self.login_frame, text="Email:").pack(anchor="w", pady=(10, 0))
                self.email_var = ctk.StringVar()
                ctk.CTkEntry(
                    self.login_frame,
                    textvariable=self.email_var,
                    width=250
                ).pack(pady=(0, 10))
                
                ctk.CTkLabel(self.login_frame, text="Mot de passe:").pack(anchor="w", pady=(10, 0))
                self.password_var = ctk.StringVar()
                ctk.CTkEntry(
                    self.login_frame,
                    textvariable=self.password_var,
                    show="•",
                    width=250
                ).pack(pady=(0, 10))
                
                # Bouton de connexion
                ctk.CTkButton(
                    self.login_frame,
                    text="Se connecter",
                    command=self._handle_login,
                    width=250
                ).pack(pady=20)
                
                # Message d'erreur
                self.login_status_label = ctk.CTkLabel(
                    self.login_frame,
                    text="",
                    text_color="red"
                )
                self.login_status_label.pack(pady=5)
                
                logger.info("Interface d'authentification simplifiée créée")
            except Exception as e2:
                logger.critical(f"Échec critique lors de la création d'une interface de secours: {e2}")
    
    def _create_header(self):
        """Crée l'en-tête avec logo"""
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill=ctk.X, pady=(0, 20))
        
        # Logo/Icône
        logo_label = ctk.CTkLabel(
            header,
            text="👤",  # Emoji comme icône
            font=ctk.CTkFont(size=48)
        )
        logo_label.pack(pady=(0, 10))
        
        # Titre
        title_label = ctk.CTkLabel(
            header,
            text="Bienvenue",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack()
    
    def _create_tabs(self):
        """Crée les onglets de navigation"""
        try:
            # Créer le frame des onglets
            self.tabs = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.tabs.pack(fill=ctk.X, padx=10, pady=(10, 0))
            
            # Styles des onglets
            tab_height = 30
            tab_width = 120
            tab_corner_radius = 8
            
            # Créer les onglets
            # Onglet Connexion
            self.login_tab = ctk.CTkButton(
                self.tabs,
                text="Connexion",
                height=tab_height,
                width=tab_width,
                corner_radius=tab_corner_radius,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda: self._show_tab("login")
            )
            self.login_tab.pack(side=ctk.LEFT, padx=5, pady=0)
            
            # Onglet Inscription
            self.register_tab = ctk.CTkButton(
                self.tabs,
                text="Inscription",
                height=tab_height,
                width=tab_width,
                corner_radius=tab_corner_radius,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda: self._show_tab("register")
            )
            self.register_tab.pack(side=ctk.LEFT, padx=5, pady=0)
            
            # Onglet Compte (visible uniquement si connecté)
            self.account_tab = ctk.CTkButton(
                self.tabs,
                text="Compte",
                height=tab_height,
                width=tab_width,
                corner_radius=tab_corner_radius,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda: self._show_tab("account")
            )
            self.account_tab.pack(side=ctk.LEFT, padx=5, pady=0)
            
            # Séparateur horizontal sous les onglets
            ctk.CTkFrame(self.main_frame, height=1, fg_color="gray").pack(fill=ctk.X, padx=10, pady=(0, 0))
            
            # Mettre en évidence l'onglet actuel
            tab_name = self.current_tab.get()
            if tab_name == "login":
                self.login_tab.configure(fg_color=("gray85", "gray25"))
            elif tab_name == "register":
                self.register_tab.configure(fg_color=("gray85", "gray25"))
            elif tab_name == "account":
                self.account_tab.configure(fg_color=("gray85", "gray25"))
                
            logger.debug("Onglets créés avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la création des onglets: {e}")
            # Créer une version simplifiée des onglets avec une gestion d'erreur plus robuste
            try:
                # Si le frame des onglets existe déjà, le nettoyer
                if hasattr(self, 'tabs') and self.tabs:
                    for widget in self.tabs.winfo_children():
                        widget.destroy()
                else:
                    # Sinon créer un nouveau frame
                    self.tabs = ctk.CTkFrame(self.main_frame, fg_color="transparent")
                    self.tabs.pack(fill=ctk.X, padx=10, pady=(10, 0))
                
                # Créer les onglets basiques
                tabs_info = [
                    {"name": "login", "text": "Connexion"},
                    {"name": "register", "text": "Inscription"},
                    {"name": "account", "text": "Compte"}
                ]
                
                # Créer chaque onglet individuellement
                for tab in tabs_info:
                    btn = ctk.CTkButton(
                        self.tabs,
                        text=tab["text"],
                        height=30,
                        width=120,
                        corner_radius=8,
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray85", "gray25"),
                        command=lambda t=tab["name"]: self._show_tab(t)
                    )
                    btn.pack(side=ctk.LEFT, padx=5, pady=0)
                    
                    # Garder une référence aux onglets
                    setattr(self, f"{tab['name']}_tab", btn)
                
                # Séparateur
                ctk.CTkFrame(self.main_frame, height=1, fg_color="gray").pack(fill=ctk.X, padx=10, pady=(0, 0))
                
                logger.debug("Version simplifiée des onglets créée après erreur")
            except Exception as e2:
                logger.error(f"Échec critique lors de la création des onglets alternatifs: {e2}")
                # Dernière tentative ultra simplifiée
                self.tabs = ctk.CTkFrame(self.main_frame, fg_color="transparent")
                self.tabs.pack(fill=ctk.X, padx=10, pady=(10, 0))
                
                # Juste un titre pour indiquer l'onglet actuel
                tab_name = self.current_tab.get().capitalize()
                ctk.CTkLabel(
                    self.tabs,
                    text=f"Vue: {tab_name}",
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(pady=5)
    
    def _create_login_view(self):
        """Crée la vue de connexion"""
        self.login_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Titre
        ctk.CTkLabel(
            self.login_frame,
            text="Connexion à votre compte",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        # Cadre du formulaire
        form_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        form_frame.pack(fill=ctk.X, padx=20)
        
        # Champ email
        email_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        email_frame.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(
            email_frame,
            text="Adresse email",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.login_email = ctk.CTkEntry(
            email_frame,
            textvariable=self.email_var,
            placeholder_text="Votre adresse email",
            height=40,
            border_width=1
        )
        self.login_email.pack(fill=ctk.X)
        
        # Message d'erreur email
        self.login_email_error = ctk.CTkLabel(
            email_frame,
            text="",
            text_color="red",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.login_email_error.pack(fill=ctk.X, padx=5)
        
        # Champ mot de passe
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(fill=ctk.X, pady=(0, 10))
        
        # Libellé et lien "Mot de passe oublié"
        pwd_header = ctk.CTkFrame(password_frame, fg_color="transparent")
        pwd_header.pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        ctk.CTkLabel(
            pwd_header,
            text="Mot de passe",
            anchor="w"
        ).pack(side=ctk.LEFT)
        
        # Champ de saisie du mot de passe
        self.login_password = ctk.CTkEntry(
            password_frame,
            textvariable=self.password_var,
            placeholder_text="Votre mot de passe",
            show="•",
            height=40,
            border_width=1
        )
        self.login_password.pack(fill=ctk.X)
        
        # Message d'erreur mot de passe
        self.login_password_error = ctk.CTkLabel(
            password_frame,
            text="",
            text_color="red",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.login_password_error.pack(fill=ctk.X, padx=5)
        
        # Option "Se souvenir de moi"
        self.remember_var = ctk.BooleanVar(value=False)
        remember_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        remember_frame.pack(fill=ctk.X, pady=(0, 20))
        
        remember_checkbox = ctk.CTkCheckBox(
            remember_frame,
            text="Se souvenir de moi",
            variable=self.remember_var,
            border_width=2,
            corner_radius=6,
            hover_color=("#3498db", "#2980b9"),
            fg_color=("#3498db", "#2980b9")
        )
        remember_checkbox.pack(side=ctk.LEFT, padx=5)
        
        # Message de statut pour la connexion
        self.login_status_label = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="red",
            anchor="center",
            font=ctk.CTkFont(size=12)
        )
        self.login_status_label.pack(fill=ctk.X, padx=5, pady=(0, 10))
        
        # Bouton de connexion
        self.login_button = ctk.CTkButton(
            form_frame,
            text="Se connecter",
            command=self._handle_login,
            height=40,
            corner_radius=8,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d")
        )
        self.login_button.pack(fill=ctk.X, pady=(0, 20))
        
        # Pas de séparateur pour simplifier
        # self._create_separator(form_frame)
        
        # Lien vers l'inscription
        register_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        register_frame.pack(fill=ctk.X, pady=(10, 0))
        
        ctk.CTkLabel(
            register_frame,
            text="Vous n'avez pas de compte ?",
            anchor="center"
        ).pack(pady=(0, 5))
        
        register_link = ctk.CTkButton(
            register_frame,
            text="Créer un compte",
            font=ctk.CTkFont(size=13, underline=True),
            fg_color="transparent",
            hover_color="transparent",
            text_color=("#3498db", "#2980b9"),
            width=30,
            height=20,
            command=lambda: self._show_tab("register")
        )
        register_link.pack()
    
    def _create_separator(self, parent):
        """
        Crée un séparateur avec le texte 'ou'
        
        Args:
            parent: Widget parent
        """
        separator_frame = ctk.CTkFrame(parent, fg_color="transparent")
        separator_frame.pack(fill=ctk.X, pady=10)
        
        # Ligne gauche
        left_line = ctk.CTkFrame(separator_frame, height=1, fg_color="gray")
        left_line.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 10))
        
        # Texte "ou"
        ctk.CTkLabel(
            separator_frame,
            text="ou",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        ).pack(side=ctk.LEFT)
        
        # Ligne droite
        right_line = ctk.CTkFrame(separator_frame, height=1, fg_color="gray")
        right_line.pack(side=ctk.RIGHT, fill=ctk.X, expand=True, padx=(10, 0))
    
    def _create_register_view(self):
        """Crée la vue d'inscription"""
        self.register_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Titre
        ctk.CTkLabel(
            self.register_frame,
            text="Créer un compte",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # Cadre du formulaire
        form_frame = ctk.CTkFrame(self.register_frame, fg_color="transparent")
        form_frame.pack(fill=ctk.X, padx=20)
        
        # Champ nom
        name_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        name_frame.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(
            name_frame,
            text="Nom complet",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.name_var = ctk.StringVar()
        self.register_name = ctk.CTkEntry(
            name_frame,
            textvariable=self.name_var,
            placeholder_text="Votre nom complet",
            height=40,
            border_width=1
        )
        self.register_name.pack(fill=ctk.X)
        
        # Message d'erreur nom
        self.register_name_error = ctk.CTkLabel(
            name_frame,
            text="",
            text_color="red",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.register_name_error.pack(fill=ctk.X, padx=5)
        
        # Champ email
        email_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        email_frame.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(
            email_frame,
            text="Adresse email",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.register_email = ctk.CTkEntry(
            email_frame,
            textvariable=self.email_var,
            placeholder_text="Votre adresse email",
            height=40,
            border_width=1
        )
        self.register_email.pack(fill=ctk.X)
        
        # Message d'erreur email
        self.register_email_error = ctk.CTkLabel(
            email_frame,
            text="",
            text_color="red",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.register_email_error.pack(fill=ctk.X, padx=5)
        
        # Champ mot de passe
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(
            password_frame,
            text="Mot de passe",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.register_password = ctk.CTkEntry(
            password_frame,
            textvariable=self.password_var,
            placeholder_text="Créez un mot de passe sécurisé",
            show="•",
            height=40,
            border_width=1
        )
        self.register_password.pack(fill=ctk.X)
        
        # Message d'erreur mot de passe
        self.register_password_error = ctk.CTkLabel(
            password_frame,
            text="",
            text_color="red",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.register_password_error.pack(fill=ctk.X, padx=5)
        
        # Indicateur de force du mot de passe
        self.password_strength_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        self.password_strength_frame.pack(fill=ctk.X, padx=5, pady=(5, 0))
        
        self.password_strength_indicator = ctk.CTkProgressBar(
            self.password_strength_frame,
            width=200,
            height=8,
            corner_radius=2,
            mode="determinate"
        )
        self.password_strength_indicator.pack(side=ctk.LEFT, fill=ctk.X, expand=True)
        self.password_strength_indicator.set(0)
        
        self.password_strength_label = ctk.CTkLabel(
            self.password_strength_frame,
            text="Faible",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.password_strength_label.pack(side=ctk.RIGHT, padx=(10, 0))
        
        # Champ confirmation de mot de passe
        confirm_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        confirm_frame.pack(fill=ctk.X, pady=(0, 15))
        
        ctk.CTkLabel(
            confirm_frame,
            text="Confirmer le mot de passe",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.register_confirm = ctk.CTkEntry(
            confirm_frame,
            textvariable=self.confirm_password_var,
            placeholder_text="Confirmez votre mot de passe",
            show="•",
            height=40,
            border_width=1
        )
        self.register_confirm.pack(fill=ctk.X)
        
        # Message d'erreur confirmation
        self.register_confirm_error = ctk.CTkLabel(
            confirm_frame,
            text="",
            text_color="red",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.register_confirm_error.pack(fill=ctk.X, padx=5)
        
        # Conditions d'utilisation
        terms_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        terms_frame.pack(fill=ctk.X, pady=(0, 20))
        
        self.terms_var = ctk.BooleanVar(value=False)
        terms_checkbox = ctk.CTkCheckBox(
            terms_frame,
            text="J'accepte les ",
            variable=self.terms_var,
            border_width=2,
            corner_radius=6,
            hover_color=("#3498db", "#2980b9"),
            fg_color=("#3498db", "#2980b9")
        )
        terms_checkbox.pack(side=ctk.LEFT, padx=5)
        
        terms_link = ctk.CTkButton(
            terms_frame,
            text="conditions d'utilisation",
            font=ctk.CTkFont(size=13, underline=True),
            fg_color="transparent",
            hover_color="transparent",
            text_color=("#3498db", "#2980b9"),
            width=30,
            height=20,
            command=self._show_terms
        )
        terms_link.pack(side=ctk.LEFT, padx=0)
        
        # Bouton d'inscription
        self.register_button = ctk.CTkButton(
            form_frame,
            text="Créer mon compte",
            command=self._handle_register,
            height=40,
            corner_radius=8,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d")
        )
        self.register_button.pack(fill=ctk.X, pady=(0, 20))
        
        # Séparateur ou
        self._create_separator(form_frame)
        
        # Bouton d'authentification Google
        google_button = ctk.CTkButton(
            form_frame,
            text="S'inscrire avec Google",
            image=self._get_google_icon(),
            compound="left",
            command=self._handle_google_auth,
            height=40,
            corner_radius=8,
            fg_color=("#ffffff", "#333333"),
            text_color=("#333333", "#ffffff"),
            hover_color=("#eeeeee", "#444444"),
            border_width=1,
            border_color=("#dddddd", "#555555")
        )
        google_button.pack(fill=ctk.X, pady=(0, 10))
        
        # Déjà un compte ?
        login_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        login_frame.pack(fill=ctk.X, pady=(10, 0))
        
        ctk.CTkLabel(
            login_frame,
            text="Déjà un compte ?",
            font=ctk.CTkFont(size=13)
        ).pack(side=ctk.LEFT, padx=(5, 5))
        
        login_link = ctk.CTkButton(
            login_frame,
            text="Se connecter",
            font=ctk.CTkFont(size=13, underline=True),
            fg_color="transparent",
            hover_color="transparent",
            text_color=("#3498db", "#2980b9"),
            width=30,
            height=20,
            command=lambda: self._show_tab("login")
        )
        login_link.pack(side=ctk.LEFT)
    
    def _create_account_view(self):
        """Crée la vue de compte utilisateur"""
        self.account_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Titre et bienvenue
        welcome_frame = ctk.CTkFrame(self.account_frame, fg_color="transparent")
        welcome_frame.pack(fill=ctk.X, pady=(0, 20))
        
        # Avatar utilisateur
        self.avatar_label = ctk.CTkLabel(
            welcome_frame,
            text="👤",
            font=ctk.CTkFont(size=48)
        )
        self.avatar_label.pack(pady=(0, 10))
        
        # Nom de l'utilisateur
        self.user_name_label = ctk.CTkLabel(
            welcome_frame,
            text="",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.user_name_label.pack(pady=(0, 5))
        
        # Email de l'utilisateur
        self.user_email_label = ctk.CTkLabel(
            welcome_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.user_email_label.pack()
        
        # Statut du compte
        self.account_status_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        self.account_status_frame.pack(pady=10)
        
        self.account_status_label = ctk.CTkLabel(
            self.account_status_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.account_status_label.pack(side=ctk.LEFT, padx=(0, 5))
        
        self.account_status_badge = ctk.CTkLabel(
            self.account_status_frame,
            text="",
            width=80,
            height=22,
            corner_radius=11,
            font=ctk.CTkFont(size=11)
        )
        self.account_status_badge.pack(side=ctk.LEFT)
        
        # Séparateur
        ctk.CTkFrame(self.account_frame, height=1, fg_color="gray70").pack(fill=ctk.X, padx=20, pady=10)
        
        # Contenu principal en onglets
        self.account_tabs_var = ctk.StringVar(value="profile")
        
        # Frame des onglets du compte
        tabs_frame = ctk.CTkFrame(self.account_frame, fg_color="transparent")
        tabs_frame.pack(fill=ctk.X, pady=10)
        
        # Style des onglets
        tab_style = {
            "corner_radius": 6,
            "fg_color": "transparent",
            "hover_color": ("gray90", "gray30"),
            "height": 35
        }
        
        # Onglets
        self.profile_tab_btn = ctk.CTkButton(
            tabs_frame,
            text="Mon profil",
            command=lambda: self._show_account_tab("profile"),
            **tab_style
        )
        self.profile_tab_btn.pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)
        
        self.security_tab_btn = ctk.CTkButton(
            tabs_frame,
            text="Sécurité",
            command=lambda: self._show_account_tab("security"),
            **tab_style
        )
        self.security_tab_btn.pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)
        
        self.preferences_tab_btn = ctk.CTkButton(
            tabs_frame,
            text="Préférences",
            command=lambda: self._show_account_tab("preferences"),
            **tab_style
        )
        self.preferences_tab_btn.pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)
        
        # Contenu des onglets
        self.account_content_frame = ctk.CTkFrame(self.account_frame, fg_color="transparent")
        self.account_content_frame.pack(fill=ctk.BOTH, expand=True, pady=10)
        
        # Créer les contenus des différents onglets
        self._create_profile_tab()
        self._create_security_tab()
        self._create_preferences_tab()
        
        # Bouton de déconnexion
        self.logout_button = ctk.CTkButton(
            self.account_frame,
            text="Se déconnecter",
            command=self._handle_logout,
            height=40,
            corner_radius=8,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.logout_button.pack(fill=ctk.X, padx=20, pady=20)
    
    def _create_profile_tab(self):
        """Crée l'onglet de profil utilisateur"""
        self.profile_frame = ctk.CTkFrame(self.account_content_frame, fg_color="transparent")
        
        # Informations utilisateur
        info_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        info_frame.pack(fill=ctk.X, pady=10)
        
        # Champ nom
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(fill=ctk.X, pady=5)
        
        ctk.CTkLabel(
            name_frame,
            text="Nom complet",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.profile_name_var = ctk.StringVar()
        self.profile_name = ctk.CTkEntry(
            name_frame,
            textvariable=self.profile_name_var,
            placeholder_text="Votre nom complet",
            height=40,
            border_width=1
        )
        self.profile_name.pack(fill=ctk.X)
        
        # Champ email (non éditable)
        email_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        email_frame.pack(fill=ctk.X, pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Adresse email",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.profile_email_var = ctk.StringVar()
        self.profile_email = ctk.CTkEntry(
            email_frame,
            textvariable=self.profile_email_var,
            placeholder_text="Votre adresse email",
            height=40,
            border_width=1,
            state="disabled"
        )
        self.profile_email.pack(fill=ctk.X)
        
        # Date d'inscription
        created_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        created_frame.pack(fill=ctk.X, pady=5)
        
        ctk.CTkLabel(
            created_frame,
            text="Date d'inscription",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.profile_created_var = ctk.StringVar()
        self.profile_created = ctk.CTkEntry(
            created_frame,
            textvariable=self.profile_created_var,
            placeholder_text="Date d'inscription",
            height=40,
            border_width=1,
            state="disabled"
        )
        self.profile_created.pack(fill=ctk.X)
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        action_frame.pack(fill=ctk.X, pady=10)
        
        # Message de statut pour le profil
        self.profile_status_label = ctk.CTkLabel(
            action_frame,
            text="",
            text_color="red",
            anchor="center",
            font=ctk.CTkFont(size=12)
        )
        self.profile_status_label.pack(fill=ctk.X, padx=5, pady=(0, 10))
        
        # Bouton pour sauvegarder les modifications
        save_profile_button = ctk.CTkButton(
            action_frame,
            text="Enregistrer les modifications",
            command=self._save_profile,
            height=40,
            corner_radius=8,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d")
        )
        save_profile_button.pack(fill=ctk.X, pady=(0, 10))
    
    def _create_security_tab(self):
        """Crée l'onglet de sécurité"""
        self.security_frame = ctk.CTkFrame(self.account_content_frame, fg_color="transparent")
        
        # Titre de l'onglet
        ctk.CTkLabel(
            self.security_frame,
            text="Paramètres de sécurité",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 15))
        
        # Section de changement de mot de passe
        pwd_section = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        pwd_section.pack(fill=ctk.X, pady=10)
        
        ctk.CTkLabel(
            pwd_section,
            text="Changer votre mot de passe",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 10))
        
        # Mot de passe actuel
        current_frame = ctk.CTkFrame(pwd_section, fg_color="transparent")
        current_frame.pack(fill=ctk.X, pady=5)
        
        ctk.CTkLabel(
            current_frame,
            text="Mot de passe actuel",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.current_password_var = ctk.StringVar()
        self.current_password = ctk.CTkEntry(
            current_frame,
            textvariable=self.current_password_var,
            placeholder_text="Votre mot de passe actuel",
            show="•",
            height=40,
            border_width=1
        )
        self.current_password.pack(fill=ctk.X)
        
        # Nouveau mot de passe
        new_frame = ctk.CTkFrame(pwd_section, fg_color="transparent")
        new_frame.pack(fill=ctk.X, pady=5)
        
        ctk.CTkLabel(
            new_frame,
            text="Nouveau mot de passe",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.new_password_var = ctk.StringVar()
        self.new_password = ctk.CTkEntry(
            new_frame,
            textvariable=self.new_password_var,
            placeholder_text="Nouveau mot de passe",
            show="•",
            height=40,
            border_width=1
        )
        self.new_password.pack(fill=ctk.X)
        
        # Confirmation du nouveau mot de passe
        confirm_frame = ctk.CTkFrame(pwd_section, fg_color="transparent")
        confirm_frame.pack(fill=ctk.X, pady=5)
        
        ctk.CTkLabel(
            confirm_frame,
            text="Confirmer le nouveau mot de passe",
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        self.confirm_new_password_var = ctk.StringVar()
        self.confirm_new_password = ctk.CTkEntry(
            confirm_frame,
            textvariable=self.confirm_new_password_var,
            placeholder_text="Confirmer le nouveau mot de passe",
            show="•",
            height=40,
            border_width=1
        )
        self.confirm_new_password.pack(fill=ctk.X)
        
        # Message de statut pour le changement de mot de passe
        self.password_status_label = ctk.CTkLabel(
            pwd_section,
            text="",
            text_color="red",
            anchor="center",
            font=ctk.CTkFont(size=12)
        )
        self.password_status_label.pack(fill=ctk.X, padx=5, pady=(5, 10))
        
        # Bouton pour changer le mot de passe
        change_password_button = ctk.CTkButton(
            pwd_section,
            text="Changer mon mot de passe",
            command=self._change_password,
            height=40,
            corner_radius=8,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d")
        )
        change_password_button.pack(fill=ctk.X, pady=(0, 10))
    
    def _create_preferences_tab(self):
        """Crée l'onglet des préférences"""
        self.preferences_frame = ctk.CTkFrame(self.account_content_frame, fg_color="transparent")
        
        # Titre de l'onglet
        ctk.CTkLabel(
            self.preferences_frame,
            text="Préférences",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 15))
        
        # Section thème
        theme_section = ctk.CTkFrame(self.preferences_frame, fg_color="transparent")
        theme_section.pack(fill=ctk.X, pady=10)
        
        ctk.CTkLabel(
            theme_section,
            text="Thème de l'application",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 10))
        
        # Options de thème
        self.theme_var = ctk.StringVar(value="system")
        
        theme_options = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_options.pack(fill=ctk.X, pady=5)
        
        light_radio = ctk.CTkRadioButton(
            theme_options,
            text="Clair",
            variable=self.theme_var,
            value="light",
            command=self._change_theme
        )
        light_radio.pack(anchor="w", padx=20, pady=5)
        
        dark_radio = ctk.CTkRadioButton(
            theme_options,
            text="Sombre",
            variable=self.theme_var,
            value="dark",
            command=self._change_theme
        )
        dark_radio.pack(anchor="w", padx=20, pady=5)
        
        system_radio = ctk.CTkRadioButton(
            theme_options,
            text="Système",
            variable=self.theme_var,
            value="system",
            command=self._change_theme
        )
        system_radio.pack(anchor="w", padx=20, pady=5)
        
        # Section notifications
        notif_section = ctk.CTkFrame(self.preferences_frame, fg_color="transparent")
        notif_section.pack(fill=ctk.X, pady=10)
        
        ctk.CTkLabel(
            notif_section,
            text="Notifications",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(fill=ctk.X, padx=5, pady=(0, 10))
        
        # Options de notifications
        self.email_notif_var = ctk.BooleanVar(value=True)
        email_checkbox = ctk.CTkCheckBox(
            notif_section,
            text="Recevoir des notifications par email",
            variable=self.email_notif_var,
            command=self._save_preferences,
            border_width=2,
            corner_radius=6,
            hover_color=("#3498db", "#2980b9"),
            fg_color=("#3498db", "#2980b9")
        )
        email_checkbox.pack(anchor="w", padx=20, pady=5)
        
        self.update_notif_var = ctk.BooleanVar(value=True)
        update_checkbox = ctk.CTkCheckBox(
            notif_section,
            text="M'informer des mises à jour",
            variable=self.update_notif_var,
            command=self._save_preferences,
            border_width=2,
            corner_radius=6,
            hover_color=("#3498db", "#2980b9"),
            fg_color=("#3498db", "#2980b9")
        )
        update_checkbox.pack(anchor="w", padx=20, pady=5)
        
        # Message de statut pour les préférences
        self.preferences_status_label = ctk.CTkLabel(
            self.preferences_frame,
            text="",
            text_color="green",
            anchor="center",
            font=ctk.CTkFont(size=12)
        )
        self.preferences_status_label.pack(fill=ctk.X, padx=5, pady=(10, 0))
    
    def _handle_keyboard_nav(self, event):
        """
        Gère la navigation au clavier pour améliorer l'accessibilité
        
        Args:
            event: Événement clavier
        """
        try:
            # Récupérer la touche pressée
            key = event.keysym
            
            # Gérer la touche Tab pour la navigation entre les champs
            if key == "Tab":
                # La navigation par défaut est gérée par Tkinter
                pass
                
            # Gérer la touche Entrée pour soumettre le formulaire
            elif key == "Return":
                # Déterminer l'onglet actif
                current_tab = self.current_tab.get()
                
                # Soumettre le formulaire correspondant
                if current_tab == "login":
                    self._handle_login()
                elif current_tab == "register":
                    self._handle_register()
                elif current_tab == "account":
                    self._save_profile()
                    
            # Gérer les touches de navigation entre les onglets
            elif key == "1" and event.state & 4:  # Ctrl+1
                self._show_tab("login")
            elif key == "2" and event.state & 4:  # Ctrl+2
                self._show_tab("register")
            elif key == "3" and event.state & 4:  # Ctrl+3
                self._show_tab("account")
                
            # Gérer la touche Échap pour fermer la fenêtre
            elif key == "Escape":
                self.hide()
        except Exception as e:
            logger.error(f"Erreur lors de la gestion de la navigation au clavier: {e}")

    def _check_login_attempts(self, email):
        """
        Vérifie si l'utilisateur a dépassé le nombre maximum de tentatives de connexion
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            bool: True si l'utilisateur peut tenter de se connecter, False sinon
        """
        try:
            # Si l'email n'est pas dans le dictionnaire des tentatives, autoriser
            if email not in self.login_attempts:
                return True
                
            # Récupérer les informations sur les tentatives
            timestamp, count = self.login_attempts[email]
            
            # Vérifier si le délai d'attente est écoulé
            elapsed = (datetime.now() - timestamp).total_seconds()
            if elapsed > self.LOGIN_TIMEOUT:
                # Réinitialiser les tentatives
                del self.login_attempts[email]
                return True
                
            # Vérifier si le nombre maximum de tentatives est atteint
            if count >= self.MAX_LOGIN_ATTEMPTS:
                logger.warning(f"Nombre maximum de tentatives atteint pour {email}")
                return False
                
            # Autoriser la tentative
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des tentatives de connexion: {e}")
            # En cas d'erreur, autoriser par défaut
            return True
        
    def _handle_logout(self):
        """Gère la déconnexion de l'utilisateur"""
        try:
            # Vérifier si un utilisateur est connecté
            if not self.current_user:
                logger.warning("Tentative de déconnexion sans utilisateur connecté")
                return
                
            # Déconnecter l'utilisateur
            email = self.current_user.get("email", "")
            success = self.usage_tracker.clear_current_user()
            
            if success:
                logger.info(f"Utilisateur déconnecté: {email}")
                
                # Réinitialiser l'utilisateur courant
                self.current_user = None
                
                # Mettre à jour l'interface
                self._update_auth_state()
                
                # Appeler le callback d'authentification si défini
                if hasattr(self, 'auth_callback') and self.auth_callback:
                    self.auth_callback(False, None)
                
                # Afficher l'onglet login
                self._show_tab("login")
                
                # Afficher un message de succès
                if hasattr(self, 'login_status_label'):
                    self.login_status_label.configure(
                        text="Déconnexion réussie",
                        text_color="green"
                    )
                    # Effacer le message après 3 secondes
                    self.window.after(3000, lambda: self.login_status_label.configure(text=""))
            else:
                logger.error(f"Erreur lors de la déconnexion de {email}")
                
                # Afficher un message d'erreur
                if hasattr(self, 'login_status_label'):
                    self.login_status_label.configure(
                        text="Erreur lors de la déconnexion",
                        text_color="red"
                    )
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            
            # Afficher un message d'erreur
            if hasattr(self, 'login_status_label'):
                self.login_status_label.configure(
                    text=f"Erreur: {str(e)}",
                    text_color="red"
                )
        
    def _get_google_icon(self):
        """Récupère l'icône Google ou crée une icône temporaire"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "google_icon.png")
            if os.path.exists(icon_path):
                return ctk.CTkImage(Image.open(icon_path), size=(20, 20))
            else:
                # Créer une icône Google factice
                logger.info("Icône Google non trouvée, création d'une icône factice")
                # Créer une image avec un G blanc sur fond rouge
                img = Image.new("RGB", (20, 20), color=(234, 67, 53))  # Rouge Google
                return ctk.CTkImage(img, size=(20, 20))
        except Exception as e:
            logger.warning(f"Impossible de charger l'icône Google: {e}")
            # Si une erreur se produit, retourner une image vide
            img = Image.new("RGB", (20, 20), color=(255, 255, 255))
            return ctk.CTkImage(img, size=(20, 20))

    def _show_tab(self, tab_name):
        """
        Affiche l'onglet spécifié
        
        Args:
            tab_name: Nom de l'onglet à afficher ("login", "register", "account")
        """
        try:
            # Vérifier que les onglets existent
            if not hasattr(self, 'tabs') or not self.tabs:
                logger.warning("Les onglets n'existent pas, recréation nécessaire")
                # Si les onglets n'existent pas, tenter de les recréer
                if hasattr(self, 'main_frame') and self.main_frame:
                    self._create_tabs()
                else:
                    # Si le frame principal n'existe pas, recréer tous les widgets
                    self._create_widgets()
            
            # Vérifier que l'onglet demandé existe
            valid_tabs = ["login", "register", "account"]
            if tab_name not in valid_tabs:
                logger.warning(f"Onglet demandé '{tab_name}' invalide, utilisation de 'login' par défaut")
                tab_name = "login"
            
            # Mettre à jour la variable de l'onglet courant
            if hasattr(self, 'current_tab'):
                self.current_tab.set(tab_name)
                
                # Afficher le contenu approprié
                self._update_tab_content()
                
                logger.info(f"Onglet {tab_name} affiché")
            else:
                logger.error("Variable current_tab non disponible")
                # Tenter de la recréer
                self.current_tab = ctk.StringVar(value=tab_name)
                self._update_tab_content()
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de l'onglet {tab_name}: {e}")
            # En cas d'erreur grave, tenter de recréer complètement l'interface
            try:
                self._create_widgets()
                # Mettre à jour la variable et afficher l'onglet
                self.current_tab.set(tab_name)
                self._update_tab_content()
                logger.info(f"Interface recréée et onglet {tab_name} affiché après erreur")
            except Exception as e2:
                logger.error(f"Échec critique lors de la recréation de l'interface: {e2}")
    
    def _update_tab_content(self):
        """Met à jour le contenu affiché selon l'onglet sélectionné"""
        try:
            tab_name = self.current_tab.get()
            
            # Masquer tous les contenus d'onglets
            for content in ["login_frame", "register_frame", "account_frame"]:
                if hasattr(self, content) and getattr(self, content):
                    getattr(self, content).pack_forget()
            
            # Afficher le contenu approprié
            if tab_name == "login" and hasattr(self, 'login_frame'):
                self.login_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            elif tab_name == "register" and hasattr(self, 'register_frame'):
                self.register_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            elif tab_name == "account" and hasattr(self, 'account_frame'):
                self.account_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # Mettre à jour les styles des onglets
            if hasattr(self, 'tabs') and self.tabs:
                for tab in self.tabs.winfo_children():
                    tab_id = tab.cget("text").lower()
                    if tab_id == tab_name:
                        tab.configure(fg_color=("gray85", "gray25"))
                    else:
                        tab.configure(fg_color="transparent")
                        
            logger.debug(f"Contenu de l'onglet {tab_name} affiché")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du contenu de l'onglet: {e}")
            # En cas d'erreur, on peut essayer une approche plus directe
            try:
                if tab_name == "login" and hasattr(self, 'login_frame'):
                    for content in ["register_frame", "account_frame"]:
                        if hasattr(self, content) and getattr(self, content):
                            getattr(self, content).pack_forget()
                    self.login_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
                elif tab_name == "register" and hasattr(self, 'register_frame'):
                    for content in ["login_frame", "account_frame"]:
                        if hasattr(self, content) and getattr(self, content):
                            getattr(self, content).pack_forget()
                    self.register_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
                elif tab_name == "account" and hasattr(self, 'account_frame'):
                    for content in ["login_frame", "register_frame"]:
                        if hasattr(self, content) and getattr(self, content):
                            getattr(self, content).pack_forget()
                    self.account_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
                    
                logger.debug(f"Contenu de l'onglet {tab_name} affiché via méthode alternative")
            except Exception as e2:
                logger.error(f"Échec critique lors de l'affichage alternatif de l'onglet: {e2}")
    
    def _load_user_data(self):
        """
        Charge les données de l'utilisateur actuellement connecté
        et met à jour l'interface en conséquence
        """
        try:
            # Récupérer les données utilisateur
            user_data = self.usage_tracker.get_user_data()
            
            if user_data and "email" in user_data:
                self.current_user = user_data
                logger.info(f"Utilisateur chargé: {user_data.get('email')}")
                
                # Mettre à jour les champs du profil
                if hasattr(self, 'user_name_label'):
                    name = user_data.get('name', 'Utilisateur')
                    self.user_name_label.configure(text=name)
                
                if hasattr(self, 'user_email_label'):
                    email = user_data.get('email', '')
                    self.user_email_label.configure(text=email)
                
                # Mettre à jour les autres champs du profil si disponibles
                if hasattr(self, 'profile_name_var') and 'name' in user_data:
                    self.profile_name_var.set(user_data['name'])
                
                if hasattr(self, 'profile_email_var') and 'email' in user_data:
                    self.profile_email_var.set(user_data['email'])
                
                if hasattr(self, 'profile_created_var') and 'created_at' in user_data:
                    created_at = user_data.get('created_at', '')
                    if created_at:
                        try:
                            # Formater la date si c'est une chaîne ISO
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                            self.profile_created_var.set(formatted_date)
                        except:
                            self.profile_created_var.set(created_at)
                
                # Appeler le callback d'authentification si défini
                if hasattr(self, 'auth_callback') and self.auth_callback:
                    self.auth_callback(True, user_data)
            else:
                self.current_user = None
                logger.info("Aucun utilisateur connecté")
                
                # Appeler le callback d'authentification si défini
                if hasattr(self, 'auth_callback') and self.auth_callback:
                    self.auth_callback(False, None)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données utilisateur: {e}")
            self.current_user = None
    
    def _update_auth_state(self):
        """
        Met à jour l'interface en fonction de l'état d'authentification
        """
        try:
            # Vérifier si un utilisateur est connecté
            is_logged_in = self.current_user is not None
            
            # Mettre à jour la visibilité des onglets
            if is_logged_in:
                # Afficher l'onglet Compte et masquer l'onglet Inscription
                self.account_tab.grid()
                
                # Si on est sur l'onglet login ou register, basculer vers account
                current_tab = self.current_tab.get()
                if current_tab in ["login", "register"]:
                    self._show_tab("account")
            else:
                # Masquer l'onglet Compte si on n'est pas connecté
                # et qu'on est sur cet onglet, basculer vers login
                current_tab = self.current_tab.get()
                if current_tab == "account":
                    self._show_tab("login")
            
            # Mettre à jour les boutons de connexion/déconnexion
            if hasattr(self, 'login_button') and hasattr(self, 'logout_button'):
                if is_logged_in:
                    self.login_button.pack_forget()
                    self.logout_button.pack(fill=ctk.X, pady=(10, 0))
                else:
                    self.logout_button.pack_forget()
                    self.login_button.pack(fill=ctk.X, pady=(10, 0))
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'état d'authentification: {e}")
            
    def _save_user_settings(self, user_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde les paramètres de l'utilisateur
        
        Args:
            user_data: Données utilisateur à sauvegarder
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            if not user_data or "email" not in user_data:
                logger.error("Données utilisateur invalides")
                return False
                
            # Récupérer les utilisateurs existants
            users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.json")
            users = {}
            
            if os.path.exists(users_file):
                try:
                    with open(users_file, 'r', encoding='utf-8') as f:
                        users = json.load(f)
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture des utilisateurs: {e}")
            
            # Mettre à jour les données de l'utilisateur
            email = user_data.get("email")
            
            # Supprimer l'email des données pour éviter la duplication
            user_data_copy = user_data.copy()
            if "email" in user_data_copy:
                del user_data_copy["email"]
                
            # Mettre à jour les données
            users[email] = user_data_copy
            
            # Sauvegarder les utilisateurs
            os.makedirs(os.path.dirname(users_file), exist_ok=True)
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Paramètres utilisateur sauvegardés pour {email}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres utilisateur: {e}")
            return False
            
    def _save_profile(self):
        """Sauvegarde les modifications du profil utilisateur"""
        try:
            if not self.current_user:
                logger.error("Aucun utilisateur connecté")
                return
                
            # Récupérer les valeurs des champs
            name = self.profile_name_var.get() if hasattr(self, 'profile_name_var') else ""
            
            # Mettre à jour les données utilisateur
            user_data = self.current_user.copy()
            user_data["name"] = name
            
            # Sauvegarder les modifications
            if self._save_user_settings(user_data):
                # Mettre à jour l'utilisateur courant
                self.current_user = user_data
                
                # Mettre à jour l'interface
                if hasattr(self, 'user_name_label'):
                    self.user_name_label.configure(text=name)
                    
                # Afficher un message de succès
                logger.info("Profil mis à jour avec succès")
                
                # Afficher un message dans l'interface
                if hasattr(self, 'profile_status_label'):
                    self.profile_status_label.configure(
                        text="Profil mis à jour avec succès",
                        text_color="green"
                    )
                    # Effacer le message après 3 secondes
                    self.window.after(3000, lambda: self.profile_status_label.configure(text=""))
            else:
                # Afficher un message d'erreur
                logger.error("Erreur lors de la mise à jour du profil")
                
                # Afficher un message dans l'interface
                if hasattr(self, 'profile_status_label'):
                    self.profile_status_label.configure(
                        text="Erreur lors de la mise à jour du profil",
                        text_color="red"
                    )
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du profil: {e}")
            
            # Afficher un message dans l'interface
            if hasattr(self, 'profile_status_label'):
                self.profile_status_label.configure(
                    text=f"Erreur: {str(e)}",
                    text_color="red"
                )
                
    def _handle_login(self):
        """Gère la connexion de l'utilisateur"""
        try:
            # Récupérer les valeurs des champs
            email = self.email_var.get()
            password = self.password_var.get()
            remember_me = self.remember_var.get() if hasattr(self, 'remember_var') else False
            
            # Vérifier que les champs sont remplis
            if not email or not password:
                logger.warning("Champs de connexion incomplets")
                if hasattr(self, 'login_status_label'):
                    self.login_status_label.configure(
                        text="Veuillez remplir tous les champs",
                        text_color="red"
                    )
                return
            
            # Vérifier le format de l'email
            if not self._is_valid_email(email):
                logger.warning("Format d'email invalide")
                if hasattr(self, 'login_status_label'):
                    self.login_status_label.configure(
                        text="Format d'email invalide",
                        text_color="red"
                    )
                return
            
            # Vérifier les tentatives de connexion
            if not self._check_login_attempts(email):
                logger.warning(f"Trop de tentatives de connexion pour {email}")
                if hasattr(self, 'login_status_label'):
                    self.login_status_label.configure(
                        text=f"Trop de tentatives, réessayez dans {self.LOGIN_TIMEOUT//60} minutes",
                        text_color="red"
                    )
                return
            
            # Vérifier les identifiants
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_data = self.usage_tracker.authenticate_user(email, hashed_password)
            
            if user_data:
                logger.info(f"Utilisateur connecté: {email} (Rester connecté: {remember_me})")
                
                # Mettre à jour l'utilisateur courant
                self.current_user = user_data
                
                # Enregistrer la préférence "Rester connecté"
                self.usage_tracker.set_remember_me(email, remember_me)
                logger.info(f"Préférence 'Rester connecté' définie à {remember_me} pour {email}")
                
                # Réinitialiser les tentatives de connexion
                if email in self.login_attempts:
                    del self.login_attempts[email]
                
                # Mettre à jour l'interface
                self._update_auth_state()
                
                # Masquer la fenêtre d'authentification
                self.hide()
                
                # Appeler le callback d'authentification si défini
                if hasattr(self, 'auth_callback') and self.auth_callback:
                    self.auth_callback(True, user_data)
                
                # Restaurer complètement l'interface principale
                if hasattr(self.parent, 'main_frame') and self.parent.main_frame:
                    # S'assurer que tous les widgets sont visibles et correctement positionnés
                    try:
                        if not self.parent.main_frame.winfo_ismapped():
                            self.parent.main_frame.pack(fill="both", expand=True)
                            logger.info("Interface principale restaurée après connexion")
                    except Exception as e:
                        logger.error(f"Erreur lors de la restauration de l'interface principale: {e}")
                
                # S'assurer que le tableau de bord est affiché
                if hasattr(self.parent, 'show_dashboard'):
                    try:
                        self.parent.show_dashboard()
                        logger.info("Tableau de bord affiché après connexion")
                    except Exception as e:
                        logger.error(f"Erreur lors de l'affichage du tableau de bord: {e}")
                
                # Charger les paramètres utilisateur
                self._load_user_data()
                
                return True
            else:
                logger.warning(f"Échec de connexion pour {email}")
                
                # Incrémenter les tentatives de connexion
                if email in self.login_attempts:
                    self.login_attempts[email][1] += 1
                else:
                    self.login_attempts[email] = [datetime.now(), 1]
                
                # Afficher un message d'erreur
                if hasattr(self, 'login_status_label'):
                    self.login_status_label.configure(
                        text="Email ou mot de passe incorrect",
                        text_color="red"
                    )
                
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            
            # Afficher un message d'erreur
            if hasattr(self, 'login_status_label'):
                self.login_status_label.configure(
                    text=f"Erreur: {str(e)}",
                    text_color="red"
                )
            
            return False
            
    def _is_valid_email(self, email):
        """Vérifie si l'email est valide"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def _handle_register(self):
        """Gère l'inscription d'un nouvel utilisateur"""
        try:
            # Récupérer les valeurs des champs
            name = self.register_name_var.get() if hasattr(self, 'register_name_var') else ""
            email = self.email_var.get()
            password = self.password_var.get()
            confirm_password = self.confirm_password_var.get()
            
            # Vérifier que les champs sont remplis
            if not email or not password or not confirm_password:
                logger.warning("Champs d'inscription incomplets")
                if hasattr(self, 'register_status_label'):
                    self.register_status_label.configure(
                        text="Veuillez remplir tous les champs obligatoires",
                        text_color="red"
                    )
                return False
            
            # Vérifier le format de l'email
            if not self._is_valid_email(email):
                logger.warning("Format d'email invalide")
                if hasattr(self, 'register_status_label'):
                    self.register_status_label.configure(
                        text="Format d'email invalide",
                        text_color="red"
                    )
                return False
            
            # Vérifier que les mots de passe correspondent
            if password != confirm_password:
                logger.warning("Les mots de passe ne correspondent pas")
                if hasattr(self, 'register_status_label'):
                    self.register_status_label.configure(
                        text="Les mots de passe ne correspondent pas",
                        text_color="red"
                    )
                return False
            
            # Vérifier la complexité du mot de passe
            if len(password) < self.PASSWORD_MIN_LENGTH:
                logger.warning("Mot de passe trop court")
                if hasattr(self, 'register_status_label'):
                    self.register_status_label.configure(
                        text=f"Le mot de passe doit contenir au moins {self.PASSWORD_MIN_LENGTH} caractères",
                        text_color="red"
                    )
                return False
            
            # Vérifier si l'utilisateur existe déjà
            users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.json")
            users = {}
            
            if os.path.exists(users_file):
                try:
                    with open(users_file, 'r', encoding='utf-8') as f:
                        users = json.load(f)
                        
                    if email in users:
                        logger.warning(f"L'utilisateur {email} existe déjà")
                        if hasattr(self, 'register_status_label'):
                            self.register_status_label.configure(
                                text="Cet email est déjà utilisé",
                                text_color="red"
                            )
                        return False
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture des utilisateurs: {e}")
            
            # Créer le nouvel utilisateur
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_data = {
                "email": email,
                "password": hashed_password,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "settings": {}
            }
            
            # Sauvegarder l'utilisateur
            users[email] = {k: v for k, v in user_data.items() if k != "email"}
            
            os.makedirs(os.path.dirname(users_file), exist_ok=True)
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Nouvel utilisateur créé: {email}")
            
            # Connecter l'utilisateur
            self.current_user = user_data
            self.usage_tracker.set_current_user(user_data)
            
            # Mettre à jour l'interface
            self._update_auth_state()
            
            # Afficher un message de succès temporaire
            if hasattr(self, 'register_status_label'):
                self.register_status_label.configure(
                    text="Inscription réussie ! Redirection vers le tableau de bord...",
                    text_color="green"
                )
            
            # Créer un spinner de chargement pendant la redirection
            loading_frame = None
            try:
                loading_frame = ctk.CTkFrame(self.window)
                loading_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
                
                # Titre du chargement
                ctk.CTkLabel(
                    loading_frame,
                    text="Préparation du tableau de bord",
                    font=ctk.CTkFont(size=16, weight="bold")
                ).pack(pady=(10, 5))
                
                # Message
                ctk.CTkLabel(
                    loading_frame,
                    text="Veuillez patienter pendant l'initialisation de votre tableau de bord..."
                ).pack(pady=5)
                
                # Spinner
                spinner = ctk.CTkProgressBar(loading_frame, width=200)
                spinner.pack(pady=10)
                spinner.configure(mode="indeterminate")
                spinner.start()
                
                # Forcer la mise à jour de l'interface
                self.window.update()
            except Exception as e:
                logger.error(f"Erreur lors de la création du spinner: {e}")
            
            # Appeler le callback d'authentification si défini après un court délai
            def complete_registration():
                try:
                    # Appeler le callback d'authentification si défini
                    if hasattr(self, 'auth_callback') and self.auth_callback:
                        self.auth_callback(True, user_data)
                    
                    # Fermer la fenêtre d'authentification
                    self.hide()
                    
                    # Afficher un message de succès et rediriger vers le tableau de bord
                    if hasattr(self.parent, 'show_dashboard') and callable(self.parent.show_dashboard):
                        # Rediriger vers le tableau de bord
                        self.parent.show_dashboard()
                        logger.info("Utilisateur redirigé vers le tableau de bord après inscription")
                    else:
                        logger.warning("Impossible de rediriger vers le tableau de bord: méthode non trouvée")
                        # Tentative alternative pour afficher le tableau de bord
                        try:
                            if hasattr(self.parent, 'show_view') and callable(self.parent.show_view):
                                self.parent.show_view("dashboard")
                                logger.info("Redirection alternative vers le tableau de bord")
                            elif hasattr(self.parent, 'winfo_toplevel') and hasattr(self.parent.winfo_toplevel(), 'show_view'):
                                # Si nous sommes dans une fenêtre modale, essayer avec la fenêtre principale
                                self.parent.winfo_toplevel().show_view("dashboard")
                                logger.info("Redirection via la fenêtre principale vers le tableau de bord")
                        except Exception as e:
                            logger.error(f"Erreur lors de la redirection vers le tableau de bord: {e}")
                    
                    # Afficher un message de bienvenue
                    if hasattr(self.parent, 'show_message'):
                        self.parent.show_message(
                            "Inscription réussie",
                            f"Bienvenue {name if name else email} ! Votre compte a été créé avec succès.",
                            "success"
                        )
                except Exception as e:
                    logger.error(f"Erreur lors de la finalisation de l'inscription: {e}")
                    if loading_frame and loading_frame.winfo_exists():
                        loading_frame.destroy()
            
            # Déclencher la redirection après un court délai pour permettre l'affichage du spinner
            self.window.after(500, complete_registration)
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {e}")
            
            # Afficher un message d'erreur
            if hasattr(self, 'register_status_label'):
                self.register_status_label.configure(
                    text=f"Erreur: {str(e)}",
                    text_color="red"
                )
            
            return False
            
    def _validate_email(self, *args):
        """Valide le format de l'email en temps réel"""
        try:
            email = self.email_var.get()
            
            # Vérifier si l'email est vide
            if not email:
                self.email_valid = False
                
                # Mettre à jour les messages d'erreur
                if hasattr(self, 'login_email_error'):
                    self.login_email_error.configure(text="")
                if hasattr(self, 'register_email_error'):
                    self.register_email_error.configure(text="")
                    
                return
            
            # Vérifier le format de l'email
            is_valid = self._is_valid_email(email)
            self.email_valid = is_valid
            
            # Mettre à jour les messages d'erreur
            error_msg = "" if is_valid else "Format d'email invalide"
            
            if hasattr(self, 'login_email_error'):
                self.login_email_error.configure(text=error_msg)
                
            if hasattr(self, 'register_email_error'):
                self.register_email_error.configure(text=error_msg)
        except Exception as e:
            logger.error(f"Erreur lors de la validation de l'email: {e}")
            
    def _validate_password(self, *args):
        """Valide la complexité du mot de passe en temps réel"""
        try:
            password = self.password_var.get()
            
            # Vérifier si le mot de passe est vide
            if not password:
                self.password_valid = False
                
                # Mettre à jour les messages d'erreur
                if hasattr(self, 'login_password_error'):
                    self.login_password_error.configure(text="")
                if hasattr(self, 'register_password_error'):
                    self.register_password_error.configure(text="")
                    
                return
            
            # Vérifier la longueur du mot de passe
            is_valid = len(password) >= self.PASSWORD_MIN_LENGTH
            self.password_valid = is_valid
            
            # Mettre à jour les messages d'erreur
            error_msg = "" if is_valid else f"Minimum {self.PASSWORD_MIN_LENGTH} caractères"
            
            if hasattr(self, 'login_password_error'):
                self.login_password_error.configure(text=error_msg)
                
            if hasattr(self, 'register_password_error'):
                self.register_password_error.configure(text=error_msg)
                
            # Valider également la confirmation si elle existe
            if hasattr(self, 'confirm_password_var'):
                self._validate_confirm_password()
        except Exception as e:
            logger.error(f"Erreur lors de la validation du mot de passe: {e}")
            
    def _validate_confirm_password(self, *args):
        """Valide que la confirmation du mot de passe correspond au mot de passe"""
        try:
            password = self.password_var.get()
            confirm_password = self.confirm_password_var.get()
            
            # Vérifier si la confirmation est vide
            if not confirm_password:
                self.confirm_password_valid = False
                
                # Mettre à jour le message d'erreur
                if hasattr(self, 'register_confirm_password_error'):
                    self.register_confirm_password_error.configure(text="")
                    
                return
            
            # Vérifier que les mots de passe correspondent
            is_valid = password == confirm_password
            self.confirm_password_valid = is_valid
            
            # Mettre à jour le message d'erreur
            error_msg = "" if is_valid else "Les mots de passe ne correspondent pas"
            
            if hasattr(self, 'register_confirm_password_error'):
                self.register_confirm_password_error.configure(text=error_msg)
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la confirmation du mot de passe: {e}")

    def hide(self):
        """Masque la fenêtre d'authentification"""
        try:
            # Si nous utilisons une fenêtre Toplevel, la masquer
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.withdraw()
                logger.info("Fenêtre d'authentification masquée")
            # Si nous utilisons le parent directement, masquer les widgets
            elif hasattr(self, 'main_frame'):
                self.main_frame.pack_forget()
                logger.info("Widgets d'authentification masqués")
        except Exception as e:
            logger.error(f"Erreur lors du masquage de l'interface d'authentification: {e}")
            
    def show(self):
        """Affiche la fenêtre d'authentification"""
        try:
            # Détruire toute fenêtre TopLevel existante pour éviter les doublons
            if hasattr(self, 'window') and self.window.winfo_exists():
                try:
                    self.window.destroy()
                except Exception as e:
                    logger.debug(f"Erreur lors de la destruction de la fenêtre existante: {e}")
            
            # Créer une interface directement dans le parent
            if not hasattr(self, 'main_frame') or not self.main_frame:
                # Créer les widgets directement dans le parent
                self._create_widgets()
                logger.info("Widgets d'authentification créés directement dans le parent")
            
            # Mettre à jour l'interface selon l'état de connexion
            self._update_auth_state()
            
            # S'assurer que le contenu est visible
            if hasattr(self, 'main_frame'):
                self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Forcer la mise à jour pour éviter les problèmes d'affichage
            self.parent.update_idletasks()
            
            logger.info("Interface d'authentification affichée directement dans le parent")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de l'interface d'authentification: {e}")
            # Créer une interface de secours en cas d'erreur
            try:
                # Nettoyer l'interface existante
                for widget in self.parent.winfo_children():
                    widget.destroy()
                
                # Créer une interface minimaliste
                frame = ctk.CTkFrame(self.parent)
                frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                label = ctk.CTkLabel(
                    frame,
                    text="Interface d'authentification",
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                label.pack(pady=20)
                
                # Champs d'authentification simples
                email_label = ctk.CTkLabel(frame, text="Email:")
                email_label.pack(anchor="w", pady=(10, 0))
                
                self.email_var = ctk.StringVar()
                email_entry = ctk.CTkEntry(frame, width=300, textvariable=self.email_var)
                email_entry.pack(pady=(0, 10))
                
                password_label = ctk.CTkLabel(frame, text="Mot de passe:")
                password_label.pack(anchor="w", pady=(10, 0))
                
                self.password_var = ctk.StringVar()
                password_entry = ctk.CTkEntry(frame, show="•", width=300, textvariable=self.password_var)
                password_entry.pack(pady=(0, 20))
                
                login_button = ctk.CTkButton(
                    frame,
                    text="Se connecter",
                    width=200,
                    command=self._handle_login
                )
                login_button.pack(pady=10)
                
                logger.info("Interface d'authentification simplifiée créée après erreur")
            except Exception as e2:
                logger.critical(f"Échec critique lors de la création d'une interface de secours: {e2}")
                # Afficher un simple message d'erreur
                try:
                    label = ctk.CTkLabel(
                        self.parent,
                        text="Erreur lors de l'affichage de l'interface d'authentification.\nVeuillez redémarrer l'application.",
                        font=ctk.CTkFont(size=14),
                        text_color="red"
                    )
                    label.pack(expand=True, pady=50)
                except:
                    pass

    def set_auth_callback(self, callback):
        """
        Définit le callback à appeler lorsque l'état d'authentification change
        
        Args:
            callback: Fonction à appeler avec (is_authenticated, user_data)
        """
        self.auth_callback = callback
        logger.info("Callback d'authentification défini")
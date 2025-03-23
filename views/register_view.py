#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue d'inscription simplifiée pour l'application Vynal Docs Automator
"""

import os
import json
import logging
import hashlib
import customtkinter as ctk
import re
from typing import Callable, Dict, Any, Optional
from utils.usage_tracker import UsageTracker
from datetime import datetime
import tkinter as tk
import time
import shutil

logger = logging.getLogger("VynalDocsAutomator.RegisterView")

class RegisterView(ctk.CTkFrame):
    """Vue d'inscription simplifiée en une seule page"""
    
    # Constantes pour la validation
    PASSWORD_MIN_LENGTH = 8
    
    def __init__(self, parent, usage_tracker=None, on_success=None):
        """
        Initialise la vue d'inscription
        
        Args:
            parent: Widget parent
            usage_tracker: Instance du gestionnaire d'utilisation
            on_success: Callback appelé après inscription réussie
        """
        super().__init__(parent)
        self.parent = parent
        self.usage_tracker = usage_tracker or UsageTracker()
        self.on_success_callback = on_success
        
        # Variables de saisie
        self.name_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.confirm_password_var = ctk.StringVar()
        self.marketing_var = ctk.BooleanVar(value=False)
        
        # Variables d'état
        self.email_valid = False
        self.password_valid = False
        self.confirm_password_valid = False
        
        # Configurer les callbacks de validation
        self.email_var.trace_add("write", self._validate_email)
        self.password_var.trace_add("write", self._validate_password)
        self.confirm_password_var.trace_add("write", self._validate_confirm_password)
        
        # Créer l'interface
        self._create_widgets()
        
        logger.info("Vue d'inscription simplifiée initialisée")
    
    def _create_widgets(self):
        """Crée le formulaire d'inscription"""
        # En-tête avec logo
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill=ctk.X, padx=20, pady=(20, 10))
        
        # Logo/Icône
        ctk.CTkLabel(
            header_frame,
            text="Vynal Docs Automator",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(10, 5))
        
        # Titre
        ctk.CTkLabel(
            header_frame,
            text="Créer un compte",
            font=ctk.CTkFont(size=18)
        ).pack(pady=5)
        
        # Formulaire
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)
        
        # Champ Nom
        ctk.CTkLabel(
            form_frame,
            text="Nom :",
            anchor="w",
            font=ctk.CTkFont(size=14)
        ).pack(fill=ctk.X, padx=5, pady=(10, 0))
        
        self.name_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.name_var,
            height=40,
            placeholder_text="Votre nom complet"
        )
        self.name_entry.pack(fill=ctk.X, padx=5, pady=5)
        
        # Champ Email
        ctk.CTkLabel(
            form_frame,
            text="Email :",
            anchor="w",
            font=ctk.CTkFont(size=14)
        ).pack(fill=ctk.X, padx=5, pady=(10, 0))
        
        self.email_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.email_var,
            height=40,
            placeholder_text="votre.email@exemple.com"
        )
        self.email_entry.pack(fill=ctk.X, padx=5, pady=5)
        
        self.email_status = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="gray",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.email_status.pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        # Champ Mot de passe
        ctk.CTkLabel(
            form_frame,
            text="Mot de passe :",
            anchor="w",
            font=ctk.CTkFont(size=14)
        ).pack(fill=ctk.X, padx=5, pady=(10, 0))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.password_var,
            height=40,
            placeholder_text="Votre mot de passe",
            show="●"
        )
        self.password_entry.pack(fill=ctk.X, padx=5, pady=5)
        
        self.password_status = ctk.CTkLabel(
            form_frame,
            text=f"Le mot de passe doit contenir au moins {self.PASSWORD_MIN_LENGTH} caractères",
            text_color="gray",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.password_status.pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        # Champ Confirmation du mot de passe
        ctk.CTkLabel(
            form_frame,
            text="Confirmer le mot de passe :",
            anchor="w",
            font=ctk.CTkFont(size=14)
        ).pack(fill=ctk.X, padx=5, pady=(10, 0))
        
        self.confirm_password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.confirm_password_var,
            height=40,
            placeholder_text="Confirmez votre mot de passe",
            show="●"
        )
        self.confirm_password_entry.pack(fill=ctk.X, padx=5, pady=5)
        
        self.confirm_status = ctk.CTkLabel(
            form_frame,
            text="",
            text_color="gray",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.confirm_status.pack(fill=ctk.X, padx=5, pady=(0, 5))
        
        # Label d'état
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.pack(fill=ctk.X, padx=5, pady=10)
        
        # Option marketing
        self.marketing_checkbox = ctk.CTkCheckBox(
            form_frame,
            text="Je souhaite recevoir des informations sur les nouveautés",
            variable=self.marketing_var,
            checkbox_width=20,
            checkbox_height=20
        )
        self.marketing_checkbox.pack(fill=ctk.X, padx=5, pady=5)
        
        # Boutons
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, padx=20, pady=(5, 20))
        
        # Configuration de la grille pour les boutons
        buttons_frame.columnconfigure(0, weight=1)  # Pour le bouton retour (à gauche)
        buttons_frame.columnconfigure(1, weight=1)  # Pour le bouton d'inscription (à droite)
        
        # Bouton de retour (à gauche)
        self.back_button = ctk.CTkButton(
            buttons_frame,
            text="Retour",
            command=self._handle_back,
            width=150,
            height=40,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        self.back_button.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Bouton d'inscription (à droite)
        self.register_button = ctk.CTkButton(
            buttons_frame,
            text="Créer mon compte",
            command=self._handle_register,
            width=150,
            height=40
        )
        self.register_button.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Focus sur le premier champ
        self.name_entry.focus_set()
    
    def _validate_email(self, *args):
        """Valide le format de l'email en temps réel"""
        try:
            email = self.email_var.get()
            
            # Vérifier si l'email est vide
            if not email:
                self.email_valid = False
                self.email_status.configure(text="")
                return
            
            # Vérifier le format de l'email
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid = re.match(pattern, email) is not None
            self.email_valid = is_valid
            
            # Mettre à jour le message d'erreur
            self.email_status.configure(
                text="" if is_valid else "Format d'email invalide"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la validation de l'email: {e}")
    
    def _validate_password(self, *args):
        """Valide la complexité du mot de passe en temps réel"""
        try:
            password = self.password_var.get()
            
            # Vérifier si le mot de passe est vide
            if not password:
                self.password_valid = False
                self.password_status.configure(text="")
                return
            
            # Vérifier la longueur du mot de passe
            is_valid = len(password) >= self.PASSWORD_MIN_LENGTH
            self.password_valid = is_valid
            
            # Mettre à jour le message d'erreur
            self.password_status.configure(
                text="" if is_valid else f"Le mot de passe doit contenir au moins {self.PASSWORD_MIN_LENGTH} caractères"
            )
            
            # Valider également la confirmation
            self._validate_confirm_password()
        except Exception as e:
            logger.error(f"Erreur lors de la validation du mot de passe: {e}")
    
    def _validate_confirm_password(self, *args):
        """Valide que la confirmation correspond au mot de passe"""
        try:
            password = self.password_var.get()
            confirm = self.confirm_password_var.get()
            
            # Vérifier si la confirmation est vide
            if not confirm:
                self.confirm_password_valid = False
                self.confirm_status.configure(text="")
                return
            
            # Vérifier que les mots de passe correspondent
            is_valid = password == confirm
            self.confirm_password_valid = is_valid
            
            # Mettre à jour le message d'erreur
            self.confirm_status.configure(
                text="" if is_valid else "Les mots de passe ne correspondent pas"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la confirmation: {e}")
    
    def _handle_register(self):
        """Traite le formulaire d'inscription"""
        try:
            # Récupérer les valeurs des champs
            name = self.name_var.get().strip()
            email = self.email_var.get().strip()
            password = self.password_var.get()
            confirm_password = self.confirm_password_var.get()
            
            # Vérifier que les champs obligatoires sont remplis
            if not all([name, email, password, confirm_password]):
                self.status_label.configure(text="Tous les champs sont obligatoires", text_color="red")
                return
            
            # Vérifier que les mots de passe correspondent
            if password != confirm_password:
                self.status_label.configure(text="Les mots de passe ne correspondent pas", text_color="red")
                return
            
            # Valider l'email
            if not self.email_valid:
                self.status_label.configure(text="Adresse email invalide", text_color="red")
                return
            
            # Valider le mot de passe
            if not self.password_valid:
                self.status_label.configure(
                    text=f"Le mot de passe doit contenir au moins {self.PASSWORD_MIN_LENGTH} caractères",
                    text_color="red"
                )
                return
            
            # Vérifier que l'email n'est pas déjà utilisé
            existing_users = {}
            users_file = os.path.join('data', 'users.json')
            os.makedirs(os.path.dirname(users_file), exist_ok=True)
            
            if os.path.exists(users_file):
                try:
                    with open(users_file, 'r', encoding='utf-8') as f:
                        existing_users = json.load(f)
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture du fichier utilisateurs: {e}")
                    self.status_label.configure(text="Erreur lors de l'inscription, veuillez réessayer", text_color="red")
                    return
            
            if email in existing_users:
                self.status_label.configure(text="Cette adresse email est déjà utilisée", text_color="red")
                return
            
            # Hacher le mot de passe
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Créer l'utilisateur
            user_data = {
                'name': name,
                'email': email,
                'password': hashed_password,
                'created_at': time.time(),
                'last_login': datetime.now().isoformat(),
                'theme': 'dark',
                'license_key': '',
                'license_valid': False,
                'license_verified_at': int(time.time()),
                'terms_accepted': True,
                'privacy_accepted': True,
                'marketing_accepted': self.marketing_var.get()
            }
            
            # Sauvegarder l'utilisateur sans l'email comme clé pour éviter les problèmes d'encodage
            try:
                # Faire une sauvegarde du fichier existant si nécessaire
                if os.path.exists(users_file):
                    try:
                        backup_file = f"{users_file}.bak"
                        shutil.copy2(users_file, backup_file)
                        logger.info(f"Sauvegarde du fichier utilisateurs créée: {backup_file}")
                    except Exception as e:
                        logger.warning(f"Impossible de créer une sauvegarde du fichier utilisateurs: {e}")
                
                # Écrire dans le fichier utilisateurs
                try:
                    existing_users[email] = user_data
                    with open(users_file, 'w', encoding='utf-8') as f:
                        json.dump(existing_users, f, indent=4, ensure_ascii=False)
                    logger.info(f"Utilisateur enregistré avec succès: {email}")
                except PermissionError:
                    logger.error(f"Erreur de permission lors de l'écriture dans {users_file}")
                    self.status_label.configure(text="Erreur de permission lors de l'inscription", text_color="red")
                    return
                except Exception as e:
                    logger.error(f"Erreur lors de l'écriture dans le fichier utilisateurs: {e}", exc_info=True)
                    self.status_label.configure(text="Erreur lors de l'inscription, veuillez réessayer", text_color="red")
                    return
                
                # Mettre à jour l'état d'authentification
                self.usage_tracker.set_active_user(email, user_data)
                self.usage_tracker.save_session()
                
                # Configuration temporaire pour le message de succès
                self.status_label.configure(
                    text="Inscription réussie ! Redirection...",
                    text_color="green"
                )
                
                # Créer un écran de chargement avec un spinner
                try:
                    loading_frame = ctk.CTkFrame(self)
                    loading_frame.pack(fill=ctk.BOTH, expand=True)
                    
                    spinner_content = ctk.CTkFrame(loading_frame, fg_color="transparent")
                    spinner_content.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
                    
                    ctk.CTkLabel(
                        spinner_content,
                        text="Préparation du tableau de bord",
                        font=ctk.CTkFont(size=16, weight="bold")
                    ).pack(pady=(0, 20))
                    
                    progress_bar = ctk.CTkProgressBar(spinner_content, width=300)
                    progress_bar.pack(pady=10)
                    progress_bar.configure(mode="indeterminate")
                    progress_bar.start()
                    
                    # Forcer la mise à jour pour afficher le spinner
                    self.master.update()
                    
                    # Fonction pour finaliser l'inscription
                    def on_complete():
                        try:
                            # Sauvegarder le callback et les données pour l'utiliser après fermeture de la fenêtre
                            callback = self.on_success_callback
                            data = user_data
                            
                            logger.info(f"Finalisation de l'inscription pour: {email}")
                            
                            # Fermer la fenêtre d'inscription
                            if self.master and self.master.winfo_exists():
                                window_reference = self.master
                                
                                # Utiliser after_idle pour assurer que le callback est appelé après la destruction
                                window_reference.after_idle(lambda: self._invoke_callback(callback, data))
                                
                                # Détruire la fenêtre
                                window_reference.destroy()
                            else:
                                logger.warning("La fenêtre d'inscription n'existe plus")
                                # Appeler le callback directement si la fenêtre n'existe plus
                                if callback:
                                    callback(data)
                        except Exception as e:
                            logger.error(f"Erreur lors de la finalisation de l'inscription: {e}", exc_info=True)
                            # Essayer de fermer la fenêtre même en cas d'erreur
                            try:
                                if self.master and self.master.winfo_exists():
                                    self.master.destroy()
                            except Exception:
                                pass
                    
                    # Appeler on_complete après un court délai pour permettre au spinner d'être visible
                    self.master.after(500, on_complete)
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la création du spinner: {e}", exc_info=True)
                    # Appeler directement le callback en cas d'erreur
                    if self.on_success_callback:
                        self.on_success_callback(user_data)
                    # Fermer la fenêtre même en cas d'erreur
                    if self.master and self.master.winfo_exists():
                        self.master.destroy()
                
            except Exception as e:
                logger.error(f"Erreur lors de l'inscription: {e}", exc_info=True)
                self.status_label.configure(text=f"Erreur: {str(e)}", text_color="red")
                
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'inscription: {e}", exc_info=True)
            self.status_label.configure(text="Une erreur inattendue est survenue", text_color="red")
    
    def _invoke_callback(self, callback, data):
        """Appelle le callback avec les données utilisateur de manière sécurisée"""
        try:
            if callback:
                logger.info("Exécution du callback de succès d'inscription")
                callback(data)
            else:
                logger.warning("Aucun callback de succès fourni pour l'inscription")
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du callback d'inscription: {e}", exc_info=True)
    
    def _handle_back(self):
        """Ferme la vue d'inscription et ouvre la vue de connexion"""
        try:
            # Fermer la fenêtre d'inscription
            if self.parent and self.parent.winfo_exists():
                self.parent.destroy()
            logger.info("Retour à la vue de connexion")
        except Exception as e:
            logger.error(f"Erreur lors du retour à la vue de connexion: {e}")
            # Tenter de fermer quand même
            try:
                if self.parent and self.parent.winfo_exists():
                    self.parent.destroy()
            except Exception:
                pass 
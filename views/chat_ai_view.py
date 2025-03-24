#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue pour l'interface de Chat IA de l'application Vynal Docs Automator
"""

import customtkinter as ctk
import logging
from ai.chat_interface import AIChatInterface
from typing import Any
import tkinter as tk
from tkinter import ttk
import webbrowser

logger = logging.getLogger("VynalDocsAutomator.ChatAIView")

class ChatAIView:
    """
    Vue pour l'interface de Chat IA
    Permet d'interagir avec le modèle d'IA via une interface conversationnelle
    """
    
    def __init__(self, parent: ctk.CTkFrame, app_model: Any):
        """
        Initialise la vue de Chat IA
        
        Args:
            parent: Widget parent
            app_model: Modèle de l'application
        """
        self.parent = parent
        self.model = app_model
        
        # Créer le cadre principal
        self.frame = ctk.CTkFrame(parent)
        
        # Configurer les styles ttk pour les erreurs
        self.configure_styles()
        
        # Créer les widgets
        self.create_widgets()
        
        logger.info("Vue de Chat IA initialisée")
    
    def configure_styles(self):
        """Configure les styles pour l'affichage d'erreurs"""
        try:
            style = ttk.Style()
            style.configure("Error.TFrame", background="#ffeded")
            style.configure("Error.TLabel", background="#ffeded", foreground="#d32f2f", 
                            font=("Segoe UI", 11))
            logger.debug("Styles pour les erreurs configurés")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration des styles: {e}", exc_info=True)
    
    def show(self):
        """Affiche la vue"""
        if self.frame is not None:
            self.frame.pack(fill=ctk.BOTH, expand=True)
            logger.debug("Vue de Chat IA affichée")
    
    def hide(self):
        """Cache la vue"""
        if self.frame is not None:
            self.frame.pack_forget()
            logger.debug("Vue de Chat IA masquée")
    
    def update_view(self):
        """Met à jour la vue"""
        # Pas d'opération spécifique pour la mise à jour
        pass
    
    def create_widgets(self):
        """Crée les widgets pour l'onglet"""
        try:
            # Vérifier si l'utilisateur a une licence active
            has_license = self.model.check_license()
            
            # Si l'utilisateur n'a pas de licence, vérifier l'accès au chat IA
            if not has_license:
                # Vérifier l'accès via le gestionnaire de version gratuite
                can_access, message = self.model.free_version_manager.check_ai_chat_access()
                if not can_access:
                    # Afficher le message sur les limitations de la version gratuite
                    self.afficher_limitation_version_gratuite(message)
                    return
            
            # Créer un conteneur pour l'interface de chat
            self.chat_container = ttk.Frame(self.frame)
            self.chat_container.pack(fill="both", expand=True, padx=0, pady=0)
            
            # Créer l'interface de chat
            try:
                from ai.chat_interface import AIChatInterface
                self.chat_interface = AIChatInterface(self.chat_container)
                self.chat_interface.frame.pack(fill="both", expand=True)
                logger.info("Interface de chat IA créée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'interface de chat: {e}", exc_info=True)
                # Afficher un message d'erreur dans l'interface
                self.afficher_erreur(f"Impossible de charger l'interface de chat: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur lors de la création des widgets: {e}", exc_info=True)
            # Afficher un message d'erreur simple
            self.afficher_erreur(f"Erreur lors du chargement de l'onglet Chat AI: {str(e)}")
    
    def afficher_erreur(self, message):
        """Affiche un message d'erreur dans l'interface"""
        try:
            # Vider le cadre principal
            for widget in self.frame.winfo_children():
                widget.destroy()
                
            # Créer un conteneur pour le message d'erreur
            error_frame = ttk.Frame(self.frame, style="Error.TFrame")
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Créer une étiquette pour le message d'erreur
            error_label = ttk.Label(
                error_frame, 
                text=f"⚠️ {message}\n\nVérifiez que le service Ollama est installé et en cours d'exécution.", 
                style="Error.TLabel",
                wraplength=500,
                justify="center"
            )
            error_label.pack(pady=50)
            
            # Ajouter un bouton pour réessayer
            retry_button = ttk.Button(
                error_frame,
                text="Réessayer",
                command=self.recharger_interface
            )
            retry_button.pack(pady=10)
            
            # Ajouter un lien vers la documentation
            help_label = ttk.Label(
                error_frame,
                text="Aide: Comment installer Ollama",
                cursor="hand2",
                foreground="blue"
            )
            help_label.pack(pady=5)
            help_label.bind("<Button-1>", lambda e: self.ouvrir_aide())
            
            logger.info("Message d'erreur affiché")
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du message d'erreur: {e}", exc_info=True)
    
    def recharger_interface(self):
        """Recharge l'interface de chat"""
        try:
            # Supprimer tous les widgets existants
            for widget in self.frame.winfo_children():
                widget.destroy()
            
            # Recréer les widgets
            self.create_widgets()
            logger.info("Interface rechargée")
        except Exception as e:
            logger.error(f"Erreur lors du rechargement de l'interface: {e}", exc_info=True)
    
    def ouvrir_aide(self):
        """Ouvre la documentation d'aide pour installer Ollama"""
        webbrowser.open("https://ollama.com/download")
    
    def afficher_limitation_version_gratuite(self, message):
        """Affiche un message concernant les limitations de la version gratuite"""
        try:
            # Vider le cadre principal
            for widget in self.frame.winfo_children():
                widget.destroy()
            
            # Créer un cadre pour le message
            message_frame = ctk.CTkFrame(self.frame)
            message_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Icône de verrou (ou texte si pas d'image disponible)
            lock_label = ctk.CTkLabel(
                message_frame,
                text="🔒",  # Emoji verrou
                font=ctk.CTkFont(size=48)
            )
            lock_label.pack(pady=(30, 10))
            
            # Titre
            title_label = ctk.CTkLabel(
                message_frame,
                text="Fonctionnalité Premium",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.pack(pady=(10, 5))
            
            # Message
            info_label = ctk.CTkLabel(
                message_frame,
                text=message,
                font=ctk.CTkFont(size=14),
                wraplength=500,
                justify="center"
            )
            info_label.pack(pady=(5, 20))
            
            # Bouton pour activer une licence
            activate_button = ctk.CTkButton(
                message_frame,
                text="Activer une licence",
                command=self.ouvrir_activation_licence
            )
            activate_button.pack(pady=(0, 30))
            
            logger.info("Message de limitation de version gratuite affiché")
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du message de limitation: {e}", exc_info=True)
            # En cas d'erreur, afficher un message simple
            self.afficher_erreur(f"Version gratuite - Chat IA non disponible\n\n{message}")
    
    def ouvrir_activation_licence(self):
        """Ouvre la boîte de dialogue d'activation de licence"""
        try:
            # Accéder à la vue du compte si disponible
            if hasattr(self.model, 'main_view') and hasattr(self.model.main_view, 'show_account'):
                # Naviguer vers la vue Mon Compte
                self.model.main_view.show_account()
                logger.info("Navigation vers la vue Mon Compte pour activation de licence")
            else:
                logger.warning("Impossible de naviguer vers la vue Mon Compte")
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture de l'activation de licence: {e}", exc_info=True) 
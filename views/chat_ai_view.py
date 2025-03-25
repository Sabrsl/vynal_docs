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
            # Afficher un indicateur de chargement
            self._show_loading_indicator()
            
            # Essayer d'accéder directement à la vue des paramètres avec un délai minimal
            self.frame.after(50, self._try_open_license_dialog)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture de l'activation de licence: {e}", exc_info=True)
            # En cas d'erreur, afficher un message à l'utilisateur
            try:
                from CTkMessagebox import CTkMessagebox
                CTkMessagebox(
                    title="Activation de licence",
                    message="Une erreur s'est produite. Veuillez réessayer.",
                    icon="info"
                )
            except Exception:
                logger.error("Impossible d'afficher le message d'information")
    
    def _show_loading_indicator(self):
        """Affiche un indicateur de chargement temporaire"""
        try:
            # Désactiver temporairement le bouton d'activation pour éviter les doubles clics
            for widget in self.frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for subwidget in widget.winfo_children():
                        if isinstance(subwidget, ctk.CTkButton) and subwidget.cget("text") == "Activer une licence":
                            subwidget.configure(state="disabled", text="Chargement...")
                            break
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de l'indicateur de chargement: {e}")
    
    def _try_open_license_dialog(self):
        """Tente d'ouvrir la boîte de dialogue de licence avec différentes méthodes"""
        # Réactiver le bouton en cas d'échec
        def restore_button():
            try:
                for widget in self.frame.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for subwidget in widget.winfo_children():
                            if isinstance(subwidget, ctk.CTkButton) and subwidget.cget("text") == "Chargement...":
                                subwidget.configure(state="normal", text="Activer une licence")
                                break
            except Exception:
                pass
        
        try:
            # Méthode 1: Accéder à la vue des paramètres et ouvrir la gestion des licences
            if hasattr(self.model, 'settings_view') and self.model.settings_view:
                if hasattr(self.model.settings_view, 'show_license_management'):
                    self.model.settings_view.show_license_management()
                    logger.info("Ouverture de la gestion des licences depuis la vue des paramètres")
                    return
            
            # Méthode 2: Utiliser la vue principale
            if hasattr(self.model, 'main_view'):
                main_view = self.model.main_view
                # Vérifier si la vue principale a une vue des paramètres
                if hasattr(main_view, 'settings_view') and main_view.settings_view:
                    if hasattr(main_view.settings_view, 'show_license_management'):
                        main_view.settings_view.show_license_management()
                        logger.info("Ouverture de la gestion des licences depuis la vue principale")
                        return
                
                # Méthode 3: Ouvrir les paramètres
                if hasattr(main_view, 'show_settings'):
                    main_view.show_settings()
                    logger.info("Navigation vers les paramètres pour activation de licence")
                    return
            
            # Méthode 4 (en dernier recours): Créer notre propre boîte de dialogue
            restore_button()  # Restaurer le bouton avant de créer la boîte de dialogue
            self._create_license_activation_dialog()
            logger.info("Création directe d'une boîte de dialogue d'activation de licence")
            
        except Exception as e:
            logger.error(f"Erreur lors de la tentative d'ouverture de licence: {e}", exc_info=True)
            restore_button()
            # Afficher un message d'erreur
            try:
                from CTkMessagebox import CTkMessagebox
                CTkMessagebox(
                    title="Activation de licence",
                    message="Impossible d'ouvrir le gestionnaire de licences. Veuillez réessayer.",
                    icon="warning"
                )
            except Exception:
                logger.error("Impossible d'afficher le message d'erreur")
    
    def _create_license_activation_dialog(self):
        """Crée une boîte de dialogue simple pour l'activation de licence"""
        try:
            from CTkMessagebox import CTkMessagebox
            
            # Créer la fenêtre de dialogue avec des paramètres optimisés
            dialog = ctk.CTkToplevel(self.frame)
            dialog.title("Activation de licence")
            dialog.geometry("480x360")  # Légèrement plus petite pour un chargement plus rapide
            dialog.attributes("-topmost", True)  # Garder au premier plan
            dialog.resizable(True, True)
            dialog.minsize(400, 360)
            
            # Cadre principal sans défilement pour éviter les problèmes de performance
            main_frame = ctk.CTkFrame(dialog)
            main_frame.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Titre
            title_label = ctk.CTkLabel(
                main_frame,
                text="Activer une licence",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.pack(pady=(5, 15))
            
            # Vérifier si l'utilisateur est connecté
            user_email = ""
            user_registered = False
            
            if hasattr(self.model, 'current_user') and self.model.current_user:
                user_email = self.model.current_user.get('email', '')
                user_registered = bool(user_email)
            
            # Formulaire simplifié
            form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            form_frame.pack(fill="x", padx=10, pady=10)
            
            # Email
            email_label = ctk.CTkLabel(form_frame, text="Email :", anchor="w")
            email_label.pack(anchor="w", pady=(5, 0))
            
            email_var = ctk.StringVar(value=user_email)
            email_entry = ctk.CTkEntry(
                form_frame, 
                textvariable=email_var,
                state="disabled" if user_registered else "normal",
                fg_color=("#D3D3D3", "#4A4A4A") if user_registered else None
            )
            email_entry.pack(fill="x", pady=(0, 10))
            
            # Clé de licence
            key_label = ctk.CTkLabel(form_frame, text="Clé de licence :", anchor="w")
            key_label.pack(anchor="w", pady=(5, 0))
            
            key_var = ctk.StringVar()
            key_entry = ctk.CTkEntry(form_frame, textvariable=key_var)
            key_entry.pack(fill="x", pady=(0, 10))
            
            # Message informatif
            info_text = "La licence sera activée pour votre compte." if user_registered else "L'activation créera un compte avec l'email fourni."
            
            # Cadre pour le message informatif (avec fond de couleur)
            info_frame = ctk.CTkFrame(form_frame, fg_color=("gray95", "gray10"), corner_radius=6)
            info_frame.pack(fill="x", pady=10)
            
            info_label = ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray45"),
                wraplength=350,  # Valeur initiale qui sera ajustée
                justify="left"
            )
            info_label.pack(padx=10, pady=10)
            
            # Mettre à jour la largeur du texte lorsque la fenêtre change de taille
            def update_wraplength(event):
                new_width = info_frame.winfo_width() - 20  # 20 pixels de marge
                if new_width > 50:  # Éviter les valeurs négatives ou trop petites
                    info_label.configure(wraplength=new_width)
            
            # Lier l'événement de redimensionnement
            info_frame.bind("<Configure>", update_wraplength)
            
            # Fonction d'activation
            def activate_license():
                license_key = key_var.get().strip()
                email = email_var.get().strip()
                
                # Validation basique
                if not license_key:
                    CTkMessagebox(title="Erreur", message="Veuillez entrer une clé de licence.", icon="warning")
                    return
                
                if not user_registered and not email:
                    CTkMessagebox(title="Erreur", message="Veuillez entrer un email valide.", icon="warning")
                    return
                
                # Désactiver les boutons pendant le traitement
                cancel_btn.configure(state="disabled")
                activate_btn.configure(state="disabled", text="Traitement...")
                
                # Traiter l'activation
                dialog.after(100, lambda: self._process_license_activation(dialog, email if not user_registered else user_email, license_key))
            
            # Boutons placés directement sous le cadre informatif
            button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            button_frame.pack(pady=(15, 0))
            
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="Annuler",
                command=dialog.destroy,
                width=115,
                height=32
            )
            cancel_btn.pack(side="left", padx=5)
            
            activate_btn = ctk.CTkButton(
                button_frame,
                text="Activer",
                command=activate_license,
                width=115,
                height=32,
                fg_color="#2ecc71",
                hover_color="#27ae60"
            )
            activate_btn.pack(side="left", padx=5)
            
            # Centrer la fenêtre après avoir défini les widgets
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Donner le focus à l'entrée qui peut être modifiée
            if not user_registered:
                email_entry.focus_set()
            else:
                key_entry.focus_set()
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la boîte de dialogue: {e}", exc_info=True)
    
    def _process_license_activation(self, dialog, email, license_key):
        """Traite l'activation de licence de manière asynchrone"""
        try:
            from CTkMessagebox import CTkMessagebox
            
            # Vérifier que le modèle de licence existe
            if not hasattr(self.model, 'license_model') or not self.model.license_model:
                CTkMessagebox(
                    title="Erreur",
                    message="Le modèle de licence n'est pas disponible.",
                    icon="cancel"
                )
                dialog.destroy()
                return
            
            # Si l'utilisateur n'est pas inscrit, créer un compte
            user_registered = bool(self.model.current_user and self.model.current_user.get('email'))
            if not user_registered:
                success_registration = self._register_new_user(email)
                if not success_registration:
                    CTkMessagebox(
                        title="Erreur",
                        message="Impossible de créer un compte avec cet email.",
                        icon="cancel"
                    )
                    dialog.destroy()
                    return
            
            # Activer la licence
            success, message = self.model.license_model.activate_license(email, license_key)
            
            if success:
                CTkMessagebox(
                    title="Succès",
                    message="Licence activée avec succès. L'application va être rechargée.",
                    icon="check"
                )
                dialog.destroy()
                # Recharger l'interface après activation
                self.frame.after(500, self.recharger_interface)
            else:
                CTkMessagebox(
                    title="Erreur",
                    message=f"Impossible d'activer la licence: {message}",
                    icon="cancel"
                )
                dialog.destroy()
                
        except Exception as e:
            logger.error(f"Erreur lors de l'activation: {e}", exc_info=True)
            CTkMessagebox(
                title="Erreur",
                message="Une erreur s'est produite lors de l'activation de la licence.",
                icon="cancel"
            )
            dialog.destroy()
    
    def _register_new_user(self, email):
        """Inscrit un nouvel utilisateur avec l'email fourni
        
        Args:
            email: Adresse email du nouvel utilisateur
            
        Returns:
            bool: True si l'inscription a réussi, False sinon
        """
        try:
            if not hasattr(self.model, 'register_user'):
                # Si la méthode n'existe pas directement, chercher dans d'autres objets
                if hasattr(self.model, 'main_view') and hasattr(self.model.main_view, 'register_user'):
                    register_method = self.model.main_view.register_user
                elif hasattr(self.model, 'auth_model') and hasattr(self.model.auth_model, 'register_user'):
                    register_method = self.model.auth_model.register_user
                else:
                    # Si pas de méthode d'inscription trouvée, utiliser le modèle d'usage
                    from utils.usage_tracker import UsageTracker
                    usage_tracker = UsageTracker()
                    # Créer des données utilisateur simples
                    user_data = {
                        "email": email,
                        "created_at": self.model.get_current_time_iso() if hasattr(self.model, 'get_current_time_iso') else None,
                        "is_registered": True
                    }
                    usage_tracker.save_user_data(user_data)
                    return True
            else:
                register_method = self.model.register_user
            
            # Appeler la méthode d'inscription
            result = register_method(email=email, password="", auto_generated=True)
            
            if isinstance(result, tuple):
                return result[0]  # Supposons que le premier élément est un booléen indiquant le succès
            return bool(result)  # Sinon, convertir le résultat en booléen
            
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription d'un nouvel utilisateur: {e}")
            return False 
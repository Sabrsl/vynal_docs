#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue principale de l'application Vynal Docs Automator
"""

import os
import logging
import customtkinter as ctk
from PIL import Image, ImageTk
import json
import tkinter as tk
import hashlib
from datetime import datetime
import tkinter.messagebox as messagebox
from CTkMessagebox import CTkMessagebox
import traceback
import time

# Importation des vues
from views.dashboard_view import DashboardView
from views.client_view import ClientView
from views.document_view import DocumentView
from views.template_view import TemplateView
from views.settings_view import SettingsView
from views.chat_ai_view import ChatAIView

# Importer le moniteur d'activité
from utils.activity_monitor import ActivityMonitor

logger = logging.getLogger("VynalDocsAutomator.MainView")

class MainView:
    """
    Vue principale de l'application
    Gère l'interface utilisateur globale et la navigation entre les différentes vues
    """
    
    def __init__(self, root, app_model, on_ready=None):
        """
        Initialiser la vue principale
        
        Args:
            root: Fenêtre principale
            app_model: Modèle de l'application
            on_ready: Callback à appeler lorsque l'interface est prête
        """
        # Initialiser les attributs de base
        self.root = root
        self.model = app_model
        self.on_ready = on_ready
        
        # Si c'est une réinitialisation, nettoyer d'abord les widgets existants
        if hasattr(self, 'main_frame') and self.main_frame:
            try:
                self.main_frame.destroy()
            except Exception:
                pass  # Ignorer les erreurs de suppression
        
        # Nettoyer les autres widgets potentiellement existants
        for attr_name in ['sidebar', 'content_area', 'main_content']:
            if hasattr(self, attr_name):
                try:
                    widget = getattr(self, attr_name)
                    if widget:
                        widget.destroy()
                except Exception:
                    pass  # Ignorer les erreurs
        
        # Initialiser le gestionnaire d'utilisation
        from utils.usage_tracker import UsageTracker
        self.usage_tracker = UsageTracker()
        
        # Vérifier s'il existe une session "rester connecté"
        remembered_user = self.usage_tracker.check_remembered_session()
        if remembered_user:
            logger.info(f"Session 'Rester connecté' trouvée pour {remembered_user.get('email', 'utilisateur inconnu')}")
            # Connexion automatique si une session valide existe
            self.auto_login_data = remembered_user
        else:
            self.auto_login_data = None
        
        # Configurer la fenêtre principale
        self.root.title(self.model.config.get("app.name", "Vynal Docs Automator"))
        
        # Récupérer le thème des préférences utilisateur ou de la configuration globale
        user_theme = None
        if self.usage_tracker.is_user_registered():
            try:
                user_data = self.usage_tracker.get_user_data()
                if isinstance(user_data, dict) and "theme" in user_data:
                    user_theme = user_data["theme"].lower()
            except Exception as e:
                logger.warning(f"Erreur lors de la lecture des préférences utilisateur: {e}")
        
        # Utiliser le thème utilisateur ou la configuration globale
        theme = user_theme if user_theme else self.model.config.get("app.theme", "dark").lower()
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # Créer le cadre principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Initialiser les dictionnaires de widgets
        self.views = {}
        self.nav_buttons = {}
        self.sidebar_items = []
        
        # Moniteur d'activité
        self.activity_monitor = {
            "enabled": False,
            "timeout": 300,  # 5 minutes par défaut
            "last_activity": time.time(),
            "timer_id": None
        }
        
        # Créer l'interface
        self._create_widgets()
        
        # Initialiser le moniteur d'activité
        self._setup_activity_monitor()
        
        # Configurer les événements pour détecter l'activité
        self._setup_activity_events()
        
        logger.info("Vue principale initialisée")
        
        # Exécuter après l'initialisation
        if on_ready:
            on_ready()
            
        # Si une session "rester connecté" a été trouvée, afficher directement le tableau de bord
        if self.auto_login_data:
            self.root.after(100, lambda: self._perform_auto_login(self.auto_login_data))
    
    def _perform_auto_login(self, user_data):
        """
        Effectue la connexion automatique avec les données utilisateur
        
        Args:
            user_data: Données de l'utilisateur
        """
        try:
            # Créer un écran de chargement
            loading_frame = ctk.CTkFrame(self.root)
            loading_frame.pack(fill=ctk.BOTH, expand=True)

            # Frame centré pour le contenu du spinner
            spinner_content = ctk.CTkFrame(loading_frame, fg_color="transparent")
            spinner_content.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

            # Titre
            ctk.CTkLabel(
                spinner_content,
                text="Connexion automatique",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("gray10", "gray90")
            ).pack(pady=(0, 20))

            # Message de chargement
            name = user_data.get('name', '')
            email = user_data.get('email', '')
            greeting = f"Bienvenue {name}" if name else f"Bienvenue {email}"
            
            loading_label = ctk.CTkLabel(
                spinner_content,
                text=f"{greeting} ! Veuillez patienter pendant le chargement du tableau de bord...",
                font=ctk.CTkFont(size=14)
            )
            loading_label.pack(pady=(0, 15))

            # Créer un spinner avec CustomTkinter
            spinner = ctk.CTkProgressBar(spinner_content, width=300)
            spinner.pack(pady=10)
            spinner.configure(mode="indeterminate")
            spinner.start()

            # Force le rafraîchissement pour afficher le spinner
            self.root.update()
            
            def complete_auto_login():
                try:
                    # Stocker une référence au loading_frame
                    global spinner_reference
                    spinner_reference = loading_frame
                    
                    # Mettre à jour l'état d'authentification
                    self._update_auth_state()
                    
                    # Afficher le dashboard
                    self.show_dashboard()
                    
                    # Détruire le spinner après un court délai
                    self.root.after(800, lambda: self._destroy_spinner_safely(spinner_reference))
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la connexion automatique: {e}", exc_info=True)
                    # En cas d'erreur, nettoyer et afficher un message
                    try:
                        if loading_frame and loading_frame.winfo_exists():
                            loading_frame.destroy()
                    except Exception:
                        pass
                    
                    from utils.notification import show_notification
                    show_notification(
                        "Erreur de connexion",
                        "Impossible de restaurer votre session. Veuillez vous reconnecter.",
                        "error"
                    )
                    
                    # Afficher l'écran de connexion
                    self.show_login()
            
            # Lancer le processus après un court délai
            self.root.after(1000, complete_auto_login)
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de la connexion automatique: {e}", exc_info=True)
            # Afficher l'écran de connexion en cas d'erreur
            self.show_login()
    
    def _create_widgets(self):
        """
        Crée la barre latérale et le contenu principal
        """
        # Créer la barre latérale et le contenu principal
        try:
            self.create_sidebar()
            self.create_content_area()
            
            # Créer les différentes vues
            self.create_views()
            
            # Afficher la vue par défaut (tableau de bord)
            self.show_view("dashboard")
            
            logger.info("Vue dashboard affichée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la vue principale: {e}")
            # Afficher un message d'erreur à l'utilisateur
            self.root.after(100, lambda: self.show_message(
                "Erreur d'initialisation", 
                f"Une erreur est survenue lors de l'initialisation de l'application: {e}",
                "error"
            ))

    def create_sidebar(self):
        """
        Crée la barre latérale avec le menu de navigation
        """
        # Cadre de la barre latérale
        self.sidebar = ctk.CTkFrame(self.main_frame, width=200, corner_radius=0)
        self.sidebar.pack(side=ctk.LEFT, fill=ctk.Y, padx=0, pady=0)
        self.sidebar.pack_propagate(False)  # Empêcher le redimensionnement
        
        # Logo et titre
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(side=ctk.TOP, fill=ctk.X, padx=20, pady=20)
        
        # Charger le logo s'il existe
        logo_path = self.model.config.get("app.company_logo", "")
        try:
            # Utiliser l'image du logo si elle existe, sinon créer un placeholder
            if logo_path and os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((150, 70), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                
                self.logo_label = ctk.CTkLabel(self.logo_frame, image=logo_photo, text="")
                self.logo_label.image = logo_photo  # Garder une référence
                self.logo_label.pack(side=ctk.TOP, pady=5)
            else:
                # Créer une image de placeholder
                logger.info("Logo non trouvé, utilisation d'un texte à la place")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du logo: {e}")
        
        # Titre de l'application en dégradé visuel très subtil
        self.title_label = ctk.CTkLabel(
            self.logo_frame, 
            text="Vynal Docs",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="normal"),  # Plus petit et normal
            text_color=("gray65", "gray75")  # Couleur encore plus subtile
        )
        self.title_label.pack(side=ctk.TOP, pady=(3, 0))  # Espacement minimal

        # Version intégrée avec dégradé subtil
        version_text = f"Version {self.model.config.get('app.version', '1.0.0')}"
        ctk.CTkLabel(
            self.logo_frame,
            text=version_text,
            font=ctk.CTkFont(family="Helvetica", size=7),  # Encore plus petit
            text_color=("gray55", "gray65")  # Couleur encore plus subtile
        ).pack(side=ctk.TOP, pady=(0, 3))  # Espacement minimal
        
        # Séparateur
        ctk.CTkFrame(self.sidebar, height=1, fg_color="gray").pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=5)
        
        # Boutons de navigation
        
        # Cadre pour les boutons
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Définition des boutons du menu
        nav_items = [
            {"id": "dashboard", "text": "Tableau de bord", "icon": "📊"},
            {"id": "clients", "text": "Clients", "icon": "👥"},
            {"id": "templates", "text": "Modèles", "icon": "📋"},
            {"id": "documents", "text": "Documents", "icon": "📄"},
            {"id": "analysis", "text": "Chat IA", "icon": "🤖"},
            {"id": "settings", "text": "Paramètres", "icon": "⚙️"}
        ]
        
        # Créer les boutons
        for item in nav_items:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"{item['icon']} {item['text']}",
                anchor="w",
                height=40,
                corner_radius=10,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda i=item["id"]: self.show_view(i)
            )
            btn.pack(side=ctk.TOP, fill=ctk.X, padx=5, pady=2)
            self.nav_buttons[item["id"]] = btn
        
        # Informations en bas de la barre latérale
        self.sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_footer.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=10)
        
        # Toolbar pour les boutons supplémentaires
        self.toolbar = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.toolbar.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=5)
        
        # Version de l'application
        ctk.CTkLabel(
            self.sidebar_footer,
            text=f"Version {self.model.config.get('app.version', '1.0.0')}",
            font=ctk.CTkFont(size=10)
        ).pack(side=ctk.TOP, pady=2)
        
        # Copyright
        ctk.CTkLabel(
            self.sidebar_footer,
            text=f"© {self.model.config.get('app.company_name', 'Vynal Agency LTD')}",
            font=ctk.CTkFont(size=10)
        ).pack(side=ctk.TOP, pady=2)
        
        # Bouton Mon compte
        # Vérifier l'état de connexion
        is_logged_in = self.usage_tracker.is_user_registered()
        
        # Créer le bouton principal selon l'état de connexion
        if is_logged_in:
            # Utilisateur connecté - afficher son nom
            user_data = self.usage_tracker.get_user_data()
            display_name = user_data.get('email', 'Utilisateur').split('@')[0]
            button_text = f"👤 {display_name}"
            button_color = "#3498db"
            hover_color = "#2980b9"
        else:
            # Utilisateur non connecté - afficher "Se connecter"
            button_text = "👤 Se connecter"
            button_color = "#2ecc71"
            hover_color = "#27ae60"
        
        # Créer le bouton principal
        auth_button = ctk.CTkButton(
            self.sidebar_footer,
            text=button_text,
            command=self._show_auth_dialog,
            fg_color=button_color,
            hover_color=hover_color
        )
        auth_button.pack(side=ctk.TOP, fill=ctk.X, pady=5)
        self.auth_button = auth_button
        
        # Nous n'ajoutons pas les boutons supplémentaires ici
        # Ils seront ajoutés par update_auth_button
        self.update_auth_button()

    def create_content_area(self):
        """
        Crée la zone de contenu principal
        """
        try:
            # Cadre pour le contenu
            self.content_area = ctk.CTkFrame(self.main_frame)
            self.content_area.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=0, pady=0)
            
            # En-tête du contenu
            self.content_header = ctk.CTkFrame(self.content_area, height=60, fg_color=("gray90", "gray20"))
            self.content_header.pack(side=ctk.TOP, fill=ctk.X, padx=0, pady=0)
            self.content_header.pack_propagate(False)  # Empêcher le redimensionnement
            
            # Titre de la page
            self.page_title = ctk.CTkLabel(
                self.content_header,
                text="Tableau de bord",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            self.page_title.pack(side=ctk.LEFT, padx=20, pady=10)
            
            # Barre d'état
            self.status_bar = ctk.CTkFrame(
                self.content_area,
                height=25,
                fg_color=("#DBDBDB", "#2B2B2B")  # Gris clair pour le mode clair, gris foncé pour le mode sombre
            )
            self.status_bar.pack(side=ctk.BOTTOM, fill=ctk.X)
            
            # Label de statut
            self.status_label = ctk.CTkLabel(
                self.status_bar,
                text="Prêt",
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=("gray10", "gray90")  # Texte foncé pour le mode clair, clair pour le mode sombre
            )
            self.status_label.pack(side=ctk.LEFT, padx=10, pady=2)
            
            # Cadre principal pour les différentes vues
            self.main_content = ctk.CTkFrame(self.content_area, fg_color="transparent")
            self.main_content.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            logger.debug("Zone de contenu créée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la création de la zone de contenu: {e}")
            # Créer une structure minimale en cas d'erreur
            self.content_area = ctk.CTkFrame(self.main_frame)
            self.content_area.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
            self.main_content = ctk.CTkFrame(self.content_area)
            self.main_content.pack(fill=ctk.BOTH, expand=True)
    
    def create_views(self):
        """
        Crée les différentes vues de l'application
        """
        try:
            # Initialiser le dictionnaire des vues s'il n'existe pas
            if not hasattr(self, 'views'):
                self.views = {}
            
            # Créer les vues dans le bon conteneur
            view_classes = {
                "dashboard": DashboardView,
                "clients": ClientView,
                "templates": TemplateView,
                "documents": DocumentView,
                "analysis": ChatAIView,
                "settings": SettingsView
            }
            
            # Importer document_creator_view si nécessaire
            try:
                from views.document_creator_view import DocumentCreatorView
                view_classes["document_creator"] = DocumentCreatorView
                logger.info("DocumentCreatorView importée dans les classes de vues disponibles")
            except Exception as e:
                logger.warning(f"Impossible d'importer DocumentCreatorView: {e}")
            
            # Créer chaque vue individuellement avec gestion des erreurs
            for view_id, view_class in view_classes.items():
                try:
                    if view_id not in self.views:
                        self.views[view_id] = view_class(self.main_content, self.model)
                        logger.info(f"Vue {view_id} créée avec succès")
                except Exception as e:
                    logger.error(f"Erreur lors de la création de la vue {view_id}: {e}")
            
            # S'assurer que toutes les vues sont initialement cachées
            for view_id, view in self.views.items():
                try:
                    if hasattr(view, 'hide'):
                        view.hide()
                        logger.debug(f"Vue {view_id} masquée")
                except Exception as e:
                    logger.error(f"Erreur lors du masquage de la vue {view_id}: {e}")
            
            logger.info("Toutes les vues ont été initialisées")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des vues: {e}")
            # Créer une structure minimale pour éviter les erreurs fatales
            if "dashboard" not in self.views:
                self.views["dashboard"] = DashboardView(self.main_content, self.model)
                logger.info("Vue dashboard créée comme fallback")
    
    def show_view(self, view_id):
        """
        Affiche une vue spécifique et masque les autres
        
        Args:
            view_id: Identifiant de la vue à afficher
        """
        # Vérifier si la vue existe, sinon tenter de la créer
        if view_id not in self.views:
            try:
                view_classes = {
                    "dashboard": DashboardView,
                    "clients": ClientView,
                    "templates": TemplateView,
                    "documents": DocumentView,
                    "analysis": ChatAIView,
                    "settings": SettingsView
                }
                # Ajouter DocumentCreatorView si elle n'est pas déjà là
                if "document_creator" not in view_classes and view_id == "document_creator":
                    try:
                        from views.document_creator_view import DocumentCreatorView
                        view_classes["document_creator"] = DocumentCreatorView
                    except Exception as e:
                        logger.error(f"Erreur d'importation de DocumentCreatorView: {e}")
                
                if view_id in view_classes:
                    self.views[view_id] = view_classes[view_id](self.main_content, self.model)
                    logger.info(f"Vue {view_id} créée avec succès")
                else:
                    logger.error(f"Vue {view_id} non trouvée et impossible à créer")
                    return
            except Exception as e:
                logger.error(f"Erreur lors de la création de la vue {view_id}: {e}")
                return
        
        # Mettre à jour le titre de la page
        titles = {
            "dashboard": "Tableau de bord",
            "clients": "Gestion des clients",
            "templates": "Modèles de documents",
            "documents": "Documents",
            "analysis": "Chat IA",
            "settings": "Paramètres",
            "document_creator": "Création de document"
        }
        
        self.page_title.configure(text=titles.get(view_id, view_id.capitalize()))
        
        # Masquer toutes les vues
        for _id, view in self.views.items():
            view.hide()
        
        # Mettre en évidence le bouton actif
        for btn_id, button in self.nav_buttons.items():
            if btn_id == view_id:
                button.configure(fg_color=("gray85", "gray25"))
            else:
                button.configure(fg_color="transparent")
        
        # Si c'est la vue des paramètres, force une mise à jour complète
        if view_id == "settings":
            # Pour la vue des paramètres, toujours mettre à jour avant d'afficher
            self.views[view_id].update_view()
            
            # Mettre à jour l'état du bouton d'authentification au cas où
            self.update_auth_button()
        
        # Afficher la vue sélectionnée
        self.views[view_id].show()
        
        logger.info(f"Vue {view_id} affichée")
    
    def show_message(self, title, message, message_type="info"):
        """
        Affiche une boîte de dialogue avec un message
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message à afficher
            message_type: Type de message ('info', 'error', 'warning')
        """
        if message_type == "error":
            icon = "❌"
        elif message_type == "warning":
            icon = "⚠️"
        else:
            icon = "ℹ️"
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.lift()  # Mettre au premier plan
        dialog.focus_force()  # Donner le focus
        dialog.grab_set()  # Modal
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Message
        msg_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        msg_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            msg_frame,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            msg_frame,
            text=message,
            wraplength=360
        ).pack(pady=10)
        
        # Bouton OK
        ctk.CTkButton(
            msg_frame,
            text="OK",
            width=100,
            command=dialog.destroy
        ).pack(pady=10)
    
    def show_confirmation(self, title, message, on_yes, on_no=None):
        """
        Affiche une boîte de dialogue de confirmation
        
        Args:
            title: Titre de la boîte de dialogue
            message: Message à afficher
            on_yes: Fonction à appeler si l'utilisateur confirme
            on_no: Fonction à appeler si l'utilisateur annule
        """
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Message
        msg_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        msg_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            msg_frame,
            text=f"⚠️ {title}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            msg_frame,
            text=message,
            wraplength=360
        ).pack(pady=10)
        
        # Boutons
        btn_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def yes_action():
            dialog.destroy()
            if on_yes:
                on_yes()
        
        def no_action():
            dialog.destroy()
            if on_no:
                on_no()
        
        ctk.CTkButton(
            btn_frame,
            text="Oui",
            width=100,
            fg_color="green",
            command=yes_action
        ).pack(side=ctk.LEFT, padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Non",
            width=100,
            fg_color="red",
            command=no_action
        ).pack(side=ctk.LEFT, padx=10)
    
    def update_view(self):
        """
        Méthode générique pour mettre à jour la vue principale
        """
        # Mettre à jour le titre de l'application
        self.root.title(self.model.config.get("app.name", "Vynal Docs Automator"))
        
        # Mettre à jour le thème
        theme = self.model.config.get("app.theme", "dark").lower()
        ctk.set_appearance_mode(theme)

    def _show_auth_dialog(self):
        """Affiche la fenêtre d'authentification"""
        try:
            # Créer la vue d'authentification si elle n'existe pas
            if not hasattr(self, 'auth_view'):
                from views.auth_view import AuthView
                self.auth_view = AuthView(self.root, self.usage_tracker)
                self.auth_view.set_auth_callback(self._on_auth_change)
            
            # Vérifier si l'utilisateur est connecté
            is_logged_in = self.usage_tracker.is_user_registered()
            
            # Afficher la vue d'authentification
            self.auth_view.show()
            
            # Afficher l'onglet approprié
            if is_logged_in:
                self.auth_view._show_tab("account")
            else:
                self.auth_view._show_tab("login")
                
            logger.info("Fenêtre d'authentification affichée")
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la fenêtre d'authentification: {e}")
            self.show_message(
                "Erreur",
                "Une erreur est survenue lors de l'affichage de la fenêtre d'authentification.",
                "error"
            )

    def _on_auth_change(self, is_logged_in=None, user_data=None):
        """
        Callback appelé lorsque l'état d'authentification change
        
        Args:
            is_logged_in (bool, optional): True si l'utilisateur est connecté, False sinon
            user_data (dict, optional): Données de l'utilisateur si connecté, None sinon
        """
        try:
            # Si les paramètres ne sont pas fournis, les récupérer de l'usage tracker
            if is_logged_in is None:
                is_logged_in = self.usage_tracker.has_active_user()
                
            if user_data is None and is_logged_in:
                user_data = self.usage_tracker.get_user_data()
                
            # Mettre à jour l'interface utilisateur
            self.update_auth_button(is_logged_in)
            
            # Afficher un message approprié
            if is_logged_in:
                self.show_message(
                    "Connexion réussie",
                    f"Bienvenue {user_data.get('name', 'utilisateur')} !",
                    "success"
                )
            else:
                self.show_message(
                    "Déconnexion",
                    "Vous avez été déconnecté avec succès.",
                    "info"
                )
                
            logger.info(f"État d'authentification mis à jour - Connecté: {is_logged_in}")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'état d'authentification: {e}")
            
    def update_auth_button(self, is_logged_in=None):
        """
        Met à jour l'interface utilisateur selon l'état d'authentification
        
        Args:
            is_logged_in (bool, optional): État de connexion. Si None, il sera déterminé automatiquement.
        """
        if not hasattr(self, 'usage_tracker'):
            from utils.usage_tracker import UsageTracker
            self.usage_tracker = UsageTracker()
        
        # Si l'état de connexion n'est pas fourni, le déterminer
        if is_logged_in is None:
            is_logged_in = self.usage_tracker.has_active_user()
        
        # Mettre à jour le texte et la couleur des boutons selon l'état de connexion
        if is_logged_in:
            button_text = "👤 Mon compte"
            button_color = ("gray75", "gray25")  # Couleur plus subtile
            hover_color = ("gray85", "gray15")
        else:
            button_text = "🔑 Se connecter"
            button_color = "#4285F4"  # Bleu Google
            hover_color = "#3367D6"  # Bleu plus foncé au survol
        
        # Appliquer les modifications au bouton si disponible
        if hasattr(self, 'auth_button') and self.auth_button:
            try:
                self.auth_button.configure(
                    text=button_text,
                    fg_color=button_color,
                    hover_color=hover_color
                )
            except Exception as e:
                logger.warning(f"Erreur lors de la mise à jour du bouton d'authentification: {e}")
        
        # Nettoyer tous les boutons existants dans la barre latérale
        try:
            if hasattr(self, 'sidebar_footer') and self.sidebar_footer:
                # Supprimer tous les widgets enfants sauf le bouton principal
                for widget in list(self.sidebar_footer.winfo_children()):
                    if widget != self.auth_button:
                        try:
                            widget.destroy()
                        except Exception as e:
                            logger.warning(f"Erreur lors de la suppression d'un widget: {e}")
            
            # Supprimer les références aux boutons
            for btn_name in ['logout_button', 'register_button', 'login_button']:
                if hasattr(self, btn_name):
                    delattr(self, btn_name)
            
            # Ajouter les boutons appropriés selon l'état de connexion
            if hasattr(self, 'sidebar_footer') and self.sidebar_footer:
                if is_logged_in:
                    # Utilisateur connecté - ajouter le bouton de déconnexion
                    logout_button = ctk.CTkButton(
                        self.sidebar_footer,
                        text="🔒 Déconnexion",
                        command=self._handle_logout,
                        fg_color="transparent",
                        hover_color=("gray85", "gray25"),
                        anchor="w"
                    )
                    logout_button.pack(side=ctk.TOP, fill=ctk.X, pady=5)
                    self.logout_button = logout_button
                else:
                    # Utilisateur non connecté - ajouter les boutons d'inscription et de connexion
                    register_button = ctk.CTkButton(
                        self.sidebar_footer,
                        text="✏️ S'inscrire",
                        command=self._show_register_view,
                        fg_color="transparent",
                        hover_color=("gray85", "gray25"),
                        anchor="w"
                    )
                    register_button.pack(side=ctk.TOP, fill=ctk.X, pady=5)
                    self.register_button = register_button
                    
                    login_button = ctk.CTkButton(
                        self.sidebar_footer,
                        text="🔑 Se connecter",
                        command=lambda: self._show_auth_dialog_tab("login"),
                        fg_color="transparent",
                        hover_color=("gray85", "gray25"),
                        anchor="w"
                    )
                    login_button.pack(side=ctk.TOP, fill=ctk.X, pady=5)
                    self.login_button = login_button
        except Exception as e:
            logger.warning(f"Erreur lors de la mise à jour des boutons d'authentification: {e}")
        
        # Mettre à jour l'interface de la vue principale
        self.update_view()
        
        # Journaliser le changement d'état
        logger.info(f"État d'authentification mis à jour - Connecté: {is_logged_in}")

    def _handle_logout(self):
        """
        Gère l'action de déconnexion de l'utilisateur
        """
        try:
            # Demander confirmation
            self.show_confirmation(
                "Déconnexion",
                "Êtes-vous sûr de vouloir vous déconnecter ?",
                on_yes=self._confirm_logout
            )
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            self.show_message("Erreur", f"Une erreur est survenue lors de la déconnexion: {e}", "error")
    
    def _confirm_logout(self):
        """Confirme la déconnexion et effectue le processus de logout"""
        logger.info("Confirmation de déconnexion")
        try:
            # Tenter de déconnecter l'utilisateur
            if self.usage_tracker.logout():
                logger.info("Déconnexion réussie")
                # Notifier le changement d'état d'authentification
                self._on_auth_change(False)
                
                # Nettoyer l'interface actuelle
                try:
                    # S'assurer que les vues actuelles sont masquées
                    if hasattr(self, 'views'):
                        for view_id, view in self.views.items():
                            if hasattr(view, 'pack_forget'):
                                view.pack_forget()
                                
                    # Masquer tous les widgets de l'interface principale
                    if hasattr(self, 'main_frame'):
                        for widget in self.main_frame.winfo_children():
                            widget.pack_forget()
                            
                    # Réafficher les widgets de base
                    if hasattr(self, 'main_frame') and not self.main_frame.winfo_ismapped():
                        self.main_frame.pack(fill=ctk.BOTH, expand=True)
                        
                    # Forcer la mise à jour de l'interface
                    self.root.update_idletasks()
                except Exception as e:
                    logger.error(f"Erreur lors du nettoyage de l'interface: {e}")
                
                # Afficher la vue de connexion standard
                self.show_login()
                
            else:
                logger.warning("Échec de la déconnexion")
                messagebox.showwarning("Erreur", "Impossible de se déconnecter.")
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            messagebox.showerror("Erreur", f"Une erreur est survenue: {e}")
    
    def _show_register_view(self):
        """Affiche la vue d'inscription"""
        # Importer ici pour éviter les imports circulaires
        from views.register_view import RegisterView
        
        # Créer une fenêtre modale pour l'inscription
        register_window = ctk.CTkToplevel(self.root)
        register_window.title("Créer un compte - Vynal Docs Automator")
        register_window.geometry("500x650")
        register_window.resizable(False, False)
        register_window.transient(self.root)
        register_window.grab_set()
        
        # Centrer la fenêtre
        register_window.update_idletasks()
        width = register_window.winfo_width()
        height = register_window.winfo_height()
        x = (register_window.winfo_screenwidth() // 2) - (width // 2)
        y = (register_window.winfo_screenheight() // 2) - (height // 2)
        register_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Créer la vue d'inscription
        register_view = RegisterView(register_window, self.usage_tracker)
        register_view.pack(fill="both", expand=True)
        
        # Définir le callback de succès
        register_view.on_success_callback = self._on_registration_success
        
    def _on_registration_success(self, user_data):
        """Callback appelé lors d'une inscription réussie
        
        Args:
            user_data (dict): Les données de l'utilisateur inscrit
        """
        try:
            # Afficher un message de bienvenue
            email = user_data.get('email', '')
            name = user_data.get('name', '')
            greeting = f"Bienvenue {name}" if name else f"Bienvenue {email}"
            
            # Mettre à jour le label d'information utilisateur
            if hasattr(self, 'user_info_label'):
                self.user_info_label.configure(text=greeting)
            
            # Créer un écran de chargement
            loading_frame = ctk.CTkFrame(self.root)
            loading_frame.pack(fill=ctk.BOTH, expand=True)

            # Frame centré pour le contenu du spinner
            spinner_content = ctk.CTkFrame(loading_frame, fg_color="transparent")
            spinner_content.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

            # Titre
            ctk.CTkLabel(
                spinner_content,
                text="Chargement du tableau de bord",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("gray10", "gray90")
            ).pack(pady=(0, 20))

            # Message de chargement
            loading_label = ctk.CTkLabel(
                spinner_content,
                text=f"Bienvenue {name if name else email} ! Veuillez patienter pendant le chargement des données...",
                font=ctk.CTkFont(size=14)
            )
            loading_label.pack(pady=(0, 15))

            # Créer un spinner avec CustomTkinter
            spinner = ctk.CTkProgressBar(spinner_content, width=300)
            spinner.pack(pady=10)
            spinner.configure(mode="indeterminate")
            spinner.start()

            # Force le rafraîchissement pour afficher le spinner
            self.root.update()
            
            # Fonction pour initialiser le tableau de bord
            def complete_registration():
                try:
                    logger.info(f"Redirection vers le tableau de bord après inscription: {email}")
                    
                    # Stocker une référence au loading_frame 
                    # afin de pouvoir le détruire après le chargement du dashboard
                    global spinner_reference
                    spinner_reference = loading_frame
                    
                    # S'assurer que l'état d'authentification est mis à jour
                    self._update_auth_state()
                    
                    # S'assurer que les vues sont créées
                    if not hasattr(self, 'views') or not self.views:
                        self.create_views()
                    
                    # S'assurer que les widgets principaux sont correctement affichés
                    widgets_to_check = {
                        'main_frame': {'pack_args': {'fill': ctk.BOTH, 'expand': True}},
                        'sidebar': {'pack_args': {'side': ctk.LEFT, 'fill': ctk.Y, 'padx': 0, 'pady': 0}},
                        'content_area': {'pack_args': {'side': ctk.RIGHT, 'fill': ctk.BOTH, 'expand': True, 'padx': 0, 'pady': 0}},
                        'main_content': {'pack_args': {'side': ctk.TOP, 'fill': ctk.BOTH, 'expand': True, 'padx': 20, 'pady': 20}}
                    }
                    
                    # Vérifier et afficher chaque widget
                    for widget_name, config in widgets_to_check.items():
                        if hasattr(self, widget_name):
                            widget = getattr(self, widget_name)
                            if widget and not widget.winfo_ismapped():
                                widget.pack(**config['pack_args'])
                    
                    # Forcer la mise à jour de l'interface
                    self.root.update()
                    
                    # Créer les vues si elles n'existent pas
                    if not self.views or "dashboard" not in self.views:
                        self.create_views()
                        # Forcer une mise à jour pour s'assurer que les vues sont bien créées
                        self.root.update()
                    
                    # Afficher le dashboard après un court délai
                    def show_dashboard_after_delay():
                        try:
                            # Afficher le dashboard
                            if "dashboard" in self.views:
                                self.show_view("dashboard")
                                logger.info("Dashboard affiché avec succès après inscription")
                            else:
                                logger.error("La vue dashboard n'existe pas après sa création")
                                
                            # Détruire le spinner après un court délai
                            self.root.after(500, lambda: self._destroy_spinner_safely(spinner_reference))
                        except Exception as e:
                            logger.error(f"Erreur lors de l'affichage différé du dashboard: {e}", exc_info=True)
                            self._destroy_spinner_safely(spinner_reference)
                    
                    # Lancer l'affichage du dashboard après un court délai
                    self.root.after(200, show_dashboard_after_delay)
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la redirection vers le tableau de bord: {e}", exc_info=True)
                    # En cas d'erreur, toujours supprimer le spinner
                    try:
                        if 'loading_frame' in locals() and loading_frame and loading_frame.winfo_exists():
                            loading_frame.destroy()
                    except Exception:
                        pass
                    
                    # Afficher un message dans une notification
                    from utils.notification import show_notification
                    show_notification(
                        "Erreur",
                        "Une erreur est survenue lors du chargement du tableau de bord. Veuillez redémarrer l'application.",
                        "error"
                    )
            
            # Lancer le processus après un court délai
            self.root.after(1000, complete_registration)
            
        except Exception as e:
            logger.error(f"Erreur lors de la gestion du succès d'inscription: {e}", exc_info=True)
            # Afficher un message dans une notification
            from utils.notification import show_notification
            show_notification(
                "Erreur",
                "Une erreur est survenue lors de la finalisation de l'inscription. Veuillez redémarrer l'application.",
                "error"
            )
    
    def _destroy_spinner_safely(self, spinner_frame):
        """Détruit le spinner de façon sécurisée"""
        try:
            if spinner_frame and spinner_frame.winfo_exists():
                spinner_frame.destroy()
                logger.info("Spinner supprimé après chargement du dashboard")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du spinner: {e}")

    def _show_auth_dialog_tab(self, tab_name):
        """
        Affiche le dialogue d'authentification avec un onglet spécifique
        
        Args:
            tab_name: Nom de l'onglet à afficher ("login", "register" ou "account")
        """
        # Si l'onglet demandé est "register", utiliser la nouvelle méthode d'inscription
        if tab_name == "register":
            self._show_register_view()
            return
            
        # Pour les autres onglets, utiliser la méthode standard
        self._show_auth_dialog()
        
        # Puis afficher l'onglet spécifié
        try:
            if hasattr(self, 'auth_view') and self.auth_view:
                logger.info(f"Affichage de l'onglet {tab_name}")
                self.auth_view._show_tab(tab_name)
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de l'onglet {tab_name}: {e}")

    # Methods for activity monitor integration and lock/unlock functionality
    def _setup_activity_monitor(self):
        """Configure et initialise le moniteur d'activité si nécessaire"""
        try:
            # Créer une instance du moniteur d'activité
            self.activity_monitor = ActivityMonitor(
                lock_callback=self._lock_application,
                config_manager=self.model.config
            )
            
            # Démarrer le moniteur si les conditions sont remplies
            self.activity_monitor.start()
            
            logger.info("Moniteur d'activité configuré")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration du moniteur d'activité: {e}")
    
    def _setup_activity_events(self):
        """Configure les événements pour détecter l'activité de l'utilisateur"""
        try:
            if self.activity_monitor:
                # Associer les événements de la fenêtre principale
                self.root.bind("<Motion>", self._on_user_activity)
                self.root.bind("<Key>", self._on_user_activity)
                self.root.bind("<Button>", self._on_user_activity)
                self.root.bind("<MouseWheel>", self._on_user_activity)
                
                # Bind événements sur le frame principal aussi
                self.main_frame.bind("<Motion>", self._on_user_activity)
                self.main_frame.bind("<Button>", self._on_user_activity)
                
                logger.debug("Événements de surveillance d'activité configurés")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration des événements d'activité: {e}")
    
    def _on_user_activity(self, event=None):
        """Callback appelé lors d'une activité utilisateur"""
        if self.activity_monitor:
            self.activity_monitor.register_activity(event)
    
    def _lock_application(self):
        """Verrouille l'application et affiche l'écran de connexion"""
        try:
            # Exécuter sur le thread principal pour éviter les problèmes d'interface
            self.root.after(0, self._show_unlock_dialog)
            logger.info("Application verrouillée par inactivité")
        except Exception as e:
            logger.error(f"Erreur lors du verrouillage de l'application: {e}")
    
    def _show_unlock_dialog(self):
        """Affiche la boîte de dialogue de déverrouillage"""
        try:
            # Masquer l'application principale
            for widget in self.root.winfo_children():
                widget.pack_forget()
            
            # Créer une fenêtre modale par-dessus l'application
            self.lock_dialog = ctk.CTkToplevel(self.root)
            self.lock_dialog.title("Déverrouillage requis")
            self.lock_dialog.attributes("-topmost", True)
            
            # Rendre la fenêtre modale
            self.lock_dialog.grab_set()
            self.lock_dialog.focus_force()
            
            # Empêcher la fermeture par la croix
            self.lock_dialog.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Dimensions
            width = 400
            height = 250
            self.lock_dialog.geometry(f"{width}x{height}")
            
            # Centrer la fenêtre
            self.lock_dialog.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.lock_dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal avec padding
            main_frame = ctk.CTkFrame(self.lock_dialog)
            main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # Titre
            title_label = ctk.CTkLabel(
                main_frame,
                text="🔒 Session verrouillée",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Message
            message_label = ctk.CTkLabel(
                main_frame,
                text="Votre session a été verrouillée en raison d'inactivité.\nVeuillez entrer votre mot de passe pour continuer.",
                wraplength=350
            )
            message_label.pack(pady=(0, 20))
            
            # Champ de mot de passe
            password_var = ctk.StringVar()
            password_entry = ctk.CTkEntry(
                main_frame,
                placeholder_text="Mot de passe",
                show="•",
                width=200,
                textvariable=password_var
            )
            password_entry.pack(pady=(0, 10))
            password_entry.focus_set()
            
            # Message d'erreur
            error_label = ctk.CTkLabel(
                main_frame,
                text="",
                text_color="red"
            )
            error_label.pack(pady=(0, 10))
            
            # Fonction de validation
            def validate_password():
                password = password_var.get()
                if not password:
                    error_label.configure(text="Veuillez entrer votre mot de passe")
                    return
                
                # Vérifier le mot de passe
                if self._check_password(password):
                    # Fermer la boîte de dialogue
                    self.lock_dialog.destroy()
                    
                    # Réafficher les widgets principaux de l'application
                    self._restore_main_view()
                    
                    # Réinitialiser le moniteur d'activité
                    if self.activity_monitor:
                        self.activity_monitor.reset()
                    
                    logger.info("Application déverrouillée avec succès")
                else:
                    error_label.configure(text="Mot de passe incorrect")
                    password_entry.delete(0, "end")
            
            # Gestion de l'événement Entrée
            password_entry.bind("<Return>", lambda event: validate_password())
            
            # Bouton de déverrouillage
            unlock_button = ctk.CTkButton(
                main_frame,
                text="Déverrouiller",
                width=150,
                command=validate_password
            )
            unlock_button.pack(pady=10)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la boîte de dialogue de déverrouillage: {e}")
            # En cas d'erreur, restaurer l'interface principale
            self._restore_main_view()
    
    def _restore_main_view(self):
        """Restaure l'affichage principal de l'application après déverrouillage"""
        try:
            # Réafficher les widgets principaux
            if hasattr(self, 'main_frame'):
                # Clear le root d'abord
                for widget in self.root.winfo_children():
                    if widget != self.lock_dialog:  # Ne pas toucher au dialogue de verrouillage
                        widget.pack_forget()
                
                # Réafficher le frame principal
                self.main_frame.pack(fill=ctk.BOTH, expand=True)
                
                # Réorganiser les composants principaux
                if hasattr(self, 'sidebar'):
                    self.sidebar.pack(side=ctk.LEFT, fill=ctk.Y, padx=0, pady=0)
                
                if hasattr(self, 'content_area'):
                    self.content_area.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
                    
                    # Réafficher les composants de la zone de contenu
                    if hasattr(self, 'toolbar_frame'):
                        self.toolbar_frame.pack(side=ctk.TOP, fill=ctk.X, padx=0, pady=0)
                    
                    if hasattr(self, 'main_content'):
                        self.main_content.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=20, pady=20)
                    
                    if hasattr(self, 'status_bar'):
                        self.status_bar.pack(side=ctk.BOTTOM, fill=ctk.X)
            
            # Redessiner la fenêtre
            self.root.update_idletasks()
            logger.info("Interface principale restaurée après déverrouillage")
        except Exception as e:
            logger.error(f"Erreur lors de la restauration de l'interface principale: {e}")
            # En cas d'erreur grave, essayer de recharger complètement l'interface
            try:
                self._create_widgets()
                logger.info("Interface réinitialisée après erreur de restauration")
            except Exception as e2:
                logger.critical(f"Erreur critique lors de la réinitialisation de l'interface: {e2}")
    
    def _check_password(self, password):
        """
        Vérifie si le mot de passe est correct
        
        Args:
            password: Mot de passe à vérifier
            
        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        try:
            # Récupérer les données de l'utilisateur
            user_data = self.usage_tracker.get_user_data()
            if not user_data:
                logger.warning("Aucun utilisateur actif")
                return False
                
            # Récupérer le mot de passe haché
            stored_password = user_data.get('password', '')
            if not stored_password:
                logger.warning("Aucun mot de passe stocké")
                return False
                
            # Hacher le mot de passe entré
            import hashlib
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Comparer les mots de passe
            return hashed_password == stored_password
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
            return False
    
    def update_activity_monitor(self):
        """Met à jour le moniteur d'activité selon les paramètres actuels"""
        if self.activity_monitor:
            # Arrêter l'ancien moniteur
            self.activity_monitor.stop()
            
            # Redémarrer avec les nouveaux paramètres
            self.activity_monitor.start()
            
            logger.info("Moniteur d'activité mis à jour")
    
    def shutdown(self):
        """Arrête proprement le moniteur d'activité lors de la fermeture"""
        if self.activity_monitor:
            self.activity_monitor.stop()
            logger.info("Moniteur d'activité arrêté lors de la fermeture de l'application")

    def show_settings(self):
        """Affiche la vue des paramètres"""
        try:
            # Masquer toutes les autres vues
            self.hide_all_views()
            
            # Créer la vue des paramètres si elle n'existe pas
            if not hasattr(self, 'settings_view') or self.settings_view is None:
                from views.settings_view import SettingsView
                self.settings_view = SettingsView(self.content_frame, self.app_model)
            
            # Mettre à jour et afficher la vue
            self.settings_view.update_view()
            self.settings_view.show()
            
            # Mettre à jour le titre
            self.update_view_title("Paramètres")
            
            # Activer le bouton dans la barre latérale
            self.highlight_sidebar_button("settings")
            
            logger.info("Vue des paramètres affichée")
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la vue des paramètres: {e}")
            self.show_error(f"Impossible d'afficher les paramètres: {str(e)}")

    def refresh_license_status(self):
        """
        Rafraîchit l'état de la licence dans toute l'application
        Cette méthode est appelée après une mise à jour de licence
        """
        try:
            logger.info("Rafraîchissement de l'état de la licence dans l'application")
            
            # Vérifier si nous avons un modèle de licence
            if hasattr(self.app_model, 'license_model') and self.app_model.license_model:
                # Récupérer les données utilisateur depuis UsageTracker
                from utils.usage_tracker import UsageTracker
                usage_tracker = UsageTracker()
                
                if usage_tracker.is_user_registered():
                    user_data = usage_tracker.get_user_data() or {}
                    email = user_data.get('email', '')
                    license_key = user_data.get('license_key', '')
                    license_valid = user_data.get('license_valid', False)
                    
                    # Mettre à jour le statut dans le modèle de l'application
                    if hasattr(self.app_model, 'set_license_status'):
                        self.app_model.set_license_status(license_valid, email, license_key)
                        logger.info(f"Statut de licence mis à jour: valide={license_valid}")
                
                # Rafraîchir toutes les vues
                if hasattr(self, 'dashboard_view') and self.dashboard_view:
                    self.dashboard_view.update_view()
                
                if hasattr(self, 'settings_view') and self.settings_view:
                    self.settings_view.update_view()
                
                # Mettre à jour l'interface utilisateur en fonction de la licence
                self.update_features_availability()
                
                logger.info("Rafraîchissement de l'état de licence terminé")
            else:
                logger.warning("Modèle de licence non disponible pour le rafraîchissement")
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement de l'état de licence: {e}")
    
    def update_features_availability(self):
        """
        Met à jour la disponibilité des fonctionnalités en fonction de l'état de la licence
        """
        try:
            # Vérifier si nous avons un modèle de licence
            if hasattr(self.app_model, 'license_model') and self.app_model.license_model:
                # Récupérer les informations de licence
                from utils.usage_tracker import UsageTracker
                usage_tracker = UsageTracker()
                
                license_valid = False
                features = []
                
                if usage_tracker.is_user_registered():
                    user_data = usage_tracker.get_user_data() or {}
                    email = user_data.get('email', '')
                    license_valid = user_data.get('license_valid', False)
                    
                    if license_valid and email:
                        # Récupérer les fonctionnalités actives pour cette licence
                        license_data = self.app_model.license_model.get_license(email)
                        if license_data and "features" in license_data:
                            features = license_data.get("features", [])
                
                # Mettre à jour les boutons et menus en fonction des fonctionnalités disponibles
                # Par exemple, activer/désactiver certains boutons selon les fonctionnalités
                
                logger.info(f"Mise à jour des fonctionnalités disponibles: licence valide={license_valid}, fonctionnalités={features}")
            else:
                logger.warning("Modèle de licence non disponible pour la mise à jour des fonctionnalités")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des fonctionnalités disponibles: {e}")

    def show_dashboard(self):
        """
        Affiche le tableau de bord principal de l'application.
        Cette méthode est appelée après une connexion réussie pour réafficher l'interface principale.
        """
        try:
            logger.info("Tentative d'affichage du tableau de bord...")
            
            # S'assurer que l'interface principale est bien créée
            if not hasattr(self, 'main_frame') or not self.main_frame:
                logger.warning("Main frame manquant, recréation de l'interface...")
                self._create_widgets()
            
            # Utiliser une seule vérification pour tous les widgets principaux
            widgets_to_check = {
                'main_frame': {'pack_args': {'fill': ctk.BOTH, 'expand': True}},
                'sidebar': {'pack_args': {'side': ctk.LEFT, 'fill': ctk.Y, 'padx': 0, 'pady': 0}},
                'content_area': {'pack_args': {'side': ctk.RIGHT, 'fill': ctk.BOTH, 'expand': True, 'padx': 0, 'pady': 0}},
                'main_content': {'pack_args': {'side': ctk.TOP, 'fill': ctk.BOTH, 'expand': True, 'padx': 20, 'pady': 20}}
            }
            
            # Vérifier et afficher chaque widget en une seule passe
            for widget_name, config in widgets_to_check.items():
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if widget and not widget.winfo_ismapped():
                        widget.pack(**config['pack_args'])
                else:
                    logger.warning(f"Widget {widget_name} manquant lors de l'affichage du dashboard")
            
            # Forcer la mise à jour de l'interface
            self.root.update_idletasks()
            
            # Vérifier si les vues existent, sinon les créer
            if not hasattr(self, 'views') or not self.views or len(self.views) == 0:
                logger.info("Vues manquantes, création des vues...")
                self.create_views()
                # Forcer une mise à jour pour s'assurer que les vues sont bien créées
                self.root.update_idletasks()
            
            # Vérifier si la vue dashboard existe, sinon recréer toutes les vues
            if "dashboard" not in self.views:
                logger.warning("Vue dashboard manquante, recréation des vues...")
                self.create_views()
                # Forcer une mise à jour
                self.root.update_idletasks()
                
                # Vérifier à nouveau si la création a fonctionné
                if "dashboard" not in self.views:
                    logger.error("Impossible de créer la vue dashboard, affichage d'un message d'erreur")
                    self.show_message("Erreur", "Impossible de charger le tableau de bord. Veuillez redémarrer l'application.", "error")
                    return
            
            # S'assurer que la vue dashboard est mise à jour avant d'être affichée
            if hasattr(self.views["dashboard"], "update_view"):
                try:
                    logger.info("Mise à jour de la vue dashboard...")
                    self.views["dashboard"].update_view()
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de la vue dashboard: {e}")
            
            # Afficher la vue dashboard
            logger.info("Affichage de la vue dashboard...")
            self.show_view("dashboard")
            
            logger.info("Tableau de bord affiché avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du tableau de bord: {e}", exc_info=True)
            # Approche minimaliste en cas d'erreur
            try:
                # Recréer uniquement les composants essentiels de l'interface
                self._create_widgets()
                self.create_views()
                self.root.update_idletasks()
                
                if "dashboard" in self.views:
                    self.show_view("dashboard")
                else:
                    self.show_message("Erreur", "Une erreur est survenue lors de l'affichage du tableau de bord.", "error")
            except Exception as e2:
                logger.critical(f"Erreur critique lors de la recréation de l'interface: {e2}")
                self.show_message("Erreur", "Une erreur est survenue lors de l'affichage du tableau de bord.", "error")

    def reset(self, keep_attributes=None):
        """
        Réinitialise complètement l'instance en conservant certains attributs
        
        Args:
            keep_attributes: Liste des attributs à conserver
        """
        if keep_attributes is None:
            keep_attributes = ['root', 'model', 'on_ready', 'usage_tracker']
        
        try:
            # Sauvegarder les attributs spécifiés
            saved_attributes = {}
            for attr in keep_attributes:
                if hasattr(self, attr):
                    saved_attributes[attr] = getattr(self, attr)
            
            # Arrêter proprement toutes les ressources
            if hasattr(self, 'activity_monitor') and self.activity_monitor:
                self.activity_monitor.stop()
            
            # Détruire tous les widgets qui pourraient exister
            for attr_name, attr_value in list(self.__dict__.items()):
                if isinstance(attr_value, (ctk.CTkBaseClass, tk.BaseWidget)):
                    try:
                        attr_value.destroy()
                    except Exception:
                        pass
            
            # Supprimer tous les attributs
            for attr in list(self.__dict__.keys()):
                if attr not in keep_attributes:
                    delattr(self, attr)
            
            # Restaurer les attributs sauvegardés
            for attr, value in saved_attributes.items():
                setattr(self, attr, value)
            
            logger.info("Instance réinitialisée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation de l'instance: {e}")
            return False

    def _update_auth_state(self):
        """Mettre à jour l'état d'authentification et l'interface utilisateur"""
        try:
            # Vérifier et récupérer l'état de connexion
            is_logged_in = self.usage_tracker.has_active_user()
            logger.info(f"Mise à jour de l'état d'authentification: utilisateur connecté = {is_logged_in}")
            
            # Récupérer les informations de l'utilisateur si connecté
            user_data = self.usage_tracker.get_user_data() if is_logged_in else None
            
            # Mettre à jour le bouton d'authentification et les options liées
            self.update_auth_button(is_logged_in)
            
            # Mettre à jour l'étiquette d'information utilisateur si disponible
            if hasattr(self, 'user_info_label') and self.user_info_label:
                if is_logged_in and user_data:
                    # Privilégier le nom, sinon utiliser l'email
                    user_display = user_data.get('name', user_data.get('email', 'Utilisateur'))
                    self.user_info_label.configure(text=f"Bienvenue, {user_display}")
                else:
                    self.user_info_label.configure(text="Utilisateur non connecté")
            
            # Si l'utilisateur est connecté, s'assurer que la vue dashboard existe
            if is_logged_in:
                # Vérifier si les vues existent, et les créer si nécessaire
                if not hasattr(self, 'views') or not self.views:
                    logger.info("Vues non créées, création des vues...")
                    self.create_views()
                
                # S'assurer que les widgets principaux sont visibles
                widgets_to_check = {
                    'main_frame': {'pack_args': {'fill': ctk.BOTH, 'expand': True}},
                    'sidebar': {'pack_args': {'side': ctk.LEFT, 'fill': ctk.Y, 'padx': 0, 'pady': 0}},
                    'content_area': {'pack_args': {'side': ctk.RIGHT, 'fill': ctk.BOTH, 'expand': True, 'padx': 0, 'pady': 0}},
                    'main_content': {'pack_args': {'side': ctk.TOP, 'fill': ctk.BOTH, 'expand': True, 'padx': 20, 'pady': 20}}
                }
                
                # Vérifier et afficher chaque widget
                for widget_name, config in widgets_to_check.items():
                    if hasattr(self, widget_name):
                        widget = getattr(self, widget_name)
                        if widget and not widget.winfo_ismapped():
                            widget.pack(**config['pack_args'])
                            logger.debug(f"Widget {widget_name} affiché")
                
                # Forcer une mise à jour de l'interface
                self.root.update_idletasks()
            
            logger.info("État d'authentification mis à jour avec succès")
            return is_logged_in
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'état d'authentification: {e}", exc_info=True)
            return False

    def show_login(self):
        """Affiche le dialogue de connexion"""
        try:
            # Nettoyer l'interface principale
            try:
                if hasattr(self, 'main_frame'):
                    # Masquer temporairement le contenu existant
                    for widget in self.main_frame.winfo_children():
                        widget.pack_forget()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage de l'interface principale: {e}")
                
            # Créer le formulaire de connexion
            login_frame = ctk.CTkFrame(self.main_frame)
            login_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # En-tête avec le logo et le titre
            header_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(20, 30))
            
            # Titre de l'application
            app_title = ctk.CTkLabel(
                header_frame,
                text=self.model.config.get("app.name", "Vynal Docs Automator"),
                font=ctk.CTkFont(size=24, weight="bold")
            )
            app_title.pack(pady=(0, 10))
            
            # Formulaire
            form_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
            form_frame.pack(pady=20)
            
            # Label d'instructions
            instructions = ctk.CTkLabel(
                form_frame,
                text="Veuillez vous connecter pour accéder à votre compte",
                font=ctk.CTkFont(size=14)
            )
            instructions.pack(pady=(0, 20))
            
            # Champ email
            email_label = ctk.CTkLabel(form_frame, text="Email", anchor="w")
            email_label.pack(fill="x", padx=10, pady=(0, 5))
            
            email_var = ctk.StringVar(value=self.usage_tracker.get_last_email() or "")
            email_entry = ctk.CTkEntry(
                form_frame, 
                width=300,
                placeholder_text="Votre adresse email",
                textvariable=email_var
            )
            email_entry.pack(pady=(0, 15))
            
            # Champ mot de passe
            password_label = ctk.CTkLabel(form_frame, text="Mot de passe", anchor="w")
            password_label.pack(fill="x", padx=10, pady=(0, 5))
            
            password_var = ctk.StringVar()
            password_entry = ctk.CTkEntry(
                form_frame, 
                width=300,
                placeholder_text="Votre mot de passe",
                show="•",
                textvariable=password_var
            )
            password_entry.pack(pady=(0, 15))
            
            # Option "Rester connecté"
            remember_var = ctk.BooleanVar(value=False)
            remember_checkbox = ctk.CTkCheckBox(
                form_frame,
                text="Rester connecté",
                variable=remember_var
            )
            remember_checkbox.pack(anchor="w", pady=(0, 15))
            
            # Message d'erreur
            error_var = ctk.StringVar()
            error_label = ctk.CTkLabel(
                form_frame,
                textvariable=error_var,
                text_color="red"
            )
            error_label.pack(pady=(0, 15))
            
            # Fonction de connexion
            def handle_login():
                try:
                    email = email_var.get().strip()
                    password = password_var.get()
                    remember = remember_var.get()
                    
                    # Valider les entrées
                    if not email:
                        error_var.set("Veuillez entrer votre adresse email")
                        return
                        
                    if not password:
                        error_var.set("Veuillez entrer votre mot de passe")
                        return
                    
                    # Vérifier les informations de connexion
                    success = self.usage_tracker.login(email, password, remember)
                    
                    if success:
                        # Connecté avec succès
                        error_var.set("")
                        login_frame.destroy()  # Supprimer le formulaire
                        
                        # Mise à jour de l'état d'authentification
                        user_data = self.usage_tracker.get_user_data()
                        self._on_auth_change(True, user_data)
                        
                        # Afficher le tableau de bord
                        self.show_dashboard()
                    else:
                        # Échec de connexion
                        error_var.set("Email ou mot de passe incorrect")
                except Exception as e:
                    logger.error(f"Erreur lors de la connexion: {e}")
                    error_var.set(f"Une erreur est survenue: {str(e)}")
            
            # Bouton de connexion
            login_button = ctk.CTkButton(
                form_frame,
                text="Se connecter",
                width=300,
                command=handle_login
            )
            login_button.pack(pady=(0, 20))
            
            # Lien pour s'inscrire
            register_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            register_frame.pack(pady=(0, 10))
            
            register_label = ctk.CTkLabel(
                register_frame,
                text="Vous n'avez pas de compte ? ",
                font=ctk.CTkFont(size=12)
            )
            register_label.pack(side="left")
            
            register_link = ctk.CTkButton(
                register_frame,
                text="Créer un compte",
                command=self._show_register_view,
                fg_color="transparent",
                hover_color=("gray90", "gray20"),
                text_color=["#1f538d", "#3a7ebf"],
                font=ctk.CTkFont(size=12)
            )
            register_link.pack(side="left")
            
            # Pied de page
            footer = ctk.CTkLabel(
                login_frame,
                text=f"© {datetime.now().year} Vynal Docs Automator",
                font=ctk.CTkFont(size=10)
            )
            footer.pack(side="bottom", pady=10)
            
            # S'assurer que le cadre principal est visible
            if not self.main_frame.winfo_ismapped():
                self.main_frame.pack(fill=ctk.BOTH, expand=True)
                
            # Forcer une mise à jour de l'interface
            self.root.update_idletasks()
            
            # Focus sur le premier champ vide
            if not email_var.get():
                email_entry.focus_set()
            else:
                password_entry.focus_set()
                
            logger.info("Dialogue de connexion affiché")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du dialogue de connexion: {e}")
            self.show_message(
                "Erreur",
                f"Une erreur s'est produite lors de l'affichage du dialogue de connexion: {str(e)}",
                "error"
            )
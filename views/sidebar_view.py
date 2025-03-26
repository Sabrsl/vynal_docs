import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Any, Dict, Optional
from models.app_model import AppModel
import os
import logging

# Configuration du logger
logger = logging.getLogger("VynalDocsAutomator.SidebarView")

def safe_load_image(path, size=(150, 40)):
    """
    Charge une image de manière sécurisée avec gestion d'erreur
    
    Args:
        path: Chemin de l'image
        size: Taille de l'image (largeur, hauteur)
        
    Returns:
        CTkImage ou None en cas d'erreur
    """
    try:
        if os.path.exists(path):
            return ctk.CTkImage(
                light_image=Image.open(path),
                dark_image=Image.open(path),
                size=size
            )
        else:
            logger.warning(f"Image non trouvée: {path}. Utilisation d'une image par défaut.")
            # Création d'une image vide avec texte comme fallback
            img = Image.new('RGB', size, color=(52, 53, 65))
            return ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=size
            )
    except Exception as e:
        logger.error(f"Erreur lors du chargement de l'image {path}: {e}")
        # Création d'une image vide comme fallback
        img = Image.new('RGB', size, color=(52, 53, 65))
        return ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=size
        )

class SidebarView:
    """Vue de la barre latérale intégrant un style inspiré de n8n"""
    
    def __init__(self, parent: ctk.CTkFrame, model: AppModel, main_view=None):
        """
        Initialise la vue de la barre latérale
        
        Args:
            parent: Frame parent dans laquelle afficher la barre latérale
            model: Modèle de l'application
            main_view: Référence à la vue principale pour la navigation
        """
        self.parent = parent
        self.model = model
        self.main_view = main_view
        self.active_view = None
        self.hover_button = None
        
        # Création du frame principal
        self.frame = ctk.CTkFrame(
            parent,
            corner_radius=0,
            fg_color=("#F9FAFB", "#1F2022")
        )
        self.frame.pack(fill=ctk.Y, side=ctk.LEFT, padx=0, pady=0)
        
        # Couleurs pour le style n8n
        self.colors = {
            "active": ("#2563EB", "#3B82F6"),      # Bleu primaire
            "hover": ("#F3F4F6", "#2A2D34"),        # Gris très léger / Gris foncé
            "background": ("#F9FAFB", "#1F2022"),   # Fond de la barre latérale
            "text": ("#111827", "#FFFFFF"),         # Texte principal
            "text_secondary": ("#6B7280", "#9CA3AF") # Texte secondaire
        }
        
        # Dictionnaire pour stocker les widgets de navigation
        self.nav_button_widgets = {}
        
        # Créer les widgets de l'interface
        self.create_widgets()
        
        logger.info("SidebarView initialisée")
        
        # Créer les boutons de navigation
        self.create_navigation_buttons()
    
    def create_widgets(self) -> None:
        """
        Crée les widgets de la barre latérale avec un style minimaliste
        """
        # Logo plus petit et centré
        logo_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        logo_frame.pack(fill=ctk.X, padx=10, pady=(25, 15))
        
        logo_image = safe_load_image("assets/images/logo.png")
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="",
            image=logo_image
        )
        logo_label.pack()
        
        # Séparateur subtil
        separator = ctk.CTkFrame(self.frame, height=1, fg_color=("#D1D5DB", "#2D3035"))
        separator.pack(fill=ctk.X, padx=15, pady=(5, 20))
    
    def create_navigation_buttons(self) -> None:
        """
        Crée les boutons de navigation avec un style inspiré de n8n
        """
        # Cadre pour les boutons
        buttons_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, padx=10, pady=5)
        
        # Boutons de navigation avec icônes minimalistes
        # Utilise des émojis comme placeholder, idéalement remplacer par des icônes SVG
        nav_buttons = [
            ("🏠", "Accueil", "home"),
            ("📄", "Documents", "documents"),
            ("👥", "Clients", "clients"),
            ("📝", "Modèles", "templates"),
            ("🤖", "IA", "ai"),
            ("⚙️", "Paramètres", "settings"),
        ]
        
        for icon, text, view in nav_buttons:
            # Conteneur pour chaque ligne
            button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent", height=42)
            button_container.pack(fill=ctk.X, pady=3)
            button_container.pack_propagate(False)
            
            # Indicateur de sélection (barre verticale)
            selection_indicator = ctk.CTkFrame(button_container, width=3, fg_color="transparent")
            selection_indicator.pack(side=ctk.LEFT, fill=ctk.Y)
            
            # Bouton principal avec un style plus épuré
            button = ctk.CTkButton(
                button_container,
                text=f" {icon}  {text}",
                anchor="w",
                height=36,
                corner_radius=6,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("#F3F4F6", "#2A2D34"),
                font=ctk.CTkFont(size=13),
                command=lambda v=view: self._handle_view_change(v)
            )
            button.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(10, 5))
            
            # Stocker les références pour pouvoir modifier les styles plus tard
            self.nav_button_widgets[view] = {
                "button": button,
                "container": button_container,
                "indicator": selection_indicator
            }
            
            # Ajouter les événements de survol
            def on_enter(e, v=view):
                if self.active_view != v:
                    self.nav_button_widgets[v]["button"].configure(fg_color=("#F3F4F6", "#2A2D34"))
                    self.hover_button = v
            
            def on_leave(e, v=view):
                if self.active_view != v:
                    self.nav_button_widgets[v]["button"].configure(fg_color="transparent")
                self.hover_button = None
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        
        # Ajouter un espace extensible
        spacer = ctk.CTkFrame(self.frame, fg_color="transparent")
        spacer.pack(fill=ctk.BOTH, expand=True)
        
        # Section du bas pour le profil utilisateur
        self.create_user_profile_section()
    
    def create_user_profile_section(self):
        """
        Crée la section de profil utilisateur dans le style n8n
        """
        # Séparateur subtil avant la section utilisateur
        separator = ctk.CTkFrame(self.frame, height=1, fg_color=("#D1D5DB", "#2D3035"))
        separator.pack(fill=ctk.X, padx=15, pady=10)
        
        # Conteneur pour le profil utilisateur
        profile_container = ctk.CTkFrame(self.frame, fg_color="transparent", height=60)
        profile_container.pack(fill=ctk.X, padx=10, pady=(5, 15))
        
        # Icône utilisateur (peut être remplacée par la photo de profil)
        user_icon = ctk.CTkLabel(
            profile_container,
            text="👤",
            font=ctk.CTkFont(size=20),
            width=32
        )
        user_icon.pack(side=ctk.LEFT, padx=(10, 5))
        
        # Obtenir les infos utilisateur
        user_info = self.model.get_user_info() if hasattr(self.model, "get_user_info") else {}
        user_name = user_info.get("username", "Utilisateur")
        user_email = user_info.get("email", "")
        
        # Informations utilisateur dans un sous-conteneur vertical
        user_info_container = ctk.CTkFrame(profile_container, fg_color="transparent")
        user_info_container.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        
        # Nom d'utilisateur
        username_label = ctk.CTkLabel(
            user_info_container,
            text=user_name,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        username_label.pack(anchor="w", fill=ctk.X)
        
        # Email (si connecté)
        if user_email:
            email_label = ctk.CTkLabel(
                user_info_container,
                text=user_email,
                anchor="w",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray70")
            )
            email_label.pack(anchor="w", fill=ctk.X)
        
        # Bouton de menu d'options (trois points)
        menu_button = ctk.CTkButton(
            profile_container,
            text="⋮",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color=("#F3F4F6", "#2A2D34"),
            font=ctk.CTkFont(size=16),
            command=self.show_account_dialog
        )
        menu_button.pack(side=ctk.RIGHT, padx=5)
    
    def set_active(self, view_id):
        """
        Définit le bouton actif dans la barre latérale
        
        Args:
            view_id: ID de la vue active
        """
        # Réinitialiser tous les boutons
        for v, widgets in self.nav_button_widgets.items():
            widgets["button"].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )
            widgets["indicator"].configure(fg_color="transparent")
        
        # Mettre en évidence le bouton actif
        if view_id in self.nav_button_widgets:
            self.active_view = view_id
            self.nav_button_widgets[view_id]["button"].configure(
                fg_color=("#E2E8F0", "#2D3748"),
                text_color=("#2563EB", "#3B82F6")
            )
            self.nav_button_widgets[view_id]["indicator"].configure(
                fg_color=("#2563EB", "#3B82F6")
            )
    
    def show_account_dialog(self) -> None:
        """
        Affiche la boîte de dialogue du compte utilisateur
        """
        try:
            # Créer la fenêtre de dialogue
            dialog = ctk.CTkToplevel(self.frame)
            dialog.title("Mon Compte")
            dialog.geometry("400x500")
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
            
            # Contenu de la fenêtre
            content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            content_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # Titre
            title_label = ctk.CTkLabel(
                content_frame,
                text="Mon Compte",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Informations de l'utilisateur
            user_info = self.model.get_user_info()
            
            # Photo de profil
            profile_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            profile_frame.pack(fill=ctk.X, pady=(0, 20))
            
            # Photo de profil (placeholder)
            profile_image = safe_load_image("assets/images/profile_placeholder.png")
            profile_label = ctk.CTkLabel(
                profile_frame,
                text="",
                image=profile_image
            )
            profile_label.pack(side=ctk.LEFT, padx=(0, 20))
            
            # Informations utilisateur
            info_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
            info_frame.pack(side=ctk.LEFT, fill=ctk.Y)
            
            # Nom d'utilisateur
            username_label = ctk.CTkLabel(
                info_frame,
                text=user_info.get("username", "Utilisateur"),
                font=ctk.CTkFont(size=16, weight="bold")
            )
            username_label.pack(anchor="w")
            
            # Email
            email_label = ctk.CTkLabel(
                info_frame,
                text=user_info.get("email", "email@example.com"),
                font=ctk.CTkFont(size=12)
            )
            email_label.pack(anchor="w")
            
            # Type de compte
            account_type_label = ctk.CTkLabel(
                info_frame,
                text=f"Type de compte : {user_info.get('account_type', 'Standard')}",
                font=ctk.CTkFont(size=12)
            )
            account_type_label.pack(anchor="w")
            
            # Séparateur
            separator = ctk.CTkFrame(content_frame, height=2)
            separator.pack(fill=ctk.X, pady=20)
            
            # Options du compte
            options_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            options_frame.pack(fill=ctk.X)
            
            # Modifier le mot de passe
            change_password_button = ctk.CTkButton(
                options_frame,
                text="🔑 Modifier le mot de passe",
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=self.show_change_password_dialog
            )
            change_password_button.pack(fill=ctk.X, pady=2)
            
            # Préférences de notification
            notification_button = ctk.CTkButton(
                options_frame,
                text="🔔 Préférences de notification",
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=self.show_notification_preferences
            )
            notification_button.pack(fill=ctk.X, pady=2)
            
            # Gérer les abonnements
            subscription_button = ctk.CTkButton(
                options_frame,
                text="💳 Gérer les abonnements",
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=self.show_subscription_management
            )
            subscription_button.pack(fill=ctk.X, pady=2)
            
            # Supprimer le compte
            delete_account_button = ctk.CTkButton(
                options_frame,
                text="🗑️ Supprimer le compte",
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=self.show_delete_account_dialog
            )
            delete_account_button.pack(fill=ctk.X, pady=2)
            
            # Bouton Fermer
            close_button = ctk.CTkButton(
                content_frame,
                text="Fermer",
                width=100,
                command=dialog.destroy
            )
            close_button.pack(pady=(20, 0))
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du compte : {e}")
            self.show_message(
                "Erreur",
                f"Impossible d'afficher le compte : {e}",
                "error"
            )
    
    def show_login_dialog(self) -> None:
        """
        Affiche la boîte de dialogue de connexion
        """
        try:
            # Créer la fenêtre de dialogue
            dialog = ctk.CTkToplevel(self.frame)
            dialog.title("Connexion")
            dialog.geometry("400x500")
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
            
            # Contenu de la fenêtre
            content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            content_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # Titre
            title_label = ctk.CTkLabel(
                content_frame,
                text="Connexion",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Formulaire de connexion
            form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            form_frame.pack(fill=ctk.X, pady=(0, 20))
            
            # Email
            email_label = ctk.CTkLabel(form_frame, text="Email")
            email_label.pack(anchor="w")
            
            email_entry = ctk.CTkEntry(form_frame)
            email_entry.pack(fill=ctk.X, pady=(0, 10))
            
            # Mot de passe
            password_label = ctk.CTkLabel(form_frame, text="Mot de passe")
            password_label.pack(anchor="w")
            
            password_entry = ctk.CTkEntry(form_frame, show="•")
            password_entry.pack(fill=ctk.X, pady=(0, 10))
            
            # Mot de passe oublié
            forgot_password_button = ctk.CTkButton(
                form_frame,
                text="Mot de passe oublié ?",
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=self.show_forgot_password_dialog
            )
            forgot_password_button.pack(anchor="e", pady=(0, 20))
            
            # Bouton de connexion
            login_button = ctk.CTkButton(
                content_frame,
                text="Se connecter",
                width=200,
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda: self.login(email_entry.get(), password_entry.get(), dialog)
            )
            login_button.pack(pady=(0, 20))
            
            # Séparateur
            separator = ctk.CTkFrame(content_frame, height=2)
            separator.pack(fill=ctk.X, pady=20)
            
            # Lien vers l'inscription
            register_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            register_frame.pack(fill=ctk.X)
            
            register_label = ctk.CTkLabel(
                register_frame,
                text="Vous n'avez pas de compte ?",
                font=ctk.CTkFont(size=12)
            )
            register_label.pack(side=ctk.LEFT)
            
            register_link = ctk.CTkButton(
                register_frame,
                text="S'inscrire",
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=lambda: self.show_register_dialog(dialog)
            )
            register_link.pack(side=ctk.LEFT, padx=5)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la connexion : {e}")
            self.show_message(
                "Erreur",
                f"Impossible d'afficher la connexion : {e}",
                "error"
            )
    
    def show_register_dialog(self, parent_dialog: Optional[ctk.CTkToplevel] = None) -> None:
        """
        Affiche la boîte de dialogue d'inscription
        
        Args:
            parent_dialog: Fenêtre parente à fermer (optionnel)
        """
        try:
            # Créer la fenêtre de dialogue
            dialog = ctk.CTkToplevel(self.frame)
            dialog.title("Inscription")
            dialog.geometry("400x600")
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
            
            # Contenu de la fenêtre
            content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            content_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # Titre
            title_label = ctk.CTkLabel(
                content_frame,
                text="Créer un compte",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Formulaire d'inscription
            form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            form_frame.pack(fill=ctk.X, pady=(0, 20))
            
            # Nom d'utilisateur
            username_label = ctk.CTkLabel(form_frame, text="Nom d'utilisateur")
            username_label.pack(anchor="w")
            
            username_entry = ctk.CTkEntry(form_frame)
            username_entry.pack(fill=ctk.X, pady=(0, 10))
            
            # Email
            email_label = ctk.CTkLabel(form_frame, text="Email")
            email_label.pack(anchor="w")
            
            email_entry = ctk.CTkEntry(form_frame)
            email_entry.pack(fill=ctk.X, pady=(0, 10))
            
            # Mot de passe
            password_label = ctk.CTkLabel(form_frame, text="Mot de passe")
            password_label.pack(anchor="w")
            
            password_entry = ctk.CTkEntry(form_frame, show="•")
            password_entry.pack(fill=ctk.X, pady=(0, 10))
            
            # Confirmer le mot de passe
            confirm_password_label = ctk.CTkLabel(form_frame, text="Confirmer le mot de passe")
            confirm_password_label.pack(anchor="w")
            
            confirm_password_entry = ctk.CTkEntry(form_frame, show="•")
            confirm_password_entry.pack(fill=ctk.X, pady=(0, 20))
            
            # Bouton d'inscription
            register_button = ctk.CTkButton(
                content_frame,
                text="S'inscrire",
                width=200,
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda: self.register(
                    username_entry.get(),
                    email_entry.get(),
                    password_entry.get(),
                    confirm_password_entry.get(),
                    dialog,
                    parent_dialog
                )
            )
            register_button.pack(pady=(0, 20))
            
            # Séparateur
            separator = ctk.CTkFrame(content_frame, height=2)
            separator.pack(fill=ctk.X, pady=20)
            
            # Lien vers la connexion
            login_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            login_frame.pack(fill=ctk.X)
            
            login_label = ctk.CTkLabel(
                login_frame,
                text="Vous avez déjà un compte ?",
                font=ctk.CTkFont(size=12)
            )
            login_label.pack(side=ctk.LEFT)
            
            login_link = ctk.CTkButton(
                login_frame,
                text="Se connecter",
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=lambda: self.show_login_dialog(dialog)
            )
            login_link.pack(side=ctk.LEFT, padx=5)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de l'inscription : {e}")
            self.show_message(
                "Erreur",
                f"Impossible d'afficher l'inscription : {e}",
                "error"
            )
    
    def show_forgot_password_dialog(self) -> None:
        """
        Affiche la boîte de dialogue de mot de passe oublié
        """
        try:
            # Créer la fenêtre de dialogue
            dialog = ctk.CTkToplevel(self.frame)
            dialog.title("Mot de passe oublié")
            dialog.geometry("400x300")
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
            
            # Contenu de la fenêtre
            content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            content_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            # Titre
            title_label = ctk.CTkLabel(
                content_frame,
                text="Mot de passe oublié",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Description
            description_label = ctk.CTkLabel(
                content_frame,
                text="Entrez votre email pour recevoir un lien de réinitialisation",
                wraplength=300,
                justify="center"
            )
            description_label.pack(pady=(0, 20))
            
            # Email
            email_label = ctk.CTkLabel(content_frame, text="Email")
            email_label.pack(anchor="w")
            
            email_entry = ctk.CTkEntry(content_frame)
            email_entry.pack(fill=ctk.X, pady=(0, 20))
            
            # Bouton d'envoi
            send_button = ctk.CTkButton(
                content_frame,
                text="Envoyer le lien",
                width=200,
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda: self.send_reset_link(email_entry.get(), dialog)
            )
            send_button.pack(pady=(0, 20))
            
            # Lien retour à la connexion
            back_link = ctk.CTkButton(
                content_frame,
                text="Retour à la connexion",
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=dialog.destroy
            )
            back_link.pack()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du mot de passe oublié : {e}")
            self.show_message(
                "Erreur",
                f"Impossible d'afficher le mot de passe oublié : {e}",
                "error"
            )
    
    def send_reset_link(self, email: str, dialog: ctk.CTkToplevel) -> None:
        """
        Envoie un lien de réinitialisation de mot de passe
        
        Args:
            email: Email de l'utilisateur
            dialog: Fenêtre de dialogue à fermer
        """
        try:
            # Vérifier l'email
            if not email:
                self.show_message(
                    "Erreur",
                    "Veuillez entrer votre email",
                    "error"
                )
                return
            
            # Envoyer le lien
            if self.model.send_reset_link(email):
                # Fermer la fenêtre de dialogue
                dialog.destroy()
                
                # Afficher un message de succès
                self.show_message(
                    "Email envoyé",
                    "Un lien de réinitialisation a été envoyé à votre adresse email",
                    "success"
                )
            else:
                self.show_message(
                    "Erreur",
                    "Impossible d'envoyer le lien de réinitialisation",
                    "error"
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du lien de réinitialisation : {e}")
            self.show_message(
                "Erreur",
                f"Impossible d'envoyer le lien de réinitialisation : {e}",
                "error"
            )
    
    def login(self, email: str, password: str, dialog: ctk.CTkToplevel) -> None:
        """
        Connecte l'utilisateur
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe de l'utilisateur
            dialog: Fenêtre de dialogue à fermer
        """
        try:
            # Vérifier les champs
            if not email or not password:
                self.show_message(
                    "Erreur",
                    "Veuillez remplir tous les champs",
                    "error"
                )
                return
            
            # Tenter la connexion
            if self.model.login(email, password):
                # Fermer la fenêtre de dialogue
                dialog.destroy()
                
                # Afficher un message de succès
                self.show_message(
                    "Connexion réussie",
                    "Vous êtes maintenant connecté",
                    "success"
                )
            else:
                self.show_message(
                    "Erreur",
                    "Email ou mot de passe incorrect",
                    "error"
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion : {e}")
            self.show_message(
                "Erreur",
                f"Impossible de se connecter : {e}",
                "error"
            )
    
    def logout(self) -> None:
        """
        Déconnecte l'utilisateur
        """
        try:
            # Demander confirmation
            if not self.show_confirmation(
                "Confirmer la déconnexion",
                "Êtes-vous sûr de vouloir vous déconnecter ?"
            ):
                return
            
            # Déconnecter l'utilisateur
            self.model.logout()
            
            # Afficher un message de succès
            self.show_message(
                "Déconnexion réussie",
                "Vous avez été déconnecté",
                "success"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion : {e}")
            self.show_message(
                "Erreur",
                f"Impossible de se déconnecter : {e}",
                "error"
            )

    def _handle_view_change(self, view_id):
        """
        Gère le changement de vue en appelant la bonne méthode
        
        Args:
            view_id: Identifiant de la vue à afficher
        """
        if self.main_view and hasattr(self.main_view, 'show_view'):
            self.main_view.show_view(view_id)
        elif hasattr(self.model, 'show_view'):
            self.model.show_view(view_id)
        else:
            logger.error(f"Aucune méthode show_view disponible pour afficher {view_id}") 
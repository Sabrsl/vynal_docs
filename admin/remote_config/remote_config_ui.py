#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'interface pour le système de configuration distante.
Gère l'affichage des mises à jour, messages et fonctionnalités dynamiques.
"""

import os
import logging
import threading
import tkinter as tk
import customtkinter as ctk
from typing import Optional, Dict, Any, Callable, List
import webbrowser
import sys

# Ajouter le chemin racine au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importer les modules nécessaires depuis la nouvelle structure
from admin.remote_config.remote_config_manager import RemoteConfigManager
from utils.dialog_utils import DialogUtils

logger = logging.getLogger("VynalDocsAutomator.RemoteConfigUI")

class RemoteConfigUI:
    """
    Interface utilisateur pour interagir avec le système de configuration distante.
    Affiche les mises à jour disponibles, les messages globaux et gère les fonctionnalités dynamiques.
    
    Attributes:
        parent (tk.Widget): Widget parent pour l'interface
        remote_config (RemoteConfigManager): Gestionnaire de configuration distante
        on_update_confirm (Callable): Fonction à appeler lors de la confirmation d'une mise à jour
        update_dialog (ctk.CTkToplevel): Fenêtre de dialogue pour les mises à jour
        message_dialog (ctk.CTkToplevel): Fenêtre de dialogue pour les messages globaux
        changelog_dialog (ctk.CTkToplevel): Fenêtre de dialogue pour le changelog
        status_bar (ctk.CTkFrame): Barre de statut pour afficher les informations
    """
    
    def __init__(self, parent: tk.Widget, remote_config: RemoteConfigManager):
        """
        Initialise l'interface utilisateur pour la configuration distante.
        
        Args:
            parent (tk.Widget): Widget parent pour l'interface
            remote_config (RemoteConfigManager): Gestionnaire de configuration distante
        """
        self.parent = parent
        self.remote_config = remote_config
        self.on_update_confirm = None
        self.update_dialog = None
        self.message_dialog = None
        self.changelog_dialog = None
        self.status_bar = None
        
        # Configurer les callbacks
        self.remote_config.on_update_available = self.show_update_notification
        self.remote_config.on_message_received = self.show_global_message
        
        logger.info("RemoteConfigUI initialisée")
    
    def create_status_bar(self, parent: tk.Widget) -> ctk.CTkFrame:
        """
        Crée une barre de statut pour afficher les informations de mise à jour et messages.
        
        Args:
            parent (tk.Widget): Widget parent pour la barre de statut
        
        Returns:
            ctk.CTkFrame: Barre de statut créée
        """
        self.status_bar = ctk.CTkFrame(parent, height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=0)
        
        # Label pour les messages
        self.status_label = ctk.CTkLabel(self.status_bar, text="", anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Bouton pour vérifier les mises à jour
        self.update_button = ctk.CTkButton(
            self.status_bar,
            text="🔄 Vérifier les mises à jour",
            width=180,
            height=24,
            command=self.check_for_updates_manual
        )
        self.update_button.pack(side=tk.RIGHT, padx=10, pady=3)
        
        return self.status_bar
    
    def check_for_updates_manual(self) -> None:
        """
        Vérifie manuellement les mises à jour et informe l'utilisateur.
        """
        # Désactiver le bouton pendant la vérification
        self.update_button.configure(state="disabled", text="Vérification en cours...")
        
        def check_and_update_ui():
            try:
                # Vérifier les mises à jour
                updated = self.remote_config.check_for_updates(force=True)
                
                # Vérifier si une mise à jour est disponible
                update_available, update_info = self.remote_config.update_is_available()
                
                if update_available:
                    # Afficher la notification de mise à jour
                    self.show_update_notification(update_info)
                else:
                    # Informer l'utilisateur qu'aucune mise à jour n'est disponible
                    DialogUtils.show_message(
                        self.parent,
                        "Mise à jour",
                        "Votre application est à jour.",
                        "info"
                    )
                
                # Réactiver le bouton
                self.update_button.configure(state="normal", text="🔄 Vérifier les mises à jour")
                
                # Mettre à jour le statut
                self.update_status()
            except Exception as e:
                logger.error(f"Erreur lors de la vérification manuelle des mises à jour: {e}")
                # Réactiver le bouton
                self.update_button.configure(state="normal", text="🔄 Vérifier les mises à jour")
                # Informer l'utilisateur
                DialogUtils.show_message(
                    self.parent,
                    "Erreur",
                    f"Erreur lors de la vérification des mises à jour: {str(e)}",
                    "error"
                )
        
        # Exécuter la vérification dans un thread séparé
        threading.Thread(target=check_and_update_ui, daemon=True).start()
    
    def show_update_notification(self, update_info: Dict[str, Any]) -> None:
        """
        Affiche une notification pour une mise à jour disponible.
        
        Args:
            update_info (Dict[str, Any]): Informations sur la mise à jour
        """
        # Éviter d'afficher plusieurs dialogues en même temps
        if self.update_dialog is not None:
            try:
                self.update_dialog.destroy()
            except Exception:
                pass
            self.update_dialog = None
        
        # Créer le dialogue de notification
        self.update_dialog = ctk.CTkToplevel(self.parent)
        self.update_dialog.title("Mise à jour disponible")
        self.update_dialog.geometry("600x400")
        self.update_dialog.resizable(False, False)
        self.update_dialog.transient(self.parent)
        self.update_dialog.grab_set()
        
        # Centrer le dialogue
        self.update_dialog.update_idletasks()
        x = (self.update_dialog.winfo_screenwidth() - self.update_dialog.winfo_width()) // 2
        y = (self.update_dialog.winfo_screenheight() - self.update_dialog.winfo_height()) // 2
        self.update_dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.update_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text="🚀 Mise à jour disponible",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Version
        version_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        version_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text="Version:",
            font=ctk.CTkFont(weight="bold"),
            width=100
        ).pack(side=tk.LEFT, padx=10)
        
        ctk.CTkLabel(
            version_frame,
            text=update_info.get("latest_version", "Inconnue")
        ).pack(side=tk.LEFT, padx=10)
        
        # Description
        changelog_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        changelog_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(
            changelog_frame,
            text="Nouveautés:",
            font=ctk.CTkFont(weight="bold"),
            width=100
        ).pack(side=tk.LEFT, padx=10, anchor="n")
        
        changelog_text = ctk.CTkTextbox(
            changelog_frame,
            width=400,
            height=150,
            wrap="word"
        )
        changelog_text.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        changelog_text.insert("1.0", update_info.get("changelog", "Aucune information disponible"))
        changelog_text.configure(state="disabled")
        
        # Options automatiques
        auto_update = ctk.BooleanVar(value=self.remote_config.get_setting("auto_update", True))
        
        auto_update_checkbox = ctk.CTkCheckBox(
            main_frame,
            text="Télécharger et installer automatiquement",
            variable=auto_update
        )
        auto_update_checkbox.pack(pady=20)
        
        # Boutons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=10)
        
        # Fonction pour fermer le dialogue
        def close_dialog():
            self.update_dialog.destroy()
            self.update_dialog = None
        
        # Fonction pour télécharger la mise à jour
        def download_update():
            # Désactiver les boutons pendant le téléchargement
            download_button.configure(state="disabled", text="Téléchargement en cours...")
            later_button.configure(state="disabled")
            changelog_button.configure(state="disabled")
            
            def do_download():
                try:
                    # Télécharger la mise à jour
                    success, result = self.remote_config.download_update(update_info)
                    
                    if success:
                        # Si l'installation automatique est activée
                        if auto_update.get():
                            # Appliquer la mise à jour
                            apply_success, message = self.remote_config.apply_update(result)
                            
                            if apply_success:
                                # Informer l'utilisateur
                                DialogUtils.show_message(
                                    self.update_dialog,
                                    "Mise à jour appliquée",
                                    message,
                                    "success"
                                )
                                # Fermer le dialogue
                                close_dialog()
                            else:
                                # Informer l'utilisateur
                                DialogUtils.show_message(
                                    self.update_dialog,
                                    "Erreur",
                                    f"Erreur lors de l'application de la mise à jour: {message}",
                                    "error"
                                )
                                # Réactiver les boutons
                                download_button.configure(state="normal", text="Télécharger et installer")
                                later_button.configure(state="normal")
                                changelog_button.configure(state="normal")
                        else:
                            # Si l'installation automatique est désactivée, demander confirmation
                            DialogUtils.show_confirmation(
                                self.update_dialog,
                                "Installation",
                                "La mise à jour a été téléchargée. Voulez-vous l'installer maintenant?",
                                on_yes=lambda: self._confirm_install_update(result)
                            )
                            # Réactiver les boutons
                            download_button.configure(state="normal", text="Télécharger et installer")
                            later_button.configure(state="normal")
                            changelog_button.configure(state="normal")
                    else:
                        # Informer l'utilisateur
                        DialogUtils.show_message(
                            self.update_dialog,
                            "Erreur",
                            f"Erreur lors du téléchargement: {result}",
                            "error"
                        )
                        # Réactiver les boutons
                        download_button.configure(state="normal", text="Télécharger et installer")
                        later_button.configure(state="normal")
                        changelog_button.configure(state="normal")
                except Exception as e:
                    logger.error(f"Erreur lors du téléchargement de la mise à jour: {e}")
                    # Informer l'utilisateur
                    DialogUtils.show_message(
                        self.update_dialog,
                        "Erreur",
                        f"Erreur inattendue: {str(e)}",
                        "error"
                    )
                    # Réactiver les boutons
                    download_button.configure(state="normal", text="Télécharger et installer")
                    later_button.configure(state="normal")
                    changelog_button.configure(state="normal")
            
            # Exécuter le téléchargement dans un thread séparé
            threading.Thread(target=do_download, daemon=True).start()
        
        # Fonction pour afficher le changelog complet
        def show_full_changelog():
            self.show_changelog()
        
        # Bouton pour télécharger et installer
        download_button = ctk.CTkButton(
            button_frame,
            text="Télécharger et installer",
            width=200,
            height=35,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=download_update
        )
        download_button.pack(side=tk.RIGHT, padx=10)
        
        # Bouton pour plus tard
        later_button = ctk.CTkButton(
            button_frame,
            text="Plus tard",
            width=100,
            height=35,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=close_dialog
        )
        later_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton pour voir le changelog complet
        changelog_button = ctk.CTkButton(
            button_frame,
            text="Changelog complet",
            width=150,
            height=35,
            command=show_full_changelog
        )
        changelog_button.pack(side=tk.LEFT, padx=10)
        
        # Mettre à jour le statut
        self.update_status()
    
    def _confirm_install_update(self, update_file_path: str) -> None:
        """
        Confirme et applique l'installation d'une mise à jour.
        
        Args:
            update_file_path (str): Chemin du fichier de mise à jour
        """
        try:
            # Appliquer la mise à jour
            success, message = self.remote_config.apply_update(update_file_path)
            
            if success:
                # Informer l'utilisateur
                DialogUtils.show_message(
                    self.parent,
                    "Mise à jour appliquée",
                    message,
                    "success"
                )
                # Fermer le dialogue de mise à jour
                if self.update_dialog:
                    self.update_dialog.destroy()
                    self.update_dialog = None
            else:
                # Informer l'utilisateur
                DialogUtils.show_message(
                    self.parent,
                    "Erreur",
                    f"Erreur lors de l'application de la mise à jour: {message}",
                    "error"
                )
        except Exception as e:
            logger.error(f"Erreur lors de l'application de la mise à jour: {e}")
            # Informer l'utilisateur
            DialogUtils.show_message(
                self.parent,
                "Erreur",
                f"Erreur inattendue: {str(e)}",
                "error"
            )
    
    def show_global_message(self, message_info: Dict[str, Any]) -> None:
        """
        Affiche un message global.
        
        Args:
            message_info (Dict[str, Any]): Informations sur le message
        """
        # Éviter d'afficher plusieurs dialogues en même temps
        if self.message_dialog is not None:
            try:
                self.message_dialog.destroy()
            except Exception:
                pass
            self.message_dialog = None
        
        # Vérifier si le message est visible
        if not message_info.get("visible", False):
            return
        
        # Récupérer les informations du message
        title = message_info.get("title", "Message")
        body = message_info.get("body", "")
        message_type = message_info.get("type", "info")
        
        # Créer le dialogue de message
        self.message_dialog = ctk.CTkToplevel(self.parent)
        self.message_dialog.title(title)
        self.message_dialog.geometry("500x300")
        self.message_dialog.resizable(False, False)
        self.message_dialog.transient(self.parent)
        self.message_dialog.grab_set()
        
        # Centrer le dialogue
        self.message_dialog.update_idletasks()
        x = (self.message_dialog.winfo_screenwidth() - self.message_dialog.winfo_width()) // 2
        y = (self.message_dialog.winfo_screenheight() - self.message_dialog.winfo_height()) // 2
        self.message_dialog.geometry(f"+{x}+{y}")
        
        # Icône pour le type de message
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        # Couleurs pour le type de message
        colors = {
            "info": ("#3498db", "#2980b9"),
            "warning": ("#f39c12", "#d35400"),
            "error": ("#e74c3c", "#c0392b"),
            "success": ("#2ecc71", "#27ae60")
        }
        
        # Récupérer l'icône et les couleurs
        icon = icons.get(message_type, icons["info"])
        color, hover_color = colors.get(message_type, colors["info"])
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.message_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Corps du message
        message_text = ctk.CTkTextbox(
            main_frame,
            width=400,
            height=150,
            wrap="word"
        )
        message_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        message_text.insert("1.0", body)
        message_text.configure(state="disabled")
        
        # Bouton pour fermer
        def close_dialog():
            self.message_dialog.destroy()
            self.message_dialog = None
        
        close_button = ctk.CTkButton(
            main_frame,
            text="OK",
            width=100,
            height=35,
            fg_color=color,
            hover_color=hover_color,
            command=close_dialog
        )
        close_button.pack(pady=15)
    
    def show_changelog(self) -> None:
        """
        Affiche le changelog complet.
        """
        # Éviter d'afficher plusieurs dialogues en même temps
        if self.changelog_dialog is not None:
            try:
                self.changelog_dialog.destroy()
            except Exception:
                pass
            self.changelog_dialog = None
        
        # Récupérer le changelog
        changelog = self.remote_config.get_full_changelog()
        
        if not changelog:
            # Informer l'utilisateur
            DialogUtils.show_message(
                self.parent,
                "Changelog",
                "Aucune information disponible sur les versions.",
                "info"
            )
            return
        
        # Créer le dialogue de changelog
        self.changelog_dialog = ctk.CTkToplevel(self.parent)
        self.changelog_dialog.title("Historique des versions")
        self.changelog_dialog.geometry("700x500")
        self.changelog_dialog.resizable(True, True)
        self.changelog_dialog.minsize(500, 400)
        self.changelog_dialog.transient(self.parent)
        self.changelog_dialog.grab_set()
        
        # Centrer le dialogue
        self.changelog_dialog.update_idletasks()
        x = (self.changelog_dialog.winfo_screenwidth() - self.changelog_dialog.winfo_width()) // 2
        y = (self.changelog_dialog.winfo_screenheight() - self.changelog_dialog.winfo_height()) // 2
        self.changelog_dialog.geometry(f"+{x}+{y}")
        
        # Frame principal avec défilement
        main_frame = ctk.CTkScrollableFrame(self.changelog_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text="📋 Historique des versions",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Créer une entrée pour chaque version
        for entry in changelog:
            # Créer un cadre pour chaque version
            version_frame = ctk.CTkFrame(main_frame)
            version_frame.pack(fill=tk.X, pady=10, padx=5)
            
            # En-tête de version
            header_frame = ctk.CTkFrame(version_frame, fg_color=("gray85", "gray25"))
            header_frame.pack(fill=tk.X, pady=0)
            
            # Version et date
            version_text = f"Version {entry.get('version', 'Inconnue')}"
            if "date" in entry:
                version_text += f" - {entry['date']}"
            
            version_label = ctk.CTkLabel(
                header_frame,
                text=version_text,
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            )
            version_label.pack(fill=tk.X, padx=10, pady=5)
            
            # Notes de version
            notes_frame = ctk.CTkFrame(version_frame, fg_color="transparent")
            notes_frame.pack(fill=tk.X, padx=10, pady=10)
            
            notes_text = ctk.CTkTextbox(
                notes_frame,
                height=100,
                wrap="word"
            )
            notes_text.pack(fill=tk.BOTH, expand=True)
            notes_text.insert("1.0", entry.get("notes", "Aucune information disponible"))
            notes_text.configure(state="disabled")
        
        # Bouton pour fermer
        close_button = ctk.CTkButton(
            self.changelog_dialog,
            text="Fermer",
            width=100,
            height=35,
            command=lambda: self.changelog_dialog.destroy()
        )
        close_button.pack(pady=15)
    
    def show_support_info(self) -> None:
        """
        Affiche les informations de support.
        """
        # Récupérer les informations de support
        support_info = self.remote_config.get_support_info()
        
        if not support_info:
            # Informer l'utilisateur
            DialogUtils.show_message(
                self.parent,
                "Support",
                "Aucune information de support disponible.",
                "info"
            )
            return
        
        # Créer le dialogue de support
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Support")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Centrer le dialogue
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text="🛟 Support technique",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Informations de support
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill=tk.X, pady=10)
        
        # Email de support
        if "email" in support_info:
            email_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            email_frame.pack(fill=tk.X, pady=5)
            
            ctk.CTkLabel(
                email_frame,
                text="Email:",
                font=ctk.CTkFont(weight="bold"),
                width=100
            ).pack(side=tk.LEFT, padx=10)
            
            email_value = ctk.CTkLabel(
                email_frame,
                text=support_info["email"],
                cursor="hand2",
                text_color=("#3498db", "#3498db")
            )
            email_value.pack(side=tk.LEFT, padx=10)
            
            # Configurer l'email comme un lien
            email_value.bind("<Button-1>", lambda e: webbrowser.open(f"mailto:{support_info['email']}"))
        
        # URL de support
        if "url" in support_info:
            url_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            url_frame.pack(fill=tk.X, pady=5)
            
            ctk.CTkLabel(
                url_frame,
                text="Site web:",
                font=ctk.CTkFont(weight="bold"),
                width=100
            ).pack(side=tk.LEFT, padx=10)
            
            url_value = ctk.CTkLabel(
                url_frame,
                text=support_info["url"],
                cursor="hand2",
                text_color=("#3498db", "#3498db")
            )
            url_value.pack(side=tk.LEFT, padx=10)
            
            # Configurer l'URL comme un lien
            url_value.bind("<Button-1>", lambda e: webbrowser.open(support_info["url"]))
        
        # Bouton pour fermer
        close_button = ctk.CTkButton(
            main_frame,
            text="Fermer",
            width=100,
            height=35,
            command=lambda: dialog.destroy()
        )
        close_button.pack(pady=15)
    
    def update_status(self) -> None:
        """
        Met à jour la barre de statut avec les informations actuelles.
        """
        if not self.status_bar or not self.status_label:
            return
        
        try:
            # Vérifier si une mise à jour est disponible
            update_available, update_info = self.remote_config.update_is_available()
            
            if update_available:
                version = update_info.get("latest_version", "inconnue")
                self.status_label.configure(
                    text=f"Mise à jour disponible: v{version}",
                    text_color=("#3498db", "#3498db"),
                    cursor="hand2"
                )
                # Configurer le label comme un lien
                self.status_label.bind("<Button-1>", lambda e: self.show_update_notification(update_info))
            else:
                # Vérifier si un message global est disponible
                message = self.remote_config.get_global_message()
                
                if message:
                    self.status_label.configure(
                        text=f"Message: {message.get('title', '')}",
                        text_color=("#3498db", "#3498db"),
                        cursor="hand2"
                    )
                    # Configurer le label comme un lien
                    self.status_label.bind("<Button-1>", lambda e: self.show_global_message(message))
                else:
                    self.status_label.configure(
                        text="Application à jour",
                        text_color=("gray50", "gray50"),
                        cursor=""
                    )
                    # Supprimer le lien
                    self.status_label.unbind("<Button-1>")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {e}")
            self.status_label.configure(
                text="Erreur de mise à jour",
                text_color=("#e74c3c", "#e74c3c"),
                cursor=""
            )
            # Supprimer le lien
            self.status_label.unbind("<Button-1>") 
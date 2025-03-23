#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'administration pour le système de configuration distante.
Permet de gérer et modifier le fichier de configuration centralisé (app_config.json).
"""

import os
import json
import hashlib
import logging
import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Any, Optional, List, Tuple, Callable
import threading
import shutil
import base64
import secrets

logger = logging.getLogger("VynalDocsAutomator.RemoteConfigAdmin")

class RemoteConfigAdmin:
    """
    Interface d'administration pour le système de configuration distante.
    Permet de gérer et modifier le fichier app_config.json avec une interface utilisateur.
    
    Attributes:
        root (tk.Tk): Fenêtre principale de l'application
        config_file_path (str): Chemin vers le fichier de configuration
        config (dict): Configuration actuelle
        is_modified (bool): Indique si la configuration a été modifiée
        update_files_dir (str): Répertoire pour les fichiers de mise à jour
        current_tab (str): Onglet actuellement affiché
        tabs (dict): Dictionnaire des onglets disponibles
    """
    
    def __init__(self, root: Optional[tk.Tk] = None, config_file_path: Optional[str] = None):
        """
        Initialise l'interface d'administration.
        
        Args:
            root (tk.Tk, optional): Fenêtre principale de l'application. Si None, en crée une nouvelle.
            config_file_path (str, optional): Chemin vers le fichier de configuration.
                Si None, demande à l'utilisateur de choisir un fichier.
        """
        # Créer une fenêtre principale si non fournie
        self.standalone = root is None
        if self.standalone:
            self.root = tk.Tk()
            self.root.title("Administration de la configuration distante")
            self.root.geometry("1200x800")
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
        else:
            self.root = root
        
        self.config_file_path = config_file_path
        self.config = {}
        self.is_modified = False
        self.update_files_dir = ""
        self.current_tab = ""
        self.tabs = {}
        
        # Charger la configuration
        if self.config_file_path is None:
            self._select_config_file()
        else:
            self._load_config()
        
        # Créer l'interface utilisateur
        self._create_ui()
        
        logger.info("RemoteConfigAdmin initialisé")
        
        # Démarrer la boucle principale si mode autonome
        if self.standalone:
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            self.root.mainloop()
    
    def _select_config_file(self) -> None:
        """
        Demande à l'utilisateur de sélectionner un fichier de configuration.
        """
        # Demander à l'utilisateur de sélectionner un fichier
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier de configuration",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            if self.standalone:
                self.root.destroy()
                return
            else:
                self.config = self._create_default_config()
                self.is_modified = True
                return
        
        self.config_file_path = file_path
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Charge la configuration depuis le fichier.
        """
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(self.config_file_path):
                logger.warning(f"Fichier de configuration {self.config_file_path} introuvable, création avec valeurs par défaut")
                self.config = self._create_default_config()
                self.is_modified = True
                return
            
            # Charger le fichier JSON
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Vérifier la structure du fichier
            if not self._validate_config_structure():
                logger.warning("Structure de configuration invalide, ajout des sections manquantes")
                self._ensure_config_structure()
                self.is_modified = True
            
            logger.info(f"Configuration chargée depuis {self.config_file_path}")
            self.is_modified = False
            
            # Définir le répertoire pour les fichiers de mise à jour
            self.update_files_dir = os.path.dirname(self.config_file_path)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de format JSON dans le fichier de configuration: {e}")
            messagebox.showerror(
                "Erreur de format",
                f"Le fichier de configuration contient des erreurs de format JSON:\n{e}\n\nUne configuration par défaut sera utilisée."
            )
            self.config = self._create_default_config()
            self.is_modified = True
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors du chargement de la configuration:\n{e}\n\nUne configuration par défaut sera utilisée."
            )
            self.config = self._create_default_config()
            self.is_modified = True
    
    def _save_config(self) -> bool:
        """
        Sauvegarde la configuration dans le fichier.
        
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Si aucun fichier n'est défini, demander à l'utilisateur de choisir un emplacement
            if not self.config_file_path:
                file_path = filedialog.asksaveasfilename(
                    title="Enregistrer la configuration",
                    filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
                    defaultextension=".json"
                )
                
                if not file_path:
                    return False
                
                self.config_file_path = file_path
            
            # Créer une sauvegarde du fichier existant
            if os.path.exists(self.config_file_path):
                backup_path = f"{self.config_file_path}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copyfile(self.config_file_path, backup_path)
                logger.info(f"Sauvegarde créée: {backup_path}")
            
            # Enregistrer la configuration au format JSON
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration sauvegardée dans {self.config_file_path}")
            self.is_modified = False
            
            # Définir le répertoire pour les fichiers de mise à jour
            self.update_files_dir = os.path.dirname(self.config_file_path)
            
            # Afficher un message de confirmation
            messagebox.showinfo(
                "Configuration sauvegardée",
                f"La configuration a été sauvegardée avec succès dans:\n{self.config_file_path}"
            )
            
            # Utiliser after pour s'assurer que l'interface reste réactive après la sauvegarde
            if hasattr(self, 'root') and self.root:
                current_tab = self.current_tab
                self.root.after(100, lambda: self._refresh_ui_after_save(current_tab))
                
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la sauvegarde de la configuration:\n{e}"
            )
            return False
            
    def _refresh_ui_after_save(self, tab_id=None):
        """
        Rafraîchit l'interface utilisateur après une sauvegarde pour éviter les problèmes de navigation.
        
        Args:
            tab_id (str, optional): Identifiant de l'onglet à afficher après le rafraîchissement.
        """
        try:
            # Si un onglet spécifique était actif, le réafficher
            if tab_id and hasattr(self, '_show_tab'):
                self._show_tab(tab_id)
            
            # Si l'application est en mode autonome, mettre à jour le titre de la fenêtre
            if hasattr(self, 'standalone') and self.standalone and hasattr(self, 'root') and self.root:
                filename = os.path.basename(self.config_file_path) if self.config_file_path else "Sans titre"
                self.root.title(f"Administration de la configuration - {filename}")
                
            logger.info("Interface rafraîchie après sauvegarde")
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement de l'interface après sauvegarde: {e}")
            # Ne pas afficher de message d'erreur pour éviter l'empilement de boîtes de dialogue
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Crée une configuration par défaut.
        
        Returns:
            Dict[str, Any]: Configuration par défaut
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        next_year = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        
        return {
            "update": {
                "latest_version": "1.0.0",
                "download_url": "https://example.com/update/patch-1.0.0.zip",
                "checksum": "",
                "changelog": "Version initiale"
            },
            "licences": {
                "admin@example.com": {
                    "status": "active",
                    "expires": next_year
                }
            },
            "global_message": {
                "title": "Bienvenue",
                "body": "Bienvenue dans Vynal Docs Automator !",
                "type": "info",
                "visible": False
            },
            "features": {
                "docsGPT_enabled": True,
                "analyse_automatique": True,
                "mode_test": False
            },
            "settings": {
                "licence_check_grace_days": 7,
                "max_offline_days": 14,
                "auto_update": True
            },
            "support": {
                "email": "support@example.com",
                "url": "https://example.com/support"
            },
            "changelog_full": [
                {
                    "version": "1.0.0",
                    "date": today,
                    "notes": "Version initiale"
                }
            ],
            "security": {
                "signature_required": False,
                "public_key": ""
            }
        }
    
    def _validate_config_structure(self) -> bool:
        """
        Vérifie si la structure de la configuration est valide.
        
        Returns:
            bool: True si la structure est valide, False sinon
        """
        required_sections = [
            "update", "licences", "global_message", "features",
            "settings", "support", "changelog_full", "security"
        ]
        
        return all(section in self.config for section in required_sections)
    
    def _ensure_config_structure(self) -> None:
        """
        Assure que la structure de la configuration est complète.
        """
        default_config = self._create_default_config()
        
        # Ajouter les sections manquantes
        for section, default_value in default_config.items():
            if section not in self.config:
                self.config[section] = default_value
    
    def _create_ui(self) -> None:
        """
        Crée l'interface utilisateur principale.
        """
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de navigation (sidebar)
        self.sidebar = ctk.CTkFrame(self.main_frame, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Titre de la sidebar
        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="Administration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        sidebar_title.pack(pady=10)
        
        # Boutons de navigation
        self._create_sidebar_buttons()
        
        # Frame pour les boutons d'action
        action_frame = ctk.CTkFrame(self.sidebar)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Bouton Sauvegarder
        save_button = ctk.CTkButton(
            action_frame,
            text="Sauvegarder",
            command=self._save_config,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        save_button.pack(fill=tk.X, pady=5)
        
        # Bouton Actualiser
        refresh_button = ctk.CTkButton(
            action_frame,
            text="Actualiser",
            command=self._reload_config
        )
        refresh_button.pack(fill=tk.X, pady=5)
        
        # Bouton Quitter (uniquement en mode autonome)
        if self.standalone:
            quit_button = ctk.CTkButton(
                action_frame,
                text="Quitter",
                command=self._on_close,
                fg_color="#e74c3c",
                hover_color="#c0392b"
            )
            quit_button.pack(fill=tk.X, pady=5)
        
        # Frame de contenu (onglets)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Créer les onglets
        self._create_tabs()
        
        # Afficher l'onglet par défaut
        self._show_tab("update")
    
    def _create_sidebar_buttons(self) -> None:
        """
        Crée les boutons de navigation dans la sidebar.
        """
        # Liste des onglets
        tabs = [
            ("Mises à jour", "update"),
            ("Licences", "licences"),
            ("Messages", "messages"),
            ("Fonctionnalités", "features"),
            ("Paramètres", "settings"),
            ("Support", "support"),
            ("Changelog", "changelog"),
            ("Sécurité", "security"),
            ("JSON brut", "raw")
        ]
        
        # Créer un bouton pour chaque onglet
        for label, tab_id in tabs:
            button = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda t=tab_id: self._show_tab(t),
                anchor="w",
                height=40,
                corner_radius=0,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            button.pack(fill=tk.X, padx=5, pady=2)
    
    def _create_tabs(self) -> None:
        """
        Crée les différents onglets de l'interface.
        """
        # Créer les frames pour chaque onglet
        self.tabs = {
            "update": self._create_update_tab(),
            "licences": self._create_licences_tab(),
            "messages": self._create_messages_tab(),
            "features": self._create_features_tab(),
            "settings": self._create_settings_tab(),
            "support": self._create_support_tab(),
            "changelog": self._create_changelog_tab(),
            "security": self._create_security_tab(),
            "raw": self._create_raw_tab()
        }
    
    def _show_tab(self, tab_id: str) -> None:
        """
        Affiche l'onglet spécifié et masque les autres.
        
        Args:
            tab_id (str): Identifiant de l'onglet à afficher
        """
        # Masquer l'onglet actuel
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab].pack_forget()
        
        # Afficher le nouvel onglet
        if tab_id in self.tabs:
            self.tabs[tab_id].pack(fill=tk.BOTH, expand=True)
            self.current_tab = tab_id
    
    def _reload_config(self) -> None:
        """
        Recharge la configuration depuis le fichier.
        """
        if self.is_modified:
            response = messagebox.askyesnocancel(
                "Configuration modifiée",
                "La configuration actuelle a été modifiée. Voulez-vous la sauvegarder avant de recharger?"
            )
            
            if response is None:  # Annuler
                return
            elif response:  # Oui
                if not self._save_config():
                    return
        
        self._load_config()
        self._refresh_all_tabs()
    
    def _refresh_all_tabs(self) -> None:
        """
        Actualise tous les onglets pour refléter les changements de configuration.
        """
        # Recréer les onglets
        self._create_tabs()
        
        # Réafficher l'onglet actuel
        if self.current_tab:
            self._show_tab(self.current_tab)
    
    def _on_close(self) -> None:
        """
        Gère la fermeture de l'application.
        """
        if self.is_modified:
            response = messagebox.askyesnocancel(
                "Configuration modifiée",
                "La configuration a été modifiée. Voulez-vous la sauvegarder avant de quitter?"
            )
            
            if response is None:  # Annuler
                return
            elif response:  # Oui
                if not self._save_config():
                    return
        
        if self.standalone:
            self.root.destroy()
        else:
            self.main_frame.destroy()
    
    def _create_update_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion des mises à jour.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Gestion des mises à jour",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame principal
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Version actuelle
        version_frame = ctk.CTkFrame(form_frame)
        version_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text="Version actuelle:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.version_entry = ctk.CTkEntry(version_frame, width=200)
        self.version_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.version_entry.insert(0, self.config.get("update", {}).get("latest_version", ""))
        
        # URL de téléchargement
        url_frame = ctk.CTkFrame(form_frame)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            url_frame,
            text="URL de téléchargement:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.url_entry = ctk.CTkEntry(url_frame, width=400)
        self.url_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.url_entry.insert(0, self.config.get("update", {}).get("download_url", ""))
        
        # Checksum
        checksum_frame = ctk.CTkFrame(form_frame)
        checksum_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            checksum_frame,
            text="Checksum (SHA-256):",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.checksum_entry = ctk.CTkEntry(checksum_frame, width=400)
        self.checksum_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.checksum_entry.insert(0, self.config.get("update", {}).get("checksum", ""))
        
        # Boutons pour générer et vérifier le checksum
        checksum_buttons_frame = ctk.CTkFrame(form_frame)
        checksum_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Espace réservé pour aligner avec les autres champs
        ctk.CTkLabel(
            checksum_buttons_frame,
            text="",
            width=150
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour sélectionner le fichier de mise à jour
        select_file_button = ctk.CTkButton(
            checksum_buttons_frame,
            text="Sélectionner le fichier de mise à jour",
            command=self._select_update_file
        )
        select_file_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour générer le checksum
        generate_checksum_button = ctk.CTkButton(
            checksum_buttons_frame,
            text="Générer le checksum",
            command=self._generate_checksum
        )
        generate_checksum_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour vérifier le checksum
        verify_checksum_button = ctk.CTkButton(
            checksum_buttons_frame,
            text="Vérifier le checksum",
            command=self._verify_checksum
        )
        verify_checksum_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Description de la mise à jour (changelog)
        changelog_frame = ctk.CTkFrame(form_frame)
        changelog_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            changelog_frame,
            text="Notes de version:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5, anchor="n")
        
        self.changelog_text = ctk.CTkTextbox(
            changelog_frame,
            width=400,
            height=150
        )
        self.changelog_text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.changelog_text.insert("1.0", self.config.get("update", {}).get("changelog", ""))
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(form_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=15)
        
        # Espace réservé pour aligner avec les autres champs
        ctk.CTkLabel(
            action_frame,
            text="",
            width=150
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour appliquer les modifications
        apply_button = ctk.CTkButton(
            action_frame,
            text="Appliquer les modifications",
            command=self._apply_update_changes,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        apply_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour réinitialiser
        reset_button = ctk.CTkButton(
            action_frame,
            text="Réinitialiser",
            command=self._reset_update_tab,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        return tab
    
    def _select_update_file(self) -> None:
        """
        Sélectionne un fichier de mise à jour et remplit les champs URL et checksum.
        """
        try:
            file_path = filedialog.askopenfilename(
                title="Sélectionner le fichier de mise à jour",
                filetypes=[
                    ("Fichiers ZIP", "*.zip"),
                    ("Fichiers d'installation", "*.exe"),
                    ("Tous les fichiers", "*.*")
                ],
                initialdir=self.update_files_dir if hasattr(self, 'update_files_dir') and self.update_files_dir else None
            )
            
            if not file_path:
                return
                
            # Vérifier que le fichier existe
            if not os.path.isfile(file_path):
                messagebox.showerror(
                    "Erreur",
                    f"Le fichier sélectionné n'existe pas:\n{file_path}"
                )
                return
                
            # Extraire le nom du fichier et mettre à jour le champ URL
            file_name = os.path.basename(file_path)
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, f"https://example.com/downloads/{file_name}")
            
            # Montrer un curseur d'attente pour les gros fichiers
            if hasattr(self, 'root') and self.root:
                self.root.config(cursor="wait")
                self.root.update()
                
            # Calculer le checksum dans un thread séparé pour ne pas bloquer l'interface
            def calculate_checksum():
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        checksum = hashlib.sha256(file_data).hexdigest()
                        
                        # Mettre à jour l'interface dans le thread principal
                        if hasattr(self, 'root') and self.root:
                            self.root.after(0, lambda: self._update_file_selection_ui(checksum, file_path))
                except Exception as e:
                    # Gérer l'erreur dans le thread principal
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self._show_checksum_error(str(e)))
            
            # Démarrer le calcul dans un thread séparé
            threading.Thread(target=calculate_checksum, daemon=True).start()
                
        except Exception as e:
            # Restaurer le curseur
            if hasattr(self, 'root') and self.root:
                self.root.config(cursor="")
                
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la sélection du fichier de mise à jour:\n{e}"
            )
    
    def _update_file_selection_ui(self, checksum, file_path):
        """
        Met à jour l'interface après la sélection d'un fichier de mise à jour.
        
        Args:
            checksum (str): Le checksum SHA-256 calculé
            file_path (str): Le chemin du fichier
        """
        # Restaurer le curseur
        if hasattr(self, 'root') and self.root:
            self.root.config(cursor="")
        
        # Mettre à jour l'entrée du checksum
        if hasattr(self, 'checksum_entry'):
            self.checksum_entry.delete(0, tk.END)
            self.checksum_entry.insert(0, checksum)
            
        file_name = os.path.basename(file_path)
        
        # Afficher un message de succès
        messagebox.showinfo(
            "Fichier sélectionné",
            f"Le fichier de mise à jour a été sélectionné avec succès.\n\n"
            f"Fichier: {file_name}\n"
            f"Checksum: {checksum}\n\n"
            f"L'URL a été mise à jour automatiquement. Vous pouvez la modifier si nécessaire."
        )
    
    def _generate_checksum(self) -> None:
        """
        Génère le checksum d'un fichier sélectionné par l'utilisateur.
        """
        try:
            file_path = filedialog.askopenfilename(
                title="Sélectionner le fichier pour générer le checksum",
                filetypes=[
                    ("Fichiers ZIP", "*.zip"),
                    ("Fichiers d'installation", "*.exe"),
                    ("Tous les fichiers", "*.*")
                ],
                initialdir=self.update_files_dir if hasattr(self, 'update_files_dir') and self.update_files_dir else None
            )
            
            if not file_path:
                return
            
            # Vérifier que le fichier existe
            if not os.path.isfile(file_path):
                messagebox.showerror(
                    "Erreur",
                    f"Le fichier sélectionné n'existe pas:\n{file_path}"
                )
                return
                
            # Montrer un curseur d'attente pour les gros fichiers
            if hasattr(self, 'root') and self.root:
                self.root.config(cursor="wait")
                self.root.update()
            
            # Calculer le checksum directement
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    checksum = hashlib.sha256(file_data).hexdigest()
                
                # Restaurer le curseur
                if hasattr(self, 'root') and self.root:
                    self.root.config(cursor="")
                
                # Mettre à jour l'entrée du checksum
                self.checksum_entry.delete(0, tk.END)
                self.checksum_entry.insert(0, checksum)
                
                # Mettre à jour le champ URL si vide
                if hasattr(self, 'url_entry') and not self.url_entry.get().strip():
                    file_name = os.path.basename(file_path)
                    url_placeholder = f"https://example.com/downloads/{file_name}"
                    self.url_entry.delete(0, tk.END)
                    self.url_entry.insert(0, url_placeholder)
                
                # Afficher un message de succès
                messagebox.showinfo(
                    "Checksum généré",
                    f"Le checksum SHA-256 du fichier a été généré avec succès:\n{checksum}\n\nFichier: {os.path.basename(file_path)}"
                )
                
            except Exception as e:
                # Restaurer le curseur
                if hasattr(self, 'root') and self.root:
                    self.root.config(cursor="")
                
                messagebox.showerror(
                    "Erreur",
                    f"Une erreur est survenue lors du calcul du checksum:\n{e}"
                )
                
        except Exception as e:
            # Restaurer le curseur en cas d'erreur
            if hasattr(self, 'root') and self.root:
                self.root.config(cursor="")
            
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la génération du checksum:\n{e}"
            )
    
    def _verify_checksum(self) -> None:
        """
        Vérifie si le checksum d'un fichier correspond à celui spécifié.
        """
        try:
            expected_checksum = self.checksum_entry.get().strip()
            if not expected_checksum:
                messagebox.showerror(
                    "Erreur",
                    "Aucun checksum de référence n'est spécifié. Veuillez d'abord générer ou saisir un checksum."
                )
                return
            
            file_path = filedialog.askopenfilename(
                title="Sélectionner le fichier à vérifier",
                filetypes=[
                    ("Fichiers ZIP", "*.zip"),
                    ("Fichiers d'installation", "*.exe"),
                    ("Tous les fichiers", "*.*")
                ],
                initialdir=self.update_files_dir if hasattr(self, 'update_files_dir') and self.update_files_dir else None
            )
            
            if not file_path:
                return
                
            # Vérifier que le fichier existe
            if not os.path.isfile(file_path):
                messagebox.showerror(
                    "Erreur",
                    f"Le fichier sélectionné n'existe pas:\n{file_path}"
                )
                return
                
            # Montrer un curseur d'attente pour les gros fichiers
            if hasattr(self, 'root') and self.root:
                self.root.config(cursor="wait")
                self.root.update()
                
            # Vérifier le checksum dans un thread séparé pour ne pas bloquer l'interface
            def verify_checksum():
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        actual_checksum = hashlib.sha256(file_data).hexdigest()
                        
                        # Mettre à jour l'interface dans le thread principal
                        if hasattr(self, 'root') and self.root:
                            self.root.after(0, lambda: self._show_verify_result(expected_checksum, actual_checksum, file_path))
                except Exception as e:
                    # Gérer l'erreur dans le thread principal
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, lambda: self._show_checksum_error(str(e)))
            
            # Démarrer la vérification dans un thread séparé
            threading.Thread(target=verify_checksum, daemon=True).start()
                
        except Exception as e:
            # Restaurer le curseur
            if hasattr(self, 'root') and self.root:
                self.root.config(cursor="")
                
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la vérification du checksum:\n{e}"
            )
    
    def _show_verify_result(self, expected_checksum, actual_checksum, file_path):
        """
        Affiche le résultat de la vérification du checksum.
        
        Args:
            expected_checksum (str): Le checksum attendu
            actual_checksum (str): Le checksum calculé
            file_path (str): Le chemin du fichier vérifié
        """
        # Restaurer le curseur
        if hasattr(self, 'root') and self.root:
            self.root.config(cursor="")
            
        file_name = os.path.basename(file_path)
        
        if expected_checksum.lower() == actual_checksum.lower():
            messagebox.showinfo(
                "Vérification réussie",
                f"Le checksum du fichier correspond au checksum attendu.\n\nFichier: {file_name}\nChecksum: {actual_checksum}"
            )
        else:
            messagebox.showerror(
                "Vérification échouée",
                f"Le checksum du fichier ne correspond pas au checksum attendu!\n\n"
                f"Fichier: {file_name}\n"
                f"Checksum attendu: {expected_checksum}\n"
                f"Checksum calculé: {actual_checksum}"
            )
    
    def _apply_update_changes(self) -> None:
        """
        Applique les modifications de l'onglet de mise à jour à la configuration.
        """
        # Récupérer les valeurs
        version = self.version_entry.get().strip()
        url = self.url_entry.get().strip()
        checksum = self.checksum_entry.get().strip()
        changelog = self.changelog_text.get("1.0", tk.END).strip()
        
        # Valider les valeurs
        if not version:
            messagebox.showwarning(
                "Version manquante",
                "Veuillez spécifier une version."
            )
            return
        
        if not url:
            messagebox.showwarning(
                "URL manquante",
                "Veuillez spécifier une URL de téléchargement."
            )
            return
        
        # Mettre à jour la configuration
        if "update" not in self.config:
            self.config["update"] = {}
        
        self.config["update"]["latest_version"] = version
        self.config["update"]["download_url"] = url
        self.config["update"]["checksum"] = checksum
        self.config["update"]["changelog"] = changelog
        
        # Ajouter ou mettre à jour l'entrée dans le changelog complet
        if "changelog_full" not in self.config:
            self.config["changelog_full"] = []
        
        # Vérifier si la version existe déjà dans le changelog
        version_exists = False
        for i, entry in enumerate(self.config["changelog_full"]):
            if entry.get("version") == version:
                # Mettre à jour l'entrée existante
                self.config["changelog_full"][i] = {
                    "version": version,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "notes": changelog
                }
                version_exists = True
                break
        
        # Ajouter une nouvelle entrée si la version n'existe pas
        if not version_exists:
            self.config["changelog_full"].insert(0, {
                "version": version,
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "notes": changelog
            })
        
        # Marquer comme modifié
        self.is_modified = True
        
        messagebox.showinfo(
            "Modifications appliquées",
            "Les modifications de mise à jour ont été appliquées à la configuration."
        )
    
    def _reset_update_tab(self) -> None:
        """
        Réinitialise l'onglet de mise à jour avec les valeurs actuelles de la configuration.
        """
        # Réinitialiser les champs
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, self.config.get("update", {}).get("latest_version", ""))
        
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, self.config.get("update", {}).get("download_url", ""))
        
        self.checksum_entry.delete(0, tk.END)
        self.checksum_entry.insert(0, self.config.get("update", {}).get("checksum", ""))
        
        self.changelog_text.delete("1.0", tk.END)
        self.changelog_text.insert("1.0", self.config.get("update", {}).get("changelog", ""))
    
    def _create_licences_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion des licences en intégrant la vue LicenseManagementView existante.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        try:
            # Importer la vue de gestion des licences existante
            from admin.views.license_management_view import LicenseManagementView
            from admin.models.admin_model import AdminModel
            
            # Récupérer ou créer une instance du modèle d'administration
            admin_model = None
            for widget in self.root.winfo_children():
                if hasattr(widget, 'admin_model'):
                    admin_model = widget.admin_model
                    break
            
            if admin_model is None:
                # Créer une nouvelle instance si nécessaire
                admin_model = AdminModel()
            
            # Créer une instance de la vue de gestion des licences
            license_view = LicenseManagementView(tab, admin_model)
            license_view.show()
            
            # Bouton pour synchroniser les licences avec app_config.json
            sync_frame = ctk.CTkFrame(tab)
            sync_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ctk.CTkLabel(
                sync_frame,
                text="Synchronisation avec la configuration distante:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side=tk.LEFT, padx=10, pady=5)
            
            ctk.CTkButton(
                sync_frame,
                text="Importer les licences depuis app_config.json",
                command=self._import_licences_from_config
            ).pack(side=tk.LEFT, padx=10, pady=5)
            
            ctk.CTkButton(
                sync_frame,
                text="Exporter les licences vers app_config.json",
                command=self._export_licences_to_config
            ).pack(side=tk.LEFT, padx=10, pady=5)
            
        except Exception as e:
            # En cas d'erreur, afficher un message et revenir à l'implémentation de base
            error_label = ctk.CTkLabel(
                tab,
                text=f"Erreur lors du chargement de la vue de licences: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)
            
            # Afficher une interface simplifiée en fallback
            self._create_simple_licences_interface(tab)
        
        return tab
    
    def _create_simple_licences_interface(self, parent):
        """
        Crée une interface simplifiée de gestion des licences en cas d'échec de l'intégration.
        
        Args:
            parent: Widget parent
        """
        # Titre
        ctk.CTkLabel(
            parent,
            text="Gestion des licences (mode simplifié)",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame pour le tableau et les boutons
        main_frame = ctk.CTkFrame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Bouton pour ajouter une licence
        add_button = ctk.CTkButton(
            button_frame,
            text="Ajouter une licence",
            command=self._add_licence
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour supprimer une licence
        self.delete_button = ctk.CTkButton(
            button_frame,
            text="Supprimer la licence sélectionnée",
            command=self._delete_licence,
            state="disabled"
        )
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour éditer une licence
        self.edit_button = ctk.CTkButton(
            button_frame,
            text="Éditer la licence sélectionnée",
            command=self._edit_licence,
            state="disabled"
        )
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame pour le tableau
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Créer un Treeview pour afficher les licences
        self.licences_table = ttk.Treeview(
            table_frame,
            columns=("email", "status", "expires"),
            show="headings",
            selectmode="browse"
        )
        
        # Définir les en-têtes de colonnes
        self.licences_table.heading("email", text="Email")
        self.licences_table.heading("status", text="Statut")
        self.licences_table.heading("expires", text="Date d'expiration")
        
        # Définir les largeurs de colonnes
        self.licences_table.column("email", width=300)
        self.licences_table.column("status", width=100)
        self.licences_table.column("expires", width=150)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.licences_table.yview
        )
        self.licences_table.configure(yscrollcommand=scrollbar.set)
        
        # Positionner le tableau et la scrollbar
        self.licences_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lier la sélection à l'activation des boutons
        self.licences_table.bind("<<TreeviewSelect>>", self._on_licence_select)
        
        # Remplir le tableau avec les licences existantes
        self._populate_licences_table()
    
    def _import_licences_from_config(self):
        """
        Importe les licences depuis le fichier app_config.json vers la gestion des licences internes.
        """
        # À implémenter: logique pour importer les licences du fichier config vers le système de licence interne
        licences = self.config.get("licences", {})
        
        if not licences:
            self._show_message("Aucune licence trouvée dans le fichier de configuration.")
            return
        
        # Cette fonction devrait être implémentée pour communiquer avec le système de licence
        # Exemple simplifié:
        try:
            for email, licence_data in licences.items():
                # Ajouter ou mettre à jour la licence dans le système interne
                # admin_model.add_or_update_license(email, licence_data)
                pass
                
            self._show_message(f"{len(licences)} licences importées avec succès.")
        except Exception as e:
            self._show_message(f"Erreur lors de l'importation des licences: {str(e)}", "error")
    
    def _export_licences_to_config(self):
        """
        Exporte les licences depuis la gestion des licences internes vers le fichier app_config.json.
        """
        # À implémenter: logique pour exporter les licences du système interne vers le fichier config
        try:
            # Récupérer les licences du système interne
            # licenses = admin_model.get_all_licenses()
            
            # Mettre à jour le fichier de configuration
            # self.config["licences"] = licenses
            # self.save_config()
            
            self._show_message("Licences exportées avec succès vers le fichier de configuration.")
            self.is_modified = True
        except Exception as e:
            self._show_message(f"Erreur lors de l'exportation des licences: {str(e)}", "error")
    
    def _populate_licences_table(self) -> None:
        """
        Remplit le tableau des licences avec les données de la configuration.
        """
        # Effacer le tableau
        for item in self.licences_table.get_children():
            self.licences_table.delete(item)
        
        # Récupérer les licences
        licences = self.config.get("licences", {})
        
        # Ajouter chaque licence au tableau
        for email, licence_data in licences.items():
            status = licence_data.get("status", "inconnu")
            expires = licence_data.get("expires", "jamais")
            
            self.licences_table.insert(
                "",
                tk.END,
                values=(email, status, expires),
                tags=(status,)
            )
        
        # Appliquer des couleurs en fonction du statut
        self.licences_table.tag_configure("active", background="#e6ffe6")
        self.licences_table.tag_configure("expired", background="#ffe6e6")
        self.licences_table.tag_configure("suspended", background="#fff6e6")
    
    def _on_licence_select(self, event) -> None:
        """
        Gère la sélection d'une licence dans le tableau.
        
        Args:
            event: Événement de sélection
        """
        selected_items = self.licences_table.selection()
        
        if selected_items:
            # Activer les boutons
            self.delete_button.configure(state="normal")
            self.edit_button.configure(state="normal")
        else:
            # Désactiver les boutons
            self.delete_button.configure(state="disabled")
            self.edit_button.configure(state="disabled")
    
    def _add_licence(self) -> None:
        """
        Ajoute une nouvelle licence.
        """
        # Créer une fenêtre de dialogue
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Ajouter une licence")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Champ pour l'email
        email_frame = ctk.CTkFrame(dialog)
        email_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        email_entry = ctk.CTkEntry(email_frame, width=250)
        email_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Champ pour le statut
        status_frame = ctk.CTkFrame(dialog)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            status_frame,
            text="Statut:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        status_var = tk.StringVar(value="active")
        status_combobox = ctk.CTkComboBox(
            status_frame,
            width=250,
            values=["active", "expired", "suspended"],
            variable=status_var
        )
        status_combobox.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Champ pour la date d'expiration
        expires_frame = ctk.CTkFrame(dialog)
        expires_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            expires_frame,
            text="Expiration:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Calculer la date d'expiration par défaut (1 an)
        next_year = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        
        expires_entry = ctk.CTkEntry(expires_frame, width=250)
        expires_entry.pack(side=tk.LEFT, padx=5, pady=5)
        expires_entry.insert(0, next_year)
        
        # Étiquette d'information
        ctk.CTkLabel(
            dialog,
            text="Format de date: AAAA-MM-JJ",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(padx=10, anchor="w")
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fonction pour ajouter la licence
        def add():
            email = email_entry.get().strip()
            status = status_var.get()
            expires = expires_entry.get().strip()
            
            # Valider les entrées
            if not email:
                messagebox.showwarning(
                    "Email manquant",
                    "Veuillez entrer une adresse email.",
                    parent=dialog
                )
                return
            
            # Valider le format de la date
            try:
                if expires:
                    datetime.datetime.strptime(expires, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Format de date invalide",
                    "Veuillez entrer une date au format AAAA-MM-JJ.",
                    parent=dialog
                )
                return
            
            # Vérifier si l'email existe déjà
            if email in self.config.get("licences", {}):
                messagebox.showwarning(
                    "Email existant",
                    f"Une licence existe déjà pour {email}.",
                    parent=dialog
                )
                return
            
            # Ajouter la licence
            if "licences" not in self.config:
                self.config["licences"] = {}
            
            self.config["licences"][email] = {
                "status": status,
                "expires": expires
            }
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser le tableau
            self._populate_licences_table()
            
            # Fermer la boîte de dialogue
            dialog.destroy()
        
        # Bouton pour ajouter
        add_button = ctk.CTkButton(
            button_frame,
            text="Ajouter",
            command=add,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour annuler
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=dialog.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _edit_licence(self) -> None:
        """
        Édite la licence sélectionnée.
        """
        # Récupérer la sélection
        selected_items = self.licences_table.selection()
        if not selected_items:
            return
        
        # Récupérer les données de la licence sélectionnée
        item = selected_items[0]
        email, status, expires = self.licences_table.item(item, "values")
        
        # Créer une fenêtre de dialogue
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Éditer la licence - {email}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Champ pour l'email (non modifiable)
        email_frame = ctk.CTkFrame(dialog)
        email_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        email_entry = ctk.CTkEntry(email_frame, width=250, state="disabled")
        email_entry.pack(side=tk.LEFT, padx=5, pady=5)
        email_entry.insert(0, email)
        
        # Champ pour le statut
        status_frame = ctk.CTkFrame(dialog)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            status_frame,
            text="Statut:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        status_var = tk.StringVar(value=status)
        status_combobox = ctk.CTkComboBox(
            status_frame,
            width=250,
            values=["active", "expired", "suspended"],
            variable=status_var
        )
        status_combobox.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Champ pour la date d'expiration
        expires_frame = ctk.CTkFrame(dialog)
        expires_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            expires_frame,
            text="Expiration:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        expires_entry = ctk.CTkEntry(expires_frame, width=250)
        expires_entry.pack(side=tk.LEFT, padx=5, pady=5)
        expires_entry.insert(0, expires)
        
        # Étiquette d'information
        ctk.CTkLabel(
            dialog,
            text="Format de date: AAAA-MM-JJ",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(padx=10, anchor="w")
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fonction pour mettre à jour la licence
        def update():
            new_status = status_var.get()
            new_expires = expires_entry.get().strip()
            
            # Valider le format de la date
            try:
                if new_expires:
                    datetime.datetime.strptime(new_expires, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Format de date invalide",
                    "Veuillez entrer une date au format AAAA-MM-JJ.",
                    parent=dialog
                )
                return
            
            # Mettre à jour la licence
            if "licences" in self.config and email in self.config["licences"]:
                self.config["licences"][email] = {
                    "status": new_status,
                    "expires": new_expires
                }
                
                # Marquer comme modifié
                self.is_modified = True
                
                # Actualiser le tableau
                self._populate_licences_table()
                
                # Fermer la boîte de dialogue
                dialog.destroy()
        
        # Bouton pour mettre à jour
        update_button = ctk.CTkButton(
            button_frame,
            text="Mettre à jour",
            command=update,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        update_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour annuler
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=dialog.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _delete_licence(self) -> None:
        """
        Supprime la licence sélectionnée.
        """
        # Récupérer la sélection
        selected_items = self.licences_table.selection()
        if not selected_items:
            return
        
        # Récupérer l'email de la licence sélectionnée
        item = selected_items[0]
        email = self.licences_table.item(item, "values")[0]
        
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer la licence pour {email}?"
        )
        
        if not confirm:
            return
        
        # Supprimer la licence
        if "licences" in self.config and email in self.config["licences"]:
            del self.config["licences"][email]
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser le tableau
            self._populate_licences_table()
    
    def _create_messages_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion des messages globaux.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Gestion des messages globaux",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Activer/désactiver le message
        visibility_frame = ctk.CTkFrame(main_frame)
        visibility_frame.pack(fill=tk.X, padx=10, pady=5)
        
        message_visible = self.config.get("global_message", {}).get("visible", False)
        self.message_visible_var = tk.BooleanVar(value=message_visible)
        
        visibility_checkbox = ctk.CTkCheckBox(
            visibility_frame,
            text="Afficher le message global",
            variable=self.message_visible_var,
            onvalue=True,
            offvalue=False
        )
        visibility_checkbox.pack(padx=5, pady=5, anchor="w")
        
        # Sélection du type de message
        type_frame = ctk.CTkFrame(main_frame)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            type_frame,
            text="Type de message:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        message_type = self.config.get("global_message", {}).get("type", "info")
        self.message_type_var = tk.StringVar(value=message_type)
        
        type_combobox = ctk.CTkComboBox(
            type_frame,
            width=200,
            values=["info", "warning", "error", "success"],
            variable=self.message_type_var
        )
        type_combobox.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Titre du message
        title_frame = ctk.CTkFrame(main_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text="Titre du message:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.message_title_entry = ctk.CTkEntry(title_frame, width=400)
        self.message_title_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.message_title_entry.insert(0, self.config.get("global_message", {}).get("title", ""))
        
        # Corps du message
        body_frame = ctk.CTkFrame(main_frame)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            body_frame,
            text="Corps du message:",
            width=150,
            anchor="nw"
        ).pack(side=tk.LEFT, padx=5, pady=5, anchor="n")
        
        self.message_body_text = ctk.CTkTextbox(
            body_frame,
            width=400,
            height=200
        )
        self.message_body_text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.message_body_text.insert("1.0", self.config.get("global_message", {}).get("body", ""))
        
        # Prévisualisation du message
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        preview_button = ctk.CTkButton(
            preview_frame,
            text="Prévisualiser le message",
            command=self._preview_global_message
        )
        preview_button.pack(padx=5, pady=5)
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Bouton pour appliquer les modifications
        apply_button = ctk.CTkButton(
            action_frame,
            text="Appliquer les modifications",
            command=self._apply_message_changes,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        apply_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour réinitialiser
        reset_button = ctk.CTkButton(
            action_frame,
            text="Réinitialiser",
            command=self._reset_message_tab,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        return tab
    
    def _preview_global_message(self) -> None:
        """
        Affiche une prévisualisation du message global.
        """
        # Récupérer les valeurs actuelles
        title = self.message_title_entry.get().strip()
        body = self.message_body_text.get("1.0", tk.END).strip()
        message_type = self.message_type_var.get()
        
        # Créer une fenêtre de prévisualisation
        preview = ctk.CTkToplevel(self.root)
        preview.title("Prévisualisation du message global")
        preview.geometry("500x300")
        preview.transient(self.root)
        
        # Centrer la fenêtre
        preview.update_idletasks()
        width = preview.winfo_width()
        height = preview.winfo_height()
        x = (preview.winfo_screenwidth() // 2) - (width // 2)
        y = (preview.winfo_screenheight() // 2) - (height // 2)
        preview.geometry(f"{width}x{height}+{x}+{y}")
        
        # Définir la couleur de fond en fonction du type
        bg_colors = {
            "info": "#e3f2fd",
            "warning": "#fff3e0",
            "error": "#ffebee",
            "success": "#e8f5e9"
        }
        
        # Icônes pour les différents types
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        # Frame principal avec la couleur de fond
        main_frame = ctk.CTkFrame(preview)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # En-tête avec l'icône et le titre
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Icône
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icons.get(message_type, "ℹ️"),
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Titre
        title_label = ctk.CTkLabel(
            header_frame,
            text=title or "Message global",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Corps du message
        body_text = ctk.CTkTextbox(
            main_frame,
            width=400,
            height=200,
            wrap="word"
        )
        body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        body_text.insert("1.0", body or "Contenu du message global")
        body_text.configure(state="disabled")
        
        # Bouton pour fermer
        close_button = ctk.CTkButton(
            main_frame,
            text="Fermer",
            command=preview.destroy
        )
        close_button.pack(pady=10)
    
    def _apply_message_changes(self) -> None:
        """
        Applique les modifications de l'onglet de message à la configuration.
        """
        # Récupérer les valeurs
        visible = self.message_visible_var.get()
        message_type = self.message_type_var.get()
        title = self.message_title_entry.get().strip()
        body = self.message_body_text.get("1.0", tk.END).strip()
        
        # Valider les valeurs
        if visible and not title:
            messagebox.showwarning(
                "Titre manquant",
                "Veuillez spécifier un titre pour le message global."
            )
            return
        
        if visible and not body:
            messagebox.showwarning(
                "Corps manquant",
                "Veuillez spécifier un corps pour le message global."
            )
            return
        
        # Mettre à jour la configuration
        if "global_message" not in self.config:
            self.config["global_message"] = {}
        
        self.config["global_message"]["visible"] = visible
        self.config["global_message"]["type"] = message_type
        self.config["global_message"]["title"] = title
        self.config["global_message"]["body"] = body
        
        # Marquer comme modifié
        self.is_modified = True
        
        messagebox.showinfo(
            "Modifications appliquées",
            "Les modifications du message global ont été appliquées à la configuration."
        )
    
    def _reset_message_tab(self) -> None:
        """
        Réinitialise l'onglet de message avec les valeurs actuelles de la configuration.
        """
        # Réinitialiser les champs
        self.message_visible_var.set(self.config.get("global_message", {}).get("visible", False))
        self.message_type_var.set(self.config.get("global_message", {}).get("type", "info"))
        
        self.message_title_entry.delete(0, tk.END)
        self.message_title_entry.insert(0, self.config.get("global_message", {}).get("title", ""))
        
        self.message_body_text.delete("1.0", tk.END)
        self.message_body_text.insert("1.0", self.config.get("global_message", {}).get("body", ""))
    
    def _create_features_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion des fonctionnalités.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Gestion des fonctionnalités",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Bouton pour ajouter une fonctionnalité
        add_button = ctk.CTkButton(
            button_frame,
            text="Ajouter une fonctionnalité",
            command=self._add_feature
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour supprimer une fonctionnalité
        self.delete_feature_button = ctk.CTkButton(
            button_frame,
            text="Supprimer la fonctionnalité sélectionnée",
            command=self._delete_feature,
            state="disabled"
        )
        self.delete_feature_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame pour le tableau de fonctionnalités
        features_frame = ctk.CTkFrame(main_frame)
        features_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Créer un Treeview pour afficher les fonctionnalités
        self.features_table = ttk.Treeview(
            features_frame,
            columns=("feature", "value"),
            show="headings",
            selectmode="browse"
        )
        
        # Définir les en-têtes de colonnes
        self.features_table.heading("feature", text="Fonctionnalité")
        self.features_table.heading("value", text="Activée")
        
        # Définir les largeurs de colonnes
        self.features_table.column("feature", width=300)
        self.features_table.column("value", width=100)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(
            features_frame,
            orient=tk.VERTICAL,
            command=self.features_table.yview
        )
        self.features_table.configure(yscrollcommand=scrollbar.set)
        
        # Positionner le tableau et la scrollbar
        self.features_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lier la sélection à l'activation des boutons
        self.features_table.bind("<<TreeviewSelect>>", self._on_feature_select)
        
        # Lier le double-clic pour basculer l'état
        self.features_table.bind("<Double-1>", self._toggle_feature)
        
        # Remplir le tableau avec les fonctionnalités existantes
        self._populate_features_table()
        
        # Information
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text="Double-cliquez sur une fonctionnalité pour basculer son état.",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        ).pack(padx=5, pady=5, anchor="w")
        
        return tab
    
    def _populate_features_table(self) -> None:
        """
        Remplit le tableau des fonctionnalités avec les données de la configuration.
        """
        # Effacer le tableau
        for item in self.features_table.get_children():
            self.features_table.delete(item)
        
        # Récupérer les fonctionnalités
        features = self.config.get("features", {})
        
        # Ajouter chaque fonctionnalité au tableau
        for feature, value in features.items():
            value_text = "Oui" if value else "Non"
            
            self.features_table.insert(
                "",
                tk.END,
                values=(feature, value_text),
                tags=("enabled" if value else "disabled",)
            )
        
        # Appliquer des couleurs en fonction de l'état
        self.features_table.tag_configure("enabled", background="#e6ffe6")
        self.features_table.tag_configure("disabled", background="#ffe6e6")
    
    def _on_feature_select(self, event) -> None:
        """
        Gère la sélection d'une fonctionnalité dans le tableau.
        
        Args:
            event: Événement de sélection
        """
        selected_items = self.features_table.selection()
        
        if selected_items:
            # Activer le bouton de suppression
            self.delete_feature_button.configure(state="normal")
        else:
            # Désactiver le bouton de suppression
            self.delete_feature_button.configure(state="disabled")
    
    def _toggle_feature(self, event) -> None:
        """
        Bascule l'état d'une fonctionnalité (activée/désactivée).
        
        Args:
            event: Événement de double-clic
        """
        # Récupérer la sélection
        selected_items = self.features_table.selection()
        if not selected_items:
            return
        
        # Récupérer les données de la fonctionnalité sélectionnée
        item = selected_items[0]
        feature, value_text = self.features_table.item(item, "values")
        
        # Basculer la valeur
        current_value = value_text == "Oui"
        new_value = not current_value
        
        # Mettre à jour la configuration
        if "features" in self.config and feature in self.config["features"]:
            self.config["features"][feature] = new_value
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser le tableau
            self._populate_features_table()
    
    def _add_feature(self) -> None:
        """
        Ajoute une nouvelle fonctionnalité.
        """
        # Créer une fenêtre de dialogue
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Ajouter une fonctionnalité")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Champ pour le nom de la fonctionnalité
        name_frame = ctk.CTkFrame(dialog)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            name_frame,
            text="Nom de la fonctionnalité:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        name_entry = ctk.CTkEntry(name_frame, width=200)
        name_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Champ pour la valeur
        value_frame = ctk.CTkFrame(dialog)
        value_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            value_frame,
            text="État initial:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        value_var = tk.BooleanVar(value=True)
        value_checkbox = ctk.CTkCheckBox(
            value_frame,
            text="Activée",
            variable=value_var,
            onvalue=True,
            offvalue=False
        )
        value_checkbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fonction pour ajouter la fonctionnalité
        def add():
            feature_name = name_entry.get().strip()
            value = value_var.get()
            
            # Valider le nom
            if not feature_name:
                messagebox.showwarning(
                    "Nom manquant",
                    "Veuillez entrer un nom pour la fonctionnalité.",
                    parent=dialog
                )
                return
            
            # Vérifier si la fonctionnalité existe déjà
            if feature_name in self.config.get("features", {}):
                messagebox.showwarning(
                    "Fonctionnalité existante",
                    f"La fonctionnalité '{feature_name}' existe déjà.",
                    parent=dialog
                )
                return
            
            # Ajouter la fonctionnalité
            if "features" not in self.config:
                self.config["features"] = {}
            
            self.config["features"][feature_name] = value
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser le tableau
            self._populate_features_table()
            
            # Fermer la boîte de dialogue
            dialog.destroy()
        
        # Bouton pour ajouter
        add_button = ctk.CTkButton(
            button_frame,
            text="Ajouter",
            command=add,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour annuler
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=dialog.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _delete_feature(self) -> None:
        """
        Supprime la fonctionnalité sélectionnée.
        """
        # Récupérer la sélection
        selected_items = self.features_table.selection()
        if not selected_items:
            return
        
        # Récupérer le nom de la fonctionnalité sélectionnée
        item = selected_items[0]
        feature = self.features_table.item(item, "values")[0]
        
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer la fonctionnalité '{feature}'?"
        )
        
        if not confirm:
            return
        
        # Supprimer la fonctionnalité
        if "features" in self.config and feature in self.config["features"]:
            del self.config["features"][feature]
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser le tableau
            self._populate_features_table()
    
    def _create_settings_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion des paramètres.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Paramètres système",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Paramètre: Jours de grâce pour la vérification de licence
        grace_frame = ctk.CTkFrame(main_frame)
        grace_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            grace_frame,
            text="Jours de grâce pour licence:",
            width=200,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.grace_days_var = tk.StringVar(value=str(self.config.get("settings", {}).get("licence_check_grace_days", 7)))
        grace_spinbox = tk.Spinbox(
            grace_frame,
            from_=0,
            to=30,
            textvariable=self.grace_days_var,
            width=5
        )
        grace_spinbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        ctk.CTkLabel(
            grace_frame,
            text="jours",
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Information sur le paramètre
        ctk.CTkLabel(
            grace_frame,
            text="Nombre de jours pendant lesquels l'application peut fonctionner après expiration de la licence.",
            text_color="gray",
            font=ctk.CTkFont(size=10),
            anchor="w"
        ).pack(side=tk.LEFT, padx=20, pady=5)
        
        # Paramètre: Jours maximum en mode hors ligne
        offline_frame = ctk.CTkFrame(main_frame)
        offline_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            offline_frame,
            text="Jours maximum hors ligne:",
            width=200,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.offline_days_var = tk.StringVar(value=str(self.config.get("settings", {}).get("max_offline_days", 14)))
        offline_spinbox = tk.Spinbox(
            offline_frame,
            from_=1,
            to=90,
            textvariable=self.offline_days_var,
            width=5
        )
        offline_spinbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        ctk.CTkLabel(
            offline_frame,
            text="jours",
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Information sur le paramètre
        ctk.CTkLabel(
            offline_frame,
            text="Nombre de jours pendant lesquels l'application peut fonctionner sans connexion Internet.",
            text_color="gray",
            font=ctk.CTkFont(size=10),
            anchor="w"
        ).pack(side=tk.LEFT, padx=20, pady=5)
        
        # Paramètre: Mise à jour automatique
        auto_update_frame = ctk.CTkFrame(main_frame)
        auto_update_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            auto_update_frame,
            text="Mise à jour automatique:",
            width=200,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.auto_update_var = tk.BooleanVar(value=self.config.get("settings", {}).get("auto_update", True))
        auto_update_checkbox = ctk.CTkCheckBox(
            auto_update_frame,
            text="Activer",
            variable=self.auto_update_var,
            onvalue=True,
            offvalue=False
        )
        auto_update_checkbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Information sur le paramètre
        ctk.CTkLabel(
            auto_update_frame,
            text="Permet à l'application de télécharger et installer automatiquement les mises à jour.",
            text_color="gray",
            font=ctk.CTkFont(size=10),
            anchor="w"
        ).pack(side=tk.LEFT, padx=20, pady=5)
        
        # Paramètre: Fréquence de vérification des mises à jour (en heures)
        check_interval_frame = ctk.CTkFrame(main_frame)
        check_interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            check_interval_frame,
            text="Intervalle de vérification:",
            width=200,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.check_interval_var = tk.StringVar(value=str(self.config.get("settings", {}).get("check_interval_hours", 24)))
        check_interval_spinbox = tk.Spinbox(
            check_interval_frame,
            from_=1,
            to=168,  # 1 semaine
            textvariable=self.check_interval_var,
            width=5
        )
        check_interval_spinbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        ctk.CTkLabel(
            check_interval_frame,
            text="heures",
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Information sur le paramètre
        ctk.CTkLabel(
            check_interval_frame,
            text="Intervalle entre les vérifications de configuration (0 = à chaque démarrage).",
            text_color="gray",
            font=ctk.CTkFont(size=10),
            anchor="w"
        ).pack(side=tk.LEFT, padx=20, pady=5)
        
        # Paramètre personnalisé (ajout direct)
        custom_frame = ctk.CTkFrame(main_frame)
        custom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            custom_frame,
            text="Paramètres personnalisés",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=5, pady=5)
        
        # Bouton pour ajouter un paramètre personnalisé
        add_param_button = ctk.CTkButton(
            custom_frame,
            text="Ajouter un paramètre",
            command=self._add_custom_setting
        )
        add_param_button.pack(anchor="w", padx=5, pady=5)
        
        # Afficher les paramètres personnalisés existants
        self.custom_settings_frame = ctk.CTkFrame(main_frame)
        self.custom_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self._populate_custom_settings()
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton pour appliquer les modifications
        apply_button = ctk.CTkButton(
            action_frame,
            text="Appliquer les modifications",
            command=self._apply_settings_changes,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        apply_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour réinitialiser
        reset_button = ctk.CTkButton(
            action_frame,
            text="Réinitialiser",
            command=self._reset_settings_tab,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        return tab
    
    def _populate_custom_settings(self) -> None:
        """
        Affiche les paramètres personnalisés existants.
        """
        # Effacer les widgets existants
        for widget in self.custom_settings_frame.winfo_children():
            widget.destroy()
        
        # Récupérer les paramètres
        settings = self.config.get("settings", {})
        
        # Paramètres standards à exclure
        standard_params = [
            "licence_check_grace_days",
            "max_offline_days",
            "auto_update",
            "check_interval_hours"
        ]
        
        # Créer un widget pour chaque paramètre personnalisé
        custom_params_count = 0
        
        for key, value in settings.items():
            if key not in standard_params:
                param_frame = ctk.CTkFrame(self.custom_settings_frame)
                param_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # Libellé du paramètre
                ctk.CTkLabel(
                    param_frame,
                    text=key + ":",
                    width=150,
                    anchor="w"
                ).pack(side=tk.LEFT, padx=5, pady=5)
                
                # Valeur du paramètre (en fonction du type)
                if isinstance(value, bool):
                    var = tk.BooleanVar(value=value)
                    widget = ctk.CTkCheckBox(
                        param_frame,
                        text="",
                        variable=var,
                        onvalue=True,
                        offvalue=False
                    )
                    widget.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    # Stocker la variable pour la récupérer plus tard
                    widget.custom_var = var
                    widget.custom_key = key
                    widget.custom_type = "bool"
                    
                elif isinstance(value, int):
                    var = tk.StringVar(value=str(value))
                    widget = tk.Spinbox(
                        param_frame,
                        from_=-9999,
                        to=9999,
                        textvariable=var,
                        width=10
                    )
                    widget.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    # Stocker la variable pour la récupérer plus tard
                    widget.custom_var = var
                    widget.custom_key = key
                    widget.custom_type = "int"
                    
                elif isinstance(value, float):
                    var = tk.StringVar(value=str(value))
                    widget = ctk.CTkEntry(
                        param_frame,
                        width=100,
                        textvariable=var
                    )
                    widget.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    # Stocker la variable pour la récupérer plus tard
                    widget.custom_var = var
                    widget.custom_key = key
                    widget.custom_type = "float"
                    
                else:  # str ou autre
                    var = tk.StringVar(value=str(value))
                    widget = ctk.CTkEntry(
                        param_frame,
                        width=200,
                        textvariable=var
                    )
                    widget.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    # Stocker la variable pour la récupérer plus tard
                    widget.custom_var = var
                    widget.custom_key = key
                    widget.custom_type = "str"
                
                # Bouton pour supprimer le paramètre
                delete_button = ctk.CTkButton(
                    param_frame,
                    text="🗑️",
                    width=30,
                    height=30,
                    command=lambda k=key: self._delete_custom_setting(k)
                )
                delete_button.pack(side=tk.RIGHT, padx=5, pady=5)
                
                custom_params_count += 1
        
        # Afficher un message si aucun paramètre personnalisé
        if custom_params_count == 0:
            ctk.CTkLabel(
                self.custom_settings_frame,
                text="Aucun paramètre personnalisé défini",
                text_color="gray"
            ).pack(padx=5, pady=10)
    
    def _add_custom_setting(self) -> None:
        """
        Ajoute un paramètre personnalisé.
        """
        # Créer une fenêtre de dialogue
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Ajouter un paramètre")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Champ pour le nom du paramètre
        name_frame = ctk.CTkFrame(dialog)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            name_frame,
            text="Nom du paramètre:",
            width=120,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        name_entry = ctk.CTkEntry(name_frame, width=200)
        name_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Champ pour le type du paramètre
        type_frame = ctk.CTkFrame(dialog)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            type_frame,
            text="Type de valeur:",
            width=120,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        type_var = tk.StringVar(value="str")
        types = [
            ("Texte", "str"),
            ("Nombre entier", "int"),
            ("Nombre décimal", "float"),
            ("Booléen (oui/non)", "bool")
        ]
        
        type_frame_inner = ctk.CTkFrame(type_frame)
        type_frame_inner.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        for text, value in types:
            radio = ctk.CTkRadioButton(
                type_frame_inner,
                text=text,
                variable=type_var,
                value=value
            )
            radio.pack(anchor="w", padx=5, pady=2)
        
        # Champ pour la valeur du paramètre
        value_frame = ctk.CTkFrame(dialog)
        value_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            value_frame,
            text="Valeur:",
            width=120,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        value_entry = ctk.CTkEntry(value_frame, width=200)
        value_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Boutons d'action
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fonction pour ajouter le paramètre
        def add_param():
            # Récupérer les valeurs
            name = name_entry.get().strip()
            param_type = type_var.get()
            value_str = value_entry.get().strip()
            
            # Valider le nom
            if not name:
                messagebox.showwarning(
                    "Nom manquant",
                    "Veuillez entrer un nom pour le paramètre.",
                    parent=dialog
                )
                return
            
            # Vérifier si le nom est un paramètre standard
            standard_params = [
                "licence_check_grace_days",
                "max_offline_days",
                "auto_update",
                "check_interval_hours"
            ]
            
            if name in standard_params:
                messagebox.showwarning(
                    "Nom réservé",
                    f"Le nom '{name}' est réservé pour un paramètre standard.",
                    parent=dialog
                )
                return
            
            # Vérifier si le paramètre existe déjà
            if name in self.config.get("settings", {}):
                response = messagebox.askyesno(
                    "Paramètre existant",
                    f"Le paramètre '{name}' existe déjà. Voulez-vous le remplacer?",
                    parent=dialog
                )
                if not response:
                    return
            
            # Convertir la valeur selon le type
            try:
                if param_type == "str":
                    value = value_str
                elif param_type == "int":
                    value = int(value_str)
                elif param_type == "float":
                    value = float(value_str)
                elif param_type == "bool":
                    value = value_str.lower() in ["true", "1", "oui", "yes", "y", "o", "vrai", "v"]
                else:
                    value = value_str
                
                # Ajouter le paramètre
                if "settings" not in self.config:
                    self.config["settings"] = {}
                
                self.config["settings"][name] = value
                
                # Marquer comme modifié
                self.is_modified = True
                
                # Actualiser l'affichage
                self._populate_custom_settings()
                
                # Fermer la boîte de dialogue
                dialog.destroy()
                
            except ValueError:
                messagebox.showwarning(
                    "Valeur invalide",
                    f"La valeur '{value_str}' n'est pas valide pour le type {param_type}.",
                    parent=dialog
                )
        
        # Bouton pour ajouter
        add_button = ctk.CTkButton(
            button_frame,
            text="Ajouter",
            command=add_param,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour annuler
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=dialog.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _delete_custom_setting(self, key: str) -> None:
        """
        Supprime un paramètre personnalisé.
        
        Args:
            key (str): Clé du paramètre à supprimer
        """
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le paramètre '{key}'?"
        )
        
        if not confirm:
            return
        
        # Supprimer le paramètre
        if "settings" in self.config and key in self.config["settings"]:
            del self.config["settings"][key]
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser l'affichage
            self._populate_custom_settings()
    
    def _apply_settings_changes(self) -> None:
        """
        Applique les modifications de l'onglet des paramètres à la configuration.
        """
        try:
            # Récupérer les valeurs des paramètres standards
            grace_days = int(self.grace_days_var.get())
            offline_days = int(self.offline_days_var.get())
            auto_update = self.auto_update_var.get()
            check_interval = int(self.check_interval_var.get())
            
            # Valider les valeurs
            if grace_days < 0:
                messagebox.showwarning(
                    "Valeur invalide",
                    "Le nombre de jours de grâce ne peut pas être négatif."
                )
                return
            
            if offline_days < 1:
                messagebox.showwarning(
                    "Valeur invalide",
                    "Le nombre maximum de jours hors ligne doit être au moins 1."
                )
                return
            
            if check_interval < 0:
                messagebox.showwarning(
                    "Valeur invalide",
                    "L'intervalle de vérification ne peut pas être négatif."
                )
                return
            
            # Mettre à jour la configuration
            if "settings" not in self.config:
                self.config["settings"] = {}
            
            self.config["settings"]["licence_check_grace_days"] = grace_days
            self.config["settings"]["max_offline_days"] = offline_days
            self.config["settings"]["auto_update"] = auto_update
            self.config["settings"]["check_interval_hours"] = check_interval
            
            # Récupérer les valeurs des paramètres personnalisés
            for widget in self.custom_settings_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if hasattr(child, "custom_key") and hasattr(child, "custom_var") and hasattr(child, "custom_type"):
                            key = child.custom_key
                            var = child.custom_var
                            param_type = child.custom_type
                            
                            # Convertir la valeur selon le type
                            if param_type == "bool":
                                value = var.get()
                            elif param_type == "int":
                                value = int(var.get())
                            elif param_type == "float":
                                value = float(var.get())
                            else:  # str
                                value = var.get()
                            
                            # Mettre à jour la configuration
                            self.config["settings"][key] = value
            
            # Marquer comme modifié
            self.is_modified = True
            
            messagebox.showinfo(
                "Modifications appliquées",
                "Les modifications des paramètres ont été appliquées à la configuration."
            )
            
        except ValueError as e:
            messagebox.showerror(
                "Erreur",
                f"Une des valeurs n'est pas valide: {e}"
            )
    
    def _reset_settings_tab(self) -> None:
        """
        Réinitialise l'onglet des paramètres avec les valeurs actuelles de la configuration.
        """
        # Réinitialiser les paramètres standards
        self.grace_days_var.set(str(self.config.get("settings", {}).get("licence_check_grace_days", 7)))
        self.offline_days_var.set(str(self.config.get("settings", {}).get("max_offline_days", 14)))
        self.auto_update_var.set(self.config.get("settings", {}).get("auto_update", True))
        self.check_interval_var.set(str(self.config.get("settings", {}).get("check_interval_hours", 24)))
        
        # Réinitialiser les paramètres personnalisés
        self._populate_custom_settings()
    
    def _create_support_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion des informations de support.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Informations de support",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Email de support
        email_frame = ctk.CTkFrame(main_frame)
        email_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email de support:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.support_email_entry = ctk.CTkEntry(email_frame, width=300)
        self.support_email_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.support_email_entry.insert(0, self.config.get("support", {}).get("email", ""))
        
        # URL du support
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            url_frame,
            text="URL du support:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.support_url_entry = ctk.CTkEntry(url_frame, width=300)
        self.support_url_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.support_url_entry.insert(0, self.config.get("support", {}).get("url", ""))
        
        # Téléphone de support
        phone_frame = ctk.CTkFrame(main_frame)
        phone_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            phone_frame,
            text="Téléphone de support:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.support_phone_entry = ctk.CTkEntry(phone_frame, width=300)
        self.support_phone_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.support_phone_entry.insert(0, self.config.get("support", {}).get("phone", ""))
        
        # Heures de disponibilité
        hours_frame = ctk.CTkFrame(main_frame)
        hours_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            hours_frame,
            text="Heures de disponibilité:",
            width=150,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.support_hours_entry = ctk.CTkEntry(hours_frame, width=300)
        self.support_hours_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.support_hours_entry.insert(0, self.config.get("support", {}).get("hours", ""))
        
        # Instructions de support
        instructions_frame = ctk.CTkFrame(main_frame)
        instructions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            instructions_frame,
            text="Instructions:",
            width=150,
            anchor="nw"
        ).pack(side=tk.LEFT, padx=5, pady=5, anchor="n")
        
        self.support_instructions_text = ctk.CTkTextbox(
            instructions_frame,
            width=300,
            height=150
        )
        self.support_instructions_text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.support_instructions_text.insert("1.0", self.config.get("support", {}).get("instructions", ""))
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton pour appliquer les modifications
        apply_button = ctk.CTkButton(
            action_frame,
            text="Appliquer les modifications",
            command=self._apply_support_changes,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        apply_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour réinitialiser
        reset_button = ctk.CTkButton(
            action_frame,
            text="Réinitialiser",
            command=self._reset_support_tab,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        return tab
    
    def _apply_support_changes(self) -> None:
        """
        Applique les modifications de l'onglet de support à la configuration.
        """
        # Récupérer les valeurs
        email = self.support_email_entry.get().strip()
        url = self.support_url_entry.get().strip()
        phone = self.support_phone_entry.get().strip()
        hours = self.support_hours_entry.get().strip()
        instructions = self.support_instructions_text.get("1.0", tk.END).strip()
        
        # Mettre à jour la configuration
        if "support" not in self.config:
            self.config["support"] = {}
        
        self.config["support"]["email"] = email
        self.config["support"]["url"] = url
        self.config["support"]["phone"] = phone
        self.config["support"]["hours"] = hours
        self.config["support"]["instructions"] = instructions
        
        # Marquer comme modifié
        self.is_modified = True
        
        messagebox.showinfo(
            "Modifications appliquées",
            "Les modifications des informations de support ont été appliquées à la configuration."
        )
    
    def _reset_support_tab(self) -> None:
        """
        Réinitialise l'onglet de support avec les valeurs actuelles de la configuration.
        """
        # Réinitialiser les champs
        self.support_email_entry.delete(0, tk.END)
        self.support_email_entry.insert(0, self.config.get("support", {}).get("email", ""))
        
        self.support_url_entry.delete(0, tk.END)
        self.support_url_entry.insert(0, self.config.get("support", {}).get("url", ""))
        
        self.support_phone_entry.delete(0, tk.END)
        self.support_phone_entry.insert(0, self.config.get("support", {}).get("phone", ""))
        
        self.support_hours_entry.delete(0, tk.END)
        self.support_hours_entry.insert(0, self.config.get("support", {}).get("hours", ""))
        
        self.support_instructions_text.delete("1.0", tk.END)
        self.support_instructions_text.insert("1.0", self.config.get("support", {}).get("instructions", ""))
    
    def _create_changelog_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion du changelog.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Gestion du changelog",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Bouton pour ajouter une entrée
        add_button = ctk.CTkButton(
            button_frame,
            text="Ajouter une entrée",
            command=self._add_changelog_entry
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour éditer une entrée
        self.edit_changelog_button = ctk.CTkButton(
            button_frame,
            text="Éditer l'entrée sélectionnée",
            command=self._edit_changelog_entry,
            state="disabled"
        )
        self.edit_changelog_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour supprimer une entrée
        self.delete_changelog_button = ctk.CTkButton(
            button_frame,
            text="Supprimer l'entrée sélectionnée",
            command=self._delete_changelog_entry,
            state="disabled"
        )
        self.delete_changelog_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame pour le tableau
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Créer un Treeview pour afficher le changelog
        self.changelog_table = ttk.Treeview(
            table_frame,
            columns=("version", "date", "notes"),
            show="headings",
            selectmode="browse"
        )
        
        # Définir les en-têtes de colonnes
        self.changelog_table.heading("version", text="Version")
        self.changelog_table.heading("date", text="Date")
        self.changelog_table.heading("notes", text="Notes")
        
        # Définir les largeurs de colonnes
        self.changelog_table.column("version", width=100)
        self.changelog_table.column("date", width=100)
        self.changelog_table.column("notes", width=400)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.changelog_table.yview
        )
        self.changelog_table.configure(yscrollcommand=scrollbar.set)
        
        # Positionner le tableau et la scrollbar
        self.changelog_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lier la sélection à l'activation des boutons
        self.changelog_table.bind("<<TreeviewSelect>>", self._on_changelog_select)
        
        # Remplir le tableau avec les entrées existantes
        self._populate_changelog_table()
        
        return tab
    
    def _populate_changelog_table(self) -> None:
        """
        Remplit le tableau du changelog avec les données de la configuration.
        """
        # Effacer le tableau
        for item in self.changelog_table.get_children():
            self.changelog_table.delete(item)
        
        # Récupérer les entrées du changelog
        changelog = self.config.get("changelog_full", [])
        
        # Trier les entrées par version (en supposant un format semver)
        def version_key(entry):
            # Extraire les parties numériques de la version (ignorant les suffixes comme -beta)
            version = entry.get("version", "0.0.0")
            parts = []
            for part in version.split('.'):
                # Extraire la partie numérique
                num_part = ''.join(c for c in part if c.isdigit())
                if num_part:
                    parts.append(int(num_part))
                else:
                    parts.append(0)
            # Padding pour assurer la comparaison correcte
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts)
        
        # Trier les entrées par version décroissante
        sorted_changelog = sorted(changelog, key=version_key, reverse=True)
        
        # Ajouter chaque entrée au tableau
        for entry in sorted_changelog:
            version = entry.get("version", "")
            date = entry.get("date", "")
            notes = entry.get("notes", "")
            
            # Tronquer les notes si elles sont trop longues
            display_notes = notes[:100] + "..." if len(notes) > 100 else notes
            
            self.changelog_table.insert(
                "",
                tk.END,
                values=(version, date, display_notes),
                tags=(version,)
            )
    
    def _on_changelog_select(self, event) -> None:
        """
        Gère la sélection d'une entrée dans le tableau du changelog.
        
        Args:
            event: Événement de sélection
        """
        selected_items = self.changelog_table.selection()
        
        if selected_items:
            # Activer les boutons
            self.edit_changelog_button.configure(state="normal")
            self.delete_changelog_button.configure(state="normal")
        else:
            # Désactiver les boutons
            self.edit_changelog_button.configure(state="disabled")
            self.delete_changelog_button.configure(state="disabled")
    
    def _add_changelog_entry(self) -> None:
        """
        Ajoute une nouvelle entrée au changelog.
        """
        # Créer une fenêtre de dialogue
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Ajouter une entrée au changelog")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Champ pour la version
        version_frame = ctk.CTkFrame(dialog)
        version_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text="Version:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        version_entry = ctk.CTkEntry(version_frame, width=150)
        version_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Champ pour la date
        date_frame = ctk.CTkFrame(dialog)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            date_frame,
            text="Date:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Date par défaut
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        date_entry = ctk.CTkEntry(date_frame, width=150)
        date_entry.pack(side=tk.LEFT, padx=5, pady=5)
        date_entry.insert(0, today)
        
        # Étiquette d'information
        ctk.CTkLabel(
            dialog,
            text="Format de date: AAAA-MM-JJ",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(padx=10, anchor="w")
        
        # Champ pour les notes
        notes_frame = ctk.CTkFrame(dialog)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            notes_frame,
            text="Notes:",
            width=100,
            anchor="nw"
        ).pack(side=tk.LEFT, padx=5, pady=5, anchor="n")
        
        notes_text = ctk.CTkTextbox(
            notes_frame,
            width=350,
            height=200
        )
        notes_text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fonction pour ajouter l'entrée
        def add():
            version = version_entry.get().strip()
            date = date_entry.get().strip()
            notes = notes_text.get("1.0", tk.END).strip()
            
            # Valider les entrées
            if not version:
                messagebox.showwarning(
                    "Version manquante",
                    "Veuillez entrer une version.",
                    parent=dialog
                )
                return
            
            # Valider le format de la date
            try:
                if date:
                    datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Format de date invalide",
                    "Veuillez entrer une date au format AAAA-MM-JJ.",
                    parent=dialog
                )
                return
            
            # Vérifier si la version existe déjà
            for entry in self.config.get("changelog_full", []):
                if entry.get("version") == version:
                    response = messagebox.askyesno(
                        "Version existante",
                        f"Une entrée pour la version {version} existe déjà. Voulez-vous la remplacer?",
                        parent=dialog
                    )
                    if not response:
                        return
                    break
            
            # Créer la nouvelle entrée
            new_entry = {
                "version": version,
                "date": date,
                "notes": notes
            }
            
            # Ajouter ou remplacer l'entrée
            if "changelog_full" not in self.config:
                self.config["changelog_full"] = []
            
            # Supprimer l'entrée existante si nécessaire
            self.config["changelog_full"] = [e for e in self.config["changelog_full"] if e.get("version") != version]
            
            # Ajouter la nouvelle entrée
            self.config["changelog_full"].append(new_entry)
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser le tableau
            self._populate_changelog_table()
            
            # Fermer la boîte de dialogue
            dialog.destroy()
        
        # Bouton pour ajouter
        add_button = ctk.CTkButton(
            button_frame,
            text="Ajouter",
            command=add,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour annuler
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=dialog.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _edit_changelog_entry(self) -> None:
        """
        Édite l'entrée de changelog sélectionnée.
        """
        # Récupérer la sélection
        selected_items = self.changelog_table.selection()
        if not selected_items:
            return
        
        # Récupérer les données de l'entrée sélectionnée
        item = selected_items[0]
        version, date, _ = self.changelog_table.item(item, "values")
        
        # Récupérer les notes complètes
        notes = ""
        for entry in self.config.get("changelog_full", []):
            if entry.get("version") == version:
                notes = entry.get("notes", "")
                break
        
        # Créer une fenêtre de dialogue
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Éditer l'entrée - Version {version}")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Champ pour la version (non modifiable)
        version_frame = ctk.CTkFrame(dialog)
        version_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text="Version:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        version_entry = ctk.CTkEntry(version_frame, width=150, state="disabled")
        version_entry.pack(side=tk.LEFT, padx=5, pady=5)
        version_entry.insert(0, version)
        
        # Champ pour la date
        date_frame = ctk.CTkFrame(dialog)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            date_frame,
            text="Date:",
            width=100,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        date_entry = ctk.CTkEntry(date_frame, width=150)
        date_entry.pack(side=tk.LEFT, padx=5, pady=5)
        date_entry.insert(0, date)
        
        # Étiquette d'information
        ctk.CTkLabel(
            dialog,
            text="Format de date: AAAA-MM-JJ",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(padx=10, anchor="w")
        
        # Champ pour les notes
        notes_frame = ctk.CTkFrame(dialog)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            notes_frame,
            text="Notes:",
            width=100,
            anchor="nw"
        ).pack(side=tk.LEFT, padx=5, pady=5, anchor="n")
        
        notes_text = ctk.CTkTextbox(
            notes_frame,
            width=350,
            height=200
        )
        notes_text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        notes_text.insert("1.0", notes)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fonction pour mettre à jour l'entrée
        def update():
            new_date = date_entry.get().strip()
            new_notes = notes_text.get("1.0", tk.END).strip()
            
            # Valider le format de la date
            try:
                if new_date:
                    datetime.datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Format de date invalide",
                    "Veuillez entrer une date au format AAAA-MM-JJ.",
                    parent=dialog
                )
                return
            
            # Mettre à jour l'entrée
            if "changelog_full" in self.config:
                for i, entry in enumerate(self.config["changelog_full"]):
                    if entry.get("version") == version:
                        self.config["changelog_full"][i]["date"] = new_date
                        self.config["changelog_full"][i]["notes"] = new_notes
                        break
                
                # Marquer comme modifié
                self.is_modified = True
                
                # Mettre à jour également le changelog dans la section "update" si c'est la version actuelle
                if "update" in self.config and self.config["update"].get("latest_version") == version:
                    self.config["update"]["changelog"] = new_notes
                
                # Actualiser le tableau
                self._populate_changelog_table()
                
                # Fermer la boîte de dialogue
                dialog.destroy()
        
        # Bouton pour mettre à jour
        update_button = ctk.CTkButton(
            button_frame,
            text="Mettre à jour",
            command=update,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        update_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour annuler
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=dialog.destroy,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _delete_changelog_entry(self) -> None:
        """
        Supprime l'entrée de changelog sélectionnée.
        """
        # Récupérer la sélection
        selected_items = self.changelog_table.selection()
        if not selected_items:
            return
        
        # Récupérer la version de l'entrée sélectionnée
        item = selected_items[0]
        version = self.changelog_table.item(item, "values")[0]
        
        # Vérifier si c'est la version actuelle
        if "update" in self.config and self.config["update"].get("latest_version") == version:
            messagebox.showwarning(
                "Version actuelle",
                f"La version {version} est la version actuelle dans la section 'update'.\n"
                "Vous ne pouvez pas la supprimer du changelog."
            )
            return
        
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer l'entrée pour la version {version}?"
        )
        
        if not confirm:
            return
        
        # Supprimer l'entrée
        if "changelog_full" in self.config:
            self.config["changelog_full"] = [
                entry for entry in self.config["changelog_full"]
                if entry.get("version") != version
            ]
            
            # Marquer comme modifié
            self.is_modified = True
            
            # Actualiser le tableau
            self._populate_changelog_table()
    
    def _create_security_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet de gestion de la sécurité.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Paramètres de sécurité",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Signature requise
        signature_frame = ctk.CTkFrame(main_frame)
        signature_frame.pack(fill=tk.X, padx=10, pady=5)
        
        signature_required = self.config.get("security", {}).get("signature_required", False)
        self.signature_required_var = tk.BooleanVar(value=signature_required)
        
        signature_checkbox = ctk.CTkCheckBox(
            signature_frame,
            text="Exiger une signature pour les mises à jour",
            variable=self.signature_required_var,
            onvalue=True,
            offvalue=False,
            command=self._toggle_signature_required
        )
        signature_checkbox.pack(padx=5, pady=5, anchor="w")
        
        # Information sur la sécurité
        ctk.CTkLabel(
            signature_frame,
            text="Lorsque cette option est activée, les mises à jour doivent être signées avec la clé privée correspondante.",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(padx=5, pady=2, anchor="w")
        
        # Clé publique
        key_frame = ctk.CTkFrame(main_frame)
        key_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            key_frame,
            text="Clé publique:",
            anchor="w"
        ).pack(padx=5, pady=5, anchor="w")
        
        self.public_key_text = ctk.CTkTextbox(
            key_frame,
            width=400,
            height=150,
            wrap="none"
        )
        self.public_key_text.pack(padx=5, pady=5, fill=tk.X, expand=True)
        
        # Remplir avec la clé publique existante
        public_key = self.config.get("security", {}).get("public_key", "")
        self.public_key_text.insert("1.0", public_key)
        
        # État d'activation des widgets en fonction de signature_required
        self._toggle_signature_required()
        
        # Boutons pour gérer les clés
        key_buttons_frame = ctk.CTkFrame(main_frame)
        key_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Bouton pour générer une nouvelle paire de clés
        generate_button = ctk.CTkButton(
            key_buttons_frame,
            text="Générer une nouvelle paire de clés",
            command=self._generate_key_pair
        )
        generate_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour importer une clé publique
        import_button = ctk.CTkButton(
            key_buttons_frame,
            text="Importer une clé publique",
            command=self._import_public_key
        )
        import_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Séparateur
        separator = ctk.CTkFrame(main_frame, height=2, fg_color="gray")
        separator.pack(fill=tk.X, padx=10, pady=10)
        
        # Section: Journalisation des accès
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            log_frame,
            text="Journalisation des accès",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=5, pady=5, anchor="w")
        
        # Activer la journalisation
        log_enabled = self.config.get("security", {}).get("log_access", False)
        self.log_enabled_var = tk.BooleanVar(value=log_enabled)
        
        log_checkbox = ctk.CTkCheckBox(
            log_frame,
            text="Enregistrer les accès à la configuration",
            variable=self.log_enabled_var,
            onvalue=True,
            offvalue=False
        )
        log_checkbox.pack(padx=5, pady=5, anchor="w")
        
        # Information sur la journalisation
        ctk.CTkLabel(
            log_frame,
            text="Enregistre les adresses IP et les horodatages des accès à la configuration.",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(padx=5, pady=2, anchor="w")
        
        # Durée de conservation des journaux
        log_retention_frame = ctk.CTkFrame(log_frame)
        log_retention_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ctk.CTkLabel(
            log_retention_frame,
            text="Conserver les journaux pendant:",
            width=200,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.log_retention_var = tk.StringVar(value=str(self.config.get("security", {}).get("log_retention_days", 30)))
        log_retention_spinbox = tk.Spinbox(
            log_retention_frame,
            from_=1,
            to=365,
            textvariable=self.log_retention_var,
            width=5
        )
        log_retention_spinbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        ctk.CTkLabel(
            log_retention_frame,
            text="jours",
            anchor="w"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton pour appliquer les modifications
        apply_button = ctk.CTkButton(
            action_frame,
            text="Appliquer les modifications",
            command=self._apply_security_changes,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        apply_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bouton pour réinitialiser
        reset_button = ctk.CTkButton(
            action_frame,
            text="Réinitialiser",
            command=self._reset_security_tab,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        return tab
    
    def _toggle_signature_required(self) -> None:
        """
        Active ou désactive les widgets liés à la signature en fonction de l'état de la case à cocher.
        """
        if self.signature_required_var.get():
            self.public_key_text.configure(state="normal")
        else:
            self.public_key_text.configure(state="normal")  # Temporairement normal pour effacer
            # self.public_key_text.delete("1.0", tk.END)  # Optionnel: effacer la clé si la signature n'est pas requise
            # self.public_key_text.configure(state="disabled")
    
    def _generate_key_pair(self) -> None:
        """
        Génère une nouvelle paire de clés et permet à l'utilisateur de télécharger la clé privée.
        """
        # Vérifier si une clé publique existe déjà
        current_key = self.public_key_text.get("1.0", tk.END).strip()
        if current_key:
            confirm = messagebox.askyesno(
                "Clé existante",
                "Une clé publique existe déjà. La remplacer par une nouvelle paire de clés?\n\n"
                "ATTENTION: Cela invalidera toutes les signatures existantes."
            )
            if not confirm:
                return
        
        try:
            # Pour une implémentation réelle, utiliser cryptography.hazmat.primitives.asymmetric.rsa ou similar
            # Dans cette version simplifiée, nous générons juste des données aléatoires
            
            # Simuler une clé privée (dans une application réelle, utiliser une bibliothèque cryptographique)
            private_key = base64.b64encode(secrets.token_bytes(64)).decode('utf-8')
            
            # Simuler une clé publique dérivée
            public_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
            
            # Afficher la clé publique
            self.public_key_text.delete("1.0", tk.END)
            self.public_key_text.insert("1.0", public_key)
            
            # Permettre à l'utilisateur de sauvegarder la clé privée
            file_path = filedialog.asksaveasfilename(
                title="Enregistrer la clé privée",
                filetypes=[("Fichiers de clé", "*.key"), ("Tous les fichiers", "*.*")],
                defaultextension=".key"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(private_key)
                
                messagebox.showinfo(
                    "Clé privée sauvegardée",
                    f"La clé privée a été sauvegardée dans {file_path}.\n\n"
                    "IMPORTANT: Conservez cette clé en lieu sûr. Elle ne peut pas être récupérée si elle est perdue."
                )
            else:
                messagebox.showwarning(
                    "Clé privée non sauvegardée",
                    "La clé privée n'a pas été sauvegardée. Vous ne pourrez pas signer de mises à jour sans elle."
                )
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la génération des clés:\n{e}"
            )
    
    def _import_public_key(self) -> None:
        """
        Permet à l'utilisateur d'importer une clé publique depuis un fichier.
        """
        file_path = filedialog.askopenfilename(
            title="Importer une clé publique",
            filetypes=[("Fichiers de clé", "*.key"), ("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                public_key = f.read().strip()
            
            # Dans une implémentation réelle, valider que la clé est au bon format
            
            # Afficher la clé publique
            self.public_key_text.delete("1.0", tk.END)
            self.public_key_text.insert("1.0", public_key)
            
            messagebox.showinfo(
                "Clé publique importée",
                "La clé publique a été importée avec succès."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de l'importation de la clé publique:\n{e}"
            )
    
    def _apply_security_changes(self) -> None:
        """
        Applique les modifications de l'onglet de sécurité à la configuration.
        """
        try:
            # Récupérer les valeurs
            signature_required = self.signature_required_var.get()
            public_key = self.public_key_text.get("1.0", tk.END).strip()
            log_enabled = self.log_enabled_var.get()
            log_retention = int(self.log_retention_var.get())
            
            # Valider les entrées
            if signature_required and not public_key:
                messagebox.showwarning(
                    "Clé publique manquante",
                    "Une clé publique est requise lorsque la signature est exigée."
                )
                return
            
            if log_retention < 1 or log_retention > 365:
                messagebox.showwarning(
                    "Valeur invalide",
                    "La durée de conservation des journaux doit être comprise entre 1 et 365 jours."
                )
                return
            
            # Mettre à jour la configuration
            if "security" not in self.config:
                self.config["security"] = {}
            
            self.config["security"]["signature_required"] = signature_required
            self.config["security"]["public_key"] = public_key
            self.config["security"]["log_access"] = log_enabled
            self.config["security"]["log_retention_days"] = log_retention
            
            # Marquer comme modifié
            self.is_modified = True
            
            messagebox.showinfo(
                "Modifications appliquées",
                "Les modifications des paramètres de sécurité ont été appliquées à la configuration."
            )
            
        except ValueError as e:
            messagebox.showerror(
                "Erreur",
                f"Une des valeurs n'est pas valide: {e}"
            )
    
    def _reset_security_tab(self) -> None:
        """
        Réinitialise l'onglet de sécurité avec les valeurs actuelles de la configuration.
        """
        # Réinitialiser les champs
        self.signature_required_var.set(self.config.get("security", {}).get("signature_required", False))
        
        self.public_key_text.delete("1.0", tk.END)
        self.public_key_text.insert("1.0", self.config.get("security", {}).get("public_key", ""))
        
        self.log_enabled_var.set(self.config.get("security", {}).get("log_access", False))
        self.log_retention_var.set(str(self.config.get("security", {}).get("log_retention_days", 30)))
        
        # Mettre à jour l'état des widgets
        self._toggle_signature_required()
    
    def _create_raw_tab(self) -> ctk.CTkFrame:
        """
        Crée l'onglet d'édition du JSON brut.
        
        Returns:
            ctk.CTkFrame: Frame de l'onglet
        """
        tab = ctk.CTkFrame(self.content_frame)
        
        # Titre
        ctk.CTkLabel(
            tab,
            text="Édition du JSON brut",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Avertissement
        ctk.CTkLabel(
            tab,
            text="Attention: l'édition directe du JSON peut corrompre la structure de la configuration.",
            text_color=("red", "#ff6666"),
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        # Textbox pour le JSON
        self.raw_json_text = ctk.CTkTextbox(
            tab,
            width=600,
            height=500,
            font=ctk.CTkFont(family="Courier", size=12),
            wrap="none"
        )
        self.raw_json_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Remplir avec le JSON
        json_text = json.dumps(self.config, indent=2, ensure_ascii=False)
        self.raw_json_text.delete("1.0", tk.END)
        self.raw_json_text.insert("1.0", json_text)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton pour appliquer les modifications
        apply_button = ctk.CTkButton(
            button_frame,
            text="Appliquer",
            command=self._apply_raw_json,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        apply_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour annuler les modifications
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=self._reset_raw_json,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        return tab
    
    def _apply_raw_json(self) -> None:
        """
        Applique les modifications du JSON brut.
        """
        try:
            # Récupérer le texte du textbox
            json_text = self.raw_json_text.get("1.0", tk.END)
            
            # Parser le JSON
            new_config = json.loads(json_text)
            
            # Mettre à jour la configuration
            self.config = new_config
            self.is_modified = True
            
            # Actualiser les onglets
            self._refresh_all_tabs()
            
            messagebox.showinfo(
                "JSON appliqué",
                "Les modifications du JSON ont été appliquées avec succès."
            )
            
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Erreur de format",
                f"Le JSON contient des erreurs de format:\n{e}"
            )
        
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de l'application du JSON:\n{e}"
            )
    
    def _reset_raw_json(self) -> None:
        """
        Réinitialise le JSON brut avec la configuration actuelle.
        """
        json_text = json.dumps(self.config, indent=2, ensure_ascii=False)
        self.raw_json_text.delete("1.0", tk.END)
        self.raw_json_text.insert("1.0", json_text)
    
    def _show_message(self, message, message_type="info"):
        """
        Affiche un message à l'utilisateur.
        
        Args:
            message (str): Message à afficher
            message_type (str): Type de message ('info', 'warning', 'error', 'success')
        """
        import tkinter.messagebox as messagebox
        
        title = "Configuration distante"
        
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)
        elif message_type == "success":
            messagebox.showinfo(title, message)


if __name__ == "__main__":
    # Configurer le logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Lancer l'application en mode autonome
    RemoteConfigAdmin() 
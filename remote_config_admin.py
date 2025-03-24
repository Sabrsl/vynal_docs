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
        uploader (UpdateUploader): Instance de l'uploader Google Drive
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
        self.uploader = None
        
        # Charger la configuration
        if self.config_file_path is None:
            self._select_config_file()
        else:
            self._load_config()
            
        # Initialiser l'uploader Google Drive
        self._init_uploader()
        
        # Créer l'interface utilisateur
        self._create_ui()
        
        logger.info("RemoteConfigAdmin initialisé")
        
        # Démarrer la boucle principale si mode autonome
        if self.standalone:
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            self.root.mainloop()

    def _on_config_change(self, *args):
        """Handle changes to config values"""
        try:
            # Get current values
            current_values = self._get_current_values()
            
            # Save to config file
            self._save_config(current_values, show_confirmation=False)
            
            # Update status
            self._update_status("Config updated")
            
        except Exception as e:
            self._update_status(f"Error updating config: {str(e)}")
            messagebox.showerror("Error", f"Failed to update config: {str(e)}")

    def _get_current_values(self) -> Dict[str, Any]:
        """
        Récupère les valeurs actuelles de tous les champs de configuration.
        
        Returns:
            Dict[str, Any]: Dictionnaire des valeurs de configuration
        """
        values = {}
        
        # Parcourir tous les widgets de configuration
        for section, fields in self.config_widgets.items():
            values[section] = {}
            for field_name, widget in fields.items():
                if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                    values[section][field_name] = widget.get()
                elif isinstance(widget, ctk.CTkSwitch):
                    values[section][field_name] = widget.get() == 1
                elif isinstance(widget, ctk.CTkComboBox):
                    values[section][field_name] = widget.get()
        
        return values

    def _save_config(self, values: Dict[str, Any], show_confirmation: bool = True) -> bool:
        """
        Sauvegarde la configuration dans le fichier et sur Google Drive.
        
        Args:
            values (Dict[str, Any]): Nouvelles valeurs de configuration
            show_confirmation (bool): Si True, affiche un message de confirmation
        
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Mettre à jour la configuration
            self.config.update(values)
            
            # Si aucun fichier n'est défini, demander à l'utilisateur
            if not self.config_file_path:
                file_path = filedialog.asksaveasfilename(
                    title="Enregistrer la configuration",
                    filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
                    defaultextension=".json"
                )
                
                if not file_path:
                    return False
                
                self.config_file_path = file_path
            
            # Créer une sauvegarde
            if os.path.exists(self.config_file_path):
                backup_path = f"{self.config_file_path}.bak"
                shutil.copy2(self.config_file_path, backup_path)
            
            # Sauvegarder le fichier
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Mettre à jour l'état
            self.is_modified = False
            self._update_status("Configuration sauvegardée")
            
            # Afficher confirmation si demandé
            if show_confirmation:
                messagebox.showinfo(
                    "Succès",
                    "La configuration a été sauvegardée avec succès."
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            messagebox.showerror(
                "Erreur",
                f"Impossible de sauvegarder la configuration:\n{str(e)}"
            )
            return False

    def _update_status(self, message: str) -> None:
        """
        Met à jour le message de statut dans l'interface.
        
        Args:
            message (str): Message à afficher
        """
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
        logger.info(message) 
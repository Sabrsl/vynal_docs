#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue des paramètres pour l'application Vynal Docs Automator
"""

import os
import sys
import logging
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from functools import lru_cache, partial
from typing import Optional, Dict, Any, List, Tuple
import weakref
import threading
import time

# Importer les utilitaires pour les licences
try:
    from utils.license_utils import verify_license, get_expiration_date_string
except ImportError:
    # Module facultatif
    pass

logger = logging.getLogger("VynalDocsAutomator.SettingsView")

class DialogUtils:
    """
    Utilitaires pour créer des boîtes de dialogue cohérentes dans l'application
    """
    
    _dialog_cache = weakref.WeakValueDictionary()
    _active_dialog = None
    _lock = threading.Lock()
    
    @classmethod
    def _cleanup_dialog(cls, dialog_key: tuple):
        """Nettoie le dialogue du cache"""
        try:
            with cls._lock:
                if dialog_key in cls._dialog_cache:
                    dialog = cls._dialog_cache[dialog_key]
                    if dialog == cls._active_dialog:
                        cls._active_dialog = None
                    del cls._dialog_cache[dialog_key]
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du dialogue: {e}")
    
    @classmethod
    def _create_dialog(cls, parent: tk.Widget, dialog_key: tuple) -> ctk.CTkToplevel:
        """Crée un nouveau dialogue"""
        try:
            dialog = ctk.CTkToplevel(parent)
            dialog.transient(parent)
            dialog.geometry("400x200")
            dialog.resizable(False, False)
            dialog.protocol("WM_DELETE_WINDOW", lambda: cls._on_dialog_close(dialog, dialog_key))
            
            # Empêcher l'interaction avec la fenêtre parent
            dialog.grab_set()
            
            # Centrer le dialogue
            cls._center_dialog(dialog)
            
            return dialog
        except Exception as e:
            logger.error(f"Erreur lors de la création du dialogue: {e}")
            raise
    
    @classmethod
    def _on_dialog_close(cls, dialog: ctk.CTkToplevel, dialog_key: tuple):
        """Gère la fermeture propre du dialogue"""
        try:
            if dialog == cls._active_dialog:
                dialog.grab_release()
                cls._active_dialog = None
            dialog.destroy()
            cls._cleanup_dialog(dialog_key)
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture du dialogue: {e}")
    
    @classmethod
    def _center_dialog(cls, dialog: ctk.CTkToplevel):
        """Centre le dialogue sur l'écran"""
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        size = tuple(int(_) for _ in dialog.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        dialog.geometry("+%d+%d" % (x, y))

    @classmethod
    def show_message(cls, parent: tk.Widget, title: str, message: str, message_type: str = "info"):
        """Affiche une boîte de dialogue avec un message (optimisée)"""
        try:
            if cls._active_dialog:
                cls._active_dialog.destroy()
                cls._active_dialog = None
            
            dialog = cls._create_dialog(parent, ("message", message_type))
            cls._active_dialog = dialog
            
            styles = {
                "info": ("ℹ️", "#3498db", "#2980b9"),
                "error": ("❌", "#e74c3c", "#c0392b"),
                "warning": ("⚠️", "#f39c12", "#d35400"),
                "success": ("✅", "#2ecc71", "#27ae60")
            }
            
            icon, button_color, hover_color = styles.get(message_type, styles["info"])
            
            dialog.title(title)
            
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            title_label = ctk.CTkLabel(
                frame,
                text=f"{icon} {title}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(0, 10))
            
            message_label = ctk.CTkLabel(
                frame,
                text=message,
                wraplength=360
            )
            message_label.pack(pady=10)
            
            def close_dialog():
                try:
                    dialog.grab_release()
                    dialog.destroy()
                    cls._active_dialog = None
                except Exception as e:
                    logger.error(f"Erreur lors de la fermeture du dialogue: {e}")
            
            ok_button = ctk.CTkButton(
                frame,
                text="OK",
                command=close_dialog,
                width=100,
                fg_color=button_color,
                hover_color=hover_color
            )
            ok_button.pack(pady=10)
            
            dialog.wait_window()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du message: {e}")
            try:
                if cls._active_dialog:
                    cls._active_dialog.destroy()
                    cls._active_dialog = None
            except:
                pass

    @classmethod
    def show_confirmation(cls, parent: tk.Widget, title: str, message: str, 
                         on_yes: Optional[callable] = None, 
                         on_no: Optional[callable] = None) -> bool:
        """Affiche une boîte de dialogue de confirmation optimisée"""
        try:
            if cls._active_dialog:
                cls._active_dialog.destroy()
                cls._active_dialog = None
            
            dialog = cls._create_dialog(parent, ("confirmation", title))
            cls._active_dialog = dialog
            
            result = [False]
            dialog.title(title)
            
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            title_label = ctk.CTkLabel(
                frame,
                text=f"⚠️ {title}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(0, 10))
            
            message_label = ctk.CTkLabel(
                frame,
                text=message,
                wraplength=360
            )
            message_label.pack(pady=10)
            
            button_frame = ctk.CTkFrame(frame, fg_color="transparent")
            button_frame.pack(pady=10)
            
            def cleanup_and_action(action_func=None):
                try:
                    dialog.grab_release()
                    if action_func:
                        result[0] = True
                        dialog.destroy()
                        cls._active_dialog = None
                        parent.after(100, action_func)
                    else:
                        dialog.destroy()
                        cls._active_dialog = None
                except Exception as e:
                    logger.error(f"Erreur dans l'action du dialogue: {e}")
                    dialog.destroy()
                    cls._active_dialog = None
            
            no_button = ctk.CTkButton(
                button_frame,
                text="Non",
                command=lambda: cleanup_and_action(on_no),
                width=100,
                fg_color="#e74c3c",
                hover_color="#c0392b"
            )
            no_button.pack(side=ctk.LEFT, padx=10)
            
            yes_button = ctk.CTkButton(
                button_frame,
                text="Oui",
                command=lambda: cleanup_and_action(on_yes),
                width=100,
                fg_color="#2ecc71",
                hover_color="#27ae60"
            )
            yes_button.pack(side=ctk.LEFT, padx=10)
            
            dialog.wait_window()
            return result[0]
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la confirmation: {e}")
            try:
                if cls._active_dialog:
                    cls._active_dialog.destroy()
                    cls._active_dialog = None
            except:
                pass
            return False

class SettingsView:
    """
    Vue des paramètres optimisée
    """
    
    def __init__(self, parent: tk.Widget, app_model: Any):
        """
        Initialise la vue des paramètres avec optimisations
        """
        self.parent = parent
        self.model = app_model
        self._widgets: Dict[str, Any] = {}
        self._variables: Dict[str, tk.Variable] = {}
        self._update_lock = threading.Lock()
        self._is_updating = False
        self._last_saved_values = {}
        self._save_in_progress = False
        
        # Cache pour les widgets fréquemment utilisés
        self._widget_cache = {}
        
        # Cadre principal de la vue
        self.frame = ctk.CTkFrame(parent)
        
        # Créer les composants de l'interface
        self._create_widgets()
        
        # Configurer les observateurs
        self._setup_observers()
        
        logger.info("SettingsView initialisée")
    
    def _setup_observers(self):
        """Configure les observateurs pour les variables"""
        for key, var in self._variables.items():
            var.trace_add("write", partial(self._on_variable_change, key))
    
    def _on_variable_change(self, key: str, *args):
        """Gère les changements de variables"""
        if self._is_updating:
            return
            
        try:
            with self._update_lock:
                # Mettre à jour les widgets dépendants
                if key == "app.auto_save":
                    save_interval_widget = self._widgets.get("app.save_interval")
                    if save_interval_widget:
                        save_interval_widget.configure(
                            state="normal" if self._variables[key].get() else "disabled"
                        )
                elif key == "security.auto_lock":
                    lock_time_widget = self._widgets.get("security.lock_time")
                    if lock_time_widget:
                        lock_time_widget.configure(
                            state="normal" if self._variables[key].get() else "disabled"
                        )
                elif key == "app.theme":
                    # Sauvegarder le thème dans les préférences utilisateur
                    try:
                        from utils.usage_tracker import UsageTracker
                        usage_tracker = UsageTracker()
                        if usage_tracker.is_user_registered():
                            user_data = usage_tracker.get_user_data() or {}
                            user_data["theme"] = self._variables[key].get()
                            usage_tracker.save_user_data(user_data)
                    except Exception as e:
                        logger.error(f"Erreur lors de la sauvegarde du thème dans les préférences utilisateur: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des widgets: {e}")
            self._restore_last_saved_values()

    def _backup_current_values(self):
        """Sauvegarde les valeurs actuelles"""
        try:
            self._last_saved_values = {
                key: var.get() for key, var in self._variables.items()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des valeurs actuelles: {e}")

    def _restore_last_saved_values(self):
        """Restaure les dernières valeurs sauvegardées"""
        try:
            self._is_updating = True
            for key, value in self._last_saved_values.items():
                if key in self._variables:
                    self._variables[key].set(value)
        except Exception as e:
            logger.error(f"Erreur lors de la restauration des valeurs: {e}")
        finally:
            self._is_updating = False

    def _normalize_path(self, path: str) -> str:
        """Normalise un chemin pour le système d'exploitation actuel"""
        if not path:
            return path
        try:
            # Convertir les séparateurs pour le système actuel
            normalized = os.path.normpath(path)
            # Assurer un chemin absolu
            if not os.path.isabs(normalized):
                normalized = os.path.abspath(normalized)
            return normalized
        except Exception as e:
            logger.error(f"Erreur lors de la normalisation du chemin {path}: {e}")
            return path

    def _validate_settings(self, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Valide les paramètres avant la sauvegarde"""
        try:
            # Valider les chemins
            for path_key in ["paths.documents", "paths.templates"]:
                path = settings.get(path_key)
                if path:
                    try:
                        normalized_path = self._normalize_path(path)
                        if not os.path.isabs(normalized_path):
                            return False, f"Le chemin {path_key} doit être absolu"
                        settings[path_key] = normalized_path
                    except Exception as e:
                        return False, f"Chemin invalide pour {path_key}: {str(e)}"
            
            # Valider l'intervalle de sauvegarde
            if settings.get("app.auto_save"):
                save_interval = settings.get("app.save_interval", 0)
                try:
                    save_interval = int(save_interval)
                    if not (1 <= save_interval <= 30):
                        return False, "L'intervalle de sauvegarde doit être entre 1 et 30 minutes"
                except ValueError:
                    return False, "L'intervalle de sauvegarde doit être un nombre entier"
            
            # Valider le délai de verrouillage
            if settings.get("security.auto_lock"):
                lock_time = settings.get("security.lock_time", 0)
                try:
                    lock_time = int(lock_time)
                    if not (1 <= lock_time <= 60):
                        return False, "Le délai de verrouillage doit être entre 1 et 60 minutes"
                except ValueError:
                    return False, "Le délai de verrouillage doit être un nombre entier"
            
            # Valider le format de date
            date_format = settings.get("document.date_format", "")
            if not date_format:
                return False, "Le format de date ne peut pas être vide"
            try:
                from datetime import datetime
                datetime.now().strftime(date_format)
            except ValueError as e:
                return False, f"Format de date invalide: {str(e)}"
            
            # Valider le pattern de nom de fichier
            filename_pattern = settings.get("document.filename_pattern", "")
            if not filename_pattern:
                return False, "Le modèle de nom de fichier ne peut pas être vide"
            
            required_placeholders = ["{document_type}", "{client_name}", "{date}"]
            if not all(ph in filename_pattern for ph in required_placeholders):
                return False, "Le modèle de nom de fichier doit contenir {document_type}, {client_name} et {date}"
            
            # Valider les caractères interdits dans le pattern
            invalid_chars = '<>:"/\\|?*'
            if any(c in filename_pattern.replace("{", "").replace("}", "") for c in invalid_chars):
                return False, f"Le modèle de nom de fichier contient des caractères interdits: {invalid_chars}"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation des paramètres: {e}")
            return False, f"Erreur de validation: {str(e)}"

    def _create_widgets(self):
        """
        Crée les widgets de la vue avec optimisations
        """
        # Zone de défilement optimisée
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.frame,
            label_text="",
            label_fg_color="transparent"
        )
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialisation optimisée des variables
        self._init_variables()
        
        # Création optimisée des sections
        self._create_general_settings()
        self._create_path_settings()
        self._create_security_settings()
        self._create_document_settings()
        self._create_backup_settings()
        self._create_license_settings()
        
        # Optimisation du rendu
        self.frame.update_idletasks()

    @lru_cache(maxsize=1)
    def _get_default_values(self) -> Dict[str, Any]:
        """
        Retourne les valeurs par défaut (mise en cache)
        """
        return {
            "app.name": "Vynal Docs Automator",
            "app.theme": "dark",
            "app.company_name": "",
            "app.company_logo": "",
            "app.auto_save": True,
            "app.save_interval": 5,
            "paths.documents": "",
            "paths.templates": "",
            "security.require_password": False,
            "security.auto_lock": False,
            "security.lock_time": 10,
            "document.default_format": "pdf",
            "document.filename_pattern": "{document_type}_{client_name}_{date}",
            "document.date_format": "%Y-%m-%d"
        }

    def _init_variables(self):
        """
        Initialise les variables Tkinter de manière optimisée
        """
        defaults = self._get_default_values()
        
        for key, default_value in defaults.items():
            var_type = type(default_value)
            try:
                # Vérifier si config existe et a une méthode get
                config_value = default_value
                if hasattr(self.model, 'config') and self.model.config is not None and hasattr(self.model.config, 'get'):
                    config_value = self.model.config.get(key, default_value)
                
                if var_type == bool:
                    self._variables[key] = ctk.BooleanVar(value=config_value)
                elif var_type == int:
                    self._variables[key] = ctk.IntVar(value=config_value)
                else:
                    self._variables[key] = ctk.StringVar(value=config_value)
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation de la variable {key}: {e}")
                # En cas d'erreur, initialiser avec la valeur par défaut
                if var_type == bool:
                    self._variables[key] = ctk.BooleanVar(value=default_value)
                elif var_type == int:
                    self._variables[key] = ctk.IntVar(value=default_value)
                else:
                    self._variables[key] = ctk.StringVar(value=default_value)

    def _create_section(self, title: str) -> ctk.CTkFrame:
        """
        Crée une section optimisée
        """
        section_frame = ctk.CTkFrame(self.scrollable_frame)
        section_frame.pack(fill=ctk.X, pady=10)
        
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=10, pady=5)
        
        separator = ctk.CTkFrame(section_frame, height=1, fg_color="gray")
        separator.pack(fill=ctk.X, padx=10, pady=5)
        
        return section_frame

    def _create_setting_widget(self, 
                             parent: tk.Widget,
                             label: str,
                             description: str,
                             widget_type: str,
                             variable: tk.Variable,
                             options: Optional[Any] = None) -> None:
        """
        Crée un widget de paramètre optimisé
        """
        setting_frame = ctk.CTkFrame(parent, fg_color="transparent")
        setting_frame.pack(fill=ctk.X, pady=5)
        
        # Zone d'étiquette optimisée
        label_frame = ctk.CTkFrame(setting_frame, fg_color="transparent", width=200)
        label_frame.pack(side=ctk.LEFT, padx=10, fill=ctk.Y)
        label_frame.pack_propagate(False)
        
        # Étiquettes optimisées
        ctk.CTkLabel(
            label_frame,
            text=label,
            anchor="w",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(5, 0))
        
        if description:
            ctk.CTkLabel(
                label_frame,
                text=description,
                anchor="w",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            ).pack(anchor="w", pady=(0, 5))
        
        # Zone de widget optimisée
        widget_frame = ctk.CTkFrame(setting_frame, fg_color="transparent")
        widget_frame.pack(side=ctk.RIGHT, padx=10, fill=ctk.BOTH, expand=True)
        
        # Création optimisée du widget selon le type
        if widget_type == "entry":
            entry = ctk.CTkEntry(widget_frame, textvariable=variable, width=250)
            entry.pack(side=ctk.RIGHT, pady=5)
            
        elif widget_type == "combobox":
            combo = ctk.CTkComboBox(
                widget_frame,
                values=options,
                variable=variable,
                width=250,
                state="readonly"
            )
            combo.pack(side=ctk.RIGHT, pady=5)
            
        elif widget_type == "switch":
            switch = ctk.CTkSwitch(
                widget_frame,
                text="",
                variable=variable,
                onvalue=True,
                offvalue=False
            )
            switch.pack(side=ctk.RIGHT, pady=5)
            
        elif widget_type == "slider":
            min_val, max_val = options
            slider_frame = ctk.CTkFrame(widget_frame, fg_color="transparent")
            slider_frame.pack(side=ctk.RIGHT, fill=ctk.X, expand=True, pady=5)
            
            slider = ctk.CTkSlider(
                slider_frame,
                from_=min_val,
                to=max_val,
                number_of_steps=max_val-min_val,
                variable=variable
            )
            slider.pack(side=ctk.LEFT, fill=ctk.X, expand=True, pady=5)
            
            value_label = ctk.CTkLabel(slider_frame, text=str(variable.get()), width=30)
            value_label.pack(side=ctk.RIGHT, padx=10)
            
            # Mise à jour optimisée de l'étiquette
            def update_value(*_):
                try:
                    value_label.configure(text=str(int(variable.get())))
                except (ValueError, tk.TclError):
                    pass
            
            variable.trace_add("write", update_value)
            
        elif widget_type in ("file", "directory"):
            file_frame = ctk.CTkFrame(widget_frame, fg_color="transparent")
            file_frame.pack(side=ctk.RIGHT, fill=ctk.X, expand=True, pady=5)
            
            entry = ctk.CTkEntry(file_frame, textvariable=variable, width=200)
            entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True)
            
            def browse():
                if widget_type == "file":
                    path = filedialog.askopenfilename(
                        filetypes=options if options else [("Tous les fichiers", "*.*")]
                    )
                else:
                    path = filedialog.askdirectory()
                
                if path:
                    variable.set(path)
            
            browse_button = ctk.CTkButton(
                file_frame,
                text="Parcourir",
                width=80,
                command=browse
            )
            browse_button.pack(side=ctk.RIGHT, padx=5)

    def show(self):
        """
        Affiche la vue
        """
        self.frame.pack(fill=ctk.BOTH, expand=True)
        self.update_view()

    def hide(self):
        """
        Masque la vue
        """
        self.frame.pack_forget()

    def update_view(self):
        """
        Met à jour la vue avec les données actuelles
        """
        if hasattr(self, '_is_updating') and self._is_updating:
            return

        try:
            if hasattr(self, '_is_updating'):
                self._is_updating = True
                
            # Mettre à jour les variables avec des valeurs par défaut si non définies
            defaults = self._get_default_values()
            for key, default_value in defaults.items():
                try:
                    # Vérifier si config existe et a une méthode get
                    config_value = default_value
                    if hasattr(self.model, 'config') and self.model.config is not None and hasattr(self.model.config, 'get'):
                        config_value = self.model.config.get(key, default_value)
                    
                    if key in self._variables:
                        self._variables[key].set(config_value)
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de {key}: {e}")
                    # En cas d'erreur, utiliser la valeur par défaut
                    if key in self._variables:
                        self._variables[key].set(default_value)
                    continue
            
            # Supprimer et récréer les sections existantes pour garantir qu'elles sont à jour
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Recréer les sections
            self._create_general_settings()
            self._create_path_settings()
            self._create_document_settings()
            self._create_security_settings()
            self._create_backup_settings()
            self._create_license_settings()

            logger.info("SettingsView mise à jour")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la vue: {e}")
        finally:
            if hasattr(self, '_is_updating'):
                self._is_updating = False

    def _create_general_settings(self):
        """
        Crée la section des paramètres généraux
        """
        section = self._create_section("Paramètres généraux")
        
        # Nom de l'entreprise
        self._create_setting_widget(
            section,
            "Nom de l'entreprise",
            "Nom qui apparaîtra sur les documents",
            "entry",
            self._variables["app.company_name"]
        )
        
        # Logo de l'entreprise
        self._create_setting_widget(
            section,
            "Logo de l'entreprise",
            "Image qui apparaîtra sur les documents",
            "file",
            self._variables["app.company_logo"],
            [("Images", "*.png;*.jpg;*.jpeg")]
        )
        
        # Thème
        self._create_setting_widget(
            section,
            "Thème",
            "Apparence de l'application",
            "combobox",
            self._variables["app.theme"],
            ["system", "light", "dark"]
        )
        
        # Sauvegarde automatique
        self._create_setting_widget(
            section,
            "Sauvegarde automatique",
            "Enregistrer automatiquement les modifications",
            "switch",
            self._variables["app.auto_save"]
        )
        
        # Intervalle de sauvegarde
        self._create_setting_widget(
            section,
            "Intervalle de sauvegarde",
            "Minutes entre chaque sauvegarde automatique",
            "slider",
            self._variables["app.save_interval"],
            (1, 30)
        )

    def _create_path_settings(self):
        """
        Crée la section des paramètres de chemins
        """
        section = self._create_section("Dossiers par défaut")
        
        # Dossier des documents
        self._create_setting_widget(
            section,
            "Dossier des documents",
            "Emplacement des documents générés",
            "directory",
            self._variables["paths.documents"]
        )
        
        # Dossier des modèles
        self._create_setting_widget(
            section,
            "Dossier des modèles",
            "Emplacement des modèles de documents",
            "directory",
            self._variables["paths.templates"]
        )

    def _create_security_settings(self):
        """
        Crée la section des paramètres de sécurité
        """
        section = self._create_section("Sécurité")
        
        # Protection par mot de passe
        password_frame = ctk.CTkFrame(section, fg_color="transparent")
        password_frame.pack(fill=ctk.X, pady=5)
        
        # Zone d'étiquette
        label_frame = ctk.CTkFrame(password_frame, fg_color="transparent", width=200)
        label_frame.pack(side=ctk.LEFT, padx=10, fill=ctk.Y)
        label_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            label_frame,
            text="Protection par mot de passe",
            anchor="w",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(5, 0))
        
        ctk.CTkLabel(
            label_frame,
            text="Demander un mot de passe au démarrage",
            anchor="w",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 5))
        
        # Zone de widget
        widget_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        widget_frame.pack(side=ctk.RIGHT, padx=10, fill=ctk.BOTH, expand=True)
        
        # Switch pour activer/désactiver la protection
        switch = ctk.CTkSwitch(
            widget_frame,
            text="",
            variable=self._variables["security.require_password"],
            onvalue=True,
            offvalue=False,
            command=self._on_password_protection_change
        )
        switch.pack(side=ctk.RIGHT, pady=5)
        
        # Verrouillage automatique
        self._create_setting_widget(
            section,
            "Verrouillage automatique",
            "Verrouiller après une période d'inactivité",
            "switch",
            self._variables["security.auto_lock"]
        )
        
        # Délai de verrouillage
        self._create_setting_widget(
            section,
            "Délai de verrouillage",
            "Minutes d'inactivité avant verrouillage",
            "slider",
            self._variables["security.lock_time"],
            (1, 60)
        )

    def _on_password_protection_change(self):
        """Gère le changement d'état de la protection par mot de passe"""
        try:
            if self._variables["security.require_password"].get():
                self._show_password_dialog()
            else:
                # Désactiver la protection par mot de passe
                self.model.config.set("security.require_password", False)
                # Sauvegarder immédiatement la configuration
                self.model.config.save()
        except Exception as e:
            logger.error(f"Erreur lors du changement de la protection par mot de passe: {e}")
            self._variables["security.require_password"].set(False)

    def _show_password_dialog(self):
        """Affiche le dialogue de configuration du mot de passe"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Configuration du mot de passe")
        dialog.geometry("400x350")  # Augmenté la hauteur pour mieux afficher les boutons
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Centrer le dialogue
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal avec padding
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔒 Configuration du mot de passe",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Message avec les exigences
        message_label = ctk.CTkLabel(
            main_frame,
            text="Le mot de passe doit contenir au moins:\n- 6 caractères\n- 1 chiffre\n- 1 caractère spécial (!@#$%^&*)",
            wraplength=300,
            justify="left"
        )
        message_label.pack(pady=(0, 15))
        
        # Frame pour les champs de saisie
        entry_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        entry_frame.pack(fill=ctk.X, pady=(0, 15))
        
        # Champs de mot de passe
        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Mot de passe",
            show="•",
            width=250,
            textvariable=password_var
        )
        password_entry.pack(pady=(0, 10))
        
        confirm_var = ctk.StringVar()
        confirm_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Confirmer le mot de passe",
            show="•",
            width=250,
            textvariable=confirm_var
        )
        confirm_entry.pack(pady=(0, 10))
        
        # Message d'erreur
        error_label = ctk.CTkLabel(
            main_frame,
            text="",
            text_color="red",
            wraplength=300
        )
        error_label.pack(pady=(0, 15))
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill=ctk.X, pady=(10, 0))
        
        def validate_and_save():
            """Valide et enregistre le mot de passe"""
            try:
                password = password_var.get()
                confirm = confirm_var.get()
                
                if not password:
                    error_label.configure(text="Le mot de passe ne peut pas être vide")
                    return
                
                if password != confirm:
                    error_label.configure(text="Les mots de passe ne correspondent pas")
                    return
                
                if len(password) < 6:
                    error_label.configure(text="Le mot de passe doit contenir au moins 6 caractères")
                    return
                
                # Vérifier la présence d'un chiffre
                if not any(c.isdigit() for c in password):
                    error_label.configure(text="Le mot de passe doit contenir au moins un chiffre")
                    return
                
                # Vérifier la présence d'un caractère spécial
                special_chars = "!@#$%^&*"
                if not any(c in special_chars for c in password):
                    error_label.configure(text="Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*)")
                    return
                
                # Hasher le mot de passe
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Sauvegarder le hash et activer la protection
                self.model.config.set("security.password_hash", password_hash)
                self.model.config.set("security.require_password", True)
                
                # Sauvegarder immédiatement la configuration
                self.model.config.save()
                
                dialog.destroy()
                
                # Afficher un message de succès
                DialogUtils.show_message(
                    self.parent,
                    "Protection activée",
                    "La protection par mot de passe a été activée avec succès.",
                    "success"
                )
                
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde du mot de passe: {e}")
                error_label.configure(text="Une erreur est survenue lors de la sauvegarde")
                self._variables["security.require_password"].set(False)
        
        def cancel():
            """Annule la configuration du mot de passe"""
            self._variables["security.require_password"].set(False)
            dialog.destroy()
        
        # Boutons avec taille fixe
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            width=120,
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=cancel
        )
        cancel_button.pack(side=ctk.LEFT, padx=10)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Enregistrer",
            width=120,
            height=35,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=validate_and_save
        )
        save_button.pack(side=ctk.RIGHT, padx=10)
        
        # Focus sur le premier champ
        password_entry.focus()
        
        # Lier la touche Entrée au bouton Enregistrer
        dialog.bind('<Return>', lambda e: validate_and_save())
        
        # Empêcher la fermeture par la croix
        dialog.protocol("WM_DELETE_WINDOW", cancel)

    def _create_document_settings(self):
        """
        Crée la section des paramètres de documents
        """
        section = self._create_section("Format des documents")
        
        # Format par défaut
        self._create_setting_widget(
            section,
            "Format par défaut",
            "Format utilisé lors de la génération de documents",
            "combobox",
            self._variables["document.default_format"],
            ["pdf", "docx"]
        )
        
        # Modèle de nom de fichier
        self._create_setting_widget(
            section,
            "Modèle de nom de fichier",
            "Pattern pour nommer les fichiers (ex: {document_type}_{client_name}_{date})",
            "entry",
            self._variables["document.filename_pattern"]
        )
        
        # Format de date
        self._create_setting_widget(
            section,
            "Format de date",
            "Format des dates dans les noms de fichiers",
            "entry",
            self._variables["document.date_format"]
        )

    def _create_backup_settings(self):
        """
        Crée la section des paramètres de sauvegarde
        """
        section = self._create_section("Sauvegarde et restauration")
        
        # Cadre pour les boutons
        button_frame = ctk.CTkFrame(section, fg_color="transparent")
        button_frame.pack(fill=ctk.X, pady=10)
        
        # Boutons de sauvegarde et restauration
        backup_button = ctk.CTkButton(
            button_frame,
            text="Créer une sauvegarde",
            command=self.create_backup
        )
        backup_button.pack(side=ctk.LEFT, padx=10)
        
        restore_button = ctk.CTkButton(
            button_frame,
            text="Restaurer une sauvegarde",
            command=self.restore_backup
        )
        restore_button.pack(side=ctk.LEFT, padx=10)
        
        reset_button = ctk.CTkButton(
            button_frame,
            text="Réinitialiser",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.reset_settings
        )
        reset_button.pack(side=ctk.RIGHT, padx=10)
        
        # Bouton Enregistrer
        save_frame = ctk.CTkFrame(section, fg_color="transparent")
        save_frame.pack(fill=ctk.X, pady=20)
        
        save_button = ctk.CTkButton(
            save_frame,
            text="Enregistrer les paramètres",
            width=200,
            height=40,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.save_settings
        )
        save_button.pack(side=ctk.RIGHT, padx=10)

    def save_settings(self):
        """Enregistre les paramètres avec validation"""
        try:
            logger.info("Sauvegarde des paramètres initiée")
            # Appeler la méthode _apply_settings qui contient la logique complète
            # y compris la mise à jour du moniteur d'activité
            self._apply_settings()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres: {e}")
            self.show_message(
                "Erreur",
                f"Une erreur est survenue lors de la sauvegarde des paramètres: {e}",
                "error"
            )
            return False

    def create_backup(self):
        """
        Crée une sauvegarde des données avec gestion des erreurs améliorée
        """
        try:
            # Demander l'emplacement de la sauvegarde
            backup_path = filedialog.asksaveasfilename(
                title="Créer une sauvegarde",
                defaultextension=".zip",
                filetypes=[("Fichiers ZIP", "*.zip"), ("Tous les fichiers", "*.*")]
            )
            
            if not backup_path:
                return
            
            # Vérifier l'espace disque disponible
            try:
                import shutil
                free_space = shutil.disk_usage(os.path.dirname(backup_path)).free
                if free_space < 1024 * 1024 * 100:  # 100 MB minimum
                    DialogUtils.show_message(
                        self.parent,
                        "Espace insuffisant",
                        "L'espace disque disponible est insuffisant pour créer la sauvegarde.",
                        "warning"
                    )
                    return
            except Exception as e:
                logger.warning(f"Impossible de vérifier l'espace disque: {e}")
            
            # Créer la sauvegarde
            result = self.model.create_backup(backup_path)
            
            if result:
                DialogUtils.show_message(
                    self.parent,
                    "Sauvegarde créée",
                    f"Sauvegarde créée avec succès:\n{backup_path}",
                    "success"
                )
                logger.info(f"Sauvegarde créée: {backup_path}")
            else:
                DialogUtils.show_message(
                    self.parent,
                    "Erreur",
                    "Impossible de créer la sauvegarde.",
                    "error"
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            DialogUtils.show_message(
                self.parent,
                "Erreur",
                f"Erreur lors de la création de la sauvegarde:\n{str(e)}",
                "error"
            )

    def restore_backup(self):
        """
        Restaure les données à partir d'une sauvegarde avec validation améliorée
        """
        try:
            # Demander le fichier de sauvegarde
            backup_path = filedialog.askopenfilename(
                title="Restaurer une sauvegarde",
                filetypes=[("Fichiers ZIP", "*.zip"), ("Tous les fichiers", "*.*")]
            )
            
            if not backup_path:
                return
            
            # Vérifier la taille du fichier
            try:
                backup_size = os.path.getsize(backup_path)
                if backup_size > 1024 * 1024 * 500:  # 500 MB maximum
                    DialogUtils.show_message(
                        self.parent,
                        "Fichier trop volumineux",
                        "Le fichier de sauvegarde est trop volumineux.",
                        "warning"
                    )
                    return
            except Exception as e:
                logger.warning(f"Impossible de vérifier la taille du fichier: {e}")
            
            def process_restore():
                try:
                    # Vérifier l'intégrité de la sauvegarde
                    import zipfile
                    try:
                        with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                            if zip_ref.testzip() is not None:
                                raise ValueError("Le fichier de sauvegarde est corrompu")
                    except zipfile.BadZipFile:
                        raise ValueError("Le fichier n'est pas une sauvegarde valide")
                    
                    # Restaurer la sauvegarde
                    result = self.model.restore_backup(backup_path)
                    
                    if result:
                        DialogUtils.show_message(
                            self.parent,
                            "Restauration terminée",
                            "La sauvegarde a été restaurée avec succès.\nVeuillez redémarrer l'application pour appliquer les changements.",
                            "success"
                        )
                        logger.info(f"Sauvegarde restaurée: {backup_path}")
                        
                        # Mettre à jour la vue
                        self.update_view()
                    else:
                        DialogUtils.show_message(
                            self.parent,
                            "Erreur",
                            "Impossible de restaurer la sauvegarde.",
                            "error"
                        )
                except Exception as e:
                    logger.error(f"Erreur lors de la restauration: {e}")
                    DialogUtils.show_message(
                        self.parent,
                        "Erreur",
                        f"Erreur lors de la restauration:\n{str(e)}",
                        "error"
                    )
            
            # Demander confirmation
            DialogUtils.show_confirmation(
                self.parent,
                "Confirmer la restauration",
                "Restaurer une sauvegarde remplacera toutes vos données actuelles. Cette action est irréversible.\n\nÊtes-vous sûr de vouloir continuer?",
                on_yes=process_restore
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration de la sauvegarde: {e}")
            DialogUtils.show_message(
                self.parent,
                "Erreur",
                f"Erreur lors de la restauration de la sauvegarde:\n{str(e)}",
                "error"
            )

    def reset_settings(self):
        """
        Réinitialise les paramètres aux valeurs par défaut
        """
        # Demander confirmation
        def confirm_reset():
            try:
                # Définir des valeurs par défaut sécurisées
                default_values = {
                    "app.name": "Vynal Docs Automator",
                    "app.theme": "dark",
                    "app.company_name": "Vynal Docs",
                    "app.company_logo": "",
                    "app.auto_save": True,
                    "app.save_interval": 5,
                    "paths.documents": os.path.join(os.path.expanduser("~"), "VynalDocs", "Documents"),
                    "paths.templates": os.path.join(os.path.expanduser("~"), "VynalDocs", "Templates"),
                    "security.require_password": False,
                    "security.auto_lock": False,
                    "security.lock_time": 10,
                    "document.default_format": "pdf",
                    "document.filename_pattern": "{document_type}_{client_name}_{date}",
                    "document.date_format": "%Y-%m-%d"
                }
                
                # Éviter d'utiliser la méthode reset_to_defaults qui peut causer des problèmes
                # Définir directement les valeurs dans la configuration
                try:
                    # Sauvegarder le thème actuel pour le restaurer après
                    current_theme = self.model.config.get("app.theme", "dark")
                    
                    # Définir chaque valeur individuellement
                    for key, value in default_values.items():
                        self.model.config.set(key, value)
                    
                    # Créer les répertoires nécessaires
                    os.makedirs(default_values["paths.documents"], exist_ok=True)
                    os.makedirs(default_values["paths.templates"], exist_ok=True)
                    
                    # Mettre à jour les chemins dans le modèle
                    self.model.paths['documents'] = default_values["paths.documents"]
                    self.model.paths['templates'] = default_values["paths.templates"]
                    
                    # Mettre à jour la vue sans toucher au thème pour l'instant
                    self._variables["app.company_name"].set(default_values["app.company_name"])
                    self._variables["app.company_logo"].set(default_values["app.company_logo"])
                    self._variables["app.theme"].set(default_values["app.theme"])
                    self._variables["app.auto_save"].set(default_values["app.auto_save"])
                    self._variables["app.save_interval"].set(default_values["app.save_interval"])
                    self._variables["paths.documents"].set(default_values["paths.documents"])
                    self._variables["paths.templates"].set(default_values["paths.templates"])
                    self._variables["security.require_password"].set(default_values["security.require_password"])
                    self._variables["security.auto_lock"].set(default_values["security.auto_lock"])
                    self._variables["security.lock_time"].set(default_values["security.lock_time"])
                    self._variables["document.default_format"].set(default_values["document.default_format"])
                    self._variables["document.filename_pattern"].set(default_values["document.filename_pattern"])
                    self._variables["document.date_format"].set(default_values["document.date_format"])
                    
                    # Afficher un message de succès
                    DialogUtils.show_message(
                        self.parent,
                        "Paramètres réinitialisés",
                        "Les paramètres ont été réinitialisés aux valeurs par défaut.",
                        "success"
                    )
                    
                    logger.info("Paramètres réinitialisés avec succès")
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la réinitialisation des paramètres: {e}")
                    DialogUtils.show_message(
                        self.parent,
                        "Erreur",
                        f"Erreur lors de la réinitialisation des paramètres:\n{str(e)}",
                        "error"
                    )
            except Exception as e:
                logger.error(f"Erreur globale lors de la réinitialisation des paramètres: {e}")
                DialogUtils.show_message(
                    self.parent,
                    "Erreur",
                    f"Une erreur inattendue s'est produite:\n{str(e)}",
                    "error"
                )
        
        DialogUtils.show_confirmation(
            self.parent,
            "Confirmer la réinitialisation",
            "Êtes-vous sûr de vouloir réinitialiser tous les paramètres aux valeurs par défaut ?",
            on_yes=confirm_reset
        )

    def _create_license_settings(self):
        """
        Crée la section des paramètres de licence avec un bouton unique pour gérer la licence
        """
        # Créer la section
        section = self._create_section("Licence et Activation")
        
        # Bouton principal pour gérer la licence
        manage_license_button = ctk.CTkButton(
            section,
            text="Gérer ma licence",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.show_license_management
        )
        manage_license_button.pack(pady=20, padx=20)
        
        # Ajouter une description
        description = ctk.CTkLabel(
            section,
            text="Accédez aux informations de votre licence, vérifiez son statut ou activez un nouveau produit.",
            wraplength=400,
            justify="center"
        )
        description.pack(pady=(0, 20), padx=20)

    def show_license_management(self):
        """
        Affiche la boîte de dialogue de gestion de licence
        """
        # Créer la fenêtre de gestion de licence
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Gestion de licence")
        dialog.geometry("650x580")
        dialog.grab_set()
        dialog.resizable(True, True)  # Rendre la fenêtre redimensionnable
        dialog.minsize(650, 580)  # Définir une taille minimale
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Récupérer l'email et la licence actuelle si disponible
        email = ""
        license_key = ""
        license_data = None
        is_license_valid = False
        verification_time = 0
        
        try:
            # Essayer de récupérer l'email et les données de licence de l'utilisateur
            from utils.usage_tracker import UsageTracker
            import time
            import os
            usage_tracker = UsageTracker()
            
            # Forcer la vérification des fichiers pour s'assurer que les données sont correctement chargées
            user_data_file = os.path.join(usage_tracker.data_dir, "current_user.json")
            logger.info(f"Tentative de chargement des données utilisateur depuis: {user_data_file}")
            
            if usage_tracker.is_user_registered():
                user_data = usage_tracker.get_user_data() or {}
                logger.info(f"Données utilisateur chargées: {user_data}")
                
                email = user_data.get('email', '')
                license_key = user_data.get('license_key', '')
                is_license_valid = user_data.get('license_valid', False)
                verification_time = user_data.get('license_verified_at', 0)
                
                logger.info(f"État de licence chargé - Email: {email}, Licence valide: {is_license_valid}, Vérifiée le: {verification_time}")
            
            # Récupérer la licence actuelle si elle existe
            if email and hasattr(self.model, 'license_model') and self.model.license_model:
                license_data = self.model.license_model.get_license(email)
                logger.info(f"Données de licence récupérées: {license_data != None}")
                
                # Double vérification avec la licence actuelle
                if license_data and is_license_valid:
                    logger.info("Licence valide confirmée par les données de licence")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations utilisateur: {e}")
        
        # Fonction pour masquer la clé de licence
        def mask_license_key(key):
            if not key or len(key) < 8:
                return key
            visible_chars = 4  # Nombre de caractères visibles à la fin
            masked_part = '*' * (len(key) - visible_chars)
            visible_part = key[-visible_chars:]
            return masked_part + visible_part
        
        # Cadre principal avec défilement
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = ctk.CTkLabel(
            main_frame,
            text="Informations de licence",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(10, 25))
        
        # Section pour l'entrée/vérification de licence
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        # Email
        email_label = ctk.CTkLabel(
            input_frame,
            text="Email :",
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="e"
        )
        email_label.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="e")
        
        email_var = ctk.StringVar(value=email)
        email_entry = ctk.CTkEntry(
            input_frame,
            width=350,
            textvariable=email_var,
            placeholder_text="Entrez votre adresse email"
        )
        email_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Clé de licence
        key_label = ctk.CTkLabel(
            input_frame,
            text="Clé :",
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="e"
        )
        key_label.grid(row=1, column=0, padx=(10, 10), pady=10, sticky="e")
        
        # Si la licence est valide, masquer la clé
        displayed_key = mask_license_key(license_key) if is_license_valid else license_key
        
        key_var = ctk.StringVar(value=displayed_key)
        key_entry = ctk.CTkEntry(
            input_frame,
            width=350,
            textvariable=key_var,
            placeholder_text="Entrez votre clé de licence",
            show="•" if is_license_valid else ""  # Masquer les caractères si licence valide
        )
        key_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Configurer le redimensionnement
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Section d'informations de licence
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre de la section
        info_title = ctk.CTkLabel(
            info_frame,
            text="Détails de la licence",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        info_title.pack(pady=(15, 20))
        
        # Tableau d'informations (grid layout)
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(fill=ctk.BOTH, expand=True, padx=30, pady=10)
        
        # Fonction pour créer une ligne d'information
        def create_info_row(parent, row, label_text, value_text="", value_color=None):
            label = ctk.CTkLabel(
                parent,
                text=label_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                width=150,
                anchor="w"
            )
            label.grid(row=row, column=0, padx=10, pady=8, sticky="w")
            
            value = ctk.CTkLabel(
                parent,
                text=value_text,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            if value_color:
                value.configure(text_color=value_color)
            value.grid(row=row, column=1, padx=10, pady=8, sticky="w")
            return value
        
        # Dictionnaire pour stocker l'état de la vérification
        verification_state = {
            "is_verified": is_license_valid,
            "license_data": license_data
        }
        
        # Créer les lignes d'information avec l'état initial
        initial_status = "Active" if is_license_valid else "Non vérifié"
        initial_color = "#27ae60" if is_license_valid else ("gray70", "gray70")
        
        status_value = create_info_row(details_frame, 0, "Statut:", initial_status, initial_color)
        type_value = create_info_row(details_frame, 1, "Type de licence:", "Non disponible")
        activation_value = create_info_row(details_frame, 2, "Date d'activation:", "Non disponible")
        expiration_value = create_info_row(details_frame, 3, "Date d'expiration:", "Non disponible")
        features_label = create_info_row(details_frame, 4, "Fonctionnalités:", "")
        
        # Cadre pour les fonctionnalités
        features_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        features_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        
        # Bouton de vérification et renouvellement
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill=ctk.X, padx=10, pady=(5, 15))
        
        # Définir les fonctions pour les boutons
        def open_renewal_page():
            try:
                import webbrowser
                webbrowser.open("https://vynaldocs.com/renew")
            except Exception as e:
                logger.error(f"Impossible d'ouvrir la page de renouvellement: {e}")
                from views.settings_view import DialogUtils
                DialogUtils.show_message(
                    dialog,
                    "Information",
                    "Pour renouveler votre licence, veuillez vous rendre sur notre site web: https://vynaldocs.com/renew",
                    "info"
                )
        
        def do_verify_license():
            """Fonction qui sera appelée quand on clique sur le bouton Vérifier ma licence"""
            try:
                # Récupérer les valeurs des entrées
                email = email_var.get().strip()
                license_key = key_var.get().strip()
                
                # Si la licence est déjà vérifiée et que l'utilisateur n'a pas modifié les données, ne pas revérifier
                if verification_state["is_verified"] and displayed_key == key_var.get():
                    logger.info("La licence est déjà vérifiée, pas besoin de revérifier.")
                    return
                
                logger.info(f"Vérification de licence: {email}, clé: {license_key}")
                
                # Réinitialiser les valeurs d'affichage
                status_value.configure(text="Non vérifié", text_color=("gray70", "gray70"))
                type_value.configure(text="Non disponible")
                activation_value.configure(text="Non disponible")
                expiration_value.configure(text="Non disponible")
                
                # Nettoyer le cadre des fonctionnalités
                for widget in features_frame.winfo_children():
                    widget.destroy()
                
                # Vérifier que les champs sont remplis
                if not email:
                    status_value.configure(text="Erreur: Email requis", text_color="#e74c3c")
                    return
                
                if not license_key:
                    status_value.configure(text="Erreur: Clé de licence requise", text_color="#e74c3c")
                    return
                
                # Vérifier la validité de l'email
                import re
                email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(email_pattern, email):
                    status_value.configure(text="Erreur: Email invalide", text_color="#e74c3c")
                    return
                
                license_valid = False
                license_data = None
                
                # Définir une variable pour suivre le statut de la vérification
                verification_result = False
                verification_message = ""
                
                # Vérifier si le modèle de licence existe
                if hasattr(self.model, 'license_model') and self.model.license_model:
                    # Utiliser directement la méthode check_license_is_valid du modèle
                    verification_result, verification_message, license_data_from_check = self.model.license_model.check_license_is_valid(email, license_key)
                    
                    # Récupérer les données complètes de la licence si non fournies
                    if not license_data_from_check:
                        license_data = self.model.license_model.get_license(email)
                    else:
                        license_data = license_data_from_check
                    license_valid = verification_result
                else:
                    # Fallback vers l'utilitaire de licence si le modèle n'est pas disponible
                    from utils.license_utils import verify_license as verify_license_func
                    verification_result, verification_message, license_data = verify_license_func(email, license_key)
                    license_valid = verification_result
                
                logger.info(f"Résultat de vérification: {verification_result}, message: {verification_message}")
                
                # Mettre à jour l'état de vérification
                verification_state["is_verified"] = license_valid
                verification_state["license_data"] = license_data
                
                if license_valid:
                    # Mettre à jour les informations de licence
                    status_value.configure(text="Active", text_color="#27ae60")
                    
                    # Masquer la clé de licence après vérification réussie
                    masked_key = mask_license_key(license_key)
                    key_var.set(masked_key)
                    key_entry.configure(show="•")  # Masquer les caractères
                    
                    # Obtenir les détails de la licence
                    if license_data:
                        from utils.license_utils import get_expiration_date_string
                        
                        # Type de licence
                        license_type = license_data.get("license_type", "Standard").capitalize()
                        type_value.configure(text=license_type)
                        
                        # Date d'activation
                        activation_date = "Non disponible"
                        if "created_at" in license_data:
                            import datetime
                            activation_date = datetime.datetime.fromtimestamp(license_data["created_at"]).strftime("%d/%m/%Y")
                        activation_value.configure(text=activation_date)
                        
                        # Date d'expiration
                        expiration_date = "Non disponible"
                        if "expires_at" in license_data:
                            expiration_date = get_expiration_date_string(license_data)
                        expiration_value.configure(text=expiration_date)
                        
                        # Fonctionnalités
                        if "features" in license_data and license_data["features"]:
                            for i, feature in enumerate(license_data["features"]):
                                feature_label = ctk.CTkLabel(
                                    features_frame,
                                    text=f"• {feature}",
                                    font=ctk.CTkFont(size=13),
                                    anchor="w"
                                )
                                feature_label.pack(anchor="w", padx=20, pady=2)
                    
                    # Mémoriser l'état de la licence dans UsageTracker
                    try:
                        from utils.usage_tracker import UsageTracker
                        import time
                        usage_tracker = UsageTracker()
                        user_data = usage_tracker.get_user_data() or {}
                        user_data['email'] = email
                        user_data['license_key'] = license_key
                        user_data['license_valid'] = True
                        user_data['license_verified_at'] = int(time.time())
                        # Utiliser explicitement save_user_data qui est maintenant disponible
                        success = usage_tracker.save_user_data(user_data)
                        logger.info(f"Sauvegarde des données de licence réussie: {success}")
                        
                        # Si la sauvegarde échoue, utiliser set_current_user comme fallback
                        if not success:
                            logger.warning("Échec de save_user_data, utilisation de set_current_user comme fallback")
                            usage_tracker.set_current_user(user_data)
                        
                        # Message de succès
                        from views.settings_view import DialogUtils
                        DialogUtils.show_message(
                            dialog,
                            "Licence valide",
                            f"Votre licence {license_data.get('license_type', 'Standard').capitalize() if license_data else 'Standard'} est active et valide.",
                            "success"
                        )
                        
                        # Mettre à jour l'interface utilisateur pour refléter la nouvelle licence
                        if hasattr(self.model, 'main_view') and self.model.main_view:
                            # Forcer la mise à jour globale de l'application via la vue principale
                            self.model.main_view.refresh_license_status()
                            
                            # Informer le contrôleur principal du changement d'état de la licence
                            if hasattr(self.model, 'on_license_updated') and callable(self.model.on_license_updated):
                                self.model.on_license_updated(email, license_key, True)
                    except Exception as e:
                        logger.error(f"Erreur lors de la sauvegarde des données utilisateur: {e}")
                else:
                    # Déterminer le statut de la licence
                    status_text = "Invalide"
                    status_color = "#e74c3c"  # Rouge
                    
                    if verification_message:
                        if "blocked" in verification_message.lower() or "bloquée" in verification_message.lower():
                            status_text = "Bloquée"
                        elif "expired" in verification_message.lower() or "expirée" in verification_message.lower():
                            status_text = "Expirée"
                            status_color = "#f39c12"  # Orange
                    
                    status_value.configure(text=status_text, text_color=status_color)
                    
                    # Si nous avons des données partielles, les afficher
                    if license_data:
                        from utils.license_utils import get_expiration_date_string
                        
                        if "license_type" in license_data:
                            type_value.configure(text=license_data.get("license_type", "Standard").capitalize())
                        
                        if "created_at" in license_data:
                            import datetime
                            activation_date = datetime.datetime.fromtimestamp(license_data["created_at"]).strftime("%d/%m/%Y")
                            activation_value.configure(text=activation_date)
                        
                        if "expires_at" in license_data:
                            expiration_date = get_expiration_date_string(license_data)
                            expiration_value.configure(text=expiration_date)
                    
                    # Mémoriser l'état invalide de la licence
                    try:
                        from utils.usage_tracker import UsageTracker
                        import time
                        usage_tracker = UsageTracker()
                        user_data = usage_tracker.get_user_data() or {}
                        user_data['email'] = email
                        user_data['license_key'] = license_key
                        user_data['license_valid'] = False
                        user_data['license_verified_at'] = int(time.time())
                        # Utiliser explicitement save_user_data qui est maintenant disponible
                        success = usage_tracker.save_user_data(user_data)
                        logger.info(f"Sauvegarde des données de licence (invalide) réussie: {success}")
                        
                        # Si la sauvegarde échoue, utiliser set_current_user comme fallback
                        if not success:
                            logger.warning("Échec de save_user_data, utilisation de set_current_user comme fallback")
                            usage_tracker.set_current_user(user_data)
                        
                        # Message d'erreur
                        from views.settings_view import DialogUtils
                        DialogUtils.show_message(
                            dialog,
                            "Licence invalide",
                            f"Votre licence n'est pas valide: {verification_message}",
                            "error"
                        )
                        
                        # Mettre à jour l'interface utilisateur pour refléter le changement de licence
                        if hasattr(self.model, 'main_view') and self.model.main_view:
                            # Forcer la mise à jour globale de l'application via la vue principale
                            self.model.main_view.refresh_license_status()
                            
                            # Informer le contrôleur principal du changement d'état de la licence
                            if hasattr(self.model, 'on_license_updated') and callable(self.model.on_license_updated):
                                self.model.on_license_updated(email, license_key, False)
                    except Exception as e:
                        logger.error(f"Erreur lors de la sauvegarde des données utilisateur: {e}")
            
            except ImportError as ie:
                logger.error(f"Module utils.license_utils non disponible: {ie}")
                status_value.configure(text="Erreur: Module de licence manquant", text_color="#e74c3c")
                from views.settings_view import DialogUtils
                DialogUtils.show_message(
                    dialog,
                    "Erreur",
                    "Le module de licence n'est pas disponible. Veuillez contacter le support.",
                    "error"
                )
            except Exception as e:
                logger.error(f"Erreur lors de la vérification de la licence: {e}")
                status_value.configure(text=f"Erreur: {str(e)}", text_color="#e74c3c")
                from views.settings_view import DialogUtils
                DialogUtils.show_message(
                    dialog,
                    "Erreur",
                    f"Une erreur est survenue lors de la vérification: {str(e)}",
                    "error"
                )
        
        # Créer les boutons de vérification et de renouvellement
        verify_button = ctk.CTkButton(
            button_frame,
            text="✅ Vérifier ma licence",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=do_verify_license
        )
        verify_button.pack(side=ctk.LEFT, padx=(100, 0))
        
        renew_button = ctk.CTkButton(
            button_frame,
            text="🔄 Renouveler",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=open_renewal_page
        )
        renew_button.pack(side=ctk.RIGHT, padx=(0, 100))
        
        # Remplir l'interface avec les informations de licence déjà vérifiées si disponibles
        if is_license_valid and license_data:
            try:
                from utils.license_utils import get_expiration_date_string
                
                # Mettre à jour les détails de la licence
                type_value.configure(text=license_data.get("license_type", "Standard").capitalize())
                
                if "created_at" in license_data:
                    import datetime
                    activation_date = datetime.datetime.fromtimestamp(license_data["created_at"]).strftime("%d/%m/%Y")
                    activation_value.configure(text=activation_date)
                
                if "expires_at" in license_data:
                    expiration_date = get_expiration_date_string(license_data)
                    expiration_value.configure(text=expiration_date)
                
                # Afficher les fonctionnalités
                if "features" in license_data and license_data["features"]:
                    for feature in license_data["features"]:
                        feature_label = ctk.CTkLabel(
                            features_frame,
                            text=f"• {feature}",
                            font=ctk.CTkFont(size=13),
                            anchor="w"
                        )
                        feature_label.pack(anchor="w", padx=20, pady=2)
            except Exception as e:
                logger.error(f"Erreur lors de l'affichage des détails de licence: {e}")
        
        # Bouton de fermeture
        close_button = ctk.CTkButton(
            main_frame,
            text="Fermer",
            width=120,
            height=32,
            command=dialog.destroy,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        )
        close_button.pack(pady=15)
        
        # S'assurer que le dialogue reste au premier plan
        dialog.lift()
        dialog.focus_set()
        
        # Fonction pour sauvegarder l'état de la licence avant de fermer
        def save_license_state_and_close():
            try:
                # Sauvegarder à nouveau l'état de la licence pour s'assurer qu'il persiste
                if verification_state["is_verified"]:
                    from utils.usage_tracker import UsageTracker
                    import time
                    usage_tracker = UsageTracker()
                    user_data = usage_tracker.get_user_data() or {}
                    user_data['email'] = email_var.get().strip()
                    user_data['license_key'] = key_var.get().strip()
                    user_data['license_valid'] = verification_state["is_verified"]
                    user_data['license_verified_at'] = int(time.time())
                    
                    # Utiliser save_user_data pour une sauvegarde plus complète
                    success = usage_tracker.save_user_data(user_data)
                    logger.info(f"Sauvegarde finale de l'état de licence réussie: {success}")
                    
                    # Si la sauvegarde échoue, essayer avec set_current_user comme fallback
                    if not success:
                        logger.warning("Échec de save_user_data pour la sauvegarde finale, utilisation de set_current_user")
                        usage_tracker.set_current_user(user_data)
                    
                    # Force aussi la sauvegarde des fichiers
                    try:
                        import os
                        import json
                        
                        # Vérifier que les données sont correctement sauvegardées
                        users_file = os.path.join(usage_tracker.data_dir, "users.json")
                        current_user_file = os.path.join(usage_tracker.data_dir, "current_user.json")
                        
                        if os.path.exists(users_file):
                            with open(users_file, 'r', encoding='utf-8') as f:
                                users = json.load(f)
                                # Vérifier que l'entrée existe
                                if user_data['email'] in users:
                                    logger.info(f"Utilisateur {user_data['email']} trouvé dans users.json")
                                else:
                                    logger.warning(f"Utilisateur {user_data['email']} non trouvé dans users.json")
                        
                        if os.path.exists(current_user_file):
                            with open(current_user_file, 'r', encoding='utf-8') as f:
                                current_user = json.load(f)
                                if current_user.get('email') == user_data['email']:
                                    logger.info(f"Utilisateur actuel {user_data['email']} trouvé dans current_user.json")
                                else:
                                    logger.warning(f"Utilisateur actuel {user_data['email']} ne correspond pas à {current_user.get('email')}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors de la vérification des fichiers utilisateur: {e}")
                    
                    logger.info(f"État de licence sauvegardé à la fermeture pour {email_var.get().strip()}, valide={verification_state['is_verified']}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde de l'état de licence à la fermeture: {e}")
            finally:
                dialog.destroy()
        
        # Remplacer la commande du bouton de fermeture pour sauvegarder l'état avant de fermer
        close_button.configure(command=save_license_state_and_close)
        
        # Remplacer également le gestionnaire de l'événement de fermeture de la fenêtre
        dialog.protocol("WM_DELETE_WINDOW", save_license_state_and_close)

    def show_renew_license_dialog(self):
        """
        Affiche la boîte de dialogue de renouvellement de licence
        """
        # Cette méthode pourrait contenir une logique pour renouveler la licence
        # ou rediriger vers un site web pour le renouvellement
        DialogUtils.show_message(
            self.parent,
            "Renouvellement de licence",
            "Pour renouveler votre licence, veuillez contacter notre service clientèle ou vous rendre sur notre site web.",
            "info"
        )
    
    def deactivate_license(self):
        """
        Désactive la licence de l'utilisateur actuel
        """
        def confirm_deactivation():
            # Récupérer le nom d'utilisateur
            username = None
            if hasattr(self.model, 'current_user') and self.model.current_user is not None:
                username = self.model.current_user.get('username')
            
            if not username:
                DialogUtils.show_message(
                    self.parent,
                    "Erreur",
                    "Vous devez être connecté pour désactiver une licence.",
                    "error"
                )
                return
            
            # Désactiver la licence
            try:
                if hasattr(self.model, 'license_model') and self.model.license_model is not None:
                    success, message = self.model.license_model.deactivate_license(username)
                    
                    if success:
                        DialogUtils.show_message(
                            self.parent,
                            "Licence désactivée",
                            "Votre licence a été désactivée avec succès.",
                            "success"
                        )
                        
                        # Mettre à jour la vue
                        self._create_license_settings()
                    else:
                        DialogUtils.show_message(
                            self.parent,
                            "Erreur",
                            f"Impossible de désactiver la licence: {message}",
                            "error"
                        )
                else:
                    DialogUtils.show_message(
                        self.parent,
                        "Erreur",
                        "Le système de licence n'est pas disponible.",
                        "error"
                    )
            except Exception as e:
                logger.error(f"Erreur lors de la désactivation de la licence: {e}")
                DialogUtils.show_message(
                    self.parent,
                    "Erreur",
                    f"Une erreur s'est produite: {str(e)}",
                    "error"
                )
        
        # Demander confirmation
        DialogUtils.show_confirmation(
            self.parent,
            "Confirmer la désactivation",
            "Êtes-vous sûr de vouloir désactiver votre licence ?\n\nVous ne pourrez plus accéder aux fonctionnalités premium jusqu'à ce que vous la réactiviez.",
            on_yes=confirm_deactivation
        )

    def _apply_settings(self):
        """
        Applique les paramètres modifiés
        """
        try:
            # Récupérer les valeurs des variables
            settings = {}
            for key, var in self._variables.items():
                settings[key] = var.get()
            
            # Valider les paramètres avant de les appliquer
            valid, error_message = self._validate_settings(settings)
            if not valid:
                self.show_message("Erreur de validation", error_message, "error")
                return
            
            # Vérifier si les paramètres de sécurité ont changé
            security_changed = False
            old_auto_lock = self.model.config.get("security.auto_lock", False)
            old_lock_time = self.model.config.get("security.lock_time", 10)
            old_require_password = self.model.config.get("security.require_password", False)
            
            if (settings.get("security.auto_lock") != old_auto_lock or
                settings.get("security.lock_time") != old_lock_time or
                settings.get("security.require_password") != old_require_password):
                security_changed = True
            
            # Appliquer les paramètres
            for key, value in settings.items():
                self.model.config.set(key, value)
            
            # Sauvegarder la configuration
            self.model.config.save()
            
            # Si les paramètres de sécurité ont changé, mettre à jour le moniteur d'activité
            if security_changed:
                # Mettre à jour le moniteur d'activité si présent
                if hasattr(self.parent, 'update_activity_monitor'):
                    self.parent.update_activity_monitor()
                elif hasattr(self.parent, 'master') and hasattr(self.parent.master, 'update_activity_monitor'):
                    self.parent.master.update_activity_monitor()
            
            # Montrer un message de confirmation
            self.show_message("Paramètres mis à jour", "Les paramètres ont été appliqués avec succès.", "success")
            
            # Mettre à jour l'interface
            self.update_view()
        except Exception as e:
            logger.error(f"Erreur lors de l'application des paramètres: {e}")
            self.show_message("Erreur", f"Une erreur est survenue lors de l'application des paramètres: {e}", "error")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue de gestion des licences pour l'interface d'administration
"""

import logging
import customtkinter as ctk
import datetime
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger("VynalDocsAutomator.Admin.LicenseManagementView")

class LicenseManagementView:
    """
    Vue pour la gestion des licences utilisateurs dans l'interface d'administration
    """
    
    def __init__(self, parent, app_model):
        """
        Initialise la vue de gestion des licences
        
        Args:
            parent: Widget parent
            app_model: Modèle de l'application
        """
        self.parent = parent
        self.model = app_model
        
        # Cadre principal de la vue
        self.frame = ctk.CTkFrame(parent)
        
        # Variables pour les widgets
        self.license_table = None
        self.selected_username = None
        self.selected_license_data = None
        self.details_frame = None
        self.status_label = None
        self.search_entry = None
        self.filter_var = ctk.StringVar(value="all")
        
        # Création de l'interface
        self.create_widgets()
        
        logger.info("LicenseManagementView initialisée")
    
    def create_widgets(self):
        """
        Crée les widgets de la vue de gestion des licences
        """
        # En-tête
        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.pack(fill=ctk.X, padx=20, pady=10)
        
        # Titre de la page
        ctk.CTkLabel(
            header,
            text="Gestion des licences",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side=ctk.LEFT)
        
        # Barre d'outils supérieure
        toolbar = ctk.CTkFrame(self.frame, fg_color="transparent")
        toolbar.pack(fill=ctk.X, padx=20, pady=(0, 10))
        
        # Recherche
        search_frame = ctk.CTkFrame(toolbar, fg_color="#2a2a2a")
        search_frame.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 10))
        
        search_icon = ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=14),
            width=20
        )
        search_icon.pack(side=ctk.LEFT, padx=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Rechercher une licence...",
            border_width=0,
            fg_color="#2a2a2a"
        )
        self.search_entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=5, pady=5)
        self.search_entry.bind("<Return>", lambda e: self.refresh_licenses())
        
        clear_btn = ctk.CTkButton(
            search_frame,
            text="✖",
            width=20,
            fg_color="transparent",
            hover_color="#333333",
            command=self.clear_search
        )
        clear_btn.pack(side=ctk.RIGHT, padx=5)
        
        # Filtres
        filter_frame = ctk.CTkFrame(toolbar, fg_color="#2a2a2a")
        filter_frame.pack(side=ctk.LEFT, padx=(0, 10))
        
        ctk.CTkLabel(
            filter_frame,
            text="Statut:",
            font=ctk.CTkFont(size=12),
            width=40
        ).pack(side=ctk.LEFT, padx=5)
        
        filter_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=["all", "active", "expired", "disabled", "blocked", "trial"],
            width=120,
            command=lambda _: self.refresh_licenses()
        )
        filter_dropdown.pack(side=ctk.LEFT, padx=5, pady=5)
        
        # Boutons d'action
        add_btn = ctk.CTkButton(
            toolbar,
            text="Ajouter une licence",
            font=ctk.CTkFont(weight="bold"),
            command=self.show_add_license_dialog,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_btn.pack(side=ctk.LEFT, padx=5)
        
        generate_btn = ctk.CTkButton(
            toolbar,
            text="Générer une clé",
            command=self.show_generate_key_dialog
        )
        generate_btn.pack(side=ctk.LEFT, padx=5)
        
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="Rafraîchir",
            command=self.refresh_licenses
        )
        refresh_btn.pack(side=ctk.LEFT, padx=5)
        
        # Créer le layout principal à deux colonnes
        main_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_container.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)
        
        # Partie gauche: liste des licences
        left_frame = ctk.CTkFrame(main_container)
        left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 10))
        
        # Tableau des licences
        self.create_license_table(left_frame)
        
        # Partie droite: détails et actions
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(10, 0), pady=0)
        
        # Cadre des détails
        self.details_frame = ctk.CTkScrollableFrame(right_frame)
        self.details_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))
        
        # Message initial
        self.status_label = ctk.CTkLabel(
            self.details_frame,
            text="Sélectionnez une licence pour voir les détails",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=20)
        
        # Cadre des actions
        actions_frame = ctk.CTkFrame(right_frame)
        actions_frame.pack(fill=ctk.X, pady=(10, 0))
        
        # Créer les boutons d'action
        self.create_action_buttons(actions_frame)
    
    def create_license_table(self, parent):
        """
        Crée le tableau pour afficher les licences
        
        Args:
            parent: Widget parent
        """
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill=ctk.BOTH, expand=True)
        
        # En-tête du tableau
        header_frame = ctk.CTkFrame(table_frame, fg_color="#1a1a1a", height=40)
        header_frame.pack(fill=ctk.X, pady=0)
        header_frame.pack_propagate(False)
        
        # Colonnes
        ctk.CTkLabel(header_frame, text="Email / Utilisateur", font=ctk.CTkFont(weight="bold"), width=200).pack(side=ctk.LEFT, padx=10)
        ctk.CTkLabel(header_frame, text="Type", font=ctk.CTkFont(weight="bold"), width=100).pack(side=ctk.LEFT, padx=10)
        ctk.CTkLabel(header_frame, text="Statut", font=ctk.CTkFont(weight="bold"), width=100).pack(side=ctk.LEFT, padx=10)
        ctk.CTkLabel(header_frame, text="Expiration", font=ctk.CTkFont(weight="bold"), width=120).pack(side=ctk.LEFT, padx=10)
        
        # Conteneur pour les lignes du tableau
        self.license_table = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.license_table.pack(fill=ctk.BOTH, expand=True)
        
        # Charger les données
        self.refresh_licenses()
    
    def create_action_buttons(self, parent):
        """
        Crée les boutons d'action pour gérer les licences
        
        Args:
            parent: Widget parent
        """
        # Boutons d'action
        button_frame1 = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame1.pack(fill=ctk.X, pady=(5, 5))
        
        button_frame2 = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame2.pack(fill=ctk.X, pady=(0, 5))
        
        # Première rangée de boutons
        ctk.CTkButton(
            button_frame1,
            text="Activer / Désactiver",
            command=self.toggle_license_status,
            height=40
        ).pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        
        ctk.CTkButton(
            button_frame1,
            text="Bloquer / Débloquer",
            command=self.toggle_license_block,
            height=40
        ).pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        
        # Deuxième rangée de boutons
        ctk.CTkButton(
            button_frame2,
            text="Renouveler",
            command=self.renew_license,
            height=40,
            fg_color="#3498db",
            hover_color="#2980b9"
        ).pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        
        ctk.CTkButton(
            button_frame2,
            text="Mettre à niveau",
            command=self.upgrade_license,
            height=40,
            fg_color="#3498db",
            hover_color="#2980b9"
        ).pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        
        # Bouton de suppression en bas, séparé
        ctk.CTkButton(
            parent,
            text="Supprimer la licence",
            command=self.delete_license,
            height=30,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(fill=ctk.X, pady=(5, 0))
    
    def clear_search(self):
        """
        Efface le champ de recherche et actualise la liste
        """
        self.search_entry.delete(0, ctk.END)
        self.refresh_licenses()

    def refresh_licenses(self):
        """
        Rafraîchit la liste des licences avec filtrage
        """
        # Effacer le tableau existant
        for widget in self.license_table.winfo_children():
            widget.destroy()
        
        # Récupérer toutes les licences
        licenses = self.model.get_all_licenses()
        
        if not licenses:
            ctk.CTkLabel(
                self.license_table,
                text="Aucune licence trouvée",
                font=ctk.CTkFont(size=14),
                fg_color="transparent"
            ).pack(pady=20)
            return
        
        # Récupérer les termes de recherche et filtres
        search_term = self.search_entry.get().lower().strip()
        status_filter = self.filter_var.get()
        
        # Filtrer les licences
        filtered_licenses = {}
        for username, license_data in licenses.items():
            # Filtre par statut
            if status_filter != "all" and license_data.get("status") != status_filter:
                continue
                
            # Filtre par recherche
            if search_term and search_term not in username.lower() and search_term not in str(license_data).lower():
                continue
                
            # Ajouter à la liste filtrée
            filtered_licenses[username] = license_data
        
        if not filtered_licenses:
            ctk.CTkLabel(
                self.license_table,
                text="Aucune licence ne correspond aux critères",
                font=ctk.CTkFont(size=14),
                fg_color="transparent"
            ).pack(pady=20)
            return
        
        # Trier par date d'expiration (pour mettre en avant celles qui expirent bientôt)
        sorted_licenses = sorted(
            filtered_licenses.items(),
            key=lambda x: x[1].get("expires_at", 0) if x[1].get("status") not in ["blocked", "disabled"] else float('inf')
        )
        
        # Ajouter chaque licence au tableau
        row_index = 0
        for username, license_data in sorted_licenses:
            row_bg = "#2a2a2a" if row_index % 2 == 0 else "#222222"
            
            # Mettre en évidence les lignes nécessitant une attention
            if license_data.get("status") == "blocked":
                row_bg = "#5e2e2e"  # Rouge foncé pour les bloquées
            elif license_data.get("status") == "expired":
                row_bg = "#5e4c2e"  # Orange foncé pour les expirées
                
            row = ctk.CTkFrame(self.license_table, fg_color=row_bg, height=40)
            row.pack(fill=ctk.X, pady=1)
            row.pack_propagate(False)
            
            # Colonnes de données
            status = license_data.get("status", "unknown")
            expires_at = license_data.get("expires_at", 0)
            exp_date = datetime.datetime.fromtimestamp(expires_at).strftime('%d/%m/%Y') if expires_at else "N/A"
            
            # Couleur du statut
            status_color = {
                "active": "#4CAF50",
                "expired": "#FF5722",
                "disabled": "#9E9E9E",
                "blocked": "#F44336",
                "trial": "#2196F3"
            }.get(status, "#9E9E9E")
            
            # Texte localisé du statut
            status_text = {
                "active": "Active",
                "expired": "Expirée",
                "disabled": "Désactivée",
                "blocked": "Bloquée",
                "trial": "Essai"
            }.get(status, "Inconnu")
            
            # Éléments de la ligne
            ctk.CTkLabel(row, text=username, width=200).pack(side=ctk.LEFT, padx=10)
            ctk.CTkLabel(row, text=license_data.get("type_name", "Inconnu"), width=100).pack(side=ctk.LEFT, padx=10)
            ctk.CTkLabel(row, text=status_text, text_color=status_color, width=100).pack(side=ctk.LEFT, padx=10)
            ctk.CTkLabel(row, text=exp_date, width=120).pack(side=ctk.LEFT, padx=10)
            
            # Rendre la ligne cliquable
            row.bind("<Button-1>", lambda e, u=username: self.select_license(u))
            for widget in row.winfo_children():
                widget.bind("<Button-1>", lambda e, u=username: self.select_license(u))
            
            row_index += 1
    
    def select_license(self, username):
        """
        Sélectionne une licence et affiche ses détails
        
        Args:
            username: Nom d'utilisateur associé à la licence
        """
        self.selected_username = username
        self.show_license_details(username)
    
    def show_license_details(self, username):
        """
        Affiche les détails d'une licence
        
        Args:
            username: Nom d'utilisateur associé à la licence
        """
        # Effacer les détails existants
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Récupérer les données de la licence
        license_data = self.model.get_user_license(username)
        
        if not license_data:
            ctk.CTkLabel(
                self.details_frame,
                text=f"Aucune licence trouvée pour {username}",
                font=ctk.CTkFont(size=14)
            ).pack(pady=20)
            return
        
        # En-tête des détails
        header = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        header.pack(fill=ctk.X, pady=(10, 20))
        
        ctk.CTkLabel(
            header,
            text=f"Détails de la licence: {username}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w")
        
        # Conteneur des détails
        details_container = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        details_container.pack(fill=ctk.BOTH, expand=True, padx=20)
        
        # Informations sur la licence
        license_type = license_data.get("license_type", "unknown")
        type_name = license_data.get("type_name", "Inconnu")
        status = license_data.get("status", "unknown")
        
        # Formatage des dates
        created_at = datetime.datetime.fromtimestamp(license_data.get("created_at", 0)).strftime('%d/%m/%Y') if license_data.get("created_at") else "N/A"
        activated_at = datetime.datetime.fromtimestamp(license_data.get("activated_at", 0)).strftime('%d/%m/%Y') if license_data.get("activated_at") else "N/A"
        expires_at = datetime.datetime.fromtimestamp(license_data.get("expires_at", 0)).strftime('%d/%m/%Y') if license_data.get("expires_at") else "N/A"
        
        # Couleur du statut
        status_color = {
            "active": "#4CAF50",
            "expired": "#FF5722",
            "disabled": "#9E9E9E",
            "blocked": "#F44336",
            "trial": "#2196F3"
        }.get(status, "#9E9E9E")
        
        # Texte localisé du statut
        status_text = {
            "active": "Active",
            "expired": "Expirée",
            "disabled": "Désactivée",
            "blocked": "Bloquée",
            "trial": "Essai"
        }.get(status, "Inconnu")
        
        # Afficher les détails principaux
        row_style = {"pady": 5}
        
        # Email / Utilisateur
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Utilisateur:", width=150, anchor="w").pack(side=ctk.LEFT)
        ctk.CTkLabel(row, text=username, font=ctk.CTkFont(weight="bold")).pack(side=ctk.LEFT)
        
        # Type de licence
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Type de licence:", width=150, anchor="w").pack(side=ctk.LEFT)
        ctk.CTkLabel(row, text=type_name).pack(side=ctk.LEFT)
        
        # Statut
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Statut:", width=150, anchor="w").pack(side=ctk.LEFT)
        ctk.CTkLabel(row, text=status_text, text_color=status_color, font=ctk.CTkFont(weight="bold")).pack(side=ctk.LEFT)
        
        # Raison du blocage si applicable
        if license_data.get("blocked", False) and license_data.get("block_reason"):
            row = ctk.CTkFrame(details_container, fg_color="transparent")
            row.pack(fill=ctk.X, **row_style)
            ctk.CTkLabel(row, text="Raison du blocage:", width=150, anchor="w").pack(side=ctk.LEFT)
            ctk.CTkLabel(row, text=license_data.get("block_reason"), text_color="#F44336").pack(side=ctk.LEFT)
        
        # Clé de licence
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Clé de licence:", width=150, anchor="w").pack(side=ctk.LEFT)
        key_value = license_data.get("license_key", "N/A")
        key_label = ctk.CTkLabel(row, text=key_value)
        key_label.pack(side=ctk.LEFT)
        
        # Bouton pour copier la clé
        if key_value != "N/A":
            def copy_key_to_clipboard():
                self.parent.clipboard_clear()
                self.parent.clipboard_append(key_value)
                self.show_toast("Clé copiée dans le presse-papiers")
            
            copy_button = ctk.CTkButton(
                row, 
                text="📋", 
                width=30, 
                command=copy_key_to_clipboard,
                fg_color="transparent",
                hover_color="#2a2a2a"
            )
            copy_button.pack(side=ctk.LEFT, padx=5)
        
        # Dates
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Créée le:", width=150, anchor="w").pack(side=ctk.LEFT)
        ctk.CTkLabel(row, text=created_at).pack(side=ctk.LEFT)
        
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Activée le:", width=150, anchor="w").pack(side=ctk.LEFT)
        ctk.CTkLabel(row, text=activated_at).pack(side=ctk.LEFT)
        
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Expire le:", width=150, anchor="w").pack(side=ctk.LEFT)
        expiry_label = ctk.CTkLabel(row, text=expires_at)
        expiry_label.pack(side=ctk.LEFT)
        
        # Si la licence est sur le point d'expirer, montrer un avertissement
        if status == "active" and license_data.get("expires_at"):
            days_remaining = (license_data.get("expires_at") - int(datetime.datetime.now().timestamp())) // 86400
            if days_remaining <= 30:
                expiry_warn = ctk.CTkLabel(
                    row, 
                    text=f" (Expire dans {days_remaining} jours)", 
                    text_color="#FF9800"
                )
                expiry_warn.pack(side=ctk.LEFT, padx=5)
        
        # Activations
        row = ctk.CTkFrame(details_container, fg_color="transparent")
        row.pack(fill=ctk.X, **row_style)
        ctk.CTkLabel(row, text="Activations:", width=150, anchor="w").pack(side=ctk.LEFT)
        ctk.CTkLabel(row, text=f"{license_data.get('activations', 0)} / {license_data.get('max_activations', 1)}").pack(side=ctk.LEFT)
        
        # Fonctionnalités
        if license_data.get("features"):
            row = ctk.CTkFrame(details_container, fg_color="transparent")
            row.pack(fill=ctk.X, **row_style)
            ctk.CTkLabel(row, text="Fonctionnalités:", width=150, anchor="w").pack(side=ctk.LEFT)
            
            features_frame = ctk.CTkFrame(details_container, fg_color="#2a2a2a")
            features_frame.pack(fill=ctk.X, pady=5, padx=20)
            
            for i, feature in enumerate(license_data.get("features", [])):
                feature_row = ctk.CTkFrame(features_frame, fg_color="transparent")
                feature_row.pack(fill=ctk.X, pady=2)
                ctk.CTkLabel(feature_row, text=f"• {feature}", anchor="w").pack(side=ctk.LEFT, padx=10)
        
        # Boutons d'action
        actions_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        actions_frame.pack(fill=ctk.X, pady=15, padx=20)
        
        # Activation/Désactivation
        if status in ["disabled", "expired"]:
            ctk.CTkButton(
                actions_frame,
                text="Activer",
                fg_color="#4CAF50",
                hover_color="#2E7D32",
                command=lambda: self.toggle_license_status(username, True)
            ).pack(side=ctk.LEFT, padx=5)
        elif status == "active":
            ctk.CTkButton(
                actions_frame,
                text="Désactiver",
                fg_color="#FF5722",
                hover_color="#E64A19",
                command=lambda: self.toggle_license_status(username, False)
            ).pack(side=ctk.LEFT, padx=5)
        
        # Blocage/Déblocage
        if not license_data.get("blocked", False):
            ctk.CTkButton(
                actions_frame,
                text="Bloquer",
                fg_color="#F44336",
                hover_color="#D32F2F",
                command=lambda: self.toggle_license_block(username, True)
            ).pack(side=ctk.LEFT, padx=5)
        else:
            ctk.CTkButton(
                actions_frame,
                text="Débloquer",
                fg_color="#9E9E9E",
                hover_color="#757575",
                command=lambda: self.toggle_license_block(username, False)
            ).pack(side=ctk.LEFT, padx=5)
        
        # Renouvellement
        ctk.CTkButton(
            actions_frame,
            text="Renouveler",
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=lambda: self.renew_license(username)
        ).pack(side=ctk.LEFT, padx=5)
        
        # Supprimer
        ctk.CTkButton(
            actions_frame,
            text="Supprimer",
            fg_color="#9E9E9E",
            hover_color="#757575",
            command=lambda: self.delete_license(username)
        ).pack(side=ctk.RIGHT, padx=5)
    
    def show_add_license_dialog(self):
        """
        Affiche la boîte de dialogue pour ajouter une nouvelle licence
        """
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Ajouter une licence")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Contenu de la boîte de dialogue
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        ctk.CTkLabel(
            frame,
            text="Nouvelle licence",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20))
        
        # Formulaire
        form_frame = ctk.CTkFrame(frame, fg_color="transparent")
        form_frame.pack(fill=ctk.X)
        
        # Nom d'utilisateur
        username_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_row.pack(fill=ctk.X, pady=10)
        ctk.CTkLabel(username_row, text="Nom d'utilisateur:", width=150, anchor="w").pack(side=ctk.LEFT)
        username_var = ctk.StringVar()
        username_entry = ctk.CTkEntry(username_row, textvariable=username_var, width=250)
        username_entry.pack(side=ctk.LEFT)
        
        # Type de licence
        type_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_row.pack(fill=ctk.X, pady=10)
        ctk.CTkLabel(type_row, text="Type de licence:", width=150, anchor="w").pack(side=ctk.LEFT)
        type_var = ctk.StringVar(value="basic")
        type_frame = ctk.CTkFrame(type_row, fg_color="transparent")
        type_frame.pack(side=ctk.LEFT)
        
        license_types = [
            ("Basique", "basic"),
            ("Professionnel", "pro"),
            ("Entreprise", "enterprise"),
            ("Essai", "trial")
        ]
        
        for i, (text, value) in enumerate(license_types):
            ctk.CTkRadioButton(
                type_frame,
                text=text,
                value=value,
                variable=type_var
            ).pack(anchor="w", pady=5)
        
        # Durée
        duration_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        duration_row.pack(fill=ctk.X, pady=10)
        ctk.CTkLabel(duration_row, text="Durée (jours):", width=150, anchor="w").pack(side=ctk.LEFT)
        duration_var = ctk.StringVar(value="365")
        duration_entry = ctk.CTkEntry(duration_row, textvariable=duration_var, width=100)
        duration_entry.pack(side=ctk.LEFT, padx=10)
        
        # Boutons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=20)
        
        def cancel_dialog():
            dialog.destroy()
        
        def create_license():
            username = username_var.get().strip()
            license_type = type_var.get()
            
            try:
                duration = int(duration_var.get())
                if duration <= 0:
                    raise ValueError("La durée doit être un nombre positif")
            except ValueError:
                # Afficher un message d'erreur
                self.show_error_message(dialog, "Durée invalide", "Veuillez entrer un nombre entier positif pour la durée.")
                return
            
            if not username:
                self.show_error_message(dialog, "Nom d'utilisateur manquant", "Veuillez entrer un nom d'utilisateur.")
                return
            
            # Créer la licence
            license_data = self.model.create_license(username, license_type, duration)
            
            if license_data:
                dialog.destroy()
                self.refresh_licenses()
                self.select_license(username)
            else:
                self.show_error_message(dialog, "Erreur", "Impossible de créer la licence.")
        
        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            command=cancel_dialog,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Créer",
            command=create_license,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=100
        ).pack(side=ctk.RIGHT, padx=5)
    
    def show_error_message(self, parent, title, message):
        """
        Affiche un message d'erreur
        
        Args:
            parent: Widget parent
            title: Titre du message
            message: Contenu du message
        """
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e74c3c"
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            frame,
            text=message,
            wraplength=360
        ).pack(pady=10)
        
        ctk.CTkButton(
            frame,
            text="OK",
            command=dialog.destroy,
            width=100,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(pady=10)
    
    def toggle_license_status(self, username, activate):
        """
        Active ou désactive la licence sélectionnée
        """
        if not username:
            return
        
        license_data = self.model.get_user_license(username)
        if not license_data:
            return
        
        if activate:
            # Activer la licence
            success, message = self.model.activate_license(username, license_data.get("license_key", ""))
        else:
            # Désactiver la licence
            success, message = self.model.deactivate_license(username)
        
        if success:
            self.refresh_licenses()
            self.show_license_details(username)
    
    def toggle_license_block(self, username, block):
        """
        Bloque ou débloque la licence sélectionnée
        """
        if not username:
            return
        
        license_data = self.model.get_user_license(username)
        if not license_data:
            return
        
        if block:
            # Demander la raison du blocage
            self.show_block_dialog()
            return  # Sortir de la fonction car show_block_dialog gère déjà le rafraîchissement
        else:
            # Débloquer la licence
            success, message = self.model.unblock_user_license(username)
            
            if success:
                self.refresh_licenses()
                self.show_license_details(username)
    
    def show_block_dialog(self):
        """
        Affiche la boîte de dialogue pour bloquer une licence
        """
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Bloquer la licence")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"Bloquer la licence de {self.selected_username}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            frame,
            text="Raison du blocage:"
        ).pack(anchor="w")
        
        reason_var = ctk.StringVar(value="Violation des conditions d'utilisation")
        reason_entry = ctk.CTkTextbox(frame, height=80)
        reason_entry.pack(fill=ctk.X, pady=10)
        reason_entry.insert("1.0", "Violation des conditions d'utilisation")
        
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=10)
        
        def cancel_dialog():
            dialog.destroy()
        
        def block_license():
            reason = reason_entry.get("1.0", "end-1c").strip()
            if not reason:
                reason = "Bloqué par l'administrateur"
            
            success, message = self.model.block_user_license(self.selected_username, reason)
            
            if success:
                dialog.destroy()
                self.refresh_licenses()
                self.show_license_details(self.selected_username)
            else:
                self.show_error_message(dialog, "Erreur", f"Impossible de bloquer la licence: {message}")
        
        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            command=cancel_dialog,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Bloquer",
            command=block_license,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100
        ).pack(side=ctk.RIGHT, padx=5)
    
    def renew_license(self, username):
        """
        Renouvelle la licence sélectionnée
        """
        if not username:
            return
        
        self.show_renew_dialog()
    
    def show_renew_dialog(self):
        """
        Affiche la boîte de dialogue pour renouveler une licence
        """
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Renouveler la licence")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"Renouveler la licence de {self.selected_username}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))
        
        duration_frame = ctk.CTkFrame(frame, fg_color="transparent")
        duration_frame.pack(fill=ctk.X, pady=10)
        
        ctk.CTkLabel(
            duration_frame,
            text="Durée (jours):",
            width=100,
            anchor="w"
        ).pack(side=ctk.LEFT)
        
        duration_var = ctk.StringVar(value="365")
        duration_entry = ctk.CTkEntry(duration_frame, textvariable=duration_var, width=100)
        duration_entry.pack(side=ctk.LEFT, padx=10)
        
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=20)
        
        def cancel_dialog():
            dialog.destroy()
        
        def renew_license_action():
            try:
                duration = int(duration_var.get())
                if duration <= 0:
                    raise ValueError("La durée doit être un nombre positif")
            except ValueError:
                self.show_error_message(dialog, "Durée invalide", "Veuillez entrer un nombre entier positif pour la durée.")
                return
            
            success, message = self.model.renew_license(self.selected_username, duration)
            
            if success:
                dialog.destroy()
                self.refresh_licenses()
                self.show_license_details(self.selected_username)
            else:
                self.show_error_message(dialog, "Erreur", f"Impossible de renouveler la licence: {message}")
        
        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            command=cancel_dialog,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Renouveler",
            command=renew_license_action,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=100
        ).pack(side=ctk.RIGHT, padx=5)
    
    def upgrade_license(self):
        """
        Met à niveau la licence sélectionnée
        """
        if not self.selected_username:
            return
        
        self.show_upgrade_dialog()
    
    def show_upgrade_dialog(self):
        """
        Affiche la boîte de dialogue pour mettre à niveau une licence
        """
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Mettre à niveau la licence")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"Mettre à niveau la licence de {self.selected_username}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))
        
        # Type de licence
        ctk.CTkLabel(
            frame,
            text="Sélectionnez le nouveau type de licence:",
            anchor="w"
        ).pack(anchor="w")
        
        type_var = ctk.StringVar(value="basic")
        type_frame = ctk.CTkFrame(frame, fg_color="transparent")
        type_frame.pack(fill=ctk.X, pady=10)
        
        license_types = [
            ("Basique", "basic"),
            ("Professionnel", "pro"),
            ("Entreprise", "enterprise")
        ]
        
        for i, (text, value) in enumerate(license_types):
            ctk.CTkRadioButton(
                type_frame,
                text=text,
                value=value,
                variable=type_var
            ).pack(anchor="w", pady=5)
        
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=20)
        
        def cancel_dialog():
            dialog.destroy()
        
        def upgrade_license_action():
            new_type = type_var.get()
            
            success, message = self.model.upgrade_license(self.selected_username, new_type)
            
            if success:
                dialog.destroy()
                self.refresh_licenses()
                self.show_license_details(self.selected_username)
            else:
                self.show_error_message(dialog, "Erreur", f"Impossible de mettre à niveau la licence: {message}")
        
        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            command=cancel_dialog,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Mettre à niveau",
            command=upgrade_license_action,
            fg_color="#3498db",
            hover_color="#2980b9",
            width=120
        ).pack(side=ctk.RIGHT, padx=5)
    
    def show_generate_key_dialog(self):
        """
        Affiche la boîte de dialogue pour générer une clé de licence sans créer immédiatement la licence
        """
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Générer une clé de licence")
        dialog.geometry("600x600")  # Augmenté la hauteur pour afficher plus d'informations
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Contenu de la boîte de dialogue
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        ctk.CTkLabel(
            frame,
            text="Générer une clé de licence",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(0, 20))
        
        # Formulaire
        form_frame = ctk.CTkFrame(frame, fg_color="transparent")
        form_frame.pack(fill=ctk.X)
        
        # Email de l'utilisateur
        email_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        email_row.pack(fill=ctk.X, pady=10)
        ctk.CTkLabel(email_row, text="Email de l'utilisateur:", width=150, anchor="w").pack(side=ctk.LEFT)
        email_var = ctk.StringVar()
        email_entry = ctk.CTkEntry(email_row, textvariable=email_var, width=350)
        email_entry.pack(side=ctk.LEFT)
        
        # Type de licence
        type_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_row.pack(fill=ctk.X, pady=10)
        ctk.CTkLabel(type_row, text="Type de licence:", width=150, anchor="w").pack(side=ctk.LEFT)
        type_var = ctk.StringVar(value="standard")
        
        type_frame = ctk.CTkFrame(type_row, fg_color="transparent")
        type_frame.pack(side=ctk.LEFT)
        
        license_types = [
            ("Standard", "standard"),
            ("Premium", "premium"),
            ("Professionnel", "pro"),
            ("Entreprise", "enterprise")
        ]
        
        for i, (text, value) in enumerate(license_types):
            ctk.CTkRadioButton(
                type_frame,
                text=text,
                value=value,
                variable=type_var
            ).pack(anchor="w", pady=5)
        
        # Durée
        duration_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        duration_row.pack(fill=ctk.X, pady=10)
        ctk.CTkLabel(duration_row, text="Durée (jours):", width=150, anchor="w").pack(side=ctk.LEFT)
        duration_var = ctk.StringVar(value="365")
        duration_entry = ctk.CTkEntry(duration_row, textvariable=duration_var, width=100)
        duration_entry.pack(side=ctk.LEFT, padx=10)
        
        # Zone d'affichage de la clé générée
        result_frame = ctk.CTkFrame(frame)
        result_frame.pack(fill=ctk.X, pady=20)
        
        ctk.CTkLabel(
            result_frame,
            text="Clé de licence générée:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))
        
        key_display = ctk.CTkTextbox(result_frame, height=60, wrap="word")
        key_display.pack(fill=ctk.X, padx=10, pady=5)
        key_display.configure(state="disabled")
        
        # Détails de la licence
        license_info_frame = ctk.CTkFrame(result_frame, fg_color="#2a2a2a")
        license_info_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        # Étiquettes pour afficher les détails décodés de la licence
        license_email = ctk.CTkLabel(license_info_frame, text="Email: -", anchor="w")
        license_email.pack(anchor="w", padx=10, pady=2)
        
        license_type_display = ctk.CTkLabel(license_info_frame, text="Type: -", anchor="w")
        license_type_display.pack(anchor="w", padx=10, pady=2)
        
        license_created = ctk.CTkLabel(license_info_frame, text="Date de création: -", anchor="w")
        license_created.pack(anchor="w", padx=10, pady=2)
        
        license_expiry = ctk.CTkLabel(license_info_frame, text="Date d'expiration: -", anchor="w")
        license_expiry.pack(anchor="w", padx=10, pady=2)
        
        info_label = ctk.CTkLabel(
            result_frame,
            text="Cette clé n'est pas encore associée à l'utilisateur. Utilisez le bouton 'Associer à un utilisateur' pour l'activer.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=500
        )
        info_label.pack(pady=5)
        
        # Création des variables pour stocker les informations décodées de la licence
        license_data = {"key": "", "email": "", "created_at": 0, "expires_at": 0, "type": ""}
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=10)
        
        def copy_to_clipboard():
            """Copie la clé générée dans le presse-papier"""
            dialog.clipboard_clear()
            dialog.clipboard_append(key_display.get("1.0", "end-1c"))
            
            info_label.configure(text="✓ Clé copiée dans le presse-papier!", text_color="#4CAF50")
            dialog.after(2000, lambda: info_label.configure(
                text="Cette clé n'est pas encore associée à l'utilisateur. Utilisez le bouton 'Associer à un utilisateur' pour l'activer.",
                text_color="gray"
            ))
        
        def associate_to_user():
            """Ouvre une boîte de dialogue pour associer la clé à un utilisateur"""
            if not license_data["key"]:
                info_label.configure(text="⚠️ Veuillez d'abord générer une clé!", text_color="#FF5722")
                return
            
            # Récupérer l'email de la licence
            email = license_data["email"]
            key = license_data["key"]
            
            # Créer une boîte de dialogue d'association
            assoc_dialog = ctk.CTkToplevel(dialog)
            assoc_dialog.title("Associer la licence à un utilisateur")
            assoc_dialog.geometry("450x300")
            assoc_dialog.resizable(False, False)
            assoc_dialog.grab_set()
            
            # Centrer la boîte de dialogue
            assoc_dialog.update_idletasks()
            width = assoc_dialog.winfo_width()
            height = assoc_dialog.winfo_height()
            x = (assoc_dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (assoc_dialog.winfo_screenheight() // 2) - (height // 2)
            assoc_dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Contenu
            assoc_frame = ctk.CTkFrame(assoc_dialog, fg_color="transparent")
            assoc_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                assoc_frame,
                text="Associer la licence à un utilisateur",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(0, 20))
            
            # Afficher l'email de la licence
            email_frame = ctk.CTkFrame(assoc_frame, fg_color="transparent")
            email_frame.pack(fill=ctk.X, pady=5)
            ctk.CTkLabel(email_frame, text="Email de la licence:", width=120, anchor="w").pack(side=ctk.LEFT)
            ctk.CTkLabel(email_frame, text=email, font=ctk.CTkFont(weight="bold")).pack(side=ctk.LEFT)
            
            # Champ pour entrer le nom d'utilisateur
            username_frame = ctk.CTkFrame(assoc_frame, fg_color="transparent")
            username_frame.pack(fill=ctk.X, pady=10)
            ctk.CTkLabel(username_frame, text="Nom d'utilisateur:", width=120, anchor="w").pack(side=ctk.LEFT)
            username_var = ctk.StringVar(value=email)  # Par défaut, utilisez l'email comme nom d'utilisateur
            username_entry = ctk.CTkEntry(username_frame, textvariable=username_var, width=250)
            username_entry.pack(side=ctk.LEFT)
            
            # Message d'info
            ctk.CTkLabel(
                assoc_frame,
                text="Note: Le nom d'utilisateur sera utilisé comme identifiant pour cette licence dans le système.",
                font=ctk.CTkFont(size=12),
                text_color="gray",
                wraplength=400
            ).pack(pady=10)
            
            # Boutons
            btn_frame = ctk.CTkFrame(assoc_frame, fg_color="transparent")
            btn_frame.pack(fill=ctk.X, pady=10)
            
            result_label = ctk.CTkLabel(
                assoc_frame,
                text="",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            result_label.pack(pady=10)
            
            def do_associate():
                username = username_var.get().strip()
                if not username:
                    result_label.configure(text="⚠️ Veuillez entrer un nom d'utilisateur", text_color="#FF5722")
                    return
                
                try:
                    # Créer une licence pour l'utilisateur si elle n'existe pas déjà
                    # Nous extrayons d'abord le type et la durée de la licence depuis les données décodées
                    license_type = license_data["type"] or "standard"  # Utiliser le type décodé ou "standard" par défaut
                    
                    # Calculer la durée restante à partir de la date d'expiration
                    current_time = int(datetime.datetime.now().timestamp())
                    expires_at = license_data["expires_at"]
                    remaining_days = max(1, int((expires_at - current_time) / 86400))  # Convertir en jours, minimum 1 jour
                    
                    # Créer la licence d'abord, en utilisant la clé que nous avons déjà générée
                    license_data_obj = self.model.create_license(
                        username=username,
                        license_type=license_type,
                        duration_days=remaining_days,
                        key=key  # Utiliser la clé qui a été générée
                    )
                    
                    if not license_data_obj:
                        result_label.configure(text="⚠️ Erreur lors de la création de la licence", text_color="#FF5722")
                        return
                    
                    # Maintenant activer la licence
                    success, message = self.model.activate_license(username, key)
                    
                    if success:
                        result_label.configure(text=f"✓ Licence créée et activée avec succès pour {username}", text_color="#4CAF50")
                        # Rafraîchir la liste des licences
                        self.refresh_licenses()
                        
                        # Fermer la boîte de dialogue après 1.5 secondes
                        assoc_dialog.after(1500, assoc_dialog.destroy)
                    else:
                        result_label.configure(text=f"⚠️ Licence créée mais erreur lors de l'activation: {message}", text_color="#FF9800")
                except Exception as e:
                    logger.error(f"Erreur lors de l'association de la licence: {e}")
                    result_label.configure(text=f"⚠️ Erreur: {str(e)}", text_color="#FF5722")
            
            ctk.CTkButton(
                btn_frame,
                text="Annuler",
                command=assoc_dialog.destroy,
                width=100
            ).pack(side=ctk.LEFT, padx=5)
            
            ctk.CTkButton(
                btn_frame,
                text="Associer & Activer",
                command=do_associate,
                fg_color="#2ecc71",
                hover_color="#27ae60",
                width=150
            ).pack(side=ctk.RIGHT, padx=5)
        
        def show_license_details():
            """Affiche les détails décodés de la licence dans l'interface"""
            if not license_data["key"]:
                return
                
            try:
                license_email.configure(text=f"Email: {license_data['email']}")
                license_type_display.configure(text=f"Type: {license_data['type']}")
                
                created_date = datetime.datetime.fromtimestamp(license_data['created_at']).strftime('%d/%m/%Y')
                license_created.configure(text=f"Date de création: {created_date}")
                
                expiry_date = datetime.datetime.fromtimestamp(license_data['expires_at']).strftime('%d/%m/%Y')
                license_expiry.configure(text=f"Date d'expiration: {expiry_date}")
                
                license_info_frame.pack(fill=ctk.X, padx=10, pady=10)
            except Exception as e:
                logger.error(f"Erreur lors de l'affichage des détails de licence: {e}")
                license_info_frame.pack_forget()
        
        def decode_license_data(license_key):
            """Décode les données de la licence à partir de la clé"""
            try:
                import base64
                import json
                
                # Décoder la clé Base64 en JSON
                decoded = base64.b64decode(license_key.encode('utf-8')).decode('utf-8')
                license_json = json.loads(decoded)
                
                # Extraire les informations
                if "data" in license_json:
                    data = license_json["data"]
                    license_data["email"] = data.get("email", "")
                    license_data["created_at"] = data.get("created_at", 0)
                    license_data["expires_at"] = data.get("expires_at", 0)
                    license_data["type"] = data.get("license_type", "")
                
                # Mettre à jour l'interface avec les détails décodés
                show_license_details()
                
                return True
            except Exception as e:
                logger.error(f"Erreur lors du décodage de la clé de licence: {e}")
                return False
        
        def generate_key():
            """Génère une clé de licence basée sur les paramètres saisis"""
            email = email_var.get().strip()
            
            if not email:
                info_label.configure(text="⚠️ Veuillez saisir un email valide!", text_color="#FF5722")
                return
                
            try:
                duration = int(duration_var.get())
                if duration <= 0:
                    raise ValueError("La durée doit être positive")
            except ValueError:
                info_label.configure(text="⚠️ Durée invalide! Entrez un nombre positif.", text_color="#FF5722")
                return
            
            try:
                # Utiliser la méthode du modèle pour générer la clé
                license_key = self.model.generate_license_key(
                    email=email, 
                    duration_days=duration, 
                    license_type=type_var.get()
                )
                
                if license_key:
                    # Stocker la clé dans les données de licence
                    license_data["key"] = license_key
                    
                    # Afficher la clé générée
                    key_display.configure(state="normal")
                    key_display.delete("1.0", "end")
                    key_display.insert("1.0", license_key)
                    
                    # Activer les boutons maintenant que nous avons une clé
                    copy_btn.configure(state="normal")
                    associate_btn.configure(state="normal")
                    
                    key_display.configure(state="disabled")
                    
                    # Décoder et afficher les informations de la licence
                    if decode_license_data(license_key):
                        info_label.configure(text="✓ Clé générée avec succès! Vous pouvez maintenant l'associer à un utilisateur.", text_color="#4CAF50")
                    else:
                        info_label.configure(text="✓ Clé générée, mais impossible de décoder les détails.", text_color="#FF9800")
                else:
                    info_label.configure(text="⚠️ Erreur lors de la génération de la clé", text_color="#FF5722")
            except Exception as e:
                logger.error(f"Erreur lors de la génération de la clé: {e}")
                info_label.configure(text=f"⚠️ Erreur: {str(e)}", text_color="#FF5722")
        
        copy_btn = ctk.CTkButton(
            buttons_frame,
            text="Copier la clé",
            command=copy_to_clipboard,
            width=120,
            state="disabled"  # Désactivé jusqu'à ce qu'une clé soit générée
        )
        copy_btn.pack(side=ctk.LEFT, padx=5)
        
        associate_btn = ctk.CTkButton(
            buttons_frame,
            text="Associer à un utilisateur",
            command=associate_to_user,
            width=160,
            state="disabled"  # Désactivé jusqu'à ce qu'une clé soit générée
        )
        associate_btn.pack(side=ctk.LEFT, padx=5)
        
        # Activer les boutons lorsqu'une clé est générée
        def check_key_display(*args):
            has_key = key_display.get("1.0", "end-1c").strip()
            if has_key:
                copy_btn.configure(state="normal")
                associate_btn.configure(state="normal")
            else:
                copy_btn.configure(state="disabled")
                associate_btn.configure(state="disabled")
                
        # Observer les changements dans le contenu de key_display
        key_display.bind("<KeyRelease>", check_key_display)
        
        generate_btn = ctk.CTkButton(
            buttons_frame,
            text="Générer une clé",
            command=generate_key,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=150
        )
        generate_btn.pack(side=ctk.RIGHT, padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Fermer",
            command=dialog.destroy,
            width=100
        ).pack(side=ctk.RIGHT, padx=5)
    
    def delete_license(self, username):
        """
        Supprime la licence sélectionnée après confirmation
        """
        if not username:
            return
            
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Confirmer la suppression")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="⚠️ Supprimer la licence",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF5722"
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            frame,
            text=f"Êtes-vous sûr de vouloir supprimer définitivement\nla licence de {username} ?",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            frame,
            text="Cette action ne peut pas être annulée.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=10)
        
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=10)
        
        def confirm_delete():
            if self.model.delete_user_license(username):
                dialog.destroy()
                self.selected_username = None
                self.selected_license_data = None
                self.refresh_licenses()
                
                # Réinitialiser le panneau de détails
                for widget in self.details_frame.winfo_children():
                    widget.destroy()
                    
                self.status_label = ctk.CTkLabel(
                    self.details_frame,
                    text="Sélectionnez une licence pour voir les détails",
                    font=ctk.CTkFont(size=14)
                )
                self.status_label.pack(pady=20)
            else:
                self.show_error_message(dialog, "Erreur", "Impossible de supprimer la licence.")
        
        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            command=dialog.destroy,
            width=120
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Supprimer",
            command=confirm_delete,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=120
        ).pack(side=ctk.RIGHT, padx=5)
    
    def show(self):
        """Affiche la vue"""
        self.frame.pack(fill=ctk.BOTH, expand=True)
    
    def hide(self):
        """Cache la vue"""
        self.frame.pack_forget()
    
    def show_toast(self, message, message_type="success", duration=2000):
        """
        Affiche un message toast temporaire
        
        Args:
            message: Message à afficher
            message_type: Type de message (success, warning, error, info)
            duration: Durée d'affichage en millisecondes
        """
        # Définir les couleurs en fonction du type de message
        if message_type == "error":
            bg_color = "#F44336"
            fg_color = "white"
        elif message_type == "warning":
            bg_color = "#FF9800"
            fg_color = "black"
        elif message_type == "info":
            bg_color = "#2196F3"
            fg_color = "white"
        else:  # success
            bg_color = "#4CAF50"
            fg_color = "white"
        
        # Créer la fenêtre toast
        toast_window = ctk.CTkToplevel(self.parent)
        toast_window.overrideredirect(True)
        toast_window.attributes("-topmost", True)
        
        # Créer le cadre du message
        frame = ctk.CTkFrame(toast_window, fg_color=bg_color)
        frame.pack(fill=ctk.BOTH, expand=True)
        
        # Ajouter le message
        label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=fg_color
        )
        label.pack(padx=20, pady=10)
        
        # Positionner la fenêtre
        toast_window.update_idletasks()
        width = toast_window.winfo_width()
        height = toast_window.winfo_height()
        
        # Centrer en bas de la fenêtre parent
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + parent_height - height - 20
        
        toast_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Fermer automatiquement après duration ms
        toast_window.after(duration, toast_window.destroy) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue de gestion des permissions pour l'interface d'administration
"""

import logging
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional

logger = logging.getLogger("VynalDocsAutomator.Admin.PermissionsView")

class PermissionsView:
    """
    Vue pour la gestion des permissions des utilisateurs
    """
    
    def __init__(self, parent, app_model):
        """
        Initialise la vue de gestion des permissions
        
        Args:
            parent: Widget parent
            app_model: Modèle de l'application
        """
        self.parent = parent
        self.model = app_model
        
        # Cadre principal de la vue
        self.frame = ctk.CTkFrame(parent)
        
        # Définition des rôles et permissions disponibles
        # Utiliser les méthodes du modèle si elles existent
        if hasattr(self.model, 'get_available_roles'):
            roles_list = self.model.get_available_roles()
            self.available_roles = [role["id"] for role in roles_list]
        else:
            # Valeurs par défaut
            self.available_roles = [
                "admin",      # Administrateur système avec accès complet
                "manager",    # Gestionnaire avec accès étendu
                "user",       # Utilisateur standard
                "viewer",     # Utilisateur en lecture seule
                "custom"      # Rôle personnalisé
            ]
        
        if hasattr(self.model, 'get_available_permissions'):
            self.available_permissions = self.model.get_available_permissions()
        else:
            # Valeurs par défaut
            self.available_permissions = {
                "admin_access": "Accès à l'interface d'administration",
                "manage_users": "Gérer les utilisateurs",
                "manage_templates": "Gérer les modèles de document",
                "edit_documents": "Modifier les documents",
                "view_documents": "Voir les documents",
                "export_data": "Exporter les données",
                "view_logs": "Consulter les journaux",
                "manage_settings": "Gérer les paramètres",
                "manage_licenses": "Gérer les licences"
            }
        
        # Définition des permissions par défaut pour chaque rôle
        self.role_permissions = {}
        
        if hasattr(self.model, 'get_role_permissions'):
            # Récupérer les permissions pour chaque rôle
            for role in self.available_roles:
                self.role_permissions[role] = self.model.get_role_permissions(role)
        else:
            # Valeurs par défaut
            self.role_permissions = {
                "admin": list(self.available_permissions.keys()),
                "manager": ["manage_users", "manage_templates", "edit_documents", "view_documents", "export_data"],
                "user": ["edit_documents", "view_documents", "export_data"],
                "viewer": ["view_documents"],
                "custom": []
            }
        
        # Variables pour les widgets
        self.users_table = None
        self.selected_user_id = None
        self.role_var = ctk.StringVar(value="user")
        self.permissions_vars = {}
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        # Création de l'interface
        self.create_widgets()
        
        logger.info("PermissionsView initialisée")
    
    def create_widgets(self):
        """
        Crée les widgets de la vue de gestion des permissions
        """
        # Cadre pour le titre de la page
        self.header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.header_frame.pack(fill=ctk.X, pady=(0, 10))
        
        # Titre principal
        ctk.CTkLabel(
            self.header_frame,
            text="Gestion des permissions",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", padx=20, pady=10)
        
        # Barre de recherche
        search_frame = ctk.CTkFrame(self.header_frame)
        search_frame.pack(side=ctk.RIGHT, padx=20)
        
        ctk.CTkLabel(
            search_frame,
            text="Rechercher:",
            font=ctk.CTkFont(size=12)
        ).pack(side=ctk.LEFT, padx=5)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            width=200,
            textvariable=self.search_var
        )
        search_entry.pack(side=ctk.LEFT, padx=5)
        
        # Conteneur principal à deux colonnes
        main_container = ctk.CTkFrame(self.frame)
        main_container.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Colonne gauche : liste des utilisateurs
        users_frame = ctk.CTkFrame(main_container)
        users_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=(0, 10), pady=0, expand=False)
        
        # Étiquette pour la liste des utilisateurs
        ctk.CTkLabel(
            users_frame,
            text="Utilisateurs",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        # Tableau des utilisateurs
        table_frame = ctk.CTkFrame(users_frame)
        table_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=5)
        
        # Créer un Treeview pour afficher les utilisateurs
        self.users_table = ttk.Treeview(
            table_frame,
            columns=("name", "email", "role"),
            show="headings",
            selectmode="browse",
            height=20
        )
        
        # Définir les en-têtes
        self.users_table.heading("name", text="Nom")
        self.users_table.heading("email", text="Email")
        self.users_table.heading("role", text="Rôle")
        
        # Définir les largeurs de colonnes
        self.users_table.column("name", width=150)
        self.users_table.column("email", width=200)
        self.users_table.column("role", width=100)
        
        # Ajouter une scrollbar
        users_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.users_table.yview
        )
        self.users_table.configure(yscrollcommand=users_scrollbar.set)
        
        # Positionner la table et la scrollbar
        self.users_table.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        users_scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        
        # Lier la sélection d'un utilisateur
        self.users_table.bind("<<TreeviewSelect>>", self._on_user_select)
        
        # Colonne droite : détails des permissions
        details_frame = ctk.CTkFrame(main_container)
        details_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=0, pady=0)
        
        # Créer un conteneur scrollable pour les permissions
        self.details_scroll = ctk.CTkScrollableFrame(details_frame)
        self.details_scroll.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre de la section des détails
        self.details_title = ctk.CTkLabel(
            self.details_scroll,
            text="Permissions de l'utilisateur",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.details_title.pack(anchor="w", padx=10, pady=5)
        
        # Section du rôle
        role_frame = ctk.CTkFrame(self.details_scroll)
        role_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            role_frame,
            text="Rôle:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            width=100
        ).pack(side=ctk.LEFT, padx=10)
        
        role_dropdown = ctk.CTkOptionMenu(
            role_frame,
            values=self.available_roles,
            variable=self.role_var,
            width=150,
            command=self._on_role_changed
        )
        role_dropdown.pack(side=ctk.LEFT, padx=10)
        
        # Section des permissions
        permissions_frame = ctk.CTkFrame(self.details_scroll)
        permissions_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            permissions_frame,
            text="Permissions:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=10, pady=5)
        
        # Créer les cases à cocher pour chaque permission
        self.permission_checkboxes = {}
        for perm_id, perm_desc in self.available_permissions.items():
            var = ctk.BooleanVar()
            self.permissions_vars[perm_id] = var
            
            checkbox = ctk.CTkCheckBox(
                permissions_frame,
                text=perm_desc,
                variable=var,
                command=self._on_permission_change
            )
            checkbox.pack(anchor="w", padx=20, pady=3)
            self.permission_checkboxes[perm_id] = checkbox
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Enregistrer les modifications",
            command=self._save_user_permissions,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        save_button.pack(side=ctk.RIGHT, padx=5)
        
        reset_button = ctk.CTkButton(
            buttons_frame,
            text="Réinitialiser",
            command=self._reset_form
        )
        reset_button.pack(side=ctk.RIGHT, padx=5)
        
        # Remplir la table des utilisateurs
        self._populate_users_table()
    
    def _populate_users_table(self, search_term=None):
        """
        Remplit le tableau des utilisateurs
        
        Args:
            search_term (str, optional): Terme de recherche pour filtrer les utilisateurs
        """
        # Effacer la table
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        
        # Récupérer les utilisateurs depuis le modèle
        users = self.model.get_users() if hasattr(self.model, 'get_users') else []
        
        # Filtrer si un terme de recherche est spécifié
        if search_term:
            search_term = search_term.lower()
            filtered_users = []
            for user in users:
                if (search_term in user.get("email", "").lower() or
                    search_term in user.get("first_name", "").lower() or
                    search_term in user.get("last_name", "").lower()):
                    filtered_users.append(user)
            users = filtered_users
        
        # Ajouter les utilisateurs à la table
        for user in users:
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            self.users_table.insert(
                "",
                "end",
                values=(full_name, user.get("email", ""), user.get("role", "user")),
                tags=(user.get("id", ""))
            )
    
    def _on_search_changed(self, *args):
        """Callback lorsque le terme de recherche change"""
        self._populate_users_table(self.search_var.get())
    
    def _on_user_select(self, event):
        """
        Callback lorsqu'un utilisateur est sélectionné dans la table
        
        Args:
            event: Événement de sélection
        """
        selection = self.users_table.selection()
        if not selection:
            return
        
        item = selection[0]
        user_tag = self.users_table.item(item, "tags")[0]
        self.selected_user_id = user_tag
        
        # Récupérer les informations de l'utilisateur
        user = self.model.get_user_by_id(self.selected_user_id) if hasattr(self.model, 'get_user_by_id') else None
        
        if user:
            # Mettre à jour le titre
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            self.details_title.configure(text=f"Permissions de {full_name}")
            
            # Mettre à jour le rôle
            role = user.get("role", "user")
            self.role_var.set(role)
            
            # Mettre à jour les permissions
            self._on_role_changed(None)
    
    def _on_role_changed(self, event=None):
        """
        Gère le changement de rôle pour un utilisateur et met à jour les cases à cocher des permissions
        """
        selected_role = self.role_var.get()
        
        # Désactiver toutes les cases à cocher d'abord
        for perm_id, checkbox in self.permission_checkboxes.items():
            checkbox.deselect()
            
            # Activer uniquement pour le rôle personnalisé
            if selected_role == "custom":
                checkbox.configure(state="normal")
            else:
                checkbox.configure(state="disabled")
        
        # Si ce n'est pas un rôle personnalisé, remplir avec les permissions par défaut du rôle
        if selected_role != "custom":
            # Récupérer les permissions pour ce rôle
            role_perms = self.role_permissions.get(selected_role, [])
            
            # Cocher les cases correspondantes
            for perm_id in role_perms:
                if perm_id in self.permission_checkboxes:
                    self.permission_checkboxes[perm_id].select()
    
    def _on_permission_change(self):
        """Callback lorsqu'une permission est modifiée"""
        # Si des permissions personnalisées sont sélectionnées, passer au rôle personnalisé
        self.role_var.set("custom")
    
    def _save_user_permissions(self):
        """
        Enregistre les permissions de l'utilisateur sélectionné
        """
        # Vérifier qu'un utilisateur est sélectionné
        if not self.selected_user_id:
            messagebox.showerror("Erreur", "Aucun utilisateur sélectionné.")
            return
        
        # Récupérer le rôle sélectionné
        role = self.role_var.get()
        
        # Récupérer les permissions sélectionnées (uniquement pertinent pour le rôle personnalisé)
        selected_permissions = []
        if role == "custom":
            for perm_id, checkbox in self.permission_checkboxes.items():
                if checkbox.get() == 1:  # Vérifie si la case est cochée
                    selected_permissions.append(perm_id)
        else:
            # Pour les rôles prédéfinis, utiliser les permissions du rôle
            selected_permissions = self.role_permissions.get(role, [])
        
        # Enregistrer les modifications
        try:
            # Si la méthode update_user_role existe dans le modèle, l'utiliser
            if hasattr(self.model, 'update_user_role'):
                success = self.model.update_user_role(self.selected_user_id, role, selected_permissions)
                if success:
                    messagebox.showinfo("Succès", "Les permissions de l'utilisateur ont été mises à jour.")
                    self._populate_users_table()  # Actualiser la liste
                else:
                    messagebox.showerror("Erreur", "Une erreur est survenue lors de la mise à jour des permissions.")
            else:
                # Méthode alternative avec update_user
                user = self.model.get_user_by_id(self.selected_user_id)
                if user:
                    user["role"] = role
                    user["permissions"] = selected_permissions
                    success = self.model.update_user(user)
                    if success:
                        messagebox.showinfo("Succès", "Les permissions de l'utilisateur ont été mises à jour.")
                        self._populate_users_table()  # Actualiser la liste
                    else:
                        messagebox.showerror("Erreur", "Une erreur est survenue lors de la mise à jour des permissions.")
                else:
                    messagebox.showerror("Erreur", "Utilisateur non trouvé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
    
    def _reset_form(self):
        """Réinitialise le formulaire"""
        if self.selected_user_id:
            # Recharger les données de l'utilisateur
            user = self.model.get_user_by_id(self.selected_user_id) if hasattr(self.model, 'get_user_by_id') else None
            
            if user:
                self.role_var.set(user.get("role", "user"))
                self._on_role_changed(None)
    
    def show(self):
        """
        Affiche la vue de gestion des permissions
        """
        self.frame.pack(fill=ctk.BOTH, expand=True)
    
    def hide(self):
        """
        Masque la vue de gestion des permissions
        """
        self.frame.pack_forget()
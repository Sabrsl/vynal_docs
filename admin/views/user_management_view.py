#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue de gestion des utilisateurs pour l'interface d'administration
"""

import logging
import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from datetime import datetime
from CTkMessagebox import CTkMessagebox

logger = logging.getLogger("VynalDocsAutomator.Admin.UserManagementView")

class UserManagementView:
    """
    Vue pour la gestion des utilisateurs
    """
    
    def __init__(self, parent, app_model):
        """
        Initialise la vue de gestion des utilisateurs
        
        Args:
            parent: Widget parent
            app_model: Modèle de l'application
        """
        self.parent = parent
        self.model = app_model
        
        # Cadre principal de la vue
        self.frame = ctk.CTkFrame(parent)
        
        # Récupérer une référence au contrôleur d'utilisateurs
        from admin.controllers.user_management_controller import UserManagementController
        self.controller = UserManagementController(None, app_model)
        
        # Variables d'état
        self.selected_user_id = None
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        # Création de l'interface
        self.create_widgets()
        
        logger.info("UserManagementView initialisée")
    
    def create_widgets(self):
        """
        Crée les widgets de la vue de gestion des utilisateurs
        """
        # En-tête
        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.pack(fill=ctk.X, padx=20, pady=10)
        
        # Titre de la page
        ctk.CTkLabel(
            header,
            text="Gestion des utilisateurs",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side=ctk.LEFT)
        
        # Barre d'outils
        tools_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        tools_frame.pack(fill=ctk.X, padx=20, pady=(0, 10))
        
        # Zone de recherche
        search_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        search_frame.pack(side=ctk.LEFT, fill=ctk.X, expand=True)
        
        # Label et champ de recherche
        ctk.CTkLabel(
            search_frame, 
            text="Rechercher:", 
            font=ctk.CTkFont(size=12)
        ).pack(side=ctk.LEFT, padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            width=250,
            placeholder_text="Nom, email, rôle..."
        )
        search_entry.pack(side=ctk.LEFT, padx=5)
        
        # Boutons d'action
        actions_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        actions_frame.pack(side=ctk.RIGHT)
        
        # Bouton Ajouter
        self.add_user_btn = ctk.CTkButton(
            actions_frame,
            text="+ Ajouter",
            command=self._add_user
        )
        self.add_user_btn.pack(side=ctk.LEFT, padx=5)
        
        # Bouton Modifier
        self.edit_user_btn = ctk.CTkButton(
            actions_frame,
            text="✎ Modifier",
            command=self._edit_user,
            state="disabled"
        )
        self.edit_user_btn.pack(side=ctk.LEFT, padx=5)
        
        # Bouton Supprimer
        self.delete_user_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Supprimer",
            command=self._delete_user,
            state="disabled",
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        self.delete_user_btn.pack(side=ctk.LEFT, padx=5)
        
        # Bouton Réinitialiser mot de passe
        self.reset_pwd_btn = ctk.CTkButton(
            actions_frame,
            text="🔑 Réinitialiser MDP",
            command=self._reset_password,
            state="disabled"
        )
        self.reset_pwd_btn.pack(side=ctk.LEFT, padx=5)
        
        # Conteneur principal pour la liste des utilisateurs
        main_container = ctk.CTkFrame(self.frame)
        main_container.pack(fill=ctk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Créer un style personnalisé pour Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        font=('Arial', 11),
                        rowheight=25,
                        background="#2a2d2e",
                        foreground="white",
                        fieldbackground="#2a2d2e")
        style.configure("Treeview.Heading", 
                        font=('Arial', 11, 'bold'),
                        background="#1f2122",
                        foreground="white")
        style.map("Treeview", background=[("selected", "#3a7ebf")])
        
        # Créer un Treeview pour la liste des utilisateurs
        self.users_table = ttk.Treeview(
            main_container,
            columns=("id", "nom", "email", "role", "statut", "derniere_connexion"),
            show="headings",
            selectmode="browse"
        )
        
        # Définir les en-têtes
        self.users_table.heading("id", text="ID")
        self.users_table.heading("nom", text="Nom")
        self.users_table.heading("email", text="Email")
        self.users_table.heading("role", text="Rôle")
        self.users_table.heading("statut", text="Statut")
        self.users_table.heading("derniere_connexion", text="Dernière connexion")
        
        # Définir les largeurs de colonnes
        self.users_table.column("id", width=80, minwidth=80)
        self.users_table.column("nom", width=150, minwidth=150)
        self.users_table.column("email", width=200, minwidth=200)
        self.users_table.column("role", width=100, minwidth=100)
        self.users_table.column("statut", width=100, minwidth=100)
        self.users_table.column("derniere_connexion", width=150, minwidth=150)
        
        # Configurer le scroll vertical
        users_scrollbar = ttk.Scrollbar(
            main_container,
            orient="vertical",
            command=self.users_table.yview
        )
        self.users_table.configure(yscrollcommand=users_scrollbar.set)
        
        # Positionner le tableau et la scrollbar
        self.users_table.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        users_scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        
        # Configurer l'événement de sélection
        self.users_table.bind("<<TreeviewSelect>>", self._on_user_select)
        
        # Double-clic pour modifier
        self.users_table.bind("<Double-1>", lambda e: self._edit_user())
    
    def _on_user_select(self, event):
        """
        Gère la sélection d'un utilisateur dans la table
        """
        selected_items = self.users_table.selection()
        
        if selected_items:
            item = selected_items[0]
            user_id = self.users_table.item(item, "values")[0]
            self.selected_user_id = user_id
            
            # Activer les boutons
            self.edit_user_btn.configure(state="normal")
            self.delete_user_btn.configure(state="normal")
            self.reset_pwd_btn.configure(state="normal")
        else:
            self.selected_user_id = None
            
            # Désactiver les boutons
            self.edit_user_btn.configure(state="disabled")
            self.delete_user_btn.configure(state="disabled")
            self.reset_pwd_btn.configure(state="disabled")
    
    def _on_search_changed(self, *args):
        """
        Filtre les utilisateurs en fonction du texte de recherche
        """
        self.refresh_users()
    
    def _add_user(self):
        """
        Ouvre le dialogue pour ajouter un utilisateur
        """
        self.open_user_dialog()
    
    def _edit_user(self):
        """
        Ouvre le dialogue pour modifier l'utilisateur sélectionné
        """
        if self.selected_user_id:
            selected_user = self.controller.get_user_by_id(self.selected_user_id)
            if selected_user:
                self.open_user_dialog(selected_user)
    
    def _delete_user(self):
        """
        Supprime l'utilisateur sélectionné après confirmation
        """
        if not self.selected_user_id:
            return
            
        # Obtenir les informations de l'utilisateur
        user = self.controller.get_user_by_id(self.selected_user_id)
        if not user:
            return
            
        # Demander confirmation
        if not ctk.CTkMessagebox(
            title="Confirmation",
            message=f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user.get('email')} ?",
            icon="warning",
            option_1="Annuler",
            option_2="Supprimer"
        ).get() == "Supprimer":
            return
            
        # Supprimer l'utilisateur
        success, message = self.controller.delete_user(self.selected_user_id)
        
        # Afficher le résultat
        if success:
            ctk.CTkMessagebox(
                title="Succès",
                message="Utilisateur supprimé avec succès.",
                icon="check"
            )
            self.refresh_users()
        else:
            ctk.CTkMessagebox(
                title="Erreur",
                message=f"Erreur lors de la suppression : {message}",
                icon="cancel"
            )
    
    def _reset_password(self):
        """
        Réinitialise le mot de passe de l'utilisateur sélectionné
        """
        if not self.selected_user_id:
            return
            
        # Obtenir les informations de l'utilisateur
        user = self.controller.get_user_by_id(self.selected_user_id)
        if not user:
            return
            
        # Demander confirmation
        if not ctk.CTkMessagebox(
            title="Confirmation",
            message=f"Réinitialiser le mot de passe de {user.get('email')} ?",
            icon="question",
            option_1="Annuler",
            option_2="Réinitialiser"
        ).get() == "Réinitialiser":
            return
            
        # Réinitialiser le mot de passe
        success, message, new_password = self.controller.reset_password(self.selected_user_id)
        
        # Afficher le résultat
        if success:
            ctk.CTkMessagebox(
                title="Succès",
                message=f"Mot de passe réinitialisé avec succès.\n\nNouveau mot de passe : {new_password}",
                icon="check"
            )
        else:
            ctk.CTkMessagebox(
                title="Erreur",
                message=f"Erreur lors de la réinitialisation : {message}",
                icon="cancel"
            )
    
    def open_user_dialog(self, user=None):
        """
        Ouvre une boîte de dialogue pour ajouter ou modifier un utilisateur
        
        Args:
            user: Utilisateur à modifier (None pour un nouvel utilisateur)
        """
        is_new = user is None
        title = "Ajouter un utilisateur" if is_new else "Modifier l'utilisateur"
        
        # Créer une fenêtre modale
        dialog = ctk.CTkToplevel(self.frame)
        dialog.title(title)
        dialog.geometry("500x520")
        dialog.transient(self.frame.winfo_toplevel())
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = self.frame.winfo_toplevel().winfo_rootx() + (self.frame.winfo_toplevel().winfo_width() - dialog.winfo_width()) // 2
        y = self.frame.winfo_toplevel().winfo_rooty() + (self.frame.winfo_toplevel().winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Créer le formulaire
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Variables pour les champs
        email_var = tk.StringVar(value=user.get("email", "") if user else "")
        first_name_var = tk.StringVar(value=user.get("first_name", "") if user else "")
        last_name_var = tk.StringVar(value=user.get("last_name", "") if user else "")
        role_var = tk.StringVar(value=user.get("role", "user") if user else "user")
        is_active_var = tk.BooleanVar(value=user.get("is_active", True) if user else True)
        password_var = tk.StringVar()
        confirm_password_var = tk.StringVar()
        
        # Email
        ctk.CTkLabel(main_frame, text="Email *", anchor="w").pack(fill=ctk.X, pady=(0, 5))
        email_entry = ctk.CTkEntry(main_frame, textvariable=email_var, width=460)
        email_entry.pack(fill=ctk.X, pady=(0, 15))
        
        # Nom et prénom (sur la même ligne)
        name_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        name_frame.pack(fill=ctk.X, pady=(0, 15))
        
        # Prénom
        name_left = ctk.CTkFrame(name_frame, fg_color="transparent")
        name_left.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 5))
        ctk.CTkLabel(name_left, text="Prénom", anchor="w").pack(fill=ctk.X, pady=(0, 5))
        ctk.CTkEntry(name_left, textvariable=first_name_var).pack(fill=ctk.X)
        
        # Nom
        name_right = ctk.CTkFrame(name_frame, fg_color="transparent")
        name_right.pack(side=ctk.RIGHT, fill=ctk.X, expand=True, padx=(5, 0))
        ctk.CTkLabel(name_right, text="Nom", anchor="w").pack(fill=ctk.X, pady=(0, 5))
        ctk.CTkEntry(name_right, textvariable=last_name_var).pack(fill=ctk.X)
        
        # Rôle
        ctk.CTkLabel(main_frame, text="Rôle *", anchor="w").pack(fill=ctk.X, pady=(0, 5))
        
        roles = self.controller.get_user_roles()
        role_descriptions = {
            "admin": "Administrateur - Accès complet",
            "manager": "Gestionnaire - Gestion des utilisateurs et données",
            "support": "Support - Assistance et questions",
            "user": "Utilisateur - Fonctionnalités standard"
        }
        role_options = [f"{role} ({role_descriptions.get(role, '')})" for role in roles]
        
        role_menu = ctk.CTkOptionMenu(
            main_frame,
            values=role_options,
            command=lambda x: role_var.set(x.split(" ")[0])
        )
        # Sélectionner le rôle actuel
        if user and user.get("role") in roles:
            selected_index = roles.index(user.get("role"))
            role_menu.set(role_options[selected_index])
        else:
            role_menu.set(role_options[roles.index("user")])
            
        role_menu.pack(fill=ctk.X, pady=(0, 15))
        
        # Statut
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill=ctk.X, pady=(0, 15))
        
        is_active_checkbox = ctk.CTkCheckBox(
            status_frame,
            text="Utilisateur actif",
            variable=is_active_var
        )
        is_active_checkbox.pack(anchor="w")
        
        # Mot de passe
        if is_new:
            # Pour les nouveaux utilisateurs, on affiche les champs de mot de passe
            password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            password_frame.pack(fill=ctk.X, pady=(0, 15))
            
            ctk.CTkLabel(password_frame, text="Mot de passe *", anchor="w").pack(fill=ctk.X, pady=(0, 5))
            password_entry = ctk.CTkEntry(password_frame, textvariable=password_var, show="•")
            password_entry.pack(fill=ctk.X, pady=(0, 10))
            
            ctk.CTkLabel(password_frame, text="Confirmer le mot de passe *", anchor="w").pack(fill=ctk.X, pady=(0, 5))
            confirm_password_entry = ctk.CTkEntry(password_frame, textvariable=confirm_password_var, show="•")
            confirm_password_entry.pack(fill=ctk.X)
            
            # Exigences de mot de passe
            requirements_text = self.controller.get_password_requirements_message()
            ctk.CTkLabel(
                password_frame,
                text=requirements_text,
                font=ctk.CTkFont(size=10),
                text_color="gray",
                anchor="w"
            ).pack(fill=ctk.X, pady=(5, 0))
            
            # Bouton pour générer un mot de passe
            def generate_password():
                pwd = self.controller.generate_secure_password()
                password_var.set(pwd)
                confirm_password_var.set(pwd)
                
            ctk.CTkButton(
                password_frame,
                text="Générer un mot de passe",
                command=generate_password
            ).pack(pady=(10, 0))
        
        # Boutons d'action
        actions_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        actions_frame.pack(fill=ctk.X, padx=20, pady=20)
        
        # Fonction pour valider et sauvegarder
        def save_user():
            # Validation des champs obligatoires
            if not email_var.get().strip():
                ctk.CTkMessagebox(
                    title="Erreur",
                    message="L'email est obligatoire.",
                    icon="cancel"
                )
                return
                
            # Validation des mots de passe pour les nouveaux utilisateurs
            if is_new:
                if password_var.get() != confirm_password_var.get():
                    ctk.CTkMessagebox(
                        title="Erreur",
                        message="Les mots de passe ne correspondent pas.",
                        icon="cancel"
                    )
                    return
                    
                if not password_var.get():
                    ctk.CTkMessagebox(
                        title="Erreur",
                        message="Le mot de passe est obligatoire pour un nouvel utilisateur.",
                        icon="cancel"
                    )
                    return
            
            # Préparer les données de l'utilisateur
            user_data = {
                "email": email_var.get().strip(),
                "first_name": first_name_var.get().strip(),
                "last_name": last_name_var.get().strip(),
                "role": role_var.get(),
                "is_active": is_active_var.get()
            }
            
            # Ajouter l'ID pour les mises à jour
            if not is_new and user:
                user_data["id"] = user.get("id")
            
            # Ajouter le mot de passe pour les nouveaux utilisateurs
            if is_new:
                user_data["password"] = password_var.get()
            
            # Enregistrer l'utilisateur
            if is_new:
                success, message, _ = self.controller.create_user(user_data)
            else:
                success, message = self.controller.update_user(user_data)
            
            # Afficher le résultat
            if success:
                ctk.CTkMessagebox(
                    title="Succès",
                    message="Utilisateur enregistré avec succès.",
                    icon="check"
                )
                dialog.destroy()
                self.refresh_users()
            else:
                ctk.CTkMessagebox(
                    title="Erreur",
                    message=f"Erreur: {message}",
                    icon="cancel"
                )
        
        # Bouton Annuler
        ctk.CTkButton(
            actions_frame,
            text="Annuler",
            command=dialog.destroy,
            fg_color="#6c757d",
            hover_color="#5a6268"
        ).pack(side=ctk.LEFT, padx=(0, 10))
        
        # Bouton Enregistrer
        ctk.CTkButton(
            actions_frame,
            text="Enregistrer",
            command=save_user
        ).pack(side=ctk.RIGHT)
    
    def refresh_users(self):
        """
        Rafraîchit la liste des utilisateurs
        """
        # Effacer le tableau
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        
        # Obtenir les utilisateurs
        users = self.controller.get_users(force_refresh=True)
        
        # Filtrer selon la recherche
        search_text = self.search_var.get().lower()
        if search_text:
            filtered_users = []
            for user in users:
                # Rechercher dans nom, prénom, email et rôle
                if (search_text in user.get("email", "").lower() or
                    search_text in user.get("first_name", "").lower() or
                    search_text in user.get("last_name", "").lower() or
                    search_text in user.get("role", "").lower()):
                    filtered_users.append(user)
            users = filtered_users
        
        # Ajouter les utilisateurs au tableau
        for user in users:
            # Récupérer les valeurs à afficher
            user_id = user.get("id", "")
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            if not name:
                name = "(Sans nom)"
            email = user.get("email", "")
            role = user.get("role", "user")
            role_display = {
                "admin": "Administrateur",
                "manager": "Gestionnaire",
                "support": "Support",
                "user": "Utilisateur"
            }.get(role, role)
            
            status = "Actif" if user.get("is_active", True) else "Inactif"
            
            # Formatage de la date de dernière connexion
            last_login = user.get("last_login", "")
            if last_login:
                try:
                    last_login = datetime.fromisoformat(last_login)
                    last_login = last_login.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    last_login = "(Invalide)"
            else:
                last_login = "Jamais"
            
            # Ajouter l'utilisateur au tableau
            self.users_table.insert(
                "",
                "end",
                values=(user_id, name, email, role_display, status, last_login)
            )
        
        # Désélectionner tout
        self.selected_user_id = None
        self.edit_user_btn.configure(state="disabled")
        self.delete_user_btn.configure(state="disabled")
        self.reset_pwd_btn.configure(state="disabled")
    
    def show_password_reset(self):
        """
        Affiche le gestionnaire de réinitialisation de mot de passe
        """
        # Le gestionnaire de réinitialisation sera affiché par la classe parente
        if hasattr(self.model, 'show_password_reset'):
            self.model.show_password_reset()
    
    def show(self):
        """Affiche la vue et charge les données"""
        self.frame.pack(fill=ctk.BOTH, expand=True)
        self.refresh_users()
    
    def hide(self):
        """Cache la vue"""
        self.frame.pack_forget()
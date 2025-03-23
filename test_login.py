#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour le système d'authentification locale
"""

import os
import logging
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# S'assurer que les répertoires nécessaires existent
os.makedirs("data", exist_ok=True)
os.makedirs("config", exist_ok=True)

# Importer après avoir créé les répertoires
from utils.login_manager import LoginManager
from views.login_view import LoginView

class TestApp:
    """Application de test pour le système d'authentification"""
    
    def __init__(self):
        """Initialise l'application de test"""
        # Configuration de l'interface
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Test d'authentification")
        self.root.geometry("500x700")
        self.root.minsize(450, 650)
        
        # État de l'authentification
        self.logged_in = False
        self.current_user = None
        
        # Créer les conteneurs
        self.auth_container = ctk.CTkFrame(self.root)
        self.auth_container.pack(fill=tk.BOTH, expand=True)
        
        self.main_container = ctk.CTkFrame(self.root)
        
        # Créer l'interface d'authentification
        self.login_view = LoginView(self.auth_container, on_auth_success=self.on_auth_success)
        
        # Créer l'interface principale (masquée au départ)
        self._create_main_view()
    
    def _create_main_view(self):
        """Crée l'interface principale de l'application"""
        # Titre
        title = ctk.CTkLabel(
            self.main_container,
            text="Tableau de bord",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Informations utilisateur
        self.user_frame = ctk.CTkFrame(self.main_container)
        self.user_frame.pack(fill=tk.X, padx=20, pady=10)
        
        user_icon_frame = ctk.CTkFrame(self.user_frame, width=80, height=80, corner_radius=40)
        user_icon_frame.pack(side=tk.LEFT, padx=20, pady=20)
        user_icon_frame.pack_propagate(False)
        
        user_icon_label = ctk.CTkLabel(
            user_icon_frame,
            text="👤",
            font=ctk.CTkFont(size=36)
        )
        user_icon_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        user_info = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        user_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=20)
        
        self.user_name = ctk.CTkLabel(
            user_info,
            text="Non connecté",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self.user_name.pack(fill=tk.X, pady=(0, 5))
        
        self.user_email = ctk.CTkLabel(
            user_info,
            text="",
            anchor="w"
        )
        self.user_email.pack(fill=tk.X)
        
        self.user_license = ctk.CTkLabel(
            user_info,
            text="",
            anchor="w"
        )
        self.user_license.pack(fill=tk.X)
        
        # Conteneur de contenu
        content = ctk.CTkFrame(self.main_container)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Message de bienvenue
        welcome = ctk.CTkLabel(
            content,
            text="Bienvenue dans Vynal Docs Automator!",
            font=ctk.CTkFont(size=16)
        )
        welcome.pack(pady=50)
        
        info_text = ("Votre compte est maintenant connecté et vous pouvez utiliser toutes les "
                    "fonctionnalités de l'application. Vos informations d'identification sont "
                    "stockées localement et sécurisées par chiffrement.")
        
        info = ctk.CTkLabel(
            content,
            text=info_text,
            wraplength=400,
            justify="center"
        )
        info.pack(pady=10)
        
        # Bouton de déconnexion
        logout_button = ctk.CTkButton(
            content,
            text="Se déconnecter",
            command=self.logout
        )
        logout_button.pack(pady=30)
    
    def on_auth_success(self, user_info):
        """
        Appelé lorsque l'authentification réussit
        
        Args:
            user_info: Informations de l'utilisateur
        """
        self.logged_in = True
        self.current_user = user_info
        
        # Mettre à jour l'interface avec les informations utilisateur
        self.user_name.configure(text=user_info.get("email", "").split('@')[0])
        self.user_email.configure(text=user_info.get("email", ""))
        
        license_status = "Active" if user_info.get("license_valid", False) else "Inactive"
        self.user_license.configure(
            text=f"Licence: {license_status}",
            text_color="#4CAF50" if user_info.get("license_valid", False) else "#E53935"
        )
        
        # Basculer vers l'interface principale
        self.auth_container.pack_forget()
        self.main_container.pack(fill=tk.BOTH, expand=True)
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        # Réinitialiser l'état
        self.logged_in = False
        self.current_user = None
        
        # Déconnecter dans le gestionnaire de login
        self.login_view.logout()
        
        # Basculer vers l'interface d'authentification
        self.main_container.pack_forget()
        self.auth_container.pack(fill=tk.BOTH, expand=True)
    
    def run(self):
        """Démarre l'application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run() 
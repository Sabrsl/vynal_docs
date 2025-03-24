#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vue Mon Compte pour l'application Vynal Docs Automator
"""

import os
import logging
import customtkinter as ctk
from datetime import datetime
from typing import Callable, Dict, Any, Optional
from PIL import Image, ImageTk

logger = logging.getLogger("VynalDocsAutomator.AccountView")

class AccountView:
    """Vue moderne pour la gestion du compte utilisateur"""
    
    def __init__(self, parent, app_model=None, user_data=None, on_logout=None, on_back=None):
        """Initialise la vue Mon Compte
        
        Args:
            parent: Le widget parent
            app_model: Le modèle de l'application
            user_data: Les données de l'utilisateur
            on_logout: Callback de déconnexion
            on_back: Callback de retour
        """
        self.parent = parent
        self.app_model = app_model
        self.user_data = user_data or {}
        self.on_logout = on_logout
        self.on_back = on_back
        
        # Frame principal avec fond transparent
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Créer l'interface
        self._create_widgets()
        logger.info("Vue Mon Compte initialisée")
    
    def _create_widgets(self):
        """Crée l'interface utilisateur moderne"""
        # Container principal avec scroll
        self.main_container = ctk.CTkScrollableFrame(
            self.frame,
            fg_color="transparent"
        )
        self.main_container.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # En-tête avec avatar et infos principales
        self._create_header()
        
        # Section licence et limitations
        self._create_license_section()
        
        # Section limitations pour version gratuite
        if not self.user_data.get("license_valid", False):
            self._create_limitations_section()
        
        # Section statistiques
        self._create_stats_section()
        
        # Boutons d'action
        self._create_action_buttons()
    
    def _create_header(self):
        """Crée l'en-tête avec avatar et informations principales"""
        header = ctk.CTkFrame(self.main_container, corner_radius=15)
        header.pack(fill=ctk.X, pady=(0, 20))
        
        # Container flex pour l'avatar et les infos
        flex_container = ctk.CTkFrame(header, fg_color="transparent")
        flex_container.pack(fill=ctk.X, padx=30, pady=30)
        
        # Avatar (cercle avec initiales)
        avatar_size = 90
        avatar_frame = ctk.CTkFrame(
            flex_container,
            width=avatar_size,
            height=avatar_size,
            corner_radius=avatar_size//2,
            fg_color=("#2980b9", "#3498db")
        )
        avatar_frame.pack(side="left", padx=(0, 20))
        avatar_frame.pack_propagate(False)
        
        # Initiales dans l'avatar
        email = self.user_data.get("email", "").strip()
        initials = email[0].upper() if email else "U"
        
        avatar_text = ctk.CTkLabel(
            avatar_frame,
            text=initials,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        avatar_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Informations utilisateur
        info_frame = ctk.CTkFrame(flex_container, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Email
        email_label = ctk.CTkLabel(
            info_frame,
            text=email,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        email_label.pack(anchor="w")
        
        # Date d'inscription
        created_at = self._format_date(self.user_data.get("created_at", ""))
        join_date = ctk.CTkLabel(
            info_frame,
            text=f"Membre depuis le {created_at}",
            font=ctk.CTkFont(size=13),
            text_color=("gray60", "gray45")
        )
        join_date.pack(anchor="w", pady=(5, 0))
    
    def _create_license_section(self):
        """Crée la section d'informations sur la licence"""
        license_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        license_frame.pack(fill=ctk.X, pady=(0, 20))
        
        # Titre de section
        title_frame = ctk.CTkFrame(license_frame, fg_color="transparent")
        title_frame.pack(fill=ctk.X, padx=30, pady=(20, 0))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Statut de la licence",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(side="left")
        
        # Badge de statut
        is_premium = self.user_data.get("license_valid", False)
        status_text = "Premium" if is_premium else "Gratuit"
        status_color = ("#2ecc71", "#27ae60") if is_premium else ("#e74c3c", "#c0392b")
        
        status_badge = ctk.CTkFrame(
            title_frame,
            corner_radius=12,
            fg_color=status_color,
            height=24
        )
        status_badge.pack(side="left", padx=(10, 0))
        status_badge.pack_propagate(False)
        
        status_label = ctk.CTkLabel(
            status_badge,
            text=f" {status_text} ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        status_label.pack(expand=True, padx=10)
        
        # Détails de la licence
        details_frame = ctk.CTkFrame(license_frame, fg_color="transparent")
        details_frame.pack(fill=ctk.X, padx=30, pady=20)
        
        # Grid pour les détails
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Type de licence
        ctk.CTkLabel(
            details_frame,
            text="Type:",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        ctk.CTkLabel(
            details_frame,
            text=self.user_data.get("license_type", "Version gratuite")
        ).grid(row=0, column=1, sticky="w", padx=(20, 0), pady=5)
        
        # Date d'expiration si premium
        if is_premium and self.user_data.get("license_expiry"):
            ctk.CTkLabel(
                details_frame,
                text="Expire le:",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=1, column=0, sticky="w", pady=5)
            
            expiry_date = self._format_date(self.user_data.get("license_expiry"))
            ctk.CTkLabel(
                details_frame,
                text=expiry_date
            ).grid(row=1, column=1, sticky="w", padx=(20, 0), pady=5)
            
        # Bouton upgrade si version gratuite
        if not is_premium:
            upgrade_btn = ctk.CTkButton(
                license_frame,
                text="Passer à la version Premium",
                font=ctk.CTkFont(weight="bold"),
                fg_color=("#f39c12", "#d35400"),
                hover_color=("#e67e22", "#c0392b"),
                height=40
            )
            upgrade_btn.pack(padx=30, pady=(0, 20))
    
    def _create_limitations_section(self):
        """Crée la section des limitations pour la version gratuite"""
        limitations_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        limitations_frame.pack(fill=ctk.X, pady=(0, 20))
        
        # Titre avec icône d'avertissement
        title_frame = ctk.CTkFrame(limitations_frame, fg_color="transparent")
        title_frame.pack(fill=ctk.X, padx=30, pady=(20, 15))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Limitations de la version gratuite",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#e67e22", "#f39c12")
        )
        title.pack(anchor="w")
        
        # Liste des limitations
        limitations = [
            ("Nombre de clients", "5 maximum"),
            ("Documents par mois", "20 maximum"),
            ("Modèles personnalisés", "2 maximum"),
            ("Stockage total", "100 MB maximum"),
            ("Chat IA", "Non disponible"),
            ("Export PDF avancé", "Non disponible"),
            ("Support prioritaire", "Non disponible")
        ]
        
        # Grid pour les limitations
        grid = ctk.CTkFrame(limitations_frame, fg_color="transparent")
        grid.pack(fill=ctk.X, padx=30, pady=(0, 20))
        grid.grid_columnconfigure(1, weight=1)
        
        for i, (label, value) in enumerate(limitations):
            # Label
            ctk.CTkLabel(
                grid,
                text=label,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=i, column=0, sticky="w", pady=5)
            
            # Valeur
            ctk.CTkLabel(
                grid,
                text=value,
                text_color=("gray60", "gray45")
            ).grid(row=i, column=1, sticky="w", padx=(20, 0), pady=5)
    
    def _create_stats_section(self):
        """Crée la section des statistiques d'utilisation"""
        stats_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        stats_frame.pack(fill=ctk.X)
        
        # Titre
        ctk.CTkLabel(
            stats_frame,
            text="Statistiques d'utilisation",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=30, pady=(20, 15))
        
        # Grid pour les stats
        grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid.pack(fill=ctk.X, padx=30, pady=(0, 20))
        
        # Configuration des colonnes
        grid.grid_columnconfigure((0, 1), weight=1)
        
        # Stats (à adapter selon vos besoins)
        stats = [
            ("Documents créés", self.user_data.get("docs_created", 0)),
            ("Modèles utilisés", self.user_data.get("templates_used", 0)),
            ("Dernière activité", self._format_date(self.user_data.get("last_activity", ""))),
            ("Espace utilisé", self._format_size(self.user_data.get("storage_used", 0)))
        ]
        
        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            stat_frame = ctk.CTkFrame(grid, fg_color=("gray95", "gray10"), corner_radius=10)
            stat_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
            # Valeur
            ctk.CTkLabel(
                stat_frame,
                text=str(value),
                font=ctk.CTkFont(size=20, weight="bold")
            ).pack(anchor="w", padx=15, pady=(15, 5))
            
            # Label
            ctk.CTkLabel(
                stat_frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray45")
            ).pack(anchor="w", padx=15, pady=(0, 15))
    
    def _create_action_buttons(self):
        """Crée les boutons d'action"""
        buttons_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        buttons_frame.pack(fill=ctk.X, pady=(20, 0))
        
        # Bouton de déconnexion
        logout_btn = ctk.CTkButton(
            buttons_frame,
            text="Déconnexion",
            command=self._handle_logout,
            fg_color=("#e74c3c", "#c0392b"),
            hover_color=("#c0392b", "#a93226"),
            height=40
        )
        logout_btn.pack(side="left")
        
        # Bouton retour
        back_btn = ctk.CTkButton(
            buttons_frame,
            text="Retour",
            command=self._handle_back,
            height=40
        )
        back_btn.pack(side="left", padx=(10, 0))
    
    def _format_date(self, date_str):
        """Formate une date pour l'affichage"""
        if not date_str:
            return "Non disponible"
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif isinstance(date_str, datetime):
                date_obj = date_str
            else:
                return str(date_str)
            return date_obj.strftime("%d/%m/%Y %H:%M")
        except:
            return str(date_str)
    
    def _format_size(self, size_bytes):
        """Formate une taille en bytes en format lisible"""
        if not isinstance(size_bytes, (int, float)):
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _handle_logout(self):
        """Gère la déconnexion"""
        if self.on_logout:
            self.on_logout()
    
    def _handle_back(self):
        """Gère le retour"""
        if self.on_back:
            self.on_back()
    
    def show(self):
        """Affiche la vue"""
        logger.info("Affichage de la vue Mon Compte")
        self.frame.pack(fill=ctk.BOTH, expand=True)
    
    def hide(self):
        """Cache la vue"""
        logger.info("Masquage de la vue Mon Compte")
        self.frame.pack_forget() 
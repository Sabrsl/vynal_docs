#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptateur pour connecter le système d'authentification à l'UsageTracker existant.
Cet adaptateur permet d'utiliser l'UsageTracker comme gestionnaire d'authentification
tout en préservant une interface moderne pour les vues d'authentification.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Importer l'UsageTracker
from utils.usage_tracker import UsageTracker

logger = logging.getLogger("VynalDocsAutomator.AuthAdapter")

class AuthAdapter:
    """
    Adaptateur qui connecte le système d'authentification (LoginView, etc.)
    au système d'UsageTracker existant.
    
    Cette classe convertit les appels de l'interface utilisateur aux 
    fonctions équivalentes de l'UsageTracker et vice versa.
    """
    
    def __init__(self):
        """Initialise l'adaptateur d'authentification"""
        self.usage_tracker = UsageTracker()
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration de l'application"""
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            self.config = {
                "authentication": {
                    "enabled": True,
                    "allow_registration": True,
                    "max_login_attempts": 5
                }
            }
    
    @property
    def is_authenticated(self) -> bool:
        """
        Vérifie si un utilisateur est actuellement authentifié
        
        Returns:
            bool: True si un utilisateur est authentifié, False sinon
        """
        return self.usage_tracker.has_active_user()
    
    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authentifie un utilisateur avec son email et son mot de passe
        
        Args:
            email: Adresse email de l'utilisateur
            password: Mot de passe de l'utilisateur
            
        Returns:
            Dict[str, Any]: Informations de l'utilisateur ou None si l'authentification échoue
            
        Raises:
            ValueError: Si les identifiants sont incorrects
        """
        try:
            # Vérifier si l'authentification est activée
            if not self.config.get("authentication", {}).get("enabled", True):
                raise ValueError("Le système d'authentification est désactivé")
            
            # Authentifier l'utilisateur avec l'UsageTracker
            result = self.usage_tracker.authenticate_user(email, password)
            
            if result:
                # Récupérer les informations de l'utilisateur
                user_info = self.usage_tracker.get_user_info(email)
                
                # Formater les informations utilisateur pour l'interface
                formatted_user = {
                    "email": email,
                    "name": user_info.get("name", email.split("@")[0]),
                    "role": user_info.get("role", "user"),
                    "usage": {
                        "documents_created": user_info.get("docs_created", 0),
                        "total_usage_time": user_info.get("total_usage_time", 0),
                        "last_login": user_info.get("last_login", "")
                    }
                }
                
                return formatted_user
            else:
                logger.warning(f"Échec de l'authentification pour {email}")
                raise ValueError("Email ou mot de passe incorrect")
        except Exception as e:
            logger.error(f"Erreur d'authentification: {e}")
            raise ValueError(f"Erreur d'authentification: {str(e)}")
    
    def register(self, email: str, password: str, name: str = None) -> Dict[str, Any]:
        """
        Enregistre un nouvel utilisateur
        
        Args:
            email: Adresse email de l'utilisateur
            password: Mot de passe de l'utilisateur
            name: Nom de l'utilisateur (optionnel)
            
        Returns:
            Dict[str, Any]: Informations de l'utilisateur ou None si l'enregistrement échoue
            
        Raises:
            ValueError: Si l'email est déjà utilisé ou si les données sont invalides
        """
        try:
            # Vérifier si l'inscription est activée
            if not self.config.get("authentication", {}).get("allow_registration", True):
                raise ValueError("L'inscription de nouveaux utilisateurs est désactivée")
            
            # Vérifier si l'email est valide
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValueError("Format d'email invalide")
            
            # Vérifier si un utilisateur avec cet email existe déjà
            if self.usage_tracker.user_exists(email):
                raise ValueError(f"Un utilisateur avec l'email {email} existe déjà")
            
            # Préparer les données utilisateur
            user_data = {
                "name": name or email.split("@")[0],
                "role": "user",
                "created_at": datetime.now().isoformat(),
                "docs_created": 0,
                "total_usage_time": 0
            }
            
            # Enregistrer l'utilisateur
            result = self.usage_tracker.register_user(email, password, user_data)
            
            if not result:
                raise ValueError("Erreur lors de l'enregistrement de l'utilisateur")
                
            logger.info(f"Nouvel utilisateur enregistré: {email}")
            
            if result:
                # Authentifier immédiatement l'utilisateur
                self.usage_tracker.authenticate_user(email, password)
                
                # Formater les informations utilisateur pour l'interface
                formatted_user = {
                    "email": email,
                    "name": name or email.split("@")[0],
                    "role": "user",
                    "usage": {
                        "documents_created": 0,
                        "total_usage_time": 0,
                        "last_login": "Maintenant"
                    }
                }
                
                return formatted_user
            else:
                raise ValueError("Erreur lors de l'enregistrement de l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur d'enregistrement: {e}")
            raise ValueError(f"Erreur d'enregistrement: {str(e)}")
    
    def logout(self) -> bool:
        """
        Déconnecte l'utilisateur actuel
        
        Returns:
            bool: True si la déconnexion a réussi, False sinon
        """
        try:
            result = self.usage_tracker.logout_user()
            if result:
                logger.info("Utilisateur déconnecté")
            return result
        except Exception as e:
            logger.error(f"Erreur de déconnexion: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations de l'utilisateur actuellement connecté
        
        Returns:
            Optional[Dict[str, Any]]: Informations de l'utilisateur ou None si aucun utilisateur n'est connecté
        """
        if not self.is_authenticated:
            return None
        
        # Récupérer l'email de l'utilisateur actif
        user_email = self.usage_tracker.get_active_user()
        
        if not user_email:
            return None
        
        # Récupérer les informations de l'utilisateur
        user_info = self.usage_tracker.get_user_info(user_email)
        
        # Formater les informations utilisateur pour l'interface
        formatted_user = {
            "email": user_email,
            "name": user_info.get("name", user_email.split("@")[0]),
            "role": user_info.get("role", "user"),
            "usage": {
                "documents_created": user_info.get("docs_created", 0),
                "total_usage_time": user_info.get("total_usage_time", 0),
                "last_login": user_info.get("last_login", "")
            }
        }
        
        return formatted_user
    
    def check_password_reset(self, email: str) -> bool:
        """
        Vérifie si un utilisateur peut réinitialiser son mot de passe
        
        Args:
            email: Adresse email de l'utilisateur
            
        Returns:
            bool: True si l'utilisateur peut réinitialiser son mot de passe, False sinon
        """
        # Pour simplifier, on vérifie juste si l'utilisateur existe
        return self.usage_tracker.user_exists(email)
    
    def reset_password(self, email: str, new_password: str) -> bool:
        """
        Réinitialise le mot de passe d'un utilisateur
        
        Args:
            email: Adresse email de l'utilisateur
            new_password: Nouveau mot de passe
            
        Returns:
            bool: True si la réinitialisation a réussi, False sinon
            
        Raises:
            ValueError: Si l'utilisateur n'existe pas ou si le mot de passe est invalide
        """
        try:
            # Vérifier si l'utilisateur existe
            if not self.usage_tracker.user_exists(email):
                raise ValueError(f"Aucun compte trouvé avec l'email {email}")
            
            # Vérifier la longueur du mot de passe
            min_length = self.config.get("security", {}).get("min_password_length", 6)
            if len(new_password) < min_length:
                raise ValueError(f"Le mot de passe doit contenir au moins {min_length} caractères")
            
            # Réinitialiser le mot de passe
            result = self.usage_tracker.update_user_password(email, new_password)
            
            if result:
                logger.info(f"Mot de passe réinitialisé pour {email}")
                return True
            else:
                raise ValueError("Erreur lors de la réinitialisation du mot de passe")
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation du mot de passe: {e}")
            raise ValueError(f"Erreur lors de la réinitialisation du mot de passe: {str(e)}")
    
    def update_user_info(self, email: str, user_data: Dict[str, Any]) -> bool:
        """
        Met à jour les informations d'un utilisateur
        
        Args:
            email: Adresse email de l'utilisateur
            user_data: Nouvelles informations utilisateur
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
            
        Raises:
            ValueError: Si l'utilisateur n'existe pas
        """
        try:
            # Vérifier si l'utilisateur existe
            if not self.usage_tracker.user_exists(email):
                raise ValueError(f"Aucun compte trouvé avec l'email {email}")
            
            # Mettre à jour les informations utilisateur
            result = self.usage_tracker.update_user_info(email, user_data)
            
            if result:
                logger.info(f"Informations utilisateur mises à jour pour {email}")
                return True
            else:
                raise ValueError("Erreur lors de la mise à jour des informations utilisateur")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des informations utilisateur: {e}")
            raise ValueError(f"Erreur lors de la mise à jour des informations utilisateur: {str(e)}") 
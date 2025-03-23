#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire d'authentification local pour l'application Vynal Docs Automator
Gère les utilisateurs, les sessions et les authentifications en mode hors-ligne
"""

import os
import json
import time
import logging
import hashlib
import base64
import uuid
from typing import Dict, Tuple, Any, Optional
from datetime import datetime, timedelta

# Configuration du logger
logger = logging.getLogger("VynalDocsAutomator.LoginManager")

class LoginManager:
    """
    Gestionnaire d'authentification local pour l'application
    
    Gère l'enregistrement des utilisateurs, l'authentification et les sessions
    Les données sont stockées localement dans un fichier JSON
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'authentification"""
        # Chargement de la configuration
        self.config = self._load_config()
        
        # Paramètres de sécurité
        self.security_config = self.config.get("security", {})
        self.auth_config = self.config.get("authentication", {})
        
        # Algorithme et paramètres de hachage
        self.hash_algorithm = self.security_config.get("hash_algorithm", "sha256")
        self.hash_iterations = self.security_config.get("hash_iterations", 100000)
        
        # Paramètres d'authentification
        self.min_password_length = self.security_config.get("min_password_length", 6)
        self.session_expiry_hours = self.security_config.get("session_expiry_hours", 24)
        
        # Chemins des fichiers de données
        self.data_dir = self._ensure_data_dir()
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.session_file = os.path.join(self.data_dir, "session.json")
        
        # Chargement des données utilisateurs
        self.users = self._load_users()
        self.current_session = self._load_session()
        
        # Vérification de la session active
        self._validate_current_session()
    
    def _load_config(self) -> Dict:
        """Charge la configuration de l'application"""
        try:
            config_path = "config.json"
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning("Fichier de configuration introuvable. Utilisation des valeurs par défaut.")
                return {}
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            return {}
    
    def _ensure_data_dir(self) -> str:
        """Assure l'existence du répertoire de données"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def _load_users(self) -> Dict:
        """Charge les données utilisateurs depuis le fichier JSON"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement des utilisateurs: {e}")
                return {}
        else:
            return {}
    
    def _save_users(self) -> bool:
        """Enregistre les données utilisateurs dans le fichier JSON"""
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des utilisateurs: {e}")
            return False
    
    def _load_session(self) -> Dict:
        """Charge les données de session depuis le fichier JSON"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement de la session: {e}")
                return {}
        else:
            return {}
    
    def _save_session(self) -> bool:
        """Enregistre les données de session dans le fichier JSON"""
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.current_session, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la session: {e}")
            return False
    
    def _validate_current_session(self) -> bool:
        """Vérifie si la session actuelle est valide et non expirée"""
        if not self.current_session:
            return False
        
        # Vérifier l'existence des champs requis
        if not all(key in self.current_session for key in ["email", "token", "expires_at"]):
            self.current_session = {}
            self._save_session()
            return False
        
        # Vérifier si la session a expiré
        expires_at = self.current_session.get("expires_at", 0)
        current_time = time.time()
        
        if current_time > expires_at:
            logger.info("Session expirée, déconnexion automatique")
            self.current_session = {}
            self._save_session()
            return False
        
        # Vérifier si l'utilisateur existe toujours
        email = self.current_session.get("email")
        if email not in self.users:
            logger.warning(f"Utilisateur {email} de la session non trouvé dans la base de données")
            self.current_session = {}
            self._save_session()
            return False
        
        return True
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hache un mot de passe avec un sel (généré ou fourni)
        
        Args:
            password: Mot de passe à hacher
            salt: Sel à utiliser (si None, un nouveau sel est généré)
            
        Returns:
            Tuple (hachage, sel)
        """
        if salt is None:
            # Générer un nouveau sel
            salt = base64.b64encode(os.urandom(16)).decode("utf-8")
        
        # Hacher le mot de passe avec le sel
        password_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")
        
        password_hash = hashlib.pbkdf2_hmac(
            self.hash_algorithm,
            password_bytes,
            salt_bytes,
            self.hash_iterations
        )
        
        # Encoder le hachage en base64
        password_hash_b64 = base64.b64encode(password_hash).decode("utf-8")
        
        return password_hash_b64, salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """
        Vérifie si un mot de passe correspond au hachage stocké
        
        Args:
            password: Mot de passe à vérifier
            stored_hash: Hachage stocké
            salt: Sel utilisé
            
        Returns:
            True si le mot de passe correspond, False sinon
        """
        # Hacher le mot de passe fourni avec le sel stocké
        calculated_hash, _ = self._hash_password(password, salt)
        
        # Comparer les hachages
        return calculated_hash == stored_hash
    
    def _generate_session_token(self) -> str:
        """Génère un jeton de session unique"""
        return str(uuid.uuid4())
    
    def register_user(self, email: str, password: Optional[str] = None, 
                      license_key: Optional[str] = None) -> Tuple[bool, str]:
        """
        Enregistre un nouvel utilisateur
        
        Args:
            email: Adresse email (identifiant unique)
            password: Mot de passe (optionnel si license_key est fourni)
            license_key: Clé de licence (optionnelle si password est fourni)
            
        Returns:
            Tuple (succès, message)
        """
        # Vérifier si l'inscription est activée
        if not self.auth_config.get("allow_registration", True):
            return False, "L'inscription de nouveaux utilisateurs est désactivée"
        
        # Vérifier si l'email est déjà utilisé
        if email in self.users:
            return False, "Cette adresse email est déjà utilisée"
        
        # Vérifier qu'au moins un mot de passe ou une clé de licence est fourni
        if not password and not license_key:
            return False, "Un mot de passe ou une clé de licence est requis"
        
        # Valider le mot de passe si fourni
        if password and len(password) < self.min_password_length:
            return False, f"Le mot de passe doit contenir au moins {self.min_password_length} caractères"
        
        # Préparer les données utilisateur
        user_data = {
            "email": email,
            "created_at": time.time(),
            "last_login": None
        }
        
        # Hacher et stocker le mot de passe si fourni
        if password:
            password_hash, salt = self._hash_password(password)
            user_data["password_hash"] = password_hash
            user_data["salt"] = salt
        
        # Stocker la clé de licence si fournie
        if license_key:
            user_data["license_key"] = license_key
        
        # Enregistrer l'utilisateur
        self.users[email] = user_data
        if self._save_users():
            logger.info(f"Nouvel utilisateur enregistré: {email}")
            return True, "Inscription réussie"
        else:
            return False, "Erreur lors de l'enregistrement de l'utilisateur"
    
    def authenticate(self, email: str, password: Optional[str] = None,
                     license_key: Optional[str] = None, stay_connected: bool = False) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authentifie un utilisateur
        
        Args:
            email: Adresse email
            password: Mot de passe (optionnel si license_key est fourni)
            license_key: Clé de licence (optionnelle si password est fourni)
            stay_connected: Si True, la session expirera après une période plus longue
            
        Returns:
            Tuple (succès, message, informations utilisateur)
        """
        # Vérifier si l'authentification est activée
        if not self.auth_config.get("enabled", True):
            return False, "L'authentification est désactivée", None
        
        # Vérifier si l'utilisateur existe
        if email not in self.users:
            return False, "Email ou mot de passe incorrect", None
        
        user_data = self.users[email]
        authenticated = False
        
        # Authentification par mot de passe
        if password and "password_hash" in user_data:
            stored_hash = user_data["password_hash"]
            salt = user_data["salt"]
            authenticated = self._verify_password(password, stored_hash, salt)
        
        # Authentification par clé de licence
        elif license_key and "license_key" in user_data:
            authenticated = license_key == user_data["license_key"]
        
        if not authenticated:
            return False, "Email ou mot de passe incorrect", None
        
        # Mettre à jour la date de dernière connexion
        self.users[email]["last_login"] = time.time()
        self._save_users()
        
        # Créer une session
        session_token = self._generate_session_token()
        
        # Calculer la date d'expiration
        expiry_hours = self.session_expiry_hours * 3 if stay_connected else self.session_expiry_hours
        expiry_time = time.time() + (expiry_hours * 3600)
        
        # Enregistrer la session
        self.current_session = {
            "email": email,
            "token": session_token,
            "created_at": time.time(),
            "expires_at": expiry_time,
            "stay_connected": stay_connected
        }
        self._save_session()
        
        # Préparer les informations utilisateur à retourner
        user_info = {
            "email": email,
            "created_at": user_data["created_at"],
            "last_login": user_data["last_login"]
        }
        
        logger.info(f"Authentification réussie: {email}")
        return True, "Authentification réussie", user_info
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations de l'utilisateur actuellement connecté
        
        Returns:
            Dictionnaire des informations utilisateur ou None si aucune session active
        """
        if not self._validate_current_session():
            return None
        
        email = self.current_session.get("email")
        if email not in self.users:
            return None
        
        user_data = self.users[email]
        
        # Préparer les informations utilisateur à retourner
        user_info = {
            "email": email,
            "created_at": user_data["created_at"],
            "last_login": user_data["last_login"]
        }
        
        return user_info
    
    def reset_password(self, email: str, new_password: str) -> Tuple[bool, str]:
        """
        Réinitialise le mot de passe d'un utilisateur
        
        Args:
            email: Adresse email
            new_password: Nouveau mot de passe
            
        Returns:
            Tuple (succès, message)
        """
        # Vérifier si l'utilisateur existe
        if email not in self.users:
            return False, "Utilisateur non trouvé"
        
        # Valider le nouveau mot de passe
        if len(new_password) < self.min_password_length:
            return False, f"Le mot de passe doit contenir au moins {self.min_password_length} caractères"
        
        # Hacher et stocker le nouveau mot de passe
        password_hash, salt = self._hash_password(new_password)
        
        self.users[email]["password_hash"] = password_hash
        self.users[email]["salt"] = salt
        
        # Enregistrer les modifications
        if self._save_users():
            logger.info(f"Mot de passe réinitialisé pour: {email}")
            return True, "Mot de passe réinitialisé avec succès"
        else:
            return False, "Erreur lors de la réinitialisation du mot de passe"
    
    def logout(self) -> bool:
        """
        Déconnecte l'utilisateur actuel
        
        Returns:
            True si la déconnexion a réussi, False sinon
        """
        self.current_session = {}
        success = self._save_session()
        
        if success:
            logger.info("Utilisateur déconnecté")
        
        return success
    
    def delete_user(self, email: str) -> Tuple[bool, str]:
        """
        Supprime un utilisateur
        
        Args:
            email: Adresse email de l'utilisateur à supprimer
            
        Returns:
            Tuple (succès, message)
        """
        # Vérifier si l'utilisateur existe
        if email not in self.users:
            return False, "Utilisateur non trouvé"
        
        # Supprimer l'utilisateur
        del self.users[email]
        
        # Si l'utilisateur supprimé était connecté, le déconnecter
        if self.current_session.get("email") == email:
            self.logout()
        
        # Enregistrer les modifications
        if self._save_users():
            logger.info(f"Utilisateur supprimé: {email}")
            return True, "Utilisateur supprimé avec succès"
        else:
            return False, "Erreur lors de la suppression de l'utilisateur"
    
    @property
    def is_authenticated(self) -> bool:
        """Indique si un utilisateur est actuellement authentifié"""
        return self._validate_current_session()


# Test du gestionnaire d'authentification
if __name__ == "__main__":
    # Configuration du logging pour les tests
    logging.basicConfig(level=logging.INFO)
    
    # Créer une instance du gestionnaire
    login_manager = LoginManager()
    
    # Tester les fonctionnalités
    print("Test d'inscription:")
    success, message = login_manager.register_user("test@example.com", "password123")
    print(f"Résultat: {success}, Message: {message}")
    
    print("\nTest d'authentification:")
    success, message, user_info = login_manager.authenticate("test@example.com", "password123")
    print(f"Résultat: {success}, Message: {message}")
    print(f"Informations utilisateur: {user_info}")
    
    print("\nTest de récupération de l'utilisateur courant:")
    current_user = login_manager.get_current_user()
    print(f"Utilisateur actuel: {current_user}")
    
    print("\nTest de déconnexion:")
    success = login_manager.logout()
    print(f"Déconnexion réussie: {success}")
    print(f"Utilisateur toujours connecté: {login_manager.is_authenticated}") 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire de suivi d'utilisation simplifié pour l'application Vynal Docs Automator
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import time
from utils.security import SecureFileManager

# Configuration du logger
logger = logging.getLogger("VynalDocsAutomator.UsageTracker")

class UsageTracker:
    """Gestionnaire de suivi d'utilisation simplifié"""
    
    def __init__(self):
        """Initialise le gestionnaire de suivi"""
        self.data_dir = os.path.join("data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialiser le gestionnaire de fichiers sécurisés
        self.secure_files = SecureFileManager(self.data_dir)
        
        self.usage_file = os.path.join(self.data_dir, "usage_count.json")
        self.usage_count = self._load_usage_count()
        
        # Limites d'utilisation
        self.max_uses = 10  # Nombre maximum d'utilisations avant demande d'inscription
        
        # Fonctionnalités nécessitant une inscription
        self.protected_features = {
            "password_protection": True,    # Protection par mot de passe
            "template_editing": True,       # Modification de modèles
            "template_deletion": True,      # Suppression de modèles
            "export_pdf": False,           # Export PDF (libre)
            "create_document": False       # Création de documents (libre)
        }
        
        # Utilisateur actif
        self.current_user = None
        self.session_start_time = None
        
        # Charger l'utilisateur actif au démarrage
        self._load_current_user()
        
        # Sécuriser tous les fichiers existants
        self.secure_files.secure_all_files()
    
    def _load_usage_count(self) -> int:
        """Charge le compteur d'utilisation"""
        try:
            data = self.secure_files.read_secure_file("usage_count.json")
            return data.get("count", 0)
        except Exception as e:
            logger.error(f"Erreur lors du chargement du compteur: {e}")
            return 0
    
    def _save_usage_count(self):
        """Sauvegarde le compteur d'utilisation"""
        try:
            self.secure_files.write_secure_file("usage_count.json", {"count": self.usage_count})
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du compteur: {e}")
    
    def increment_usage(self) -> Dict[str, Any]:
        """
        Incrémente le compteur d'utilisation
        
        Returns:
            Dict contenant les informations sur l'utilisation
        """
        self.usage_count += 1
        self._save_usage_count()
        
        remaining = max(0, self.max_uses - self.usage_count)
        should_register = self.usage_count >= self.max_uses
        
        return {
            "count": self.usage_count,
            "remaining": remaining,
            "should_register": should_register,
            "message": f"Il vous reste {remaining} utilisation{'s' if remaining > 1 else ''} avant de devoir vous inscrire."
        }
    
    def needs_registration(self, feature: str = None) -> Dict[str, Any]:
        """
        Vérifie si l'inscription est nécessaire
        
        Args:
            feature: Nom de la fonctionnalité à vérifier (optionnel)
        
        Returns:
            Dict contenant les informations sur la nécessité de s'inscrire
        """
        # Si une fonctionnalité spécifique est vérifiée
        if feature and self.is_protected_feature(feature):
            return {
                "needs_registration": True,
                "reason": "protected_feature",
                "message": "Cette fonctionnalité nécessite un compte utilisateur."
            }
        
        # Vérification basée sur le nombre d'utilisations
        if self.usage_count >= self.max_uses:
            return {
                "needs_registration": True,
                "reason": "usage_limit",
                "message": "Vous avez atteint le nombre maximum d'utilisations. Veuillez vous inscrire pour continuer."
            }
        
        return {
            "needs_registration": False,
            "reason": None,
            "message": None
        }
    
    def is_protected_feature(self, feature: str) -> bool:
        """
        Vérifie si une fonctionnalité nécessite une inscription
        
        Args:
            feature: Nom de la fonctionnalité à vérifier
        
        Returns:
            bool: True si la fonctionnalité nécessite une inscription, False sinon
        """
        return self.protected_features.get(feature, False)
    
    def reset_usage(self):
        """Réinitialise le compteur d'utilisation"""
        self.usage_count = 0
        self._save_usage_count()
    
    def is_user_registered(self) -> bool:
        """
        Vérifie si un utilisateur est inscrit
        
        Returns:
            bool: True si au moins un utilisateur est inscrit, False sinon
        """
        try:
            # D'abord, vérifier s'il y a un utilisateur actif
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if os.path.exists(current_user_file):
                try:
                    with open(current_user_file, 'r', encoding='utf-8', errors='ignore') as f:
                        current_user = json.load(f)
                        if current_user.get("email"):
                            # Vérifier que cet utilisateur existe toujours
                            users_file = os.path.join(self.data_dir, "users.json")
                            if os.path.exists(users_file):
                                with open(users_file, 'r', encoding='utf-8', errors='ignore') as f2:
                                    users = json.load(f2)
                                    if current_user.get("email") in users:
                                        return True
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de l'utilisateur actif: {e}")
            
            # Sinon, vérifier s'il y a des utilisateurs enregistrés
            users_file = os.path.join(self.data_dir, "users.json")
            if os.path.exists(users_file):
                try:
                    with open(users_file, 'r', encoding='utf-8', errors='ignore') as f:
                        users = json.load(f)
                        return bool(users)  # True si le dictionnaire n'est pas vide
                except json.JSONDecodeError:
                    logger.error("Fichier users.json corrompu, création d'un nouveau fichier")
                    with open(users_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
                    return False
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des utilisateurs: {e}")
            return False

    def get_user_data(self) -> Dict[str, Any]:
        """
        Récupère les données de l'utilisateur actuellement connecté
        
        Returns:
            Dict: Données de l'utilisateur ou un dictionnaire vide si aucun utilisateur n'est connecté
        """
        try:
            # Vérifier s'il y a un utilisateur actif
            current_user = self.secure_files.read_secure_file("current_user.json")
            if current_user and current_user.get("email"):
                # Récupérer les données complètes de cet utilisateur
                users = self.secure_files.read_secure_file("users.json")
                if users and current_user.get("email") in users:
                    user_data = users[current_user.get("email")]
                    user_data["email"] = current_user.get("email")
                    return user_data
            
            return {}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données utilisateur: {e}")
            return {}
    
    def set_current_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Définit l'utilisateur actuellement connecté
        
        Args:
            user_data: Données de l'utilisateur
            
        Returns:
            bool: True si l'opération a réussi
        """
        try:
            if not user_data.get("email"):
                logger.error("Email manquant dans les données utilisateur")
                return False
            
            # Sauvegarder l'utilisateur actif
            current_user = {
                "email": user_data["email"],
                "last_login": datetime.now().isoformat()
            }
            
            return self.secure_files.write_secure_file("current_user.json", current_user)
        except Exception as e:
            logger.error(f"Erreur lors de la définition de l'utilisateur actif: {e}")
            return False
    
    def clear_current_user(self) -> bool:
        """
        Supprime l'utilisateur actuellement connecté
        
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if os.path.exists(current_user_file):
                os.remove(current_user_file)
                logger.info("Utilisateur actif supprimé")
                return True
            return True  # Aucun utilisateur à supprimer
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'utilisateur actif: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authentifie un utilisateur avec son email et son mot de passe
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe de l'utilisateur
            
        Returns:
            Dict: Données de l'utilisateur si l'authentification réussit, sinon un dictionnaire vide
        """
        try:
            # Vérifier que l'email et le mot de passe sont fournis
            if not email or not password:
                logger.error("Email ou mot de passe manquant")
                return {}
                
            # Récupérer les utilisateurs
            users_file = os.path.join(self.data_dir, "users.json")
            if not os.path.exists(users_file):
                logger.error("Fichier utilisateurs non trouvé")
                return {}
                
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
                
            # Vérifier si l'utilisateur existe
            if email not in users:
                logger.warning(f"Utilisateur {email} non trouvé")
                return {}
                
            # Vérifier le mot de passe
            user_data = users[email]
            stored_password = user_data.get("password", "")
            
            # Convertir le mot de passe stocké en bytes
            stored_password_bytes = stored_password.encode()
            
            # Vérifier le mot de passe avec bcrypt
            from utils.security import verify_password
            if not verify_password(password, stored_password_bytes):
                logger.warning(f"Mot de passe incorrect pour {email}")
                return {}
                
            # Authentification réussie
            logger.info(f"Authentification réussie pour {email}")
            return user_data
                
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return {}

    def save_user_data(self, user_data: Dict[str, Any]) -> bool:
        """
        Enregistre les données de l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à enregistrer
            
        Returns:
            bool: True si l'opération a réussi
        """
        try:
            if not user_data.get("email"):
                logger.error("Email manquant dans les données utilisateur")
                return False
            
            email = user_data["email"]
            users = self.secure_files.read_secure_file("users.json") or {}
            
            # Mettre à jour les données utilisateur
            users[email] = {k: v for k, v in user_data.items() if k != "email"}
            
            # Sauvegarder les modifications
            if self.secure_files.write_secure_file("users.json", users):
                logger.info(f"Données utilisateur sauvegardées pour {email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données utilisateur: {e}")
            return False
    
    # --- Nouvelles méthodes pour compléter l'API ---
    
    def has_active_user(self) -> bool:
        """
        Vérifie si un utilisateur est actuellement connecté ou a une session "Rester connecté" active
        
        Returns:
            bool: True si un utilisateur est connecté, False sinon
        """
        try:
            # 1. Vérifier si l'attribut current_user est défini
            if self.current_user:
                return True
            
            # 2. Vérifier s'il existe un utilisateur actif dans le fichier current_user.json
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if os.path.exists(current_user_file):
                try:
                    with open(current_user_file, 'r', encoding='utf-8', errors='ignore') as f:
                        current_user = json.load(f)
                        email = current_user.get("email")
                        if email:
                            # Vérifier si cet utilisateur existe toujours
                            users_file = os.path.join(self.data_dir, "users.json")
                            if os.path.exists(users_file):
                                with open(users_file, 'r', encoding='utf-8', errors='ignore') as f2:
                                    users = json.load(f2)
                                    if email in users:
                                        # Utilisateur trouvé - mettre à jour l'état interne
                                        self.current_user = email
                                        return True
                except Exception as e:
                    logger.error(f"Erreur lors de la vérification de l'utilisateur actif: {e}")
            
            # 3. Vérifier s'il existe une session "Rester connecté" valide
            session_data = self.check_remembered_session()
            if session_data and session_data.get("email"):
                # Une session valide a été trouvée et l'utilisateur a été restauré
                return True
            
            # Aucun utilisateur actif trouvé
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'utilisateur actif: {e}")
            return False
    
    def get_active_user(self) -> str:
        """
        Récupère l'email de l'utilisateur actuellement connecté
        
        Returns:
            str: Email de l'utilisateur ou chaîne vide si aucun utilisateur n'est connecté
        """
        try:
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if not os.path.exists(current_user_file):
                return ""
                
            with open(current_user_file, 'r', encoding='utf-8', errors='ignore') as f:
                current_user = json.load(f)
                return current_user.get("email", "")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur actif: {e}")
            return ""
    
    def user_exists(self, email: str) -> bool:
        """
        Vérifie si un utilisateur existe
        
        Args:
            email: Email de l'utilisateur à vérifier
            
        Returns:
            bool: True si l'utilisateur existe, False sinon
        """
        try:
            if not email:
                return False
                
            users_file = os.path.join(self.data_dir, "users.json")
            if not os.path.exists(users_file):
                return False
                
            with open(users_file, 'r', encoding='utf-8', errors='ignore') as f:
                users = json.load(f)
                return email in users
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'existence de l'utilisateur: {e}")
            return False
    
    def register_user(self, email: str, password: str, user_data: Dict[str, Any]) -> bool:
        """
        Enregistre un nouvel utilisateur
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            user_data: Données supplémentaires de l'utilisateur
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        try:
            # Vérifier que l'email et le mot de passe sont fournis
            if not email or not password:
                logger.error("Email ou mot de passe manquant")
                return False
                
            # Vérifier si l'utilisateur existe déjà
            if self.user_exists(email):
                logger.warning(f"L'utilisateur {email} existe déjà")
                return False
                
            # Valider le mot de passe
            from utils.security import validate_password
            is_valid, message = validate_password(password)
            if not is_valid:
                logger.error(f"Mot de passe invalide: {message}")
                return False
                
            # Hacher le mot de passe avec bcrypt
            from utils.security import hash_password
            hashed_password, salt = hash_password(password)
            
            # Préparer les données utilisateur
            full_user_data = {
                "password": hashed_password.decode(),  # Convertir bytes en str pour JSON
                "salt": salt.decode(),  # Convertir bytes en str pour JSON
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            
            # Ajouter les données supplémentaires
            for key, value in user_data.items():
                if key not in full_user_data:
                    full_user_data[key] = value
            
            # Enregistrer l'utilisateur
            users_file = os.path.join(self.data_dir, "users.json")
            if os.path.exists(users_file):
                try:
                    with open(users_file, 'r', encoding='utf-8', errors='ignore') as f:
                        users = json.load(f)
                except json.JSONDecodeError:
                    # Fichier corrompu, créer un nouveau dictionnaire vide
                    users = {}
            else:
                users = {}
                
            # Ajouter l'utilisateur
            users[email] = full_user_data
            
            # Sauvegarder les modifications
            try:
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users, f, indent=4, ensure_ascii=False)
                logger.info(f"Utilisateur {email} enregistré avec succès")
                return True
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde de l'utilisateur: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'utilisateur: {e}")
            return False
    
    def get_user_info(self, email: str) -> Dict[str, Any]:
        """
        Récupère les informations d'un utilisateur
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            Dict: Informations de l'utilisateur ou dictionnaire vide si l'utilisateur n'existe pas
        """
        try:
            if not email:
                return {}
                
            users_file = os.path.join(self.data_dir, "users.json")
            if not os.path.exists(users_file):
                return {}
                
            with open(users_file, 'r', encoding='utf-8', errors='ignore') as f:
                users = json.load(f)
                if email in users:
                    user_info = users[email].copy()
                    # Ne pas renvoyer le mot de passe
                    if "password" in user_info:
                        del user_info["password"]
                    return user_info
                return {}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations utilisateur: {e}")
            return {}
    
    def logout(self) -> bool:
        """
        Déconnecte l'utilisateur actuel
        
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            # Enregistrer la session actuelle avant de se déconnecter
            if self.session_start_time and self.current_user:
                session_duration = time.time() - self.session_start_time
                self._record_session(session_duration)
                logger.info(f"Session enregistrée: {session_duration:.2f} secondes")
            
            # Récupérer l'email actuel pour la suppression du "Rester connecté"
            current_email = self.current_user
            
            # Réinitialiser les variables internes
            self.current_user = None
            self.session_start_time = 0
            
            # Supprimer le fichier d'utilisateur actuel
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if os.path.exists(current_user_file):
                try:
                    os.remove(current_user_file)
                    logger.info("Fichier utilisateur actif supprimé")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression du fichier utilisateur: {e}")
            
            # Supprimer le fichier de session "Rester connecté"
            session_file = os.path.join(self.data_dir, "session.json")
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                    logger.info("Fichier de session 'Rester connecté' supprimé")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression du fichier de session: {e}")
            
            # Désactiver explicitement l'option "Rester connecté" dans les données utilisateur
            if current_email:
                # Récupérer le fichier des utilisateurs
                users_file = os.path.join(self.data_dir, "users.json")
                if os.path.exists(users_file):
                    try:
                        # Lire les données utilisateur
                        with open(users_file, 'r', encoding='utf-8') as f:
                            users = json.load(f)
                        
                        # Désactiver l'option si l'utilisateur existe
                        if current_email in users:
                            if "settings" not in users[current_email]:
                                users[current_email]["settings"] = {}
                            
                            # Désactiver explicitement
                            users[current_email]["settings"]["remember_me"] = False
                            
                            # Sauvegarder les modifications
                            with open(users_file, 'w', encoding='utf-8') as f:
                                json.dump(users, f, indent=4)
                            
                            logger.info(f"Option 'Rester connecté' désactivée pour {current_email}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la désactivation de l'option 'Rester connecté': {e}")
                
                logger.info(f"Utilisateur {current_email} déconnecté avec succès")
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return False
    
    def login(self, email, password, remember_me=False):
        """
        Connecte un utilisateur avec son email et son mot de passe
        
        Args:
            email (str): Email de l'utilisateur
            password (str): Mot de passe en clair
            remember_me (bool): Définit si l'utilisateur reste connecté
            
        Returns:
            bool: True si l'authentification a réussi, False sinon
        """
        try:
            # Vérifier si l'email et le mot de passe sont valides
            if not email or not password:
                logger.warning("Email ou mot de passe vide")
                return False
            
            # Hasher le mot de passe
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Vérifier si l'utilisateur existe et si le mot de passe correspond
            user_data = self.authenticate_user(email, password_hash)
            
            if user_data:
                # Mise à jour de l'utilisateur actuel
                self.current_user = email
                self.session_start_time = time.time()
                self._save_current_user()
                
                # Définir explicitement la préférence "Rester connecté" selon le choix de l'utilisateur
                # Forcer l'appel à set_remember_me, même si remember_me est False
                remember_result = self.set_remember_me(email, bool(remember_me))
                
                if not remember_result:
                    logger.warning(f"Erreur lors de la définition de 'Rester connecté' pour {email}")
                    # Continuer malgré l'erreur, l'authentification a réussi
                
                logger.info(f"Utilisateur {email} connecté avec succès (remember_me={remember_me})")
                return True
            else:
                logger.warning(f"Échec d'authentification pour l'utilisateur {email}")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            return False

    def _load_current_user(self):
        """Charge l'utilisateur actif depuis le fichier current_user.json"""
        try:
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if os.path.exists(current_user_file):
                with open(current_user_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                    if content:
                        current_user = json.loads(content)
                        if current_user.get("email"):
                            self.current_user = current_user.get("email")
                            self.session_start_time = time.time()
                            logger.info(f"Utilisateur actif chargé: {self.current_user}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'utilisateur actif: {e}")
    
    def _save_current_user(self):
        """Sauvegarde l'utilisateur actuel dans le fichier current_user.json"""
        try:
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if self.current_user:
                current_user = {
                    "email": self.current_user,
                    "last_login": datetime.now().isoformat()
                }
                with open(current_user_file, 'w', encoding='utf-8') as f:
                    json.dump(current_user, f, indent=4)
                logger.info(f"Utilisateur actif sauvegardé: {self.current_user}")
            else:
                # Supprimer le fichier s'il existe
                if os.path.exists(current_user_file):
                    os.remove(current_user_file)
                    logger.info("Fichier utilisateur actif supprimé")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'utilisateur actif: {e}")
            
    def _record_session(self, duration):
        """
        Enregistre la durée d'une session pour l'utilisateur actuel
        
        Args:
            duration (float): Durée de la session en secondes
        """
        if not self.current_user:
            return
            
        try:
            # Récupérer les données de l'utilisateur
            users_file = os.path.join(self.data_dir, "users.json")
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
                
                if self.current_user in users:
                    # Ajouter la session aux statistiques de l'utilisateur
                    if "sessions" not in users[self.current_user]:
                        users[self.current_user]["sessions"] = []
                    
                    users[self.current_user]["sessions"].append({
                        "date": datetime.now().isoformat(),
                        "duration": duration
                    })
                    
                    # Mettre à jour le temps total d'utilisation
                    if "total_usage_time" not in users[self.current_user]:
                        users[self.current_user]["total_usage_time"] = 0
                    
                    users[self.current_user]["total_usage_time"] += duration
                    
                    # Sauvegarder les modifications
                    with open(users_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, indent=4)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la session: {e}")

    def set_remember_me(self, email: str, remember: bool) -> bool:
        """
        Définit la préférence "Rester connecté" pour un utilisateur
        
        Args:
            email: Email de l'utilisateur
            remember: True pour activer "Rester connecté", False sinon
            
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            if not email:
                logger.error("Email non fourni pour set_remember_me")
                return False
                
            # Vérifier si l'utilisateur existe
            users_file = os.path.join(self.data_dir, "users.json")
            if not os.path.exists(users_file):
                logger.error("Fichier utilisateurs non trouvé")
                return False
            
            # Lire le fichier utilisateurs
            try:    
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier utilisateurs: {e}")
                return False
                
            # Vérifier si l'utilisateur existe
            if email not in users:
                logger.warning(f"Utilisateur {email} non trouvé pour set_remember_me")
                return False
                
            # Mettre à jour la préférence
            if "settings" not in users[email]:
                users[email]["settings"] = {}
            
            # Définir explicitement la valeur
            users[email]["settings"]["remember_me"] = bool(remember)
            
            # Sauvegarder les modifications
            try:
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users, f, indent=4)
                logger.info(f"Préférence 'remember_me' mise à jour: {remember}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde des préférences: {e}")
                return False
                
            # Gérer le fichier de session en fonction de la valeur remember_me
            session_file = os.path.join(self.data_dir, "session.json")
            
            if remember:
                # Créer ou mettre à jour le fichier de session
                try:
                    session_data = {
                        "email": email,
                        "timestamp": datetime.now().isoformat(),
                        "remember_me": True
                    }
                    
                    with open(session_file, 'w', encoding='utf-8') as f:
                        json.dump(session_data, f, indent=4)
                    logger.info(f"Session persistante créée pour {email}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création du fichier de session: {e}")
                    return False
            else:
                # Supprimer le fichier de session s'il existe
                if os.path.exists(session_file):
                    try:
                        os.remove(session_file)
                        logger.info("Fichier de session supprimé")
                    except Exception as e:
                        logger.error(f"Erreur lors de la suppression du fichier de session: {e}")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la préférence 'Rester connecté': {e}")
            return False
            
    def check_remembered_session(self) -> Dict[str, Any]:
        """
        Vérifie s'il existe une session "Rester connecté" valide
        
        Returns:
            Dict: Données de l'utilisateur si une session valide existe, sinon un dictionnaire vide
        """
        try:
            # Vérifier si le fichier de session existe
            session_file = os.path.join(self.data_dir, "session.json")
            if not os.path.exists(session_file):
                logger.debug("Aucun fichier de session trouvé")
                return {}
                
            # Lire le fichier de session
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Format JSON invalide dans le fichier de session: {e}")
                # Supprimer le fichier corrompu
                os.remove(session_file)
                return {}
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier de session: {e}")
                return {}
                
            # Vérifier si la session contient les informations nécessaires
            if "email" not in session or "remember_me" not in session:
                logger.warning("Fichier de session incomplet")
                os.remove(session_file)
                return {}
                
            # Vérifier explicitement si remember_me est True
            if not session.get("remember_me") == True:  # Comparaison stricte
                logger.info("Option 'Rester connecté' non activée dans le fichier de session")
                os.remove(session_file)
                return {}
                
            email = session.get("email")
            if not email:
                logger.warning("Email manquant dans le fichier de session")
                os.remove(session_file)
                return {}
                
            # Vérifier si l'utilisateur existe toujours
            users_file = os.path.join(self.data_dir, "users.json")
            if not os.path.exists(users_file):
                logger.warning("Fichier utilisateurs non trouvé")
                os.remove(session_file)
                return {}
            
            try:    
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier utilisateurs: {e}")
                return {}
                
            if email not in users:
                # Supprimer le fichier de session si l'utilisateur n'existe plus
                logger.warning(f"Utilisateur {email} du fichier de session non trouvé")
                os.remove(session_file)
                return {}
                
            # Vérifier si l'option "Rester connecté" est toujours activée pour cet utilisateur
            user_settings = users[email].get("settings", {})
            if not user_settings.get("remember_me") == True:  # Comparaison stricte
                # Supprimer le fichier de session si l'option n'est plus activée
                logger.info(f"Option 'Rester connecté' désactivée pour {email} dans les données utilisateur")
                os.remove(session_file)
                return {}
                
            # Session valide, récupérer les données de l'utilisateur
            user_data = users[email].copy()
            user_data["email"] = email
            
            # Mettre à jour la dernière connexion
            user_data["last_login"] = datetime.now().isoformat()
            users[email]["last_login"] = user_data["last_login"]
            
            # Sauvegarder la mise à jour
            try:
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users, f, indent=4)
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour des données utilisateur: {e}")
                # Continuer malgré l'erreur, nous avons déjà les données
            
            # Enregistrer l'utilisateur comme utilisateur actif
            self.set_current_user(user_data)
            
            logger.info(f"Session 'Rester connecté' restaurée pour {email}")
            return user_data
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la session 'Rester connecté': {e}")
            return {}

    def get_last_email(self):
        """
        Récupère le dernier email utilisé pour se connecter
        
        Returns:
            str: Dernier email utilisé ou chaîne vide si aucun
        """
        try:
            # Vérifier d'abord l'utilisateur actif
            if self.current_user:
                return self.current_user
            
            # Vérifier le fichier de session pour un utilisateur "Rester connecté"
            session_file = os.path.join(self.data_dir, "session.json")
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session = json.load(f)
                        if session.get("email"):
                            return session.get("email")
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture du fichier de session: {e}")
            
            # Vérifier le fichier utilisateur actif
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            if os.path.exists(current_user_file):
                try:
                    with open(current_user_file, 'r', encoding='utf-8') as f:
                        current_user = json.load(f)
                        if current_user.get("email"):
                            return current_user.get("email")
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de l'utilisateur actif: {e}")
            
            return ""
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du dernier email: {e}")
            return ""

    def set_active_user(self, email: str, user_data: Dict[str, Any]) -> bool:
        """
        Définit l'utilisateur actif et ses données
        
        Args:
            email: Email de l'utilisateur
            user_data: Données de l'utilisateur
            
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            if not email:
                logger.error("Email manquant pour définir l'utilisateur actif")
                return False
            
            # Mettre à jour les données utilisateur
            users_file = os.path.join(self.data_dir, "users.json")
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
                    
                # Mettre à jour ou créer l'utilisateur
                if email not in users:
                    users[email] = {}
                
                # Mettre à jour les données
                for key, value in user_data.items():
                    if key != 'email':  # Ne pas stocker l'email dans les données
                        users[email][key] = value
                
                # Sauvegarder les modifications
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users, f, indent=4)
            else:
                # Créer le fichier s'il n'existe pas
                users = {email: {k: v for k, v in user_data.items() if k != 'email'}}
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users, f, indent=4)
            
            # Définir l'utilisateur comme actif
            self.current_user = email
            self.session_start_time = time.time()
            
            # Sauvegarder dans current_user.json
            current_user_file = os.path.join(self.data_dir, "current_user.json")
            current_user_data = {
                "email": email,
                "last_login": datetime.now().isoformat()
            }
            with open(current_user_file, 'w', encoding='utf-8') as f:
                json.dump(current_user_data, f, indent=4)
            
            logger.info(f"Utilisateur actif défini: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la définition de l'utilisateur actif: {e}")
            return False 
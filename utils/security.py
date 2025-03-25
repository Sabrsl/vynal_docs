#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilitaires de sécurité pour l'application Vynal Docs Automator
"""

import os
import logging
import bcrypt
import secrets
import re
import json
from typing import Tuple, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger("VynalDocsAutomator.Security")

# Configuration de la sécurité
PASSWORD_MIN_LENGTH = 8
PASSWORD_SPECIAL_CHARS = "!@#$%^&*(),.?\":{}|<>"
CSRF_TOKEN_LENGTH = 32
CSRF_TOKEN_EXPIRY = timedelta(hours=1)

def hash_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hache un mot de passe en utilisant bcrypt
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Tuple[bytes, bytes]: (hachage, sel)
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed, salt

def verify_password(password: str, hashed: bytes) -> bool:
    """
    Vérifie un mot de passe avec son hachage bcrypt
    
    Args:
        password: Mot de passe en clair
        hashed: Hachage bcrypt à vérifier
        
    Returns:
        bool: True si le mot de passe correspond
    """
    try:
        return bcrypt.checkpw(password.encode(), hashed)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
        return False

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Valide la complexité d'un mot de passe
    
    Args:
        password: Mot de passe à valider
        
    Returns:
        Tuple[bool, str]: (True si valide, message d'erreur si invalide)
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Le mot de passe doit contenir au moins {PASSWORD_MIN_LENGTH} caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    if not any(c in PASSWORD_SPECIAL_CHARS for c in password):
        return False, f"Le mot de passe doit contenir au moins un caractère spécial parmi {PASSWORD_SPECIAL_CHARS}"
    
    return True, ""

def generate_csrf_token() -> Tuple[str, datetime]:
    """
    Génère un token CSRF
    
    Returns:
        Tuple[str, datetime]: (token, date d'expiration)
    """
    token = secrets.token_urlsafe(CSRF_TOKEN_LENGTH)
    expiry = datetime.now() + CSRF_TOKEN_EXPIRY
    return token, expiry

def verify_csrf_token(token: str, stored_token: str, expiry: datetime) -> bool:
    """
    Vérifie un token CSRF
    
    Args:
        token: Token à vérifier
        stored_token: Token stocké
        expiry: Date d'expiration
        
    Returns:
        bool: True si le token est valide et non expiré
    """
    if not token or not stored_token:
        return False
    
    if datetime.now() > expiry:
        return False
    
    return secrets.compare_digest(token, stored_token)

class CSRFProtection:
    """Gestionnaire de protection CSRF"""
    
    def __init__(self):
        self._tokens = {}  # {form_id: (token, expiry)}
    
    def generate_token(self, form_id: str) -> str:
        """
        Génère un token CSRF pour un formulaire
        
        Args:
            form_id: Identifiant du formulaire
            
        Returns:
            str: Token CSRF
        """
        token, expiry = generate_csrf_token()
        self._tokens[form_id] = (token, expiry)
        return token
    
    def verify_token(self, form_id: str, token: str) -> bool:
        """
        Vérifie un token CSRF
        
        Args:
            form_id: Identifiant du formulaire
            token: Token à vérifier
            
        Returns:
            bool: True si le token est valide
        """
        if form_id not in self._tokens:
            return False
        
        stored_token, expiry = self._tokens[form_id]
        is_valid = verify_csrf_token(token, stored_token, expiry)
        
        if is_valid:
            # Supprimer le token après utilisation
            del self._tokens[form_id]
        
        return is_valid
    
    def clear_expired_tokens(self) -> None:
        """Supprime les tokens expirés"""
        now = datetime.now()
        expired = [form_id for form_id, (_, expiry) in self._tokens.items() if now > expiry]
        for form_id in expired:
            del self._tokens[form_id]

class SecureFileManager:
    """Gestionnaire de fichiers sensibles"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialise le gestionnaire de fichiers sensibles
        
        Args:
            data_dir: Répertoire des données
        """
        self.data_dir = data_dir
        self._ensure_secure_dir()
        
        # Liste des fichiers sensibles à protéger
        self.sensitive_files = {
            "users.json": "Données des utilisateurs",
            "current_user.json": "Session utilisateur actif",
            "session.json": "Données de session",
            "licenses.json": "Licences",
            ".key": "Clé de chiffrement"
        }
        
        # Initialiser le chiffrement
        self._init_encryption()
    
    def _ensure_secure_dir(self):
        """Crée et sécurise le répertoire des données"""
        try:
            # Créer le répertoire s'il n'existe pas
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Masquer le répertoire sous Windows
            if os.name == 'nt':  # Windows
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                ret = ctypes.windll.kernel32.SetFileAttributesW(self.data_dir, FILE_ATTRIBUTE_HIDDEN)
                if not ret:
                    logger.warning("Impossible de masquer le répertoire de données")
                
                # Définir les permissions Windows
                import win32security
                import ntsecuritycon as con
                
                # Obtenir le SID de l'utilisateur actuel
                user_sid = win32security.GetTokenInformation(
                    win32security.OpenProcessToken(win32security.GetCurrentProcess(), win32security.TOKEN_QUERY),
                    win32security.TokenUser
                )[0]
                
                # Créer une DACL qui donne le contrôle total à l'utilisateur actuel
                dacl = win32security.ACL()
                dacl.Initialize()
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    con.FILE_ALL_ACCESS,
                    user_sid
                )
                
                # Appliquer la DACL au répertoire
                security = win32security.SECURITY_DESCRIPTOR()
                security.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(
                    self.data_dir,
                    win32security.DACL_SECURITY_INFORMATION,
                    security
                )
            else:
                # Définir les permissions sous Unix
                os.chmod(self.data_dir, 0o700)  # rwx------ (propriétaire uniquement)
            
            logger.info("Répertoire de données sécurisé")
        except Exception as e:
            logger.error(f"Erreur lors de la sécurisation du répertoire: {e}")
    
    def _init_encryption(self):
        """Initialise le chiffrement des fichiers"""
        try:
            from cryptography.fernet import Fernet
            
            key_file = os.path.join(self.data_dir, ".key")
            
            # Générer une nouvelle clé si elle n'existe pas
            if not os.path.exists(key_file):
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Masquer le fichier de clé
                self._hide_file(key_file)
            else:
                try:
                    # Lire la clé en mode binaire d'abord
                    with open(key_file, 'rb') as f:
                        key = f.read().strip()
                    
                    # Vérifier si c'est une clé Fernet valide
                    try:
                        Fernet(key)
                        logger.debug("Clé Fernet valide lue avec succès")
                    except Exception:
                        # Si ce n'est pas une clé Fernet valide, réessayer en UTF-8
                        try:
                            key_str = key.decode('utf-8').strip()
                            
                            # Vérifier si c'est du JSON
                            try:
                                import json
                                key_data = json.loads(key_str)
                                # Extraire la clé du JSON
                                if isinstance(key_data, dict) and "key" in key_data:
                                    key = key_data["key"].encode('utf-8')
                                else:
                                    # JSON mais pas de clé
                                    raise ValueError("Format JSON sans attribut 'key'")
                            except json.JSONDecodeError:
                                # Pas du JSON, mais peut-être une clé en texte
                                if '=' in key_str and len(key_str) >= 32:
                                    # Semble être une clé base64
                                    key = key_str.encode('utf-8')
                                else:
                                    # Format inconnu
                                    raise ValueError("Format de clé inconnu")
                            
                            # Vérifier que la clé est valide
                            Fernet(key)
                        except Exception as str_err:
                            # Échec de la lecture en UTF-8 ou clé invalide
                            logger.warning(f"Échec de la lecture de la clé comme texte: {str_err}")
                            # Créer une nouvelle clé
                            key = Fernet.generate_key()
                            with open(key_file, 'wb') as f:
                                f.write(key)
                            logger.info("Nouvelle clé générée")
                except Exception as e:
                    # Échec de la lecture de la clé
                    logger.error(f"Erreur lors de la lecture de la clé: {e}")
                    # Créer une nouvelle clé en cas d'erreur
                    key = Fernet.generate_key()
                    with open(key_file, 'wb') as f:
                        f.write(key)
                    logger.info("Nouvelle clé générée suite à une erreur")
            
            self.cipher = Fernet(key)
            logger.info("Chiffrement initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du chiffrement: {e}")
            self.cipher = None
    
    def _hide_file(self, filepath: str):
        """
        Masque un fichier
        
        Args:
            filepath: Chemin du fichier à masquer
        """
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                ret = ctypes.windll.kernel32.SetFileAttributesW(filepath, FILE_ATTRIBUTE_HIDDEN)
                if not ret:
                    logger.warning(f"Impossible de masquer le fichier: {filepath}")
            else:
                # Renommer le fichier pour le masquer sous Unix
                dirname = os.path.dirname(filepath)
                basename = os.path.basename(filepath)
                if not basename.startswith('.'):
                    new_path = os.path.join(dirname, f".{basename}")
                    os.rename(filepath, new_path)
                    filepath = new_path
                
                # Définir les permissions
                os.chmod(filepath, 0o600)  # rw------- (propriétaire uniquement)
            
            logger.debug(f"Fichier masqué: {filepath}")
        except Exception as e:
            logger.error(f"Erreur lors du masquage du fichier {filepath}: {e}")
    
    def read_secure_file(self, filename: str) -> Dict[str, Any]:
        """
        Lit un fichier sécurisé
        
        Args:
            filename: Nom du fichier à lire
            
        Returns:
            Dict: Contenu du fichier déchiffré
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                return {}
            
            # Essayer d'abord de lire en mode binaire (fichier chiffré)
            try:
                with open(filepath, 'rb') as f:
                    encrypted_data = f.read()
                
                if self.cipher and encrypted_data:
                    # Déchiffrer les données
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    return json.loads(decrypted_data)
            except Exception as e:
                logger.warning(f"Échec de la lecture chiffrée de {filename}: {e}")
            
            # Fallback : essayer de lire en mode texte (fichier non chiffré)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Si le fichier n'est pas un JSON valide, essayer de lire la sauvegarde
                backup_path = f"{filepath}.bak"
                if os.path.exists(backup_path):
                    try:
                        with open(backup_path, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception as e:
                        logger.error(f"Échec de la lecture de la sauvegarde de {filename}: {e}")
                
                # Si tout échoue, retourner un dictionnaire vide
                return {}
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier {filename}: {e}")
                return {}
                
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier {filename}: {e}")
            return {}
    
    def write_secure_file(self, filename: str, data: Dict[str, Any]) -> bool:
        """
        Écrit des données dans un fichier sécurisé
        
        Args:
            filename: Nom du fichier
            data: Données à écrire
            
        Returns:
            bool: True si l'écriture a réussi
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            backup_path = f"{filepath}.bak"
            
            # Créer une copie de sauvegarde si le fichier existe
            if os.path.exists(filepath):
                try:
                    import shutil
                    shutil.copy2(filepath, backup_path)
                    self._hide_file(backup_path)
                except Exception as e:
                    logger.warning(f"Impossible de créer la sauvegarde de {filename}: {e}")
            
            # Chiffrer et écrire les données
            json_data = json.dumps(data, indent=4)
            if self.cipher:
                encrypted_data = self.cipher.encrypt(json_data.encode())
                # Écrire d'abord dans un fichier temporaire
                temp_path = f"{filepath}.tmp"
                with open(temp_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Renommer le fichier temporaire en fichier final
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    os.rename(temp_path, filepath)
                except Exception as e:
                    logger.error(f"Erreur lors du remplacement du fichier {filename}: {e}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    # Restaurer la sauvegarde si elle existe
                    if os.path.exists(backup_path):
                        shutil.copy2(backup_path, filepath)
                    return False
            else:
                # Fallback en cas d'erreur de chiffrement
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_data)
            
            # Masquer le fichier
            self._hide_file(filepath)
            
            # Supprimer la sauvegarde si tout s'est bien passé
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except Exception as e:
                    logger.warning(f"Impossible de supprimer la sauvegarde de {filename}: {e}")
            
            logger.info(f"Fichier {filename} écrit et sécurisé")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du fichier {filename}: {e}")
            return False
    
    def secure_all_files(self):
        """Sécurise tous les fichiers sensibles existants"""
        try:
            for filename in self.sensitive_files:
                # Ignorer le fichier .key qui a un format spécial
                if filename == ".key":
                    logger.info("Fichier .key ignoré (format spécial)")
                    continue
                    
                filepath = os.path.join(self.data_dir, filename)
                if os.path.exists(filepath):
                    # Lire le contenu actuel
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Réécrire le fichier de manière sécurisée
                        self.write_secure_file(filename, data)
                        logger.info(f"Fichier {filename} sécurisé")
                    except Exception as e:
                        logger.error(f"Erreur lors de la sécurisation de {filename}: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de la sécurisation des fichiers: {e}")
    
    def is_file_secure(self, filename: str) -> bool:
        """
        Vérifie si un fichier est correctement sécurisé
        
        Args:
            filename: Nom du fichier à vérifier
            
        Returns:
            bool: True si le fichier est sécurisé
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                return False
            
            # Vérifier si le fichier est masqué
            if os.name == 'nt':  # Windows
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                attributes = ctypes.windll.kernel32.GetFileAttributesW(filepath)
                if attributes == -1:  # Erreur
                    return False
                is_hidden = bool(attributes & FILE_ATTRIBUTE_HIDDEN)
            else:
                # Sous Unix, vérifier si le nom commence par un point
                is_hidden = os.path.basename(filepath).startswith('.')
                # Vérifier les permissions
                is_secure = (os.stat(filepath).st_mode & 0o777) <= 0o600
            
            return is_hidden if os.name == 'nt' else (is_hidden and is_secure)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la sécurité de {filename}: {e}")
            return False
    
    def reset_data_files(self):
        """
        Réinitialise les fichiers de données en cas de corruption
        """
        try:
            # Sauvegarder les fichiers existants
            backup_dir = os.path.join(self.data_dir, "backup")
            os.makedirs(backup_dir, exist_ok=True)
            
            for filename in self.sensitive_files:
                filepath = os.path.join(self.data_dir, filename)
                if os.path.exists(filepath):
                    try:
                        backup_path = os.path.join(backup_dir, f"{filename}.bak")
                        import shutil
                        shutil.copy2(filepath, backup_path)
                        logger.info(f"Sauvegarde de {filename} créée")
                    except Exception as e:
                        logger.error(f"Erreur lors de la sauvegarde de {filename}: {e}")
            
            # Réinitialiser les fichiers avec des données par défaut
            default_data = {
                "users.json": {"users": []},
                "current_user.json": {"user": None, "session": None},
                "session.json": {"sessions": []},
                "licenses.json": {"licenses": []}
            }
            
            for filename, data in default_data.items():
                try:
                    self.write_secure_file(filename, data)
                    logger.info(f"Fichier {filename} réinitialisé")
                except Exception as e:
                    logger.error(f"Erreur lors de la réinitialisation de {filename}: {e}")
            
            logger.info("Fichiers de données réinitialisés")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation des fichiers: {e}")
            return False
    
    def fix_file_permissions(self):
        """
        Vérifie et corrige les permissions des fichiers sensibles
        """
        try:
            for filename in self.sensitive_files:
                filepath = os.path.join(self.data_dir, filename)
                if os.path.exists(filepath):
                    try:
                        if os.name == 'nt':  # Windows
                            import win32security
                            import ntsecuritycon as con
                            
                            # Obtenir le SID de l'utilisateur actuel
                            user_sid = win32security.GetTokenInformation(
                                win32security.OpenProcessToken(win32security.GetCurrentProcess(), win32security.TOKEN_QUERY),
                                win32security.TokenUser
                            )[0]
                            
                            # Créer une DACL qui donne le contrôle total à l'utilisateur actuel
                            dacl = win32security.ACL()
                            dacl.Initialize()
                            dacl.AddAccessAllowedAce(
                                win32security.ACL_REVISION,
                                con.FILE_ALL_ACCESS,
                                user_sid
                            )
                            
                            # Appliquer la DACL au fichier
                            security = win32security.SECURITY_DESCRIPTOR()
                            security.SetSecurityDescriptorDacl(1, dacl, 0)
                            win32security.SetFileSecurity(
                                filepath,
                                win32security.DACL_SECURITY_INFORMATION,
                                security
                            )
                        else:
                            # Sous Unix, définir les permissions rw------- (600)
                            os.chmod(filepath, 0o600)
                        
                        # Masquer le fichier
                        self._hide_file(filepath)
                        logger.info(f"Permissions corrigées pour {filename}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la correction des permissions de {filename}: {e}")
            
            logger.info("Vérification des permissions terminée")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la correction des permissions: {e}")
            return False 
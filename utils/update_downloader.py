#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire de téléchargement des mises à jour depuis Google Drive
avec déchiffrement sécurisé
"""

import os
import json
import hashlib
import zipfile
import tempfile
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import b64encode, b64decode
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pickle

logger = logging.getLogger("VynalDocsAutomator.UpdateDownloader")

class UpdateDownloader:
    """Gestionnaire de téléchargement des mises à jour depuis Google Drive"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    ENCRYPTION_KEY_FILE = "data/.update_key"
    
    def __init__(self, credentials_path: str, folder_id: str, encryption_password: str):
        """
        Initialise le downloader de mises à jour
        
        Args:
            credentials_path: Chemin vers le fichier credentials.json de Google Drive
            folder_id: ID du dossier Google Drive contenant les mises à jour
            encryption_password: Mot de passe pour le déchiffrement des fichiers
        """
        self.credentials_path = credentials_path
        self.folder_id = folder_id
        self.encryption_key = self._setup_decryption(encryption_password)
        self.drive_service = self._init_drive_service()
        
        # Créer les répertoires nécessaires
        os.makedirs("data/updates", exist_ok=True)
        os.makedirs("data/backups", exist_ok=True)
    
    def _setup_decryption(self, password: str) -> bytes:
        """
        Configure le déchiffrement avec la clé
        
        Args:
            password: Mot de passe pour la clé
            
        Returns:
            bytes: Clé de déchiffrement
        """
        try:
            # Dériver la clé du mot de passe
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            return b64encode(kdf.derive(password.encode()))
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration du déchiffrement: {e}")
            raise ValueError("Impossible de configurer le déchiffrement")
    
    def _init_drive_service(self):
        """
        Initialise le service Google Drive
        
        Returns:
            Resource: Service Google Drive authentifié
        """
        try:
            creds = None
            token_path = "data/token.pickle"
            
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            return build('drive', 'v3', credentials=creds)
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à Google Drive: {e}")
            raise ValueError("Impossible de se connecter à Google Drive")
    
    def check_for_updates(self, current_version: str) -> Optional[Dict]:
        """
        Vérifie si des mises à jour sont disponibles
        
        Args:
            current_version: Version actuelle de l'application
            
        Returns:
            Dict: Informations sur la mise à jour disponible ou None
        """
        try:
            # Rechercher les mises à jour dans le dossier
            results = self.drive_service.files().list(
                q=f"'{self.folder_id}' in parents and trashed = false",
                orderBy="createdTime desc",
                pageSize=1,
                fields="files(id, name, description, size, createdTime, appProperties)",
                supportsAllDrives=True
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return None
            
            latest = files[0]
            latest_version = latest['appProperties']['version']
            
            # Vérifier si la version est plus récente
            if not self._is_newer_version(current_version, latest_version):
                return None
            
            return {
                'version': latest_version,
                'description': latest['description'],
                'size': latest['size'],
                'file_id': latest['id'],
                'checksum': latest['appProperties']['checksum'],
                'security_level': latest['appProperties']['security_level']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des mises à jour: {e}")
            return None
    
    def _is_newer_version(self, current: str, new: str) -> bool:
        """
        Vérifie si la nouvelle version est plus récente
        
        Args:
            current: Version actuelle
            new: Nouvelle version
            
        Returns:
            bool: True si la nouvelle version est plus récente
        """
        try:
            current_parts = [int(x) for x in current.split('.')]
            new_parts = [int(x) for x in new.split('.')]
            
            for i in range(max(len(current_parts), len(new_parts))):
                c = current_parts[i] if i < len(current_parts) else 0
                n = new_parts[i] if i < len(new_parts) else 0
                if n > c:
                    return True
                if n < c:
                    return False
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison des versions: {e}")
            return False
    
    def download_update(self, file_id: str, expected_checksum: str) -> Optional[str]:
        """
        Télécharge et déchiffre une mise à jour
        
        Args:
            file_id: ID du fichier sur Google Drive
            expected_checksum: Checksum attendu
            
        Returns:
            str: Chemin du fichier téléchargé et déchiffré ou None si échec
        """
        try:
            # Créer un fichier temporaire pour le téléchargement
            with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as tmp_file:
                try:
                    # Télécharger le fichier chiffré
                    request = self.drive_service.files().get_media(fileId=file_id)
                    downloader = MediaIoBaseDownload(tmp_file, request)
                    
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        if status:
                            logger.info(f"Téléchargement: {int(status.progress() * 100)}%")
                    
                    tmp_file.flush()
                    
                    # Vérifier le checksum
                    if not self._verify_checksum(tmp_file.name, expected_checksum):
                        raise ValueError("Checksum invalide")
                    
                    # Déchiffrer le fichier
                    decrypted_file = self._decrypt_file(tmp_file.name)
                    
                    # Déplacer vers le répertoire des mises à jour
                    update_path = os.path.join(
                        "data/updates",
                        f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    )
                    os.rename(decrypted_file, update_path)
                    
                    return update_path
                    
                finally:
                    # Nettoyer les fichiers temporaires
                    if os.path.exists(tmp_file.name):
                        os.unlink(tmp_file.name)
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la mise à jour: {e}")
            return None
    
    def _verify_checksum(self, filepath: str, expected: str) -> bool:
        """
        Vérifie le checksum d'un fichier
        
        Args:
            filepath: Chemin du fichier
            expected: Checksum attendu
            
        Returns:
            bool: True si le checksum est valide
        """
        try:
            calculated = self._calculate_file_hash(filepath)
            return calculated == expected
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du checksum: {e}")
            return False
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """
        Calcule le hash SHA-256 d'un fichier
        
        Args:
            filepath: Chemin du fichier
            
        Returns:
            str: Hash SHA-256 du fichier
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Erreur lors du calcul du hash: {e}")
            return ""
    
    def _decrypt_file(self, encrypted_file: str) -> str:
        """
        Déchiffre un fichier
        
        Args:
            encrypted_file: Chemin du fichier chiffré
            
        Returns:
            str: Chemin du fichier déchiffré
        """
        try:
            f = Fernet(self.encryption_key)
            
            # Lire le fichier chiffré
            with open(encrypted_file, 'rb') as file:
                encrypted_data = file.read()
            
            # Déchiffrer
            decrypted_data = f.decrypt(encrypted_data)
            
            # Sauvegarder dans un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(decrypted_data)
                return tmp_file.name
                
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement: {e}")
            raise
    
    def install_update(self, update_file: str) -> bool:
        """
        Installe une mise à jour
        
        Args:
            update_file: Chemin du fichier de mise à jour déchiffré
            
        Returns:
            bool: True si l'installation a réussi
        """
        try:
            # Créer une sauvegarde avant l'installation
            backup_path = self._create_backup()
            if not backup_path:
                raise ValueError("Impossible de créer la sauvegarde")
            
            # Extraire et vérifier le manifest
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                manifest_data = zip_ref.read('manifest.json')
                manifest = json.loads(manifest_data)
                
                # Vérifier la version minimale requise
                min_version = manifest['security']['min_app_version']
                if not self._check_version_compatibility(min_version):
                    raise ValueError(f"Version minimale requise: {min_version}")
                
                # Extraire les fichiers
                for file_info in manifest['files']:
                    file_path = file_info['path']
                    is_sensitive = file_info.get('sensitive', False)
                    
                    if is_sensitive:
                        # Déchiffrer et installer les fichiers sensibles
                        encrypted_path = file_path + '.enc'
                        if encrypted_path in zip_ref.namelist():
                            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                tmp_file.write(zip_ref.read(encrypted_path))
                                tmp_file.flush()
                                decrypted_path = self._decrypt_file(tmp_file.name)
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                os.rename(decrypted_path, file_path)
                    else:
                        # Installer les fichiers non sensibles
                        if file_path in zip_ref.namelist():
                            zip_ref.extract(file_path)
            
            logger.info("Mise à jour installée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'installation: {e}")
            # Restaurer la sauvegarde en cas d'erreur
            if 'backup_path' in locals():
                self._restore_backup(backup_path)
            return False
    
    def _create_backup(self) -> Optional[str]:
        """
        Crée une sauvegarde des fichiers actuels
        
        Returns:
            str: Chemin de la sauvegarde ou None si échec
        """
        try:
            backup_dir = os.path.join(
                "data/backups",
                f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(backup_dir)
            
            # Copier les fichiers importants
            important_dirs = ['app', 'utils', 'config']
            for dir_name in important_dirs:
                if os.path.exists(dir_name):
                    shutil.copytree(
                        dir_name,
                        os.path.join(backup_dir, dir_name),
                        dirs_exist_ok=True
                    )
            
            return backup_dir
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            return None
    
    def _restore_backup(self, backup_path: str) -> bool:
        """
        Restaure une sauvegarde
        
        Args:
            backup_path: Chemin de la sauvegarde
            
        Returns:
            bool: True si la restauration a réussi
        """
        try:
            # Restaurer chaque dossier
            for item in os.listdir(backup_path):
                src = os.path.join(backup_path, item)
                dst = item
                
                if os.path.isdir(src):
                    shutil.rmtree(dst, ignore_errors=True)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            logger.info("Sauvegarde restaurée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration: {e}")
            return False
    
    def _check_version_compatibility(self, min_version: str) -> bool:
        """
        Vérifie la compatibilité des versions
        
        Args:
            min_version: Version minimale requise
            
        Returns:
            bool: True si la version actuelle est compatible
        """
        try:
            # Lire la version actuelle depuis config.json
            with open('config.json', 'r') as f:
                config = json.load(f)
                current_version = config.get('version', '0.0.0')
            
            # Comparer les versions
            current_parts = [int(x) for x in current_version.split('.')]
            min_parts = [int(x) for x in min_version.split('.')]
            
            for i in range(max(len(current_parts), len(min_parts))):
                c = current_parts[i] if i < len(current_parts) else 0
                m = min_parts[i] if i < len(min_parts) else 0
                if c < m:
                    return False
                if c > m:
                    return True
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de compatibilité: {e}")
            return False
    
    def download_config(self) -> Optional[str]:
        """
        Télécharge le fichier de configuration depuis Google Drive.
        
        Returns:
            Optional[str]: Chemin du fichier de configuration téléchargé ou None en cas d'erreur
        """
        try:
            # Initialiser le service Google Drive
            service = self._init_drive_service()
            if not service:
                logger.error("Impossible d'initialiser le service Google Drive")
                return None
            
            # Rechercher le fichier de configuration dans le dossier
            query = f"'{self.folder_id}' in parents and name = 'app_config.json'"
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)'
            ).execute()
            
            files = results.get('files', [])
            if not files:
                logger.error("Fichier de configuration non trouvé sur Google Drive")
                return None
            
            # Trier par date de modification pour prendre le plus récent
            config_file = sorted(
                files,
                key=lambda x: x.get('modifiedTime', ''),
                reverse=True
            )[0]
            
            # Créer un fichier temporaire
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            temp_file_path = temp_file.name
            temp_file.close()
            
            # Télécharger le fichier
            request = service.files().get_media(fileId=config_file['id'])
            with open(temp_file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            # Déchiffrer le fichier si nécessaire
            if self.encryption_password:
                try:
                    decrypted_path = self._decrypt_file(temp_file_path)
                    os.unlink(temp_file_path)  # Supprimer le fichier chiffré
                    return decrypted_path
                except Exception as e:
                    logger.error(f"Erreur lors du déchiffrement du fichier de configuration: {e}")
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    return None
            
            return temp_file_path
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du fichier de configuration: {e}")
            return None 
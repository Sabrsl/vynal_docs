#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour l'upload des fichiers de configuration et des mises à jour sur Google Drive
"""

import os
import json
import hashlib
import zipfile
import tempfile
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import b64encode, b64decode
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import time

logger = logging.getLogger("VynalDocsAutomator.UpdateUploader")

class UpdateUploader:
    """Gestionnaire d'upload des fichiers sur Google Drive avec chiffrement"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_path: str, folder_id: str, encryption_password: str):
        """
        Initialise l'uploader
        
        Args:
            credentials_path: Chemin vers le fichier credentials.json
            folder_id: ID du dossier Google Drive
            encryption_password: Mot de passe pour le chiffrement
        """
        self.credentials_path = credentials_path
        self.folder_id = folder_id
        self.encryption_key = self._setup_encryption(encryption_password)
        self.drive_service = self._init_drive_service()
    
    def _setup_encryption(self, password: str) -> bytes:
        """
        Configure le chiffrement en dérivant une clé à partir du mot de passe
        
        Args:
            password: Mot de passe pour le chiffrement
            
        Returns:
            bytes: Clé de chiffrement dérivée
        """
        # Utiliser un sel constant pour avoir la même clé à chaque fois
        salt = b'vynal_docs_salt'
        
        # Configurer PBKDF2 pour dériver la clé
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        # Dériver la clé à partir du mot de passe
        key = b64encode(kdf.derive(password.encode()))
        return key
    
    def _init_drive_service(self):
        """Initialise le service Google Drive"""
        creds = None
        
        # Charger les credentials existants
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # Si pas de credentials valides
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Sauvegarder les credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # Construire le service
        service = build('drive', 'v3', credentials=creds)
        return service
    
    def _get_temp_path(self, suffix: str) -> str:
        """Génère un chemin de fichier temporaire unique"""
        timestamp = int(time.time() * 1000)
        return os.path.join(
            tempfile.gettempdir(),
            f'vynal_docs_temp_{timestamp}{suffix}'
        )
    
    def _encrypt_file(self, file_path: str) -> str:
        """
        Chiffre un fichier
        
        Args:
            file_path: Chemin du fichier à chiffrer
            
        Returns:
            str: Chemin du fichier chiffré
        """
        f = Fernet(self.encryption_key)
        
        # Lire le fichier
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # Chiffrer les données
        encrypted_data = f.encrypt(file_data)
        
        # Créer un fichier temporaire pour les données chiffrées
        encrypted_path = self._get_temp_path('.enc')
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        return encrypted_path
    
    def upload_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Téléverse le fichier de configuration sur Google Drive
        
        Args:
            config_data: Données de configuration à téléverser
            
        Returns:
            bool: True si le téléversement a réussi
        """
        temp_files = []
        try:
            # Créer un fichier temporaire pour la configuration
            temp_fd, temp_path = tempfile.mkstemp(suffix='.json', prefix='vynal_docs_temp_')
            temp_files.append(temp_path)
            
            # Écrire les données de configuration et fermer le descripteur de fichier
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Chiffrer le fichier
            encrypted_path = self._encrypt_file(temp_path)
            if encrypted_path:
                temp_files.append(encrypted_path)
            else:
                logger.error("Échec du chiffrement du fichier")
                return False
            
            # Rechercher si un fichier de configuration existe déjà
            results = self.drive_service.files().list(
                q=f"'{self.folder_id}' in parents and name = 'app_config.json'",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            # Préparer le fichier
            media = MediaFileUpload(
                encrypted_path,
                mimetype='application/json',
                resumable=True
            )
            
            try:
                if results.get('files'):
                    # Mettre à jour le fichier existant
                    file_id = results['files'][0]['id']
                    
                    # Utiliser update au lieu de delete/create
                    self.drive_service.files().update(
                        fileId=file_id,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    logger.info("Configuration mise à jour sur Google Drive")
                else:
                    # Créer un nouveau fichier
                    file_metadata = {
                        'name': 'app_config.json',
                        'parents': [self.folder_id]
                    }
                    
                    self.drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    logger.info("Configuration créée sur Google Drive")
                
                return True
                
            finally:
                # S'assurer que l'objet MediaFileUpload est fermé
                if hasattr(media, '_fd') and not media._fd.closed:
                    media._fd.close()
            
        except Exception as e:
            logger.error(f"Erreur lors du téléversement: {e}")
            return False
            
        finally:
            # Nettoyer les fichiers temporaires
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        # Attendre un peu pour s'assurer que le fichier n'est plus utilisé
                        time.sleep(0.1)
                        os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le fichier temporaire {temp_file}: {e}")
                    # Ne pas bloquer le processus si un fichier ne peut pas être supprimé

    def prepare_update(self, 
                      version: str,
                      description: str,
                      files_to_update: List[Dict[str, bool]],
                      source_dir: str) -> Optional[Tuple[str, str]]:
        """
        Prépare un fichier de mise à jour chiffré
        
        Args:
            version: Numéro de version (format: x.y.z)
            description: Description de la mise à jour
            files_to_update: Liste des fichiers à inclure avec leur sensibilité
            source_dir: Répertoire source des fichiers
            
        Returns:
            Tuple[str, str]: (chemin du fichier ZIP chiffré, checksum) ou None si échec
        """
        try:
            # Vérifier le format de version
            if not isinstance(version, str) or not version.count('.') >= 2:
                raise ValueError("Format de version invalide (utilisez x.y.z)")
            
            # Créer un fichier ZIP temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                try:
                    # Créer le manifest avec informations de sécurité
                    manifest = {
                        "version": version,
                        "description": description,
                        "created_at": datetime.now().isoformat(),
                        "files": files_to_update,
                        "security": {
                            "min_app_version": "1.0.0",  # Version minimale requise
                            "encryption_version": "1.0",  # Version du système de chiffrement
                            "checksum_algo": "sha256"    # Algorithme de hachage utilisé
                        }
                    }
                    
                    # Créer l'archive ZIP
                    with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        # Ajouter le manifest
                        zipf.writestr('manifest.json', json.dumps(manifest, indent=2))
                        
                        # Ajouter les fichiers (chiffrés si sensibles)
                        for file_info in files_to_update:
                            file_path = file_info["path"]
                            src_path = os.path.join(source_dir, file_path)
                            
                            if not os.path.exists(src_path):
                                raise ValueError(f"Fichier introuvable: {src_path}")
                            
                            if file_info.get("sensitive", False):
                                # Chiffrer le fichier avant de l'ajouter
                                encrypted_path = self._encrypt_file(src_path)
                                zipf.write(encrypted_path, file_path + '.enc')
                                os.unlink(encrypted_path)  # Nettoyer
                            else:
                                zipf.write(src_path, file_path)
                    
                    # Calculer le checksum du ZIP
                    checksum = self._calculate_file_hash(tmp_file.name)
                    
                    # Chiffrer le ZIP entier
                    encrypted_zip = self._encrypt_file(tmp_file.name)
                    
                    return encrypted_zip, checksum
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la création du fichier de mise à jour: {e}")
                    if os.path.exists(tmp_file.name):
                        os.unlink(tmp_file.name)
                    return None, None
                
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de la mise à jour: {e}")
            return None, None
    
    def upload_update(self, 
                     update_file: str,
                     version: str,
                     description: str,
                     checksum: str) -> bool:
        """
        Upload une mise à jour sur Google Drive
        
        Args:
            update_file: Chemin du fichier de mise à jour chiffré
            version: Numéro de version
            description: Description de la mise à jour
            checksum: Checksum du fichier
            
        Returns:
            bool: True si l'upload a réussi
        """
        try:
            # Vérifier que le fichier existe et est chiffré
            if not os.path.exists(update_file) or not update_file.endswith('.enc'):
                raise ValueError("Fichier de mise à jour invalide ou non chiffré")
            
            # Préparer les métadonnées avec informations de sécurité
            file_metadata = {
                'name': f'update_v{version}.zip.enc',
                'description': description,
                'parents': [self.folder_id],
                'appProperties': {
                    'version': version,
                    'checksum': checksum,
                    'signature': self._calculate_file_hash(update_file),
                    'encryption_version': '1.0',
                    'upload_date': datetime.now().isoformat(),
                    'security_level': 'encrypted'
                }
            }
            
            # Préparer le fichier pour l'upload
            media = MediaFileUpload(
                update_file,
                mimetype='application/octet-stream',
                resumable=True
            )
            
            # Upload le fichier
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, appProperties',
                supportsAllDrives=True
            ).execute()
            
            logger.info(f"Mise à jour v{version} uploadée avec succès (ID: {file['id']})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'upload de la mise à jour: {e}")
            return False

    def _calculate_file_hash(self, filepath: str) -> str:
        """Calcule le hash SHA-256 d'un fichier"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Erreur lors du calcul du hash pour {filepath}: {e}")
            return ""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire de mises à jour sécurisé pour l'application Vynal Docs Automator
Utilise Google Drive pour la distribution des mises à jour
"""

import os
import json
import logging
import hashlib
import requests
import tempfile
import shutil
import zipfile
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from utils.security import SecureFileManager
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from base64 import b64decode
import pickle

logger = logging.getLogger("VynalDocsAutomator.UpdateManager")

class UpdateManager:
    """Gestionnaire de mises à jour sécurisé utilisant Google Drive"""
    
    # Si vous modifiez ces scopes, supprimez le fichier token.pickle
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, app_version: str, credentials_path: str, folder_id: str):
        """
        Initialise le gestionnaire de mises à jour
        
        Args:
            app_version: Version actuelle de l'application
            credentials_path: Chemin vers le fichier credentials.json de Google Drive
            folder_id: ID du dossier Google Drive contenant les mises à jour
        """
        self.app_version = app_version
        self.credentials_path = credentials_path
        self.folder_id = folder_id
        self.data_dir = "data"
        self.updates_dir = os.path.join(self.data_dir, "updates")
        self.backup_dir = os.path.join(self.data_dir, "backups")
        
        # Créer les répertoires nécessaires
        os.makedirs(self.updates_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Gestionnaire de fichiers sécurisés
        self.secure_files = SecureFileManager(self.data_dir)
        
        # Liste des fichiers critiques à sauvegarder
        self.critical_files = [
            "users.json",
            "current_user.json",
            "session.json",
            "licenses.json",
            ".key",
            "config.json"
        ]
        
        # Charger l'historique des mises à jour
        self.update_history = self._load_update_history()
        
        # Initialiser le service Google Drive
        self.drive_service = self._init_drive_service()
    
    def _init_drive_service(self):
        """
        Initialise le service Google Drive avec authentification
        
        Returns:
            Resource: Service Google Drive authentifié
        """
        creds = None
        token_path = os.path.join(self.data_dir, "token.pickle")
        
        # Charger les tokens existants
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logger.error(f"Erreur lors du chargement du token: {e}")
        
        # Si pas de tokens valides, authentifier
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Erreur lors du rafraîchissement du token: {e}")
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"Erreur lors de l'authentification Google Drive: {e}")
                    raise ValueError("Impossible d'authentifier Google Drive")
            
            # Sauvegarder les tokens de manière sécurisée
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                self.secure_files._hide_file(token_path)
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde du token: {e}")
        
        try:
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Erreur lors de la création du service Drive: {e}")
            raise ValueError("Impossible de créer le service Google Drive")

    def _verify_file_metadata(self, file_metadata: Dict) -> bool:
        """
        Vérifie les métadonnées d'un fichier de mise à jour
        
        Args:
            file_metadata: Métadonnées du fichier
            
        Returns:
            bool: True si les métadonnées sont valides
        """
        try:
            required_fields = ['name', 'description', 'appProperties']
            if not all(field in file_metadata for field in required_fields):
                return False
            
            app_properties = file_metadata['appProperties']
            required_props = ['version', 'signature', 'checksum']
            if not all(prop in app_properties for prop in required_props):
                return False
            
            # Vérifier le format de version
            version = app_properties['version']
            if not isinstance(version, str) or not version.count('.') >= 2:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des métadonnées: {e}")
            return False

    def check_for_updates(self) -> Dict[str, Any]:
        """
        Vérifie si des mises à jour sont disponibles sur Google Drive
        
        Returns:
            Dict: Informations sur la mise à jour disponible ou None
        """
        try:
            # Rechercher les fichiers de mise à jour dans le dossier spécifié
            results = self.drive_service.files().list(
                q=f"'{self.folder_id}' in parents and trashed = false",
                orderBy="createdTime desc",
                pageSize=1,
                fields="files(id, name, description, size, createdTime, appProperties)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return None
            
            latest_update = files[0]
            if not self._verify_file_metadata(latest_update):
                logger.error("Métadonnées de mise à jour invalides")
                return None
            
            app_properties = latest_update['appProperties']
            latest_version = app_properties['version']
            
            # Vérifier si la version est plus récente
            if not self._is_newer_version(latest_version):
                return None
            
            return {
                "version": latest_version,
                "description": latest_update['description'],
                "size": int(latest_update['size']),
                "file_id": latest_update['id'],
                "signature": app_properties['signature'],
                "checksum": app_properties['checksum'],
                "release_date": latest_update['createdTime']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des mises à jour: {e}")
            return None
    
    def _is_newer_version(self, version: str) -> bool:
        """
        Vérifie si la version est plus récente que la version actuelle
        
        Args:
            version: Version à vérifier
            
        Returns:
            bool: True si la version est plus récente
        """
        try:
            current = [int(x) for x in self.app_version.split('.')]
            new = [int(x) for x in version.split('.')]
            
            for i in range(max(len(current), len(new))):
                c = current[i] if i < len(current) else 0
                n = new[i] if i < len(new) else 0
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
        Télécharge une mise à jour depuis Google Drive
        
        Args:
            file_id: ID du fichier sur Google Drive
            expected_checksum: Checksum attendu du fichier
            
        Returns:
            str: Chemin du fichier téléchargé ou None si échec
        """
        try:
            # Créer un fichier temporaire pour le téléchargement
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                try:
                    # Télécharger le fichier
                    request = self.drive_service.files().get_media(fileId=file_id)
                    downloader = MediaIoBaseDownload(tmp_file, request)
                    
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        if status:
                            logger.info(f"Téléchargement: {int(status.progress() * 100)}%")
                    
                    tmp_file.flush()
                    
                    # Vérifier le checksum
                    if not self._verify_file_checksum(tmp_file.name, expected_checksum):
                        logger.error("Checksum du fichier invalide")
                        os.unlink(tmp_file.name)
                        return None
                    
                    # Déplacer le fichier vers le répertoire des mises à jour
                    update_file = os.path.join(
                        self.updates_dir,
                        f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    )
                    shutil.move(tmp_file.name, update_file)
                    
                    # Masquer le fichier
                    self.secure_files._hide_file(update_file)
                    
                    logger.info(f"Mise à jour téléchargée: {update_file}")
                    return update_file
                    
                except Exception as e:
                    logger.error(f"Erreur lors du téléchargement: {e}")
                    if os.path.exists(tmp_file.name):
                        os.unlink(tmp_file.name)
                    return None
                
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la mise à jour: {e}")
            return None
    
    def _verify_file_checksum(self, filepath: str, expected_checksum: str) -> bool:
        """
        Vérifie le checksum d'un fichier
        
        Args:
            filepath: Chemin du fichier
            expected_checksum: Checksum attendu
            
        Returns:
            bool: True si le checksum est valide
        """
        try:
            calculated_checksum = self._calculate_file_hash(filepath)
            return calculated_checksum == expected_checksum
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du checksum: {e}")
            return False
    
    def _init_secure_session(self):
        """Initialise une session sécurisée pour les requêtes API"""
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'X-Client-Version': self.app_version,
            'X-Device-ID': self._get_device_id(),
            'User-Agent': 'VynalDocsAutomator-UpdateManager'
        })
    
    def _get_device_id(self) -> str:
        """
        Génère ou récupère l'identifiant unique du dispositif
        
        Returns:
            str: Identifiant unique du dispositif
        """
        device_id_file = os.path.join(self.data_dir, ".device_id")
        try:
            if os.path.exists(device_id_file):
                return self.secure_files.read_secure_file(device_id_file)["device_id"]
            
            # Générer un nouvel ID unique
            device_id = hashlib.sha256(os.urandom(32)).hexdigest()
            self.secure_files.write_secure_file(device_id_file, {"device_id": device_id})
            return device_id
        except Exception as e:
            logger.error(f"Erreur lors de la génération/récupération de l'ID du dispositif: {e}")
            return hashlib.sha256(str(datetime.now()).encode()).hexdigest()
    
    def _verify_server_certificate(self, cert: Dict) -> bool:
        """
        Vérifie le certificat du serveur
        
        Args:
            cert: Certificat à vérifier
            
        Returns:
            bool: True si le certificat est valide
        """
        try:
            # Vérifier l'empreinte du certificat
            cert_fingerprint = cert.get('fingerprint')
            if not cert_fingerprint:
                return False
            
            # Charger les empreintes de certificats approuvées
            trusted_fingerprints = self.secure_files.read_secure_file("trusted_certs.json")
            if not trusted_fingerprints:
                return False
            
            return cert_fingerprint in trusted_fingerprints.get('fingerprints', [])
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du certificat: {e}")
            return False
    
    def _decrypt_update_url(self, encrypted_url: str, key: str) -> str:
        """
        Déchiffre l'URL de mise à jour
        
        Args:
            encrypted_url: URL chiffrée
            key: Clé de déchiffrement
            
        Returns:
            str: URL déchiffrée
        """
        try:
            from cryptography.fernet import Fernet
            from base64 import urlsafe_b64encode
            
            # Dériver une clé de chiffrement à partir de la clé fournie
            key_bytes = hashlib.sha256(key.encode()).digest()
            key = urlsafe_b64encode(key_bytes)
            
            f = Fernet(key)
            decrypted_url = f.decrypt(encrypted_url.encode())
            return decrypted_url.decode()
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement de l'URL: {e}")
            return None
    
    def _load_update_history(self) -> List[Dict[str, Any]]:
        """
        Charge l'historique des mises à jour
        
        Returns:
            List[Dict]: Liste des mises à jour effectuées
        """
        try:
            data = self.secure_files.read_secure_file("update_history.json")
            return data.get("updates", [])
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique des mises à jour: {e}")
            return []
    
    def _save_update_history(self):
        """Sauvegarde l'historique des mises à jour"""
        try:
            self.secure_files.write_secure_file("update_history.json", {
                "updates": self.update_history
            })
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique des mises à jour: {e}")
    
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
            logger.error(f"Erreur lors du calcul du hash pour {filepath}: {e}")
            return ""
    
    def _verify_update_signature(self, update_file: str, signature: str) -> bool:
        """
        Vérifie la signature d'une mise à jour
        
        Args:
            update_file: Chemin du fichier de mise à jour
            signature: Signature à vérifier
            
        Returns:
            bool: True si la signature est valide
        """
        try:
            calculated_hash = self._calculate_file_hash(update_file)
            return calculated_hash == signature
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la signature: {e}")
            return False
    
    def _backup_critical_files(self) -> str:
        """
        Crée une sauvegarde des fichiers critiques
        
        Returns:
            str: Chemin du répertoire de sauvegarde ou chaîne vide si échec
        """
        try:
            # Créer un répertoire de sauvegarde horodaté
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copier les fichiers critiques
            for filename in self.critical_files:
                src_path = os.path.join(self.data_dir, filename)
                if os.path.exists(src_path):
                    dst_path = os.path.join(backup_dir, filename)
                    shutil.copy2(src_path, dst_path)
                    # Masquer le fichier de sauvegarde
                    self.secure_files._hide_file(dst_path)
            
            # Masquer le répertoire de sauvegarde
            self.secure_files._hide_file(backup_dir)
            
            logger.info(f"Sauvegarde créée dans {backup_dir}")
            return backup_dir
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            return ""
    
    def _restore_from_backup(self, backup_dir: str) -> bool:
        """
        Restaure les fichiers depuis une sauvegarde
        
        Args:
            backup_dir: Chemin du répertoire de sauvegarde
            
        Returns:
            bool: True si la restauration a réussi
        """
        try:
            # Restaurer chaque fichier critique
            for filename in self.critical_files:
                src_path = os.path.join(backup_dir, filename)
                if os.path.exists(src_path):
                    dst_path = os.path.join(self.data_dir, filename)
                    shutil.copy2(src_path, dst_path)
                    # Masquer le fichier restauré
                    self.secure_files._hide_file(dst_path)
            
            logger.info(f"Restauration depuis {backup_dir} réussie")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la restauration depuis {backup_dir}: {e}")
            return False
    
    def install_update(self, update_file: str) -> bool:
        """
        Installe une mise à jour
        
        Args:
            update_file: Chemin du fichier de mise à jour
            
        Returns:
            bool: True si l'installation a réussi
        """
        try:
            # Créer une sauvegarde avant l'installation
            backup_dir = self._backup_critical_files()
            if not backup_dir:
                logger.error("Impossible de créer une sauvegarde")
                return False
            
            # Extraire la mise à jour dans un répertoire temporaire
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    with zipfile.ZipFile(update_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Vérifier le fichier manifest
                    manifest_path = os.path.join(temp_dir, "manifest.json")
                    if not os.path.exists(manifest_path):
                        raise ValueError("Fichier manifest manquant")
                    
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                    
                    # Vérifier la version
                    if not manifest.get("version"):
                        raise ValueError("Version manquante dans le manifest")
                    
                    # Copier les fichiers mis à jour
                    for file_info in manifest.get("files", []):
                        src_path = os.path.join(temp_dir, file_info["path"])
                        dst_path = file_info["path"]
                        
                        # Créer les répertoires nécessaires
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        
                        # Copier le fichier
                        shutil.copy2(src_path, dst_path)
                        
                        # Masquer si nécessaire
                        if file_info.get("sensitive", False):
                            self.secure_files._hide_file(dst_path)
                    
                    # Mettre à jour l'historique
                    self.update_history.append({
                        "version": manifest["version"],
                        "date": datetime.now().isoformat(),
                        "backup_dir": backup_dir
                    })
                    self._save_update_history()
                    
                    logger.info(f"Mise à jour {manifest['version']} installée avec succès")
                    return True
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'installation: {e}")
                    # Restaurer depuis la sauvegarde
                    if self._restore_from_backup(backup_dir):
                        logger.info("Restauration réussie après échec de l'installation")
                    else:
                        logger.error("Échec de la restauration après échec de l'installation")
                    return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'installation de la mise à jour: {e}")
            return False
    
    def cleanup_old_updates(self, days: int = 30):
        """
        Nettoie les anciennes mises à jour et sauvegardes
        
        Args:
            days: Nombre de jours à conserver
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Nettoyer les anciennes sauvegardes
            for item in os.listdir(self.backup_dir):
                if item.startswith("backup_"):
                    try:
                        # Extraire la date de la sauvegarde
                        date_str = item.replace("backup_", "").split("_")[0]
                        date = datetime.strptime(date_str, "%Y%m%d")
                        
                        if date < cutoff_date:
                            backup_path = os.path.join(self.backup_dir, item)
                            if os.path.isdir(backup_path):
                                shutil.rmtree(backup_path)
                            logger.info(f"Ancienne sauvegarde supprimée: {item}")
                    except Exception as e:
                        logger.error(f"Erreur lors du nettoyage de la sauvegarde {item}: {e}")
            
            # Nettoyer les anciens fichiers de mise à jour
            for item in os.listdir(self.updates_dir):
                if item.startswith("update_"):
                    try:
                        # Extraire la date du fichier de mise à jour
                        date_str = item.replace("update_", "").split("_")[0]
                        date = datetime.strptime(date_str, "%Y%m%d")
                        
                        if date < cutoff_date:
                            update_path = os.path.join(self.updates_dir, item)
                            os.unlink(update_path)
                            logger.info(f"Ancien fichier de mise à jour supprimé: {item}")
                    except Exception as e:
                        logger.error(f"Erreur lors du nettoyage du fichier de mise à jour {item}: {e}")
            
            # Nettoyer l'historique des mises à jour
            self.update_history = [
                update for update in self.update_history
                if datetime.fromisoformat(update["date"]) >= cutoff_date
            ]
            self._save_update_history()
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des anciennes mises à jour: {e}")
    
    def get_update_history(self) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des mises à jour
        
        Returns:
            List[Dict]: Liste des mises à jour effectuées
        """
        return self.update_history.copy()
    
    def rollback_update(self, version: str) -> bool:
        """
        Annule une mise à jour en restaurant depuis la sauvegarde
        
        Args:
            version: Version à restaurer
            
        Returns:
            bool: True si la restauration a réussi
        """
        try:
            # Trouver la sauvegarde correspondante
            for update in reversed(self.update_history):
                if update["version"] == version:
                    backup_dir = update["backup_dir"]
                    if os.path.exists(backup_dir):
                        # Créer une sauvegarde de l'état actuel
                        current_backup = self._backup_critical_files()
                        if not current_backup:
                            logger.error("Impossible de créer une sauvegarde de l'état actuel")
                            return False
                        
                        # Restaurer depuis la sauvegarde
                        if self._restore_from_backup(backup_dir):
                            logger.info(f"Restauration vers la version {version} réussie")
                            return True
                        else:
                            # En cas d'échec, restaurer l'état précédent
                            if self._restore_from_backup(current_backup):
                                logger.info("Restauration de l'état précédent réussie")
                            else:
                                logger.error("Échec de la restauration de l'état précédent")
                            return False
                    else:
                        logger.error(f"Sauvegarde introuvable pour la version {version}")
                        return False
            
            logger.error(f"Version {version} non trouvée dans l'historique")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la restauration vers la version {version}: {e}")
            return False 
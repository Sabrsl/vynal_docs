#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion de configuration distante pour l'application Vynal Docs Automator.
Permet de charger et d'interpréter un fichier JSON distant, vérifier les mises à jour, les licences et gérer les fonctionnalités dynamiques.
"""

import os
import json
import hashlib
import logging
import threading
import time
import datetime
import tempfile
import shutil
import base64
import urllib.request
from urllib.error import URLError, HTTPError
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
import ssl
import tkinter as tk

from utils.license_utils import verify_license, get_expiration_date_string, get_remaining_days
from utils.notification import show_notification, notification_manager

logger = logging.getLogger("VynalDocsAutomator.RemoteConfigManager")

class RemoteConfigManager:
    """
    Gestionnaire de configuration distante pour l'application.
    Gère le chargement et l'interprétation d'un fichier de configuration distant.
    
    Attributes:
        config_url (str): URL du fichier de configuration distant
        local_cache_path (str): Chemin vers le cache local du fichier de configuration
        update_log_path (str): Chemin vers le fichier de log des mises à jour
        config (dict): Configuration distante actuelle
        last_check_time (float): Timestamp de la dernière vérification
        check_interval (int): Intervalle entre les vérifications (en secondes)
        on_config_updated (Callable): Fonction à appeler lors de la mise à jour de la configuration
        on_update_available (Callable): Fonction à appeler lorsqu'une mise à jour est disponible
        on_message_received (Callable): Fonction à appeler lorsqu'un message global est reçu
        offline_mode (bool): Indique si l'application est en mode hors ligne
        last_successful_check (float): Timestamp de la dernière vérification réussie
    """
    
    def __init__(self, config_url: str, local_cache_dir: str, check_interval: int = 3600):
        """
        Initialise le gestionnaire de configuration distante.
        
        Args:
            config_url (str): URL du fichier de configuration distant
            local_cache_dir (str): Répertoire de cache local
            check_interval (int, optional): Intervalle entre les vérifications (en secondes)
        """
        self.config_url = config_url
        
        # Assurer que le répertoire de cache existe
        os.makedirs(local_cache_dir, exist_ok=True)
        
        self.local_cache_path = os.path.join(local_cache_dir, "app_config_cache.json")
        self.update_log_path = os.path.join(local_cache_dir, "update.log")
        
        self.config = {}
        self.last_check_time = 0
        self.check_interval = check_interval
        self.on_config_updated = None
        self.on_update_available = None
        self.on_message_received = None
        self.offline_mode = False
        self.last_successful_check = 0
        self.features_enabled_locally = {}
        
        # Initialiser le système de notifications
        try:
            root = tk.Tk()
            root.withdraw()  # Cacher la fenêtre racine
            notification_manager.initialize(root)
            logger.info("Système de notifications initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du système de notifications: {e}")
        
        # Chargement initial de la configuration
        self._load_local_cache()
        
        # Démarrer une vérification asynchrone
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        
        logger.info("RemoteConfigManager initialisé")
    
    def _load_local_cache(self) -> Dict[str, Any]:
        """
        Charge la configuration depuis le cache local.
        Si le fichier n'existe pas ou est invalide, initialise une configuration vide.
        
        Returns:
            Dict[str, Any]: Configuration chargée
        """
        if not os.path.exists(self.local_cache_path):
            logger.info(f"Fichier de cache local {self.local_cache_path} n'existe pas, initialisation avec une configuration vide")
            self.config = {}
            return self.config
        
        try:
            with open(self.local_cache_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info(f"Configuration chargée depuis le cache local {self.local_cache_path}")
            return self.config
        
        except json.JSONDecodeError as e:
            error_msg = f"Erreur de format JSON dans le fichier de cache local: {e}"
            logger.error(error_msg)
            show_notification(
                "Erreur de configuration",
                "Le fichier de configuration est corrompu. Une nouvelle configuration sera créée.",
                "error"
            )
            # Faire une sauvegarde du fichier corrompu
            backup_file = f"{self.local_cache_path}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            try:
                shutil.copyfile(self.local_cache_path, backup_file)
                logger.info(f"Fichier de cache local corrompu sauvegardé sous {backup_file}")
            except Exception as backup_error:
                logger.error(f"Erreur lors de la sauvegarde du fichier corrompu: {backup_error}")
            self.config = {}
            return self.config
        
        except Exception as e:
            error_msg = f"Erreur lors du chargement du cache local: {e}"
            logger.error(error_msg)
            show_notification(
                "Erreur de configuration",
                "Impossible de charger la configuration. Une nouvelle configuration sera créée.",
                "error"
            )
            self.config = {}
            return self.config
    
    def _save_local_cache(self) -> bool:
        """
        Sauvegarde la configuration dans le cache local.
        
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Utiliser un fichier temporaire pour éviter la corruption en cas d'erreur
            temp_file = f"{self.local_cache_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Remplacer le fichier original par le temporaire
            if os.path.exists(self.local_cache_path):
                os.replace(temp_file, self.local_cache_path)
            else:
                os.rename(temp_file, self.local_cache_path)
            
            logger.info(f"Configuration sauvegardée dans le cache local {self.local_cache_path}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache local: {e}")
            return False
    
    def _fetch_remote_config(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Récupère la configuration depuis Google Drive.
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (succès, configuration)
        """
        try:
            # Initialiser le gestionnaire de mises à jour
            from utils.update_downloader import UpdateDownloader
            
            # Récupérer les paramètres depuis la configuration locale
            config = self._load_local_cache()
            credentials_path = config.get('update', {}).get('credentials_path', 'credentials.json')
            folder_id = config.get('update', {}).get('folder_id', '')
            encryption_password = config.get('update', {}).get('encryption_password', '')
            
            if not all([credentials_path, folder_id, encryption_password]):
                logger.warning("Configuration Google Drive incomplète")
                return False, {}
            
            # Initialiser le gestionnaire de mises à jour
            updater = UpdateDownloader(credentials_path, folder_id, encryption_password)
            
            # Récupérer le fichier de configuration
            config_file = updater.download_config()
            if not config_file:
                logger.error("Erreur lors du téléchargement de la configuration")
                return False, {}
            
            # Lire et décoder le contenu
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    remote_config = json.load(f)
                
                # Nettoyer le fichier temporaire
                os.unlink(config_file)
                
                # Mettre à jour le timestamp de la dernière vérification réussie
                self.last_successful_check = time.time()
                self.offline_mode = False
                
                return True, remote_config
                
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de format JSON dans la configuration distante: {e}")
                return False, {}
            finally:
                # S'assurer que le fichier temporaire est supprimé
                if os.path.exists(config_file):
                    os.unlink(config_file)
        
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération de la configuration distante: {e}")
            self.offline_mode = True
            return False, {}
    
    def check_for_updates(self, force: bool = False) -> bool:
        """
        Vérifie les mises à jour de la configuration distante.
        Si une mise à jour est disponible, met à jour le cache local et notifie les observateurs.
        
        Args:
            force (bool, optional): Force la vérification même si l'intervalle n'est pas écoulé
        
        Returns:
            bool: True si la configuration a été mise à jour, False sinon
        """
        # Vérifier si l'intervalle de vérification est écoulé
        current_time = time.time()
        if not force and current_time - self.last_check_time < self.check_interval:
            logger.debug("Intervalle de vérification non écoulé, utilisation du cache")
            return False
        
        # Mettre à jour le timestamp de la dernière vérification
        self.last_check_time = current_time
        
        # Récupérer la configuration distante
        success, remote_config = self._fetch_remote_config()
        if not success:
            logger.warning("Échec de la récupération de la configuration distante, utilisation du cache")
            return False
        
        # Vérifier si la configuration a changé
        if remote_config == self.config:
            logger.info("La configuration distante n'a pas changé")
            return False
        
        # Sauvegarder l'ancienne configuration pour la comparaison
        old_config = self.config.copy()
        
        # Mettre à jour la configuration
        self.config = remote_config
        
        # Sauvegarder le cache local
        self._save_local_cache()
        
        # Vérifier les mises à jour
        if self._check_updates(old_config):
            logger.info("Mise à jour détectée")
            # Si une fonction de callback est définie pour les mises à jour, l'appeler
            if self.on_update_available:
                self.on_update_available(self.config.get('update', {}))
        
        # Vérifier les messages globaux
        if self._check_global_messages(old_config):
            logger.info("Message global détecté")
            # Si une fonction de callback est définie pour les messages, l'appeler
            if self.on_message_received:
                self.on_message_received(self.config.get('global_message', {}))
        
        # Vérifier les modifications de fonctionnalités
        self._check_features(old_config)
        
        # Si une fonction de callback est définie pour les mises à jour de configuration, l'appeler
        if self.on_config_updated:
            self.on_config_updated(self.config)
        
        logger.info("Configuration distante mise à jour avec succès")
        return True
    
    def _check_updates(self, old_config: Dict[str, Any]) -> bool:
        """
        Vérifie si des mises à jour sont disponibles en comparant l'ancienne et la nouvelle configuration.
        
        Args:
            old_config (Dict[str, Any]): Ancienne configuration
        
        Returns:
            bool: True si des mises à jour sont disponibles, False sinon
        """
        try:
            # Vérifier la version de l'application
            old_version = old_config.get('app', {}).get('version', '0.0.0')
            new_version = self.config.get('app', {}).get('version', '0.0.0')
            
            if new_version != old_version:
                logger.info(f"Nouvelle version détectée: {new_version} (ancienne: {old_version})")
                
                # Créer un message de notification
                notification = {
                    'type': 'update',
                    'title': 'Nouvelle mise à jour disponible',
                    'message': f'Une nouvelle version ({new_version}) est disponible. Voulez-vous la télécharger maintenant ?',
                    'version': new_version,
                    'changelog': self.config.get('update', {}).get('changelog', ''),
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                # Sauvegarder la notification dans la configuration
                if 'notifications' not in self.config:
                    self.config['notifications'] = []
                self.config['notifications'].append(notification)
                
                # Afficher la notification
                show_notification(
                    notification['title'],
                    notification['message'],
                    'info',
                    10000  # Plus long pour les mises à jour
                )
                
                # Si une fonction de callback est définie pour les mises à jour, l'appeler
                if self.on_update_available:
                    self.on_update_available(self.config.get('update', {}))
                
                return True
            
            return False
            
        except Exception as e:
            error_msg = f"Erreur lors de la vérification des mises à jour: {e}"
            logger.error(error_msg)
            show_notification(
                "Erreur de mise à jour",
                "Impossible de vérifier les mises à jour. Veuillez réessayer plus tard.",
                "error"
            )
            return False
    
    def _check_global_messages(self, old_config: Dict[str, Any]) -> bool:
        """
        Vérifie si un message global a été ajouté ou modifié.
        
        Args:
            old_config (Dict[str, Any]): Ancienne configuration
        
        Returns:
            bool: True si un message global a été ajouté ou modifié, False sinon
        """
        # Vérifier si la section global_message existe dans les deux configurations
        if 'global_message' not in self.config:
            return False
        
        # Vérifier si le message est visible
        if not self.config['global_message'].get('visible', False):
            return False
        
        # Si le message n'existait pas avant ou s'il a changé
        if ('global_message' not in old_config or 
            old_config['global_message'].get('title') != self.config['global_message'].get('title') or
            old_config['global_message'].get('body') != self.config['global_message'].get('body')):
            return True
        
        # Si le message existait déjà mais n'était pas visible avant
        if not old_config['global_message'].get('visible', False):
            return True
        
        return False
    
    def _check_features(self, old_config: Dict[str, Any]) -> None:
        """
        Vérifie si des fonctionnalités ont été activées ou désactivées.
        
        Args:
            old_config (Dict[str, Any]): Ancienne configuration
        """
        if 'features' not in self.config:
            return
        
        # Comparaison avec les anciens paramètres
        if 'features' in old_config:
            for feature, enabled in self.config['features'].items():
                if feature not in old_config['features'] or old_config['features'][feature] != enabled:
                    logger.info(f"Fonctionnalité '{feature}' {'activée' if enabled else 'désactivée'}")
        else:
            # Si features n'existait pas avant
            for feature, enabled in self.config['features'].items():
                logger.info(f"Nouvelle fonctionnalité '{feature}' {'activée' if enabled else 'désactivée'}")
    
    def update_is_available(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Vérifie si une mise à jour est disponible pour l'application.
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (disponible, informations de mise à jour)
        """
        if 'update' not in self.config:
            return False, {}
        
        update_info = self.config['update']
        
        # Vérifier si les informations nécessaires sont présentes
        if 'latest_version' not in update_info or 'download_url' not in update_info:
            return False, {}
        
        # Récupérer la version actuelle de l'application
        from utils.config_manager import ConfigManager
        config_manager = ConfigManager()
        current_version = config_manager.get('app.version', '0.0.0')
        
        # Comparer les versions (simple comparaison lexicographique)
        if update_info['latest_version'] > current_version:
            return True, update_info
        
        return False, {}
    
    def download_update(self, update_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Télécharge une mise à jour depuis Google Drive.
        
        Args:
            update_info (Dict[str, Any]): Informations sur la mise à jour
            
        Returns:
            Tuple[bool, str]: (succès, chemin du fichier ou message d'erreur)
        """
        try:
            # Initialiser le gestionnaire de mises à jour
            from utils.update_downloader import UpdateDownloader
            
            # Récupérer les paramètres depuis la configuration
            config = self._load_local_cache()
            credentials_path = config.get('update', {}).get('credentials_path', 'credentials.json')
            folder_id = config.get('update', {}).get('folder_id', '')
            encryption_password = config.get('update', {}).get('encryption_password', '')
            
            if not all([credentials_path, folder_id, encryption_password]):
                logger.error("Configuration Google Drive incomplète")
                return False, "Configuration Google Drive incomplète"
            
            # Initialiser le gestionnaire de mises à jour
            updater = UpdateDownloader(credentials_path, folder_id, encryption_password)
            
            # Télécharger la mise à jour
            update_file = updater.download_update(
                update_info['file_id'],
                update_info['checksum']
            )
            
            if not update_file:
                logger.error("Erreur lors du téléchargement de la mise à jour")
                return False, "Erreur lors du téléchargement"
            
            # Vérifier la signature si nécessaire
            if self.config.get('security', {}).get('signature_required', False):
                if not updater.verify_signature(update_file, update_info.get('signature', '')):
                    os.unlink(update_file)
                    return False, "Signature invalide"
            
            # Enregistrer l'information dans le fichier de log
            try:
                with open(self.update_log_path, 'a', encoding='utf-8') as f:
                    log_entry = f"{datetime.datetime.now().isoformat()} - Mise à jour téléchargée: {update_info.get('latest_version', 'inconnu')}\n"
                    f.write(log_entry)
            except Exception as e:
                logger.error(f"Erreur lors de l'écriture dans le fichier de log des mises à jour: {e}")
            
            return True, update_file
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la mise à jour: {e}")
            return False, str(e)
    
    def apply_update(self, update_file_path: str) -> Tuple[bool, str]:
        """
        Applique une mise à jour.
        
        Args:
            update_file_path (str): Chemin du fichier de mise à jour
        
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        import zipfile
        
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(update_file_path):
                return False, "Fichier de mise à jour introuvable"
            
            # Vérifier si c'est un fichier ZIP valide
            if not zipfile.is_zipfile(update_file_path):
                return False, "Fichier de mise à jour invalide"
            
            # Récupérer le répertoire de base de l'application
            from utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            base_dir = config_manager.base_dir
            
            # Créer un répertoire temporaire pour l'extraction
            temp_dir = tempfile.mkdtemp()
            
            # Extraire le fichier ZIP
            with zipfile.ZipFile(update_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Récupérer la version de la mise à jour
            update_info = self.config.get('update', {})
            update_version = update_info.get('latest_version', 'inconnue')
            
            # Appliquer la mise à jour (copier les fichiers extraits vers le répertoire de l'application)
            # Cette opération doit être adaptée en fonction de la structure de l'application
            # et peut nécessiter des privilèges d'administrateur
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, temp_dir)
                    dest_path = os.path.join(base_dir, rel_path)
                    
                    # Créer le répertoire de destination s'il n'existe pas
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    # Copier le fichier
                    shutil.copy2(src_path, dest_path)
            
            # Supprimer les fichiers temporaires
            shutil.rmtree(temp_dir)
            os.unlink(update_file_path)
            
            # Mettre à jour la version dans la configuration
            config_manager.set('app.version', update_version)
            config_manager.save()
            
            # Enregistrer l'information dans le fichier de log
            try:
                with open(self.update_log_path, 'a', encoding='utf-8') as f:
                    log_entry = f"{datetime.datetime.now().isoformat()} - Mise à jour appliquée: {update_version}\n"
                    f.write(log_entry)
            except Exception as e:
                logger.error(f"Erreur lors de l'écriture dans le fichier de log des mises à jour: {e}")
            
            return True, f"Mise à jour vers la version {update_version} appliquée avec succès. Veuillez redémarrer l'application."
        
        except Exception as e:
            logger.error(f"Erreur lors de l'application de la mise à jour: {e}")
            return False, f"Erreur lors de l'application de la mise à jour: {str(e)}"
    
    def check_license(self, email: str, license_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Vérifie si une licence est valide en utilisant les informations locales et distantes.
        
        Args:
            email (str): Email de l'utilisateur
            license_key (str): Clé de licence
        
        Returns:
            Tuple[bool, str, Dict[str, Any]]: (valide, message, données de licence)
        """
        try:
            # Normaliser l'email
            email = email.lower().strip()
            
            # Vérifier si l'application est en mode hors ligne
            if self.offline_mode:
                logger.info(f"Vérification de licence en mode hors ligne pour {email}")
                
                # Récupérer les paramètres de grâce
                grace_days = self.config.get('settings', {}).get('licence_check_grace_days', 7)
                max_offline_days = self.config.get('settings', {}).get('max_offline_days', 14)
                
                # Calculer le nombre de jours depuis la dernière vérification réussie
                days_since_check = (time.time() - self.last_successful_check) / 86400
                
                # Si la période de grâce est dépassée, vérifier localement
                if days_since_check > grace_days:
                    logger.warning(f"Période de grâce dépassée ({days_since_check:.1f} jours), vérification locale uniquement")
                    if days_since_check > max_offline_days:
                        error_msg = f"Période maximale hors ligne dépassée ({max_offline_days} jours). Veuillez vous connecter pour vérifier votre licence."
                        show_notification("Erreur de licence", error_msg, "error")
                        return False, error_msg, {}
                
                # Vérifier avec les informations locales uniquement
                is_valid, message, license_data = verify_license(email, license_key)
                if not is_valid:
                    show_notification("Erreur de licence", message, "error")
                return is_valid, message, license_data
            
            # Vérifier dans la configuration distante
            if 'licences' in self.config and email in self.config['licences']:
                remote_license = self.config['licences'][email]
                
                # Vérifier le statut
                if remote_license.get('status') == 'blocked':
                    error_msg = "Licence bloquée par l'administrateur."
                    show_notification("Erreur de licence", error_msg, "error")
                    logger.warning(f"Licence bloquée pour {email}")
                    return False, error_msg, remote_license
                
                # Vérifier la date d'expiration
                expires_str = remote_license.get('expires')
                if expires_str:
                    try:
                        expires_date = datetime.datetime.strptime(expires_str, "%Y-%m-%d").date()
                        today = datetime.datetime.now().date()
                        
                        if expires_date < today:
                            error_msg = f"Licence expirée le {expires_str}."
                            show_notification("Erreur de licence", error_msg, "error")
                            logger.warning(f"Licence expirée pour {email} (expirée le {expires_str})")
                            return False, error_msg, remote_license
                    except Exception as e:
                        logger.error(f"Erreur lors de l'analyse de la date d'expiration: {e}")
                
                # Vérifier la licence localement également
                is_valid, message, license_data = verify_license(email, license_key)
                if is_valid:
                    # Si la licence est valide localement et distante, retourner les informations distantes
                    logger.info(f"Licence valide pour {email} (vérification distante et locale)")
                    return True, "Licence valide", remote_license
                else:
                    logger.warning(f"Licence invalide localement pour {email}: {message}")
                    show_notification("Erreur de licence", message, "error")
                    return False, message, license_data
            
            # Si la licence n'est pas dans la configuration distante, vérifier localement
            logger.info(f"Licence non trouvée dans la configuration distante pour {email}, vérification locale")
            is_valid, message, license_data = verify_license(email, license_key)
            if not is_valid:
                show_notification("Erreur de licence", message, "error")
            return is_valid, message, license_data
            
        except Exception as e:
            error_msg = f"Erreur lors de la vérification de la licence: {e}"
            logger.error(error_msg)
            show_notification("Erreur de licence", "Une erreur est survenue lors de la vérification de la licence.", "error")
            return False, error_msg, {}
    
    def get_license_details(self, email: str) -> Dict[str, Any]:
        """
        Récupère les détails d'une licence depuis la configuration distante.
        
        Args:
            email (str): Email de l'utilisateur
        
        Returns:
            Dict[str, Any]: Détails de la licence
        """
        # Normaliser l'email
        email = email.lower().strip()
        
        # Vérifier dans la configuration distante
        if 'licences' in self.config and email in self.config['licences']:
            return self.config['licences'][email]
        
        return {}
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Vérifie si une fonctionnalité est activée.
        
        Args:
            feature_name (str): Nom de la fonctionnalité
        
        Returns:
            bool: True si la fonctionnalité est activée, False sinon
        """
        # Vérifier si la fonctionnalité a été modifiée localement
        if feature_name in self.features_enabled_locally:
            return self.features_enabled_locally[feature_name]
        
        # Vérifier dans la configuration distante
        if 'features' in self.config and feature_name in self.config['features']:
            return self.config['features'][feature_name]
        
        # Par défaut, retourner False
        return False
    
    def set_feature_enabled_locally(self, feature_name: str, enabled: bool) -> None:
        """
        Définit localement si une fonctionnalité est activée.
        
        Args:
            feature_name (str): Nom de la fonctionnalité
            enabled (bool): True pour activer, False pour désactiver
        """
        self.features_enabled_locally[feature_name] = enabled
        logger.info(f"Fonctionnalité '{feature_name}' {'activée' if enabled else 'désactivée'} localement")
    
    def get_global_message(self) -> Optional[Dict[str, Any]]:
        """
        Récupère le message global depuis la configuration distante.
        
        Returns:
            Optional[Dict[str, Any]]: Message global ou None si aucun message n'est disponible
        """
        if 'global_message' in self.config and self.config['global_message'].get('visible', False):
            return self.config['global_message']
        
        return None
    
    def get_full_changelog(self) -> List[Dict[str, Any]]:
        """
        Récupère le changelog complet depuis la configuration distante.
        
        Returns:
            List[Dict[str, Any]]: Liste des entrées du changelog
        """
        return self.config.get('changelog_full', [])
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Récupère un paramètre depuis la configuration distante.
        
        Args:
            key (str): Clé du paramètre
            default (Any, optional): Valeur par défaut si le paramètre n'existe pas
        
        Returns:
            Any: Valeur du paramètre
        """
        if 'settings' in self.config and key in self.config['settings']:
            return self.config['settings'][key]
        
        return default
    
    def get_support_info(self) -> Dict[str, str]:
        """
        Récupère les informations de support depuis la configuration distante.
        
        Returns:
            Dict[str, str]: Informations de support
        """
        return self.config.get('support', {})
    
    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """
        Récupère les notifications en attente.
        
        Returns:
            List[Dict[str, Any]]: Liste des notifications en attente
        """
        try:
            notifications = self.config.get('notifications', [])
            # Filtrer les notifications non lues
            pending = [n for n in notifications if not n.get('read', False)]
            return pending
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des notifications: {e}")
            return []
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """
        Marque une notification comme lue.
        
        Args:
            notification_id (str): ID de la notification
        
        Returns:
            bool: True si la notification a été marquée comme lue, False sinon
        """
        try:
            notifications = self.config.get('notifications', [])
            for notification in notifications:
                if notification.get('id') == notification_id:
                    notification['read'] = True
                    self._save_local_cache()
                    return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors du marquage de la notification comme lue: {e}")
            return False 
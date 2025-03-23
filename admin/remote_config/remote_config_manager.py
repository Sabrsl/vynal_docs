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

from utils.license_utils import verify_license, get_expiration_date_string, get_remaining_days

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
            logger.error(f"Erreur de format JSON dans le fichier de cache local: {e}")
            # Faire une sauvegarde du fichier corrompu
            backup_file = f"{self.local_cache_path}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copyfile(self.local_cache_path, backup_file)
            logger.info(f"Fichier de cache local corrompu sauvegardé sous {backup_file}")
            self.config = {}
            return self.config
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement du cache local: {e}")
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
        Récupère la configuration depuis l'URL distante.
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (succès, configuration)
        """
        try:
            # Créer un contexte SSL pour ignorer les erreurs de certificat en développement
            # En production, ce comportement devrait être modifié
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Ouvrir l'URL avec un timeout
            with urllib.request.urlopen(self.config_url, timeout=10, context=ctx) as response:
                if response.status == 200:
                    # Lire et décoder le contenu
                    content = response.read().decode('utf-8')
                    remote_config = json.loads(content)
                    
                    # Mettre à jour le timestamp de la dernière vérification réussie
                    self.last_successful_check = time.time()
                    self.offline_mode = False
                    
                    return True, remote_config
                else:
                    logger.error(f"Erreur lors de la récupération de la configuration distante: {response.status} {response.reason}")
                    return False, {}
        
        except (URLError, HTTPError) as e:
            logger.error(f"Erreur de connexion lors de la récupération de la configuration distante: {e}")
            self.offline_mode = True
            return False, {}
        
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de format JSON dans la configuration distante: {e}")
            return False, {}
        
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération de la configuration distante: {e}")
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
        Vérifie si une mise à jour est disponible.
        
        Args:
            old_config (Dict[str, Any]): Ancienne configuration
        
        Returns:
            bool: True si une mise à jour est disponible, False sinon
        """
        # Vérifier si la section update existe dans les deux configurations
        if 'update' not in self.config or 'update' not in old_config:
            return 'update' in self.config
        
        # Vérifier si la version a changé
        new_version = self.config['update'].get('latest_version')
        old_version = old_config['update'].get('latest_version')
        
        if new_version != old_version and new_version is not None:
            # Enregistrer l'information dans le fichier de log
            try:
                with open(self.update_log_path, 'a', encoding='utf-8') as f:
                    log_entry = f"{datetime.datetime.now().isoformat()} - Nouvelle version disponible: {new_version}\n"
                    f.write(log_entry)
            except Exception as e:
                logger.error(f"Erreur lors de l'écriture dans le fichier de log des mises à jour: {e}")
            
            return True
        
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
        Télécharge une mise à jour.
        
        Args:
            update_info (Dict[str, Any]): Informations de mise à jour
        
        Returns:
            Tuple[bool, str]: (succès, chemin du fichier téléchargé ou message d'erreur)
        """
        if 'download_url' not in update_info:
            return False, "URL de téléchargement manquante"
        
        download_url = update_info['download_url']
        
        try:
            # Créer un fichier temporaire pour le téléchargement
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                # Créer un contexte SSL pour ignorer les erreurs de certificat en développement
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                # Télécharger le fichier
                with urllib.request.urlopen(download_url, context=ctx) as response:
                    if response.status != 200:
                        return False, f"Erreur HTTP {response.status} {response.reason}"
                    
                    # Lire le contenu et l'écrire dans le fichier temporaire
                    content = response.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name
            
            # Vérifier le checksum si disponible
            if 'checksum' in update_info:
                actual_checksum = hashlib.sha256(content).hexdigest()
                expected_checksum = update_info['checksum']
                
                if actual_checksum != expected_checksum:
                    # Supprimer le fichier téléchargé si le checksum ne correspond pas
                    os.unlink(temp_file_path)
                    return False, "Checksum invalide, le fichier peut être corrompu ou altéré"
            
            # Vérifier la signature si disponible
            if 'security' in self.config and self.config['security'].get('signature_required', False):
                if 'signature' in update_info and 'public_key' in self.config['security']:
                    # Cette vérification serait à implémenter selon les besoins spécifiques
                    pass
            
            # Enregistrer l'information dans le fichier de log
            try:
                with open(self.update_log_path, 'a', encoding='utf-8') as f:
                    log_entry = f"{datetime.datetime.now().isoformat()} - Mise à jour téléchargée: {update_info.get('latest_version', 'inconnu')}\n"
                    f.write(log_entry)
            except Exception as e:
                logger.error(f"Erreur lors de l'écriture dans le fichier de log des mises à jour: {e}")
            
            return True, temp_file_path
        
        except (URLError, HTTPError) as e:
            logger.error(f"Erreur de connexion lors du téléchargement de la mise à jour: {e}")
            return False, f"Erreur de connexion: {str(e)}"
        
        except Exception as e:
            logger.error(f"Erreur inattendue lors du téléchargement de la mise à jour: {e}")
            return False, f"Erreur inattendue: {str(e)}"
    
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
                    return False, f"Période maximale hors ligne dépassée ({max_offline_days} jours). Veuillez vous connecter pour vérifier votre licence.", {}
            
            # Vérifier avec les informations locales uniquement
            is_valid, message, license_data = verify_license(email, license_key)
            return is_valid, message, license_data
        
        # Vérifier dans la configuration distante
        if 'licences' in self.config and email in self.config['licences']:
            remote_license = self.config['licences'][email]
            
            # Vérifier le statut
            if remote_license.get('status') == 'blocked':
                logger.warning(f"Licence bloquée pour {email}")
                return False, "Licence bloquée par l'administrateur.", remote_license
            
            # Vérifier la date d'expiration
            expires_str = remote_license.get('expires')
            if expires_str:
                try:
                    expires_date = datetime.datetime.strptime(expires_str, "%Y-%m-%d").date()
                    today = datetime.datetime.now().date()
                    
                    if expires_date < today:
                        logger.warning(f"Licence expirée pour {email} (expirée le {expires_str})")
                        return False, f"Licence expirée le {expires_str}.", remote_license
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
                return False, message, license_data
        
        # Si la licence n'est pas dans la configuration distante, vérifier localement
        logger.info(f"Licence non trouvée dans la configuration distante pour {email}, vérification locale")
        is_valid, message, license_data = verify_license(email, license_key)
        return is_valid, message, license_data
    
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
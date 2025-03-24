#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour la synchronisation des fichiers de configuration avec Google Drive.
Permet de télécharger et de vérifier automatiquement les mises à jour du fichier de configuration
à partir d'un lien de partage Google Drive.
"""

import os
import time
import json
import threading
import logging
import ssl
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Tuple, List

logger = logging.getLogger("VynalDocsAutomator.GoogleDriveSync")

class GoogleDriveSync:
    """
    Classe pour gérer la synchronisation avec Google Drive.
    Surveille et télécharge les fichiers de configuration partagés via Google Drive.
    """
    
    def __init__(self, 
                 drive_file_id: str, 
                 local_dir: str, 
                 check_interval: int = 60, 
                 backup_count: int = 5):
        """
        Initialise le gestionnaire de synchronisation Google Drive.
        
        Args:
            drive_file_id: ID du fichier Google Drive à synchroniser
            local_dir: Répertoire local où stocker les fichiers téléchargés
            check_interval: Intervalle de vérification en secondes (défaut: 60 secondes = 1 minute)
            backup_count: Nombre de sauvegardes à conserver
        """
        self.drive_file_id = drive_file_id
        self.local_dir = local_dir
        self.check_interval = check_interval
        self.backup_count = backup_count
        
        # Assurer que le répertoire local existe
        os.makedirs(self.local_dir, exist_ok=True)
        
        # Fichier de configuration principal
        self.config_file = os.path.join(self.local_dir, "current_config.json")
        
        # Variables pour le suivi des changements
        self.last_check_time = 0
        self.last_modified = 0
        self.sync_active = False
        self.sync_thread = None
        self.current_config = {}
        self.file_url = self._build_direct_link()
        
        # Callbacks
        self.on_config_updated = None  # Callback appelé quand la config est mise à jour
        self.on_sync_error = None      # Callback appelé en cas d'erreur
        
        # Charger la configuration initiale si elle existe
        self._load_config()
        
        logger.info(f"GoogleDriveSync initialisé avec un intervalle de {check_interval} secondes")
    
    def _build_direct_link(self) -> str:
        """
        Construit le lien direct pour télécharger le fichier depuis Google Drive.
        
        Returns:
            URL directe pour télécharger le fichier
        """
        return f"https://drive.google.com/uc?export=download&id={self.drive_file_id}"
    
    def _load_config(self) -> bool:
        """
        Charge la configuration locale si elle existe.
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        if not os.path.exists(self.config_file):
            logger.info("Aucun fichier de configuration local trouvé")
            return False
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.current_config = json.load(f)
            
            # Obtenir la date de dernière modification
            self.last_modified = os.path.getmtime(self.config_file)
            logger.info(f"Configuration chargée depuis {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration locale: {str(e)}")
            return False
    
    def _save_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde la configuration et crée une copie de sauvegarde.
        
        Args:
            config_data: Données de configuration à sauvegarder
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # Créer une sauvegarde de la configuration actuelle si elle existe
            if os.path.exists(self.config_file):
                # Format de nom: backup_YYYYMMDD_HHMMSS.json
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.local_dir, f"backup_{timestamp}.json")
                
                # Copier le fichier actuel vers la sauvegarde
                with open(self.config_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                logger.info(f"Sauvegarde créée: {backup_file}")
                
                # Nettoyer les anciennes sauvegardes
                self._cleanup_old_backups()
            
            # Sauvegarder la nouvelle configuration
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.current_config = config_data
            self.last_modified = time.time()
            
            logger.info(f"Configuration sauvegardée dans {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
            return False
    
    def _cleanup_old_backups(self) -> None:
        """
        Supprime les anciennes sauvegardes pour ne conserver que les plus récentes.
        """
        try:
            # Lister tous les fichiers de sauvegarde
            backup_files = [f for f in os.listdir(self.local_dir) 
                           if f.startswith("backup_") and f.endswith(".json")]
            
            # S'il y a plus de fichiers que la limite, supprimer les plus anciens
            if len(backup_files) > self.backup_count:
                # Trier par date (les plus anciens en premier)
                backup_files.sort()
                
                # Supprimer les fichiers en trop
                files_to_remove = backup_files[0:len(backup_files) - self.backup_count]
                for file in files_to_remove:
                    os.remove(os.path.join(self.local_dir, file))
                    logger.debug(f"Ancienne sauvegarde supprimée: {file}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des sauvegardes: {str(e)}")
    
    def _download_config(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Télécharge la dernière version du fichier de configuration depuis Google Drive.
        
        Returns:
            Tuple (succès, données de configuration)
        """
        try:
            # Créer un contexte SSL qui ignore les erreurs de certificat (utile pour les environnements restreints)
            context = ssl._create_unverified_context()
            
            # Effectuer la requête
            logger.debug(f"Téléchargement du fichier depuis: {self.file_url}")
            with urllib.request.urlopen(self.file_url, context=context, timeout=30) as response:
                # Lire et décoder la réponse
                content = response.read().decode('utf-8')
                
                # Vérifier que la réponse est un JSON valide
                config_data = json.loads(content)
                return True, config_data
                
        except urllib.error.URLError as e:
            logger.error(f"Erreur de connexion: {str(e)}")
            if self.on_sync_error:
                self.on_sync_error("Erreur de connexion", str(e))
            return False, {}
            
        except json.JSONDecodeError as e:
            logger.error(f"Format JSON invalide: {str(e)}")
            if self.on_sync_error:
                self.on_sync_error("Format JSON invalide", str(e))
            return False, {}
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {str(e)}")
            if self.on_sync_error:
                self.on_sync_error("Erreur de téléchargement", str(e))
            return False, {}
    
    def check_for_updates(self, force: bool = False) -> bool:
        """
        Vérifie s'il y a des mises à jour et télécharge la dernière version si nécessaire.
        
        Args:
            force: Force la vérification même si l'intervalle n'est pas écoulé
            
        Returns:
            True si une mise à jour a été trouvée et appliquée, False sinon
        """
        current_time = time.time()
        
        # Si l'intervalle n'est pas écoulé et que la vérification n'est pas forcée, ignorer
        if not force and (current_time - self.last_check_time) < self.check_interval:
            return False
            
        # Mettre à jour le timestamp de dernière vérification
        self.last_check_time = current_time
        
        # Télécharger la configuration
        success, new_config = self._download_config()
        if not success:
            return False
            
        # Vérifier si la configuration a changé
        if new_config == self.current_config:
            logger.debug("La configuration n'a pas changé")
            return False
            
        # Sauvegarder la nouvelle configuration
        if self._save_config(new_config):
            logger.info("Nouvelle configuration téléchargée et sauvegardée")
            
            # Notifier les observateurs
            if self.on_config_updated:
                self.on_config_updated(new_config)
                
            return True
        
        return False
    
    def _sync_thread_func(self) -> None:
        """
        Fonction exécutée dans le thread de synchronisation.
        Vérifie périodiquement les mises à jour.
        """
        logger.info("Thread de synchronisation démarré")
        
        while self.sync_active:
            try:
                # Vérifier les mises à jour
                self.check_for_updates()
                
                # Attendre l'intervalle spécifié
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Erreur dans le thread de synchronisation: {str(e)}")
                # En cas d'erreur, attendre un peu avant de réessayer
                time.sleep(10)
    
    def start_sync(self) -> bool:
        """
        Démarre la synchronisation automatique en arrière-plan.
        
        Returns:
            True si le thread a été démarré, False s'il était déjà en cours d'exécution
        """
        if self.sync_active and self.sync_thread and self.sync_thread.is_alive():
            logger.info("La synchronisation est déjà active")
            return False
            
        # Activer la synchronisation
        self.sync_active = True
        
        # Créer et démarrer le thread
        self.sync_thread = threading.Thread(
            target=self._sync_thread_func,
            daemon=True  # Le thread s'arrêtera quand le programme principal se terminera
        )
        self.sync_thread.start()
        
        logger.info(f"Synchronisation démarrée avec intervalle de {self.check_interval} secondes")
        return True
    
    def stop_sync(self) -> None:
        """
        Arrête la synchronisation automatique.
        """
        self.sync_active = False
        logger.info("Synchronisation arrêtée")
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration actuelle.
        
        Returns:
            Configuration actuelle
        """
        return self.current_config
    
    def get_user_config(self, user_id: str) -> Dict[str, Any]:
        """
        Extrait la configuration spécifique à un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Configuration spécifique à l'utilisateur ou un dictionnaire vide
        """
        if not self.current_config:
            return {}
            
        users = self.current_config.get("users", {})
        return users.get(user_id, {})
    
    def set_callback_on_update(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Définit la fonction à appeler lorsque la configuration est mise à jour.
        
        Args:
            callback: Fonction à appeler avec la nouvelle configuration
        """
        self.on_config_updated = callback
    
    def set_callback_on_error(self, callback: Callable[[str, str], None]) -> None:
        """
        Définit la fonction à appeler en cas d'erreur de synchronisation.
        
        Args:
            callback: Fonction à appeler avec le type d'erreur et le message
        """
        self.on_sync_error = callback 
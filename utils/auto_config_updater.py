#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour la vérification automatique des mises à jour de configuration.
Ce module permet de vérifier à intervalle régulier si la configuration Google Drive
a été mise à jour et d'appliquer automatiquement les changements.
"""

import os
import json
import time
import logging
import threading
import ssl
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional, Callable

# Importer la configuration globale
from config import CONFIG_CHECK_INTERVAL

# Configuration du logger
logger = logging.getLogger("VynalDocsAutomator.AutoConfigUpdater")

class AutoConfigUpdater:
    """
    Gère la vérification automatique des mises à jour de configuration.
    Vérifie périodiquement si le fichier de configuration sur Google Drive a été modifié.
    """
    
    def __init__(self, 
                 drive_file_id: str, 
                 local_config_path: str, 
                 check_interval: int = CONFIG_CHECK_INTERVAL,
                 root_window=None):
        """
        Initialise le vérificateur de configuration automatique.
        
        Args:
            drive_file_id: ID du fichier sur Google Drive
            local_config_path: Chemin vers le fichier de configuration local
            check_interval: Intervalle de vérification en secondes (défaut: valeur de CONFIG_CHECK_INTERVAL)
            root_window: Fenêtre principale de l'application (pour les notifications)
        """
        self.drive_file_id = drive_file_id
        self.local_config_path = local_config_path
        self.check_interval = check_interval
        self.last_check_time = 0
        self.last_modification_time = 0
        self.update_thread = None
        self.is_running = False
        self.on_update_callback = None
        self.root_window = root_window
        
        # Vérifier si le fichier local existe
        if os.path.exists(local_config_path):
            self.last_modification_time = os.path.getmtime(local_config_path)
        
        logger.info(f"AutoConfigUpdater initialisé: vérification toutes les {check_interval} secondes")
    
    def start(self) -> bool:
        """
        Démarre la vérification automatique en arrière-plan.
        
        Returns:
            True si le thread a démarré, False sinon
        """
        if self.is_running and self.update_thread and self.update_thread.is_alive():
            logger.info("La vérification automatique est déjà en cours d'exécution")
            return False
        
        # Activer la vérification
        self.is_running = True
        
        # Créer et démarrer le thread
        self.update_thread = threading.Thread(
            target=self._update_thread_func,
            daemon=True  # Le thread s'arrêtera quand le programme principal se terminera
        )
        self.update_thread.start()
        
        logger.info(f"Vérification automatique démarrée avec intervalle de {self.check_interval} secondes")
        return True
    
    def stop(self) -> None:
        """
        Arrête la vérification automatique.
        """
        self.is_running = False
        logger.info("Vérification automatique arrêtée")
    
    def set_update_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Définit le callback à appeler lorsqu'une mise à jour est détectée.
        
        Args:
            callback: Fonction à appeler avec la nouvelle configuration
        """
        self.on_update_callback = callback
    
    def _update_thread_func(self) -> None:
        """
        Fonction exécutée dans le thread de vérification.
        Vérifie périodiquement les mises à jour.
        """
        logger.info("Thread de vérification automatique démarré")
        
        try:
            # Force une vérification au démarrage
            self.check_for_updates(force=True)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification initiale: {str(e)}")
        
        while self.is_running:
            try:
                # Vérifier les mises à jour
                self.check_for_updates()
                
                # Attendre l'intervalle spécifié
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Erreur dans le thread de vérification: {str(e)}")
                # En cas d'erreur, attendre un peu avant de réessayer
                time.sleep(10)
    
    def _show_notification(self, title: str, message: str, message_type: str = "info") -> None:
        """
        Affiche une notification avec l'icône appropriée selon le type de message.
        
        Args:
            title: Titre de la notification
            message: Contenu du message
            message_type: Type de message ("info", "warning", "error")
        """
        try:
            # Importer tkinter dans une fonction pour éviter les dépendances inutiles
            import tkinter as tk
            from tkinter import messagebox
            import threading
            
            # Utiliser un thread pour éviter de bloquer
            def show_notification():
                try:
                    # Utiliser la fenêtre principale si disponible
                    if self.root_window and isinstance(self.root_window, tk.Tk):
                        root = self.root_window
                    else:
                        # Créer une fenêtre temporaire si aucune fenêtre principale n'est disponible
                        root = tk.Tk()
                        root.withdraw()
                    
                    # Déterminer l'icône appropriée
                    icon = message_type
                    
                    # Afficher la notification avec l'icône appropriée
                    if message_type == "info":
                        messagebox.showinfo(title, message, icon=icon, parent=root)
                    elif message_type == "warning":
                        messagebox.showwarning(title, message, icon=icon, parent=root)
                    elif message_type == "error":
                        messagebox.showerror(title, message, icon=icon, parent=root)
                    else:
                        messagebox.showinfo(title, message, icon=icon, parent=root)
                    
                    # Si nous avons créé une fenêtre temporaire, la détruire
                    if not self.root_window:
                        root.destroy()
                        
                except Exception as e:
                    logger.error(f"Erreur lors de l'affichage de la notification: {e}")
            
            # Lancer la notification dans un thread séparé
            notification_thread = threading.Thread(target=show_notification)
            notification_thread.daemon = True
            notification_thread.start()
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la notification: {e}")

    def check_for_updates(self, force: bool = False) -> bool:
        """
        Vérifie si des mises à jour sont disponibles et télécharge la configuration si nécessaire.
        
        Args:
            force: Force la vérification même si l'intervalle n'est pas écoulé
        
        Returns:
            True si une mise à jour a été appliquée, False sinon
        """
        current_time = time.time()
        
        # Vérifier si l'intervalle est écoulé ou si la vérification est forcée
        if not force and (current_time - self.last_check_time) < self.check_interval:
            logger.debug(f"Vérification ignorée (prochain check dans {int(self.check_interval - (current_time - self.last_check_time))}s)")
            return False
        
        # Mettre à jour le temps de la dernière vérification
        self.last_check_time = current_time
        
        try:
            logger.debug(f"Début de la vérification des mises à jour (ID: {self.drive_file_id})")
            
            # Télécharger et vérifier la configuration
            new_config = self._download_config()
            if not new_config:
                logger.warning("Impossible de télécharger la configuration")
                self._show_notification(
                    "Erreur de configuration",
                    "Impossible de télécharger la configuration depuis Google Drive.\nVeuillez vérifier votre connexion.",
                    "error"
                )
                return False
            
            logger.debug(f"Configuration téléchargée ({len(json.dumps(new_config))} octets)")
            
            # Vérifier si la configuration locale existe
            current_config = {}
            if os.path.exists(self.local_config_path):
                with open(self.local_config_path, 'r', encoding='utf-8') as f:
                    current_config = json.load(f)
            
            # Comparer les configurations
            if new_config == current_config:
                logger.debug("Aucune différence détectée dans la configuration")
                return False
            
            # Journaliser les différences (uniquement les clés de premier niveau)
            if logger.isEnabledFor(logging.DEBUG):
                old_keys = set(current_config.keys())
                new_keys = set(new_config.keys())
                added_keys = new_keys - old_keys
                removed_keys = old_keys - new_keys
                changed_keys = {k for k in old_keys.intersection(new_keys) 
                               if current_config[k] != new_config[k]}
                
                if added_keys:
                    logger.debug(f"Clés ajoutées: {', '.join(added_keys)}")
                if removed_keys:
                    logger.debug(f"Clés supprimées: {', '.join(removed_keys)}")
                if changed_keys:
                    logger.debug(f"Clés modifiées: {', '.join(changed_keys)}")
            
            # Sauvegarder l'ancienne configuration si elle existe
            if os.path.exists(self.local_config_path):
                backup_dir = os.path.dirname(self.local_config_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(backup_dir, f"config_backup_{timestamp}.json")
                
                with open(self.local_config_path, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                logger.info(f"Sauvegarde de l'ancienne configuration créée: {backup_file}")
            
            # Enregistrer la nouvelle configuration
            with open(self.local_config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            
            # Mettre à jour le temps de dernière modification
            self.last_modification_time = os.path.getmtime(self.local_config_path)
            
            logger.info("Configuration mise à jour avec succès")
            
            # Afficher une notification de succès
            self._show_notification(
                "Configuration mise à jour",
                "La configuration a été mise à jour depuis Google Drive.\n\nLes nouveaux paramètres sont maintenant actifs.",
                "info"
            )
            
            # Appeler le callback si défini
            if self.on_update_callback:
                logger.debug("Appel du callback de mise à jour")
                self.on_update_callback(new_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des mises à jour: {str(e)}")
            self._show_notification(
                "Erreur de configuration",
                f"Une erreur est survenue lors de la mise à jour de la configuration:\n{str(e)}",
                "error"
            )
            return False
    
    def _download_config(self) -> Optional[Dict[str, Any]]:
        """
        Télécharge la configuration depuis Google Drive.
        
        Returns:
            La configuration téléchargée ou None en cas d'erreur
        """
        if not self.drive_file_id:
            logger.warning("Aucun ID de fichier Google Drive configuré")
            return None
        
        try:
            # Construire l'URL directe
            url = f"https://drive.google.com/uc?export=download&id={self.drive_file_id}"
            
            # Créer un contexte SSL qui ignore les erreurs de certificat
            context = ssl._create_unverified_context()
            
            # Télécharger le fichier
            logger.debug(f"Téléchargement de la configuration depuis: {url}")
            with urllib.request.urlopen(url, context=context, timeout=30) as response:
                content = response.read().decode('utf-8')
                
                # Vérifier que la réponse est un JSON valide
                config_data = json.loads(content)
                return config_data
                
        except urllib.error.URLError as e:
            logger.error(f"Erreur de connexion: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Format JSON invalide: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {str(e)}")
        
        return None


# Exemple d'utilisation:
if __name__ == "__main__":
    # Configuration du logging pour les tests
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Exemple d'ID de fichier Google Drive
    drive_file_id = "your_drive_file_id_here"
    
    # Créer le vérificateur
    updater = AutoConfigUpdater(drive_file_id, "config/auto_updated_config.json")
    
    # Définir un callback pour les mises à jour
    def on_config_updated(new_config):
        print(f"Nouvelle configuration détectée: {len(new_config)} éléments")
    
    updater.set_update_callback(on_config_updated)
    
    # Démarrer la vérification
    updater.start()
    
    # Garder le programme en cours d'exécution pour les tests
    try:
        print("Vérification des mises à jour en cours...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt de la vérification...")
        updater.stop() 
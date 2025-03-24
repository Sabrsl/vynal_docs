#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des notifications pour l'application.
"""

import tkinter as tk
from tkinter import ttk
import logging
import threading
import queue
import time
from typing import Optional, Dict, Any
import sys

logger = logging.getLogger("VynalDocsAutomator.Notification")

class NotificationManager:
    """Gestionnaire de notifications global"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NotificationManager, cls).__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.notification_queue = queue.Queue()
            self.notification_window = None
            self.notification_thread = None
            self.root = None
            self.initialized = True
            logger.info("NotificationManager initialisé")
    
    def initialize(self, root: Optional[tk.Tk] = None) -> None:
        """
        Initialise le gestionnaire de notifications avec une fenêtre racine.
        
        Args:
            root (Optional[tk.Tk]): Fenêtre racine Tkinter
        """
        try:
            if root is None:
                # Créer une fenêtre racine si aucune n'est fournie
                self.root = tk.Tk()
                self.root.withdraw()  # Cacher la fenêtre racine
            else:
                self.root = root
            
            logger.info("NotificationManager initialisé avec la fenêtre racine")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du NotificationManager: {e}")
    
    def show_notification(self, title: str, message: str, message_type: str = "info", duration: int = 5000) -> None:
        """
        Affiche une notification.
        
        Args:
            title (str): Titre de la notification
            message (str): Message de la notification
            message_type (str, optional): Type de notification (info, warning, error). Defaults to "info".
            duration (int, optional): Durée d'affichage en ms. Defaults to 5000.
        """
        try:
            # S'assurer que le gestionnaire est initialisé
            if self.root is None:
                self.initialize()
            
            notification = {
                'title': title,
                'message': message,
                'type': message_type,
                'duration': duration
            }
            
            logger.info(f"Notification en attente: {title} - {message}")
            self.notification_queue.put(notification)
            
            # Démarrer le thread de notification si nécessaire
            if self.notification_thread is None or not self.notification_thread.is_alive():
                self.notification_thread = threading.Thread(target=self._process_notifications, daemon=True)
                self.notification_thread.start()
                logger.info("Thread de notification démarré")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la notification: {e}")
    
    def _process_notifications(self) -> None:
        """Traite la file d'attente des notifications"""
        while True:
            try:
                notification = self.notification_queue.get()
                logger.info(f"Traitement de la notification: {notification['title']}")
                self._show_notification_window(notification)
                self.notification_queue.task_done()
                time.sleep(0.1)  # Petit délai entre les notifications
            except Exception as e:
                logger.error(f"Erreur lors du traitement des notifications: {e}")
                time.sleep(1)  # Délai plus long en cas d'erreur
    
    def _show_notification_window(self, notification: Dict[str, Any]) -> None:
        """
        Affiche une fenêtre de notification.
        
        Args:
            notification (Dict[str, Any]): Données de la notification
        """
        try:
            # Créer une nouvelle fenêtre de notification
            window = tk.Toplevel(self.root)
            window.title(notification['title'])
            
            # Positionner la fenêtre en haut à droite
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            window_width = 300
            window_height = 100
            x = screen_width - window_width - 20
            y = 20
            window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Configurer le style selon le type de notification
            style = ttk.Style()
            if notification['type'] == 'error':
                style.configure('Notification.TFrame', background='#ffebee')
            elif notification['type'] == 'warning':
                style.configure('Notification.TFrame', background='#fff3e0')
            else:
                style.configure('Notification.TFrame', background='#e3f2fd')
            
            # Créer le conteneur principal
            frame = ttk.Frame(window, style='Notification.TFrame', padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Titre
            title_label = ttk.Label(
                frame,
                text=notification['title'],
                font=('Helvetica', 10, 'bold')
            )
            title_label.pack(anchor='w')
            
            # Message
            message_label = ttk.Label(
                frame,
                text=notification['message'],
                wraplength=window_width - 20
            )
            message_label.pack(anchor='w', pady=(5, 0))
            
            # Bouton de fermeture
            close_button = ttk.Button(
                frame,
                text="Fermer",
                command=window.destroy
            )
            close_button.pack(side=tk.BOTTOM, pady=(10, 0))
            
            # Fermer automatiquement après la durée spécifiée
            window.after(notification['duration'], window.destroy)
            
            # Garder la fenêtre au premier plan
            window.attributes('-topmost', True)
            
            # Gérer la fermeture de la fenêtre
            window.protocol("WM_DELETE_WINDOW", window.destroy)
            
            logger.info(f"Fenêtre de notification affichée: {notification['title']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la fenêtre de notification: {e}")

# Instance globale du gestionnaire de notifications
notification_manager = NotificationManager()

def show_notification(title: str, message: str, message_type: str = "info", duration: int = 5000) -> None:
    """
    Fonction utilitaire pour afficher une notification.
    
    Args:
        title (str): Titre de la notification
        message (str): Message de la notification
        message_type (str, optional): Type de notification (info, warning, error). Defaults to "info".
        duration (int, optional): Durée d'affichage en ms. Defaults to 5000.
    """
    try:
        logger.info(f"Tentative d'affichage de notification: {title}")
        notification_manager.show_notification(title, message, message_type, duration)
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de la notification: {e}") 
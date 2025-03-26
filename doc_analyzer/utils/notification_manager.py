import tkinter as tk
from tkinter import ttk
import queue
import threading
import logging
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gestionnaire centralisé des notifications."""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        Initialise le gestionnaire de notifications.
        
        Args:
            root: Fenêtre principale Tkinter (optionnel)
        """
        self.root = root
        self.notification_queue = queue.Queue()
        self.notification_window = None
        self.notification_thread = threading.Thread(target=self._process_notifications, daemon=True)
        self.notification_thread.start()
        logger.info("NotificationManager initialisé")
    
    def _process_notifications(self):
        """Traite la file d'attente des notifications."""
        while True:
            try:
                title, message = self.notification_queue.get()
                self._show_notification(title, message)
            except Exception as e:
                logger.error(f"Erreur lors du traitement des notifications : {e}")
            finally:
                self.notification_queue.task_done()
    
    def _show_notification(self, title: str, message: str):
        """Affiche une notification."""
        if self.root:
            # Créer une fenêtre de notification
            self.notification_window = tk.Toplevel(self.root)
            self.notification_window.overrideredirect(True)  # Supprime les bordures
            
            # Positionner la fenêtre en haut à droite
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = 400
            window_height = 300
            x = screen_width - window_width - 20
            y = 20
            self.notification_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Style
            self.notification_window.configure(bg='#2c3e50')
            
            # Titre
            title_frame = ttk.Frame(self.notification_window)
            title_frame.pack(fill='x', padx=10, pady=5)
            title_label = ttk.Label(
                title_frame,
                text=title,
                font=('Helvetica', 12, 'bold'),
                foreground='white',
                background='#2c3e50'
            )
            title_label.pack(side='left')
            
            # Bouton de fermeture
            close_btn = ttk.Button(
                title_frame,
                text='×',
                command=self.notification_window.destroy,
                width=3
            )
            close_btn.pack(side='right')
            
            # Message
            message_frame = ttk.Frame(self.notification_window)
            message_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            # Zone de texte avec défilement
            text_widget = tk.Text(
                message_frame,
                wrap='word',
                font=('Helvetica', 10),
                bg='#34495e',
                fg='white',
                padx=10,
                pady=10
            )
            text_widget.pack(fill='both', expand=True)
            text_widget.insert('1.0', message)
            text_widget.configure(state='disabled')
            
            # Barre de défilement
            scrollbar = ttk.Scrollbar(message_frame, orient='vertical', command=text_widget.yview)
            scrollbar.pack(side='right', fill='y')
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # Auto-fermeture après 10 secondes
            self.notification_window.after(10000, self.notification_window.destroy)
            
            # Rendre la fenêtre toujours au premier plan
            self.notification_window.attributes('-topmost', True)
            
            # Ajouter des effets de survol
            def on_enter(e):
                self.notification_window.attributes('-alpha', 1.0)
            
            def on_leave(e):
                self.notification_window.attributes('-alpha', 0.8)
            
            self.notification_window.bind('<Enter>', on_enter)
            self.notification_window.bind('<Leave>', on_leave)
            
            # Animation d'apparition
            self.notification_window.attributes('-alpha', 0.0)
            self._fade_in()
        else:
            # Fallback : affichage console
            print("\n" + "="*50)
            print(f"📢 {title}")
            print("-"*50)
            print(message)
            print("="*50 + "\n")
    
    def _fade_in(self, alpha: float = 0.0):
        """Animation de fondu à l'apparition."""
        if alpha < 1.0:
            self.notification_window.attributes('-alpha', alpha)
            self.notification_window.after(50, lambda: self._fade_in(alpha + 0.1))
    
    def show_notification(self, title: str, message: str):
        """
        Ajoute une notification à la file d'attente.
        
        Args:
            title (str): Titre de la notification
            message (str): Message de la notification
        """
        self.notification_queue.put((title, message))
    
    def stop(self):
        """Arrête le gestionnaire de notifications."""
        self.notification_thread.join(timeout=1)
        if self.notification_window:
            self.notification_window.destroy()
        logger.info("NotificationManager arrêté") 
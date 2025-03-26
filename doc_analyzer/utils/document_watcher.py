import time
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from pathlib import Path
import threading
import queue
import hashlib
from docx import Document
from PyPDF2 import PdfReader
import io

from .document_analyzer import DocumentAnalyzer
from .notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class DocumentWatcher(FileSystemEventHandler):
    """
    Classe pour surveiller les modifications de documents et déclencher leur analyse.
    """
    
    def __init__(self, cache_dir: str = ".cache", root_window=None):
        """
        Initialise le surveillant de documents.
        
        Args:
            cache_dir (str): Dossier pour stocker le cache des analyses
            root_window: Fenêtre principale Tkinter (optionnel)
        """
        super().__init__()
        # Initialisation du verrou en premier
        self.lock = threading.Lock()
        
        # Initialisation des autres attributs
        self.analyzer = DocumentAnalyzer()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "analysis_cache.json"
        
        # Initialisation du gestionnaire de notifications
        self.notification_manager = NotificationManager(root_window)
        
        # File d'attente pour les analyses
        self.analysis_queue = queue.Queue()
        self.analysis_thread = threading.Thread(target=self._process_analysis_queue, daemon=True)
        self.analysis_thread.start()
        
        # Formats de fichiers supportés
        self.supported_extensions = {
            '.txt': self._read_text_file,
            '.docx': self._read_docx_file,
            '.pdf': self._read_pdf_file,
            '.md': self._read_text_file,
            '.rtf': self._read_text_file
        }
        
        # Initialisation de l'observateur
        self.observer = Observer()
        self.observer.schedule(self, path=str(self.cache_dir.parent), recursive=True)
        self.observer.start()
        
        # Chargement du cache après l'initialisation du verrou
        self.cache = self._load_cache()
        
        logger.info("DocumentWatcher initialisé")
    
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """
        Charge le cache des analyses précédentes.
        
        Returns:
            Dict[str, Dict[str, Any]]: Cache des analyses
        """
        with self.lock:
            if self.cache_file.exists():
                try:
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Erreur lors du chargement du cache : {e}")
                    return {}
            return {}
    
    def _save_cache(self):
        """Sauvegarde le cache des analyses."""
        with self.lock:
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde du cache : {e}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """
        Calcule un hash MD5 du fichier.
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            str: Hash MD5 du fichier
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Erreur lors du calcul du hash pour {file_path}: {e}")
            return ""
    
    def _should_analyze(self, file_path: str) -> bool:
        """
        Vérifie si le fichier doit être analysé.
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            bool: True si le fichier doit être analysé
        """
        # Vérifier l'extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_extensions:
            return False
        
        # Vérifier le cache
        file_hash = self._get_file_hash(file_path)
        with self.lock:
            cached_data = self.cache.get(file_path, {})
            if cached_data.get('hash') == file_hash:
                logger.debug(f"Fichier {file_path} inchangé, analyse ignorée")
                return False
        
        return True
    
    def _read_text_file(self, file_path: str) -> str:
        """Lit un fichier texte."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Essayer d'autres encodages
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Impossible de lire le fichier {file_path} avec les encodages supportés")
    
    def _read_docx_file(self, file_path: str) -> str:
        """Lit un fichier DOCX."""
        try:
            doc = Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier DOCX {file_path}: {e}")
            raise
    
    def _read_pdf_file(self, file_path: str) -> str:
        """Lit un fichier PDF."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier PDF {file_path}: {e}")
            raise
    
    def on_modified(self, event):
        """
        Gère les événements de modification de fichier.
        
        Args:
            event: Événement de modification
        """
        if not event.is_directory:
            self.analysis_queue.put(('modified', event.src_path))
    
    def on_created(self, event):
        """
        Gère les événements de création de fichier.
        
        Args:
            event: Événement de création
        """
        if not event.is_directory:
            self.analysis_queue.put(('created', event.src_path))
    
    def _process_analysis_queue(self):
        """Traite la file d'attente des analyses."""
        while True:
            try:
                event_type, file_path = self.analysis_queue.get()
                self._handle_file_event(file_path)
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la file d'attente : {e}")
            finally:
                self.analysis_queue.task_done()
    
    def wait_for_analysis(self, timeout: float = 5.0) -> bool:
        """
        Attend que toutes les analyses en cours soient terminées.
        
        Args:
            timeout (float): Temps maximum d'attente en secondes
            
        Returns:
            bool: True si toutes les analyses sont terminées, False si timeout
        """
        try:
            self.analysis_queue.join(timeout=timeout)
            return True
        except TimeoutError:
            logger.warning("Timeout en attendant la fin des analyses")
            return False
    
    def _handle_file_event(self, file_path: str):
        """
        Traite un événement de fichier.
        
        Args:
            file_path (str): Chemin du fichier
        """
        if not self._should_analyze(file_path):
            return
        
        try:
            logger.info(f"Analyse du fichier : {file_path}")
            
            # Lire le contenu du fichier selon son type
            ext = os.path.splitext(file_path)[1].lower()
            read_func = self.supported_extensions.get(ext)
            if not read_func:
                logger.warning(f"Format de fichier non supporté : {ext}")
                return
            
            contenu = read_func(file_path)
            
            # Analyser le document
            rapport = self.analyzer.analyser_document(contenu)
            
            # Mettre à jour le cache
            with self.lock:
                self.cache[file_path] = {
                    'hash': self._get_file_hash(file_path),
                    'last_analysis': datetime.now().isoformat(),
                    'rapport': rapport
                }
                self._save_cache()
            
            # Générer une notification si nécessaire
            self._generate_notification(file_path, rapport)
            
            logger.info(f"Analyse terminée pour {file_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {file_path} : {e}")
    
    def _generate_notification(self, file_path: str, rapport: Dict[str, Any]):
        """
        Génère une notification si nécessaire.
        
        Args:
            file_path (str): Chemin du fichier
            rapport (Dict[str, Any]): Rapport d'analyse
        """
        nom_fichier = os.path.basename(file_path)
        messages = []
        
        # Vérifier les alertes d'échéance
        if rapport.get('alertes'):
            messages.append("📅 Échéances proches :")
            for alerte in rapport['alertes']:
                messages.append(f"  • {alerte}")
        
        # Vérifier les zones incomplètes
        if rapport.get('zones_incomplètes'):
            messages.append("\n📝 Champs à compléter :")
            for zone in rapport['zones_incomplètes']:
                messages.append(f"  • {zone}")
        
        # Vérifier les informations importantes
        if rapport.get('informations_extraites'):
            infos = rapport['informations_extraites']
            messages.append("\nℹ️ Informations détectées :")
            if infos.get('siret'):
                messages.append(f"  • SIRET : {infos['siret']}")
            if infos.get('montant'):
                messages.append(f"  • Montant : {infos['montant']}€")
            if infos.get('adresse'):
                messages.append(f"  • Adresse : {infos['adresse']}")
            if infos.get('email'):
                messages.append(f"  • Email : {infos['email']}")
            if infos.get('telephone'):
                messages.append(f"  • Téléphone : {infos['telephone']}")
            if infos.get('iban'):
                messages.append(f"  • IBAN : {infos['iban']}")
        
        # Vérifier les dates importantes
        if rapport.get('dates_trouvees'):
            messages.append("\n📆 Dates importantes :")
            for date in rapport['dates_trouvees']:
                messages.append(f"  • {date}")
        
        # Si des messages ont été générés, afficher la notification
        if messages:
            titre = f"📄 Analyse du document : {nom_fichier}"
            message = "\n".join(messages)
            self._show_notification(titre, message)
    
    def _show_notification(self, title: str, message: str):
        """
        Affiche une notification système.
        
        Args:
            title (str): Titre de la notification
            message (str): Message de la notification
        """
        self.notification_manager.show_notification(title, message)

    def stop(self):
        """Arrête la surveillance des fichiers."""
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        if hasattr(self, 'analysis_thread'):
            self.analysis_queue.join()  # Attendre que toutes les analyses soient terminées
        if hasattr(self, 'notification_manager'):
            self.notification_manager.stop()
        logger.info("DocumentWatcher arrêté")

def start_watching(modeles_dir: str = "./data/modeles", documents_dir: str = "./data/documents"):
    """
    Démarre la surveillance des dossiers.
    
    Args:
        modeles_dir (str): Dossier des modèles
        documents_dir (str): Dossier des documents
    """
    # Créer les dossiers s'ils n'existent pas
    os.makedirs(modeles_dir, exist_ok=True)
    os.makedirs(documents_dir, exist_ok=True)
    
    # Initialiser l'observateur
    observer = Observer()
    event_handler = DocumentWatcher()
    
    # Ajouter les dossiers à surveiller
    observer.schedule(event_handler, path=modeles_dir, recursive=True)
    observer.schedule(event_handler, path=documents_dir, recursive=True)
    
    # Démarrer la surveillance
    observer.start()
    logger.info(f"👁️ Surveillance active des dossiers :\n- {modeles_dir}\n- {documents_dir}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Surveillance arrêtée")
    
    observer.join()

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Démarrer la surveillance
    start_watching() 
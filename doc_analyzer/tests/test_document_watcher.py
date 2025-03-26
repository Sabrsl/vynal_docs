import os
import time
import shutil
import tempfile
import logging
import unittest
from unittest.mock import patch
from pathlib import Path
import tkinter as tk
from docx import Document
from PyPDF2 import PdfWriter

from doc_analyzer.utils.document_watcher import DocumentWatcher

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDocumentWatcher(unittest.TestCase):
    """Tests pour le DocumentWatcher."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Créer un dossier temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.modeles_dir = os.path.join(self.temp_dir, "modeles")
        self.documents_dir = os.path.join(self.temp_dir, "documents")
        os.makedirs(self.modeles_dir)
        os.makedirs(self.documents_dir)
        
        # Créer une fenêtre Tkinter pour les notifications
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre principale
        
        # Initialiser le DocumentWatcher
        self.watcher = DocumentWatcher(
            cache_dir=os.path.join(self.temp_dir, ".cache"),
            root_window=self.root
        )
        
        logger.info(f"Dossiers de test créés :\n- {self.modeles_dir}\n- {self.documents_dir}")
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        # Arrêter le watcher
        self.watcher.stop()
        
        # Nettoyer les fichiers temporaires
        shutil.rmtree(self.temp_dir)
        
        # Fermer la fenêtre Tkinter
        self.root.destroy()
        
        logger.info("Nettoyage des fichiers temporaires effectué")
    
    def test_creation_fichier_texte(self):
        """Test de la création d'un fichier texte."""
        # Créer un fichier texte avec des informations
        fichier = os.path.join(self.documents_dir, "test.txt")
        contenu = """
        Date : 15/03/2024
        Montant : 1500€
        SIRET : 12345678901234
        Email : test@example.com
        """
        with open(fichier, "w", encoding="utf-8") as f:
            f.write(contenu)
        
        # Attendre l'analyse
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Vérifier que le fichier a été analysé
        self.assertTrue(fichier in self.watcher.cache)
        rapport = self.watcher.cache[fichier]["rapport"]
        
        # Vérifier les informations extraites
        self.assertIn("informations_extraites", rapport)
        infos = rapport["informations_extraites"]
        self.assertEqual(infos["montant"], "1500€")
        self.assertEqual(infos["siret"], "12345678901234")
        self.assertEqual(infos["email"], "test@example.com")
    
    def test_modification_fichier(self):
        """Test de la modification d'un fichier."""
        # Créer un fichier initial
        fichier = os.path.join(self.documents_dir, "modif.txt")
        with open(fichier, "w", encoding="utf-8") as f:
            f.write("Version 1")
        
        # Attendre l'analyse initiale
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Sauvegarder le hash initial
        hash_initial = self.watcher.cache[fichier]["hash"]
        
        # Modifier le fichier
        with open(fichier, "w", encoding="utf-8") as f:
            f.write("Version 2")
        
        # Attendre la nouvelle analyse
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Vérifier que le hash a changé
        self.assertNotEqual(hash_initial, self.watcher.cache[fichier]["hash"])
    
    def test_champs_vides(self):
        """Test de la détection des champs vides."""
        fichier = os.path.join(self.documents_dir, "incomplet.txt")
        contenu = """
        Nom : 
        Date : 20/03/2024
        Montant : 
        """
        with open(fichier, "w", encoding="utf-8") as f:
            f.write(contenu)
        
        # Attendre l'analyse
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Vérifier la détection des champs vides
        rapport = self.watcher.cache[fichier]["rapport"]
        self.assertIn("zones_incomplètes", rapport)
        zones_vides = rapport["zones_incomplètes"]
        self.assertIn("Nom", zones_vides)
        self.assertIn("Montant", zones_vides)
    
    def test_formats_multiples(self):
        """Test de la gestion des différents formats de fichiers."""
        # Test PDF
        pdf_file = os.path.join(self.documents_dir, "test.pdf")
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(pdf_file, "wb") as f:
            writer.write(f)
        
        # Test DOCX
        docx_file = os.path.join(self.documents_dir, "test.docx")
        doc = Document()
        doc.add_paragraph("Test DOCX")
        doc.save(docx_file)
        
        # Attendre les analyses
        time.sleep(2)
        self.watcher.wait_for_analysis()
        
        # Vérifier que les fichiers ont été analysés
        self.assertIn(pdf_file, self.watcher.cache)
        self.assertIn(docx_file, self.watcher.cache)
    
    def test_notifications(self):
        """Test du système de notifications."""
        fichier = os.path.join(self.documents_dir, "notification.txt")
        contenu = """
        Date d'échéance : 25/03/2024
        Montant : 2000€
        """
        with open(fichier, "w", encoding="utf-8") as f:
            f.write(contenu)
        
        # Attendre l'analyse
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Vérifier que le rapport contient les informations nécessaires
        rapport = self.watcher.cache[fichier]["rapport"]
        self.assertIn("informations_extraites", rapport)
        self.assertIn("dates_trouvees", rapport)
    
    def test_cache(self):
        """Test du système de cache."""
        fichier = os.path.join(self.documents_dir, "cache.txt")
        contenu = "Test de cache"
        with open(fichier, "w", encoding="utf-8") as f:
            f.write(contenu)
        
        # Première analyse
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Vérifier que le hash est stocké
        self.assertIn("hash", self.watcher.cache[fichier])
        
        # Deuxième analyse (sans modification)
        self.watcher._handle_file_event(fichier)
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Vérifier que le hash n'a pas changé
        hash_initial = self.watcher.cache[fichier]["hash"]
        self.assertEqual(hash_initial, self.watcher._get_file_hash(fichier))
    
    def test_encodages(self):
        """Test de la gestion des différents encodages."""
        # Test UTF-8
        fichier_utf8 = os.path.join(self.documents_dir, "utf8.txt")
        with open(fichier_utf8, "w", encoding="utf-8") as f:
            f.write("Test UTF-8 : éèêë")
        
        # Test Latin-1
        fichier_latin1 = os.path.join(self.documents_dir, "latin1.txt")
        with open(fichier_latin1, "w", encoding="latin-1") as f:
            f.write("Test Latin-1 : éèêë")
        
        # Attendre les analyses
        time.sleep(2)
        self.watcher.wait_for_analysis()
        
        # Vérifier que les fichiers ont été analysés
        self.assertIn(fichier_utf8, self.watcher.cache)
        self.assertIn(fichier_latin1, self.watcher.cache)
    
    def test_surveillance_recursive(self):
        """Test de la surveillance récursive des dossiers."""
        # Créer un sous-dossier
        sous_dossier = os.path.join(self.documents_dir, "sous_dossier")
        os.makedirs(sous_dossier)
        
        # Créer un fichier dans le sous-dossier
        fichier = os.path.join(sous_dossier, "test.txt")
        with open(fichier, "w", encoding="utf-8") as f:
            f.write("Test dans sous-dossier")
        
        # Attendre l'analyse
        time.sleep(1)
        self.watcher.wait_for_analysis()
        
        # Vérifier que le fichier a été analysé
        self.assertIn(fichier, self.watcher.cache)

def run_tests():
    """Lance tous les tests."""
    # Créer un dossier temporaire pour les tests
    with tempfile.TemporaryDirectory() as temp_dir:
        # Configurer les dossiers de test
        os.environ["TEST_MODELES_DIR"] = os.path.join(temp_dir, "modeles")
        os.environ["TEST_DOCUMENTS_DIR"] = os.path.join(temp_dir, "documents")
        
        # Lancer les tests
        unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests() 
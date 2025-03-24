#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests pour vérifier les limitations de la version gratuite
"""

import unittest
import os
import shutil
import json
import tempfile
from unittest.mock import MagicMock, patch
import sys

# Ajouter le répertoire parent au chemin pour l'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules à tester
from utils.free_version_manager import FreeVersionManager


class TestFreeVersionLimits(unittest.TestCase):
    """Tests des limitations de la version gratuite"""
    
    def setUp(self):
        """Prépare l'environnement de test"""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        self.free_manager = FreeVersionManager(app_data_dir=self.test_dir)
        
        # S'assurer que les compteurs sont réinitialisés
        self.free_manager.reset_counters()
        
    def tearDown(self):
        """Nettoie l'environnement après les tests"""
        # Supprimer le répertoire temporaire
        shutil.rmtree(self.test_dir)
    
    def test_initial_limits(self):
        """Vérifie les limites initiales de la version gratuite"""
        # Vérifier les limites par défaut
        self.assertEqual(self.free_manager.FREE_LIMITS["max_documents"], 50)
        self.assertEqual(self.free_manager.FREE_LIMITS["max_users"], 50)
        self.assertEqual(self.free_manager.FREE_LIMITS["max_templates"], 5)
        self.assertFalse(self.free_manager.FREE_LIMITS["ai_chat_enabled"])
        
        # Vérifier les compteurs initiaux
        self.assertEqual(self.free_manager.usage_counters["documents_count"], 0)
        self.assertEqual(self.free_manager.usage_counters["users_count"], 0)
        self.assertEqual(self.free_manager.usage_counters["templates_count"], 0)
        self.assertFalse(self.free_manager.usage_counters["ai_chat_enabled"])
    
    def test_document_limit(self):
        """Vérifie la limite de documents"""
        # Créer 50 documents (limite)
        for i in range(self.free_manager.FREE_LIMITS["max_documents"]):
            success, message = self.free_manager.increment_document_count()
            self.assertTrue(success, f"Échec de l'incrémentation à l'itération {i}: {message}")
        
        # Vérifier que le compteur est à 50
        self.assertEqual(self.free_manager.usage_counters["documents_count"], 50)
        
        # Essayer d'ajouter un document supplémentaire (devrait échouer)
        success, message = self.free_manager.increment_document_count()
        self.assertFalse(success, "L'ajout d'un document au-delà de la limite a réussi alors qu'il devrait échouer")
        self.assertTrue("limite" in message.lower(), "Message d'erreur ne mentionne pas la limite")
    
    def test_user_limit(self):
        """Vérifie la limite d'utilisateurs"""
        # Créer 50 utilisateurs (limite)
        for i in range(self.free_manager.FREE_LIMITS["max_users"]):
            success, message = self.free_manager.increment_user_count()
            self.assertTrue(success, f"Échec de l'incrémentation à l'itération {i}: {message}")
        
        # Vérifier que le compteur est à 50
        self.assertEqual(self.free_manager.usage_counters["users_count"], 50)
        
        # Essayer d'ajouter un utilisateur supplémentaire (devrait échouer)
        success, message = self.free_manager.increment_user_count()
        self.assertFalse(success, "L'ajout d'un utilisateur au-delà de la limite a réussi alors qu'il devrait échouer")
        self.assertTrue("limite" in message.lower(), "Message d'erreur ne mentionne pas la limite")
    
    def test_template_limit(self):
        """Vérifie la limite de modèles"""
        # Créer 5 modèles (limite)
        for i in range(self.free_manager.FREE_LIMITS["max_templates"]):
            success, message = self.free_manager.increment_template_count()
            self.assertTrue(success, f"Échec de l'incrémentation à l'itération {i}: {message}")
        
        # Vérifier que le compteur est à 5
        self.assertEqual(self.free_manager.usage_counters["templates_count"], 5)
        
        # Essayer d'ajouter un modèle supplémentaire (devrait échouer)
        success, message = self.free_manager.increment_template_count()
        self.assertFalse(success, "L'ajout d'un modèle au-delà de la limite a réussi alors qu'il devrait échouer")
        self.assertTrue("limite" in message.lower(), "Message d'erreur ne mentionne pas la limite")
    
    def test_ai_chat_access(self):
        """Vérifie l'accès au chat IA"""
        # L'accès au chat IA devrait être refusé dans la version gratuite
        success, message = self.free_manager.check_ai_chat_access()
        self.assertFalse(success, "L'accès au chat IA a été autorisé alors qu'il devrait être refusé")
        self.assertTrue("limitée" in message.lower() or "limité" in message.lower(), "Message d'erreur ne mentionne pas la limitation")
    
    def test_license_bypass(self):
        """Vérifie que la licence bypass les limitations"""
        # Créer un mock de modèle de licence et d'email
        mock_license_model = MagicMock()
        mock_license_model.check_license_is_valid.return_value = (True, "Licence valide", {})
        email = "test@example.com"
        
        # Tester la limite de documents avec licence
        success, message = self.free_manager.increment_document_count(email, mock_license_model)
        self.assertTrue(success, "L'ajout de document a échoué malgré la licence")
        self.assertTrue("licence active" in message.lower(), "Message ne mentionne pas la licence active")
        
        # Forcer le compteur à la limite
        self.free_manager.set_document_count(self.free_manager.FREE_LIMITS["max_documents"])
        
        # Essayer d'ajouter un document supplémentaire avec licence (devrait réussir)
        success, message = self.free_manager.increment_document_count(email, mock_license_model)
        self.assertTrue(success, "L'ajout de document a échoué malgré la licence")
        
        # Test avec AI Chat
        success, message = self.free_manager.check_ai_chat_access(email, mock_license_model)
        self.assertTrue(success, "L'accès au chat IA a été refusé malgré la licence")
    
    def test_persist_counters(self):
        """Vérifie la persistance des compteurs"""
        # Modifier les compteurs
        self.free_manager.set_document_count(10)
        self.free_manager.set_user_count(20)
        self.free_manager.set_template_count(3)
        
        # Créer une nouvelle instance pour vérifier la persistance
        new_manager = FreeVersionManager(app_data_dir=self.test_dir)
        
        # Vérifier que les compteurs ont été chargés correctement
        self.assertEqual(new_manager.usage_counters["documents_count"], 10)
        self.assertEqual(new_manager.usage_counters["users_count"], 20)
        self.assertEqual(new_manager.usage_counters["templates_count"], 3)
    
    def test_get_usage_stats(self):
        """Vérifie les statistiques d'utilisation"""
        # Configurer les compteurs
        self.free_manager.set_document_count(25)  # 50% de la limite
        self.free_manager.set_user_count(10)      # 20% de la limite
        self.free_manager.set_template_count(4)   # 80% de la limite
        
        # Récupérer les statistiques
        stats = self.free_manager.get_usage_stats()
        
        # Vérifier les pourcentages
        self.assertEqual(stats["documents"]["percent"], 50)
        self.assertEqual(stats["users"]["percent"], 20)
        self.assertEqual(stats["templates"]["percent"], 80)
        
        # Vérifier les valeurs
        self.assertEqual(stats["documents"]["count"], 25)
        self.assertEqual(stats["users"]["count"], 10)
        self.assertEqual(stats["templates"]["count"], 4)
        
        # Vérifier les limites
        self.assertEqual(stats["documents"]["max"], 50)
        self.assertEqual(stats["users"]["max"], 50)
        self.assertEqual(stats["templates"]["max"], 5)


if __name__ == "__main__":
    unittest.main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire des limitations de la version gratuite de l'application
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("VynalDocsAutomator.FreeVersionManager")

class FreeVersionManager:
    """
    Gestionnaire des limitations de la version gratuite de l'application.
    Gère les limitations suivantes :
    - Nombre maximum de documents (50)
    - Nombre maximum d'utilisateurs/clients (50)
    - Nombre maximum de modèles personnalisés (5)
    - Accès limité au chat IA (Vynal GPT)
    """
    
    def __init__(self, app_data_dir=None):
        """
        Initialise le gestionnaire de versions gratuites
        
        Args:
            app_data_dir: Répertoire des données de l'application
        """
        # Configurer le répertoire de données
        self.app_data_dir = app_data_dir or os.path.join(os.path.expanduser("~"), ".vynal_docs")
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        # Fichier de stockage des limitations
        self.limits_file = os.path.join(self.app_data_dir, "free_version_limits.json")
        
        # Limites par défaut
        self.default_limits = {
            "documents": 50,
            "users": 50,
            "templates": 5,
            "ai_chat_enabled": False
        }
        
        # Compteurs
        self.counters = {
            "documents": 0,
            "users": 0,
            "templates": 0
        }
        
        # Charger les compteurs existants
        self._load_counters()
        
        logger.info("Gestionnaire de limitations de la version gratuite initialisé")
    
    def _load_counters(self):
        """Charge les compteurs depuis le fichier"""
        try:
            if os.path.exists(self.limits_file):
                with open(self.limits_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Mettre à jour les compteurs
                for key in self.counters:
                    if key in data:
                        self.counters[key] = data[key]
                
                logger.info(f"Compteurs chargés: {self.counters}")
            else:
                # Si le fichier n'existe pas, créer un fichier avec les valeurs par défaut
                self._persist_counters()
                logger.info("Fichier de compteurs créé avec les valeurs par défaut")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des compteurs: {e}")
    
    def _persist_counters(self):
        """Persiste les compteurs dans le fichier"""
        try:
            with open(self.limits_file, 'w', encoding='utf-8') as f:
                json.dump(self.counters, f, indent=4)
            
            logger.info(f"Compteurs sauvegardés: {self.counters}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des compteurs: {e}")
            return False
    
    def increment_counter(self, counter_type, amount=1):
        """
        Incrémente un compteur
        
        Args:
            counter_type: Type de compteur ('documents', 'users', 'templates')
            amount: Montant à ajouter (défaut: 1)
            
        Returns:
            Tuple (succès, msg, nouveau_compte)
        """
        if counter_type not in self.counters:
            logger.error(f"Type de compteur inconnu: {counter_type}")
            return False, f"Type de compteur inconnu: {counter_type}", 0
        
        # Récupérer la limite pour ce type
        limit = self.default_limits.get(counter_type, float('inf'))
        
        # Vérifier si l'incrémentation dépasserait la limite
        if self.counters[counter_type] + amount > limit:
            message = f"Limite de {counter_type} atteinte ({limit})"
            logger.warning(message)
            return False, message, self.counters[counter_type]
        
        # Incrémenter le compteur
        self.counters[counter_type] += amount
        
        # Sauvegarder les compteurs
        self._persist_counters()
        
        return True, "OK", self.counters[counter_type]
    
    def decrement_counter(self, counter_type, amount=1):
        """
        Décrémente un compteur
        
        Args:
            counter_type: Type de compteur ('documents', 'users', 'templates')
            amount: Montant à soustraire (défaut: 1)
            
        Returns:
            Tuple (succès, msg, nouveau_compte)
        """
        if counter_type not in self.counters:
            logger.error(f"Type de compteur inconnu: {counter_type}")
            return False, f"Type de compteur inconnu: {counter_type}", 0
        
        # Vérifier que le compteur ne devienne pas négatif
        if self.counters[counter_type] - amount < 0:
            message = f"Le compteur {counter_type} ne peut pas être négatif"
            logger.warning(message)
            return False, message, self.counters[counter_type]
        
        # Décrémenter le compteur
        self.counters[counter_type] -= amount
        
        # Sauvegarder les compteurs
        self._persist_counters()
        
        return True, "OK", self.counters[counter_type]
    
    def get_counter(self, counter_type):
        """
        Récupère la valeur d'un compteur
        
        Args:
            counter_type: Type de compteur ('documents', 'users', 'templates')
            
        Returns:
            Valeur du compteur ou 0 si inconnu
        """
        return self.counters.get(counter_type, 0)
    
    def get_max_limit(self, counter_type):
        """
        Récupère la valeur maximale pour un type de compteur
        
        Args:
            counter_type: Type de compteur ('documents', 'users', 'templates')
            
        Returns:
            Valeur maximale ou float('inf') si inconnu
        """
        return self.default_limits.get(counter_type, float('inf'))
    
    def reset_counters(self):
        """
        Réinitialise tous les compteurs à 0
        
        Returns:
            True si succès, False sinon
        """
        for key in self.counters:
            self.counters[key] = 0
        
        return self._persist_counters()
    
    def check_can_add_document(self):
        """
        Vérifie si un document peut être ajouté
        
        Returns:
            Tuple (peut_ajouter, message)
        """
        limit = self.default_limits.get("documents", float('inf'))
        current = self.counters.get("documents", 0)
        
        if current >= limit:
            return False, f"Limite de documents atteinte ({limit})"
        
        return True, "OK"
    
    def check_can_add_user(self):
        """
        Vérifie si un utilisateur/client peut être ajouté
        
        Returns:
            Tuple (peut_ajouter, message)
        """
        limit = self.default_limits.get("users", float('inf'))
        current = self.counters.get("users", 0)
        
        if current >= limit:
            return False, f"Limite d'utilisateurs atteinte ({limit})"
        
        return True, "OK"
    
    def check_can_add_template(self):
        """
        Vérifie si un modèle peut être ajouté
        
        Returns:
            Tuple (peut_ajouter, message)
        """
        limit = self.default_limits.get("templates", float('inf'))
        current = self.counters.get("templates", 0)
        
        if current >= limit:
            return False, f"Limite de modèles atteinte ({limit})"
        
        return True, "OK"
    
    def check_ai_chat_access(self):
        """
        Vérifie si l'accès au chat IA est autorisé
        
        Returns:
            Tuple (accès_autorisé, message)
        """
        # Dans la version gratuite, le chat IA est limité
        return False, "L'accès au chat IA est limité dans la version gratuite"
    
    def get_usage_stats(self):
        """
        Récupère les statistiques d'utilisation
        
        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {}
        
        # Pour chaque type de compteur
        for counter_type in self.counters:
            current = self.counters.get(counter_type, 0)
            max_value = self.default_limits.get(counter_type, float('inf'))
            
            # Si max_value est infini, définir une valeur par défaut pour le calcul du pourcentage
            if max_value == float('inf'):
                max_value = 100
            
            # Calcul du pourcentage
            percent = (current / max_value) * 100 if max_value > 0 else 0
            
            # Ajouter les statistiques
            stats[counter_type] = {
                "count": current,
                "max": max_value,
                "percent": percent
            }
        
        # Ajouter l'accès au chat IA
        stats["ai_chat_enabled"] = self.default_limits.get("ai_chat_enabled", False)
        
        return stats 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modèle pour la gestion des licences dans l'application Vynal Docs Automator
"""

import os
import json
import uuid
import time
import logging
import datetime
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("VynalDocsAutomator.LicenseModel")

class LicenseModel:
    """
    Modèle pour la gestion des licences utilisateurs
    """
    
    # Définition des types de licences
    LICENSE_TYPES = {
        "basic": {
            "name": "Basique",
            "duration_days": 365,
            "features": ["import_documents", "basic_analysis", "export_results"]
        },
        "pro": {
            "name": "Professionnel",
            "duration_days": 365,
            "features": ["import_documents", "advanced_analysis", "export_results", 
                         "batch_processing", "api_access"]
        },
        "enterprise": {
            "name": "Entreprise",
            "duration_days": 365,
            "features": ["import_documents", "advanced_analysis", "export_results",
                         "batch_processing", "api_access", "priority_support",
                         "unlimited_documents", "custom_templates"]
        },
        "trial": {
            "name": "Essai",
            "duration_days": 30,
            "features": ["import_documents", "basic_analysis", "export_results"],
            "is_trial": True
        }
    }
    
    # États possibles d'une licence
    LICENSE_STATUS = {
        "active": "Active",
        "expired": "Expirée",
        "disabled": "Désactivée",
        "blocked": "Bloquée",
        "trial": "Période d'essai",
        "pending": "En attente d'activation"
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialise le modèle de gestion des licences
        
        Args:
            data_dir: Répertoire des données (facultatif)
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.licenses_dir = os.path.join(self.data_dir, "licenses")
        self.licenses_file = os.path.join(self.licenses_dir, "licenses.json")
        
        # Création du répertoire des licences s'il n'existe pas
        if not os.path.exists(self.licenses_dir):
            os.makedirs(self.licenses_dir, exist_ok=True)
        
        # Chargement des licences existantes
        self.licenses = self._load_licenses()
        
        logger.info("Modèle de licences initialisé")
    
    def _load_licenses(self) -> Dict[str, Dict[str, Any]]:
        """
        Charge les licences existantes depuis le fichier
        
        Returns:
            Dictionnaire des licences par utilisateur
        """
        if not os.path.exists(self.licenses_file):
            return {}
        
        try:
            with open(self.licenses_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Licences chargées: {len(data)} entrées")
            return data
        except Exception as e:
            logger.error(f"Erreur lors du chargement des licences: {str(e)}")
            return {}
    
    def _save_licenses(self) -> bool:
        """
        Sauvegarde les licences dans le fichier
        
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            with open(self.licenses_file, 'w', encoding='utf-8') as f:
                json.dump(self.licenses, f, indent=2, ensure_ascii=False)
            logger.info(f"Licences sauvegardées: {len(self.licenses)} entrées")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des licences: {str(e)}")
            return False
    
    def create_license(self, username: str, license_type: str = "basic", 
                       duration_days: Optional[int] = None, 
                       features: Optional[List[str]] = None,
                       key: Optional[str] = None) -> Dict[str, Any]:
        """
        Crée une nouvelle licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            license_type: Type de licence (basic, pro, enterprise, trial)
            duration_days: Durée en jours (écrase la valeur par défaut du type)
            features: Liste des fonctionnalités (écrase la liste par défaut du type)
            key: Clé de licence (générée automatiquement si None)
            
        Returns:
            Dictionnaire contenant les informations de licence
        """
        if license_type not in self.LICENSE_TYPES:
            license_type = "basic"
            
        license_info = self.LICENSE_TYPES[license_type].copy()
        
        # Utiliser les valeurs personnalisées si fournies
        if duration_days is not None:
            license_info["duration_days"] = duration_days
        
        if features is not None:
            license_info["features"] = features
        
        # Générer une clé de licence unique si non fournie
        if not key:
            key = f"VDA-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:8].upper()}"
        
        # Date actuelle en timestamp
        now = int(time.time())
        
        # Informations de la licence
        license_data = {
            "username": username,
            "license_key": key,
            "license_type": license_type,
            "type_name": license_info["name"],
            "features": license_info["features"],
            "created_at": now,
            "activated_at": now,
            "expires_at": now + (license_info["duration_days"] * 86400),
            "status": "trial" if license_info.get("is_trial", False) else "active",
            "activations": 1,
            "max_activations": 1 if license_type == "basic" else (2 if license_type == "pro" else 5),
            "blocked": False,
            "block_reason": None
        }
        
        # Enregistrer la licence
        if username in self.licenses:
            # Si l'utilisateur a déjà une licence, archiver l'ancienne
            if "history" not in self.licenses[username]:
                self.licenses[username]["history"] = []
            
            self.licenses[username]["history"].append(self.licenses[username].copy())
            
            # Mettre à jour avec la nouvelle licence
            for key, value in license_data.items():
                self.licenses[username][key] = value
        else:
            # Création d'une nouvelle entrée
            license_data["history"] = []
            self.licenses[username] = license_data
        
        # Sauvegarder les modifications
        self._save_licenses()
        
        logger.info(f"Licence créée pour {username} de type {license_type}")
        
        return license_data
    
    def activate_license(self, username: str, license_key: str) -> Tuple[bool, str]:
        """
        Active une licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            license_key: Clé de licence à activer
            
        Returns:
            (succès, message)
        """
        # Vérifier si la licence existe pour cet utilisateur
        if username not in self.licenses:
            return False, "Aucune licence trouvée pour cet utilisateur"
        
        license_data = self.licenses[username]
        
        # Vérifier si la clé correspond
        if license_data.get("license_key") != license_key:
            return False, "Clé de licence invalide"
        
        # Vérifier si la licence est déjà active
        if license_data.get("status") == "active":
            return True, "La licence est déjà active"
        
        # Vérifier si la licence est bloquée
        if license_data.get("blocked", False):
            return False, f"Licence bloquée: {license_data.get('block_reason', 'Raison inconnue')}"
        
        # Vérifier si la licence est expirée
        if license_data.get("expires_at", 0) < int(time.time()):
            return False, "Cette licence a expiré"
        
        # Vérifier le nombre d'activations
        if license_data.get("activations", 0) >= license_data.get("max_activations", 1):
            return False, "Nombre maximum d'activations atteint"
        
        # Activer la licence
        license_data["status"] = "active"
        license_data["activated_at"] = int(time.time())
        license_data["activations"] = license_data.get("activations", 0) + 1
        
        # Sauvegarder les modifications
        self._save_licenses()
        
        logger.info(f"Licence activée pour {username}")
        
        return True, "Licence activée avec succès"
    
    def deactivate_license(self, username: str) -> Tuple[bool, str]:
        """
        Désactive une licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            (succès, message)
        """
        # Vérifier si la licence existe pour cet utilisateur
        if username not in self.licenses:
            return False, "Aucune licence trouvée pour cet utilisateur"
        
        license_data = self.licenses[username]
        
        # Vérifier si la licence est déjà désactivée
        if license_data.get("status") == "disabled":
            return True, "La licence est déjà désactivée"
        
        # Désactiver la licence
        license_data["status"] = "disabled"
        license_data["activations"] = max(0, license_data.get("activations", 1) - 1)
        
        # Sauvegarder les modifications
        self._save_licenses()
        
        logger.info(f"Licence désactivée pour {username}")
        
        return True, "Licence désactivée avec succès"
    
    def block_license(self, username: str, reason: str = "Violation des conditions d'utilisation") -> Tuple[bool, str]:
        """
        Bloque une licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            reason: Raison du blocage
            
        Returns:
            (succès, message)
        """
        # Vérifier si la licence existe pour cet utilisateur
        if username not in self.licenses:
            return False, "Aucune licence trouvée pour cet utilisateur"
        
        license_data = self.licenses[username]
        
        # Vérifier si la licence est déjà bloquée
        if license_data.get("blocked", False):
            return True, "La licence est déjà bloquée"
        
        # Bloquer la licence
        license_data["blocked"] = True
        license_data["block_reason"] = reason
        license_data["status"] = "blocked"
        
        # Sauvegarder les modifications
        self._save_licenses()
        
        logger.info(f"Licence bloquée pour {username}: {reason}")
        
        return True, "Licence bloquée avec succès"
    
    def unblock_license(self, username: str) -> Tuple[bool, str]:
        """
        Débloque une licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            (succès, message)
        """
        # Vérifier si la licence existe pour cet utilisateur
        if username not in self.licenses:
            return False, "Aucune licence trouvée pour cet utilisateur"
        
        license_data = self.licenses[username]
        
        # Vérifier si la licence est bloquée
        if not license_data.get("blocked", False):
            return True, "La licence n'est pas bloquée"
        
        # Débloquer la licence
        license_data["blocked"] = False
        license_data["block_reason"] = None
        
        # Restaurer l'état actif si possible
        if license_data.get("expires_at", 0) > int(time.time()):
            license_data["status"] = "active"
        else:
            license_data["status"] = "expired"
        
        # Sauvegarder les modifications
        self._save_licenses()
        
        logger.info(f"Licence débloquée pour {username}")
        
        return True, "Licence débloquée avec succès"
    
    def renew_license(self, username: str, duration_days: int = 365) -> Tuple[bool, str]:
        """
        Renouvelle une licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            duration_days: Durée du renouvellement en jours
            
        Returns:
            (succès, message)
        """
        # Vérifier si la licence existe pour cet utilisateur
        if username not in self.licenses:
            return False, "Aucune licence trouvée pour cet utilisateur"
        
        license_data = self.licenses[username]
        
        # Vérifier si la licence est bloquée
        if license_data.get("blocked", False):
            return False, "Impossible de renouveler une licence bloquée"
        
        # Calculer la nouvelle date d'expiration
        current_time = int(time.time())
        current_expiration = license_data.get("expires_at", current_time)
        
        # Si la licence a expiré, commencer à partir de maintenant
        if current_expiration < current_time:
            new_expiration = current_time + (duration_days * 86400)
        else:
            # Sinon, ajouter à la date d'expiration actuelle
            new_expiration = current_expiration + (duration_days * 86400)
        
        # Mettre à jour la licence
        license_data["expires_at"] = new_expiration
        license_data["status"] = "active"
        
        # Archiver l'ancienne licence
        if "history" not in license_data:
            license_data["history"] = []
        
        license_data["history"].append({
            "type": license_data.get("license_type"),
            "expires_at": current_expiration,
            "renewed_at": current_time
        })
        
        # Sauvegarder les modifications
        self._save_licenses()
        
        # Format lisible de la nouvelle date d'expiration
        expiration_date = datetime.datetime.fromtimestamp(new_expiration).strftime('%d/%m/%Y')
        
        logger.info(f"Licence renouvelée pour {username} jusqu'au {expiration_date}")
        
        return True, f"Licence renouvelée avec succès jusqu'au {expiration_date}"
    
    def upgrade_license(self, username: str, new_type: str) -> Tuple[bool, str]:
        """
        Change le type de licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            new_type: Nouveau type de licence
            
        Returns:
            (succès, message)
        """
        # Vérifier si la licence existe pour cet utilisateur
        if username not in self.licenses:
            return False, "Aucune licence trouvée pour cet utilisateur"
        
        # Vérifier si le type est valide
        if new_type not in self.LICENSE_TYPES:
            return False, "Type de licence invalide"
        
        license_data = self.licenses[username]
        
        # Vérifier si la licence est bloquée
        if license_data.get("blocked", False):
            return False, "Impossible de mettre à niveau une licence bloquée"
        
        # Récupérer les informations du nouveau type
        new_type_info = self.LICENSE_TYPES[new_type]
        
        # Archiver l'ancienne licence
        if "history" not in license_data:
            license_data["history"] = []
        
        license_data["history"].append({
            "type": license_data.get("license_type"),
            "features": license_data.get("features", []),
            "upgraded_at": int(time.time())
        })
        
        # Mettre à jour la licence
        license_data["license_type"] = new_type
        license_data["type_name"] = new_type_info["name"]
        license_data["features"] = new_type_info["features"]
        license_data["status"] = "active"
        
        # Augmenter le nombre maximum d'activations selon le type
        if new_type == "pro":
            license_data["max_activations"] = 2
        elif new_type == "enterprise":
            license_data["max_activations"] = 5
        
        # Sauvegarder les modifications
        self._save_licenses()
        
        logger.info(f"Licence mise à niveau pour {username} vers {new_type}")
        
        return True, f"Licence mise à niveau avec succès vers {new_type_info['name']}"
    
    def get_license(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations de licence pour un utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            Dictionnaire contenant les informations de licence ou None
        """
        if username not in self.licenses:
            return None
        
        # Vérifier si la licence est expirée mais pas encore marquée comme telle
        license_data = self.licenses[username].copy()
        
        if license_data.get("expires_at", 0) < int(time.time()) and license_data.get("status") not in ["expired", "blocked"]:
            # Mettre à jour le statut dans le dictionnaire original
            self.licenses[username]["status"] = "expired"
            self._save_licenses()
            
            # Et aussi dans la copie
            license_data["status"] = "expired"
        
        return license_data
    
    def get_all_licenses(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère toutes les licences
        
        Returns:
            Dictionnaire de toutes les licences
        """
        # Mettre à jour les statuts expirés
        current_time = int(time.time())
        for username, license_data in self.licenses.items():
            if license_data.get("expires_at", 0) < current_time and license_data.get("status") not in ["expired", "blocked"]:
                self.licenses[username]["status"] = "expired"
        
        # Sauvegarder si des modifications ont été faites
        self._save_licenses()
        
        return self.licenses.copy()
    
    def check_feature_access(self, email: str, feature: str) -> bool:
        """
        Vérifie si l'utilisateur a accès à une fonctionnalité spécifique
        
        Args:
            email: Email de l'utilisateur
            feature: Nom de la fonctionnalité à vérifier
            
        Returns:
            bool: True si l'accès est autorisé, False sinon
        """
        try:
            # Vérifier d'abord si la licence est valide
            is_valid, message, _ = self.check_license_is_valid(email)
            if not is_valid:
                logger.warning(f"Accès refusé à {feature} pour {email}: {message}")
                return False
                
            # Récupérer les données de la licence
            license_data = self.get_license_by_email(email)
            if not license_data:
                logger.warning(f"Accès refusé à {feature} pour {email}: Licence non trouvée")
                return False
                
            # Vérifier le type de licence
            license_type = license_data.get('type', 'basic')
            if license_type not in self.LICENSE_TYPES:
                logger.warning(f"Accès refusé à {feature} pour {email}: Type de licence invalide")
                return False
                
            # Vérifier les fonctionnalités autorisées
            allowed_features = self.LICENSE_TYPES[license_type].get('features', [])
            if feature not in allowed_features:
                logger.warning(f"Accès refusé à {feature} pour {email}: Fonctionnalité non incluse dans le type de licence {license_type}")
                return False
                
            # Vérifier les restrictions d'utilisation
            if license_data.get('disabled', False):
                logger.warning(f"Accès refusé à {feature} pour {email}: Licence désactivée")
                return False
                
            # Vérifier la limite d'utilisations
            max_uses = license_data.get('max_uses')
            current_uses = license_data.get('current_uses', 0)
            if max_uses and current_uses >= max_uses:
                logger.warning(f"Accès refusé à {feature} pour {email}: Limite d'utilisations atteinte")
                return False
                
            # Si toutes les vérifications sont passées
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'accès à {feature} pour {email}: {e}")
            return False
    
    def verify_hmac_license(self, username: str, license_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Vérifie la validité d'une licence avec le nouveau système basé sur HMAC SHA256
        
        Args:
            username: Email de l'utilisateur (utilisé comme identifiant)
            license_key: Clé de licence à vérifier
            
        Returns:
            Tuple (est_valide, message, données_licence)
        """
        try:
            # Importer l'utilitaire de licence seulement quand nécessaire
            from utils.license_utils import verify_license
            
            # Utiliser le nouveau système de vérification
            is_valid, message, license_data = verify_license(username, license_key)
            
            # Si la licence est valide, synchroniser avec l'ancien système pour compatibilité
            if is_valid:
                # Ajout d'une entrée dans l'ancien système si elle n'existe pas
                if username not in self.licenses:
                    license_type = license_data.get("license_type", "basic")
                    if license_type not in self.LICENSE_TYPES:
                        license_type = "basic"
                    
                    # Créer une licence compatible avec l'ancien système
                    self.create_license(
                        username=username,
                        license_type=license_type,
                        key=license_key  # Utiliser la clé HMAC comme identifiant
                    )
                else:
                    # Mettre à jour le statut si nécessaire
                    if "expires_at" in license_data and license_data["expires_at"] < int(time.time()):
                        self.licenses[username]["status"] = "expired"
                    else:
                        self.licenses[username]["status"] = "active"
                    
                    # Mettre à jour la date d'expiration si disponible
                    if "expires_at" in license_data:
                        self.licenses[username]["expires_at"] = license_data["expires_at"]
                    
                    # Sauvegarder les modifications
                    self._save_licenses()
            
            return is_valid, message, license_data
            
        except ImportError:
            logger.error("Module utils.license_utils non disponible")
            return False, "Système de licence non disponible", {}
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la licence HMAC: {str(e)}")
            return False, f"Erreur lors de la vérification: {str(e)}", {}
    
    def check_license_is_valid(self, email: str, license_key: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Vérifie si une licence est valide pour un email donné
        
        Args:
            email: Email de l'utilisateur
            license_key: Clé de licence à vérifier (optionnel)
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (validité, message, données de licence)
        """
        try:
            # Si pas de clé fournie, chercher dans les licences existantes
            if not license_key:
                license_data = self.get_license_by_email(email)
                if not license_data:
                    return False, "Aucune licence trouvée pour cet email", None
                license_key = license_data.get('key')
            
            # Vérifier le format de la clé
            if not license_key or len(license_key) < 10:
                return False, "Format de licence invalide", None
                
            # Vérifier si la licence existe
            license_data = self.get_license_by_key(license_key)
            if not license_data:
                return False, "Licence non trouvée", None
                
            # Vérifier si la licence est associée à l'email
            if license_data.get('email') != email:
                return False, "Licence non associée à cet email", None
                
            # Vérifier si la licence est activée
            if not license_data.get('activated', False):
                return False, "Licence non activée", None
                
            # Vérifier si la licence est expirée
            expiry_date = license_data.get('expiry_date')
            if expiry_date:
                try:
                    expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                    if expiry < datetime.now():
                        return False, "Licence expirée", None
                except ValueError:
                    return False, "Format de date d'expiration invalide", None
                    
            # Vérifier si la licence est désactivée
            if license_data.get('disabled', False):
                return False, "Licence désactivée", None
                
            # Vérifier si la licence a atteint sa limite d'utilisations
            max_uses = license_data.get('max_uses')
            current_uses = license_data.get('current_uses', 0)
            if max_uses and current_uses >= max_uses:
                return False, "Limite d'utilisations atteinte", None
                
            # Vérifier si la licence est bloquée
            if license_data.get('blocked', False):
                return False, f"Licence bloquée: {license_data.get('block_reason', 'Raison inconnue')}", None
                
            # Vérifier si la licence est en période d'essai expirée
            if license_data.get('type') == 'trial':
                trial_end = license_data.get('trial_end')
                if trial_end and datetime.strptime(trial_end, "%Y-%m-%d") < datetime.now():
                    return False, "Période d'essai expirée", None
                    
            # Si toutes les vérifications sont passées
            return True, "Licence valide", license_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la licence: {e}")
            return False, f"Erreur lors de la vérification: {str(e)}", None
    
    def generate_trial_license(self, username: str) -> Dict[str, Any]:
        """
        Génère une licence d'essai pour un nouvel utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            Dictionnaire contenant les informations de licence
        """
        return self.create_license(username, license_type="trial")
    
    def delete_license(self, username: str) -> bool:
        """
        Supprime une licence
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        if username not in self.licenses:
            return False
        
        # Supprimer la licence
        del self.licenses[username]
        
        # Sauvegarder les modifications
        return self._save_licenses()
    
    def get_license_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une licence par sa clé
        
        Args:
            key: Clé de licence à rechercher
            
        Returns:
            Dict contenant les informations de licence ou None si non trouvée
        """
        try:
            # Parcourir toutes les licences pour trouver celle avec la clé correspondante
            for username, license_data in self.licenses.items():
                if license_data.get("license_key") == key:
                    # Vérifier si la licence est expirée
                    if license_data.get("expires_at", 0) < int(time.time()) and license_data.get("status") not in ["expired", "blocked"]:
                        # Mettre à jour le statut
                        self.licenses[username]["status"] = "expired"
                        self._save_licenses()
                        license_data["status"] = "expired"
                    return license_data
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de licence par clé: {e}")
            return None 
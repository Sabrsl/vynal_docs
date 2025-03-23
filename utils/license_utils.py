#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilitaires pour la gestion des licences basées sur HMAC-SHA256
Système simplifié de gestion de licences basé sur l'adresse email de l'utilisateur.
"""

import hmac
import hashlib
import logging
import time
from typing import Tuple, Dict, Any, Optional
import base64
import json

logger = logging.getLogger("VynalDocsAutomator.LicenseUtils")

# Clé secrète utilisée pour la génération des licences
# Dans un environnement de production, cette clé devrait être stockée de manière sécurisée
# et non directement dans le code source.
SECRET_KEY = "ma_cle_super_secrete_vynal_docs_automator"

def generate_license(email: str, expiration_days: Optional[int] = 365, additional_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Génère une clé de licence basée sur l'email de l'utilisateur et une clé secrète.
    
    Args:
        email: L'adresse email de l'utilisateur
        expiration_days: Nombre de jours avant expiration (facultatif)
        additional_data: Données supplémentaires à inclure dans la licence (facultatif)
    
    Returns:
        Clé de licence encodée
    """
    try:
        # Normaliser l'email (en minuscules)
        email = email.lower().strip()
        
        # Créer les données de licence
        license_data = {
            "email": email,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + (expiration_days * 86400) if expiration_days else None
        }
        
        # Ajouter des données supplémentaires si fournies
        if additional_data:
            for key, value in additional_data.items():
                license_data[key] = value
        
        # Convertir les données en chaîne JSON
        license_json = json.dumps(license_data, sort_keys=True)
        
        # Calculer le HMAC-SHA256
        signature = hmac.new(
            SECRET_KEY.encode('utf-8'),
            license_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Créer le ticket de licence final (données + signature)
        license_ticket = {
            "data": license_data,
            "signature": signature
        }
        
        # Encoder en base64 pour faciliter le stockage et le transport
        license_encoded = base64.b64encode(json.dumps(license_ticket).encode('utf-8')).decode('utf-8')
        
        logger.info(f"Licence générée pour {email}, expire dans {expiration_days} jours")
        return license_encoded
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la licence: {str(e)}")
        return ""

def verify_license(email: str, license_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Vérifie si une clé de licence est valide pour l'adresse email fournie.
    
    Args:
        email: L'adresse email de l'utilisateur
        license_key: La clé de licence à vérifier
    
    Returns:
        Tuple (est_valide, message, données_licence)
    """
    try:
        # Normaliser l'email
        email = email.lower().strip()
        
        # Décoder la licence
        try:
            license_json = base64.b64decode(license_key.encode('utf-8')).decode('utf-8')
            license_ticket = json.loads(license_json)
        except Exception as e:
            logger.error(f"Erreur lors du décodage de la licence: {str(e)}")
            return False, "Format de licence invalide", {}
        
        # Extraire les données et la signature
        if "data" not in license_ticket or "signature" not in license_ticket:
            return False, "Structure de licence invalide", {}
            
        license_data = license_ticket["data"]
        stored_signature = license_ticket["signature"]
        
        # Vérifier que l'email correspond
        if license_data.get("email", "").lower() != email:
            return False, "Cette licence n'est pas associée à cet email", {}
        
        # Recalculer la signature
        license_json = json.dumps(license_data, sort_keys=True)
        computed_signature = hmac.new(
            SECRET_KEY.encode('utf-8'),
            license_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Vérifier que les signatures correspondent
        if computed_signature != stored_signature:
            return False, "Signature de licence invalide", {}
        
        # Vérifier la date d'expiration si elle existe
        if license_data.get("expires_at"):
            current_time = int(time.time())
            if license_data["expires_at"] < current_time:
                return False, "Licence expirée", license_data
        
        # La licence est valide
        return True, "Licence valide", license_data
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la licence: {str(e)}")
        return False, f"Erreur lors de la vérification: {str(e)}", {}

def get_expiration_date_string(license_data: Dict[str, Any]) -> str:
    """
    Convertit la date d'expiration en chaîne lisible.
    
    Args:
        license_data: Données de licence
    
    Returns:
        Chaîne représentant la date d'expiration
    """
    import datetime
    
    if "expires_at" not in license_data:
        return "Pas de date d'expiration"
    
    try:
        expiration_date = datetime.datetime.fromtimestamp(license_data["expires_at"])
        return expiration_date.strftime("%d/%m/%Y")
    except Exception:
        return "Date invalide"

def get_remaining_days(license_data: Dict[str, Any]) -> int:
    """
    Calcule le nombre de jours restants avant l'expiration de la licence.
    
    Args:
        license_data: Données de licence
    
    Returns:
        Nombre de jours restants (0 si expiré ou invalide)
    """
    if "expires_at" not in license_data:
        return 0
    
    try:
        current_time = int(time.time())
        remaining_seconds = max(0, license_data["expires_at"] - current_time)
        return remaining_seconds // 86400  # Convertir en jours
    except Exception:
        return 0

def admin_generate_license_key(email: str, duration_days: int = 365, license_type: str = "standard") -> str:
    """
    Fonction administrative pour générer une clé de licence.
    À utiliser uniquement côté administrateur.
    
    Args:
        email: L'adresse email de l'utilisateur
        duration_days: Nombre de jours avant expiration
        license_type: Type de licence (standard, premium, etc.)
    
    Returns:
        Clé de licence générée
    """
    additional_data = {
        "license_type": license_type,
        "issued_by": "admin_tool"
    }
    
    return generate_license(email, duration_days, additional_data) 
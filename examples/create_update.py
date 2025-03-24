#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemple de création et téléversement d'une mise à jour
"""

import os
import json
import logging
from utils.update_uploader import UpdateUploader

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Configuration
    CREDENTIALS_PATH = "credentials.json"  # Fichier de credentials Google Drive
    FOLDER_ID = "votre_folder_id"  # ID du dossier Google Drive
    ENCRYPTION_PASSWORD = "votre_mot_de_passe_secret"  # Mot de passe pour le chiffrement
    
    # Informations sur la mise à jour
    update_info = {
        'version': '1.1.0',
        'description': 'Ajout de nouvelles fonctionnalités et corrections de bugs',
        'min_version': '1.0.0',  # Version minimale requise
        'files_to_update': [
            'app/',
            'utils/',
            'config.json'
        ],
        'exclude_patterns': [
            '*.pyc',
            '__pycache__',
            '*.log'
        ]
    }
    
    try:
        # Initialiser l'uploader
        uploader = UpdateUploader(CREDENTIALS_PATH, FOLDER_ID, ENCRYPTION_PASSWORD)
        
        print("Préparation de la mise à jour...")
        print(f"Version: {update_info['version']}")
        print(f"Description: {update_info['description']}")
        
        # Créer le package de mise à jour
        update_file = uploader.create_update_package(
            update_info['version'],
            update_info['description'],
            update_info['min_version'],
            update_info['files_to_update'],
            update_info['exclude_patterns']
        )
        
        if not update_file:
            print("Erreur lors de la création du package")
            return
        
        print(f"\nPackage créé: {update_file}")
        
        # Téléverser la mise à jour
        print("\nTéléversement de la mise à jour...")
        if uploader.upload_update(update_file, update_info):
            print("Mise à jour téléversée avec succès!")
        else:
            print("Erreur lors du téléversement")
        
        # Nettoyer le fichier temporaire
        if os.path.exists(update_file):
            os.unlink(update_file)
            print("\nFichier temporaire nettoyé")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main() 
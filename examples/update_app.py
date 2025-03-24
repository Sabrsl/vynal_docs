#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemple de vérification et installation des mises à jour
"""

import os
import json
import logging
from utils.update_downloader import UpdateDownloader

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Configuration
    CREDENTIALS_PATH = "credentials.json"  # Fichier de credentials Google Drive
    FOLDER_ID = "votre_folder_id"  # ID du dossier Google Drive
    ENCRYPTION_PASSWORD = "votre_mot_de_passe_secret"  # Mot de passe pour le déchiffrement
    
    try:
        # Lire la version actuelle
        with open('config.json', 'r') as f:
            config = json.load(f)
            current_version = config.get('version', '1.0.0')
        
        print(f"Version actuelle: {current_version}")
        
        # Initialiser le gestionnaire de mises à jour
        updater = UpdateDownloader(CREDENTIALS_PATH, FOLDER_ID, ENCRYPTION_PASSWORD)
        
        # Vérifier les mises à jour disponibles
        print("\nRecherche de mises à jour...")
        update_info = updater.check_for_updates(current_version)
        
        if not update_info:
            print("Aucune mise à jour disponible")
            return
        
        print(f"\nMise à jour disponible: v{update_info['version']}")
        print(f"Description: {update_info['description']}")
        print(f"Taille: {update_info['size'] / 1024 / 1024:.2f} MB")
        
        # Demander confirmation
        response = input("\nVoulez-vous installer cette mise à jour ? (o/N) ")
        if response.lower() != 'o':
            print("Mise à jour annulée")
            return
        
        # Télécharger la mise à jour
        print("\nTéléchargement de la mise à jour...")
        update_file = updater.download_update(
            update_info['file_id'],
            update_info['checksum']
        )
        
        if not update_file:
            print("Erreur lors du téléchargement")
            return
        
        print(f"Téléchargement terminé: {update_file}")
        
        # Installer la mise à jour
        print("\nInstallation de la mise à jour...")
        if updater.install_update(update_file):
            print("Mise à jour installée avec succès!")
            
            # Mettre à jour la version dans config.json
            config['version'] = update_info['version']
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Application mise à jour vers la version {update_info['version']}")
        else:
            print("Erreur lors de l'installation")
        
        # Nettoyer le fichier de mise à jour
        if os.path.exists(update_file):
            os.unlink(update_file)
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main() 
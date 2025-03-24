#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from utils.update_uploader import UpdateUploader

# Configuration
FOLDER_ID = "1Lmh0m7CvkmiSKyXAKZWw0asSfhLwofF5"
ENCRYPTION_PASSWORD = "vynal_docs_secure_key"  # Mot de passe pour le chiffrement

def main():
    try:
        # Charger la configuration
        with open('test_config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Initialiser l'uploader
        uploader = UpdateUploader(
            credentials_path="credentials.json",
            folder_id=FOLDER_ID,
            encryption_password=ENCRYPTION_PASSWORD
        )
        
        print("Téléversement de la configuration...")
        
        # Upload la configuration
        if uploader.upload_config(config_data):
            print("✅ Configuration téléversée avec succès!")
        else:
            print("❌ Erreur lors du téléversement")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    main() 
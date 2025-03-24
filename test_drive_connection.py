#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# ID du dossier Google Drive
FOLDER_ID = "1Lmh0m7CvkmiSKyXAKZWw0asSfhLwofF5"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def init_drive_service():
    """Initialise le service Google Drive"""
    creds = None
    
    # Charger les credentials existants si disponibles
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si pas de credentials valides, demander à l'utilisateur de se connecter
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarder les credentials pour la prochaine fois
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Construire le service
    service = build('drive', 'v3', credentials=creds)
    return service

def test_connection():
    """Teste la connexion à Google Drive"""
    try:
        # Initialiser le service
        service = init_drive_service()
        
        # Tester l'accès au dossier
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            pageSize=1,
            fields="files(id, name)"
        ).execute()
        
        print("✅ Connexion à Google Drive réussie!")
        print(f"📁 Dossier testé: {FOLDER_ID}")
        print("\nContenu du dossier:")
        for file in results.get('files', []):
            print(f"- {file['name']} (ID: {file['id']})")
        
        if not results.get('files'):
            print("Le dossier est vide.")
            
        return True
        
    except Exception as e:
        print("❌ Erreur lors de la connexion à Google Drive:")
        print(str(e))
        return False

if __name__ == "__main__":
    test_connection() 
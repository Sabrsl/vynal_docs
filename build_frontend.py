import os
import subprocess
import shutil

def build_frontend():
    """Construit le frontend React pour le déploiement"""
    print("Début de la construction du frontend...")
    
    # Vérifier si le dossier frontend existe
    if not os.path.exists('frontend'):
        print("Erreur: Dossier frontend non trouvé")
        return False
    
    # Entrer dans le dossier frontend
    os.chdir('frontend')
    
    try:
        # Installer les dépendances
        print("Installation des dépendances...")
        subprocess.run(["npm", "install"], check=True)
        
        # Construire le projet
        print("Construction du projet...")
        subprocess.run(["npm", "run", "build"], check=True)
        
        print("Frontend construit avec succès !")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la construction du frontend: {e}")
        return False
    finally:
        # Revenir au dossier racine
        os.chdir('..')

if __name__ == "__main__":
    build_frontend() 
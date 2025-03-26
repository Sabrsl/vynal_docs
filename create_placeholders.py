from PIL import Image, ImageDraw
import os

# Créer le répertoire s'il n'existe pas
os.makedirs("assets/images", exist_ok=True)

# Créer le logo
logo = Image.new('RGB', (150, 40), color=(52, 53, 65))
draw = ImageDraw.Draw(logo)
draw.text((10, 10), 'VynalDocs', fill=(255, 255, 255))
logo.save('assets/images/logo.png')
print("Logo créé: assets/images/logo.png")

# Créer le placeholder de profil
profile = Image.new('RGB', (100, 100), color=(52, 53, 65))
draw = ImageDraw.Draw(profile)
draw.ellipse((10, 10, 90, 90), fill=(100, 100, 100))
profile.save('assets/images/profile_placeholder.png')
print("Image de profil créée: assets/images/profile_placeholder.png")

print("Création des images placeholder terminée") 
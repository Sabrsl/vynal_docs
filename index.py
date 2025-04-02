from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
import pathlib
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Essayer de construire le frontend si on est dans un environnement Vercel
try:
    if os.environ.get("VERCEL", "0") == "1":
        # La construction du frontend est gérée par Vercel via le buildCommand dans vercel.json
        logger.info("Environnement Vercel détecté. Le frontend sera construit par Vercel.")
    else:
        logger.info("Tentative de construction du frontend...")
        import build_frontend
        build_frontend.build_frontend()
except Exception as e:
    logger.error(f"Erreur lors de la construction du frontend: {e}")

# Configuration de l'application
app = FastAPI(
    title="Vynal Docs API",
    description="API pour la gestion des documents",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vérifier si le dossier des fichiers statiques existe
static_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(static_dir):
    logger.info(f"Dossier de fichiers statiques trouvé: {static_dir}")
    # Monter les fichiers statiques
    app.mount("/assets", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"Dossier de fichiers statiques non trouvé: {static_dir}")

@app.get("/api")
async def api_home():
    """Endpoint d'accueil de l'API"""
    return {
        "message": "Bienvenue sur l'API Vynal Docs",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/api/health")
async def health_check():
    """Endpoint de vérification de la santé de l'API"""
    return {
        "status": "healthy",
        "environment": os.environ.get("VERCEL_ENV", "development"),
        "static_dir_exists": os.path.exists(static_dir)
    }

# Page HTML simple pour rediriger vers l'API si le frontend n'est pas disponible
FALLBACK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VynalDocs - Redirection</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        .container { max-width: 600px; margin: auto; }
        .btn { display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; 
               text-decoration: none; border-radius: 4px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VynalDocs</h1>
        <p>Le frontend n'est pas encore disponible. Vous pouvez accéder à l'API en attendant.</p>
        <a href="/api" class="btn">Accéder à l'API</a>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    """Page d'accueil - sert index.html si disponible, sinon une page de redirection"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content=FALLBACK_HTML)

@app.get("/{full_path:path}")
async def serve_static(request: Request, full_path: str):
    """
    Sert les fichiers statiques ou renvoie vers index.html pour le routing côté client
    """
    # Vérifier si c'est une demande d'API
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Essayer de servir un fichier statique
    file_path = os.path.join(static_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Pour toutes les autres routes, servir index.html pour le SPA routing
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Fallback
    return HTMLResponse(content=FALLBACK_HTML) 
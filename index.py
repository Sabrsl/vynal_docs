from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "environment": os.environ.get("VERCEL_ENV", "development")
    }

# Page HTML simple pour la page d'accueil
STATIC_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VynalDocs</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #f8f9fa; color: #212529; }
        .hero { padding: 100px 0; background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); color: white; }
        .features { padding: 80px 0; }
        .feature-card { padding: 30px; border-radius: 10px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%; }
        .icon { font-size: 40px; margin-bottom: 20px; color: #6a11cb; }
        .footer { padding: 40px 0; background: #212529; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">VynalDocs</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="#">Accueil</a></li>
                    <li class="nav-item"><a class="nav-link" href="#features">Fonctionnalités</a></li>
                    <li class="nav-item"><a class="nav-link" href="/api">API</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <section class="hero text-center">
        <div class="container">
            <h1 class="display-4 fw-bold mb-4">Automatisation de documents intelligente</h1>
            <p class="lead mb-5">VynalDocs vous aide à créer, gérer et analyser vos documents avec une simplicité inégalée</p>
            <a href="/api" class="btn btn-light btn-lg px-4 me-md-2">Accéder à l'API</a>
        </div>
    </section>

    <section class="features" id="features">
        <div class="container">
            <h2 class="text-center mb-5">Fonctionnalités principales</h2>
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="icon">📄</div>
                        <h3>Gestion des documents</h3>
                        <p>Création, conversion et analyse de documents à partir de modèles personnalisables.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="icon">👁️</div>
                        <h3>OCR et reconnaissance</h3>
                        <p>Extraction intelligente de texte à partir d'images et de documents scannés.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="icon">🧠</div>
                        <h3>Intelligence artificielle</h3>
                        <p>Analyse sémantique et classification automatique de vos documents.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer text-center">
        <div class="container">
            <p>© 2025 VynalDocs. Tous droits réservés.</p>
            <p>Version 1.0.0</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    """Page d'accueil - sert une page HTML statique"""
    return HTMLResponse(content=STATIC_HTML)

@app.get("/{full_path:path}")
async def serve_static(request: Request, full_path: str):
    """
    Redirection vers la page d'accueil pour toutes les autres routes non-API
    """
    # Vérifier si c'est une demande d'API
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Rediriger vers la page d'accueil
    return HTMLResponse(content=STATIC_HTML) 
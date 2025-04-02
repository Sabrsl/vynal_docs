from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

# Configuration de l'application avec un préfixe pour les routes
app = FastAPI(
    title="Vynal Docs API",
    description="API pour la gestion des documents",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
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
async def home():
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
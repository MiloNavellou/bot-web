"""
app/__init__.py - Initialisation de l'application Flask

C'est ici qu'on crée l'app Flask et qu'on enregistre les routes.
"""

from flask import Flask
import os
from app.routes import register_routes


def create_app():
    """
    Crée et configure l'application Flask
    
    Cette fonction est appelée depuis run.py
    
    Returns:
        Flask: L'application Flask configurée
    """
    
    # Obtenir le dossier racine du projet
    basedir = os.path.abspath(os.path.dirname(__file__))
    template_folder = os.path.join(os.path.dirname(basedir), 'templates')
    static_folder = os.path.join(os.path.dirname(basedir), 'static')
    
    # Crée l'app Flask avec les bons chemins
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    
    # Enregistre les routes
    register_routes(app)
    
    return app
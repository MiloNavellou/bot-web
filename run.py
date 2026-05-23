"""
run.py - Point d'entrée du serveur Flask

C'est LE fichier qu'on exécute pour démarrer le bot.
"""

import os
from app import create_app


if __name__ == '__main__':
    # Crée l'app Flask
    app = create_app()
    
    # Affiche les infos de démarrage
    print("🚀 Serveur en cours de démarrage...")
    print("📍 Ouvre http://localhost:5000 dans ton navigateur")
    print("💡 Appuie sur Ctrl+C pour arrêter le serveur")
    print()
    
    # Lance le serveur
    # host='0.0.0.0': accessible de partout
    # port: Render définit la variable PORT
    # debug=False: en production, pas de debug
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
"""
run.py - Point d'entrée du serveur Flask

C'est LE fichier qu'on exécute pour démarrer le bot.
"""

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
    # debug=True: redémarre automatiquement quand tu modifies le code
    # port=5000: le serveur écoute sur le port 5000
    app.run(debug=True, port=5000)
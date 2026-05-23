"""
app/routes.py - Les routes (URLs) de l'application

Ici on définit:
- Quelle URL fait quoi
- Quelles données elle retourne
"""

from flask import render_template, request, jsonify
from app.bot_logic import process_message
from app.validators import validate_request_data, test_xss_injection, test_sql_injection


def register_routes(app):
    """
    Enregistre toutes les routes sur l'app Flask
    
    On met cette fonction ici pour que run.py reste simple.
    
    Args:
        app: L'application Flask
    """
    
    # ===== ROUTE HTML =====
    
    @app.route('/')
    def index():
        """
        Route racine - Retourne la page HTML principale
        URL: http://localhost:5000/
        """
        return render_template('index.html')
    
    
    # ===== ROUTES API =====
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """
        Route API pour envoyer un message et recevoir une réponse
        
        AVEC VALIDATION ET SÉCURITÉ!
        
        URL: http://localhost:5000/api/chat
        Méthode: POST
        
        Données reçues (JSON):
            {
                "message": "Salut!"
            }
        
        Données retournées (JSON):
            {
                "response": "Salut! 👋 Comment ça va?",
                "status": "ok"
            }
        """
        
        # Récupère les données JSON envoyées par le frontend
        data = request.get_json()
        
        # ===== VALIDATION 1: Vérifier que c'est du JSON valide =====
        if not data:
            return jsonify({'error': 'Aucune donnée envoyée'}), 400
        
        # ===== VALIDATION 2: Valider et nettoyer le message =====
        is_valid, error, clean_message = validate_request_data(data)
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # ===== SÉCURITÉ: Détecter les injections =====
        if test_xss_injection(clean_message):
            # On log cet essai (pour la debug)
            print(f"⚠️  Tentative de XSS détectée: {clean_message}")
            return jsonify({'error': 'Message contient des caractères non autorisés'}), 400
        
        if test_sql_injection(clean_message):
            # On log cet essai
            print(f"⚠️  Tentative de SQL injection détectée: {clean_message}")
            return jsonify({'error': 'Message contient des caractères non autorisés'}), 400
        
        # ===== TRAITEMENT: Le message est safe! =====
        try:
            response = process_message(clean_message)
        except Exception as e:
            # Si le bot crash, on retourne une erreur propre
            print(f"❌ Erreur du bot: {e}")
            return jsonify({'error': 'Une erreur est survenue'}), 500
        
        # ===== RETOUR: Réponse valide =====
        return jsonify({
            'response': response,
            'status': 'ok'
        })
    
    
    @app.route('/api/test', methods=['GET'])
    def test():
        """
        Route API simple pour tester la connexion
        
        URL: http://localhost:5000/api/test
        Méthode: GET
        """
        return jsonify({
            'status': 'ok',
            'message': 'Le serveur fonctionne!'
        })
    
    
    # ===== GESTION DES ERREURS =====
    
    @app.errorhandler(404)
    def not_found(error):
        """Gère les erreurs 404 (page non trouvée)"""
        return jsonify({'error': 'Route non trouvée'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Gère les erreurs 500 (erreur serveur)"""
        return jsonify({'error': 'Erreur interne du serveur'}), 500
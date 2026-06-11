"""
Factory de l'application Flask.
Initialise tous les modules (DB, CORS, SocketIO, Blueprints).
"""
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import get_config
from app.database import init_db, db
from app.sockets import init_socketio, socketio


def create_app(config_class=None) -> Flask:
    """
    Crée et configure l'application Flask.

    Args:
        config_class: Classe de configuration (optionnel, autodétecté sinon)

    Returns:
        L'application Flask configurée.
    """
    app = Flask(__name__)

    # Chargement de la configuration
    cfg = config_class or get_config()
    app.config.from_object(cfg)

    # CORS – autorise le frontend
    CORS(app, origins=app.config.get("CORS_ORIGINS", ["*"]),
         supports_credentials=True)

    # Base de données
    init_db(app)

    # Socket.IO
    init_socketio(app)

    # Enregistrement des blueprints
    from app.routes import (
        auth_bp, profile_bp, offers_bp,
        matching_bp, messages_bp, notifications_bp,
    )
    for bp in [auth_bp, profile_bp, offers_bp, matching_bp, messages_bp, notifications_bp]:
        app.register_blueprint(bp)

    # Route de santé
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "app": "IFRI MentorLink"}), 200

    # Gestion des erreurs globales
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Ressource introuvable", "code": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Méthode non autorisée", "code": 405}), 405

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({"error": "Erreur interne du serveur", "code": 500}), 500

    return app

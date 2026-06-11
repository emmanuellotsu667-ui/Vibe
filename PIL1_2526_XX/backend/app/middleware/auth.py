"""
Middleware d'authentification JWT.
Décorateur @token_required à utiliser sur les routes protégées.
"""
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User


def token_required(f):
    """
    Décorateur qui vérifie la présence et la validité du JWT.
    Injecte l'utilisateur courant (current_user) dans la fonction décorée.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Cherche le token dans l'en-tête Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        if not token:
            return jsonify({"error": "Token manquant", "code": "TOKEN_MISSING"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"]
            )
            current_user = User.query.get(payload["user_id"])
            if not current_user or not current_user.is_active:
                return jsonify({"error": "Utilisateur introuvable ou inactif",
                                "code": "USER_INACTIVE"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expiré", "code": "TOKEN_EXPIRED"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide", "code": "TOKEN_INVALID"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

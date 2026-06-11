"""
Routes d'authentification : inscription, connexion, reset password.
"""
import jwt
import secrets
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, current_app
from app.database import db
from app.models import User, Profile, Notification
from app.middleware import token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def generate_token(user_id: int) -> str:
    """Génère un JWT signé avec expiration configurable."""
    exp_hours = current_app.config.get("JWT_EXPIRATION_HOURS", 24)
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=exp_hours),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Inscription d'un nouvel utilisateur."""
    data = request.get_json(silent=True) or {}

    # Validation basique
    required = ["nom", "prenom", "email", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    telephone = data.get("telephone", "").strip() or None

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Cet email est déjà utilisé"}), 409

    if telephone and User.query.filter_by(telephone=telephone).first():
        return jsonify({"error": "Ce numéro de téléphone est déjà utilisé"}), 409

    if len(data["password"]) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères"}), 400

    user = User(
        nom=data["nom"].strip(),
        prenom=data["prenom"].strip(),
        email=email,
        telephone=telephone,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.flush()  # Obtenir l'ID avant commit

    # Créer un profil vide
    profile = Profile(user_id=user.id)
    db.session.add(profile)

    # Notification de bienvenue
    notif = Notification(
        user_id=user.id,
        type="system",
        title="Bienvenue sur IFRI MentorLink !",
        body="Complète ton profil pour commencer à trouver des mentors ou des mentorés.",
    )
    db.session.add(notif)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Connexion par email ou téléphone + mot de passe."""
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier", "").strip().lower()  # email ou téléphone
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "Identifiant et mot de passe requis"}), 400

    # Cherche par email ou téléphone
    user = User.query.filter(
        (User.email == identifier) | (User.telephone == identifier)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Identifiant ou mot de passe incorrect"}), 401

    if not user.is_active:
        return jsonify({"error": "Compte désactivé. Contacte l'administration."}), 403

    token = generate_token(user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@token_required
def me(current_user):
    """Retourne les informations de l'utilisateur connecté."""
    return jsonify({"user": current_user.to_dict()}), 200


@auth_bp.route("/change-password", methods=["PUT"])
@token_required
def change_password(current_user):
    """Change le mot de passe de l'utilisateur connecté."""
    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not current_user.check_password(old_password):
        return jsonify({"error": "Ancien mot de passe incorrect"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "Le nouveau mot de passe doit contenir au moins 8 caractères"}), 400

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Mot de passe mis à jour avec succès"}), 200

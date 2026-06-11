"""
Routes de gestion du profil, compétences, lacunes, disponibilités.
"""
from datetime import time
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Profile, Competence, Lacune, Disponibilite
from app.middleware import token_required

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("/", methods=["GET"])
@token_required
def get_profile(current_user):
    """Retourne le profil complet de l'utilisateur connecté."""
    if not current_user.profile:
        return jsonify({"error": "Profil introuvable"}), 404
    return jsonify({"profile": current_user.profile.to_dict()}), 200


@profile_bp.route("/<int:user_id>", methods=["GET"])
@token_required
def get_user_profile(current_user, user_id):
    """Retourne le profil d'un autre utilisateur."""
    from app.models import User
    user = User.query.get_or_404(user_id)
    if not user.profile:
        return jsonify({"error": "Profil introuvable"}), 404
    data = user.profile.to_dict()
    data["user"] = user.to_dict()
    return jsonify({"profile": data}), 200


@profile_bp.route("/", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Met à jour les champs de base du profil."""
    data = request.get_json(silent=True) or {}
    profile = current_user.profile

    allowed = ["filiere", "niveau", "bio", "centres_interet", "photo_url", "onboarding_done"]
    for field in allowed:
        if field in data:
            setattr(profile, field, data[field])

    db.session.commit()
    return jsonify({"profile": profile.to_dict()}), 200


# ─── Compétences ──────────────────────────────────────────────────────────────

@profile_bp.route("/competences", methods=["POST"])
@token_required
def add_competence(current_user):
    data = request.get_json(silent=True) or {}
    if not data.get("matiere"):
        return jsonify({"error": "La matière est requise"}), 400

    comp = Competence(
        profile_id=current_user.profile.id,
        matiere=data["matiere"].strip(),
        niveau_maitrise=int(data.get("niveau_maitrise", 3)),
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify({"competence": comp.to_dict()}), 201


@profile_bp.route("/competences/<int:comp_id>", methods=["PUT"])
@token_required
def update_competence(current_user, comp_id):
    comp = Competence.query.get_or_404(comp_id)
    if comp.profile_id != current_user.profile.id:
        return jsonify({"error": "Non autorisé"}), 403

    data = request.get_json(silent=True) or {}
    if "matiere" in data:
        comp.matiere = data["matiere"].strip()
    if "niveau_maitrise" in data:
        comp.niveau_maitrise = int(data["niveau_maitrise"])
    db.session.commit()
    return jsonify({"competence": comp.to_dict()}), 200


@profile_bp.route("/competences/<int:comp_id>", methods=["DELETE"])
@token_required
def delete_competence(current_user, comp_id):
    comp = Competence.query.get_or_404(comp_id)
    if comp.profile_id != current_user.profile.id:
        return jsonify({"error": "Non autorisé"}), 403
    db.session.delete(comp)
    db.session.commit()
    return jsonify({"message": "Compétence supprimée"}), 200


# ─── Lacunes ──────────────────────────────────────────────────────────────────

@profile_bp.route("/lacunes", methods=["POST"])
@token_required
def add_lacune(current_user):
    data = request.get_json(silent=True) or {}
    if not data.get("matiere"):
        return jsonify({"error": "La matière est requise"}), 400

    lacune = Lacune(
        profile_id=current_user.profile.id,
        matiere=data["matiere"].strip(),
        priorite=int(data.get("priorite", 1)),
    )
    db.session.add(lacune)
    db.session.commit()
    return jsonify({"lacune": lacune.to_dict()}), 201


@profile_bp.route("/lacunes/<int:lacune_id>", methods=["DELETE"])
@token_required
def delete_lacune(current_user, lacune_id):
    lacune = Lacune.query.get_or_404(lacune_id)
    if lacune.profile_id != current_user.profile.id:
        return jsonify({"error": "Non autorisé"}), 403
    db.session.delete(lacune)
    db.session.commit()
    return jsonify({"message": "Lacune supprimée"}), 200


# ─── Disponibilités ───────────────────────────────────────────────────────────

@profile_bp.route("/disponibilites", methods=["POST"])
@token_required
def add_disponibilite(current_user):
    data = request.get_json(silent=True) or {}
    required = ["jour", "heure_debut", "heure_fin"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400

    try:
        h_debut = time.fromisoformat(data["heure_debut"])
        h_fin = time.fromisoformat(data["heure_fin"])
    except ValueError:
        return jsonify({"error": "Format d'heure invalide (HH:MM)"}), 400

    dispo = Disponibilite(
        profile_id=current_user.profile.id,
        jour=data["jour"],
        heure_debut=h_debut,
        heure_fin=h_fin,
    )
    db.session.add(dispo)
    db.session.commit()
    return jsonify({"disponibilite": dispo.to_dict()}), 201


@profile_bp.route("/disponibilites/<int:dispo_id>", methods=["DELETE"])
@token_required
def delete_disponibilite(current_user, dispo_id):
    dispo = Disponibilite.query.get_or_404(dispo_id)
    if dispo.profile_id != current_user.profile.id:
        return jsonify({"error": "Non autorisé"}), 403
    db.session.delete(dispo)
    db.session.commit()
    return jsonify({"message": "Disponibilité supprimée"}), 200

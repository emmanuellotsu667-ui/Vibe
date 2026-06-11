"""
Routes CRUD pour les offres et demandes de mentorat.
"""
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Offer, Demand
from app.middleware import token_required

offers_bp = Blueprint("offers", __name__, url_prefix="/api")


# ─── OFFRES ───────────────────────────────────────────────────────────────────

@offers_bp.route("/offers", methods=["GET"])
@token_required
def list_offers(current_user):
    """Liste les offres actives avec filtres optionnels (matiere, format)."""
    q = Offer.query.filter_by(is_active=True)
    matiere = request.args.get("matiere", "").strip()
    fmt = request.args.get("format", "").strip()

    if matiere:
        q = q.filter(Offer.matiere.ilike(f"%{matiere}%"))
    if fmt:
        q = q.filter(Offer.format == fmt)

    offers = q.order_by(Offer.created_at.desc()).all()
    return jsonify({"offers": [o.to_dict() for o in offers]}), 200


@offers_bp.route("/offers", methods=["POST"])
@token_required
def create_offer(current_user):
    """Crée une nouvelle offre de mentorat."""
    data = request.get_json(silent=True) or {}
    if not data.get("matiere"):
        return jsonify({"error": "La matière est requise"}), 400

    offer = Offer(
        user_id=current_user.id,
        matiere=data["matiere"].strip(),
        description=data.get("description", "").strip(),
        format=data.get("format", "les deux"),
    )
    db.session.add(offer)
    db.session.commit()
    return jsonify({"offer": offer.to_dict()}), 201


@offers_bp.route("/offers/<int:offer_id>", methods=["GET"])
@token_required
def get_offer(current_user, offer_id):
    offer = Offer.query.get_or_404(offer_id)
    return jsonify({"offer": offer.to_dict()}), 200


@offers_bp.route("/offers/<int:offer_id>", methods=["PUT"])
@token_required
def update_offer(current_user, offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if offer.user_id != current_user.id:
        return jsonify({"error": "Non autorisé"}), 403

    data = request.get_json(silent=True) or {}
    for field in ["matiere", "description", "format", "is_active"]:
        if field in data:
            setattr(offer, field, data[field])
    db.session.commit()
    return jsonify({"offer": offer.to_dict()}), 200


@offers_bp.route("/offers/<int:offer_id>", methods=["DELETE"])
@token_required
def delete_offer(current_user, offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if offer.user_id != current_user.id:
        return jsonify({"error": "Non autorisé"}), 403
    db.session.delete(offer)
    db.session.commit()
    return jsonify({"message": "Offre supprimée"}), 200


# ─── DEMANDES ─────────────────────────────────────────────────────────────────

@offers_bp.route("/demands", methods=["GET"])
@token_required
def list_demands(current_user):
    """Liste les demandes actives avec filtres optionnels."""
    q = Demand.query.filter_by(is_active=True)
    matiere = request.args.get("matiere", "").strip()
    fmt = request.args.get("format", "").strip()

    if matiere:
        q = q.filter(Demand.matiere.ilike(f"%{matiere}%"))
    if fmt:
        q = q.filter(Demand.format == fmt)

    demands = q.order_by(Demand.created_at.desc()).all()
    return jsonify({"demands": [d.to_dict() for d in demands]}), 200


@offers_bp.route("/demands", methods=["POST"])
@token_required
def create_demand(current_user):
    """Crée une nouvelle demande de mentorat."""
    data = request.get_json(silent=True) or {}
    if not data.get("matiere"):
        return jsonify({"error": "La matière est requise"}), 400

    demand = Demand(
        user_id=current_user.id,
        matiere=data["matiere"].strip(),
        description=data.get("description", "").strip(),
        format=data.get("format", "les deux"),
    )
    db.session.add(demand)
    db.session.commit()
    return jsonify({"demand": demand.to_dict()}), 201


@offers_bp.route("/demands/<int:demand_id>", methods=["GET"])
@token_required
def get_demand(current_user, demand_id):
    demand = Demand.query.get_or_404(demand_id)
    return jsonify({"demand": demand.to_dict()}), 200


@offers_bp.route("/demands/<int:demand_id>", methods=["PUT"])
@token_required
def update_demand(current_user, demand_id):
    demand = Demand.query.get_or_404(demand_id)
    if demand.user_id != current_user.id:
        return jsonify({"error": "Non autorisé"}), 403

    data = request.get_json(silent=True) or {}
    for field in ["matiere", "description", "format", "is_active"]:
        if field in data:
            setattr(demand, field, data[field])
    db.session.commit()
    return jsonify({"demand": demand.to_dict()}), 200


@offers_bp.route("/demands/<int:demand_id>", methods=["DELETE"])
@token_required
def delete_demand(current_user, demand_id):
    demand = Demand.query.get_or_404(demand_id)
    if demand.user_id != current_user.id:
        return jsonify({"error": "Non autorisé"}), 403
    db.session.delete(demand)
    db.session.commit()
    return jsonify({"message": "Demande supprimée"}), 200

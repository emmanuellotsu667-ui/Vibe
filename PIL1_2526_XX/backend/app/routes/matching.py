"""
Routes pour l'algorithme de matching.
"""
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Offer, Demand, Matching, Notification
from app.middleware import token_required
from app.services.matching import run_matching_for_demand, compute_score

matching_bp = Blueprint("matching", __name__, url_prefix="/api/matching")


@matching_bp.route("/suggest", methods=["GET"])
@token_required
def suggest_matches(current_user):
    """
    Propose des matchings pour les demandes de l'utilisateur connecté.
    Retourne les meilleures offres scorées.
    """
    demands = Demand.query.filter_by(user_id=current_user.id, is_active=True).all()
    offers = Offer.query.filter(
        Offer.is_active == True,
        Offer.user_id != current_user.id
    ).all()

    all_results = []
    for demand in demands:
        results = run_matching_for_demand(demand, offers)
        for r in results:
            all_results.append({
                "demand_id": demand.id,
                "demand_matiere": demand.matiere,
                "offer_id": r["offer"].id,
                "mentor": r["offer"].user.to_dict(),
                "mentor_profile": r["offer"].user.profile.to_dict() if r["offer"].user.profile else None,
                "score": r["score"],
                "matieres_communes": r["matieres_communes"],
                "dispos_communes": r["dispos_communes"],
                "detail": r["detail"],
            })

    all_results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"matchings": all_results}), 200


@matching_bp.route("/run", methods=["POST"])
@token_required
def run_and_save_matching(current_user):
    """
    Calcule et sauvegarde les matchings pour une demande spécifique.
    Body: { demand_id: int }
    """
    data = request.get_json(silent=True) or {}
    demand_id = data.get("demand_id")
    if not demand_id:
        return jsonify({"error": "demand_id requis"}), 400

    demand = Demand.query.get_or_404(demand_id)
    if demand.user_id != current_user.id:
        return jsonify({"error": "Non autorisé"}), 403

    offers = Offer.query.filter(
        Offer.is_active == True,
        Offer.user_id != current_user.id
    ).all()

    results = run_matching_for_demand(demand, offers)
    saved = []

    for r in results[:10]:  # Sauvegarde les 10 meilleurs
        # Évite les doublons
        existing = Matching.query.filter_by(
            offer_id=r["offer"].id,
            demand_id=demand.id
        ).first()

        if existing:
            existing.score = r["score"]
            existing.matieres_communes = r["matieres_communes"]
            existing.dispos_communes = r["dispos_communes"]
            saved.append(existing)
        else:
            m = Matching(
                offer_id=r["offer"].id,
                demand_id=demand.id,
                score=r["score"],
                matieres_communes=r["matieres_communes"],
                dispos_communes=r["dispos_communes"],
            )
            db.session.add(m)
            saved.append(m)

            # Notifie le mentor potentiel
            notif = Notification(
                user_id=r["offer"].user_id,
                type="new_match",
                title="Nouveau matching !",
                body=f"Tu es un bon match pour une demande en {demand.matiere} (score: {r['score']:.0f}/100).",
                ref_id=demand.id,
            )
            db.session.add(notif)

    db.session.commit()
    return jsonify({"matchings": [m.to_dict() for m in saved], "count": len(saved)}), 200


@matching_bp.route("/<int:match_id>/status", methods=["PUT"])
@token_required
def update_match_status(current_user, match_id):
    """Accepte ou rejette un matching (par le mentor ou le mentoré)."""
    matching = Matching.query.get_or_404(match_id)

    # Vérifie que l'utilisateur est l'un des participants
    is_mentor = matching.offer.user_id == current_user.id
    is_mentoree = matching.demand.user_id == current_user.id
    if not is_mentor and not is_mentoree:
        return jsonify({"error": "Non autorisé"}), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ["accepted", "rejected"]:
        return jsonify({"error": "Statut invalide (accepted/rejected)"}), 400

    matching.status = new_status
    db.session.commit()
    return jsonify({"matching": matching.to_dict()}), 200

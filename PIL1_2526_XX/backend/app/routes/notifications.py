"""
Routes de notifications.
"""
from flask import Blueprint, jsonify
from app.database import db
from app.models import Notification
from app.middleware import token_required

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.route("/", methods=["GET"])
@token_required
def list_notifications(current_user):
    """Retourne les notifications de l'utilisateur (50 dernières)."""
    notifs = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    unread_count = sum(1 for n in notifs if not n.is_read)
    return jsonify({
        "notifications": [n.to_dict() for n in notifs],
        "unread_count": unread_count,
    }), 200


@notifications_bp.route("/read-all", methods=["PUT"])
@token_required
def mark_all_read(current_user):
    """Marque toutes les notifications comme lues."""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "Toutes les notifications marquées comme lues"}), 200


@notifications_bp.route("/<int:notif_id>/read", methods=["PUT"])
@token_required
def mark_read(current_user, notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        return jsonify({"error": "Non autorisé"}), 403
    notif.is_read = True
    db.session.commit()
    return jsonify({"notification": notif.to_dict()}), 200

"""
Routes de messagerie : conversations et messages.
"""
from flask import Blueprint, request, jsonify
from app.database import db
from app.models import User, Conversation, Message, Notification
from app.middleware import token_required

messages_bp = Blueprint("messages", __name__, url_prefix="/api/messages")


@messages_bp.route("/conversations", methods=["GET"])
@token_required
def list_conversations(current_user):
    """Liste les conversations de l'utilisateur connecté."""
    convs = (
        Conversation.query
        .filter(Conversation.participants.any(id=current_user.id))
        .all()
    )
    return jsonify({"conversations": [c.to_dict(current_user.id) for c in convs]}), 200


@messages_bp.route("/conversations", methods=["POST"])
@token_required
def create_or_get_conversation(current_user):
    """
    Crée une conversation ou retourne la conversation existante avec un utilisateur.
    Body: { user_id: int }
    """
    data = request.get_json(silent=True) or {}
    other_id = data.get("user_id")
    if not other_id or other_id == current_user.id:
        return jsonify({"error": "user_id invalide"}), 400

    other = User.query.get_or_404(other_id)

    # Cherche une conversation existante entre les deux
    existing = (
        Conversation.query
        .filter(Conversation.participants.any(id=current_user.id))
        .filter(Conversation.participants.any(id=other_id))
        .first()
    )
    if existing:
        return jsonify({"conversation": existing.to_dict(current_user.id)}), 200

    conv = Conversation()
    conv.participants.append(current_user)
    conv.participants.append(other)
    db.session.add(conv)
    db.session.commit()
    return jsonify({"conversation": conv.to_dict(current_user.id)}), 201


@messages_bp.route("/conversations/<int:conv_id>", methods=["GET"])
@token_required
def get_conversation(current_user, conv_id):
    """Retourne les messages d'une conversation."""
    conv = Conversation.query.get_or_404(conv_id)
    if not any(p.id == current_user.id for p in conv.participants):
        return jsonify({"error": "Non autorisé"}), 403

    # Marque les messages reçus comme lus
    unread = Message.query.filter_by(
        conversation_id=conv_id, is_read=False
    ).filter(Message.sender_id != current_user.id).all()
    for msg in unread:
        msg.is_read = True
    db.session.commit()

    return jsonify({
        "conversation": conv.to_dict(current_user.id),
        "messages": [m.to_dict() for m in conv.messages],
    }), 200


@messages_bp.route("/conversations/<int:conv_id>/send", methods=["POST"])
@token_required
def send_message(current_user, conv_id):
    """Envoie un message dans une conversation."""
    conv = Conversation.query.get_or_404(conv_id)
    if not any(p.id == current_user.id for p in conv.participants):
        return jsonify({"error": "Non autorisé"}), 403

    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "Le contenu du message est requis"}), 400

    msg = Message(
        conversation_id=conv_id,
        sender_id=current_user.id,
        content=content,
    )
    db.session.add(msg)

    # Notifie les autres participants
    for participant in conv.participants:
        if participant.id != current_user.id:
            notif = Notification(
                user_id=participant.id,
                type="new_message",
                title=f"Message de {current_user.prenom} {current_user.nom}",
                body=content[:100],
                ref_id=conv_id,
            )
            db.session.add(notif)

    db.session.commit()

    # Émet via Socket.IO si disponible
    try:
        from app.sockets import socketio
        socketio.emit(
            "new_message",
            msg.to_dict(),
            room=f"conv_{conv_id}",
        )
    except Exception:
        pass  # Fallback si Socket.IO non configuré

    return jsonify({"message": msg.to_dict()}), 201

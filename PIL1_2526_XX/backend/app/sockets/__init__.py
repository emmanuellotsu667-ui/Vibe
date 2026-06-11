"""
Configuration Socket.IO pour la messagerie temps réel.
"""
from flask_socketio import SocketIO, join_room, leave_room, emit
from app.middleware.auth import token_required as jwt_check
import jwt

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")


def init_socketio(app):
    """Initialise Socket.IO avec l'application Flask."""
    socketio.init_app(app)


@socketio.on("connect")
def on_connect(auth):
    """Vérifie le token JWT à la connexion WebSocket."""
    token = (auth or {}).get("token")
    if not token:
        return False  # Refuse la connexion

    try:
        from flask import current_app
        payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        from app.models import User
        user = User.query.get(payload["user_id"])
        if not user or not user.is_active:
            return False
    except Exception:
        return False


@socketio.on("join_conversation")
def on_join(data):
    """Rejoindre la room d'une conversation pour recevoir les messages."""
    conv_id = data.get("conversation_id")
    if conv_id:
        join_room(f"conv_{conv_id}")
        emit("joined", {"room": f"conv_{conv_id}"})


@socketio.on("leave_conversation")
def on_leave(data):
    conv_id = data.get("conversation_id")
    if conv_id:
        leave_room(f"conv_{conv_id}")


@socketio.on("disconnect")
def on_disconnect():
    pass

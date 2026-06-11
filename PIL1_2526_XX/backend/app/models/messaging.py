"""
Modèles de messagerie : Conversation, Message, Notification.
"""
from datetime import datetime, timezone
from app.database import db

# Table d'association participants d'une conversation
conversation_participants = db.Table(
    "conversation_participants",
    db.Column("conversation_id", db.Integer, db.ForeignKey("conversations.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    participants = db.relationship("User", secondary=conversation_participants,
                                    backref="conversations")
    messages = db.relationship("Message", back_populates="conversation",
                                cascade="all, delete-orphan",
                                order_by="Message.created_at")

    def to_dict(self, current_user_id=None):
        last_msg = self.messages[-1] if self.messages else None
        return {
            "id": self.id,
            "participants": [p.to_dict() for p in self.participants],
            "last_message": last_msg.to_dict() if last_msg else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = db.relationship("Conversation", back_populates="messages")
    sender = db.relationship("User", foreign_keys=[sender_id])

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sender_name": f"{self.sender.prenom} {self.sender.nom}" if self.sender else None,
            "content": self.content,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)   # new_message / new_match / system
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    ref_id = db.Column(db.Integer, nullable=True)     # ID de la ressource liée
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "body": self.body,
            "is_read": self.is_read,
            "ref_id": self.ref_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

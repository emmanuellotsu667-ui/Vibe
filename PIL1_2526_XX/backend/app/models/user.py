"""
Modèle User : compte utilisateur IFRI.
"""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telephone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    profile = db.relationship("Profile", back_populates="user", uselist=False,
                               cascade="all, delete-orphan")
    offers = db.relationship("Offer", back_populates="user",
                              cascade="all, delete-orphan")
    demands = db.relationship("Demand", back_populates="user",
                               cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user",
                                     cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hash et stocke le mot de passe."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe en clair contre le hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "telephone": self.telephone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.email}>"

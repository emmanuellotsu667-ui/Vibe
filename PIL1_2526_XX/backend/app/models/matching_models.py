"""
Modèles Offer (offre de mentorat) et Demand (demande de mentorat).
"""
from datetime import datetime, timezone
from app.database import db


class Offer(db.Model):
    """Un étudiant propose de tutorer une matière."""
    __tablename__ = "offers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    format = db.Column(db.String(20), default="les deux")  # présentiel / en ligne / les deux
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="offers")
    matchings = db.relationship("Matching", back_populates="offer",
                                 cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "matiere": self.matiere,
            "description": self.description,
            "format": self.format,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "mentor": {
                "id": self.user.id,
                "nom": self.user.nom,
                "prenom": self.user.prenom,
                "filiere": self.user.profile.filiere if self.user.profile else None,
                "niveau": self.user.profile.niveau if self.user.profile else None,
            } if self.user else None,
        }


class Demand(db.Model):
    """Un étudiant recherche un mentor pour une matière."""
    __tablename__ = "demands"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    format = db.Column(db.String(20), default="les deux")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="demands")
    matchings = db.relationship("Matching", back_populates="demand",
                                 cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "matiere": self.matiere,
            "description": self.description,
            "format": self.format,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "mentoré": {
                "id": self.user.id,
                "nom": self.user.nom,
                "prenom": self.user.prenom,
                "filiere": self.user.profile.filiere if self.user.profile else None,
                "niveau": self.user.profile.niveau if self.user.profile else None,
            } if self.user else None,
        }

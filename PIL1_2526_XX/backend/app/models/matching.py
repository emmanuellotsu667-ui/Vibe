"""
Modèle Matching : résultat de l'algorithme de matching.
"""
from datetime import datetime, timezone
from app.database import db


class Matching(db.Model):
    __tablename__ = "matchings"

    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey("offers.id"), nullable=False)
    demand_id = db.Column(db.Integer, db.ForeignKey("demands.id"), nullable=False)
    score = db.Column(db.Float, nullable=False, default=0.0)   # /100
    matieres_communes = db.Column(db.Text, nullable=True)       # CSV
    dispos_communes = db.Column(db.Text, nullable=True)         # JSON string
    status = db.Column(db.String(20), default="pending")        # pending / accepted / rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    offer = db.relationship("Offer", back_populates="matchings")
    demand = db.relationship("Demand", back_populates="matchings")

    def to_dict(self):
        return {
            "id": self.id,
            "offer_id": self.offer_id,
            "demand_id": self.demand_id,
            "score": self.score,
            "matieres_communes": self.matieres_communes,
            "dispos_communes": self.dispos_communes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "mentor": self.offer.user.to_dict() if self.offer and self.offer.user else None,
            "mentoré": self.demand.user.to_dict() if self.demand and self.demand.user else None,
        }

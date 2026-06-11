"""
Modèles liés au profil étudiant :
Profile, Competence, Lacune, Disponibilite
"""
from datetime import datetime, timezone
from app.database import db

FILIERES = ["IA", "IM", "GL", "SE&IoT", "SI"]
NIVEAUX = ["L1", "L2", "L3", "M1", "M2"]
FORMATS = ["présentiel", "en ligne", "les deux"]
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    filiere = db.Column(db.String(20), nullable=True)
    niveau = db.Column(db.String(10), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    centres_interet = db.Column(db.Text, nullable=True)   # CSV ou JSON string
    photo_url = db.Column(db.String(255), nullable=True)
    onboarding_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    user = db.relationship("User", back_populates="profile")
    competences = db.relationship("Competence", back_populates="profile",
                                   cascade="all, delete-orphan")
    lacunes = db.relationship("Lacune", back_populates="profile",
                               cascade="all, delete-orphan")
    disponibilites = db.relationship("Disponibilite", back_populates="profile",
                                      cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filiere": self.filiere,
            "niveau": self.niveau,
            "bio": self.bio,
            "centres_interet": self.centres_interet,
            "photo_url": self.photo_url,
            "onboarding_done": self.onboarding_done,
            "competences": [c.to_dict() for c in self.competences],
            "lacunes": [l.to_dict() for l in self.lacunes],
            "disponibilites": [d.to_dict() for d in self.disponibilites],
        }


class Competence(db.Model):
    __tablename__ = "competences"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    niveau_maitrise = db.Column(db.Integer, default=3)   # 1-5

    profile = db.relationship("Profile", back_populates="competences")

    def to_dict(self):
        return {"id": self.id, "matiere": self.matiere, "niveau_maitrise": self.niveau_maitrise}


class Lacune(db.Model):
    __tablename__ = "lacunes"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    priorite = db.Column(db.Integer, default=1)   # 1 = haute priorité

    profile = db.relationship("Profile", back_populates="lacunes")

    def to_dict(self):
        return {"id": self.id, "matiere": self.matiere, "priorite": self.priorite}


class Disponibilite(db.Model):
    __tablename__ = "disponibilites"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    jour = db.Column(db.String(20), nullable=False)    # ex: "Lundi"
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)

    profile = db.relationship("Profile", back_populates="disponibilites")

    def to_dict(self):
        return {
            "id": self.id,
            "jour": self.jour,
            "heure_debut": self.heure_debut.strftime("%H:%M") if self.heure_debut else None,
            "heure_fin": self.heure_fin.strftime("%H:%M") if self.heure_fin else None,
        }

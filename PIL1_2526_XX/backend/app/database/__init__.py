"""
Initialisation de SQLAlchemy et connexion à PostgreSQL.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initialise la base de données avec l'application Flask."""
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import des modèles pour que SQLAlchemy les découvre
        from app.models import (  # noqa: F401
            User, Profile, Competence, Lacune, Disponibilite,
            Offer, Demand, Matching, Conversation, Message, Notification
        )

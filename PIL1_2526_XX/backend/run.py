"""
Point d'entrée de l'application IFRI MentorLink.
Lancement : python run.py
"""
import os
from app import create_app
from app.sockets import socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    print(f"IFRI MentorLink backend demarre sur http://localhost:{port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)

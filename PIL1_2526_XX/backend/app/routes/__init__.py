from .auth import auth_bp
from .profile import profile_bp
from .offers import offers_bp
from .matching import matching_bp
from .messages import messages_bp
from .notifications import notifications_bp

__all__ = [
    "auth_bp", "profile_bp", "offers_bp",
    "matching_bp", "messages_bp", "notifications_bp",
]

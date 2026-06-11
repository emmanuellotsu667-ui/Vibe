"""
Validateurs utilitaires pour l'API.
"""
import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9]{8,15}$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip().lower()))


def is_valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone.strip()))


def is_strong_password(password: str) -> bool:
    """Au moins 8 caractères, une lettre et un chiffre."""
    return (
        len(password) >= 8
        and any(c.isalpha() for c in password)
        and any(c.isdigit() for c in password)
    )

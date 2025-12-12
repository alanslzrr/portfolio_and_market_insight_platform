"""Lightweight validators for form inputs."""
import re
from datetime import date
from typing import Optional


def validate_email(email: str) -> Optional[str]:
    if not email:
        return "El correo es obligatorio."
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(pattern, email):
        return "Ingresa un correo válido."
    return None


def validate_password(password: str) -> Optional[str]:
    if not password or len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return "Agrega al menos una mayúscula."
    if not re.search(r"[a-z]", password):
        return "Agrega al menos una minúscula."
    if not re.search(r"\d", password):
        return "Agrega al menos un número."
    return None


def validate_positive_number(value, field_name: str) -> Optional[str]:
    try:
        if float(value) <= 0:
            return f"{field_name} debe ser mayor a cero."
    except (TypeError, ValueError):
        return f"{field_name} debe ser numérico."
    return None


def validate_not_future(selected_date: date, field_name: str) -> Optional[str]:
    if selected_date > date.today():
        return f"{field_name} no puede estar en el futuro."
    return None

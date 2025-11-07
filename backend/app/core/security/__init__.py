"""
componentes de seguridad.

este paquete contiene todas las utilidades de seguridad:
- password.py: hashing y verificacion de contrasenas (bcrypt)
- jwt.py: creacion y validacion de tokens jwt
- tokens.py: tokens de verificacion y reset

todos los componentes estan disenados para ser seguros y faciles de usar.
"""
from app.core.security.password import password_hasher, PasswordHasher
from app.core.security.jwt import jwt_handler, JWTHandler
from app.core.security.tokens import (
    generate_verification_token,
    generate_reset_token,
    verify_token_expiration,
    generate_token_with_expiration,
    EMAIL_VERIFICATION_TTL,
    PASSWORD_RESET_TTL
)

__all__ = [
    # Password hashing
    "password_hasher",
    "PasswordHasher",
    # JWT
    "jwt_handler",
    "JWTHandler",
    # Verification tokens
    "generate_verification_token",
    "generate_reset_token",
    "verify_token_expiration",
    "generate_token_with_expiration",
    "EMAIL_VERIFICATION_TTL",
    "PASSWORD_RESET_TTL",
]

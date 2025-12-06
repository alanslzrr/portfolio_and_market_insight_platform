"""
middleware y dependencias para fastapi.

este paquete contiene:
- dependencies.py: dependencias de inyeccion (get_current_user, etc)
- error_handler.py: manejo centralizado de excepciones

nota: usamos dependencias de fastapi en lugar de middleware tradicional
porque son mas flexibles y faciles de testear.
"""
from app.middleware.dependencies import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    get_db
)
from app.middleware.error_handler import (
    AppException,
    NotFoundError,
    AlreadyExistsError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    InsufficientFundsError,
    ExternalServiceError,
    register_exception_handlers
)

__all__ = [
    # dependencies
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "get_db",
    # exceptions
    "AppException",
    "NotFoundError",
    "AlreadyExistsError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "BusinessRuleError",
    "InsufficientFundsError",
    "ExternalServiceError",
    "register_exception_handlers",
]

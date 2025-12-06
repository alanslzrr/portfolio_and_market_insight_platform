"""
manejo centralizado de excepciones.

define excepciones personalizadas del dominio y handlers
para convertirlas en respuestas http estandarizadas.

esto permite:
- separar logica de negocio de detalles http
- respuestas de error consistentes
- logging centralizado de errores
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict


# ------------ // ------------
# EXCEPCIONES DE DOMINIO
# ------------ // ------------

class AppException(Exception):
    """
    excepcion base de la aplicacion.
    
    todas las excepciones de dominio heredan de esta clase.
    permite capturar todas las excepciones de negocio de manera uniforme.
    """
    def __init__(self, message: str, status_code: int = 400, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """recurso no encontrado (404)."""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} no encontrado"
        if identifier:
            message = f"{resource} '{identifier}' no encontrado"
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class AlreadyExistsError(AppException):
    """recurso ya existe (409 conflict)."""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} ya existe"
        if identifier:
            message = f"{resource} '{identifier}' ya existe"
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class ValidationError(AppException):
    """error de validacion de datos (422)."""
    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class AuthenticationError(AppException):
    """error de autenticacion (401)."""
    def __init__(self, message: str = "credenciales invalidas"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """error de autorizacion/permisos (403)."""
    def __init__(self, message: str = "no tienes permiso para realizar esta accion"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class BusinessRuleError(AppException):
    """violacion de regla de negocio (400)."""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class InsufficientFundsError(BusinessRuleError):
    """cantidad insuficiente para operacion."""
    def __init__(self, asset: str, available: str, requested: str):
        message = f"cantidad insuficiente de {asset}: disponible {available}, solicitado {requested}"
        super().__init__(message)


class ExternalServiceError(AppException):
    """error en servicio externo (502 bad gateway)."""
    def __init__(self, service: str, message: str = None):
        msg = f"error en servicio externo: {service}"
        if message:
            msg = f"{msg} - {message}"
        super().__init__(msg, status_code=status.HTTP_502_BAD_GATEWAY)


# ------------ // ------------
# HANDLERS DE EXCEPCIONES
# ------------ // ------------

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    handler para excepciones de la aplicacion.
    
    convierte AppException y sus subclases en respuestas json estandarizadas.
    
    formato de respuesta:
    {
        "error": true,
        "message": "descripcion del error",
        "details": {...}  // opcional
    }
    """
    content = {
        "error": True,
        "message": exc.message,
    }
    
    if exc.details:
        content["details"] = exc.details
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    handler para ValueError.
    
    captura errores de validacion que vienen de la logica de negocio.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": True,
            "message": str(exc)
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    handler para excepciones no manejadas.
    
    captura cualquier excepcion no esperada y retorna error 500.
    en produccion, deberia loggear el error completo.
    """
    # en desarrollo podemos mostrar el error, en produccion no
    # TODO: agregar logging
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "error interno del servidor"
        }
    )


def register_exception_handlers(app):
    """
    registra todos los handlers de excepciones en la aplicacion fastapi.
    
    llamar esta funcion en main.py despues de crear la app:
        app = FastAPI()
        register_exception_handlers(app)
    
    args:
        app: instancia de FastAPI
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    # descomentar para capturar todas las excepciones:
    # app.add_exception_handler(Exception, generic_exception_handler)


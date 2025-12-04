"""
generadores de tokens para verificacion de email y reset de password.

estos tokens son diferentes a jwt:
- se almacenan en base de datos
- se usan una sola vez
- tienen ttl (time to live) especifico
- son url-safe para enviar por email

usamos secrets module de python que es criptograficamente seguro.
"""
import secrets
from datetime import datetime, timedelta
from typing import Tuple


def generate_verification_token(length: int = 32) -> str:
    """
    genera un token aleatorio para verificacion de email.
    
    el token es criptograficamente seguro y url-safe (sin caracteres especiales).
    
    args:
        length: numero de bytes del token (default 32 = 43 caracteres en base64)
        
    returns:
        str: token aleatorio url-safe
        
    example:
        >>> token = generate_verification_token()
        >>> len(token)  # ~43 caracteres
        >>> token  # 'x7k8m2nq...' (url-safe)
    """
    return secrets.token_urlsafe(length)


def generate_reset_token(length: int = 32) -> str:
    """
    genera un token aleatorio para reset de password.
    
    mismo mecanismo que verification_token pero semanticamente diferente.
    podrian tener diferentes longitudes o caracteristicas en el futuro.
    
    args:
        length: numero de bytes del token
        
    returns:
        str: token aleatorio url-safe
    """
    return secrets.token_urlsafe(length)


def verify_token_expiration(created_at: datetime, ttl_hours: int) -> bool:
    """
    verifica si un token ha expirado.
    
    args:
        created_at: timestamp de cuando se creo el token
        ttl_hours: tiempo de vida en horas
        
    returns:
        bool: true si el token aun es valido, false si expiro
        
    example:
        >>> from datetime import datetime
        >>> created = datetime.utcnow()
        >>> verify_token_expiration(created, 24)  # true (recien creado)
        >>> old_time = datetime.utcnow() - timedelta(hours=25)
        >>> verify_token_expiration(old_time, 24)  # false (expirado)
    """
    expiration_time = created_at + timedelta(hours=ttl_hours)
    return datetime.utcnow() <= expiration_time


def generate_token_with_expiration(ttl_hours: int = 24, length: int = 32) -> Tuple[str, datetime]:
    """
    genera un token y calcula su tiempo de expiracion.
    
    util para crear tokens y su expiration en una sola llamada.
    
    args:
        ttl_hours: tiempo de vida en horas (default 24)
        length: longitud del token
        
    returns:
        tuple[str, datetime]: (token, expiration_datetime)
        
    example:
        >>> token, expires_at = generate_token_with_expiration(24)
        >>> # almacenar en bd: {token: token, expires_at: expires_at}
    """
    token = secrets.token_urlsafe(length)
    expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
    return token, expires_at


# constantes de ttl recomendadas (en horas)
EMAIL_VERIFICATION_TTL = 48  # 2 dias para verificar email
PASSWORD_RESET_TTL = 1  # 1 hora para reset de password (mas seguro)

"""
handler para creacion y validacion de tokens jwt.

jwt (json web tokens) se usa para autenticacion stateless:
- access token: vida corta (15-30 min), usado en cada request
- refresh token: vida larga (7 dias), usado para renovar access tokens

ventajas de jwt:
- stateless: no requiere almacenar sesiones en servidor
- portable: funciona en distributed systems
- seguro: firmado criptograficamente
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt

from app.core.config import settings


class JWTHandler:
    """
    maneja la creacion y validacion de tokens jwt.
    
    usa el algoritmo hs256 (hmac con sha-256) que es estandar
    y suficientemente seguro para aplicaciones web.
    """
    
    def __init__(self):
        """inicializa el handler con configuracion desde settings."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, any]) -> str:
        """
        crea un access token jwt.
        
        el token incluye:
        - los datos proporcionados (tipicamente {'sub': user_id})
        - timestamp de expiracion
        - tipo de token
        
        args:
            data: datos a incluir en el token (payload)
            
        returns:
            str: token jwt codificado
            
        example:
            >>> handler = jwthandler()
            >>> token = handler.create_access_token({"sub": "user123"})
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, any]) -> str:
        """
        crea un refresh token jwt.
        
        tiene vida mas larga que access tokens.
        se usa exclusivamente para obtener nuevos access tokens.
        
        args:
            data: datos a incluir en el token
            
        returns:
            str: token jwt codificado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, any]]:
        """
        decodifica y valida un token jwt.
        
        verifica:
        - firma del token
        - expiracion
        - formato correcto
        
        args:
            token: token jwt a decodificar
            
        returns:
            dict con el payload del token, o none si es invalido
            
        example:
            >>> handler = jwthandler()
            >>> token = handler.create_access_token({"sub": "user123"})
            >>> payload = handler.decode_token(token)
            >>> payload["sub"]  # "user123"
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            # token invalido, expirado o firma incorrecta
            return None
    
    def verify_token(self, token: str, token_type: str = "access") -> bool:
        """
        verifica si un token es valido y del tipo correcto.
        
        args:
            token: token jwt a verificar
            token_type: tipo esperado ("access" o "refresh")
            
        returns:
            bool: true si el token es valido, false en caso contrario
        """
        payload = self.decode_token(token)
        if payload is None:
            return False
        
        # verificar que sea del tipo correcto
        if payload.get("type") != token_type:
            return False
        
        return True
    
    def get_token_subject(self, token: str) -> Optional[str]:
        """
        extrae el subject (tipicamente user_id) de un token.
        
        args:
            token: token jwt
            
        returns:
            str: subject del token (user_id), o none si el token es invalido
        """
        payload = self.decode_token(token)
        if payload is None:
            return None
        return payload.get("sub")


# instancia singleton para usar en toda la aplicacion
# uso: from app.core.security.jwt import jwt_handler
jwt_handler = JWTHandler()

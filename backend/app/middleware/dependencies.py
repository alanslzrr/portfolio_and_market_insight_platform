"""
dependencias de fastapi para inyeccion en endpoints.

proporciona:
- get_db: sesion de base de datos
- get_current_user: usuario autenticado desde jwt
- get_current_active_user: usuario autenticado y activo

uso en endpoints:
    @router.get("/me")
    def get_profile(current_user: User = Depends(get_current_active_user)):
        return current_user
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database.session import SessionLocal
from app.core.security import jwt_handler
from app.models.user import User
from app.repositories.user import UserRepository


# esquema de seguridad http bearer para extraer el token
# esto hace que swagger ui muestre el boton de autorizacion
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    dependency que proporciona una sesion de base de datos.
    
    usa el patron generator para asegurar que la sesion
    se cierra correctamente despues de cada request.
    
    yields:
        sesion de sqlalchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    dependency que extrae y valida el usuario del token jwt.
    
    flujo:
    1. extrae el token del header authorization
    2. decodifica y valida el jwt
    3. busca el usuario en la bd
    4. verifica que el usuario existe
    
    args:
        credentials: token bearer del header
        db: sesion de base de datos
        
    returns:
        usuario autenticado
        
    raises:
        HTTPException 401: si el token es invalido o el usuario no existe
    """
    # definir excepcion una vez para reusar
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="credenciales invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # extraer token
    token = credentials.credentials
    
    # decodificar jwt
    payload = jwt_handler.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # verificar que es access token (no refresh)
    if payload.get("type") != "access":
        raise credentials_exception
    
    # obtener user_id del payload
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    # buscar usuario
    user_repo = UserRepository(db)
    try:
        from uuid import UUID
        user_id = UUID(user_id_str)
        user = user_repo.get_by_id(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    dependency que verifica que el usuario esta activo.
    
    extiende get_current_user agregando validacion de is_active.
    usar esta dependency en endpoints que requieren usuario activo.
    
    args:
        current_user: usuario del token
        
    returns:
        usuario activo
        
    raises:
        HTTPException 403: si el usuario esta desactivado
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="usuario desactivado"
        )
    return current_user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> User | None:
    """
    dependency opcional que retorna usuario si hay token valido, none si no.
    
    util para endpoints que tienen comportamiento diferente segun
    si el usuario esta autenticado o no.
    
    args:
        credentials: token bearer opcional
        db: sesion de base de datos
        
    returns:
        usuario si hay token valido, none en caso contrario
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt_handler.decode_token(token)
        
        if payload is None or payload.get("type") != "access":
            return None
        
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        
        from uuid import UUID
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(UUID(user_id_str))
        
        return user if user and user.is_active else None
        
    except Exception:
        return None


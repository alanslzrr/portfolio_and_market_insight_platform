"""
endpoints de autenticacion.

proporciona:
- POST /register: registro de nuevos usuarios
- POST /login: autenticacion y generacion de tokens
- POST /refresh: renovacion de access token
- POST /logout: cierre de sesion

todos los endpoints retornan respuestas json estandarizadas.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.middleware.dependencies import get_db, get_current_active_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister, 
    UserLogin, 
    TokenResponse, 
    RefreshTokenRequest
)
from app.schemas.user import UserResponse
from app.models.user import User
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    registra un nuevo usuario en el sistema.
    
    crea el usuario con su perfil asociado.
    el usuario puede hacer login inmediatamente despues del registro.
    
    **validaciones:**
    - email debe ser unico
    - password debe tener minimo 8 caracteres, una mayuscula, una minuscula y un numero
    
    **returns:**
    - datos del usuario creado (sin password)
    """
    auth_service = AuthService(db)
    
    try:
        user = auth_service.register(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    autentica un usuario y genera tokens jwt.
    
    **flujo:**
    1. valida email y password
    2. genera access token (30 min) y refresh token (7 dias)
    3. crea una sesion en la bd
    
    **returns:**
    - access_token: para autenticar requests
    - refresh_token: para renovar el access token
    - expires_in: segundos hasta que expire el access token
    """
    auth_service = AuthService(db)
    
    result = auth_service.login(
        email=credentials.email,
        password=credentials.password
    )
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user, access_token, refresh_token = result
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # convertir a segundos
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(token_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    renueva el access token usando un refresh token valido.
    
    el refresh token debe ser valido y no haber expirado.
    se genera un nuevo par de tokens y se invalida el anterior.
    
    **returns:**
    - nuevos access_token y refresh_token
    """
    auth_service = AuthService(db)
    
    result = auth_service.refresh_tokens(token_request.refresh_token)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    new_access_token, new_refresh_token = result
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    cierra la sesion invalidando el refresh token.
    
    requiere estar autenticado (access token en header).
    el refresh token se elimina de la base de datos.
    """
    auth_service = AuthService(db)
    auth_service.logout(token_request.refresh_token)
    return None


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    cierra todas las sesiones del usuario.
    
    util cuando el usuario quiere cerrar sesion en todos sus dispositivos
    o cuando cambia su password.
    """
    auth_service = AuthService(db)
    auth_service.logout_all(current_user.id)
    return None


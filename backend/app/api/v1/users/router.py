"""
endpoints de usuarios.

proporciona:
- GET /me: obtener perfil del usuario autenticado
- PUT /me: actualizar perfil
- PUT /me/password: cambiar password

todos los endpoints requieren autenticacion.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.middleware.dependencies import get_db, get_current_active_user
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.schemas.user import UserProfileResponse, UserUpdate, PasswordChange
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    obtiene el perfil completo del usuario autenticado.
    
    incluye informacion basica del usuario y sus preferencias de perfil.
    
    **returns:**
    - datos del usuario con perfil completo
    """
    user_service = UserService(db)
    user_with_profile = user_service.get_user_by_id(current_user.id)
    
    if not user_with_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="usuario no encontrado"
        )
    
    # construir response con perfil
    profile_data = {
        "currency": "USD",
        "timezone": "UTC",
        "language": "en",
        "preferences": {}
    }
    
    if user_with_profile.profile:
        profile_data = {
            "currency": user_with_profile.profile.currency,
            "timezone": user_with_profile.profile.timezone,
            "language": user_with_profile.profile.language,
            "preferences": user_with_profile.profile.preferences or {}
        }
    
    return UserProfileResponse(
        id=user_with_profile.id,
        email=user_with_profile.email,
        full_name=user_with_profile.full_name,
        is_active=user_with_profile.is_active,
        is_verified=user_with_profile.is_verified,
        created_at=user_with_profile.created_at,
        updated_at=user_with_profile.updated_at,
        profile=profile_data
    )


@router.put("/me", response_model=UserProfileResponse)
def update_current_user(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    actualiza el perfil del usuario autenticado.
    
    solo se actualizan los campos que se envian (semantica PATCH).
    
    **campos actualizables:**
    - full_name: nombre completo
    - currency: moneda preferida (ISO 4217)
    - timezone: zona horaria (IANA)
    - language: idioma (ISO 639-1)
    - preferences: preferencias adicionales (json)
    """
    user_service = UserService(db)
    
    # separar campos de usuario y perfil
    user_fields = {}
    profile_fields = {}
    
    if update_data.full_name is not None:
        user_fields["full_name"] = update_data.full_name
    
    if update_data.currency is not None:
        profile_fields["currency"] = update_data.currency
    if update_data.timezone is not None:
        profile_fields["timezone"] = update_data.timezone
    if update_data.language is not None:
        profile_fields["language"] = update_data.language
    if update_data.preferences is not None:
        profile_fields["preferences"] = update_data.preferences
    
    # actualizar campos de usuario si hay
    if user_fields:
        user_service.update_user_info(current_user.id, **user_fields)
    
    # actualizar campos de perfil si hay
    if profile_fields:
        user_service.update_user_profile(current_user.id, **profile_fields)
    
    # obtener usuario actualizado
    updated_user = user_service.get_user_by_id(current_user.id)
    
    profile_data = {
        "currency": "USD",
        "timezone": "UTC",
        "language": "en",
        "preferences": {}
    }
    
    if updated_user.profile:
        profile_data = {
            "currency": updated_user.profile.currency,
            "timezone": updated_user.profile.timezone,
            "language": updated_user.profile.language,
            "preferences": updated_user.profile.preferences or {}
        }
    
    return UserProfileResponse(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        profile=profile_data
    )


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    cambia la password del usuario autenticado.
    
    requiere la password actual para verificar identidad.
    despues del cambio, todas las sesiones se invalidan por seguridad.
    
    **validaciones:**
    - password actual debe ser correcta
    - nueva password debe tener min 8 chars, una mayuscula, una minuscula y un numero
    """
    auth_service = AuthService(db)
    
    success = auth_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password actual incorrecta"
        )
    
    return None


"""
modelos pydantic para usuarios.
nunca exponemos password_hash en las responses.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserProfileData(BaseModel):
    """datos del perfil del usuario (preferencias, config, etc)"""
    currency: str = Field(default="USD", max_length=3)
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="en", max_length=2)
    preferences: dict = Field(default_factory=dict)
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        # forzar uppercase, 3 letras (iso 4217)
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError('moneda debe ser codigo iso 4217 de 3 letras (ej: USD, EUR)')
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        # forzar lowercase, 2 letras (iso 639-1)
        v = v.lower()
        if len(v) != 2 or not v.isalpha():
            raise ValueError('idioma debe ser codigo iso 639-1 de 2 letras (ej: en, es)')
        return v
    
    # ejemplos para openapi docs
    model_config = {"json_schema_extra": {
        "example": {
            "currency": "USD",
            "timezone": "America/New_York",
            "language": "en",
            "preferences": {"theme": "dark", "notifications": True}
        }
    }}


class UserResponse(BaseModel):
    """response con datos del usuario (sin password ni info sensible)"""
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    # from_attributes permite crear desde orm model
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "usuario@example.com",
                "full_name": "Juan Perez",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    }


class UserProfileResponse(BaseModel):
    """response de usuario con perfil completo incluido"""
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    profile: UserProfileData
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "usuario@example.com",
                "full_name": "Juan Perez",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "profile": {
                    "currency": "USD",
                    "timezone": "America/New_York",
                    "language": "en",
                    "preferences": {}
                }
            }
        }
    }


class UserUpdate(BaseModel):
    """
    request para actualizar usuario.
    todos los campos opcionales (semantica PATCH - solo actualizar lo que se envia).
    """
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    currency: Optional[str] = Field(None, max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=2)
    preferences: Optional[dict] = None
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError('moneda debe ser codigo iso 4217 de 3 letras')
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.lower()
        if len(v) != 2 or not v.isalpha():
            raise ValueError('idioma debe ser codigo iso 639-1 de 2 letras')
        return v
    
    model_config = {"json_schema_extra": {
        "example": {
            "full_name": "Juan Perez Garcia",
            "currency": "EUR",
            "timezone": "Europe/Madrid"
        }
    }}


class PasswordChange(BaseModel):
    """cambiar password (requiere password actual por seguridad)"""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('la password debe tener al menos una mayuscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('la password debe tener al menos una minuscula')
        if not re.search(r'\d', v):
            raise ValueError('la password debe tener al menos un numero')
        return v
    
    model_config = {"json_schema_extra": {
        "example": {
            "current_password": "OldPassword123",
            "new_password": "NewPassword456"
        }
    }}

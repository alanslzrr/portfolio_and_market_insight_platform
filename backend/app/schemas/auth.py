"""
modelos pydantic para validar requests/responses de autenticacion.
incluye validators custom para password strength.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserRegister(BaseModel):
    """datos para registrar un usuario nuevo"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=255)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # checkear que tenga mayuscula, minuscula y numero
        # no pido simbolos para no complicar al usuario
        if not re.search(r'[A-Z]', v):
            raise ValueError('la password debe tener al menos una mayuscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('la password debe tener al menos una minuscula')
        if not re.search(r'\d', v):
            raise ValueError('la password debe tener al menos un numero')
        return v
    
    # ejemplos para la doc auto de fastapi
    model_config = {"json_schema_extra": {
        "example": {
            "email": "usuario@example.com",
            "password": "Password123",
            "full_name": "Juan Perez"
        }
    }}


class UserLogin(BaseModel):
    """datos para login"""
    email: EmailStr
    password: str
    
    model_config = {"json_schema_extra": {
        "example": {
            "email": "usuario@example.com",
            "password": "Password123"
        }
    }}


class TokenResponse(BaseModel):
    """
    response con tokens jwt despues de login exitoso.
    access token dura poco (30min), refresh token dura mas (7 dias).
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos hasta que expire el access token
    
    model_config = {"json_schema_extra": {
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 1800
        }
    }}


class RefreshTokenRequest(BaseModel):
    """request para renovar access token usando refresh token"""
    refresh_token: str
    
    model_config = {"json_schema_extra": {
        "example": {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    }}


class PasswordReset(BaseModel):
    """
    resetear password con el token que se envia por email.
    el token tiene ttl de 1 hora.
    """
    token: str
    new_password: str = Field(min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # misma validacion que en registro
        if not re.search(r'[A-Z]', v):
            raise ValueError('la password debe tener al menos una mayuscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('la password debe tener al menos una minuscula')
        if not re.search(r'\d', v):
            raise ValueError('la password debe tener al menos un numero')
        return v
    
    model_config = {"json_schema_extra": {
        "example": {
            "token": "abc123def456",
            "new_password": "NewPassword123"
        }
    }}


class EmailVerification(BaseModel):
    """verificar email con token enviado al registrarse"""
    token: str
    
    model_config = {"json_schema_extra": {
        "example": {
            "token": "abc123def456"
        }
    }}

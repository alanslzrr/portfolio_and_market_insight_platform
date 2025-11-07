"""
modelos orm para usuarios y autenticacion.

define los modelos de sqlalchemy para:
- User: datos basicos del usuario y credenciales de autenticacion
- UserProfile: preferencias y configuracion personal (relacion one-to-one con User)
- UserSession: gestion de sesiones y refresh tokens (relacion one-to-many con User)

los modelos incluyen metodos de negocio basicos relacionados con el propio modelo
(como verify_password, hash_password) pero la logica compleja se delega a servicios.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from app.core.database import Base


# contexto para hashing de passwords con bcrypt
# rounds=12 es un buen balance entre seguridad y performance
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    modelo de usuario principal.
    
    representa un usuario del sistema con sus credenciales de autenticacion.
    cada usuario tiene un perfil asociado (UserProfile) y puede tener multiples
    sesiones activas (UserSession) y portfolios (Portfolio).
    
    campos:
        id: uuid unico (generado automaticamente)
        email: email unico para login (indexado para busquedas rapidas)
        password_hash: hash bcrypt de la password (nunca almacenar plain text)
        full_name: nombre completo
        is_active: flag para deshabilitar usuarios sin borrarlos (soft delete)
        is_verified: flag que indica si el email fue verificado
        created_at: timestamp de creacion
        updated_at: timestamp de ultima actualizacion
    """
    __tablename__ = "users"
    
    # clave primaria: uuid en lugar de int secuencial (mas seguro y escalable)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # credenciales de autenticacion
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # informacion basica
    full_name = Column(String(255), nullable=False)
    
    # flags de estado
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # timestamps automaticos
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # relaciones
    # one-to-one: cada usuario tiene un perfil
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # one-to-many: un usuario puede tener multiples sesiones activas
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    # one-to-many: un usuario puede tener multiples portfolios
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    
    def verify_password(self, password: str) -> bool:
        """
        verifica si una password coincide con el hash almacenado.
        
        usa bcrypt para comparar de forma segura, resistente a timing attacks.
        
        args:
            password: password en texto plano a verificar
            
        returns:
            true si la password es correcta, false en caso contrario
        """
        return pwd_context.verify(password, self.password_hash)
    
    def __repr__(self) -> str:
        return f"<User(email='{self.email}', active={self.is_active})>"


class UserProfile(Base):
    """
    perfil extendido del usuario.
    
    almacena preferencias y configuracion personal del usuario.
    se separa de User para mantener la tabla de usuarios ligera
    (principio de segregacion de interfaces).
    
    campos:
        id: uuid del perfil
        user_id: referencia al usuario (relacion one-to-one)
        currency: moneda preferida para mostrar valores (USD, EUR, etc)
        timezone: zona horaria del usuario
        language: idioma de la interfaz (es, en, etc)
        preferences: json con preferencias adicionales (flexible para futuras features)
    """
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # foreign key al usuario (one-to-one)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # preferencias del usuario
    currency = Column(String(3), default="USD", nullable=False)  # iso 4217 (3 letras)
    timezone = Column(String(50), default="UTC", nullable=False)  # iana timezone
    language = Column(String(2), default="en", nullable=False)  # iso 639-1 (2 letras)
    
    # json para preferencias flexibles (tema, notificaciones, etc)
    # evitamos crear muchas columnas para preferencias que pueden cambiar
    preferences = Column(JSON, default=dict, nullable=False)
    
    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # relacion one-to-one con User
    user = relationship("User", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile(user_id='{self.user_id}', currency='{self.currency}')>"


class UserSession(Base):
    """
    sesion de usuario para gestion de refresh tokens.
    
    permite a un usuario tener multiples sesiones activas (web, movil, etc)
    y poder invalidarlas individualmente. esto mejora la seguridad permitiendo
    logout selectivo por dispositivo.
    
    campos:
        id: uuid de la sesion
        user_id: referencia al usuario
        refresh_token: token de refresco (hashed por seguridad)
        expires_at: cuando expira este refresh token
        created_at: cuando se creo la sesion
        last_used_at: ultima vez que se uso (para analytics)
    """
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # foreign key al usuario
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # refresh token (almacenamos hash, no el token original)
    refresh_token = Column(String(500), nullable=False, unique=True, index=True)
    
    # control de expiracion
    expires_at = Column(DateTime, nullable=False)
    
    # timestamps para auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # relacion many-to-one con User
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self) -> bool:
        """
        verifica si la sesion ha expirado.
        
        returns:
            true si expiro, false si aun es valida
        """
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self) -> str:
        return f"<UserSession(user_id='{self.user_id}', expires_at='{self.expires_at}')>"

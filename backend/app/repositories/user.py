"""
repositorio para gestion de usuarios.

extiende baserepository con metodos especificos del dominio de usuarios:
- busqueda por email
- gestion de perfil
- gestion de sesiones
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.repositories.base import BaseRepository
from app.models.user import User, UserProfile, UserSession


class UserRepository(BaseRepository[User]):
    """
    repositorio para operaciones relacionadas con usuarios.
    """
    
    def __init__(self, db: Session):
        """inicializa el repositorio de usuarios."""
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        busca un usuario por email (case-insensitive).
        
        args:
            email: email del usuario
            
        returns:
            usuario si existe, none en caso contrario
        """
        return self.db.query(User).filter(
            User.email.ilike(email)  # ilike = case-insensitive
        ).first()
    
    def get_with_profile(self, user_id: UUID) -> Optional[User]:
        """
        obtiene usuario con su perfil cargado (eager loading).
        
        evita el problema n+1 al cargar el perfil en la misma query.
        
        args:
            user_id: id del usuario
            
        returns:
            usuario con perfil cargado
        """
        return self.db.query(User).options(
            joinedload(User.profile)
        ).filter(User.id == user_id).first()
    
    def create_with_profile(self, user: User, profile_data: dict) -> User:
        """
        crea usuario y su perfil en una transaccion atomica.
        
        args:
            user: instancia de user a crear
            profile_data: datos del perfil
            
        returns:
            usuario creado con su perfil
        """
        try:
            # crear usuario
            self.db.add(user)
            self.db.flush()  # flush para obtener el user.id sin hacer commit
            
            # crear perfil asociado
            profile = UserProfile(
                user_id=user.id,
                **profile_data
            )
            self.db.add(profile)
            
            # commit de ambos
            self.db.commit()
            self.db.refresh(user)
            
            return user
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_profile(self, user_id: UUID, profile_data: dict) -> Optional[UserProfile]:
        """
        actualiza el perfil de un usuario.
        
        args:
            user_id: id del usuario
            profile_data: datos a actualizar
            
        returns:
            perfil actualizado o none si no existe
        """
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            return None
        
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def create_session(self, user_id: UUID, refresh_token: str, expires_at: datetime) -> UserSession:
        """
        crea una nueva sesion para el usuario.
        
        args:
            user_id: id del usuario
            refresh_token: token de refresco
            expires_at: cuando expira la sesion
            
        returns:
            sesion creada
        """
        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session_by_token(self, refresh_token: str) -> Optional[UserSession]:
        """
        busca una sesion por su refresh token.
        
        args:
            refresh_token: token de refresco
            
        returns:
            sesion si existe, none en caso contrario
        """
        return self.db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token
        ).first()
    
    def get_active_sessions(self, user_id: UUID) -> List[UserSession]:
        """
        obtiene todas las sesiones activas (no expiradas) de un usuario.
        
        args:
            user_id: id del usuario
            
        returns:
            lista de sesiones activas
        """
        return self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.expires_at > datetime.utcnow()
        ).all()
    
    def delete_session(self, session_id: UUID) -> bool:
        """
        elimina una sesion (logout).
        
        args:
            session_id: id de la sesion
            
        returns:
            true si se elimino, false si no existia
        """
        session = self.db.query(UserSession).filter(
            UserSession.id == session_id
        ).first()
        
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
    
    def delete_all_sessions(self, user_id: UUID) -> int:
        """
        elimina todas las sesiones de un usuario (logout global).
        
        args:
            user_id: id del usuario
            
        returns:
            numero de sesiones eliminadas
        """
        count = self.db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).delete()
        self.db.commit()
        return count
    
    def update_session_token(self, session_id: UUID, new_refresh_token: str) -> Optional[UserSession]:
        """
        actualiza el refresh token de una sesion.
        
        usado cuando se renueva el token.
        
        args:
            session_id: id de la sesion
            new_refresh_token: nuevo token
            
        returns:
            sesion actualizada o none
        """
        session = self.db.query(UserSession).filter(
            UserSession.id == session_id
        ).first()
        
        if session:
            session.refresh_token = new_refresh_token
            session.last_used_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
            return session
        return None
    
    def invalidate_session(self, session_id: UUID) -> bool:
        """
        invalida una sesion eliminandola de la bd.
        
        args:
            session_id: id de la sesion
            
        returns:
            true si se invalido, false si no existia
        """
        return self.delete_session(session_id)
    
    def invalidate_all_sessions(self, user_id: UUID) -> int:
        """
        invalida todas las sesiones de un usuario.
        
        alias de delete_all_sessions para consistencia semantica.
        
        args:
            user_id: id del usuario
            
        returns:
            numero de sesiones invalidadas
        """
        return self.delete_all_sessions(user_id)

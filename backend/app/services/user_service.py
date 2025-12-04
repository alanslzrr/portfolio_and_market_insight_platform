"""
servicio de usuarios - logica de negocio para gestion de usuarios.

este servicio coordina las operaciones relacionadas con usuarios,
aplicando validaciones y reglas de negocio antes de usar los repositorios.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user import UserRepository
from app.core.security import password_hasher


class UserService:
    """
    servicio para operaciones de usuarios.
    
    proporciona metodos de alto nivel para:
    - crear usuarios con validaciones
    - actualizar informacion de usuarios
    - gestionar perfiles
    - eliminar usuarios
    
    usa userrepository para acceso a datos.
    """
    
    def __init__(self, db: Session):
        """
        inicializa el servicio.
        
        args:
            db: sesion de base de datos
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    def create_user(self, email: str, password: str, full_name: str,
                    currency: str = "USD", timezone: str = "UTC", 
                    language: str = "en") -> User:
        """
        crea un nuevo usuario con su perfil.
        
        aplica validaciones:
        - email no debe estar registrado
        - password se hashea con bcrypt
        - crea perfil asociado automaticamente
        
        args:
            email: email del usuario
            password: password en texto plano (se hasheara)
            full_name: nombre completo
            currency: moneda preferida (default USD)
            timezone: zona horaria (default UTC)
            language: idioma (default en)
            
        returns:
            usuario creado con perfil
            
        raises:
            ValueError: si el email ya existe
        """
        # validar que el email no exista
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError(f"el email {email} ya esta registrado")
        
        # crear usuario con password hasheada
        user = User(
            email=email.lower().strip(),
            password_hash=password_hasher.hash_password(password),
            full_name=full_name.strip(),
            is_active=True,
            is_verified=False  # requiere verificacion de email
        )
        
        # datos del perfil
        profile_data = {
            "currency": currency,
            "timezone": timezone,
            "language": language,
            "preferences": {}
        }
        
        # crear usuario con perfil en una transaccion
        created_user = self.user_repo.create_with_profile(user, profile_data)
        
        return created_user
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        obtiene un usuario por su id con su perfil cargado.
        
        args:
            user_id: id del usuario
            
        returns:
            usuario con perfil o none si no existe
        """
        user = self.user_repo.get_with_profile(user_id)
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        obtiene un usuario por su email.
        
        args:
            email: email del usuario
            
        returns:
            usuario o none si no existe
        """
        user = self.user_repo.get_by_email(email)
        return user
    
    def update_user_profile(self, user_id: UUID, **profile_data) -> Optional[User]:
        """
        actualiza el perfil de un usuario.
        
        args:
            user_id: id del usuario
            **profile_data: datos a actualizar (currency, timezone, language, preferences)
            
        returns:
            usuario actualizado o none si no existe
        """
        # verificar que el usuario exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        # actualizar perfil
        updated_profile = self.user_repo.update_profile(user_id, profile_data)
        if updated_profile:
            # recargar usuario con perfil actualizado
            return self.user_repo.get_with_profile(user_id)
        
        return None
    
    def update_user_info(self, user_id: UUID, full_name: Optional[str] = None,
                        is_active: Optional[bool] = None) -> Optional[User]:
        """
        actualiza informacion basica del usuario.
        
        args:
            user_id: id del usuario
            full_name: nuevo nombre (opcional)
            is_active: nuevo estado activo (opcional)
            
        returns:
            usuario actualizado o none si no existe
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        # actualizar campos proporcionados
        if full_name is not None:
            user.full_name = full_name.strip()
        if is_active is not None:
            user.is_active = is_active
        
        # guardar cambios
        updated_user = self.user_repo.update(user)
        return updated_user
    
    def delete_user(self, user_id: UUID) -> bool:
        """
        elimina un usuario (soft delete - marca como inactivo).
        
        args:
            user_id: id del usuario a eliminar
            
        returns:
            true si se elimino, false si no existia
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # en lugar de borrar, desactivamos (soft delete)
        user.is_active = False
        self.user_repo.update(user)
        return True
    
    def verify_user_email(self, user_id: UUID) -> bool:
        """
        marca el email de un usuario como verificado.
        
        args:
            user_id: id del usuario
            
        returns:
            true si se verifico, false si no existe
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        user.is_verified = True
        self.user_repo.update(user)
        return True
    
    def list_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        lista todos los usuarios con paginacion.
        
        args:
            skip: registros a saltar
            limit: maximo de registros
            
        returns:
            lista de usuarios
        """
        users = self.user_repo.get_all(skip=skip, limit=limit)
        return users
    
    def count_users(self) -> int:
        """
        cuenta el total de usuarios en el sistema.
        
        returns:
            numero total de usuarios
        """
        count = self.user_repo.count()
        return count

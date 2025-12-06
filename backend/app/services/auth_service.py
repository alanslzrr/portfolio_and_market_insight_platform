"""
servicio de autenticacion - logica de negocio para auth.

coordina el flujo completo de autenticacion:
- registro de usuarios nuevos
- login y generacion de tokens jwt
- renovacion de access tokens
- logout e invalidacion de sesiones
- verificacion de email (opcional)
- cambio de password

este servicio usa:
- userrepository para acceso a datos
- passwordhasher para hashear passwords
- jwthandler para tokens jwt
"""
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User, UserSession
from app.repositories.user import UserRepository
from app.core.security import password_hasher, jwt_handler
from app.core.config import settings


class AuthService:
    """
    servicio para operaciones de autenticacion.
    
    proporciona metodos de alto nivel para:
    - registrar usuarios con perfil
    - autenticar y generar tokens
    - renovar tokens
    - gestionar sesiones
    """
    
    def __init__(self, db: Session):
        """
        inicializa el servicio.
        
        args:
            db: sesion de base de datos
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register(self, email: str, password: str, full_name: str,
                 currency: str = "USD", timezone: str = "UTC",
                 language: str = "en") -> User:
        """
        registra un nuevo usuario con su perfil.
        
        flujo:
        1. validar que el email no exista
        2. hashear password con bcrypt
        3. crear usuario y perfil en transaccion atomica
        
        args:
            email: email del usuario (sera lowercase)
            password: password en texto plano
            full_name: nombre completo
            currency: moneda preferida
            timezone: zona horaria
            language: idioma
            
        returns:
            usuario creado
            
        raises:
            ValueError: si el email ya esta registrado
        """
        # normalizar email
        email = email.lower().strip()
        
        # validar email unico
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError(f"el email {email} ya esta registrado")
        
        # crear usuario con password hasheada
        user = User(
            email=email,
            password_hash=password_hasher.hash_password(password),
            full_name=full_name.strip(),
            is_active=True,
            is_verified=False
        )
        
        # datos del perfil
        profile_data = {
            "currency": currency.upper(),
            "timezone": timezone,
            "language": language,
            "preferences": {}
        }
        
        # crear en transaccion
        created_user = self.user_repo.create_with_profile(user, profile_data)
        
        return created_user
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        autentica un usuario por email y password.
        
        verifica:
        - que el usuario existe
        - que el password es correcto
        - que el usuario esta activo
        
        args:
            email: email del usuario
            password: password en texto plano
            
        returns:
            usuario autenticado o none si falla
        """
        # buscar usuario
        user = self.user_repo.get_by_email(email.lower().strip())
        
        if not user:
            return None
        
        # verificar que este activo
        if not user.is_active:
            return None
        
        # verificar password
        if not user.verify_password(password):
            return None
        
        return user
    
    def login(self, email: str, password: str) -> Optional[Tuple[User, str, str]]:
        """
        realiza login completo y genera tokens.
        
        flujo:
        1. autenticar usuario
        2. generar access token
        3. generar refresh token
        4. crear sesion en bd
        
        args:
            email: email del usuario
            password: password
            
        returns:
            tupla (user, access_token, refresh_token) o none si falla
        """
        # autenticar
        user = self.authenticate(email, password)
        if not user:
            return None
        
        # generar tokens
        token_data = {"sub": str(user.id)}
        access_token = jwt_handler.create_access_token(token_data)
        refresh_token = jwt_handler.create_refresh_token(token_data)
        
        # calcular expiracion del refresh token
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # crear sesion
        self.user_repo.create_session(user.id, refresh_token, expires_at)
        
        return user, access_token, refresh_token
    
    def refresh_tokens(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """
        renueva tokens usando un refresh token valido.
        
        flujo:
        1. decodificar y validar refresh token
        2. verificar que la sesion existe
        3. generar nuevos tokens
        4. actualizar sesion con nuevo refresh token
        
        args:
            refresh_token: refresh token actual
            
        returns:
            tupla (new_access_token, new_refresh_token) o none si falla
        """
        # decodificar token
        payload = jwt_handler.decode_token(refresh_token)
        if not payload:
            return None
        
        # verificar que es refresh token
        if payload.get("type") != "refresh":
            return None
        
        # obtener user_id
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None
        
        # verificar que el usuario existe y esta activo
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        # verificar que la sesion existe y no ha expirado
        session = self.user_repo.get_session_by_token(refresh_token)
        if not session or session.is_expired():
            return None
        
        # generar nuevos tokens
        token_data = {"sub": str(user.id)}
        new_access_token = jwt_handler.create_access_token(token_data)
        new_refresh_token = jwt_handler.create_refresh_token(token_data)
        
        # actualizar sesion
        self.user_repo.update_session_token(session.id, new_refresh_token)
        
        return new_access_token, new_refresh_token
    
    def logout(self, refresh_token: str) -> bool:
        """
        cierra sesion invalidando el refresh token.
        
        args:
            refresh_token: token a invalidar
            
        returns:
            true si se cerro sesion, false si no existia
        """
        session = self.user_repo.get_session_by_token(refresh_token)
        if not session:
            return False
        
        # invalidar sesion
        self.user_repo.invalidate_session(session.id)
        return True
    
    def logout_all(self, user_id: UUID) -> int:
        """
        cierra todas las sesiones de un usuario.
        
        util cuando el usuario cambia password o quiere
        cerrar sesion en todos sus dispositivos.
        
        args:
            user_id: id del usuario
            
        returns:
            numero de sesiones cerradas
        """
        return self.user_repo.invalidate_all_sessions(user_id)
    
    def get_user_from_token(self, access_token: str) -> Optional[User]:
        """
        obtiene el usuario a partir de un access token.
        
        usado principalmente por el middleware de autenticacion.
        
        args:
            access_token: token jwt
            
        returns:
            usuario o none si token invalido
        """
        # decodificar token
        payload = jwt_handler.decode_token(access_token)
        if not payload:
            return None
        
        # verificar que es access token
        if payload.get("type") != "access":
            return None
        
        # obtener user_id
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None
        
        # buscar usuario activo
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    def change_password(self, user_id: UUID, current_password: str, 
                        new_password: str) -> bool:
        """
        cambia la password de un usuario.
        
        verifica el password actual antes de cambiar.
        invalida todas las sesiones existentes por seguridad.
        
        args:
            user_id: id del usuario
            current_password: password actual
            new_password: nueva password
            
        returns:
            true si se cambio, false si el password actual es incorrecto
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # verificar password actual
        if not user.verify_password(current_password):
            return False
        
        # actualizar password
        user.password_hash = password_hasher.hash_password(new_password)
        self.user_repo.update(user)
        
        # invalidar todas las sesiones por seguridad
        self.user_repo.invalidate_all_sessions(user_id)
        
        return True
    
    def verify_email(self, user_id: UUID) -> bool:
        """
        marca el email de un usuario como verificado.
        
        nota: en este sistema la verificacion de email es opcional,
        el usuario puede usar el sistema sin verificar.
        
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


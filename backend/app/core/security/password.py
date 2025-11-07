"""
componente para hashing y verificacion de contrasenas.

usa bcrypt que es el estandar de la industria para hashing de contrasenas.
caracteristicas de bcrypt:
- salt aleatorio automatico (previene rainbow tables)
- cost factor ajustable (resistencia a brute force)
- disenado especificamente para passwords (lento intencionalmente)
"""
from passlib.context import CryptContext


class PasswordHasher:
    """
    maneja hashing y verificacion de contrasenas usando bcrypt.
    
    el cost factor de 12 es un buen balance para proyectos academicos:
    - suficientemente seguro para produccion
    - no tan lento como para afectar la experiencia en desarrollo
    
    en produccion enterprise se podria aumentar a 13-14.
    """
    
    def __init__(self, cost_factor: int = 12):
        """
        inicializa el contexto de bcrypt.
        
        args:
            cost_factor: numero de rondas de bcrypt (default 12).
                        cada aumento duplica el tiempo de procesamiento.
        """
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=cost_factor
        )
    
    def hash_password(self, password: str) -> str:
        """
        genera un hash bcrypt de la contrasena.
        
        el hash incluye el salt automaticamente, por lo que cada
        hash es unico incluso para la misma contrasena.
        
        args:
            password: contrasena en texto plano
            
        returns:
            str: hash bcrypt (60 caracteres)
            
        example:
            >>> hasher = passwordhasher()
            >>> hash1 = hasher.hash_password("securepass123")
            >>> hash2 = hasher.hash_password("securepass123")
            >>> hash1 != hash2  # true - diferentes salts
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        verifica si una contrasena coincide con un hash.
        
        es resistente a timing attacks gracias a la implementacion de bcrypt.
        
        args:
            password: contrasena en texto plano a verificar
            password_hash: hash bcrypt almacenado
            
        returns:
            bool: true si la contrasena es correcta, false en caso contrario
            
        example:
            >>> hasher = passwordhasher()
            >>> hash_val = hasher.hash_password("securepass123")
            >>> hasher.verify_password("securepass123", hash_val)  # true
            >>> hasher.verify_password("wrongpassword", hash_val)  # false
        """
        return self.pwd_context.verify(password, password_hash)


# instancia singleton para usar en toda la aplicacion
# uso: from app.core.security.password import password_hasher
password_hasher = PasswordHasher()

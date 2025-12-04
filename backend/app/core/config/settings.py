"""
configuracion de la aplicacion usando pydantic settings.
gestiona variables de entorno y configuracion.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    configuracion de la aplicacion cargada desde variables de entorno.
    
    toda la configuracion sensible se almacena en config/.env y se carga aqui.
    proporciona acceso tipado y seguro a la configuracion en toda la aplicacion.
    """
    
    # configuracion de base de datos
    DATABASE_URL: str  # string de conexion postgresql: postgresql://user:pass@host:port/dbname
    DB_POOL_SIZE: int = 5  # numero de conexiones a mantener en el pool
    DB_MAX_OVERFLOW: int = 10  # maximo de conexiones adicionales al pool_size
    
    # configuracion de seguridad (para autenticacion jwt en fase 3)
    SECRET_KEY: str  # clave secreta para firmar tokens jwt - debe mantenerse secreta
    ALGORITHM: str = "HS256"  # algoritmo para codificacion jwt (hs256 es estandar)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # duracion de tokens de acceso
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # duracion de tokens de refresco
    
    # apis externas (opcional - se usaran en fase 5 y fase 9)
    ALPHA_VANTAGE_API_KEY: str = ""  # api key para datos de mercado (alpha vantage)
    OPENAI_API_KEY: str = ""  # api key para analisis con ia (openai)
    
    # configuracion cors (para comunicacion con frontend)
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"  # origenes permitidos separados por comas
    
    # configuracion de aplicacion
    DEBUG: bool = False  # activar modo debug (logging mas detallado)
    ENVIRONMENT: str = "development"  # entorno actual: development, production, testing
    
    model_config = SettingsConfigDict(
        env_file="../config/.env",  # ruta al archivo .env
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def cors_origins(self) -> List[str]:
        """parsea el string de origenes cors en una lista para fastapi corsmiddleware."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# instancia singleton - importar en toda la aplicacion
# uso: from app.core.config import settings
settings = Settings()


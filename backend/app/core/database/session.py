"""
configuracion del motor de base de datos y sesiones de sqlalchemy.

este modulo establece la conexion con postgresql y proporciona:
- engine: motor de conexion configurado con pool de conexiones
- sessionlocal: fabrica de sesiones para transacciones
- base: clase base declarativa para todos los modelos orm
- get_db(): dependency para fastapi que gestiona el ciclo de vida de las sesiones

el patron usado aqui (dependency injection con get_db) es fundamental para:
1. asegurar que cada request tenga su propia sesion de bd
2. cerrar automaticamente las sesiones al finalizar el request
3. facilitar testing mediante mocking de la dependencia
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.core.config import settings

# motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # desactivamos el logging de sql para mantener la salida limpia
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# fabrica de sesiones: cada vez que llamemos sessionlocal() obtenemos una nueva sesion
# autocommit=false: las transacciones deben confirmarse explicitamente (mas seguro)
# autoflush=false: el flush de cambios a bd se controla manualmente
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# base declarativa para todos los modelos orm
# todos los modelos heredaran de esta clase para obtener funcionalidad orm
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    dependency de fastapi para obtener una sesion de base de datos.
    
    esta funcion se usa en los endpoints como dependencia para obtener
    automaticamente una sesion de bd que se cierra al terminar el request.
    
    uso en fastapi:
        @app.get("/users")
        def get_users(db: session = depends(get_db)):
            return db.query(user).all()
    
    el patron try-finally asegura que:
    - la sesion siempre se cierra, incluso si hay errores
    - no hay fugas de conexiones a la base de datos
    - cada request tiene una sesion independiente
    
    yields:
        session: sesion de sqlalchemy lista para usar
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
modulo de base de datos.

exporta los componentes principales para trabajar con sqlalchemy:
- base: clase base para modelos orm
- get_db: dependency para obtener sesiones de bd
- engine: motor de conexion (util para alembic)
"""
from app.core.database.session import Base, get_db, engine

__all__ = ["Base", "get_db", "engine"]

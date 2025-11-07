"""
configuracion de alembic para migraciones de base de datos.

este archivo configura alembic para:
1. cargar todos nuestros modelos orm automaticamente
2. usar database_url desde nuestra configuracion (settings.py)
3. soportar autogenerate de migraciones

la configuracion es estandar pero adaptada para nuestro proyecto academico.
"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# importar nuestra configuracion y base declarativa
import sys
import os

# agregar el directorio padre al path para poder importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import Base

# importar todos los modelos para que alembic los detecte
# es critico importarlos aqui para que autogenerate funcione
from app.models import (
    User, UserProfile, UserSession,
    Portfolio, PortfolioAsset,
    Operation,
    Asset, AssetPrice,
    Analysis, AnalysisRequest
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# sobrescribir sqlalchemy.url con nuestra configuracion
# esto nos permite usar database_url desde settings.py
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata de nuestros modelos para autogenerate
# base.metadata contiene todos los modelos que heredan de base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """run migrations in 'offline' mode.

    this configures the context with just a url
    and not an engine, though an engine is acceptable
    here as well. by skipping the engine creation
    we don't even need a dbapi to be available.

    calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """run migrations in 'online' mode.

    in this scenario we need to create an engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# Configuración de Base de Datos

Este módulo contiene toda la configuración relacionada con la base de datos PostgreSQL, incluyendo la creación del engine de SQLAlchemy, la gestión de sesiones y la base para los modelos.

## Archivos que Contendrá

- **base.py**: Configuración principal de SQLAlchemy:
  - `engine`: Motor de base de datos configurado con la URL de PostgreSQL
  - `SessionLocal`: Factory para crear sesiones de base de datos
  - `Base`: Clase base para todos los modelos SQLAlchemy
  - Configuración de pool de conexiones
  - Configuración de logging de queries (opcional para desarrollo)

- **session.py**: Gestión de sesiones de base de datos:
  - `get_db()`: Dependency de FastAPI que proporciona una sesión de base de datos
  - Manejo del ciclo de vida de sesiones (creación, uso, cierre)
  - Gestión de transacciones y rollback en caso de errores
  - Context manager para asegurar el cierre correcto de sesiones

## Funcionalidades

Este módulo proporciona:

- Conexión centralizada a PostgreSQL mediante SQLAlchemy
- Gestión automática del ciclo de vida de sesiones
- Dependency injection de sesiones en endpoints FastAPI
- Base para definir modelos de dominio
- Configuración de pool de conexiones para optimizar rendimiento

## Configuración

La configuración de la base de datos se carga desde variables de entorno:

- `DATABASE_URL`: URL completa de conexión a PostgreSQL (incluye usuario, contraseña, host, puerto, nombre de base de datos)
- `DATABASE_POOL_SIZE`: Tamaño del pool de conexiones (por defecto 5)
- `DATABASE_MAX_OVERFLOW`: Conexiones adicionales permitidas (por defecto 10)

## Uso

Las sesiones de base de datos se utilizan mediante dependency injection en los endpoints, asegurando que cada petición tenga su propia sesión y que esta se cierre correctamente al finalizar la petición, incluso en caso de errores.


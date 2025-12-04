# Core - Configuración y Componentes Centrales

Este módulo contiene la configuración central del sistema y los componentes fundamentales que son utilizados en toda la aplicación. Incluye la configuración de la base de datos, la seguridad, y otros componentes compartidos.

## Estructura

- **config/**: Configuración de la aplicación mediante variables de entorno
- **security/**: Componentes de seguridad como JWT y hashing de contraseñas
- **database/**: Configuración y conexión a la base de datos PostgreSQL

## Archivos que Contendrá

### config/
- **settings.py**: Clase de configuración que carga variables de entorno y define valores por defecto
- **constants.py**: Constantes compartidas de la aplicación (rutas, límites, configuraciones)

### security/
- **jwt_handler.py**: Manejo de tokens JWT (creación, verificación, decodificación)
- **password.py**: Funciones para hash y verificación de contraseñas usando bcrypt
- **dependencies.py**: Dependencias de seguridad para autenticación en endpoints

### database/
- **base.py**: Configuración de SQLAlchemy (engine, session maker, base class)
- **session.py**: Gestión de sesiones de base de datos y dependency injection

## Configuración

El módulo core se encarga de:

- Cargar y validar variables de entorno
- Configurar la conexión a PostgreSQL mediante SQLAlchemy
- Gestionar sesiones de base de datos con dependency injection
- Proporcionar utilidades de seguridad reutilizables

## Principios

Este módulo sigue principios de diseño:

- **Configuración centralizada**: Toda la configuración se gestiona desde un solo lugar
- **Separación de concerns**: Cada componente tiene una responsabilidad específica
- **Dependency injection**: Los componentes se inyectan donde se necesitan
- **Testabilidad**: La configuración puede ser fácilmente mockeada en tests


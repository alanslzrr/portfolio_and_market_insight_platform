# Capa de Repositorios

Este módulo implementa el patrón Repository para abstraer el acceso a datos. Cada repositorio proporciona métodos específicos para realizar operaciones CRUD y consultas especializadas sobre las entidades del dominio.

## Archivos que Contendrá

- **base.py**: Repositorio base abstracto:
  - `BaseRepository`: Clase base con métodos CRUD genéricos (create, get_by_id, update, delete, list)
  - Define la interfaz común para todos los repositorios
  - Implementa métodos genéricos que pueden ser sobrescritos por repositorios específicos

- **user_repository.py**: Repositorio de usuarios:
  - `get_by_email()`: Obtener usuario por email
  - `get_user_profile()`: Obtener perfil de usuario
  - `update_profile()`: Actualizar perfil de usuario
  - `get_active_sessions()`: Obtener sesiones activas de un usuario
  - `deactivate_session()`: Invalidar una sesión específica

- **portfolio_repository.py**: Repositorio de carteras:
  - `get_by_user_id()`: Obtener todas las carteras de un usuario
  - `get_portfolio_positions()`: Obtener todas las posiciones de una cartera
  - `get_portfolio_operations()`: Obtener todas las operaciones de una cartera
  - `update_portfolio_balance()`: Actualizar balance y métricas de una cartera
  - `calculate_portfolio_metrics()`: Calcular métricas de rendimiento

- **operation_repository.py**: Repositorio de operaciones:
  - `get_by_portfolio()`: Obtener operaciones de una cartera
  - `get_by_asset()`: Obtener operaciones de un activo específico
  - `filter_by_date_range()`: Filtrar operaciones por rango de fechas
  - `filter_by_type()`: Filtrar operaciones por tipo (compra/venta)
  - `get_portfolio_statistics()`: Obtener estadísticas de operaciones

- **asset_repository.py**: Repositorio de activos:
  - `get_by_symbol()`: Obtener activo por símbolo
  - `search_assets()`: Buscar activos por nombre o símbolo
  - `get_historical_prices()`: Obtener precios históricos de un activo
  - `get_latest_price()`: Obtener el precio más reciente
  - `sync_asset_data()`: Sincronizar datos de activo desde API externa

- **analysis_repository.py**: Repositorio de análisis:
  - `get_by_portfolio()`: Obtener análisis de una cartera
  - `get_by_asset()`: Obtener análisis de un activo
  - `get_cached_analysis()`: Obtener análisis desde caché si está válido
  - `invalidate_cache()`: Invalidar análisis en caché

## Patrón Repository

Este módulo implementa el patrón Repository que:

- Abstrae el acceso a datos de la lógica de negocio
- Facilita el testing mediante mock de repositorios
- Proporciona una interfaz clara para operaciones de datos
- Permite cambiar la implementación de persistencia sin afectar servicios

## Principios

Los repositorios siguen principios de diseño:

- **Single Responsibility**: Cada repositorio maneja una entidad específica
- **Dependency Inversion**: Los servicios dependen de abstracciones (repositorios)
- **Query Methods**: Métodos con nombres descriptivos que expresan la intención
- **Transaction Management**: Los repositorios trabajan dentro de transacciones gestionadas por servicios


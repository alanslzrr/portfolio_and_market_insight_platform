# Modelos de Dominio

Este módulo contiene todas las entidades del dominio representadas como modelos SQLAlchemy. Estos modelos definen la estructura de las tablas de la base de datos y las relaciones entre ellas.

## Archivos que Contendrá

- **user.py**: Modelo de usuario:
  - `User`: Representa usuarios del sistema con email, contraseña hasheada, nombre completo, estado de verificación
  - `UserProfile`: Perfil extendido del usuario con preferencias, moneda por defecto, timezone
  - `UserSession`: Sesiones activas con refresh tokens

- **portfolio.py**: Modelos relacionados con carteras:
  - `Portfolio`: Cartera principal con nombre, moneda base, descripción y métricas calculadas
  - `PortfolioAsset`: Posiciones de activos dentro de una cartera con cantidad, precio promedio, valor actual

- **operation.py**: Modelo de operaciones:
  - `Operation`: Operaciones de compra y venta con cantidad, precio, comisiones, fecha, notas

- **asset.py**: Modelos de activos financieros:
  - `Asset`: Información de activos (símbolo, nombre, tipo, exchange, moneda)
  - `AssetPrice`: Precios históricos y actuales de activos con timestamp y fuente

- **analysis.py**: Modelos de análisis:
  - `Analysis`: Análisis generados por IA con texto, indicadores técnicos, fecha de generación
  - `AnalysisRequest`: Registro de solicitudes de análisis con estado y timestamps

- **__init__.py**: Exporta todos los modelos y configura las relaciones entre ellos

## Relaciones

Los modelos están relacionados mediante foreign keys:

- User → Portfolios (un usuario tiene muchas carteras)
- Portfolio → PortfolioAssets (una cartera tiene muchas posiciones)
- Portfolio → Operations (una cartera tiene muchas operaciones)
- Portfolio → Analysis (una cartera puede tener análisis)
- Operation → Asset (una operación referencia un activo)
- PortfolioAsset → Asset (una posición referencia un activo)

## Funcionalidades

Los modelos incluyen:

- Métodos de negocio: `calculate_metrics()`, `update_balance()`, `verify_password()`
- Validaciones: Métodos para validar datos antes de persistir
- Relaciones lazy loading: Optimización de consultas mediante relaciones SQLAlchemy
- Timestamps automáticos: `created_at` y `updated_at` gestionados automáticamente

## Migraciones

Los modelos se utilizan con Alembic para generar migraciones de base de datos que crean y actualizan las tablas según la estructura definida en los modelos.


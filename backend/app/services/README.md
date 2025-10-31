# Capa de Servicios - Lógica de Negocio

Este módulo contiene toda la lógica de negocio de la aplicación. Los servicios coordinan las operaciones complejas, aplican las reglas de negocio y utilizan los repositorios para acceder a los datos.

## Archivos que Contendrá

- **auth_service.py**: Servicio de autenticación:
  - `register_user()`: Registra nuevo usuario con hash de contraseña y verificación de email
  - `authenticate_user()`: Autentica usuario y genera tokens JWT
  - `verify_email()`: Verifica email mediante token
  - `refresh_token()`: Renueva access token usando refresh token
  - `logout()`: Cierra sesión e invalida refresh token
  - `forgot_password()`: Genera token de recuperación de contraseña
  - `reset_password()`: Restablece contraseña con token válido

- **portfolio_service.py**: Servicio de carteras:
  - `create_portfolio()`: Crea nueva cartera con validaciones
  - `get_portfolio()`: Obtiene cartera con validación de permisos
  - `update_portfolio()`: Actualiza información de cartera
  - `delete_portfolio()`: Elimina cartera y sus datos relacionados
  - `get_portfolio_details()`: Obtiene detalles completos con métricas actualizadas
  - `calculate_portfolio_metrics()`: Calcula métricas de rendimiento en tiempo real

- **operation_service.py**: Servicio de operaciones:
  - `create_operation()`: Crea operación con validaciones de negocio
  - `get_operations()`: Obtiene operaciones con filtros aplicados
  - `update_operation()`: Actualiza operación existente
  - `delete_operation()`: Elimina operación y actualiza cartera
  - `import_operations_csv()`: Importa operaciones desde CSV con validación
  - `export_operations_csv()`: Exporta operaciones a CSV
  - `validate_operation_quantity()`: Valida cantidad disponible para ventas

- **market_data_service.py**: Servicio de datos de mercado:
  - `get_current_price()`: Obtiene precio actual con caché
  - `get_historical_prices()`: Obtiene datos históricos con caché
  - `get_asset_info()`: Obtiene información de activo
  - `sync_market_data()`: Sincroniza datos desde Alpha Vantage API
  - `refresh_price_cache()`: Actualiza caché de precios

- **ai_service.py**: Servicio de análisis con IA:
  - `generate_portfolio_analysis()`: Genera análisis completo de cartera con IA
  - `generate_asset_analysis()`: Genera análisis de activo individual
  - `get_cached_analysis()`: Obtiene análisis desde caché si está válido
  - `process_market_data()`: Procesa datos históricos para análisis

- **user_service.py**: Servicio de usuarios:
  - `get_user_profile()`: Obtiene perfil de usuario
  - `update_user_profile()`: Actualiza perfil con validaciones
  - `change_password()`: Cambia contraseña con validación de contraseña actual
  - `delete_user_account()`: Elimina cuenta de usuario
  - `get_user_activity()`: Obtiene historial de actividad

## Responsabilidades

Los servicios se encargan de:

- **Lógica de negocio**: Aplican reglas y validaciones de negocio
- **Coordinación**: Coordinan múltiples repositorios y servicios externos
- **Transacciones**: Gestionan transacciones de base de datos
- **Integraciones**: Integran con servicios externos (APIs, caché)
- **Transformaciones**: Transforman datos entre capas (modelos ↔ esquemas)

## Principios

Los servicios siguen principios de diseño:

- **Single Responsibility**: Cada servicio tiene un dominio específico
- **Dependency Injection**: Reciben repositorios y otros servicios como dependencias
- **Transaction Management**: Gestionan transacciones de base de datos
- **Error Handling**: Manejan errores de negocio y los convierten en excepciones apropiadas

## Integraciones

Los servicios se integran con:

- **Repositorios**: Para acceso a datos
- **Servicios externos**: Alpha Vantage API, OpenAI API
- **Caché**: Redis para optimización
- **Servicios de utilidad**: Email, logging, etc.


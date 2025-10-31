# Esquemas de Validación y Serialización

Este módulo contiene todos los esquemas de Pydantic que definen la estructura de los datos de entrada y salida de la API. Estos esquemas validan los datos, proporcionan documentación automática y serializan las respuestas.

## Estructura

Los esquemas están organizados por dominio funcional:

- **auth/**: Esquemas relacionados con autenticación
- **portfolio/**: Esquemas relacionados con carteras
- **operation/**: Esquemas relacionados con operaciones
- **user/**: Esquemas relacionados con usuarios
- **market/**: Esquemas relacionados con datos de mercado
- **common/**: Esquemas compartidos y base

## Archivos que Contendrá

### auth/
- **schemas.py**: Esquemas de autenticación:
  - `UserRegister`: Datos de registro (email, password, full_name)
  - `UserLogin`: Credenciales de login (email, password)
  - `TokenResponse`: Respuesta con tokens (access_token, refresh_token, token_type, expires_in)
  - `RefreshTokenRequest`: Solicitud de renovación de token
  - `PasswordReset`: Solicitud de restablecimiento de contraseña

### portfolio/
- **schemas.py**: Esquemas de carteras:
  - `PortfolioCreate`: Datos para crear cartera (name, base_currency, description)
  - `PortfolioUpdate`: Datos para actualizar cartera
  - `PortfolioResponse`: Respuesta con información de cartera (id, name, métricas)
  - `PortfolioAssetResponse`: Respuesta con información de posición (symbol, quantity, valor actual)
  - `PerformanceResponse`: Respuesta con métricas de rendimiento

### operation/
- **schemas.py**: Esquemas de operaciones:
  - `OperationCreate`: Datos para crear operación (portfolio_id, asset_symbol, type, quantity, price, fees, date)
  - `OperationUpdate`: Datos para actualizar operación
  - `OperationResponse`: Respuesta con información de operación
  - `OperationFilters`: Filtros para consultar operaciones (portfolio_id, asset_symbol, type, date_range)

### user/
- **schemas.py**: Esquemas de usuarios:
  - `UserProfileResponse`: Respuesta con perfil de usuario
  - `UserUpdate`: Datos para actualizar perfil
  - `PasswordChange`: Datos para cambiar contraseña
  - `ActivityResponse`: Respuesta con actividad del usuario

### market/
- **schemas.py**: Esquemas de datos de mercado:
  - `QuoteResponse`: Respuesta con cotización (symbol, price, currency, timestamp)
  - `HistoricalPriceResponse`: Respuesta con datos históricos
  - `AssetInfoResponse`: Respuesta con información de activo
  - `SearchResponse`: Respuesta de búsqueda de activos

### common/
- **schemas.py**: Esquemas compartidos:
  - `BaseSchema`: Clase base con configuración común
  - `PaginationParams`: Parámetros de paginación (limit, offset)
  - `ErrorMessage`: Mensaje de error estándar
  - `SuccessMessage`: Mensaje de éxito estándar

## Funcionalidades

Los esquemas proporcionan:

- **Validación automática**: Validan tipos, rangos y formatos de datos
- **Documentación automática**: FastAPI genera documentación OpenAPI desde los esquemas
- **Serialización**: Convierten modelos SQLAlchemy a diccionarios JSON
- **Type hints**: Proporcionan type hints para mejor desarrollo
- **Validadores personalizados**: Validaciones de negocio específicas (emails, fechas, cantidades)

## Ventajas

El uso de esquemas Pydantic ofrece:

- Validación temprana de datos de entrada
- Documentación automática y siempre actualizada
- Type safety mediante type hints
- Serialización consistente de respuestas
- Mensajes de error claros y descriptivos


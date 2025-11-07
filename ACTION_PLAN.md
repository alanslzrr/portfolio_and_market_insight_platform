# Backend Implementation Plan

## FASE 0: Configuración Base del Proyecto

### Bloque 0.1: Estructura de Directorios y Dependencias

**Archivo:** `backend/requirements.txt`

**Objetivo:**
Establecer la estructura base del proyecto y definir todas las dependencias necesarias para el desarrollo del backend.

**Tareas de Implementación:**
- Crear estructura completa de directorios `/backend/app/` con subdirectorios: api, core, models, repositories, schemas, services, middleware, utils
- Definir lista completa de dependencias en requirements.txt (FastAPI, SQLAlchemy, Alembic, Pydantic, Passlib, Redis, Pandas, OpenAI, Pytest)
- Crear archivos `__init__.py` en todos los paquetes Python
- Configurar archivo `.gitignore` para Python

**Test Asociado:**
- Ejecutar `pip install -r requirements.txt` sin errores de dependencias
- Verificar importación exitosa: `python -c "import fastapi, sqlalchemy, pydantic"`
- Validar ausencia de conflictos de versiones con `pip check`

**Resultado Esperado:**
- Estructura de directorios completa según arquitectura documentada
- requirements.txt con 15+ dependencias especificadas con versiones
- Entorno virtual configurado sin errores de instalación
- Sin warnings de dependencias incompatibles

**Estado:** Pendiente

---

### Bloque 0.2: Configuración Central con Variables de Entorno

**Archivo:** `backend/app/core/config/settings.py`

**Objetivo:**
Implementar sistema centralizado de configuración usando Pydantic Settings para gestionar variables de entorno de forma tipada y segura.

**Tareas de Implementación:**
- Crear clase `Settings` heredando de `BaseSettings` de pydantic-settings
- Definir variables agrupadas por categoría:
  - Database: DATABASE_URL, pool_size, max_overflow
  - Security: SECRET_KEY, ALGORITHM, token TTLs
  - APIs externas: ALPHA_VANTAGE_API_KEY, OPENAI_API_KEY
  - Cache: REDIS_URL, TTL configs
  - CORS: lista de orígenes permitidos
- Configurar lectura desde `.env` con `Config.env_file`
- Establecer valores por defecto razonables
- Exportar singleton `settings`

**Test Asociado:**
- Test unitario: validar carga de variables desde .env
- Test: verificar ValidationError si faltan variables críticas
- Test: comprobar aplicación de valores por defecto
- Test: validar tipos de datos correctos (str, int, list)

**Resultado Esperado:**
- Clase Settings completamente tipada con 15+ variables
- Archivo `.env.example` con plantilla de todas las variables
- ValidationError claro si falta DATABASE_URL, SECRET_KEY o API keys
- Singleton accesible: `from core.config.settings import settings`

**Estado:** Pendiente

---

### Bloque 0.3: Configuración de Motor de Base de Datos

**Archivo:** `backend/app/core/database/session.py`

**Objetivo:**
Configurar motor SQLAlchemy con pool de conexiones, crear Base declarativa y definir dependency injection para sesiones.

**Tareas de Implementación:**
- Crear `engine` usando create_engine con DATABASE_URL
- Configurar pool: pool_pre_ping=True, pool_size desde settings
- Crear `SessionLocal` con sessionmaker (autocommit=False, autoflush=False)
- Definir `Base` declarativa con declarative_base()
- Implementar generador `get_db()` con try/finally para cleanup

**Test Asociado:**
- Test integración: establecer conexión exitosa a PostgreSQL
- Test: ejecutar `SELECT 1` y verificar resultado
- Test: crear tabla temporal, validar creación, eliminar
- Test: probar rollback de transacción
- Test: validar cierre de sesiones (no memory leaks)

**Resultado Esperado:**
- Conexión estable a PostgreSQL sin errores
- Pool configurado con límites definidos (size=5, max_overflow=10)
- Función get_db() retorna Generator funcional
- Base declarativa lista para herencia en modelos
- Sessions se crean y destruyen correctamente

**Estado:** Pendiente

---

## FASE 1: Capa de Modelos (Domain Models)

### Bloque 1.1: Modelos de Usuario y Autenticación

**Archivos:** `backend/app/models/user.py`

**Objetivo:**
Implementar modelos ORM para gestión de usuarios, perfiles y sesiones con relaciones y constraints apropiados.

**Tareas de Implementación:**
- **Clase User**: definir con 12 campos incluyendo id (UUID), email (unique, indexed), password_hash, is_active, is_verified, tokens, timestamps
- Relaciones: profile (one-to-one, cascade delete), sessions (one-to-many), portfolios (one-to-many)
- Métodos: verify_password(password: str) -> bool, hash_password(password: str) -> str (static)
- **Clase UserProfile**: FK a User, campos default_currency, timezone, language, preferences (JSON)
- Constraint unique en user_id
- **Clase UserSession**: FK a User, refresh_token (unique, indexed), expires_at, is_active
- Configurar cascadas de eliminación en todas las FKs

**Test Asociado:**
- Test: crear User, verificar generación automática de UUID
- Test: validar hashing y verificación de contraseñas
- Test: constraint email único (IntegrityError esperado en duplicado)
- Test: relación User-UserProfile (one-to-one bidireccional)
- Test: relación User-UserSession (one-to-many)
- Test: cascade delete - eliminar User elimina Profile y Sessions
- Test: validar índices creados en email y refresh_token

**Resultado Esperado:**
- 3 clases ORM: User, UserProfile, UserSession funcionales
- Relaciones bidireccionales configuradas correctamente
- Constraints aplicados: unique email, unique user_id en profile
- Cascadas de eliminación funcionando
- Métodos de negocio (verify_password) operativos
- Índices optimizando queries frecuentes

**Estado:** Pendiente

---

### Bloque 1.2: Modelos de Portfolio y Posiciones

**Archivos:** `backend/app/models/portfolio.py`

**Objetivo:**
Implementar modelos para gestión de carteras y posiciones de activos con cálculo automático de métricas financieras.

**Tareas de Implementación:**
- **Clase Portfolio**: 12 campos incluyendo métricas calculadas (total_value, total_cost, gain_loss con Decimal 20,2)
- Constraint UniqueConstraint en (user_id, name)
- Índice compuesto en (user_id, created_at)
- Relaciones: user, assets (one-to-many, cascade delete), operations, analyses
- Métodos: calculate_metrics() -> dict, update_balance() actualiza campos
- **Clase PortfolioAsset**: cantidad (Decimal 20,8), precios, ganancias
- Constraint UniqueConstraint en (portfolio_id, asset_symbol)
- Métodos: calculate_position_value() -> Decimal, update_current_price(price)

**Test Asociado:**
- Test: crear Portfolio, verificar inicialización con métricas en 0
- Test: constraint unique (user_id, name) - dos portfolios mismo nombre falla
- Test: crear PortfolioAsset, calcular current_value correctamente
- Test: constraint unique (portfolio_id, asset_symbol)
- Test: calculate_metrics() con múltiples posiciones suma correctamente
- Test: update_balance() actualiza campos total_value, total_cost, gain_loss
- Test: cascade delete Portfolio elimina PortfolioAssets
- Test: precisión decimal - verificar cálculos con 2 decimales

**Resultado Esperado:**
- 2 clases: Portfolio, PortfolioAsset funcionales
- Cálculos financieros precisos usando Decimal (no float)
- Constraints de unicidad aplicados correctamente
- Métodos calculan métricas: gain_loss_percent = (gain_loss/total_cost)*100
- Relaciones y cascadas configuradas
- Índices optimizando consultas por usuario y símbolo

**Estado:** Pendiente

---

### Bloque 1.3: Modelo de Operaciones Financieras

**Archivos:** `backend/app/models/operation.py`

**Objetivo:**
Implementar modelo para registro de operaciones de compra/venta con validaciones de integridad y cálculos automáticos.

**Tareas de Implementación:**
- Definir Enum **OperationType** con valores: BUY, SELL
- **Clase Operation**: 11 campos incluyendo operation_type (Enum), quantity (Decimal 20,8), price, fees, total_amount
- Aplicar CheckConstraints: quantity > 0, price > 0, fees >= 0
- Crear índices compuestos: (portfolio_id, date), (asset_symbol, date), (operation_type)
- Relación: portfolio (FK con cascade delete)
- Métodos: calculate_total() diferenciado por tipo (BUY: qty*price+fees, SELL: qty*price-fees), validate_operation() -> bool

**Test Asociado:**
- Test: operación BUY - calculate_total() = (10 * 150) + 5 = 1505
- Test: operación SELL - calculate_total() = (10 * 160) - 5 = 1595
- Test: CheckConstraint quantity negativa lanza IntegrityError
- Test: CheckConstraint price ≤ 0 lanza IntegrityError
- Test: CheckConstraint fees < 0 lanza IntegrityError
- Test: validate_operation() retorna True con datos válidos, False con inválidos
- Test: relación con Portfolio funcional
- Test: cascade delete Portfolio elimina Operations

**Resultado Esperado:**
- Clase Operation completamente funcional con 11 campos
- Enum OperationType aplicado correctamente en BD
- CheckConstraints impiden datos inválidos a nivel de BD
- Cálculo total_amount diferenciado por tipo
- Validación pre-persistencia funcional
- 3 índices optimizando queries por cartera, activo y fecha

**Estado:** Pendiente

---

### Bloque 1.4: Modelos de Activos y Precios

**Archivos:** `backend/app/models/asset.py`

**Objetivo:**
Implementar modelos para catálogo de activos financieros y registro de precios históricos con validaciones temporales.

**Tareas de Implementación:**
- Definir Enum **AssetType** con valores: STOCK, ETF, CRYPTO
- **Clase Asset**: symbol (unique, indexed), name, asset_type (Enum), currency, exchange, metadata (JSON)
- Relación: prices (one-to-many)
- **Clase AssetPrice**: asset_symbol (FK), price (Decimal 20,2), date, timestamp, source
- Constraint UniqueConstraint en (asset_symbol, timestamp)
- Índice compuesto en (asset_symbol, date)
- Método: is_valid() verifica price > 0 y timestamp no futuro

**Test Asociado:**
- Test: crear Asset, verificar constraint unique en symbol
- Test: Enum AssetType rechaza valores no permitidos
- Test: crear múltiples AssetPrice para mismo Asset
- Test: constraint unique (asset_symbol, timestamp) - duplicado falla
- Test: índice compuesto permite queries eficientes por rango de fechas
- Test: is_valid() retorna False con price = 0
- Test: is_valid() retorna False con timestamp futuro
- Test: relación Asset-AssetPrice (one-to-many) funcional

**Resultado Esperado:**
- 2 clases: Asset, AssetPrice funcionales
- Symbol único por activo garantizado por constraint
- Precios históricos sin duplicados por timestamp
- Índice compuesto (asset_symbol, date) optimiza queries temporales
- Validación is_valid() previene datos inconsistentes
- Campo metadata JSON permite extensibilidad futura

**Estado:** Pendiente

---

### Bloque 1.5: Modelos de Análisis con IA

**Archivos:** `backend/app/models/analysis.py`

**Objetivo:**
Implementar modelos para almacenar análisis generados por IA con sistema de caché y tracking de requests.

**Tareas de Implementación:**
- Definir Enum **AnalysisType**: PORTFOLIO, ASSET
- Definir Enum **AnalysisStatus**: PENDING, PROCESSING, COMPLETED, FAILED
- **Clase Analysis**: portfolio_id (FK nullable), asset_symbol (nullable), analysis_type, analysis_text (Text), technical_indicators (JSON)
- Campos temporales: generated_at, expires_at, cached (boolean)
- Índice compuesto en (portfolio_id, asset_symbol, cached)
- Métodos: is_expired() compara expires_at con now(), get_disclaimer() retorna texto legal
- **Clase AnalysisRequest**: user_id (FK), portfolio_id (FK nullable), asset_symbol (nullable), status (Enum), error_message, timestamps
- Índice en (user_id, status)

**Test Asociado:**
- Test: crear Analysis tipo PORTFOLIO con portfolio_id
- Test: crear Analysis tipo ASSET con asset_symbol
- Test: is_expired() retorna True si expires_at < now()
- Test: is_expired() retorna False si expires_at > now()
- Test: get_disclaimer() retorna disclaimer estándar (>50 caracteres)
- Test: crear AnalysisRequest con status PENDING
- Test: actualizar status a COMPLETED, verified completed_at se setea
- Test: índices en caché y status optimizan queries
- Test: relaciones con User y Portfolio (nullable) funcionales

**Resultado Esperado:**
- 2 clases: Analysis, AnalysisRequest funcionales
- Sistema de caché temporal basado en expires_at
- Estados de análisis bien definidos con Enum
- Disclaimer legal incluido automáticamente
- Tracking de requests para auditoría
- Índices optimizando búsquedas de caché activo

**Estado:** Pendiente

---

### Bloque 1.6: Configuración de Migraciones con Alembic

**Archivos:** `backend/alembic/`, `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/001_initial_migration.py`

**Objetivo:**
Inicializar Alembic para gestión de migraciones de BD y generar migración inicial con todos los modelos.

**Tareas de Implementación:**
- Ejecutar `alembic init alembic` en directorio backend
- Configurar alembic.ini: reemplazar sqlalchemy.url con referencia a settings
- Modificar env.py:
  - Importar Base y todos los modelos (user, portfolio, operation, asset, analysis)
  - Configurar target_metadata = Base.metadata
  - Implementar run_migrations_offline() y run_migrations_online()
- Generar migración: `alembic revision --autogenerate -m "Initial migration with all models"`
- Revisar archivo de migración generado verificando:
  - 8 tablas creadas: users, user_profiles, user_sessions, portfolios, portfolio_assets, operations, assets, asset_prices, analyses, analysis_requests
  - Todos los índices presentes
  - Foreign keys configurados con CASCADE
  - Constraints (unique, check) aplicados
  - Enums de PostgreSQL creados
- Aplicar migración: `alembic upgrade head`

**Test de Integración:**
- Test: ejecutar `alembic upgrade head` en BD limpia
- Test: verificar creación de 10 tablas usando query a information_schema.tables
- Test: validar índices creados usando pg_indexes
- Test: verificar foreign keys con pg_constraint (8+ FKs esperados)
- Test: comprobar constraints unique y check aplicados
- Test: verificar enums PostgreSQL creados (operation_type, asset_type, analysis_type, analysis_status)
- Test: ejecutar `alembic downgrade base`
- Test: verificar todas las tablas eliminadas
- Test: re-ejecutar upgrade para validar idempotencia

**Resultado Esperado:**
- Alembic configurado y funcional con env.py personalizado
- Migración inicial generada con 10 tablas
- Upgrade crea esquema completo sin errores SQL
- Downgrade limpia esquema completamente
- 15+ índices creados correctamente
- 8+ foreign keys con CASCADE
- 5+ constraints unique
- 3+ constraints check
- 4 enums PostgreSQL
- Migraciones versionadas en /alembic/versions/

**Estado:** Pendiente

---

## FASE 2: Capa de Schemas (Pydantic DTOs)

### Bloque 2.1: Schemas de Autenticación

**Archivos:** `backend/app/schemas/auth.py`

**Objetivo:**
Implementar esquemas Pydantic para validación de requests/responses de autenticación con validators personalizados.

**Tareas de Implementación:**
- **UserRegister**: email, password, full_name
  - Validator email: regex EmailStr de Pydantic
  - Validator password: min 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número
- **UserLogin**: email, password
- **TokenResponse**: access_token, refresh_token, token_type (default "bearer"), expires_in
- **RefreshTokenRequest**: refresh_token
- **ForgotPassword**: email
- **PasswordReset**: token, new_password (con mismo validator que UserRegister)
- Configurar `Config.from_attributes = True` para ORM compatibility

**Test Asociado:**
- Test: UserRegister con email inválido lanza ValidationError
- Test: UserRegister con password débil (<8 chars) lanza ValidationError
- Test: UserRegister con password sin mayúscula lanza ValidationError
- Test: Serialización TokenResponse a dict JSON
- Test: Deserialización desde dict a UserRegister
- Test: Campos opcionales vs requeridos funcionan correctamente

**Resultado Esperado:**
- 6 schemas de autenticación funcionales
- Validadores custom para email y password strength
- Mensajes de error descriptivos en español
- ORM compatibility configurado
- Serialization/deserialization funcional

**Estado:** Pendiente

---

### Bloque 2.2: Schemas de Usuario

**Archivos:** `backend/app/schemas/user.py`

**Objetivo:**
Implementar schemas para gestión de perfiles de usuario con responses y updates.

**Tareas de Implementación:**
- **UserResponse**: id (UUID), email, full_name, is_verified, is_active, created_at
  - Excluir password_hash y tokens sensibles
- **UserProfileResponse**: UserResponse + default_currency, timezone, language, preferences
- **UserUpdate**: full_name (opcional), default_currency, timezone, language
  - Validators para currency (3 chars ISO), timezone (pytz válido)
- **PasswordChange**: current_password, new_password (con validator strength)
- **ActivityResponse**: action (str), timestamp (datetime), details (dict)
- Configurar `Config.from_attributes = True`

**Test Asociado:**
- Test: UserResponse excluye campos sensibles (password_hash, tokens)
- Test: UserUpdate con currency inválida (<3 chars) lanza ValidationError
- Test: UserUpdate con timezone inválido lanza ValidationError
- Test: PasswordChange valida strength de new_password
- Test: Serialización desde modelo User ORM a UserResponse
- Test: Todos los campos UUID serializan como string

**Resultado Esperado:**
- 5 schemas de usuario funcionales
- Campos sensibles excluidos de responses
- Validators para currency y timezone
- ORM compatibility funcional
- UUID serialization configurada

**Estado:** Pendiente

---

### Bloque 2.3: Schemas de Portfolio

**Archivos:** `backend/app/schemas/portfolio.py`

**Objetivo:**
Implementar schemas para gestión de carteras con responses detallados incluyendo métricas y posiciones.

**Tareas de Implementación:**
- **PortfolioCreate**: name, base_currency, description (opcional)
  - Validator name: 3-100 caracteres
  - Validator base_currency: 3 chars ISO
- **PortfolioUpdate**: name (opcional), description (opcional)
- **PortfolioResponse**: id, user_id, name, base_currency, total_value, total_cost, total_gain_loss, total_gain_loss_percent, created_at, updated_at
  - Decimals serializan como float con 2 decimales
- **PortfolioAssetResponse**: asset_symbol, quantity, average_price, current_price, current_value, gain_loss, gain_loss_percent
- **PortfolioDetailResponse**: hereda PortfolioResponse + positions (List[PortfolioAssetResponse]) + recent_operations (List[OperationResponse])
- Configurar JSON encoders para Decimal y UUID

**Test Asociado:**
- Test: PortfolioCreate con name <3 chars lanza ValidationError
- Test: PortfolioCreate con base_currency inválida lanza ValidationError
- Test: PortfolioResponse serializa Decimals como float con 2 decimales
- Test: PortfolioDetailResponse incluye lista de positions y operations
- Test: Serialización desde Portfolio ORM a PortfolioResponse
- Test: UUID serializa como string en JSON

**Resultado Esperado:**
- 5 schemas de portfolio funcionales
- Validators para name length y currency format
- Serialization de Decimal configurada (2 decimales)
- Responses nested con positions y operations
- JSON encoders custom configurados

**Estado:** Pendiente

---

### Bloque 2.4: Schemas de Operaciones

**Archivos:** `backend/app/schemas/operation.py`

**Objetivo:**
Implementar schemas para registro y consulta de operaciones financieras con validación de datos transaccionales.

**Tareas de Implementación:**
- **OperationCreate**: portfolio_id (UUID), asset_symbol, operation_type (Literal["buy", "sell"]), quantity (Decimal), price (Decimal), currency, fees (Decimal opcional, default 0), date (datetime), notes (opcional)
  - Validators: quantity > 0, price > 0, fees >= 0
- **OperationUpdate**: price (opcional), fees (opcional), notes (opcional)
- **OperationResponse**: todos los campos + total_amount (Decimal), created_at
- **OperationFilter**: portfolio_id (opcional), asset_symbol (opcional), operation_type (opcional), date_from (opcional), date_to (opcional)
  - Validator: date_from < date_to si ambos presentes
- **OperationImportRow**: para CSV import - asset_symbol, operation_type, quantity, price, fees, date
- Configurar validators para Decimals positivos

**Test Asociado:**
- Test: OperationCreate con quantity ≤ 0 lanza ValidationError
- Test: OperationCreate con price ≤ 0 lanza ValidationError
- Test: OperationCreate con fees < 0 lanza ValidationError
- Test: OperationFilter con date_from > date_to lanza ValidationError
- Test: OperationResponse calcula total_amount correctamente
- Test: Serialización Decimal con precisión 20,2

**Resultado Esperado:**
- 5 schemas de operaciones funcionales
- Validators impiden valores negativos/cero
- Validación de rangos de fechas
- CSV import schema funcional
- Cálculo de total_amount integrado en response

**Estado:** Pendiente

---

### Bloque 2.5: Schemas de Mercado

**Archivos:** `backend/app/schemas/market.py`

**Objetivo:**
Implementar schemas para datos de mercado (activos, precios actuales, históricos) con estructuras para integración externa.

**Tareas de Implementación:**
- **AssetInfo**: symbol, name, asset_type (Literal["stock", "etf", "crypto"]), currency, exchange, metadata (dict opcional)
- **PricePoint**: date, open, high, low, close, volume
  - Validators: OHLC values > 0, high >= low, high >= open, high >= close
- **CurrentPriceResponse**: symbol, price (Decimal), currency, timestamp, source (default "alpha_vantage")
- **HistoricalPriceResponse**: symbol, prices (List[PricePoint]), date_from, date_to
- **AssetSearchResponse**: results (List[AssetInfo]), total_count
- Configurar serialization para datetime con timezone UTC

**Test Asociado:**
- Test: PricePoint con high < low lanza ValidationError
- Test: PricePoint con valores OHLC ≤ 0 lanza ValidationError
- Test: CurrentPriceResponse serializa timestamp con timezone
- Test: HistoricalPriceResponse ordena prices por date
- Test: AssetInfo con asset_type inválido lanza ValidationError
- Test: Serialización de lista de PricePoint a JSON

**Resultado Esperado:**
- 5 schemas de mercado funcionales
- Validators para consistencia de datos OHLC
- Timezone handling configurado (UTC)
- Soporte para metadatos flexibles (dict)
- Listas ordenadas por fecha

**Estado:** Pendiente

---

### Bloque 2.6: Schemas de Análisis

**Archivos:** `backend/app/schemas/analysis.py`

**Objetivo:**
Implementar schemas para requests y responses de análisis con IA incluyendo indicadores técnicos estructurados.

**Tareas de Implementación:**
- **TechnicalIndicators**: rsi (float), macd (dict con signal, histogram), moving_averages (dict con sma_20, sma_50, ema_20), volatility (float), trend (str)
- **AnalysisRequest**: portfolio_id (UUID opcional), asset_symbol (opcional)
  - Validator: al menos uno de portfolio_id o asset_symbol debe estar presente
- **AnalysisResponse**: analysis_text (str largo), technical_indicators (TechnicalIndicators), generated_at (datetime), expires_at (datetime), disclaimer (str), cached (bool)
- **AnalysisHistory**: analyses (List[AnalysisResponse]), total_count
- Configurar disclaimer predeterminado: "Este análisis es informativo..."

**Test Asociado:**
- Test: AnalysisRequest sin portfolio_id ni asset_symbol lanza ValidationError
- Test: AnalysisRequest con ambos portfolio_id y asset_symbol es válido
- Test: AnalysisResponse incluye disclaimer automáticamente
- Test: TechnicalIndicators serializa correctamente nested dicts
- Test: Serialización de analysis_text largo (>1000 chars)
- Test: cached flag presente en response

**Resultado Esperado:**
- 4 schemas de análisis funcionales
- Validator custom para campos mutuamente exclusivos
- Disclaimer automático incluido
- Nested schemas (TechnicalIndicators) funcionales
- Soporte para textos largos (analysis_text)

**Estado:** Pendiente

---

### Bloque 2.7: Test Integral de Schemas

**Archivos:** `backend/tests/unit/schemas/test_all_schemas.py`

**Objetivo:**
Validar comportamiento integral de todos los schemas Pydantic con casos edge y serialization completa.

**Tareas de Test:**
- Test: serialización de 20+ schemas a dict
- Test: deserialización desde dict/JSON a schemas
- Test: validators custom funcionan correctamente (30+ casos)
- Test: campos requeridos vs opcionales
- Test: valores por defecto aplicados
- Test: tipos de datos validados (UUID, Decimal, datetime, Enum)
- Test: mensajes de error descriptivos en ValidationError
- Test: nested schemas serializan correctamente
- Test: listas de schemas funcionan
- Test: Config.from_attributes funciona con modelos ORM

**Resultado Esperado:**
- Suite completa de tests unitarios para schemas
- 100+ assertions ejecutándose exitosamente
- Cobertura >95% en módulo schemas
- Todos los validators probados con casos válidos e inválidos
- Serialization/deserialization bidireccional funcional
- ORM compatibility verificada con fixtures

**Estado:** Pendiente

---

## FASE 3: Componentes de Seguridad

### Bloque 3.1: Password Hasher con Bcrypt

**Archivos:** `backend/app/core/security/password.py`

**Objetivo:**
Implementar componente para hashing y verificación segura de contraseñas usando bcrypt con cost factor configurable.

**Tareas de Implementación:**
- Clase **PasswordHasher**:
  - Método `hash_password(password: str) -> str`: genera hash con bcrypt usando cost factor 12
  - Método `verify_password(plain_password: str, hashed_password: str) -> bool`: verifica password contra hash
  - Configurar bcrypt rounds desde settings (default 12)
  - Manejar excepciones de bcrypt apropiadamente

**Test Asociado:**
- Test: hash_password genera hash diferente cada vez (debido a salt)
- Test: verify_password retorna True con password correcta
- Test: verify_password retorna False con password incorrecta
- Test: hash generado tiene formato bcrypt válido ($2b$12$...)
- Test: tiempo de hash es razonable (<200ms)
- Test: hash de 2 passwords iguales produce salts diferentes

**Resultado Esperado:**
- Clase PasswordHasher funcional
- Hashes bcrypt con cost factor 12
- Verificación funciona correctamente
- Salts aleatorios en cada hash
- Tiempo de procesamiento aceptable (<200ms por hash)

**Estado:** Pendiente

---

### Bloque 3.2: JWT Handler para Tokens de Acceso

**Archivos:** `backend/app/core/security/jwt.py`

**Objetivo:**
Implementar handler para creación y validación de tokens JWT (access y refresh) con configuración de expiración.

**Tareas de Implementación:**
- Clase **JWTHandler**:
  - Método `create_access_token(data: dict, expires_delta: timedelta = None) -> str`: genera JWT con payload y TTL 15min
  - Método `create_refresh_token(user_id: UUID) -> str`: genera refresh token con TTL 7 días
  - Método `decode_token(token: str) -> dict`: decodifica y valida JWT, retorna payload
  - Método `verify_token(token: str) -> bool`: valida firma y expiración sin decodificar
  - Usar algoritmo HS256 con SECRET_KEY desde settings
  - Incluir claims: sub (user_id), exp (expiration), iat (issued at), type (access/refresh)
  - Manejar excepciones: JWTError, ExpiredSignatureError

**Test Asociado:**
- Test: create_access_token genera token JWT válido
- Test: decode_token retorna payload correcto
- Test: token expirado lanza ExpiredSignatureError
- Test: token con firma inválida lanza JWTError
- Test: verify_token retorna True para token válido
- Test: verify_token retorna False para token expirado/inválido
- Test: refresh token tiene TTL de 7 días
- Test: access token tiene TTL de 15 minutos

**Resultado Esperado:**
- Clase JWTHandler funcional
- Tokens generados con algoritmo HS256
- Access tokens con TTL 15min
- Refresh tokens con TTL 7 días
- Validación de firma y expiración funcional
- Excepciones manejadas apropiadamente

**Estado:** Pendiente

---

### Bloque 3.3: Generador de Tokens de Verificación

**Archivos:** `backend/app/core/security/tokens.py`

**Objetivo:**
Implementar generadores de tokens seguros para verificación de email y reset de contraseña con TTL configurable.

**Tareas de Implementación:**
- Función `generate_verification_token() -> str`: usa secrets.token_urlsafe(32)
- Función `generate_reset_token() -> str`: usa secrets.token_urlsafe(32)
- Función `verify_token_expiration(created_at: datetime, ttl_hours: int) -> bool`: verifica si token ha expirado
- Constantes configurables: EMAIL_VERIFICATION_TTL (24 horas), PASSWORD_RESET_TTL (1 hora)
- Tokens deben ser URL-safe y criptográficamente seguros

**Test Asociado:**
- Test: generate_verification_token produce token de 43 caracteres (32 bytes base64)
- Test: 2 tokens generados consecutivamente son diferentes
- Test: token contiene solo caracteres URL-safe [A-Za-z0-9_-]
- Test: verify_token_expiration retorna False si created_at + ttl < now()
- Test: verify_token_expiration retorna True si created_at + ttl > now()
- Test: tokens son criptográficamente seguros (alta entropía)

**Resultado Esperado:**
- 3 funciones generadoras funcionales
- Tokens de 43 caracteres URL-safe
- Tokens únicos con alta entropía
- Validación de expiración funcional
- TTLs configurables desde settings

**Estado:** Pendiente

---

### Bloque 3.4: Test Integral de Seguridad

**Archivos:** `backend/tests/unit/security/test_security_suite.py`

**Objetivo:**
Validar comportamiento integral de componentes de seguridad con escenarios complejos y casos edge.

**Tareas de Test:**
- Test: flujo completo registro usuario - hash password - verify
- Test: flujo completo login - create access token - decode - verificar claims
- Test: flujo refresh token - create - decode - renovar access token
- Test: token expirado no puede ser usado
- Test: token con SECRET_KEY incorrecta falla validación
- Test: password hasher resiste timing attacks
- Test: verificación de tokens con diferentes TTLs
- Test: casos edge: password vacío, token malformado, claims faltantes

**Resultado Esperado:**
- Suite de tests de seguridad completa
- 50+ assertions ejecutándose exitosamente
- Flujos end-to-end validados
- Casos edge cubiertos
- Cobertura >95% en módulo security
- No vulnerabilidades detectadas

**Estado:** Pendiente

---

## FASE 4: Capa de Repositorios (Repository Pattern)

### Bloque 4.1: Base Repository Genérico

**Archivos:** `backend/app/repositories/base.py`

**Objetivo:**
Implementar repositorio base genérico con operaciones CRUD comunes usando generics de Python para reutilización.

**Tareas de Implementación:**
- Clase genérica **BaseRepository[T]**:
  - Constructor: recibe Session de SQLAlchemy
  - Método `create(entity: T) -> T`: inserta y retorna entidad
  - Método `get_by_id(id: UUID) -> Optional[T]`: busca por ID
  - Método `update(entity: T) -> T`: actualiza entidad existente
  - Método `delete(id: UUID) -> bool`: elimina por ID, retorna success
  - Método `list(limit: int = 100, offset: int = 0, filters: dict = None) -> List[T]`: lista con paginación
  - Método `count(filters: dict = None) -> int`: cuenta registros
  - Usar TypeVar para generics: `T = TypeVar('T')`
  - Commit automático en create/update/delete con manejo de errores

**Test Asociado:**
- Test: create inserta registro y retorna con ID generado
- Test: get_by_id encuentra registro existente
- Test: get_by_id retorna None si no existe
- Test: update modifica registro y persiste cambios
- Test: delete elimina registro y retorna True
- Test: delete retorna False si registro no existe
- Test: list retorna registros paginados
- Test: count retorna número correcto de registros
- Test: rollback automático en caso de error

**Resultado Esperado:**
- Clase BaseRepository[T] completamente genérica
- 8 métodos CRUD funcionales
- Paginación implementada (limit/offset)
- Manejo de errores con rollback
- Reutilizable para todos los modelos
- Type hints correctos con generics

**Estado:** Pendiente

---

### Bloque 4.2: UserRepository

**Archivos:** `backend/app/repositories/user.py`

**Objetivo:**
Implementar repositorio especializado para gestión de usuarios, perfiles y sesiones con métodos específicos del dominio.

**Tareas de Implementación:**
- Clase **UserRepository** hereda BaseRepository[User]:
  - Método `get_by_email(email: str) -> Optional[User]`: busca por email (case-insensitive)
  - Método `get_user_profile(user_id: UUID) -> Optional[UserProfile]`: obtiene perfil con eager loading
  - Método `update_profile(user_id: UUID, data: dict) -> UserProfile`: actualiza o crea perfil
  - Método `create_session(user_id: UUID, refresh_token: str, expires_at: datetime) -> UserSession`: crea sesión activa
  - Método `get_active_sessions(user_id: UUID) -> List[UserSession]`: lista sesiones activas no expiradas
  - Método `deactivate_session(session_id: UUID) -> bool`: marca sesión como inactiva
  - Método `get_by_verification_token(token: str) -> Optional[User]`: busca por token verificación
  - Método `get_by_reset_token(token: str) -> Optional[User]`: busca por token reset, valida expiración
  - Usar joinedload para optimizar queries con relaciones

**Test de Integración:**
- Test: crear usuario y perfil en una transacción
- Test: get_by_email encuentra usuario (case-insensitive)
- Test: update_profile crea perfil si no existe
- Test: update_profile actualiza perfil existente
- Test: create_session genera sesión activa
- Test: get_active_sessions excluye sesiones expiradas
- Test: get_active_sessions excluye sesiones inactivas
- Test: deactivate_session marca is_active=False
- Test: get_by_verification_token encuentra usuario
- Test: get_by_reset_token valida expiración del token
- Test: manejo de duplicados (email único)

**Resultado Esperado:**
- Clase UserRepository con 8+ métodos específicos
- Búsquedas case-insensitive funcionales
- Eager loading optimiza queries
- Gestión completa de sesiones
- Validación de tokens con expiración
- Manejo de errores de integridad

**Estado:** Pendiente

---

### Bloque 4.3: PortfolioRepository

**Archivos:** `backend/app/repositories/portfolio.py`

**Objetivo:**
Implementar repositorio para gestión de carteras y posiciones con cálculo de métricas financieras.

**Tareas de Implementación:**
- Clase **PortfolioRepository** hereda BaseRepository[Portfolio]:
  - Método `get_by_user_id(user_id: UUID) -> List[Portfolio]`: lista carteras del usuario
  - Método `get_with_positions(portfolio_id: UUID) -> Optional[Portfolio]`: obtiene con eager loading de assets
  - Método `get_portfolio_positions(portfolio_id: UUID) -> List[PortfolioAsset]`: lista posiciones
  - Método `get_portfolio_operations(portfolio_id: UUID, limit: int = 50) -> List[Operation]`: últimas operaciones
  - Método `update_portfolio_balance(portfolio_id: UUID) -> Portfolio`: recalcula y actualiza métricas
  - Método `calculate_portfolio_metrics(portfolio_id: UUID) -> dict`: calcula sin persistir
  - Método `create_or_update_position(portfolio_id: UUID, asset_symbol: str, data: dict) -> PortfolioAsset`: upsert posición
  - Método `get_position(portfolio_id: UUID, asset_symbol: str) -> Optional[PortfolioAsset]`: busca posición específica
  - Método `delete_position(portfolio_id: UUID, asset_symbol: str) -> bool`: elimina posición si quantity = 0

**Test de Integración:**
- Test: get_by_user_id retorna solo carteras del usuario
- Test: get_with_positions hace eager loading de assets
- Test: create_or_update_position crea nueva posición
- Test: create_or_update_position actualiza posición existente
- Test: calculate_portfolio_metrics suma correctamente
- Test: update_portfolio_balance persiste métricas calculadas
- Test: get_position encuentra posición específica
- Test: delete_position elimina posición vacía
- Test: constraint unique (user_id, name) manejado

**Resultado Esperado:**
- Clase PortfolioRepository con 9 métodos
- Cálculo preciso de métricas financieras
- Upsert de posiciones funcional
- Eager loading optimiza queries
- Validación de ownership (user_id)
- Manejo de constraints de unicidad

**Estado:** Pendiente

---

### Bloque 4.4: OperationRepository

**Archivos:** `backend/app/repositories/operation.py`

**Objetivo:**
Implementar repositorio para gestión de operaciones financieras con filtrado avanzado y estadísticas.

**Tareas de Implementación:**
- Clase **OperationRepository** hereda BaseRepository[Operation]:
  - Método `get_by_portfolio(portfolio_id: UUID, filters: dict = None) -> List[Operation]`: lista con filtros opcionales
  - Método `get_by_asset(asset_symbol: str, user_id: UUID = None) -> List[Operation]`: operaciones por activo
  - Método `filter_by_date_range(portfolio_id: UUID, start: datetime, end: datetime) -> List[Operation]`: rango fechas
  - Método `filter_by_type(portfolio_id: UUID, operation_type: OperationType) -> List[Operation]`: por tipo
  - Método `get_portfolio_statistics(portfolio_id: UUID) -> dict`: calcula total_invested, total_sold, net_investment, operation_count
  - Método `bulk_create(operations: List[dict]) -> List[Operation]`: inserción masiva para CSV import
  - Método `get_latest_operations(portfolio_id: UUID, limit: int = 10) -> List[Operation]`: últimas N operaciones
  - Aplicar ordenamiento por date DESC por defecto

**Test de Integración:**
- Test: get_by_portfolio retorna solo operaciones del portfolio
- Test: filter_by_date_range respeta límites inclusivos
- Test: filter_by_type filtra correctamente BUY vs SELL
- Test: get_portfolio_statistics calcula totales correctamente
- Test: get_portfolio_statistics diferencia BUY (invested) y SELL (sold)
- Test: bulk_create inserta 100+ operaciones eficientemente
- Test: bulk_create maneja errores parciales
- Test: get_latest_operations retorna ordenadas por fecha DESC
- Test: combinación de filtros funciona (date + type)

**Resultado Esperado:**
- Clase OperationRepository con 7 métodos
- Filtrado avanzado multi-criterio
- Estadísticas financieras precisas
- Bulk insert eficiente para imports
- Ordenamiento por fecha por defecto
- Queries optimizadas con índices

**Estado:** Pendiente

---

### Bloque 4.5: AssetRepository

**Archivos:** `backend/app/repositories/asset.py`

**Objetivo:**
Implementar repositorio para catálogo de activos y gestión de precios históricos con operaciones bulk.

**Tareas de Implementación:**
- Clase **AssetRepository** hereda BaseRepository[Asset]:
  - Método `get_by_symbol(symbol: str) -> Optional[Asset]`: busca por símbolo (case-insensitive)
  - Método `search_assets(query: str, limit: int = 20) -> List[Asset]`: búsqueda fuzzy en name y symbol
  - Método `get_or_create(symbol: str, data: dict = None) -> Asset`: obtiene o crea si no existe
  - Método `get_historical_prices(symbol: str, days: int = 90) -> List[AssetPrice]`: precios históricos
  - Método `get_latest_price(symbol: str) -> Optional[AssetPrice]`: precio más reciente
  - Método `bulk_insert_prices(prices: List[dict]) -> List[AssetPrice]`: inserción masiva de precios
  - Método `delete_old_prices(days: int = 365) -> int`: limpieza de precios antiguos
  - Método `get_price_range(symbol: str, start: datetime, end: datetime) -> List[AssetPrice]`: rango específico
  - Usar upsert (ON CONFLICT) para bulk_insert_prices

**Test de Integración:**
- Test: get_by_symbol encuentra asset (case-insensitive)
- Test: search_assets encuentra por nombre parcial
- Test: get_or_create retorna existente si ya creado
- Test: get_or_create crea nuevo si no existe
- Test: get_historical_prices retorna últimos N días
- Test: get_latest_price retorna precio más reciente por timestamp
- Test: bulk_insert_prices inserta 1000+ registros eficientemente
- Test: bulk_insert_prices maneja duplicados (upsert)
- Test: delete_old_prices elimina solo registros antiguos
- Test: constraint unique (asset_symbol, timestamp) respetado

**Resultado Esperado:**
- Clase AssetRepository con 8 métodos
- Búsqueda fuzzy funcional
- Get-or-create pattern implementado
- Bulk upsert eficiente con ON CONFLICT
- Queries temporales optimizadas
- Limpieza automática de datos antiguos

**Estado:** Pendiente

---

### Bloque 4.6: AnalysisRepository

**Archivos:** `backend/app/repositories/analysis.py`

**Objetivo:**
Implementar repositorio para gestión de análisis con IA incluyendo sistema de caché y tracking de requests.

**Tareas de Implementación:**
- Clase **AnalysisRepository** hereda BaseRepository[Analysis]:
  - Método `get_by_portfolio(portfolio_id: UUID) -> List[Analysis]`: análisis de cartera
  - Método `get_by_asset(asset_symbol: str) -> List[Analysis]`: análisis de activo
  - Método `get_cached_analysis(portfolio_id: UUID = None, asset_symbol: str = None) -> Optional[Analysis]`: busca caché válido (expires_at > now, cached=True)
  - Método `invalidate_cache(portfolio_id: UUID) -> int`: marca cached=False para portfolio
  - Método `cleanup_expired() -> int`: elimina análisis con expires_at < now()
  - Método `create_request(user_id: UUID, data: dict) -> AnalysisRequest`: crea request con status PENDING
  - Método `update_request_status(request_id: UUID, status: AnalysisStatus, error: str = None) -> AnalysisRequest`: actualiza status y completed_at
  - Método `get_user_requests(user_id: UUID, limit: int = 20) -> List[AnalysisRequest]`: historial usuario

**Test de Integración:**
- Test: get_cached_analysis retorna solo análisis no expirados
- Test: get_cached_analysis retorna None si expires_at < now()
- Test: invalidate_cache marca cached=False
- Test: cleanup_expired elimina solo registros expirados
- Test: create_request crea con status PENDING
- Test: update_request_status actualiza a COMPLETED y setea completed_at
- Test: update_request_status puede setear error_message en FAILED
- Test: get_user_requests retorna ordenado por created_at DESC
- Test: índice (portfolio_id, asset_symbol, cached) optimiza búsqueda

**Resultado Esperado:**
- Clase AnalysisRepository con 8 métodos
- Sistema de caché temporal funcional
- Invalidación selectiva de caché
- Limpieza automática de expirados
- Tracking completo de requests
- Estados de análisis bien gestionados

**Estado:** Pendiente

---

## FASE 5: Integraciones Externas

### Bloque 5.1: Cliente Alpha Vantage API

**Archivos:** `backend/app/clients/alpha_vantage.py`

**Objetivo:**
Implementar cliente HTTP para integración con Alpha Vantage API para obtención de datos de mercado (cotizaciones, históricos).

**Tareas de Implementación:**
- Clase **AlphaVantageClient**:
  - Método `get_quote(symbol: str) -> dict`: obtiene cotización actual (función GLOBAL_QUOTE)
  - Método `get_daily_prices(symbol: str, outputsize: str = "compact") -> dict`: datos históricos diarios (TIME_SERIES_DAILY)
  - Método `search_symbol(keywords: str) -> List[dict]`: búsqueda de símbolos (SYMBOL_SEARCH)
  - Configurar httpx.AsyncClient con timeout 30s, retry 3 intentos
  - Manejar rate limiting (5 requests/min en free tier)
  - Parsear respuestas JSON, extraer campos relevantes
  - Logging de requests/responses para debugging

**Test de Integración:**
- Test: get_quote retorna price, volume, timestamp para símbolo válido (AAPL)
- Test: get_quote lanza exception con símbolo inválido
- Test: get_daily_prices retorna lista de precios con OHLCV
- Test: search_symbol encuentra resultados para "Apple"
- Test: rate limiting se respeta (max 5 requests en 60s)
- Test: retry funciona ante timeout temporal
- Test: manejo de API key inválida (401)

**Resultado Esperado:**
- Cliente funcional con 3 métodos principales
- Rate limiting implementado con contador/timer
- Retry automático en errores temporales (500, timeout)
- Parsing correcto de respuestas Alpha Vantage
- Manejo de errores HTTP (401, 404, 500)
- Logging estructurado de llamadas API

**Estado:** Pendiente

---

### Bloque 5.2: Cliente OpenAI API

**Archivos:** `backend/app/clients/openai_client.py`

**Objetivo:**
Implementar wrapper para OpenAI API para generación de análisis de mercado en lenguaje natural.

**Tareas de Implementación:**
- Clase **OpenAIClient**:
  - Método `generate_analysis(prompt: str, model: str = "gpt-4") -> str`: genera análisis con chat completion
  - Método `validate_response(response: str) -> bool`: valida que respuesta es coherente (>100 chars, no errores API)
  - Configurar openai SDK con api_key desde settings
  - Parámetros: temperature=0.7, max_tokens=1500, top_p=1
  - Implementar retry con exponential backoff (3 intentos)
  - Manejar rate limits y errores API (429, 500)
  - Logging de tokens consumidos para tracking de costos

**Test de Integración:**
- Test: generate_analysis retorna texto coherente (>100 chars)
- Test: generate_analysis con prompt válido sobre mercado
- Test: retry funciona ante error 429 (rate limit)
- Test: manejo de API key inválida (401)
- Test: validate_response rechaza respuestas cortas o vacías
- Test: tracking de tokens consumidos en logs
- Test: timeout configurado a 60s funciona

**Resultado Esperado:**
- Cliente funcional con SDK oficial OpenAI
- Retry con exponential backoff (1s, 2s, 4s)
- Rate limiting manejado correctamente
- Validación de respuestas generadas
- Logging de consumo de tokens
- Timeout de 60s por request

**Estado:** Pendiente

---

### Bloque 5.3: Cliente Redis Cache

**Archivos:** `backend/app/clients/redis_client.py`

**Objetivo:**
Implementar wrapper para Redis como sistema de caché para precios de mercado y análisis.

**Tareas de Implementación:**
- Clase **RedisClient**:
  - Método `get(key: str) -> Optional[str]`: obtiene valor de caché
  - Método `set(key: str, value: str, ttl: int) -> bool`: almacena con TTL
  - Método `delete(key: str) -> bool`: elimina clave
  - Método `exists(key: str) -> bool`: verifica existencia
  - Método `get_json(key: str) -> Optional[dict]`: deserializa JSON automáticamente
  - Método `set_json(key: str, value: dict, ttl: int) -> bool`: serializa a JSON
  - Configurar redis.Redis con connection pool
  - Prefijos de claves: "price:{symbol}", "analysis:{portfolio_id}", "user:{user_id}"
  - Manejar conexiones fallidas gracefully

**Test de Integración:**
- Test: set y get funcionan con strings
- Test: set_json y get_json serializan/deserializan correctamente
- Test: TTL expira correctamente (test con ttl=1s)
- Test: delete elimina clave existente
- Test: exists retorna True/False apropiadamente
- Test: conexión fallida no rompe aplicación
- Test: prefijos de claves se aplican correctamente

**Resultado Esperado:**
- Cliente funcional con connection pool (size=10)
- Métodos de serialización JSON automáticos
- TTL configurable por operación
- Prefijos de claves organizados por dominio
- Manejo graceful de Redis no disponible
- Connection pool optimiza reuso de conexiones

**Estado:** Pendiente

---

### Bloque 5.4: Test Integral de Clientes Externos

**Archivos:** `backend/tests/integration/clients/test_external_clients.py`

**Objetivo:**
Validar comportamiento de clientes externos con APIs reales y mocks para casos edge.

**Tareas de Test:**
- Test: flujo completo Alpha Vantage - buscar símbolo → obtener quote → obtener históricos
- Test: flujo completo OpenAI - generar análisis técnico de portfolio
- Test: flujo completo Redis - cache miss → fetch API → cache hit
- Test: rate limiting Alpha Vantage respetado en requests concurrentes
- Test: retry OpenAI funciona con mock de errores 429
- Test: cache invalidation Redis funciona correctamente
- Test: manejo de timeouts en todos los clientes
- Test: manejo de API keys inválidas

**Resultado Esperado:**
- Suite de tests de integración con APIs reales
- 30+ assertions ejecutándose exitosamente
- Mocks para casos edge (rate limit, timeout, errores HTTP)
- Validación de retry logic en todos los clientes
- Cache hit/miss rate verificable
- No errores en conexiones concurrentes

**Estado:** Pendiente

---

## FASE 6: Capa de Servicios (Business Logic)

### Bloque 6.1: AuthService

**Archivos:** `backend/app/services/auth_service.py`

**Objetivo:**
Implementar lógica de negocio para autenticación, registro, verificación de email y gestión de sesiones.

**Tareas de Implementación:**
- Clase **AuthService**:
  - Dependencias: UserRepository, PasswordHasher, JWTHandler, EmailService (futuro)
  - Método `register_user(email: str, password: str, full_name: str) -> User`: valida email único, hashea password, crea user + profile, genera token verificación
  - Método `authenticate_user(email: str, password: str) -> dict`: valida credenciales, actualiza last_login, genera access + refresh tokens, crea session
  - Método `verify_email(token: str) -> bool`: valida token, marca is_verified=True
  - Método `refresh_access_token(refresh_token: str) -> dict`: valida refresh token activo, genera nuevo access token
  - Método `logout(user_id: UUID, refresh_token: str) -> bool`: desactiva session
  - Método `forgot_password(email: str) -> bool`: genera reset token, guarda con expiración
  - Método `reset_password(token: str, new_password: str) -> bool`: valida token no expirado, actualiza password
  - Validaciones: email formato válido, password strength mínima, tokens no expirados

**Test Unitario:**
- Test: register_user crea User + UserProfile en transacción
- Test: register_user rechaza email duplicado
- Test: authenticate_user retorna tokens con credenciales válidas
- Test: authenticate_user rechaza password incorrecta
- Test: authenticate_user rechaza usuario no verificado
- Test: verify_email marca is_verified=True
- Test: verify_email rechaza token inválido
- Test: refresh_access_token genera nuevo token
- Test: logout desactiva session
- Test: reset_password valida expiración de token

**Resultado Esperado:**
- Clase AuthService con 7 métodos de negocio
- Validaciones completas de seguridad
- Transacciones atómicas (register crea user + profile)
- Gestión completa de ciclo de vida de tokens
- Actualización de last_login en authenticate
- Rate limiting considerado (futuro)

**Estado:** Pendiente

---

### Bloque 6.2: PortfolioService

**Archivos:** `backend/app/services/portfolio_service.py`

**Objetivo:**
Implementar lógica de negocio para gestión de carteras, cálculo de métricas y validación de ownership.

**Tareas de Implementación:**
- Clase **PortfolioService**:
  - Dependencias: PortfolioRepository, OperationRepository, MarketDataService
  - Método `create_portfolio(user_id: UUID, data: PortfolioCreate) -> Portfolio`: valida nombre único por usuario, crea portfolio con métricas inicializadas
  - Método `get_portfolio(user_id: UUID, portfolio_id: UUID) -> Portfolio`: valida ownership, retorna con posiciones eager loaded
  - Método `get_portfolio_details(portfolio_id: UUID, user_id: UUID) -> dict`: obtiene portfolio + positions + recent operations + métricas actualizadas
  - Método `update_portfolio(user_id: UUID, portfolio_id: UUID, data: PortfolioUpdate) -> Portfolio`: valida ownership, actualiza campos
  - Método `delete_portfolio(user_id: UUID, portfolio_id: UUID) -> bool`: valida ownership, elimina portfolio (cascade assets + operations)
  - Método `calculate_and_update_metrics(portfolio_id: UUID) -> Portfolio`: obtiene precios actuales, recalcula métricas, persiste
  - Método `get_user_portfolios(user_id: UUID) -> List[Portfolio]`: lista portfolios del usuario
  - Validaciones: ownership en todas las operaciones, nombre único por usuario

**Test Unitario:**
- Test: create_portfolio crea con métricas en 0
- Test: create_portfolio rechaza nombre duplicado para mismo usuario
- Test: get_portfolio valida ownership (rechaza portfolio de otro usuario)
- Test: get_portfolio_details incluye positions y operations
- Test: update_portfolio valida ownership
- Test: delete_portfolio valida ownership
- Test: calculate_and_update_metrics actualiza total_value correctamente
- Test: get_user_portfolios retorna solo portfolios del usuario

**Resultado Esperado:**
- Clase PortfolioService con 7 métodos
- Validación de ownership en todos los métodos
- Cálculo de métricas integra precios actuales de MarketDataService
- Eager loading de relaciones para optimización
- Transacciones atómicas en operaciones complejas
- Constraint de nombre único por usuario respetado

**Estado:** Pendiente

---

### Bloque 6.3: OperationService

**Archivos:** `backend/app/services/operation_service.py`

**Objetivo:**
Implementar lógica de negocio para operaciones de compra/venta con actualización automática de posiciones.

**Tareas de Implementación:**
- Clase **OperationService**:
  - Dependencias: OperationRepository, PortfolioRepository, MarketDataService
  - Método `create_buy_operation(user_id: UUID, data: OperationCreate) -> Operation`: valida ownership portfolio, calcula total_amount, crea operation, actualiza/crea position, recalcula metrics portfolio
  - Método `create_sell_operation(user_id: UUID, data: OperationCreate) -> Operation`: valida ownership, valida cantidad disponible, calcula total_amount, crea operation, actualiza position, recalcula metrics
  - Método `get_operations(user_id: UUID, filters: OperationFilter) -> List[Operation]`: aplica filtros, valida ownership de portfolios
  - Método `update_operation(user_id: UUID, operation_id: UUID, data: OperationUpdate) -> Operation`: valida ownership, actualiza, recalcula metrics
  - Método `delete_operation(user_id: UUID, operation_id: UUID) -> bool`: valida ownership, revierte cambios en position, recalcula metrics
  - Método `import_operations_csv(user_id: UUID, portfolio_id: UUID, file: UploadFile) -> dict`: parsea CSV, valida datos, bulk create operations, actualiza positions
  - Método `export_operations_csv(user_id: UUID, filters: OperationFilter) -> File`: genera CSV con operaciones filtradas
  - Validaciones: cantidad disponible en SELL, ownership portfolio, total_amount calculado correctamente

**Test Unitario:**
- Test: create_buy_operation crea operation y actualiza position
- Test: create_buy_operation crea nueva position si no existe
- Test: create_sell_operation valida cantidad disponible
- Test: create_sell_operation rechaza venta sin posición existente
- Test: update_operation recalcula metrics portfolio
- Test: delete_operation revierte cambios en position
- Test: import_operations_csv procesa 100 operaciones
- Test: export_operations_csv genera formato válido
- Test: validación de ownership en todos los métodos

**Resultado Esperado:**
- Clase OperationService con 7 métodos
- Lógica diferenciada BUY vs SELL
- Actualización automática de PortfolioAsset en cada operación
- Recálculo de métricas portfolio tras operaciones
- Validación de cantidad disponible en SELL
- Import/export CSV funcional
- Transacciones atómicas (operation + position + metrics)

**Estado:** Pendiente

---

### Bloque 6.4: MarketDataService

**Archivos:** `backend/app/services/market_data_service.py`

**Objetivo:**
Implementar lógica para obtención de datos de mercado con caché multinivel y sincronización.

**Tareas de Implementación:**
- Clase **MarketDataService**:
  - Dependencias: AssetRepository, AlphaVantageClient, RedisClient
  - Método `get_current_price(symbol: str, currency: str = "USD") -> Decimal`: verifica caché Redis (TTL 5min), si miss → Alpha Vantage → guarda en caché + BD
  - Método `get_historical_prices(symbol: str, days: int = 90) -> List[AssetPrice]`: verifica BD, si incompleto → Alpha Vantage → bulk insert BD
  - Método `get_asset_info(symbol: str) -> Asset`: verifica BD, si no existe → Alpha Vantage search → create Asset
  - Método `sync_market_data(symbol: str) -> Asset`: fuerza refresh desde Alpha Vantage, actualiza caché + BD
  - Método `refresh_price_cache(symbol: str) -> AssetPrice`: invalida caché, obtiene nuevo precio, guarda
  - Método `search_assets(query: str) -> List[Asset]`: busca en BD local, si no hay resultados → Alpha Vantage
  - Lógica de caché: Redis (5min) → BD (históricos) → Alpha Vantage (source of truth)

**Test Unitario:**
- Test: get_current_price retorna desde caché si disponible (cache hit)
- Test: get_current_price consulta Alpha Vantage en cache miss
- Test: get_current_price guarda en caché con TTL correcto
- Test: get_historical_prices retorna desde BD si completo
- Test: get_historical_prices consulta Alpha Vantage si faltan datos
- Test: sync_market_data invalida caché y actualiza
- Test: search_assets busca local antes que API
- Test: manejo de rate limit Alpha Vantage

**Resultado Esperado:**
- Clase MarketDataService con 6 métodos
- Caché multinivel (Redis → BD → API) funcional
- TTL de 5min para precios actuales
- Bulk insert eficiente para históricos
- Rate limiting manejado con cache
- Fallback a BD si Alpha Vantage falla
- Get-or-create pattern para Assets

**Estado:** Pendiente

---

### Bloque 6.5: AIService

**Archivos:** `backend/app/services/ai_service.py`

**Objetivo:**
Implementar lógica para generación de análisis con IA incluyendo procesamiento de indicadores técnicos y caché.

**Tareas de Implementación:**
- Clase **AIService**:
  - Dependencias: AnalysisRepository, MarketDataService, OpenAIClient, DataProcessor (módulo IA)
  - Método `generate_portfolio_analysis(portfolio_id: UUID, user_id: UUID) -> Analysis`: valida ownership, verifica caché (1h), si miss → obtiene positions → procesa datos históricos → genera prompt → OpenAI → guarda con TTL
  - Método `generate_asset_analysis(asset_symbol: str, user_id: UUID) -> Analysis`: verifica caché, obtiene históricos (90 días) → calcula indicadores técnicos → genera prompt → OpenAI → guarda
  - Método `get_cached_analysis(portfolio_id: UUID = None, asset_symbol: str = None) -> Optional[Analysis]`: busca análisis válido (no expirado)
  - Método `invalidate_portfolio_cache(portfolio_id: UUID) -> int`: invalida tras operaciones nuevas
  - Método `process_market_data(historical_prices: List[AssetPrice]) -> dict`: calcula RSI, MACD, SMA, volatility usando procesador
  - Método `build_analysis_prompt(data: dict, type: AnalysisType) -> str`: construye prompt estructurado con datos técnicos
  - Caché: TTL 1 hora, invalidación automática tras operaciones

**Test Unitario:**
- Test: generate_portfolio_analysis retorna desde caché si válido
- Test: generate_portfolio_analysis genera nuevo si expirado
- Test: generate_asset_analysis calcula indicadores correctamente
- Test: get_cached_analysis retorna None si expirado
- Test: invalidate_portfolio_cache marca cached=False
- Test: process_market_data calcula RSI, MACD, SMA
- Test: build_analysis_prompt incluye todos los indicadores
- Test: disclaimer incluido en todos los análisis
- Test: validación de ownership en portfolio analysis

**Resultado Esperado:**
- Clase AIService con 6 métodos
- Caché de análisis con TTL 1 hora
- Invalidación automática tras operaciones
- Integración con DataProcessor del módulo IA
- Prompts estructurados con datos técnicos
- Disclaimer legal automático
- Tracking de requests con AnalysisRequest

**Estado:** Pendiente

---

### Bloque 6.6: UserService

**Archivos:** `backend/app/services/user_service.py`

**Objetivo:**
Implementar lógica para gestión de perfiles de usuario y actividad.

**Tareas de Implementación:**
- Clase **UserService**:
  - Dependencias: UserRepository, PasswordHasher
  - Método `get_user_profile(user_id: UUID) -> UserProfile`: obtiene con eager loading de user
  - Método `update_user_profile(user_id: UUID, data: UserUpdate) -> UserProfile`: actualiza campos, valida currency/timezone
  - Método `change_password(user_id: UUID, current_password: str, new_password: str) -> bool`: verifica password actual, valida nueva, actualiza hash
  - Método `delete_user_account(user_id: UUID) -> bool`: elimina user (cascade profile, sessions, portfolios)
  - Método `get_user_activity(user_id: UUID, limit: int = 50) -> List[dict]`: compila operaciones, análisis solicitados, logins
  - Validaciones: password actual correcta, currency ISO válida, timezone válido

**Test Unitario:**
- Test: get_user_profile retorna profile completo
- Test: update_user_profile actualiza campos correctamente
- Test: update_user_profile valida currency ISO (3 chars)
- Test: change_password verifica password actual
- Test: change_password valida strength nueva password
- Test: delete_user_account elimina todo en cascade
- Test: get_user_activity retorna ordenado por fecha
- Test: get_user_activity incluye operaciones + análisis

**Resultado Esperado:**
- Clase UserService con 5 métodos
- Validaciones de currency y timezone
- Cambio de password seguro con verificación
- Cascade delete completo al eliminar cuenta
- Activity log compilado de múltiples fuentes
- Eager loading para optimización

**Estado:** Pendiente

---

## FASE 7: Middleware y Dependencias

### Bloque 7.1: Authentication Middleware

**Archivos:** `backend/app/middleware/auth_middleware.py`

**Objetivo:**
Implementar middleware para validación automática de tokens JWT en requests protegidos.

**Tareas de Implementación:**
- Función **get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User**:
  - Extrae token de header Authorization
  - Decodifica JWT y obtiene user_id del payload
  - Busca User en BD por ID
  - Valida user is_active y is_verified
  - Retorna User para uso en endpoints
  - Lanza HTTPException(401) si token inválido/expirado
  - Lanza HTTPException(403) si user inactivo/no verificado
- Configurar oauth2_scheme con tokenUrl="/api/v1/auth/login"
- Dependency reutilizable en todos los endpoints protegidos

**Test Unitario:**
- Test: get_current_user retorna User con token válido
- Test: get_current_user lanza 401 con token expirado
- Test: get_current_user lanza 401 con token malformado
- Test: get_current_user lanza 403 con user inactivo
- Test: get_current_user lanza 403 con user no verificado
- Test: extracción correcta de token de header

**Resultado Esperado:**
- Dependency funcional para protección de endpoints
- Validación automática de JWT
- Verificación de user activo y verificado
- Errores HTTP apropiados (401 vs 403)
- Reutilizable con Depends() en rutas

**Estado:** Pendiente

---

### Bloque 7.2: Error Handling Middleware

**Archivos:** `backend/app/middleware/error_handler.py`

**Objetivo:**
Implementar middleware para manejo centralizado de excepciones con respuestas estandarizadas.

**Tareas de Implementación:**
- Clase **ErrorHandlerMiddleware**:
  - Captura todas las excepciones no manejadas
  - Transforma a respuestas JSON estandarizadas: {error: str, detail: str, status_code: int}
  - Mapea excepciones comunes:
    - SQLAlchemyError → 500 Internal Server Error
    - IntegrityError → 409 Conflict
    - HTTPException → mantiene status original
    - ValidationError → 422 Unprocessable Entity
  - Logging estructurado de errores con traceback
  - No exponer detalles sensibles en producción

**Test Unitario:**
- Test: IntegrityError se convierte en 409 Conflict
- Test: ValidationError se convierte en 422
- Test: HTTPException mantiene status code original
- Test: SQLAlchemyError se convierte en 500
- Test: respuesta JSON contiene error y detail
- Test: traceback logueado pero no expuesto en response

**Resultado Esperado:**
- Middleware registrado en app FastAPI
- Respuestas de error estandarizadas
- Logging de errores con contexto
- Sin exposición de detalles sensibles
- Status codes HTTP apropiados

**Estado:** Pendiente

---

### Bloque 7.3: CORS Middleware

**Archivos:** `backend/app/middleware/cors.py`

**Objetivo:**
Configurar CORS para permitir requests desde frontend con orígenes configurables.

**Tareas de Implementación:**
- Configurar CORSMiddleware de FastAPI:
  - allow_origins desde settings.CORS_ORIGINS
  - allow_credentials=True
  - allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
  - allow_headers=["*"]
  - max_age=3600 (1 hora de cache preflight)
- Validar orígenes contra lista permitida
- Logging de requests CORS bloqueados

**Test Unitario:**
- Test: request desde origen permitido funciona
- Test: request desde origen no permitido bloqueado
- Test: preflight OPTIONS manejado correctamente
- Test: headers permitidos incluidos en response
- Test: credentials permitidas en response

**Resultado Esperado:**
- CORS configurado con orígenes dinámicos
- Preflight requests manejados
- Credentials permitidas
- Configuración desde settings
- Logging de requests bloqueados

**Estado:** Pendiente

---

### Bloque 7.4: Rate Limiting Middleware (Futuro)

**Archivos:** `backend/app/middleware/rate_limiter.py`

**Objetivo:**
Implementar rate limiting básico para prevenir abuso de API.

**Tareas de Implementación:**
- Clase **RateLimitMiddleware**:
  - Tracking de requests por IP usando Redis
  - Límites configurables: 100 requests/min por IP
  - Sliding window algorithm
  - Retorna 429 Too Many Requests si excedido
  - Headers de rate limit en responses: X-RateLimit-Limit, X-RateLimit-Remaining
  - Whitelist de IPs exentas (servidor interno)

**Test Unitario:**
- Test: requests dentro del límite funcionan
- Test: request 101 en 1 min retorna 429
- Test: sliding window resetea correctamente
- Test: headers X-RateLimit presentes
- Test: whitelist IPs bypass rate limit
- Test: tracking por IP funciona

**Resultado Esperado:**
- Rate limiting funcional con Redis
- Sliding window de 1 minuto
- Headers informativos en responses
- Whitelist configurable
- 429 retornado cuando excedido

**Estado:** Pendiente

---

## FASE 8: Capa de API (Endpoints REST)

### Bloque 8.1: Auth Endpoints

**Archivos:** `backend/app/api/v1/auth/router.py`

**Objetivo:**
Implementar endpoints REST para autenticación, registro y gestión de sesiones.

**Tareas de Implementación:**
- Router `/api/v1/auth` con 7 endpoints:
  - POST `/register`: recibe UserRegister, retorna 201 con UserResponse
  - POST `/login`: recibe UserLogin (form data OAuth2), retorna TokenResponse
  - POST `/refresh`: recibe RefreshTokenRequest, retorna TokenResponse
  - POST `/logout`: recibe refresh_token, requiere auth, retorna 204
  - POST `/verify-email`: recibe token query param, retorna 200
  - POST `/forgot-password`: recibe ForgotPassword, retorna 200
  - POST `/reset-password`: recibe PasswordReset, retorna 200
- Documentación OpenAPI con ejemplos
- Manejo de errores: 400, 401, 409, 422

**Test de Integración:**
- Test: POST /register crea usuario y retorna 201
- Test: POST /register rechaza email duplicado (409)
- Test: POST /login retorna tokens con credenciales válidas
- Test: POST /login rechaza password incorrecta (401)
- Test: POST /refresh genera nuevo access token
- Test: POST /logout desactiva sesión
- Test: POST /verify-email marca usuario como verificado
- Test: POST /reset-password actualiza password

**Resultado Esperado:**
- 7 endpoints funcionales
- Validación de schemas automática
- Documentación Swagger generada
- Status codes HTTP apropiados
- Manejo de errores centralizado

**Estado:** Pendiente

---

### Bloque 8.2: Users Endpoints

**Archivos:** `backend/app/api/v1/users/router.py`

**Objetivo:**
Implementar endpoints para gestión de perfil de usuario.

**Tareas de Implementación:**
- Router `/api/v1/users` con 5 endpoints protegidos:
  - GET `/me`: retorna UserProfileResponse del usuario autenticado
  - PUT `/me`: recibe UserUpdate, actualiza perfil, retorna UserProfileResponse
  - PUT `/me/password`: recibe PasswordChange, retorna 204
  - DELETE `/me`: elimina cuenta, retorna 204
  - GET `/me/activity`: retorna List[ActivityResponse]
- Todos requieren autenticación (Depends(get_current_user))
- Documentación con ejemplos

**Test de Integración:**
- Test: GET /me retorna perfil completo
- Test: GET /me sin auth retorna 401
- Test: PUT /me actualiza campos correctamente
- Test: PUT /me/password cambia password
- Test: PUT /me/password rechaza password actual incorrecta
- Test: DELETE /me elimina usuario completamente
- Test: GET /me/activity retorna operaciones recientes

**Resultado Esperado:**
- 5 endpoints protegidos funcionales
- Validación de ownership automática
- Actualización de perfil funcional
- Cambio de password seguro
- Delete cascade completo

**Estado:** Pendiente

---

### Bloque 8.3: Portfolios Endpoints

**Archivos:** `backend/app/api/v1/portfolios/router.py`

**Objetivo:**
Implementar endpoints CRUD para gestión de carteras con métricas y análisis.

**Tareas de Implementación:**
- Router `/api/v1/portfolios` con 8 endpoints protegidos:
  - GET `/`: lista portfolios del usuario, retorna List[PortfolioResponse]
  - POST `/`: recibe PortfolioCreate, retorna 201 con PortfolioResponse
  - GET `/{portfolio_id}`: retorna PortfolioDetailResponse con positions
  - PUT `/{portfolio_id}`: recibe PortfolioUpdate, retorna PortfolioResponse
  - DELETE `/{portfolio_id}`: elimina portfolio, retorna 204
  - GET `/{portfolio_id}/positions`: retorna List[PortfolioAssetResponse]
  - GET `/{portfolio_id}/operations`: retorna List[OperationResponse], paginado
  - GET `/{portfolio_id}/analytics`: retorna AnalysisResponse (análisis IA)
- Validación de ownership en todos los endpoints
- Query params: limit, offset para paginación

**Test de Integración:**
- Test: GET / retorna solo portfolios del usuario
- Test: POST / crea portfolio correctamente
- Test: GET /{id} valida ownership (403 si no es del usuario)
- Test: PUT /{id} actualiza portfolio
- Test: DELETE /{id} elimina con cascade
- Test: GET /{id}/positions retorna posiciones actualizadas
- Test: GET /{id}/operations retorna paginado
- Test: GET /{id}/analytics genera análisis con IA

**Resultado Esperado:**
- 8 endpoints CRUD completos
- Validación de ownership estricta
- Paginación funcional
- Análisis IA integrado
- Eager loading en detalle de portfolio

**Estado:** Pendiente

---

### Bloque 8.4: Operations Endpoints

**Archivos:** `backend/app/api/v1/operations/router.py`

**Objetivo:**
Implementar endpoints para registro y gestión de operaciones financieras.

**Tareas de Implementación:**
- Router `/api/v1/operations` con 7 endpoints protegidos:
  - GET `/`: lista operaciones con filtros, retorna List[OperationResponse], paginado
  - POST `/`: recibe OperationCreate, retorna 201 con OperationResponse
  - GET `/{operation_id}`: retorna OperationResponse
  - PUT `/{operation_id}`: recibe OperationUpdate, retorna OperationResponse
  - DELETE `/{operation_id}`: elimina, retorna 204
  - POST `/import`: recibe file CSV, retorna {imported: int, errors: List}
  - GET `/export`: retorna CSV file con operaciones filtradas
- Query params para filtros: portfolio_id, asset_symbol, operation_type, date_from, date_to
- Validación de cantidad disponible en SELL

**Test de Integración:**
- Test: GET / retorna con filtros aplicados
- Test: POST / BUY crea operación y actualiza position
- Test: POST / SELL valida cantidad disponible
- Test: PUT /{id} actualiza y recalcula metrics
- Test: DELETE /{id} revierte cambios en position
- Test: POST /import procesa CSV válido
- Test: GET /export genera CSV descargable
- Test: validación ownership en todas las operaciones

**Resultado Esperado:**
- 7 endpoints funcionales
- Filtrado avanzado multi-criterio
- Import/export CSV funcional
- Validación de cantidad en SELL
- Actualización automática de posiciones
- Recálculo de metrics tras operaciones

**Estado:** Pendiente

---

### Bloque 8.5: Market Endpoints

**Archivos:** `backend/app/api/v1/market/router.py`

**Objetivo:**
Implementar endpoints para consulta de datos de mercado con caché integrado.

**Tareas de Implementación:**
- Router `/api/v1/market` con 4 endpoints:
  - GET `/quote/{symbol}`: retorna CurrentPriceResponse
  - GET `/historical/{symbol}`: retorna HistoricalPriceResponse, query param days (default 90)
  - GET `/assets/search`: query param q, retorna AssetSearchResponse
  - GET `/assets/{symbol}`: retorna AssetInfo
- Integración con caché Redis
- Rate limiting considerado (futuro)
- Sin autenticación requerida (público)

**Test de Integración:**
- Test: GET /quote/{symbol} retorna precio actual
- Test: GET /quote/{symbol} usa caché en segundo request
- Test: GET /historical/{symbol} retorna últimos N días
- Test: GET /assets/search encuentra símbolos
- Test: GET /assets/{symbol} retorna info completa
- Test: manejo de símbolo inválido (404)

**Resultado Esperado:**
- 4 endpoints públicos funcionales
- Caché Redis integrado (cache hit rate alto)
- Integración con Alpha Vantage transparente
- Respuestas rápidas (<500ms con cache)
- Manejo de símbolos inválidos

**Estado:** Pendiente

---

### Bloque 8.6: Main Application Setup

**Archivos:** `backend/main.py`

**Objetivo:**
Configurar aplicación FastAPI principal con routers, middleware y lifecycle events.

**Tareas de Implementación:**
- Crear instancia FastAPI con metadata (title, version, description)
- Registrar routers:
  - app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
  - app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
  - app.include_router(portfolios_router, prefix="/api/v1/portfolios", tags=["portfolios"])
  - app.include_router(operations_router, prefix="/api/v1/operations", tags=["operations"])
  - app.include_router(market_router, prefix="/api/v1/market", tags=["market"])
- Registrar middleware: CORS, ErrorHandler
- Configurar lifecycle: startup (crear tablas BD), shutdown (cerrar conexiones)
- Health check endpoint: GET /health retorna {status: "ok"}

**Test de Integración:**
- Test: GET /health retorna 200
- Test: GET /docs retorna Swagger UI
- Test: GET /openapi.json retorna spec completa
- Test: CORS funciona desde origen permitido
- Test: error handling retorna JSON estandarizado
- Test: startup crea conexiones necesarias

**Resultado Esperado:**
- Aplicación FastAPI completa
- 5 routers registrados con prefijos
- Swagger UI funcional en /docs
- CORS configurado
- Error handling centralizado
- Health check endpoint

**Estado:** Pendiente

---

## FASE 9: Módulo de Análisis con IA

### Bloque 9.1: Data Processor - Indicadores Técnicos

**Archivos:** `ai_module/src/processors/technical_indicators.py`

**Objetivo:**
Implementar cálculo de indicadores técnicos para análisis de mercado.

**Tareas de Implementación:**
- Clase **TechnicalIndicatorProcessor**:
  - Método `calculate_rsi(prices: List[float], period: int = 14) -> float`: calcula RSI
  - Método `calculate_macd(prices: List[float]) -> dict`: retorna {macd, signal, histogram}
  - Método `calculate_sma(prices: List[float], period: int) -> float`: media móvil simple
  - Método `calculate_ema(prices: List[float], period: int) -> float`: media móvil exponencial
  - Método `calculate_volatility(prices: List[float]) -> float`: desviación estándar
  - Método `identify_trend(prices: List[float]) -> str`: retorna "bullish", "bearish", "neutral"
  - Usar Pandas y NumPy para cálculos
  - Validar longitud mínima de datos (50 puntos)

**Test Unitario:**
- Test: calculate_rsi con datos reales retorna valor entre 0-100
- Test: calculate_macd retorna dict con 3 valores
- Test: calculate_sma con período 20 calcula correctamente
- Test: calculate_ema da más peso a valores recientes
- Test: calculate_volatility retorna desviación estándar
- Test: identify_trend detecta bullish/bearish correctamente
- Test: validación de longitud mínima de datos

**Resultado Esperado:**
- Clase con 6 métodos de cálculo
- Indicadores precisos usando fórmulas estándar
- Validación de datos de entrada
- Uso eficiente de Pandas/NumPy
- Tests con datos reales de mercado

**Estado:** Pendiente

---

### Bloque 9.2: Prompt Builder

**Archivos:** `ai_module/src/templates/prompt_builder.py`

**Objetivo:**
Construir prompts estructurados para OpenAI con datos técnicos y contexto.

**Tareas de Implementación:**
- Clase **PromptBuilder**:
  - Método `build_portfolio_prompt(portfolio_data: dict, technical_data: dict) -> str`: construye prompt para análisis de portfolio
  - Método `build_asset_prompt(asset_symbol: str, technical_data: dict) -> str`: prompt para activo individual
  - Templates estructurados:
    - Contexto: descripción del portfolio/activo
    - Datos técnicos: RSI, MACD, SMA, volatility
    - Instrucciones: analizar tendencia, identificar riesgos, sugerencias
    - Formato: lenguaje natural, párrafos estructurados
  - Método `add_disclaimer() -> str`: agrega disclaimer legal al final
  - Longitud prompts: 500-1000 tokens

**Test Unitario:**
- Test: build_portfolio_prompt incluye todos los indicadores
- Test: build_asset_prompt formateado correctamente
- Test: disclaimer incluido en todos los prompts
- Test: longitud prompt dentro de límite (< 1500 tokens)
- Test: formato estructurado válido para GPT-4

**Resultado Esperado:**
- Templates reutilizables para prompts
- Estructura consistente en análisis
- Disclaimer automático incluido
- Longitud optimizada de prompts
- Contexto relevante incluido

**Estado:** Pendiente

---

### Bloque 9.3: Analysis Generator

**Archivos:** `ai_module/src/analyzers/market_analyzer.py`

**Objetivo:**
Orquestar proceso completo de análisis: datos → indicadores → prompt → OpenAI → response.

**Tareas de Implementación:**
- Clase **MarketAnalyzer**:
  - Dependencias: TechnicalIndicatorProcessor, PromptBuilder, OpenAIClient
  - Método `analyze_portfolio(portfolio_data: dict, historical_prices: dict) -> str`: flujo completo análisis portfolio
  - Método `analyze_asset(symbol: str, historical_prices: List[dict]) -> str`: flujo análisis activo
  - Flujo:
    1. Validar datos históricos (min 50 puntos)
    2. Calcular indicadores técnicos
    3. Construir prompt estructurado
    4. Enviar a OpenAI
    5. Validar respuesta (> 100 chars)
    6. Agregar disclaimer
  - Logging de cada paso
  - Manejo de errores OpenAI

**Test de Integración:**
- Test: analyze_portfolio con datos reales genera análisis coherente
- Test: analyze_asset calcula indicadores correctamente
- Test: flujo completo ejecuta sin errores
- Test: validación de respuesta OpenAI funciona
- Test: disclaimer incluido en output final
- Test: manejo de error OpenAI (retry)

**Resultado Esperado:**
- Orquestación completa del análisis
- Flujo de 6 pasos funcional
- Integración OpenAI estable
- Validación de outputs
- Logging detallado de proceso
- Manejo de errores robusto

**Estado:** Pendiente

---

### Bloque 9.4: Configuration del Módulo IA

**Archivos:** `ai_module/src/config.py`

**Objetivo:**
Configurar módulo IA con parámetros ajustables.

**Tareas de Implementación:**
- Clase **AIModuleConfig**:
  - OPENAI_API_KEY desde variable de entorno
  - OPENAI_MODEL: "gpt-4" (configurable)
  - TEMPERATURE: 0.7
  - MAX_TOKENS: 1500
  - MIN_DATA_POINTS: 50 (validación)
  - TECHNICAL_INDICATORS_CONFIG: períodos RSI, MACD, SMA
  - CACHE_TTL: 3600 (1 hora)
  - DISCLAIMER_TEXT: texto legal estándar
- Validación de configuración al iniciar
- Export singleton `ai_config`

**Test Unitario:**
- Test: configuración carga correctamente
- Test: valores por defecto aplicados
- Test: validación de OPENAI_API_KEY
- Test: parámetros ajustables funcionan

**Resultado Esperado:**
- Configuración centralizada del módulo IA
- Parámetros ajustables sin cambiar código
- Validación de configuración requerida
- Singleton accesible globalmente

**Estado:** Pendiente

---

## FASE 10: Testing Integral y Documentación

### Bloque 10.1: Test de Integración End-to-End

**Archivos:** `backend/tests/integration/test_e2e_flows.py`

**Objetivo:**
Validar flujos completos de usuario desde registro hasta análisis con IA.

**Tareas de Test:**
- Test: flujo registro → verificación email → login → crear portfolio → registrar operación → obtener análisis
- Test: flujo de inversión completa: buy 10 AAPL → buy 5 GOOGL → sell 3 AAPL → verificar métricas
- Test: flujo de consulta: obtener quote → obtener históricos → generar análisis
- Test: flujo de gestión: actualizar portfolio → cambiar password → ver actividad → eliminar cuenta
- Test: flujo con caché: primera consulta precio (miss) → segunda consulta (hit)
- Test: manejo de errores: operación inválida → validación → error apropiado
- Usar fixtures para datos de test
- Cliente HTTP real contra API levantada

**Resultado Esperado:**
- 6+ flujos E2E validados
- Integración completa de todos los componentes
- Validación de caché funcional
- Manejo de errores consistente
- Fixtures reutilizables
- Tests ejecutables contra API real

**Estado:** Pendiente

---

### Bloque 10.2: Test de Carga y Performance

**Archivos:** `backend/tests/performance/test_load.py`

**Objetivo:**
Validar comportamiento bajo carga y medir tiempos de respuesta.

**Tareas de Test:**
- Test: 100 requests concurrentes a GET /portfolios (< 500ms p95)
- Test: 1000 operaciones bulk import (< 5s total)
- Test: caché Redis soporta 500 req/s
- Test: conexiones DB no se agotan con 50 usuarios concurrentes
- Test: análisis IA completa en < 10s
- Usar locust o pytest-benchmark
- Métricas: p50, p95, p99, throughput

**Resultado Esperado:**
- Suite de tests de performance
- Métricas de latencia documentadas
- Validación de pool de conexiones
- Throughput medido (req/s)
- Identificación de bottlenecks

**Estado:** Pendiente

---

### Bloque 10.3: Cobertura de Tests

**Archivos:** `backend/tests/`, configuración pytest-cov

**Objetivo:**
Alcanzar >80% de cobertura de código con tests automatizados.

**Tareas:**
- Configurar pytest-cov en pytest.ini
- Ejecutar tests con coverage: `pytest --cov=app --cov-report=html`
- Identificar módulos con <80% cobertura
- Escribir tests faltantes para:
  - Edge cases en servicios
  - Manejo de errores en repositorios
  - Validaciones en schemas
  - Middleware excepciones
- Generar reporte HTML de cobertura
- CI/CD: fallar build si cobertura < 80%

**Resultado Esperado:**
- Cobertura global >80%
- Cobertura por módulo visible
- Reporte HTML generado
- Tests de edge cases completos
- CI/CD validando cobertura

**Estado:** Pendiente

---

### Bloque 10.4: Documentación API

**Archivos:** `docs/api_documentation.md`

**Objetivo:**
Documentar todos los endpoints REST con ejemplos y casos de uso.

**Tareas:**
- Documentar 30+ endpoints con:
  - Método HTTP y ruta
  - Parámetros de entrada (path, query, body)
  - Schemas de request/response
  - Códigos de status posibles
  - Ejemplos de curl
  - Casos de error comunes
- Organizar por dominio: Auth, Users, Portfolios, Operations, Market
- Incluir guía de autenticación con JWT
- Ejemplos de flujos comunes
- Publicar en Swagger UI automáticamente

**Resultado Esperado:**
- Documentación completa de API
- Ejemplos ejecutables con curl
- Swagger UI generado automáticamente
- Guías de integración
- Casos de error documentados

**Estado:** Pendiente

---

### Bloque 10.5: Guía de Deployment

**Archivos:** `docs/deployment.md`

**Objetivo:**
Documentar proceso de deployment en producción con configuraciones.

**Tareas:**
- Documentar requisitos del sistema:
  - Python 3.11+
  - PostgreSQL 14+
  - Redis 7+
  - API keys (Alpha Vantage, OpenAI)
- Proceso de instalación paso a paso
- Configuración de variables de entorno (.env)
- Migraciones de BD con Alembic
- Configuración de Uvicorn para producción (workers, logging)
- Docker compose para ambiente completo
- Nginx como reverse proxy
- Monitoreo y logging (futuro)

**Resultado Esperado:**
- Guía completa de deployment
- Docker compose funcional
- Configuración de producción documentada
- Checklist de deployment
- Troubleshooting común

**Estado:** Pendiente

---

### Bloque 10.6: README y Documentación General

**Archivos:** Actualizar `README.md`

**Objetivo:**
Mantener README actualizado con instrucciones de setup y uso.

**Tareas:**
- Actualizar sección de instalación:
  - Clonar repositorio
  - Configurar .env
  - Instalar dependencias
  - Ejecutar migraciones
  - Levantar servidor
- Agregar sección de desarrollo:
  - Ejecutar tests
  - Generar cobertura
  - Linter y formateo (black, flake8)
- Documentar scripts de utilidad
- Agregar badges: tests passing, coverage, version
- Links a documentación detallada

**Resultado Esperado:**
- README completo y actualizado
- Quick start funcional en <5 min
- Badges informativos
- Links a docs detalladas
- Sección de contribución

**Estado:** Pendiente

---

**FIN DEL PLAN DE IMPLEMENTACIÓN**

Total de bloques: 60
- FASE 0: 3 bloques (Configuración Base)
- FASE 1: 6 bloques (Modelos)
- FASE 2: 7 bloques (Schemas)
- FASE 3: 4 bloques (Seguridad)
- FASE 4: 6 bloques (Repositorios)
- FASE 5: 4 bloques (Integraciones)
- FASE 6: 6 bloques (Servicios)
- FASE 7: 4 bloques (Middleware)
- FASE 8: 6 bloques (API Endpoints)
- FASE 9: 4 bloques (Módulo IA)
- FASE 10: 6 bloques (Testing y Docs)

Cada bloque especifica:
- ✅ Archivos exactos a crear
- ✅ Objetivos técnicos claros
- ✅ Tareas de implementación sin código
- ✅ Tests específicos con criterios
- ✅ Resultados esperados medibles
- ✅ Estado tracking

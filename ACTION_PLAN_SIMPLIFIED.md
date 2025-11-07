# Plan de Implementación del Backend

## Introducción

Este documento describe el plan de implementación del backend de nuestra plataforma de gestión de carteras. Organizamos el desarrollo en fases progresivas, comenzando con la configuración base y avanzando hasta la integración con servicios de inteligencia artificial.

El objetivo es construir una API REST funcional aplicando patrones de arquitectura de software que hemos estudiado. Cada fase introduce nuevos conceptos y componentes, permitiendo validar el funcionamiento antes de continuar con la siguiente.

---

## aclaraciones criticas del sistema

**verificacion de email no es requisito para jwt**

jwt funciona sin verificar email. un usuario con `is_verified=false` puede hacer login y usar el sistema completo. los tokens de verificacion existen en el modelo pero no se usan si no hay servicio de email configurado. opcionalmente se puede auto-verificar usuarios en desarrollo.

**integraciones externas opcionales**

**alpha vantage:** solo para obtener precios automaticamente. sin api key el usuario ingresa precios manualmente.

**openai:** solo para generar analisis con ia. sin api key esa funcionalidad no esta disponible.

el core del sistema (portfolios, operaciones, reportes) funciona sin estas integraciones.

---

## Seguimiento de Implementación

Para mantener trazabilidad sobre el progreso del proyecto, decidimos documentar cada sesión de trabajo indicando los bloques completados, la fecha de implementación y observaciones relevantes. Esto nos permite tener un registro claro de las decisiones tomadas y facilita la comprensión del proceso de desarrollo cuando revisamos el código posteriormente.

---

### DIA 7 DE NOVIEMBRE - 10:00 AM - BLOQUES 0.1 Y 0.2 COMPLETADOS

Bloques implementados:
- Bloque 0.1: Estructura de Directorios y Dependencias
- Bloque 0.2: Configuración Central con Variables de Entorno

Comentarios:
Hoy nos dedicamos al paso de configuracion inicial del proyecto. Configuramos el archivo requirements.txt con todas las dependencias esenciales (FastAPI, SQLAlchemy, Pydantic, etc.) y creamos el sistema de configuracion centralizado usando Pydantic Settings. 

Decidimos mantener las API keys de OpenAI y Alpha Vantage opcionales por ahora, dejandolas con valores vacios que podemos rellenar mas adelante cuando implementemos esas integraciones. El archivo .env ya contiene la conexion a PostgreSQL configurada y funcionando.

Actualizamos tambien el .gitignore para asegurar que no subamos informacion sensible al repositorio. Todas las dependencias se instalaron sin conflictos en el entorno conda uie_arquitectura_software.

Validaciones realizadas:
- Instalacion de dependencias sin errores
- Verificacion de imports: fastapi, sqlalchemy, pydantic
- Sin conflictos de versiones (pip check)
- Carga correcta de configuracion desde .env

---

### DIA 7 DE NOVIEMBRE - 2:00 PM - BLOQUE 0.3 COMPLETADO

Bloque implementado:
- Bloque 0.3: Configuracion de Motor de Base de Datos

Comentarios:
Implementamos el archivo session.py que maneja la conexion con PostgreSQL. Este archivo es fundamental porque define el engine de sqlalchemy, la sesion de base de datos y la funcion get_db que usaremos en fastapi para inyectar la sesion en los endpoints.

Configuramos el pool de conexiones con valores razonables para desarrollo: 5 conexiones base y hasta 10 adicionales. Tambien activamos pool_pre_ping que verifica las conexiones antes de usarlas para evitar errores con conexiones muertas.

La funcion get_db usa el patron de generador de python para asegurar que la sesion siempre se cierre correctamente, incluso si hay errores. Esto previene fugas de conexiones.

Validaciones realizadas:
- Conexion exitosa a PostgreSQL
- Pool de conexiones funcionando correctamente

---

### DIA 7 DE NOVIEMBRE - 3:00 PM - BLOQUES 1.1 A 1.5 COMPLETADOS

Bloques implementados:
- Bloque 1.1: Modelos de Usuario y Autenticacion
- Bloque 1.2: Modelos de Portfolio y Posiciones
- Bloque 1.3: Modelo de Operaciones Financieras
- Bloque 1.4: Modelos de Activos y Precios
- Bloque 1.5: Modelos de Analisis con IA

Comentarios:
Dedicamos esta sesion a crear todos los modelos ORM que representan las entidades del dominio. Cada modelo hereda de Base para que sqlalchemy los detecte.

En user.py creamos User, UserProfile y UserSession. Decidimos separar el perfil del usuario para mantener la tabla users liviana con solo lo esencial para autenticacion. UserSession almacena los refresh tokens para que un usuario pueda tener multiples sesiones activas en diferentes dispositivos.

En portfolio.py implementamos Portfolio y PortfolioAsset. Lo mas importante aqui es que usamos el tipo Decimal para todos los valores monetarios porque float tiene problemas de precision con decimales. Un portfolio tiene metodos para calcular sus metricas financieras sumando el valor de todas sus posiciones.

En operation.py creamos el modelo Operation que registra cada compra o venta. El total_amount se calcula diferente segun el tipo: en compras sumamos fees, en ventas los restamos. Esto es importante para saber cuanto realmente pagamos o recibimos.

En asset.py definimos Asset (catalogo de activos disponibles) y AssetPrice (historico de precios). AssetPrice usa la estructura OHLCV estandar: open high low close volume. Estos datos los usaremos despues para calcular indicadores tecnicos.

En analysis.py creamos Analysis y AnalysisRequest. Analysis almacena el texto generado por la IA con un sistema de cache temporal (expires_at) para no regenerar el mismo analisis repetidamente y ahorrar costos de API. AnalysisRequest trackea quien solicito que analisis y si se completo o fallo.

Decisiones de diseño que tomamos:
- UUID como primary keys en lugar de integers secuenciales
- Decimal para valores monetarios
- Timestamps automaticos en todos los modelos
- Cascade delete donde tiene sentido (eliminar usuario elimina sus portfolios)
- Constraints a nivel de base de datos para integridad

---

### DIA 7 DE NOVIEMBRE - 4:00 PM - BLOQUE 1.6 COMPLETADO

Bloque implementado:
- Bloque 1.6: Configuracion de Migraciones con Alembic

Comentarios:
Inicializamos alembic para gestionar las migraciones de base de datos. Configuramos el archivo env.py para que importe automaticamente todos nuestros modelos, esto es critico para que alembic pueda detectarlos y generar las migraciones.

Modificamos alembic.ini para comentar la linea de sqlalchemy.url porque en su lugar usamos la configuracion desde settings.py. Asi centralizamos la configuracion de base de datos en un solo lugar.

Generamos la migracion inicial con alembic revision --autogenerate y revisamos el archivo generado para verificar que detecto todas las tablas, foreign keys y constraints. Todo se veia correcto.

Aplicamos la migracion con alembic upgrade head y verificamos en pgadmin que todas las tablas se crearon correctamente con sus relaciones.

Validaciones realizadas:
- Migracion generada detecta todas las tablas
- Upgrade exitoso sin errores
- Todas las foreign keys y constraints creados correctamente
- Tablas visibles en postgresql

---

### DIA 7 DE NOVIEMBRE - 5:00 PM - BLOQUES 2.1 A 2.6 COMPLETADOS

Bloques implementados:
- Bloque 2.1: Schemas de Autenticacion
- Bloque 2.2: Schemas de Usuario
- Bloque 2.3: Schemas de Portfolio
- Bloque 2.4: Schemas de Operaciones
- Bloque 2.5: Schemas de Mercado
- Bloque 2.6: Schemas de Analisis

Comentarios:
Creamos todos los schemas pydantic que usaremos para validar requests y serializar responses. Pydantic se encarga automaticamente de validar tipos y lanzar errores claros si algo esta mal.

En auth.py implementamos schemas para registro y login. Agregamos un validator custom para password que verifica que tenga al menos una mayuscula, una minuscula y un numero. No pedimos simbolos especiales para no complicar innecesariamente. El validator lanza errores descriptivos si la password no cumple.

En user.py creamos schemas que nunca exponen el password_hash por seguridad. UserProfileResponse incluye datos anidados del perfil. UserUpdate tiene todos los campos opcionales porque usamos semantica PATCH (solo actualizar lo que se envia).

En portfolio.py los schemas incluyen campos calculados como gain_loss y gain_loss_percent que se derivan de otros valores. PortfolioDetailResponse tiene una lista anidada de posiciones para retornar todo el portfolio con sus assets en una sola response.

En operation.py agregamos validators para asegurar que quantity y price sean siempre positivos. OperationFilter tiene todos los campos opcionales para permitir filtrar por cualquier combinacion de criterios.

En market.py definimos la estructura OHLCV en PricePoint que coincide con lo que retornan las APIs de mercado.

En analysis.py implementamos un validator que verifica que la solicitud tenga portfolio_id O asset_symbol pero no ambos. Esto asegura que el tipo de analisis sea consistente con los datos proporcionados.

---

### DIA 7 DE NOVIEMBRE - 6:00 PM - BLOQUES 3.1 A 3.3 COMPLETADOS

Bloques implementados:
- Bloque 3.1: Password Hasher con Bcrypt
- Bloque 3.2: JWT Handler para Tokens
- Bloque 3.3: Generador de Tokens de Verificacion

Comentarios:
Implementamos los componentes de seguridad que manejaran autenticacion y encriptacion.

En password.py creamos PasswordHasher que usa bcrypt con cost factor 12. Bcrypt es el estandar para passwords porque genera un salt aleatorio automaticamente y es resistente a ataques de fuerza bruta. El cost factor 12 es un buen balance entre seguridad y performance para nuestro caso academico.

En jwt.py implementamos JWTHandler para crear y validar tokens JWT. Decidimos usar access tokens de 30 minutos y refresh tokens de 7 dias. Los access tokens son cortos para limitar el tiempo de exposicion si alguien los roba. Los refresh tokens duran mas para que el usuario no tenga que hacer login constantemente. Usamos el algoritmo HS256 que es estandar y suficientemente seguro.

En tokens.py creamos funciones para generar tokens aleatorios url-safe usando el modulo secrets de python que es criptograficamente seguro. Estos tokens se usan para verificacion de email y reset de password. Definimos TTLs de 48 horas para verificacion de email y 1 hora para reset de password (mas corto por seguridad).

---

### DIA 7 DE NOVIEMBRE - 7:00 PM - BLOQUES 4.1 A 4.6 COMPLETADOS

Bloques implementados:
- Bloque 4.1: Base Repository Generico
- Bloque 4.2: UserRepository
- Bloque 4.3: PortfolioRepository
- Bloque 4.4: OperationRepository
- Bloque 4.5: AssetRepository
- Bloque 4.6: AnalysisRepository

Comentarios:
Implementamos el patron repository para separar la logica de acceso a datos de la logica de negocio. Esto hace el codigo mas testeable y mantenible.

En base.py creamos BaseRepository generico usando TypeVar. Este repositorio tiene los metodos CRUD basicos que todos los modelos necesitan: create, get_by_id, update, delete, etc. Los repositorios especificos heredan de esta clase y agregan metodos propios de su dominio. Esto evita repetir codigo.

En user.py agregamos metodos especificos como get_by_email con busqueda case-insensitive, create_with_profile que crea usuario y perfil en una transaccion atomica, y metodos para gestionar sesiones de usuario.

En portfolio.py (que falta implementar todavia) agregaremos metodos para crear o actualizar posiciones (upsert pattern) y cargar portfolios con sus posiciones en una sola query (eager loading para evitar el problema n+1).

En operation.py implementamos filtrado multi-criterio para que se puedan buscar operaciones por portfolio, asset, tipo, rango de fechas o cualquier combinacion.

En asset.py agregamos search_assets para busqueda fuzzy por simbolo o nombre, y get_or_create que es util para no duplicar activos cuando se opera un simbolo por primera vez.

En analysis.py implementamos get_cached_analysis que busca analisis no expirados para evitar regenerarlos, y metodos para trackear el estado de las solicitudes de analisis.

Todos los repositorios manejan transacciones y hacen rollback automatico si hay errores.

---

---

## FASE 0: Configuración Base del Proyecto

### Bloque 0.1: Estructura de Directorios y Dependencias

**Archivo:** `backend/requirements.txt`

**Objetivo:**
Establecer la estructura base del proyecto y definir las dependencias necesarias para el desarrollo del backend.

**Tareas de Implementación:**
- Crear estructura completa de directorios según la arquitectura documentada
- Definir dependencias en requirements.txt: FastAPI, SQLAlchemy, Alembic, Pydantic, Passlib, Pandas, OpenAI, Pytest
- Crear archivos `__init__.py` en todos los paquetes Python
- Configurar archivo `.gitignore` para Python

**Validación:**
- Instalar dependencias sin errores: `pip install -r requirements.txt`
- Verificar importación básica: `python -c "import fastapi, sqlalchemy, pydantic"`
- Comprobar que no hay conflictos de versiones con `pip check`

**Resultado Esperado:**
- Estructura de directorios completa y organizada
- requirements.txt con todas las dependencias especificadas
- Entorno virtual funcionando correctamente

---

### Bloque 0.2: Configuración Central con Variables de Entorno

**Archivo:** `backend/app/core/config/settings.py`

**Objetivo:**
Implementar un sistema centralizado de configuración usando Pydantic Settings para gestionar variables de entorno de forma tipada y segura.

**Tareas de Implementación:**
- Crear clase `Settings` heredando de `BaseSettings`
- Definir variables agrupadas por categoría:
  - Database: DATABASE_URL, pool_size
  - Security: SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
  - External APIs: ALPHA_VANTAGE_API_KEY, OPENAI_API_KEY
  - CORS: lista de orígenes permitidos
- Configurar lectura desde archivo `.env`
- Exportar singleton `settings` para uso global

**Validación:**
- Cargar variables desde archivo .env de prueba
- Verificar que lanza error si faltan variables críticas
- Comprobar tipos de datos correctos

**Resultado Esperado:**
- Clase Settings funcionando con variables tipadas
- Archivo `.env.example` documentado
- Singleton accesible desde cualquier módulo

---

### Bloque 0.3: Configuración de Motor de Base de Datos

**Archivo:** `backend/app/core/database/session.py`

**Objetivo:**
Configurar el motor de SQLAlchemy para la conexión con PostgreSQL y definir la sesión de base de datos.

**Tareas de Implementación:**
- Crear `engine` usando create_engine con DATABASE_URL
- Configurar pool de conexiones básico
- Crear `SessionLocal` con sessionmaker
- Definir `Base` declarativa para los modelos
- Implementar función `get_db()` para dependency injection

**Validación:**
- Establecer conexión a PostgreSQL
- Ejecutar query simple: `SELECT 1`
- Verificar que las sesiones se crean y destruyen correctamente

**Resultado Esperado:**
- Conexión estable a PostgreSQL
- Base declarativa lista para usar en modelos
- Función get_db() funcional para FastAPI

---

## FASE 1: Capa de Modelos (Domain Models)

### Bloque 1.1: Modelos de Usuario y Autenticación

**Archivos:** `backend/app/models/user.py`

**Objetivo:**
Implementar los modelos ORM para gestión de usuarios, perfiles y sesiones.

**Tareas de Implementación:**
- **Clase User**: campos básicos (id, email, password_hash, is_active, is_verified, timestamps)
- Relaciones: profile (one-to-one), sessions (one-to-many), portfolios (one-to-many)
- Métodos: verify_password(), hash_password()
- **Clase UserProfile**: información adicional del usuario (currency, timezone, language, preferences)
- **Clase UserSession**: gestión de refresh tokens

**Validación:**
- Crear usuario y verificar generación de UUID
- Probar hashing y verificación de contraseñas
- Validar constraint de email único
- Verificar relaciones User-UserProfile

**Resultado Esperado:**
- Tres clases ORM funcionales
- Relaciones entre modelos configuradas
- Métodos de negocio operativos

---

### Bloque 1.2: Modelos de Portfolio y Posiciones

**Archivos:** `backend/app/models/portfolio.py`

**Objetivo:**
Implementar modelos para la gestión de carteras y posiciones de activos.

**Tareas de Implementación:**
- **Clase Portfolio**: campos para métricas financieras (total_value, total_cost, gain_loss)
- Constraint único en (user_id, name)
- Relaciones: user, assets (one-to-many)
- Métodos: calculate_metrics(), update_balance()
- **Clase PortfolioAsset**: representación de posiciones (quantity, average_price, current_price)
- Métodos: calculate_position_value()

**Validación:**
- Crear portfolio y verificar inicialización
- Crear posiciones y calcular valores
- Probar cálculo de métricas con múltiples posiciones
- Verificar constraint de nombre único por usuario

**Resultado Esperado:**
- Modelos Portfolio y PortfolioAsset funcionales
- Cálculos financieros precisos usando Decimal
- Relaciones configuradas correctamente

---

### Bloque 1.3: Modelo de Operaciones Financieras

**Archivos:** `backend/app/models/operation.py`

**Objetivo:**
Implementar el modelo para registro de operaciones de compra y venta.

**Tareas de Implementación:**
- Definir Enum **OperationType** (BUY, SELL)
- **Clase Operation**: campos transaccionales (quantity, price, fees, total_amount)
- CheckConstraints: quantity > 0, price > 0, fees >= 0
- Relación con Portfolio
- Métodos: calculate_total() diferenciado por tipo

**Validación:**
- Crear operación BUY y verificar cálculo total
- Crear operación SELL y verificar cálculo
- Probar constraints de valores positivos
- Verificar relación con Portfolio

**Resultado Esperado:**
- Modelo Operation funcional
- Enum OperationType configurado
- Cálculos correctos según tipo de operación

---

### Bloque 1.4: Modelos de Activos y Precios

**Archivos:** `backend/app/models/asset.py`

**Objetivo:**
Implementar modelos para el catálogo de activos financieros y sus precios históricos.

**Tareas de Implementación:**
- Definir Enum **AssetType** (STOCK, ETF, CRYPTO)
- **Clase Asset**: información del activo (symbol, name, type, currency)
- **Clase AssetPrice**: precios históricos con timestamp
- Constraint único en (asset_symbol, timestamp)

**Validación:**
- Crear activo y verificar constraint de symbol único
- Agregar precios históricos
- Probar constraint de timestamp único por activo

**Resultado Esperado:**
- Modelos Asset y AssetPrice funcionales
- Constraints de unicidad aplicados
- Relaciones configuradas

---

### Bloque 1.5: Modelos de Análisis con IA

**Archivos:** `backend/app/models/analysis.py`

**Objetivo:**
Implementar modelos para almacenar análisis generados por IA.

**Tareas de Implementación:**
- Definir Enums: **AnalysisType** (PORTFOLIO, ASSET), **AnalysisStatus** (PENDING, COMPLETED, FAILED)
- **Clase Analysis**: almacena el análisis generado (text, technical_indicators, expires_at)
- **Clase AnalysisRequest**: tracking de solicitudes de análisis
- Métodos: is_expired(), get_disclaimer()

**Validación:**
- Crear análisis y verificar campos
- Probar método is_expired()
- Crear request de análisis
- Verificar disclaimer automático

**Resultado Esperado:**
- Modelos de análisis funcionales
- Sistema de caché temporal implementado
- Tracking de requests operativo

---

### Bloque 1.6: Configuración de Migraciones con Alembic

**Archivos:** `backend/alembic/`, `backend/alembic.ini`

**Objetivo:**
Inicializar Alembic para gestión de migraciones y crear la migración inicial.

**Tareas de Implementación:**
- Ejecutar `alembic init alembic`
- Configurar alembic.ini y env.py
- Importar todos los modelos en env.py
- Generar migración inicial: `alembic revision --autogenerate -m "Initial migration"`
- Revisar archivo de migración generado
- Aplicar migración: `alembic upgrade head`

**Validación:**
- Ejecutar upgrade en base de datos limpia
- Verificar creación de todas las tablas
- Comprobar foreign keys y constraints
- Ejecutar downgrade y verificar limpieza

**Resultado Esperado:**
- Alembic configurado y funcional
- Migración inicial genera esquema completo
- Upgrade/downgrade funciona correctamente

---

## FASE 2: Capa de Schemas (Pydantic DTOs)

### Bloque 2.1: Schemas de Autenticación

**Archivos:** `backend/app/schemas/auth.py`

**Objetivo:**
Implementar esquemas Pydantic para validación de requests y responses de autenticación.

**Tareas de Implementación:**
- **UserRegister**: email, password, full_name con validators
- **UserLogin**: email, password
- **TokenResponse**: access_token, refresh_token, token_type, expires_in
- **PasswordReset**: token, new_password
- Validators personalizados para email y password strength

**Validación:**
- Probar validator de email con formato inválido
- Probar validator de password con password débil
- Serializar/deserializar schemas

**Resultado Esperado:**
- Schemas de autenticación funcionales
- Validadores custom operativos
- Mensajes de error descriptivos

---

### Bloque 2.2: Schemas de Usuario

**Archivos:** `backend/app/schemas/user.py`

**Objetivo:**
Implementar schemas para gestión de perfiles de usuario.

**Tareas de Implementación:**
- **UserResponse**: información pública del usuario (excluye password_hash)
- **UserProfileResponse**: incluye datos del perfil
- **UserUpdate**: campos actualizables
- **PasswordChange**: current_password, new_password

**Validación:**
- Verificar exclusión de campos sensibles
- Probar validators de currency y timezone
- Serializar desde modelo ORM

**Resultado Esperado:**
- Schemas de usuario funcionales
- Campos sensibles excluidos
- Compatibilidad ORM configurada

---

### Bloque 2.3: Schemas de Portfolio

**Archivos:** `backend/app/schemas/portfolio.py`

**Objetivo:**
Implementar schemas para gestión de carteras.

**Tareas de Implementación:**
- **PortfolioCreate**: name, base_currency, description
- **PortfolioUpdate**: campos modificables
- **PortfolioResponse**: incluye métricas calculadas
- **PortfolioAssetResponse**: información de posiciones
- **PortfolioDetailResponse**: response completo con posiciones

**Validación:**
- Probar validators de name y currency
- Verificar serialización de Decimals
- Probar schemas anidados

**Resultado Esperado:**
- Schemas de portfolio funcionales
- Serialización de tipos complejos configurada
- Responses anidados operativos

---

### Bloque 2.4: Schemas de Operaciones

**Archivos:** `backend/app/schemas/operation.py`

**Objetivo:**
Implementar schemas para operaciones financieras.

**Tareas de Implementación:**
- **OperationCreate**: datos de la operación con validators
- **OperationUpdate**: campos modificables
- **OperationResponse**: incluye total_amount calculado
- **OperationFilter**: parámetros de filtrado

**Validación:**
- Probar validators de valores positivos
- Verificar validación de rangos de fechas
- Probar cálculo de total_amount

**Resultado Esperado:**
- Schemas de operaciones funcionales
- Validators impiden valores inválidos
- Filtros configurados

---

### Bloque 2.5: Schemas de Mercado

**Archivos:** `backend/app/schemas/market.py`

**Objetivo:**
Implementar schemas para datos de mercado.

**Tareas de Implementación:**
- **AssetInfo**: información del activo
- **PricePoint**: punto de precio OHLCV
- **CurrentPriceResponse**: precio actual
- **HistoricalPriceResponse**: histórico de precios

**Validación:**
- Probar validators de datos OHLCV
- Verificar serialización de datetime
- Probar listas de PricePoint

**Resultado Esperado:**
- Schemas de mercado funcionales
- Validación de consistencia OHLCV
- Timezone handling configurado

---

### Bloque 2.6: Schemas de Análisis

**Archivos:** `backend/app/schemas/analysis.py`

**Objetivo:**
Implementar schemas para análisis con IA.

**Tareas de Implementación:**
- **TechnicalIndicators**: estructura de indicadores técnicos
- **AnalysisRequest**: solicitud de análisis
- **AnalysisResponse**: resultado del análisis con disclaimer
- Validator: portfolio_id o asset_symbol debe estar presente

**Validación:**
- Probar validator de campos mutuamente exclusivos
- Verificar inclusión automática de disclaimer
- Probar schemas anidados

**Resultado Esperado:**
- Schemas de análisis funcionales
- Validators custom operativos
- Disclaimer automático incluido

---

## FASE 3: Componentes de Seguridad

### Bloque 3.1: Password Hasher con Bcrypt

**Archivos:** `backend/app/core/security/password.py`

**Objetivo:**
Implementar componente para hashing y verificación de contraseñas.

**Tareas de Implementación:**
- Clase **PasswordHasher**:
  - Método `hash_password(password: str) -> str`
  - Método `verify_password(password: str, hash: str) -> bool`
- Usar bcrypt con cost factor 12

**Validación:**
- Verificar que hash genera salt diferente cada vez
- Probar verify_password con password correcta e incorrecta
- Validar formato bcrypt del hash generado

**Resultado Esperado:**
- Hashing seguro con bcrypt
- Verificación funcional
- Salts aleatorios

---

### Bloque 3.2: JWT Handler para Tokens

**Archivos:** `backend/app/core/security/jwt.py`

**Objetivo:**
Implementar handler para creación y validación de tokens JWT.

**Tareas de Implementación:**
- Clase **JWTHandler**:
  - Método `create_access_token(data: dict) -> str`
  - Método `create_refresh_token(data: dict) -> str`
  - Método `decode_token(token: str) -> dict`
  - Método `verify_token(token: str) -> bool`

**Validación:**
- Crear y decodificar token correctamente
- Verificar expiración de tokens
- Probar con token inválido

**Resultado Esperado:**
- Generación de tokens JWT funcional
- Validación de firma y expiración
- Access tokens (15min) y refresh tokens (7 días)

---

### Bloque 3.3: Generador de Tokens de Verificación

**Archivos:** `backend/app/core/security/tokens.py`

**Objetivo:**
Implementar generadores de tokens seguros para verificación de email y reset de password.

**Tareas de Implementación:**
- Función `generate_verification_token() -> str`
- Función `generate_reset_token() -> str`
- Función `verify_token_expiration(created_at, ttl_hours) -> bool`

**Validación:**
- Verificar que tokens son únicos
- Probar validación de expiración
- Comprobar que tokens son URL-safe

**Resultado Esperado:**
- Tokens criptográficamente seguros
- Validación de expiración funcional
- Tokens URL-safe

---

## FASE 4: Capa de Repositorios (Repository Pattern)

### Bloque 4.1: Base Repository Genérico

**Archivos:** `backend/app/repositories/base.py`

**Objetivo:**
Implementar repositorio base genérico con operaciones CRUD comunes.

**Tareas de Implementación:**
- Clase genérica **BaseRepository[T]**:
  - Métodos: create(), get_by_id(), update(), delete()
  - Métodos: list(), count()
  - Manejo de transacciones

**Validación:**
- Probar operaciones CRUD básicas
- Verificar paginación en list()
- Probar manejo de errores con rollback

**Resultado Esperado:**
- Repositorio base genérico funcional
- Métodos CRUD reutilizables
- Type hints correctos

---

### Bloque 4.2: UserRepository

**Archivos:** `backend/app/repositories/user.py`

**Objetivo:**
Implementar repositorio especializado para usuarios.

**Tareas de Implementación:**
- Clase **UserRepository** hereda BaseRepository[User]:
  - `get_by_email(email: str)`
  - `update_profile(user_id, profile_data)`
  - `create_session(user_id, refresh_token)`
  - `get_active_sessions(user_id)`

**Validación:**
- Probar búsqueda por email (case-insensitive)
- Crear y actualizar perfil
- Gestionar sesiones

**Resultado Esperado:**
- Repositorio de usuarios funcional
- Métodos específicos del dominio
- Eager loading optimizado

---

### Bloque 4.3: PortfolioRepository

**Archivos:** `backend/app/repositories/portfolio.py`

**Objetivo:**
Implementar repositorio para carteras y posiciones.

**Tareas de Implementación:**
- Clase **PortfolioRepository**:
  - `get_by_user_id(user_id)`
  - `get_with_positions(portfolio_id)`
  - `create_or_update_position(portfolio_id, asset_data)`
  - `calculate_portfolio_metrics(portfolio_id)`

**Validación:**
- Listar carteras de un usuario
- Crear y actualizar posiciones
- Calcular métricas financieras

**Resultado Esperado:**
- Repositorio de portfolios funcional
- Cálculo de métricas implementado
- Upsert de posiciones operativo

---

### Bloque 4.4: OperationRepository

**Archivos:** `backend/app/repositories/operation.py`

**Objetivo:**
Implementar repositorio para operaciones financieras.

**Tareas de Implementación:**
- Clase **OperationRepository**:
  - `get_by_portfolio(portfolio_id, filters)`
  - `filter_by_date_range(date_from, date_to)`
  - `get_portfolio_statistics(portfolio_id)`

**Validación:**
- Filtrar operaciones por criterios
- Calcular estadísticas básicas
- Aplicar rangos de fechas

**Resultado Esperado:**
- Repositorio de operaciones funcional
- Filtrado multi-criterio
- Estadísticas básicas

---

### Bloque 4.5: AssetRepository

**Archivos:** `backend/app/repositories/asset.py`

**Objetivo:**
Implementar repositorio para activos y precios.

**Tareas de Implementación:**
- Clase **AssetRepository**:
  - `get_by_symbol(symbol)`
  - `search_assets(query)`
  - `get_or_create(asset_data)`
  - `get_historical_prices(symbol, days)`

**Validación:**
- Buscar por símbolo
- Búsqueda fuzzy de activos
- Get-or-create pattern
- Consultar históricos

**Resultado Esperado:**
- Repositorio de activos funcional
- Búsqueda flexible
- Gestión de precios históricos

---

### Bloque 4.6: AnalysisRepository

**Archivos:** `backend/app/repositories/analysis.py`

**Objetivo:**
Implementar repositorio para análisis con IA.

**Tareas de Implementación:**
- Clase **AnalysisRepository**:
  - `get_cached_analysis(portfolio_id, asset_symbol)`
  - `invalidate_cache(portfolio_id)`
  - `create_request(request_data)`
  - `update_request_status(request_id, status)`

**Validación:**
- Obtener análisis cacheado
- Invalidar caché
- Gestionar requests de análisis

**Resultado Esperado:**
- Repositorio de análisis funcional
- Sistema de caché implementado
- Tracking de requests

---

## FASE 5: Integraciones Externas

### Bloque 5.1: Cliente Alpha Vantage API

**Archivos:** `backend/app/clients/alpha_vantage.py`

**Objetivo:**
Implementar cliente HTTP para Alpha Vantage API.

**Tareas de Implementación:**
- Clase **AlphaVantageClient**:
  - `get_quote(symbol) -> dict`
  - `get_daily_prices(symbol, days) -> list`
  - `search_symbol(query) -> list`
- Manejo de errores HTTP
- Retry simple en errores temporales

**Validación:**
- Obtener cotización de símbolo válido
- Consultar precios históricos
- Buscar símbolos
- Manejar símbolo inválido

**Resultado Esperado:**
- Cliente funcional con 3 métodos principales
- Manejo básico de errores
- Parsing de respuestas

---

### Bloque 5.2: Cliente OpenAI API

**Archivos:** `backend/app/clients/openai_client.py`

**Objetivo:**
Implementar wrapper para OpenAI API.

**Tareas de Implementación:**
- Clase **OpenAIClient**:
  - `generate_analysis(prompt, model) -> str`
  - `validate_response(response) -> bool`
- Timeout configurado
- Logging básico

**Validación:**
- Generar análisis con prompt válido
- Validar respuesta generada
- Manejar errores de API

**Resultado Esperado:**
- Cliente funcional con SDK oficial
- Validación de respuestas
- Timeout configurado

---

### Bloque 5.3: Cliente Redis Cache (Opcional)

**Archivos:** `backend/app/clients/redis_client.py`

**Objetivo:**
Implementar wrapper básico para Redis como caché.

**Tareas de Implementación:**
- Clase **RedisClient**:
  - `get(key)`
  - `set(key, value, ttl)`
  - `delete(key)`
- Manejo graceful si Redis no disponible

**Validación:**
- Operaciones básicas get/set
- Expiración por TTL
- Fallback si Redis no disponible

**Resultado Esperado:**
- Cliente básico funcional
- TTL configurable
- Fallback graceful

---

## FASE 6: Capa de Servicios (Business Logic)

### Bloque 6.1: AuthService

**Archivos:** `backend/app/services/auth_service.py`

**Objetivo:**
Implementar lógica de negocio para autenticación.

**Tareas de Implementación:**
- Clase **AuthService**:
  - `register_user(user_data)`
  - `authenticate_user(email, password)`
  - `verify_email(token)`
  - `refresh_access_token(refresh_token)`
  - `logout(user_id, session_id)`

**Validación:**
- Registrar usuario completo (User + UserProfile)
- Autenticar con credenciales válidas
- Verificar email
- Refrescar token
- Cerrar sesión

**Resultado Esperado:**
- Servicio de autenticación funcional
- Validaciones de seguridad implementadas
- Transacciones atómicas

---

### Bloque 6.2: PortfolioService

**Archivos:** `backend/app/services/portfolio_service.py`

**Objetivo:**
Implementar lógica de negocio para carteras.

**Tareas de Implementación:**
- Clase **PortfolioService**:
  - `create_portfolio(user_id, portfolio_data)`
  - `get_portfolio(portfolio_id, user_id)`
  - `get_portfolio_details(portfolio_id, user_id)`
  - `update_portfolio(portfolio_id, user_id, data)`
  - `delete_portfolio(portfolio_id, user_id)`

**Validación:**
- Crear portfolio
- Validar ownership
- Obtener detalles con posiciones
- Actualizar y eliminar

**Resultado Esperado:**
- Servicio de portfolios funcional
- Validación de ownership en todos los métodos
- Cálculo de métricas integrado

---

### Bloque 6.3: OperationService

**Archivos:** `backend/app/services/operation_service.py`

**Objetivo:**
Implementar lógica para operaciones de compra/venta.

**Tareas de Implementación:**
- Clase **OperationService**:
  - `create_buy_operation(operation_data)`
  - `create_sell_operation(operation_data)`
  - `update_operation(operation_id, data)`
  - `delete_operation(operation_id)`

**Validación:**
- Crear operación BUY y actualizar posición
- Crear operación SELL validando cantidad disponible
- Actualizar operación
- Eliminar operación

**Resultado Esperado:**
- Servicio de operaciones funcional
- Lógica diferenciada BUY vs SELL
- Actualización automática de posiciones

---

### Bloque 6.4: MarketDataService

**Archivos:** `backend/app/services/market_data_service.py`

**Objetivo:**
Implementar lógica para obtención de datos de mercado.

**Tareas de Implementación:**
- Clase **MarketDataService**:
  - `get_current_price(symbol)`
  - `get_historical_prices(symbol, days)`
  - `search_assets(query)`
- Caché simple en Redis (si disponible)

**Validación:**
- Obtener precio actual
- Consultar históricos
- Buscar activos
- Verificar caché básico

**Resultado Esperado:**
- Servicio de mercado funcional
- Caché básico implementado
- Integración con Alpha Vantage

---

### Bloque 6.5: AIService

**Archivos:** `backend/app/services/ai_service.py`

**Objetivo:**
Implementar lógica para generación de análisis con IA.

**Tareas de Implementación:**
- Clase **AIService**:
  - `generate_portfolio_analysis(portfolio_id)`
  - `generate_asset_analysis(symbol)`
  - `get_cached_analysis(portfolio_id, symbol)`
- Integración con módulo IA

**Validación:**
- Generar análisis de portfolio
- Generar análisis de activo
- Usar caché si disponible

**Resultado Esperado:**
- Servicio de IA funcional
- Integración con OpenAI
- Caché de análisis

---

### Bloque 6.6: UserService

**Archivos:** `backend/app/services/user_service.py`

**Objetivo:**
Implementar lógica para gestión de usuarios.

**Tareas de Implementación:**
- Clase **UserService**:
  - `get_user_profile(user_id)`
  - `update_user_profile(user_id, profile_data)`
  - `change_password(user_id, current_password, new_password)`

**Validación:**
- Obtener perfil
- Actualizar perfil
- Cambiar password

**Resultado Esperado:**
- Servicio de usuarios funcional
- Validaciones implementadas
- Actualización segura de password

---

## FASE 7: Middleware y Dependencias

### Bloque 7.1: Authentication Middleware

**Archivos:** `backend/app/middleware/auth_middleware.py`

**Objetivo:**
Implementar dependency para validación de JWT.

**Tareas de Implementación:**
- Función **get_current_user(token, db)**:
  - Extraer token del header
  - Decodificar y validar JWT
  - Obtener usuario de base de datos
  - Verificar usuario activo

**Validación:**
- Probar con token válido
- Probar con token expirado
- Probar con token inválido
- Probar con usuario inactivo

**Resultado Esperado:**
- Dependency funcional para proteger endpoints
- Validación automática de JWT
- Errores HTTP apropiados

---

### Bloque 7.2: Error Handling Middleware

**Archivos:** `backend/app/middleware/error_handler.py`

**Objetivo:**
Implementar middleware para manejo de errores.

**Tareas de Implementación:**
- Clase **ErrorHandlerMiddleware**:
  - Capturar excepciones
  - Convertir a respuestas HTTP estandarizadas
  - Logging de errores

**Validación:**
- Probar manejo de diferentes tipos de excepciones
- Verificar respuestas estandarizadas
- Comprobar logging

**Resultado Esperado:**
- Middleware de errores funcional
- Respuestas estandarizadas
- Logging apropiado

---

### Bloque 7.3: CORS Middleware

**Archivos:** `backend/app/middleware/cors.py`

**Objetivo:**
Configurar CORS para permitir requests desde frontend.

**Tareas de Implementación:**
- Configurar CORSMiddleware:
  - Orígenes permitidos desde settings
  - Métodos y headers permitidos
  - Credentials habilitadas

**Validación:**
- Probar request desde origen permitido
- Verificar preflight OPTIONS

**Resultado Esperado:**
- CORS configurado correctamente
- Preflight requests manejados
- Configuración desde settings

---

## FASE 8: Capa de API (Endpoints REST)

### Bloque 8.1: Auth Endpoints

**Archivos:** `backend/app/api/v1/auth/router.py`

**Objetivo:**
Implementar endpoints de autenticación.

**Tareas de Implementación:**
- Router `/api/v1/auth`:
  - POST `/register`
  - POST `/login`
  - POST `/refresh`
  - POST `/logout`
  - POST `/verify-email`

**Validación:**
- Registrar usuario nuevo
- Login con credenciales válidas
- Refrescar token
- Logout
- Verificar email

**Resultado Esperado:**
- Endpoints de autenticación funcionales
- Documentación OpenAPI generada
- Status codes apropiados

---

### Bloque 8.2: Users Endpoints

**Archivos:** `backend/app/api/v1/users/router.py`

**Objetivo:**
Implementar endpoints de gestión de usuario.

**Tareas de Implementación:**
- Router `/api/v1/users`:
  - GET `/me`
  - PUT `/me`
  - PUT `/me/password`

**Validación:**
- Obtener perfil propio
- Actualizar perfil
- Cambiar password

**Resultado Esperado:**
- Endpoints de usuario funcionales
- Protección con autenticación
- Validación de ownership

---

### Bloque 8.3: Portfolios Endpoints

**Archivos:** `backend/app/api/v1/portfolios/router.py`

**Objetivo:**
Implementar endpoints CRUD de carteras.

**Tareas de Implementación:**
- Router `/api/v1/portfolios`:
  - GET `/`
  - POST `/`
  - GET `/{portfolio_id}`
  - PUT `/{portfolio_id}`
  - DELETE `/{portfolio_id}`
  - GET `/{portfolio_id}/positions`

**Validación:**
- Listar portfolios propios
- Crear portfolio
- Obtener detalle
- Actualizar y eliminar
- Ver posiciones

**Resultado Esperado:**
- Endpoints CRUD completos
- Validación de ownership
- Paginación básica

---

### Bloque 8.4: Operations Endpoints

**Archivos:** `backend/app/api/v1/operations/router.py`

**Objetivo:**
Implementar endpoints de operaciones.

**Tareas de Implementación:**
- Router `/api/v1/operations`:
  - GET `/`
  - POST `/`
  - PUT `/{operation_id}`
  - DELETE `/{operation_id}`

**Validación:**
- Listar operaciones con filtros
- Crear operación BUY
- Crear operación SELL
- Actualizar y eliminar

**Resultado Esperado:**
- Endpoints de operaciones funcionales
- Filtrado básico
- Validación de cantidad en SELL

---

### Bloque 8.5: Market Endpoints

**Archivos:** `backend/app/api/v1/market/router.py`

**Objetivo:**
Implementar endpoints de datos de mercado.

**Tareas de Implementación:**
- Router `/api/v1/market`:
  - GET `/quote/{symbol}`
  - GET `/historical/{symbol}`
  - GET `/assets/search`

**Validación:**
- Obtener cotización actual
- Consultar históricos
- Buscar activos

**Resultado Esperado:**
- Endpoints de mercado funcionales
- Sin autenticación requerida (públicos)
- Caché integrado

---

### Bloque 8.6: Main Application Setup

**Archivos:** `backend/main.py`

**Objetivo:**
Configurar aplicación FastAPI principal.

**Tareas de Implementación:**
- Crear instancia FastAPI
- Registrar todos los routers
- Registrar middleware
- Health check endpoint

**Validación:**
- GET /health funciona
- GET /docs muestra Swagger UI
- CORS funciona
- Error handling funciona

**Resultado Esperado:**
- Aplicación FastAPI completa
- Routers registrados
- Swagger UI funcional
- Middleware configurado

---

## FASE 9: Módulo de Análisis con IA

### Bloque 9.1: Data Processor - Indicadores Técnicos

**Archivos:** `ai_module/src/processors/technical_indicators.py`

**Objetivo:**
Implementar cálculo de indicadores técnicos básicos.

**Tareas de Implementación:**
- Clase **TechnicalIndicatorProcessor**:
  - `calculate_rsi(prices, period=14)`
  - `calculate_sma(prices, period=20)`
  - `calculate_volatility(prices)`
  - `identify_trend(prices)`

**Validación:**
- Calcular RSI con datos reales
- Calcular SMA
- Calcular volatilidad
- Identificar tendencia

**Resultado Esperado:**
- Cálculo de 4 indicadores básicos
- Uso de Pandas para eficiencia
- Validación de datos de entrada

---

### Bloque 9.2: Prompt Builder

**Archivos:** `ai_module/src/templates/prompt_builder.py`

**Objetivo:**
Construir prompts estructurados para OpenAI.

**Tareas de Implementación:**
- Clase **PromptBuilder**:
  - `build_portfolio_prompt(portfolio_data, technical_data)`
  - `build_asset_prompt(asset_data, technical_data)`
  - `include_disclaimer()`

**Validación:**
- Construir prompt de portfolio
- Construir prompt de activo
- Verificar inclusión de disclaimer

**Resultado Esperado:**
- Templates de prompts estructurados
- Disclaimer automático
- Formato optimizado para GPT-4

---

### Bloque 9.3: Analysis Generator

**Archivos:** `ai_module/src/analyzers/market_analyzer.py`

**Objetivo:**
Orquestar proceso completo de análisis.

**Tareas de Implementación:**
- Clase **MarketAnalyzer**:
  - `analyze_portfolio(portfolio_data)`
  - `analyze_asset(symbol)`
- Integración: datos → indicadores → prompt → OpenAI

**Validación:**
- Generar análisis completo de portfolio
- Generar análisis de activo
- Verificar flujo completo

**Resultado Esperado:**
- Orquestación del análisis funcional
- Integración con OpenAI
- Validación de outputs

---

### Bloque 9.4: Configuration del Módulo IA

**Archivos:** `ai_module/src/config.py`

**Objetivo:**
Configurar módulo IA.

**Tareas de Implementación:**
- Clase **AIModuleConfig**:
  - API keys
  - Parámetros de indicadores técnicos
  - Configuración de prompts

**Validación:**
- Cargar configuración
- Validar parámetros

**Resultado Esperado:**
- Configuración centralizada
- Parámetros ajustables
- Validación de API keys

---

## FASE 10: Testing Básico y Documentación

### Bloque 10.1: Tests Esenciales

**Archivos:** `backend/tests/`

**Objetivo:**
Implementar tests básicos para validar funcionalidad core.

**Tareas de Implementación:**
- Tests unitarios de modelos (crear, relaciones básicas)
- Tests unitarios de schemas (validación)
- Tests de servicios principales (AuthService, PortfolioService)
- Tests de endpoints principales (register, login, create portfolio)

**Validación:**
- Ejecutar suite de tests
- Verificar cobertura básica

**Resultado Esperado:**
- Suite de tests básica funcional
- Cobertura de funcionalidad core
- CI/CD preparado (opcional)

---

### Bloque 10.2: Documentación API

**Archivos:** `docs/API.md`

**Objetivo:**
Documentar API para uso y evaluación.

**Tareas de Implementación:**
- Documentar endpoints principales
- Incluir ejemplos de requests/responses
- Describir autenticación
- Casos de uso comunes

**Resultado Esperado:**
- Documentación clara y completa
- Ejemplos funcionales
- Swagger UI complementado

---

### Bloque 10.3: README del Backend

**Archivos:** `backend/README.md`

**Objetivo:**
Documentar setup y uso del backend.

**Tareas de Implementación:**
- Instrucciones de instalación
- Configuración de variables de entorno
- Cómo ejecutar migraciones
- Cómo correr el servidor
- Cómo ejecutar tests

**Resultado Esperado:**
- README completo y claro
- Instrucciones paso a paso
- Troubleshooting básico

---

## Notas Finales

Este plan de implementación está diseñado para un proyecto académico, priorizando el aprendizaje de patrones de arquitectura y buenas prácticas sobre optimizaciones de producción.

**Lo que incluimos:**
- Arquitectura en capas bien definida
- Patrones de diseño (Repository, Service)
- Validaciones y seguridad básica
- Integración con APIs externas
- Tests esenciales para validar funcionalidad

**Lo que NO incluimos (por ser proyecto académico):**
- Rate limiting avanzado
- Tests de carga y concurrencia
- Optimizaciones de producción
- Monitoreo y observabilidad
- Deployment en la nube
- Caching complejo multicapa

El objetivo es tener una aplicación funcional que demuestre comprensión de los conceptos de arquitectura de software, no una solución enterprise-ready.

# Plan de Implementación del Backend

## Introducción

Este documento describe el plan de implementación del backend de nuestra plataforma de gestión de carteras. Decidimos organizar el desarrollo en fases progresivas, comenzando con la configuración base y avanzando hasta la integración con servicios de inteligencia artificial. Esta aproximación incremental nos permite validar cada componente antes de continuar con el siguiente, reduciendo la complejidad y facilitando la identificación temprana de problemas.

El objetivo principal es construir una API REST funcional aplicando patrones de arquitectura de software que hemos estudiado. Cada fase introduce nuevos conceptos y componentes de manera estructurada, permitiendo que entendamos cómo se relacionan las diferentes partes del sistema antes de avanzar. Esta metodología nos ayuda a mantener un código organizado y mantenible, mientras aprendemos los principios de diseño que estamos aplicando.

---

## Instalación y Configuración de Base de Datos

Para configurar PostgreSQL y la base de datos del proyecto, sigue estos pasos. Asume que ya tienes Python y el entorno virtual configurados.

### 1. Instalar PostgreSQL
```bash
brew install postgresql
```

### 2. Iniciar PostgreSQL como Servicio
```bash
brew services start postgresql
```

### 3. Crear la Base de Datos
```bash
createdb portfolio_db
```

### 4. Configurar Variables de Entorno
Edita el archivo `config/.env` (o créalo si no existe) con la conexión a PostgreSQL y las API keys:
```
DATABASE_URL=postgresql://username:password@localhost:5432/portfolio_db
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
OPENAI_API_KEY=tu_api_key_aqui
```
Reemplaza `username` y `password` con tus credenciales de PostgreSQL (por defecto, username es tu usuario de macOS, password puede estar vacío inicialmente).

**Nota sobre API Keys:**
- ALPHA_VANTAGE_API_KEY: Obtén una clave gratuita en https://www.alphavantage.co/support/#api-key
- OPENAI_API_KEY: Obtén una clave en https://platform.openai.com/api-keys
- Ambas API keys son opcionales. Sin ellas, esas funcionalidades específicas no estarán disponibles pero el resto del sistema funcionará normalmente.

### 5. Ejecutar Migraciones con Alembic
```bash
cd backend
alembic upgrade head
```

### Verificación
- Para verificar que PostgreSQL esté corriendo: `brew services list`
- Para detener PostgreSQL: `brew services stop postgresql`
- Si hay errores de conexión, se debe revisar que la DATABASE_URL sea correcta y que la DB exista.

## Aclaraciones Críticas del Sistema

Al definir la arquitectura del sistema, tomamos decisiones importantes que afectan el diseño y la implementación. Documentamos estas decisiones aquí para mantener claridad sobre el alcance y las limitaciones del proyecto.

**Verificación de Email No Es Requisito para JWT**

Decidimos que la verificación de email no es un requisito obligatorio para la autenticación mediante JWT. Un usuario con `is_verified=false` puede hacer login y usar el sistema completo sin restricciones. Esta decisión la tomamos porque queremos que el sistema funcione de manera independiente sin depender de servicios externos de email, lo cual simplifica el desarrollo y las pruebas.

Los tokens de verificación existen en el modelo de datos para mantener la flexibilidad futura, pero no se utilizan si no hay servicio de email configurado. En desarrollo, podemos auto-verificar usuarios para facilitar las pruebas sin necesidad de configurar infraestructura de correo electrónico.

**Integraciones Externas**

Diseñamos el sistema para que las integraciones externas sean completamente opcionales, permitiendo que el núcleo funcional opere de manera independiente.

**Alpha Vantage:** Esta integración solo se utiliza para obtener precios de mercado automáticamente. Sin API key configurada, el usuario puede ingresar precios manualmente cuando registra operaciones. Esta flexibilidad nos permite desarrollar y probar el sistema sin depender de servicios externos, y también permite que usuarios sin acceso a la API puedan utilizar la plataforma.

**OpenAI:** Esta integración se utiliza exclusivamente para generar análisis con inteligencia artificial. Sin API key configurada, esa funcionalidad específica no está disponible, pero todas las demás características del sistema funcionan normalmente.

El núcleo del sistema (gestión de portfolios, registro de operaciones, cálculo de reportes y métricas financieras) funciona completamente sin estas integraciones. Esta arquitectura modular nos permite desarrollar y validar cada componente de manera independiente.

---

## Seguimiento de Implementación

Para mantener trazabilidad sobre el progreso del proyecto, decidimos documentar cada sesión de trabajo indicando los bloques completados, la fecha de implementación y observaciones relevantes. Esta práctica nos permite tener un registro claro de las decisiones tomadas y facilita la comprensión del proceso de desarrollo cuando revisamos el código posteriormente. Además, nos ayuda a identificar patrones en nuestro proceso de desarrollo y a entender por qué tomamos ciertas decisiones en momentos específicos del proyecto.

---

### DIA 7 DE NOVIEMBRE - 10:00 AM - BLOQUES 0.1 Y 0.2 COMPLETADOS

Bloques implementados:
- Bloque 0.1: Estructura de Directorios y Dependencias
- Bloque 0.2: Configuración Central con Variables de Entorno

Comentarios:
Iniciamos el desarrollo estableciendo los fundamentos del proyecto. Comenzamos configurando el archivo requirements.txt con todas las dependencias esenciales que necesitamos: FastAPI como framework web, SQLAlchemy para el ORM, Pydantic para validación de datos, Alembic para migraciones, y otras librerías necesarias para el funcionamiento completo del sistema.

Decidimos implementar un sistema de configuración centralizado usando Pydantic Settings porque nos permite gestionar variables de entorno de forma tipada y segura. Esta elección nos ayuda a detectar errores de configuración en tiempo de desarrollo en lugar de en tiempo de ejecución, y además proporciona validación automática de tipos.

Mantuvimos las API keys de OpenAI y Alpha Vantage como opcionales desde el inicio, dejándolas con valores vacíos que podemos rellenar más adelante cuando implementemos esas integraciones. Esta decisión nos permite desarrollar el núcleo del sistema sin depender de servicios externos, facilitando las pruebas y el desarrollo local. El archivo .env ya contiene la conexión a PostgreSQL configurada y funcionando, lo cual nos permitió avanzar rápidamente con la configuración de base de datos.

También actualizamos el .gitignore para asegurar que no subamos información sensible al repositorio. Esta es una práctica esencial de seguridad que implementamos desde el principio del proyecto. Todas las dependencias se instalaron sin conflictos en el entorno conda uie_arquitectura_software, lo que nos confirmó que nuestras elecciones de versiones eran compatibles.

Validaciones realizadas:
- Instalación de dependencias sin errores
- Verificación de imports: fastapi, sqlalchemy, pydantic
- Sin conflictos de versiones (pip check)
- Carga correcta de configuración desde .env

---

### DIA 7 DE NOVIEMBRE - 2:00 PM - BLOQUE 0.3 COMPLETADO

Bloque implementado:
- Bloque 0.3: Configuración de Motor de Base de Datos

Comentarios:
Implementamos el archivo session.py que maneja la conexión con PostgreSQL. Este archivo es fundamental porque define el engine de SQLAlchemy, la sesión de base de datos y la función get_db que usaremos en FastAPI para inyectar la sesión en los endpoints mediante dependency injection.

Configuramos el pool de conexiones con valores razonables para desarrollo: 5 conexiones base y hasta 10 adicionales. Elegimos estos valores porque son suficientes para desarrollo local sin sobrecargar la base de datos, y nos permiten escalar cuando sea necesario. También activamos pool_pre_ping que verifica las conexiones antes de usarlas para evitar errores con conexiones muertas que pueden ocurrir después de períodos de inactividad o problemas de red.

La función get_db usa el patrón de generador de Python para asegurar que la sesión siempre se cierre correctamente, incluso si hay errores durante el procesamiento de la request. Esta decisión previene fugas de conexiones que podrían agotar el pool y causar problemas de rendimiento o bloqueos en la aplicación.

Validaciones realizadas:
- Conexión correcta a PostgreSQL
- Pool de conexiones funcionando correctamente

---

### DIA 7 DE NOVIEMBRE - 3:00 PM - BLOQUES 1.1 A 1.5 COMPLETADOS

Bloques implementados:
- Bloque 1.1: Modelos de Usuario y Autenticación
- Bloque 1.2: Modelos de Portfolio y Posiciones
- Bloque 1.3: Modelo de Operaciones Financieras
- Bloque 1.4: Modelos de Activos y Precios
- Bloque 1.5: Modelos de Análisis con IA

Comentarios:
Dedicamos esta sesión a crear todos los modelos ORM que representan las entidades del dominio. Cada modelo hereda de Base para que SQLAlchemy los detecte automáticamente y pueda generar las migraciones correctamente.

En user.py creamos tres modelos: User, UserProfile y UserSession. Decidimos separar el perfil del usuario para mantener la tabla users liviana con solo lo esencial para autenticación, lo cual mejora el rendimiento de las consultas de login y permite que el perfil evolucione independientemente sin afectar la tabla principal. UserSession almacena los refresh tokens para que un usuario pueda tener múltiples sesiones activas en diferentes dispositivos, una funcionalidad esencial para la experiencia de usuario moderna.

En portfolio.py implementamos Portfolio y PortfolioAsset. Lo más importante aquí es que usamos el tipo Decimal para todos los valores monetarios porque float tiene problemas de precisión con decimales que pueden causar errores de redondeo en cálculos financieros. Esta decisión es crítica porque los errores de precisión en valores monetarios pueden acumularse y generar discrepancias significativas en los reportes. Un portfolio tiene métodos para calcular sus métricas financieras sumando el valor de todas sus posiciones, lo que nos permite mantener los datos normalizados y calcular métricas bajo demanda.

En operation.py creamos el modelo Operation que registra cada compra o venta. El total_amount se calcula diferente según el tipo: en compras sumamos fees porque representan un costo adicional que pagamos, en ventas los restamos porque representan un costo que reduce lo que recibimos. Esta diferenciación es importante para saber cuánto realmente pagamos o recibimos en cada operación, lo cual es esencial para calcular correctamente el costo promedio de las posiciones y las ganancias o pérdidas realizadas.

En asset.py definimos Asset (catálogo de activos disponibles) y AssetPrice (histórico de precios). AssetPrice usa la estructura OHLCV estándar (open, high, low, close, volume) que es el formato universal en análisis técnico financiero. Estos datos los usaremos después para calcular indicadores técnicos como RSI, medias móviles y volatilidad, que son necesarios para los análisis con IA.

En analysis.py creamos Analysis y AnalysisRequest. Analysis almacena el texto generado por la IA con un sistema de caché temporal (expires_at) para no regenerar el mismo análisis repetidamente y ahorrar costos de API. Esta decisión es importante porque las llamadas a OpenAI tienen costo, y regenerar análisis idénticos sería ineficiente. AnalysisRequest trackea quién solicitó qué análisis y si se completó o falló, lo que nos permite monitorear el uso del servicio y diagnosticar problemas.

Decisiones de diseño que tomamos:
- UUID como primary keys en lugar de integers secuenciales: Esta decisión mejora la seguridad al evitar que se puedan enumerar recursos, facilita la distribución de datos en sistemas distribuidos, y evita problemas de colisión cuando se integran datos de múltiples fuentes.
- Decimal para valores monetarios: Como mencionamos anteriormente, esto previene errores de precisión que son críticos en cálculos financieros.
- Timestamps automáticos en todos los modelos: Esto nos permite auditar cuándo se crearon y modificaron los registros sin tener que implementar esta lógica manualmente en cada operación.
- Cascade delete donde tiene sentido: Eliminar un usuario elimina sus portfolios y operaciones relacionadas, lo que mantiene la integridad referencial y simplifica la gestión de datos.
- Constraints a nivel de base de datos para integridad: Los constraints garantizan que los datos sean válidos incluso si hay errores en la lógica de aplicación, proporcionando una capa adicional de seguridad.

---

### DIA 7 DE NOVIEMBRE - 4:00 PM - BLOQUE 1.6 COMPLETADO

Bloque implementado:
- Bloque 1.6: Configuración de Migraciones con Alembic

Comentarios:
Inicializamos Alembic para gestionar las migraciones de base de datos de manera versionada y controlada. Configuramos el archivo env.py para que importe automáticamente todos nuestros modelos, esto es crítico para que Alembic pueda detectarlos y generar las migraciones correctamente. Sin esta configuración, tendríamos que especificar manualmente cada modelo en cada migración, lo cual sería propenso a errores.

Modificamos alembic.ini para comentar la línea de sqlalchemy.url porque en su lugar usamos la configuración desde settings.py. Esta decisión centraliza la configuración de base de datos en un solo lugar, lo que facilita el mantenimiento y evita inconsistencias entre diferentes partes del sistema. Además, nos permite usar variables de entorno de manera consistente en toda la aplicación.

Generamos la migración inicial con alembic revision --autogenerate y revisamos cuidadosamente el archivo generado para verificar que detectó todas las tablas, foreign keys y constraints. Esta revisión manual es importante porque Alembic puede tener limitaciones en algunos casos y necesitamos asegurarnos de que la migración refleje exactamente lo que queremos. Todo se veía correcto, lo que nos confirmó que nuestros modelos estaban bien definidos.

Aplicamos la migración con alembic upgrade head y verificamos en pgAdmin que todas las tablas se crearon correctamente con sus relaciones. Esta verificación visual nos ayudó a confirmar que las foreign keys, constraints y tipos de datos se aplicaron correctamente en la base de datos.

Validaciones realizadas:
- Migración generada detecta todas las tablas
- Upgrade correcto sin errores
- Todas las foreign keys y constraints creados correctamente
- Tablas visibles en PostgreSQL

---

### DIA 7 DE NOVIEMBRE - 5:00 PM - BLOQUES 2.1 A 2.6 COMPLETADOS

Bloques implementados:
- Bloque 2.1: Schemas de Autenticación
- Bloque 2.2: Schemas de Usuario
- Bloque 2.3: Schemas de Portfolio
- Bloque 2.4: Schemas de Operaciones
- Bloque 2.5: Schemas de Mercado
- Bloque 2.6: Schemas de Análisis

Comentarios:
Creamos todos los schemas Pydantic que usaremos para validar requests y serializar responses. Pydantic se encarga automáticamente de validar tipos y lanzar errores claros si algo está mal, lo que nos ahorra escribir código de validación manual y garantiza que los datos sean consistentes antes de llegar a la lógica de negocio.

En auth.py implementamos schemas para registro y login. Agregamos un validator custom para password que verifica que tenga al menos una mayúscula, una minúscula y un número. Decidimos no pedir símbolos especiales para no complicar innecesariamente la experiencia del usuario, ya que los requisitos que implementamos proporcionan un nivel de seguridad adecuado para un proyecto académico. El validator lanza errores descriptivos si la password no cumple, lo que ayuda a los usuarios a entender qué deben corregir.

En user.py creamos schemas que nunca exponen el password_hash por seguridad. Esta es una práctica esencial que implementamos desde el principio para evitar que información sensible se filtre en las respuestas de la API. UserProfileResponse incluye datos anidados del perfil para evitar hacer múltiples requests cuando el cliente necesita información completa del usuario. UserUpdate tiene todos los campos opcionales porque usamos semántica PATCH (solo actualizar lo que se envía), lo que permite actualizaciones parciales sin necesidad de enviar todos los campos.

En portfolio.py los schemas incluyen campos calculados como gain_loss y gain_loss_percent que se derivan de otros valores. Estos campos calculados simplifican la lógica del cliente al evitar que tenga que calcular estas métricas manualmente. PortfolioDetailResponse tiene una lista anidada de posiciones para retornar todo el portfolio con sus assets en una sola response, reduciendo el número de requests necesarios y mejorando el rendimiento.

En operation.py agregamos validators para asegurar que quantity y price sean siempre positivos. Esta validación previene errores lógicos que podrían causar problemas en los cálculos financieros. OperationFilter tiene todos los campos opcionales para permitir filtrar por cualquier combinación de criterios, lo que proporciona flexibilidad en las consultas sin necesidad de crear múltiples endpoints especializados.

En market.py definimos la estructura OHLCV en PricePoint que coincide con lo que retornan las APIs de mercado. Esta estandarización facilita la integración con diferentes proveedores de datos financieros y mantiene consistencia en todo el sistema.

En analysis.py implementamos un validator que verifica que la solicitud tenga portfolio_id O asset_symbol pero no ambos. Esta validación asegura que el tipo de análisis sea consistente con los datos proporcionados y previene ambigüedades que podrían llevar a generar análisis incorrectos o confusos.

---

### DIA 7 DE NOVIEMBRE - 6:00 PM - BLOQUES 3.1 A 3.3 COMPLETADOS

Bloques implementados:
- Bloque 3.1: Password Hasher con Bcrypt
- Bloque 3.2: JWT Handler para Tokens
- Bloque 3.3: Generador de Tokens de Verificación

Comentarios:
Implementamos los componentes de seguridad que manejarán autenticación y encriptación. Estas son las bases de seguridad del sistema y decidimos implementarlas cuidadosamente desde el principio.

En password.py creamos PasswordHasher que usa bcrypt con cost factor 12. Elegimos bcrypt porque es el estándar de la industria para passwords: genera un salt aleatorio automáticamente para cada password, es resistente a ataques de fuerza bruta, y está ampliamente probado en producción. El cost factor 12 es un buen balance entre seguridad y performance para nuestro caso académico: proporciona seguridad adecuada sin hacer que las operaciones de hash sean demasiado lentas durante el desarrollo y las pruebas.

En jwt.py implementamos JWTHandler para crear y validar tokens JWT. Decidimos usar access tokens de 30 minutos y refresh tokens de 7 días. Los access tokens son cortos para limitar el tiempo de exposición si alguien los roba, minimizando el daño potencial. Los refresh tokens duran más para que el usuario no tenga que hacer login constantemente, mejorando la experiencia de usuario. Usamos el algoritmo HS256 que es estándar y suficientemente seguro para nuestras necesidades, además de ser ampliamente soportado y fácil de implementar.

En tokens.py creamos funciones para generar tokens aleatorios url-safe usando el módulo secrets de Python que es criptográficamente seguro. Esta elección es importante porque los generadores pseudoaleatorios estándar no son adecuados para propósitos de seguridad. Estos tokens se usan para verificación de email y reset de password. Definimos TTLs de 48 horas para verificación de email (más largo porque no es crítico) y 1 hora para reset de password (más corto por seguridad, ya que comprometer una cuenta es más grave). Estos tiempos de expiración balancean seguridad y usabilidad.

---

### DIA 7 DE NOVIEMBRE - 7:00 PM - BLOQUES 4.1 A 4.6 COMPLETADOS

Bloques implementados:
- Bloque 4.1: Base Repository Genérico
- Bloque 4.2: UserRepository
- Bloque 4.3: PortfolioRepository
- Bloque 4.4: OperationRepository
- Bloque 4.5: AssetRepository
- Bloque 4.6: AnalysisRepository

Comentarios:
Implementamos el patrón repository para separar la lógica de acceso a datos de la lógica de negocio. Esta separación hace el código más testeable y mantenible, ya que podemos mockear los repositorios en las pruebas y cambiar la implementación de acceso a datos sin afectar la lógica de negocio.

En base.py creamos BaseRepository genérico usando TypeVar. Este repositorio tiene los métodos CRUD básicos que todos los modelos necesitan: create, get_by_id, update, delete, etc. Los repositorios específicos heredan de esta clase y agregan métodos propios de su dominio. Esta abstracción evita repetir código y garantiza consistencia en las operaciones básicas de todos los repositorios.

En user.py agregamos métodos específicos como get_by_email con búsqueda case-insensitive (importante para la experiencia de usuario), create_with_profile que crea usuario y perfil en una transacción atómica (garantiza consistencia de datos), y métodos para gestionar sesiones de usuario que nos permiten rastrear y controlar las sesiones activas.

En portfolio.py implementamos métodos para crear o actualizar posiciones usando el patrón upsert, que simplifica la lógica cuando no sabemos si una posición ya existe. También implementamos métodos para cargar portfolios con sus posiciones en una sola query usando eager loading, lo que evita el problema n+1 y mejora significativamente el rendimiento cuando necesitamos datos relacionados.

En operation.py implementamos filtrado multi-criterio para que se puedan buscar operaciones por portfolio, asset, tipo, rango de fechas o cualquier combinación. Esta flexibilidad permite consultas complejas sin necesidad de crear múltiples métodos especializados, simplificando la API del repositorio.

En asset.py agregamos search_assets para búsqueda fuzzy por símbolo o nombre, lo que mejora la experiencia de usuario al permitir encontrar activos incluso con errores de tipeo. También implementamos get_or_create que es útil para no duplicar activos cuando se opera un símbolo por primera vez, manteniendo la integridad del catálogo.

En analysis.py implementamos get_cached_analysis que busca análisis no expirados para evitar regenerarlos, lo que reduce costos de API y mejora el rendimiento. También agregamos métodos para trackear el estado de las solicitudes de análisis, lo que nos permite monitorear el proceso y diagnosticar problemas.

Todos los repositorios manejan transacciones y hacen rollback automático si hay errores, garantizando la integridad de los datos incluso cuando ocurren excepciones inesperadas.

---

### DIA 5 DE DICIEMBRE - SESIÓN 1 - BLOQUES 6.1, 6.2, 6.3 Y 7.1, 7.2 COMPLETADOS

Bloques implementados:
- Bloque 6.1: AuthService
- Bloque 6.2: PortfolioService (ya existía, se verificó)
- Bloque 6.3: OperationService
- Bloque 7.1: Authentication Middleware (Dependencies)
- Bloque 7.2: Error Handling Middleware

Comentarios:
En esta sesión completamos la capa de servicios faltante y el middleware de autenticación. Decidimos dejar las integraciones externas (Alpha Vantage, OpenAI) para el final, enfocándonos primero en tener el backend completamente funcional.

**AuthService (auth_service.py):**
Implementamos el servicio de autenticación que coordina todo el flujo de auth. Los métodos principales son:
- `register()`: crea usuario con perfil, validando email único y hasheando password
- `authenticate()`: valida credenciales sin generar tokens
- `login()`: autenticación completa con generación de tokens JWT y creación de sesión en BD
- `refresh_tokens()`: renueva tokens validando la sesión en BD
- `logout()` y `logout_all()`: invalidan sesiones
- `get_user_from_token()`: extrae usuario de un access token (usado por middleware)
- `change_password()`: cambia password invalidando todas las sesiones por seguridad

Decidimos que al cambiar password se invaliden todas las sesiones activas como medida de seguridad. Esto protege al usuario en caso de que su password haya sido comprometida.

**OperationService (operation_service.py):**
Este servicio complementa a PortfolioService con funcionalidades de consulta y estadísticas. La creación de operaciones sigue en PortfolioService porque necesita actualizar posiciones en la misma transacción. OperationService provee:
- Métodos de filtrado por asset, tipo, rango de fechas
- `get_portfolio_statistics()`: estadísticas agregadas (total compras, ventas, fees, etc.)
- `get_asset_statistics()`: estadísticas por activo individual

**Middleware de Autenticación (dependencies.py):**
Usamos el patrón de dependencias de FastAPI en lugar de middleware tradicional porque es más flexible y testeable. Implementamos:
- `get_db()`: inyecta sesión de BD con cleanup automático
- `get_current_user()`: extrae y valida usuario del JWT, lanza 401 si inválido
- `get_current_active_user()`: extiende anterior verificando is_active, lanza 403 si desactivado
- `get_optional_user()`: retorna usuario o None, útil para endpoints que funcionan con y sin auth

Usamos HTTPBearer de FastAPI que automáticamente muestra el botón de autorización en Swagger UI.

**Error Handler (error_handler.py):**
Definimos una jerarquía de excepciones de dominio para separar lógica de negocio de detalles HTTP:
- `AppException`: base para todas las excepciones
- `NotFoundError`, `AlreadyExistsError`, `ValidationError`: errores comunes
- `AuthenticationError`, `AuthorizationError`: errores de auth
- `BusinessRuleError`, `InsufficientFundsError`: errores de reglas de negocio

Cada excepción tiene su status code apropiado. Los handlers convierten estas excepciones en respuestas JSON estandarizadas.

Validaciones realizadas:
- Estructura de servicios coherente con repositorios
- Dependencies usan correctamente el patrón generator
- Excepciones cubren casos de uso principales

---

### DIA 5 DE DICIEMBRE - SESIÓN 2 - BLOQUES 8.1 A 8.6 COMPLETADOS

Bloques implementados:
- Bloque 8.1: Auth Endpoints
- Bloque 8.2: Users Endpoints
- Bloque 8.3: Portfolios Endpoints
- Bloque 8.4: Operations Endpoints
- Bloque 8.6: Main Application Setup

Comentarios:
Completamos toda la capa de API REST con endpoints funcionales para cada dominio.

**Auth Endpoints (/api/v1/auth/):**
- `POST /register`: registra usuario, retorna datos sin password
- `POST /login`: autentica y retorna tokens JWT
- `POST /refresh`: renueva access token con refresh token
- `POST /logout`: invalida sesión actual (requiere auth)
- `POST /logout-all`: invalida todas las sesiones (requiere auth)

Todos los endpoints usan los schemas de Pydantic para validación automática.

**Users Endpoints (/api/v1/users/):**
- `GET /me`: obtiene perfil del usuario autenticado
- `PUT /me`: actualiza perfil (semántica PATCH)
- `PUT /me/password`: cambia password verificando la actual

Estos endpoints solo permiten operar sobre el propio usuario, nunca sobre otros.

**Portfolios Endpoints (/api/v1/portfolios/):**
- `GET /`: lista portfolios del usuario
- `POST /`: crea portfolio nuevo
- `GET /{id}`: obtiene portfolio con posiciones (valida ownership)
- `PUT /{id}`: actualiza nombre/descripción
- `DELETE /{id}`: elimina portfolio y posiciones

Implementamos validación de ownership en cada operación que accede a un portfolio específico.

**Operations Endpoints (/api/v1/operations/):**
- `GET /`: lista operaciones con filtros (asset, tipo, fechas)
- `POST /`: crea operación BUY o SELL
- `GET /stats/{portfolio_id}`: estadísticas del portfolio
- `GET /{id}`: detalle de operación
- `PUT /{id}`: actualiza notas (valores financieros inmutables)

Para SELL validamos que haya cantidad suficiente. Los valores financieros no se pueden modificar después de crear la operación para mantener integridad del historial.

**Main Application (main.py):**
Configuramos la aplicación FastAPI completa con:
- Metadatos para documentación OpenAPI
- CORS configurado desde settings
- Exception handlers registrados
- Todos los routers incluidos bajo /api/v1
- Endpoints de health check (/, /health, /health/db)
- Eventos de startup/shutdown para logging

El script anterior de pruebas se renombró a test_services.py para conservarlo.

**Estructura de routers:**
Organizamos la API en un router principal (api_router) que agrupa todos los sub-routers:
```
/api/v1/
  /auth/      (autenticación)
  /users/     (gestión de usuario)
  /portfolios/ (carteras)
  /operations/ (operaciones)
```

Validaciones realizadas:
- Endpoints siguen convenciones REST
- Validación de ownership en todas las operaciones
- Schemas de response correctamente definidos
- Documentación OpenAPI generada automáticamente

---

### DIA 5 DE DICIEMBRE - SESIÓN 3 - BLOQUE 8.5 COMPLETADO (MARKET ENDPOINTS)

Bloque implementado:
- Bloque 8.5: Market Endpoints

Comentarios:
Completamos la última pieza faltante de la capa de API: los endpoints de datos de mercado. Estos endpoints proporcionan acceso al catálogo de activos financieros y sus precios, sentando las bases para la futura integración con Alpha Vantage.

**Market Endpoints (/api/v1/market/):**

Implementamos cuatro endpoints principales para gestión de activos y precios:

- `GET /assets/search?q=<query>`: Búsqueda fuzzy de activos por símbolo o nombre. Este endpoint es fundamental para la experiencia de usuario ya que permite encontrar activos incluso cuando no se conoce el símbolo exacto. La búsqueda es case-insensitive y soporta coincidencias parciales tanto en símbolo como en nombre.

- `GET /assets/{symbol}`: Obtiene información detallada de un activo específico incluyendo tipo (STOCK, ETF, CRYPTO), moneda, exchange y descripción. Este endpoint es útil para mostrar detalles del activo antes de realizar operaciones.

- `GET /prices/{symbol}/current`: Retorna el precio actual de un activo. Actualmente obtiene el último precio almacenado en la base de datos; cuando se integre Alpha Vantage en la Fase 5, este endpoint consultará precios en tiempo real.

- `GET /prices/{symbol}/historical?days=30`: Obtiene precios históricos en formato OHLCV (Open, High, Low, Close, Volume). Estos datos son esenciales para el módulo de IA que calculará indicadores técnicos como RSI, SMA y volatilidad.

- `POST /assets`: Endpoint para crear activos en el catálogo. Aunque los activos normalmente se crean automáticamente cuando un usuario registra una operación con un símbolo nuevo, este endpoint permite poblar el catálogo inicial o agregar activos manualmente.

**Decisiones de diseño:**

1. **Endpoints públicos**: A diferencia de otros endpoints, los de mercado no requieren autenticación porque la información de precios y activos es pública. Decidimos incluir `get_optional_user` para poder personalizar respuestas en el futuro si el usuario está autenticado.

2. **Preparación para Alpha Vantage**: Los endpoints están diseñados para ser compatibles con la estructura de datos que retornará Alpha Vantage. Cuando implementemos la integración, solo necesitaremos agregar la lógica de consulta externa sin cambiar la interfaz de la API.

3. **Manejo de datos faltantes**: Los endpoints de precios manejan graciosamente el caso donde no hay datos disponibles, retornando mensajes claros que indican que los precios se actualizarán cuando se configure Alpha Vantage.

**Estructura de routers actualizada:**
```
/api/v1/
  /auth/       (autenticación)
  /users/      (gestión de usuario)
  /portfolios/ (carteras)
  /operations/ (operaciones)
  /market/     (datos de mercado) ← NUEVO
```

Validaciones realizadas:
- Todos los routers se cargan correctamente
- Endpoints de búsqueda funcionan con queries case-insensitive
- Schemas de respuesta siguen estructura OHLCV estándar
- Documentación OpenAPI actualizada automáticamente

Con esta sesión completamos al 100% las Fases 6 (Servicios), 7 (Middleware) y 8 (API Endpoints). El backend está completamente funcional y listo para las integraciones externas de la Fase 5 (Alpha Vantage, OpenAI).

---

### DIA 5 DE DICIEMBRE - SESIÓN 2 - INTEGRACIONES EXTERNAS COMPLETADAS

**Bloques implementados:**
- Fase 5: Integraciones Externas (Alpha Vantage)
- Fase 9: Módulo de IA (OpenAI)

**Comentarios:**

En esta sesión implementamos las integraciones externas con Alpha Vantage y OpenAI, completando las funcionalidades de datos de mercado en tiempo real y análisis con inteligencia artificial.

**Cliente Alpha Vantage (alpha_vantage_client.py):**
Implementamos un cliente robusto para interactuar con la API de Alpha Vantage que proporciona:
- `get_quote()`: obtiene cotización actual con precio, volumen, cambio porcentual
- `get_daily_prices()`: descarga datos históricos OHLCV (open, high, low, close, volume)
- `search_symbol()`: busca activos por keywords

El cliente maneja automáticamente los errores de API, rate limiting y formatea las respuestas al formato esperado. Usa httpx para requests con timeout configurado (10 segundos). Implementamos context manager support para manejo limpio de conexiones, lo que garantiza que los recursos se liberen adecuadamente después de cada uso.

**Servicio de Datos de Mercado (market_service.py):**
Este servicio coordina la obtención y cache de datos financieros:
- `get_current_price()`: cachea precios por 5 minutos para optimizar requests a Alpha Vantage
- `get_historical_prices()`: consulta y almacena datos históricos en BD para análisis posterior
- `search_assets()`: busca primero en catálogo local, luego en Alpha Vantage
- `update_portfolio_prices()`: actualiza todos los precios de un portfolio automáticamente

El servicio implementa una estrategia de cache inteligente: primero verifica datos locales recientes, solo consulta API externa si es necesario. Esto respeta los límites del free tier de Alpha Vantage (25 requests por día con máximo de 5 requests por minuto), evitando exceder cuotas y garantizando disponibilidad continua del servicio.

**Procesador de Indicadores Técnicos (technical_indicators.py):**
Implementamos cálculo de indicadores estándar usando pandas-ta (biblioteca especializada en análisis técnico financiero):
- RSI (Relative Strength Index): detecta condiciones de sobrecompra/sobreventa con período de 14 días
- MACD (Moving Average Convergence Divergence): identifica momentum y señales de trading
- Medias Móviles (SMA): períodos estándar de 20, 50 y 200 días para análisis de tendencias
- Volatilidad: desviación estándar anualizada de retornos logarítmicos
- Bandas de Bollinger: banda superior, media e inferior con 2 desviaciones estándar
- Análisis de tendencia: clasifica como alcista, bajista o lateral basándose en las medias móviles

Cada indicador incluye documentación completa explicando su interpretación y uso en análisis técnico. El procesador maneja automáticamente casos donde no hay suficientes datos históricos para calcular ciertos indicadores.

**Cliente OpenAI (openai_client.py):**
Implementamos cliente para generar análisis descriptivos usando gpt-5-mini:
- `generate_analysis()`: método genérico para generación usando OpenAI Responses API
- Sistema de extracción robusto que maneja diferentes tipos de respuesta (reasoning, message)
- Validación de disponibilidad del cliente antes de cada operación

El cliente usa exclusivamente gpt-5-mini con máximo de 5000 tokens de salida. Todos los análisis incluyen system prompt que instruye al modelo a ser descriptivo (no prescriptivo) y siempre incluir disclaimers. La extracción de texto de las respuestas maneja múltiples formatos de contenido para garantizar robustez.

**Servicio de Análisis con IA (analysis_service.py):**
Coordina el flujo completo de generación de análisis:
- `generate_asset_analysis()`: obtiene datos históricos, calcula indicadores, genera análisis con IA
- `generate_portfolio_analysis()`: actualiza precios, prepara datos, genera análisis de portfolio
- `get_analysis_history()`: recupera análisis previos del usuario
- Validación de ownership antes de generar análisis de portfolios

Los análisis se almacenan en base de datos con timestamps para mantener historial completo. Cada solicitud se trackea en la tabla analysis_requests con estados (processing, completed, failed), lo que permite monitorear el proceso y diagnosticar fallos. El sistema verifica disponibilidad de datos históricos suficientes antes de generar análisis técnicos.

**Nuevos Endpoints de Análisis (analysis/router.py):**
- `POST /analysis/asset/{symbol}`: genera análisis técnico de activo
- `POST /analysis/portfolio/{portfolio_id}`: genera análisis de portfolio
- `GET /analysis/history`: obtiene historial de análisis
- `DELETE /analysis/cache/*`: invalida cache para regenerar

**Actualización de Endpoints de Mercado:**
Integramos MarketDataService en los endpoints existentes:
- `/market/assets/search`: ahora busca en Alpha Vantage si no hay resultados locales
- `/market/prices/{symbol}/current`: consulta precio actual en tiempo real
- `/market/prices/{symbol}/historical`: descarga y cachea datos históricos

**Decisiones de diseño importantes:**

1. **Cache en base de datos**: Implementamos almacenamiento de datos históricos en PostgreSQL para minimizar llamadas a APIs externas y respetar rate limits. Los precios y datos históricos se consultan primero localmente antes de hacer requests a Alpha Vantage, optimizando el uso de la cuota gratuita.

2. **Manejo de errores robusto**: Los clientes manejan graciosamente errores de API (rate limit, autenticación, timeout). El sistema incluye logging detallado de todos los errores para facilitar diagnóstico y monitoreo.

3. **Indicadores técnicos estándar**: Usamos fórmulas y períodos estándar de la industria (RSI 14, SMA 20/50/200) para compatibilidad con análisis técnico tradicional. La biblioteca pandas-ta garantiza cálculos precisos y consistentes.

4. **Prompts estructurados**: El servicio de análisis construye prompts con contexto completo (indicadores, precios, métricas) de forma organizada. Los datos se formatean claramente para que el modelo GPT pueda interpretarlos correctamente.

5. **Disclaimers automáticos**: El system prompt instruye al modelo a ser objetivo y descriptivo, nunca prescriptivo. Los análisis generados incluyen disclaimers indicando que no constituyen consejo financiero.

6. **Arquitectura modular**: Las integraciones son completamente opcionales. Sin API keys, esas funcionalidades no están disponibles pero el resto del sistema funciona normalmente.

Validaciones realizadas:
- Cliente Alpha Vantage obtiene correctamente cotizaciones, datos históricos y búsqueda de símbolos
- Procesador de indicadores técnicos calcula RSI, MACD, medias móviles con valores correctos
- Cliente OpenAI genera análisis usando Responses API con extracción robusta de texto
- Endpoints de análisis retornan respuestas en formato JSON correcto con estados apropiados
- Sistema funciona correctamente sin API keys (funcionalidades limitadas) y con API keys configuradas
- Manejo de errores funciona adecuadamente ante fallos de APIs externas

---

## Conclusiones

A lo largo del desarrollo de esta plataforma de gestión de carteras y análisis de mercado, hemos construido un sistema completo que integra múltiples componentes y servicios externos. El proceso de implementación incremental nos permitió validar cada pieza antes de continuar, lo cual fue fundamental para mantener la calidad y coherencia del código mientras aprendíamos los patrones arquitectónicos que estábamos aplicando.

### Logros Principales

Hemos logrado implementar exitosamente todas las fases planificadas del backend. El sistema cuenta con una arquitectura robusta que separa claramente las responsabilidades entre capas: modelos de datos, repositorios para acceso a datos, servicios para lógica de negocio, y endpoints para la interfaz REST. Esta separación nos ha permitido mantener un código organizado y testeable, facilitando el mantenimiento y la evolución futura del sistema.

La implementación de autenticación mediante JWT nos proporcionó una solución segura y escalable para gestionar sesiones de usuario. El uso de refresh tokens y la invalidación de sesiones al cambiar contraseñas nos permitió implementar prácticas de seguridad adecuadas para un sistema que maneja información financiera sensible.

Las integraciones externas con Alpha Vantage y OpenAI se diseñaron como módulos completamente opcionales, lo que nos permitió desarrollar y probar el núcleo del sistema sin depender de servicios externos. Esta decisión arquitectónica resultó ser fundamental porque nos permitió avanzar en el desarrollo mientras gestionábamos el acceso a las API keys, y además hace que el sistema sea más resiliente ante fallos de servicios externos.

### Aprendizajes Arquitectónicos

El patrón Repository que implementamos nos demostró la importancia de abstraer el acceso a datos. Esta abstracción no solo hizo el código más testeable, sino que también nos permitió cambiar detalles de implementación sin afectar la lógica de negocio. El BaseRepository genérico que creamos evitó repetición de código y garantizó consistencia en las operaciones CRUD básicas.

La separación entre schemas Pydantic para validación y modelos SQLAlchemy para persistencia nos enseñó la importancia de mantener capas de abstracción claras. Los schemas nos permiten validar datos de entrada y formatear respuestas sin exponer detalles internos de la base de datos, mejorando tanto la seguridad como la flexibilidad de la API.

El uso de dependency injection en FastAPI mediante las funciones `get_db()` y `get_current_user()` nos mostró cómo los frameworks modernos facilitan la gestión de dependencias y el ciclo de vida de objetos. Esta aproximación hizo el código más limpio y testeable que si hubiéramos usado variables globales o singletons.

### Decisiones de Diseño Destacadas

La decisión de usar Decimal en lugar de float para valores monetarios fue crítica para mantener precisión en los cálculos financieros. Este aprendizaje nos recordó la importancia de entender las limitaciones de los tipos de datos cuando trabajamos con información que requiere precisión exacta.

El sistema de almacenamiento de datos históricos en base de datos que implementamos nos demostró cómo optimizar el uso de servicios externos respetando rate limits. Este patrón de consultar primero localmente antes de hacer requests externos es aplicable a muchos otros escenarios donde necesitamos balancear frescura de datos con eficiencia y costos.

La arquitectura modular que diseñamos, donde las integraciones externas son opcionales, nos permitió construir un sistema que funciona completamente sin ellas. Esta flexibilidad es valiosa tanto para desarrollo como para despliegues en entornos donde ciertos servicios no están disponibles.

### Consideraciones para el Futuro

El sistema está preparado para evolucionar en varias direcciones. La estructura de análisis con IA puede extenderse para incluir más tipos de análisis o diferentes modelos de lenguaje. El módulo de indicadores técnicos puede expandirse con nuevos indicadores o estrategias de trading más complejas.

La integración con Alpha Vantage puede complementarse con otros proveedores de datos financieros para aumentar la cobertura de mercados o mejorar la disponibilidad. La arquitectura actual facilita esta extensión mediante la abstracción del servicio de datos de mercado.

Para un entorno de producción, consideraríamos implementar más funcionalidades de seguridad como rate limiting por usuario, auditoría completa de operaciones, y backups automáticos de la base de datos. También podríamos agregar funcionalidades de colaboración como compartir portfolios entre usuarios o crear análisis comparativos entre diferentes carteras.

El sistema de notificaciones podría extenderse para alertar a usuarios sobre cambios significativos en sus posiciones o cuando se generen nuevos análisis. La infraestructura actual ya soporta estas extensiones gracias a la separación de responsabilidades que implementamos.

### Reflexión Final

Este proyecto nos ha permitido aplicar los conceptos teóricos de arquitectura de software en un contexto práctico y real. La metodología incremental que seguimos nos demostró la importancia de validar decisiones arquitectónicas temprano y ajustar el diseño cuando era necesario. La documentación detallada que mantuvimos durante el desarrollo nos ayudó a recordar las razones detrás de cada decisión y facilita el mantenimiento futuro.

La plataforma resultante demuestra cómo los patrones arquitectónicos bien aplicados pueden resultar en un sistema mantenible, extensible y robusto. Cada componente fue diseñado pensando no solo en su funcionalidad inmediata, sino también en cómo interactúa con el resto del sistema y cómo puede evolucionar en el futuro. Esta perspectiva holística es esencial para construir software que perdure y siga siendo útil a medida que los requisitos cambian.


# Plan de Implementación del Backend

## Introducción

Este documento describe el plan de implementación del backend de nuestra plataforma de gestión de carteras. Decidimos organizar el desarrollo en fases progresivas, comenzando con la configuración base y avanzando hasta la integración con servicios de inteligencia artificial. Esta aproximación incremental nos permite validar cada componente antes de continuar con el siguiente, reduciendo la complejidad y facilitando la identificación temprana de problemas.

El objetivo principal es construir una API REST funcional aplicando patrones de arquitectura de software que hemos estudiado. Cada fase introduce nuevos conceptos y componentes de manera estructurada, permitiendo que entendamos cómo se relacionan las diferentes partes del sistema antes de avanzar. Esta metodología nos ayuda a mantener un código organizado y mantenible, mientras aprendemos los principios de diseño que estamos aplicando.

---

## Aclaraciones Críticas del Sistema

Al definir la arquitectura del sistema, tomamos decisiones importantes que afectan el diseño y la implementación. Documentamos estas decisiones aquí para mantener claridad sobre el alcance y las limitaciones del proyecto.

**Verificación de Email No Es Requisito para JWT**

Decidimos que la verificación de email no es un requisito obligatorio para la autenticación mediante JWT. Un usuario con `is_verified=false` puede hacer login y usar el sistema completo sin restricciones. Esta decisión la tomamos porque queremos que el sistema funcione de manera independiente sin depender de servicios externos de email, lo cual simplifica el desarrollo y las pruebas.

Los tokens de verificación existen en el modelo de datos para mantener la flexibilidad futura, pero no se utilizan si no hay servicio de email configurado. En desarrollo, podemos auto-verificar usuarios para facilitar las pruebas sin necesidad de configurar infraestructura de correo electrónico.

**Integraciones Externas Opcionales**

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
- Conexión exitosa a PostgreSQL
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
- Upgrade exitoso sin errores
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
Implementar handler para creación y validación de tokens JWT. Este componente es fundamental para la autenticación stateless que permite escalar la aplicación sin necesidad de sesiones en servidor.

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
- Access tokens (30 minutos) y refresh tokens (7 días)

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

Este plan de implementación está diseñado específicamente para un proyecto académico, donde priorizamos el aprendizaje de patrones de arquitectura y buenas prácticas sobre optimizaciones de producción. Esta decisión nos permite enfocarnos en entender los principios fundamentales sin la complejidad adicional que requeriría un sistema en producción real.

**Lo que incluimos:**

Decidimos incluir estos elementos porque son esenciales para demostrar comprensión de arquitectura de software:
- Arquitectura en capas bien definida: Esta separación nos ayuda a entender cómo organizar código de manera mantenible y escalable.
- Patrones de diseño (Repository, Service): Estos patrones son fundamentales en el desarrollo de software y queremos demostrar que entendemos cuándo y cómo aplicarlos.
- Validaciones y seguridad básica: Aunque no implementamos seguridad de nivel enterprise, incluimos las prácticas esenciales como hashing de passwords y autenticación JWT.
- Integración con APIs externas: Esto nos permite demostrar cómo diseñar sistemas que interactúan con servicios externos de manera resiliente.
- Tests esenciales para validar funcionalidad: Los tests nos ayudan a validar que nuestro código funciona correctamente y demuestran que entendemos la importancia de la calidad del software.

**Lo que NO incluimos (por ser proyecto académico):**

Decidimos conscientemente excluir estos elementos porque agregarían complejidad sin contribuir significativamente a nuestros objetivos de aprendizaje:
- Rate limiting avanzado: Aunque es importante en producción, no es esencial para demostrar comprensión de arquitectura.
- Tests de carga y concurrencia: Estos requieren infraestructura adicional y tiempo que preferimos invertir en entender los patrones fundamentales.
- Optimizaciones de producción: Las optimizaciones prematuras pueden complicar el código sin beneficio educativo claro.
- Monitoreo y observabilidad: Aunque importante, no es crítico para un proyecto académico que se ejecuta localmente.
- Deployment en la nube: Esto agregaría complejidad de infraestructura que está fuera del alcance de nuestro objetivo principal.
- Caching complejo multicapa: El caching básico que implementamos es suficiente para demostrar el concepto sin la complejidad adicional.

El objetivo final es tener una aplicación funcional que demuestre comprensión de los conceptos de arquitectura de software, no una solución enterprise-ready. Esta claridad de objetivos nos permite mantener el foco en el aprendizaje sin distraernos con optimizaciones que, aunque valiosas, no son esenciales para nuestro propósito educativo.

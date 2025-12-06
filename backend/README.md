# Backend - Portfolio & Market Insight Platform

## Descripción General

El backend de la Portfolio & Market Insight Platform es una API REST construida con FastAPI que implementa un sistema completo para la gestión de carteras de inversión, análisis de mercado en tiempo real e inteligencia artificial aplicada a finanzas. El sistema integra datos de mercado mediante Alpha Vantage API y capacidades de análisis avanzado con GPT-5-mini, proporcionando una plataforma robusta para la toma de decisiones financieras informadas.

## Stack Tecnológico

El proyecto utiliza las siguientes tecnologías principales:

- **Framework Web**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+
- **Base de Datos**: PostgreSQL 14+
- **Validación**: Pydantic 2.0+
- **Autenticación**: JWT con python-jose
- **Migraciones**: Alembic
- **Cliente HTTP**: httpx
- **Análisis Técnico**: pandas-ta

## Arquitectura del Sistema

### Principios Arquitectónicos

La arquitectura del backend sigue los principios de Clean Architecture y Domain-Driven Design (DDD), implementando una clara separación de responsabilidades mediante capas independientes. Este enfoque permite que cada capa tenga una responsabilidad específica y bien definida, facilitando el mantenimiento, la extensibilidad y las pruebas del sistema.

El principio de inversión de dependencias se aplica sistemáticamente: las capas superiores no dependen directamente de implementaciones concretas de las capas inferiores, sino de abstracciones. Los servicios dependen de interfaces de repositorio en lugar de implementaciones específicas, lo que permite reemplazar componentes sin afectar la lógica de negocio y facilita la creación de pruebas mediante el uso de mocks.

La validación de datos se realiza de forma exhaustiva mediante Pydantic, garantizando que todos los datos que entran y salen del sistema cumplan con las reglas de negocio definidas. Este enfoque proporciona seguridad de tipos en tiempo de ejecución y documentación automática de la API.

### Estructura de Capas

El sistema se organiza en cuatro capas principales:

#### Capa de Presentación (API)

Ubicada en `app/api/`, esta capa maneja todas las interacciones HTTP con los clientes. Los endpoints están organizados por dominio de negocio y versionados para permitir evolución de la API sin romper compatibilidad. La capa incluye:

- Endpoints REST organizados por funcionalidad (auth, users, portfolios, operations, market, analysis)
- Validación automática de entrada mediante esquemas Pydantic
- Documentación automática con OpenAPI/Swagger
- Manejo de autenticación mediante tokens JWT
- Serialización y deserialización de respuestas

#### Capa de Servicios

La capa de servicios en `app/services/` implementa toda la lógica de negocio del sistema. Esta capa orquesta operaciones complejas que pueden involucrar múltiples repositorios y validaciones. Incluye:

- Validación de reglas de negocio específicas del dominio
- Coordinación entre múltiples repositorios para operaciones transaccionales
- Cálculos financieros complejos (rendimientos, métricas de portfolio)
- Integración con servicios externos (APIs de mercado y análisis)
- Gestión de transacciones y manejo de errores de negocio

Los servicios principales son:

- **AuthService**: Gestiona autenticación, registro de usuarios y manejo de tokens JWT
- **UserService**: Administra perfiles de usuario y preferencias
- **PortfolioService**: Coordina operaciones de carteras, incluyendo cálculo de métricas agregadas
- **OperationService**: Registra y procesa transacciones de compra/venta
- **MarketService**: Obtiene y procesa datos de mercado en tiempo real
- **AnalysisService**: Genera análisis financieros utilizando IA

#### Capa de Repositorios

La capa de repositorios en `app/repositories/` abstrae completamente el acceso a datos, implementando el patrón Repository. Esta abstracción permite:

- Aislar la lógica de negocio de los detalles de persistencia
- Facilitar pruebas mediante repositorios mock
- Optimizar queries mediante eager loading de relaciones
- Reutilizar queries complejas
- Gestionar transacciones de forma coherente

Todos los repositorios heredan de `BaseRepository`, que proporciona operaciones CRUD genéricas. Los repositorios especializados agregan queries específicas del dominio.

#### Capa de Dominio

La capa de dominio en `app/models/` define las entidades del negocio y sus relaciones mediante modelos SQLAlchemy. Esta capa incluye:

- Modelos que mapean directamente a tablas PostgreSQL
- Uso de UUIDs como identificadores primarios para mayor escalabilidad
- Tipos de datos precisos (Decimal para valores financieros)
- Relaciones bidireccionales entre entidades
- Constraints de integridad referencial

Las entidades principales del dominio son:

**User**: Representa usuarios del sistema con autenticación y preferencias personalizadas.

**Portfolio**: Cartera de inversión que agrupa múltiples activos. Incluye métodos para calcular métricas agregadas como valor total, ganancia/pérdida y porcentajes de rendimiento.

**PortfolioAsset**: Posición individual de un activo dentro de un portfolio, manteniendo cantidad, precio promedio de compra y métodos para calcular valor actual de la posición.

**Operation**: Transacción de compra o venta de un activo. Registra tipo de operación, cantidad, precio y fecha, permitiendo reconstruir el historial completo de un portfolio.

**Asset**: Información de activos financieros (acciones, criptomonedas, ETFs) incluyendo símbolo, nombre, tipo y datos de mercado actuales.

**Analysis**: Análisis generado por IA para activos individuales o portfolios completos, almacenando el análisis, indicadores utilizados y timestamp de generación.

### Schemas y Validación

Los schemas en `app/schemas/` definen contratos de datos mediante Pydantic. Cada entidad tiene múltiples schemas:

- **Create**: Validación de datos para crear nuevas entidades
- **Update**: Validación de datos para actualizar entidades existentes
- **Response**: Formato de datos en respuestas al cliente
- **InDB**: Representación completa incluyendo todos los campos de base de datos

Esta separación permite controlar exactamente qué campos son requeridos, opcionales o de solo lectura en cada operación.

### Manejo de Datos Financieros

Un aspecto crítico del sistema es el manejo preciso de valores financieros. Los tipos `float` de punto flotante tienen errores de redondeo inherentes que son inaceptables en aplicaciones financieras. Por esta razón, el sistema utiliza exclusivamente el tipo `Decimal` de Python y `Numeric` de PostgreSQL.

Todas las operaciones financieras se realizan con precisión decimal:

```python
from decimal import Decimal

# Forma correcta para valores financieros
price = Decimal('150.25')
quantity = Decimal('10.5')
total = price * quantity  # Precisión exacta sin errores de redondeo
```

Las columnas de base de datos utilizan tipos específicos según la naturaleza del valor:

- Precios: `Numeric(11, 2)` - permite valores hasta $999,999,999.99
- Cantidades: `Numeric(16, 8)` - permite hasta 999,999,999.99999999 unidades con 8 decimales
- Valores totales: `Numeric(15, 2)` - permite valores hasta $9,999,999,999,999.99

Los cálculos de rendimiento se implementan directamente en los modelos de dominio:

```python
class Portfolio:
    def calculate_metrics(self):
        total_value = sum(asset.calculate_position_value() for asset in self.assets)
        total_cost = sum(asset.quantity * asset.average_price for asset in self.assets)
        self.total_gain_loss = total_value - total_cost
        self.total_gain_loss_percent = (
            (total_value - total_cost) / total_cost * 100 
            if total_cost > 0 else Decimal('0')
        )
```

### Seguridad

El sistema implementa múltiples capas de seguridad:

**Autenticación JWT**: Los usuarios se autentican mediante JSON Web Tokens. Tras un login correcto, el sistema genera un token firmado con HS256 que el cliente debe incluir en el header `Authorization: Bearer <token>` en todas las peticiones protegidas. Los tokens tienen una expiración configurable (por defecto 30 días).

**Hashing de Contraseñas**: Las contraseñas se hashean utilizando bcrypt, que automáticamente genera un salt único por contraseña y permite configurar el factor de costo computacional. Esto protege contra ataques de fuerza bruta y hace imposible recuperar la contraseña original.

**Validación de Permisos**: Cada operación sobre un recurso verifica que el usuario autenticado tenga permisos sobre ese recurso. Por ejemplo, un usuario solo puede acceder a sus propios portfolios, no a portfolios de otros usuarios.

### Integraciones Externas

#### Alpha Vantage API

El cliente `AlphaVantageClient` en `app/clients/alpha_vantage_client.py` integra la plataforma con datos de mercado en tiempo real. Utiliza los siguientes endpoints:

- `GLOBAL_QUOTE`: Obtiene la cotización actual de un activo
- `SYMBOL_SEARCH`: Búsqueda de símbolos por nombre
- `TIME_SERIES_DAILY`: Datos históricos de precios

El cliente implementa manejo de rate limiting (5 llamadas/minuto, 500 llamadas/día) y cacheo para optimizar el uso de la API.

#### OpenAI API

El cliente `OpenAIClient` en `app/clients/openai_client.py` genera análisis financieros utilizando GPT-5-mini mediante la Responses API. El sistema implementa extracción robusta de respuestas que maneja múltiples estructuras:

- Items tipo 'reasoning' con campo summary
- Items tipo 'message' con campo content
- Soporte para objetos y diccionarios

Los prompts están especializados para generar análisis técnico, evaluación de diversificación e identificación de riesgos basándose en indicadores técnicos calculados.

#### Procesador de Indicadores Técnicos

El módulo `ai_module/src/processors/technical_indicators.py` utiliza pandas-ta para calcular indicadores técnicos:

- **RSI (Relative Strength Index)**: Periodo 14, identifica condiciones de sobrecompra (>70) y sobreventa (<30)
- **MACD (Moving Average Convergence Divergence)**: Parámetros 12, 26, 9 - identifica cambios en momentum
- **Medias Móviles**: Periodos 20, 50 y 200 días para identificar tendencias
- **Detección de Tendencias**: Clasifica tendencia como alcista, bajista o lateral basándose en relaciones entre medias móviles

## Endpoints de la API

La API REST expone los siguientes grupos de endpoints bajo `/api/v1/`:

### Autenticación

- `POST /api/v1/auth/register` - Registro de nuevo usuario con validación de email único
- `POST /api/v1/auth/login` - Autenticación de usuario, retorna token JWT
- `GET /api/v1/auth/me` - Obtiene información del usuario autenticado actual

### Gestión de Usuarios

- `GET /api/v1/users` - Lista todos los usuarios (requiere permisos admin)
- `GET /api/v1/users/{id}` - Obtiene información detallada de un usuario
- `PATCH /api/v1/users/{id}` - Actualiza perfil de usuario (nombre, email, preferencias)

### Portfolios

- `POST /api/v1/portfolios` - Crea nuevo portfolio para el usuario autenticado
- `GET /api/v1/portfolios` - Lista todos los portfolios del usuario autenticado
- `GET /api/v1/portfolios/{id}` - Obtiene portfolio con todas sus posiciones y métricas calculadas
- `PATCH /api/v1/portfolios/{id}` - Actualiza nombre o descripción del portfolio
- `DELETE /api/v1/portfolios/{id}` - Elimina portfolio y todas sus posiciones asociadas

### Operaciones Financieras

- `POST /api/v1/operations` - Registra operación de compra o venta, actualizando automáticamente las posiciones del portfolio
- `GET /api/v1/operations` - Lista todas las operaciones del usuario
- `GET /api/v1/portfolios/{id}/operations` - Lista operaciones específicas de un portfolio

### Datos de Mercado

- `GET /api/v1/market/quote/{symbol}` - Obtiene cotización actual de un activo
- `GET /api/v1/market/search` - Busca símbolos por nombre o ticker
- `GET /api/v1/market/history/{symbol}` - Obtiene historial de precios diarios

### Análisis con IA

- `POST /api/v1/analysis/asset` - Genera análisis de un activo individual basado en indicadores técnicos
- `POST /api/v1/analysis/portfolio/{id}` - Genera análisis completo de un portfolio evaluando diversificación y riesgos
- `GET /api/v1/analysis/{id}` - Obtiene un análisis previamente generado

## Pruebas del Sistema

Se implementaron pruebas exhaustivas en dos niveles para verificar la correcta integración y funcionamiento de todos los componentes del sistema.

### Pruebas de Integración Externas

El archivo `test_integrations.py` verifica la correcta integración con servicios externos:

**Cliente Alpha Vantage**: Se probó correctamente la obtención de cotizaciones en tiempo real (AAPL a $278.78 con volumen de 47,234,255) y la búsqueda de símbolos (búsqueda de 'Apple' retornó 10 resultados incluyendo AAPL, APLE, AAPL34.SAO).

**Cliente OpenAI**: Se verificó la generación de análisis financiero usando GPT-5-mini con Responses API. El sistema generó correctamente un análisis en 6.7 segundos basándose en indicadores técnicos (RSI 65, tendencia alcista), demostrando la correcta extracción de respuestas de múltiples estructuras de la API.

**Procesador de Indicadores Técnicos**: Con 30 días de datos históricos se calcularon correctamente RSI (45.13), MA20 ($150.40) y detección de tendencia lateral. El sistema emitió advertencias esperadas sobre datos insuficientes para MACD (requiere mínimo 26 períodos), MA50 (requiere 50 períodos) y MA200 (requiere 200 períodos), demostrando validación robusta de datos.

### Pruebas de Servicios del Backend

El archivo `test_services.py` verifica la lógica de negocio implementada en los servicios:

**User Service**: Se probó el ciclo completo CRUD de usuarios incluyendo creación (juan.perez, maria.garcia, john.doe), listado (3 usuarios), búsqueda, actualización de perfil (moneda preferida EUR, zona horaria Europe/London), verificación de email y desactivación de usuario.

**Portfolio Service**: Se verificó la gestión completa de portfolios y operaciones:

- Creación de portfolios (Conservador, Agresivo, Diversificado)
- Registro de operaciones de compra (10 AAPL @ $150.50, 5 AAPL @ $155.00, 8 GOOGL @ $2800.00, 0.5 BTC @ $45000.00)
- Cálculo correcto de métricas (valor total: $47,225.00, costo total: $47,180.00, ganancia: $45.00)
- Cálculo de precios promedio por posición (AAPL: 15 unidades @ $152.00 promedio)
- Operaciones de venta (SELL 3 AAPL @ $160.00)
- Historial de operaciones en orden cronológico inverso
- Actualización y eliminación de portfolios

Todas las pruebas pasaron correctamente, confirmando que el sistema maneja correctamente la persistencia de datos, cálculos financieros y lógica de negocio.


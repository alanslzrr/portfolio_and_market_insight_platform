# Guía de pruebas de APIs en Postman

Este documento describe el proceso de prueba de todos los endpoints de la API, organizado según el flujo lógico del sistema.

## Prerrequisitos

Antes de comenzar, nos aseguramos de tener la API en ejecución.

### Iniciar la API

Ejecutamos el siguiente comando desde la raíz del proyecto:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Una vez que la API esté en ejecución, podremos acceder a ella desde Postman.

## Importación automática en Postman

Postman permite importar automáticamente todos los endpoints desde el archivo OpenAPI generado por FastAPI. Esto evita tener que crear cada endpoint manualmente.

### Instrucciones de Importación

1. Abrimos Postman
2. Hacemos clic en Import (botón ubicado en la esquina superior izquierda)
3. Seleccionamos la pestaña Link
4. Pegamos la siguiente URL:
   ```
   http://localhost:8000/openapi.json
   ```
5. Hacemos clic en Continue e Import

![Importar Colección de Postman](images/import-postman-collection.png)

Postman creará automáticamente una colección con:

* Todos los endpoints disponibles (`/auth`, `/users`, `/portfolios`, `/operations`, `/market`, `/analysis`, etc.)
* Métodos HTTP correctos (GET, POST, PUT, DELETE, etc.)
* Parámetros de ruta, query y cuerpos de ejemplo según los esquemas Pydantic definidos

![Importación Masiva](images/bulk-import.png)

Esta importación masiva nos permite no tener que escribir cada endpoint manualmente y facilita el testing de toda la aplicación.

### Configurar la Variable de Entorno Base URL

Como estamos trabajando en un entorno local, necesitamos configurar la variable `base_url` para que apunte a `localhost:8000`.

1. En Postman, vamos a la colección importada
2. Hacemos clic en la pestaña Variables
3. Actualizamos la variable `base_url` con el valor: `http://localhost:8000`

![Configurar Base URL](images/base-url-localhost.png)

Ahora podemos usar `{{base_url}}` en todas nuestras solicitudes para facilitar el cambio de entorno más adelante.

Una vez completados estos pasos, podremos:

* Probar todos los endpoints de la API
* Ver la documentación generada automáticamente
* Guardar ejemplos de respuestas
* Reutilizar las configuraciones en diferentes entornos

---

## 1. Autenticación (sin Authorization)

Ninguno de estos endpoints requiere header `Authorization`.

### POST `/api/v1/auth/register`

Registro de usuario.

![Prueba de registro](images/api:v1:register.png)

Body de ejemplo:

```json
{
  "email": "alan.salazar.01@uie.edu",
  "full_name": "Alan Salazar",
  "password": "Argentina123321"
}
```

La respuesta incluye solo los datos del usuario creado. No devuelve tokens.

Respuesta de ejemplo:

```json
{
    "id": "8c7442c6-bdbe-4691-b4cb-ccb98052037f",
    "email": "alan.salazar.01@uie.edu",
    "full_name": "Alan Salazar",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-12-11T15:50:23.589595",
    "updated_at": "2025-12-11T15:50:23.589603"
}
```

### POST `/api/v1/auth/login`

Inicio de sesión.

![Prueba de login](images/api:v1:auth:login.png)

Body de ejemplo:

```json
{
  "email": "alan.salazar.01@uie.edu",
  "password": "Argentina123321"
}
```

La respuesta incluye `access_token` y `refresh_token`.

Respuesta de ejemplo:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Yzc0NDJjNi1iZGJlLTQ2OTEtYjRjYi1jY2I5ODA1MjAzN2YiLCJleHAiOjE3NjU0NzE4NTAsInR5cGUiOiJhY2Nlc3MifQ.Cr9EpCzPQnAS2sAAkcYk56StIADJxPtKqB86YyF1Ewc",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Yzc0NDJjNi1iZGJlLTQ2OTEtYjRjYi1jY2I5ODA1MjAzN2YiLCJleHAiOjE3NjYwNzQ4NTAsInR5cGUiOiJyZWZyZXNoIn0.PekxNgBUAPZOaT3JkcUV4vEWsX2zfizzxLLOByQ-_II",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### POST `/api/v1/auth/refresh`

Renovación de token de acceso.

![Prueba de refresh token](images/api:v1:auth:refresh.png)

Body de ejemplo:

```json
{
  "refresh_token": "tu_refresh_token_aqui"
}
```

Respuesta de ejemplo:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Yzc0NDJjNi1iZGJlLTQ2OTEtYjRjYi1jY2I5ODA1MjAzN2YiLCJleHAiOjE3NjU0NzE5NTMsInR5cGUiOiJhY2Nlc3MifQ.xpqUlEMTsrfAyqJqDJdp2R9_ZNgMLBZ5lVMiH6aRKsE",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Yzc0NDJjNi1iZGJlLTQ2OTEtYjRjYi1jY2I5ODA1MjAzN2YiLCJleHAiOjE3NjYwNzQ5NTMsInR5cGUiOiJyZWZyZXNoIn0.EHh3fjkUMS0rzb_BeA7yWjNaAMkHeGZcxPMUwN6-0Qg",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### POST `/api/v1/auth/logout`

Cierre de sesión mediante invalidación del refresh token.
Requiere autenticación.

![Prueba de logout](images/api:v1:auth:logout.png)

Body de ejemplo:

```json
{
  "refresh_token": "tu_refresh_token_aqui"
}
```

La respuesta exitosa no devuelve contenido (HTTP 204).

En caso de error:

```json
{
    "detail": "credenciales invalidas"
}
```

### POST `/api/v1/auth/logout-all`

Cierre de todas las sesiones del usuario.
Requiere autenticación.
No requiere body.

![Prueba de logout-all](images/api:v1:auth:logout-all.png)

---

## 2. Configuración de autenticación en Postman

A partir de este punto, todos los endpoints que indiquen "requiere autenticación" necesitan el header:

* En cada petición:
  `Authorization: Bearer {access_token}`

o bien en la colección:

* Authorization Type: `Bearer Token`
* Token: `{{access_token}}`

---

## 3. Usuarios (requiere autenticación)

Todos los endpoints de esta sección requieren `Authorization: Bearer {access_token}`.

### GET `/api/v1/users/me`

Obtiene el perfil del usuario autenticado.
No requiere body.

### PUT `/api/v1/users/me`

Actualiza el perfil del usuario autenticado.

Body de ejemplo (todos los campos son opcionales):

```json
{
  "full_name": "Nuevo Nombre",
  "currency": "USD",
  "timezone": "UTC",
  "language": "en",
  "preferences": {}
}
```

### PUT `/api/v1/users/me/password`

Cambia la contraseña del usuario.

Body de ejemplo:

```json
{
  "current_password": "Password123!",
  "new_password": "NewPassword456!"
}
```

Después del cambio todas las sesiones se invalidan automáticamente.

---

## 4. Portfolios (requiere autenticación)

Todos los endpoints de esta sección requieren `Authorization: Bearer {access_token}`.

### POST `/api/v1/portfolios`

Crea un nuevo portfolio.

Body de ejemplo:

```json
{
  "name": "Mi Portfolio Principal",
  "description": "Portfolio de largo plazo",
  "base_currency": "USD"
}
```

Guarde el `id` del portfolio creado para las pruebas posteriores.

### GET `/api/v1/portfolios`

Lista todos los portfolios del usuario.
No requiere body.

### GET `/api/v1/portfolios/{portfolio_id}`

Obtiene el detalle de un portfolio concreto con todas sus posiciones.
No requiere body.
Utilice el `portfolio_id` obtenido en la creación o en el listado.

### PUT `/api/v1/portfolios/{portfolio_id}`

Actualiza un portfolio existente.

Body de ejemplo (todos los campos son opcionales):

```json
{
  "name": "Portfolio Actualizado",
  "description": "Nueva descripción"
}
```

### DELETE `/api/v1/portfolios/{portfolio_id}`

Elimina un portfolio junto con todas sus posiciones y operaciones.
No requiere body.
Esta acción es irreversible.

---

## 5. Operaciones (requiere autenticación)

Todos los endpoints de esta sección requieren `Authorization: Bearer {access_token}`.

### POST `/api/v1/operations`

Crea una operación de compra o venta en un portfolio.

Ejemplo de body para COMPRA:

```json
{
  "portfolio_id": "uuid-del-portfolio",
  "asset_symbol": "AAPL",
  "operation_type": "BUY",
  "quantity": 10,
  "price": 150.50,
  "fees": 1.50,
  "operation_date": "2025-12-11T10:00:00Z",
  "notes": "Compra de Apple"
}
```

Ejemplo de body para VENTA:

```json
{
  "portfolio_id": "uuid-del-portfolio",
  "asset_symbol": "AAPL",
  "operation_type": "SELL",
  "quantity": 5,
  "price": 160.00,
  "fees": 1.00,
  "operation_date": "2025-12-11T15:00:00Z",
  "notes": "Venta parcial de Apple"
}
```

El campo `fees` es opcional y por defecto es 0.

### GET `/api/v1/operations`

Lista operaciones del usuario con filtros opcionales.

Parámetros de consulta requeridos:

* `portfolio_id`: UUID del portfolio (obligatorio)

Parámetros de consulta opcionales:

* `asset_symbol`: filtrar por símbolo
* `operation_type`: filtrar por tipo (BUY o SELL)
* `date_from`: fecha inicio (YYYY-MM-DD)
* `date_to`: fecha fin (YYYY-MM-DD)
* `skip`: registros a saltar (paginación)
* `limit`: máximo de registros (default 100, max 500)

Ejemplo:
`/api/v1/operations?portfolio_id=xxx&operation_type=BUY&asset_symbol=AAPL`

### GET `/api/v1/operations/{operation_id}`

Obtiene el detalle de una operación concreta.
No requiere body.

### PUT `/api/v1/operations/{operation_id}`

Actualiza una operación existente.

Body de ejemplo:

```json
{
  "notes": "Notas actualizadas"
}
```

Solo se pueden actualizar las notas. Los valores financieros son inmutables.

### GET `/api/v1/operations/stats/{portfolio_id}`

Devuelve estadísticas agregadas del portfolio indicado.
No requiere body.

Incluye:

* `total_operations`: número total de operaciones
* `total_buys`: número de compras
* `total_sells`: número de ventas
* `total_invested`: suma total invertida en compras
* `total_withdrawn`: suma total retirada en ventas
* `total_fees`: suma de comisiones pagadas
* `unique_assets`: número de activos distintos operados

---

## 6. Mercado (sin autenticación)

Ninguno de estos endpoints requiere header `Authorization`.

### GET `/api/v1/market/assets/search`

Busca activos por nombre o símbolo.
No requiere body.

Parámetro de consulta obligatorio:

* `q`: término de búsqueda (mínimo 1 carácter)

Parámetro de consulta opcional:

* `limit`: máximo de resultados (default 20, max 100)

Ejemplos:

* `/api/v1/market/assets/search?q=apple`
* `/api/v1/market/assets/search?q=AAPL&limit=10`

### GET `/api/v1/market/assets/{symbol}`

Devuelve información detallada de un activo específico.
No requiere body.

Ejemplo:
`/api/v1/market/assets/AAPL`

### GET `/api/v1/market/prices/{symbol}/current`

Devuelve el precio actual de un activo.
No requiere body.

Ejemplo:
`/api/v1/market/prices/AAPL/current`

### GET `/api/v1/market/prices/{symbol}/historical`

Devuelve precios históricos de un activo en formato OHLCV.
No requiere body.

Parámetro de consulta opcional:

* `days`: número de días de histórico (default 30, max 100)

Ejemplo:
`/api/v1/market/prices/AAPL/historical?days=60`

### POST `/api/v1/market/assets`

Crea un activo en el catálogo del sistema.
No requiere autenticación.

Parámetros de consulta requeridos:

* `symbol`: símbolo del activo (se convierte a mayúsculas)
* `name`: nombre del activo
* `asset_type`: tipo de activo (STOCK, ETF, CRYPTO)

Parámetros de consulta opcionales:

* `currency`: moneda del activo (default USD)
* `exchange`: exchange o bolsa
* `description`: descripción del activo

Ejemplo:
`/api/v1/market/assets?symbol=TSLA&name=Tesla%20Inc&asset_type=STOCK&exchange=NASDAQ`

---

## 7. Análisis con IA (requiere autenticación)

Todos los endpoints de esta sección requieren `Authorization: Bearer {access_token}` y tener configurada la variable de entorno `OPENAI_API_KEY` en el backend.

### POST `/api/v1/analysis/asset/{symbol}`

Genera un análisis del activo indicado.
No requiere body.

Parámetro de consulta opcional:

* `force_regenerate`: forzar regeneración ignorando cache (default false)

Ejemplo:
`/api/v1/analysis/asset/AAPL?force_regenerate=false`

### POST `/api/v1/analysis/portfolio/{portfolio_id}`

Genera un análisis del portfolio indicado.
No requiere body.

Parámetro de consulta opcional:

* `force_regenerate`: forzar regeneración ignorando cache (default false)

### GET `/api/v1/analysis/history`

Lista el historial de análisis realizados.
No requiere body.

Parámetros de consulta opcionales:

* `portfolio_id`: filtrar por portfolio
* `asset_symbol`: filtrar por activo
* `limit`: máximo de resultados (default 10, max 50)

Ejemplo:
`/api/v1/analysis/history?portfolio_id=xxx&limit=20`

### DELETE `/api/v1/analysis/cache/asset/{symbol}`

Elimina la caché de análisis de un activo.
No requiere body.

Ejemplo:
`/api/v1/analysis/cache/asset/AAPL`

### DELETE `/api/v1/analysis/cache/portfolio/{portfolio_id}`

Elimina la caché de análisis de un portfolio.
No requiere body.

---

## Flujo de prueba recomendado

1. `POST /api/v1/auth/register` → obtener datos del usuario.
2. `POST /api/v1/auth/login` → obtener `access_token` y `refresh_token`.
3. Configurar el `access_token` en Postman (colección o petición).
4. `GET /api/v1/users/me` → verificar que la autenticación funciona.
5. `POST /api/v1/portfolios` → crear un portfolio y guardar su `id`.
6. `POST /api/v1/operations` (BUY) → registrar compra de 10 acciones de AAPL en el portfolio.
7. `GET /api/v1/portfolios/{portfolio_id}` → comprobar posiciones del portfolio.
8. `POST /api/v1/operations` (SELL) → registrar venta de 5 acciones de AAPL.
9. `GET /api/v1/operations/stats/{portfolio_id}` → revisar estadísticas del portfolio.
10. `GET /api/v1/market/prices/AAPL/current` → consultar precio actual de AAPL.
11. `POST /api/v1/analysis/portfolio/{portfolio_id}` → solicitar análisis IA del portfolio (si `OPENAI_API_KEY` está configurada).


# Endpoints de Carteras

Este módulo contiene todos los endpoints relacionados con la gestión de carteras de inversión. Permite a los usuarios crear, consultar, actualizar y eliminar carteras, así como obtener información detallada sobre sus posiciones y rendimiento.

## Archivos que Contendrá

- **router.py**: Contiene los endpoints principales de gestión de carteras:
  - `GET /`: Listar todas las carteras del usuario autenticado
  - `POST /`: Crear una nueva cartera
  - `GET /{portfolio_id}`: Obtener detalles completos de una cartera específica
  - `PUT /{portfolio_id}`: Actualizar información de una cartera
  - `DELETE /{portfolio_id}`: Eliminar una cartera
  - `GET /{portfolio_id}/positions`: Obtener todas las posiciones de una cartera
  - `GET /{portfolio_id}/operations`: Obtener todas las operaciones de una cartera
  - `GET /{portfolio_id}/performance`: Obtener métricas de rendimiento de una cartera
  - `GET /{portfolio_id}/analytics`: Obtener análisis con IA de una cartera

- **dependencies.py**: Contiene dependencias compartidas:
  - `get_portfolio_by_id`: Función para obtener una cartera y validar que pertenece al usuario
  - `validate_portfolio_access`: Validador de permisos de acceso a carteras

## Funcionalidades

Este módulo implementa la gestión completa de carteras:

- Creación de carteras con nombre, moneda base y descripción
- Consulta de detalles con métricas actualizadas en tiempo real
- Cálculo automático de valor total, ganancias/pérdidas y rendimiento porcentual
- Actualización de precios mediante integración con Alpha Vantage API
- Visualización de posiciones con precios actualizados
- Análisis asistido por IA de la cartera completa

## Integraciones

Los endpoints se integran con:

- **MarketDataService**: Para obtener precios actualizados de activos
- **PortfolioService**: Para calcular métricas y actualizar balances
- **AIService**: Para generar análisis descriptivos de carteras


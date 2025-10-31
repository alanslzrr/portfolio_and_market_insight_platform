# Endpoints de Datos de Mercado

Este módulo contiene todos los endpoints relacionados con la consulta de datos de mercado financiero. Permite a los usuarios obtener cotizaciones en tiempo real, datos históricos de precios e información sobre activos financieros.

## Archivos que Contendrá

- **router.py**: Contiene los endpoints principales de datos de mercado:
  - `GET /quote/{symbol}`: Obtener cotización en tiempo real de un activo
  - `GET /historical/{symbol}`: Obtener datos históricos de precios de un activo
  - `GET /asset/{symbol}`: Obtener información detallada de un activo
  - `GET /search`: Buscar activos por nombre o símbolo
  - `GET /batch-quotes`: Obtener múltiples cotizaciones en una sola petición

- **dependencies.py**: Contiene dependencias compartidas:
  - `validate_symbol`: Validador de símbolos de activos
  - `validate_date_range`: Validador de rangos de fechas para datos históricos

## Funcionalidades

Este módulo implementa la consulta de datos de mercado:

- Obtención de cotizaciones en tiempo real mediante Alpha Vantage API
- Consulta de datos históricos con diferentes intervalos (diario, semanal, mensual)
- Búsqueda de activos por nombre o símbolo
- Información detallada de activos (nombre, tipo, exchange, moneda)
- Caché de precios para optimizar consultas frecuentes
- Batch queries para obtener múltiples cotizaciones eficientemente

## Integraciones

Los endpoints se integran con:

- **Alpha Vantage API**: Para obtener datos de mercado en tiempo real
- **MarketDataService**: Para gestionar caché y procesamiento de datos
- **Redis**: Para almacenar precios en caché y reducir llamadas a APIs externas

## Optimizaciones

El módulo incluye optimizaciones para mejorar el rendimiento:

- Caché de precios con TTL configurable
- Rate limiting para respetar límites de APIs externas
- Batch processing para múltiples consultas
- Fallback a datos históricos cuando la API está temporalmente no disponible


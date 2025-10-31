# Clientes para Servicios Externos

Este módulo contiene los clientes que se comunican con servicios externos necesarios para el funcionamiento del módulo de análisis con IA. Principalmente incluye el cliente para OpenAI API.

## Archivos que Contendrá

- **openai_client.py**: Cliente para OpenAI API:
  - `OpenAIClient`: Clase cliente que encapsula comunicación con OpenAI
  - `generate_analysis()`: Genera análisis enviando prompt a OpenAI
  - `optimize_prompt()`: Optimiza prompts para cumplir límites de tokens
  - `check_token_limit()`: Verifica si un prompt excede límites de tokens
  - Manejo de rate limiting y reintentos
  - Manejo de errores de API y timeouts

## Funcionalidades

El cliente proporciona:

- Comunicación segura con OpenAI API mediante autenticación
- Gestión de tokens y límites de la API
- Manejo de errores y reintentos automáticos
- Optimización de prompts para eficiencia
- Logging de interacciones con la API

## Configuración

El cliente requiere configuración:

- `OPENAI_API_KEY`: Clave API de OpenAI
- `OPENAI_MODEL`: Modelo a utilizar (por defecto gpt-4 o gpt-3.5-turbo)
- `MAX_TOKENS`: Límite máximo de tokens en respuesta
- `TEMPERATURE`: Temperatura para generación (creatividad)
- `TIMEOUT`: Timeout para peticiones a la API

## Manejo de Errores

El cliente maneja:

- Errores de autenticación (API key inválida)
- Rate limiting (demasiadas peticiones)
- Timeouts (peticiones que tardan demasiado)
- Errores de formato (prompts inválidos)
- Errores de red (conexión fallida)

## Optimizaciones

El cliente incluye optimizaciones:

- Caché de respuestas para prompts similares
- Batching de peticiones cuando es posible
- Compresión de prompts para reducir tokens
- Reintentos exponenciales para errores temporales
- Logging detallado para debugging


# Configuración de la Aplicación

Este módulo contiene toda la configuración de la aplicación, incluyendo la carga de variables de entorno, valores por defecto y constantes utilizadas en toda la plataforma.

## Archivos que Contendrá

- **settings.py**: Clase principal de configuración que:
  - Carga variables de entorno desde archivo .env
  - Define valores por defecto para todas las configuraciones
  - Valida configuraciones críticas al iniciar la aplicación
  - Proporciona acceso centralizado a configuraciones (base de datos, APIs externas, seguridad)

  Configuraciones principales:
  - `DATABASE_URL`: URL de conexión a PostgreSQL
  - `SECRET_KEY`: Clave secreta para firmar tokens JWT
  - `ALGORITHM`: Algoritmo de encriptación para JWT
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración de access tokens (15 minutos)
  - `REFRESH_TOKEN_EXPIRE_DAYS`: Tiempo de expiración de refresh tokens (7 días)
  - `ALPHA_VANTAGE_API_KEY`: Clave API para Alpha Vantage
  - `OPENAI_API_KEY`: Clave API para OpenAI
  - `REDIS_URL`: URL de conexión a Redis para caché
  - `ENVIRONMENT`: Entorno de ejecución (development, production, testing)

- **constants.py**: Constantes compartidas:
  - Símbolos de monedas soportadas
  - Tipos de activos financieros
  - Tipos de operaciones (buy, sell)
  - Límites y validaciones (cantidades mínimas, rangos de fechas)
  - Mensajes de error estándar
  - Configuraciones de caché (TTL para precios, análisis)

## Uso

La configuración se utiliza mediante una instancia singleton de `Settings` que se importa en toda la aplicación. Esto asegura que todas las partes de la aplicación utilicen la misma configuración y facilita el testing mediante la sobreescritura de valores en entornos de prueba.


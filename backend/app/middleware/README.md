# Middleware Personalizado

Este módulo contiene middleware personalizado para procesamiento de peticiones HTTP. El middleware intercepta las peticiones antes de que lleguen a los endpoints y puede realizar procesamiento adicional como logging, manejo de errores, y validaciones adicionales.

## Archivos que Contendrá

- **error_handler.py**: Manejo centralizado de errores:
  - `setup_exception_handlers()`: Configura handlers para diferentes tipos de excepciones
  - Manejo de excepciones HTTP estándar (404, 422, 500)
  - Manejo de excepciones de negocio personalizadas
  - Formateo consistente de respuestas de error
  - Logging de errores para debugging

- **logging_middleware.py**: Middleware de logging:
  - `logging_middleware()`: Intercepta peticiones y respuestas para logging
  - Registra información de peticiones (método, ruta, parámetros)
  - Registra información de respuestas (código de estado, tiempo de respuesta)
  - Logging de errores y excepciones
  - Filtrado de información sensible (passwords, tokens)

- **cors_middleware.py**: Configuración de CORS:
  - Configuración de orígenes permitidos
  - Configuración de métodos HTTP permitidos
  - Configuración de headers permitidos
  - Manejo de credenciales en peticiones CORS

- **rate_limiting.py**: Rate limiting (opcional):
  - Limita número de peticiones por IP
  - Prevención de ataques de fuerza bruta
  - Rate limiting específico por endpoint
  - Configuración de límites por entorno

## Funcionalidades

El middleware proporciona:

- Manejo centralizado de errores con respuestas consistentes
- Logging de todas las peticiones para auditoría y debugging
- Configuración de CORS para acceso desde frontend
- Protección contra abuso mediante rate limiting
- Transformación de errores en respuestas HTTP apropiadas

## Uso

El middleware se configura en `main.py` y se aplica automáticamente a todas las peticiones. Los handlers de errores capturan excepciones que ocurren en cualquier parte de la aplicación y las convierten en respuestas HTTP apropiadas con códigos de estado y mensajes descriptivos.


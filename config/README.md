# Configuración del Proyecto

Este directorio contiene archivos de configuración del proyecto que no son código fuente pero son necesarios para el funcionamiento del sistema. Incluye archivos de configuración para diferentes entornos y herramientas.

## Archivos que Contendrá

- **.env.example**: Archivo de ejemplo de variables de entorno:
  - Muestra todas las variables de entorno necesarias
  - Incluye valores de ejemplo
  - Documenta el propósito de cada variable
  - Debe copiarse a `.env` y completarse con valores reales

- **.env.development**: Variables de entorno para desarrollo (opcional):
  - Configuración específica para entorno de desarrollo
  - Puede incluir datos de prueba
  - No debe incluirse en control de versiones

- **.env.production**: Variables de entorno para producción (opcional):
  - Configuración específica para producción
  - Debe mantenerse segura y no incluirse en control de versiones
  - Puede gestionarse mediante secretos del sistema

- **alembic.ini**: Configuración de Alembic para migraciones:
  - Configuración de conexión a base de datos
  - Configuración de rutas de migraciones
  - Configuración de logging

- **.gitignore**: Archivos y directorios a ignorar en git:
  - Archivos de entorno (.env)
  - Archivos de Python (__pycache__, .pyc)
  - Archivos de IDE (.vscode, .idea)
  - Archivos de base de datos locales
  - Archivos de logs

## Variables de Entorno Principales

Las variables de entorno principales incluyen:

- **Base de datos**: `DATABASE_URL`
- **Seguridad**: `SECRET_KEY`, `ALGORITHM`
- **APIs externas**: `ALPHA_VANTAGE_API_KEY`, `OPENAI_API_KEY`
- **Caché**: `REDIS_URL`
- **Entorno**: `ENVIRONMENT` (development, production, testing)

## Seguridad

- Los archivos `.env` con valores reales NO deben incluirse en control de versiones
- Solo `.env.example` debe estar en el repositorio
- Las variables de entorno de producción deben gestionarse mediante secretos seguros
- Las claves API deben mantenerse seguras y rotarse periódicamente


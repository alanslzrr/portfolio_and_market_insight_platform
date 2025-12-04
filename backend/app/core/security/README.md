# Componentes de Seguridad

Este módulo contiene todos los componentes relacionados con la seguridad de la aplicación, incluyendo el manejo de tokens JWT, el hashing de contraseñas y las dependencias de autenticación para los endpoints.

## Archivos que Contendrá

- **jwt_handler.py**: Manejo completo de tokens JWT:
  - `create_access_token()`: Genera access tokens con tiempo de expiración corto (15 minutos)
  - `create_refresh_token()`: Genera refresh tokens con tiempo de expiración largo (7 días)
  - `verify_token()`: Verifica la validez y firma de un token JWT
  - `decode_token()`: Decodifica un token y extrae el payload (user_id, email, etc.)
  - `get_user_from_token()`: Extrae información del usuario desde el token

- **password.py**: Funciones para manejo seguro de contraseñas:
  - `hash_password()`: Genera hash seguro de contraseñas usando bcrypt
  - `verify_password()`: Verifica una contraseña contra su hash almacenado
  - Utiliza bcrypt con salt automático para máxima seguridad

- **dependencies.py**: Dependencias de FastAPI para autenticación:
  - `get_current_user()`: Dependency que extrae el usuario actual desde el token JWT en el header Authorization
  - `get_current_active_user()`: Dependency que valida que el usuario esté activo y verificado
  - Manejo de excepciones para tokens inválidos o expirados

## Funcionalidades

Este módulo proporciona:

- Generación segura de tokens JWT con información del usuario
- Verificación de tokens en cada petición autenticada
- Hash seguro de contraseñas que previene ataques de diccionario
- Dependencias reutilizables para proteger endpoints
- Manejo consistente de errores de autenticación

## Seguridad

Las medidas de seguridad implementadas incluyen:

- Tokens JWT firmados con clave secreta
- Expiración de tokens para limitar ventanas de ataque
- Hash de contraseñas con bcrypt (one-way hashing)
- Validación de tokens antes de procesar peticiones
- Manejo seguro de errores sin exponer información sensible


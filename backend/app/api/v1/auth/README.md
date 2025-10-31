# Endpoints de Autenticación

Este módulo contiene todos los endpoints relacionados con la autenticación y gestión de sesiones de usuario. Implementa un sistema completo de autenticación que incluye registro, verificación de email, login, renovación de tokens y recuperación de contraseña.

## Archivos que Contendrá

- **router.py**: Contiene los endpoints principales de autenticación:
  - `POST /register`: Registro de nuevos usuarios con verificación de email
  - `POST /login`: Autenticación de usuarios y generación de tokens JWT
  - `POST /refresh`: Renovación de access token usando refresh token
  - `POST /logout`: Cierre de sesión e invalidación de refresh token
  - `POST /verify-email`: Verificación de email mediante token
  - `POST /forgot-password`: Solicitud de recuperación de contraseña
  - `POST /reset-password`: Restablecimiento de contraseña con token

- **dependencies.py**: Contiene dependencias compartidas:
  - `get_current_user`: Función para obtener el usuario actual desde el token JWT
  - `get_current_active_user`: Función para obtener usuario activo y verificado
  - Validadores de tokens JWT

## Funcionalidades

Este módulo implementa un sistema de autenticación robusto que incluye:

- Registro de usuarios con hash seguro de contraseñas usando bcrypt
- Verificación de email mediante tokens únicos
- Autenticación mediante tokens JWT con access token (15 minutos) y refresh token (7 días)
- Recuperación de contraseña mediante tokens temporales enviados por email
- Gestión de sesiones múltiples con refresh tokens

## Seguridad

Las medidas de seguridad implementadas incluyen:

- Hash de contraseñas con bcrypt
- Tokens JWT firmados con secret key
- Validación de tokens expirados
- Verificación de email antes de permitir acceso completo
- Rate limiting para prevenir ataques de fuerza bruta


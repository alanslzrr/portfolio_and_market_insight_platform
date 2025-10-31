# Endpoints de Usuarios

Este módulo contiene todos los endpoints relacionados con la gestión de perfiles de usuario. Permite a los usuarios consultar y actualizar su información personal, cambiar contraseñas y gestionar su cuenta.

## Archivos que Contendrá

- **router.py**: Contiene los endpoints principales de gestión de usuarios:
  - `GET /profile`: Obtener el perfil completo del usuario autenticado
  - `PUT /profile`: Actualizar información del perfil de usuario
  - `POST /change-password`: Cambiar la contraseña del usuario
  - `DELETE /account`: Eliminar la cuenta del usuario
  - `GET /activity`: Obtener historial de actividad del usuario

- **dependencies.py**: Contiene dependencias compartidas:
  - `get_current_user`: Función para obtener el usuario actual desde el token
  - `validate_password_change`: Validador para cambios de contraseña

## Funcionalidades

Este módulo implementa la gestión completa de perfiles de usuario:

- Consulta de perfil con información personal y preferencias
- Actualización de información del perfil (nombre, preferencias, configuración)
- Cambio seguro de contraseña con validación de contraseña actual
- Eliminación de cuenta con confirmación
- Historial de actividad del usuario en la plataforma

## Seguridad

Las operaciones sobre usuarios incluyen medidas de seguridad:

- Validación de contraseña actual antes de permitir cambios
- Hash seguro de nuevas contraseñas
- Validación de permisos para asegurar que usuarios solo accedan a su propia información
- Auditoría de cambios importantes en la cuenta


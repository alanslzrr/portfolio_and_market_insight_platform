# Capa de API - Endpoints HTTP

Esta capa contiene todos los endpoints HTTP que exponen la funcionalidad de la plataforma a través de una API REST. Los endpoints están organizados por dominios de negocio para facilitar la navegación y el mantenimiento.

## Estructura

Los endpoints están agrupados en routers por dominio funcional:

- **v1/auth/**: Endpoints relacionados con autenticación y gestión de sesiones de usuario
- **v1/portfolios/**: Endpoints para la gestión de carteras de inversión
- **v1/operations/**: Endpoints para el registro y consulta de operaciones de compra y venta
- **v1/users/**: Endpoints para la gestión de perfiles de usuario
- **v1/market/**: Endpoints para consultar datos de mercado y cotizaciones

## Archivos que Contendrá

### v1/auth/
- **router.py**: Define los endpoints de autenticación (registro, login, refresh token, logout)
- **dependencies.py**: Dependencias compartidas para validación de tokens JWT

### v1/portfolios/
- **router.py**: Define los endpoints para gestión de carteras (crear, listar, obtener detalles, actualizar, eliminar)
- **dependencies.py**: Dependencias para validar permisos de acceso a carteras

### v1/operations/
- **router.py**: Define los endpoints para operaciones (crear, listar, obtener detalles, actualizar, eliminar, importar/exportar CSV)
- **dependencies.py**: Dependencias para validación de operaciones

### v1/users/
- **router.py**: Define los endpoints para gestión de perfil de usuario (obtener perfil, actualizar perfil, cambiar contraseña, eliminar cuenta)
- **dependencies.py**: Dependencias para validación de usuario autenticado

### v1/market/
- **router.py**: Define los endpoints para consultar datos de mercado (cotizaciones en tiempo real, datos históricos, información de activos)

## Principios de Diseño

Los endpoints siguen las mejores prácticas de diseño de APIs REST:

- **Rutas RESTful**: Las rutas siguen convenciones REST estándar
- **Validación de entrada**: Todos los datos de entrada se validan mediante esquemas Pydantic
- **Manejo de errores**: Errores consistentes con códigos HTTP apropiados
- **Documentación automática**: FastAPI genera documentación automática en `/docs`
- **Autenticación**: La mayoría de endpoints requieren autenticación mediante tokens JWT


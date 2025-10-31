# Aplicación Principal

Este directorio contiene el código fuente principal de la aplicación backend. La estructura está organizada siguiendo los principios de arquitectura en capas, donde cada capa tiene responsabilidades específicas y bien definidas.

## Organización de Capas

La aplicación está dividida en capas que facilitan la separación de responsabilidades:

- **api/**: Capa de presentación que expone los endpoints HTTP
- **core/**: Configuración y componentes centrales del sistema
- **models/**: Modelos de dominio que representan las entidades del sistema
- **repositories/**: Capa de acceso a datos que abstrae las operaciones de base de datos
- **schemas/**: Esquemas de validación y serialización de datos
- **services/**: Capa de servicios que contiene la lógica de negocio
- **middleware/**: Middleware personalizado para procesamiento de peticiones
- **utils/**: Utilidades y funciones auxiliares compartidas

## Principios de Diseño

Esta estructura sigue principios de diseño que facilitan el mantenimiento y la testabilidad:

- **Separación de responsabilidades**: Cada capa tiene un propósito específico y claro
- **Dependencias unidireccionales**: Las capas superiores dependen de las inferiores, pero no al revés
- **Inversión de dependencias**: Los servicios dependen de abstracciones (repositorios) y no de implementaciones concretas
- **Testabilidad**: La separación de capas facilita la creación de pruebas unitarias y de integración


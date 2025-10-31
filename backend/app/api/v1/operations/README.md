# Endpoints de Operaciones

Este módulo contiene todos los endpoints relacionados con el registro y gestión de operaciones de compra y venta. Permite a los usuarios registrar operaciones, consultarlas, actualizarlas y gestionarlas mediante importación y exportación desde CSV.

## Archivos que Contendrá

- **router.py**: Contiene los endpoints principales de gestión de operaciones:
  - `GET /`: Listar operaciones con filtros opcionales (cartera, activo, tipo, fecha)
  - `POST /`: Registrar una nueva operación de compra o venta
  - `GET /{operation_id}`: Obtener detalles de una operación específica
  - `PUT /{operation_id}`: Actualizar una operación existente
  - `DELETE /{operation_id}`: Eliminar una operación
  - `POST /import`: Importar operaciones desde un archivo CSV
  - `GET /export`: Exportar operaciones a un archivo CSV con filtros opcionales

- **dependencies.py**: Contiene dependencias compartidas:
  - `get_operation_by_id`: Función para obtener una operación y validar permisos
  - `validate_operation_data`: Validador de datos de operaciones

## Funcionalidades

Este módulo implementa la gestión completa de operaciones:

- Registro de operaciones de compra con validación de datos
- Registro de operaciones de venta con validación de cantidad disponible
- Cálculo automático de total_amount incluyendo comisiones
- Actualización automática de posiciones en cartera
- Recalculación de precio promedio de compra
- Actualización de balance de cartera tras cada operación
- Importación masiva desde CSV con validación
- Exportación a CSV con filtros personalizables

## Validaciones

Las operaciones incluyen validaciones importantes:

- Validación de pertenencia de cartera al usuario
- Validación de cantidad disponible para operaciones de venta
- Validación de datos financieros (precios positivos, cantidades válidas)
- Validación de formato de fechas y monedas


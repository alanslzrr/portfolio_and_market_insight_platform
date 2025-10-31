# Utilidades y Funciones Auxiliares

Este módulo contiene funciones auxiliares y utilidades que pueden ser utilizadas en diferentes partes de la aplicación. Estas funciones proporcionan funcionalidad común que no pertenece a un dominio específico.

## Archivos que Contendrá

- **email.py**: Utilidades para envío de emails:
  - `send_verification_email()`: Envía email de verificación de cuenta
  - `send_password_reset_email()`: Envía email de recuperación de contraseña
  - `send_notification_email()`: Envía notificaciones generales
  - Configuración de servidor SMTP
  - Plantillas de email HTML

- **validators.py**: Validadores personalizados:
  - `validate_email()`: Validación de formato de email
  - `validate_password_strength()`: Validación de fortaleza de contraseña
  - `validate_symbol()`: Validación de símbolos de activos financieros
  - `validate_currency()`: Validación de códigos de moneda
  - `validate_date_range()`: Validación de rangos de fechas

- **formatters.py**: Funciones de formateo:
  - `format_currency()`: Formatea números como moneda
  - `format_percentage()`: Formatea números como porcentaje
  - `format_date()`: Formatea fechas en diferentes formatos
  - `format_large_number()`: Formatea números grandes (miles, millones)

- **calculators.py**: Funciones de cálculo financiero:
  - `calculate_percentage_change()`: Calcula cambio porcentual
  - `calculate_gain_loss()`: Calcula ganancia/pérdida
  - `calculate_average_price()`: Calcula precio promedio ponderado
  - `calculate_total_value()`: Calcula valor total de posiciones

- **csv_handler.py**: Utilidades para manejo de CSV:
  - `parse_operations_csv()`: Parsea archivo CSV de operaciones
  - `generate_operations_csv()`: Genera archivo CSV de operaciones
  - `validate_csv_format()`: Valida formato de CSV
  - Manejo de diferentes formatos de fecha y moneda

- **cache_helper.py**: Utilidades para caché:
  - `get_cache_key()`: Genera claves de caché consistentes
  - `is_cache_valid()`: Verifica si un caché es válido
  - `parse_cache_response()`: Parsea respuestas de caché

## Funcionalidades

Este módulo proporciona:

- Funciones reutilizables para operaciones comunes
- Validaciones consistentes en toda la aplicación
- Formateo consistente de datos para presentación
- Cálculos financieros estándar
- Utilidades para integración con servicios externos

## Principios

Las utilidades siguen principios:

- **Pure Functions**: Funciones sin efectos secundarios cuando es posible
- **Reusabilidad**: Funciones que pueden usarse en múltiples contextos
- **Claridad**: Funciones con nombres descriptivos y propósito claro
- **Testabilidad**: Funciones fáciles de testear unitariamente


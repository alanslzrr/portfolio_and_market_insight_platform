# Tests - Suite de Pruebas

Este directorio contiene todas las pruebas automatizadas del sistema. Las pruebas están organizadas siguiendo la estructura de la aplicación para facilitar el mantenimiento y la ejecución de tests específicos.

## Estructura

- **unit/**: Pruebas unitarias que prueban componentes individuales de forma aislada
- **integration/**: Pruebas de integración que prueban la interacción entre componentes
- **fixtures/**: Datos de prueba y fixtures reutilizables

## Archivos que Contendrá

### unit/
- **api/**: Tests de endpoints API:
  - `test_auth_endpoints.py`: Tests de endpoints de autenticación
  - `test_portfolio_endpoints.py`: Tests de endpoints de carteras
  - `test_operation_endpoints.py`: Tests de endpoints de operaciones
  - `test_user_endpoints.py`: Tests de endpoints de usuarios
  - `test_market_endpoints.py`: Tests de endpoints de mercado

- **services/**: Tests de servicios:
  - `test_auth_service.py`: Tests del servicio de autenticación
  - `test_portfolio_service.py`: Tests del servicio de carteras
  - `test_operation_service.py`: Tests del servicio de operaciones
  - `test_market_data_service.py`: Tests del servicio de datos de mercado
  - `test_ai_service.py`: Tests del servicio de análisis con IA

- **repositories/**: Tests de repositorios:
  - `test_user_repository.py`: Tests del repositorio de usuarios
  - `test_portfolio_repository.py`: Tests del repositorio de carteras
  - `test_operation_repository.py`: Tests del repositorio de operaciones
  - `test_asset_repository.py`: Tests del repositorio de activos

### integration/
- **test_auth_flow.py**: Tests del flujo completo de autenticación
- **test_portfolio_operations.py**: Tests de creación y gestión de carteras
- **test_operation_flow.py**: Tests del flujo completo de registro de operaciones
- **test_market_data_integration.py**: Tests de integración con Alpha Vantage API
- **test_ai_analysis_integration.py**: Tests de integración con OpenAI API

### fixtures/
- **database.py**: Fixtures para base de datos de prueba
- **users.py**: Datos de prueba para usuarios
- **portfolios.py**: Datos de prueba para carteras
- **operations.py**: Datos de prueba para operaciones
- **market_data.py**: Datos de prueba para datos de mercado

## Configuración

- **conftest.py**: Configuración de pytest con fixtures compartidas
- **pytest.ini**: Configuración de pytest (marcadores, paths, opciones)

## Cobertura

Las pruebas cubren:

- Funcionalidad de todos los endpoints API
- Lógica de negocio de todos los servicios
- Operaciones de todos los repositorios
- Integraciones con servicios externos
- Manejo de errores y casos límite
- Validaciones de datos y seguridad

## Ejecución

Las pruebas se ejecutan mediante:

- `pytest`: Ejecuta todas las pruebas
- `pytest tests/unit/`: Ejecuta solo pruebas unitarias
- `pytest tests/integration/`: Ejecuta solo pruebas de integración
- `pytest --cov`: Ejecuta pruebas con reporte de cobertura


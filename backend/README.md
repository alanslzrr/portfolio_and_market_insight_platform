# Backend - API REST

Este directorio contiene la implementación completa del backend de la plataforma, desarrollado utilizando FastAPI como framework principal. El backend sigue una arquitectura en capas que separa claramente las responsabilidades entre la presentación, la lógica de negocio y el acceso a datos.

## Estructura del Backend

El backend está organizado en módulos que reflejan la arquitectura en capas del sistema:

- **app/api/**: Contiene los endpoints HTTP que exponen la funcionalidad de la plataforma a través de una API REST. Los endpoints están organizados por dominios de negocio (autenticación, carteras, operaciones, usuarios, mercado).

- **app/core/**: Contiene la configuración central del sistema, incluyendo la configuración de la aplicación, la conexión a la base de datos, y los componentes de seguridad como el manejo de tokens JWT y el hashing de contraseñas.

- **app/models/**: Define las entidades del dominio utilizando SQLAlchemy. Estos modelos representan las tablas de la base de datos y las relaciones entre ellas.

- **app/repositories/**: Implementa el patrón Repository para abstraer el acceso a datos. Cada repositorio proporciona métodos para realizar operaciones CRUD sobre las entidades del dominio.

- **app/schemas/**: Contiene los esquemas de Pydantic que definen la estructura de los datos de entrada y salida de la API. Estos esquemas validan los datos y proporcionan documentación automática.

- **app/services/**: Contiene la lógica de negocio de la aplicación. Los servicios coordinan las operaciones complejas, aplican las reglas de negocio y utilizan los repositorios para acceder a los datos.

- **app/middleware/**: Contiene middleware personalizado para el manejo de peticiones, como la autenticación mediante tokens JWT y el manejo de errores.

- **app/utils/**: Contiene utilidades y funciones auxiliares que pueden ser utilizadas en diferentes partes de la aplicación.

## Archivos Principales

- **requirements.txt**: Define las dependencias de Python necesarias para el backend, incluyendo FastAPI, SQLAlchemy, Pydantic, y otras librerías utilizadas.

- **main.py**: Punto de entrada principal de la aplicación FastAPI. Configura la aplicación, registra los routers y maneja el ciclo de vida de la aplicación.

- **.env.example**: Archivo de ejemplo que muestra las variables de entorno necesarias para configurar el backend, incluyendo las claves de API, la configuración de la base de datos y otros secretos.

## Configuración

El backend requiere configuración mediante variables de entorno para funcionar correctamente. Las variables principales incluyen la URL de la base de datos PostgreSQL, las claves de API para Alpha Vantage y OpenAI, y la configuración de seguridad para los tokens JWT.


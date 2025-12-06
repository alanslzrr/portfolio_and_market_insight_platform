"""
Punto de entrada principal de la aplicacion FastAPI.

Este modulo constituye el nucleo de la aplicacion web, implementando el patron
de arquitectura de microservicios mediante FastAPI. Se encarga de:

- Inicializacion y configuracion de la aplicacion FastAPI
- Registro de routers para endpoints versionados (API v1)
- Configuracion de middleware CORS para comunicacion cross-origin
- Registro de manejadores de excepciones globales
- Definicion de endpoints de health check para monitoreo
- Gestion de eventos de ciclo de vida (startup/shutdown)

El sistema sigue el principio de separacion de responsabilidades, donde este
archivo actua como punto de entrada y orquestador, delegando la logica especifica
a los modulos correspondientes.

Ejecucion:
    Desarrollo: uvicorn main:app --reload --port 8000
    Produccion: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

Autor: Sistema de Arquitectura de Software
Institucion: Universidad
Fecha: Diciembre 2025
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.api.v1 import api_router
from app.core.config import settings
from app.middleware.error_handler import register_exception_handlers

# Configuracion del sistema de logging
# El logging centralizado facilita el debugging y el monitoreo en produccion
# Se utiliza el formato estandar con timestamps para auditoria
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


# ============================================================================
# INSTANCIACION DE LA APLICACION FASTAPI
# ============================================================================

app = FastAPI(
    title="Portfolio & Market Insight Platform",
    description="""
    Plataforma de gestion de carteras de inversion con analisis asistido por IA.
    
    ## Descripcion
    
    Sistema integral para la gestion de portfolios de inversion que integra:
    - Gestion de carteras multi-activo (acciones, criptomonedas, etc)
    - Registro y seguimiento de operaciones financieras
    - Consulta de datos de mercado en tiempo real via Alpha Vantage
    - Analisis asistido por inteligencia artificial usando GPT-5
    - Calculo automatico de indicadores tecnicos (RSI, MACD, MAs)
    - Metricas de rendimiento con precision decimal
    
    ## Funcionalidades
    
    * **Autenticacion**: Sistema JWT completo con registro y login
    * **Usuarios**: Gestion de perfil y preferencias de usuario
    * **Portfolios**: CRUD completo de carteras de inversion
    * **Operaciones**: Registro de compras y ventas de activos
    * **Mercado**: Consulta de cotizaciones y datos historicos
    * **Analisis IA**: Generacion de analisis financieros automatizados
    
    ## Autenticacion
    
    La mayoria de endpoints requieren autenticacion mediante JWT:
    
    1. Registrar usuario: `POST /api/v1/auth/register`
    2. Iniciar sesion: `POST /api/v1/auth/login`
    3. Incluir token en el header: `Authorization: Bearer <access_token>`
    
    ## Arquitectura
    
    El backend implementa una arquitectura en capas:
    - API Layer: Endpoints REST versionados
    - Service Layer: Logica de negocio
    - Repository Layer: Acceso a datos
    - Domain Layer: Modelos y entidades
    
    Ver documentacion completa en /docs/ARQUITECTURA.md
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============================================================================
# CONFIGURACION DE CORS (Cross-Origin Resource Sharing)
# ============================================================================
# Permite que el frontend (u otros origenes) puedan consumir la API
# En produccion, settings.cors_origins debe contener solo dominios confiables

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REGISTRO DE MANEJADORES DE EXCEPCIONES
# ============================================================================
# Centraliza el manejo de errores para respuestas HTTP consistentes

register_exception_handlers(app)


# ============================================================================
# REGISTRO DE ROUTERS DE API
# ============================================================================
# Incluye todos los endpoints versionados bajo /api/v1/

app.include_router(api_router)


# ============================================================================
# ENDPOINTS DE HEALTH CHECK Y MONITOREO
# ============================================================================

@app.get("/", tags=["Health"])
def root():
    """
    Endpoint raiz de la API.
    
    Proporciona informacion basica sobre la API y enlaces a la documentacion.
    Util como punto de verificacion rapida de que el servidor esta activo.
    
    Returns:
        dict: Mensaje de bienvenida y enlaces a recursos
    """
    return {
        "message": "Portfolio & Market Insight Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Verifica el estado general de la aplicacion.
    
    Health check basico que confirma que la aplicacion esta corriendo.
    Este endpoint es utilizado por load balancers y sistemas de monitoreo
    para determinar si la instancia de la aplicacion esta saludable.
    
    Returns:
        dict: Estado de la aplicacion, version y entorno
        
    Status Codes:
        200: Aplicacion funcionando correctamente
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/db", tags=["Health"])
def health_check_db():
    """
    Verifica la conectividad con la base de datos.
    
    Health check avanzado que prueba la conexion a PostgreSQL ejecutando
    una query simple. Util para diagnosticar problemas de conectividad
    de base de datos en ambientes de produccion.
    
    Returns:
        dict: Estado de la base de datos y mensaje de error si aplica
        
    Status Codes:
        200: Base de datos conectada y respondiendo
        200: Base de datos no disponible (status: unhealthy)
    """
    from sqlalchemy import text
    from app.core.database.session import SessionLocal
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected", 
            "error": str(e)
        }


# ============================================================================
# EVENTOS DE CICLO DE VIDA DE LA APLICACION
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Manejador de evento de inicio de la aplicacion.
    
    Este evento se dispara cuando la aplicacion inicia. Se utiliza para:
    - Inicializar conexiones a servicios externos
    - Cargar configuraciones en memoria
    - Registrar el inicio en logs
    - Realizar validaciones de pre-inicio
    
    En el futuro podria incluir:
    - Inicializacion de conexion a Redis para cache
    - Conexion a servicios de mensajeria (RabbitMQ, Kafka)
    - Calentamiento de cache con datos frecuentes
    """
    print("=" * 70)
    print("Portfolio & Market Insight Platform API - Iniciando")
    print("=" * 70)
    print(f"Entorno: {settings.ENVIRONMENT}")
    print(f"Documentacion interactiva: /docs")
    print(f"Documentacion alternativa: /redoc")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Manejador de evento de cierre de la aplicacion.
    
    Este evento se dispara cuando la aplicacion se detiene. Se utiliza para:
    - Cerrar conexiones a bases de datos limpiamente
    - Finalizar sesiones activas
    - Guardar estado si es necesario
    - Liberar recursos del sistema
    
    Garantiza un shutdown graceful que permite completar requests en curso
    y cerrar conexiones de manera ordenada.
    """
    print("=" * 70)
    print("Portfolio & Market Insight Platform API - Cerrando")
    print("=" * 70)

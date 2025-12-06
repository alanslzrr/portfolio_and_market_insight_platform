"""
api v1 - endpoints de la aplicacion.

este paquete contiene todos los routers de la version 1 de la api:
- auth: autenticacion (register, login, logout)
- users: gestion de usuarios
- portfolios: gestion de carteras
- operations: operaciones de compra/venta
- market: datos de mercado y catalogo de activos
- analysis: analisis con inteligencia artificial
"""
from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.portfolios.router import router as portfolios_router
from app.api.v1.operations.router import router as operations_router
from app.api.v1.market.router import router as market_router
from app.api.v1.analysis.router import router as analysis_router


# router principal que agrupa todos los sub-routers
api_router = APIRouter(prefix="/api/v1")

# registrar sub-routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(portfolios_router)
api_router.include_router(operations_router)
api_router.include_router(market_router)
api_router.include_router(analysis_router)

__all__ = ["api_router"]

"""
market api endpoints.

proporciona acceso a:
- catalogo de activos financieros
- precios actuales e historicos
- busqueda de activos
"""
from app.api.v1.market.router import router

__all__ = ["router"]

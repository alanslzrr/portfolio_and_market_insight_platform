"""
modelos de dominio (orm).

este paquete contiene todos los modelos de sqlalchemy que representan
las entidades del dominio de negocio.

estructura:
- user.py: usuario, perfil y sesiones
- portfolio.py: carteras y posiciones de activos
- operation.py: operaciones de compra/venta
- asset.py: catalogo de activos y precios
- analysis.py: analisis generados por ia

todos los modelos heredan de base (declarative_base de sqlalchemy)
y se migran a la base de datos usando alembic.
"""
from app.models.user import User, UserProfile, UserSession
from app.models.portfolio import Portfolio, PortfolioAsset
from app.models.operation import Operation, OperationType
from app.models.asset import Asset, AssetPrice, AssetType
from app.models.analysis import Analysis, AnalysisRequest, AnalysisType, AnalysisStatus

__all__ = [
    # user models
    "User",
    "UserProfile",
    "UserSession",
    # Portfolio models
    "Portfolio",
    "PortfolioAsset",
    # Operation models
    "Operation",
    "OperationType",
    # Asset models
    "Asset",
    "AssetPrice",
    "AssetType",
    # Analysis models
    "Analysis",
    "AnalysisRequest",
    "AnalysisType",
    "AnalysisStatus",
]

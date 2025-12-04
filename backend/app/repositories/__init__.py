"""
repositorios (patron repository).

este paquete implementa el patron repository para abstraer el acceso a datos.

beneficios del patron repository:
- separa logica de acceso a datos de logica de negocio
- facilita testing (se puede mockear)
- centraliza queries complejas
- permite cambiar la implementacion de bd sin afectar servicios

estructura:
- base.py: repositorio generico con crud basico
- user.py: gestion de usuarios, perfiles y sesiones
- portfolio.py: gestion de carteras y posiciones
- operation.py: gestion de operaciones financieras
- asset.py: gestion de activos y precios
- analysis.py: gestion de analisis con ia
"""
from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.portfolio import PortfolioRepository
from app.repositories.operation import OperationRepository
from app.repositories.asset import AssetRepository
from app.repositories.analysis import AnalysisRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "PortfolioRepository",
    "OperationRepository",
    "AssetRepository",
    "AnalysisRepository",
]

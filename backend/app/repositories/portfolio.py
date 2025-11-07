"""
repositorio para gestion de portfolios y posiciones.

maneja operaciones relacionadas con carteras de inversion y sus activos.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload

from app.repositories.base import BaseRepository
from app.models.portfolio import Portfolio, PortfolioAsset


class PortfolioRepository(BaseRepository[Portfolio]):
    """repositorio para operaciones de portfolios."""
    
    def __init__(self, db: Session):
        super().__init__(Portfolio, db)
    
    def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Portfolio]:
        """
        obtiene todos los portfolios de un usuario.
        
        args:
            user_id: id del usuario
            skip: offset para paginacion
            limit: limite de resultados
            
        returns:
            lista de portfolios del usuario
        """
        return self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_with_positions(self, portfolio_id: UUID) -> Optional[Portfolio]:
        """
        obtiene portfolio con todas sus posiciones cargadas (eager loading).
        
        args:
            portfolio_id: id del portfolio
            
        returns:
            portfolio con posiciones cargadas
        """
        return self.db.query(Portfolio).options(
            joinedload(Portfolio.assets)
        ).filter(Portfolio.id == portfolio_id).first()
    
    def get_by_user_and_name(self, user_id: UUID, name: str) -> Optional[Portfolio]:
        """
        busca portfolio por usuario y nombre.
        
        util para validar nombres unicos por usuario.
        
        args:
            user_id: id del usuario
            name: nombre del portfolio
            
        returns:
            portfolio si existe
        """
        return self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id,
            Portfolio.name == name
        ).first()
    
    def create_or_update_position(self, portfolio_id: UUID, asset_symbol: str, 
                                   quantity: Decimal, average_price: Decimal, 
                                   current_price: Decimal) -> PortfolioAsset:
        """
        crea o actualiza una posicion de activo en el portfolio (upsert).
        
        args:
            portfolio_id: id del portfolio
            asset_symbol: simbolo del activo
            quantity: cantidad
            average_price: precio promedio
            current_price: precio actual
            
        returns:
            portfolioasset creado o actualizado
        """
        position = self.db.query(PortfolioAsset).filter(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_symbol == asset_symbol
        ).first()
        
        if position:
            # actualizar posicion existente
            position.quantity = quantity
            position.average_price = average_price
            position.current_price = current_price
        else:
            # crear nueva posicion
            position = PortfolioAsset(
                portfolio_id=portfolio_id,
                asset_symbol=asset_symbol,
                quantity=quantity,
                average_price=average_price,
                current_price=current_price
            )
            self.db.add(position)
        
        self.db.commit()
        self.db.refresh(position)
        return position
    
    def get_position(self, portfolio_id: UUID, asset_symbol: str) -> Optional[PortfolioAsset]:
        """
        obtiene una posicion especifica del portfolio.
        
        args:
            portfolio_id: id del portfolio
            asset_symbol: simbolo del activo
            
        returns:
            posicion si existe
        """
        return self.db.query(PortfolioAsset).filter(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.asset_symbol == asset_symbol
        ).first()
    
    def delete_position(self, portfolio_id: UUID, asset_symbol: str) -> bool:
        """
        elimina una posicion del portfolio.
        
        args:
            portfolio_id: id del portfolio
            asset_symbol: simbolo del activo
            
        returns:
            true si se elimino
        """
        position = self.get_position(portfolio_id, asset_symbol)
        if position:
            self.db.delete(position)
            self.db.commit()
            return True
        return False
    
    def calculate_portfolio_metrics(self, portfolio_id: UUID) -> None:
        """
        calcula y actualiza las metricas del portfolio.
        
        llama al metodo calculate_metrics() del modelo portfolio.
        
        args:
            portfolio_id: id del portfolio
        """
        portfolio = self.get_with_positions(portfolio_id)
        if portfolio:
            portfolio.calculate_metrics()
            self.db.commit()

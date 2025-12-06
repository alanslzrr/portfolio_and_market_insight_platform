"""
repositorio para gestion de operaciones financieras.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.operation import Operation, OperationType


class OperationRepository(BaseRepository[Operation]):
    """repositorio para operaciones de compra/venta."""
    
    def __init__(self, db: Session):
        super().__init__(Operation, db)
    
    def get_by_portfolio(self, portfolio_id: UUID, skip: int = 0, limit: int = 100) -> List[Operation]:
        """obtiene operaciones de un portfolio."""
        return self.db.query(Operation).filter(
            Operation.portfolio_id == portfolio_id
        ).order_by(Operation.operation_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_asset(self, portfolio_id: UUID, asset_symbol: str) -> List[Operation]:
        """obtiene operaciones de un activo especifico en un portfolio."""
        return self.db.query(Operation).filter(
            Operation.portfolio_id == portfolio_id,
            Operation.asset_symbol == asset_symbol.upper()
        ).order_by(Operation.operation_date.desc()).all()
    
    def get_by_type(self, portfolio_id: UUID, operation_type: OperationType) -> List[Operation]:
        """obtiene operaciones por tipo (BUY o SELL)."""
        return self.db.query(Operation).filter(
            Operation.portfolio_id == portfolio_id,
            Operation.operation_type == operation_type
        ).order_by(Operation.operation_date.desc()).all()
    
    def get_by_date_range(self, portfolio_id: UUID,
                          date_from: Optional[date] = None,
                          date_to: Optional[date] = None) -> List[Operation]:
        """obtiene operaciones en un rango de fechas."""
        query = self.db.query(Operation).filter(
            Operation.portfolio_id == portfolio_id
        )
        
        if date_from:
            query = query.filter(Operation.operation_date >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.filter(Operation.operation_date <= datetime.combine(date_to, datetime.max.time()))
        
        return query.order_by(Operation.operation_date.desc()).all()
    
    def filter_operations(self, portfolio_id: UUID,
                          asset_symbol: Optional[str] = None,
                          operation_type: Optional[OperationType] = None,
                          date_from: Optional[date] = None,
                          date_to: Optional[date] = None,
                          skip: int = 0, limit: int = 100) -> List[Operation]:
        """filtra operaciones por multiples criterios."""
        query = self.db.query(Operation).filter(
            Operation.portfolio_id == portfolio_id
        )
        
        if asset_symbol:
            query = query.filter(Operation.asset_symbol == asset_symbol.upper())
        if operation_type:
            query = query.filter(Operation.operation_type == operation_type)
        if date_from:
            query = query.filter(Operation.operation_date >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.filter(Operation.operation_date <= datetime.combine(date_to, datetime.max.time()))
        
        return query.order_by(Operation.operation_date.desc()).offset(skip).limit(limit).all()
    
    def count_by_portfolio(self, portfolio_id: UUID) -> int:
        """cuenta operaciones de un portfolio."""
        return self.db.query(Operation).filter(
            Operation.portfolio_id == portfolio_id
        ).count()

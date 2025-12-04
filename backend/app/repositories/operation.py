"""
repositorio para gestion de operaciones financieras.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
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
    
    def filter_by_criteria(self, portfolio_id: Optional[UUID] = None,
                          asset_symbol: Optional[str] = None,
                          operation_type: Optional[OperationType] = None,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None,
                          skip: int = 0, limit: int = 100) -> List[Operation]:
        """filtra operaciones por multiples criterios."""
        query = self.db.query(Operation)
        
        if portfolio_id:
            query = query.filter(Operation.portfolio_id == portfolio_id)
        if asset_symbol:
            query = query.filter(Operation.asset_symbol == asset_symbol.upper())
        if operation_type:
            query = query.filter(Operation.operation_type == operation_type)
        if date_from:
            query = query.filter(Operation.operation_date >= date_from)
        if date_to:
            query = query.filter(Operation.operation_date <= date_to)
        
        return query.order_by(Operation.operation_date.desc()).offset(skip).limit(limit).all()

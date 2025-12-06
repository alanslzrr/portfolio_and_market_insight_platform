"""
servicio de operaciones - logica de negocio para operaciones financieras.

proporciona funcionalidades adicionales para gestion de operaciones:
- consultas y filtrado avanzado
- actualizacion y eliminacion de operaciones
- estadisticas de operaciones

nota: la creacion de operaciones y actualizacion de posiciones
se maneja en portfolioservice para mantener la coherencia transaccional.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.operation import Operation, OperationType
from app.repositories.operation import OperationRepository
from app.repositories.portfolio import PortfolioRepository


class OperationService:
    """
    servicio para consultas y gestion de operaciones.
    
    complementa portfolioservice con funcionalidades adicionales
    enfocadas en la gestion individual de operaciones.
    """
    
    def __init__(self, db: Session):
        """
        inicializa el servicio.
        
        args:
            db: sesion de base de datos
        """
        self.db = db
        self.operation_repo = OperationRepository(db)
        self.portfolio_repo = PortfolioRepository(db)
    
    def get_operation(self, operation_id: UUID) -> Optional[Operation]:
        """
        obtiene una operacion por su id.
        
        args:
            operation_id: id de la operacion
            
        returns:
            operacion o none si no existe
        """
        return self.operation_repo.get_by_id(operation_id)
    
    def get_operations_by_portfolio(self, portfolio_id: UUID, 
                                     skip: int = 0, 
                                     limit: int = 100) -> List[Operation]:
        """
        obtiene operaciones de un portfolio con paginacion.
        
        args:
            portfolio_id: id del portfolio
            skip: registros a saltar
            limit: maximo de registros
            
        returns:
            lista de operaciones
        """
        return self.operation_repo.get_by_portfolio(portfolio_id, skip, limit)
    
    def get_operations_by_asset(self, portfolio_id: UUID, 
                                 asset_symbol: str) -> List[Operation]:
        """
        obtiene todas las operaciones de un activo en un portfolio.
        
        args:
            portfolio_id: id del portfolio
            asset_symbol: simbolo del activo
            
        returns:
            lista de operaciones
        """
        return self.operation_repo.get_by_asset(portfolio_id, asset_symbol.upper())
    
    def get_operations_by_type(self, portfolio_id: UUID, 
                                operation_type: OperationType) -> List[Operation]:
        """
        filtra operaciones por tipo (BUY o SELL).
        
        args:
            portfolio_id: id del portfolio
            operation_type: tipo de operacion
            
        returns:
            lista de operaciones
        """
        return self.operation_repo.get_by_type(portfolio_id, operation_type)
    
    def get_operations_by_date_range(self, portfolio_id: UUID,
                                      date_from: Optional[date] = None,
                                      date_to: Optional[date] = None) -> List[Operation]:
        """
        filtra operaciones por rango de fechas.
        
        args:
            portfolio_id: id del portfolio
            date_from: fecha inicio (inclusive)
            date_to: fecha fin (inclusive)
            
        returns:
            lista de operaciones en el rango
        """
        return self.operation_repo.get_by_date_range(portfolio_id, date_from, date_to)
    
    def filter_operations(self, portfolio_id: UUID,
                          asset_symbol: Optional[str] = None,
                          operation_type: Optional[OperationType] = None,
                          date_from: Optional[date] = None,
                          date_to: Optional[date] = None,
                          skip: int = 0,
                          limit: int = 100) -> List[Operation]:
        """
        filtra operaciones con multiples criterios.
        
        todos los filtros son opcionales y se combinan con AND.
        
        args:
            portfolio_id: id del portfolio
            asset_symbol: filtrar por activo
            operation_type: filtrar por tipo
            date_from: fecha inicio
            date_to: fecha fin
            skip: offset para paginacion
            limit: maximo de resultados
            
        returns:
            lista de operaciones que cumplen los criterios
        """
        return self.operation_repo.filter_operations(
            portfolio_id=portfolio_id,
            asset_symbol=asset_symbol.upper() if asset_symbol else None,
            operation_type=operation_type,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit
        )
    
    def update_operation_notes(self, operation_id: UUID, 
                                notes: Optional[str]) -> Optional[Operation]:
        """
        actualiza las notas de una operacion.
        
        solo las notas pueden actualizarse, los valores financieros son inmutables.
        
        args:
            operation_id: id de la operacion
            notes: nuevas notas
            
        returns:
            operacion actualizada o none si no existe
        """
        operation = self.operation_repo.get_by_id(operation_id)
        if not operation:
            return None
        
        operation.notes = notes
        return self.operation_repo.update(operation)
    
    def count_operations(self, portfolio_id: UUID) -> int:
        """
        cuenta el total de operaciones en un portfolio.
        
        args:
            portfolio_id: id del portfolio
            
        returns:
            numero de operaciones
        """
        return self.operation_repo.count_by_portfolio(portfolio_id)
    
    def get_portfolio_statistics(self, portfolio_id: UUID) -> dict:
        """
        obtiene estadisticas de operaciones de un portfolio.
        
        args:
            portfolio_id: id del portfolio
            
        returns:
            diccionario con estadisticas:
            - total_operations: numero total
            - total_buys: numero de compras
            - total_sells: numero de ventas
            - total_invested: suma de compras
            - total_withdrawn: suma de ventas
            - total_fees: suma de comisiones
            - unique_assets: numero de activos distintos
        """
        operations = self.operation_repo.get_by_portfolio(portfolio_id, skip=0, limit=10000)
        
        stats = {
            "total_operations": 0,
            "total_buys": 0,
            "total_sells": 0,
            "total_invested": Decimal("0"),
            "total_withdrawn": Decimal("0"),
            "total_fees": Decimal("0"),
            "unique_assets": set()
        }
        
        for op in operations:
            stats["total_operations"] += 1
            stats["total_fees"] += op.fees
            stats["unique_assets"].add(op.asset_symbol)
            
            if op.operation_type == OperationType.BUY:
                stats["total_buys"] += 1
                stats["total_invested"] += op.total_amount
            else:
                stats["total_sells"] += 1
                stats["total_withdrawn"] += op.total_amount
        
        # convertir set a count
        stats["unique_assets"] = len(stats["unique_assets"])
        
        return stats
    
    def get_asset_statistics(self, portfolio_id: UUID, asset_symbol: str) -> dict:
        """
        obtiene estadisticas de operaciones para un activo especifico.
        
        args:
            portfolio_id: id del portfolio
            asset_symbol: simbolo del activo
            
        returns:
            diccionario con estadisticas del activo
        """
        operations = self.operation_repo.get_by_asset(portfolio_id, asset_symbol.upper())
        
        stats = {
            "asset_symbol": asset_symbol.upper(),
            "total_operations": 0,
            "total_buys": 0,
            "total_sells": 0,
            "total_quantity_bought": Decimal("0"),
            "total_quantity_sold": Decimal("0"),
            "average_buy_price": Decimal("0"),
            "average_sell_price": Decimal("0"),
            "first_operation_date": None,
            "last_operation_date": None
        }
        
        buy_total = Decimal("0")
        sell_total = Decimal("0")
        
        for op in operations:
            stats["total_operations"] += 1
            
            if op.operation_type == OperationType.BUY:
                stats["total_buys"] += 1
                stats["total_quantity_bought"] += op.quantity
                buy_total += op.quantity * op.price
            else:
                stats["total_sells"] += 1
                stats["total_quantity_sold"] += op.quantity
                sell_total += op.quantity * op.price
            
            # actualizar fechas
            if stats["first_operation_date"] is None or op.operation_date < stats["first_operation_date"]:
                stats["first_operation_date"] = op.operation_date
            if stats["last_operation_date"] is None or op.operation_date > stats["last_operation_date"]:
                stats["last_operation_date"] = op.operation_date
        
        # calcular promedios
        if stats["total_quantity_bought"] > 0:
            stats["average_buy_price"] = buy_total / stats["total_quantity_bought"]
        if stats["total_quantity_sold"] > 0:
            stats["average_sell_price"] = sell_total / stats["total_quantity_sold"]
        
        return stats


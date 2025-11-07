"""
servicio de portfolios - logica de negocio para gestion de carteras.

coordina operaciones complejas de portfolios, validaciones de permisos,
y actualizacion de metricas financieras.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.operation import Operation, OperationType
from app.repositories.portfolio import PortfolioRepository
from app.repositories.operation import OperationRepository


class PortfolioService:
    """
    servicio para operaciones de portfolios.
    
    proporciona metodos de alto nivel para:
    - crear y gestionar portfolios
    - registrar operaciones de compra/venta
    - actualizar posiciones y metricas
    - calcular rendimiento
    """
    
    def __init__(self, db: Session):
        """
        inicializa el servicio.
        
        args:
            db: sesion de base de datos
        """
        self.db = db
        self.portfolio_repo = PortfolioRepository(db)
        self.operation_repo = OperationRepository(db)
    
    def create_portfolio(self, user_id: UUID, name: str, 
                        description: Optional[str] = None,
                        base_currency: str = "USD") -> Portfolio:
        """
        crea un nuevo portfolio para un usuario.
        
        validaciones:
        - el nombre debe ser unico por usuario
        - la moneda debe ser valida
        
        args:
            user_id: id del usuario propietario
            name: nombre del portfolio
            description: descripcion opcional
            base_currency: moneda base (default USD)
            
        returns:
            portfolio creado
            
        raises:
            ValueError: si ya existe un portfolio con ese nombre
        """
        # validar nombre unico
        existing = self.portfolio_repo.get_by_user_and_name(user_id, name)
        if existing:
            raise ValueError(f"ya existe un portfolio llamado '{name}' para este usuario")
        
        # crear portfolio
        portfolio = Portfolio(
            user_id=user_id,
            name=name.strip(),
            description=description,
            base_currency=base_currency.upper(),
            total_value=Decimal('0'),
            total_cost=Decimal('0'),
            total_gain_loss=Decimal('0'),
            total_gain_loss_percent=Decimal('0')
        )
        
        created = self.portfolio_repo.create(portfolio)
        return created
    
    def get_portfolio(self, portfolio_id: UUID) -> Optional[Portfolio]:
        """
        obtiene un portfolio con todas sus posiciones.
        
        args:
            portfolio_id: id del portfolio
            
        returns:
            portfolio con posiciones cargadas o none
        """
        portfolio = self.portfolio_repo.get_with_positions(portfolio_id)
        return portfolio
    
    def update_portfolio(self, portfolio_id: UUID, name: Optional[str] = None,
                        description: Optional[str] = None) -> Optional[Portfolio]:
        """
        actualiza informacion de un portfolio.
        
        args:
            portfolio_id: id del portfolio
            name: nuevo nombre (opcional)
            description: nueva descripcion (opcional)
            
        returns:
            portfolio actualizado o none
        """
        portfolio = self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            return None
        
        if name is not None:
            portfolio.name = name.strip()
        if description is not None:
            portfolio.description = description
        
        updated = self.portfolio_repo.update(portfolio)
        return updated
    
    def delete_portfolio(self, portfolio_id: UUID) -> bool:
        """
        elimina un portfolio y todas sus posiciones.
        
        args:
            portfolio_id: id del portfolio
            
        returns:
            true si se elimino, false si no existia
        """
        portfolio = self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            return False
        
        name = portfolio.name
        result = self.portfolio_repo.delete(portfolio_id)
        return result
    
    def add_operation(self, portfolio_id: UUID, asset_symbol: str,
                     operation_type: OperationType, quantity: Decimal,
                     price: Decimal, fees: Decimal = Decimal('0'),
                     notes: Optional[str] = None) -> Operation:
        """
        registra una operacion de compra o venta.
        
        actualiza automaticamente:
        - la posicion del activo en el portfolio
        - las metricas del portfolio
        
        args:
            portfolio_id: id del portfolio
            asset_symbol: simbolo del activo
            operation_type: BUY o SELL
            quantity: cantidad operada
            price: precio unitario
            fees: comisiones (default 0)
            notes: notas opcionales
            
        returns:
            operacion creada
        """
        from datetime import datetime
        
        # crear operacion
        operation = Operation(
            portfolio_id=portfolio_id,
            asset_symbol=asset_symbol.upper(),
            operation_type=operation_type,
            quantity=quantity,
            price=price,
            fees=fees,
            operation_date=datetime.utcnow(),
            notes=notes
        )
        
        # calcular total_amount
        operation.total_amount = operation.calculate_total()
        
        # guardar operacion
        created_op = self.operation_repo.create(operation)
        
        # actualizar posicion en el portfolio
        self._update_position_from_operation(created_op)
        
        # recalcular metricas del portfolio
        self.portfolio_repo.calculate_portfolio_metrics(portfolio_id)
        
        return created_op
    
    def _update_position_from_operation(self, operation: Operation) -> None:
        """
        actualiza la posicion de un activo basado en una operacion.
        
        implementa logica de promedio ponderado para el precio.
        
        args:
            operation: operacion a procesar
        """
        position = self.portfolio_repo.get_position(
            operation.portfolio_id,
            operation.asset_symbol
        )
        
        if operation.operation_type == OperationType.BUY:
            if position:
                # actualizar posicion existente con promedio ponderado
                total_cost = (position.quantity * position.average_price) + \
                            (operation.quantity * operation.price)
                new_quantity = position.quantity + operation.quantity
                new_avg_price = total_cost / new_quantity
                
                self.portfolio_repo.create_or_update_position(
                    operation.portfolio_id,
                    operation.asset_symbol,
                    new_quantity,
                    new_avg_price,
                    operation.price  # usar precio de operacion como current_price
                )
            else:
                # crear nueva posicion
                self.portfolio_repo.create_or_update_position(
                    operation.portfolio_id,
                    operation.asset_symbol,
                    operation.quantity,
                    operation.price,
                    operation.price
                )
        
        elif operation.operation_type == OperationType.SELL:
            if not position:
                raise ValueError(f"no hay posicion de {operation.asset_symbol} para vender")
            
            if position.quantity < operation.quantity:
                raise ValueError(
                    f"cantidad insuficiente: tienes {position.quantity}, "
                    f"intentas vender {operation.quantity}"
                )
            
            # reducir cantidad (mantener precio promedio)
            new_quantity = position.quantity - operation.quantity
            
            if new_quantity == 0:
                # cerrar posicion
                self.portfolio_repo.delete_position(
                    operation.portfolio_id,
                    operation.asset_symbol
                )
            else:
                # actualizar cantidad
                self.portfolio_repo.create_or_update_position(
                    operation.portfolio_id,
                    operation.asset_symbol,
                    new_quantity,
                    position.average_price,  # mantener precio promedio
                    operation.price  # actualizar precio actual
                )
    
    def get_portfolio_operations(self, portfolio_id: UUID, 
                                skip: int = 0, limit: int = 100) -> List[Operation]:
        """
        obtiene el historial de operaciones de un portfolio.
        
        args:
            portfolio_id: id del portfolio
            skip: offset para paginacion
            limit: limite de resultados
            
        returns:
            lista de operaciones ordenadas por fecha descendente
        """
        operations = self.operation_repo.get_by_portfolio(portfolio_id, skip, limit)
        return operations
    
    def list_user_portfolios(self, user_id: UUID) -> List[Portfolio]:
        """
        lista todos los portfolios de un usuario.
        
        args:
            user_id: id del usuario
            
        returns:
            lista de portfolios
        """
        portfolios = self.portfolio_repo.get_by_user_id(user_id)
        return portfolios

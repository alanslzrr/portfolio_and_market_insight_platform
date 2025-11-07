"""
modelos orm para operaciones financieras (compra/venta).

define:
- OperationType: enum para tipos de operacion (BUY, SELL)
- Operation: modelo que registra cada transaccion de compra o venta

cada operacion queda registrada para:
1. auditoria: historial completo de transacciones
2. reportes: analisis de rendimiento y fiscales
3. calculos: actualizacion de precio promedio en posiciones
"""
import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class OperationType(str, enum.Enum):
    """
    tipo de operacion financiera.
    
    BUY: compra de activos (aumenta posicion)
    SELL: venta de activos (disminuye posicion)
    
    heredamos de str para que sea json-serializable automaticamente
    (util para apis rest).
    """
    BUY = "BUY"
    SELL = "SELL"


class Operation(Base):
    """
    registro de una operacion de compra o venta de activos.
    
    cada operacion afecta la posicion de un activo en un portfolio:
    - BUY: aumenta quantity, actualiza average_price
    - SELL: disminuye quantity, realiza ganancia/perdida
    
    los fees (comisiones) se registran por separado para transparencia.
    el total_amount incluye fees para reflejar el costo/ingreso real.
    
    campos:
        id: uuid de la operacion
        portfolio_id: portfolio donde se ejecuta
        asset_symbol: activo operado
        operation_type: BUY o SELL
        quantity: cantidad de activos operados
        price: precio unitario de ejecucion
        fees: comisiones de la operacion
        total_amount: monto total (cantidad × precio ± fees)
        operation_date: fecha/hora de la operacion
        notes: notas opcionales del usuario
    """
    __tablename__ = "operations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # foreign key al portfolio
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # informacion de la operacion
    asset_symbol = Column(String(20), nullable=False, index=True)
    operation_type = Column(SQLEnum(OperationType), nullable=False)
    
    # datos financieros
    # quantity: 20 digitos con 8 decimales (para crypto)
    quantity = Column(Numeric(20, 8), nullable=False)
    
    # price: precio unitario al que se ejecuto la operacion
    price = Column(Numeric(15, 2), nullable=False)
    
    # fees: comisiones del broker/exchange
    fees = Column(Numeric(10, 2), default=0, nullable=False)
    
    # total_amount: se calcula diferente segun tipo de operacion
    # BUY: (quantity × price) + fees (lo que pagamos)
    # SELL: (quantity × price) - fees (lo que recibimos)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # fecha de la operacion (puede ser diferente a created_at si se registra retroactivamente)
    operation_date = Column(DateTime, nullable=False, index=True)
    
    # notas opcionales del usuario
    notes = Column(Text, nullable=True)
    
    # timestamps de auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # relacion con Portfolio
    portfolio = relationship("Portfolio", back_populates="operations")
    
    # constraints: valores deben ser positivos (validacion a nivel de bd)
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('price > 0', name='check_price_positive'),
        CheckConstraint('fees >= 0', name='check_fees_non_negative'),
    )
    
    def calculate_total(self) -> Decimal:
        """
        calcula el monto total de la operacion segun su tipo.
        
        BUY: total = (cantidad × precio) + comisiones
             representa lo que pagamos para adquirir los activos
        
        SELL: total = (cantidad × precio) - comisiones
              representa lo que recibimos por vender los activos
        
        este metodo se llama antes de guardar la operacion para
        asegurar que total_amount siempre este correcto.
        
        returns:
            Decimal: monto total de la operacion
        """
        base_amount = self.quantity * self.price
        
        if self.operation_type == OperationType.BUY:
            # en compra, las comisiones se suman (costo total)
            return base_amount + self.fees
        else:  # SELL
            # en venta, las comisiones se restan (ingreso neto)
            return base_amount - self.fees
    
    def __repr__(self) -> str:
        return f"<Operation({self.operation_type} {self.quantity} {self.asset_symbol} @ {self.price})>"

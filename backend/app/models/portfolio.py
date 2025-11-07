"""
modelos orm para carteras de inversion (portfolios).

define los modelos de sqlalchemy para:
- Portfolio: cartera de inversion del usuario
- PortfolioAsset: posicion individual de un activo en la cartera

los calculos financieros usan Decimal para evitar errores de redondeo
tipicos de float (critico en aplicaciones financieras).
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Portfolio(Base):
    """
    cartera de inversion de un usuario.
    
    representa un portfolio con multiples activos financieros.
    un usuario puede tener varios portfolios (ej: "largo plazo", "trading", etc).
    
    el modelo mantiene metricas calculadas que se actualizan cuando cambian las posiciones.
    usamos Decimal(15, 2) que permite valores hasta 9,999,999,999,999.99 con 2 decimales.
    
    campos:
        id: uuid del portfolio
        user_id: dueño del portfolio
        name: nombre descriptivo (ej: "portfolio conservador")
        description: descripcion opcional
        base_currency: moneda base para calculos (USD, EUR, etc)
        total_value: valor actual total de todos los activos
        total_cost: costo total de adquisicion (suma de compras)
        total_gain_loss: ganancia/perdida total (total_value - total_cost)
        total_gain_loss_percent: porcentaje de ganancia/perdida
    """
    __tablename__ = "portfolios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # foreign key al usuario dueño
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # informacion del portfolio
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    base_currency = Column(String(3), default="USD", nullable=False)
    
    # metricas financieras calculadas
    # Decimal(15, 2): 15 digitos totales, 2 decimales (suficiente para millones con centavos)
    total_value = Column(Numeric(15, 2), default=0, nullable=False)  # valor actual
    total_cost = Column(Numeric(15, 2), default=0, nullable=False)  # costo de adquisicion
    total_gain_loss = Column(Numeric(15, 2), default=0, nullable=False)  # ganancia/perdida absoluta
    total_gain_loss_percent = Column(Numeric(8, 4), default=0, nullable=False)  # ganancia/perdida %
    
    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # relaciones
    user = relationship("User", back_populates="portfolios")
    assets = relationship("PortfolioAsset", back_populates="portfolio", cascade="all, delete-orphan")
    operations = relationship("Operation", back_populates="portfolio", cascade="all, delete-orphan")
    
    # constraint: un usuario no puede tener dos portfolios con el mismo nombre
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_portfolio_name'),
    )
    
    def calculate_metrics(self) -> None:
        """
        calcula y actualiza las metricas financieras del portfolio.
        
        recorre todas las posiciones (assets) y suma sus valores y costos.
        este metodo se llama despues de crear/actualizar/eliminar operaciones.
        
        la logica de calculo esta aqui (en el modelo) porque es intrinseca
        al concepto de portfolio. no es logica de negocio compleja, sino
        una propiedad del dominio.
        """
        total_value = Decimal('0.00')
        total_cost = Decimal('0.00')
        
        # sumar valores y costos de todas las posiciones
        for asset in self.assets:
            if asset.quantity > 0:  # solo considerar posiciones abiertas
                total_value += asset.calculate_position_value()
                total_cost += asset.quantity * asset.average_price
        
        self.total_value = total_value
        self.total_cost = total_cost
        self.total_gain_loss = total_value - total_cost
        
        # calcular porcentaje de ganancia/perdida (evitar division por cero)
        if total_cost > 0:
            self.total_gain_loss_percent = (self.total_gain_loss / total_cost) * Decimal('100')
        else:
            self.total_gain_loss_percent = Decimal('0.00')
    
    def __repr__(self) -> str:
        return f"<Portfolio(name='{self.name}', value={self.total_value})>"


class PortfolioAsset(Base):
    """
    posicion de un activo especifico dentro de un portfolio.
    
    representa cuanto de un activo tiene el usuario en este portfolio.
    por ejemplo: "10 acciones de AAPL a precio promedio de $150.50"
    
    el precio promedio se actualiza con cada compra usando el metodo FIFO o
    promedio ponderado (implementado en el servicio de operaciones).
    
    campos:
        id: uuid de la posicion
        portfolio_id: portfolio al que pertenece
        asset_symbol: simbolo del activo (AAPL, BTC, etc)
        quantity: cantidad de unidades del activo
        average_price: precio promedio de adquisicion
        current_price: ultimo precio conocido del mercado
    """
    __tablename__ = "portfolio_assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # foreign keys
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # informacion del activo
    # usamos el simbolo directamente en lugar de FK a Asset por simplicidad academica
    # en produccion podria ser FK para integridad referencial
    asset_symbol = Column(String(20), nullable=False)
    
    # datos de la posicion
    quantity = Column(Numeric(20, 8), nullable=False)  # 8 decimales para crypto (BTC tiene 8 decimales)
    average_price = Column(Numeric(15, 2), nullable=False)  # precio promedio de compra
    current_price = Column(Numeric(15, 2), default=0, nullable=False)  # precio actual de mercado
    
    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # relaciones
    portfolio = relationship("Portfolio", back_populates="assets")
    
    # constraint: un portfolio no puede tener dos entradas del mismo activo
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'asset_symbol', name='uq_portfolio_asset'),
    )
    
    def calculate_position_value(self) -> Decimal:
        """
        calcula el valor actual de la posicion.
        
        valor = cantidad × precio_actual
        
        returns:
            Decimal: valor total de la posicion en la moneda del portfolio
        """
        return self.quantity * self.current_price
    
    def calculate_position_gain_loss(self) -> Decimal:
        """
        calcula la ganancia/perdida de la posicion.
        
        ganancia = (precio_actual - precio_promedio) × cantidad
        
        returns:
            Decimal: ganancia o perdida de esta posicion
        """
        return (self.current_price - self.average_price) * self.quantity
    
    def calculate_position_gain_loss_percent(self) -> Decimal:
        """
        calcula el porcentaje de ganancia/perdida.
        
        returns:
            Decimal: porcentaje de ganancia/perdida
        """
        if self.average_price > 0:
            return ((self.current_price - self.average_price) / self.average_price) * Decimal('100')
        return Decimal('0.00')
    
    def __repr__(self) -> str:
        return f"<PortfolioAsset(symbol='{self.asset_symbol}', qty={self.quantity}, price={self.current_price})>"

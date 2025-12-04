"""
modelos orm para activos financieros y sus precios.

define:
- AssetType: enum para tipos de activos (STOCK, ETF, CRYPTO)
- Asset: catalogo de activos disponibles
- AssetPrice: historial de precios para analisis tecnico

el catalogo de activos se puede poblar inicialmente con activos
comunes y expandir cuando los usuarios operen nuevos simbolos.
"""
import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Text, UniqueConstraint, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AssetType(str, enum.Enum):
    """
    tipo de activo financiero.
    
    STOCK: acciones (ej: AAPL, GOOGL)
    ETF: fondos cotizados (ej: SPY, QQQ)
    CRYPTO: criptomonedas (ej: BTC, ETH)
    
    esta clasificacion es util para:
    - aplicar validaciones especificas por tipo
    - filtrar busquedas
    - mostrar informacion relevante en el ui
    """
    STOCK = "STOCK"
    ETF = "ETF"
    CRYPTO = "CRYPTO"


class Asset(Base):
    """
    catalogo de activos financieros disponibles.
    
    mantiene informacion basica de cada activo que se puede operar.
    los activos se pueden crear automaticamente cuando un usuario
    opera un simbolo nuevo (get_or_create pattern).
    
    campos:
        id: uuid del activo
        symbol: simbolo unico (AAPL, BTC, etc) - identificador principal
        name: nombre completo del activo
        asset_type: tipo (STOCK, ETF, CRYPTO)
        currency: moneda en que cotiza (USD, EUR, etc)
        exchange: bolsa o exchange donde cotiza (opcional)
        description: descripcion del activo
        is_active: flag para desactivar activos sin borrarlos
    """
    __tablename__ = "assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # simbolo unico del activo (clave de negocio)
    # lo hacemos uppercase para consistencia
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    
    # informacion del activo
    name = Column(String(255), nullable=False)
    asset_type = Column(SQLEnum(AssetType), nullable=False, index=True)
    
    # moneda en que cotiza (iso 4217)
    currency = Column(String(3), default="USD", nullable=False)
    
    # exchange/bolsa (NYSE, NASDAQ, Binance, etc)
    exchange = Column(String(50), nullable=True)
    
    # descripcion opcional
    description = Column(Text, nullable=True)
    
    # flag para desactivar activos
    is_active = Column(Boolean, default=True, nullable=False)
    
    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # relacion one-to-many con precios historicos
    prices = relationship("AssetPrice", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Asset(symbol='{self.symbol}', name='{self.name}', type={self.asset_type})>"


class AssetPrice(Base):
    """
    historial de precios de un activo.
    
    almacena datos ohlcv (open, high, low, close, volume) para
    analisis tecnico y graficos historicos.
    
    los precios se pueden obtener de apis como alpha vantage y
    almacenar para reducir llamadas a la api y permitir analisis
    offline.
    
    campos:
        id: uuid del registro de precio
        asset_symbol: simbolo del activo
        timestamp: momento del precio (puede ser diario, horario, etc)
        open_price: precio de apertura
        high_price: precio maximo
        low_price: precio minimo
        close_price: precio de cierre
        volume: volumen operado
    """
    __tablename__ = "asset_prices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # foreign key al activo (usamos symbol directamente por simplicidad)
    asset_symbol = Column(String(20), ForeignKey('assets.symbol', ondelete='CASCADE'), nullable=False, index=True)
    
    # timestamp del precio (incluye fecha y hora)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # datos ohlcv (open, high, low, close, volume)
    # Numeric(15, 4): permite hasta 99,999,999,999.9999 (4 decimales para precision)
    open_price = Column(Numeric(15, 4), nullable=False)
    high_price = Column(Numeric(15, 4), nullable=False)
    low_price = Column(Numeric(15, 4), nullable=False)
    close_price = Column(Numeric(15, 4), nullable=False)
    
    # volumen: cantidad de unidades operadas
    volume = Column(Numeric(20, 2), nullable=False)
    
    # timestamps de auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # relacion many-to-one con Asset
    asset = relationship("Asset", back_populates="prices")
    
    # constraints:
    # 1. un activo no puede tener dos precios en el mismo timestamp
    # 2. indice compuesto para queries rapidas por simbolo y fecha
    __table_args__ = (
        UniqueConstraint('asset_symbol', 'timestamp', name='uq_asset_price_timestamp'),
        Index('idx_asset_symbol_timestamp', 'asset_symbol', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<AssetPrice(symbol='{self.asset_symbol}', timestamp='{self.timestamp}', close={self.close_price})>"

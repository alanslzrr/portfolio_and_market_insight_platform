"""
repositorio para gestion de activos y precios.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.repositories.base import BaseRepository
from app.models.asset import Asset, AssetPrice, AssetType


class AssetRepository(BaseRepository[Asset]):
    """repositorio para activos financieros."""
    
    def __init__(self, db: Session):
        super().__init__(Asset, db)
    
    def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """obtiene activo por simbolo."""
        return self.db.query(Asset).filter(
            Asset.symbol == symbol.upper()
        ).first()
    
    def search_assets(self, query: str, limit: int = 20) -> List[Asset]:
        """
        busqueda de activos por simbolo o nombre.
        
        args:
            query: termino de busqueda
            limit: maximo de resultados
            
        returns:
            lista de activos que coinciden
        """
        search = f"%{query}%"
        return self.db.query(Asset).filter(
            or_(
                Asset.symbol.ilike(search),
                Asset.name.ilike(search)
            ),
            Asset.is_active == True
        ).limit(limit).all()
    
    def get_or_create(self, symbol: str, name: str, asset_type: AssetType, 
                     currency: str = "USD") -> Asset:
        """
        obtiene un activo o lo crea si no existe (get-or-create pattern).
        
        args:
            symbol: simbolo del activo
            name: nombre
            asset_type: tipo de activo
            currency: moneda
            
        returns:
            activo existente o recien creado
        """
        asset = self.get_by_symbol(symbol)
        if asset:
            return asset
        
        asset = Asset(
            symbol=symbol.upper(),
            name=name,
            asset_type=asset_type,
            currency=currency
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset
    
    def add_price(self, asset_symbol: str, timestamp: datetime, 
                  open_price: float, high_price: float, low_price: float,
                  close_price: float, volume: float) -> AssetPrice:
        """agrega un precio historico para un activo."""
        price = AssetPrice(
            asset_symbol=asset_symbol.upper(),
            timestamp=timestamp,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=volume
        )
        self.db.add(price)
        self.db.commit()
        self.db.refresh(price)
        return price
    
    def get_historical_prices(self, symbol: str, days: int = 30) -> List[AssetPrice]:
        """
        obtiene precios historicos de un activo.
        
        args:
            symbol: simbolo del activo
            days: numero de dias hacia atras
            
        returns:
            lista de precios ordenados por fecha
        """
        date_from = datetime.utcnow() - timedelta(days=days)
        return self.db.query(AssetPrice).filter(
            AssetPrice.asset_symbol == symbol.upper(),
            AssetPrice.timestamp >= date_from
        ).order_by(AssetPrice.timestamp.asc()).all()

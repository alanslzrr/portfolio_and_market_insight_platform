"""
modelos pydantic para datos de mercado.

define dtos para informacion de activos y precios.
incluye estructura ohlcv (open high low close volume) para historicos.
"""
from typing import List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.asset import AssetType


class AssetInfo(BaseModel):
    """informacion basica de un activo (simbolo, nombre, tipo, etc)"""
    symbol: str
    name: str
    asset_type: AssetType
    currency: str
    exchange: str | None
    description: str | None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "asset_type": "STOCK",
                "currency": "USD",
                "exchange": "NASDAQ",
                "description": "Tecnologia - Electronica de consumo"
            }
        }
    }


class PricePoint(BaseModel):
    """
    un punto de precio ohlcv (open high low close volume).
    
    estructura estandar para precios historicos, compatible con apis de mercado.
    """
    timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "timestamp": "2024-01-01T00:00:00Z",
                "open_price": "150.00",
                "high_price": "152.50",
                "low_price": "149.00",
                "close_price": "151.25",
                "volume": "1000000"
            }
        }
    }


class CurrentPriceResponse(BaseModel):
    """response con precio actual de un activo"""
    symbol: str
    price: Decimal
    timestamp: datetime
    currency: str = Field(default="USD")
    
    model_config = {"json_schema_extra": {
        "example": {
            "symbol": "AAPL",
            "price": "175.50",
            "timestamp": "2024-01-01T15:30:00Z",
            "currency": "USD"
        }
    }}


class HistoricalPriceResponse(BaseModel):
    """response con lista de precios historicos (serie temporal)"""
    symbol: str
    currency: str
    prices: List[PricePoint]
    
    model_config = {"json_schema_extra": {
        "example": {
            "symbol": "AAPL",
            "currency": "USD",
            "prices": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "open_price": "150.00",
                    "high_price": "152.50",
                    "low_price": "149.00",
                    "close_price": "151.25",
                    "volume": "1000000"
                }
            ]
        }
    }}


class AssetSearchResult(BaseModel):
    """resultado de busqueda de activos (busqueda fuzzy por simbolo o nombre)"""
    symbol: str
    name: str
    asset_type: AssetType
    currency: str
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "asset_type": "STOCK",
                "currency": "USD"
            }
        }
    }

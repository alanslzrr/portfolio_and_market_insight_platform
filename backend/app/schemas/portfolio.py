"""
modelos pydantic para portfolios y posiciones.

define los dtos (data transfer objects) para operaciones crud de portfolios.
pydantic valida automaticamente los datos y genera la doc openapi.
los campos Decimal se serializan automaticamente a float en json.

incluye:
- PortfolioCreate: crear portfolio nuevo
- PortfolioUpdate: actualizar portfolio (patch semantico)
- PortfolioAssetResponse: response de una posicion individual
- PortfolioResponse: response basica de portfolio sin posiciones
- PortfolioDetailResponse: response completa con todas las posiciones
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class PortfolioCreate(BaseModel):
    """
    request para crear un portfolio nuevo.
    
    valida que el nombre no este vacio, que la moneda sea formato iso 4217.
    """
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_currency: str = Field(default="USD", max_length=3)
    
    @field_validator('base_currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        # forzar uppercase, 3 letras
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError('moneda debe ser codigo iso 4217 de 3 letras')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        # limpiar espacios
        return v.strip()
    
    model_config = {"json_schema_extra": {
        "example": {
            "name": "Mi Portfolio Conservador",
            "description": "Inversiones a largo plazo con bajo riesgo",
            "base_currency": "USD"
        }
    }}


class PortfolioUpdate(BaseModel):
    """
    request para actualizar portfolio.
    
    todos los campos son opcionales (semantica PATCH).
    solo se actualizan los campos que se envian.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    base_currency: Optional[str] = Field(None, max_length=3)
    
    @field_validator('base_currency')
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError('moneda debe ser codigo iso 4217 de 3 letras')
        return v
    
    model_config = {"json_schema_extra": {
        "example": {
            "name": "Portfolio Actualizado",
            "description": "Nueva descripcion"
        }
    }}


class PortfolioAssetResponse(BaseModel):
    """
    response de una posicion de activo dentro del portfolio.
    incluye metricas calculadas (gain/loss, valor actual, etc).
    """
    id: UUID
    asset_symbol: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    position_value: Decimal  # qty × current_price
    gain_loss: Decimal  # ganancia/perdida absoluta
    gain_loss_percent: Decimal  # ganancia/perdida porcentual
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "asset_symbol": "AAPL",
                "quantity": "10.00000000",
                "average_price": "150.50",
                "current_price": "160.25",
                "position_value": "1602.50",
                "gain_loss": "97.50",
                "gain_loss_percent": "6.48",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    }


class PortfolioResponse(BaseModel):
    """
    response basica de portfolio sin las posiciones.
    incluye metricas agregadas del portfolio completo.
    """
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    base_currency: str
    total_value: Decimal
    total_cost: Decimal
    total_gain_loss: Decimal
    total_gain_loss_percent: Decimal
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-43d3-a456-426614174000",
                "name": "Mi Portfolio",
                "description": "Portfolio principal",
                "base_currency": "USD",
                "total_value": "50000.00",
                "total_cost": "45000.00",
                "total_gain_loss": "5000.00",
                "total_gain_loss_percent": "11.11",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    }


class PortfolioDetailResponse(BaseModel):
    """
    response completa de portfolio con todas sus posiciones incluidas.
    util para mostrar el portfolio entero en una sola llamada.
    """
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    base_currency: str
    total_value: Decimal
    total_cost: Decimal
    total_gain_loss: Decimal
    total_gain_loss_percent: Decimal
    created_at: datetime
    updated_at: datetime
    
    # lista de posiciones del portfolio
    assets: List[PortfolioAssetResponse] = Field(default_factory=list)
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-43d3-a456-426614174000",
                "name": "Mi Portfolio",
                "description": "Portfolio principal",
                "base_currency": "USD",
                "total_value": "50000.00",
                "total_cost": "45000.00",
                "total_gain_loss": "5000.00",
                "total_gain_loss_percent": "11.11",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "assets": [
                    {
                        "id": "111e4567-e89b-12d3-a456-426614174000",
                        "asset_symbol": "AAPL",
                        "quantity": "10.00000000",
                        "average_price": "150.50",
                        "current_price": "160.25",
                        "position_value": "1602.50",
                        "gain_loss": "97.50",
                        "gain_loss_percent": "6.48",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                ]
            }
        }
    }
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-43d3-a456-426614174000",
                "name": "Mi Portfolio",
                "description": "Portfolio principal",
                "base_currency": "USD",
                "total_value": "50000.00",
                "total_cost": "45000.00",
                "total_gain_loss": "5000.00",
                "total_gain_loss_percent": "11.11",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "assets": [
                    {
                        "id": "111e4567-e89b-12d3-a456-426614174000",
                        "asset_symbol": "AAPL",
                        "quantity": "10.00000000",
                        "average_price": "150.50",
                        "current_price": "160.25",
                        "position_value": "1602.50",
                        "gain_loss": "97.50",
                        "gain_loss_percent": "6.48",
                        "updated_at": "2024-01-01T12:00:00Z"
                    }
                ]
            }
        }
    }

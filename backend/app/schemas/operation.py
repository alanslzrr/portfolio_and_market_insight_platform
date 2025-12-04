"""
modelos pydantic para operaciones financieras (compra/venta).

define dtos para crear, actualizar y filtrar operaciones.
valida que quantity y price sean siempre positivos.
normaliza symbols a uppercase automaticamente.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from app.models.operation import OperationType


class OperationCreate(BaseModel):
    """
    request para crear una operacion de compra o venta.
    
    valida quantity > 0, price > 0, fees >= 0.
    """
    portfolio_id: UUID
    asset_symbol: str = Field(min_length=1, max_length=20)
    operation_type: OperationType
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    fees: Decimal = Field(default=Decimal('0'), ge=0)
    operation_date: datetime
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('asset_symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        # normalizar a uppercase y quitar espacios
        return v.upper().strip()
    
    model_config = {"json_schema_extra": {
        "example": {
            "portfolio_id": "123e4567-e89b-12d3-a456-426614174000",
            "asset_symbol": "AAPL",
            "operation_type": "BUY",
            "quantity": "10",
            "price": "150.50",
            "fees": "5.00",
            "operation_date": "2024-01-01T10:30:00Z",
            "notes": "Compra inicial"
        }
    }}


class OperationUpdate(BaseModel):
    """
    request para actualizar una operacion.
    
    solo permitimos actualizar notes y operation_date.
    no permitimos cambiar quantity, price o tipo para mantener integridad.
    """
    operation_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    model_config = {"json_schema_extra": {
        "example": {
            "operation_date": "2024-01-01T11:00:00Z",
            "notes": "Nota actualizada"
        }
    }}


class OperationResponse(BaseModel):
    """
    response de una operacion.
    
    incluye total_amount calculado (para BUY: qty*price+fees, para SELL: qty*price-fees).
    """
    id: UUID
    portfolio_id: UUID
    asset_symbol: str
    operation_type: OperationType
    quantity: Decimal
    price: Decimal
    fees: Decimal
    total_amount: Decimal
    operation_date: datetime
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "portfolio_id": "987e6543-e21b-43d3-a456-426614174000",
                "asset_symbol": "AAPL",
                "operation_type": "BUY",
                "quantity": "10.00000000",
                "price": "150.50",
                "fees": "5.00",
                "total_amount": "1510.00",
                "operation_date": "2024-01-01T10:30:00Z",
                "notes": "Compra inicial",
                "created_at": "2024-01-01T10:30:00Z",
                "updated_at": "2024-01-01T10:30:00Z"
            }
        }
    }


class OperationFilter(BaseModel):
    """
    filtros para buscar operaciones.
    
    todos los campos opcionales, se combinan con AND logico.
    """
    portfolio_id: Optional[UUID] = None
    asset_symbol: Optional[str] = None
    operation_type: Optional[OperationType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    @field_validator('asset_symbol')
    @classmethod
    def validate_symbol(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.upper().strip()
    
    model_config = {"json_schema_extra": {
        "example": {
            "portfolio_id": "123e4567-e89b-12d3-a456-426614174000",
            "asset_symbol": "AAPL",
            "operation_type": "BUY",
            "date_from": "2024-01-01T00:00:00Z",
            "date_to": "2024-12-31T23:59:59Z"
        }
    }}

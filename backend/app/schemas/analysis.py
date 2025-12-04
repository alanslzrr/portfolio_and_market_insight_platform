"""
modelos pydantic para analisis con ia.

define dtos para solicitar y recibir analisis generados por openai.
incluye validators para asegurar que el tipo de analisis coincida con los datos proporcionados
(portfolio_id para PORTFOLIO, asset_symbol para ASSET, mutuamente excluyentes).
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator
from app.models.analysis import AnalysisType, AnalysisStatus


class TechnicalIndicators(BaseModel):
    """
    indicadores tecnicos calculados sobre el activo o portfolio.
    
    estructura flexible - no todos los indicadores son obligatorios.
    """
    rsi: Optional[Decimal] = None  # relative strength index (0-100)
    sma_20: Optional[Decimal] = None  # simple moving average 20 periodos
    sma_50: Optional[Decimal] = None  # simple moving average 50 periodos
    volatility: Optional[Decimal] = None  # volatilidad (desviacion estandar)
    trend: Optional[str] = None  # tendencia: BULLISH, BEARISH, NEUTRAL
    
    model_config = {"json_schema_extra": {
        "example": {
            "rsi": "65.5",
            "sma_20": "150.25",
            "sma_50": "148.75",
            "volatility": "2.5",
            "trend": "BULLISH"
        }
    }}


class AnalysisRequest(BaseModel):
    """
    request para solicitar un analisis.
    
    debe incluir portfolio_id O asset_symbol, no ambos (validacion en model_validator).
    """
    analysis_type: AnalysisType
    portfolio_id: Optional[UUID] = None
    asset_symbol: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_request(self):
        # validar que portfolio_id y asset_symbol sean mutuamente excluyentes
        # y que coincidan con el tipo de analisis solicitado
        
        if self.analysis_type == AnalysisType.PORTFOLIO:
            if not self.portfolio_id:
                raise ValueError('para analisis de portfolio, debe proporcionar portfolio_id')
            if self.asset_symbol:
                raise ValueError('para analisis de portfolio, no debe proporcionar asset_symbol')
        
        if self.analysis_type == AnalysisType.ASSET:
            if not self.asset_symbol:
                raise ValueError('para analisis de activo, debe proporcionar asset_symbol')
            if self.portfolio_id:
                raise ValueError('para analisis de activo, no debe proporcionar portfolio_id')
        
        return self
    
    model_config = {"json_schema_extra": {
        "examples": [
            {
                "analysis_type": "PORTFOLIO",
                "portfolio_id": "123e4567-e89b-12d3-a456-426614174000"
            },
            {
                "analysis_type": "ASSET",
                "asset_symbol": "AAPL"
            }
        ]
    }}


class AnalysisResponse(BaseModel):
    """
    response con analisis generado por ia.
    
    incluye el texto del analisis, indicadores tecnicos y disclaimer legal.
    el disclaimer siempre se incluye para proteccion legal.
    """
    id: UUID
    analysis_type: AnalysisType
    portfolio_id: Optional[UUID]
    asset_symbol: Optional[str]
    analysis_text: str
    technical_indicators: TechnicalIndicators
    generated_at: datetime
    expires_at: datetime
    disclaimer: str  # disclaimer legal siempre incluido
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "analysis_type": "ASSET",
                "portfolio_id": None,
                "asset_symbol": "AAPL",
                "analysis_text": "Analisis detallado del activo AAPL...",
                "technical_indicators": {
                    "rsi": "65.5",
                    "sma_20": "150.25",
                    "volatility": "2.5",
                    "trend": "BULLISH"
                },
                "generated_at": "2024-01-01T12:00:00Z",
                "expires_at": "2024-01-02T12:00:00Z",
                "disclaimer": "Este analisis es generado por IA..."
            }
        }
    }


class AnalysisRequestStatus(BaseModel):
    """
    response con estado de una solicitud de analisis asincrona.
    
    permite trackear si el analisis esta pendiente, completado o fallo.
    """
    id: UUID
    status: AnalysisStatus
    requested_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    analysis_id: Optional[UUID] = None  # id del analisis generado (si completo exitosamente)
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "COMPLETED",
                "requested_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:05:00Z",
                "error_message": None,
                "analysis_id": "987e6543-e21b-43d3-a456-426614174000"
            }
        }
    }

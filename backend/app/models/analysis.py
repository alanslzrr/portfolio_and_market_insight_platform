"""
modelos orm para analisis con ia.

define:
- AnalysisType: enum para tipo de analisis (PORTFOLIO, ASSET)
- AnalysisStatus: enum para estado del analisis  
- Analysis: resultado de un analisis generado por ia
- AnalysisRequest: registro de solicitudes de analisis

el sistema de cache permite:
1. evitar generar el mismo analisis repetidamente (ahorro de costos api)
2. responder rapido a requests repetidas
3. trackear uso de ia para metricas
"""
import uuid
import enum
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisType(str, enum.Enum):
    """
    tipo de analisis solicitado.
    
    PORTFOLIO: analisis de un portfolio completo (todas las posiciones)
    ASSET: analisis de un activo especifico
    """
    PORTFOLIO = "PORTFOLIO"
    ASSET = "ASSET"


class AnalysisStatus(str, enum.Enum):
    """
    estado del proceso de analisis.
    
    PENDING: solicitado pero aun no procesado
    COMPLETED: analisis completado exitosamente
    FAILED: error al generar el analisis
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Analysis(Base):
    """
    analisis generado por ia almacenado en cache.
    
    guarda el resultado de un analisis para servirlo multiples veces
    sin volver a llamar a openai (que es costoso en dinero y tiempo).
    
    el cache expira despues de cierto tiempo (ej: 24 horas) porque
    las condiciones de mercado cambian constantemente.
    
    campos:
        id: uuid del analisis
        analysis_type: PORTFOLIO o ASSET
        portfolio_id: si es analisis de portfolio (nullable)
        asset_symbol: si es analisis de activo (nullable)
        analysis_text: texto generado por ia
        technical_indicators: json con indicadores calculados
        generated_at: cuando se genero
        expires_at: cuando expira el cache
    """
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # tipo de analisis
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False, index=True)
    
    # referencias (solo una debe estar presente segun el tipo)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=True, index=True)
    asset_symbol = Column(String(20), nullable=True, index=True)
    
    # contenido del analisis
    # el texto puede ser largo (varios parrafos de explicacion)
    analysis_text = Column(Text, nullable=False)
    
    # indicadores tecnicos calculados (rsi, sma, volatilidad, etc)
    # almacenamos como json para flexibilidad
    technical_indicators = Column(JSON, default=dict, nullable=False)
    
    # control de cache
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # calculado al crear
    
    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # relacion con Portfolio (si aplica)
    portfolio = relationship("Portfolio")
    
    def is_expired(self) -> bool:
        """
        verifica si el analisis ha expirado.
        
        un analisis expirado debe regenerarse para reflejar
        condiciones actuales del mercado.
        
        returns:
            bool: true si expiro, false si aun es valido
        """
        return datetime.utcnow() > self.expires_at
    
    @staticmethod
    def get_disclaimer() -> str:
        """
        retorna el disclaimer legal estandar para analisis financieros.
        
        siempre incluir este disclaimer para dejar claro que el analisis
        es informativo, no asesoria financiera.
        
        returns:
            str: texto del disclaimer
        """
        return (
            "DISCLAIMER: Este analisis es generado por inteligencia artificial "
            "con fines informativos unicamente. No constituye asesoria financiera, "
            "de inversion o recomendacion de compra/venta. Las inversiones implican "
            "riesgos y el rendimiento pasado no garantiza resultados futuros. "
            "Consulte con un asesor financiero certificado antes de tomar decisiones "
            "de inversion."
        )
    
    def __repr__(self) -> str:
        return f"<Analysis(type={self.analysis_type}, generated_at='{self.generated_at}')>"


class AnalysisRequest(Base):
    """
    registro de solicitudes de analisis.
    
    util para:
    - auditoria: quien solicito que y cuando
    - metricas: uso del sistema de ia
    - debugging: rastrear errores en generacion
    - facturacion: tracking de costos de api
    
    campos:
        id: uuid de la solicitud
        user_id: usuario que solicito
        analysis_type: tipo solicitado
        portfolio_id: portfolio analizado (si aplica)
        asset_symbol: activo analizado (si aplica)
        status: PENDING, COMPLETED o FAILED
        error_message: si fallo, que error ocurrio
        analysis_id: referencia al analisis generado (si completo)
    """
    __tablename__ = "analysis_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # usuario que solicito
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # que se solicito
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=True)
    asset_symbol = Column(String(20), nullable=True)
    
    # estado del request
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False, index=True)
    
    # si fallo, el mensaje de error
    error_message = Column(Text, nullable=True)
    
    # si completo, referencia al analisis generado
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="SET NULL"), nullable=True)
    
    # timestamps
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # relaciones
    user = relationship("User")
    portfolio = relationship("Portfolio")
    analysis = relationship("Analysis")
    
    def __repr__(self) -> str:
        return f"<AnalysisRequest(type={self.analysis_type}, status={self.status})>"

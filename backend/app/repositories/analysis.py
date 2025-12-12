"""
repositorio para gestion de analisis con ia.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.analysis import Analysis, AnalysisRequest, AnalysisType, AnalysisStatus


class AnalysisRepository(BaseRepository[Analysis]):
    """repositorio para analisis con ia."""
    
    def __init__(self, db: Session):
        super().__init__(Analysis, db)
    
    def get_cached_analysis(self, portfolio_id: Optional[UUID] = None,
                           asset_symbol: Optional[str] = None,
                           analysis_type: Optional[AnalysisType] = None) -> Optional[Analysis]:
        """
        obtiene un analisis cacheado valido (no expirado).
        
        FIX: agregado parametro analysis_type para filtrar correctamente el cache
        problema: sin este parametro se retornaban analisis de tipo incorrecto
        
        args:
            portfolio_id: id del portfolio (para analisis de portfolio)
            asset_symbol: simbolo del activo (para analisis de activo)
            analysis_type: tipo de analisis
            
        returns:
            analisis valido si existe en cache
        """
        query = self.db.query(Analysis).filter(
            Analysis.expires_at > datetime.utcnow()
        )
        
        if portfolio_id:
            query = query.filter(Analysis.portfolio_id == portfolio_id)
        if asset_symbol:
            query = query.filter(Analysis.asset_symbol == asset_symbol.upper())
        if analysis_type:
            query = query.filter(Analysis.analysis_type == analysis_type)
        
        return query.first()
    
    def invalidate_cache(self, portfolio_id: UUID) -> int:
        """
        invalida (elimina) analisis cacheados de un portfolio.
        
        util cuando cambian las posiciones del portfolio.
        
        args:
            portfolio_id: id del portfolio
            
        returns:
            numero de analisis eliminados
        """
        count = self.db.query(Analysis).filter(
            Analysis.portfolio_id == portfolio_id
        ).delete()
        self.db.commit()
        return count
    
    def create_request(self, user_id: UUID, analysis_type: AnalysisType,
                      portfolio_id: Optional[UUID] = None,
                      asset_symbol: Optional[str] = None) -> AnalysisRequest:
        """
        crea un registro de solicitud de analisis.
        
        args:
            user_id: usuario que solicita
            analysis_type: tipo de analisis
            portfolio_id: id del portfolio (opcional)
            asset_symbol: simbolo del activo (opcional)
            
        returns:
            solicitud creada
        """
        request = AnalysisRequest(
            user_id=user_id,
            analysis_type=analysis_type,
            portfolio_id=portfolio_id,
            asset_symbol=asset_symbol.upper() if asset_symbol else None,
            status=AnalysisStatus.PENDING
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
    
    def update_request_status(self, request_id: UUID, status: AnalysisStatus,
                             analysis_id: Optional[UUID] = None,
                             error_message: Optional[str] = None) -> Optional[AnalysisRequest]:
        """
        actualiza el estado de una solicitud de analisis.
        
        args:
            request_id: id de la solicitud
            status: nuevo estado
            analysis_id: id del analisis generado (si completo)
            error_message: mensaje de error (si fallo)
            
        returns:
            solicitud actualizada
        """
        request = self.db.query(AnalysisRequest).filter(
            AnalysisRequest.id == request_id
        ).first()
        
        if request:
            request.status = status
            if analysis_id:
                request.analysis_id = analysis_id
            if error_message:
                request.error_message = error_message
            if status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
                request.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(request)
        
        return request
    
    def get_by_portfolio(self, portfolio_id: UUID, limit: int = 10) -> list[Analysis]:
        """
        obtiene analisis recientes de un portfolio.
        
        args:
            portfolio_id: id del portfolio
            limit: numero maximo de resultados
            
        returns:
            lista de analisis ordenados por fecha desc
        """
        return self.db.query(Analysis).filter(
            Analysis.portfolio_id == portfolio_id
        ).order_by(Analysis.generated_at.desc()).limit(limit).all()
    
    def get_by_asset(self, asset_symbol: str, limit: int = 10) -> list[Analysis]:
        """
        obtiene analisis recientes de un activo.
        
        args:
            asset_symbol: simbolo del activo
            limit: numero maximo de resultados
            
        returns:
            lista de analisis ordenados por fecha desc
        """
        return self.db.query(Analysis).filter(
            Analysis.asset_symbol == asset_symbol.upper()
        ).order_by(Analysis.generated_at.desc()).limit(limit).all()

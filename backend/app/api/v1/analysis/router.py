"""
router para endpoints de analisis con ia.

proporciona endpoints para:
- generar analisis de activos
- generar analisis de portfolios
- obtener historial de analisis
- invalidar cache
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.middleware.dependencies import get_db, get_current_active_user
from app.models.user import User
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisRequestStatus
)


router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/asset/{symbol}", response_model=AnalysisResponse)
def generate_asset_analysis(
    symbol: str,
    force_regenerate: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    genera analisis con ia de un activo especifico.
    
    el analisis incluye:
    - interpretacion de indicadores tecnicos (rsi, macd, medias moviles)
    - identificacion de tendencias
    - niveles de soporte/resistencia
    - evaluacion de volatilidad
    
    el resultado se cachea por 24 horas para optimizar costos.
    usa force_regenerate=true para forzar regeneracion.
    
    **importante**: este analisis es puramente descriptivo y no constituye
    consejo financiero. siempre incluye disclaimers apropiados.
    
    args:
        symbol: simbolo del activo (ej: AAPL, MSFT)
        force_regenerate: forzar regeneracion ignorando cache
        
    returns:
        analisis generado con indicadores tecnicos
        
    raises:
        404: si no hay datos suficientes del activo
        500: si falla la generacion (api key invalida, rate limit, etc)
    """
    service = AnalysisService(db)
    
    analysis = service.generate_asset_analysis(
        user_id=current_user.id,
        symbol=symbol,
        force_regenerate=force_regenerate
    )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"no se pudo generar analisis para {symbol}. "
                "verifica que openai api key este configurada y que haya "
                "suficientes datos historicos del activo"
            )
        )
    
    # FIX: removido cached=analysis.cached (el campo no existe en el modelo Analysis)
    # FIX: agregado disclaimer requerido por el schema AnalysisResponse
    return AnalysisResponse(
        id=analysis.id,
        portfolio_id=analysis.portfolio_id,
        asset_symbol=analysis.asset_symbol,
        analysis_type=analysis.analysis_type,
        analysis_text=analysis.analysis_text,
        technical_indicators=analysis.technical_indicators,
        generated_at=analysis.generated_at,
        expires_at=analysis.expires_at,
        disclaimer="Este análisis es generado por IA y no constituye asesoramiento financiero."
    )


@router.post("/portfolio/{portfolio_id}", response_model=AnalysisResponse)
def generate_portfolio_analysis(
    portfolio_id: UUID,
    force_regenerate: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    genera analisis con ia de un portfolio completo.
    
    el analisis incluye:
    - evaluacion de diversificacion
    - analisis de posiciones principales
    - rendimiento general del portfolio
    - balance de riesgo
    
    el resultado se cachea por 24 horas.
    
    **importante**: este analisis es descriptivo y no constituye
    consejo de inversion.
    
    args:
        portfolio_id: id del portfolio a analizar
        force_regenerate: forzar regeneracion ignorando cache
        
    returns:
        analisis generado del portfolio
        
    raises:
        404: si el portfolio no existe o no pertenece al usuario
        500: si falla la generacion
    """
    # verificar ownership del portfolio
    from app.repositories.portfolio import PortfolioRepository
    
    portfolio_repo = PortfolioRepository(db)
    portfolio = portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"portfolio {portfolio_id} no encontrado"
        )
    
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no tienes permiso para acceder a este portfolio"
        )
    
    # generar analisis
    service = AnalysisService(db)
    
    analysis = service.generate_portfolio_analysis(
        user_id=current_user.id,
        portfolio_id=portfolio_id,
        force_regenerate=force_regenerate
    )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "no se pudo generar analisis del portfolio. "
                "verifica que openai api key este configurada y que "
                "el portfolio tenga posiciones activas"
            )
        )
    
    return AnalysisResponse(
        id=analysis.id,
        portfolio_id=analysis.portfolio_id,
        asset_symbol=analysis.asset_symbol,
        analysis_type=analysis.analysis_type,
        analysis_text=analysis.analysis_text,
        technical_indicators=analysis.technical_indicators,
        generated_at=analysis.generated_at,
        expires_at=analysis.expires_at,
        disclaimer="Este análisis es generado por IA y no constituye asesoramiento financiero."
    )


@router.get("/history", response_model=List[AnalysisResponse])
def get_analysis_history(
    portfolio_id: Optional[UUID] = None,
    asset_symbol: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    obtiene historial de analisis generados.
    
    puede filtrar por portfolio o activo especifico.
    
    args:
        portfolio_id: filtrar por portfolio (opcional)
        asset_symbol: filtrar por activo (opcional)
        limit: numero maximo de resultados (max 50)
        
    returns:
        lista de analisis ordenados por fecha descendente
    """
    if limit > 50:
        limit = 50
    
    service = AnalysisService(db)
    
    analyses = service.get_analysis_history(
        user_id=current_user.id,
        portfolio_id=portfolio_id,
        asset_symbol=asset_symbol,
        limit=limit
    )
    
    return [
        AnalysisResponse(
            id=analysis.id,
            portfolio_id=analysis.portfolio_id,
            asset_symbol=analysis.asset_symbol,
            analysis_type=analysis.analysis_type,
            analysis_text=analysis.analysis_text,
            technical_indicators=analysis.technical_indicators,
            generated_at=analysis.generated_at,
            expires_at=analysis.expires_at,
            disclaimer="Este análisis es generado por IA y no constituye asesoramiento financiero."
        )
        for analysis in analyses
    ]


@router.delete("/cache/portfolio/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def invalidate_portfolio_cache(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    invalida cache de analisis de un portfolio.
    
    util cuando se hacen cambios significativos al portfolio
    (compra/venta importante) y se quiere regenerar analisis.
    
    args:
        portfolio_id: id del portfolio
    """
    # verificar ownership
    from app.repositories.portfolio import PortfolioRepository
    
    portfolio_repo = PortfolioRepository(db)
    portfolio = portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"portfolio {portfolio_id} no encontrado"
        )
    
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no tienes permiso para acceder a este portfolio"
        )
    
    # invalidar cache
    service = AnalysisService(db)
    service.invalidate_cache(portfolio_id=portfolio_id)


@router.delete("/cache/asset/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def invalidate_asset_cache(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    invalida cache de analisis de un activo.
    
    util cuando hay eventos significativos que requieren
    regenerar analisis (earnings, noticias importantes, etc).
    
    args:
        symbol: simbolo del activo
    """
    service = AnalysisService(db)
    service.invalidate_cache(asset_symbol=symbol.upper())

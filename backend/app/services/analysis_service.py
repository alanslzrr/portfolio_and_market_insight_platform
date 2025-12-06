"""
servicio de analisis con inteligencia artificial.

coordina la generacion de analisis usando openai y datos de mercado.
cachea resultados para optimizar costos de api.
"""
import sys
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

# agregar el directorio padre al path para importar ai_module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.clients.openai_client import OpenAIClient
from app.services.market_service import MarketDataService
from app.models.analysis import Analysis, AnalysisRequest
from app.repositories.analysis import AnalysisRepository
from app.repositories.portfolio import PortfolioRepository
from ai_module.src.processors.technical_indicators import TechnicalIndicators


logger = logging.getLogger(__name__)


class AnalysisService:
    """
    servicio para generacion de analisis con ia.
    
    responsabilidades:
    - generar analisis de activos individuales
    - generar analisis de portfolios completos
    - cachear resultados para reducir costos
    - trackear solicitudes de analisis
    """
    
    # tiempo de vida del cache (en horas)
    CACHE_TTL_HOURS = 24
    
    def __init__(self, db: Session):
        """
        inicializa el servicio.
        
        args:
            db: sesion de base de datos
        """
        self.db = db
        self.analysis_repo = AnalysisRepository(db)
        self.portfolio_repo = PortfolioRepository(db)
        self.market_service = MarketDataService(db)
        self.openai_client = OpenAIClient()
    
    def generate_asset_analysis(
        self,
        user_id: UUID,
        symbol: str,
        force_regenerate: bool = False
    ) -> Optional[Analysis]:
        """
        genera analisis de un activo especifico.
        
        flujo:
        1. verifica cache (si no es force_regenerate)
        2. obtiene datos historicos del activo
        3. calcula indicadores tecnicos
        4. genera analisis con openai
        5. guarda y retorna resultado
        
        args:
            user_id: id del usuario solicitante
            symbol: simbolo del activo
            force_regenerate: forzar regeneracion (ignorar cache)
            
        returns:
            objeto analysis con el analisis generado o none si falla
        """
        symbol = symbol.upper()
        
        # verificar si openai esta disponible
        if not self.openai_client.is_available():
            logger.error("openai no disponible - api key no configurada")
            return None
        
        # buscar en cache si no es force_regenerate
        if not force_regenerate:
            cached = self.analysis_repo.get_cached_analysis(
                asset_symbol=symbol,
                analysis_type="asset_technical"
            )
            if cached:
                logger.info(f"usando analisis cacheado para {symbol}")
                return cached
        
        # crear solicitud de analisis
        request = AnalysisRequest(
            user_id=user_id,
            asset_symbol=symbol,
            portfolio_id=None,
            status="processing"
        )
        self.db.add(request)
        self.db.commit()
        
        try:
            # obtener datos historicos (ultimos 100 dias)
            logger.info(f"obteniendo datos historicos para {symbol}")
            price_history = self.market_service.get_historical_prices(symbol, days=100)
            
            if not price_history or len(price_history) < 30:
                logger.warning(f"insuficientes datos historicos para {symbol}")
                request.status = "failed"
                self.db.commit()
                return None
            
            # extraer precios de cierre para indicadores
            close_prices = [p["close"] for p in price_history]
            
            # calcular indicadores tecnicos
            logger.info(f"calculando indicadores tecnicos para {symbol}")
            indicators = TechnicalIndicators.calculate_all_indicators(close_prices)
            
            # generar analisis con openai
            logger.info(f"generando analisis con ia para {symbol}")
            analysis_text = self.openai_client.generate_asset_analysis(
                symbol=symbol,
                indicators=indicators,
                price_history=price_history[:30]  # ultimos 30 dias para contexto
            )
            
            if not analysis_text:
                logger.error(f"fallo la generacion de analisis para {symbol}")
                request.status = "failed"
                self.db.commit()
                return None
            
            # crear objeto analysis
            expires_at = datetime.utcnow() + timedelta(hours=self.CACHE_TTL_HOURS)
            
            analysis = Analysis(
                portfolio_id=None,
                asset_symbol=symbol,
                analysis_type="asset_technical",
                analysis_text=analysis_text,
                technical_indicators=indicators,
                generated_at=datetime.utcnow(),
                expires_at=expires_at,
                cached=True
            )
            
            self.db.add(analysis)
            
            # actualizar solicitud
            request.status = "completed"
            
            self.db.commit()
            
            logger.info(f"analisis generado correctamente para {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"error generando analisis para {symbol}: {e}")
            request.status = "failed"
            self.db.commit()
            return None
    
    def generate_portfolio_analysis(
        self,
        user_id: UUID,
        portfolio_id: UUID,
        force_regenerate: bool = False
    ) -> Optional[Analysis]:
        """
        genera analisis de un portfolio completo.
        
        flujo:
        1. verifica cache
        2. obtiene portfolio con posiciones
        3. actualiza precios de activos
        4. calcula indicadores para cada posicion
        5. genera analisis con openai
        6. guarda y retorna resultado
        
        args:
            user_id: id del usuario solicitante
            portfolio_id: id del portfolio
            force_regenerate: forzar regeneracion (ignorar cache)
            
        returns:
            objeto analysis con el analisis generado o none si falla
        """
        # verificar si openai esta disponible
        if not self.openai_client.is_available():
            logger.error("openai no disponible - api key no configurada")
            return None
        
        # buscar en cache
        if not force_regenerate:
            cached = self.analysis_repo.get_cached_analysis(
                portfolio_id=portfolio_id,
                analysis_type="portfolio_overview"
            )
            if cached:
                logger.info(f"usando analisis cacheado para portfolio {portfolio_id}")
                return cached
        
        # crear solicitud de analisis
        request = AnalysisRequest(
            user_id=user_id,
            asset_symbol=None,
            portfolio_id=portfolio_id,
            status="processing"
        )
        self.db.add(request)
        self.db.commit()
        
        try:
            # obtener portfolio con posiciones
            portfolio = self.portfolio_repo.get_with_positions(portfolio_id)
            
            if not portfolio:
                logger.error(f"portfolio {portfolio_id} no encontrado")
                request.status = "failed"
                self.db.commit()
                return None
            
            # verificar que haya posiciones
            if not portfolio.assets or len(portfolio.assets) == 0:
                logger.warning(f"portfolio {portfolio_id} no tiene posiciones")
                request.status = "failed"
                self.db.commit()
                return None
            
            # actualizar precios de activos
            logger.info(f"actualizando precios para portfolio {portfolio_id}")
            self.market_service.update_portfolio_prices(portfolio_id)
            
            # refrescar portfolio
            self.db.refresh(portfolio)
            
            # preparar datos del portfolio
            portfolio_data = {
                "name": portfolio.name,
                "total_value": float(portfolio.total_value),
                "total_cost": float(portfolio.total_cost),
                "gain_loss": float(portfolio.total_gain_loss),
                "gain_loss_percent": float(portfolio.total_gain_loss_percent)
            }
            
            # preparar datos de posiciones
            positions = []
            for position in portfolio.assets:
                if position.quantity <= 0:
                    continue
                
                positions.append({
                    "symbol": position.asset_symbol,
                    "quantity": float(position.quantity),
                    "value": float(position.current_value),
                    "cost": float(position.total_cost),
                    "gain_loss": float(position.gain_loss),
                    "gain_loss_percent": float(position.gain_loss_percent)
                })
            
            # generar analisis con openai
            logger.info(f"generando analisis de portfolio {portfolio_id} con ia")
            analysis_text = self.openai_client.generate_portfolio_analysis(
                portfolio_data=portfolio_data,
                positions=positions
            )
            
            if not analysis_text:
                logger.error(f"fallo la generacion de analisis para portfolio {portfolio_id}")
                request.status = "failed"
                self.db.commit()
                return None
            
            # crear objeto analysis
            expires_at = datetime.utcnow() + timedelta(hours=self.CACHE_TTL_HOURS)
            
            analysis = Analysis(
                portfolio_id=portfolio_id,
                asset_symbol=None,
                analysis_type="portfolio_overview",
                analysis_text=analysis_text,
                technical_indicators={
                    "total_positions": len(positions),
                    "total_value": portfolio_data["total_value"],
                    "performance": portfolio_data["gain_loss_percent"]
                },
                generated_at=datetime.utcnow(),
                expires_at=expires_at,
                cached=True
            )
            
            self.db.add(analysis)
            
            # actualizar solicitud
            request.status = "completed"
            
            self.db.commit()
            
            logger.info(f"analisis de portfolio generado correctamente")
            return analysis
            
        except Exception as e:
            logger.error(f"error generando analisis de portfolio {portfolio_id}: {e}")
            request.status = "failed"
            self.db.commit()
            return None
    
    def get_analysis_history(
        self,
        user_id: UUID,
        portfolio_id: Optional[UUID] = None,
        asset_symbol: Optional[str] = None,
        limit: int = 10
    ) -> List[Analysis]:
        """
        obtiene historial de analisis del usuario.
        
        args:
            user_id: id del usuario
            portfolio_id: filtrar por portfolio (opcional)
            asset_symbol: filtrar por activo (opcional)
            limit: numero maximo de resultados
            
        returns:
            lista de analisis ordenados por fecha desc
        """
        # esta funcionalidad requiere agregar user_id a la tabla analysis
        # por ahora retornamos analisis por portfolio/asset
        
        if portfolio_id:
            analyses = self.analysis_repo.get_by_portfolio(portfolio_id, limit)
        elif asset_symbol:
            analyses = self.analysis_repo.get_by_asset(asset_symbol.upper(), limit)
        else:
            # retornar analisis recientes generales
            analyses = self.db.query(Analysis)\
                .order_by(Analysis.generated_at.desc())\
                .limit(limit)\
                .all()
        
        return analyses
    
    def invalidate_cache(
        self,
        portfolio_id: Optional[UUID] = None,
        asset_symbol: Optional[str] = None
    ) -> int:
        """
        invalida cache de analisis.
        
        util cuando hay cambios significativos que requieren
        regenerar analisis.
        
        args:
            portfolio_id: invalidar cache de portfolio
            asset_symbol: invalidar cache de activo
            
        returns:
            numero de analisis invalidados
        """
        count = 0
        
        if portfolio_id:
            analyses = self.analysis_repo.get_by_portfolio(portfolio_id)
            for analysis in analyses:
                analysis.expires_at = datetime.utcnow()
                count += 1
        
        if asset_symbol:
            analyses = self.analysis_repo.get_by_asset(asset_symbol.upper())
            for analysis in analyses:
                analysis.expires_at = datetime.utcnow()
                count += 1
        
        self.db.commit()
        logger.info(f"invalidados {count} analisis del cache")
        
        return count

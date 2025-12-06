"""
servicio de datos de mercado.

coordina la obtencion de datos financieros desde alpha vantage
y los almacena/actualiza en la base de datos local.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.clients.alpha_vantage_client import AlphaVantageClient
from app.models.asset import Asset, AssetPrice
from app.repositories.asset import AssetRepository


logger = logging.getLogger(__name__)


class MarketDataService:
    """
    servicio para gestion de datos de mercado.
    
    responsabilidades:
    - obtener precios actuales y historicos desde alpha vantage
    - cachear datos en base de datos local
    - buscar y registrar nuevos activos
    - actualizar catalogo de activos
    """
    
    def __init__(self, db: Session):
        """
        inicializa el servicio.
        
        args:
            db: sesion de base de datos
        """
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.alpha_client = AlphaVantageClient()
    
    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """
        obtiene el precio actual de un activo.
        
        flujo:
        1. busca precio reciente en cache (< 5 minutos)
        2. si no hay cache valido, consulta alpha vantage
        3. almacena el nuevo precio en cache
        
        args:
            symbol: simbolo del activo
            
        returns:
            precio actual como decimal o none si no se encuentra
        """
        symbol = symbol.upper()
        
        # intentar obtener precio del cache
        cached_price = self.asset_repo.get_latest_price(symbol)
        if cached_price and self._is_price_fresh(cached_price.timestamp):
            logger.info(f"usando precio cacheado para {symbol}: ${cached_price.price}")
            return cached_price.price
        
        # obtener precio de alpha vantage
        logger.info(f"consultando alpha vantage para {symbol}")
        quote = self.alpha_client.get_quote(symbol)
        
        if not quote:
            logger.warning(f"no se pudo obtener precio para {symbol}")
            return None
        
        # guardar precio en cache
        price = Decimal(str(quote["price"]))
        self._save_price(
            symbol=symbol,
            price=price,
            open_price=Decimal(str(quote["open"])),
            high=Decimal(str(quote["high"])),
            low=Decimal(str(quote["low"])),
            volume=quote["volume"],
            date=quote["timestamp"]
        )
        
        logger.info(f"precio actualizado para {symbol}: ${price}")
        return price
    
    def get_historical_prices(
        self, 
        symbol: str, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        obtiene datos historicos de precios.
        
        flujo:
        1. verifica cache local
        2. si faltan datos, consulta alpha vantage
        3. almacena datos nuevos
        
        args:
            symbol: simbolo del activo
            days: numero de dias de historia (max 100 en free tier)
            
        returns:
            lista de precios historicos ordenados por fecha desc
        """
        symbol = symbol.upper()
        
        # intentar obtener del cache
        cached_prices = self.asset_repo.get_price_history(symbol, days)
        
        # si tenemos datos recientes suficientes, retornarlos
        if cached_prices and len(cached_prices) >= days:
            logger.info(f"usando {len(cached_prices)} precios cacheados para {symbol}")
            return self._format_price_history(cached_prices)
        
        # obtener datos de alpha vantage
        logger.info(f"consultando datos historicos de alpha vantage para {symbol}")
        outputsize = "compact" if days <= 100 else "full"
        prices_data = self.alpha_client.get_daily_prices(symbol, outputsize)
        
        if not prices_data:
            logger.warning(f"no se pudieron obtener datos historicos para {symbol}")
            # retornar cache si lo hay
            return self._format_price_history(cached_prices) if cached_prices else []
        
        # guardar precios en cache
        for price_data in prices_data[:days]:
            self._save_price(
                symbol=symbol,
                price=Decimal(str(price_data["close"])),
                open_price=Decimal(str(price_data["open"])),
                high=Decimal(str(price_data["high"])),
                low=Decimal(str(price_data["low"])),
                volume=price_data["volume"],
                date=price_data["date"]
            )
        
        # obtener precios actualizados del cache
        updated_prices = self.asset_repo.get_price_history(symbol, days)
        logger.info(f"datos historicos actualizados para {symbol}: {len(updated_prices)} registros")
        
        return self._format_price_history(updated_prices)
    
    def search_assets(self, keywords: str) -> List[Dict[str, Any]]:
        """
        busca activos por keywords.
        
        primero busca en catalogo local, luego en alpha vantage.
        
        args:
            keywords: terminos de busqueda
            
        returns:
            lista de activos encontrados
        """
        # buscar en catalogo local
        local_results = self.asset_repo.search_assets(keywords)
        
        if local_results:
            logger.info(f"encontrados {len(local_results)} activos locales para '{keywords}'")
            results = []
            for asset in local_results:
                results.append({
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "type": asset.asset_type,
                    "currency": asset.currency,
                    "source": "local"
                })
            return results
        
        # buscar en alpha vantage
        logger.info(f"buscando en alpha vantage para '{keywords}'")
        av_results = self.alpha_client.search_symbol(keywords)
        
        if not av_results:
            return []
        
        # formatear resultados
        results = []
        for match in av_results:
            results.append({
                "symbol": match["symbol"],
                "name": match["name"],
                "type": match["type"],
                "currency": match["currency"],
                "source": "alpha_vantage"
            })
        
        return results
    
    def register_asset(
        self,
        symbol: str,
        name: str,
        asset_type: str = "Stock",
        currency: str = "USD",
        exchange: Optional[str] = None
    ) -> Asset:
        """
        registra un nuevo activo en el catalogo.
        
        usa get_or_create para evitar duplicados.
        
        args:
            symbol: simbolo del activo
            name: nombre del activo
            asset_type: tipo (Stock, ETF, Crypto, etc)
            currency: moneda
            exchange: bolsa donde cotiza
            
        returns:
            activo registrado
        """
        asset = self.asset_repo.get_or_create(
            symbol=symbol.upper(),
            name=name,
            asset_type=asset_type,
            currency=currency.upper(),
            exchange=exchange
        )
        
        logger.info(f"activo registrado: {asset.symbol} - {asset.name}")
        return asset
    
    def update_portfolio_prices(self, portfolio_id) -> int:
        """
        actualiza precios de todos los activos en un portfolio.
        
        util para refrescar valores antes de calcular metricas.
        
        args:
            portfolio_id: id del portfolio
            
        returns:
            numero de precios actualizados
        """
        from app.repositories.portfolio import PortfolioRepository
        
        portfolio_repo = PortfolioRepository(self.db)
        portfolio = portfolio_repo.get_with_positions(portfolio_id)
        
        if not portfolio:
            logger.warning(f"portfolio {portfolio_id} no encontrado")
            return 0
        
        updated_count = 0
        for position in portfolio.assets:
            if position.quantity <= 0:
                continue
            
            price = self.get_current_price(position.asset_symbol)
            if price:
                position.current_price = price
                updated_count += 1
        
        # recalcular metricas del portfolio
        portfolio.calculate_metrics()
        self.db.commit()
        
        logger.info(f"actualizados {updated_count} precios para portfolio {portfolio_id}")
        return updated_count
    
    def _is_price_fresh(self, timestamp: datetime, max_age_minutes: int = 5) -> bool:
        """
        verifica si un precio esta actualizado.
        
        args:
            timestamp: timestamp del precio
            max_age_minutes: antiguedad maxima en minutos
            
        returns:
            true si el precio es reciente
        """
        age = datetime.utcnow() - timestamp
        return age < timedelta(minutes=max_age_minutes)
    
    def _save_price(
        self,
        symbol: str,
        price: Decimal,
        open_price: Decimal,
        high: Decimal,
        low: Decimal,
        volume: int,
        date: str
    ):
        """
        guarda un precio en la base de datos.
        
        args:
            symbol: simbolo del activo
            price: precio de cierre
            open_price: precio de apertura
            high: precio maximo
            low: precio minimo
            volume: volumen
            date: fecha (formato YYYY-MM-DD)
        """
        # verificar si ya existe este precio
        existing = self.asset_repo.get_price_by_date(symbol, date)
        if existing:
            # actualizar precio existente
            existing.price = price
            existing.open_price = open_price
            existing.high = high
            existing.low = low
            existing.volume = volume
            existing.timestamp = datetime.utcnow()
        else:
            # crear nuevo registro
            price_obj = AssetPrice(
                asset_symbol=symbol,
                price=price,
                open_price=open_price,
                high=high,
                low=low,
                volume=volume,
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                timestamp=datetime.utcnow(),
                source="alpha_vantage"
            )
            self.db.add(price_obj)
        
        self.db.commit()
    
    def _format_price_history(self, prices: List[AssetPrice]) -> List[Dict[str, Any]]:
        """
        formatea lista de precios para respuesta.
        
        args:
            prices: lista de objetos AssetPrice
            
        returns:
            lista de diccionarios con datos formateados
        """
        return [
            {
                "date": price.date.strftime("%Y-%m-%d"),
                "open": float(price.open_price),
                "high": float(price.high),
                "low": float(price.low),
                "close": float(price.price),
                "volume": price.volume
            }
            for price in prices
        ]
    
    def __del__(self):
        """cierra el cliente al destruir el servicio."""
        if hasattr(self, 'alpha_client'):
            self.alpha_client.close()

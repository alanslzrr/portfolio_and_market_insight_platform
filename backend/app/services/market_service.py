from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
import logging

from app.clients.alpha_vantage_client import AlphaVantageClient
from app.models.asset import Asset, AssetPrice
from app.repositories.asset import AssetRepository

logger = logging.getLogger(__name__)

# Movimos ALPHA_VANTAGE_TYPE_MAPPING y DEFAULT_ASSET_TYPE a nivel de módulo para centralizar
# la lógica de tipado. Sino cambiábamos esto así, íbamos a tener duplicación de mapeos por toda
# la aplicación y era un dolor mantenerlos sincronizados.
ALPHA_VANTAGE_TYPE_MAPPING = {
    "Equity": "STOCK",
    "Common Stock": "STOCK",
    "Stock": "STOCK",
    "ETF": "ETF",
    "Exchange Traded Fund": "ETF",
    "Cryptocurrency": "CRYPTO",
    "Digital Currency": "CRYPTO",
    "Mutual Fund": "STOCK",
    "Index": "STOCK",
    "Fund": "STOCK",
}

DEFAULT_ASSET_TYPE = "STOCK"


class MarketDataService:
    """Servicio para gestión de datos de mercado."""

    def __init__(self, db: Session):
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.alpha_client = AlphaVantageClient()

    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Obtiene el precio actual de un activo, registrándolo automáticamente si no existe."""
        symbol = symbol.upper()
        quote = None  # inicializar quote
        
        # Priorizamos fetch directo del quote sobre search_symbol para no quemar el rate-limit tan rápido.
        # Sino cambiábamos esto así, se agotaba el rate-limit de Alpha Vantage en minutos por llamadas
        # innecesarias a búsqueda.
        asset = self.asset_repo.get_by_symbol(symbol)
        if not asset:
            # intentar obtener quote directamente (evita search que consume rate limit)
            logger.info(f"Consultando quote directo para {symbol}")
            quote = self.alpha_client.get_quote(symbol)
            
            if quote and "price" in quote:
                # crear asset con info basica del quote
                asset = self.asset_repo.get_or_create(
                    symbol=symbol,
                    name=symbol,  # usamos el simbolo como nombre
                    asset_type=DEFAULT_ASSET_TYPE,
                    currency="USD"
                )
                logger.info(f"Asset {symbol} registrado desde quote directo")
            else:
                # fallback: intentar search solo si quote falla
                search_results = self.alpha_client.search_symbol(symbol)
                if not search_results:
                    logger.error(f"Símbolo {symbol} no encontrado en Alpha Vantage")
                    return None
                
                match = search_results[0]
                asset = self.asset_repo.get_or_create(
                    symbol=symbol,
                    name=match.get("name", symbol),
                    asset_type=ALPHA_VANTAGE_TYPE_MAPPING.get(match.get("type", ""), DEFAULT_ASSET_TYPE),
                    currency=match.get("currency", "USD")
                )
                logger.info(f"Asset {symbol} registrado desde búsqueda")
                
                # resetear quote para forzar nueva consulta
                quote = None
        
        # Unificamos todo bajo get_historical_prices. Antes teníamos código duplicado con diferentes
        # nombres para lo mismo (get_price_history vs get_historical_prices).
        cached_prices = self.asset_repo.get_historical_prices(symbol, days=1)
        if cached_prices:
            latest = cached_prices[-1]
            if self._is_price_fresh(latest.timestamp):
                logger.info(f"Precio en cache para {symbol}: ${latest.close_price}")
                return latest.close_price
        
        # solo consultar si no lo hicimos arriba
        if quote is None:
            logger.info(f"Consultando Alpha Vantage para {symbol}")
            quote = self.alpha_client.get_quote(symbol)
        
        if not quote or "price" not in quote:
            logger.error(
                f"Símbolo {symbol} no tiene datos en Alpha Vantage "
                f"(aparece en búsqueda pero sin quotes disponibles)"
            )
            return None
        
        try:
            price = Decimal(str(quote["price"]))
            if price <= 0:
                logger.warning(f"Precio inválido para {symbol}: {price}")
                return None
        except (ValueError, TypeError) as e:
            logger.error(f"Error al parsear precio para {symbol}: {e}")
            return None
        
        # Alpha Vantage a veces no devuelve todos los campos, así que usamos .get() con defaults.
        # Sino cambiábamos esto así, el servicio se caía con KeyError cuando faltaban datos.
        self._save_price(
            symbol=symbol,
            price=price,
            open_price=Decimal(str(quote.get("open", "0"))),
            high=Decimal(str(quote.get("high", "0"))),
            low=Decimal(str(quote.get("low", "0"))),
            volume=int(float(quote.get("volume", 0))),
            date=quote.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d"))
        )
        
        logger.info(f"Precio actualizado para {symbol}: ${price}")
        return price

    def get_historical_prices(
        self,
        symbol: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Obtiene datos históricos, registrando automáticamente el asset si no existe."""
        symbol = symbol.upper()
        
        # Registramos automáticamente el asset si no existe. Antes fallaba silenciosamente y el
        # frontend no podía mostrar gráficos para símbolos nuevos.
        asset = self.asset_repo.get_by_symbol(symbol)
        if not asset:
            search_results = self.alpha_client.search_symbol(symbol)
            if not search_results:
                logger.error(f"Símbolo {symbol} no encontrado en Alpha Vantage")
                return []
            
            match = search_results[0]
            asset = self.asset_repo.get_or_create(
                symbol=symbol,
                name=match.get("name", symbol),
                asset_type=ALPHA_VANTAGE_TYPE_MAPPING.get(match.get("type", ""), DEFAULT_ASSET_TYPE),
                currency=match.get("currency", "USD")
            )
            logger.info(f"Asset {symbol} registrado automáticamente")
        
        cached_prices = self.asset_repo.get_historical_prices(symbol, days)
        
        if cached_prices and len(cached_prices) >= days:
            logger.info(f"Usando {len(cached_prices)} precios en cache para {symbol}")
            return self._format_price_history(cached_prices)
        
        logger.info(f"Consultando historicos para {symbol}")
        outputsize = "compact" if days <= 100 else "full"
        prices_data = self.alpha_client.get_daily_prices(symbol, outputsize)
        
        if not prices_data:
            logger.warning(f"Sin datos históricos para {symbol}")
            return self._format_price_history(cached_prices) if cached_prices else []
        
        for price_data in prices_data[:days]:
            self._save_price(
                symbol=symbol,
                price=Decimal(str(price_data["close"])),
                open_price=Decimal(str(price_data["open"])),
                high=Decimal(str(price_data["high"])),
                low=Decimal(str(price_data["low"])),
                volume=int(float(price_data.get("volume", 0))),
                date=price_data["date"]
            )
        
        updated_prices = self.asset_repo.get_historical_prices(symbol, days)
        logger.info(f"Historicos actualizados para {symbol}: {len(updated_prices)} registros")
        
        return self._format_price_history(updated_prices)

    def search_assets(self, keywords: str) -> List[Dict[str, Any]]:
        """Busca activos: primero BD local, luego Alpha Vantage."""
        local_results = self.asset_repo.search_assets(keywords)
        
        if local_results:
            logger.info(f"Encontrados {len(local_results)} assets locales para '{keywords}'")
            return [
                {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "type": asset.asset_type,
                    "currency": asset.currency,
                    "source": "local"
                }
                for asset in local_results
            ]
        
        logger.info(f"Buscando en Alpha Vantage: '{keywords}'")
        av_results = self.alpha_client.search_symbol(keywords)
        
        if not av_results:
            return []
        
        # Aplicamos mapeo consistente de tipos de Alpha Vantage. Antes teníamos 'Equity' vs 'STOCK'
        # mezclados en la base y era un desastre.
        return [
            {
                "symbol": match["symbol"],
                "name": match["name"],
                "type": ALPHA_VANTAGE_TYPE_MAPPING.get(
                    match.get("type", ""), DEFAULT_ASSET_TYPE
                ),
                "currency": match.get("currency", "USD"),
                "source": "alpha_vantage"
            }
            for match in av_results
        ]

    def register_asset(
        self,
        symbol: str,
        name: str,
        asset_type: str = "STOCK",
        currency: str = "USD"
    ) -> Asset:
        """Registra explícitamente un nuevo asset en BD."""
        asset = self.asset_repo.get_or_create(
            symbol=symbol.upper(),
            name=name,
            asset_type=asset_type.upper(),
            currency=currency.upper()
        )
        
        logger.info(f"Asset registrado: {asset.symbol} - {asset.name}")
        return asset

    def update_portfolio_prices(self, portfolio_id: int) -> int:
        """Actualiza precios de assets en un portfolio."""
        from app.repositories.portfolio import PortfolioRepository
        
        portfolio_repo = PortfolioRepository(self.db)
        portfolio = portfolio_repo.get_with_positions(portfolio_id)
        
        if not portfolio:
            logger.warning(f"Portfolio {portfolio_id} no encontrado")
            return 0
        
        updated_count = 0
        for position in portfolio.assets:
            if position.quantity <= 0:
                continue
            
            price = self.get_current_price(position.asset_symbol)
            if price:
                position.current_price = price
                updated_count += 1
        
        portfolio.calculate_metrics()
        self.db.commit()
        
        logger.info(f"Actualizados {updated_count} precios para portfolio {portfolio_id}")
        return updated_count

    def _is_price_fresh(self, timestamp: datetime, max_age_minutes: int = 5) -> bool:
        """Verifica si un precio está actualizado."""
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
    ) -> None:
        """
        Guarda precio en BD.
        
        Precondición: El asset DEBE existir en BD antes de llamar esto.
        """
        # El repositorio ahora usa open_price, high_price, low_price, close_price explícitamente.
        # Antes había mismatch entre el modelo AssetPrice y lo que guardábamos.
        try:
            timestamp = datetime.strptime(date, "%Y-%m-%d")
            self.asset_repo.add_price(
                asset_symbol=symbol,
                timestamp=timestamp,
                open_price=float(open_price),
                high_price=float(high),
                low_price=float(low),
                close_price=float(price),
                volume=float(volume)
            )
        except Exception as e:
            logger.error(f"Error guardando precio para {symbol}: {e}")

    def _format_price_history(self, prices: List[AssetPrice]) -> List[Dict[str, Any]]:
        """Formatea precios para respuesta API."""
        # AssetPrice ya no tiene 'price', ahora es 'close_price'. Sino cambiábamos esto así,
        # el API devolvía AttributeError: 'AssetPrice' has no 'price'.
        return [
            {
                "date": price.timestamp.strftime("%Y-%m-%d"),
                "open": float(price.open_price),
                "high": float(price.high_price),
                "low": float(price.low_price),
                "close": float(price.close_price),
                "volume": float(price.volume)
            }
            for price in prices
        ]

    def __del__(self) -> None:
        if hasattr(self, 'alpha_client'):
            self.alpha_client.close()

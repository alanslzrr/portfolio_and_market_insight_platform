"""
cliente para alpha vantage api.

proporciona metodos para obtener datos de mercado financiero:
- precios actuales (quote endpoint)
- datos historicos (time series daily)
- busqueda de simbolos

documentacion oficial: https://www.alphavantage.co/documentation/
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from decimal import Decimal

import httpx
from app.core.config import settings


logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """
    cliente para interactuar con alpha vantage api.
    
    alpha vantage proporciona datos de mercado gratuitos con rate limiting:
    - free tier: 25 requests/dia, 5 requests/minuto
    - importante cachear resultados para no exceder limites
    
    endpoints principales:
    - GLOBAL_QUOTE: precio actual de un activo
    - TIME_SERIES_DAILY: datos historicos diarios
    - SYMBOL_SEARCH: buscar simbolos por keywords
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    TIMEOUT = 10.0  # segundos
    
    def __init__(self, api_key: Optional[str] = None):
        """
        inicializa el cliente.
        
        args:
            api_key: api key de alpha vantage (usa settings si no se proporciona)
        """
        self.api_key = api_key or settings.alpha_vantage_api_key
        self.client = httpx.Client(timeout=self.TIMEOUT)
    
    def __enter__(self):
        """context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """cierra el cliente al salir del context."""
        self.client.close()
    
    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        realiza una peticion a la api.
        
        args:
            params: parametros de la query
            
        returns:
            respuesta json parseada
            
        raises:
            ValueError: si no hay api key configurada
            httpx.HTTPError: si falla la peticion
            Exception: si la api retorna error
        """
        if not self.api_key:
            raise ValueError(
                "alpha vantage api key no configurada. "
                "configura ALPHA_VANTAGE_API_KEY en .env"
            )
        
        # agregar api key a los parametros
        params["apikey"] = self.api_key
        
        logger.info(f"alpha vantage request: {params.get('function')} - {params.get('symbol', 'N/A')}")
        
        try:
            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # alpha vantage retorna errores en el json
            if "Error Message" in data:
                raise Exception(f"alpha vantage error: {data['Error Message']}")
            
            if "Note" in data:
                # rate limit excedido
                raise Exception(
                    f"alpha vantage rate limit: {data['Note']}. "
                    "free tier permite 25 requests/dia, 5/minuto"
                )
            
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"error en peticion alpha vantage: {e}")
            raise
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        obtiene cotizacion actual de un activo.
        
        usa el endpoint GLOBAL_QUOTE que retorna:
        - precio actual
        - precio de apertura
        - maximo y minimo del dia
        - volumen
        - cambio y cambio porcentual
        
        args:
            symbol: simbolo del activo (ej: "AAPL", "MSFT")
            
        returns:
            diccionario con datos de cotizacion o none si no se encuentra
            formato:
            {
                "symbol": "AAPL",
                "price": 150.25,
                "open": 149.80,
                "high": 151.00,
                "low": 149.50,
                "volume": 50000000,
                "change": 0.45,
                "change_percent": "0.30%",
                "timestamp": "2024-12-05"
            }
        """
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol.upper()
            }
            
            data = self._make_request(params)
            
            # verificar que haya datos
            if "Global Quote" not in data or not data["Global Quote"]:
                logger.warning(f"no se encontraron datos para {symbol}")
                return None
            
            quote = data["Global Quote"]
            
            # parsear y normalizar datos
            return {
                "symbol": quote.get("01. symbol", symbol.upper()),
                "price": float(quote.get("05. price", 0)),
                "open": float(quote.get("02. open", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "volume": int(quote.get("06. volume", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "timestamp": quote.get("07. latest trading day", datetime.now().strftime("%Y-%m-%d"))
            }
            
        except Exception as e:
            logger.error(f"error obteniendo quote para {symbol}: {e}")
            return None
    
    def get_daily_prices(
        self, 
        symbol: str, 
        outputsize: str = "compact"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        obtiene datos historicos diarios de un activo.
        
        usa el endpoint TIME_SERIES_DAILY que retorna datos OHLCV
        (open, high, low, close, volume) por cada dia.
        
        args:
            symbol: simbolo del activo
            outputsize: "compact" (100 ultimos dias) o "full" (20+ años)
            
        returns:
            lista de diccionarios con datos historicos ordenados por fecha desc
            formato:
            [
                {
                    "date": "2024-12-05",
                    "open": 149.80,
                    "high": 151.00,
                    "low": 149.50,
                    "close": 150.25,
                    "volume": 50000000
                },
                ...
            ]
        """
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol.upper(),
                "outputsize": outputsize
            }
            
            data = self._make_request(params)
            
            # verificar que haya datos
            if "Time Series (Daily)" not in data:
                logger.warning(f"no se encontraron datos historicos para {symbol}")
                return None
            
            time_series = data["Time Series (Daily)"]
            
            # convertir a lista de dicts y ordenar por fecha descendente
            prices = []
            for date_str, values in time_series.items():
                prices.append({
                    "date": date_str,
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0))
                })
            
            # ordenar por fecha descendente (mas reciente primero)
            prices.sort(key=lambda x: x["date"], reverse=True)
            
            return prices
            
        except Exception as e:
            logger.error(f"error obteniendo datos historicos para {symbol}: {e}")
            return None
    
    def search_symbol(self, keywords: str) -> Optional[List[Dict[str, Any]]]:
        """
        busca simbolos por keywords.
        
        usa el endpoint SYMBOL_SEARCH para encontrar activos
        que coincidan con los terminos de busqueda.
        
        args:
            keywords: terminos de busqueda (nombre o simbolo)
            
        returns:
            lista de activos encontrados
            formato:
            [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "type": "Equity",
                    "region": "United States",
                    "currency": "USD"
                },
                ...
            ]
        """
        try:
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": keywords
            }
            
            data = self._make_request(params)
            
            # verificar que haya resultados
            if "bestMatches" not in data or not data["bestMatches"]:
                logger.info(f"no se encontraron resultados para '{keywords}'")
                return []
            
            # parsear resultados
            matches = []
            for match in data["bestMatches"]:
                matches.append({
                    "symbol": match.get("1. symbol", ""),
                    "name": match.get("2. name", ""),
                    "type": match.get("3. type", ""),
                    "region": match.get("4. region", ""),
                    "currency": match.get("8. currency", "USD")
                })
            
            return matches
            
        except Exception as e:
            logger.error(f"error buscando simbolos para '{keywords}': {e}")
            return []
    
    def close(self):
        """cierra el cliente http."""
        self.client.close()


# ejemplo de uso:
# 
# with AlphaVantageClient() as client:
#     # obtener precio actual
#     quote = client.get_quote("AAPL")
#     if quote:
#         print(f"AAPL: ${quote['price']}")
#     
#     # obtener historico
#     prices = client.get_daily_prices("AAPL", outputsize="compact")
#     if prices:
#         print(f"ultimos {len(prices)} dias de datos")
#     
#     # buscar simbolos
#     results = client.search_symbol("apple")
#     for result in results:
#         print(f"{result['symbol']} - {result['name']}")

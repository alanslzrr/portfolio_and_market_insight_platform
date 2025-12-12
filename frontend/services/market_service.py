"""Market data service."""
from typing import Any, Dict, List, Optional

from frontend.services.api_client import ApiClient


class MarketService:
    def __init__(self, client: ApiClient | None = None):
        self.client = client or ApiClient()

    def search_assets(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        return self.client.get("/api/v1/market/assets/search", params={"q": query, "limit": limit})

    def get_asset_info(self, symbol: str) -> Dict[str, Any]:
        return self.client.get(f"/api/v1/market/assets/{symbol}")

    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        return self.client.get(f"/api/v1/market/prices/{symbol}/current")

    def get_historical_prices(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        return self.client.get(f"/api/v1/market/prices/{symbol}/historical", params={"days": days})

    def create_asset(
        self,
        symbol: str,
        name: str,
        asset_type: str,
        currency: str = "USD",
        exchange: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {
            "symbol": symbol,
            "name": name,
            "asset_type": asset_type,
            "currency": currency,
            "exchange": exchange,
            "description": description,
        }
        return self.client.post("/api/v1/market/assets", params=params)

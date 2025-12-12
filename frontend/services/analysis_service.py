"""AI analysis endpoints wrapper."""
from typing import Any, Dict, List, Optional

from frontend.services.api_client import ApiClient


class AnalysisService:
    def __init__(self, client: ApiClient | None = None):
        self.client = client or ApiClient()

    def generate_asset_analysis(self, symbol: str, force_regenerate: bool = False) -> Dict[str, Any]:
        # FIX: cambio de params dict a query string en URL
        # problema: ApiClient no pasaba correctamente los params al backend
        force_str = "true" if force_regenerate else "false"
        endpoint = f"/api/v1/analysis/asset/{symbol}?force_regenerate={force_str}"
        return self.client.post(endpoint)

    def generate_portfolio_analysis(self, portfolio_id: str, force_regenerate: bool = False) -> Dict[str, Any]:
        force_str = "true" if force_regenerate else "false"
        endpoint = f"/api/v1/analysis/portfolio/{portfolio_id}?force_regenerate={force_str}"
        return self.client.post(endpoint)

    def get_history(
        self,
        portfolio_id: Optional[str] = None,
        asset_symbol: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if portfolio_id:
            params["portfolio_id"] = portfolio_id
        if asset_symbol:
            params["asset_symbol"] = asset_symbol
        return self.client.get("/api/v1/analysis/history", params=params)

    def invalidate_portfolio_cache(self, portfolio_id: str) -> None:
        self.client.delete(f"/api/v1/analysis/cache/portfolio/{portfolio_id}")

    def invalidate_asset_cache(self, symbol: str) -> None:
        self.client.delete(f"/api/v1/analysis/cache/asset/{symbol}")

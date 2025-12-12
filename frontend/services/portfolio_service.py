"""Portfolio related service calls."""
from typing import Any, Dict, List, Optional

from frontend.services.api_client import ApiClient


class PortfolioService:
    def __init__(self, client: ApiClient | None = None):
        self.client = client or ApiClient()

    def list_portfolios(self) -> List[Dict[str, Any]]:
        return self.client.get("/api/v1/portfolios/")

    def get_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        return self.client.get(f"/api/v1/portfolios/{portfolio_id}")

    def create_portfolio(self, name: str, description: Optional[str], base_currency: str) -> Dict[str, Any]:
        payload = {
            "name": name,
            "description": description,
            "base_currency": base_currency or "USD",
        }
        return self.client.post("/api/v1/portfolios/", payload)

    def update_portfolio(
        self,
        portfolio_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        return self.client.put(f"/api/v1/portfolios/{portfolio_id}", payload)

    def delete_portfolio(self, portfolio_id: str) -> None:
        self.client.delete(f"/api/v1/portfolios/{portfolio_id}")

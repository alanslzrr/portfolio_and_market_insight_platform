"""Service for operations CRUD and statistics."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from frontend.services.api_client import ApiClient


class OperationService:
    def __init__(self, client: ApiClient | None = None):
        self.client = client or ApiClient()

    def list_operations(
        self,
        portfolio_id: str,
        asset_symbol: Optional[str] = None,
        operation_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"portfolio_id": portfolio_id, "skip": skip, "limit": limit}
        if asset_symbol:
            params["asset_symbol"] = asset_symbol
        if operation_type:
            params["operation_type"] = operation_type
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        return self.client.get("/api/v1/operations/", params=params)

    def create_operation(
        self,
        portfolio_id: str,
        asset_symbol: str,
        operation_type: str,
        quantity: float,
        price: float,
        fees: float,
        operation_date: datetime,
        notes: Optional[str],
    ) -> Dict[str, Any]:
        payload = {
            "portfolio_id": portfolio_id,
            "asset_symbol": asset_symbol,
            "operation_type": operation_type,
            "quantity": str(quantity),
            "price": str(price),
            "fees": str(fees or 0),
            "operation_date": operation_date.isoformat(),
            "notes": notes,
        }
        return self.client.post("/api/v1/operations/", payload)

    def update_operation(self, operation_id: str, notes: Optional[str] = None, operation_date: Optional[datetime] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if notes is not None:
            payload["notes"] = notes
        if operation_date is not None:
            payload["operation_date"] = operation_date.isoformat()
        return self.client.put(f"/api/v1/operations/{operation_id}", payload)

    def get_operation(self, operation_id: str) -> Dict[str, Any]:
        return self.client.get(f"/api/v1/operations/{operation_id}")

    def get_statistics(self, portfolio_id: str) -> Dict[str, Any]:
        return self.client.get(f"/api/v1/operations/stats/{portfolio_id}")

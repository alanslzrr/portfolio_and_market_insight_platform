"""User profile related operations."""
from typing import Any, Dict, Optional

from frontend.services.api_client import ApiClient
from frontend.utils import session as session_utils


class UserService:
    def __init__(self, client: ApiClient | None = None):
        self.client = client or ApiClient()

    def get_profile(self) -> Dict[str, Any]:
        profile = self.client.get("/api/v1/users/me")
        session_utils.set_current_user(profile)
        return profile

    def update_profile(
        self,
        full_name: Optional[str] = None,
        currency: Optional[str] = None,
        timezone: Optional[str] = None,
        language: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if full_name is not None:
            payload["full_name"] = full_name
        if currency is not None:
            payload["currency"] = currency
        if timezone is not None:
            payload["timezone"] = timezone
        if language is not None:
            payload["language"] = language
        if preferences is not None:
            payload["preferences"] = preferences
        updated = self.client.put("/api/v1/users/me", payload)
        session_utils.set_current_user(updated)
        return updated

    def change_password(self, current_password: str, new_password: str) -> None:
        payload = {"current_password": current_password, "new_password": new_password}
        self.client.put("/api/v1/users/me/password", payload)

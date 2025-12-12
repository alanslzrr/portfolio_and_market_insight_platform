"""Authentication service wrapper."""
from typing import Any, Dict
import streamlit as st

from frontend.services.api_client import ApiClient, ApiError
from frontend.utils import session as session_utils


class AuthService:
    def __init__(self, client: ApiClient | None = None):
        self.client = client or ApiClient()

    def register(self, email: str, full_name: str, password: str) -> Dict[str, Any]:
        payload = {"email": email, "full_name": full_name, "password": password}
        return self.client.post("/api/v1/auth/register", payload)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        payload = {"email": email, "password": password}
        tokens = self.client.post("/api/v1/auth/login", payload)
        session_utils.store_tokens(
            tokens.get("access_token"),
            tokens.get("refresh_token"),
            tokens.get("expires_in", 1800),
        )
        return tokens

    def refresh(self) -> bool:
        refresh_token = st.session_state.get("refresh_token")
        if not refresh_token:
            return False
        try:
            tokens = self.client.post("/api/v1/auth/refresh", {"refresh_token": refresh_token})
        except ApiError:
            session_utils.clear_session()
            return False
        session_utils.store_tokens(
            tokens.get("access_token"),
            tokens.get("refresh_token"),
            tokens.get("expires_in", 1800),
        )
        return True

    def logout(self) -> None:
        refresh_token = st.session_state.get("refresh_token")
        if refresh_token:
            try:
                self.client.post("/api/v1/auth/logout", {"refresh_token": refresh_token})
            except ApiError:
                # Ignore API errors on logout; session will be cleared locally.
                pass
        session_utils.clear_session()

    def logout_all(self) -> None:
        try:
            self.client.post("/api/v1/auth/logout-all", {})
        except ApiError:
            pass
        session_utils.clear_session()

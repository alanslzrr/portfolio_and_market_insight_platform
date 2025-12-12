"""HTTP client wrapper used by all services."""
from typing import Any, Dict, Optional
import requests
import streamlit as st

from frontend.config.settings import get_settings
from frontend.utils import session as session_utils


class ApiError(Exception):
    """Represents an error returned by the API or network layer."""

    def __init__(self, message: str, status_code: Optional[int] = None, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class ApiClient:
    """Lightweight client that handles auth headers, refresh flow, and common errors."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        settings = get_settings()
        self.base_url = (base_url or settings.api_base_url).rstrip("/")
        self.timeout = timeout or settings.api_timeout

    def _build_url(self, endpoint: str) -> str:
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return f"{self.base_url}{endpoint}"

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _refresh_tokens(self) -> bool:
        refresh_token = st.session_state.get("refresh_token")
        if not refresh_token:
            return False

        url = self._build_url("/api/v1/auth/refresh")
        try:
            response = requests.post(
                url,
                json={"refresh_token": refresh_token},
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
        except requests.RequestException:
            return False

        if response.status_code != 200:
            session_utils.clear_session()
            return False

        try:
            data = response.json()
        except ValueError:
            session_utils.clear_session()
            return False

        session_utils.store_tokens(
            data.get("access_token"),
            data.get("refresh_token"),
            data.get("expires_in", 1800),
        )
        return True

    def _request(self, method: str, endpoint: str, retry: bool = True, **kwargs) -> Any:
        url = self._build_url(endpoint)
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}

        try:
            response = requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise ApiError("No se pudo conectar al backend.", payload={"error": str(exc)})

        if response.status_code == 401 and retry and self._refresh_tokens():
            return self._request(method, endpoint, retry=False, **kwargs)

        if response.status_code >= 400:
            error_detail: Any
            try:
                body = response.json()
                error_detail = body.get("detail", body)
            except ValueError:
                error_detail = response.text or "Error desconocido"
                body = {"detail": error_detail}

            raise ApiError(str(error_detail), status_code=response.status_code, payload=body)

        if response.status_code == 204:
            return None

        try:
            return response.json()
        except ValueError:
            return None

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("POST", endpoint, json=data, params=params)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("PUT", endpoint, json=data, params=params)

    def delete(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("DELETE", endpoint, json=data, params=params)

"""Session state helpers for the Streamlit UI."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import streamlit as st


DEFAULT_SESSION_VALUES: Dict[str, Any] = {
    "authenticated": False,
    "access_token": None,
    "refresh_token": None,
    "token_expires_at": None,
    "current_user": None,
}


def init_session_state() -> None:
    """Ensure expected keys exist in Streamlit session state."""
    for key, default in DEFAULT_SESSION_VALUES.items():
        if key not in st.session_state:
            st.session_state[key] = default


def store_tokens(access_token: str, refresh_token: str, expires_in: int) -> None:
    """Persist tokens and mark the session as authenticated."""
    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    st.session_state.authenticated = True


def token_needs_refresh() -> bool:
    """Return True if the access token is close to expiring."""
    expires_at: Optional[datetime] = st.session_state.get("token_expires_at")
    if not expires_at:
        return False
    return datetime.utcnow() > (expires_at - timedelta(seconds=60))


def is_authenticated() -> bool:
    """Check whether the current session has a valid access token."""
    return bool(st.session_state.get("access_token"))


def set_current_user(user: Dict[str, Any]) -> None:
    """Cache user profile information in the session."""
    st.session_state.current_user = user


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return cached user data, if available."""
    return st.session_state.get("current_user")


def clear_session() -> None:
    """Reset authentication-related session state."""
    for key in list(st.session_state.keys()):
        st.session_state.pop(key)
    init_session_state()

"""Entry point for the Streamlit frontend."""
from pathlib import Path
import sys

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR.parent) not in sys.path:
    sys.path.append(str(ROOT_DIR.parent))

from frontend.components.auth import render_login, render_register, render_user_sidebar
from frontend.config.settings import get_settings
from frontend.services.auth_service import AuthService
from frontend.services.user_service import UserService
from frontend.utils import session as session_utils


def main() -> None:
    settings = get_settings()
    st.set_page_config(page_title=settings.page_title, page_icon=settings.page_icon, layout=settings.layout)

    session_utils.init_session_state()
    auth_service = AuthService()
    user_service = UserService()

    with st.sidebar:
        if session_utils.is_authenticated():
            render_user_sidebar(auth_service)
        else:
            st.info("Inicia sesión para acceder a todas las secciones.")

    st.title(settings.page_title)
    st.caption("Frontend ligero en Streamlit para consumir la API FastAPI.")

    if session_utils.is_authenticated():
        user = session_utils.get_current_user() or user_service.get_profile()
        welcome_name = user.get("full_name") or user.get("email") or "Usuario"
        st.success(f"Sesión activa: {welcome_name}")
        st.write("Usa el menú lateral para abrir las páginas de Portfolios, Operaciones, Mercado, Análisis IA y Perfil.")
    else:
        tabs = st.tabs(["Iniciar sesión", "Registrarse"])
        with tabs[0]:
            render_login(auth_service, user_service)
        with tabs[1]:
            render_register(auth_service)


if __name__ == "__main__":
    main()

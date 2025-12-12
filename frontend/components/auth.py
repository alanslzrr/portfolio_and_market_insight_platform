"""Authentication UI components."""
import streamlit as st

from frontend.services.auth_service import AuthService
from frontend.services.user_service import UserService
from frontend.services.api_client import ApiError
from frontend.utils import session as session_utils
from frontend.utils import validators


def render_login(auth_service: AuthService, user_service: UserService) -> None:
    st.subheader("Iniciar sesión")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        email_error = validators.validate_email(email)
        if email_error:
            st.error(email_error)
            return

        try:
            auth_service.login(email=email, password=password)
            user_service.get_profile()
            st.success("Sesión iniciada.")
            st.rerun()
        except ApiError as e:
            st.error(str(e))


def render_register(auth_service: AuthService) -> None:
    st.subheader("Crear cuenta")
    with st.form("register_form", clear_on_submit=True):
        email = st.text_input("Correo electrónico")
        full_name = st.text_input("Nombre completo")
        password = st.text_input("Contraseña", type="password")
        confirm = st.text_input("Confirmar contraseña", type="password")
        submitted = st.form_submit_button("Registrarse")

    if submitted:
        email_error = validators.validate_email(email)
        if email_error:
            st.error(email_error)
            return

        pwd_error = validators.validate_password(password)
        if pwd_error:
            st.error(pwd_error)
            return

        if password != confirm:
            st.error("Las contraseñas no coinciden.")
            return

        try:
            auth_service.register(email=email, full_name=full_name, password=password)
            st.success("Registro exitoso. Ahora puedes iniciar sesión.")
        except ApiError as e:
            st.error(str(e))


def render_user_sidebar(auth_service: AuthService) -> None:
    user = session_utils.get_current_user()
    if not user:
        st.info("No autenticado.")
        return

    st.markdown(f"**{user.get('full_name', 'Usuario')}**")
    st.caption(user.get("email", ""))
    st.divider()
    st.caption("Sesión activa")
    if st.button("Cerrar sesión", use_container_width=True):
        auth_service.logout()
        st.rerun()

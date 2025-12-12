"""User profile page."""
import json
import streamlit as st

from frontend.components.auth import render_user_sidebar
from frontend.services.api_client import ApiError
from frontend.services.auth_service import AuthService
from frontend.services.user_service import UserService
from frontend.utils import validators
from frontend.utils import session as session_utils


st.set_page_config(layout="wide", page_title="Perfil")
session_utils.init_session_state()

auth_service = AuthService()
user_service = UserService()

with st.sidebar:
    if session_utils.is_authenticated():
        render_user_sidebar(auth_service)
    else:
        st.info("Inicia sesión para ver tu perfil.")

if not session_utils.is_authenticated():
    st.warning("Se requiere inicio de sesión para acceder al perfil.")
    st.stop()

st.title("Perfil de usuario")

try:
    profile = user_service.get_profile()
except ApiError as e:
    st.error(str(e))
    st.stop()

st.subheader("Información")
st.write(f"Correo: {profile.get('email')}")
st.write(f"Estado: {'Activo' if profile.get('is_active') else 'Inactivo'}")
st.write(f"Verificado: {'Sí' if profile.get('is_verified') else 'No'}")

prefs = profile.get("profile") or {}

st.divider()
st.subheader("Actualizar perfil")
with st.form("update_profile_form"):
    full_name = st.text_input("Nombre", value=profile.get("full_name", ""))
    currency = st.text_input("Moneda", value=prefs.get("currency", "USD"))
    timezone = st.text_input("Zona horaria", value=prefs.get("timezone", "UTC"))
    language = st.text_input("Idioma", value=prefs.get("language", "es"))
    preferences_raw = st.text_area(
        "Preferencias (JSON)",
        value=json.dumps(prefs.get("preferences", {}), indent=2),
        height=120,
    )
    submitted = st.form_submit_button("Guardar cambios")

if submitted:
    preferences = None
    if preferences_raw.strip():
        try:
            preferences = json.loads(preferences_raw)
        except json.JSONDecodeError:
            st.error("Las preferencias deben estar en formato JSON válido.")
            st.stop()
    try:
        updated = user_service.update_profile(
            full_name=full_name,
            currency=currency,
            timezone=timezone,
            language=language,
            preferences=preferences,
        )
        st.success("Perfil actualizado.")
    except ApiError as e:
        st.error(str(e))

st.divider()
st.subheader("Cambiar contraseña")
with st.form("change_password_form"):
    current_password = st.text_input("Contraseña actual", type="password")
    new_password = st.text_input("Nueva contraseña", type="password")
    confirm_password = st.text_input("Confirmar nueva contraseña", type="password")
    submitted_pwd = st.form_submit_button("Actualizar contraseña")

if submitted_pwd:
    pwd_error = validators.validate_password(new_password)
    if pwd_error:
        st.error(pwd_error)
    elif new_password != confirm_password:
        st.error("Las contraseñas no coinciden.")
    else:
        try:
            user_service.change_password(current_password, new_password)
            st.success("Contraseña actualizada. Se cerrarán tus sesiones activas.")
            auth_service.logout_all()
            st.rerun()
        except ApiError as e:
            st.error(str(e))

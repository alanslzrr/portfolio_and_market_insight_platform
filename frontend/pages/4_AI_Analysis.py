"""AI analysis page."""
import streamlit as st

from frontend.components.auth import render_user_sidebar
from frontend.services.analysis_service import AnalysisService
from frontend.services.api_client import ApiError
from frontend.services.auth_service import AuthService
from frontend.services.portfolio_service import PortfolioService
from frontend.utils import session as session_utils


st.set_page_config(layout="wide", page_title="Análisis IA")
session_utils.init_session_state()

auth_service = AuthService()
analysis_service = AnalysisService()
portfolio_service = PortfolioService()

with st.sidebar:
    if session_utils.is_authenticated():
        render_user_sidebar(auth_service)
    else:
        st.info("Inicia sesión para solicitar análisis con IA.")

if not session_utils.is_authenticated():
    st.warning("Se requiere inicio de sesión para usar esta sección.")
    st.stop()

st.title("Análisis con IA")
st.caption("Genera análisis de activos o portfolios usando los endpoints de IA.")

tabs = st.tabs(["Activo", "Portfolio"])

# Asset analysis tab
with tabs[0]:
    st.subheader("Análisis de activo")
    symbol = st.text_input("Símbolo del activo")
    force_asset = st.checkbox("Forzar regenerar", value=False)
    if st.button("Generar análisis de activo"):
        if not symbol:
            st.error("Ingresa un símbolo.")
        else:
            try:
                analysis = analysis_service.generate_asset_analysis(symbol, force_asset)
                st.success("Análisis generado.")
                st.write(analysis.get("analysis_text", ""))
                indicators = analysis.get("technical_indicators")
                if indicators:
                    st.json(indicators)
            except ApiError as e:
                st.error(str(e))

    st.markdown("Historial reciente")
    try:
        history = analysis_service.get_history(asset_symbol=symbol or None, limit=5)
        for item in history:
            with st.expander(f"{item.get('asset_symbol') or item.get('portfolio_id')} - {item.get('generated_at')}"):
                st.write(item.get("analysis_text", ""))
    except ApiError:
        st.info("No hay historial disponible.")

# Portfolio analysis tab
with tabs[1]:
    st.subheader("Análisis de portfolio")
    try:
        portfolios = portfolio_service.list_portfolios()
    except ApiError as e:
        st.error(str(e))
        portfolios = []

    if not portfolios:
        st.info("Crea un portfolio para solicitar análisis.")
    else:
        options = {p["name"]: p["id"] for p in portfolios}
        selected_name = st.selectbox("Portfolio", list(options.keys()))
        force_portfolio = st.checkbox("Forzar regenerar análisis", value=False, key="force_portfolio")
        if st.button("Generar análisis de portfolio"):
            try:
                analysis = analysis_service.generate_portfolio_analysis(options[selected_name], force_portfolio)
                st.success("Análisis generado.")
                st.write(analysis.get("analysis_text", ""))
                if analysis.get("technical_indicators"):
                    st.json(analysis["technical_indicators"])
            except ApiError as e:
                st.error(str(e))

        st.markdown("Historial")
        try:
            history = analysis_service.get_history(portfolio_id=options[selected_name], limit=5)
            for item in history:
                with st.expander(f"{item.get('generated_at')}"):
                    st.write(item.get("analysis_text", ""))
        except ApiError:
            st.info("No hay historial disponible para este portfolio.")

st.divider()
st.caption("Los análisis generados son informativos y no constituyen asesoría financiera.")

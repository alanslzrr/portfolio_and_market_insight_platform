"""Portfolios page."""
import pandas as pd
import streamlit as st

from frontend.components.auth import render_user_sidebar
from frontend.components.charts import allocation_pie
from frontend.components.metrics import render_metrics
from frontend.components.portfolio_card import portfolio_card
from frontend.services.api_client import ApiError
from frontend.services.auth_service import AuthService
from frontend.services.portfolio_service import PortfolioService
from frontend.services.user_service import UserService
from frontend.utils import formatters
from frontend.utils import session as session_utils


st.set_page_config(layout="wide", page_title="Portfolios")
session_utils.init_session_state()

auth_service = AuthService()
portfolio_service = PortfolioService()
user_service = UserService()

with st.sidebar:
    if session_utils.is_authenticated():
        render_user_sidebar(auth_service)
    else:
        st.info("Inicia sesión en la página principal.")


if not session_utils.is_authenticated():
    st.warning("Se requiere inicio de sesión para ver tus portfolios.")
    st.stop()

st.title("Portfolios")
st.caption("Administra tus carteras y revisa sus métricas.")


def refresh_profile() -> None:
    if not session_utils.get_current_user():
        try:
            user_service.get_profile()
        except ApiError:
            pass


refresh_profile()

# Create portfolio
with st.expander("Crear nuevo portfolio", expanded=False):
    with st.form("create_portfolio_form"):
        name = st.text_input("Nombre", placeholder="Mi cartera principal")
        description = st.text_area("Descripción", height=80)
        currency = st.text_input("Moneda base", value="USD", max_chars=3)
        submitted = st.form_submit_button("Crear")

    if submitted:
        if not name.strip():
            st.error("El nombre es obligatorio.")
        else:
            try:
                new_portfolio = portfolio_service.create_portfolio(name.strip(), description or None, currency.upper())
                st.success("Portfolio creado.")
                st.session_state.selected_portfolio_id = new_portfolio.get("id")
                st.rerun()
            except ApiError as e:
                st.error(str(e))


try:
    portfolios = portfolio_service.list_portfolios()
except ApiError as e:
    st.error(str(e))
    st.stop()

if "selected_portfolio_id" not in st.session_state:
    st.session_state.selected_portfolio_id = portfolios[0]["id"] if portfolios else None

if portfolios:
    st.subheader("Resumen")
    for portfolio in portfolios:
        actions = portfolio_card(portfolio)
        if actions["view"]:
            st.session_state.selected_portfolio_id = portfolio["id"]
            st.rerun()
        if actions["delete"]:
            try:
                portfolio_service.delete_portfolio(portfolio["id"])
                st.success("Portfolio eliminado.")
                st.rerun()
            except ApiError as e:
                st.error(str(e))
else:
    st.info("Aún no tienes portfolios creados.")


selected_id = st.session_state.get("selected_portfolio_id")
if not selected_id:
    st.stop()


try:
    detail = portfolio_service.get_portfolio(selected_id)
except ApiError as e:
    st.error(str(e))
    st.stop()

st.divider()
st.subheader(f"Detalle: {detail.get('name')}")

render_metrics(
    [
        ("Valor total", formatters.format_currency(detail.get("total_value"), detail.get("base_currency", "USD"))),
        ("Costo total", formatters.format_currency(detail.get("total_cost"), detail.get("base_currency", "USD"))),
        ("Ganancia/pérdida", formatters.format_currency(detail.get("total_gain_loss"), detail.get("base_currency", "USD"))),
        ("Variación", formatters.format_percentage(detail.get("total_gain_loss_percent"))),
    ]
)

left, right = st.columns([1, 1])
with left:
    allocation_pie(detail)
with right:
    st.caption("Posiciones")
    assets = detail.get("assets", [])
    if assets:
        df = pd.DataFrame(assets)
        df["position_value_fmt"] = df.apply(lambda row: formatters.format_currency(row["position_value"], detail.get("base_currency", "USD")), axis=1)
        df["gain_loss_fmt"] = df.apply(lambda row: formatters.format_currency(row["gain_loss"], detail.get("base_currency", "USD")), axis=1)
        df["gain_loss_percent_fmt"] = df["gain_loss_percent"].apply(formatters.format_percentage)
        st.dataframe(
            df[
                [
                    "asset_symbol",
                    "quantity",
                    "average_price",
                    "current_price",
                    "position_value_fmt",
                    "gain_loss_fmt",
                    "gain_loss_percent_fmt",
                ]
            ].rename(
                columns={
                    "asset_symbol": "Activo",
                    "quantity": "Cantidad",
                    "average_price": "Precio prom.",
                    "current_price": "Precio actual",
                    "position_value_fmt": "Valor",
                    "gain_loss_fmt": "G/P",
                    "gain_loss_percent_fmt": "% G/P",
                }
            ),
            use_container_width=True,
        )
    else:
        st.info("Aún no hay posiciones en este portfolio.")

"""Operations management page."""
import pandas as pd
import streamlit as st
from datetime import datetime, date

from frontend.components.auth import render_user_sidebar
from frontend.components.metrics import render_metrics
from frontend.components.operation_form import render_operation_form
from frontend.services.api_client import ApiError
from frontend.services.auth_service import AuthService
from frontend.services.operation_service import OperationService
from frontend.services.portfolio_service import PortfolioService
from frontend.utils import formatters
from frontend.utils import session as session_utils


st.set_page_config(layout="wide", page_title="Operaciones")
session_utils.init_session_state()

auth_service = AuthService()
portfolio_service = PortfolioService()
operation_service = OperationService()

with st.sidebar:
    if session_utils.is_authenticated():
        render_user_sidebar(auth_service)
    else:
        st.info("Inicia sesión en la página principal.")


if not session_utils.is_authenticated():
    st.warning("Se requiere inicio de sesión para gestionar operaciones.")
    st.stop()

st.title("Operaciones")
st.caption("Registra compras y ventas, consulta historial y estadísticas.")

try:
    portfolios = portfolio_service.list_portfolios()
except ApiError as e:
    st.error(str(e))
    st.stop()

if not portfolios:
    st.info("Crea un portfolio primero para registrar operaciones.")
    st.stop()

portfolio_names = [p["name"] for p in portfolios]
default_portfolio = portfolio_names[0]
selected_name = st.selectbox("Portfolio", portfolio_names, index=portfolio_names.index(default_portfolio))
selected_portfolio_id = next(p["id"] for p in portfolios if p["name"] == selected_name)

# Quick stats
try:
    stats = operation_service.get_statistics(selected_portfolio_id)
except ApiError as e:
    st.error(str(e))
    stats = None

if stats:
    render_metrics(
        [
            ("Operaciones", str(stats.get("total_operations", 0))),
            ("Compras", str(stats.get("total_buys", 0))),
            ("Ventas", str(stats.get("total_sells", 0))),
            ("Invertido", formatters.format_currency(stats.get("total_invested"), "USD")),
            ("Retirado", formatters.format_currency(stats.get("total_withdrawn"), "USD")),
            ("Comisiones", formatters.format_currency(stats.get("total_fees"), "USD")),
        ]
    )

st.divider()
st.subheader("Registrar nueva operación")
payload = render_operation_form(portfolios)
if payload:
    try:
        operation_service.create_operation(**payload)
        st.success("Operación registrada.")
        st.rerun()
    except ApiError as e:
        st.error(str(e))

st.divider()
st.subheader("Historial")

col_filters = st.columns([1, 1, 1])
asset_filter = col_filters[0].text_input("Activo", placeholder="AAPL, MSFT...")
type_filter = col_filters[1].selectbox("Tipo", ["Todos", "BUY", "SELL"])
enable_date_filter = col_filters[2].checkbox("Filtrar por fecha")

operation_type = None if type_filter == "Todos" else type_filter
date_from_str = None
date_to_str = None

if enable_date_filter:
    d1, d2 = st.columns(2)
    date_from = d1.date_input("Desde", value=date.today())
    date_to = d2.date_input("Hasta", value=date.today())
    date_from_str = date_from.isoformat()
    date_to_str = date_to.isoformat()

try:
    operations = operation_service.list_operations(
        portfolio_id=selected_portfolio_id,
        asset_symbol=asset_filter or None,
        operation_type=operation_type,
        date_from=date_from_str,
        date_to=date_to_str,
        limit=200,
    )
except ApiError as e:
    st.error(str(e))
    operations = []

if operations:
    df = pd.DataFrame(operations)
    df["operation_date"] = pd.to_datetime(df["operation_date"])
    df = df.sort_values("operation_date", ascending=False)
    df["total_amount_fmt"] = df["total_amount"].apply(formatters.format_currency)
    df["price_fmt"] = df["price"].apply(formatters.format_currency)
    df["quantity_fmt"] = df["quantity"].apply(formatters.format_number)
    st.dataframe(
        df[
            ["operation_date", "operation_type", "asset_symbol", "quantity_fmt", "price_fmt", "total_amount_fmt", "notes"]
        ].rename(
            columns={
                "operation_date": "Fecha",
                "operation_type": "Tipo",
                "asset_symbol": "Activo",
                "quantity_fmt": "Cantidad",
                "price_fmt": "Precio",
                "total_amount_fmt": "Total",
                "notes": "Notas",
            }
        ),
        use_container_width=True,
    )
else:
    st.info("No hay operaciones registradas con los filtros actuales.")

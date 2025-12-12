"""Market data and search page."""
import streamlit as st

from frontend.components.auth import render_user_sidebar
from frontend.components.charts import price_history_chart
from frontend.components.metrics import render_metrics
from frontend.services.api_client import ApiError
from frontend.services.auth_service import AuthService
from frontend.services.market_service import MarketService
from frontend.utils import session as session_utils


st.set_page_config(layout="wide", page_title="Mercado")
session_utils.init_session_state()

auth_service = AuthService()
market_service = MarketService()

with st.sidebar:
    if session_utils.is_authenticated():
        render_user_sidebar(auth_service)
    else:
        st.caption("Puedes consultar mercado sin iniciar sesión.")

st.title("Mercado")
st.caption("Busca activos, consulta información y precios históricos.")

search_query = st.text_input("Símbolo o nombre")
limit = st.slider("Resultados", min_value=5, max_value=50, value=10, step=5)

if st.button("Buscar") and search_query:
    try:
        st.session_state.market_results = market_service.search_assets(search_query, limit=limit)
    except ApiError as e:
        st.error(str(e))

results = st.session_state.get("market_results", [])

if results:
    symbols = [f"{r['symbol']} - {r['name']}" for r in results]
    selection = st.selectbox("Selecciona un activo", symbols)
    selected_symbol = selection.split(" - ")[0]

    info_col, price_col = st.columns([1, 1])
    try:
        asset_info = market_service.get_asset_info(selected_symbol)
        with info_col:
            st.subheader(asset_info.get("symbol"))
            st.write(asset_info.get("name", ""))
            st.write(f"Tipo: {asset_info.get('asset_type')}")
            st.write(f"Moneda: {asset_info.get('currency')}")
            if asset_info.get("exchange"):
                st.write(f"Exchange: {asset_info.get('exchange')}")
            if asset_info.get("description"):
                st.caption(asset_info["description"])
    except ApiError as e:
        st.error(str(e))
        asset_info = None

    with price_col:
        try:
            current = market_service.get_current_price(selected_symbol)
            render_metrics([("Precio actual", f"{current.get('price')} {current.get('currency', 'USD')}")])
        except ApiError as e:
            st.error(str(e))

    days = st.slider("Días de histórico", min_value=7, max_value=100, value=30, step=7)
    try:
        history = market_service.get_historical_prices(selected_symbol, days=days)
        price_history_chart(history)
    except ApiError as e:
        st.error(str(e))
else:
    st.info("Busca un activo para ver resultados.")

"""Operation entry form."""
from datetime import date, datetime
from typing import Dict, List, Optional
import streamlit as st

from frontend.utils import validators


def render_operation_form(portfolios: List[Dict]) -> Optional[Dict]:
    """Render a buy/sell form. Returns payload dict when submitted and valid."""
    if not portfolios:
        st.info("Crea un portfolio antes de registrar operaciones.")
        return None

    portfolio_options = {p["name"]: p["id"] for p in portfolios}

    with st.form("operation_form"):
        portfolio_name = st.selectbox("Portfolio", list(portfolio_options.keys()))
        asset_symbol = st.text_input("Símbolo del activo")
        op_type = st.radio("Tipo", ["BUY", "SELL"], horizontal=True)
        quantity = st.number_input("Cantidad", min_value=0.0, step=0.01, format="%.4f")
        price = st.number_input("Precio", min_value=0.0, step=0.01, format="%.4f")
        fees = st.number_input("Comisiones", min_value=0.0, step=0.01, format="%.4f", value=0.0)
        op_date = st.date_input("Fecha", value=date.today())
        op_time = st.time_input("Hora", value=datetime.now().time().replace(second=0, microsecond=0))
        notes = st.text_area("Notas", height=80)
        submitted = st.form_submit_button("Guardar operación")

    if not submitted:
        return None

    errors = []
    q_error = validators.validate_positive_number(quantity, "Cantidad")
    if q_error:
        errors.append(q_error)
    p_error = validators.validate_positive_number(price, "Precio")
    if p_error:
        errors.append(p_error)
    d_error = validators.validate_not_future(op_date, "Fecha")
    if d_error:
        errors.append(d_error)

    if errors:
        for err in errors:
            st.error(err)
        return None

    operation_datetime = datetime.combine(op_date, op_time)

    return {
        "portfolio_id": portfolio_options[portfolio_name],
        "asset_symbol": asset_symbol,
        "operation_type": op_type,
        "quantity": quantity,
        "price": price,
        "fees": fees,
        "operation_date": operation_datetime,
        "notes": notes or None,
    }

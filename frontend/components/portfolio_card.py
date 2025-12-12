"""Portfolio summary card."""
import streamlit as st

from frontend.utils import formatters


def portfolio_card(portfolio: dict) -> dict:
    """
    Render a portfolio card and return pressed actions.

    Returns a dict with boolean flags: {"view": bool, "delete": bool}
    """
    actions = {"view": False, "delete": False}
    card_key = portfolio.get("id", "")

    with st.container(border=True):
        st.subheader(portfolio.get("name", "Portfolio"))
        st.caption(portfolio.get("description") or "Sin descripción")

        cols = st.columns(4)
        cols[0].metric("Valor", formatters.format_currency(portfolio.get("total_value"), portfolio.get("base_currency", "USD")))
        cols[1].metric("Costo", formatters.format_currency(portfolio.get("total_cost"), portfolio.get("base_currency", "USD")))
        gain = formatters.format_currency(portfolio.get("total_gain_loss"), portfolio.get("base_currency", "USD"))
        cols[2].metric("Ganancia/Pérdida", gain)
        cols[3].metric("Variación", formatters.format_percentage(portfolio.get("total_gain_loss_percent")))

        c1, c2 = st.columns([1, 1])
        if c1.button("Ver detalle", key=f"view_{card_key}"):
            actions["view"] = True
        if c2.button("Eliminar", key=f"delete_{card_key}"):
            actions["delete"] = True

    return actions

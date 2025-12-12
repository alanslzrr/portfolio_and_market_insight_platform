"""Plotly chart helpers."""
from typing import Dict, List
import pandas as pd
import plotly.express as px
import streamlit as st


def allocation_pie(portfolio_detail: Dict) -> None:
    assets: List[Dict] = portfolio_detail.get("assets", [])
    if not assets:
        st.info("Aún no hay posiciones en este portfolio.")
        return

    data = [
        {"Activo": asset["asset_symbol"], "Valor": float(asset["position_value"])}
        for asset in assets
    ]
    df = pd.DataFrame(data)
    fig = px.pie(df, values="Valor", names="Activo", title="Distribución del portfolio", hole=0.35)
    st.plotly_chart(fig, use_container_width=True)


def price_history_chart(history: Dict) -> None:
    prices = history.get("prices", [])
    if not prices:
        st.info("No hay datos históricos disponibles.")
        return
    df = pd.DataFrame(prices)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
    fig = px.line(df, x="timestamp", y="close_price", title="Histórico de precios", markers=True)
    st.plotly_chart(fig, use_container_width=True)

"""Reusable metric blocks."""
from typing import Iterable, Tuple
import streamlit as st


def render_metrics(pairs: Iterable[Tuple[str, str]]) -> None:
    pairs = list(pairs)
    if not pairs:
        return
    cols = st.columns(len(pairs))
    for col, (label, value) in zip(cols, pairs):
        col.metric(label, value)

"""Display helpers for numbers, dates, and labels."""
from datetime import datetime
from typing import Any, Optional


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_currency(amount: Any, currency: str = "USD") -> str:
    """Format a numeric amount as currency text."""
    value = _to_float(amount)
    if value is None:
        return "-"
    return f"{currency} {value:,.2f}"


def format_percentage(value: Any) -> str:
    """Format a numeric value as percentage text."""
    number = _to_float(value)
    if number is None:
        return "-"
    return f"{number:,.2f}%"


def format_number(value: Any, decimals: int = 2) -> str:
    """Format a generic number with a fixed decimal count."""
    number = _to_float(value)
    if number is None:
        return "-"
    return f"{number:,.{decimals}f}"


def format_date(value: Optional[datetime]) -> str:
    """Format a date for display."""
    if not value:
        return "-"
    return value.strftime("%Y-%m-%d")


def format_datetime(value: Optional[datetime]) -> str:
    """Format a datetime for display."""
    if not value:
        return "-"
    return value.strftime("%Y-%m-%d %H:%M")


def format_relative_time(value: Optional[datetime]) -> str:
    """Return a human readable relative time string."""
    if not value:
        return "-"
    delta = datetime.utcnow() - value
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def format_operation_type(value: str) -> str:
    """Render operation type consistently."""
    return "Buy" if str(value).upper() == "BUY" else "Sell"


def color_for_gain_loss(value: Any) -> str:
    """Return color name depending on sign."""
    number = _to_float(value)
    if number is None or number == 0:
        return "gray"
    return "green" if number > 0 else "red"

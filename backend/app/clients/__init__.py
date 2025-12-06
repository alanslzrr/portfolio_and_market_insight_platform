"""
clientes para servicios externos.

este paquete contiene los clientes para integraciones con APIs externas:
- alpha_vantage: datos de mercado financiero
- openai: analisis con inteligencia artificial
"""

from app.clients.alpha_vantage_client import AlphaVantageClient
from app.clients.openai_client import OpenAIClient

__all__ = ["AlphaVantageClient", "OpenAIClient"]

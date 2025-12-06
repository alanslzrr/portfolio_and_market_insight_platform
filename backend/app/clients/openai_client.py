"""
Cliente para OpenAI API.

Proporciona metodos para generar analisis de mercado usando GPT-5 mini
a traves de la API de Responses de OpenAI.
"""
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI, OpenAIError
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Cliente para interactuar con OpenAI Responses API.
    
    Utiliza GPT-5 mini para generar analisis financieros de activos y portfolios.
    Implementacion simple y robusta sin logica de reintentos.
    
    Attributes:
        DEFAULT_MODEL: modelo por defecto a utilizar
        MAX_COMPLETION_TOKENS: limite de tokens para la respuesta
    """

    DEFAULT_MODEL = "gpt-5-mini"
    MAX_COMPLETION_TOKENS = 5000

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el cliente de OpenAI.
        
        Args:
            api_key: clave de API opcional, usa settings si no se proporciona
        """
        self.api_key = api_key or settings.openai_api_key

        if not self.api_key:
            logger.warning("OpenAI API Key no configurada.")
            self.client: Optional[OpenAI] = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        """Verifica si el cliente esta disponible para usar."""
        return self.client is not None

    def generate_analysis(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """
        Genera analisis usando OpenAI Responses API.
        
        Args:
            prompt: texto del prompt para el analisis
            model: modelo a usar, por defecto gpt-5-mini
            max_completion_tokens: tokens maximos de respuesta, por defecto 5000
            
        Returns:
            texto del analisis generado o None si falla
        """
        if not self.is_available():
            logger.error("Cliente OpenAI no disponible.")
            return None

        model = model or self.DEFAULT_MODEL
        max_tokens = max_completion_tokens or self.MAX_COMPLETION_TOKENS

        try:
            logger.info(f"Solicitando analisis a {model}...")
            response = self.client.responses.create(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un analista financiero experto. Tus analisis son "
                            "objetivos, basados en datos tecnicos y siempre incluyen "
                            "disclaimers apropiados. No das consejos de inversion directos."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                max_output_tokens=max_tokens,
            )

            return self._extract_text_from_response(response)

        except Exception as e:
            logger.error(
                "Error al generar analisis con OpenAI.",
                extra={
                    "exception": str(e),
                    "model": model,
                    "max_completion_tokens": max_tokens,
                    "prompt_preview": prompt[:300] if prompt else None,
                },
            )
            return None

    def _extract_text_from_response(self, response: Any) -> Optional[str]:
        """
        Extrae el texto de la respuesta de OpenAI Responses API.
        
        Intenta multiples estrategias para extraer el contenido:
        1. Campo output_text directo
        2. Campo reasoning.summary para modelos con razonamiento
        3. Recorrido de output[].summary para items de tipo reasoning
        4. Recorrido de output[].content[].text para items de tipo message
        
        Args:
            response: objeto de respuesta de la API
            
        Returns:
            texto extraido o None si no se encuentra contenido
        """
        try:
            # Estrategia 1: campo output_text directo
            output_text = getattr(response, "output_text", None)
            if output_text:
                text_str = str(output_text).strip()
                if text_str:
                    return text_str

            # Estrategia 2: campo reasoning.summary a nivel de respuesta
            reasoning = getattr(response, "reasoning", None)
            if reasoning:
                summary = None
                if isinstance(reasoning, dict):
                    summary = reasoning.get("summary")
                else:
                    summary = getattr(reasoning, "summary", None)
                
                if summary and isinstance(summary, str) and summary.strip():
                    return summary.strip()

            # Estrategia 3 y 4: recorrer items de output
            parts: List[str] = []
            output_items = getattr(response, "output", None)
            
            if isinstance(output_items, dict):
                output_items = output_items.get("output")

            if not output_items:
                logger.error("Respuesta de OpenAI sin campo 'output'.")
                return None

            for item in output_items:
                item_type = self._get_item_type(item)
                
                # Extraer summary de items de tipo reasoning
                if item_type == "reasoning":
                    summary_text = self._extract_summary_from_item(item)
                    if summary_text:
                        parts.append(summary_text)
                    continue
                
                # Extraer content de items de tipo message
                content_text = self._extract_content_from_item(item)
                if content_text:
                    parts.append(content_text)

            analysis_text = "\n".join(parts).strip()
            if analysis_text:
                return analysis_text

            logger.error("Respuesta de OpenAI sin contenido de texto utilizable.")
            return None

        except Exception as parse_exc:
            logger.error(
                "Error al parsear la respuesta de OpenAI.",
                extra={"exception": str(parse_exc)},
            )
            return None

    def _get_item_type(self, item: Any) -> Optional[str]:
        """Obtiene el tipo de un item de output."""
        if isinstance(item, dict):
            return item.get("type")
        return getattr(item, "type", None)

    def _extract_summary_from_item(self, item: Any) -> Optional[str]:
        """Extrae el texto de summary de un item de tipo reasoning."""
        summary_list = None
        if isinstance(item, dict):
            summary_list = item.get("summary")
        else:
            summary_list = getattr(item, "summary", None)
        
        if not summary_list or not isinstance(summary_list, list):
            return None

        parts = []
        for summ in summary_list:
            if isinstance(summ, str):
                parts.append(summ)
            elif isinstance(summ, dict):
                text = summ.get("text") or summ.get("value")
                if text:
                    parts.append(str(text))
            else:
                text = getattr(summ, "text", None) or getattr(summ, "value", None)
                if text:
                    parts.append(str(text))
        
        return " ".join(parts) if parts else None

    def _extract_content_from_item(self, item: Any) -> Optional[str]:
        """Extrae el texto de content de un item."""
        content_list = None
        if isinstance(item, dict):
            content_list = item.get("content")
        else:
            content_list = getattr(item, "content", None)

        if not content_list:
            return None

        parts = []
        for content in content_list:
            # Extraer el campo text directamente
            text_value = None
            if isinstance(content, dict):
                text_value = content.get("text")
            else:
                text_value = getattr(content, "text", None)

            if text_value:
                # El text puede ser string directo u objeto
                if isinstance(text_value, str):
                    parts.append(text_value)
                else:
                    extracted = self._extract_value(text_value)
                    if extracted:
                        parts.append(extracted)

        return "\n".join(parts) if parts else None

    def _extract_value(self, text_obj: Any) -> Optional[str]:
        """
        Extrae el valor de texto de un objeto text.
        
        Maneja diferentes estructuras:
        - string directo
        - dict con clave value
        - dict con clave segments (lista recursiva)
        - objeto con atributo value
        - lista de fragmentos
        """
        if text_obj is None:
            return None
            
        if isinstance(text_obj, str):
            return text_obj
            
        if isinstance(text_obj, dict):
            if "value" in text_obj and text_obj["value"] is not None:
                return str(text_obj["value"])
            
            if "segments" in text_obj and isinstance(text_obj["segments"], list):
                seg_parts = []
                for seg in text_obj["segments"]:
                    v = self._extract_value(seg)
                    if v:
                        seg_parts.append(v)
                return " ".join(seg_parts) if seg_parts else None
        
        if isinstance(text_obj, list):
            sub_parts = []
            for frag in text_obj:
                v = self._extract_value(frag)
                if v:
                    sub_parts.append(v)
            return " ".join(sub_parts) if sub_parts else None
        
        value = getattr(text_obj, "value", None)
        if value is not None:
            return str(value)
        
        return str(text_obj)

    def generate_asset_analysis(
        self,
        symbol: str,
        indicators: Dict[str, Any],
        price_history: List[Dict[str, float]],
    ) -> Optional[str]:
        """
        Genera analisis tecnico de un activo especifico.
        
        Args:
            symbol: simbolo del activo
            indicators: diccionario con indicadores tecnicos calculados
            price_history: historial de precios del activo
            
        Returns:
            texto del analisis o None si falla
        """
        if not self.is_available():
            return None

        prompt = self._build_asset_prompt(symbol, indicators, price_history)
        return self.generate_analysis(prompt)

    def generate_portfolio_analysis(
        self,
        portfolio_data: Dict[str, Any],
        positions: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Genera analisis de un portfolio completo.
        
        Args:
            portfolio_data: datos generales del portfolio
            positions: lista de posiciones en el portfolio
            
        Returns:
            texto del analisis o None si falla
        """
        if not self.is_available():
            return None

        prompt = self._build_portfolio_prompt(portfolio_data, positions)
        return self.generate_analysis(prompt)

    def _build_asset_prompt(
        self,
        symbol: str,
        indicators: Dict[str, Any],
        price_history: List[Dict[str, float]],
    ) -> str:
        """
        Construye el prompt para analisis de activo individual.
        
        Args:
            symbol: simbolo del activo
            indicators: indicadores tecnicos calculados
            price_history: historial de precios
            
        Returns:
            prompt formateado para el modelo
        """
        if len(price_history) >= 2:
            latest_price = price_history[0]["close"]
            week_ago_price = price_history[min(5, len(price_history) - 1)]["close"]
            price_change = (
                (latest_price - week_ago_price) / week_ago_price
            ) * 100
        else:
            latest_price = indicators.get("current_price", 0)
            price_change = 0

        prompt = f"""ANALISIS TECNICO: {symbol}

DATOS DE MERCADO:
- Precio actual: ${latest_price:.2f}
- Variacion semanal: {price_change:+.2f}%

INDICADORES TECNICOS:"""

        if indicators.get("rsi"):
            prompt += f"\n- RSI(14): {indicators['rsi']:.2f}"

        if indicators.get("macd"):
            macd = indicators["macd"]
            prompt += (
                f"\n- MACD: {macd['macd']:.2f} | Signal: {macd['signal']:.2f} | "
                f"Histogram: {macd['macd'] - macd['signal']:.2f}"
            )

        if indicators.get("trend"):
            prompt += f"\n- Tendencia identificada: {indicators['trend']}"

        prompt += """

REQUERIMIENTOS DEL ANALISIS (200 palabras):

1. MOMENTUM Y DIRECCION
   - Evalua la fuerza direccional basandote en RSI y variacion de precio
   - Identifica si el momentum es sostenible o muestra senales de agotamiento

2. ESTRUCTURA TECNICA
   - Interpreta la relacion MACD/Signal y su divergencia
   - Analiza la coherencia entre indicadores (convergencia/divergencia)

3. NIVELES CRITICOS
   - Identifica zonas de soporte/resistencia tecnica implicitas
   - Establece rangos de volatilidad esperada

4. CONTEXTO DE RIESGO
   - Evalua condiciones de sobrecompra/sobreventa
   - Describe el perfil riesgo/retorno actual del activo

Utiliza terminologia tecnica profesional: momentum, volatilidad implicita, niveles tecnicos,
presion compradora/vendedora, consolidacion, breakout potencial, rango operativo."""
        return prompt

    def _build_portfolio_prompt(
        self,
        portfolio_data: Dict[str, Any],
        positions: List[Dict[str, Any]],
    ) -> str:
        """
        Construye el prompt para analisis de portfolio.
        
        Args:
            portfolio_data: metricas generales del portfolio
            positions: lista de posiciones activas
            
        Returns:
            prompt formateado para el modelo
        """
        total_value = portfolio_data.get("total_value", 0)
        gain_loss_percent = portfolio_data.get("gain_loss_percent", 0)

        prompt = f"""ANALISIS DE CARTERA

METRICAS GENERALES:
- Valor total bajo gestion: ${total_value:,.2f}
- Performance acumulado: {gain_loss_percent:+.2f}%

COMPOSICION TOP 10 POSICIONES:"""

        for pos in positions[:10]:
            symbol = pos.get("symbol", "?")
            value = pos.get("value", 0)
            weight = (value / total_value * 100) if total_value > 0 else 0
            prompt += (
                f"\n- {symbol}: ${value:,.2f} ({weight:.1f}% del total)"
            )

        prompt += """

REQUERIMIENTOS DEL ANALISIS (250 palabras):

1. EVALUACION DE CONCENTRACION
   - Analiza la distribucion de capital y concentracion en top holdings
   - Identifica concentracion sectorial o por clase de activo si es evidente
   - Evalua el impacto de las posiciones principales en el riesgo agregado

2. PERFIL DE RIESGO ESTRUCTURAL
   - Describe el balance entre posiciones de alta y baja capitalizacion
   - Identifica exposicion implicita a factores de riesgo (growth/value, sectorial)
   - Evalua la correlacion esperada entre holdings principales

3. EFICIENCIA DE DIVERSIFICACION
   - Analiza si el numero de posiciones y su ponderacion optimiza la diversificacion
   - Identifica posibles redundancias o gaps en la cobertura de sectores
   - Evalua la relacion riesgo idiosincratico vs. riesgo sistematico

4. INTERPRETACION DE PERFORMANCE
   - Contextualiza el rendimiento acumulado en terminos de volatilidad esperada
   - Identifica drivers principales del retorno (concentracion en ganadores/perdedores)
   - Describe la consistencia del performance y posibles fuentes de alpha/beta

Utiliza terminologia institucional: diversificacion, concentracion de riesgo, beta implicito,
correlacion de activos, tracking error, drawdown potential, factor exposure, capital allocation efficiency."""
        return prompt
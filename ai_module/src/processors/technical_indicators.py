"""
procesador de indicadores tecnicos.

calcula indicadores tecnicos comunes usados en analisis financiero:
- rsi (relative strength index)
- macd (moving average convergence divergence)
- medias moviles simples y exponenciales
- volatilidad
- bandas de bollinger

estos indicadores se usan para generar analisis con ia.
"""
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal
import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    procesador de indicadores tecnicos.
    
    calcula indicadores tecnicos a partir de datos historicos de precios.
    usa pandas y numpy para calculos eficientes.
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        calcula relative strength index (rsi).
        
        el rsi mide la magnitud de cambios de precio recientes para evaluar
        condiciones de sobrecompra o sobreventa.
        
        interpretacion:
        - rsi > 70: sobrecomprado (posible correccion)
        - rsi < 30: sobrevendido (posible rebote)
        - rsi ~ 50: neutral
        
        args:
            prices: lista de precios de cierre (mas reciente primero)
            period: periodo de calculo (default 14 dias)
            
        returns:
            valor de rsi (0-100) o none si no hay suficientes datos
        """
        if len(prices) < period + 1:
            logger.warning(f"insuficientes datos para calcular rsi (necesita {period + 1}, tiene {len(prices)})")
            return None
        
        try:
            # convertir a pandas series (invertir orden para tener cronologico)
            prices_series = pd.Series(prices[::-1])
            
            # calcular cambios de precio
            delta = prices_series.diff()
            
            # separar ganancias y perdidas
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # calcular medias moviles de ganancias y perdidas
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # calcular rs (relative strength)
            rs = avg_gain / avg_loss
            
            # calcular rsi
            rsi = 100 - (100 / (1 + rs))
            
            # retornar valor mas reciente
            return float(rsi.iloc[-1])
            
        except Exception as e:
            logger.error(f"error calculando rsi: {e}")
            return None
    
    @staticmethod
    def calculate_macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Optional[Dict[str, float]]:
        """
        calcula moving average convergence divergence (macd).
        
        el macd muestra la relacion entre dos medias moviles exponenciales.
        
        interpretacion:
        - macd > signal: momentum alcista
        - macd < signal: momentum bajista
        - cruce de macd y signal: señal de compra/venta
        
        args:
            prices: lista de precios de cierre (mas reciente primero)
            fast_period: periodo ema rapida (default 12)
            slow_period: periodo ema lenta (default 26)
            signal_period: periodo linea señal (default 9)
            
        returns:
            diccionario con macd, signal y histogram o none
        """
        if len(prices) < slow_period + signal_period:
            logger.warning(f"insuficientes datos para calcular macd")
            return None
        
        try:
            # convertir a pandas series (invertir orden)
            prices_series = pd.Series(prices[::-1])
            
            # calcular emas
            ema_fast = prices_series.ewm(span=fast_period, adjust=False).mean()
            ema_slow = prices_series.ewm(span=slow_period, adjust=False).mean()
            
            # calcular macd line
            macd_line = ema_fast - ema_slow
            
            # calcular signal line (ema del macd)
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
            
            # calcular histogram (diferencia entre macd y signal)
            histogram = macd_line - signal_line
            
            return {
                "macd": float(macd_line.iloc[-1]),
                "signal": float(signal_line.iloc[-1]),
                "histogram": float(histogram.iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"error calculando macd: {e}")
            return None
    
    @staticmethod
    def calculate_moving_averages(
        prices: List[float],
        periods: List[int] = [20, 50, 200]
    ) -> Dict[int, float]:
        """
        calcula medias moviles simples (sma).
        
        las medias moviles suavizan datos de precios para identificar tendencias.
        
        interpretacion:
        - precio > ma: tendencia alcista
        - precio < ma: tendencia bajista
        - golden cross (ma50 cruza ma200 al alza): señal alcista fuerte
        - death cross (ma50 cruza ma200 a la baja): señal bajista fuerte
        
        args:
            prices: lista de precios de cierre (mas reciente primero)
            periods: periodos a calcular (default [20, 50, 200])
            
        returns:
            diccionario {periodo: valor_ma}
        """
        prices_series = pd.Series(prices[::-1])
        
        mas = {}
        for period in periods:
            if len(prices) >= period:
                ma = prices_series.rolling(window=period).mean()
                mas[period] = float(ma.iloc[-1])
            else:
                logger.warning(f"insuficientes datos para ma{period}")
        
        return mas
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 30) -> Optional[float]:
        """
        calcula volatilidad historica (desviacion estandar de retornos).
        
        la volatilidad mide la dispersion de retornos.
        alta volatilidad indica mayor riesgo pero tambien mayor potencial.
        
        args:
            prices: lista de precios de cierre (mas reciente primero)
            period: periodo de calculo (default 30 dias)
            
        returns:
            volatilidad anualizada (%) o none
        """
        if len(prices) < period + 1:
            return None
        
        try:
            prices_series = pd.Series(prices[::-1])
            
            # calcular retornos logaritmicos
            returns = np.log(prices_series / prices_series.shift(1))
            
            # calcular desviacion estandar de retornos
            volatility = returns.std()
            
            # anualizar (asumiendo 252 dias de trading)
            annualized_volatility = volatility * np.sqrt(252) * 100
            
            return float(annualized_volatility)
            
        except Exception as e:
            logger.error(f"error calculando volatilidad: {e}")
            return None
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Optional[Dict[str, float]]:
        """
        calcula bandas de bollinger.
        
        las bandas muestran volatilidad y niveles de sobrecompra/sobreventa.
        
        interpretacion:
        - precio cerca de banda superior: posible sobrecompra
        - precio cerca de banda inferior: posible sobreventa
        - bandas estrechas: baja volatilidad, posible ruptura proxima
        - bandas amplias: alta volatilidad
        
        args:
            prices: lista de precios de cierre (mas reciente primero)
            period: periodo de la media movil (default 20)
            std_dev: numero de desviaciones estandar (default 2)
            
        returns:
            diccionario con upper, middle, lower o none
        """
        if len(prices) < period:
            return None
        
        try:
            prices_series = pd.Series(prices[::-1])
            
            # calcular media movil (banda media)
            middle_band = prices_series.rolling(window=period).mean()
            
            # calcular desviacion estandar
            std = prices_series.rolling(window=period).std()
            
            # calcular bandas superior e inferior
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return {
                "upper": float(upper_band.iloc[-1]),
                "middle": float(middle_band.iloc[-1]),
                "lower": float(lower_band.iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"error calculando bandas de bollinger: {e}")
            return None
    
    @staticmethod
    def analyze_trend(prices: List[float], period: int = 20) -> str:
        """
        analiza la tendencia general del precio.
        
        compara el precio actual con la media movil para determinar tendencia.
        
        args:
            prices: lista de precios de cierre (mas reciente primero)
            period: periodo para analisis (default 20)
            
        returns:
            "alcista", "bajista" o "lateral"
        """
        if len(prices) < period:
            return "desconocido"
        
        current_price = prices[0]
        ma = TechnicalIndicators.calculate_moving_averages(prices, [period])
        
        if not ma:
            return "desconocido"
        
        ma_value = ma[period]
        
        # calcular diferencia porcentual
        diff_percent = ((current_price - ma_value) / ma_value) * 100
        
        if diff_percent > 2:
            return "alcista"
        elif diff_percent < -2:
            return "bajista"
        else:
            return "lateral"
    
    @staticmethod
    def calculate_all_indicators(
        prices: List[float]
    ) -> Dict[str, Any]:
        """
        calcula todos los indicadores disponibles.
        
        metodo de conveniencia que calcula todos los indicadores
        y retorna un diccionario completo.
        
        args:
            prices: lista de precios de cierre (mas reciente primero)
            
        returns:
            diccionario con todos los indicadores calculados
        """
        indicators = {
            "rsi": TechnicalIndicators.calculate_rsi(prices),
            "macd": TechnicalIndicators.calculate_macd(prices),
            "moving_averages": TechnicalIndicators.calculate_moving_averages(prices),
            "volatility": TechnicalIndicators.calculate_volatility(prices),
            "bollinger_bands": TechnicalIndicators.calculate_bollinger_bands(prices),
            "trend": TechnicalIndicators.analyze_trend(prices),
            "current_price": prices[0] if prices else None,
            "price_change_30d": ((prices[0] / prices[29]) - 1) * 100 if len(prices) >= 30 else None
        }
        
        return indicators


# ejemplo de uso:
#
# prices = [150.0, 149.5, 151.2, 148.9, ...]  # mas reciente primero
# 
# # calcular indicador individual
# rsi = TechnicalIndicators.calculate_rsi(prices)
# print(f"RSI: {rsi:.2f}")
# 
# # calcular todos los indicadores
# indicators = TechnicalIndicators.calculate_all_indicators(prices)
# print(f"Tendencia: {indicators['trend']}")
# print(f"Volatilidad: {indicators['volatility']:.2f}%")

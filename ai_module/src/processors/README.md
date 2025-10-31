# Procesadores de Datos Financieros

Este módulo contiene los procesadores que calculan indicadores técnicos y procesan datos históricos de precios antes de enviarlos a los analizadores. Estos procesadores transforman datos brutos en información estructurada útil para el análisis.

## Archivos que Contendrá

- **technical_indicators.py**: Cálculo de indicadores técnicos:
  - `calculate_rsi()`: Calcula Relative Strength Index (RSI)
  - `calculate_macd()`: Calcula Moving Average Convergence Divergence (MACD)
  - `calculate_moving_averages()`: Calcula medias móviles simples y exponenciales
  - `calculate_bollinger_bands()`: Calcula bandas de Bollinger
  - `calculate_stochastic()`: Calcula oscilador estocástico

- **price_analyzer.py**: Análisis de precios:
  - `identify_support_resistance()`: Identifica niveles de soporte y resistencia
  - `detect_patterns()`: Detecta patrones gráficos comunes (triángulos, head and shoulders, etc.)
  - `calculate_volatility()`: Calcula volatilidad histórica
  - `analyze_volume()`: Analiza volumen de trading

- **data_processor.py**: Procesador principal de datos:
  - `process_market_data()`: Función principal que procesa datos históricos
  - Coordina cálculo de todos los indicadores
  - Estructura datos para análisis
  - Valida calidad de datos
  - Maneja datos faltantes o inconsistentes

- **statistics.py**: Funciones estadísticas:
  - `calculate_returns()`: Calcula retornos diarios y acumulados
  - `calculate_volatility()`: Calcula volatilidad histórica
  - `calculate_correlation()`: Calcula correlación entre activos
  - `calculate_beta()`: Calcula beta respecto a un índice

## Funcionalidades

Los procesadores proporcionan:

- Cálculo de indicadores técnicos estándar de análisis técnico
- Identificación de patrones en gráficos de precios
- Análisis de volatilidad y riesgo
- Procesamiento y limpieza de datos históricos
- Estructuración de datos para análisis con IA

## Bibliotecas Utilizadas

Los procesadores utilizan:

- **Pandas**: Para manipulación de datos temporales
- **NumPy**: Para cálculos numéricos eficientes
- **TA-Lib** (opcional): Para indicadores técnicos avanzados

## Output

Los procesadores generan estructuras de datos que incluyen:

- Valores calculados de indicadores técnicos
- Identificación de patrones y niveles clave
- Métricas de volatilidad y riesgo
- Series temporales procesadas y validadas
- Datos estructurados listos para análisis con IA

## Validaciones

Los procesadores incluyen validaciones:

- Verificación de suficiencia de datos históricos
- Validación de calidad de datos (sin valores faltantes críticos)
- Verificación de consistencia temporal
- Manejo de outliers y datos anómalos


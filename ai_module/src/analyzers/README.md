# Analizadores de Datos Financieros

Este módulo contiene los analizadores principales que procesan datos financieros y generan análisis descriptivos mediante inteligencia artificial. Cada analizador está especializado en un tipo específico de análisis.

## Archivos que Contendrá

- **portfolio_analyzer.py**: Analizador de carteras completas:
  - `analyze_portfolio()`: Genera análisis completo de una cartera con múltiples activos
  - Procesa todas las posiciones de la cartera
  - Calcula métricas agregadas y distribuciones
  - Genera análisis de diversificación y riesgo
  - Identifica activos con mejor y peor rendimiento

- **asset_analyzer.py**: Analizador de activos individuales:
  - `analyze_asset()`: Genera análisis detallado de un activo específico
  - Analiza tendencias de precio a corto, medio y largo plazo
  - Identifica soportes y resistencias
  - Analiza volumen y volatilidad
  - Genera descripción de patrones técnicos identificados

- **trend_analyzer.py**: Analizador de tendencias:
  - `identify_trends()`: Identifica y describe tendencias en los datos
  - Detecta tendencias alcistas, bajistas y laterales
  - Identifica puntos de cambio de tendencia
  - Analiza fuerza de las tendencias
  - Genera descripciones en lenguaje natural de las tendencias

- **base_analyzer.py**: Clase base para analizadores:
  - Funcionalidad común compartida por todos los analizadores
  - Manejo de errores común
  - Validación de datos de entrada
  - Formateo de resultados

## Funcionalidades

Los analizadores proporcionan:

- Procesamiento de datos históricos de precios
- Cálculo de indicadores técnicos mediante procesadores
- Construcción de prompts estructurados para OpenAI
- Generación de análisis descriptivos en lenguaje natural
- Formateo y estructuración de resultados

## Integraciones

Los analizadores utilizan:

- **DataProcessors**: Para calcular indicadores técnicos
- **OpenAIClient**: Para generar análisis mediante IA
- **Templates**: Para construir prompts estructurados
- **Cache**: Para almacenar y recuperar análisis previos

## Output

Los analizadores generan análisis estructurados que incluyen:

- Texto descriptivo en lenguaje natural sobre tendencias y patrones
- Indicadores técnicos calculados (RSI, MACD, medias móviles)
- Identificación de patrones gráficos
- Métricas de volatilidad y riesgo
- Disclaimers legales sobre no constituir consejo financiero


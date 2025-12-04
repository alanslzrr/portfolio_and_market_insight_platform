# Plantillas de Prompts para Análisis

Este módulo contiene las plantillas de prompts que se utilizan para generar análisis mediante la API de OpenAI. Las plantillas están estructuradas para proporcionar contexto completo y obtener respuestas consistentes y útiles.

## Archivos que Contendrá

- **portfolio_template.py**: Plantilla para análisis de carteras:
  - `build_portfolio_prompt()`: Construye prompt estructurado para análisis de cartera completa
  - Incluye información de todas las posiciones
  - Incluye métricas agregadas de la cartera
  - Solicita análisis de diversificación y riesgo
  - Especifica formato de respuesta esperado

- **asset_template.py**: Plantilla para análisis de activos:
  - `build_asset_prompt()`: Construye prompt para análisis de activo individual
  - Incluye datos históricos de precios procesados
  - Incluye indicadores técnicos calculados
  - Solicita análisis de tendencias y patrones
  - Especifica qué aspectos cubrir en el análisis

- **trend_template.py**: Plantilla para análisis de tendencias:
  - `build_trend_prompt()`: Construye prompt para análisis de tendencias específicas
  - Incluye datos de series temporales
  - Solicita identificación y descripción de tendencias
  - Pide análisis de fuerza y sostenibilidad de tendencias

- **base_template.py**: Funciones base para construcción de prompts:
  - `format_technical_indicators()`: Formatea indicadores técnicos para incluir en prompt
  - `format_price_data()`: Formatea datos de precios para prompt
  - `add_context()`: Añade contexto adicional al prompt
  - `add_disclaimer()`: Añade disclaimer legal al prompt

## Estructura de Prompts

Los prompts están estructurados para:

- Proporcionar contexto completo sobre los datos financieros
- Incluir indicadores técnicos calculados previamente
- Solicitar análisis específicos y estructurados
- Incluir instrucciones sobre formato de respuesta
- Incluir disclaimers legales sobre no constituir consejo financiero

## Personalización

Las plantillas permiten:

- Personalización del nivel de detalle del análisis
- Selección de aspectos específicos a analizar
- Configuración de tono del análisis (técnico, simple, profesional)
- Inclusión de contexto adicional según necesidades

## Mejores Prácticas

Las plantillas siguen mejores prácticas:

- Prompts claros y específicos para obtener respuestas útiles
- Estructura consistente para facilitar procesamiento
- Inclusión de ejemplos cuando es apropiado
- Separación de datos y instrucciones en el prompt
- Validación de prompts antes de enviar a OpenAI


# Módulo de Análisis con Inteligencia Artificial

Este módulo es un componente independiente que procesa datos de mercado históricos y genera análisis descriptivos utilizando la API de OpenAI. El módulo está diseñado para ser utilizado por el backend principal pero mantiene una separación clara de responsabilidades.

## Estructura

- **src/analyzers/**: Contiene los analizadores principales que procesan datos y generan análisis
- **src/templates/**: Contiene plantillas de prompts para diferentes tipos de análisis
- **src/clients/**: Contiene clientes para servicios externos (OpenAI API)
- **src/processors/**: Contiene procesadores de datos que calculan indicadores técnicos

## Funcionalidades Principales

El módulo proporciona análisis descriptivos de:

- **Análisis de carteras**: Análisis completo de una cartera con múltiples activos
- **Análisis de activos individuales**: Análisis detallado de un activo específico
- **Análisis de tendencias**: Identificación y descripción de tendencias de mercado
- **Recomendaciones**: Sugerencias basadas en análisis técnico (con disclaimer)

## Flujo de Trabajo

1. Recibe datos históricos de precios desde el backend
2. Procesa los datos calculando indicadores técnicos (RSI, MACD, medias móviles)
3. Identifica patrones y tendencias en los datos
4. Construye un prompt estructurado con los datos procesados
5. Envía el prompt a OpenAI API para generar análisis descriptivo
6. Procesa y formatea la respuesta de OpenAI
7. Retorna el análisis al backend para almacenamiento y caché

## Archivos Principales

- **requirements.txt**: Dependencias del módulo (openai, pandas, numpy, etc.)
- **config.py**: Configuración del módulo (API keys, modelos, parámetros)
- **main.py**: Punto de entrada si se ejecuta como servicio independiente

## Integración

El módulo se integra con el backend mediante:

- **Llamadas directas**: El backend importa y utiliza las funciones del módulo
- **API REST**: Opcionalmente puede exponer una API REST para análisis independientes
- **Mensajería**: Opcionalmente puede integrarse mediante colas de mensajes para procesamiento asíncrono

## Consideraciones

- Los análisis incluyen disclaimers legales sobre no constituir consejo financiero
- Los análisis se cachean para evitar llamadas repetidas a OpenAI
- El módulo maneja rate limiting de OpenAI API
- Los análisis pueden tener TTL configurable para invalidación automática


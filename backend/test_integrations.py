"""
script de prueba para verificar integraciones externas.

este script verifica que:
1. alpha vantage client funciona correctamente
2. openai client funciona correctamente
3. indicadores tecnicos se calculan correctamente
4. las api keys estan configuradas

ejecutar desde backend/:
    python test_integrations.py
"""
import sys
import os
import logging

# configurar logging para ver errores
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# agregar el directorio ai_module al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.clients.alpha_vantage_client import AlphaVantageClient
from app.clients.openai_client import OpenAIClient
from ai_module.src.processors.technical_indicators import TechnicalIndicators


def test_alpha_vantage():
    """prueba el cliente de alpha vantage."""
    print("\n" + "="*32)
    print("PRUEBA 1: Cliente Alpha Vantage")
    print("="*32)
    
    try:
        with AlphaVantageClient() as client:
            # probar quote
            print("\nObteniendo cotización de AAPL...")
            quote = client.get_quote("AAPL")
            
            if quote:
                print(f"Quote obtenido correctamente:")
                print(f"   Simbolo: {quote['symbol']}")
                print(f"   Precio: ${quote['price']:.2f}")
                print(f"   Volumen: {quote['volume']:,}")
                print(f"   Cambio: {quote['change_percent']}")
            else:
                print("No se pudo obtener quote (verifica API key)")
            
            # probar búsqueda
            print("\nBuscando 'Apple'...")
            results = client.search_symbol("Apple")
            
            if results:
                print(f"Encontrados {len(results)} resultados:")
                for i, result in enumerate(results[:3], 1):
                    print(f"   {i}. {result['symbol']} - {result['name']}")
            else:
                print("No se encontraron resultados")
                
    except ValueError as e:
        print(f"Error: {e}")
        print("   Verifica que ALPHA_VANTAGE_API_KEY este configurada en config/.env")
    except Exception as e:
        print(f"Error inesperado: {e}")


def test_openai():
    """prueba el cliente de openai."""
    print("\n" + "="*32)
    print("PRUEBA 2: Cliente OpenAI")
    print("="*32)
    
    try:
        client = OpenAIClient()
        
        if not client.is_available():
            print("OpenAI client no disponible")
            print("   Verifica que OPENAI_API_KEY este configurada en config/.env")
            return
        
        print("\nGenerando análisis de prueba...")
        prompt = """
        Analiza brevemente el siguiente indicador técnico:
        - RSI: 65
        - Tendencia: Alcista
        
        Proporciona un análisis de 50 palabras máximo.
        """
        
        analysis = client.generate_analysis(prompt, max_completion_tokens=500)
        
        if analysis:
            print(f"Analisis generado correctamente:")
            print(f"\n{analysis[:200]}...")
        else:
            print("No se pudo generar analisis")
            
    except Exception as e:
        print(f"Error: {e}")


def test_technical_indicators():
    """prueba el procesador de indicadores tecnicos."""
    print("\n" + "="*32)
    print("PRUEBA 3: Indicadores Técnicos")
    print("="*32)
    
    try:
        # precios de ejemplo (30 días, más reciente primero)
        prices = [
            150.25, 149.80, 151.20, 148.90, 149.50,
            148.75, 150.00, 151.50, 152.25, 151.00,
            150.50, 149.25, 148.80, 150.10, 151.75,
            152.00, 151.25, 150.75, 149.90, 150.50,
            151.00, 150.25, 149.75, 150.50, 151.25,
            150.80, 149.90, 150.25, 151.00, 150.50
        ]
        
        print(f"\nCalculando indicadores para {len(prices)} días de precios...")
        
        # calcular todos los indicadores
        indicators = TechnicalIndicators.calculate_all_indicators(prices)
        
        print("\nIndicadores calculados correctamente:")
        
        if indicators.get('rsi'):
            print(f"   RSI (14): {indicators['rsi']:.2f}")
        
        if indicators.get('macd'):
            macd = indicators['macd']
            print(f"   MACD: {macd['macd']:.2f}")
            print(f"   Signal: {macd['signal']:.2f}")
            print(f"   Histogram: {macd['histogram']:.2f}")
        
        if indicators.get('moving_averages'):
            mas = indicators['moving_averages']
            print(f"   Medias Móviles:")
            for period, value in sorted(mas.items()):
                print(f"      MA{period}: ${value:.2f}")
        
        if indicators.get('volatility'):
            print(f"   Volatilidad: {indicators['volatility']:.2f}%")
        
        if indicators.get('trend'):
            print(f"   Tendencia: {indicators['trend']}")
            
    except Exception as e:
        print(f"Error: {e}")


def main():
    """ejecuta todas las pruebas."""
    print("\n" + "="*32)
    print("PRUEBAS DE INTEGRACIONES EXTERNAS")
    print("="*32)
    
    # prueba 1: alpha vantage
    test_alpha_vantage()
    
    # prueba 2: openai
    test_openai()
    
    # prueba 3: indicadores tecnicos
    test_technical_indicators()
    


if __name__ == "__main__":
    main()

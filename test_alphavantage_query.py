"""
Script de prueba y validación para el conector API de Alpha Vantage (News & Sentiment).
Consulta noticias sobre mercados financieros globales (topic: financial_markets) y muestra un resumen con puntuaciones de sentimiento.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Añadir ruta src al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.alphavantage_client import AlphaVantageClient


def print_news_table(news_items, title: str):
    """Imprime una tabla de noticias en la consola."""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)
    print(f"{'Fecha Publicación':<20} | {'Sentimiento':<18} | {'Titular (Resumen)':<55}")
    print("-" * 100)
    
    # Mostrar hasta las 10 noticias más relevantes/recientes
    for item in news_items[:10]:
        time_pub = item.get("time_published", "N/A")
        # Formato de fecha del BCCh/Alpha Vantage (YYYYMMDDTHHMMSS -> YYYY-MM-DD HH:MM)
        try:
            if "T" in time_pub:
                dt = datetime.strptime(time_pub, "%Y%m%dT%H%M%S")
                time_formatted = dt.strftime("%Y-%m-%d %H:%M")
            else:
                time_formatted = time_pub
        except Exception:
            time_formatted = time_pub

        score = item.get("overall_sentiment_score", 0.0)
        label = item.get("overall_sentiment_label", "Neutral")
        sentiment_str = f"{score:+.2f} ({label})"

        headline = item.get("title", "N/A")
        if len(headline) > 52:
            headline = headline[:49] + "..."

        print(f"{time_formatted:<20} | {sentiment_str:<18} | {headline:<55}")
    print("=" * 100 + "\n")


async def main():
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY")

    if not api_key or "tu_api_key" in api_key:
        print("\n" + "!" * 70)
        print("  AVISO: ALPHAVANTAGE_API_KEY no detectada en archivo .env")
        print("!" * 70)
        print("  1. Edita el archivo '.env'")
        print("  2. Configura ALPHAVANTAGE_API_KEY con tu clave de alphavantage.co")
        print("  3. Vuelve a ejecutar este script para la consulta en vivo.")
        print("!" * 70)
        return

    print(f"\n[INFO] Conectando con API de Alpha Vantage (News & Sentiment)...")
    print(f"[INFO] Tópico de consulta: financial_markets")

    client = AlphaVantageClient()

    try:
        data = await client.get_news_sentiment(topics="financial_markets", limit=15)
        
        feed = data.get("feed", [])
        
        if not feed:
            if "Note" in data or "Information" in data:
                print(f"❌ Rate limit detectado: {data.get('Note') or data.get('Information')}")
            else:
                print(f"[WARN] No se encontraron noticias recientes en la consulta.")
        else:
            print_news_table(feed, f"NOTICIAS DE MERCADOS FINANCIEROS Y SENTIMIENTO (Alpha Vantage)")
            print(f"✅ Consulta en vivo completada exitosamente. Artículos recuperados: {len(feed)}")

    except Exception as err:
        print(f"\n❌ La consulta a Alpha Vantage falló debido a una excepción: {type(err).__name__}")


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())

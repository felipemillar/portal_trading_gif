"""
Script de prueba y validación para el conector API de FRED.
Consulta en vivo la tasa de desempleo civil de EE. UU. (Serie: UNRATE) y presenta una tabla resumen.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Añadir ruta src al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.fred_client import FredClient


def print_fred_table(observations, title: str):
    """Imprime una tabla de observaciones económicas de FRED en la consola."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"{'Fecha (ISO)':<15} | {'Valor (Tasa de Desempleo %)':<30} | {'Estado':<10}")
    print("-" * 60)
    
    # Mostrar las últimas 12 observaciones
    for obs in observations[-12:]:
        date_str = obs.get("date", "N/A")
        val = obs.get("value")
        
        if val is None:
            val_str = "N/D"
            status = "ND"
        else:
            val_str = f"{val:.1f}%"
            status = "OK"

        print(f"{date_str:<15} | {val_str:<30} | {status:<10}")
    print("=" * 60 + "\n")


async def main():
    api_key = os.environ.get("FRED_API_KEY")

    if not api_key or "tu_api_key" in api_key:
        print("\n" + "!" * 70)
        print("  AVISO: FRED_API_KEY no detectada en archivo .env")
        print("!" * 70)
        print("  1. Edita el archivo '.env'")
        print("  2. Configura FRED_API_KEY con tu clave de FRED")
        print("  3. Vuelve a ejecutar este script para la consulta en vivo.")
        print("!" * 70)
        return

    print(f"\n[INFO] Conectando con API de FRED...")
    print(f"[INFO] Serie de consulta: UNRATE (U.S. Civilian Unemployment Rate)")

    client = FredClient()

    try:
        # Consultar observaciones de UNRATE correspondientes a los últimos dos años para mostrar los meses recientes
        current_year = datetime.now().year
        start_date = f"{current_year - 1}-01-01"

        data = await client.get_series_observations(
            series_id="UNRATE",
            observation_start=start_date
        )
        
        obs = data.get("observations", [])
        
        if not obs:
            print(f"[WARN] No se encontraron observaciones para la serie UNRATE.")
        else:
            print_fred_table(obs, f"TASA DE DESEMPLEO EE. UU. (Serie: UNRATE)")
            print(f"Consulta en vivo a FRED completada exitosamente. Observaciones obtenidas: {len(obs)}")

    except Exception as err:
        print(f"\nLa consulta a FRED falló debido a una excepción: {type(err).__name__}")


if __name__ == "__main__":
    asyncio.run(main())

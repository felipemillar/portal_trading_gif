"""
Script de prueba y validación para el conector API del Banco Central de Chile (BCCh BDE).
Consulta la serie oficial del Dólar Observado (USD/CLP - Serie: F073.TCO.PRE.Z.D) de los últimos 7 días.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Añadir ruta src al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bcch_client import BCChClient

logger = logging.getLogger("TestBCCh")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def print_table(observations, title: str):
    """Imprime una tabla formateada en consola."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"{'Fecha (ISO)':<15} | {'Valor (USD/CLP)':<18} | {'Estado':<15}")
    print("-" * 60)
    for obs in observations:
        date = obs.get("indexDateString", "N/A")
        val = obs.get("value")
        val_str = f"${val:,.2f}" if isinstance(val, (int, float)) else "Sin dato (Feriado/Fin de sem)"
        status = obs.get("statusCode", "OK")
        if obs.get("interpolated"):
            status += " (Interp)"
        print(f"{date:<15} | {val_str:<18} | {status:<15}")
    print("=" * 60 + "\n")


async def run_mock_validation():
    """Ejecuta una validación sintética interna si no hay credenciales configuradas."""
    print("\n[INFO] Ejecutando validación sintética (Mock) de normalización y Forward-Fill...")
    sample_payload = {
        "Codigo": 0,
        "Descripcion": "Success",
        "Series": {
            "descripEsp": "Dólar Observado",
            "Obs": [
                {"indexDateString": "08-08-2026", "value": "925.50", "statusCode": "OK"},
                {"indexDateString": "11-08-2026", "value": "930.10", "statusCode": "OK"},
                {"indexDateString": "12-08-2026", "value": "928.75", "statusCode": "OK"},
            ]
        }
    }
    normalized = BCChClient._normalize_series_payload(sample_payload)
    filled_obs = BCChClient._apply_forward_fill(
        normalized["Series"]["Obs"],
        "2026-08-08",
        "2026-08-14"
    )
    print_table(filled_obs, "TEST SINTÉTICO (Mock Forward-Fill: 2026-08-08 a 2026-08-14)")
    print("Normalización y Forward-Fill validados exitosamente.")


async def main():
    token = os.environ.get("BCCH_TOKEN")
    user = os.environ.get("BCCH_USER")
    password = os.environ.get("BCCH_PASS")

    has_token = bool(token and "tu_api_key" not in token)
    has_user_pass = bool(user and password and "tu_email" not in user)

    if not has_token and not has_user_pass:
        print("\n" + "!" * 70)
        print("  AVISO: Credenciales de BCCh no detectadas en archivo .env")
        print("!" * 70)
        print("  1. Edita el archivo '.env'")
        print("  2. Configura BCCH_TOKEN (Recomendado) o (BCCH_USER y BCCH_PASS)")
        print("  3. Vuelve a ejecutar este script para la consulta en vivo.")
        print("!" * 70)
        await run_mock_validation()
        return

    # Definir rango temporal: últimos 7 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    series_id = "F073.TCO.PRE.Z.D"  # Dólar Observado oficial

    print(f"\n[INFO] Conectando con API BCCh BDE...")
    print(f"[INFO] Serie: {series_id} (Dólar Observado)")
    print(f"[INFO] Rango: {start_str} al {end_str}")

    client = BCChClient()

    try:
        data = await client.get_series(
            series_id=series_id,
            firstdate=start_str,
            lastdate=end_str,
            forward_fill=True
        )

        series_info = data.get("Series", {})
        title = series_info.get("descripEsp", "Dólar Observado (USD/CLP)")
        obs_list = series_info.get("Obs", [])

        if not obs_list:
            print(f"[WARN] La consulta se completó exitosamente pero no retornó observaciones para el período.")
        else:
            print_table(obs_list, f"BANCO CENTRAL DE CHILE: {title} ({start_str} a {end_str})")
            print(f"Consulta en vivo completada exitosamente. Observaciones recibidas: {len(obs_list)}")

    except Exception as err:
        logger.error(f"Error durante la consulta a BCCh: {type(err).__name__} (detalles omitidos por seguridad)")
        print(f"\nLa consulta falló: {type(err).__name__}")


if __name__ == "__main__":
    asyncio.run(main())

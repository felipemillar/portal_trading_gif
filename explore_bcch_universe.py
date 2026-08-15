import os
import asyncio
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("BCCH_USER")
PASS = os.getenv("BCCH_PASS")
KEY = os.getenv("BCCH_KEY")

# If pass is empty or key is provided, use user/key or user/pass
PASSWORD = PASS or KEY

BASE_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

async def test_search_series(frequency: str):
    params = {
        "user": USER,
        "pass": PASSWORD,
        "function": "SearchSeries",
        "frequency": frequency
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(BASE_URL, params=params)
        print(f"Status Code ({frequency}):", resp.status_code)
        try:
            data = resp.json()
        except Exception:
            text = resp.content.decode("latin-1")
            data = json.loads(text)
            
        code = data.get("Codigo")
        desc = data.get("Descripcion")
        series = data.get("SeriesInfos", [])
        print(f"Frequency: {frequency} -> Codigo: {code}, Descripcion: {desc}, Total Series: {len(series)}")
        if series:
            print(f"  Primeras 3 series de ejemplo en {frequency}:")
            for s in series[:3]:
                print(f"    - ID: {s.get('seriesId')}")
                print(f"      Titulo ES: {s.get('spanishTitle')}")
                print(f"      Rango: {s.get('firstObservation')} a {s.get('lastObservation')}")
        return series

async def main():
    print(f"Iniciando exploracion de la API del Banco Central de Chile...")
    print(f"Usuario autenticado: {USER}")
    
    results = {}
    for freq in ["DAILY", "MONTHLY", "QUARTERLY", "ANNUAL"]:
        try:
            series_list = await test_search_series(freq)
            results[freq] = series_list
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error explorando frecuencia {freq}: {type(e).__name__}")
            
    total_series = sum(len(v) for v in results.values())
    print(f"\nResumen total de series descubiertas en BCCh BDE: {total_series}")

if __name__ == "__main__":
    asyncio.run(main())

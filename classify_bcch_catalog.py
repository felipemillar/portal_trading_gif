import os
import asyncio
import json
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("BCCH_USER")
PASS = os.getenv("BCCH_PASS") or os.getenv("BCCH_KEY")
BASE_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

CATEGORIES = {
    "TIPO_DE_CAMBIO_Y_DIVISAS": [
        "Dólar", "Euro", "Yen", "Libra", "Real", "Peso", "TCM", "Tipo de cambio", "TCO", "Dólar observado"
    ],
    "TASAS_DE_INTERES_Y_POLITICA_MONETARIA": [
        "TPM", "Tasa de política", "Tasa interbancaria", "TAB", "TIP", "Captación", "Colocación", "Tasa de interés", "Bono", "BCU", "BCP"
    ],
    "INFLACION_PRECIOS_Y_UNIDADES_REAJUSTABLES": [
        "IPC", "UF", "Unidad de fomento", "UTM", "IPRI", "Índice de precios", "Inflación", "IVP"
    ],
    "ACTIVIDAD_ECONOMICA_Y_CRECIMIENTO": [
        "Imacec", "PIB", "Producto interno bruto", "Demanda interna", "Comercio", "Minería", "Industria", "Construcción", "Inversión"
    ],
    "SECTOR_EXTERNO_Y_BALANZA_DE_PAGOS": [
        "Balanza comercial", "Cuenta corriente", "Exportaciones", "Importaciones", "Cobre", "Reservas", "PII", "Deuda externa"
    ],
    "MERCADO_LABORAL_Y_EMPLEO": [
        "Desempleo", "Ocupación", "Fuerza de trabajo", "Salarios", "Remuneraciones", "Costo de la mano de obra", "ICMO", "IR"
    ],
    "MONEDA_CREDITO_Y_SISTEMA_FINANCIERO": [
        "M1", "M2", "M3", "Base monetaria", "Depósitos", "Colocaciones", "Crédito", "Ahorro", "Bancario"
    ]
}

async def fetch_all():
    all_data = {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        for freq in ["DAILY", "MONTHLY", "QUARTERLY", "ANNUAL"]:
            resp = await client.get(BASE_URL, params={
                "user": USER,
                "pass": PASS,
                "function": "SearchSeries",
                "frequency": freq
            })
            try:
                data = resp.json()
            except Exception:
                text = resp.content.decode("latin-1")
                data = json.loads(text)
            all_data[freq] = data.get("SeriesInfos", [])
            print(f"Descargadas {len(all_data[freq])} series para frecuencia {freq}")
            await asyncio.sleep(0.5)
            
    # Classify key series
    categorized = {k: [] for k in CATEGORIES}
    uncategorized_count = 0
    
    for freq, series_list in all_data.items():
        for s in series_list:
            title = s.get("spanishTitle") or ""
            matched = False
            for cat, keywords in CATEGORIES.items():
                if any(re.search(rf"\b{re.escape(kw)}\b", title, re.IGNORECASE) for kw in keywords):
                    categorized[cat].append({
                        "seriesId": s.get("seriesId"),
                        "title": title,
                        "frequency": freq,
                        "first": s.get("firstObservation"),
                        "last": s.get("lastObservation")
                    })
                    matched = True
            if not matched:
                uncategorized_count += 1

    summary = {
        "fecha_extraccion": "2026-08-15",
        "total_series": sum(len(v) for v in all_data.values()),
        "por_frecuencia": {k: len(v) for k, v in all_data.items()},
        "por_categoria": {k: len(v) for k, v in categorized.items()}
    }
    
    with open("bcch_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    with open("bcch_categorized_sample.json", "w", encoding="utf-8") as f:
        # Save up to 15 key series per category
        sample = {k: v[:15] for k, v in categorized.items()}
        json.dump(sample, f, indent=2, ensure_ascii=False)
        
    print("\nResumen de Extraccion:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(fetch_all())

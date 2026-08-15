import os
import asyncio
from dotenv import load_dotenv
from src.bcch_client import BCChClient

load_dotenv()

SERIES_TO_TEST = [
    ("Dolar Observado (USD/CLP)", "F073.TCO.PRE.Z.D", "2026-08-01", "2026-08-15"),
    ("Tasa Politica Monetaria (TPM)", "F022.TPM.TIN.D001.NO.Z.D", "2026-01-01", "2026-08-15"),
    ("Unidad de Fomento (UF)", "F073.UFF.PRE.Z.D", "2026-08-01", "2026-08-15"),
    ("IPC Empalme 2023", "G073.IPC.IND.2023.M", "2026-01-01", "2026-07-01"),
    ("Imacec Total", "F032.IMC.VMC.MDE.Z.M", "2026-01-01", "2026-07-01"),
    ("Bonos BCCh BCP 10Y", "F022.BCLP.TIS.AN10.NO.Z.D", "2026-08-01", "2026-08-13"),
    ("Base Monetaria", "F021.BMO.STO.N.CLP.0.D", "2026-07-01", "2026-07-31"),
    ("Exportaciones Cobre", "F068.B1.FLU.A1.0.C.N.Z.Z.Z.Z.6.0.D", "2026-07-01", "2026-07-31"),
]

async def run_tests():
    client = BCChClient()
    print("Iniciando validacion multidominio en vivo contra la API del Banco Central de Chile...")
    
    for name, series_id, start, end in SERIES_TO_TEST:
        try:
            data = await client.get_series(series_id, start, end, forward_fill=True)
            obs = data.get("Series", {}).get("Obs", [])
            last_val = obs[-1].get("value") if obs else "N/A"
            last_date = obs[-1].get("indexDateString") if obs else "N/A"
            print(f"[OK] {name} ({series_id}): {len(obs)} observaciones. Ultimo dato: {last_val} en fecha {last_date}")
        except Exception as e:
            print(f"[ERROR] {name} ({series_id}): {type(e).__name__}")
        await asyncio.sleep(0.3)

if __name__ == "__main__":
    asyncio.run(run_tests())

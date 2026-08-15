import json

with open("bcch_summary.json", "r") as f:
    pass

import os
import asyncio
import httpx
from dotenv import load_dotenv
load_dotenv()
USER = os.getenv("BCCH_USER")
PASS = os.getenv("BCCH_PASS") or os.getenv("BCCH_KEY")
BASE_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

async def find_active_imacec():
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(BASE_URL, params={
            "user": USER,
            "pass": PASS,
            "function": "SearchSeries",
            "frequency": "MONTHLY"
        })
        try:
            data = resp.json()
        except Exception:
            text = resp.content.decode("latin-1")
            data = json.loads(text)
        series = data.get("SeriesInfos", [])
        imacec_matches = [s for s in series if "imacec" in (s.get("spanishTitle") or "").lower() and "2026" in (s.get("lastObservation") or "")]
        print(f"Active Imacec series up to 2026 ({len(imacec_matches)}):")
        for s in imacec_matches:
            print(f"- ID: {s.get('seriesId')} | Titulo: {s.get('spanishTitle')} | Rango: {s.get('firstObservation')} a {s.get('lastObservation')}")

if __name__ == "__main__":
    asyncio.run(find_active_imacec())

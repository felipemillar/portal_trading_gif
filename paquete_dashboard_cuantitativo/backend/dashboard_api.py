import os
import sys
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Añadir raíz al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.volume_profile_engine import (
    get_available_symbols,
    load_1m_bars,
    resample_to_30m,
    compute_volume_profile
)

app = FastAPI(title="TradeStation Analytics - 30M & Volume Profile Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard")

@app.get("/api/instruments")
async def api_instruments():
    try:
        symbols = get_available_symbols()
        return JSONResponse(content={"status": "success", "data": symbols})
    except Exception as err:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error: {type(err).__name__} (detalles omitidos por seguridad)"}
        )

@app.get("/api/data/{symbol}/candles")
async def api_candles(
    symbol: str,
    days: int = Query(15, ge=1, le=250),
    year: int = Query(2026, ge=1998, le=2030)
):
    try:
        symbol = symbol.upper()
        bars_1m = load_1m_bars(symbol, target_year=year, max_days=days)
        if not bars_1m:
            # Si no hay datos en el año actual, intentar en el último año disponible
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para {symbol} en el año {year}")

        candles_30m = resample_to_30m(bars_1m)
        return JSONResponse(content={
            "status": "success",
            "symbol": symbol,
            "count": len(candles_30m),
            "candles": candles_30m
        })
    except HTTPException:
        raise
    except Exception as err:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error: {type(err).__name__} (detalles omitidos por seguridad)"}
        )

@app.get("/api/data/{symbol}/volume_profile")
async def api_volume_profile(
    symbol: str,
    days: int = Query(15, ge=1, le=250),
    year: int = Query(2026, ge=1998, le=2030),
    bins: int = Query(60, ge=20, le=150)
):
    try:
        symbol = symbol.upper()
        bars_1m = load_1m_bars(symbol, target_year=year, max_days=days)
        if not bars_1m:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para {symbol}")

        profile_data = compute_volume_profile(bars_1m, num_bins=bins)
        return JSONResponse(content={
            "status": "success",
            "symbol": symbol,
            "data": profile_data
        })
    except HTTPException:
        raise
    except Exception as err:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error: {type(err).__name__} (detalles omitidos por seguridad)"}
        )

# Servir frontend estático
if os.path.exists(DASHBOARD_DIR):
    app.mount("/static", StaticFiles(directory=DASHBOARD_DIR), name="static")

@app.get("/")
async def serve_index():
    index_file = os.path.join(DASHBOARD_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(content={"status": "running", "message": "Dashboard frontend no inicializado."})

if __name__ == "__main__":
    port = 8050
    print(f"Iniciando Servidor de Analytics en http://localhost:{port}...")
    uvicorn.run("backend.dashboard_api:app", host="0.0.0.0", port=port, reload=False)

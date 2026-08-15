import os
import csv
import glob
from datetime import datetime, timezone
from collections import defaultdict
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

INSTRUMENTS_METADATA = {
    "NFLX": {"name": "Netflix, Inc.", "category": "Renta Variable (Streaming)", "type": "Stock"},
    "ADBE": {"name": "Adobe Inc.", "category": "Renta Variable (Software SaaS)", "type": "Stock"},
    "CRM": {"name": "Salesforce, Inc.", "category": "Renta Variable (CRM Cloud)", "type": "Stock"},
    "INTC": {"name": "Intel Corporation", "category": "Renta Variable (Semiconductores)", "type": "Stock"},
    "MU": {"name": "Micron Technology, Inc.", "category": "Renta Variable (Memorias DRAM/NAND)", "type": "Stock"},
    "TSLA": {"name": "Tesla, Inc.", "category": "Renta Variable (Vehículos Eléctricos)", "type": "Stock"},
    "VALE": {"name": "Vale S.A. (ADR)", "category": "Renta Variable (Minería / Hierro)", "type": "ADR"},
    "@SI": {"name": "Futuros de Plata (Contrato Continuo)", "category": "Metales Preciosos (Silver)", "type": "Future"},
    "@GC": {"name": "Futuros de Oro (Contrato Continuo)", "category": "Metales Preciosos (Gold)", "type": "Future"},
    "USO": {"name": "United States Oil Fund (WTI ETF)", "category": "Materias Primas (Petróleo WTI)", "type": "ETF"},
}

def get_available_symbols():
    symbols = []
    for sym, meta in INSTRUMENTS_METADATA.items():
        sym_path = os.path.join(DATA_DIR, sym)
        if os.path.exists(sym_path):
            years = sorted([y for y in os.listdir(sym_path) if os.path.isdir(os.path.join(sym_path, y))])
            if years:
                symbols.append({
                    "symbol": sym,
                    "name": meta["name"],
                    "category": meta["category"],
                    "type": meta["type"],
                    "years": years,
                    "latest_year": years[-1]
                })
    return symbols

def load_1m_bars(symbol: str, target_year: int = 2026, max_days: int = None):
    """
    Carga velas de 1 minuto para un activo y año específico.
    Si max_days está presente, filtra solo los últimos N días disponibles.
    """
    csv_file = os.path.join(DATA_DIR, symbol, str(target_year), f"{symbol}_{target_year}.csv")
    if not os.path.exists(csv_file):
        return []

    bars = []
    try:
        with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    epoch = int(row.get("Epoch") or 0)
                    ts = row.get("TimeStamp", "")
                    o = float(row.get("Open") or 0)
                    h = float(row.get("High") or 0)
                    l = float(row.get("Low") or 0)
                    c = float(row.get("Close") or 0)
                    vol = int(float(row.get("TotalVolume") or 0))
                    up_vol = int(float(row.get("UpVolume") or 0))
                    down_vol = int(float(row.get("DownVolume") or 0))
                    ticks = int(float(row.get("TotalTicks") or 0))

                    if o > 0 and h > 0 and l > 0 and c > 0:
                        bars.append({
                            "timestamp": ts,
                            "epoch": epoch,
                            "open": o,
                            "high": h,
                            "low": l,
                            "close": c,
                            "volume": vol,
                            "up_volume": up_vol,
                            "down_volume": down_vol,
                            "ticks": ticks,
                            "date": ts[:10] if len(ts) >= 10 else ""
                        })
                except Exception as parse_err:
                    continue
    except Exception as err:
        print(f"Error cargando datos de {symbol}: {type(err).__name__} (detalles omitidos por seguridad)")
        return []

    if max_days and bars:
        dates = sorted(list(set(b["date"] for b in bars if b["date"])))
        selected_dates = set(dates[-max_days:])
        bars = [b for b in bars if b["date"] in selected_dates]

    return bars

def resample_to_30m(bars_1m: list):
    """
    Agrupa velas de 1 minuto en velas de 30 minutos.
    Retorna lista en formato compatible con Lightweight Charts.
    """
    if not bars_1m:
        return []

    grouped = defaultdict(list)
    for b in bars_1m:
        try:
            # Epoch en segundos
            sec = b["epoch"] // 1000
            # Redondear al inicio del intervalo de 30 min (1800 seg)
            bucket_sec = (sec // 1800) * 1800
            grouped[bucket_sec].append(b)
        except Exception:
            continue

    candles_30m = []
    sorted_buckets = sorted(grouped.keys())

    for b_sec in sorted_buckets:
        sub_bars = grouped[b_sec]
        if not sub_bars:
            continue

        o = sub_bars[0]["open"]
        h = max(b["high"] for b in sub_bars)
        l = min(b["low"] for b in sub_bars)
        c = sub_bars[-1]["close"]
        vol = sum(b["volume"] for b in sub_bars)
        up_vol = sum(b["up_volume"] for b in sub_bars)
        down_vol = sum(b["down_volume"] for b in sub_bars)

        candles_30m.append({
            "time": b_sec,
            "open": round(o, 4),
            "high": round(h, 4),
            "low": round(l, 4),
            "close": round(c, 4),
            "volume": vol,
            "up_volume": up_vol,
            "down_volume": down_vol,
            "date": sub_bars[0]["date"]
        })

    return candles_30m

def compute_volume_profile(bars_1m: list, num_bins: int = 60):
    """
    Calcula el Perfil de Volumen (Volume Profile), Point of Control (POC) y Value Area (VAH/VAL al 70%)
    tanto por sesión diaria como el consolidado global.
    """
    if not bars_1m:
        return {"global_profile": {}, "sessions": []}

    # 1. Perfil Global
    all_highs = [b["high"] for b in bars_1m]
    all_lows = [b["low"] for b in bars_1m]
    min_price = min(all_lows)
    max_price = max(all_highs)

    if max_price == min_price:
        max_price += 0.01

    bin_size = (max_price - min_price) / num_bins
    bins_edges = np.linspace(min_price, max_price, num_bins + 1)
    bin_centers = (bins_edges[:-1] + bins_edges[1:]) / 2

    global_vol = np.zeros(num_bins)
    global_buy_vol = np.zeros(num_bins)
    global_sell_vol = np.zeros(num_bins)

    for b in bars_1m:
        typ_price = (b["high"] + b["low"] + b["close"]) / 3.0
        bin_idx = min(int((typ_price - min_price) / bin_size), num_bins - 1)
        if bin_idx >= 0:
            global_vol[bin_idx] += b["volume"]
            global_buy_vol[bin_idx] += b["up_volume"]
            global_sell_vol[bin_idx] += b["down_volume"]

    # Calcular POC global
    poc_idx = int(np.argmax(global_vol))
    poc_price = float(bin_centers[poc_idx])

    # Calcular Value Area 70% Global
    total_vol = float(np.sum(global_vol))
    target_va_vol = 0.70 * total_vol
    
    current_va_vol = global_vol[poc_idx]
    upper_idx = poc_idx
    lower_idx = poc_idx

    while current_va_vol < target_va_vol and (upper_idx < num_bins - 1 or lower_idx > 0):
        next_up_vol = global_vol[upper_idx + 1] if upper_idx < num_bins - 1 else 0
        next_down_vol = global_vol[lower_idx - 1] if lower_idx > 0 else 0

        if next_up_vol >= next_down_vol and upper_idx < num_bins - 1:
            upper_idx += 1
            current_va_vol += next_up_vol
        elif lower_idx > 0:
            lower_idx -= 1
            current_va_vol += next_down_vol
        elif upper_idx < num_bins - 1:
            upper_idx += 1
            current_va_vol += next_up_vol
        else:
            break

    vah_price = float(bin_centers[upper_idx])
    val_price = float(bin_centers[lower_idx])

    global_profile_data = {
        "prices": [round(float(p), 4) for p in bin_centers],
        "volumes": [int(v) for v in global_vol],
        "buy_volumes": [int(v) for v in global_buy_vol],
        "sell_volumes": [int(v) for v in global_sell_vol],
        "poc": round(poc_price, 4),
        "vah": round(vah_price, 4),
        "val": round(val_price, 4),
        "total_volume": int(total_vol),
        "min_price": round(float(min_price), 4),
        "max_price": round(float(max_price), 4)
    }

    # 2. Perfiles por Sesión Diaria
    days_dict = defaultdict(list)
    for b in bars_1m:
        if b["date"]:
            days_dict[b["date"]].append(b)

    sessions_data = []
    for d in sorted(days_dict.keys()):
        d_bars = days_dict[d]
        d_highs = [b["high"] for b in d_bars]
        d_lows = [b["low"] for b in d_bars]
        d_min_p = min(d_lows)
        d_max_p = max(d_highs)
        if d_max_p == d_min_p:
            d_max_p += 0.01

        d_num_bins = 40
        d_bin_size = (d_max_p - d_min_p) / d_num_bins
        d_edges = np.linspace(d_min_p, d_max_p, d_num_bins + 1)
        d_centers = (d_edges[:-1] + d_edges[1:]) / 2

        d_vol = np.zeros(d_num_bins)
        d_buy = np.zeros(d_num_bins)
        d_sell = np.zeros(d_num_bins)

        for b in d_bars:
            typ_price = (b["high"] + b["low"] + b["close"]) / 3.0
            idx = min(int((typ_price - d_min_p) / d_bin_size), d_num_bins - 1)
            if idx >= 0:
                d_vol[idx] += b["volume"]
                d_buy[idx] += b["up_volume"]
                d_sell[idx] += b["down_volume"]

        d_poc_idx = int(np.argmax(d_vol))
        d_poc_price = float(d_centers[d_poc_idx])

        d_total_vol = float(np.sum(d_vol))
        d_target_va = 0.70 * d_total_vol
        d_cur_va = d_vol[d_poc_idx]
        d_up = d_poc_idx
        d_low = d_poc_idx

        while d_cur_va < d_target_va and (d_up < d_num_bins - 1 or d_low > 0):
            nxt_up = d_vol[d_up + 1] if d_up < d_num_bins - 1 else 0
            nxt_down = d_vol[d_low - 1] if d_low > 0 else 0
            if nxt_up >= nxt_down and d_up < d_num_bins - 1:
                d_up += 1
                d_cur_va += nxt_up
            elif d_low > 0:
                d_low -= 1
                d_cur_va += nxt_down
            elif d_up < d_num_bins - 1:
                d_up += 1
                d_cur_va += nxt_up
            else:
                break

        d_vah = float(d_centers[d_up])
        d_val = float(d_centers[d_low])

        sessions_data.append({
            "date": d,
            "open": round(d_bars[0]["open"], 4),
            "high": round(d_max_p, 4),
            "low": round(d_min_p, 4),
            "close": round(d_bars[-1]["close"], 4),
            "poc": round(d_poc_price, 4),
            "vah": round(d_vah, 4),
            "val": round(d_val, 4),
            "total_volume": int(d_total_vol),
            "prices": [round(float(p), 4) for p in d_centers],
            "volumes": [int(v) for v in d_vol],
            "buy_volumes": [int(v) for v in d_buy],
            "sell_volumes": [int(v) for v in d_sell]
        })

    return {
        "global_profile": global_profile_data,
        "sessions": sessions_data
    }

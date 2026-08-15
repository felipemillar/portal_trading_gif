# Módulo de Análisis Cuantitativo (Velas 30M & Perfil de Volumen)

Este paquete contiene la arquitectura completa del motor cuantitativo y el dashboard visual construido para analizar barras de 30 minutos y calcular perfiles de volumen (Point of Control, Value Area High/Low).

Está listo para ser migrado e integrado en el proyecto `portal_trading_gif`.

## Estructura del Paquete

```text
export_dashboard/
├── backend/
│   ├── volume_profile_engine.py  # Motor cuantitativo Pandas (Agrupación 30M, cálculo VAH/VAL/POC)
│   └── dashboard_api.py          # Servidor FastAPI y endpoints RESTful
├── dashboard/
│   ├── index.html                # Interfaz UI Split-Screen (70% velas, 30% histograma)
│   ├── styles.css                # Estilos institucionales Dark Mode
│   └── app.js                    # Lógica de renderizado (Lightweight Charts + Plotly)
└── run_dashboard.sh              # Script de ejecución standalone
```

## Dependencias de Python Necesarias en `portal_trading_gif`

Asegúrate de que el entorno virtual de destino tenga instaladas las siguientes librerías (puedes agregarlas a `requirements.txt`):
```bash
pip install fastapi uvicorn pandas numpy httpx
```

*(El frontend no requiere NPM, consume Lightweight Charts y Plotly vía CDN directamente).*

## Guía de Integración

1. **Mover Archivos**:
   Copia el contenido de `backend/` dentro de la carpeta `src/` o `backend/` de `portal_trading_gif`.
   Copia la carpeta `dashboard/` completa a la raíz o a la carpeta de assets/estáticos del nuevo proyecto.

2. **Ajustar la Ruta de Datos (`DATA_DIR`)**:
   El motor cuantitativo (`volume_profile_engine.py` y `dashboard_api.py`) asume la existencia de una carpeta local con archivos CSV descargados desde TradeStation.
   - **Archivo `volume_profile_engine.py`**: Cambia el `DATA_DIR = Path("data")` a la ruta absoluta o relativa donde almacenarás o descargarás los históricos en el nuevo proyecto.

3. **Montar Rutas Estáticas**:
   Si integras esto en el FastAPI principal de `portal_trading_gif`, asegúrate de montar la carpeta estática del dashboard:
   ```python
   from fastapi.staticfiles import StaticFiles
   
   app.mount("/dashboard", StaticFiles(directory="rutas_a/dashboard", html=True), name="dashboard")
   ```
   Y registra los tres endpoints (`/api/instruments`, `/api/data/{symbol}/candles`, `/api/data/{symbol}/volume_profile`) en tu enrutador principal.

## Arquitectura de Componentes

- **Lightweight Charts (TradingView)**: Renderiza las velas de 30 minutos y el sub-panel inferior con el volumen coloreado por sesgo (alcista/bajista). Se sincronizan líneas de precio horizontales (POC dorado, VAH verde, VAL azul) desde la API.
- **Plotly.js**: Renderiza el Perfil de Volumen en barras horizontales agrupadas o apiladas, permitiendo alternar entre el Perfil Global del rango completo o la disección por sesiones diarias.
- **Motor Cuantitativo**: Toma velas de 1 minuto y hace `resample('30T')`. El perfil de volumen utiliza bins de precio con interpolación linear de volumen, extrayendo el percentil 70% para el Área de Valor estadístico.

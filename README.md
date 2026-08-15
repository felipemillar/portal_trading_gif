# Portal Trading GIF - Macroeconomic Data Extractor

Extractor asíncrono, tolerante a fallos y limpio para indicadores macroeconómicos y análisis de sentimiento, desarrollado en Python. Diseñado como capa de ingesta de datos para modelos de trading algorítmico y cuantitativo.

---

## Fuentes de Datos Integradas

### 1. Banco Central de Chile (BCCh BDE)
- **Módulo**: [`src/bcch_client.py`](file:///Users/fmillar/portal_trading_gif/src/bcch_client.py)
- **Funcionalidad**: Extracción de Dólar Observado (USD/CLP), TPM, IPC, Imacec e indicadores oficiales de Chile.
- **Resiliencia & ETL**: Soporte para token y credenciales clásicas, conversión a formato ISO 8601 y **Forward-Fill** para interpolar fines de semana y feriados.

### 2. Alpha Vantage (News & Sentiment)
- **Módulo**: [`src/alphavantage_client.py`](file:///Users/fmillar/portal_trading_gif/src/alphavantage_client.py)
- **Funcionalidad**: Consultas de noticias de mercados financieros y cálculo de puntuaciones/etiquetas de sentimiento por ticker y tópico.
- **Resiliencia**: Detección inteligente de avisos de cuota gratuita (`"Note"`) y reintentos adaptativos con `tenacity`.

### 3. FRED (Federal Reserve Economic Data)
- **Módulo**: [`src/fred_client.py`](file:///Users/fmillar/portal_trading_gif/src/fred_client.py)
- **Funcionalidad**: Extracción de series históricas de la Reserva Federal (ej. desempleo `UNRATE`, PIB, tasas).
- **Resiliencia**: Semáforo asíncrono para limitar la ráfaga a 2 RPS y manejo de valores ausentes (coerción de `"."` a `None`).

---

## Requisitos e Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/felipemillar/portal_trading_gif.git
   cd portal_trading_gif
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   Copia el archivo de ejemplo y completa tus credenciales:
   ```bash
   cp .env.example .env
   ```

---

## Pruebas y Validación

### Ejecutar Suite de Pruebas Unitarias
```bash
python -m unittest discover tests/
```

### Ejecutar Consultas Interactivas en Vivo
```bash
# Banco Central de Chile (Dólar Observado)
python test_bcch_query.py

# Alpha Vantage (Noticias y Sentimiento)
python test_alphavantage_query.py

# FRED (Tasa de Desempleo)
python test_fred_query.py
```

---

## Colaboración Multimodelo (Antigravity + Claude)
Este repositorio sigue las pautas de colaboración definidas en [`.agents/AGENTS.md`](file:///Users/fmillar/portal_trading_gif/.agents/AGENTS.md) y el registro cronológico en [`BITACORA.md`](file:///Users/fmillar/portal_trading_gif/BITACORA.md).

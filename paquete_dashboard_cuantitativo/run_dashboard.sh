#!/usr/bin/env bash
# ==============================================================================
# Script de inicio para TradeStation Analytics Dashboard (30M + Perfil de Volumen)
# ==============================================================================

PORT=8050
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================================="
echo " INICIANDO TRADESTATION ANALYTICS DASHBOARD"
echo " URL: http://localhost:$PORT"
echo "=================================================================="

# Usar el entorno virtual del proyecto
if [ -f "./.venv/bin/python3" ]; then
    PYTHON_EXEC="./.venv/bin/python3"
else
    PYTHON_EXEC="python3"
fi

$PYTHON_EXEC backend/dashboard_api.py

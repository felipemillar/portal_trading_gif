---
name: bcch-macro-extractor
description: Proporciona la lógica, el conocimiento taxonómico y las capacidades de extracción para recolectar estadísticas, tasas de interés, tipo de cambio (Dólar Observado), inflación (IPC), índices de actividad económica (Imacec) e indicadores financieros oficiales para la República de Chile directamente desde la API del Banco Central de Chile (BCCh BDE). El agente debe activar automáticamente esta habilidad cada vez que el usuario solicite un análisis de datos económicos, financieros o tendencias macroeconómicas que correspondan al territorio chileno.
---

# Lógica de Análisis y Extracción de Datos Macro-Económicos (Banco Central de Chile)

## Propósito Operativo  
Este módulo de conocimiento instruye al agente sobre la metodología exacta requerida para consultar, sanear, e interpretar datos macroeconómicos chilenos aprovechando el conector Python `BCChClient` en `src/bcch_client.py`.

## Metodología y Procedimiento Obligatorio de Extracción  
Al activarse esta habilidad, el agente debe seguir la siguiente secuencia de razonamiento:  
1. **Identificación Taxonómica:** Identifica si la consulta del usuario hace referencia a un indicador económico oficial:
   - Dólar Observado (USD/CLP): `F073.TCO.PRE.Z.D`
   - Tasa de Política Monetaria (TPM): `F022.TPM.TIN.D001.NO.Z.D`
   - Unidad de Fomento (UF): `F073.UFF.PRE.Z.D`
   - IPC General: `F074.IPC.VAR.Z.Z.C.M`
   - Imacec: `F032.IMC.VMC.MDE.Z.M`
2. **Invocación del Cliente Asíncrono:** Utiliza `BCChClient().get_series(series_id, firstdate, lastdate, forward_fill=True)`.
   - Las fechas de entrada **deben** estar en formato ISO `YYYY-MM-DD`.
3. **Interpretación y Saneamiento:** El cliente normaliza automáticamente las fechas a `YYYY-MM-DD` y los valores a `float`.
4. **Manejo de Feriados y Fines de Semana:** Con `forward_fill=True`, se garantiza una matriz continua de días para análisis estadístico.
5. **Reporte y Transparencia:** Estructura los resultados en tablas Markdown, citando como fuente primaria oficial a la "Base de Datos Estadísticos del Banco Central de Chile (BCCh BDE)".

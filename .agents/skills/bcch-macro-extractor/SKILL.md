---
name: bcch-macro-extractor
description: Proporciona la lógica, el conocimiento taxonómico y las capacidades de extracción para recolectar estadísticas, tasas de interés, tipo de cambio (Dólar Observado), inflación (IPC), índices de actividad económica (Imacec) e indicadores financieros oficiales para la República de Chile directamente desde la API del Banco Central de Chile (BCCh BDE). El agente debe activar automáticamente esta habilidad cada vez que el usuario solicite un análisis de datos económicos, financieros o tendencias macroeconómicas que correspondan al territorio chileno.
---

# Logica de Analisis y Extraccion de Datos Macro-Economicos (Banco Central de Chile)

## Proposito Operativo  
Este modulo de conocimiento instruye al agente sobre la taxonomia, metodologia y extraccion de datos macroeconomicos oficiales de Chile mediante `BCChClient` (`src/bcch_client.py`). Para el catalogo exhaustivo de las 25.350 series del BCCh, consultar [CATALOGO_UNIVERSO_DATOS_BCCH_2026.md](file:///Users/fmillar/portal_trading_gif/CATALOGO_UNIVERSO_DATOS_BCCH_2026.md).

## Metodologia y Procedimiento Obligatorio de Extraccion  
Al activarse esta habilidad, el agente debe seguir la siguiente secuencia de razonamiento:  
1. **Identificacion Taxonomica:** Identifica el indicador economico oficial solicitado:
   - Dolar Observado (USD/CLP): `F073.TCO.PRE.Z.D` (Diaria)
   - Tasa de Politica Monetaria (TPM): `F022.TPM.TIN.D001.NO.Z.D` (Diaria)
   - Unidad de Fomento (UF): `F073.UFF.PRE.Z.D` (Diaria)
   - IPC General Empalmado (Base 2023): `G073.IPC.IND.2023.M` (Mensual)
   - Imacec Empalmado (Base 2018): `F032.IMC.IND.Z.Z.EP18.Z.Z.0.M` (Mensual)
   - Imacec Desestacionalizado: `F032.IMC.IND.Z.Z.EP18.Z.Z.1.M` (Mensual)
   - Bonos BCCh en Pesos 10 anos (BCP 10Y): `F022.BCLP.TIS.AN10.NO.Z.D` (Diaria)
   - Bonos BCCh en UF 5 anos (BCU 5Y): `F022.BCU.STO.Z.Z.UF.D` (Diaria)
   - Base Monetaria (Saldos diarios): `F021.BMO.STO.N.CLP.0.D` (Diaria)
   - Exportaciones Mineras de Cobre: `F068.B1.FLU.A1.0.C.N.Z.Z.Z.Z.6.0.D` (Semanal/Diaria)
   - Ventas Diarias Comercio Minorista (IVDCM): `F034.VDCM.IND.DBC.2018.0.D` (Diaria)
2. **Invocacion del Cliente Asincrono:** Utiliza `BCChClient().get_series(series_id, firstdate, lastdate, forward_fill=True)`.
   - Las fechas de entrada **deben** estar en formato ISO `YYYY-MM-DD`.
3. **Interpretacion y Saneamiento:** El cliente normaliza automaticamente las fechas a `YYYY-MM-DD` y los valores a `float`.
4. **Manejo de Feriados y Fines de Semana:** Con `forward_fill=True`, se garantiza una matriz continua de dias para analisis estadistico y trading algoritmico sin Look-Ahead Bias.
5. **Reporte y Transparencia:** Estructura los resultados en tablas Markdown, citando como fuente primaria oficial a la "Base de Datos Estadisticos del Banco Central de Chile (BCCh BDE)".

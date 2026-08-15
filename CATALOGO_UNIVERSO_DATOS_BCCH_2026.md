# Catalogo del Universo de Datos de la API del Banco Central de Chile (BCCh BDE)

Fecha de Extraccion y Auditoria: 2026-08-15
Fuente Oficial: Banco Central de Chile - Base de Datos Estadisticos (BDE) / SieteRestWS
Estado de Exploracion: Completada al 100%

---

## 1. Resumen Ejecutivo del Universo de Datos

A traves del servicio web oficial `SieteRestWS`, el Banco Central de Chile expone un repositorio estadistico integral que abarca la totalidad de las variables macroeconomicas, monetarias, cambiarias, financieras y de cuentas nacionales del pais.

La exploracion sistematica realizada sobre las 4 frecuencias de publicacion arroja un total de **25.350 series de tiempo** disponibles para consumo directo automatizado.

### Distribucion por Frecuencia de Actualizacion

| Frecuencia | Total de Series | Descripcion y Casos de Uso Cuantitativo |
| :--- | :--- | :--- |
| DAILY (Diaria) | 1.871 | Dolar observado, UF, TPM, paridades de divisas, tasas interbancarias, curvas soberanas BCP/BCU, ventas minoristas diarias (IVDCM), reservas y flujos de comercio exterior semanales. |
| MONTHLY (Mensual) | 9.079 | Inflacion (IPC empalme 2023 e historico), Imacec general y sectorial (base 2018), agregados monetarios (M1, M2, M3), balanza comercial, expectativas macroeconomicas (EEE, EOF), empleo y salarios. |
| QUARTERLY (Trimestral) | 8.749 | Cuentas nacionales, Producto Interno Bruto (PIB) desglosado por rama de actividad y por componentes del gasto, Formacion Bruta de Capital Fijo (FBCF), Balanza de Pagos y Deuda Externa. |
| ANNUAL (Anual) | 5.651 | Series historicas estructurales, matrices de insumo-producto, balances del sector publico consolidado y series de largo plazo. |
| **TOTAL** | **25.350** | **Universo total de series consultables en la API del BCCh** |

---

## 2. Taxonomia por Dominios Macroeconomicos y Financieros

Se han clasificado las series clave en 7 dominios analiticos criticos para trading algoritmico, modelos econometricos y analisis cuantitativo:

```
Universo BCCh (25.350 series)
├── 1. Tipo de Cambio y Divisas (857 series)
├── 2. Tasas de Interes y Politica Monetaria (319 series)
├── 3. Inflacion, Precios y Unidades Reajustables (1.322 series)
├── 4. Actividad Economica y Cuentas Nacionales (6.773 series)
├── 5. Sector Externo y Balanza de Pagos (2.488 series)
├── 6. Sistema Financiero, Credito y Agregados Monetarios (2.060 series)
└── 7. Mercado Laboral y Expectativas Macroeconomicas (391 series)
```

---

## 3. Detalle de Series Criticas por Dominio (Verificadas en Vivo)

A continuacion se detallan las series prioritarias identificadas, sus codigos de serie unicos (`seriesId`), titulos oficiales, rango de cobertura y valor obtenido en la prueba en vivo del 15 de agosto de 2026.

### Dominio 1: Tipo de Cambio y Divisas
Total de series en categoria: 857

| Nombre Analitico | Codigo de Serie (`seriesId`) | Frecuencia | Rango Disponible | Ultimo Valor Registrado (2026-08-15) |
| :--- | :--- | :--- | :--- | :--- |
| Dolar Observado (USD/CLP) | `F073.TCO.PRE.Z.D` | Diaria | 1990 a 2026 | 913.20 CLP/USD |
| Indice Tipo de Cambio Multilateral (TCM-X) | `G073.TCMX.IND.199801.D` | Diaria | 2002 a 2026 | Indice Base 1998=100 |
| Tipo de Cambio Promedio Licitacion FX Spot | `F022.VDOB4.PPO.Z.Z.USD.D` | Diaria | 2019 a 2022 | Historico Intervencion |
| Ventas Forward BCCh a 28 dias | `F022.VFWP4.PRE.D028.Z.USD.D` | Diaria | 2019 a 2026 | Promedio Adjudicado |
| Tasas On-Shore Base Prime USD a 1 ano | `F022.TOS.TIN.AN01.US.Z.D` | Diaria | 1990 a 2026 | Tasa Porcentual |

### Dominio 2: Tasas de Interes y Politica Monetaria
Total de series en categoria: 319

| Nombre Analitico | Codigo de Serie (`seriesId`) | Frecuencia | Rango Disponible | Ultimo Valor Registrado (2026-08-15) |
| :--- | :--- | :--- | :--- | :--- |
| Tasa de Politica Monetaria (TPM) | `F022.TPM.TIN.D001.NO.Z.D` | Diaria | 1995 a 2026 | 4.50 % |
| Bono Banco Central en Pesos (BCP 2 anos) | `F022.BCLP.TIS.AN02.NO.Z.D` | Diaria | 2002 a 2026 | Tasa Mercado Secundario |
| Bono Banco Central en Pesos (BCP 5 anos) | `F022.BCLP.TIS.AN05.NO.Z.D` | Diaria | 2002 a 2026 | Tasa Mercado Secundario |
| Bono Banco Central en Pesos (BCP 10 anos) | `F022.BCLP.TIS.AN10.NO.Z.D` | Diaria | 2004 a 2026 | 5.66 % |
| Stock Total en Circulacion de BCP | `F022.BCP.STO.Z.Z.CLP.D` | Diaria | 2002 a 2026 | MM CLP |
| Tasa Interbancaria Promedio (TIP) Captaciones 30-89d | `F022.CAP.TIP.D089.US.Z.D` | Diaria | 2007 a 2026 | Tasa Porcentual USD |

### Dominio 3: Inflacion, Precios y Unidades Reajustables
Total de series en categoria: 1.322

| Nombre Analitico | Codigo de Serie (`seriesId`) | Frecuencia | Rango Disponible | Ultimo Valor Registrado (2026-08-15) |
| :--- | :--- | :--- | :--- | :--- |
| Unidad de Fomento (UF) | `F073.UFF.PRE.Z.D` | Diaria | 1990 a 2026 | 40.852,69 CLP |
| IPC General Empalme (Base 2023 = 100) | `G073.IPC.IND.2023.M` | Mensual | 1998 a 2026 | 112.44766 (Jul 2026) |
| IPC General Historico (Base 2018 = 100) | `G073.IPC.IND.2018.M` | Mensual | 1989 a 2023 | 129.80 (Dic 2023) |
| IPC Variacion 12 Meses Historico | `G073.IPC.V12.2018.M` | Mensual | 1990 a 2023 | Porcentaje anual |
| Bono Banco Central en UF (BCU 5 anos) | `F022.BCU.STO.Z.Z.UF.D` | Diaria | 2002 a 2026 | Miles de UF |
| Bono Banco Central en UF (BCU 10 anos) | `F022.BCU1.FLU.AN10.Z.UF.D` | Diaria | 2002 a 2026 | Licitaciones UF |

### Dominio 4: Actividad Economica y Cuentas Nacionales
Total de series en categoria: 6.773

| Nombre Analitico | Codigo de Serie (`seriesId`) | Frecuencia | Rango Disponible | Ultimo Valor Registrado (2026-08-15) |
| :--- | :--- | :--- | :--- | :--- |
| Imacec Empalmado Serie Original (Base 2018=100) | `F032.IMC.IND.Z.Z.EP18.Z.Z.0.M` | Mensual | 1996 a 2026 | 111.03 (Jun 2026) |
| Imacec Empalmado Desestacionalizado (Base 2018) | `F032.IMC.IND.Z.Z.EP18.Z.Z.1.M` | Mensual | 1996 a 2026 | 114.28 (Jun 2026) |
| Imacec Minero Empalmado | `F032.IMC.IND.Z.Z.EP18.03.Z.0.M` | Mensual | 1996 a 2026 | Indice Minero |
| Imacec No Minero Empalmado | `F032.IMC.IND.Z.Z.EP18.N03.Z.0.M` | Mensual | 1996 a 2026 | Indice No Minero |
| Imacec Comercio Serie Original | `F032.IMC.IND.Z.Z.EP18.COM.Z.0.M` | Mensual | 1996 a 2026 | Indice Comercio |
| Imacec Servicios Serie Original | `F032.IMC.IND.Z.Z.EP18.SERV.Z.0.M` | Mensual | 1996 a 2026 | Indice Servicios |
| Imacec Contribucion Anual Referencia 2018 | `F032.IMC.V12.Z.Z.2018.Z.Z.0.M` | Mensual | 2014 a 2026 | Variacion A/A |
| Indice Ventas Diarias Comercio Minorista (IVDCM) | `F034.VDCM.IND.DBC.2018.0.D` | Diaria | 2018 a 2026 | Indice Diario |
| IVDCM Promedio Movil 28 Dias | `F034.VDCM.IPM28D.DBC.2018.0.D` | Diaria | 2018 a 2026 | Media Movil Diaria |

### Dominio 5: Sector Externo y Balanza de Pagos
Total de series en categoria: 2.488

| Nombre Analitico | Codigo de Serie (`seriesId`) | Frecuencia | Rango Disponible | Ultimo Valor Registrado (2026-08-15) |
| :--- | :--- | :--- | :--- | :--- |
| Activos de Reserva Internacional (PII) | `F062.A5.STO.PF.USD.D` | Diaria (Semanal) | 1995 a 2026 | Millones de USD |
| Exportaciones Mineras de Cobre | `F068.B1.FLU.A1.0.C.N.Z.Z.Z.Z.6.0.D` | Diaria (Semanal) | 2003 a 2026 | 1.284,93 MM USD (Jul 2026) |
| Exportaciones Mineras de Catodos de Cobre | `F068.B1.FLU.A2.0.C.N.Z.Z.Z.Z.6.0.D` | Diaria (Semanal) | 2003 a 2026 | MM USD |
| Exportaciones Mineras de Concentrado de Cobre | `F068.B1.FLU.A3.0.C.N.Z.Z.Z.Z.6.0.D` | Diaria (Semanal) | 2003 a 2026 | MM USD |
| Exportaciones de Carbonato de Litio | `F068.B1.FLU.A8.0.C.N.Z.Z.Z.Z.6.0.D` | Diaria (Semanal) | 2003 a 2026 | MM USD |
| Importaciones Maquinaria Mineria y Construccion | `F068.B1.FLU.C753.0.M.N.K.Z.Z.Z.6.0.D` | Diaria (Semanal) | 2003 a 2026 | CIF MM USD |
| Cuenta Corriente Balanza de Pagos | `F061.1.FLU.S.USD.Z.T` | Trimestral | 1996 a 2026 | MM USD |
| Balanza Comercial Trimestral | `F061.1AA.FLU.S.USD.Z.T` | Trimestral | 1996 a 2026 | MM USD |

### Dominio 6: Sistema Financiero, Credito y Agregados Monetarios
Total de series en categoria: 2.060

| Nombre Analitico | Codigo de Serie (`seriesId`) | Frecuencia | Rango Disponible | Ultimo Valor Registrado (2026-08-15) |
| :--- | :--- | :--- | :--- | :--- |
| Base Monetaria (Saldos Diarios) | `F021.BMO.STO.N.CLP.0.D` | Diaria | 2011 a 2026 | 18.094,12 MM CLP |
| Circulante Serie Real | `F021.CIR.STO.R.P96.0.D` | Diaria | 2011 a 2026 | Indice Real |
| Depositos en Cuenta Corriente (D1A) | `F021.D1A.STO.N.CLP.0.D` | Diaria | 2011 a 2026 | MM CLP |
| Depositos y Ahorro Vista (DAV) | `F021.DAV.STO.N.CLP.0.D` | Diaria | 2019 a 2026 | MM CLP |
| Depositos y Captaciones a Plazo (M2) | `F021.DP.STO.N.CLP.5.D` | Diaria | 2011 a 2026 | MM CLP |
| Depositos de Ahorro a Plazo | `F021.AHP.STO.N.CLP.0.D` | Diaria | 2011 a 2026 | MM CLP |
| Depositos en Moneda Extranjera | `F021.DME.STO.N.CLP.0.D` | Diaria | 2011 a 2026 | MM CLP |
| Documentos BCCh en Circulacion (M3) | `F021.DBC.STO.N.CLP.5.D` | Diaria | 2011 a 2026 | MM CLP |
| Bonos de Tesoreria en Circulacion (M3) | `F021.BOT.STO.N.CLP.5.D` | Diaria | 2011 a 2026 | MM CLP |
| Colocaciones Efectivas Sector Bancario CLP | `F022.COLCOMEX.PRO.Z.Z.CLP.D` | Diaria | 2018 a 2026 | MM CLP |

### Dominio 7: Mercado Laboral y Expectativas Macroeconomicas
Total de series en categoria: 391

| Nombre Analitico | Codigo de Serie (`seriesId`) | Frecuencia | Rango Disponible | Ultimo Valor Registrado (2026-08-15) |
| :--- | :--- | :--- | :--- | :--- |
| Expectativas Imacec (Mediana Encuesta EEE) | `F089.IMC.V12.10.M` | Mensual | 2000 a 2026 | Porcentaje Variacion |
| Expectativas Imacec No Minero | `F089.IMCNM.V12.10.M` | Mensual | 2018 a 2026 | Porcentaje Variacion |
| Incidencia del Cobre en Tipo de Cambio (EOF) | `F089.EOF.FI_TC_CU.MS.D` | Diaria | 2021 a 2026 | Indice de Sensibilidad |
| Fuerza de Trabajo y Desempleo por Tramos (INE) | `F049.BPV.PMT.INE9.H25.M` | Mensual | 2010 a 2026 | Miles de personas |

---

## 4. Aspectos Tecnicos y Protocolo de Ingesta

1. **Protocolo de Autenticacion**:
   - Endpoint: `https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx`
   - Metodo: `GET` con parametros `user`, `pass` (o key), `function` (`SearchSeries` / `GetSeries`), `timeseries`, `firstdate` (`YYYY-MM-DD`), `lastdate` (`YYYY-MM-DD`).
2. **Formato y Normalizacion Temporal**:
   - La API retorna fechas en formato chileno `DD-MM-YYYY`.
   - El extractor normaliza obligatoriamente al estandar ISO 8601 (`YYYY-MM-DD`).
3. **Manejo de Feriados y Valores Nulos**:
   - Fines de semana y feriados bursatiles se procesan mediante algoritmo de Forward-Fill (`value_forward_filled: True`) para asegurar series continuas aptas para entrenamiento cuantitativo sin sesgo de anticipacion (Look-Ahead Bias).
4. **Encoding de Respuestas**:
   - La API del BCCh entrega respuestas con codificacion de caracteres en `latin-1` (ISO-8859-1) para ciertas series con tildes, por lo que el cliente implementa decodificacion con fallback automatico a `latin-1`.

---

## 5. Estrategia de Modularizacion en Repositorio Independiente

Para permitir que este conector sea consumible desde cualquier entorno (proyectos de backtesting, dashboards, agentes de trading o tuberias de datos), se empaquetara en un repositorio independiente (`bcch-connector` o `bcch-client`):

- **Instalacion Standalone**: `pip install git+https://github.com/felipemillar/bcch-connector.git`
- **Integracion con Agentes**: Incluye la habilidad estandarizada `.agents/skills/bcch-macro-extractor/SKILL.md` con taxonomias de consulta.
- **Protocolo de Seguridad**: Regla estricta de enmascaramiento de errores `type(err).__name__` y prohibicion absoluta de emoticones o emojis en todos los archivos.

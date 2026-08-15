# Bitácora de Desarrollo - Portal de Trading (Macro Extractor)

Este archivo registra el progreso, hitos clave, decisiones técnicas y la evolución de los conectores de datos macroeconómicos del portal de trading.

---

## [2026-08-14] - Sesión de Trabajo: Integración de FRED y Configuración Multimodelo (Antigravity + Claude)

**Objetivo:** Desarrollar el conector para la API de FRED (Federal Reserve Economic Data), asegurar su resiliencia ante límites de tasa micro-ráfaga, y establecer las bases de documentación para la programación en conjunto con Claude.

### Cambios Realizados:
- ** FRED Client ([src/fred_client.py](file:///Users/fmillar/portal_trading_gif/src/fred_client.py))**: Creación de la clase `FredClient` con soporte para formato JSON nativo, semáforo asíncrono (`asyncio.Semaphore(2)`) para mitigar bloqueos de micro-ráfaga, e integración de reintentos mediante `tenacity` para respuestas HTTP 429.
- ** ETL de Limpieza de FRED**: Normalización que coerciona el carácter de datos no publicados `"."` de FRED a `None`, y castea los valores válidos a tipo float.
- ** Script de Prueba FRED ([test_fred_query.py](file:///Users/fmillar/portal_trading_gif/test_fred_query.py))**: Script interactivo para validar la serie `UNRATE` (Tasa de Desempleo de EE. UU.) e imprimir los meses recientes en consola.
- ** Pruebas Unitarias FRED ([tests/test_fred.py](file:///Users/fmillar/portal_trading_gif/tests/test_fred.py))**: Validaciones de API key vacía y conversión correcta del valor `"."`.
- ** Variables de Entorno ([.env](file:///Users/fmillar/portal_trading_gif/.env) / [.env.example](file:///Users/fmillar/portal_trading_gif/.env.example))**: Inyección segura de la credencial real `FRED_API_KEY`.
- ** Pautas de Agentes Locales ([.agents/AGENTS.md](file:///Users/fmillar/portal_trading_gif/.agents/AGENTS.md))**: Documento de directrices arquitectónicas para Claude y Antigravity.

### Decisiones y Notas de Diseño:
- **Rate Limit de FRED**: FRED bloquea IP/token si se superan las 2 peticiones por segundo. El uso del semáforo a nivel de cliente garantiza que el tráfico esté controlado sin delegar la responsabilidad al usuario.
- **Mapeo de Nulos**: Se detectan y convierten valores vacíos o nulos especiales en FRED, garantizando la compatibilidad con modelos analíticos posteriores.

### Pendientes y Siguientes Pasos:
- Analizar correlaciones cruzadas o análisis conjunto entre los tres conectores (BCCh, Alpha Vantage y FRED).

---

## [2026-08-14] - Sesión de Trabajo: Integración de Alpha Vantage (News & Sentiment API)

**Objetivo:** Desarrollar un cliente asíncrono para consumir noticias financieras y clasificar su respectiva puntuación y etiqueta de sentimiento.

### Cambios Realizados:
- ** Alpha Vantage Client ([src/alphavantage_client.py](file:///Users/fmillar/portal_trading_gif/src/alphavantage_client.py))**: Creación de la clase `AlphaVantageClient` asíncrona compatible con el endpoint `NEWS_SENTIMENT`.
- ** Control de Rate Limit Gratuito**: Implementación de lógica resiliente que detecta si el JSON de respuesta contiene las claves `"Note"` o `"Information"` (típicas del rate limit del plan gratuito de Alpha Vantage en HTTP 200) y lanza reintentos automáticos a través de `tenacity`.
- ** Script de Prueba ([test_alphavantage_query.py](file:///Users/fmillar/portal_trading_gif/test_alphavantage_query.py))**: Validación en vivo consumiendo noticias macroeconómicas del tópico `financial_markets` y listándolas en terminal con sus puntuaciones de sentimiento.
- ** Pruebas Unitarias ([tests/test_alphavantage.py](file:///Users/fmillar/portal_trading_gif/tests/test_alphavantage.py))**: Cobertura para verificar la validación de credenciales y la correcta detección de la clave `"Note"`.
- ** Variables de Entorno**: Registro de la API key real `ALPHAVANTAGE_API_KEY` en `.env` y plantilla en `.env.example`.

---

## [2026-08-14] - Sesión de Trabajo: Implementación Inicial y Conector BCCh BDE

**Objetivo:** Diseñar e implementar un conector asíncrono y tolerante a fallos para interactuar con la Base de Datos Estadísticos (BDE) del Banco Central de Chile.

### Cambios Realizados:
- ** Especificación Arquitectónica ([ESPECIFICACION_TECNICA_BCCH_ANTIGRAVITY.md](file:///Users/fmillar/portal_trading_gif/ESPECIFICACION_TECNICA_BCCH_ANTIGRAVITY.md))**: Documento de arquitectura sobre endpoints del BCCh, asimetrías de datos, fechas en formato latino y Forward-Fill.
- ** Skill Personalizada ([.agents/skills/bcch-macro-extractor/SKILL.md](file:///Users/fmillar/portal_trading_gif/.agents/skills/bcch-macro-extractor/SKILL.md))**: Declaración de la habilidad semántica para Antigravity.
- ** Core Client ([src/bcch_client.py](file:///Users/fmillar/portal_trading_gif/src/bcch_client.py))**: Creación de la clase `BCChClient` con soporte para token (API Key) y credenciales clásicas.
- ** ETL & Forward-Fill**: Conversión de fechas latinas a ISO (`YYYY-MM-DD`), normalización de flotantes, conversión de `"NaN"` a `None` para interpolación de días no hábiles (fines de semana) repitiendo el último valor oficial conocido.
- ** Suites de Prueba**:
  - [tests/test_client.py](file:///Users/fmillar/portal_trading_gif/tests/test_client.py): Pruebas de Forward-Fill y normalización.
  - [test_bcch_query.py](file:///Users/fmillar/portal_trading_gif/test_bcch_query.py): Script de consulta interactiva de Dólar Observado.
- ** Entorno & Git**: Creación del entorno virtual `.venv` y archivo `.gitignore` inicial.

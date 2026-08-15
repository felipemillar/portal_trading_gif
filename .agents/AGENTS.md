# Directrices Locales y Reglas de Colaboración (Antigravity & Claude)

Bienvenido a `portal_trading_gif`. Este archivo define el alcance, arquitectura del proyecto y las reglas del agente para asegurar la consistencia y la colaboración entre **Antigravity** (IDE) y **Claude** (Análisis y Arquitectura).

---

## Alcance del Proyecto
Este repositorio contiene un extractor de indicadores y noticias macroeconómicas asíncrono, tolerante a fallos y limpio, diseñado en Python. Sirve como capa de ingesta de datos para modelos de trading algorítmico cuantitativo.

---

## Pila Tecnológica & Arquitectura
- **Python**: `>=3.10`
- **Transporte HTTP**: `httpx` asíncrono (`AsyncClient`).
- **Resiliencia**: `tenacity` con backoff exponencial.
- **Entorno**: `python-dotenv` para configuración segura mediante `.env`.
- **Estructura del Proyecto**:
  - [src/](file:///Users/fmillar/portal_trading_gif/src): Módulos cliente de las APIs.
  - [tests/](file:///Users/fmillar/portal_trading_gif/tests): Suites de pruebas unitarias.
  - Archivos `test_*_query.py`: Scripts de validación de consulta interactiva.

---

## Protocolo de Colaboración: Antigravity + Claude
Para maximizar la sinergia multimodelo, el flujo de trabajo se divide de la siguiente manera:

1. **Claude (Arquitectura y Lógica)**:
   - Diseña nuevos algoritmos, estructuras de datos cuantitativas y refactorizaciones complejas.
   - Revisa el código generado y sugiere optimizaciones de rendimiento financiero.
2. **Antigravity (Ejecución, Testing y Bitácora)**:
   - Traduce los diseños conceptuales de Claude a archivos físicos.
   - Ejecuta comandos del sistema (test runners, scripts de consulta en vivo) y depura errores en el entorno local.
   - Escribe y mantiene actualizado el archivo [BITACORA.md](file:///Users/fmillar/portal_trading_gif/BITACORA.md) al final de cada sesión.

---

## Reglas Obligatorias del Agente

### 1. Error Masking en Python
Al escribir bloques de manejo de errores (`except`):
- **SIEMPRE** utiliza `type(err).__name__` en lugar de `str(err)` en la respuesta o en el registro de errores para prevenir fugas de información.
- **NUNCA** expongas stack traces o detalles de la excepción en las respuestas presentadas al usuario.
- Patrón Estándar:
  ```python
  except Exception as err:
      logger.error(f"Error en {contexto}: {type(err).__name__} (detalles omitidos por seguridad)")
      return f"Error de operación: {type(err).__name__}"
  ```

### 2. Gestión de Credenciales y Seguridad
- **NUNCA** escribas llaves de API (tokens) directamente en el código fuente.
- Utiliza siempre `load_dotenv()` de `python-dotenv`.
- Mantén actualizadas las plantillas en [`.env.example`](file:///Users/fmillar/portal_trading_gif/.env.example).
- Asegúrate de que las credenciales reales en [`.env`](file:///Users/fmillar/portal_trading_gif/.env) se mantengan fuera del control de versiones (incluidas en [`.gitignore`](file:///Users/fmillar/portal_trading_gif/.gitignore)).

### 3. Tratamiento de Datos Temporales (ETL)
- Toda serie de tiempo debe normalizar sus fechas al estándar ISO 8601 (`YYYY-MM-DD`).
- Los valores deben ser coercidos a tipo flotante (`float`).
- Para datos ausentes (como fines de semana en tipo de cambio o el punto "." en la API de FRED), se debe forzar la conversión a `None` y aplicar un algoritmo de **Forward-Fill** (llenado hacia adelante) arrastrando el último valor oficial conocido y documentando el estado como interpolado.

### 4. Estilo de Comunicación y Formato (Prohibición de Emojis)
- **CERO EMOJIS O ICONOS**: Está estrictamente prohibido el uso de emojis, emoticones o iconos en cualquier archivo del proyecto.
- Esta regla aplica para toda documentación (incluyendo este archivo, `README.md`, `BITACORA.md`), comentarios de código fuente, mensajes de commit, salidas en consola, logs de la aplicación y cualquier otra comunicación escrita o generada dentro del repositorio.
- Esta directriz es obligatoria para **Antigravity** y **Claude** a partir de este momento.

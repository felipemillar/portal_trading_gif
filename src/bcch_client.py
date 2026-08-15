"""
Cliente asíncrono y resiliente para la Base de Datos Estadísticos (BDE) del Banco Central de Chile (BCCh).
Implementa control de concurrencia (Semaphore), reintentos con backoff exponencial y jitter (Tenacity),
normalización de fechas a ISO 8601 (YYYY-MM-DD) y coerción de tipos a flotante nativo.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import httpx
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    retry_if_result,
    before_sleep_log,
)

# Cargar variables de entorno locales si existen (.env)
load_dotenv()

import json

# Silenciar logger detallado de httpx para evitar fugas de URLs con parámetros
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Configuración del logger
logger = logging.getLogger("BCChClient")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Excepciones transitorias de red elegibles para reintento
TRANSIENT_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.RemoteProtocolError,
)


def _evaluate_retry_necessity(result: Dict[str, Any]) -> bool:
    """Evalúa si la respuesta requiere un reintento con backoff (ej. HTTP 429 o 50x)."""
    status_code = result.get("_http_status", 200)
    return status_code in {429, 500, 502, 503, 504}


class BCChClient:
    """
    Cliente asíncrono para interactuar con la API REST del Banco Central de Chile (SieteRestWS).
    """

    BASE_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

    def __init__(
        self,
        token: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_concurrent_requests: int = 4,
        timeout_seconds: float = 15.0,
    ):
        """
        Inicializa el cliente del Banco Central de Chile.

        :param token: API Key Token generado en 'Mi Cuenta' de la BDE. Si es None, se lee de BCCH_TOKEN.
        :param user: Correo registrado en BCCh BDE. Si es None, se lee de BCCH_USER.
        :param password: Password registrado en BCCh BDE. Si es None, se lee de BCCH_PASS.
        :param max_concurrent_requests: Máximo de peticiones en vuelo (por defecto 4, < límite oficial 5 RPS).
        :param timeout_seconds: Timeout para operaciones de red.
        """
        self.token = token or os.environ.get("BCCH_TOKEN")
        self.user = user or os.environ.get("BCCH_USER")
        self.password = password or os.environ.get("BCCH_PASS")
        self._concurrency_limiter = asyncio.Semaphore(max_concurrent_requests)
        self._timeout = httpx.Timeout(
            connect=5.0,
            read=timeout_seconds,
            write=5.0,
            pool=5.0,
        )
        self._limits = httpx.Limits(
            max_connections=10,
            max_keepalive_connections=5,
        )

    def _validate_credentials(self) -> None:
        """Verifica la presencia de credenciales requeridas (Token o User+Pass)."""
        if self.token:
            return
        if not self.user or not self.password:
            raise ValueError(
                "Credenciales no configuradas: Defina BCCH_TOKEN o (BCCH_USER y BCCH_PASS) en el entorno o archivo .env."
            )

    @retry(
        retry=(retry_if_exception_type(TRANSIENT_EXCEPTIONS) | retry_if_result(_evaluate_retry_necessity)),
        wait=wait_exponential_jitter(initial=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _execute_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Ejecuta una petición HTTP asíncrona segura con semáforo y resiliencia."""
        self._validate_credentials()

        request_params = dict(params)
        if self.token:
            request_params["token"] = self.token
        else:
            request_params["user"] = self.user
            request_params["pass"] = self.password

        async with self._concurrency_limiter:
            async with httpx.AsyncClient(limits=self._limits, timeout=self._timeout) as client:
                try:
                    response = await client.get(self.BASE_URL, params=request_params)
                except TRANSIENT_EXCEPTIONS:
                    raise
                except Exception as err:
                    logger.error(f"Error en petición HTTP: {type(err).__name__} (detalles omitidos por seguridad)")
                    raise RuntimeError(f"Error de transporte: {type(err).__name__}") from None

                if response.status_code != 200:
                    logger.warning(
                        f"Respuesta con código HTTP no exitoso: {response.status_code}. Evaluando reintento."
                    )
                    return {
                        "_http_status": response.status_code,
                        "error": f"HTTP_{response.status_code}",
                    }

                try:
                    raw_bytes = response.content
                    try:
                        text = raw_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        try:
                            text = raw_bytes.decode("latin-1")
                        except UnicodeDecodeError:
                            text = raw_bytes.decode("utf-8", errors="replace")

                    data = json.loads(text)
                except Exception as err:
                    logger.error(f"Error parseando JSON de respuesta: {type(err).__name__} (detalles omitidos por seguridad)")
                    raise ValueError(f"Respuesta no válida del servidor: {type(err).__name__}") from None

                return data

    async def get_series(
        self,
        series_id: str,
        firstdate: Optional[str] = None,
        lastdate: Optional[str] = None,
        forward_fill: bool = False,
    ) -> Dict[str, Any]:
        """
        Consulta observaciones históricas para una serie macroeconómica específica.

        :param series_id: Código alfanumérico oficial de la serie (ej. 'F073.TCO.PRE.Z.D' para Dólar Observado).
        :param firstdate: Fecha de inicio en formato ISO 8601 (YYYY-MM-DD).
        :param lastdate: Fecha de fin en formato ISO 8601 (YYYY-MM-DD).
        :param forward_fill: Si es True, rellena días no hábiles con el último valor conocido.
        :return: Diccionario con metadatos y lista de observaciones normalizadas.
        """
        params: Dict[str, str] = {
            "function": "GetSeries",
            "timeseries": series_id,
        }
        if firstdate:
            params["firstdate"] = firstdate
        if lastdate:
            params["lastdate"] = lastdate

        raw_data = await self._execute_request(params)

        # Validación del estado lógico del Banco Central (Codigo 0 = Éxito)
        code = raw_data.get("Codigo")
        if code != 0:
            desc = raw_data.get("Descripcion", "Error desconocido")
            raise RuntimeError(f"Error de API BCCh (Código {code}): {desc}")

        # Normalización ETL de los datos
        normalized_data = self._normalize_series_payload(raw_data)

        if forward_fill and firstdate and lastdate:
            normalized_data["Series"]["Obs"] = self._apply_forward_fill(
                normalized_data["Series"]["Obs"],
                firstdate,
                lastdate,
            )

        return normalized_data

    async def search_series(self, frequency: str = "DAILY") -> Dict[str, Any]:
        """
        Busca y descubre el catálogo de series disponibles según su frecuencia.

        :param frequency: 'DAILY', 'MONTHLY', 'QUARTERLY' o 'ANNUAL'.
        :return: Diccionario con catálogo de 'SeriesInfos'.
        """
        valid_frequencies = {"DAILY", "MONTHLY", "QUARTERLY", "ANNUAL"}
        freq_upper = frequency.upper()
        if freq_upper not in valid_frequencies:
            raise ValueError(f"Frecuencia inválida: {frequency}. Opciones permitidas: {valid_frequencies}")

        params: Dict[str, str] = {
            "function": "SearchSeries",
            "frequency": freq_upper,
        }

        raw_data = await self._execute_request(params)
        code = raw_data.get("Codigo")
        if code != 0:
            desc = raw_data.get("Descripcion", "Error desconocido")
            raise RuntimeError(f"Error de API BCCh (Código {code}): {desc}")

        return raw_data

    @staticmethod
    def _normalize_series_payload(data: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma fechas a ISO 8601 (YYYY-MM-DD) y valores a float."""
        try:
            series = data.get("Series", {})
            observations = series.get("Obs", [])
            normalized_obs: List[Dict[str, Any]] = []

            for obs in observations:
                item = dict(obs)
                raw_date = item.get("indexDateString")
                if raw_date:
                    try:
                        # Si viene en formato latino DD-MM-YYYY
                        if "-" in raw_date and len(raw_date.split("-")[0]) == 2:
                            parsed_date = datetime.strptime(raw_date, "%d-%m-%Y")
                            item["indexDateString"] = parsed_date.strftime("%Y-%m-%d")
                    except Exception:
                        pass

                raw_val = item.get("value")
                if raw_val is not None and raw_val != "":
                    try:
                        val = float(raw_val)
                        import math
                        if math.isnan(val):
                            item["value"] = None
                        else:
                            item["value"] = val
                    except (ValueError, TypeError):
                        item["value"] = None
                else:
                    item["value"] = None

                normalized_obs.append(item)

            series["Obs"] = normalized_obs
            data["Series"] = series
            return data
        except Exception as err:
            logger.error(f"Error normalizando payload: {type(err).__name__} (detalles omitidos por seguridad)")
            return data

    @staticmethod
    def _apply_forward_fill(
        observations: List[Dict[str, Any]],
        start_date_str: str,
        end_date_str: str,
    ) -> List[Dict[str, Any]]:
        """Aplica forward-fill para construir una serie diaria continua."""
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")

            obs_by_date = {obs.get("indexDateString"): obs for obs in observations if obs.get("indexDateString")}

            continuous_obs: List[Dict[str, Any]] = []
            curr_dt = start_dt
            last_known_val: Optional[float] = None
            last_status: str = "FORWARD_FILLED"

            while curr_dt <= end_dt:
                date_str = curr_dt.strftime("%Y-%m-%d")
                if date_str in obs_by_date:
                    current_obs = dict(obs_by_date[date_str])
                    if current_obs.get("value") is not None:
                        last_known_val = current_obs["value"]
                        last_status = current_obs.get("statusCode", "OK")
                    else:
                        current_obs["value"] = last_known_val
                        current_obs["interpolated"] = True
                        if last_status:
                            current_obs["statusCode"] = f"{last_status} (FF)"
                    continuous_obs.append(current_obs)
                else:
                    continuous_obs.append({
                        "indexDateString": date_str,
                        "value": last_known_val,
                        "statusCode": last_status,
                        "interpolated": True,
                    })
                curr_dt += timedelta(days=1)

            return continuous_obs
        except Exception as err:
            logger.error(f"Error aplicando Forward-Fill: {type(err).__name__} (detalles omitidos por seguridad)")
            return observations

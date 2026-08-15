"""
Cliente asíncrono y resiliente para la API de FRED (Federal Reserve Economic Data).
Implementa un semáforo estricto para no sobrepasar la ráfaga de 2 peticiones/segundo
y reintentos automáticos en caso de recibir respuestas de límite de tasa (HTTP 429).
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
import httpx
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    before_sleep_log,
)

# Cargar variables de entorno locales (.env)
load_dotenv()

# Configuración del logger
logger = logging.getLogger("FredClient")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Silenciar logs detallados de httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Excepciones transitorias de red y códigos HTTP específicos elegibles para reintento
TRANSIENT_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.RemoteProtocolError,
)


class FredRateLimitError(Exception):
    """Excepción lanzada cuando se alcanza el límite de tasa (HTTP 429)."""
    pass


class FredClient:
    """
    Cliente asíncrono para interactuar con la API de FRED.
    """

    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout_seconds: float = 20.0,
    ):
        """
        Inicializa el cliente de FRED.

        :param api_key: API Key de FRED de 32 caracteres. Si es None, se lee de FRED_API_KEY.
        :param timeout_seconds: Timeout para operaciones de red.
        """
        self.api_key = api_key or os.environ.get("FRED_API_KEY")
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
        # Semáforo para respetar el límite de micro-ráfaga de FRED (máximo 2 peticiones por segundo)
        self._semaphore = asyncio.Semaphore(2)

    def _validate_api_key(self) -> None:
        """Verifica la presencia de la API Key."""
        if not self.api_key:
            raise ValueError(
                "API Key de FRED no configurada: Defina FRED_API_KEY en el entorno o archivo .env."
            )

    @retry(
        retry=retry_if_exception_type((TRANSIENT_EXCEPTIONS, FredRateLimitError)),
        wait=wait_exponential_jitter(initial=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _execute_request(self, endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Ejecuta una petición HTTP asíncrona segura con semáforo y resiliencia."""
        self._validate_api_key()

        request_params = {
            "api_key": self.api_key,
            "file_type": "json",
            **params,
        }

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        # Adquirir semáforo para mitigar picos de tráfico
        async with self._semaphore:
            async with httpx.AsyncClient(limits=self._limits, timeout=self._timeout) as client:
                try:
                    response = await client.get(url, params=request_params)
                except TRANSIENT_EXCEPTIONS:
                    raise
                except Exception as err:
                    logger.error(f"Error en petición HTTP a FRED: {type(err).__name__} (detalles omitidos por seguridad)")
                    raise RuntimeError(f"Error de transporte en FRED: {type(err).__name__}") from None

                if response.status_code == 429:
                    logger.warning("Límite de tasa de FRED alcanzado (HTTP 429). Activando reintento con backoff.")
                    raise FredRateLimitError("Límite de peticiones de FRED excedido.")

                if response.status_code != 200:
                    logger.error(f"Error HTTP en FRED {response.status_code} (detalles omitidos por seguridad)")
                    raise RuntimeError(f"FRED devolvió estado HTTP {response.status_code}")

                try:
                    raw_bytes = response.content
                    text = raw_bytes.decode("utf-8", errors="replace")
                    data = json.loads(text)
                except Exception as err:
                    logger.error(f"Error parseando JSON de FRED: {type(err).__name__} (detalles omitidos por seguridad)")
                    raise ValueError(f"Respuesta no válida del servidor: {type(err).__name__}") from None

                return data

    @staticmethod
    def _normalize_observations(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza las observaciones de FRED:
        - Convierte el carácter "." a None en el campo 'value'.
        - Intenta coercer los valores válidos a tipo float.
        """
        try:
            observations = data.get("observations", [])
            normalized_obs: List[Dict[str, Any]] = []

            for obs in observations:
                item = dict(obs)
                val = item.get("value")
                
                # FRED usa "." para denotar valores nulos o no disponibles en ciertas fechas
                if val is None or val == "." or str(val).strip() == "":
                    item["value"] = None
                else:
                    try:
                        item["value"] = float(val)
                    except (ValueError, TypeError):
                        item["value"] = None

                normalized_obs.append(item)

            data["observations"] = normalized_obs
            return data
        except Exception as err:
            logger.error(f"Error en normalización de observaciones de FRED: {type(err).__name__} (detalles omitidos por seguridad)")
            return data

    async def get_series_observations(
        self,
        series_id: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Recupera las observaciones de una serie económica específica.

        :param series_id: Identificador de la serie (ej. 'UNRATE', 'GDPC1').
        :param kwargs: Parámetros opcionales adicionales (realtime_start, units, frequency, etc.).
        :return: Diccionario normalizado con las observaciones.
        """
        params = {"series_id": series_id}
        for k, v in kwargs.items():
            if v is not None:
                params[k] = str(v)

        raw_data = await self._execute_request("series/observations", params)
        return self._normalize_observations(raw_data)

    async def search_series(
        self,
        search_text: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Busca series económicas que coincidan con un texto de búsqueda semántica.

        :param search_text: Texto descriptivo de búsqueda (ej. 'inflation').
        :param kwargs: Parámetros opcionales adicionales (order_by, sort_order, etc.).
        :return: Resultados de búsqueda con las series coincidentes.
        """
        params = {"search_text": search_text}
        for k, v in kwargs.items():
            if v is not None:
                params[k] = str(v)

        return await self._execute_request("series/search", params)

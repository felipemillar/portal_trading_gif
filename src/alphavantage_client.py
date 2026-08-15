"""
Cliente asíncrono y resiliente para la API de Alpha Vantage (News & Sentiment).
Soporta detección y recuperación automática del rate limit de la versión gratuita
(el cual retorna HTTP 200 pero con un JSON que contiene la clave "Note" o "Information").
"""

import os
import json
import logging
from typing import Optional, Dict, Any
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

# Configuración del logger
logger = logging.getLogger("AlphaVantageClient")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Silenciar logs detallados de httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

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
    """
    Evalúa si la respuesta requiere un reintento con backoff.
    Alpha Vantage retorna HTTP 200 pero con las claves 'Note' o 'Information' cuando se excede la tasa.
    """
    if result.get("_http_status", 200) in {429, 500, 502, 503, 504}:
        return True
    if "Note" in result or "Information" in result:
        logger.warning("Límite de tasa de Alpha Vantage alcanzado ('Note'/'Information' en respuesta). Iniciando backoff.")
        return True
    return False


class AlphaVantageClient:
    """
    Cliente asíncrono para interactuar con la API de Alpha Vantage.
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout_seconds: float = 20.0,
    ):
        """
        Inicializa el cliente de Alpha Vantage.

        :param api_key: API Key de Alpha Vantage. Si es None, se lee de ALPHAVANTAGE_API_KEY.
        :param timeout_seconds: Timeout para operaciones de red.
        """
        self.api_key = api_key or os.environ.get("ALPHAVANTAGE_API_KEY")
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

    def _validate_api_key(self) -> None:
        """Verifica la presencia de la API Key."""
        if not self.api_key:
            raise ValueError(
                "API Key no configurada: Defina ALPHAVANTAGE_API_KEY en el entorno o archivo .env."
            )

    @retry(
        retry=(retry_if_exception_type(TRANSIENT_EXCEPTIONS) | retry_if_result(_evaluate_retry_necessity)),
        wait=wait_exponential_jitter(initial=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _execute_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Ejecuta una petición HTTP asíncrona segura con resiliencia y reintentos automáticos."""
        self._validate_api_key()

        request_params = {
            "apikey": self.api_key,
            **params,
        }

        async with httpx.AsyncClient(limits=self._limits, timeout=self._timeout) as client:
            try:
                response = await client.get(self.BASE_URL, params=request_params)
            except TRANSIENT_EXCEPTIONS:
                raise
            except Exception as err:
                logger.error(f"Error en petición HTTP a Alpha Vantage: {type(err).__name__} (detalles omitidos por seguridad)")
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
                    text = raw_bytes.decode("latin-1", errors="replace")

                data = json.loads(text)
            except Exception as err:
                logger.error(f"Error parseando JSON de Alpha Vantage: {type(err).__name__} (detalles omitidos por seguridad)")
                raise ValueError(f"Respuesta no válida del servidor: {type(err).__name__}") from None

            return data

    async def get_news_sentiment(
        self,
        tickers: Optional[str] = None,
        topics: Optional[str] = None,
        sort: str = "LATEST",
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Consulta noticias y sentimiento utilizando el endpoint NEWS_SENTIMENT de Alpha Vantage.

        :param tickers: Ticker(s) a filtrar (ej. 'AAPL', 'CRYPTO:BTC', 'FOREX:EUR').
        :param topics: Tópico(s) de interés (ej. 'technology', 'financial_markets').
        :param sort: Criterio de ordenamiento ('LATEST', 'EARLIEST', 'RELEVANCE').
        :param limit: Límite de artículos (máx 1000).
        :return: Diccionario con los resultados y las noticias encontradas.
        """
        params = {
            "function": "NEWS_SENTIMENT",
            "sort": sort,
            "limit": str(limit),
        }
        if tickers:
            params["tickers"] = tickers
        if topics:
            params["topics"] = topics

        raw_data = await self._execute_request(params)

        # Si se superó el rate limit y tenacity terminó sus intentos sin éxito, lanzar error semántico
        if "Note" in raw_data or "Information" in raw_data:
            note = raw_data.get("Note") or raw_data.get("Information")
            raise RuntimeError(f"Límite de tasa de Alpha Vantage excedido de forma persistente: {note}")

        return raw_data

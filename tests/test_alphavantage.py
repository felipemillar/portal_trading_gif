"""Pruebas unitarias para el cliente AlphaVantageClient."""

import unittest
from src.alphavantage_client import AlphaVantageClient, _evaluate_retry_necessity


class TestAlphaVantageClient(unittest.TestCase):

    def test_evaluate_retry_necessity_rate_limit(self):
        # Escenario 1: JSON con clave Note (rate limit excedido en Alpha Vantage)
        rate_limit_payload = {
            "Note": "Thank you for using Alpha Vantage! Our standard API rate limit is 5 requests per minute..."
        }
        self.assertTrue(_evaluate_retry_necessity(rate_limit_payload))

        # Escenario 2: JSON con clave Information
        info_payload = {
            "Information": "Thank you for using Alpha Vantage! Our standard API rate limit..."
        }
        self.assertTrue(_evaluate_retry_necessity(info_payload))

        # Escenario 3: Respuesta normal de noticias
        normal_payload = {
            "items": "50",
            "sentiment_score_definition": "...",
            "feed": []
        }
        self.assertFalse(_evaluate_retry_necessity(normal_payload))

    def test_api_key_validation(self):
        import os
        old_val = os.environ.pop("ALPHAVANTAGE_API_KEY", None)
        try:
            client = AlphaVantageClient(api_key=None)
            with self.assertRaises(ValueError):
                import asyncio
                asyncio.run(client.get_news_sentiment())
        finally:
            if old_val is not None:
                os.environ["ALPHAVANTAGE_API_KEY"] = old_val


if __name__ == "__main__":
    unittest.main()

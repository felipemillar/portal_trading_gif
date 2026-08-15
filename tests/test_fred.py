"""Pruebas unitarias para el cliente FredClient."""

import unittest
import os
from src.fred_client import FredClient


class TestFredClient(unittest.TestCase):

    def test_normalize_observations(self):
        # Datos simulados con valores de punto ".", números en cadena y vacíos
        payload = {
            "observations": [
                {"date": "2026-01-01", "value": "."},
                {"date": "2026-02-01", "value": "5.3"},
                {"date": "2026-03-01", "value": "  "},
                {"date": "2026-04-01", "value": None},
                {"date": "2026-05-01", "value": "invalid_number"}
            ]
        }
        
        normalized = FredClient._normalize_observations(payload)
        obs = normalized["observations"]

        self.assertIsNone(obs[0]["value"])  # El punto "." se convierte a None
        self.assertEqual(obs[1]["value"], 5.3)  # Coerción exitosa a float
        self.assertIsNone(obs[2]["value"])  # Cadenas vacías se convierten a None
        self.assertIsNone(obs[3]["value"])  # None se mantiene como None
        self.assertIsNone(obs[4]["value"])  # Cadenas no numéricas se convierten a None

    def test_api_key_validation(self):
        # Validar que si no se define la API key, se lanza ValueError
        old_val = os.environ.pop("FRED_API_KEY", None)
        try:
            client = FredClient(api_key=None)
            with self.assertRaises(ValueError):
                import asyncio
                asyncio.run(client.get_series_observations("UNRATE"))
        finally:
            if old_val is not None:
                os.environ["FRED_API_KEY"] = old_val


if __name__ == "__main__":
    unittest.main()

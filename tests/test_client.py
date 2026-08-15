"""Pruebas unitarias para el cliente BCChClient."""

import unittest
from datetime import datetime
from src.bcch_client import BCChClient


class TestBCChClient(unittest.TestCase):

    def test_normalize_series_payload(self):
        raw_payload = {
            "Codigo": 0,
            "Descripcion": "Success",
            "Series": {
                "descripEsp": "Dólar Observado",
                "Obs": [
                    {"indexDateString": "14-08-2026", "value": "935.20", "statusCode": "OK"},
                    {"indexDateString": "13-08-2026", "value": "930.50", "statusCode": "OK"},
                    {"indexDateString": "12-08-2026", "value": "", "statusCode": "ND"},
                ]
            }
        }

        normalized = BCChClient._normalize_series_payload(raw_payload)
        obs = normalized["Series"]["Obs"]

        self.assertEqual(obs[0]["indexDateString"], "2026-08-14")
        self.assertEqual(obs[0]["value"], 935.20)
        self.assertIsInstance(obs[0]["value"], float)

        self.assertEqual(obs[1]["indexDateString"], "2026-08-13")
        self.assertEqual(obs[1]["value"], 930.50)

        self.assertIsNone(obs[2]["value"])

    def test_apply_forward_fill(self):
        obs = [
            {"indexDateString": "2026-08-10", "value": 920.0, "statusCode": "OK"},
            {"indexDateString": "2026-08-12", "value": 925.0, "statusCode": "OK"},
        ]

        filled = BCChClient._apply_forward_fill(obs, "2026-08-10", "2026-08-13")

        self.assertEqual(len(filled), 4)
        self.assertEqual(filled[0]["indexDateString"], "2026-08-10")
        self.assertEqual(filled[0]["value"], 920.0)

        # 2026-08-11 debe estar interpolado con el valor de 2026-08-10
        self.assertEqual(filled[1]["indexDateString"], "2026-08-11")
        self.assertEqual(filled[1]["value"], 920.0)
        self.assertTrue(filled[1].get("interpolated"))

        # 2026-08-12 es valor oficial
        self.assertEqual(filled[2]["indexDateString"], "2026-08-12")
        self.assertEqual(filled[2]["value"], 925.0)

        # 2026-08-13 interpolado con 2026-08-12
        self.assertEqual(filled[3]["indexDateString"], "2026-08-13")
        self.assertEqual(filled[3]["value"], 925.0)

    def test_search_series_frequency_validation(self):
        client = BCChClient(user="test@example.com", password="dummy_password")
        import asyncio

        with self.assertRaises(ValueError):
            asyncio.run(client.search_series("HOURLY"))


if __name__ == "__main__":
    unittest.main()

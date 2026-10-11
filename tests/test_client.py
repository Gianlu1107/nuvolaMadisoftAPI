"""
Test per il client NuvolaClient con mocking delle chiamate di rete urllib.
"""

import io
import json
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nuvola_api.client import NuvolaClient
from nuvola_api.exceptions import NuvolaAuthError, NuvolaNotFoundError, NuvolaPermissionError


class MockHTTPResponse:
    def __init__(self, data: dict, status: int = 200):
        self.raw_data = json.dumps(data).encode("utf-8")
        self.status = status

    def read(self):
        return self.raw_data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestNuvolaClient(unittest.TestCase):
    def setUp(self):
        self.client = NuvolaClient(
            username="mario.rossi",
            password="fake-password",
            session_file=None,  # Nessuna scrittura su disco durante i test
            auto_save_session=False,
        )

    @patch("urllib.request.urlopen")
    def test_login_success(self, mock_urlopen):
        mock_resp = {
            "token": "mock-jwt-token",
            "refreshToken": "mock-refresh-token",
            "idAnagrafica": 1042,
            "nome": "MARIO",
            "cognome": "ROSSI",
            "codiceCliente": "RMIC8AB001"
        }
        mock_urlopen.return_value = MockHTTPResponse(mock_resp, 200)

        ok = self.client.login()
        self.assertTrue(ok)
        self.assertEqual(self.client.session_data.get("token"), "mock-jwt-token")
        self.assertEqual(self.client.session_data.get("refreshToken"), "mock-refresh-token")
        self.assertTrue(self.client.is_authenticated())

    @patch("urllib.request.urlopen")
    def test_login_invalid_credentials(self, mock_urlopen):
        err_fp = io.BytesIO(b'{"code": 401, "message": "Username o password errate"}')
        mock_urlopen.side_effect = HTTPError("http://fake", 401, "Unauthorized", {}, err_fp)

        with self.assertRaises(NuvolaAuthError):
            self.client.login()

    @patch("urllib.request.urlopen")
    def test_refresh_token_success(self, mock_urlopen):
        self.client.session_data = {
            "token": "expired-jwt",
            "refreshToken": "valid-refresh-token",
            "expires_at": time.time() - 100
        }
        mock_resp = {
            "token": "new-jwt-token",
            "refreshToken": "new-refresh-token"
        }
        mock_urlopen.return_value = MockHTTPResponse(mock_resp, 200)

        ok = self.client.refresh_token()
        self.assertTrue(ok)
        self.assertEqual(self.client.session_data.get("token"), "new-jwt-token")
        self.assertEqual(self.client.session_data.get("refreshToken"), "new-refresh-token")

    @patch("urllib.request.urlopen")
    def test_get_alunni(self, mock_urlopen):
        self.client.session_data = {
            "token": "valid-jwt",
            "expires_at": time.time() + 1000
        }
        mock_resp = {
            "valori": [
                {
                    "id": 12345,
                    "nome": "LUCA",
                    "cognome": "ROSSI",
                    "nomeCompleto": "LUCA ROSSI",
                    "attivoInAnnoScolasticoCorrente": True,
                    "classe": "3B",
                    "scuola": "SCUOLA MEDIA"
                }
            ]
        }
        mock_urlopen.return_value = MockHTTPResponse(mock_resp, 200)

        alunni = self.client.get_alunni()
        self.assertEqual(len(alunni), 1)
        self.assertEqual(alunni[0].nome, "LUCA")
        self.assertEqual(alunni[0].classe, "3B")

    @patch("urllib.request.urlopen")
    def test_http_403_permission_error(self, mock_urlopen):
        self.client.session_data = {
            "token": "valid-jwt",
            "expires_at": time.time() + 1000
        }
        err_fp = io.BytesIO(b'{"code": 403, "message": "Access Denied"}')
        mock_urlopen.side_effect = HTTPError("http://fake", 403, "Forbidden", {}, err_fp)

        with self.assertRaises(NuvolaPermissionError):
            self.client.get_alunni()

    @patch("urllib.request.urlopen")
    def test_http_404_not_found(self, mock_urlopen):
        self.client.session_data = {
            "token": "valid-jwt",
            "expires_at": time.time() + 1000
        }
        err_fp = io.BytesIO(b'{"code": 404, "message": "Not Found"}')
        mock_urlopen.side_effect = HTTPError("http://fake", 404, "Not Found", {}, err_fp)

        with self.assertRaises(NuvolaNotFoundError):
            self.client.get_envelope_values("/not-found-endpoint")


if __name__ == "__main__":
    unittest.main()

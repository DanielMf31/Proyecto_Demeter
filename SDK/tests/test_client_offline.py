"""Tests for DemeterClient offline behaviour (mocked HTTP)."""
from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock

from demeter_sdk import DemeterClient
from demeter_sdk._types import SDKConfig


class TestClientInit:
    def test_requires_api_key(self):
        import os
        os.environ.pop("DEMETER_API_KEY", None)
        with pytest.raises(ValueError, match="api_key"):
            DemeterClient(api_key=None)

    def test_reads_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("DEMETER_API_KEY", "env_test_key")
        client = DemeterClient()
        assert client._config.api_key == "env_test_key"

    def test_base_url_trailing_slash_stripped(self):
        client = DemeterClient(api_key="x", base_url="http://localhost:8000/")
        assert not client._config.base_url.endswith("/")


class TestClientPing:
    def test_ping_true_on_200(self):
        client = DemeterClient(api_key="test", base_url="http://fake:9999")
        mock_resp = MagicMock()
        mock_resp.ok = True
        with patch.object(client._session, "get", return_value=mock_resp):
            assert client.ping() is True

    def test_ping_false_on_connection_error(self):
        import requests
        client = DemeterClient(api_key="test", base_url="http://fake:9999")
        with patch.object(
            client._session, "get",
            side_effect=requests.exceptions.ConnectionError
        ):
            assert client.ping() is False


class TestClientFetch:
    def test_get_raw_data_calls_correct_url(self, raw_records):
        client = DemeterClient(api_key="test", base_url="http://fake:9999")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.ok = True
        mock_resp.json.return_value = raw_records

        with patch.object(client._session, "get", return_value=mock_resp) as mock_get:
            with patch("demeter_sdk.fetcher._is_fresh", return_value=False):
                with patch("demeter_sdk.fetcher._save_parquet"):
                    data = client.get_raw_data(1, dias=7, force_refresh=True)

        called_url = mock_get.call_args[0][0]
        assert "/sdk/mediciones/1" in called_url
        assert len(data) == len(raw_records)

    def test_get_enriched_data_structure(self, raw_records):
        client = DemeterClient(api_key="test", base_url="http://fake:9999")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.ok = True
        mock_resp.json.return_value = raw_records

        with patch.object(client._session, "get", return_value=mock_resp):
            with patch("demeter_sdk.fetcher._is_fresh", return_value=False):
                with patch("demeter_sdk.fetcher._save_parquet"):
                    df = client.get_enriched_data(
                        1, dias=2, fecha_siembra="2025-09-01", force_refresh=True
                    )

        assert "vpd_kpa" in df.columns
        assert "dap_days" in df.columns
        assert len(df) > 0

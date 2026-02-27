"""
demeter_sdk._session
~~~~~~~~~~~~~~~~~~~~
Module 1 — Core: Robust HTTPS session with auto-retry and authentication.
"""
from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ._types import SDKConfig

logger = logging.getLogger("demeter_sdk.session")


def build_session(config: SDKConfig) -> requests.Session:
    """
    Build a requests.Session pre-configured with:
    - X-API-Key authentication header
    - Exponential-backoff retry (500/502/503/504), up to config.max_retries
    - Timeout applied on every request via a session-level hook
    """
    session = requests.Session()
    session.headers.update({
        "X-API-Key": config.api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    })

    retry_config = Retry(
        total=config.max_retries,
        backoff_factor=config.backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_config)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    logger.debug(
        "Session created for %s (retries=%d, backoff=%.1f)",
        config.base_url,
        config.max_retries,
        config.backoff_factor,
    )
    return session


def ping(session: requests.Session, base_url: str, timeout: int = 5) -> bool:
    """
    Quick health-check against the Demeter API.

    Returns:
        True if the server responds with HTTP 2xx, False otherwise.

    Example::

        client = DemeterClient(api_key="xxx")
        if not client.ping():
            print("Server offline — aborting run.")
    """
    url = f"{base_url}/api/system/status"
    try:
        resp = session.get(url, timeout=timeout)
        return resp.ok
    except requests.exceptions.ConnectionError:
        logger.warning("ping() — connection refused at %s", url)
        return False
    except requests.exceptions.Timeout:
        logger.warning("ping() — timed out after %ds", timeout)
        return False

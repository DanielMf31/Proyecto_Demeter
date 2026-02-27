"""
Demeter SDK — Official Python client for the Demeter IoT Platform.

Import the main client::

    from demeter_sdk import DemeterClient

    client = DemeterClient(api_key="dk_test_xxx")
    df = client.get_enriched_data(experimento_id=1)

Or use individual modules directly::

    from demeter_sdk import science, viz, export
    df_enriched = science.enrich(df)
    fig = viz.plot_vpd(df_enriched)
"""
from .client import DemeterClient
from . import science, transform, viz, export, fetcher

__version__ = "1.0.0"
__author__ = "Daniel M.F. — Proyecto Demeter"

__all__ = [
    "DemeterClient",
    "science",
    "transform",
    "viz",
    "export",
    "fetcher",
    "__version__",
]

import pytest
import os
from pathlib import Path
from proyecto_demeter.config import settings

def test_paths_structure():
    """Verify that important paths are resolved correctly relative to the project root."""
    # BASE_DIR should end in "Python"
    assert settings.BASE_DIR.name == "Python"
    
    # Logs dir should be Python/logs
    assert settings.LOG_DIR == settings.BASE_DIR / "logs"
    
    # Data dir should be Python/data
    assert settings.DATA_DIR == settings.BASE_DIR / "data"

    # Config dir should be Python/config
    assert settings.CONFIG_DIR == settings.BASE_DIR / "config"

def test_defaults():
    """Verify default values."""
    assert settings.APP_NAME == "Demeter IoT"
    assert settings.DB_NAME == "demeter_data.db"
    assert settings.DEBUG is False

def test_env_override(monkeypatch):
    """Verify that environment variables override defaults."""
    monkeypatch.setenv("DEMETER_DEBUG", "true")
    monkeypatch.setenv("DEMETER_APP_NAME", "Test App")
    
    # Reload settings or create new instance (since singleton is already instantiated)
    from proyecto_demeter.config.provider import Settings
    new_settings = Settings()
    
    assert new_settings.DEBUG is True
    assert new_settings.APP_NAME == "Test App"

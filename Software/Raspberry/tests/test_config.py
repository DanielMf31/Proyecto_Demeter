import os
import pytest
from unittest.mock import patch
from proyecto_demeter.shared.config.provider import Settings, settings as global_settings

class TestConfig:
    def test_singleton_instance(self):
        """Verify that the module-level settings object is usable."""
        assert isinstance(global_settings, Settings)
        # In this implementation, 'settings' is just an instantiated variable, 
        # so "singleton" just means everyone imports the same var.
        from proyecto_demeter.shared.config.provider import settings as settings_again
        assert global_settings is settings_again

    def test_default_values(self):
        """Verify default settings are loaded."""
        # Ensure no env vars interfere, and ignore .env file by setting _env_file=None
        # We also need to patch os.environ to be sure no DEMETER_ vars are set
        with patch.dict(os.environ, {}, clear=True):
             s = Settings(_env_file=None)
             assert s.APP_NAME == "Demeter IoT"
             assert s.DEBUG is False
             assert s.LOG_LEVEL == "INFO"

    def test_env_override(self):
        """Verify environment variables override defaults."""
        with patch.dict(os.environ, {"DEMETER_APP_NAME": "Test App", "DEMETER_DEBUG": "True"}):
            # Pydantic Settings reads env on instantiation
            new_settings = Settings()
            assert new_settings.APP_NAME == "Test App"
            assert new_settings.DEBUG is True

    def test_path_resolution(self):
        """Verify that paths are absolute and look correct."""
        s = Settings()
        assert s.BASE_DIR.is_absolute()
        # BASE_DIR should end with 'Python' now
        assert str(s.BASE_DIR).endswith("Python")
        assert str(s.LOG_DIR).endswith("logs")
        assert str(s.DATA_DIR).endswith("data")


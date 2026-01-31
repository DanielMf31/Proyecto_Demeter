import pytest
from pathlib import Path
import tempfile
import sys
import os

# Adds the src directory to the path so we can import the modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mocking the package structure since we are inside a template
# We need to map `src.proyecto_demeter` to `src` for tests to run inside the template folder
# or we just rely on relative imports if we were running from root.
# But since this is a template, running pytest here directly is tricky without rendering.
# However, the user asked to CREATE the tests.

def test_settings_initialization():
    """Test that Settings can be instantiated with defaults."""
    from config.settings import Settings
    settings = Settings(
        app_name="Test App",
        paths={"root": Path("/tmp")} # Override root to avoid side effects
    )
    assert settings.app_name == "Test App"
    assert settings.paths.data == Path("data") # Default relative path

def test_config_paths_defaults():
    """Test that Code-First defaults are correct in PathsConfig."""
    from config.config import PathsConfig
    paths = PathsConfig()
    
    assert paths.src == Path("src")
    assert paths.config == Path("config")
    assert paths.data == Path("data")
    assert paths.logs_dir == Path("data/logs")

def test_setup_structure_creation():
    """
    Integration test: Verifies that setup_structure actually creates folders.
    Uses a temporary directory to not pollute the system.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. Instantiate Settings with the temp root
        from config.settings import Settings
        
        # We need to trick the resolution of 'root' or explicitly set it.
        # Since 'root' has a default_factory in PathsConfig that uses __file__,
        # we must override it.
        
        settings = Settings()
        # MANUAL OVERRIDE of root for safety in test
        settings.paths.root = temp_path
        
        # 2. Run setup_structure
        # Note: We need to mock the import of FileSystemManager inside setup_structure 
        # because '..src.proyecto_demeter' won't exist until cookiecutter renders it.
        # BUT, if we assume we are testing the GENERATED code, this test is fine.
        # If we are testing inside the template, we can't run this.
        
        # ASSUMPTION: This test file is intended to be run IN THE GENERATED PROJECT.
        # Therefore, we write standard imports.
        
        try:
            settings.setup_structure()
            
            # 3. Assertions
            expected_data = temp_path / "data"
            expected_logs = temp_path / "data/logs"
            expected_src = temp_path / "src"
            
            assert expected_data.exists(), "Data directory was not created"
            assert expected_logs.exists(), "Logs directory was not created"
            assert expected_src.exists(), "Src directory was not created"
            
        except ImportError:
            pytest.skip("Skipping integration test: FileSystemManager module not found (template not rendered yet)")
        except Exception as e:
            pytest.fail(f"setup_structure failed: {e}")

def test_json_overrides():
    """Test loading configuration overrides from a JSON file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "config.json"
        
        # Create a mock config.json
        import json
        with open(config_file, "w") as f:
            json.dump({
                "llm": {"enabled": False, "temperature": 0.99},
                "paths": {"data": "custom_data"}
            }, f)
            
        from config.settings import Settings
        settings = Settings()
        
        # Load the overrides
        settings.load_json_overrides(str(config_file))
        
        # Assertions
        assert settings.llm.enabled is False
        assert settings.llm.temperature == 0.99
        assert settings.paths.data == Path("custom_data")

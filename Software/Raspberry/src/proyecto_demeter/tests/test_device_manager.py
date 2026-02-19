import pytest
import json
import os
from pathlib import Path
from proyecto_demeter.Hardware.management.device_manager import DeviceManager

@pytest.fixture
def mock_devices_json(tmp_path):
    d = tmp_path / "devices.json"
    content = {
        "devices": {
            "pump": {
                "1": {"target_id": 1, "physical_pin": 4, "label": "Bomba 1"},
                "2": {"target_id": 1, "physical_pin": 5, "label": "Bomba 2"}
            },
            "valve": {
                "1": {"target_id": 1, "physical_pin": 10, "label": "Válvula 1"}
            }
        }
    }
    d.write_text(json.dumps(content))
    return str(d)

def test_load_config(mock_devices_json):
    dm = DeviceManager(config_path=mock_devices_json)
    assert dm.load_config() is True
    config = dm.get_config()
    assert "pump" in config
    assert "valve" in config
    assert config["pump"]["1"]["physical_pin"] == 4

def test_get_physical_mapping(mock_devices_json):
    dm = DeviceManager(config_path=mock_devices_json)
    
    # Test valid pump
    mapping = dm.get_physical_mapping("pump", "1")
    assert mapping == (1, 4)
    
    # Test valid valve (string ID)
    mapping = dm.get_physical_mapping("valve", "1")
    assert mapping == (1, 10)
    
    # Test valid valve (int ID)
    mapping = dm.get_physical_mapping("valve", 1)
    assert mapping == (1, 10)
    
    # Test non-existent device
    assert dm.get_physical_mapping("pump", "99") is None
    assert dm.get_physical_mapping("unknown", "1") is None

def test_translate_pin(mock_devices_json):
    dm = DeviceManager(config_path=mock_devices_json)
    
    # Pump translation (logical 1-4)
    assert dm.translate_pin(1) == (1, 4)
    assert dm.translate_pin(2) == (1, 5)
    
    # Valve translation (logical 5-8)
    assert dm.translate_pin(5) == (1, 10)
    
    # Fallback (logical 9+)
    assert dm.translate_pin(9) == (1, 9)

def test_load_missing_file():
    dm = DeviceManager(config_path="non_existent.json")
    assert dm.load_config() is False
    assert dm.get_config() == {}

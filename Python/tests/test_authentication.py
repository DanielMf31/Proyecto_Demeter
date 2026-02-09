import pytest
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "users.json")

def test_users_json_exists():
    assert os.path.exists(CONFIG_PATH), "users.json not found"

def test_users_json_valid_structure():
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    
    assert isinstance(data, dict), "Root must be a dictionary"
    assert len(data) > 0, "Must have at least one user"
    
    for user, pwd in data.items():
        assert isinstance(user, str)
        assert isinstance(pwd, str)
        assert len(user) > 0
        assert len(pwd) > 0

def test_default_credentials():
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    
    assert "admin" in data
    assert data["admin"] == "admin123"

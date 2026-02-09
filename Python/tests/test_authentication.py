import pytest
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "users.json")

def test_users_json_exists():
    assert os.path.exists(CONFIG_PATH), "users.json not found"

def test_users_json_valid_structure():
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    
    assert "users" in data, "Root must contain 'users' key"
    assert isinstance(data["users"], list), "'users' must be a list"
    assert len(data["users"]) > 0, "Must have at least one user"
    
    for u in data["users"]:
        assert "username" in u
        assert "password" in u
        assert isinstance(u["username"], str)
        assert isinstance(u["password"], str)

def test_default_credentials():
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    
    # Check for admin user
    admin_user = next((u for u in data["users"] if u["username"] == "admin"), None)
    assert admin_user is not None
    assert admin_user["password"] == "123"

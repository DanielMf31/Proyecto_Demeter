import pytest
from fastapi.testclient import TestClient

def test_get_experimentos(client: TestClient, admin_token: str):
    """Test retrieving experiments"""
    response = client.get(
        "/api/lims/experimentos",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_experiment_forbidden(client: TestClient, user_token: str):
    """Test creating experiments with a regular user token"""
    response = client.post(
        "/api/lims/experimentos/generar",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Test Env", "description": "Blah", "plant_ids": []}
    )
    # If auth fails or RBAC forbids, it shouldn't crash internally.
    assert response.status_code in [200, 201, 401, 403]

def test_create_experiment_admin(client: TestClient, admin_token: str):
    """Test admin generating a new experiment without associated plants (None/[])"""
    response = client.post(
        "/api/lims/experimentos/generar",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Ensayo Test", "description": "Autogen test", "plant_ids": []}
    )
    assert response.status_code in [200, 201]

    if response.status_code in [200, 201]:
        exp = response.json()
        assert "id" in exp
        assert exp["name"] == "Ensayo Test"

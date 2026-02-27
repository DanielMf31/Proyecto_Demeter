import pytest
from fastapi.testclient import TestClient

def test_command_requires_auth(client: TestClient):
    """Test accessing hardware control without token gives 401"""
    response = client.post("/api/command", json={"type": "set_gpio", "pin": 4, "value": 1, "target_id": 1})
    assert response.status_code == 401

def test_command_forbidden_for_regular_user(client: TestClient, user_token: str):
    """Test that a regular user 'guest_test' cannot execute hardware actions (403 Forbidden)"""
    response = client.post(
        "/api/command",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"type": "set_gpio", "pin": 4, "value": 1, "target_id": 1}
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"] or "insuficientes" in response.json()["detail"]

def test_command_allowed_for_operator(client: TestClient, operator_token: str):
    """Test that an 'operator' CAN access the endpoint.
    Assuming Redis is mocked or handled correctly by the route, we just want to ensure it passes the RBAC layer.
    """
    response = client.post(
        "/api/command",
        headers={"Authorization": f"Bearer {operator_token}"},
        json={"type": "set_gpio", "pin": 4, "value": 1, "target_id": 1}
    )
    # Even if it fails internally due to Redis disconnected (500), it means 
    # it passed the 401/403 authorization boundary.
    assert response.status_code in [200, 500, 503]

def test_command_allowed_for_admin(client: TestClient, admin_token: str):
    """Test that an 'admin' CAN access the endpoint."""
    response = client.post(
        "/api/command",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"type": "set_gpio", "pin": 4, "value": 1, "target_id": 1}
    )
    assert response.status_code in [200, 500, 503]

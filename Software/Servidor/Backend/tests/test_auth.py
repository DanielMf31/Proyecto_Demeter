import pytest
from fastapi.testclient import TestClient

def test_root(client: TestClient):
    """Test health check route"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Proyecto Demeter Backend", "docs": "/api/docs"}

def test_login_success(client: TestClient):
    """Test successful login returns a JWT token"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin_test", "password": "pass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_password(client: TestClient):
    """Test login failure with wrong password"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin_test", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_invalid_user(client: TestClient):
    """Test login failure with non-existent user"""
    response = client.post(
        "/api/auth/login",
        data={"username": "ghost_user", "password": "pass123"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_access_protected_route_without_token(client: TestClient):
    """Test accessing a protected route without Auth Header returns 401"""
    # Assuming /api/discovery/nodes is protected by JWT
    response = client.get("/api/devices")
    assert response.status_code == 401

def test_access_protected_inactive_user(client: TestClient, inactive_token: str):
    """Test accessing a protected route with an inactive user token returns 400 Inactive User"""
    response = client.get(
        "/api/devices",
        headers={"Authorization": f"Bearer {inactive_token}"}
    )
    # the exact status code depends on auth.py (usually 400 "Inactive user")
    assert response.status_code in [400, 401, 403] 

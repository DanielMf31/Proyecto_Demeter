import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@patch("API.routers.analysis_router.task_queue.enqueue")
def test_analysis_generate_success(mock_enqueue, client: TestClient, admin_token: str):
    """Test mathematical calculation enqueued successfully in RQ"""
    # Simulate a fake RQ Job return
    fake_job = MagicMock()
    fake_job.id = "fake-job-uuid-1234"
    mock_enqueue.return_value = fake_job

    response = client.post(
        "/api/analysis/generate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"experimento_id": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["task_id"] == "fake-job-uuid-1234"

def test_analysis_generate_invalid(client: TestClient, operator_token: str):
    """Test analysis returns validation error/422 on bad body"""
    response = client.post(
        "/api/analysis/generate",
        headers={"Authorization": f"Bearer {operator_token}"},
        json={"bad_key": [1,2,3]}
    )
    assert response.status_code == 422 # Pydantic Validation Error

def test_fetch_metrics_without_auth(client: TestClient):
    """Test calculating metrics returns 401 if unauthenticated"""
    response = client.post(
        "/api/analysis/generate",
        json={"experimento_id": 5}
    )
    assert response.status_code == 401


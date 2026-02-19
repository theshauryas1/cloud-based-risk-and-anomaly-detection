"""
tests/test_health.py — Tests for GET /health.
"""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_schema(client):
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "fraud_model" in data
    assert "anomaly_model" in data


def test_health_model_versions_non_empty(client):
    data = client.get("/health").json()
    assert data["fraud_model"] != ""
    assert data["anomaly_model"] != ""

"""
tests/test_anomaly.py — Tests for POST /v1/anomaly/predict.
"""
VALID_PAYLOAD = {
    "response_time": 950.0,
    "error_rate": 0.12,
    "cpu_usage": 91.0,
    "memory_usage": 87.0,
}


def test_anomaly_predict_returns_200(client):
    response = client.post("/v1/anomaly/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200


def test_anomaly_predict_response_schema(client):
    data = client.post("/v1/anomaly/predict", json=VALID_PAYLOAD).json()
    assert "anomaly_score" in data
    assert "model_version" in data
    assert "latency_ms" in data


def test_anomaly_score_in_range(client):
    data = client.post("/v1/anomaly/predict", json=VALID_PAYLOAD).json()
    assert 0.0 <= data["anomaly_score"] <= 1.0


def test_anomaly_latency_is_positive(client):
    data = client.post("/v1/anomaly/predict", json=VALID_PAYLOAD).json()
    assert data["latency_ms"] > 0


def test_anomaly_model_version_non_empty(client):
    data = client.post("/v1/anomaly/predict", json=VALID_PAYLOAD).json()
    assert data["model_version"] != ""


def test_anomaly_predict_missing_field_returns_422(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "response_time"}
    response = client.post("/v1/anomaly/predict", json=payload)
    assert response.status_code == 422


def test_anomaly_predict_error_rate_out_of_range_returns_422(client):
    bad = {**VALID_PAYLOAD, "error_rate": 1.5}   # must be ≤ 1.0
    response = client.post("/v1/anomaly/predict", json=bad)
    assert response.status_code == 422


def test_anomaly_normal_vs_anomalous_ordering(client):
    """Normal system metrics should score lower than extreme anomalous metrics."""
    normal = {
        "response_time": 100.0,
        "error_rate": 0.01,
        "cpu_usage": 30.0,
        "memory_usage": 40.0,
    }
    anomalous = {
        "response_time": 2000.0,
        "error_rate": 0.80,
        "cpu_usage": 98.0,
        "memory_usage": 97.0,
    }
    n_score = client.post("/v1/anomaly/predict", json=normal).json()["anomaly_score"]
    a_score = client.post("/v1/anomaly/predict", json=anomalous).json()["anomaly_score"]
    assert a_score > n_score, "Anomalous metrics should score higher than normal metrics"

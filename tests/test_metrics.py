"""
tests/test_metrics.py — Tests for GET /v1/metrics.
"""


def test_metrics_returns_200(client):
    response = client.get("/v1/metrics")
    assert response.status_code == 200


def test_metrics_response_schema(client):
    data = client.get("/v1/metrics").json()
    required_keys = {
        "total_predictions",
        "fraud_predictions",
        "anomaly_predictions",
        "avg_fraud_latency_ms",
        "avg_anomaly_latency_ms",
        "avg_fraud_probability",
        "avg_anomaly_score",
    }
    assert required_keys.issubset(data.keys())


def test_metrics_totals_consistent(client):
    # Make one fraud and one anomaly prediction first
    client.post("/v1/fraud/predict", json={
        "transaction_amount": 500, "merchant_type": "grocery",
        "country": "US", "time_delta": 10, "device_type": "desktop"
    })
    client.post("/v1/anomaly/predict", json={
        "response_time": 150, "error_rate": 0.02,
        "cpu_usage": 35, "memory_usage": 50
    })

    data = client.get("/v1/metrics").json()
    assert data["total_predictions"] == data["fraud_predictions"] + data["anomaly_predictions"]
    assert data["fraud_predictions"] >= 1
    assert data["anomaly_predictions"] >= 1

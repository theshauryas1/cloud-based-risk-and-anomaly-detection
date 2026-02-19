"""
tests/test_fraud.py — Tests for POST /v1/fraud/predict.
"""
VALID_PAYLOAD = {
    "transaction_amount": 2500.00,
    "merchant_type": "electronics",
    "country": "US",
    "time_delta": 5.2,
    "device_type": "mobile",
}


def test_fraud_predict_returns_200(client):
    response = client.post("/v1/fraud/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200


def test_fraud_predict_response_schema(client):
    data = client.post("/v1/fraud/predict", json=VALID_PAYLOAD).json()
    assert "fraud_probability" in data
    assert "model_version" in data
    assert "latency_ms" in data


def test_fraud_probability_in_range(client):
    data = client.post("/v1/fraud/predict", json=VALID_PAYLOAD).json()
    assert 0.0 <= data["fraud_probability"] <= 1.0


def test_fraud_latency_is_positive(client):
    data = client.post("/v1/fraud/predict", json=VALID_PAYLOAD).json()
    assert data["latency_ms"] > 0


def test_fraud_model_version_non_empty(client):
    data = client.post("/v1/fraud/predict", json=VALID_PAYLOAD).json()
    assert data["model_version"] != ""


def test_fraud_predict_missing_field_returns_422(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "transaction_amount"}
    response = client.post("/v1/fraud/predict", json=payload)
    assert response.status_code == 422


def test_fraud_predict_negative_amount_returns_422(client):
    bad = {**VALID_PAYLOAD, "transaction_amount": -100}
    response = client.post("/v1/fraud/predict", json=bad)
    assert response.status_code == 422


def test_fraud_predict_high_risk_profile(client):
    """High-amount, overnight, risky country → should return higher probability."""
    high_risk = {
        "transaction_amount": 9999.99,
        "merchant_type": "gaming",
        "country": "NG",
        "time_delta": 0.1,
        "device_type": "mobile",
    }
    low_risk = {
        "transaction_amount": 25.00,
        "merchant_type": "grocery",
        "country": "US",
        "time_delta": 48.0,
        "device_type": "desktop",
    }
    hr = client.post("/v1/fraud/predict", json=high_risk).json()["fraud_probability"]
    lr = client.post("/v1/fraud/predict", json=low_risk).json()["fraud_probability"]
    assert hr > lr, "High-risk transaction should have higher fraud probability"

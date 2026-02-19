"""
app/models/train_fraud.py
─────────────────────────
Trains a Logistic Regression fraud classifier on synthetic transaction data.
Saves the model + metadata to app/models/artifacts/fraud_model.pkl.

Run once before starting the server:
    python -m app.models.train_fraud
"""
import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ── Reproducibility ──────────────────────────────────────────
SEED = 42
np.random.seed(SEED)

# ── Synthetic data generation ────────────────────────────────
N = 2000

merchant_types = ["electronics", "grocery", "travel", "clothing", "gaming"]
countries = ["US", "UK", "DE", "FR", "CN", "NG", "RU"]
device_types = ["mobile", "desktop", "tablet"]

merchant_enc = {m: i for i, m in enumerate(merchant_types)}
country_enc = {c: i for i, c in enumerate(countries)}
device_enc = {d: i for i, d in enumerate(device_types)}

transaction_amount = np.random.exponential(scale=500, size=N)
merchant_type_idx = np.random.choice(len(merchant_types), size=N)
country_idx = np.random.choice(len(countries), size=N)
time_delta = np.random.exponential(scale=24, size=N)
device_type_idx = np.random.choice(len(device_types), size=N)

# Fraud signal: high amount + short time_delta + risky country/device
fraud_score = (
    (transaction_amount > 1500).astype(float) * 0.4
    + (time_delta < 1.0).astype(float) * 0.3
    + (country_idx >= 4).astype(float) * 0.2          # CN, NG, RU = riskier
    + (merchant_type_idx == 4).astype(float) * 0.1    # gaming = riskier
)
labels = (fraud_score + np.random.normal(0, 0.1, N) > 0.45).astype(int)

X = np.column_stack([
    transaction_amount,
    merchant_type_idx,
    country_idx,
    time_delta,
    device_type_idx,
])
y = labels

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)

# ── Model pipeline ───────────────────────────────────────────
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000, random_state=SEED, C=1.0)),
])
pipeline.fit(X_train, y_train)

# ── Evaluation ───────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
print("[fraud] Classification report:")
print(classification_report(y_test, y_pred))

# ── Metadata ─────────────────────────────────────────────────
metadata = {
    "model_version": "fraud-v1.0.0",
    "algorithm": "LogisticRegression",
    "features": ["transaction_amount", "merchant_type", "country", "time_delta", "device_type"],
    "encodings": {
        "merchant_type": merchant_enc,
        "country": country_enc,
        "device_type": device_enc,
    },
    "training_samples": int(len(X_train)),
    "trained_at": "2026-02-19",
}

# ── Persist ──────────────────────────────────────────────────
os.makedirs("app/models/artifacts", exist_ok=True)
artifact = {"pipeline": pipeline, "metadata": metadata}
joblib.dump(artifact, "app/models/artifacts/fraud_model.pkl")
print(f"[fraud] Saved -> app/models/artifacts/fraud_model.pkl  "
      f"(version={metadata['model_version']})")

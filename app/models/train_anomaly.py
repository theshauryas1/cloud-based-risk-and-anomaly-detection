"""
app/models/train_anomaly.py
────────────────────────────
Trains an Isolation Forest anomaly detector on synthetic system-metrics data.
Saves the model + metadata to app/models/artifacts/anomaly_model.pkl.

Run once before starting the server:
    python -m app.models.train_anomaly
"""
import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ── Reproducibility ──────────────────────────────────────────
SEED = 42
np.random.seed(SEED)

# ── Synthetic data generation ────────────────────────────────
# Normal system metrics
N_NORMAL = 1800
response_time_normal = np.random.normal(loc=120, scale=20, size=N_NORMAL)   # ms
error_rate_normal    = np.random.beta(a=1, b=30, size=N_NORMAL)             # ~0-0.05
cpu_normal           = np.random.normal(loc=40, scale=10, size=N_NORMAL)    # %
memory_normal        = np.random.normal(loc=55, scale=8,  size=N_NORMAL)    # %

# Anomalous metrics (high spike / degradation)
N_ANOMALY = 200
response_time_anom = np.random.normal(loc=900, scale=150, size=N_ANOMALY)
error_rate_anom    = np.random.beta(a=5, b=5, size=N_ANOMALY)              # ~0.3-0.7
cpu_anom           = np.random.normal(loc=88, scale=8, size=N_ANOMALY)
memory_anom        = np.random.normal(loc=90, scale=5, size=N_ANOMALY)

X_normal = np.column_stack([response_time_normal, error_rate_normal, cpu_normal, memory_normal])
X_anom   = np.column_stack([response_time_anom,   error_rate_anom,   cpu_anom,   memory_anom])

# Clip to valid ranges
X_normal[:, 1] = np.clip(X_normal[:, 1], 0, 1)
X_anom[:, 1]   = np.clip(X_anom[:, 1],   0, 1)
X_normal[:, 2:] = np.clip(X_normal[:, 2:], 0, 100)
X_anom[:, 2:]   = np.clip(X_anom[:, 2:],   0, 100)

# IsolationForest trains on normal data (unsupervised)
X_train = X_normal

# ── Model pipeline ───────────────────────────────────────────
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("iso", IsolationForest(
        n_estimators=200,
        contamination=0.05,    # ~5 % anomalies expected in production traffic
        random_state=SEED,
    )),
])
pipeline.fit(X_train)

# ── Quick sanity check ───────────────────────────────────────
X_all = np.vstack([X_normal[:50], X_anom[:50]])
scores_raw = pipeline.named_steps["iso"].decision_function(
    pipeline.named_steps["scaler"].transform(X_all)
)
# Normalise so normal≈0 and anomaly≈1
score_min, score_max = scores_raw.min(), scores_raw.max()
scores_norm = 1 - (scores_raw - score_min) / (score_max - score_min + 1e-9)
avg_normal = scores_norm[:50].mean()
avg_anom   = scores_norm[50:].mean()
print(f"[anomaly] Sanity — avg normal score: {avg_normal:.3f} | avg anomaly score: {avg_anom:.3f}")

# ── Metadata ─────────────────────────────────────────────────
metadata = {
    "model_version": "anomaly-v1.0.0",
    "algorithm": "IsolationForest",
    "features": ["response_time", "error_rate", "cpu_usage", "memory_usage"],
    "contamination": 0.05,
    "score_range": {"min": float(score_min), "max": float(score_max)},
    "training_samples": int(len(X_train)),
    "trained_at": "2026-02-19",
}

# ── Persist ──────────────────────────────────────────────────
os.makedirs("app/models/artifacts", exist_ok=True)
artifact = {"pipeline": pipeline, "metadata": metadata}
joblib.dump(artifact, "app/models/artifacts/anomaly_model.pkl")
print(f"[anomaly] Saved -> app/models/artifacts/anomaly_model.pkl  "
      f"(version={metadata['model_version']})")

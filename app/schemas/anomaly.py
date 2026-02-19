"""
app/schemas/anomaly.py — Pydantic schemas for the anomaly detection endpoint.
"""
from pydantic import BaseModel, Field


class AnomalyRequest(BaseModel):
    response_time: float = Field(..., gt=0, example=950.0,
                                 description="API response time in milliseconds")
    error_rate: float = Field(..., ge=0.0, le=1.0, example=0.12,
                              description="Proportion of failed requests [0-1]")
    cpu_usage: float = Field(..., ge=0.0, le=100.0, example=91.0,
                             description="CPU utilisation percentage [0-100]")
    memory_usage: float = Field(..., ge=0.0, le=100.0, example=87.0,
                                description="Memory utilisation percentage [0-100]")

    model_config = {
        "json_schema_extra": {
            "example": {
                "response_time": 950.0,
                "error_rate": 0.12,
                "cpu_usage": 91.0,
                "memory_usage": 87.0,
            }
        }
    }


class AnomalyResponse(BaseModel):
    anomaly_score: float = Field(..., ge=0.0, le=1.0,
                                 description="Normalised anomaly score; higher = more anomalous")
    model_version: str = Field(..., description="Deployed model version")
    latency_ms: float = Field(..., description="Inference latency in milliseconds")

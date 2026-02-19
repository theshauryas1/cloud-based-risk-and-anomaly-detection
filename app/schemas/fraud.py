"""
app/schemas/fraud.py — Pydantic schemas for the fraud detection endpoint.
"""
from pydantic import BaseModel, Field


class FraudRequest(BaseModel):
    transaction_amount: float = Field(..., gt=0, example=2500.00,
                                      description="Transaction value in USD")
    merchant_type: str = Field(..., example="electronics",
                               description="Category of merchant")
    country: str = Field(..., example="US",
                         description="ISO 2-letter country code")
    time_delta: float = Field(..., ge=0, example=5.2,
                              description="Hours since last transaction")
    device_type: str = Field(..., example="mobile",
                             description="Device used: mobile | desktop | tablet")

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_amount": 2500.00,
                "merchant_type": "electronics",
                "country": "US",
                "time_delta": 5.2,
                "device_type": "mobile",
            }
        }
    }


class FraudResponse(BaseModel):
    fraud_probability: float = Field(..., ge=0.0, le=1.0,
                                     description="Probability that transaction is fraudulent")
    model_version: str = Field(..., description="Deployed model version")
    latency_ms: float = Field(..., description="Inference latency in milliseconds")

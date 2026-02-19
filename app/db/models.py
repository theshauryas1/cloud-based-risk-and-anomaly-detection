"""
app/db/models.py — SQLAlchemy ORM models for persisted predictions.
"""
import datetime
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, func
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class FraudPrediction(Base):
    __tablename__ = "fraud_predictions"

    id = Column(Integer, primary_key=True, index=True)

    # Input features
    transaction_amount = Column(Float, nullable=False)
    merchant_type = Column(String(100), nullable=False)
    country = Column(String(10), nullable=False)
    time_delta = Column(Float, nullable=False)
    device_type = Column(String(50), nullable=False)

    # Output
    fraud_probability = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    latency_ms = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnomalyPrediction(Base):
    __tablename__ = "anomaly_predictions"

    id = Column(Integer, primary_key=True, index=True)

    # Input features
    response_time = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)

    # Output
    anomaly_score = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    latency_ms = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

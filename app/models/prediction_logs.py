from sqlalchemy import Column, BigInteger, Float, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    client_id = Column(BigInteger, ForeignKey("client_features.id"), nullable=False, index=True)
    predicted_income = Column(Float, nullable=False)
    actual_income = Column(Float, nullable=True, comment="Actual income value if available for metrics calculation")
    prediction_error = Column(Float, nullable=True, comment="Absolute error: |predicted - actual| if actual is available")
    prediction_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    request_id = Column(String, nullable=True)
    source = Column(String, nullable=True)
    user = Column(String, nullable=True)


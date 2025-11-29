from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Experiment(BaseModel):
    """ML experiment metrics schema"""
    
    name: str = Field(..., description="Experiment name", example="baseline_model_v1")
    wmae: float = Field(..., description="Weighted Mean Absolute Error", example=0.125)
    date: Optional[str] = Field(None, description="Experiment date in ISO format", example="2024-01-15T10:30:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "baseline_model_v1",
                "wmae": 0.125,
                "date": "2024-01-15T10:30:00Z"
            }
        }


class SegmentError(BaseModel):
    """Segment-specific error metrics schema"""
    
    segment: str = Field(..., description="Client segment name", example="VIP")
    wmae: float = Field(..., description="Weighted Mean Absolute Error for this segment", example=0.095)
    
    class Config:
        json_schema_extra = {
            "example": {
                "segment": "VIP",
                "wmae": 0.095
            }
        }


class ModelMetrics(BaseModel):
    """Model performance metrics schema"""
    
    wmae_validation: float = Field(..., description="Weighted Mean Absolute Error on validation set", example=0.125)
    training_records: int = Field(..., description="Number of records in training set", example=10000, ge=0)
    validation_records: int = Field(..., description="Number of records in validation set", example=2000, ge=0)
    predictions_count: int = Field(..., description="Total number of predictions made", example=5000, ge=0)
    experiments: List[Experiment] = Field(..., description="List of experiment results")
    segment_errors: List[SegmentError] = Field(..., description="Error metrics by client segment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "wmae_validation": 0.125,
                "training_records": 10000,
                "validation_records": 2000,
                "predictions_count": 5000,
                "experiments": [
                    {
                        "name": "baseline_model_v1",
                        "wmae": 0.125,
                        "date": "2024-01-15T10:30:00Z"
                    }
                ],
                "segment_errors": [
                    {
                        "segment": "VIP",
                        "wmae": 0.095
                    }
                ]
            }
        }


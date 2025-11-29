from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union


class IncomePrediction(BaseModel):
    """Income prediction schema"""
    
    predicted_income: float = Field(..., description="Predicted income value", example=85000.0)
    lower_bound: float = Field(..., description="Lower bound of prediction confidence interval", example=75000.0)
    upper_bound: float = Field(..., description="Upper bound of prediction confidence interval", example=95000.0)
    base_income: Optional[float] = Field(None, description="Base income value if available", example=80000.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_income": 85000.0,
                "lower_bound": 75000.0,
                "upper_bound": 95000.0,
                "base_income": 80000.0
            }
        }


class ShapFeature(BaseModel):
    """SHAP feature contribution schema"""
    
    feature_name: str = Field(..., description="Name of the feature", example="age")
    value: Union[float, str] = Field(..., description="Feature value", example=35)
    shap_value: float = Field(..., description="SHAP value contribution", example=1250.5)
    direction: Literal["positive", "negative"] = Field(..., description="Direction of contribution", example="positive")
    description: Optional[str] = Field(None, description="Human-readable description of the feature", example="Client age in years")
    
    class Config:
        json_schema_extra = {
            "example": {
                "feature_name": "age",
                "value": 35,
                "shap_value": 1250.5,
                "direction": "positive",
                "description": "Client age in years"
            }
        }


class ShapResponse(BaseModel):
    """SHAP explanation response schema"""
    
    text_explanation: str = Field(..., description="Human-readable text explanation of the prediction", example="The model predicts higher income based on age and segment")
    features: List[ShapFeature] = Field(..., description="List of feature contributions")
    base_value: Optional[float] = Field(None, description="Base prediction value", example=80000.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text_explanation": "The model predicts higher income based on age and segment",
                "features": [
                    {
                        "feature_name": "age",
                        "value": 35,
                        "shap_value": 1250.5,
                        "direction": "positive",
                        "description": "Client age in years"
                    }
                ],
                "base_value": 80000.0
            }
        }


# Legacy schemas for backward compatibility
class PredictionRequest(BaseModel):
    """Legacy prediction request schema"""
    pass


class PredictionResponse(BaseModel):
    """Legacy prediction response schema"""
    pass


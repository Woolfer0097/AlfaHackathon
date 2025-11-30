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


class IncomeTrend(BaseModel):
    """Income trend over time period"""
    
    period: str = Field(..., description="Time period comparison", example="1 год vs 2 года")
    change_percent: float = Field(..., description="Percentage change", example=5.2)
    description: str = Field(..., description="Human-readable description", example="Зарплата выросла на 5.2%")


class IncomeDynamicsShapResponse(BaseModel):
    """SHAP analysis for income dynamics over time"""
    
    summary: str = Field(..., description="Summary of income dynamics analysis")
    base_value: Optional[float] = Field(None, description="Base prediction value", example=80000.0)
    income_features: List[ShapFeature] = Field(..., description="SHAP values for income-related features")
    income_values: dict = Field(default_factory=dict, description="Current income values by feature")
    trends: List[IncomeTrend] = Field(default_factory=list, description="Income trends over time periods")
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Наибольшее влияние на предсказание дохода оказывает dp_ils_avg_salary_1y (увеличивает предсказание на 5000 руб.). Динамика дохода: Зарплата выросла на 5.2%",
                "base_value": 80000.0,
                "income_features": [
                    {
                        "feature_name": "dp_ils_avg_salary_1y",
                        "value": 85000.0,
                        "shap_value": 5000.0,
                        "direction": "positive",
                        "description": "Средняя зарплата за 1 год"
                    }
                ],
                "income_values": {
                    "dp_ils_avg_salary_1y": 85000.0,
                    "dp_ils_avg_salary_2y": 80000.0
                },
                "trends": [
                    {
                        "period": "1 год vs 2 года",
                        "change_percent": 6.25,
                        "description": "Зарплата выросла на 6.25%"
                    }
                ]
            }
        }


# Legacy schemas for backward compatibility
class PredictionRequest(BaseModel):
    """Legacy prediction request schema"""
    pass


class PredictionResponse(BaseModel):
    """Legacy prediction response schema"""
    pass


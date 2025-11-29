from pydantic import BaseModel, Field
from typing import List


class Client(BaseModel):
    """Client information schema"""
    
    id: int = Field(..., description="Unique client identifier", example=1)
    full_name: str = Field(..., description="Client's full name", example="Иван Иванов")
    age: int = Field(..., description="Client's age", example=35, ge=0, le=120)
    city: str = Field(..., description="Client's city of residence", example="Москва")
    segment: str = Field(..., description="Client segment classification", example="VIP")
    products: List[str] = Field(..., description="List of products the client currently has", example=["credit_card", "deposit"])
    risk_score: float = Field(..., description="Client risk score", example=0.15, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "full_name": "Иван Иванов",
                "age": 35,
                "city": "Москва",
                "segment": "VIP",
                "products": ["credit_card", "deposit"],
                "risk_score": 0.15
            }
        }


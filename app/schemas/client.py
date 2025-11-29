from pydantic import BaseModel, Field
from typing import List, Optional


class Client(BaseModel):
    """Client information schema - matches frontend expectations"""
    
    id: int = Field(..., description="Unique client identifier", example=1)
    full_name: str = Field(..., description="Client's full name", example="Клиент #12345")
    age: Optional[int] = Field(None, description="Client's age", example=35, ge=0, le=120)
    city: Optional[str] = Field(None, description="Client's city of residence", example="Москва")
    segment: Optional[str] = Field(None, description="Client segment based on income category", example="500k_to_1M")
    products: List[str] = Field(default_factory=list, description="List of client products")
    risk_score: float = Field(default=0.0, description="Risk score (0-1)", ge=0.0, le=1.0)
    
    # Additional fields from DB
    adminarea: Optional[str] = Field(None, description="Client's administrative area (region)", example="Московская область")
    gender: Optional[str] = Field(None, description="Client's gender", example="Мужской")
    incomeValue: Optional[float] = Field(None, description="Current income value", example=85000.0)
    incomeValueCategory: Optional[str] = Field(None, description="Income category", example="500k_to_1M")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "full_name": "Клиент #1",
                "age": 35,
                "city": "Москва",
                "adminarea": "Московская область",
                "gender": "Мужской",
                "incomeValue": 85000.0,
                "incomeValueCategory": "500k_to_1M",
                "segment": "500k_to_1M",
                "products": [],
                "risk_score": 0.5
            }
        }


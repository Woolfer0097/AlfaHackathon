from pydantic import BaseModel, Field
from typing import Optional, Literal


class Recommendation(BaseModel):
    """Product recommendation schema"""
    
    id: int = Field(..., description="Unique recommendation identifier", example=1)
    product_name: str = Field(..., description="Name of the recommended product", example="Премиум кредитная карта")
    product_type: Literal["credit", "credit_card", "deposit", "insurance"] = Field(
        ..., 
        description="Type of product being recommended",
        example="credit_card"
    )
    limit: Optional[float] = Field(None, description="Credit limit or deposit amount", example=500000.0)
    rate: Optional[float] = Field(None, description="Interest rate (if applicable)", example=12.5)
    reason: str = Field(..., description="Reason for the recommendation", example="Based on income prediction and risk profile")
    description: Optional[str] = Field(None, description="Detailed product description", example="Premium credit card with cashback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_name": "Премиум кредитная карта",
                "product_type": "credit_card",
                "limit": 500000.0,
                "rate": 12.5,
                "reason": "Based on income prediction and risk profile",
                "description": "Premium credit card with cashback"
            }
        }


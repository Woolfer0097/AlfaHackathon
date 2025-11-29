from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List
from sqlalchemy.orm import Session
from app.schemas.recommendations import Recommendation
from app.core.logging import get_logger
from app.core.database import get_db
from app.services.client_service import ClientService
from app.services.ml_service import get_ml_service

router = APIRouter()
logger = get_logger(__name__)


# Product recommendations by segment
SEGMENT_PRODUCTS = {
    "high_income": [
        {
            "product_name": "Премиум кредитная карта",
            "product_type": "credit_card",
            "limit": 1000000.0,
            "rate": 12.5,
            "reason": "Высокий прогнозируемый доход позволяет рекомендовать премиум продукты",
            "description": "Премиум кредитная карта с кэшбэком 5% и льготным периодом"
        },
        {
            "product_name": "Инвестиционный депозит",
            "product_type": "deposit",
            "rate": 8.5,
            "reason": "Высокий доход позволяет рекомендовать инвестиционные продукты",
            "description": "Депозит с повышенной процентной ставкой для долгосрочных вложений"
        },
        {
            "product_name": "Премиум кредит",
            "product_type": "credit",
            "limit": 5000000.0,
            "rate": 10.5,
            "reason": "Премиум сегмент и высокий прогнозируемый доход",
            "description": "Кредит на крупные покупки с льготной процентной ставкой"
        },
    ],
    "medium_income": [
        {
            "product_name": "Стандартная кредитная карта",
            "product_type": "credit_card",
            "limit": 500000.0,
            "rate": 18.0,
            "reason": "Подходит для клиента со средним уровнем дохода",
            "description": "Кредитная карта с базовыми условиями"
        },
        {
            "product_name": "Накопительный депозит",
            "product_type": "deposit",
            "rate": 7.0,
            "reason": "Рекомендуется для накопления средств",
            "description": "Депозит с возможностью пополнения"
        },
    ],
    "low_income": [
        {
            "product_name": "Базовая кредитная карта",
            "product_type": "credit_card",
            "limit": 200000.0,
            "rate": 24.0,
            "reason": "Базовый продукт для клиентов с низким доходом",
            "description": "Кредитная карта с базовыми условиями"
        },
    ],
}


def determine_segment(client_data: dict, predicted_income: float) -> str:
    """Determine client segment based on predicted income and features"""
    # Check income category
    income_category = client_data.get("incomeValueCategory", "")
    
    # Check label shares
    label_below_50k = client_data.get("label_Below_50k_share_r1", 0)
    label_500k_to_1m = client_data.get("label_500k_to_1M_share_r1", 0)
    label_above_1m = client_data.get("label_Above_1M_share_r1", 0)
    
    # Determine segment
    if predicted_income > 200000 or label_above_1m > 0.5:
        return "high_income"
    elif predicted_income > 100000 or label_500k_to_1m > 0.3:
        return "medium_income"
    else:
        return "low_income"


@router.get(
    "/clients/{client_id}/recommendations",
    response_model=List[Recommendation],
    summary="Get product recommendations for client",
    description="Retrieve personalized product recommendations for a specific client based on their profile and predictions",
    response_description="List of recommended products",
    tags=["recommendations"]
)
async def get_recommendations(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0),
    db: Session = Depends(get_db)
) -> List[Recommendation]:
    """
    Get product recommendations for a specific client.
    
    Returns a list of personalized product recommendations based on:
    - Client's income prediction
    - Client's segment and income category
    - ML model analysis
    
    Each recommendation includes:
    - Product name and type
    - Suggested limits and rates (if applicable)
    - Reason for the recommendation
    - Detailed product description
    
    Args:
        client_id: Unique identifier of the client
        db: Database session
        
    Returns:
        List[Recommendation]: List of recommended products
        
    Raises:
        HTTPException: 404 if client with given ID is not found
    """
    logger.debug(f"Fetching recommendations for client ID: {client_id}")
    
    # Get client features
    client_data = ClientService.get_client_features_dict(db, client_id)
    if client_data is None:
        logger.warning(f"Client with ID {client_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Client with ID {client_id} not found"
        )
    
    # Get ML service and predict income
    ml_service = get_ml_service()
    try:
        predicted_income = ml_service.predict(client_data)
    except Exception as e:
        logger.error(f"Error predicting income for recommendations: {e}", exc_info=True)
        predicted_income = client_data.get("incomeValue", 0) or 50000.0
    
    # Determine segment
    segment = determine_segment(client_data, predicted_income)
    
    # Get recommendations for segment
    product_configs = SEGMENT_PRODUCTS.get(segment, SEGMENT_PRODUCTS["low_income"])
    
    # Convert to Recommendation objects
    recommendations = []
    for i, product_config in enumerate(product_configs, start=1):
        recommendations.append(Recommendation(
            id=i,
            product_name=product_config["product_name"],
            product_type=product_config["product_type"],
            limit=product_config.get("limit"),
            rate=product_config.get("rate"),
            reason=product_config["reason"],
            description=product_config.get("description")
        ))
    
    return recommendations


from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.schemas.recommendations import Recommendation
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


# Mock recommendations data - in real implementation, this would be generated based on client_id
MOCK_RECOMMENDATIONS = {
    1: [
        Recommendation(
            id=1,
            product_name="Премиум кредитная карта",
            product_type="credit_card",
            limit=500000.0,
            rate=12.5,
            reason="На основе прогноза дохода и VIP сегмента клиента",
            description="Премиум кредитная карта с кэшбэком 5% и льготным периодом"
        ),
        Recommendation(
            id=2,
            product_name="Инвестиционный депозит",
            product_type="deposit",
            rate=8.5,
            reason="Высокий прогнозируемый доход позволяет рекомендовать инвестиционные продукты",
            description="Депозит с повышенной процентной ставкой для долгосрочных вложений"
        ),
    ],
    2: [
        Recommendation(
            id=3,
            product_name="Стандартная кредитная карта",
            product_type="credit_card",
            limit=200000.0,
            rate=18.0,
            reason="Подходит для клиента стандартного сегмента с текущим уровнем дохода",
            description="Кредитная карта с базовыми условиями"
        ),
    ],
    3: [
        Recommendation(
            id=4,
            product_name="Премиум кредит",
            product_type="credit",
            limit=2000000.0,
            rate=10.5,
            reason="Премиум сегмент и высокий прогнозируемый доход",
            description="Кредит на крупные покупки с льготной процентной ставкой"
        ),
        Recommendation(
            id=5,
            product_name="Страхование жизни",
            product_type="insurance",
            reason="Рекомендуется для клиентов премиум сегмента",
            description="Комплексная страховка жизни и здоровья"
        ),
    ],
}


@router.get(
    "/clients/{client_id}/recommendations",
    response_model=List[Recommendation],
    summary="Get product recommendations for client",
    description="Retrieve personalized product recommendations for a specific client based on their profile and predictions",
    response_description="List of recommended products",
    tags=["recommendations"]
)
async def get_recommendations(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0)
) -> List[Recommendation]:
    """
    Get product recommendations for a specific client.
    
    Returns a list of personalized product recommendations based on:
    - Client's income prediction
    - Client's segment and risk profile
    - Current products held by the client
    - ML model analysis
    
    Each recommendation includes:
    - Product name and type
    - Suggested limits and rates (if applicable)
    - Reason for the recommendation
    - Detailed product description
    
    Args:
        client_id: Unique identifier of the client
        
    Returns:
        List[Recommendation]: List of recommended products
        
    Raises:
        HTTPException: 404 if recommendations not found for the client
    """
    logger.debug(f"Fetching recommendations for client ID: {client_id}")
    
    recommendations = MOCK_RECOMMENDATIONS.get(client_id, [])
    
    if not recommendations:
        logger.warning(f"Recommendations not found for client ID {client_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Recommendations not found for client with ID {client_id}"
        )
    
    return recommendations


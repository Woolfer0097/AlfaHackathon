from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List
from sqlalchemy.orm import Session
from app.schemas.recommendations import Recommendation
from app.core.logging import get_logger
from app.core.database import get_db
from app.services.client_service import ClientService
from app.services.ml_service import get_ml_service
from app.services.risk_service import calculate_risk_score

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
    # Check income category first (more reliable than predicted_income alone)
    income_category = client_data.get("incomeValueCategory", "")
    income_value = client_data.get("incomeValue")
    
    # Check label shares - handle None values safely
    label_below_50k = client_data.get("label_Below_50k_share_r1") or 0
    label_500k_to_1m = client_data.get("label_500k_to_1M_share_r1") or 0
    label_above_1m = client_data.get("label_Above_1M_share_r1") or 0
    
    # Ensure values are numeric
    if not isinstance(label_below_50k, (int, float)):
        label_below_50k = 0
    if not isinstance(label_500k_to_1m, (int, float)):
        label_500k_to_1m = 0
    if not isinstance(label_above_1m, (int, float)):
        label_above_1m = 0
    
    # Use income category if available (more accurate)
    if income_category:
        category_str = str(income_category).lower()
        if "above_1m" in category_str or "1m" in category_str or "above" in category_str:
            return "high_income"
        elif "500k" in category_str or "500_1m" in category_str or "500k_to_1m" in category_str:
            return "high_income"
        elif "200_500" in category_str or "200k_to_500k" in category_str:
            return "high_income"
        elif "100_200" in category_str or "100k_to_200k" in category_str:
            return "medium_income"
        elif "50_100" in category_str or "50k_to_100k" in category_str:
            return "medium_income"  # "Ниже среднего" -> medium_income для рекомендаций
    
    # Fallback to predicted_income and labels
    # Ensure predicted_income is numeric
    if predicted_income is None or not isinstance(predicted_income, (int, float)):
        predicted_income = income_value if income_value and isinstance(income_value, (int, float)) else 50000.0
    
    if predicted_income > 200000 or label_above_1m > 0.5:
        return "high_income"
    elif predicted_income > 100000 or label_500k_to_1m > 0.3:
        return "medium_income"
    elif predicted_income > 50000 or (income_value and isinstance(income_value, (int, float)) and income_value > 50000):
        # Income 50-100k should be medium_income, not low_income
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
    
    # Determine segment based on income
    segment = determine_segment(client_data, predicted_income)
    
    # Calculate risk score
    risk_score = calculate_risk_score(client_data)
    
    logger.debug(f"Client {client_id}: predicted_income={predicted_income:.2f}, segment={segment}, risk_score={risk_score:.3f}")
    
    # Get base recommendations for segment
    base_product_configs = SEGMENT_PRODUCTS.get(segment, SEGMENT_PRODUCTS["low_income"])
    logger.debug(f"Base products for segment {segment}: {len(base_product_configs)} products")
    
    # Adjust recommendations based on risk score
    # Low risk clients (green) should get more products, even with lower income
    # High risk clients should get fewer or more conservative products
    product_configs = []
    
    if risk_score < 0.4:  # Low risk (green) - offer more products
        # Low risk clients get products from their segment + products from next segment up
        product_configs = list(base_product_configs)
        logger.debug(f"Low risk: starting with {len(product_configs)} products from segment {segment}")
        
        # Add products from higher segment if available, but filter by income appropriateness
        if segment == "low_income":
            # Low risk + low income -> offer medium income products too
            medium_products = SEGMENT_PRODUCTS.get("medium_income", [])
            product_configs.extend(medium_products)
            logger.debug(f"Added {len(medium_products)} products from medium_income segment")
        elif segment == "medium_income":
            # Low risk + medium income -> offer high income products, but only appropriate ones
            # Don't offer premium credit products with very high limits to medium income clients
            high_products = SEGMENT_PRODUCTS.get("high_income", [])
            # Filter: only include deposits and products with reasonable limits
            # Max credit limit should be ~3x annual income for medium income clients
            max_reasonable_limit = predicted_income * 3 if predicted_income else 300000
            
            filtered_high_products = []
            for product in high_products:
                # Always include deposits (no limit concerns)
                if product.get("product_type") == "deposit":
                    filtered_high_products.append(product)
                # For credit products, check if limit is reasonable
                elif product.get("limit") and product.get("limit") <= max_reasonable_limit:
                    filtered_high_products.append(product)
                # Skip premium credit products with very high limits
                else:
                    logger.debug(f"Skipping {product.get('product_name')} - limit {product.get('limit')} too high for income {predicted_income:.2f}")
            
            product_configs.extend(filtered_high_products)
            logger.debug(f"Added {len(filtered_high_products)} filtered products from high_income segment (filtered from {len(high_products)})")
        # High income already has all products
        
        # Add conservative products for low risk clients
        product_configs.append({
            "product_name": "Накопительный счет",
            "product_type": "deposit",
            "rate": 6.5,
            "reason": "Низкий риск-скор позволяет рекомендовать накопительные продукты",
            "description": "Накопительный счет с возможностью пополнения и снятия"
        })
        logger.debug(f"Added накопительный счет, total products: {len(product_configs)}")
        
    elif risk_score < 0.7:  # Medium risk (yellow) - standard recommendations
        product_configs = list(base_product_configs)
        logger.debug(f"Medium risk: {len(product_configs)} products from segment {segment}")
        
    else:  # High risk (red) - conservative recommendations only
        # High risk clients get only basic products, even if they have high income
        if segment == "high_income":
            # High risk + high income -> offer only medium income products
            product_configs = SEGMENT_PRODUCTS.get("medium_income", [])
            logger.debug(f"High risk + high income: {len(product_configs)} products from medium_income")
        elif segment == "medium_income":
            # High risk + medium income -> offer only low income products
            product_configs = SEGMENT_PRODUCTS.get("low_income", [])
            logger.debug(f"High risk + medium income: {len(product_configs)} products from low_income")
        else:
            # High risk + low income -> offer only basic products
            product_configs = [
                {
                    "product_name": "Базовая кредитная карта",
                    "product_type": "credit_card",
                    "limit": 100000.0,  # Lower limit for high risk
                    "rate": 28.0,  # Higher rate for high risk
                    "reason": "Высокий риск-скор требует консервативных условий",
                    "description": "Базовая кредитная карта с ограниченным лимитом"
                }
            ]
            logger.debug(f"High risk + low income: 1 basic product")
    
    # Ensure we always have at least one recommendation
    if not product_configs:
        logger.warning(f"No products generated for client {client_id}, using default low_income product")
        product_configs = SEGMENT_PRODUCTS.get("low_income", [])
    
    # Adjust credit limits based on actual income to ensure they're reasonable
    # Credit limit should not exceed 3-4x annual income for safety
    income_value = client_data.get("incomeValue") or predicted_income
    max_reasonable_credit_limit = income_value * 4 if income_value else None
    
    # Convert to Recommendation objects and adjust limits if needed
    recommendations = []
    for i, product_config in enumerate(product_configs, start=1):
        # Adjust credit limit if it's too high for client's income
        credit_limit = product_config.get("limit")
        if credit_limit and max_reasonable_credit_limit:
            # For credit products, cap the limit at reasonable level
            if product_config.get("product_type") in ["credit_card", "credit"]:
                if credit_limit > max_reasonable_credit_limit:
                    logger.debug(f"Adjusting limit for {product_config.get('product_name')} from {credit_limit} to {max_reasonable_credit_limit} (based on income {income_value:.2f})")
                    credit_limit = max_reasonable_credit_limit
                    # Update reason to reflect adjusted limit
                    original_reason = product_config.get("reason", "")
                    if "лимит" not in original_reason.lower():
                        product_config = product_config.copy()
                        product_config["reason"] = f"{original_reason} (лимит скорректирован с учетом дохода)"
        
        recommendations.append(Recommendation(
            id=i,
            product_name=product_config["product_name"],
            product_type=product_config["product_type"],
            limit=credit_limit,
            rate=product_config.get("rate"),
            reason=product_config.get("reason", product_config.get("reason", "")),
            description=product_config.get("description")
        ))
    
    logger.info(f"Generated {len(recommendations)} recommendations for client {client_id}: segment={segment}, risk_score={risk_score:.3f}, predicted_income={predicted_income:.2f}")
    
    return recommendations


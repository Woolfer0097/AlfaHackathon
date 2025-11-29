from fastapi import APIRouter, HTTPException, Path
from app.schemas.prediction import IncomePrediction, ShapResponse, ShapFeature
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


# Mock prediction data - in real implementation, this would be generated based on client_id
MOCK_INCOME_PREDICTIONS = {
    1: IncomePrediction(
        predicted_income=85000.0,
        lower_bound=75000.0,
        upper_bound=95000.0,
        base_income=80000.0
    ),
    2: IncomePrediction(
        predicted_income=65000.0,
        lower_bound=55000.0,
        upper_bound=75000.0,
        base_income=60000.0
    ),
    3: IncomePrediction(
        predicted_income=95000.0,
        lower_bound=85000.0,
        upper_bound=105000.0,
        base_income=90000.0
    ),
}

MOCK_SHAP_RESPONSES = {
    1: ShapResponse(
        text_explanation="Модель предсказывает более высокий доход на основе возраста клиента (35 лет), VIP сегмента и наличия нескольких продуктов. Основные факторы: положительное влияние возраста и сегмента, отрицательное влияние рискового скора.",
        features=[
            ShapFeature(
                feature_name="age",
                value=35,
                shap_value=1250.5,
                direction="positive",
                description="Возраст клиента в годах"
            ),
            ShapFeature(
                feature_name="segment",
                value="VIP",
                shap_value=3200.0,
                direction="positive",
                description="Сегмент клиента"
            ),
            ShapFeature(
                feature_name="risk_score",
                value=0.15,
                shap_value=-850.0,
                direction="negative",
                description="Рисковый скор клиента"
            ),
            ShapFeature(
                feature_name="products_count",
                value=2,
                shap_value=1100.0,
                direction="positive",
                description="Количество продуктов у клиента"
            ),
        ],
        base_value=80000.0
    ),
    2: ShapResponse(
        text_explanation="Модель предсказывает средний доход. Основные факторы: положительное влияние возраста, отрицательное влияние стандартного сегмента и более высокого рискового скора.",
        features=[
            ShapFeature(
                feature_name="age",
                value=28,
                shap_value=800.0,
                direction="positive",
                description="Возраст клиента в годах"
            ),
            ShapFeature(
                feature_name="segment",
                value="Standard",
                shap_value=-1500.0,
                direction="negative",
                description="Сегмент клиента"
            ),
            ShapFeature(
                feature_name="risk_score",
                value=0.35,
                shap_value=-2200.0,
                direction="negative",
                description="Рисковый скор клиента"
            ),
        ],
        base_value=60000.0
    ),
    3: ShapResponse(
        text_explanation="Модель предсказывает высокий доход на основе премиум сегмента, возраста и наличия нескольких продуктов.",
        features=[
            ShapFeature(
                feature_name="age",
                value=42,
                shap_value=1800.0,
                direction="positive",
                description="Возраст клиента в годах"
            ),
            ShapFeature(
                feature_name="segment",
                value="Premium",
                shap_value=2800.0,
                direction="positive",
                description="Сегмент клиента"
            ),
            ShapFeature(
                feature_name="risk_score",
                value=0.22,
                shap_value=-1200.0,
                direction="negative",
                description="Рисковый скор клиента"
            ),
            ShapFeature(
                feature_name="products_count",
                value=2,
                shap_value=1300.0,
                direction="positive",
                description="Количество продуктов у клиента"
            ),
        ],
        base_value=90000.0
    ),
}


@router.get(
    "/clients/{client_id}/income",
    response_model=IncomePrediction,
    summary="Get income prediction for client",
    description="Retrieve income prediction for a specific client including predicted value and confidence intervals",
    response_description="Income prediction with bounds",
    tags=["predictions"]
)
async def get_client_income(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0)
) -> IncomePrediction:
    """
    Get income prediction for a specific client.
    
    Returns the ML model's prediction of the client's income including:
    - Predicted income value
    - Lower and upper bounds of the confidence interval
    - Base income value (if available)
    
    Args:
        client_id: Unique identifier of the client
        
    Returns:
        IncomePrediction: Income prediction with confidence bounds
        
    Raises:
        HTTPException: 404 if client with given ID is not found
    """
    logger.debug(f"Fetching income prediction for client ID: {client_id}")
    
    prediction = MOCK_INCOME_PREDICTIONS.get(client_id)
    
    if not prediction:
        logger.warning(f"Income prediction not found for client ID {client_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Income prediction not found for client with ID {client_id}"
        )
    
    return prediction


@router.get(
    "/clients/{client_id}/shap",
    response_model=ShapResponse,
    summary="Get SHAP explanation for client",
    description="Retrieve SHAP (SHapley Additive exPlanations) values explaining the income prediction for a specific client",
    response_description="SHAP explanation with feature contributions",
    tags=["predictions"]
)
async def get_client_shap(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0)
) -> ShapResponse:
    """
    Get SHAP explanation for a specific client's income prediction.
    
    Returns a detailed explanation of how each feature contributed to the
    income prediction, including:
    - Human-readable text explanation
    - Feature-by-feature SHAP values showing positive/negative contributions
    - Base prediction value
    
    SHAP values help explain which features increased or decreased the
    predicted income and by how much.
    
    Args:
        client_id: Unique identifier of the client
        
    Returns:
        ShapResponse: SHAP explanation with feature contributions
        
    Raises:
        HTTPException: 404 if SHAP explanation not found for the client
    """
    logger.debug(f"Fetching SHAP explanation for client ID: {client_id}")
    
    shap_response = MOCK_SHAP_RESPONSES.get(client_id)
    
    if not shap_response:
        logger.warning(f"SHAP explanation not found for client ID {client_id}")
        raise HTTPException(
            status_code=404,
            detail=f"SHAP explanation not found for client with ID {client_id}"
        )
    
    return shap_response


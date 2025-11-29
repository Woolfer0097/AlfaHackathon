from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
from app.schemas.prediction import IncomePrediction, ShapResponse, ShapFeature
from app.core.logging import get_logger
from app.core.database import get_db
from app.services.client_service import ClientService
from app.services.ml_service import get_ml_service
from app.models.prediction_logs import PredictionLog

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/clients/{client_id}/income",
    response_model=IncomePrediction,
    summary="Get income prediction for client",
    description="Retrieve income prediction for a specific client including predicted value and confidence intervals",
    response_description="Income prediction with bounds",
    tags=["predictions"]
)
async def get_client_income(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0),
    db: Session = Depends(get_db)
) -> IncomePrediction:
    """
    Get income prediction for a specific client.
    
    Returns the ML model's prediction of the client's income including:
    - Predicted income value
    - Lower and upper bounds of the confidence interval
    - Base income value (if available)
    
    Args:
        client_id: Unique identifier of the client
        db: Database session
        
    Returns:
        IncomePrediction: Income prediction with confidence bounds
        
    Raises:
        HTTPException: 404 if client with given ID is not found
    """
    logger.debug(f"Fetching income prediction for client ID: {client_id}")
    
    # Get client features
    client_data = ClientService.get_client_features_dict(db, client_id)
    if client_data is None:
        logger.warning(f"Client with ID {client_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Client with ID {client_id} not found"
        )
    
    # Get ML service
    ml_service = get_ml_service()
    
    # Predict income
    try:
        predicted_income = ml_service.predict(client_data)
        
        # Get actual income value if available (for metrics calculation)
        actual_income = client_data.get("incomeValue")
        prediction_error = None
        if actual_income is not None and isinstance(actual_income, (int, float)):
            # Calculate absolute error for metrics
            prediction_error = abs(predicted_income - float(actual_income))
        
        # Calculate confidence interval (simple approach: ±10%)
        lower_bound = predicted_income * 0.9
        upper_bound = predicted_income * 1.1
        
        # Log prediction with actual income and error if available
        prediction_log = PredictionLog(
            client_id=client_id,
            predicted_income=predicted_income,
            actual_income=float(actual_income) if actual_income is not None else None,
            prediction_error=prediction_error,
            prediction_time=datetime.utcnow()
        )
        db.add(prediction_log)
        db.commit()
        
        return IncomePrediction(
            predicted_income=predicted_income,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            base_income=float(actual_income) if actual_income is not None else None
        )
    except Exception as e:
        logger.error(f"Error predicting income for client {client_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating prediction: {str(e)}"
        )


@router.get(
    "/clients/{client_id}/shap",
    response_model=ShapResponse,
    summary="Get SHAP explanation for client",
    description="Retrieve SHAP (SHapley Additive exPlanations) values explaining the income prediction for a specific client",
    response_description="SHAP explanation with feature contributions",
    tags=["predictions"]
)
async def get_client_shap(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0),
    db: Session = Depends(get_db)
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
        db: Database session
        
    Returns:
        ShapResponse: SHAP explanation with feature contributions
        
    Raises:
        HTTPException: 404 if client with given ID is not found
    """
    logger.debug(f"Fetching SHAP explanation for client ID: {client_id}")
    
    # Get client features
    client_data = ClientService.get_client_features_dict(db, client_id)
    if client_data is None:
        logger.warning(f"Client with ID {client_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Client with ID {client_id} not found"
        )
    
    # Get ML service
    ml_service = get_ml_service()
    
    # Get SHAP values
    try:
        shap_result = ml_service.get_shap_values(client_data)
        
        # Sort features by absolute SHAP value (most important first)
        features_sorted = sorted(
            shap_result["features"],
            key=lambda x: abs(x["shap_value"]),
            reverse=True
        )
        
        # Take top 20 features for explanation
        top_features = features_sorted[:20]
        
        # Generate text explanation
        positive_features = [f for f in top_features if f["shap_value"] > 0]
        negative_features = [f for f in top_features if f["shap_value"] < 0]
        
        explanation_parts = []
        if positive_features:
            top_positive = positive_features[0]
            explanation_parts.append(
                f"Положительное влияние: {top_positive['feature_name']} "
                f"(вклад: {top_positive['shap_value']:.2f})"
            )
        if negative_features:
            top_negative = negative_features[0]
            explanation_parts.append(
                f"Отрицательное влияние: {top_negative['feature_name']} "
                f"(вклад: {top_negative['shap_value']:.2f})"
            )
        
        text_explanation = ". ".join(explanation_parts) if explanation_parts else "SHAP значения рассчитаны."
        
        # Convert to ShapFeature objects
        shap_features = []
        for f in top_features:
            feature_value = f["feature_value"]
            feature_name = f["feature_name"]
            
            # Handle None/NaN values - convert to appropriate type for schema
            if feature_value is None:
                # Use empty string for categorical features, 0 for numeric
                if feature_name in ml_service.cat_features:
                    feature_value = ""
                else:
                    feature_value = 0.0
            elif isinstance(feature_value, float) and np.isnan(feature_value):
                # Handle NaN values
                if feature_name in ml_service.cat_features:
                    feature_value = ""
                else:
                    feature_value = 0.0
            elif isinstance(feature_value, str) and feature_value.lower() in ['nan', 'none', '']:
                # Handle string "nan" values
                if feature_name in ml_service.cat_features:
                    feature_value = ""
                else:
                    feature_value = 0.0
            else:
                # Ensure correct type: string for categorical, number for numeric
                if feature_name in ml_service.cat_features:
                    feature_value = str(feature_value) if not isinstance(feature_value, str) else feature_value
                else:
                    # Try to convert to float, fallback to 0.0
                    try:
                        feature_value = float(feature_value) if not isinstance(feature_value, (int, float)) else feature_value
                    except (ValueError, TypeError):
                        feature_value = 0.0
            
            shap_features.append(
                ShapFeature(
                    feature_name=feature_name,
                    value=feature_value,
                    shap_value=f["shap_value"],
                    direction=f["direction"],
                    description=None
                )
            )
        
        return ShapResponse(
            text_explanation=text_explanation,
            features=shap_features,
            base_value=shap_result["base_value"]
        )
    except Exception as e:
        logger.error(f"Error calculating SHAP for client {client_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SHAP explanation: {str(e)}"
        )


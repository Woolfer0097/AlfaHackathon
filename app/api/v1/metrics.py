import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.metrics import ModelMetrics, Experiment, SegmentError
from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import get_db
from app.models.prediction_logs import PredictionLog

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/metrics",
    response_model=ModelMetrics,
    summary="Get model metrics",
    description="Retrieve performance metrics for the ML model including validation errors, training statistics, and segment-specific metrics",
    response_description="Model metrics object with performance data",
    tags=["metrics"]
)
async def get_model_metrics(db: Session = Depends(get_db)) -> ModelMetrics:
    """
    Get model performance metrics.
    
    Returns comprehensive metrics about the ML model's performance including:
    - Overall validation error (WMAE)
    - Training and validation dataset sizes
    - Total number of predictions made
    - Historical experiment results
    - Segment-specific error metrics
    
    Metrics are loaded from metrics.json file prepared by ML team.
    
    Args:
        db: Database session (for counting predictions)
    
    Returns:
        ModelMetrics: Complete model performance metrics
    """
    logger.debug("Fetching model metrics")
    
    # Load metrics from JSON file
    metrics_path = Path(settings.metrics_path)
    
    if not metrics_path.exists():
        logger.warning(f"Metrics file not found at {metrics_path}, returning default metrics")
        # Return default metrics if file doesn't exist
        predictions_count = db.query(PredictionLog).count()
        return ModelMetrics(
            wmae_validation=0.0,
            training_records=0,
            validation_records=0,
            predictions_count=predictions_count,
            experiments=[],
            segment_errors=[]
        )
    
    try:
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        
        # Get predictions count from database
        predictions_count = db.query(PredictionLog).count()
        
        # Convert JSON data to ModelMetrics schema
        experiments = [
            Experiment(
                name=exp.get("name", ""),
                wmae=exp.get("wmae", 0.0),
                date=exp.get("date")
            )
            for exp in metrics_data.get("experiments", [])
        ]
        
        segment_errors = [
            SegmentError(
                segment=seg.get("segment", ""),
                wmae=seg.get("wmae", 0.0)
            )
            for seg in metrics_data.get("segment_errors", [])
        ]
        
        return ModelMetrics(
            wmae_validation=metrics_data.get("wmae_validation", 0.0),
            training_records=metrics_data.get("training_records", 0),
            validation_records=metrics_data.get("validation_records", 0),
            predictions_count=predictions_count,
            experiments=experiments,
            segment_errors=segment_errors
        )
    except Exception as e:
        logger.error(f"Error loading metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error loading metrics: {str(e)}"
        )


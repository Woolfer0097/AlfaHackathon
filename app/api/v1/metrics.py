import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.metrics import ModelMetrics, Experiment, SegmentError, TrainingRun
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
            segment_errors=[],
            training_runs=[]
        )
    
    try:
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        
        # Get predictions count from database
        predictions_count = db.query(PredictionLog).count()
        
        # Calculate real-time metrics from predictions with actual values
        predictions_with_actual = db.query(PredictionLog).filter(
            PredictionLog.actual_income.isnot(None)
        ).all()
        
        # Calculate WMAE (Weighted Mean Absolute Error) from real predictions
        # if we have actual values, otherwise use static metrics
        real_time_wmae = None
        if predictions_with_actual:
            total_error = sum(p.prediction_error for p in predictions_with_actual if p.prediction_error is not None)
            total_actual = sum(p.actual_income for p in predictions_with_actual if p.actual_income is not None)
            if total_actual > 0:
                # WMAE = sum(|predicted - actual|) / sum(actual)
                real_time_wmae = total_error / total_actual
        
        # Use real-time WMAE if available, otherwise fall back to static validation WMAE
        wmae_to_use = real_time_wmae if real_time_wmae is not None else metrics_data.get("wmae_validation", 0.0)
        
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
        
        # Load training metrics from training_metrics.json
        training_runs = []
        training_metrics_path = Path(settings.training_metrics_path)
        if training_metrics_path.exists():
            try:
                with open(training_metrics_path, 'r', encoding='utf-8') as f:
                    training_metrics_data = json.load(f)
                
                # Handle both array and single object formats
                if isinstance(training_metrics_data, list):
                    training_runs = [
                        TrainingRun(
                            model_version=run.get("model_version", ""),
                            trained_at=run.get("trained_at", ""),
                            train_samples=run.get("train_samples", 0),
                            valid_samples=run.get("valid_samples", 0),
                            rmse=run.get("rmse", 0.0),
                            mae=run.get("mae", 0.0),
                            r2=run.get("r2", 0.0)
                        )
                        for run in training_metrics_data
                    ]
                elif isinstance(training_metrics_data, dict):
                    # Single training run
                    training_runs = [TrainingRun(
                        model_version=training_metrics_data.get("model_version", ""),
                        trained_at=training_metrics_data.get("trained_at", ""),
                        train_samples=training_metrics_data.get("train_samples", 0),
                        valid_samples=training_metrics_data.get("valid_samples", 0),
                        rmse=training_metrics_data.get("rmse", 0.0),
                        mae=training_metrics_data.get("mae", 0.0),
                        r2=training_metrics_data.get("r2", 0.0)
                    )]
            except Exception as e:
                logger.warning(f"Error loading training metrics: {e}", exc_info=True)
        
        return ModelMetrics(
            wmae_validation=wmae_to_use,  # Use real-time WMAE if available
            training_records=metrics_data.get("training_records", 0),
            validation_records=metrics_data.get("validation_records", 0),
            predictions_count=predictions_count,
            experiments=experiments,
            segment_errors=segment_errors,
            training_runs=training_runs
        )
    except Exception as e:
        logger.error(f"Error loading metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error loading metrics: {str(e)}"
        )


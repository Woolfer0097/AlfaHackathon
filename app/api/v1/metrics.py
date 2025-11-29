from fastapi import APIRouter
from app.schemas.metrics import ModelMetrics, Experiment, SegmentError
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


# Mock metrics data
MOCK_METRICS = ModelMetrics(
    wmae_validation=0.125,
    training_records=10000,
    validation_records=2000,
    predictions_count=5000,
    experiments=[
        Experiment(
            name="baseline_model_v1",
            wmae=0.125,
            date="2024-01-15T10:30:00Z"
        ),
        Experiment(
            name="improved_model_v2",
            wmae=0.112,
            date="2024-02-01T14:20:00Z"
        ),
        Experiment(
            name="ensemble_model_v3",
            wmae=0.108,
            date="2024-02-15T09:15:00Z"
        ),
    ],
    segment_errors=[
        SegmentError(segment="VIP", wmae=0.095),
        SegmentError(segment="Premium", wmae=0.110),
        SegmentError(segment="Standard", wmae=0.140),
        SegmentError(segment="Basic", wmae=0.165),
    ]
)


@router.get(
    "/metrics",
    response_model=ModelMetrics,
    summary="Get model metrics",
    description="Retrieve performance metrics for the ML model including validation errors, training statistics, and segment-specific metrics",
    response_description="Model metrics object with performance data",
    tags=["metrics"]
)
async def get_model_metrics() -> ModelMetrics:
    """
    Get model performance metrics.
    
    Returns comprehensive metrics about the ML model's performance including:
    - Overall validation error (WMAE)
    - Training and validation dataset sizes
    - Total number of predictions made
    - Historical experiment results
    - Segment-specific error metrics
    
    Returns:
        ModelMetrics: Complete model performance metrics
    """
    logger.debug("Fetching model metrics")
    return MOCK_METRICS


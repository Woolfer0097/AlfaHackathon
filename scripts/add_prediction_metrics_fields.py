#!/usr/bin/env python3
"""
Script to add actual_income and prediction_error fields to prediction_logs table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine
from app.core.logging import get_logger

logger = get_logger(__name__)


def add_prediction_metrics_fields():
    """Add actual_income and prediction_error columns to prediction_logs table"""
    logger.info("Adding actual_income and prediction_error fields to prediction_logs table...")
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'prediction_logs' 
                AND column_name IN ('actual_income', 'prediction_error')
            """)
            result = conn.execute(check_query)
            existing_columns = {row[0] for row in result}
            
            # Add actual_income if it doesn't exist
            if 'actual_income' not in existing_columns:
                logger.info("Adding actual_income column...")
                conn.execute(text("""
                    ALTER TABLE prediction_logs 
                    ADD COLUMN actual_income DOUBLE PRECISION NULL
                """))
                conn.execute(text("""
                    COMMENT ON COLUMN prediction_logs.actual_income IS 
                    'Actual income value if available for metrics calculation'
                """))
                logger.info("Added actual_income column")
            else:
                logger.info("actual_income column already exists")
            
            # Add prediction_error if it doesn't exist
            if 'prediction_error' not in existing_columns:
                logger.info("Adding prediction_error column...")
                conn.execute(text("""
                    ALTER TABLE prediction_logs 
                    ADD COLUMN prediction_error DOUBLE PRECISION NULL
                """))
                conn.execute(text("""
                    COMMENT ON COLUMN prediction_logs.prediction_error IS 
                    'Absolute error: |predicted - actual| if actual is available'
                """))
                logger.info("Added prediction_error column")
            else:
                logger.info("prediction_error column already exists")
            
            conn.commit()
            logger.info("Successfully updated prediction_logs table")
            
    except Exception as e:
        logger.error(f"Error updating prediction_logs table: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    add_prediction_metrics_fields()


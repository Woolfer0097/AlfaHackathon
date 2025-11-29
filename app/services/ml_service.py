"""
ML Service for CatBoost model inference
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from catboost import CatBoostRegressor, Pool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MLService:
    """Service for ML model operations"""
    
    def __init__(self):
        self.model: Optional[CatBoostRegressor] = None
        self.model_meta: Optional[Dict] = None
        self.feature_cols: List[str] = []
        self.cat_features: List[str] = []
        self.id_col: str = "id"
        self._load_model()
    
    def _load_model(self):
        """Load CatBoost model and metadata"""
        try:
            # Load model metadata
            model_meta_path = Path(settings.model_meta_path)
            if not model_meta_path.exists():
                raise FileNotFoundError(f"Model metadata not found at {model_meta_path}")
            
            with open(model_meta_path, 'r', encoding='utf-8') as f:
                self.model_meta = json.load(f)
            
            self.feature_cols = self.model_meta["feature_cols"]
            self.cat_features = self.model_meta["cat_features"]
            self.id_col = self.model_meta["id_col"]
            
            # Load CatBoost model
            model_path = Path(settings.model_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at {model_path}")
            
            self.model = CatBoostRegressor()
            self.model.load_model(str(model_path))
            
            # Get actual feature names from the model (in the order the model expects)
            # CatBoost models store feature names in the order they were trained
            try:
                model_feature_names = self.model.feature_names_
                if model_feature_names and len(model_feature_names) > 0:
                    # Model has feature names - use them as the source of truth for order
                    logger.info(f"Model has {len(model_feature_names)} features with names")
                    # Use model's feature names and order - this is what the model expects
                    self.feature_cols = list(model_feature_names)
                    logger.info(f"Using feature order from model ({len(self.feature_cols)} features)")
                    
                    # Update categorical features to only include those that are actually in the model
                    self.cat_features = [f for f in self.cat_features if f in self.feature_cols]
                    logger.info(f"Updated categorical features to {len(self.cat_features)} (matching model)")
                else:
                    logger.warning("Model does not have feature names, using metadata order")
            except Exception as e:
                logger.warning(f"Could not get feature names from model: {e}, using metadata order")
            
            logger.info(f"Loaded CatBoost model from {model_path}")
            logger.info(f"Model has {len(self.feature_cols)} features, {len(self.cat_features)} categorical")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            raise
    
    def prepare_features(self, client_data: Dict) -> pd.DataFrame:
        """
        Prepare features for model inference
        
        Args:
            client_data: Dictionary with client features (must include all feature_cols)
            
        Returns:
            DataFrame with features in correct order
        """
        # Create DataFrame with one row
        feature_dict = {}
        for col in self.feature_cols:
            value = client_data.get(col)
            
            # Check if value is None, NaN, or string "nan"/"NaN"
            is_missing = (
                value is None or
                (isinstance(value, float) and np.isnan(value)) or
                (isinstance(value, str) and value.lower() in ['nan', 'none', ''])
            )
            
            if is_missing:
                # For categorical features, CatBoost requires string, not NaN
                if col in self.cat_features:
                    feature_dict[col] = ""  # Empty string for missing categorical values
                else:
                    feature_dict[col] = np.nan
            else:
                # For categorical features, ensure it's a string
                if col in self.cat_features:
                    feature_dict[col] = str(value) if value is not None else ""
                else:
                    feature_dict[col] = value
        
        df = pd.DataFrame([feature_dict])
        
        # Ensure columns are in correct order
        df = df[self.feature_cols]
        
        # Replace any remaining NaN in categorical columns with empty string
        # Also handle string "nan" values
        for col in self.cat_features:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
                # Replace string "nan" with empty string
                df[col] = df[col].replace(['nan', 'NaN', 'None', 'none'], "")
        
        return df
    
    def create_pool(self, df: pd.DataFrame) -> Pool:
        """
        Create CatBoost Pool from DataFrame
        
        Args:
            df: DataFrame with features
            
        Returns:
            CatBoost Pool object
        """
        # Get indices of categorical features
        cat_indices = [df.columns.get_loc(col) for col in self.cat_features if col in df.columns]
        
        pool = Pool(
            data=df[self.feature_cols],
            cat_features=cat_indices
        )
        
        return pool
    
    def predict(self, client_data: Dict) -> float:
        """
        Predict income for a client
        
        Args:
            client_data: Dictionary with client features
            
        Returns:
            Predicted income value
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Prepare features
        df = self.prepare_features(client_data)
        
        # Create pool
        pool = self.create_pool(df)
        
        # Predict
        prediction = self.model.predict(pool)[0]
        
        return float(prediction)
    
    def get_shap_values(self, client_data: Dict) -> Dict:
        """
        Get SHAP values for a client
        
        Args:
            client_data: Dictionary with client features
            
        Returns:
            Dictionary with SHAP values and base value
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Prepare features
        df = self.prepare_features(client_data)
        
        # Create pool
        pool = self.create_pool(df)
        
        # Get SHAP values
        shap_values = self.model.get_feature_importance(pool, type="ShapValues")
        
        # For single prediction, shap_values is 2D array: [[shap_1, ..., shap_N, expected_value]]
        shap_array = shap_values[0]
        expected_value = shap_array[-1]  # Last value is expected/base value
        feature_shap_values = shap_array[:-1]  # All but last are feature contributions
        
        # Create result dictionary
        result = {
            "base_value": float(expected_value),
            "features": []
        }
        
        # Map SHAP values to features
        for i, feature_name in enumerate(self.feature_cols):
            if i < len(feature_shap_values):
                shap_value = float(feature_shap_values[i])
                feature_value = client_data.get(feature_name)
                
                result["features"].append({
                    "feature_name": feature_name,
                    "feature_value": feature_value,
                    "shap_value": shap_value,
                    "direction": "positive" if shap_value >= 0 else "negative"
                })
        
        return result


# Global ML service instance
_ml_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    """Get or create ML service instance"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service


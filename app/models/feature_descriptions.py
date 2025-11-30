"""
Feature descriptions model
Stores human-readable descriptions for ML model features
"""
from sqlalchemy import Column, String, Text
from app.core.database import Base


class FeatureDescription(Base):
    """Model for storing feature descriptions"""
    
    __tablename__ = "feature_descriptions"
    
    feature_name = Column(String, primary_key=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<FeatureDescription(feature_name='{self.feature_name}')>"


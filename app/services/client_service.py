"""
Client Service for database operations
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.client_features import ClientFeatures
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClientService:
    """Service for client data operations"""
    
    @staticmethod
    def get_client_by_id(db: Session, client_id: int) -> Optional[ClientFeatures]:
        """Get client by ID"""
        return db.query(ClientFeatures).filter(ClientFeatures.id == client_id).first()
    
    @staticmethod
    def get_client_features_dict(db: Session, client_id: int) -> Optional[Dict]:
        """
        Get client features as dictionary
        
        Returns:
            Dictionary with all feature columns or None if client not found
        """
        client = ClientService.get_client_by_id(db, client_id)
        if client is None:
            return None
        
        return client.to_dict()
    
    @staticmethod
    def list_clients(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        adminarea: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[ClientFeatures]:
        """
        List clients with pagination and optional filters
        
        Args:
            db: Database session
            limit: Maximum number of results
            offset: Offset for pagination
            adminarea: Filter by adminarea (region)
            city: Filter by city_smart_name
            
        Returns:
            List of ClientFeatures objects
        """
        query = db.query(ClientFeatures)
        
        # Apply filters
        filters = []
        if adminarea:
            filters.append(ClientFeatures.adminarea == adminarea)
        if city:
            filters.append(ClientFeatures.city_smart_name == city)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Apply pagination
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def count_clients(
        db: Session,
        adminarea: Optional[str] = None,
        city: Optional[str] = None
    ) -> int:
        """Count clients with optional filters"""
        query = db.query(ClientFeatures)
        
        filters = []
        if adminarea:
            filters.append(ClientFeatures.adminarea == adminarea)
        if city:
            filters.append(ClientFeatures.city_smart_name == city)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.count()


from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.schemas.client import Client
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


# Mock data for clients
MOCK_CLIENTS = [
    Client(
        id=1,
        full_name="Иван Иванов",
        age=35,
        city="Москва",
        segment="VIP",
        products=["credit_card", "deposit"],
        risk_score=0.15
    ),
    Client(
        id=2,
        full_name="Мария Петрова",
        age=28,
        city="Санкт-Петербург",
        segment="Standard",
        products=["credit"],
        risk_score=0.35
    ),
    Client(
        id=3,
        full_name="Алексей Смирнов",
        age=42,
        city="Новосибирск",
        segment="Premium",
        products=["credit_card", "insurance"],
        risk_score=0.22
    ),
]


@router.get(
    "/clients",
    response_model=List[Client],
    summary="Get all clients",
    description="Retrieve a list of all clients in the system",
    response_description="List of client objects",
    tags=["clients"]
)
async def get_clients() -> List[Client]:
    """
    Get all clients.
    
    Returns a list of all clients with their basic information including
    personal details, segment classification, current products, and risk score.
    
    Returns:
        List[Client]: List of all clients
    """
    logger.debug("Fetching all clients")
    return MOCK_CLIENTS


@router.get(
    "/clients/{client_id}",
    response_model=Client,
    summary="Get client by ID",
    description="Retrieve detailed information about a specific client by their ID",
    response_description="Client object with full details",
    tags=["clients"]
)
async def get_client(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0)
) -> Client:
    """
    Get a specific client by ID.
    
    Retrieves detailed information about a single client including their
    personal information, segment, products, and risk assessment.
    
    Args:
        client_id: Unique identifier of the client
        
    Returns:
        Client: Client object with full details
        
    Raises:
        HTTPException: 404 if client with given ID is not found
    """
    logger.debug(f"Fetching client with ID: {client_id}")
    
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    
    if not client:
        logger.warning(f"Client with ID {client_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Client with ID {client_id} not found"
        )
    
    return client


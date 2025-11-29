from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.client import Client
from app.core.logging import get_logger
from app.core.database import get_db
from app.services.client_service import ClientService

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/clients",
    response_model=List[Client],
    summary="Get all clients",
    description="Retrieve a list of all clients in the system with pagination and optional filters",
    response_description="List of client objects",
    tags=["clients"]
)
async def get_clients(
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    adminarea: Optional[str] = Query(None, description="Filter by administrative area (region)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    search: Optional[str] = Query(None, description="Search query (not yet implemented)"),
    db: Session = Depends(get_db)
) -> List[Client]:
    """
    Get all clients with pagination and optional filters.
    
    Returns a list of clients with their basic information including
    personal details and income information.
    
    Args:
        limit: Maximum number of results (1-1000)
        offset: Offset for pagination
        adminarea: Filter by administrative area (region)
        city: Filter by city name
        db: Database session
    
    Returns:
        List[Client]: List of clients
    """
    logger.debug(f"Fetching clients: limit={limit}, offset={offset}, adminarea={adminarea}, city={city}, search={search}")
    
    clients = ClientService.list_clients(
        db=db,
        limit=limit,
        offset=offset,
        adminarea=adminarea,
        city=city
    )
    
    # Convert to Client schema with frontend-compatible format
    result = []
    for client in clients:
        client_id = client.id
        city = getattr(client, 'city_smart_name', None)
        age = getattr(client, 'age', None)
        gender = getattr(client, 'gender', None)
        income_category_raw = getattr(client, 'incomeValueCategory', None)
        
        # Convert incomeValueCategory to string if it's a number
        if income_category_raw is not None:
            if isinstance(income_category_raw, (int, float)):
                income_category = str(int(income_category_raw)) if income_category_raw == int(income_category_raw) else str(income_category_raw)
            else:
                income_category = str(income_category_raw)
        else:
            income_category = None
        
        # Generate full_name from available data
        name_parts = []
        if gender:
            name_parts.append(str(gender))
        if age:
            name_parts.append(f"{age} лет")
        full_name = f"Клиент #{client_id}" + (f" ({', '.join(name_parts)})" if name_parts else "")
        
        # Use incomeValueCategory as segment
        segment = income_category or "unknown"
        
        # Simple risk score calculation based on income (can be improved)
        income_value = getattr(client, 'incomeValue', None)
        risk_score = 0.5  # Default
        if income_value:
            if income_value < 50000:
                risk_score = 0.7  # Higher risk for low income
            elif income_value > 200000:
                risk_score = 0.2  # Lower risk for high income
            else:
                risk_score = 0.5  # Medium risk
        
        result.append(Client(
            id=client_id,
            full_name=full_name,
            age=age,
            city=city,
            adminarea=getattr(client, 'adminarea', None),
            gender=gender,
            incomeValue=income_value,
            incomeValueCategory=income_category,
            segment=segment,
            products=[],  # Can be populated from additional tables if needed
            risk_score=risk_score
        ))
    
    return result


@router.get(
    "/clients/{client_id}",
    response_model=Client,
    summary="Get client by ID",
    description="Retrieve detailed information about a specific client by their ID",
    response_description="Client object with full details",
    tags=["clients"]
)
async def get_client(
    client_id: int = Path(..., description="Unique client identifier", example=1, gt=0),
    db: Session = Depends(get_db)
) -> Client:
    """
    Get a specific client by ID.
    
    Retrieves detailed information about a single client including their
    personal information and income data.
    
    Args:
        client_id: Unique identifier of the client
        db: Database session
        
    Returns:
        Client: Client object with full details
        
    Raises:
        HTTPException: 404 if client with given ID is not found
    """
    logger.debug(f"Fetching client with ID: {client_id}")
    
    client = ClientService.get_client_by_id(db, client_id)
    
    if not client:
        logger.warning(f"Client with ID {client_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Client with ID {client_id} not found"
        )
    
    client_id = client.id
    city = getattr(client, 'city_smart_name', None)
    age = getattr(client, 'age', None)
    gender = getattr(client, 'gender', None)
    income_category_raw = getattr(client, 'incomeValueCategory', None)
    income_value = getattr(client, 'incomeValue', None)
    
    # Convert incomeValueCategory to string if it's a number
    if income_category_raw is not None:
        if isinstance(income_category_raw, (int, float)):
            income_category = str(int(income_category_raw)) if income_category_raw == int(income_category_raw) else str(income_category_raw)
        else:
            income_category = str(income_category_raw)
    else:
        income_category = None
    
    # Generate full_name from available data
    name_parts = []
    if gender:
        name_parts.append(str(gender))
    if age:
        name_parts.append(f"{age} лет")
    full_name = f"Клиент #{client_id}" + (f" ({', '.join(name_parts)})" if name_parts else "")
    
    # Use incomeValueCategory as segment
    segment = income_category or "unknown"
    
    # Simple risk score calculation based on income
    risk_score = 0.5  # Default
    if income_value:
        if income_value < 50000:
            risk_score = 0.7  # Higher risk for low income
        elif income_value > 200000:
            risk_score = 0.2  # Lower risk for high income
        else:
            risk_score = 0.5  # Medium risk
    
    return Client(
        id=client_id,
        full_name=full_name,
        age=age,
        city=city,
        adminarea=getattr(client, 'adminarea', None),
        gender=gender,
        incomeValue=income_value,
        incomeValueCategory=income_category,
        segment=segment,
        products=[],  # Can be populated from additional tables if needed
        risk_score=risk_score
    )


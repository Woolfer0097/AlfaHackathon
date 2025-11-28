from fastapi import HTTPException, status


class MLModelError(HTTPException):
    """Raised when ML model operations fail"""
    
    def __init__(self, detail: str = "ML model error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class InvalidInputError(HTTPException):
    """Raised when input validation fails"""
    
    def __init__(self, detail: str = "Invalid input"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


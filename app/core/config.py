from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    app_name: str = "ML API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # ML Model settings
    model_path: str = "models/model.pkl"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


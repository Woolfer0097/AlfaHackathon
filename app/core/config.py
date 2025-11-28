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
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


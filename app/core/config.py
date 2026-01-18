from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration"""
    
    # App
    app_name: str = "LTI Lab Platform"
    environment: str = "development"
    debug: bool = True
    
    # Security
    secret_key: str = "your-secret-key-change-this"
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/lti_platform"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Singleton instance
settings = Settings()
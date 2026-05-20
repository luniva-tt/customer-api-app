from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Groq API Configuration
    groq_api_key: str
    
    # Database Configuration
    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_db: str = "custmore_api_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Query Decomposition Settings
    decomposition_model: str = "llama-3.3-70b-versatile"  # Active Groq model
    temperature: float = 0.3  # Lower temperature for consistent decomposition
    max_tokens: int = 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


# Load settings
try:
    settings = Settings()
except Exception as e:
    # If settings fail to load, create a dummy instance for testing
    print(f"Warning: Failed to load settings: {e}")
    settings = None


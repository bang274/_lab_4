from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Authentication
    AGENT_API_KEY: str = "your-secret-api-key"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cost guard (monthly budget in USD)
    MONTHLY_BUDGET_USD: float = 100.0
    
    # LLM Configuration
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_BASE_URL: str = "https://models.inference.ai.azure.com"
    GITHUB_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
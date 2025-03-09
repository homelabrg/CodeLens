import os
from pydantic import BaseSettings, validator
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CodeLens Source Code Service"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # File storage settings
    STORAGE_TYPE: str = "local"  # local, s3, etc.
    CLONE_BASE_PATH: str = "/tmp/codelens/repos"
    FILES_BASE_PATH: str = "/tmp/codelens/files"
    DB_PATH: str = "/tmp/codelens/db"
    ANALYSIS_RESULTS_PATH: str = "/tmp/codelens/analysis"
    CACHE_DIR: str = "/tmp/codelens/cache"
    
    # GitHub settings
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    GITHUB_DEFAULT_BRANCH: str = "main"
    
    # OpenAI settings
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2048
    OPENAI_TEMPERATURE: float = 0.0
    
    # LLM Provider setting
    LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "openai")  # "openai" or "ollama"

    # Ollama settings
    OLLAMA_API_BASE: str = os.environ.get("OLLAMA_API_BASE", "http://host.docker.internal:11434")
    OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "llama2")
    
    # MongoDB settings (for future use)
    MONGODB_URI: Optional[str] = None
    MONGODB_DB_NAME: str = "codelens"
    
    # Authentication settings (for future use)
    SECRET_KEY: str = "development_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    @validator("CLONE_BASE_PATH", "FILES_BASE_PATH", "DB_PATH", "ANALYSIS_RESULTS_PATH", "CACHE_DIR")
    def create_directories(cls, v):
        """Create directories if they don't exist"""
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()

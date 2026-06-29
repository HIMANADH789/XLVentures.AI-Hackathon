import os
from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./prospectos.db"
    ai_pipeline_version: str = "v1"
    
    # LLM Configuration
    groq_api_key: str = ""
    
    # External APIs
    hunter_api_key: str = ""
    firecrawl_api_key: str = ""
    news_api_key: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()

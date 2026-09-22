# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"

    # LLM Settings
    llm_provider: Literal["cerebras", "openrouter", "huggingface"] = "openrouter"
    llm_model: str = "openai/gpt-oss-120b"
    llm_api_key: str
    
    # TigerGraph Settings
    tg_host: str
    tg_username: str = "tigergraph"
    tg_password: str = "tigergraph"
    tg_secret: str = ""
    tg_graph_name: str = "FraudGraph"

    # Agent Limits
    max_tool_calls: int = 40
    max_llm_calls: int = 12
    max_prior_cases: int = 8
    max_evidence_items: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"

    # Add "groq" to the allowed providers
    llm_provider: Literal["cerebras", "openrouter", "huggingface", "groq"] = "groq"
    llm_model: str = "openai/gpt-oss-120b"
    llm_api_key: str = "dev-key-placeholder"
    
    # TigerGraph Settings
    tg_host: str = "http://127.0.0.1:14240"
    tg_username: str = "tigergraph"
    tg_password: str = "tigergraph"
    tg_secret: str = ""
    tg_graph_name: str = "FraudGraph"

    # Agent Limits
    max_tool_calls: int = 40
    max_llm_calls: int = 12
    max_prior_cases: int = 8
    max_evidence_items: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Facial Architecture API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENV: str = "development"

    DEFAULT_PROVIDER: str = "gemini"

    # Gemini API / Proxy 设置 (支持用户中转地址与密钥)
    GEMINI_API_KEY: str = "sk-f9ae12d50cca49a78ce1d7241caf6570"
    GEMINI_BASE_URL: str = "http://localhost:8045/v1"
    GEMINI_MODEL: str = "gemini-3.8-flash"
    HTTPS_PROXY: Optional[str] = None

    # Aliyun DashScope (国内备用通道)
    DASHSCOPE_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-vl-plus"

    PRIMARY_TIMEOUT_SECONDS: float = 30.0
    SECONDARY_TIMEOUT_SECONDS: float = 30.0

    CHROMA_PERSIST_DIR: str = "./data/chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

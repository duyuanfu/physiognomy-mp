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

    DEFAULT_PROVIDER: str = "custom_openai"  # "custom_openai", "gemini", or "qwen"

    # 默认主通道配置 (可从环境变量或 .env 读取覆盖)
    DEFAULT_API_KEY: Optional[str] = None
    DEFAULT_BASE_URL: str = "https://api.deepseek.com"
    DEFAULT_MODEL: str = "deepseek-flash"

    # ★ 系统级高可用兜底通道：Cloudflare Worker 跨境反代 Google Gemini
    GEMINI_BASE_URL: str = "https://gemini.trythis.pw/v1"
    GEMINI_API_KEY: Optional[str] = None  # 密钥通过服务器本地 .env 安全注入，绝不硬编码以保护凭证安全
    GEMINI_MODEL: str = "models/gemini-flash-latest"
    HTTPS_PROXY: Optional[str] = None

    # Aliyun DashScope (国内备用通道)
    DASHSCOPE_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-vl-plus"

    PRIMARY_TIMEOUT_SECONDS: float = 35.0
    SECONDARY_TIMEOUT_SECONDS: float = 25.0

    CHROMA_PERSIST_DIR: str = "./data/chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

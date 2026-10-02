from abc import ABC, abstractmethod
from typing import Dict, Any
from app.schemas.report import LLMReportContent


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """返回提供者名称，如 'gemini' 或 'qwen'"""
        pass

    @abstractmethod
    async def generate_report(self, image_bytes: bytes, prompt: str, timeout_seconds: float) -> LLMReportContent:
        """接收图片与提示词，异步调用多模态模型并返回强类型报告结构"""
        pass

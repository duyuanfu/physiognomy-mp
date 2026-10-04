import logging
from typing import Tuple, Optional
from app.core.config import settings
from app.core.exceptions import LLMServiceUnavailableException
from app.providers.base import BaseLLMProvider
from app.providers.gemini_provider import GeminiFlashProvider
from app.providers.qwen_provider import QwenVLProvider
from app.providers.dynamic_provider import DynamicOpenAIProvider
from app.schemas.report import LLMReportContent
from app.schemas.metrics import FacialMetrics

logger = logging.getLogger("provider_manager")


class ProviderManager:
    def __init__(self):
        self.gemini_provider = GeminiFlashProvider()
        self.qwen_provider = QwenVLProvider()

    async def generate_report_with_fallback(
        self,
        image_bytes: bytes,
        prompt: str,
        metrics: FacialMetrics,
        custom_base_url: Optional[str] = None,
        custom_api_key: Optional[str] = None,
        custom_model: Optional[str] = None
    ) -> Tuple[LLMReportContent, str, Optional[str]]:
        # 1. 确定本次调用的主模型通道 (前端动态传入优先，否则使用系统默认配置)
        target_base_url = custom_base_url or settings.DEFAULT_BASE_URL
        target_api_key = custom_api_key or settings.DEFAULT_API_KEY
        target_model = custom_model or settings.DEFAULT_MODEL

        errors = []

        if target_base_url and target_api_key:
            provider = DynamicOpenAIProvider(
                base_url=target_base_url,
                api_key=target_api_key,
                model=target_model
            )
            try:
                logger.info(f"正在调用模型 [{target_model}] @ [{target_base_url}]...")
                report = await provider.generate_report(image_bytes, prompt, settings.PRIMARY_TIMEOUT_SECONDS)
                return report, target_model, None
            except Exception as e:
                err_detail = f"模型 [{target_model}] 报错: {str(e)}"
                logger.warning(f"{err_detail}，尝试自动切换至备用通道...")
                errors.append(err_detail)
        else:
            errors.append("未配置大模型 API Key")

        # 2. 本地/云端热备通道：Gemini Flash (通过 Cloudflare Worker 或系统内置配置)
        if settings.GEMINI_API_KEY and settings.GEMINI_BASE_URL:
            try:
                logger.info(f"调用系统备用模型: {self.gemini_provider.provider_name}...")
                report = await self.gemini_provider.generate_report(image_bytes, prompt, settings.PRIMARY_TIMEOUT_SECONDS)
                fallback_reason = f"主通道异常({'; '.join(errors)})，已由系统备用通道接管"
                return report, "gemini-flash", fallback_reason
            except Exception as e:
                err_detail = f"系统备用 Gemini 失败: {str(e)}"
                logger.warning(f"{err_detail}")
                errors.append(err_detail)

        # 3. 彻底删除“自带边界的高智感底色”兜底文案，直接抛出真实的排查错误，绝不掩盖真实问题！
        full_error = "；".join(errors)
        logger.error(f"所有大模型通道均不可用: {full_error}")
        raise LLMServiceUnavailableException(f"大模型调用失败: {full_error}")


provider_manager = ProviderManager()

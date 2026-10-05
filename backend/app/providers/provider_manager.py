import logging
from typing import Tuple, Optional
from app.core.config import settings
from app.core.exceptions import LLMServiceUnavailableException
from app.providers.dynamic_provider import DynamicOpenAIProvider
from app.schemas.report import LLMReportContent
from app.schemas.metrics import FacialMetrics

logger = logging.getLogger("provider_manager")


class ProviderManager:
    async def generate_report_with_fallback(
        self,
        image_bytes: bytes,
        prompt: str,
        metrics: FacialMetrics,
        custom_base_url: Optional[str] = None,
        custom_api_key: Optional[str] = None,
        custom_model: Optional[str] = None
    ) -> Tuple[LLMReportContent, str, Optional[str]]:
        # 清洗前端传入的动态配置项
        c_key = (custom_api_key or "").strip()
        c_url = (custom_base_url or "").strip()
        c_model = (custom_model or "").strip()

        # 默认使用 Gemini 官方反代配置 (优先从服务器本地 .env 读取注入的 GEMINI_API_KEY)
        default_api_key = (settings.GEMINI_API_KEY or settings.DEFAULT_API_KEY or "").strip()
        default_base_url = (settings.GEMINI_BASE_URL or settings.DEFAULT_BASE_URL or "https://gemini.trythis.pw/v1").strip()
        default_model = (settings.GEMINI_MODEL or settings.DEFAULT_MODEL or "models/gemini-flash-latest").strip()

        errors = []

        # 1. 确定本次调用的主模型通道
        if c_key:
            # 用户在前端弹窗中显式配置了自定义 API Key
            target_base_url = c_url if c_url else default_base_url
            target_model = c_model if c_model else default_model
            target_api_key = c_key
            provider_source = "用户前端自定义配置"
        else:
            # 前端未配置或配置项缺少：自动使用后端服务器 .env 中的默认 Gemini 配置
            if not default_api_key:
                raise LLMServiceUnavailableException(
                    "后端未就绪：前端未提供 API Key，且服务器 .env 中未配置 GEMINI_API_KEY，请在 .env 中设置后生效。"
                )
            target_base_url = default_base_url
            target_model = default_model
            target_api_key = default_api_key
            provider_source = "系统默认配置(Gemini)"

        # 2. 执行主通道调用 (DynamicOpenAIProvider 已内置 503 拥堵自愈重试与纯文本多模态自适应)
        provider = DynamicOpenAIProvider(
            base_url=target_base_url,
            api_key=target_api_key,
            model=target_model
        )
        try:
            logger.info(f"正在通过 [{provider_source}] 调用模型 [{target_model}] @ [{target_base_url}]...")
            report = await provider.generate_report(image_bytes, prompt, settings.PRIMARY_TIMEOUT_SECONDS)
            return report, provider.provider_name, None
        except Exception as e:
            err_detail = f"通道 [{target_model}] 调用失败: {str(e)}"
            logger.warning(f"{err_detail}")
            errors.append(err_detail)

        # 3. 若前端自定义 Key 报错（如用户填错 Key 或额度用尽），且服务器 .env 备有默认可用 Key，自动无缝降级到默认 Gemini 通道
        if c_key and default_api_key and (c_key != default_api_key):
            try:
                logger.info("前端自定义 Key 失败，自动切换至后端 .env 内置默认 Gemini 通道...")
                backup_provider = DynamicOpenAIProvider(
                    base_url=default_base_url,
                    api_key=default_api_key,
                    model=default_model
                )
                report = await backup_provider.generate_report(image_bytes, prompt, settings.PRIMARY_TIMEOUT_SECONDS)
                fallback_reason = f"自定义配置异常({'; '.join(errors)})，已由服务器内置默认 Gemini 成功接管"
                return report, backup_provider.provider_name, fallback_reason
            except Exception as e:
                errors.append(f"内置备用 Gemini 同样失败: {str(e)}")

        full_error = "；".join(errors)
        logger.error(f"大模型调用全部失败: {full_error}")
        raise LLMServiceUnavailableException(f"大模型调用失败: {full_error}")


provider_manager = ProviderManager()

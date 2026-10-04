import base64
import json
import logging
import httpx
from app.providers.base import BaseLLMProvider
from app.schemas.report import LLMReportContent

logger = logging.getLogger("dynamic_provider")


def extract_friendly_error(status_code: int, raw_text: str, model: str) -> str:
    """提取对人类友好的简短排查报错，防止上千字的长JSON破坏微信弹窗"""
    text_lower = raw_text.lower()
    if status_code == 429 or "quota" in text_lower or "resource_exhausted" in text_lower:
        return f"模型 [{model}] 额度已耗尽 (HTTP 429): 该账号今日免费调用次数已达上限，请更换账号/Key或明日重试。"
    if status_code == 402 or "insufficient balance" in text_lower:
        return f"模型 [{model}] 余额不足 (HTTP 402): 平台账户已欠费，请充值后使用。"
    if status_code == 401 or "unauthorized" in text_lower or "invalid_api_key" in text_lower:
        return f"模型 [{model}] 认证失败 (HTTP 401): API Key 无效或权限不足，请核对。"
    if status_code == 404:
        return f"模型 [{model}] 路径不存在 (HTTP 404): 请检查 Base URL 或模型名称拼写。"
    if status_code == 503 or "overloaded" in text_lower or "high demand" in text_lower:
        return f"模型 [{model}] 暂时拥堵 (HTTP 503): 官方算力高峰期繁忙，请稍后再试。"
    
    # 截取前 100 个字符
    return f"模型 [{model}] 异常 (HTTP {status_code}): {raw_text[:100]}"


class DynamicOpenAIProvider(BaseLLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

        normalized_model = model
        m_lower = model.lower().strip()

        # 1. DeepSeek 官方模型名称别名纠偏
        if "deepseek.com" in self._base_url:
            if "flash" in m_lower or "v4.1" in m_lower or "4.1" in m_lower:
                normalized_model = "deepseek-flash"
            elif "pro" in m_lower:
                normalized_model = "deepseek-v4-pro"
            elif "chat" in m_lower:
                normalized_model = "deepseek-chat"

        # 2. Google Gemini 官方/Worker反代模型前缀纠偏
        if ("googleapis.com" in self._base_url or "gemini" in self._base_url or "trythis.pw" in self._base_url):
            if "gemini" in m_lower and not m_lower.startswith("models/"):
                normalized_model = f"models/{model}"

        self._model = normalized_model

    @property
    def provider_name(self) -> str:
        return self._model

    async def generate_report(self, image_bytes: bytes, prompt: str, timeout_seconds: float) -> LLMReportContent:
        if not self._api_key:
            raise ValueError("未配置 API Key")

        endpoint = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_img}"

        # 1. 尝试以多模态方式发送 (文本 + 图片)
        payload_multimodal = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4
        }

        raw_text = None
        async with httpx.AsyncClient(trust_env=False, timeout=timeout_seconds) as client:
            try:
                resp = await client.post(endpoint, headers=headers, json=payload_multimodal)
                if resp.status_code == 200:
                    res_json = resp.json()
                    raw_text = res_json["choices"][0]["message"]["content"]
                else:
                    err_msg = extract_friendly_error(resp.status_code, resp.text, self._model)
                    logger.warning(f"多模态请求失败: {err_msg}，尝试降级为纯文本几何描述...")
            except Exception as e:
                logger.warning(f"多模态请求异常: {e}，尝试降级为纯文本几何描述...")

            # 2. 如果模型仅支持纯文本（非视觉模型）或图片格式不兼容，自动降级为纯文本Prompt调用
            if not raw_text:
                payload_text_only = {
                    "model": self._model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.4
                }
                resp2 = await client.post(endpoint, headers=headers, json=payload_text_only)
                if resp2.status_code != 200:
                    friendly_err = extract_friendly_error(resp2.status_code, resp2.text, self._model)
                    raise RuntimeError(friendly_err)
                res_json2 = resp2.json()
                raw_text = res_json2["choices"][0]["message"]["content"]

        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        parsed_json = json.loads(clean_text.strip())
        return LLMReportContent.model_validate(parsed_json)

import base64
import json
import logging
import httpx
from app.providers.base import BaseLLMProvider
from app.schemas.report import LLMReportContent

logger = logging.getLogger("dynamic_provider")


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

        # 2. Google Gemini 官方/Worker反代模型前缀纠偏 (Google 强制要求 models/ 前缀)
        if ("googleapis.com" in self._base_url or "gemini" in self._base_url or "trythis.pw" in self._base_url):
            if "gemini" in m_lower and not m_lower.startswith("models/"):
                normalized_model = f"models/{model}"

        self._model = normalized_model

    @property
    def provider_name(self) -> str:
        return self._model

    async def generate_report(self, image_bytes: bytes, prompt: str, timeout_seconds: float) -> LLMReportContent:
        if not self._api_key:
            raise ValueError("API Key 未提供")

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
                    logger.warning(f"多模态请求返回 {resp.status_code} ({resp.text[:120]})，尝试降级为纯文本几何描述...")
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
                    raise RuntimeError(f"模型调用失败: HTTP {resp2.status_code} - {resp2.text}")
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

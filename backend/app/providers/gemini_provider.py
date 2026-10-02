import base64
import json
import httpx
from app.core.config import settings
from app.providers.base import BaseLLMProvider
from app.schemas.report import LLMReportContent


class GeminiFlashProvider(BaseLLMProvider):
    def __init__(self):
        self._provider_name = "gemini"

    @property
    def provider_name(self) -> str:
        return self._provider_name

    async def generate_report(self, image_bytes: bytes, prompt: str, timeout_seconds: float) -> LLMReportContent:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY 未配置")

        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_img}"

        # 优先使用用户配置的 OpenAI 兼容中转接口 (如 http://localhost:8045/v1)
        base_url = settings.GEMINI_BASE_URL.rstrip("/")
        endpoint = f"{base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": settings.GEMINI_MODEL,
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

        # trust_env=False 确保本地 localhost:8045 请求不会被系统外部代理劫持为 502
        async with httpx.AsyncClient(trust_env=False, timeout=timeout_seconds) as client:
            resp = await client.post(endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API 错误: {resp.status_code} - {resp.text}")

            res_json = resp.json()
            raw_text = res_json["choices"][0]["message"]["content"]

        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        parsed_json = json.loads(clean_text.strip())
        return LLMReportContent.model_validate(parsed_json)

import base64
import json
import asyncio
import dashscope
from dashscope import MultiModalConversation
from app.core.config import settings
from app.providers.base import BaseLLMProvider
from app.schemas.report import LLMReportContent


class QwenVLProvider(BaseLLMProvider):
    def __init__(self):
        self._provider_name = "qwen"
        if settings.DASHSCOPE_API_KEY:
            dashscope.api_key = settings.DASHSCOPE_API_KEY

    @property
    def provider_name(self) -> str:
        return self._provider_name

    async def generate_report(self, image_bytes: bytes, prompt: str, timeout_seconds: float) -> LLMReportContent:
        if not settings.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY 未配置")

        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_img}"

        def _call_qwen():
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": data_uri},
                        {"text": prompt}
                    ]
                }
            ]

            response = MultiModalConversation.call(
                model=settings.QWEN_MODEL,
                messages=messages,
                result_format="message"
            )

            if response.status_code != 200:
                raise RuntimeError(f"DashScope Qwen-VL error: {response.code} - {response.message}")

            return response.output.choices[0].message.content[0]["text"]

        raw_text = await asyncio.wait_for(
            asyncio.to_thread(_call_qwen),
            timeout=timeout_seconds
        )

        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        parsed_json = json.loads(clean_text.strip())
        return LLMReportContent.model_validate(parsed_json)

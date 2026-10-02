import logging
from typing import Tuple
from app.core.config import settings
from app.core.exceptions import LLMServiceUnavailableException
from app.providers.base import BaseLLMProvider
from app.providers.gemini_provider import GeminiFlashProvider
from app.providers.qwen_provider import QwenVLProvider
from app.schemas.report import (
    LLMReportContent,
    SummarySection,
    StructureSection,
    ThreePartsSection,
    BoneFrameSection,
    EarEvidenceSection,
    FeaturesSection,
    FeatureItem,
    RadarScoresSection,
    ModernAdviceSection
)
from app.schemas.metrics import FacialMetrics

logger = logging.getLogger("provider_manager")


class ProviderManager:
    def __init__(self):
        self.gemini_provider = GeminiFlashProvider()
        self.qwen_provider = QwenVLProvider()

    def _generate_mock_fallback(self, metrics: FacialMetrics) -> LLMReportContent:
        """当外部大模型均不可达或未配置API Key时，基于真实CV数据装配极简冷淡风高智感报告"""
        # 根据下颌角与脸型决定主导型
        if metrics.jaw_angle_degree < 85:
            archetype = "凛然折角型"
            bone_desc = "下颌折角锐利紧致，下庭线条清晰收束。筋骨撑肉，具备极强的决策果断力与原则底线感。"
            intellect_score = 94
            presence_score = 90
        elif metrics.jaw_angle_degree > 100:
            archetype = "温润聚势型"
            bone_desc = "下颌骨量方厚舒展，地阁承托有力。抗挫容忍力高，擅长长期战略沉淀与长周期复利。"
            intellect_score = 88
            presence_score = 86
        else:
            archetype = "清骨敛气型"
            bone_desc = "下颌转折刚柔微折，皮肉贴合紧实度极佳。兼具清冷距离感与进取韧性，骨相抗衰能力优异。"
            intellect_score = 91
            presence_score = 88

        canthal_desc = "外眦呈正向飞扬势，眼神聚焦度高，显露极强目标感知力。" if metrics.canthal_tilt_degree > 3.0 else (
            "外眦微垂温润，眼神柔和内敛，具备极佳同理心与隐形贵人缘。" if metrics.canthal_tilt_degree < -2.0 else
            "外眦平直沉稳，眼神波澜不惊，情绪自洽且观察敏锐。"
        )

        return LLMReportContent(
            summary=SummarySection(
                archetype=archetype,
                aura_title="自带边界的高智感底色",
                tags=["#高智量感", "#清冷坚定", "#隐忍蓄势"]
            ),
            structure=StructureSection(
                three_parts=ThreePartsSection(
                    ratio=f"1 : {round(metrics.face_ratio * 0.75, 2)} : 0.95",
                    verdict=f"面部长宽比 {metrics.face_ratio}，{metrics.face_type}格局舒展",
                    analysis="上庭饱满主早慧自主探索，中庭挺直利事业开拓攻坚，下庭承托力强主晚景沉淀蓄势。"
                ),
                bone_frame=BoneFrameSection(
                    title=f"{metrics.jaw_type} · 筋骨撑肉",
                    analysis=bone_desc
                ),
                ear_evidence=EarEvidenceSection(
                    title="采听轮廓贴脑，心智内敛",
                    analysis="耳廓分明且贴脑内收，主内在精神世界充沛独立，不易受外界噪音干扰节奏。"
                )
            ),
            features=FeaturesSection(
                eyes=FeatureItem(
                    title=f"眼神眉宇 · {metrics.eye_tilt_type}",
                    desc=canthal_desc
                ),
                nose=FeatureItem(
                    title="鼻岳印堂 · 山根挺秀",
                    desc="山根平直与印堂开阔呼应，进取心明确，具备极佳的全局资源掌控与调配潜能。"
                ),
                mouth=FeatureItem(
                    title="唇颌承浆 · 唇线微敛",
                    desc="唇形边缘清晰微收，言辞严谨克制，在社交互动中极其注重人际边界与空间感。"
                )
            ),
            radar_scores=RadarScoresSection(
                intellect=intellect_score,
                presence=presence_score,
                wealth_affinity=86,
                equanimity=82
            ),
            modern_advice=ModernAdviceSection(
                style="适合极简利落剪裁、冷色调（黑/白/炭灰/冷钛银）服饰与微金属配饰，进一步强化清冷骨骼感。",
                expression="在职场汇报与商务沟通中保持专注眼神凝视与微平视神态，能最大化说服力与气场优势。",
                mindset="面对外界高强度信息输入，保持定力做情绪断舍离，减少深夜过度思虑消耗。"
            )
        )

    async def generate_report_with_fallback(
        self,
        image_bytes: bytes,
        prompt: str,
        metrics: FacialMetrics
    ) -> Tuple[LLMReportContent, str]:
        # 1. 优先通道
        primary = self.gemini_provider if settings.DEFAULT_PROVIDER == "gemini" else self.qwen_provider
        secondary = self.qwen_provider if settings.DEFAULT_PROVIDER == "gemini" else self.gemini_provider

        try:
            logger.info(f"尝试调用主模型: {primary.provider_name}...")
            report = await primary.generate_report(image_bytes, prompt, settings.PRIMARY_TIMEOUT_SECONDS)
            return report, primary.provider_name
        except Exception as e:
            logger.warning(f"主模型 [{primary.provider_name}] 异常 ({str(e)})，自动切换至备用模型 [{secondary.provider_name}]...")

        # 2. 备用通道故障转移
        try:
            logger.info(f"调用备用模型: {secondary.provider_name}...")
            report = await secondary.generate_report(image_bytes, prompt, settings.SECONDARY_TIMEOUT_SECONDS)
            return report, secondary.provider_name
        except Exception as e:
            logger.warning(f"备用模型 [{secondary.provider_name}] 同样异常 ({str(e)})，启用极简离线骨相知识库装配引擎...")

        # 3. 兜底离线装配（绝不中断服务）
        report = self._generate_mock_fallback(metrics)
        return report, "offline_engine"


provider_manager = ProviderManager()

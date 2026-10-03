from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator
from app.schemas.metrics import FacialMetrics


class SummarySection(BaseModel):
    archetype: str = Field(..., description="骨相主导型，如：清骨敛气型")
    aura_title: str = Field(..., description="核心气场一句话，如：自带边界的高智感底色")
    tags: List[str] = Field(..., description="3个现代标签，如：#高智量感, #清冷坚定, #隐忍蓄势")


class ThreePartsSection(BaseModel):
    ratio: str = Field(..., description="三庭比例，如 1 : 1.05 : 0.95")
    verdict: str = Field(..., description="一句话三庭格局定调")
    analysis: str = Field(..., description="三庭深度分析")


class BoneFrameSection(BaseModel):
    title: str = Field(..., description="骨骼基底定调")
    analysis: str = Field(..., description="骨相支撑与抗老原则解构")


class EarEvidenceSection(BaseModel):
    title: str = Field(..., description="耳相特征定调")
    analysis: str = Field(..., description="耳位与定力、福蕴佐证分析")


class StructureSection(BaseModel):
    three_parts: ThreePartsSection
    bone_frame: BoneFrameSection
    ear_evidence: EarEvidenceSection


class FeatureItem(BaseModel):
    title: str = Field(default="五官气韵")
    desc: str = Field(default="")

    @model_validator(mode="before")
    @classmethod
    def normalize_feature(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "desc" not in data or not data["desc"]:
                data["desc"] = data.get("description") or data.get("content") or data.get("analysis") or data.get("title", "")
            if "title" not in data or not data["title"]:
                data["title"] = "五官特征"
        elif isinstance(data, str):
            return {"title": "特征解构", "desc": data}
        return data


# ★ 扩充至六大微观五官气韵维度
class FeaturesSection(BaseModel):
    eyebrows: FeatureItem = Field(default_factory=lambda: FeatureItem(title="眉宇骨势 · 决断思辨", desc="眉骨起伏舒展，长短适中，展现自驱探索定力。"))
    eyes: FeatureItem = Field(default_factory=lambda: FeatureItem(title="眼神明澈 · 洞察聚焦", desc="目光聚而不散，外眦上扬有势，注意力控制力极强。"))
    glabella: FeatureItem = Field(default_factory=lambda: FeatureItem(title="印堂山根 · 命宫抗压", desc="印堂开朗平整，山根贯直，抗压承载度极高。"))
    nose: FeatureItem = Field(default_factory=lambda: FeatureItem(title="鼻岳财帛 · 攻坚蓄势", desc="鼻梁直顺微挺，鼻翼聚拢收束，实操落地意志坚定。"))
    mouth: FeatureItem = Field(default_factory=lambda: FeatureItem(title="唇齿出纳 · 表达温度", desc="唇线微收分明，厚薄相称，社交互动中言辞克制有度。"))
    jaw: FeatureItem = Field(default_factory=lambda: FeatureItem(title="地阁下颌 · 稳态后劲", desc="下颌转折支撑有力，地阁平正，展现长周期复利韧劲。"))

    @model_validator(mode="before")
    @classmethod
    def handle_legacy_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 兼容老版只传了 eyes, nose, mouth 的情况
            if "eyes" in data and "eyebrows" not in data:
                data["eyebrows"] = {"title": "眉宇骨相", "desc": "眉骨开朗，眉尾聚敛，具自驱定力。"}
            if "nose" in data and "glabella" not in data:
                data["glabella"] = {"title": "印堂山根", "desc": "印堂平坦开阔，山根顺直，气韵中正。"}
            if "mouth" in data and "jaw" not in data:
                data["jaw"] = {"title": "下颌承托", "desc": "地阁支撑稳健，承载后劲充沛。"}
        return data


class RadarScoresSection(BaseModel):
    intellect: int = Field(..., ge=0, le=100, description="智感与洞察")
    presence: int = Field(..., ge=0, le=100, description="气场与边界感")
    wealth_affinity: int = Field(..., ge=0, le=100, description="蓄势与吸金力")
    equanimity: int = Field(..., ge=0, le=100, description="情绪自洽度")


class ModernAdviceSection(BaseModel):
    style: str = Field(..., description="高级感美学与配饰穿搭灵感")
    expression: str = Field(..., description="眼神与微表情管理技巧")
    mindset: str = Field(..., description="情绪自洽与断舍离锦囊")


# 中远期扩展架构预留字段 (Reserved Capabilties)
class CoupleAnalysisExtension(BaseModel):
    partner_id: Optional[str] = None
    similarity_score: Optional[float] = None
    complementary_points: List[str] = Field(default_factory=list)


class TimelineHistoryExtension(BaseModel):
    previous_record_id: Optional[str] = None
    vitality_delta: Optional[float] = None
    firmness_delta: Optional[float] = None


class SocialCardExtension(BaseModel):
    meme_title: Optional[str] = None
    aura_rarity: Optional[str] = None


class ExtensionsReserved(BaseModel):
    couple_analysis: Optional[CoupleAnalysisExtension] = None
    timeline_history: Optional[TimelineHistoryExtension] = None
    social_card: Optional[SocialCardExtension] = None


class LLMReportContent(BaseModel):
    summary: SummarySection
    structure: StructureSection
    features: FeaturesSection
    radar_scores: RadarScoresSection
    modern_advice: ModernAdviceSection


class FacialReportResponse(BaseModel):
    code: int = 200
    message: str = "success"
    provider_used: str = Field(..., description="本次实际生效的模型提供方")
    metrics: FacialMetrics
    report: LLMReportContent
    extensions: ExtensionsReserved = Field(default_factory=ExtensionsReserved)

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
    title: str = Field(default="")
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


class FeaturesSection(BaseModel):
    eyes: FeatureItem
    nose: FeatureItem
    mouth: FeatureItem


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


# 大模型输出的主体内容结构
class LLMReportContent(BaseModel):
    summary: SummarySection
    structure: StructureSection
    features: FeaturesSection
    radar_scores: RadarScoresSection
    modern_advice: ModernAdviceSection


# API 最终返回给前端的完整报文
class FacialReportResponse(BaseModel):
    code: int = 200
    message: str = "success"
    provider_used: str = Field(..., description="本次实际生效的模型提供方 (gemini / qwen)")
    metrics: FacialMetrics
    report: LLMReportContent
    extensions: ExtensionsReserved = Field(default_factory=ExtensionsReserved)

from typing import Dict, List, Tuple
from pydantic import BaseModel, Field


class ThreePartsLevels(BaseModel):
    trichion_y: float
    brow_y: float
    subnasale_y: float
    menton_y: float


class FacialCaliperPoints(BaseModel):
    trichion: Tuple[float, float]
    menton: Tuple[float, float]
    zygoma_left: Tuple[float, float]
    zygoma_right: Tuple[float, float]
    jaw_left: Tuple[float, float]
    jaw_right: Tuple[float, float]
    left_eye_inner: Tuple[float, float]
    left_eye_outer: Tuple[float, float]
    right_eye_inner: Tuple[float, float]
    right_eye_outer: Tuple[float, float]
    nose_tip: Tuple[float, float]
    subnasale: Tuple[float, float]
    nasion: Tuple[float, float] = (0.0, 0.0) # 山根点
    alar_left: Tuple[float, float] = (0.0, 0.0) # 左鼻翼
    alar_right: Tuple[float, float] = (0.0, 0.0) # 右鼻翼
    brow_peak_left: Tuple[float, float] = (0.0, 0.0) # 左眉峰
    brow_peak_right: Tuple[float, float] = (0.0, 0.0) # 右眉峰
    lip_left: Tuple[float, float] = (0.0, 0.0) # 左嘴角
    lip_right: Tuple[float, float] = (0.0, 0.0) # 右嘴角
    lip_top: Tuple[float, float] = (0.0, 0.0) # 唇峰
    contour_polygon: List[Tuple[float, float]] = Field(default_factory=list, description="面部下颌与轮廓稠密关键点集合")
    three_parts_levels: ThreePartsLevels = Field(default_factory=lambda: ThreePartsLevels(trichion_y=0, brow_y=0, subnasale_y=0, menton_y=0))


class FacialMetrics(BaseModel):
    face_ratio: float = Field(..., description="面部长宽比")
    jaw_angle_degree: float = Field(..., description="下颌收拢夹角")
    canthal_tilt_degree: float = Field(..., description="左眼外眦上扬角")
    palpebral_ratio: float = Field(..., description="眼裂长宽比")
    roll_angle_degree: float = Field(..., description="头部姿态倾斜角")

    three_parts_ratio: str = Field(..., description="三庭黄金精微比例")
    intercanthal_ratio: float = Field(..., description="内眦间距/单眼长比率")
    nasal_width_ratio: float = Field(..., description="鼻翼宽/鼻长比率")
    lip_thickness_ratio: float = Field(..., description="下唇/上唇厚度比")

    face_type: str = Field(..., description="长面型 / 中面型 / 阔面型")
    jaw_type: str = Field(..., description="锐意利落型 / 刚柔微折型 / 方正基石型")
    eye_tilt_type: str = Field(..., description="正向飞扬势 / 沉稳平视势 / 亲和微垂势")
    intercanthal_type: str = Field(..., description="开阔包容型 / 黄金标准型 / 警惕敏锐型")

    caliper_points: FacialCaliperPoints = Field(..., description="用于前端在照片上绘制工程标尺与轮廓的关键点坐标")

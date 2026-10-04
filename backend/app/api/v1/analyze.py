import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from typing import Optional
from pydantic import BaseModel

from app.services.face_mesh_service import face_mesh_service
from app.services.rag_service import rag_service
from app.providers.provider_manager import provider_manager
from app.prompts.templates import build_analysis_prompt
from app.schemas.report import FacialReportResponse, ExtensionsReserved

router = APIRouter()


@router.post("/analyze", response_model=FacialReportResponse)
async def analyze_face(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    # 支持前端动态传递自定义 LLM 参数
    custom_api_key: Optional[str] = Form(None),
    custom_base_url: Optional[str] = Form(None),
    custom_model: Optional[str] = Form(None)
):
    image_bytes = b""
    if file is not None:
        image_bytes = await file.read()
    elif image_base64 is not None:
        clean_b64 = image_base64
        if "base64," in clean_b64:
            clean_b64 = clean_b64.split("base64,")[1]
        try:
            image_bytes = base64.b64decode(clean_b64)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非法的base64图片数据")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="必须提供图片文件或 base64 字符串")

    if len(image_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传图片为空")

    # 1. CV 几何精密量测
    metrics = face_mesh_service.extract_metrics_from_bytes(image_bytes)

    # 2. RAG 知识检索
    retrieved_knowledge = rag_service.retrieve_knowledge(metrics, top_k=4)

    # 3. 构造提示词
    metrics_desc = (
        f"- 面部长宽比: {metrics.face_ratio} ({metrics.face_type})\n"
        f"- 下颌夹角: {metrics.jaw_angle_degree}° ({metrics.jaw_type})\n"
        f"- 三庭精微比率: {metrics.three_parts_ratio} (上庭:中庭:下庭)\n"
        f"- 外眦上扬角: {metrics.canthal_tilt_degree}° ({metrics.eye_tilt_type})\n"
        f"- 眼裂长宽比: {metrics.palpebral_ratio}\n"
        f"- 内眦间距/单眼长比: {metrics.intercanthal_ratio} ({metrics.intercanthal_type}五眼法则)\n"
        f"- 鼻翼宽/鼻长比: {metrics.nasal_width_ratio} (财帛中岳聚气度)\n"
        f"- 上下唇厚度比: {metrics.lip_thickness_ratio} (水星出纳官社交温度)\n"
        f"- 头部校准偏转角: {metrics.roll_angle_degree}°"
    )
    prompt = build_analysis_prompt(metrics_desc, retrieved_knowledge)

    # 4. 模型生成 (支持前端自定义 LLM 与自动故障转移)
    report_content, provider_used, llm_error = await provider_manager.generate_report_with_fallback(
        image_bytes=image_bytes,
        prompt=prompt,
        metrics=metrics,
        custom_base_url=custom_base_url,
        custom_api_key=custom_api_key,
        custom_model=custom_model
    )

    return FacialReportResponse(
        code=200,
        message="success",
        provider_used=provider_used,
        llm_error=llm_error,
        metrics=metrics,
        report=report_content,
        extensions=ExtensionsReserved()
    )

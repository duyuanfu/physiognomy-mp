import asyncio
import os
import sys

# 强制 UTF-8 打印输出
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.face_mesh_service import face_mesh_service
from app.services.rag_service import rag_service
from app.providers.provider_manager import provider_manager
from app.prompts.templates import build_analysis_prompt
from app.schemas.report import FacialReportResponse, ExtensionsReserved


async def test_single_image(file_path: str):
    print("\n" + "=" * 70)
    print(f"TESTING REAL IMAGE: {file_path}")
    print("=" * 70)

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        img_bytes = f.read()

    # 1. CV 几何测量
    metrics = face_mesh_service.extract_metrics_from_bytes(img_bytes)
    print(f"[1/4] CV 几何精密量测成功:")
    print(f"      - 面部长宽比: {metrics.face_ratio} ({metrics.face_type})")
    print(f"      - 下颌夹角:   {metrics.jaw_angle_degree}度 ({metrics.jaw_type})")
    print(f"      - 外眦上扬角: {metrics.canthal_tilt_degree}度 ({metrics.eye_tilt_type})")
    print(f"      - 眼裂长宽比: {metrics.palpebral_ratio}")
    print(f"      - 姿态偏转角: {metrics.roll_angle_degree}度")

    # 2. RAG 知识检索
    retrieved = rag_service.retrieve_knowledge(metrics, top_k=3)
    print(f"[2/4] RAG 典籍检索成功 (Top-3 规则依据召回)")

    # 3. 构造提示词
    metrics_desc = (
        f"- 面部长宽比: {metrics.face_ratio} ({metrics.face_type})\n"
        f"- 下颌夹角: {metrics.jaw_angle_degree}° ({metrics.jaw_type})\n"
        f"- 外眦上扬角: {metrics.canthal_tilt_degree}° ({metrics.eye_tilt_type})\n"
        f"- 眼裂长宽比: {metrics.palpebral_ratio}\n"
        f"- 头部校准偏转角: {metrics.roll_angle_degree}°"
    )
    prompt = build_analysis_prompt(metrics_desc, retrieved)

    # 4. 调用大模型 (Gemini 3.8 Flash via http://localhost:8045/v1)
    print(f"[3/4] 调用 Gemini 3.8 Flash 实时推理中...")
    report, provider = await provider_manager.generate_report_with_fallback(
        image_bytes=img_bytes,
        prompt=prompt,
        metrics=metrics
    )

    print(f"[4/4] 解构完成! 生效引擎: [{provider}]")
    print(f"      - 骨相主导型: 【{report.summary.archetype}】")
    print(f"      - 核心气场:   {report.summary.aura_title}")
    print(f"      - 标签:       {report.summary.tags}")
    print(f"      - 三庭格局:   {report.structure.three_parts.ratio} | {report.structure.three_parts.verdict}")
    print(f"      - 骨相解构:   {report.structure.bone_frame.title} - {report.structure.bone_frame.analysis[:60]}...")
    print(f"      - 采听耳相:   {report.structure.ear_evidence.title} - {report.structure.ear_evidence.analysis[:60]}...")
    print(f"      - 眼神眉宇:   {report.features.eyes.title} - {report.features.eyes.desc[:60]}...")
    print(f"      - 四维能量:   智感 {report.radar_scores.intellect} | 气场 {report.radar_scores.presence} | 吸金 {report.radar_scores.wealth_affinity} | 自洽 {report.radar_scores.equanimity}")
    print(f"      - 增势锦囊:   {report.modern_advice.style[:60]}...")


async def main():
    test_files = [
        r"D:\UserData\Downloads\1.webp",
        r"D:\UserData\Downloads\2.jpg",
        r"D:\UserData\Downloads\3.jpg"
    ]
    for p in test_files:
        try:
            await test_single_image(p)
        except Exception as e:
            print(f"Test failed on {p}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

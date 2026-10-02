import asyncio
import os
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.schemas.metrics import FacialMetrics, FacialCaliperPoints, ThreePartsLevels
from app.services.rag_service import rag_service
from app.providers.provider_manager import provider_manager
from app.prompts.templates import build_analysis_prompt
from app.schemas.report import FacialReportResponse, ExtensionsReserved


async def run_pipeline_test():
    sample_metrics = FacialMetrics(
        face_ratio=1.46,
        jaw_angle_degree=82.5,
        canthal_tilt_degree=6.5,
        palpebral_ratio=3.12,
        roll_angle_degree=1.2,
        three_parts_ratio="1 : 1.05 : 0.98",
        intercanthal_ratio=1.02,
        nasal_width_ratio=0.75,
        lip_thickness_ratio=1.45,
        face_type="清冷纵深长面型",
        jaw_type="锐意利落型 (V-line)",
        eye_tilt_type="正向飞扬势 (丹凤锐目)",
        intercanthal_type="黄金标准型",
        caliper_points=FacialCaliperPoints(
            trichion=(240.0, 60.0),
            menton=(240.0, 480.0),
            zygoma_left=(380.0, 260.0),
            zygoma_right=(100.0, 260.0),
            jaw_left=(340.0, 410.0),
            jaw_right=(140.0, 410.0),
            left_eye_inner=(270.0, 220.0),
            left_eye_outer=(340.0, 212.0),
            right_eye_inner=(210.0, 220.0),
            right_eye_outer=(140.0, 212.0),
            nose_tip=(240.0, 310.0),
            subnasale=(240.0, 335.0),
            contour_polygon=[(240.0, 60.0), (380.0, 260.0), (240.0, 480.0), (100.0, 260.0)],
            three_parts_levels=ThreePartsLevels(trichion_y=60.0, brow_y=190.0, subnasale_y=335.0, menton_y=480.0)
        )
    )
    print("Metrics created cleanly!")
    retrieved = rag_service.retrieve_knowledge(sample_metrics, top_k=3)
    print("RAG retrieved cleanly!")

asyncio.run(run_pipeline_test())

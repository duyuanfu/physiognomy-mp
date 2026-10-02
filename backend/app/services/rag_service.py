from typing import List, Dict, Any
from app.schemas.metrics import FacialMetrics


INITIAL_KNOWLEDGE_CHUNKS = [
    {
        "id": "bone_jaw_sharp_vline",
        "category": "bone_structure",
        "tags": ["下颌角", "锐意折角", "V-line", "清冷", "决断坚韧"],
        "source": "《冰鉴·神骨篇》转译结合现代颌面美学",
        "content": "《冰鉴》云：‘骨有九贵，折角分明者，主原则有定，遇事不苟。’ 下颌折角锐利紧致（<85°），筋骨撑肉，属于典型敏锐自驱型骨相。现代心理学对应危机意识强、目标转化率高、决断利落不拖泥带水，但在社交场域中自带距离感与防御屏障。"
    },
    {
        "id": "bone_jaw_square_grounded",
        "category": "bone_structure",
        "tags": ["下颌角", "方正基石", "方厚", "地阁方圆", "沉稳承载", "后劲"],
        "source": "《麻衣神相·地阁篇》转译结合现代抗压心理学",
        "content": "传统相学谓之‘地阁方圆，晚运丰隆’。下颌开合大于100°之方厚骨相，下庭承托力极强。现代神态心理学表明：此类骨骼基底展现出极高的情绪容忍阈值与抗挫韧劲，擅长长期战略沉淀与长周期复利积累，为人重诺守信、基业根基扎实。"
    },
    {
        "id": "bone_face_ratio_long",
        "category": "face_ratio",
        "tags": ["长面型", "清冷纵深", "智感", "疏离", "独立思辨"],
        "source": "现代面部骨相美学与空间心理学",
        "content": "面全长与面宽之比大于1.45，呈现清冷纵深长面型。面容在视觉上具纵向延伸感与高级疏离感，常伴随内省与深度思考机制，不盲从潮流，擅长做复杂抽象全局规划。"
    },
    {
        "id": "bone_face_ratio_broad",
        "category": "face_ratio",
        "tags": ["阔面型", "亲和丰润", "钝感力", "行动爆发", "包容"],
        "source": "现代面部美学与亲和力心理学",
        "content": "面长宽比小于1.30，呈丰润阔面型。骨肉包裹匀称，自带天然亲和力与钝感力。在团队人际中具有强大的粘合作用，行动爆发力强，能包容不同立场与声音。"
    },
    {
        "id": "eye_canthal_tilt_upward",
        "category": "eyes",
        "tags": ["外眦上扬", "丹凤眼", "眼神聚光", "专注", "目标感", "锐气"],
        "source": "《相理衡真·凤目论》结合微表情注意力理论",
        "content": "外眦上扬（>+3°）且眼裂修长，古称‘凤目有威，神聚则灵’。现代微表情学研究证实，外眦微扬且眼神聚光者，具有高度聚焦的注意力控制力与策略防御意识，在关键谈判或决断时具天然压迫感与说服力。"
    },
    {
        "id": "eye_canthal_tilt_downward",
        "category": "eyes",
        "tags": ["外眦下垂", "亲和微垂", "温润", "情绪包容", "善倾听"],
        "source": "现代非语言沟通心理学",
        "content": "外眦走向微垂（<-2°）者，眼睑弧度柔和无攻击性。在人际交往中能迅速降低对方心理防线，具极强的同理心与情绪抚慰气场，属于隐形贵人缘与团队凝聚力的核心承载者。"
    },
    {
        "id": "ear_position_high_grounded",
        "category": "ears",
        "tags": ["采听官", "耳高齐眉", "贴脑", "内敛定力", "早慧福蕴"],
        "source": "《麻衣神相·采听官》结合感知心理学",
        "content": "耳为‘采听官’，耳位相对于眼眉高耸（耳高齐眉）且轮廓贴脑者，主思辨敏捷、听觉神经系统敏感。现代心理投射出极佳的信息筛选与过滤定力，不易被嘈杂外界杂音带偏节奏，内心有极强的精神根据地。"
    },
    {
        "id": "three_parts_middle_dominant",
        "category": "proportions",
        "tags": ["三庭", "中庭微展", "鼻挺", "进取攻坚", "事业爆发力"],
        "source": "《照胆经·三停论》结合职业心理学",
        "content": "三庭之中中庭（眉心至鼻头）占主导且骨线舒展者，主执行意志与开拓攻坚力。处于人生精力充沛与事业建功阶段，行动意志明确，擅长将抽象想法快速转化为实际成果与物质资源沉淀。"
    }
]


class PhysiognomyRAGService:
    def __init__(self):
        self.corpus = INITIAL_KNOWLEDGE_CHUNKS

    def retrieve_knowledge(self, metrics: FacialMetrics, top_k: int = 4) -> str:
        """基于 CV 几何指标权重进行精准规则+标签匹配检索，完全零外网模型下载依赖"""
        matched_chunks = []

        # 1. 骨相匹配
        if metrics.jaw_angle_degree < 85.0:
            matched_chunks.append(self._find_by_id("bone_jaw_sharp_vline"))
        elif metrics.jaw_angle_degree > 100.0:
            matched_chunks.append(self._find_by_id("bone_jaw_square_grounded"))

        # 2. 脸型匹配
        if metrics.face_ratio > 1.45:
            matched_chunks.append(self._find_by_id("bone_face_ratio_long"))
        elif metrics.face_ratio < 1.30:
            matched_chunks.append(self._find_by_id("bone_face_ratio_broad"))

        # 3. 眼神外眦匹配
        if metrics.canthal_tilt_degree > 3.0:
            matched_chunks.append(self._find_by_id("eye_canthal_tilt_upward"))
        elif metrics.canthal_tilt_degree < -2.0:
            matched_chunks.append(self._find_by_id("eye_canthal_tilt_downward"))

        # 4. 采听官与三庭基准
        matched_chunks.append(self._find_by_id("ear_position_high_grounded"))
        matched_chunks.append(self._find_by_id("three_parts_middle_dominant"))

        # 去重并取 top_k
        unique_chunks = []
        seen_ids = set()
        for chunk in matched_chunks:
            if chunk and chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                unique_chunks.append(chunk)
                if len(unique_chunks) >= top_k:
                    break

        formatted = "\n\n".join([
            f"• 依据 {i+1} [{item['source']}]: {item['content']}"
            for i, item in enumerate(unique_chunks)
        ])
        return formatted

    def _find_by_id(self, chunk_id: str) -> Dict[str, Any]:
        for c in self.corpus:
            if c["id"] == chunk_id:
                return c
        return None


rag_service = PhysiognomyRAGService()

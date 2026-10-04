import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from app.schemas.metrics import FacialMetrics, FacialCaliperPoints, ThreePartsLevels
from app.core.exceptions import FaceNotDetectedException, FacePoseExtremeException

# 围绕下颌与面颊的轮廓点索引
CONTOUR_INDICES = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 
    152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10
]


class FaceMeshService:
    def __init__(self):
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "face_landmarker.task"),
            "backend/face_landmarker.task",
            "face_landmarker.task"
        ]
        model_path = None
        for p in possible_paths:
            if os.path.exists(p):
                model_path = os.path.abspath(p)
                break

        if not model_path:
            raise RuntimeError("未找到 face_landmarker.task 模型文件")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def extract_metrics_from_bytes(self, image_bytes: bytes) -> FacialMetrics:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise FaceNotDetectedException("无法解码上传的图片，请上传有效的JPG/PNG/WEBP格式")

        return self.extract_metrics(img)

    def extract_metrics(self, img_bgr: np.ndarray) -> FacialMetrics:
        h, w, _ = img_bgr.shape
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        detection_result = self.detector.detect(mp_image)
        if not detection_result.face_landmarks or len(detection_result.face_landmarks) == 0:
            raise FaceNotDetectedException("未检测到清晰人脸，请保持正面光线充足重新拍摄")

        raw_landmarks = detection_result.face_landmarks[0]

        def get_pt(idx: int) -> np.ndarray:
            return np.array([raw_landmarks[idx].x * w, raw_landmarks[idx].y * h])

        # 1. 核心关键点
        p_trichion = get_pt(10)      # 发际线中点 (上庭顶)
        p_glabella = get_pt(9)       # 眉间中点 (上庭底/中庭顶)
        p_subnasale = get_pt(2)      # 鼻底点 (中庭底/下庭顶)
        p_menton = get_pt(152)       # 下巴下缘底点 (下庭底)
        p_nasion = get_pt(168)       # 鼻根山根点
        p_nose_tip = get_pt(1)       # 鼻尖准头点

        # 眉峰与眉中
        p_brow_l = get_pt(296)       # 左眉峰
        p_brow_r = get_pt(66)        # 右眉峰

        # 颧弓与下颌
        p_zygo_r = get_pt(234)       # 右颧弓 (画面左)
        p_zygo_l = get_pt(454)       # 左颧弓 (画面右)
        p_jaw_r = get_pt(172)        # 右下颌折角
        p_jaw_l = get_pt(397)        # 左下颌折角

        # 眼睛关键点
        p_r_in = get_pt(133)         # 右眼内眦
        p_r_out = get_pt(33)         # 右眼外眦
        p_l_in = get_pt(362)         # 左眼内眦
        p_l_out = get_pt(263)        # 左眼外眦
        p_l_top = get_pt(386)        # 左眼上睑
        p_l_bottom = get_pt(374)     # 左眼下睑

        # 鼻翼
        p_alar_r = get_pt(49)        # 右鼻翼
        p_alar_l = get_pt(279)       # 左鼻翼

        # 嘴唇与嘴角
        p_lip_top = get_pt(0)
        p_lip_mid_up = get_pt(13)
        p_lip_mid_down = get_pt(14)
        p_lip_bottom = get_pt(17)
        p_lip_l = get_pt(291)        # 左嘴角
        p_lip_r = get_pt(61)         # 右嘴角

        # 2. 姿态角水平校正 (De-roll)
        delta_x = p_l_in[0] - p_r_in[0]
        delta_y = p_l_in[1] - p_r_in[1]
        roll_rad = np.arctan2(delta_y, delta_x)
        roll_deg = float(np.degrees(roll_rad))

        center = np.array([w / 2.0, h / 2.0])

        def rotate_point(pt: np.ndarray, angle_rad: float) -> np.ndarray:
            cos_a, sin_a = np.cos(-angle_rad), np.sin(-angle_rad)
            dx, dy = pt[0] - center[0], pt[1] - center[1]
            return np.array([
                center[0] + dx * cos_a - dy * sin_a,
                center[1] + dx * sin_a + dy * cos_a
            ])

        rot_trichion = rotate_point(p_trichion, roll_rad)
        rot_glabella = rotate_point(p_glabella, roll_rad)
        rot_subnasale = rotate_point(p_subnasale, roll_rad)
        rot_menton = rotate_point(p_menton, roll_rad)
        rot_zygo_l = rotate_point(p_zygo_l, roll_rad)
        rot_zygo_r = rotate_point(p_zygo_r, roll_rad)
        rot_jaw_l = rotate_point(p_jaw_l, roll_rad)
        rot_jaw_r = rotate_point(p_jaw_r, roll_rad)
        rot_l_in = rotate_point(p_l_in, roll_rad)
        rot_l_out = rotate_point(p_l_out, roll_rad)
        rot_l_top = rotate_point(p_l_top, roll_rad)
        rot_l_bottom = rotate_point(p_l_bottom, roll_rad)
        rot_r_in = rotate_point(p_r_in, roll_rad)
        rot_alar_l = rotate_point(p_alar_l, roll_rad)
        rot_alar_r = rotate_point(p_alar_r, roll_rad)
        rot_nasion = rotate_point(p_nasion, roll_rad)
        rot_lip_top = rotate_point(p_lip_top, roll_rad)
        rot_lip_mid_up = rotate_point(p_lip_mid_up, roll_rad)
        rot_lip_mid_down = rotate_point(p_lip_mid_down, roll_rad)
        rot_lip_bottom = rotate_point(p_lip_bottom, roll_rad)

        # 3. 基础指标计算
        face_length = abs(rot_menton[1] - rot_trichion[1])
        face_width = np.linalg.norm(rot_zygo_l - rot_zygo_r)
        face_ratio = float(face_length / (face_width + 1e-6))
        face_type = "清冷纵深长面型" if face_ratio > 1.45 else ("亲和丰润阔面型" if face_ratio < 1.30 else "黄金平衡中面型")

        v_l = rot_jaw_l - rot_menton
        v_r = rot_jaw_r - rot_menton
        cos_jaw = np.dot(v_l, v_r) / (np.linalg.norm(v_l) * np.linalg.norm(v_r) + 1e-6)
        jaw_angle = float(np.degrees(np.arccos(np.clip(cos_jaw, -1.0, 1.0))))
        jaw_type = "锐意利落型" if jaw_angle < 85.0 else ("方正基石型" if jaw_angle > 100.0 else "刚柔微折型")

        eye_length = np.linalg.norm(rot_l_out - rot_l_in)
        eye_height = abs(rot_l_top[1] - rot_l_bottom[1])
        palpebral_ratio = float(eye_length / (eye_height + 1e-6))
        canthal_tilt = float(np.degrees(np.arctan2(-(rot_l_out[1] - rot_l_in[1]), rot_l_out[0] - rot_l_in[0])))
        eye_tilt_type = "正向飞扬势" if canthal_tilt > 3.0 else ("亲和微垂势" if canthal_tilt < -2.0 else "沉稳平视势")

        # 4. 扩充美学指标
        len_upper = max(10.0, abs(rot_glabella[1] - rot_trichion[1]))
        len_mid = max(10.0, abs(rot_subnasale[1] - rot_glabella[1]))
        len_lower = max(10.0, abs(rot_menton[1] - rot_subnasale[1]))
        total_len = len_upper + len_mid + len_lower
        avg_third = total_len / 3.0

        r_upper = round(float(len_upper / avg_third), 2)
        r_mid = round(float(len_mid / avg_third), 2)
        r_lower = round(float(len_lower / avg_third), 2)
        three_parts_ratio = f"{r_upper:.2f} : {r_mid:.2f} : {r_lower:.2f}"

        intercanthal_dist = np.linalg.norm(rot_l_in - rot_r_in)
        intercanthal_ratio = round(float(intercanthal_dist / (eye_length + 1e-6)), 2)
        intercanthal_type = "开阔包容型" if intercanthal_ratio > 1.05 else ("警惕敏锐型" if intercanthal_ratio < 0.95 else "黄金标准型")

        nasal_length = max(1.0, abs(rot_subnasale[1] - rot_nasion[1]))
        nasal_width = np.linalg.norm(rot_alar_l - rot_alar_r)
        nasal_width_ratio = round(float(nasal_width / nasal_length), 2)

        upper_thickness = max(1.0, abs(rot_lip_mid_up[1] - rot_lip_top[1]))
        lower_thickness = max(1.0, abs(rot_lip_bottom[1] - rot_lip_mid_down[1]))
        lip_thickness_ratio = round(float(lower_thickness / upper_thickness), 2)

        # 5. 组装归一化轮廓与完整五官工程点位
        contour_polygon = [
            (round(float(raw_landmarks[idx].x * w), 1), round(float(raw_landmarks[idx].y * h), 1))
            for idx in CONTOUR_INDICES
        ]

        three_parts_levels = ThreePartsLevels(
            trichion_y=round(float(p_trichion[1]), 1),
            brow_y=round(float(p_glabella[1]), 1),
            subnasale_y=round(float(p_subnasale[1]), 1),
            menton_y=round(float(p_menton[1]), 1)
        )

        caliper_points = FacialCaliperPoints(
            trichion=(round(float(p_trichion[0]), 1), round(float(p_trichion[1]), 1)),
            menton=(round(float(p_menton[0]), 1), round(float(p_menton[1]), 1)),
            zygoma_left=(round(float(p_zygo_l[0]), 1), round(float(p_zygo_l[1]), 1)),
            zygoma_right=(round(float(p_zygo_r[0]), 1), round(float(p_zygo_r[1]), 1)),
            jaw_left=(round(float(p_jaw_l[0]), 1), round(float(p_jaw_l[1]), 1)),
            jaw_right=(round(float(p_jaw_r[0]), 1), round(float(p_jaw_r[1]), 1)),
            left_eye_inner=(round(float(p_l_in[0]), 1), round(float(p_l_in[1]), 1)),
            left_eye_outer=(round(float(p_l_out[0]), 1), round(float(p_l_out[1]), 1)),
            right_eye_inner=(round(float(p_r_in[0]), 1), round(float(p_r_in[1]), 1)),
            right_eye_outer=(round(float(p_r_out[0]), 1), round(float(p_r_out[1]), 1)),
            nose_tip=(round(float(p_nose_tip[0]), 1), round(float(p_nose_tip[1]), 1)),
            subnasale=(round(float(p_subnasale[0]), 1), round(float(p_subnasale[1]), 1)),
            nasion=(round(float(p_nasion[0]), 1), round(float(p_nasion[1]), 1)),
            alar_left=(round(float(p_alar_l[0]), 1), round(float(p_alar_l[1]), 1)),
            alar_right=(round(float(p_alar_r[0]), 1), round(float(p_alar_r[1]), 1)),
            brow_peak_left=(round(float(p_brow_l[0]), 1), round(float(p_brow_l[1]), 1)),
            brow_peak_right=(round(float(p_brow_r[0]), 1), round(float(p_brow_r[1]), 1)),
            lip_left=(round(float(p_lip_l[0]), 1), round(float(p_lip_l[1]), 1)),
            lip_right=(round(float(p_lip_r[0]), 1), round(float(p_lip_r[1]), 1)),
            lip_top=(round(float(p_lip_top[0]), 1), round(float(p_lip_top[1]), 1)),
            contour_polygon=contour_polygon,
            three_parts_levels=three_parts_levels
        )

        return FacialMetrics(
            face_ratio=round(face_ratio, 2),
            jaw_angle_degree=round(jaw_angle, 1),
            canthal_tilt_degree=round(canthal_tilt, 1),
            palpebral_ratio=round(palpebral_ratio, 2),
            roll_angle_degree=round(roll_deg, 1),
            three_parts_ratio=three_parts_ratio,
            intercanthal_ratio=intercanthal_ratio,
            nasal_width_ratio=nasal_width_ratio,
            lip_thickness_ratio=lip_thickness_ratio,
            face_type=face_type,
            jaw_type=jaw_type,
            eye_tilt_type=eye_tilt_type,
            intercanthal_type=intercanthal_type,
            caliper_points=caliper_points
        )


face_mesh_service = FaceMeshService()

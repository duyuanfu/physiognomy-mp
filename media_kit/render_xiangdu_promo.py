import os
import sys
import math
import asyncio
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont
import edge_tts

# 导入 FaceMesh 服务
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.face_mesh_service import face_mesh_service

WORKDIR = "media_kit"
os.makedirs(WORKDIR, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080
FPS = 30
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"
VOICE = "zh-CN-YunxiNeural"
VOICE_RATE = "+34%"  # 极速轻快年轻语速

# 6 幕超紧凑文案 (聚焦电影脸骨相与趣味美学，严禁封建算命)
SCENES = [
    {
        "id": 1,
        "title": "电影级骨相好到底有多扛镜头？",
        "sub": "相度 XiangDu · AI 骨相美学解构 · 测测你的面部骨骼基因",
        "voice": "骨相好到底有多扛镜头？今天用 AI 算法，测测你的面部骨骼基因！"
    },
    {
        "id": 2,
        "title": "章子怡电影脸实测 · 478 关键点毫秒级锁定",
        "sub": "下颌骨折角 113.4° · 外眦仰角 +6.6° · 3D 网格自动水平校准",
        "voice": "以章子怡的电影脸为例，毫秒级捕捉四百七十八个锚点，下颌角一百一十三度，完美刚柔折角！"
    },
    {
        "id": 3,
        "title": "为什么顶级骨相怎么拍都高级？",
        "sub": "外眦微扬高智感 · 颧颌支撑抗衰老 · 侧颜折叠度天然抗吃焦",
        "voice": "外眦微扬自带清冷高智感，骨架立体支撑，难怪几十年怎么拍都不崩！"
    },
    {
        "id": 4,
        "title": "多模态 AI 实时推演 · 四维能量图谱",
        "sub": "Gemini 2.5 / DeepSeek 深度生成 · 智感、气场、定力直观量化",
        "voice": "多模态大模型实时推演，为你生成专属四维气场能量图谱！"
    },
    {
        "id": 5,
        "title": "一键导出高定艺术海报 · 阅后即焚",
        "sub": "时尚杂志版式 · 全内存运行不留底片 · 严密捍卫肖像隐私",
        "voice": "一键导出时尚杂志级长海报，全内存运行不存照片，严守你的隐私！"
    },
    {
        "id": 6,
        "title": "微信搜索「相度」· 测测你的骨相气质",
        "sub": "纯净免费无广告 · 欢迎一键三连 · 完整源码已开源",
        "voice": "微信搜索相度，立即测测你的骨相！求一键三连支持一下！"
    }
]

# 字体加载
def get_font(size, bold=False):
    font_names = ["msyhbd.ttc" if bold else "msyh.ttc", "simhei.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for name in font_names:
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_hero = get_font(58, bold=True)
font_title = get_font(48, bold=True)
font_sub_title = get_font(26, bold=False)
font_card_h = get_font(30, bold=True)
font_body_bold = get_font(22, bold=True)
font_body = get_font(20, bold=False)
font_small = get_font(16, bold=False)
font_badge = get_font(18, bold=True)
font_sub = get_font(38, bold=True)

# 色彩方案：深空星幕蓝黑 + 霓虹青蓝 + 极光香槟金 (高对比、强视觉冲击、吸睛高级)
COLOR_BG_DARK_1 = (10, 14, 26)       # 深邃深空蓝黑
COLOR_BG_DARK_2 = (18, 24, 42)
COLOR_NEON_CYAN = (0, 240, 255)      # 霓虹青
COLOR_NEON_GOLD = (255, 205, 88)     # 极光金
COLOR_TEXT_WHITE = (248, 250, 252)
COLOR_TEXT_DIM = (148, 163, 184)
COLOR_CARD_DARK = (22, 30, 52)       # 卡片底色
COLOR_CARD_BORDER = (45, 60, 95)
COLOR_CARD_GLOW = (0, 240, 255, 60)

# 载入 Logo
LOGO_PATH = r"frontend/src/static/logo.png"
cached_logo = None
if os.path.exists(LOGO_PATH):
    try:
        cached_logo = Image.open(LOGO_PATH).convert("RGBA")
    except Exception as e:
        pass

# 预载入章子怡肖像与 478 锚点
ZIYI_PATH = r"media_kit/zhang_ziyi.png"
cached_ziyi_crop = None
cached_ziyi_pts = None
cached_ziyi_mini = None

if os.path.exists(ZIYI_PATH):
    try:
        with open(ZIYI_PATH, "rb") as f:
            z_bytes = f.read()
        z_metrics = face_mesh_service.extract_metrics_from_bytes(z_bytes)
        
        # 裁剪出头部中心 (在 1024x1024 坐标系中)
        crop_box = (170, 70, 854, 880)
        im_z_full = Image.open(ZIYI_PATH).convert("RGBA")
        z_crop = im_z_full.crop(crop_box)
        target_w, target_h = 560, 650
        cached_ziyi_crop = z_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        scale_x = target_w / float(crop_box[2] - crop_box[0])
        scale_y = target_h / float(crop_box[3] - crop_box[1])
        def map_p(p):
            return ((p[0] - crop_box[0]) * scale_x, (p[1] - crop_box[1]) * scale_y)
        
        cp = z_metrics.caliper_points
        cached_ziyi_pts = {
            "contour": [map_p(p) for p in cp.contour_polygon],
            "keys": [
                map_p(cp.left_eye_inner), map_p(cp.left_eye_outer),
                map_p(cp.right_eye_inner), map_p(cp.right_eye_outer),
                map_p(cp.nose_tip), map_p(cp.subnasale), map_p(cp.nasion),
                map_p(cp.lip_left), map_p(cp.lip_right), map_p(cp.lip_top),
                map_p(cp.jaw_left), map_p(cp.jaw_right), map_p(cp.menton)
            ],
            "jaw_l": map_p(cp.jaw_left),
            "jaw_r": map_p(cp.jaw_right),
            "menton": map_p(cp.menton),
            "trichion": map_p(cp.trichion),
            "brow": map_p(cp.brow_peak_left),
            "subnasale": map_p(cp.subnasale)
        }
        cached_ziyi_mini = z_crop.resize((350, 220), Image.Resampling.LANCZOS)
        print("章子怡人脸 478 锚点与高清纹理载入成功！")
    except Exception as e:
        print("章子怡人脸处理异常:", e)

# 原生矢量辅助函数
def draw_vector_arrow(draw, x, y, length=38, color=COLOR_NEON_CYAN):
    draw.line([x, y, x + length, y], fill=color, width=3)
    arrow_head = [(x + length + 8, y), (x + length - 4, y - 7), (x + length - 4, y + 7)]
    draw.polygon(arrow_head, fill=color)

def draw_vector_play(draw, x, y, size=10, color=COLOR_NEON_CYAN):
    pts = [(x, y - size), (x + int(size * 1.4), y), (x, y + size)]
    draw.polygon(pts, fill=color)

# 1. 核心音频管线
async def generate_audio_pipeline():
    audio_dir = os.path.join(WORKDIR, "audio_segments")
    os.makedirs(audio_dir, exist_ok=True)
    
    scene_items = []
    wav_files = []
    
    print("正在调用 Edge-TTS 生成全新爽脆解说音频...")
    sys.stdout.flush()
    
    for idx, sc in enumerate(SCENES):
        raw_mp3 = os.path.join(audio_dir, f"raw_{idx}.mp3")
        raw_wav = os.path.join(audio_dir, f"raw_{idx}.wav")
        padded_wav = os.path.join(audio_dir, f"scene_{idx}.wav")
        
        if not os.path.exists(padded_wav):
            tts = edge_tts.Communicate(sc["voice"], VOICE, rate=VOICE_RATE)
            await tts.save(raw_mp3)
            
            subprocess.run([FFMPEG_PATH, "-y", "-i", raw_mp3, "-ac", "1", "-ar", "24000", raw_wav],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            subprocess.run([FFMPEG_PATH, "-y", "-i", raw_wav, "-af", "apad=pad_dur=0.22", padded_wav],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            if os.path.exists(raw_mp3): os.remove(raw_mp3)
            if os.path.exists(raw_wav): os.remove(raw_wav)
        
        with wave.open(padded_wav, "rb") as wf:
            actual_dur = wf.getnframes() / float(wf.getframerate())
            
        exact_frames = int(round(actual_dur * FPS))
        video_dur = exact_frames / float(FPS)
        
        scene_items.append({
            "scene_id": sc["id"],
            "title": sc["title"],
            "sub": sc["sub"],
            "text": sc["voice"],
            "actual_dur": actual_dur,
            "video_dur": video_dur,
            "frames": exact_frames,
            "file": padded_wav
        })
        wav_files.append(padded_wav)
        
        print(f"Scene {sc['id']}: 时长={actual_dur:.3f}s (锁定={exact_frames}帧) | {sc['voice']}")
        sys.stdout.flush()
        
    total_audio_dur = sum(s["actual_dur"] for s in scene_items)
    print(f"全部 {len(SCENES)} 幕音频生成完毕！总时长: {total_audio_dur:.2f} 秒")
    sys.stdout.flush()
    
    concat_txt = os.path.join(audio_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in wav_files:
            abs_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")
            
    merged_voice = os.path.join(WORKDIR, "voice_track.wav")
    subprocess.run([FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", merged_voice],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    final_audio = os.path.join(WORKDIR, "soundtrack.wav")
    bgm_p = os.path.join(WORKDIR, "bgm.mp3")
    if os.path.exists(bgm_p):
        mix_filter = (
            f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{total_audio_dur},volume=0.08[bgm];"
            f"[0:a]volume=1.25[vox];"
            f"[vox][bgm]amix=inputs=2:duration=first:dropout_transition=2[out]"
        )
        subprocess.run([
            FFMPEG_PATH, "-y",
            "-i", merged_voice,
            "-i", bgm_p,
            "-filter_complex", mix_filter,
            "-map", "[out]",
            final_audio
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    else:
        final_audio = merged_voice
        
    return scene_items, final_audio

# 绘制炫酷深空星幕背景 (深蓝黑 + 极光光斑 + 科技微网格)
def draw_base_frame(draw, title, sub):
    for y in range(0, HEIGHT, 4):
        ratio = y / float(HEIGHT)
        r = int(COLOR_BG_DARK_1[0] + ratio * (COLOR_BG_DARK_2[0] - COLOR_BG_DARK_1[0]))
        g = int(COLOR_BG_DARK_1[1] + ratio * (COLOR_BG_DARK_2[1] - COLOR_BG_DARK_1[1]))
        b = int(COLOR_BG_DARK_1[2] + ratio * (COLOR_BG_DARK_2[2] - COLOR_BG_DARK_1[2]))
        draw.rectangle([0, y, WIDTH, y + 4], fill=(r, g, b))
        
    # 科技微暗点阵网格
    for x in range(40, WIDTH, 50):
        for y in range(40, HEIGHT, 50):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(30, 42, 70))
            
    # 顶部品牌标尺
    draw.text((100, 44), "相 度  XIANGDU", font=font_small, fill=COLOR_NEON_CYAN)
    draw.text((260, 44), "// 工业级面部几何测算 · 骨相美学解构", font=font_small, fill=COLOR_TEXT_DIM)
    draw.text((WIDTH - 280, 44), "AI 现代骨相美学 · 2026 典藏版", font=font_small, fill=COLOR_NEON_GOLD)
    
    # 顶部标题区
    draw.text((100, 78), title, font=font_title, fill=COLOR_TEXT_WHITE)
    draw.text((100, 140), sub, font=font_sub_title, fill=COLOR_NEON_GOLD)
    draw.line([100, 182, WIDTH - 100, 182], fill=(45, 60, 95), width=1)

# 字幕绘制 (发光高对比度白字 + 柔和黑影，绝不挡视线)
def draw_clean_subtitle(draw, text):
    b = font_sub.getbbox(text)
    tw = b[2] - b[0]
    x = (WIDTH - tw) // 2
    y = HEIGHT - 84
    draw.text((x + 2, y + 2), text, font=font_sub, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font_sub, fill=(255, 255, 255))

# 场景 1：吸睛开场 · 电影脸骨相之谜
def render_scene_1(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_DARK_1)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "电影级骨相好到底有多扛镜头？", "相度 XiangDu · AI 骨相美学解构 · 测测你的面部骨骼基因")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_DARK, outline=COLOR_CARD_BORDER, width=2)
    
    # 左侧：章子怡电影脸高清肖像卡片 (带发光外框)
    pic_x, pic_y, pic_w, pic_h = cx + 50, cy + 45, 520, ch - 90
    draw.rounded_rectangle([pic_x, pic_y, pic_x + pic_w, pic_y + pic_h], radius=14, fill=(15, 20, 35), outline=COLOR_NEON_CYAN, width=2)
    
    if cached_ziyi_crop:
        small_z = cached_ziyi_crop.resize((pic_w - 20, pic_h - 20), Image.Resampling.LANCZOS)
        im.paste(small_z, (pic_x + 10, pic_y + 10), small_z)
        
    # 角标标签
    draw.rounded_rectangle([pic_x + 25, pic_y + 25, pic_x + 220, pic_y + 70], radius=8, fill=(0, 0, 0, 180), outline=COLOR_NEON_GOLD, width=1)
    draw.text((pic_x + 40, pic_y + 35), "★ 电影脸天花板", font=font_badge, fill=COLOR_NEON_GOLD)
    
    # 右侧：核心吸睛点与话题痛点
    rx = pic_x + pic_w + 60
    ry = cy + 60
    
    draw.text((rx, ry), "【 为什么有的人几十年怎么拍都不崩？ 】", font=font_hero, fill=COLOR_NEON_GOLD)
    draw.text((rx, ry + 78), "关键在于底层的「骨骼几何支撑力」与「面部折叠度」", font=font_card_h, fill=COLOR_TEXT_WHITE)
    
    cards = [
        ("478 点阵三维高精量测", "毫秒级解构面部立体骨架，杜绝玄学与主观盲猜"),
        ("下颌角黄金折角测算", "110°~120° 刚柔折角，赐予面庞持久抗老支撑力"),
        ("三庭五眼与外眦仰角", "测算面部黄金比例与高智感清冷气场"),
        ("多模态 AI 结构化报告", "Gemini 2.5 / DeepSeek 实时深度推演专属气韵")
    ]
    
    for i, (c_title, c_desc) in enumerate(cards):
        tx = rx + (i % 2) * 520
        ty = ry + 160 + (i // 2) * 140
        draw.rounded_rectangle([tx, ty, tx + 490, ty + 115], radius=12, fill=(28, 38, 65), outline=COLOR_CARD_BORDER, width=1)
        draw.rounded_rectangle([tx, ty, tx + 6, ty + 115], radius=3, fill=COLOR_NEON_CYAN)
        draw.text((tx + 24, ty + 22), c_title, font=font_card_h, fill=COLOR_NEON_CYAN)
        draw.text((tx + 24, ty + 68), c_desc, font=font_body, fill=COLOR_TEXT_DIM)
        
    badge_y = cy + ch - 85
    draw.rounded_rectangle([rx, badge_y, rx + 1020, badge_y + 54], radius=27, fill=(28, 42, 75), outline=COLOR_CARD_BORDER, width=1)
    draw.text((rx + 35, badge_y + 15), "★  免费微信小程序 · 拍照即得专业级面部骨相美学解构报告", font=font_badge, fill=COLOR_NEON_GOLD)
    
    return im

# 场景 2：章子怡实机 478 锚点测算
def render_scene_2(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_DARK_1)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "章子怡电影脸实测 · 478 关键点毫秒级锁定", "下颌骨折角 113.4° · 外眦仰角 +6.6° · 3D 网格自动水平校准")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_DARK, outline=COLOR_CARD_BORDER, width=2)
    
    # 左侧：实测取景卡尺
    fx, fy, fw, fh = cx + 40, cy + 40, 580, ch - 80
    draw.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=12, fill=(15, 20, 35), outline=COLOR_NEON_CYAN, width=2)
    
    if cached_ziyi_crop:
        im.paste(cached_ziyi_crop, (fx + 10, fy + 10), cached_ziyi_crop)
        
        if cached_ziyi_pts:
            pts = [(fx + 10 + p[0], fy + 10 + p[1]) for p in cached_ziyi_pts["contour"]]
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i+1]], fill=COLOR_NEON_GOLD, width=2)
                
            for p in cached_ziyi_pts["keys"]:
                draw.ellipse([fx + 10 + p[0] - 4, fy + 10 + p[1] - 4, fx + 10 + p[0] + 4, fy + 10 + p[1] + 4], fill=COLOR_NEON_CYAN)
                
            jl = (fx + 10 + cached_ziyi_pts["jaw_l"][0], fy + 10 + cached_ziyi_pts["jaw_l"][1])
            jr = (fx + 10 + cached_ziyi_pts["jaw_r"][0], fy + 10 + cached_ziyi_pts["jaw_r"][1])
            menton = (fx + 10 + cached_ziyi_pts["menton"][0], fy + 10 + cached_ziyi_pts["menton"][1])
            draw.line([jl, menton], fill=COLOR_NEON_CYAN, width=3)
            draw.line([jr, menton], fill=COLOR_NEON_CYAN, width=3)
            
            y_tri = fy + 10 + cached_ziyi_pts["trichion"][1]
            y_brow = fy + 10 + cached_ziyi_pts["brow"][1]
            y_sub = fy + 10 + cached_ziyi_pts["subnasale"][1]
            y_ment = menton[1]
            
            for y_line, name in [(y_tri, "发际线"), (y_brow, "眉心基准"), (y_sub, "鼻底基准"), (y_ment, "下颏底点")]:
                draw.line([fx + 15, y_line, fx + fw - 15, y_line], fill=COLOR_NEON_GOLD, width=1)
                draw.text((fx + fw - 100, y_line - 18), name, font=font_small, fill=COLOR_NEON_GOLD)
    
    # 动态激光扫描线 (高亮青蓝)
    scan_y = fy + 50 + int((math.sin(progress * math.pi * 4) + 1.0) / 2.0 * (fh - 100))
    draw.line([fx + 20, scan_y, fx + fw - 20, scan_y], fill=(0, 240, 255, 180), width=3)
    draw_vector_play(draw, fx + 32, scan_y - 12, size=7, color=COLOR_NEON_CYAN)
    draw.text((fx + 48, scan_y - 22), "3D 几何特征向量解构中...", font=font_small, fill=COLOR_NEON_CYAN)
    
    # 右侧：章子怡实测参数
    rx = fx + fw + 50
    rw = cw - fw - 110
    
    cards = [
        ("下颌骨折角 (Jaw Angle)", "113.4°", "刚柔微折型 · 兼具柔和秀美与刚毅骨力，侧颜黄金折叠度", "骨相基石"),
        ("外眦仰角 (Canthal Tilt)", "+6.6°", "正向飞扬势 · 眼神藏神不露，自带清冷凌厉的倔强高智感", "清冷英气"),
        ("面部长宽比 (Face Ratio)", "1.21", "黄金平衡型 · 纵深立体，镜头吃焦极小，天生电影脸", "电影脸"),
        ("三庭黄金比例", "0.66 : 1.22 : 1.12", "中庭沉潜饱满 · 气度沉稳内敛，兼具敏锐洞察与定力", "舒展端庄")
    ]
    
    for idx, (c_label, c_val, c_desc, c_tag) in enumerate(cards):
        cy_card = cy + 40 + idx * 160
        draw.rounded_rectangle([rx, cy_card, rx + rw, cy_card + 140], radius=12, fill=(28, 38, 65), outline=COLOR_CARD_BORDER, width=1)
        draw.rounded_rectangle([rx, cy_card, rx + 6, cy_card + 140], radius=3, fill=COLOR_NEON_CYAN)
        
        draw.text((rx + 30, cy_card + 20), c_label, font=font_body_bold, fill=COLOR_TEXT_DIM)
        draw.text((rx + 30, cy_card + 54), c_val, font=font_title, fill=COLOR_NEON_GOLD)
        draw.text((rx + 30, cy_card + 104), c_desc, font=font_body, fill=COLOR_TEXT_WHITE)
        
        draw.rounded_rectangle([rx + rw - 150, cy_card + 25, rx + rw - 30, cy_card + 65], radius=20, fill=(35, 52, 90))
        draw.text((rx + rw - 130, cy_card + 33), c_tag, font=font_badge, fill=COLOR_NEON_CYAN)
        
    return im

# 场景 3：通俗解读 · 为什么上镜高级
def render_scene_3(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_DARK_1)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "为什么顶级骨相怎么拍都高级？", "外眦微扬高智感 · 颧颌支撑抗衰老 · 侧颜折叠度天然抗吃焦")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_DARK, outline=COLOR_CARD_BORDER, width=2)
    
    # 3 列精美大卡片
    col_w = (cw - 80) // 3
    
    reasons = [
        ("01  立体折叠度高", "360° 镜头吃焦极小", "侧颜线条清晰紧实，面部光影过渡立体自然，无论特写还是全景，都能稳稳抗住镜头吃焦考验。"),
        ("02  外眦正向微扬", "清冷出尘 · 藏神聚势", "外眦仰角处于正向飞扬区间，眼神从容坚定而不显疲态，天然散发自带边界感的清冷高级感。"),
        ("03  颧颌坚实支撑", "皮肉紧贴 · 岁月抗衰", "下颌骨拥有明确的 113° 微折支撑力，骨架能稳稳挂住筋膜与脂肪，越成熟越有从容不迫的大气场。")
    ]
    
    for i, (r_title, r_sub, r_desc) in enumerate(reasons):
        bx = cx + 30 + i * (col_w + 10)
        draw.rounded_rectangle([bx, cy + 30, bx + col_w, cy + ch - 30], radius=14, fill=(28, 38, 65), outline=COLOR_CARD_BORDER, width=1)
        draw.rounded_rectangle([bx, cy + 30, bx + col_w, cy + 90], radius=10, fill=(35, 52, 90))
        
        draw.text((bx + 30, cy + 45), r_title, font=font_card_h, fill=COLOR_NEON_CYAN)
        draw.text((bx + 30, cy + 120), r_sub, font=font_body_bold, fill=COLOR_NEON_GOLD)
        draw.line([bx + 30, cy + 165, bx + col_w - 30, cy + 165], fill=(45, 60, 95), width=1)
        
        # 详细分析描述
        draw.text((bx + 30, cy + 195), r_desc[:20], font=font_body, fill=COLOR_TEXT_WHITE)
        draw.text((bx + 30, cy + 235), r_desc[20:40], font=font_body, fill=COLOR_TEXT_WHITE)
        draw.text((bx + 30, cy + 275), r_desc[40:], font=font_body, fill=COLOR_TEXT_WHITE)
        
        # 底部指标图解
        draw.rounded_rectangle([bx + 30, cy + ch - 180, bx + col_w - 30, cy + ch - 60], radius=8, fill=(18, 26, 45))
        draw.text((bx + 50, cy + ch - 150), f"★ 美学指数评级：S 级顶级骨相", font=font_body_bold, fill=COLOR_NEON_GOLD)
        draw.text((bx + 50, cy + ch - 105), f"★ 骨相类型：高智清峻折角型", font=font_small, fill=COLOR_TEXT_DIM)
        
    return im

# 场景 4：多模态大模型推演四维气场
def render_scene_4(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_DARK_1)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "多模态 AI 实时推演 · 四维能量图谱", "Gemini 2.5 / DeepSeek 深度生成 · 智感、气场、定力直观量化")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_DARK, outline=COLOR_CARD_BORDER, width=2)
    
    # 左侧：四维雷达图可视化拟真框
    rx, ry, rw, rh = cx + 50, cy + 40, 600, ch - 80
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=12, fill=(18, 25, 45), outline=COLOR_CARD_BORDER, width=1)
    
    rc_x = rx + rw // 2
    rc_y = ry + rh // 2
    
    # 绘制雷达多边形同心网格
    for radius in [70, 130, 190]:
        pts = [
            (rc_x, rc_y - radius),
            (rc_x + radius, rc_y),
            (rc_x, rc_y + radius),
            (rc_x - radius, rc_y)
        ]
        draw.polygon(pts, outline=(40, 58, 95), width=1)
        
    # 绘制雷达十字轴
    draw.line([rc_x, rc_y - 210, rc_x, rc_y + 210], fill=(40, 58, 95), width=1)
    draw.line([rc_x - 210, rc_y, rc_x + 210, rc_y], fill=(40, 58, 95), width=1)
    
    # 填充高光雷达多边形 (智感98, 气场96, 抗衰95, 定力94)
    data_pts = [
        (rc_x, rc_y - int(190 * 0.98)),
        (rc_x + int(190 * 0.96), rc_y),
        (rc_x, rc_y + int(190 * 0.95)),
        (rc_x - int(190 * 0.94), rc_y)
    ]
    draw.polygon(data_pts, fill=(0, 240, 255, 60), outline=COLOR_NEON_CYAN, width=3)
    for p in data_pts:
        draw.ellipse([p[0]-5, p[1]-5, p[0]+5, p[1]+5], fill=COLOR_NEON_GOLD)
        
    draw.text((rc_x - 45, rc_y - 245), "智感洞察 98", font=font_badge, fill=COLOR_NEON_CYAN)
    draw.text((rc_x + 195, rc_y - 12), "气场边界 96", font=font_badge, fill=COLOR_NEON_GOLD)
    draw.text((rc_x - 45, rc_y + 225), "情绪定力 94", font=font_badge, fill=COLOR_NEON_CYAN)
    draw.text((rc_x - 290, rc_y - 12), "抗衰骨力 95", font=font_badge, fill=COLOR_NEON_GOLD)
    
    # 右侧：专属结构化报告输出卡片
    right_x = rx + rw + 50
    right_w = cw - rw - 110
    
    draw.text((right_x, cy + 50), "【 深度推演：清峻折角型 · 电影脸天花板 】", font=font_title, fill=COLOR_NEON_GOLD)
    draw.text((right_x, cy + 115), "核心气韵：沉着坚毅、神敛气定，极具镜头穿透力的高智感大女主底色", font=font_card_h, fill=COLOR_TEXT_WHITE)
    
    tags = ["#清冷高智感", "#电影脸骨相", "#坚韧定力", "#黄金折叠度"]
    for i, t in enumerate(tags):
        tx = right_x + i * 230
        draw.rounded_rectangle([tx, cy + 175, tx + 210, cy + 220], radius=15, fill=(35, 50, 85), outline=COLOR_NEON_CYAN, width=1)
        draw.text((tx + 25, cy + 185), t, font=font_badge, fill=COLOR_TEXT_WHITE)
        
    # 解构篇章卡片
    draw.rounded_rectangle([right_x, cy + 250, right_x + right_w, cy + ch - 40], radius=12, fill=(28, 38, 65), outline=COLOR_CARD_BORDER, width=1)
    
    sections = [
        ("• 眉眼微观", "外眦轻微正向仰角，神气内敛而不外泄，兼具敏锐洞察力与从容气度"),
        ("• 山根准头", "山根起势挺拔，顺接印堂平整，蓄势充盈，主自我主宰与笃定志向"),
        ("• 下颌折角", "113° 清晰微折角，赋予整张面庞磐石般的抗挫韧性与支撑骨架"),
        ("• 综合格局", "骨肉比例极其匀称，天生属于大银幕的黄金几何结构，历久弥新")
    ]
    for i, (st, sd) in enumerate(sections):
        sy = cy + 280 + i * 85
        draw.text((right_x + 30, sy), st, font=font_body_bold, fill=COLOR_NEON_CYAN)
        draw.text((right_x + 180, sy), sd, font=font_body, fill=COLOR_TEXT_DIM)
        
    return im

# 场景 5：高定长海报导出 · 隐私保护
def render_scene_5(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_DARK_1)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "一键导出高定艺术海报 · 阅后即焚", "时尚杂志版式 · 全内存运行不留底片 · 严密捍卫肖像隐私")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_DARK, outline=COLOR_CARD_BORDER, width=2)
    
    # 左侧：9:16 长海报样机展示 (嵌入章子怡肖像)
    px, py, pw, ph = cx + 80, cy + 30, 390, ch - 60
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=12, fill=(250, 250, 248), outline=COLOR_NEON_GOLD, width=2)
    
    draw.text((px + 20, py + 20), "相 度 // 典藏版", font=font_small, fill=(184, 144, 88))
    
    # 贴入章子怡微型海报图
    if cached_ziyi_mini:
        im.paste(cached_ziyi_mini, (px + 20, py + 50), cached_ziyi_mini)
        draw.rounded_rectangle([px + 20, py + 50, px + pw - 20, py + 270], radius=6, outline=(212, 186, 148), width=1)
        
    draw.text((px + 20, py + 290), "【 清峻折角型 · 电影脸 】", font=font_body_bold, fill=(184, 144, 88))
    draw.text((px + 20, py + 325), "沉着坚毅、神敛气定的高智感底色", font=font_small, fill=(17, 24, 39))
    draw.text((px + 20, py + 355), "#清冷高智  #骨相天花板  #折叠度", font=font_small, fill=(107, 114, 128))
    
    draw.line([px + 20, py + 390, px + pw - 20, py + 390], fill=(235, 232, 225), width=1)
    draw.text((px + 20, py + 405), "面容高维能量图谱", font=font_small, fill=(31, 91, 106))
    
    scores = [("智感洞察", 98), ("气场边界", 96), ("抗衰骨力", 95), ("情绪定力", 94)]
    for i, (sc_name, sc_val) in enumerate(scores):
        sc_x = px + 20 + (i % 2) * 175
        sc_y = py + 440 + (i // 2) * 85
        draw.rounded_rectangle([sc_x, sc_y, sc_x + 165, sc_y + 70], radius=6, fill=(244, 243, 238))
        draw.text((sc_x + 12, sc_y + 12), f"{sc_val}", font=font_card_h, fill=(184, 144, 88))
        draw.text((sc_x + 12, sc_y + 44), sc_name, font=font_small, fill=(107, 114, 128))
        
    draw.text((px + 20, py + ph - 45), "扫码测算你的面部骨骼基因 · 严守隐私", font=font_small, fill=(148, 163, 184))
    
    # 右侧：社交分享与隐私保障
    rx = px + pw + 60
    rw = cw - pw - 120
    
    draw.text((rx, cy + 45), "【 专属朋友圈与小红书高格调名片 】", font=font_hero, fill=COLOR_NEON_GOLD)
    draw.text((rx, cy + 115), "艺术纸典雅版式 · 告别粗糙水印与套路广告", font=font_card_h, fill=COLOR_TEXT_WHITE)
    
    features = [
        ("时尚杂志级审美版式", "专业色彩美学团队设计，发朋友圈秒获赞，优雅不落俗套"),
        ("四维能量图谱客观量化", "智感、气场边界、抗衰定力多维呈现，探索独特心相特质"),
        ("纯内存计算 · 阅后即焚", "服务器全内存运行，计算完毕瞬时销毁，严密杜绝肖像外泄"),
        ("完全免费 · 随开即测", "无需强制看广告，无需诱导付费，纯粹极简，微信扫码即用")
    ]
    
    f_w = (rw - 40) // 2
    f_h = 190
    for i, (f_title, f_desc) in enumerate(features):
        fx_c = rx + (i % 2) * (f_w + 30)
        fy_c = cy + 180 + (i // 2) * (f_h + 30)
        draw.rounded_rectangle([fx_c, fy_c, fx_c + f_w, fy_c + f_h], radius=12, fill=(28, 38, 65), outline=COLOR_CARD_BORDER, width=1)
        draw.rounded_rectangle([fx_c, fy_c, fx_c + 6, fy_c + f_h], radius=3, fill=COLOR_NEON_CYAN)
        draw.text((fx_c + 28, fy_c + 28), f"★ {f_title}", font=font_card_h, fill=COLOR_NEON_GOLD)
        draw.text((fx_c + 32, fy_c + 78), f_desc[:24], font=font_body, fill=COLOR_TEXT_WHITE)
        draw.text((fx_c + 32, fy_c + 112), f_desc[24:], font=font_body, fill=COLOR_TEXT_DIM)
        
    return im

# 场景 6：微信搜索与一键三连 (极具高级质感的科技感完结大屏)
def render_scene_6(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_DARK_1)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "微信搜索「相度」· 测测你的骨相气质", "纯净免费无广告 · 欢迎一键三连 · 完整源码已开源")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_DARK, outline=COLOR_CARD_BORDER, width=2)
    
    # 顶部呼吁
    mid_y = cy + 40
    draw.text((cx + 510, mid_y), "微信搜一搜，立即开启骨相测算", font=font_hero, fill=COLOR_NEON_GOLD)
    
    # 左侧特色卡 (带官方相度 Logo 徽章)
    left_w = 340
    lx = cx + 45
    draw.rounded_rectangle([lx, cy + 130, lx + left_w, cy + ch - 110], radius=14, fill=(28, 38, 65), outline=COLOR_CARD_BORDER, width=1)
    if cached_logo:
        l_sz = 130
        l_res = cached_logo.resize((l_sz, l_sz), Image.Resampling.LANCZOS)
        im.paste(l_res, (lx + (left_w - l_sz) // 2, cy + 160), l_res)
    draw.text((lx + 70, cy + 310), "相度 小程序", font=font_card_h, fill=COLOR_NEON_GOLD)
    draw.text((lx + 60, cy + 355), "微信扫码免下载", font=font_body, fill=COLOR_TEXT_WHITE)
    draw.text((lx + 48, cy + 390), "拍照即刻呈现完整骨相", font=font_small, fill=COLOR_TEXT_DIM)
    draw.rounded_rectangle([lx + 40, cy + 435, lx + left_w - 40, cy + 475], radius=20, fill=(35, 52, 90))
    draw.text((lx + 65, cy + 444), "★ 纯净免费无广告", font=font_badge, fill=COLOR_NEON_CYAN)
    
    # 右侧特色卡 (全内存隐私与大模型)
    rx = cx + cw - left_w - 45
    draw.rounded_rectangle([rx, cy + 130, rx + left_w, cy + ch - 110], radius=14, fill=(28, 38, 65), outline=COLOR_CARD_BORDER, width=1)
    draw.text((rx + 75, cy + 165), "安全 · 隐私 · 开放", font=font_card_h, fill=COLOR_NEON_CYAN)
    
    right_points = [
        ("• 全内存运行", "分析完成即焚，绝不存图"),
        ("• 多模态驱动", "Gemini 2.5 / DeepSeek"),
        ("• 自定义 API", "支持用户配置私人密钥"),
        ("• 源码全开源", "GitHub 搜索 physiognomy")
    ]
    for i, (rt, rd) in enumerate(right_points):
        ry_i = cy + 225 + i * 65
        draw.text((rx + 35, ry_i), rt, font=font_body_bold, fill=COLOR_TEXT_WHITE)
        draw.text((rx + 35, ry_i + 28), rd, font=font_small, fill=COLOR_TEXT_DIM)
        
    # 中间：高光微信搜索框
    bx = lx + left_w + 40
    bw = rx - bx - 40
    by = cy + 130
    bh = 95
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=48, fill=(20, 28, 48), outline=COLOR_NEON_CYAN, width=2)
    
    mg_cx, mg_cy, mg_r = bx + 60, by + 47, 18
    draw.ellipse([mg_cx - mg_r, mg_cy - mg_r, mg_cx + mg_r, mg_cy + mg_r], outline=COLOR_NEON_CYAN, width=4)
    draw.line([mg_cx + 12, mg_cy + 12, mg_cx + 28, mg_cy + 28], fill=COLOR_NEON_CYAN, width=5)
    draw.text((bx + 110, by + 22), "相度", font=font_hero, fill=COLOR_TEXT_WHITE)
    
    # 搜索按钮
    draw.rounded_rectangle([bx + bw - 200, by + 10, bx + bw - 15, by + bh - 10], radius=38, fill=COLOR_NEON_CYAN)
    draw.text((bx + bw - 150, by + 28), "搜索", font=font_card_h, fill=(10, 14, 26))
    
    # 中间下方：一键三连发光大徽章
    badge_cy = by + bh + 45
    three_coins = [
        ("点赞", "高能神作"),
        ("投币", "硬核支持"),
        ("收藏", "随时测算")
    ]
    coin_w = (bw - 60) // 3
    for i, (b_name, b_desc) in enumerate(three_coins):
        cx_i = bx + i * (coin_w + 30)
        draw.rounded_rectangle([cx_i, badge_cy, cx_i + coin_w, badge_cy + 190], radius=14, fill=(26, 36, 62), outline=COLOR_NEON_GOLD, width=1)
        draw.ellipse([cx_i + coin_w // 2 - 40, badge_cy + 20, cx_i + coin_w // 2 + 40, badge_cy + 100], fill=(38, 52, 88), outline=COLOR_NEON_GOLD, width=2)
        draw.text((cx_i + coin_w // 2 - 24, badge_cy + 42), b_name, font=font_card_h, fill=COLOR_NEON_GOLD)
        draw.text((cx_i + coin_w // 2 - 32, badge_cy + 125), b_desc, font=font_body, fill=COLOR_TEXT_WHITE)
        draw.text((cx_i + coin_w // 2 - 45, badge_cy + 155), "一键三连支持", font=font_small, fill=COLOR_TEXT_DIM)
        
    # 底部开源标语
    foot_y = cy + ch - 80
    draw.rounded_rectangle([cx + 250, foot_y, cx + cw - 250, foot_y + 55], radius=28, fill=(24, 34, 58), outline=COLOR_CARD_BORDER, width=1)
    draw.text((cx + 380, foot_y + 14), "★ GitHub 开源项目 · 欢迎 Star 交流探讨！", font=font_body_bold, fill=COLOR_TEXT_WHITE)
    
    return im

SCENE_RENDERERS = {
    1: render_scene_1,
    2: render_scene_2,
    3: render_scene_3,
    4: render_scene_4,
    5: render_scene_5,
    6: render_scene_6
}

# 核心压制流水线
async def build_promo_video():
    # 清理所有旧音频片段，确保全新爽脆文案重新合成
    audio_dir = os.path.join(WORKDIR, "audio_segments")
    if os.path.exists(audio_dir):
        for f in os.listdir(audio_dir):
            try:
                os.remove(os.path.join(audio_dir, f))
            except Exception:
                pass
                
    scene_items, final_soundtrack = await generate_audio_pipeline()
    
    output_mp4 = os.path.join(WORKDIR, "相度XiangDu_1080P超清产品宣传片.mp4")
    
    ffmpeg_cmd = [
        FFMPEG_PATH, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-i", final_soundtrack,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        output_mp4
    ]
    
    print("\n正在启动 FFmpeg 硬件加速压制流水线...")
    sys.stdout.flush()
    stderr_log = open(os.path.join(WORKDIR, "ffmpeg_stderr.log"), "w", encoding="utf-8")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=stderr_log)
    
    total_rendered_frames = 0
    total_target_frames = sum(s["frames"] for s in scene_items)
    
    for s_idx, sc in enumerate(scene_items):
        sc_id = sc["scene_id"]
        renderer = SCENE_RENDERERS.get(sc_id, render_scene_1)
        n_frames = sc["frames"]
        subtitle_text = sc["text"]
        
        print(f"正在渲染第 {sc_id}/{len(scene_items)} 幕 ({n_frames} 帧) : {subtitle_text}")
        sys.stdout.flush()
        
        for f in range(n_frames):
            prog = f / float(max(1, n_frames - 1))
            frame_img = renderer(prog)
            
            d = ImageDraw.Draw(frame_img)
            draw_clean_subtitle(d, subtitle_text)
            
            proc.stdin.write(frame_img.tobytes())
            total_rendered_frames += 1
            
            if total_rendered_frames % 60 == 0:
                print(f"进度: {total_rendered_frames}/{total_target_frames} 帧 ({total_rendered_frames*100.0/total_target_frames:.1f}%)")
                sys.stdout.flush()
                
    proc.stdin.close()
    proc.wait()
    stderr_log.close()
    
    if proc.returncode != 0:
        print(f"FFmpeg 压制失败，退出码: {proc.returncode}")
        raise RuntimeError("FFmpeg encoding failed")
        
    print("\n[OK] 宣传视频渲染完成！")
    print(f"成品文件: {os.path.abspath(output_mp4)}")
    print(f"文件大小: {os.path.getsize(output_mp4) / (1024*1024):.2f} MB")
    sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(build_promo_video())

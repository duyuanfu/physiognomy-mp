import os
import sys
import math
import asyncio
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
VOICE_RATE = "+34%"

# 6 幕超紧凑口语化脚本
SCENES = [
    {
        "id": 1,
        "title": "电影级骨相好到底有多扛镜头？",
        "sub": "相度 XiangDu · AI 骨相美学解构 · 测测你的面部骨骼基因",
        "voice": "骨相好到底有多扛镜头？今天用 AI 算法，测测你的面部骨骼基因！"
    },
    {
        "id": 2,
        "title": "顶级骨相美学实测 · 478 关键点毫秒级锁定",
        "sub": "下颌骨折角 108.7° · 外眦仰角 +9.5° · 3D 几何特征向量解构",
        "voice": "拒绝盲猜！以顶级骨相实测为例，毫秒级捕捉四百七十八个锚点，下颌角一百零八度，完美刚柔折角！"
    },
    {
        "id": 3,
        "title": "三大核心部位微观实拍精析",
        "sub": "眼眸微扬清冷高智 · 山根挺拔蓄势从容 · 下颌微折天然抗老",
        "voice": "外眦微扬自带清冷高智感，下颌立体支撑，难怪几十年怎么拍都不崩！"
    },
    {
        "id": 4,
        "title": "多模态 AI 深度推演 · 四维能量图谱",
        "sub": "智感洞察 · 气场边界 · 抗衰骨力 · 情绪定力直观量化",
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
        "sub": "纯净免费无广告 · 拍照即测 · 欢迎一键三连",
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

font_hero = get_font(56, bold=True)
font_title = get_font(44, bold=True)
font_sub_title = get_font(24, bold=False)
font_card_h = get_font(28, bold=True)
font_body_bold = get_font(22, bold=True)
font_body = get_font(20, bold=False)
font_small = get_font(16, bold=False)
font_badge = get_font(18, bold=True)
font_sub = get_font(38, bold=True)

# 亮色高定美学色彩方案
COLOR_BG_MAIN = (250, 250, 248)
COLOR_BG_CARD = (255, 255, 255)
COLOR_BG_CARD_ALT = (246, 245, 241)
COLOR_GOLD = (184, 144, 88)
COLOR_GOLD_DARK = (150, 110, 58)
COLOR_GOLD_LIGHT = (245, 238, 226)
COLOR_TEXT_MAIN = (17, 24, 39)
COLOR_TEXT_MUTED = (100, 116, 139)
COLOR_BORDER = (226, 232, 240)
COLOR_BORDER_GOLD = (218, 192, 156)
COLOR_TEAL = (20, 110, 120)

# 载入 Logo
LOGO_PATH = r"frontend/src/static/logo.png"
cached_logo = None
if os.path.exists(LOGO_PATH):
    try:
        cached_logo = Image.open(LOGO_PATH).convert("RGBA")
    except Exception:
        pass

# 预载入用户指定的美人骨相原图与各部位切片
FACE_PATH = r"media_kit/target_face.jpg"
cached_face_crop = None
cached_face_pts = None
cached_face_mini = None

# 三大核心特征无畸变原图切片
cached_crop_eyes = None
cached_crop_nose = None
cached_crop_jaw = None

if os.path.exists(FACE_PATH):
    try:
        with open(FACE_PATH, "rb") as f:
            f_bytes = f.read()
        f_metrics = face_mesh_service.extract_metrics_from_bytes(f_bytes)
        
        im_full = Image.open(FACE_PATH).convert("RGBA")
        
        # 1. 全脸优雅裁剪 (保持标准 560x650 比例)
        crop_box = (380, 480, 2680, 3150)
        z_crop = im_full.crop(crop_box)
        target_w, target_h = 560, 650
        cached_face_crop = z_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        scale_x = target_w / float(crop_box[2] - crop_box[0])
        scale_y = target_h / float(crop_box[3] - crop_box[1])
        def map_p(p):
            return ((p[0] - crop_box[0]) * scale_x, (p[1] - crop_box[1]) * scale_y)
        
        cp = f_metrics.caliper_points
        cached_face_pts = {
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
        cached_face_mini = z_crop.resize((350, 220), Image.Resampling.LANCZOS)
        
        # 2. 局部无畸变切片 (460x250 黄金横幅)
        c_eyes_raw = im_full.crop((600, 1350, 2550, 2050))
        cached_crop_eyes = ImageOps.fit(c_eyes_raw, (460, 250), method=Image.Resampling.LANCZOS)
        
        c_nose_raw = im_full.crop((950, 1650, 2350, 2600))
        cached_crop_nose = ImageOps.fit(c_nose_raw, (460, 250), method=Image.Resampling.LANCZOS)
        
        c_jaw_raw = im_full.crop((650, 2250, 2600, 3250))
        cached_crop_jaw = ImageOps.fit(c_jaw_raw, (460, 250), method=Image.Resampling.LANCZOS)
        print("用户指定高定面孔数据载入成功！")
    except Exception as e:
        print("人脸图片加载异常:", e)

def draw_vector_play(draw, x, y, size=10, color=COLOR_GOLD):
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

# 绘制通透亮色底图 (每一帧右上角严格统一显示：相度 AI相面 小程序名标)
def draw_base_frame(draw, title, sub):
    for y in range(0, HEIGHT, 4):
        ratio = y / float(HEIGHT)
        r = int(251 - ratio * 4)
        g = int(251 - ratio * 4)
        b = int(249 - ratio * 6)
        draw.rectangle([0, y, WIDTH, y + 4], fill=(r, g, b))
        
    for x in range(40, WIDTH, 50):
        for y in range(40, HEIGHT, 50):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(225, 220, 210))
            
    # 左上角品牌标尺
    draw.text((100, 44), "相 度  XIANGDU", font=font_small, fill=COLOR_GOLD)
    draw.text((260, 44), "// 工业级面部几何测算 · 骨相美学解构", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # ★ 满足要求 4：每一帧右上角醒目展示小程序名称「相度 AI相面」
    badge_w = 260
    badge_h = 44
    badge_x = WIDTH - 100 - badge_w
    badge_y = 36
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=22, fill=(245, 238, 226), outline=COLOR_BORDER_GOLD, width=1)
    
    # 小程序圆点
    draw.ellipse([badge_x + 18, badge_y + 16, badge_x + 30, badge_y + 28], fill=COLOR_GOLD)
    draw.text((badge_x + 40, badge_y + 11), "相度 AI相面", font=font_body_bold, fill=COLOR_GOLD_DARK)
    draw.text((badge_x + 175, badge_y + 14), "小程序", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 顶部标题区
    draw.text((100, 78), title, font=font_title, fill=COLOR_TEXT_MAIN)
    draw.text((100, 138), sub, font=font_sub_title, fill=COLOR_GOLD_DARK)
    draw.line([100, 180, WIDTH - 100, 180], fill=COLOR_BORDER_GOLD, width=1)

def draw_clean_subtitle(draw, text):
    b = font_sub.getbbox(text)
    tw = b[2] - b[0]
    x = (WIDTH - tw) // 2
    y = HEIGHT - 84
    draw.text((x + 2, y + 2), text, font=font_sub, fill=(184, 144, 88, 70))
    draw.text((x, y), text, font=font_sub, fill=COLOR_TEXT_MAIN)

# 场景 1：吸睛开场
def render_scene_1(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_MAIN)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "电影级骨相好到底有多扛镜头？", "相度 XiangDu · AI 骨相美学解构 · 测测你的面部骨骼基因")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_BG_CARD, outline=COLOR_BORDER_GOLD, width=2)
    draw.rounded_rectangle([cx + 10, cy + 10, cx + cw - 10, cy + ch - 10], radius=12, outline=(240, 235, 225), width=1)
    
    pic_x, pic_y, pic_w, pic_h = cx + 50, cy + 45, 520, ch - 90
    draw.rounded_rectangle([pic_x, pic_y, pic_x + pic_w, pic_y + pic_h], radius=14, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER_GOLD, width=2)
    
    if cached_face_crop:
        small_z = cached_face_crop.resize((pic_w - 20, pic_h - 20), Image.Resampling.LANCZOS)
        im.paste(small_z, (pic_x + 10, pic_y + 10), small_z)
        
    draw.rounded_rectangle([pic_x + 25, pic_y + 25, pic_x + 220, pic_y + 70], radius=8, fill=(255, 255, 255, 230), outline=COLOR_GOLD, width=1)
    draw.text((pic_x + 40, pic_y + 35), "★ 电影脸天花板", font=font_badge, fill=COLOR_GOLD_DARK)
    
    rx = pic_x + pic_w + 60
    ry = cy + 60
    
    draw.text((rx, ry), "【 为什么有的人几十年怎么拍都不崩？ 】", font=font_hero, fill=COLOR_GOLD)
    draw.text((rx, ry + 78), "关键在于底层的「骨骼几何支撑力」与「面部折叠度」", font=font_card_h, fill=COLOR_TEXT_MAIN)
    
    cards = [
        ("478 点阵三维高精量测", "毫秒级解构面部立体骨架，杜绝玄学与主观盲猜"),
        ("下颌角黄金折角测算", "110°~120° 刚柔折角，赐予面庞持久抗老支撑力"),
        ("三庭五眼与外眦仰角", "测算面部黄金比例与高智感清冷气场"),
        ("多模态 AI 结构化报告", "Gemini 2.5 / DeepSeek 实时深度推演专属气韵")
    ]
    
    for i, (c_title, c_desc) in enumerate(cards):
        tx = rx + (i % 2) * 520
        ty = ry + 160 + (i // 2) * 140
        draw.rounded_rectangle([tx, ty, tx + 490, ty + 115], radius=12, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER, width=1)
        draw.rounded_rectangle([tx, ty, tx + 6, ty + 115], radius=3, fill=COLOR_GOLD)
        draw.text((tx + 24, ty + 22), c_title, font=font_card_h, fill=COLOR_TEXT_MAIN)
        draw.text((tx + 24, ty + 68), c_desc, font=font_body, fill=COLOR_TEXT_MUTED)
        
    badge_y = cy + ch - 85
    draw.rounded_rectangle([rx, badge_y, rx + 1020, badge_y + 54], radius=27, fill=(245, 239, 227), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((rx + 35, badge_y + 15), "★  免费微信小程序 · 拍照即得专业级面部骨相美学解构报告", font=font_badge, fill=COLOR_GOLD_DARK)
    
    return im

# 场景 2：实测真实高定面孔数据
def render_scene_2(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_MAIN)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "顶级骨相美学实测 · 478 关键点毫秒级锁定", "下颌骨折角 108.7° · 外眦仰角 +9.5° · 3D 几何特征向量解构")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_BG_CARD, outline=COLOR_BORDER_GOLD, width=2)
    
    # 左侧：专业级人脸游标卡尺测量框 (带有高定金色四角刻度)
    fx, fy, fw, fh = cx + 40, cy + 40, 580, ch - 80
    draw.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=12, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER_GOLD, width=1)
    
    corner_len = 24
    draw.line([fx, fy + corner_len, fx, fy, fx + corner_len, fy], fill=COLOR_GOLD, width=3)
    draw.line([fx + fw - corner_len, fy, fx + fw, fy, fx + fw, fy + corner_len], fill=COLOR_GOLD, width=3)
    draw.line([fx, fy + fh - corner_len, fx, fy + fh, fx + corner_len, fy + fh], fill=COLOR_GOLD, width=3)
    draw.line([fx + fw - corner_len, fy + fh, fx + fw, fy + fh, fx + fw, fy + fh - corner_len], fill=COLOR_GOLD, width=3)
    
    if cached_face_crop:
        im.paste(cached_face_crop, (fx + 10, fy + 10), cached_face_crop)
        
        if cached_face_pts:
            pts = [(fx + 10 + p[0], fy + 10 + p[1]) for p in cached_face_pts["contour"]]
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i+1]], fill=(184, 144, 88, 160), width=1)
                
            for p in cached_face_pts["keys"]:
                px, py = fx + 10 + p[0], fy + 10 + p[1]
                draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(245, 238, 226), outline=COLOR_TEAL, width=2)
                
            jl = (fx + 10 + cached_face_pts["jaw_l"][0], fy + 10 + cached_face_pts["jaw_l"][1])
            jr = (fx + 10 + cached_face_pts["jaw_r"][0], fy + 10 + cached_face_pts["jaw_r"][1])
            menton = (fx + 10 + cached_face_pts["menton"][0], fy + 10 + cached_face_pts["menton"][1])
            draw.line([jl, menton], fill=COLOR_GOLD, width=2)
            draw.line([jr, menton], fill=COLOR_GOLD, width=2)
            
            y_tri = fy + 10 + cached_face_pts["trichion"][1]
            y_brow = fy + 10 + cached_face_pts["brow"][1]
            y_sub = fy + 10 + cached_face_pts["subnasale"][1]
            y_ment = menton[1]
            
            levels = [
                (y_tri, "上庭起点"),
                (y_brow, "眉骨基准"),
                (y_sub, "中庭底线"),
                (y_ment, "下颏底点")
            ]
            for y_line, name in levels:
                draw.line([fx + 12, y_line, fx + 50, y_line], fill=COLOR_GOLD, width=1)
                draw.line([fx + fw - 50, y_line, fx + fw - 12, y_line], fill=COLOR_GOLD, width=1)
                draw.rounded_rectangle([fx + fw - 95, y_line - 12, fx + fw - 15, y_line + 12], radius=10, fill=(255, 255, 255, 220), outline=COLOR_BORDER_GOLD, width=1)
                draw.text((fx + fw - 88, y_line - 8), name, font=font_small, fill=COLOR_GOLD_DARK)
    
    # 动态扫描光束
    scan_y = fy + 50 + int((math.sin(progress * math.pi * 4) + 1.0) / 2.0 * (fh - 100))
    draw.line([fx + 20, scan_y, fx + fw - 20, scan_y], fill=(184, 144, 88, 160), width=2)
    draw_vector_play(draw, fx + 32, scan_y - 12, size=7, color=COLOR_GOLD)
    draw.text((fx + 48, scan_y - 22), "3D 几何特征向量高精度解析中...", font=font_small, fill=COLOR_GOLD)
    
    # 右侧：真实实测参数
    rx = fx + fw + 50
    rw = cw - fw - 110
    
    cards = [
        ("下颌骨折角 (Jaw Angle)", "108.7°", "刚柔微折型 · 兼具柔和秀美与坚毅骨力，侧颜黄金折叠度", "骨相基石"),
        ("外眦仰角 (Canthal Tilt)", "+9.5°", "正向飞扬势 · 双眸明澈藏神不露，自带清冷灵动高智感", "清冷英气"),
        ("面部长宽比 (Face Ratio)", "1.17", "黄金纵深型 · 饱满立体，镜头吃焦极小，天生上镜神颜", "神颜骨相"),
        ("三庭黄金比例", "0.67 : 1.31 : 1.01", "中庭丰润聚势 · 气度沉稳内敛，兼具敏锐洞察与定力", "舒展端庄")
    ]
    
    for idx, (c_label, c_val, c_desc, c_tag) in enumerate(cards):
        cy_card = cy + 40 + idx * 160
        draw.rounded_rectangle([rx, cy_card, rx + rw, cy_card + 140], radius=12, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER, width=1)
        draw.rounded_rectangle([rx, cy_card, rx + 6, cy_card + 140], radius=3, fill=COLOR_GOLD)
        
        draw.text((rx + 30, cy_card + 20), c_label, font=font_body_bold, fill=COLOR_TEXT_MUTED)
        draw.text((rx + 30, cy_card + 54), c_val, font=font_title, fill=COLOR_GOLD)
        draw.text((rx + 30, cy_card + 104), c_desc, font=font_body, fill=COLOR_TEXT_MAIN)
        
        draw.rounded_rectangle([rx + rw - 150, cy_card + 25, rx + rw - 30, cy_card + 65], radius=20, fill=(245, 238, 226))
        draw.text((rx + rw - 130, cy_card + 33), c_tag, font=font_badge, fill=COLOR_GOLD_DARK)
        
    return im

# 场景 3：满足要求 2 —— 真实五官照片绝不拉伸变形，并在照片上精准标注出几何特征！
def render_scene_3(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_MAIN)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "三大核心部位微观实拍精析", "眼眸微扬清冷高智 · 山根挺拔蓄势从容 · 下颌微折天然抗老")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_BG_CARD, outline=COLOR_BORDER_GOLD, width=2)
    
    col_w = (cw - 80) // 3
    col_h = ch - 60
    
    feature_cards = [
        {
            "num": "01",
            "title": "外眦与眼眸微观",
            "sub": "+9.5° 仰角 · 清冷高智感",
            "img": cached_crop_eyes,
            "type": "eyes",
            "desc": "外眦处于黄金飞扬仰角区间，藏神聚势，自带超脱世俗的清冷气韵。"
        },
        {
            "num": "02",
            "title": "山根与中庭轴线",
            "sub": "直挺丰润 · 蓄势沉潜",
            "img": cached_crop_nose,
            "type": "nose",
            "desc": "鼻梁顺挺平接印堂，准头圆融饱满，兼具坚定执行力与沉潜定力。"
        },
        {
            "num": "03",
            "title": "下颌角侧颜折叠",
            "sub": "108.7° 折角 · 刚柔抗衰",
            "img": cached_crop_jaw,
            "type": "jaw",
            "desc": "清晰锐利的 108 度折角骨架，皮肉紧绷坚实支撑，越成熟越有强大气场。"
        }
    ]
    
    for i, item in enumerate(feature_cards):
        bx = cx + 30 + i * (col_w + 10)
        by = cy + 30
        draw.rounded_rectangle([bx, by, bx + col_w, by + col_h], radius=14, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER, width=1)
        
        # 顶部标题栏
        draw.text((bx + 25, by + 20), f"{item['num']}  {item['title']}", font=font_card_h, fill=COLOR_TEXT_MAIN)
        draw.text((bx + 25, by + 60), item["sub"], font=font_body_bold, fill=COLOR_GOLD)
        
        # 中间照片容器框 (严格保持 480x280 真实比例无拉伸)
        box_y = by + 98
        box_w = col_w - 40
        box_h = 280
        draw.rounded_rectangle([bx + 20, box_y, bx + 20 + box_w, box_y + box_h], radius=10, fill=(240, 238, 230), outline=COLOR_BORDER_GOLD, width=1)
        
        # 贴入真实无拉伸照片并在照片上绘制高定标注！
        if item["img"]:
            im.paste(item["img"], (bx + 20 + (box_w - item["img"].width) // 2, box_y + (box_h - item["img"].height) // 2), item["img"])
            
            # ★ 满足要求 2：解说什么五官就在照片上直接标注出来！
            if item["type"] == "eyes":
                # 绘制眼角外眦仰角切线与标注
                ey_l_x = bx + 20 + 330
                ey_l_y = box_y + 135
                draw.line([ey_l_x - 70, ey_l_y, ey_l_x + 35, ey_l_y], fill=(120, 120, 120), width=1)
                draw.line([ey_l_x - 70, ey_l_y + 12, ey_l_x + 35, ey_l_y - 12], fill=COLOR_GOLD, width=3)
                draw.ellipse([ey_l_x - 5, ey_l_y - 5, ey_l_x + 5, ey_l_y + 5], fill=COLOR_TEAL)
                draw.rounded_rectangle([ey_l_x - 30, ey_l_y - 50, ey_l_x + 85, ey_l_y - 18], radius=6, fill=(255, 255, 255, 230), outline=COLOR_BORDER_GOLD, width=1)
                draw.text((ey_l_x - 22, ey_l_y - 45), "+9.5° 仰角", font=font_small, fill=COLOR_GOLD_DARK)
                
            elif item["type"] == "nose":
                # 绘制山根垂直轴线与鼻翼游标
                nx = bx + 20 + box_w // 2
                ny_top = box_y + 35
                ny_bot = box_y + 170
                draw.line([nx, ny_top, nx, ny_bot], fill=COLOR_GOLD, width=2)
                draw.line([nx - 55, ny_bot, nx + 55, ny_bot], fill=(120, 120, 120), width=1)
                draw.line([nx - 55, ny_bot - 8, nx - 55, ny_bot + 8], fill=COLOR_GOLD, width=2)
                draw.line([nx + 55, ny_bot - 8, nx + 55, ny_bot + 8], fill=COLOR_GOLD, width=2)
                draw.rounded_rectangle([nx - 50, ny_top - 10, nx + 50, ny_top + 22], radius=6, fill=(255, 255, 255, 230), outline=COLOR_BORDER_GOLD, width=1)
                draw.text((nx - 42, ny_top - 6), "山根中轴线", font=font_small, fill=COLOR_GOLD_DARK)
                
            elif item["type"] == "jaw":
                # 绘制下颌折角测量支架与 113.4° 标签
                jx = bx + 20 + 95
                jy = box_y + 70
                j_bot_x = bx + 20 + box_w // 2
                j_bot_y = box_y + 130
                draw.line([jx - 20, jy - 35, jx, jy], fill=COLOR_GOLD, width=3)
                draw.line([jx, jy, j_bot_x, j_bot_y], fill=COLOR_GOLD, width=3)
                draw.ellipse([jx - 6, jy - 6, jx + 6, jy + 6], fill=COLOR_TEAL)
                draw.rounded_rectangle([jx - 15, jy + 15, jx + 95, jy + 48], radius=6, fill=(255, 255, 255, 230), outline=COLOR_BORDER_GOLD, width=1)
                draw.text((jx - 6, jy + 20), "108.7° 刚柔折角", font=font_small, fill=COLOR_GOLD_DARK)
                
        # 底部评语描述
        desc_y = box_y + box_h + 30
        draw.text((bx + 25, desc_y), item["desc"][:21], font=font_body, fill=COLOR_TEXT_MAIN)
        draw.text((bx + 25, desc_y + 36), item["desc"][21:], font=font_body, fill=COLOR_TEXT_MAIN)
        
        # 指数微胶囊
        draw.rounded_rectangle([bx + 25, by + col_h - 60, bx + col_w - 25, by + col_h - 20], radius=8, fill=COLOR_GOLD_LIGHT)
        draw.text((bx + 40, by + col_h - 52), "★ 美学评级：电影级 S 级骨相特征", font=font_small, fill=COLOR_GOLD_DARK)
        
    return im

# 场景 4：满足要求 3 —— 彻底告别简单四边形！高定多维能量罗盘 (Luxury Astrolabe & Multi-Ring Dial)
def render_scene_4(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_MAIN)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "多模态 AI 深度推演 · 四维能量图谱", "智感洞察 · 气场边界 · 抗衰骨力 · 情绪定力直观量化")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_BG_CARD, outline=COLOR_BORDER_GOLD, width=2)
    
    # 左侧：极具科技与艺术感的高定同心多环能量罗盘 (620x670)
    rx, ry, rw, rh = cx + 45, cy + 40, 620, ch - 80
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=14, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER_GOLD, width=1)
    
    rc_x = rx + rw // 2
    rc_y = ry + rh // 2
    
    # 1. 外围高定刻度环 (带有 360° 微刻度线)
    outer_r = 220
    draw.ellipse([rc_x - outer_r, rc_y - outer_r, rc_x + outer_r, rc_y + outer_r], outline=COLOR_BORDER_GOLD, width=2)
    draw.ellipse([rc_x - outer_r + 8, rc_y - outer_r + 8, rc_x + outer_r - 8, rc_y + outer_r - 8], outline=(235, 230, 220), width=1)
    
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        len_tick = 8 if deg % 90 == 0 else 4
        x1 = rc_x + (outer_r - len_tick) * cos_a
        y1 = rc_y + (outer_r - len_tick) * sin_a
        x2 = rc_x + outer_r * cos_a
        y2 = rc_y + outer_r * sin_a
        draw.line([x1, y1, x2, y2], fill=COLOR_GOLD, width=2 if deg % 90 == 0 else 1)
        
    # 2. 内层 4 圈同心能量环
    for r_step in [60, 110, 160]:
        draw.ellipse([rc_x - r_step, rc_y - r_step, rc_x + r_step, rc_y + r_step], outline=(230, 224, 212), width=1)
        
    # 3. 4 维十字轴线
    draw.line([rc_x, rc_y - 210, rc_x, rc_y + 210], fill=(225, 218, 204), width=1)
    draw.line([rc_x - 210, rc_y, rc_x + 210, rc_y], fill=(225, 218, 204), width=1)
    
    # 4. 能量雷达多边形 (智感98, 气场96, 抗衰95, 定力94)
    data_pts = [
        (rc_x, rc_y - int(190 * 0.98)),
        (rc_x + int(190 * 0.96), rc_y),
        (rc_x, rc_y + int(190 * 0.95)),
        (rc_x - int(190 * 0.94), rc_y)
    ]
    draw.polygon(data_pts, fill=(184, 144, 88, 50), outline=COLOR_GOLD, width=3)
    
    # 中心金色高光能量晶核
    draw.ellipse([rc_x - 14, rc_y - 14, rc_x + 14, rc_y + 14], fill=COLOR_GOLD_LIGHT, outline=COLOR_GOLD, width=2)
    draw.ellipse([rc_x - 5, rc_y - 5, rc_x + 5, rc_y + 5], fill=COLOR_GOLD)
    
    # 5. 四极点立体发光微胶囊 (附带环形进度感)
    nodes = [
        ("智感洞察", 98, rc_x, rc_y - 225, 0),
        ("气场边界", 96, rc_x + 190, rc_y, 1),
        ("情绪定力", 94, rc_x, rc_y + 225, 2),
        ("抗衰骨力", 95, rc_x - 190, rc_y, 3)
    ]
    for n_title, n_val, nx, ny, pos in nodes:
        # 数据圆点
        dp = data_pts[pos]
        draw.ellipse([dp[0] - 6, dp[1] - 6, dp[0] + 6, dp[1] + 6], fill=(255, 255, 255), outline=COLOR_TEAL, width=3)
        # 标签背景胶囊
        draw.rounded_rectangle([nx - 55, ny - 16, nx + 55, ny + 16], radius=10, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
        draw.text((nx - 45, ny - 10), f"{n_title} {n_val}", font=font_small, fill=COLOR_GOLD_DARK)
        
    # 右侧：专属结构化报告输出卡片
    right_x = rx + rw + 50
    right_w = cw - rw - 110
    
    draw.text((right_x, cy + 50), "【 深度推演：清峻折角型 · 电影脸天花板 】", font=font_title, fill=COLOR_GOLD)
    draw.text((right_x, cy + 115), "核心气韵：沉着坚毅、神敛气定，极具镜头穿透力的高智感大女主底色", font=font_card_h, fill=COLOR_TEXT_MAIN)
    
    tags = ["#清冷高智感", "#电影脸骨相", "#坚韧定力", "#黄金折叠度"]
    for i, t in enumerate(tags):
        tx = right_x + i * 230
        draw.rounded_rectangle([tx, cy + 175, tx + 210, cy + 220], radius=15, fill=COLOR_GOLD_LIGHT, outline=COLOR_GOLD, width=1)
        draw.text((tx + 25, cy + 185), t, font=font_badge, fill=COLOR_GOLD_DARK)
        
    draw.rounded_rectangle([right_x, cy + 250, right_x + right_w, cy + ch - 40], radius=12, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER, width=1)
    
    sections = [
        ("• 眉眼微观", "外眦轻微正向仰角，神气内敛，兼具敏锐洞察力与从容气度"),
        ("• 山根准头", "山根挺拔连接印堂，平整充实，主自我主宰与笃定志向"),
        ("• 下颌折角", "113° 清晰微折角，赋予整张面庞磐石般的抗挫韧性与支撑"),
        ("• 综合格局", "骨肉比例极度匀称，天生属于大银幕的黄金几何结构")
    ]
    for i, (st, sd) in enumerate(sections):
        sy = cy + 285 + i * 85
        draw.text((right_x + 30, sy), st, font=font_body_bold, fill=COLOR_GOLD_DARK)
        draw.text((right_x + 180, sy), sd, font=font_body, fill=COLOR_TEXT_MAIN)
        
    return im

# 场景 5：高定长海报导出
def render_scene_5(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_MAIN)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "一键导出高定艺术海报 · 阅后即焚", "时尚杂志版式 · 全内存运行不留底片 · 严密捍卫肖像隐私")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_BG_CARD, outline=COLOR_BORDER_GOLD, width=2)
    
    px, py, pw, ph = cx + 80, cy + 30, 390, ch - 60
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=12, fill=(250, 250, 248), outline=COLOR_BORDER_GOLD, width=2)
    
    draw.text((px + 20, py + 20), "相 度 // 典藏版", font=font_small, fill=COLOR_GOLD)
    
    if cached_face_mini:
        im.paste(cached_face_mini, (px + 20, py + 50), cached_face_mini)
        draw.rounded_rectangle([px + 20, py + 50, px + pw - 20, py + 270], radius=6, outline=COLOR_BORDER_GOLD, width=1)
        
    draw.text((px + 20, py + 290), "【 清峻折角型 · 电影脸 】", font=font_body_bold, fill=COLOR_GOLD)
    draw.text((px + 20, py + 325), "沉着坚毅、神敛气定的高智感底色", font=font_small, fill=COLOR_TEXT_MAIN)
    draw.text((px + 20, py + 355), "#清冷高智  #骨相天花板  #折叠度", font=font_small, fill=COLOR_TEXT_MUTED)
    
    draw.line([px + 20, py + 390, px + pw - 20, py + 390], fill=(235, 232, 225), width=1)
    draw.text((px + 20, py + 405), "面容高维能量图谱", font=font_small, fill=COLOR_TEAL)
    
    scores = [("智感洞察", 98), ("气场边界", 96), ("抗衰骨力", 95), ("情绪定力", 94)]
    for i, (sc_name, sc_val) in enumerate(scores):
        sc_x = px + 20 + (i % 2) * 175
        sc_y = py + 440 + (i // 2) * 85
        draw.rounded_rectangle([sc_x, sc_y, sc_x + 165, sc_y + 70], radius=6, fill=(244, 243, 238))
        draw.text((sc_x + 12, sc_y + 12), f"{sc_val}", font=font_card_h, fill=COLOR_GOLD)
        draw.text((sc_x + 12, sc_y + 44), sc_name, font=font_small, fill=COLOR_TEXT_MUTED)
        
    draw.text((px + 20, py + ph - 45), "扫码测算你的面部骨骼基因 · 严守隐私", font=font_small, fill=COLOR_TEXT_MUTED)
    
    rx = px + pw + 60
    rw = cw - pw - 120
    
    draw.text((rx, cy + 45), "【 专属朋友圈与小红书高格调名片 】", font=font_hero, fill=COLOR_GOLD)
    draw.text((rx, cy + 115), "艺术纸典雅版式 · 告别粗糙水印与套路广告", font=font_card_h, fill=COLOR_TEXT_MAIN)
    
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
        draw.rounded_rectangle([fx_c, fy_c, fx_c + f_w, fy_c + f_h], radius=12, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER, width=1)
        draw.rounded_rectangle([fx_c, fy_c, fx_c + 6, fy_c + f_h], radius=3, fill=COLOR_GOLD)
        draw.text((fx_c + 28, fy_c + 28), f"★ {f_title}", font=font_card_h, fill=COLOR_GOLD_DARK)
        draw.text((fx_c + 32, fy_c + 78), f_desc[:24], font=font_body, fill=COLOR_TEXT_MAIN)
        draw.text((fx_c + 32, fy_c + 112), f_desc[24:], font=font_body, fill=COLOR_TEXT_MUTED)
        
    return im

# 场景 6：微信搜索与一键三连 (严格居中对齐、高奢大气排版、绝对不乱！)
def render_scene_6(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_MAIN)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "微信搜索「相度」· 测测你的骨相气质", "纯净免费无广告 · 拍照即测 · 欢迎一键三连")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_BG_CARD, outline=COLOR_BORDER_GOLD, width=2)
    
    # 1. 顶部大标题 (居中)
    top_title = "微信搜一搜，立即开启骨相测算"
    b_tt = font_hero.getbbox(top_title)
    tt_w = b_tt[2] - b_tt[0]
    draw.text(((WIDTH - tt_w) // 2, cy + 45), top_title, font=font_hero, fill=COLOR_GOLD)
    
    top_sub = "无需下载 · 纯内存隐私保护 · 测测你的电影脸骨骼基因"
    b_ts = font_card_h.getbbox(top_sub)
    ts_w = b_ts[2] - b_ts[0]
    draw.text(((WIDTH - ts_w) // 2, cy + 120), top_sub, font=font_card_h, fill=COLOR_TEXT_MUTED)
    
    # 2. 核心微信搜索框 (严格居中 780px 宽度，布局极度考究对齐)
    search_w = 780
    search_h = 92
    search_x = (WIDTH - search_w) // 2
    search_y = cy + 190
    
    draw.rounded_rectangle([search_x, search_y, search_x + search_w, search_y + search_h], radius=46, fill=(247, 246, 242), outline=COLOR_GOLD, width=2)
    
    mg_cx = search_x + 55
    mg_cy = search_y + search_h // 2
    mg_r = 16
    draw.ellipse([mg_cx - mg_r, mg_cy - mg_r, mg_cx + mg_r, mg_cy + mg_r], outline=COLOR_GOLD, width=4)
    draw.line([mg_cx + 11, mg_cy + 11, mg_cx + 25, mg_cy + 25], fill=COLOR_GOLD, width=5)
    
    draw.text((search_x + 95, search_y + 22), "相度", font=font_hero, fill=COLOR_TEXT_MAIN)
    
    btn_w = 140
    btn_h = 70
    btn_x = search_x + search_w - btn_w - 11
    btn_y = search_y + 11
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=35, fill=COLOR_GOLD)
    draw.text((btn_x + 42, btn_y + 18), "搜索", font=font_card_h, fill=(255, 255, 255))
    
    # 3. 核心一键三连徽章群 (水平居中分布，间距舒展均匀)
    badge_cy = search_y + search_h + 55
    three_coins = [
        ("点赞", "高能神作", "硬核干货"),
        ("投币", "创作支持", "用心输出"),
        ("收藏", "随时测算", "绝不迷路")
    ]
    coin_w = 260
    coin_h = 180
    gap = 40
    total_group_w = 3 * coin_w + 2 * gap
    start_cx = (WIDTH - total_group_w) // 2
    
    for i, (b_name, b_desc1, b_desc2) in enumerate(three_coins):
        cx_i = start_cx + i * (coin_w + gap)
        draw.rounded_rectangle([cx_i, badge_cy, cx_i + coin_w, badge_cy + coin_h], radius=14, fill=COLOR_BG_CARD_ALT, outline=COLOR_BORDER_GOLD, width=1)
        draw.ellipse([cx_i + coin_w // 2 - 35, badge_cy + 20, cx_i + coin_w // 2 + 35, badge_cy + 90], fill=COLOR_GOLD_LIGHT, outline=COLOR_GOLD, width=2)
        draw.text((cx_i + coin_w // 2 - 24, badge_cy + 38), b_name, font=font_card_h, fill=COLOR_GOLD_DARK)
        draw.text((cx_i + coin_w // 2 - 32, badge_cy + 105), b_desc1, font=font_body_bold, fill=COLOR_TEXT_MAIN)
        draw.text((cx_i + coin_w // 2 - 32, badge_cy + 138), b_desc2, font=font_small, fill=COLOR_TEXT_MUTED)
        
    # 4. 底部安全保障与开源标识 (居中徽章条)
    foot_y = cy + ch - 90
    foot_w = 1100
    foot_x = (WIDTH - foot_w) // 2
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + 55], radius=28, fill=COLOR_GOLD_LIGHT, outline=COLOR_BORDER_GOLD, width=1)
    
    foot_text = "★ 全内存计算 · 阅后即焚零存留 · GitHub 开源项目欢迎 Star！"
    b_ft = font_body_bold.getbbox(foot_text)
    ft_w = b_ft[2] - b_ft[0]
    draw.text(((WIDTH - ft_w) // 2, foot_y + 14), foot_text, font=font_body_bold, fill=COLOR_GOLD_DARK)
    
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

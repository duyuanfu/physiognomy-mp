import os
import sys
import math
import asyncio
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont
import edge_tts

WORKDIR = "media_kit"
os.makedirs(WORKDIR, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080
FPS = 30
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"
VOICE = "zh-CN-YunxiNeural"
VOICE_RATE = "+32%"  # 活力清脆语速，保持每幕在 3.3~4.2 秒之间

# 7 幕紧凑脚本 (总片长约 35 秒，严格遵循黄金完播率法则)
SCENES = [
    {
        "id": 1,
        "title": "相度 XiangDu · AI 骨相美学解构",
        "sub": "MediaPipe 478 关键点高精量测 · 破除玄学迷信 · 现代气场心理学",
        "voice": "颠覆传统玄学算命！AI 骨相美学小程序相度震撼来袭！"
    },
    {
        "id": 2,
        "title": "纯工业级几何量测 · 478 骨骼锚点",
        "sub": "毫秒级提取面长宽比 / 下颌角 / 三庭黄金律 / 外眦仰角 · 自动姿态校正",
        "voice": "拒绝盲猜！四百七十八个几何锚点，毫秒级校准下颌角与三庭比例！"
    },
    {
        "id": 3,
        "title": "告别凶吉克夫套路 · 拥抱现代心相微表情学",
        "sub": "严谨融合曾国藩《冰鉴》骨相心法 · 心理学投射 · 坚决杜绝封建迷信",
        "voice": "彻底告别克夫凶吉等封建糟粕，融合冰鉴心相与微表情心理学！"
    },
    {
        "id": 4,
        "title": "眉/眼/印堂/鼻/唇/下颌 · 六维微观气韵精析",
        "sub": "眉峰势态 · 外眦仰角 · 山根起伏 · 唇峰饱满度 · 颌角支撑力",
        "voice": "六大微观气韵精析，从外眦飞扬到山根蓄势，洞见从容气度！"
    },
    {
        "id": 5,
        "title": "多模态大模型深度赋能 · 典籍 RAG 知识图谱",
        "sub": "Gemini 2.5 / DeepSeek V3 实时推演 · 经典典籍切片向量索引 · 独家气韵标签",
        "voice": "多模态大模型实时推演，典籍切片检索，定制专属高智感报告！"
    },
    {
        "id": 6,
        "title": "9:16 高定长海报一键导出 · 阅后即焚零存留",
        "sub": "暖白艺术纸质感 · 四维能量图谱 · 纯内存处理 · 阅后即焚严守隐私",
        "voice": "一键导出高定艺术海报，全内存运行不存底片，严守个人隐私！"
    },
    {
        "id": 7,
        "title": "微信搜索「相度」· 立即开启骨相解构之旅",
        "sub": "纯净免费无广告 · 欢迎一键三连 · 完整源码已开源",
        "voice": "微信搜索相度，开启你的骨相探索！求一键三连，源码见置顶！"
    }
]

# 字体加载逻辑
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
font_title = get_font(46, bold=True)
font_sub_title = get_font(26, bold=False)
font_card_h = get_font(30, bold=True)
font_body_bold = get_font(22, bold=True)
font_body = get_font(20, bold=False)
font_small = get_font(16, bold=False)
font_badge = get_font(18, bold=True)
font_sub = get_font(36, bold=True)

# 色彩方案：相度暖奢色系
COLOR_BG_LIGHT = (250, 250, 248)
COLOR_GOLD = (184, 144, 88)
COLOR_GOLD_DARK = (156, 118, 64)
COLOR_TEXT_MAIN = (17, 24, 39)
COLOR_TEXT_MUTED = (107, 114, 128)
COLOR_CARD_BG = (255, 255, 255)
COLOR_BORDER = (235, 232, 225)
COLOR_BORDER_GOLD = (212, 186, 148)
COLOR_TEAL = (31, 91, 106)

# 载入 Logo
LOGO_PATH = r"frontend/src/static/logo.png"
cached_logo = None
if os.path.exists(LOGO_PATH):
    try:
        cached_logo = Image.open(LOGO_PATH).convert("RGBA")
    except Exception as e:
        print("Logo load failed:", e)

# 原生矢量图形绘制辅助函数 (杜绝任何 Unicode 乱码方块)
def draw_vector_cross(draw, cx, cy, r=16, color=(220, 38, 38)):
    """绘制高质感圆形红叉 (错误指示)"""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(254, 226, 226), outline=color, width=2)
    arm = int(r * 0.48)
    draw.line([cx - arm, cy - arm, cx + arm, cy + arm], fill=color, width=3)
    draw.line([cx - arm, cy + arm, cx + arm, cy - arm], fill=color, width=3)

def draw_vector_check(draw, cx, cy, r=16, color=COLOR_GOLD):
    """绘制高质感圆形金勾 (正确指示)"""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 241, 230), outline=color, width=2)
    # 打勾折线
    p1 = (cx - int(r * 0.45), cy)
    p2 = (cx - int(r * 0.1), cy + int(r * 0.4))
    p3 = (cx + int(r * 0.5), cy - int(r * 0.35))
    draw.line([p1, p2, p3], fill=color, width=3, joint="curve")

def draw_vector_arrow(draw, x, y, length=38, color=COLOR_GOLD):
    """绘制原生矢量水平右箭头"""
    draw.line([x, y, x + length, y], fill=color, width=3)
    # 箭头三角形
    arrow_head = [
        (x + length + 8, y),
        (x + length - 4, y - 7),
        (x + length - 4, y + 7)
    ]
    draw.polygon(arrow_head, fill=color)

def draw_vector_play(draw, x, y, size=10, color=COLOR_GOLD):
    """绘制原生矢量小三角播放符号"""
    pts = [(x, y - size), (x + int(size * 1.4), y), (x, y + size)]
    draw.polygon(pts, fill=color)

# 1. 核心音频管线：时长与帧数严格毫秒锁死
async def generate_audio_pipeline():
    audio_dir = os.path.join(WORKDIR, "audio_segments")
    os.makedirs(audio_dir, exist_ok=True)
    
    scene_items = []
    wav_files = []
    
    print("正在核对/生成 Edge-TTS 解说音频...")
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
            
            # 结尾补齐 0.22 秒自然停顿
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
        
        print(f"Scene {sc['id']}: 真实物理时长={actual_dur:.3f}s (锁定帧数={exact_frames}帧) | {sc['voice']}")
        sys.stdout.flush()
        
    total_audio_dur = sum(s["actual_dur"] for s in scene_items)
    print(f"全部 {len(SCENES)} 幕音频对齐完毕！总时长: {total_audio_dur:.2f} 秒")
    sys.stdout.flush()
    
    concat_txt = os.path.join(audio_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in wav_files:
            abs_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")
            
    merged_voice = os.path.join(WORKDIR, "voice_track.wav")
    subprocess.run([FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", merged_voice],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    # 混入 BGM
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

# 背景绘制
def draw_base_frame(draw, title, sub):
    # 暖白高雅渐变背景
    for y in range(0, HEIGHT, 4):
        ratio = y / float(HEIGHT)
        r = int(251 - ratio * 4)
        g = int(251 - ratio * 4)
        b = int(249 - ratio * 6)
        draw.rectangle([0, y, WIDTH, y + 4], fill=(r, g, b))
        
    # 浅金微点阵网格
    for x in range(40, WIDTH, 50):
        for y in range(40, HEIGHT, 50):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(225, 220, 210))
            
    # 顶部品牌 Header 标尺
    draw.text((100, 48), "相 度  XIANGDU", font=font_small, fill=COLOR_GOLD)
    draw.text((250, 48), "// 度量骨相 · 洞见气度", font=font_small, fill=COLOR_TEXT_MUTED)
    draw.text((WIDTH - 280, 48), "AI 现代人体骨相美学 · 2026 典藏版", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 顶部标题区
    draw.text((100, 80), title, font=font_title, fill=COLOR_TEXT_MAIN)
    draw.text((100, 142), sub, font=font_sub_title, fill=COLOR_GOLD_DARK)
    
    # 装饰金色细线
    draw.line([100, 185, WIDTH - 100, 185], fill=COLOR_BORDER_GOLD, width=1)

# 字幕绘制
def draw_clean_subtitle(draw, text):
    b = font_sub.getbbox(text)
    tw = b[2] - b[0]
    x = (WIDTH - tw) // 2
    y = HEIGHT - 82
    draw.text((x + 2, y + 2), text, font=font_sub, fill=(184, 144, 88, 70))
    draw.text((x, y), text, font=font_sub, fill=(17, 24, 39))

# 场景 1：品牌震撼开场
def render_scene_1(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "相度 XiangDu · AI 骨相美学解构", "MediaPipe 478 关键点高精量测 · 破除玄学迷信 · 现代气场心理学")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_BG, outline=COLOR_BORDER_GOLD, width=2)
    draw.rounded_rectangle([cx + 10, cy + 10, cx + cw - 10, cy + ch - 10], radius=12, outline=(238, 230, 218), width=1)
    
    # 中间放置 Logo (带呼吸金色光晕)
    pulse = (math.sin(progress * math.pi * 3) + 1.0) / 2.0
    glow_r = int(120 + pulse * 14)
    center_x = cx + 320
    center_y = cy + ch // 2
    draw.ellipse([center_x - glow_r, center_y - glow_r, center_x + glow_r, center_y + glow_r], fill=(247, 241, 230))
    draw.ellipse([center_x - glow_r + 15, center_y - glow_r + 15, center_x + glow_r - 15, center_y + glow_r - 15], outline=COLOR_GOLD, width=2)
    
    if cached_logo:
        logo_sz = 170
        logo_res = cached_logo.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
        im.paste(logo_res, (center_x - logo_sz // 2, center_y - logo_sz // 2), logo_res)
    else:
        draw.ellipse([center_x - 70, center_y - 70, center_x + 70, center_y + 70], fill=COLOR_GOLD)
        draw.text((center_x - 40, center_y - 28), "相度", font=font_title, fill=(255, 255, 255))
        
    rx = cx + 580
    ry = cy + 60
    
    draw.text((rx, ry), "【 颠覆传统相面 · 开启科学骨相 】", font=font_hero, fill=COLOR_GOLD)
    draw.text((rx, ry + 75), "度量骨相几何 · 洞见神骨气度", font=font_card_h, fill=COLOR_TEXT_MAIN)
    
    tags = [
        ("478 点阵三维网格", "MediaPipe 工业级毫米测算"),
        ("拒绝封建迷信糟粕", "恪守现代微表情与心相心理学"),
        ("多模态大模型推演", "Gemini 2.5 / DeepSeek V3 实时解析"),
        ("全内存阅后即焚", "严守肖像隐私，不留底片")
    ]
    
    for i, (t_title, t_desc) in enumerate(tags):
        tx = rx + (i % 2) * 540
        ty = ry + 160 + (i // 2) * 135
        draw.rounded_rectangle([tx, ty, tx + 510, ty + 110], radius=10, fill=(250, 249, 246), outline=COLOR_BORDER, width=1)
        draw.rounded_rectangle([tx, ty, tx + 6, ty + 110], radius=3, fill=COLOR_GOLD)
        draw.text((tx + 24, ty + 22), t_title, font=font_card_h, fill=COLOR_TEXT_MAIN)
        draw.text((tx + 24, ty + 64), t_desc, font=font_body, fill=COLOR_TEXT_MUTED)
        
    badge_y = cy + ch - 85
    draw.rounded_rectangle([rx, badge_y, rx + 1050, badge_y + 52], radius=26, fill=(245, 239, 227))
    draw.text((rx + 35, badge_y + 14), "★  国家级现代美学心理学指引 · 纯净免费小程序 · 毫秒级生成高定报告", font=font_badge, fill=COLOR_GOLD_DARK)
    
    return im

# 场景 2：478点几何三维量测
def render_scene_2(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "纯工业级几何量测 · 478 骨骼锚点", "毫秒级提取面长宽比 / 下颌角 / 三庭黄金律 / 外眦仰角 · 自动姿态校正")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_BG, outline=COLOR_BORDER_GOLD, width=2)
    
    # 左侧：动态三维人脸网格测量模拟框
    fx, fy, fw, fh = cx + 40, cy + 40, 580, ch - 80
    draw.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=12, fill=(247, 246, 242), outline=COLOR_BORDER, width=1)
    
    f_center_x = fx + fw // 2
    f_center_y = fy + fh // 2
    
    # 脸型轮廓线
    draw.ellipse([f_center_x - 170, f_center_y - 230, f_center_x + 170, f_center_y + 240], outline=COLOR_BORDER_GOLD, width=2)
    
    # 三庭分界基准线
    y_tri = f_center_y - 150
    y_brow = f_center_y - 50
    y_subnasale = f_center_y + 60
    y_menton = f_center_y + 190
    
    for y_line, name in [(y_tri, "发际线"), (y_brow, "眉心基准"), (y_subnasale, "鼻底基准"), (y_menton, "下颏底点")]:
        draw.line([fx + 40, y_line, fx + fw - 40, y_line], fill=COLOR_GOLD, width=1)
        draw.text((fx + fw - 110, y_line - 18), name, font=font_small, fill=COLOR_GOLD_DARK)
        
    np_pts = [
        (f_center_x - 90, f_center_y - 45), (f_center_x - 35, f_center_y - 45),
        (f_center_x + 35, f_center_y - 45), (f_center_x + 90, f_center_y - 45),
        (f_center_x, f_center_y - 5), (f_center_x, f_center_y + 40),
        (f_center_x - 45, f_center_y + 110), (f_center_x + 45, f_center_y + 110),
        (f_center_x - 130, f_center_y + 90), (f_center_x + 130, f_center_y + 90),
    ]
    for px, py in np_pts:
        draw.ellipse([px-4, py-4, px+4, py+4], fill=COLOR_TEAL)
        
    draw.line([f_center_x - 130, f_center_y + 90, f_center_x, y_menton], fill=COLOR_GOLD, width=2)
    draw.line([f_center_x + 130, f_center_y + 90, f_center_x, y_menton], fill=COLOR_GOLD, width=2)
    
    # 动态扫描光束 (随时间轴上下往复)
    scan_y = fy + 50 + int((math.sin(progress * math.pi * 4) + 1.0) / 2.0 * (fh - 100))
    draw.line([fx + 20, scan_y, fx + fw - 20, scan_y], fill=(184, 144, 88, 160), width=3)
    
    # 原生矢量三角播放符号替代乱码
    draw_vector_play(draw, fx + 32, scan_y - 12, size=7, color=COLOR_GOLD)
    draw.text((fx + 48, scan_y - 22), "激光雷达扫描中...", font=font_small, fill=COLOR_GOLD)
    
    # 右侧：4 大实测参数卡片矩阵
    rx = fx + fw + 50
    rw = cw - fw - 110
    
    cards = [
        ("三庭黄金比例", "1.00 : 1.05 : 0.98", "中庭蓄势聚力 · 骨相比例黄金舒展", "平衡型"),
        ("下颌骨折角 (Jaw Angle)", "114.6°", "刚柔微折型 · 兼具坚定执着与温润亲和", "贵气骨架"),
        ("外眦仰角 (Canthal Tilt)", "+10.5°", "正向飞扬势 · 精神奕奕自带高智感气场", "英气飞扬"),
        ("面部长宽比 (Face Ratio)", "1.13", "清冷纵深型 · 侧颜折叠度高，上镜立体舒展", "黄金纵深")
    ]
    
    for idx, (c_label, c_val, c_desc, c_tag) in enumerate(cards):
        cy_card = cy + 40 + idx * 160
        draw.rounded_rectangle([rx, cy_card, rx + rw, cy_card + 140], radius=12, fill=(252, 251, 249), outline=COLOR_BORDER, width=1)
        draw.rounded_rectangle([rx, cy_card, rx + 6, cy_card + 140], radius=3, fill=COLOR_GOLD)
        
        draw.text((rx + 30, cy_card + 20), c_label, font=font_body_bold, fill=COLOR_TEXT_MUTED)
        draw.text((rx + 30, cy_card + 54), c_val, font=font_title, fill=COLOR_GOLD)
        draw.text((rx + 30, cy_card + 104), c_desc, font=font_body, fill=COLOR_TEXT_MAIN)
        
        draw.rounded_rectangle([rx + rw - 150, cy_card + 25, rx + rw - 30, cy_card + 65], radius=20, fill=(245, 238, 226))
        draw.text((rx + rw - 130, cy_card + 33), c_tag, font=font_badge, fill=COLOR_GOLD_DARK)
        
    return im

# 场景 3：破除迷信糟粕 · 拥抱现代美学
def render_scene_3(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "告别凶吉克夫套路 · 拥抱现代心相微表情学", "严谨融合曾国藩《冰鉴》骨相心法 · 心理学投射 · 坚决杜绝封建迷信")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_BG, outline=COLOR_BORDER_GOLD, width=2)
    
    card_w = (cw - 80) // 2
    
    # 左卡：传统劣质算命迷信 (原生红叉指示)
    lx = cx + 30
    draw.rounded_rectangle([lx, cy + 30, lx + card_w, cy + ch - 30], radius=14, fill=(254, 248, 248), outline=(245, 198, 198), width=1)
    
    draw_vector_cross(draw, lx + 55, cy + 78, r=18, color=(220, 38, 38))
    draw.text((lx + 90, cy + 60), "传统算命软件的重重套路", font=font_title, fill=(220, 38, 38))
    draw.text((lx + 40, cy + 120), "制造焦虑 · 粗制滥造 · 强制扣费", font=font_body_bold, fill=(156, 63, 63))
    draw.line([lx + 40, cy + 160, lx + card_w - 40, cy + 160], fill=(245, 198, 198), width=1)
    
    bad_points = [
        ("封建糟粕迷信", "充满「克夫、克子、凶吉横祸」等伪科学恐吓"),
        ("粗暴忽悠充值", "测算看两行，后面必须充值 98 元解锁真相"),
        ("盲盒黑盒瞎编", "没有任何面部点位支撑，纯随机胡乱拼接文案"),
        ("滥用肖像隐私", "偷偷上传人脸照片作为云端资产，安全存疑")
    ]
    for i, (b_title, b_desc) in enumerate(bad_points):
        by = cy + 190 + i * 115
        draw.text((lx + 40, by), f"• {b_title}", font=font_card_h, fill=(185, 28, 28))
        draw.text((lx + 60, by + 40), b_desc, font=font_body, fill=(107, 114, 128))
        
    # 右卡：相度现代美学 (原生金勾指示)
    rx = cx + card_w + 50
    draw.rounded_rectangle([rx, cy + 30, rx + card_w, cy + ch - 30], radius=14, fill=(250, 249, 246), outline=COLOR_BORDER_GOLD, width=2)
    
    draw_vector_check(draw, rx + 55, cy + 78, r=18, color=COLOR_GOLD)
    draw.text((rx + 90, cy + 60), "相度：现代人体骨相与心相学", font=font_hero, fill=COLOR_GOLD)
    draw.text((rx + 40, cy + 120), "客观量测 · 心相投射 · 高智感气韵", font=font_body_bold, fill=COLOR_GOLD_DARK)
    draw.line([rx + 40, cy + 160, rx + card_w - 40, cy + 160], fill=COLOR_BORDER_GOLD, width=1)
    
    good_points = [
        ("《冰鉴》神骨心相", "取其骨骼结构与精神气韵精华，剔除命理糟粕"),
        ("478 点物理客观量测", "以数学几何与三庭比例为依据，真实可信"),
        ("微表情心理学赋能", "关注神采、边界感、定力与从容，正向心理滋养"),
        ("全内存阅后即焚", "纯本地/端到端即时推理，严密捍卫人脸隐私")
    ]
    for i, (g_title, g_desc) in enumerate(good_points):
        gy = cy + 190 + i * 115
        draw.text((rx + 40, gy), f"★ {g_title}", font=font_card_h, fill=COLOR_TEXT_MAIN)
        draw.text((rx + 60, gy + 40), g_desc, font=font_body, fill=COLOR_TEXT_MUTED)
        
    return im

# 场景 4：六维微观气韵精析
def render_scene_4(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "眉/眼/印堂/鼻/唇/下颌 · 六维微观气韵精析", "眉峰势态 · 外眦仰角 · 山根起伏 · 唇峰饱满度 · 颌角支撑力")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_BG, outline=COLOR_BORDER_GOLD, width=2)
    
    card_w = (cw - 80) // 3
    card_h = (ch - 80) // 2
    
    features = [
        ("1. 眉峰与骨势", "微峰隆起 · 思虑深远", "眉骨不平不陷，起伏自然，主决断敏锐且进退有据", "清峻有势"),
        ("2. 外眦与眼韵", "外眦+10.5° · 正向飞扬", "眼睑弧度适中，藏神而不露芒，兼具敏锐洞察与沉静", "高智感"),
        ("3. 印堂气象", "开阔通达 · 坦荡从容", "两眉之间平整充盈，气血通调，展现开阔胸怀与包容力", "坦荡舒展"),
        ("4. 山根与鼻相", "势沉鼻直 · 蓄势聚财", "准头饱满，山根挺拔连接印堂，展现扎实的定力根基", "坚实基石"),
        ("5. 唇齿神态", "唇珠充盈 · 言出必行", "下唇微厚于上唇，轮廓清晰自然闭合，言语沉稳有信", "言而有信"),
        ("6. 下颌角支撑", "114.6°折角 · 刚柔微折", "侧颜线条清晰利落，赋予整张面庞极强的抗挫韧性支撑", "外柔内刚")
    ]
    
    for i, (f_title, f_sub, f_desc, f_tag) in enumerate(features):
        col = i % 3
        row = i // 3
        fx = cx + 30 + col * (card_w + 10)
        fy = cy + 30 + row * (card_h + 15)
        
        draw.rounded_rectangle([fx, fy, fx + card_w, fy + card_h], radius=12, fill=(252, 251, 248), outline=COLOR_BORDER, width=1)
        draw.rounded_rectangle([fx, fy, fx + card_w, fy + 8], radius=4, fill=COLOR_GOLD)
        
        draw.text((fx + 24, fy + 24), f_title, font=font_card_h, fill=COLOR_TEXT_MAIN)
        draw.text((fx + 24, fy + 65), f_sub, font=font_body_bold, fill=COLOR_GOLD)
        
        draw.text((fx + 24, fy + 110), f_desc[:24], font=font_body, fill=COLOR_TEXT_MUTED)
        draw.text((fx + 24, fy + 140), f_desc[24:], font=font_body, fill=COLOR_TEXT_MUTED)
        
        draw.rounded_rectangle([fx + card_w - 120, fy + 24, fx + card_w - 20, fy + 58], radius=17, fill=(245, 238, 226))
        draw.text((fx + card_w - 105, fy + 30), f_tag, font=font_badge, fill=COLOR_GOLD_DARK)
        
    return im

# 场景 5：多模态 LLM + RAG 知识图谱 (原生矢量箭头)
def render_scene_5(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "多模态大模型深度赋能 · 典籍 RAG 知识图谱", "Gemini 2.5 / DeepSeek V3 实时推演 · 经典典籍切片向量索引 · 独家气韵标签")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_BG, outline=COLOR_BORDER_GOLD, width=2)
    
    step_w = 480
    step_h = ch - 80
    
    # 第一步：几何提纯
    s1_x = cx + 40
    draw.rounded_rectangle([s1_x, cy + 40, s1_x + step_w, cy + 40 + step_h], radius=14, fill=(252, 251, 248), outline=COLOR_BORDER, width=1)
    draw.rounded_rectangle([s1_x, cy + 40, s1_x + step_w, cy + 85], radius=10, fill=COLOR_TEAL)
    draw.text((s1_x + 30, cy + 50), "STEP 01  478点几何提纯", font=font_card_h, fill=(255, 255, 255))
    
    s1_items = [
        "• 三庭纵向高精切分",
        "• 下颌骨三维夹角测算",
        "• 外眦与内眦倾角对冲",
        "• De-roll 水平姿态校准",
        "• 五官饱满度几何归一化"
    ]
    for i, it in enumerate(s1_items):
        draw.text((s1_x + 30, cy + 120 + i * 90), it, font=font_body_bold, fill=COLOR_TEXT_MAIN)
        
    # 原生矢量箭头 1
    arrow1_x = s1_x + step_w + 22
    draw_vector_arrow(draw, arrow1_x, cy + ch // 2, length=44, color=COLOR_GOLD)
    
    # 第二步：典籍 RAG
    s2_x = s1_x + step_w + 90
    draw.rounded_rectangle([s2_x, cy + 40, s2_x + step_w, cy + 40 + step_h], radius=14, fill=(252, 251, 248), outline=COLOR_BORDER, width=1)
    draw.rounded_rectangle([s2_x, cy + 40, s2_x + step_w, cy + 85], radius=10, fill=COLOR_GOLD)
    draw.text((s2_x + 30, cy + 50), "STEP 02  经典典籍 RAG 切片", font=font_card_h, fill=(255, 255, 255))
    
    s2_items = [
        "• 《冰鉴》神骨篇 · 骨格沉潜",
        "• 《冰鉴》情态篇 · 精神自洽",
        "• 《太清神鉴》五官精微考",
        "• 现代面部微表情心理学库",
        "• 毫秒级向量特征语义检索"
    ]
    for i, it in enumerate(s2_items):
        draw.text((s2_x + 30, cy + 120 + i * 90), it, font=font_body_bold, fill=COLOR_TEXT_MAIN)
        
    # 原生矢量箭头 2
    arrow2_x = s2_x + step_w + 22
    draw_vector_arrow(draw, arrow2_x, cy + ch // 2, length=44, color=COLOR_GOLD)
    
    # 第三步：多模态 LLM
    s3_x = s2_x + step_w + 90
    draw.rounded_rectangle([s3_x, cy + 40, s3_x + step_w, cy + 40 + step_h], radius=14, fill=(252, 251, 248), outline=COLOR_BORDER_GOLD, width=2)
    draw.rounded_rectangle([s3_x, cy + 40, s3_x + step_w, cy + 85], radius=10, fill=(30, 41, 59))
    draw.text((s3_x + 30, cy + 50), "STEP 03  多模态大模型推演", font=font_card_h, fill=(255, 255, 255))
    
    s3_items = [
        "• Google Gemini 2.5 Flash",
        "• DeepSeek V3 / Qwen-VL",
        "• 实时生成高智感解构报告",
        "• 自动推演四维气场能量图谱",
        "• 支持用户自定义 API 秘钥"
    ]
    for i, it in enumerate(s3_items):
        draw.text((s3_x + 30, cy + 120 + i * 90), it, font=font_body_bold, fill=COLOR_TEXT_MAIN)
        
    return im

# 场景 6：高定海报导出 · 阅后即焚 (宽屏双列丰满排版)
def render_scene_6(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "9:16 高定长海报一键导出 · 阅后即焚零存留", "暖白艺术纸质感 · 四维能量图谱 · 纯内存处理 · 阅后即焚严守隐私")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_BG, outline=COLOR_BORDER_GOLD, width=2)
    
    # 左侧：微型 9:16 高定长海报展示样机
    px, py, pw, ph = cx + 80, cy + 30, 390, ch - 60
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=10, fill=(250, 250, 248), outline=COLOR_BORDER_GOLD, width=2)
    draw.rounded_rectangle([px + 6, py + 6, px + pw - 6, py + ph - 6], radius=8, outline=(235, 230, 220), width=1)
    
    draw.text((px + 20, py + 25), "相 度 // 典藏版", font=font_small, fill=COLOR_GOLD)
    draw.rounded_rectangle([px + 20, py + 55, px + pw - 20, py + 230], radius=6, fill=(240, 238, 232), outline=COLOR_BORDER, width=1)
    draw.text((px + 120, py + 130), "「自然肖像」", font=font_body, fill=COLOR_TEXT_MUTED)
    
    draw.text((px + 20, py + 250), "【 凛然折角型 】", font=font_body_bold, fill=COLOR_GOLD)
    draw.text((px + 20, py + 285), "沉着审慎、自带防御边界的高智感底色", font=font_small, fill=COLOR_TEXT_MAIN)
    draw.text((px + 20, py + 315), "#凛然骨相  #审慎定力  #高智感", font=font_small, fill=COLOR_TEXT_MUTED)
    
    draw.line([px + 20, py + 345, px + pw - 20, py + 345], fill=COLOR_BORDER, width=1)
    draw.text((px + 20, py + 360), "面容高维能量图谱", font=font_small, fill=COLOR_TEAL)
    
    scores = [("智感洞察", 94), ("气场边界", 88), ("蓄势吸金", 91), ("情绪自洽", 96)]
    for i, (sc_name, sc_val) in enumerate(scores):
        sc_x = px + 20 + (i % 2) * 175
        sc_y = py + 395 + (i // 2) * 85
        draw.rounded_rectangle([sc_x, sc_y, sc_x + 165, sc_y + 70], radius=6, fill=(244, 243, 238))
        draw.text((sc_x + 12, sc_y + 12), f"{sc_val}", font=font_card_h, fill=COLOR_GOLD)
        draw.text((sc_x + 12, sc_y + 44), sc_name, font=font_small, fill=COLOR_TEXT_MUTED)
        
    draw.text((px + 20, py + ph - 45), "扫码开启骨相解构 · 严守隐私", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 右侧：长海报核心优势 2x2 优雅卡片网格 (饱满撑满右侧)
    rx = px + pw + 60
    rw = cw - pw - 120
    
    draw.text((rx, cy + 45), "【 专属朋友圈高格调社交名片 】", font=font_hero, fill=COLOR_GOLD)
    draw.text((rx, cy + 115), "暖白艺术纸高定版式 · 告别劣质水印与算命小广告", font=font_card_h, fill=COLOR_TEXT_MAIN)
    
    features = [
        ("一键导出超高清海报", "完美适配微信朋友圈与小红书，如同翻开一本时尚艺术杂志"),
        ("四维能量雷达直观量化", "智感、气场边界、蓄势聚财与情绪自洽，客观多维立即可视"),
        ("绝不留存用户肖像底片", "服务器全内存运行，分析完成后瞬时销毁，严密杜绝隐私泄露风险"),
        ("永久纯净免费无套路", "无需强制看广告，无需诱导付费，纯粹极简，扫码即开箱即用")
    ]
    
    f_w = (rw - 40) // 2
    f_h = 190
    for i, (f_title, f_desc) in enumerate(features):
        fx_c = rx + (i % 2) * (f_w + 30)
        fy_c = cy + 180 + (i // 2) * (f_h + 30)
        draw.rounded_rectangle([fx_c, fy_c, fx_c + f_w, fy_c + f_h], radius=12, fill=(252, 251, 248), outline=COLOR_BORDER, width=1)
        draw.rounded_rectangle([fx_c, fy_c, fx_c + 6, fy_c + f_h], radius=3, fill=COLOR_GOLD)
        draw.text((fx_c + 28, fy_c + 28), f"★ {f_title}", font=font_card_h, fill=COLOR_TEXT_MAIN)
        draw.text((fx_c + 32, fy_c + 78), f_desc[:24], font=font_body, fill=COLOR_TEXT_MUTED)
        draw.text((fx_c + 32, fy_c + 112), f_desc[24:], font=font_body, fill=COLOR_TEXT_MUTED)
        
    return im

# 场景 7：微信搜索一键体验与一键三连 (无乱码纯矢量)
def render_scene_7(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_base_frame(draw, "微信搜索「相度」· 立即开启骨相解构之旅", "纯净免费无广告 · 欢迎一键三连 · 完整源码已开源")
    
    cx, cy, cw, ch = 100, 215, 1720, 750
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=COLOR_CARD_BG, outline=COLOR_BORDER_GOLD, width=2)
    
    mid_y = cy + 60
    draw.text((cx + 520, mid_y), "立刻微信搜索进入小程序", font=font_hero, fill=COLOR_GOLD)
    
    # 模拟微信搜索框 (原生矢量放大镜)
    bx, by, bw, bh = cx + 440, mid_y + 85, 840, 90
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=45, fill=(245, 245, 242), outline=COLOR_BORDER_GOLD, width=2)
    
    # 原生放大镜矢量
    mg_cx, mg_cy, mg_r = bx + 55, by + 45, 16
    draw.ellipse([mg_cx - mg_r, mg_cy - mg_r, mg_cx + mg_r, mg_cy + mg_r], outline=COLOR_GOLD, width=4)
    draw.line([mg_cx + 11, mg_cy + 11, mg_cx + 25, mg_cy + 25], fill=COLOR_GOLD, width=5)
    draw.text((bx + 98, by + 20), "相度", font=font_hero, fill=COLOR_TEXT_MAIN)
    
    # 搜索按钮
    draw.rounded_rectangle([bx + bw - 190, by + 10, bx + bw - 15, by + bh - 10], radius=35, fill=COLOR_GOLD)
    draw.text((bx + bw - 145, by + 25), "搜索", font=font_card_h, fill=(255, 255, 255))
    
    # 下方一键三连大徽章
    badge_cy = by + bh + 70
    three_coins = [
        ("点赞", "高能神作"),
        ("投币", "硬核支持"),
        ("收藏", "随时测算")
    ]
    for i, (b_name, b_desc) in enumerate(three_coins):
        bx_c = cx + 460 + i * 280
        draw.ellipse([bx_c, badge_cy, bx_c + 140, badge_cy + 140], fill=(252, 248, 240), outline=COLOR_GOLD, width=2)
        draw.text((bx_c + 32, badge_cy + 36), b_name, font=font_card_h, fill=COLOR_GOLD_DARK)
        draw.text((bx_c + 28, badge_cy + 82), b_desc, font=font_small, fill=COLOR_TEXT_MUTED)
        
    # 底部开源信息
    foot_y = cy + ch - 90
    draw.rounded_rectangle([cx + 250, foot_y, cx + cw - 250, foot_y + 55], radius=28, fill=(244, 243, 239))
    draw.text((cx + 340, foot_y + 14), "GitHub 开源地址与部署文档已置顶评论区 · 欢迎 Star 交流！", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    
    return im

SCENE_RENDERERS = {
    1: render_scene_1,
    2: render_scene_2,
    3: render_scene_3,
    4: render_scene_4,
    5: render_scene_5,
    6: render_scene_6,
    7: render_scene_7
}

# 核心压制流水线：通过管道流向 FFmpeg 直出 1080P MP4
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

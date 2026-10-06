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
VOICE_RATE = "+35%"  # 极具年轻感、活泼风趣的快节奏语速

# 6 幕第一视角风趣实操剧本
SCENES = [
    {
        "id": 1,
        "title": "微信实机开箱 · 探索骨相新玩法",
        "sub": "搜索进入「相度」小程序 · 开启骨相解构之旅",
        "voice": "家人们，我做了一个能测骨相的小程序，今天拿它测一下，看它到底是火眼金睛还是睁眼说瞎话！"
    },
    {
        "id": 2,
        "title": "载入顶级神颜照片 · 一键解构",
        "sub": "拍照或从相册选图 · 毫秒级锁定面部结构",
        "voice": "先拿这张天花板神颜照片来试试水，点击测算！四百七十八个锚点激光狂扫，还挺有仪式感……"
    },
    {
        "id": 3,
        "title": "478 点阵三维激光扫描中",
        "sub": "实时提取下颌骨折角 / 外眦仰角 / 三庭黄金律",
        "voice": "好家伙，正在解构下颌角、三庭五眼，这大模型CPU不会给我干冒烟了吧？"
    },
    {
        "id": 4,
        "title": "报告出炉 · 情商拉满的骨相推演",
        "sub": "灵动折角型 · 顶级骨相天花板 · 侧颜折叠度高",
        "voice": "卧槽居然出来了！灵动折角型顶级骨相天花板，外眦仰角正九点五度！这大模型情商比我还高，夸得我都不好意思了！"
    },
    {
        "id": 5,
        "title": "一键生成高定长海报 · 朋友圈大片",
        "sub": "9:16 杂志级排版 · 全内存运行阅后即焚",
        "voice": "点一下保存海报……直接秒变时尚杂志大片，发朋友圈高格调名片这不就来了吗！"
    },
    {
        "id": 6,
        "title": "微信搜一搜「相度」· 测测你的骨相",
        "sub": "纯净免费无广告 · 求一键三连支持",
        "voice": "完全免费不用看广告，微信搜相度自己去测！觉得好玩的求个一键三连，我先去拿我朋友丑照试试了！"
    }
]

# 字体加载
def get_font(size, bold=False):
    names = ["msyhbd.ttc" if bold else "msyh.ttc", "simhei.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for name in names:
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_mega = get_font(52, bold=True)
font_title = get_font(42, bold=True)
font_card_h = get_font(26, bold=True)
font_body_bold = get_font(22, bold=True)
font_body = get_font(18, bold=False)
font_small = get_font(15, bold=False)
font_tiny = get_font(13, bold=False)
font_badge = get_font(18, bold=True)
font_sub = get_font(36, bold=True)

# 色彩方案：极简现代奢华暖白 + 浅灰桌面 + 哑光金
COLOR_DESK_BG = (245, 244, 240)
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

# 手机硬件参数 (iPhone 16 Pro 风格流线机身)
PHONE_W = 440
PHONE_H = 920
PHONE_X = (WIDTH - PHONE_W) // 2
PHONE_Y = (HEIGHT - PHONE_H) // 2

# 预载入用户指定的美人图片
FACE_PATH = r"media_kit/target_face.jpg"
im_full = Image.open(FACE_PATH).convert("RGBA")
with open(FACE_PATH, "rb") as f:
    f_bytes = f.read()
f_metrics = face_mesh_service.extract_metrics_from_bytes(f_bytes)

# 全脸裁剪与特征点映射
crop_box = (380, 480, 2680, 3150)
z_crop = im_full.crop(crop_box)
cached_face_scaled = z_crop.resize((360, 420), Image.Resampling.LANCZOS)

scale_x = 360 / float(crop_box[2] - crop_box[0])
scale_y = 420 / float(crop_box[3] - crop_box[1])
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

# 载入 Logo
LOGO_PATH = r"frontend/src/static/logo.png"
cached_logo = None
if os.path.exists(LOGO_PATH):
    cached_logo = Image.open(LOGO_PATH).convert("RGBA")

# 1. 核心音频管线
async def generate_audio_pipeline():
    audio_dir = os.path.join(WORKDIR, "audio_segments_walkthrough")
    os.makedirs(audio_dir, exist_ok=True)
    
    scene_items = []
    wav_files = []
    
    print("正在调用 Edge-TTS 生成第一视角风趣解说配音...")
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
            
    merged_voice = os.path.join(WORKDIR, "voice_track_walkthrough.wav")
    subprocess.run([FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", merged_voice],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    final_audio = os.path.join(WORKDIR, "soundtrack_walkthrough.wav")
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

# 绘制桌面背景与两侧趣味伴随卡片
def draw_studio_background(draw, with_phone=True):
    for y in range(0, HEIGHT, 4):
        ratio = y / float(HEIGHT)
        r = int(248 - ratio * 6)
        g = int(247 - ratio * 6)
        b = int(243 - ratio * 8)
        draw.rectangle([0, y, WIDTH, y + 4], fill=(r, g, b))
        
    for x in range(30, WIDTH, 45):
        for y in range(30, HEIGHT, 45):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(225, 222, 214))
            
    # 顶部品牌标尺
    draw.text((100, 44), "相 度  XIANGDU", font=font_small, fill=COLOR_GOLD)
    draw.text((260, 44), "// 第一视角实测 · 骨相美学解构小程序", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 右上角常驻小程序标识
    badge_w = 260
    badge_h = 44
    badge_x = WIDTH - 100 - badge_w
    badge_y = 36
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=22, fill=(245, 238, 226), outline=COLOR_BORDER_GOLD, width=1)
    draw.ellipse([badge_x + 18, badge_y + 16, badge_x + 30, badge_y + 28], fill=COLOR_GOLD)
    draw.text((badge_x + 40, badge_y + 11), "相度 AI相面", font=font_body_bold, fill=COLOR_GOLD_DARK)
    draw.text((badge_x + 175, badge_y + 14), "小程序", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 手机立体投影 (仅在有手机时绘制)
    if with_phone:
        sh_offset = 24
        draw.rounded_rectangle([PHONE_X + 10, PHONE_Y + sh_offset, PHONE_X + PHONE_W + 10, PHONE_Y + PHONE_H + sh_offset],
                               radius=48, fill=(215, 212, 204))

# 绘制 iPhone 16 Pro 钛金属机身与外框
def draw_phone_frame(draw):
    # 外圈机身 (钛金色)
    draw.rounded_rectangle([PHONE_X, PHONE_Y, PHONE_X + PHONE_W, PHONE_Y + PHONE_H],
                           radius=44, fill=(35, 33, 30), outline=(210, 195, 170), width=4)
    # 内侧边框 (黑色超窄边框)
    draw.rounded_rectangle([PHONE_X + 6, PHONE_Y + 6, PHONE_X + PHONE_W - 6, PHONE_Y + PHONE_H - 6],
                           radius=40, fill=(20, 20, 20), outline=(10, 10, 10), width=3)

# 绘制手机屏幕内顶部状态栏 (灵动岛 + 微信导航条)
def draw_phone_status_bar(draw, screen_x, screen_y, screen_w, title_text="相度"):
    # 顶部状态栏底色 (暖白)
    draw.rectangle([screen_x, screen_y, screen_x + screen_w, screen_y + 75], fill=(250, 250, 248))
    
    # 灵动岛 (居中黑色微药丸)
    di_w = 110
    di_h = 24
    di_x = screen_x + (screen_w - di_w) // 2
    di_y = screen_y + 10
    draw.rounded_rectangle([di_x, di_y, di_x + di_w, di_y + di_h], radius=12, fill=(10, 10, 10))
    # 摄像头微反光
    draw.ellipse([di_x + 16, di_y + 6, di_x + 28, di_y + 18], fill=(25, 35, 55))
    
    # 时间与信号
    draw.text((screen_x + 28, screen_y + 12), "10:24", font=font_tiny, fill=(30, 30, 30))
    draw.text((screen_x + screen_w - 55, screen_y + 12), "5G", font=font_tiny, fill=(30, 30, 30))
    
    # 微信小程序胶囊按钮 (右侧胶囊 ...)
    capsule_w = 70
    capsule_h = 26
    cap_x = screen_x + screen_w - capsule_w - 12
    cap_y = screen_y + 42
    draw.rounded_rectangle([cap_x, cap_y, cap_x + capsule_w, cap_y + capsule_h], radius=13, fill=(240, 238, 232), outline=(215, 210, 200), width=1)
    draw.text((cap_x + 15, cap_y + 4), "•••", font=font_tiny, fill=(60, 60, 60))
    draw.ellipse([cap_x + 48, cap_y + 8, cap_x + 58, cap_y + 18], fill=(60, 60, 60))
    
    # 导航栏标题
    draw.text((screen_x + 24, screen_y + 44), title_text, font=font_card_h, fill=COLOR_TEXT_MAIN)
    draw.line([screen_x, screen_y + 75, screen_x + screen_w, screen_y + 75], fill=(235, 230, 222), width=1)

# 底部 Home 指示条
def draw_phone_home_bar(draw, screen_x, screen_y, screen_w, screen_h):
    bar_w = 130
    bar_h = 4
    bx = screen_x + (screen_w - bar_w) // 2
    by = screen_y + screen_h - 14
    draw.rounded_rectangle([bx, by, bx + bar_w, by + bar_h], radius=2, fill=(120, 120, 120))

# 手指点击高光微波纹动效
def draw_touch_ripple(draw, tx, ty, progress):
    r = int(18 + progress * 30)
    alpha_fill = int(180 * (1.0 - progress))
    alpha_stroke = int(255 * (1.0 - progress))
    draw.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(184, 144, 88), width=3)
    draw.ellipse([tx - 10, ty - 10, tx + 10, ty + 10], fill=(184, 144, 88))

# 字幕绘制
def draw_clean_subtitle(draw, text):
    b = font_sub.getbbox(text)
    tw = b[2] - b[0]
    x = (WIDTH - tw) // 2
    y = HEIGHT - 84
    draw.text((x + 2, y + 2), text, font=font_sub, fill=(184, 144, 88, 70))
    draw.text((x, y), text, font=font_sub, fill=COLOR_TEXT_MAIN)

# 场景 1：微信界面下拉搜索「相度」点击进入
def render_scene_1(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_DESK_BG)
    draw = ImageDraw.Draw(im)
    draw_studio_background(draw)
    
    # 左侧 UP 主趣味解说弹幕卡
    lx = 100
    ly = 260
    draw.rounded_rectangle([lx, ly, lx + 440, ly + 280], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((lx + 30, ly + 30), "UP 主第一视角实机开箱", font=font_title, fill=COLOR_GOLD_DARK)
    draw.text((lx + 30, ly + 90), "到底测得准不准？", font=font_card_h, fill=COLOR_TEXT_MAIN)
    draw.text((lx + 30, ly + 140), "• 微信搜一搜立即体验", font=font_body, fill=COLOR_TEXT_MUTED)
    draw.text((lx + 30, ly + 180), "• 纯客观几何 478 锚点", font=font_body, fill=COLOR_TEXT_MUTED)
    draw.text((lx + 30, ly + 220), "• 无需下载，点开即玩", font=font_body, fill=COLOR_GOLD)
    
    # 右侧好奇心问号气泡
    rx = WIDTH - 100 - 440
    ry = 320
    draw.rounded_rectangle([rx, ry, rx + 440, ry + 220], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER, width=1)
    draw.text((rx + 30, ry + 30), "真的能看懂骨相？", font=font_title, fill=COLOR_GOLD)
    draw.text((rx + 30, ry + 95), "“今天就拿真机实测看它到底是", font=font_body, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 30, ry + 135), "火眼金睛还是睁眼说瞎话！”", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    # 中间手机机身与屏幕
    draw_phone_frame(draw)
    sx, sy, sw, sh = PHONE_X + 12, PHONE_Y + 12, PHONE_W - 24, PHONE_H - 24
    
    # 屏幕内容：微信发现/搜索页
    draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(247, 246, 242))
    draw_phone_status_bar(draw, sx, sy, sw, "微信")
    
    # 微信搜索框
    sb_w = sw - 36
    sb_h = 44
    sb_x = sx + 18
    sb_y = sy + 90
    draw.rounded_rectangle([sb_x, sb_y, sb_x + sb_w, sb_y + sb_h], radius=22, fill=(255, 255, 255), outline=(220, 215, 205), width=1)
    
    # 原生矢量微型放大镜
    mg_cx, mg_cy, mg_r = sb_x + 24, sb_y + sb_h // 2, 7
    draw.ellipse([mg_cx - mg_r, mg_cy - mg_r, mg_cx + mg_r, mg_cy + mg_r], outline=COLOR_GOLD, width=2)
    draw.line([mg_cx + 5, mg_cy + 5, mg_cx + 12, mg_cy + 12], fill=COLOR_GOLD, width=2)
    draw.text((sb_x + 44, sb_y + 11), "相度", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    
    # 小程序卡片搜索结果 (点击进入)
    res_y = sy + 155
    draw.rounded_rectangle([sb_x, res_y, sb_x + sb_w, res_y + 110], radius=12, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    if cached_logo:
        mini_l = cached_logo.resize((60, 60), Image.Resampling.LANCZOS)
        im.paste(mini_l, (sb_x + 16, res_y + 25), mini_l)
    draw.text((sb_x + 90, res_y + 24), "相度 AI相面", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    draw.text((sb_x + 90, res_y + 54), "度量骨相几何 · 洞见神骨气度", font=font_small, fill=COLOR_TEXT_MUTED)
    draw.rounded_rectangle([sb_x + sb_w - 75, res_y + 35, sb_x + sb_w - 18, res_y + 75], radius=12, fill=COLOR_GOLD_LIGHT)
    draw.text((sb_x + sb_w - 62, res_y + 44), "进入", font=font_small, fill=COLOR_GOLD_DARK)
    
    # 手指点击波纹动效 (点击“进入”)
    touch_p = min(1.0, progress * 1.5)
    draw_touch_ripple(draw, sb_x + sb_w - 46, res_y + 55, touch_p)
    
    draw_phone_home_bar(draw, sx, sy, sw, sh)
    return im

# 场景 2：进入小程序首页，点击上传美人照片
def render_scene_2(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_DESK_BG)
    draw = ImageDraw.Draw(im)
    draw_studio_background(draw)
    
    # 左侧解说亮点
    lx = 100
    ly = 260
    draw.rounded_rectangle([lx, ly, lx + 440, ly + 260], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((lx + 30, ly + 30), "实机界面：高定极简奢华", font=font_title, fill=COLOR_GOLD_DARK)
    draw.text((lx + 30, ly + 90), "拍照 / 本地相册选图", font=font_card_h, fill=COLOR_TEXT_MAIN)
    draw.text((lx + 30, ly + 140), "• 3:4 标准人脸取景框", font=font_body, fill=COLOR_TEXT_MUTED)
    draw.text((lx + 30, ly + 180), "• 选入绝美神颜测试照片", font=font_body, fill=COLOR_GOLD_DARK)
    
    # 右侧仪式感卡片
    rx = WIDTH - 100 - 440
    ry = 320
    draw.rounded_rectangle([rx, ry, rx + 440, ry + 220], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER, width=1)
    draw.text((rx + 30, ry + 30), "仪式感拉满！", font=font_title, fill=COLOR_GOLD)
    draw.text((rx + 30, ry + 95), "“先拿这张天花板神颜照片试试水，", font=font_body, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 30, ry + 135), "点击测算！四百七十八个锚点激光狂扫！”", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    draw_phone_frame(draw)
    sx, sy, sw, sh = PHONE_X + 12, PHONE_Y + 12, PHONE_W - 24, PHONE_H - 24
    
    # 屏幕内容：小程序首页 (相机取景框已载入神颜照片)
    draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(250, 250, 248))
    draw_phone_status_bar(draw, sx, sy, sw, "相度")
    
    # 取景框
    vf_w = sw - 36
    vf_h = int(vf_w * 4 / 3)
    vf_x = sx + 18
    vf_y = sy + 90
    draw.rounded_rectangle([vf_x, vf_y, vf_x + vf_w, vf_y + vf_h], radius=16, fill=(240, 238, 230), outline=COLOR_BORDER_GOLD, width=2)
    
    # 贴入神颜照片
    photo_show = cached_face_scaled.resize((vf_w - 8, vf_h - 8), Image.Resampling.LANCZOS)
    im.paste(photo_show, (vf_x + 4, vf_y + 4), photo_show)
    
    # 取景框四角微标
    draw.line([vf_x + 10, vf_y + 24, vf_x + 10, vf_y + 10, vf_x + 24, vf_y + 10], fill=COLOR_GOLD, width=3)
    draw.line([vf_x + vf_w - 24, vf_y + 10, vf_x + vf_w - 10, vf_y + 10, vf_x + vf_w - 10, vf_y + 24], fill=COLOR_GOLD, width=3)
    
    # 底部主测算按钮 (香槟金色大胶囊)
    btn_w = sw - 48
    btn_h = 52
    btn_x = sx + 24
    btn_y = vf_y + vf_h + 35
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=26, fill=COLOR_GOLD)
    draw.text((btn_x + btn_w // 2 - 68, btn_y + 14), "开始骨相测算", font=font_body_bold, fill=(255, 255, 255))
    
    # 点击按钮的水波纹动画
    touch_p = min(1.0, progress * 1.6)
    draw_touch_ripple(draw, btn_x + btn_w // 2, btn_y + btn_h // 2, touch_p)
    
    draw_phone_home_bar(draw, sx, sy, sw, sh)
    return im

# 场景 3：478 锚点三维激光仪式感狂扫
def render_scene_3(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_DESK_BG)
    draw = ImageDraw.Draw(im)
    draw_studio_background(draw)
    
    # 左侧实时量测动态参数
    lx = 100
    ly = 240
    draw.rounded_rectangle([lx, ly, lx + 440, ly + 320], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((lx + 30, ly + 28), "实时精密几何计算中", font=font_title, fill=COLOR_GOLD_DARK)
    
    calc_items = [
        ("• 下颌骨折角 (Jaw Angle)", "108.7° 刚柔微折"),
        ("• 外眦仰角 (Canthal Tilt)", "+9.5° 正向飞扬"),
        ("• 三庭黄金比例", "0.67 : 1.31 : 1.01"),
        ("• 姿态水平 De-roll 校准", "已消除偏转角")
    ]
    for i, (ct, cv) in enumerate(calc_items):
        draw.text((lx + 30, ly + 90 + i * 55), ct, font=font_body_bold, fill=COLOR_TEXT_MAIN)
        draw.text((lx + 30, ly + 118 + i * 55), cv, font=font_body, fill=COLOR_GOLD_DARK)
        
    # 右侧嘴碎吐槽气泡
    rx = WIDTH - 100 - 440
    ry = 320
    draw.rounded_rectangle([rx, ry, rx + 440, ry + 220], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER, width=1)
    draw.text((rx + 30, ry + 30), "疯狂推演中...", font=font_title, fill=COLOR_GOLD)
    draw.text((rx + 30, ry + 95), "“好家伙，正在解构下颌角、三庭五眼，", font=font_body, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 30, ry + 135), "这大模型CPU不会给我干冒烟了吧？！”", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    draw_phone_frame(draw)
    sx, sy, sw, sh = PHONE_X + 12, PHONE_Y + 12, PHONE_W - 24, PHONE_H - 24
    
    # 屏幕内容：扫描仪式蒙层 (全脸激光与几何点阵)
    draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(245, 244, 238))
    draw_phone_status_bar(draw, sx, sy, sw, "相度 · 深度解构中")
    
    # 扫描人脸卡片
    vf_w = sw - 36
    vf_h = int(vf_w * 4 / 3)
    vf_x = sx + 18
    vf_y = sy + 90
    draw.rounded_rectangle([vf_x, vf_y, vf_x + vf_w, vf_y + vf_h], radius=16, fill=(240, 238, 230), outline=COLOR_BORDER_GOLD, width=1)
    
    # 贴入人脸
    photo_show = cached_face_scaled.resize((vf_w - 8, vf_h - 8), Image.Resampling.LANCZOS)
    im.paste(photo_show, (vf_x + 4, vf_y + 4), photo_show)
    
    # 绘制实测 478 锚点金色外轮廓与关键点
    if cached_face_pts:
        pts = [(vf_x + 4 + p[0], vf_y + 4 + p[1]) for p in cached_face_pts["contour"]]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=(184, 144, 88, 190), width=1)
            
        for p in cached_face_pts["keys"]:
            px, py = vf_x + 4 + p[0], vf_y + 4 + p[1]
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255), outline=COLOR_TEAL, width=2)
            
        jl = (vf_x + 4 + cached_face_pts["jaw_l"][0], vf_y + 4 + cached_face_pts["jaw_l"][1])
        jr = (vf_x + 4 + cached_face_pts["jaw_r"][0], vf_y + 4 + cached_face_pts["jaw_r"][1])
        menton = (vf_x + 4 + cached_face_pts["menton"][0], vf_y + 4 + cached_face_pts["menton"][1])
        draw.line([jl, menton], fill=COLOR_GOLD, width=2)
        draw.line([jr, menton], fill=COLOR_GOLD, width=2)
        
    # 激光扫描线上下往复
    scan_y = vf_y + 20 + int((math.sin(progress * math.pi * 5) + 1.0) / 2.0 * (vf_h - 40))
    draw.line([vf_x + 10, scan_y, vf_x + vf_w - 10, scan_y], fill=(184, 144, 88, 200), width=3)
    
    # 扫描步骤动画指示
    step_y = vf_y + vf_h + 30
    draw.rounded_rectangle([sx + 24, step_y, sx + sw - 24, step_y + 60], radius=14, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((sx + 40, step_y + 18), "●  478点几何提纯 >> 典籍知识推演...", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    draw_phone_home_bar(draw, sx, sy, sw, sh)
    return im

# 场景 4：报告生成！手指下滑滚动长报告，情商拉满
def render_scene_4(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_DESK_BG)
    draw = ImageDraw.Draw(im)
    draw_studio_background(draw)
    
    # 左侧赞叹气泡
    lx = 100
    ly = 260
    draw.rounded_rectangle([lx, ly, lx + 440, ly + 260], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((lx + 30, ly + 30), "这情商也太高了！", font=font_title, fill=COLOR_GOLD_DARK)
    draw.text((lx + 30, ly + 95), "“灵动折角型 · 顶级骨相天花板！", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    draw.text((lx + 30, ly + 140), "外眦仰角正九点五度！", font=font_card_h, fill=COLOR_GOLD)
    draw.text((lx + 30, ly + 185), "夸得我都不好意思了哈哈哈哈！”", font=font_body, fill=COLOR_TEXT_MUTED)
    
    # 右侧实测参数浮窗
    rx = WIDTH - 100 - 440
    ry = 300
    draw.rounded_rectangle([rx, ry, rx + 440, ry + 240], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER, width=1)
    draw.text((rx + 30, ry + 30), "四维能量图谱直观呈现", font=font_title, fill=COLOR_GOLD)
    draw.text((rx + 30, ry + 90), "• 智感洞察：98 分", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 30, ry + 130), "• 气场边界：96 分", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 30, ry + 170), "• 抗衰骨力：95 分", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    draw_phone_frame(draw)
    sx, sy, sw, sh = PHONE_X + 12, PHONE_Y + 12, PHONE_W - 24, PHONE_H - 24
    
    # 模拟屏幕上下平滑滚动动画
    scroll_offset = int(progress * 260)
    
    draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(250, 250, 248))
    draw_phone_status_bar(draw, sx, sy, sw, "相度 · 骨相解构报告")
    
    # 报告卡片流 (受滚动偏移影响)
    card_y = sy + 90 - scroll_offset
    
    # 核心标签与主导型
    draw.rounded_rectangle([sx + 18, card_y, sx + sw - 18, card_y + 120], radius=14, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((sx + 35, card_y + 18), "【 灵动折角型 · 顶级骨相 】", font=font_body_bold, fill=COLOR_GOLD)
    draw.text((sx + 35, card_y + 52), "清冷灵动、自带气场边界与坚毅定力", font=font_small, fill=COLOR_TEXT_MAIN)
    draw.text((sx + 35, card_y + 82), "#清冷高智  #顶级骨相  #正向飞扬", font=font_tiny, fill=COLOR_TEXT_MUTED)
    
    # 三庭黄金律可视化条
    tp_y = card_y + 135
    draw.rounded_rectangle([sx + 18, tp_y, sx + sw - 18, tp_y + 110], radius=14, fill=(255, 255, 255), outline=COLOR_BORDER, width=1)
    draw.text((sx + 35, tp_y + 16), "三庭黄金比例 · 0.67 : 1.31 : 1.01", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    # 三庭条
    bar_y = tp_y + 50
    draw.rounded_rectangle([sx + 35, bar_y, sx + 135, bar_y + 22], radius=6, fill=(59, 130, 246))
    draw.text((sx + 65, bar_y + 4), "上庭", font=font_tiny, fill=(255, 255, 255))
    draw.rounded_rectangle([sx + 140, bar_y, sx + 270, bar_y + 22], radius=6, fill=COLOR_GOLD)
    draw.text((sx + 185, bar_y + 4), "中庭", font=font_tiny, fill=(255, 255, 255))
    draw.rounded_rectangle([sx + 275, bar_y, sx + sw - 35, bar_y + 22], radius=6, fill=(16, 185, 129))
    draw.text((sx + 315, bar_y + 4), "下庭", font=font_tiny, fill=(255, 255, 255))
    draw.text((sx + 35, tp_y + 82), "中庭饱满蓄势，神骨沉潜从容舒展", font=font_tiny, fill=COLOR_TEXT_MUTED)
    
    # 核心部位微观实拍切片卡
    feat_y = tp_y + 125
    draw.rounded_rectangle([sx + 18, feat_y, sx + sw - 18, feat_y + 140], radius=14, fill=(255, 255, 255), outline=COLOR_BORDER, width=1)
    draw.text((sx + 35, feat_y + 16), "微观部位精析 · 外眦与下颌", font=font_body_bold, fill=COLOR_TEXT_MAIN)
    draw.text((sx + 35, feat_y + 50), "• 外眦仰角：+9.5° 正向飞扬势", font=font_small, fill=COLOR_GOLD_DARK)
    draw.text((sx + 35, feat_y + 78), "• 下颌骨折角：108.7° 刚柔抗衰", font=font_small, fill=COLOR_GOLD_DARK)
    draw.text((sx + 35, feat_y + 106), "• 面部长宽比：1.17 黄金立体纵深", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 四维雷达能量卡
    rad_y = feat_y + 155
    draw.rounded_rectangle([sx + 18, rad_y, sx + sw - 18, rad_y + 130], radius=14, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((sx + 35, rad_y + 16), "面容高维能量图谱", font=font_body_bold, fill=COLOR_TEAL)
    
    scores = [("智感", 98), ("气场", 96), ("抗衰", 95), ("定力", 94)]
    for i, (sc_name, sc_val) in enumerate(scores):
        sc_x = sx + 35 + i * 85
        draw.rounded_rectangle([sc_x, rad_y + 50, sc_x + 75, rad_y + 105], radius=8, fill=COLOR_BG_CARD_ALT)
        draw.text((sc_x + 16, rad_y + 58), f"{sc_val}", font=font_body_bold, fill=COLOR_GOLD)
        draw.text((sc_x + 16, rad_y + 82), sc_name, font=font_tiny, fill=COLOR_TEXT_MUTED)
        
    draw_phone_home_bar(draw, sx, sy, sw, sh)
    return im

# 场景 5：点击保存长海报，弹出时尚杂志长图
def render_scene_5(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_DESK_BG)
    draw = ImageDraw.Draw(im)
    draw_studio_background(draw)
    
    lx = 100
    ly = 260
    draw.rounded_rectangle([lx, ly, lx + 440, ly + 260], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((lx + 30, ly + 30), "一键导出高定长海报", font=font_title, fill=COLOR_GOLD_DARK)
    draw.text((lx + 30, ly + 95), "秒变时尚杂志大片！", font=font_card_h, fill=COLOR_TEXT_MAIN)
    draw.text((lx + 30, ly + 140), "• 微信朋友圈高格调社交名片", font=font_body, fill=COLOR_TEXT_MUTED)
    draw.text((lx + 30, ly + 180), "• 全内存运行，绝不留存肖像", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    rx = WIDTH - 100 - 440
    ry = 320
    draw.rounded_rectangle([rx, ry, rx + 440, ry + 220], radius=16, fill=(255, 255, 255), outline=COLOR_BORDER, width=1)
    draw.text((rx + 30, ry + 30), "发圈必备神器", font=font_title, fill=COLOR_GOLD)
    draw.text((rx + 30, ry + 95), "“点一下保存海报……直接秒变", font=font_body, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 30, ry + 135), "时尚杂志大片，高格调名片这不就来了！”", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    draw_phone_frame(draw)
    sx, sy, sw, sh = PHONE_X + 12, PHONE_Y + 12, PHONE_W - 24, PHONE_H - 24
    
    # 屏幕内容：展示保存成功的 9:16 典藏版海报
    draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(235, 233, 226))
    draw_phone_status_bar(draw, sx, sy, sw, "典藏长海报")
    
    # 居中海报实体
    post_w = sw - 60
    post_h = sh - 130
    post_x = sx + 30
    post_y = sy + 90
    draw.rounded_rectangle([post_x, post_y, post_x + post_w, post_y + post_h], radius=12, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
    
    draw.text((post_x + 18, post_y + 16), "相 度 // 典藏版", font=font_small, fill=COLOR_GOLD)
    
    # 照片嵌入
    photo_mini = cached_face_scaled.resize((post_w - 36, 210), Image.Resampling.LANCZOS)
    im.paste(photo_mini, (post_x + 18, post_y + 45), photo_mini)
    
    draw.text((post_x + 18, post_y + 265), "【 灵动折角型 · 顶级神颜 】", font=font_body_bold, fill=COLOR_GOLD)
    draw.text((post_x + 18, post_y + 295), "清冷灵动、自带气场边界与坚毅定力", font=font_tiny, fill=COLOR_TEXT_MAIN)
    draw.text((post_x + 18, post_y + 320), "#清冷高智  #顶级骨相  #正向飞扬", font=font_tiny, fill=COLOR_TEXT_MUTED)
    
    # 四维分数块
    draw.line([post_x + 18, post_y + 348, post_x + post_w - 18, post_y + 348], fill=COLOR_BORDER, width=1)
    scores = [("智感", 98), ("气场", 96), ("抗衰", 95), ("定力", 94)]
    for i, (sc_name, sc_val) in enumerate(scores):
        sc_x = post_x + 18 + i * 78
        draw.rounded_rectangle([sc_x, post_y + 360, sc_x + 70, post_y + 405], radius=6, fill=COLOR_BG_CARD_ALT)
        draw.text((sc_x + 12, post_y + 366), f"{sc_val}", font=font_small, fill=COLOR_GOLD)
        draw.text((sc_x + 12, post_y + 386), sc_name, font=font_tiny, fill=COLOR_TEXT_MUTED)
        
    # 保存成功 Toast 弹窗动画
    toast_w = 200
    toast_h = 42
    tx = sx + (sw - toast_w) // 2
    ty = sy + sh - 90
    draw.rounded_rectangle([tx, ty, tx + toast_w, ty + toast_h], radius=21, fill=(0, 0, 0, 200))
    draw.text((tx + 28, ty + 12), "★ 已保存至系统相册", font=font_small, fill=(255, 255, 255))
    
    draw_phone_home_bar(draw, sx, sy, sw, sh)
    return im

# 场景 6：微信搜「相度」立即测测 · 一键三连求支持
def render_scene_6(progress):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_DESK_BG)
    draw = ImageDraw.Draw(im)
    draw_studio_background(draw, with_phone=False)
    
    # 顶部居中吸睛大字
    draw.text((WIDTH // 2 - 320, 100), "微信搜一搜，立即开启骨相测算", font=font_mega, fill=COLOR_GOLD)
    draw.text((WIDTH // 2 - 240, 175), "纯内存运行 · 阅后即焚 · 测测你的神颜骨骼基因", font=font_card_h, fill=COLOR_TEXT_MUTED)
    
    # 居中超大搜索框
    sb_w = 800
    sb_h = 95
    sb_x = (WIDTH - sb_w) // 2
    sb_y = 260
    draw.rounded_rectangle([sb_x, sb_y, sb_x + sb_w, sb_y + sb_h], radius=48, fill=(255, 255, 255), outline=COLOR_GOLD, width=2)
    
    # 放大镜
    mg_cx = sb_x + 60
    mg_cy = sb_y + sb_h // 2
    draw.ellipse([mg_cx - 16, mg_cy - 16, mg_cx + 16, mg_cy + 16], outline=COLOR_GOLD, width=4)
    draw.line([mg_cx + 11, mg_cy + 11, mg_cx + 25, mg_cy + 25], fill=COLOR_GOLD, width=5)
    
    draw.text((sb_x + 105, sb_y + 24), "相度", font=font_mega, fill=COLOR_TEXT_MAIN)
    
    # 搜索按钮
    draw.rounded_rectangle([sb_x + sb_w - 200, sb_y + 12, sb_x + sb_w - 15, sb_y + sb_h - 12], radius=35, fill=COLOR_GOLD)
    draw.text((sb_x + sb_w - 150, sb_y + 28), "搜索", font=font_title, fill=(255, 255, 255))
    
    # 下方一键三连徽章群 (水平居中分布)
    badge_cy = 420
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
        draw.rounded_rectangle([cx_i, badge_cy, cx_i + coin_w, badge_cy + coin_h], radius=14, fill=(255, 255, 255), outline=COLOR_BORDER_GOLD, width=1)
        draw.ellipse([cx_i + coin_w // 2 - 35, badge_cy + 20, cx_i + coin_w // 2 + 35, badge_cy + 90], fill=COLOR_GOLD_LIGHT, outline=COLOR_GOLD, width=2)
        draw.text((cx_i + coin_w // 2 - 24, badge_cy + 38), b_name, font=font_card_h, fill=COLOR_GOLD_DARK)
        draw.text((cx_i + coin_w // 2 - 32, badge_cy + 105), b_desc1, font=font_body_bold, fill=COLOR_TEXT_MAIN)
        draw.text((cx_i + coin_w // 2 - 32, badge_cy + 138), b_desc2, font=font_small, fill=COLOR_TEXT_MUTED)
        
    # 底部幽默调侃金句卡
    foot_y = 660
    foot_w = 860
    foot_x = (WIDTH - foot_w) // 2
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + 80], radius=40, fill=(245, 238, 226), outline=COLOR_BORDER_GOLD, width=1)
    foot_text = "★ 完全免费无广告 · 我先去拿我朋友丑照试试了！"
    b_ft = font_title.getbbox(foot_text)
    ft_w = b_ft[2] - b_ft[0]
    draw.text(((WIDTH - ft_w) // 2, foot_y + 18), foot_text, font=font_title, fill=COLOR_GOLD_DARK)
    
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
    
    output_mp4 = os.path.join(WORKDIR, "相度XiangDu_第一视角风趣实操视频.mp4")
    
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

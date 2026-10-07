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
FPS = 24  # 严格匹配真实录屏 capture.mp4 的原生 24 FPS
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"
VOICE = "zh-CN-YunxiNeural"
VOICE_RATE = "+34%"

REAL_VIDEO_PATH = r"D:\UserData\Downloads\capture.mp4"

# 严格按真实录屏动作节奏拆解的 5 个阶段解说词 (总长严格锁死在 31.18 秒)
TIMELINE_SCENES = [
    {
        "id": 1,
        "start": 0.0,
        "end": 4.5,
        "left_tag": "实机真机开箱测算",
        "left_title": "选入天花板神颜照片",
        "left_desc": "从手机相册挑选绝美神颜，点击完成",
        "right_bubble": "“今天就拿真机实测看它到底是火眼金睛还是睁眼说瞎话！”",
        "voice": "家人们，今天拿我做的小程序实测一张天花板神颜照片，看它到底是火眼金睛还是睁眼说瞎话！"
    },
    {
        "id": 2,
        "start": 4.5,
        "end": 8.0,
        "left_tag": "478点几何提纯中",
        "left_title": "AI 调取知识库推演",
        "left_desc": "毫秒级计算面部长宽比与三庭五眼",
        "right_bubble": "“四百七十八个锚点激光狂扫，后台正在调取典籍知识库……”",
        "voice": "点击测算！四百七十八个锚点激光狂扫，后台正在调取知识库深度推演……"
    },
    {
        "id": 3,
        "start": 8.0,
        "end": 15.0,
        "left_tag": "第一章 · 全局骨相格局",
        "left_title": "下颌夹角 108.3°",
        "left_desc": "三庭比例 0.67:1.32:1.01 · 方正基石骨相",
        "right_bubble": "“卧槽出来了！温润聚势型，这大模型情商比我还高！”",
        "voice": "卧槽居然出来了！温润聚势型，笃定后劲的高智气场！下颌角一百零八度，方正基石型骨相，这大模型情商比我还高！"
    },
    {
        "id": 4,
        "start": 15.0,
        "end": 22.5,
        "left_tag": "第二章 · 微观五官气韵",
        "left_title": "外眦上扬 10.0°",
        "left_desc": "眼裂修长眼神聚焦 · 山根挺直聚气",
        "right_bubble": "“外眦上扬整整十度，眼神聚焦有穿透力，怎么拍都上镜！”",
        "voice": "往下滑看看五官：外眦上扬整整十度，眼神聚焦有穿透力；山根挺直，上下唇厚度比一点七，难怪怎么拍都上镜！"
    },
    {
        "id": 5,
        "start": 22.5,
        "end": 31.18,
        "left_tag": "第三章 · 四维能量气场",
        "left_title": "情绪自洽 90 分",
        "left_desc": "智感88 · 气场85 · 蓄势84 · 杂志长海报",
        "right_bubble": "“微信搜「相度」自己去测！求一键三连支持，我先去测朋友了！”",
        "voice": "四维能量图谱情绪自洽高达九十分！微信搜相度自己去测测骨相，觉得好玩求个一键三连，我先去测我朋友了！"
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

font_title = get_font(38, bold=True)
font_card_h = get_font(28, bold=True)
font_body_bold = get_font(22, bold=True)
font_body = get_font(19, bold=False)
font_small = get_font(16, bold=False)
font_badge = get_font(18, bold=True)
font_sub = get_font(36, bold=True)

COLOR_BG = (250, 250, 247)
COLOR_CARD = (255, 255, 255)
COLOR_GOLD = (184, 144, 88)
COLOR_GOLD_DARK = (150, 110, 58)
COLOR_GOLD_LIGHT = (245, 238, 226)
COLOR_TEXT_MAIN = (17, 24, 39)
COLOR_TEXT_MUTED = (100, 116, 139)
COLOR_BORDER = (226, 232, 240)
COLOR_BORDER_GOLD = (218, 192, 156)
COLOR_TEAL = (20, 110, 120)

# 音频流水线：逐句生成并精确按时间轴拼合
async def generate_aligned_soundtrack():
    audio_dir = os.path.join(WORKDIR, "audio_real_capture")
    os.makedirs(audio_dir, exist_ok=True)
    
    seg_files = []
    print("正在生成与真实录屏精确毫秒级对齐的语音音轨...")
    sys.stdout.flush()
    
    for idx, sc in enumerate(TIMELINE_SCENES):
        target_dur = sc["end"] - sc["start"]
        raw_mp3 = os.path.join(audio_dir, f"seg_{idx}.mp3")
        raw_wav = os.path.join(audio_dir, f"seg_{idx}.wav")
        timed_wav = os.path.join(audio_dir, f"timed_{idx}.wav")
        
        # 1. Edge-TTS 生成
        tts = edge_tts.Communicate(sc["voice"], VOICE, rate=VOICE_RATE)
        await tts.save(raw_mp3)
        
        subprocess.run([FFMPEG_PATH, "-y", "-i", raw_mp3, "-ac", "1", "-ar", "24000", raw_wav],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        with wave.open(raw_wav, "rb") as wf:
            speech_dur = wf.getnframes() / float(wf.getframerate())
            
        # 若语音较短，末尾补齐静音垫到 target_dur；若略长，轻微加速
        if speech_dur < target_dur:
            pad_needed = target_dur - speech_dur
            subprocess.run([FFMPEG_PATH, "-y", "-i", raw_wav, "-af", f"apad=pad_dur={pad_needed:.3f}", timed_wav],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            tempo = speech_dur / target_dur
            subprocess.run([FFMPEG_PATH, "-y", "-i", raw_wav, "-af", f"atempo={tempo:.3f}", timed_wav],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
        seg_files.append(timed_wav)
        print(f"Segment {sc['id']}: 目标={target_dur:.2f}s, 发音={speech_dur:.2f}s -> 完美垫齐!")
        sys.stdout.flush()
        
    # 拼接全部语音片段
    concat_txt = os.path.join(audio_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in seg_files:
            abs_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")
            
    merged_voice = os.path.join(WORKDIR, "voice_real_capture.wav")
    subprocess.run([FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", merged_voice],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    # 混入 BGM 背景音乐
    final_audio = os.path.join(WORKDIR, "soundtrack_real_capture.wav")
    bgm_p = os.path.join(WORKDIR, "bgm.mp3")
    total_dur = 31.18
    if os.path.exists(bgm_p):
        mix_filter = (
            f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{total_dur},volume=0.08[bgm];"
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
        
    return final_audio

# 绘制每一帧的高清背景与同步伴随卡片
def render_frame_overlay(cur_time):
    # 定位当前所属的场景
    cur_sc = TIMELINE_SCENES[0]
    for sc in TIMELINE_SCENES:
        if sc["start"] <= cur_time < sc["end"]:
            cur_sc = sc
            break
    if cur_time >= TIMELINE_SCENES[-1]["start"]:
        cur_sc = TIMELINE_SCENES[-1]
        
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(im)
    
    # 暖白背景渐变
    for y in range(0, HEIGHT, 4):
        ratio = y / float(HEIGHT)
        r = int(251 - ratio * 4)
        g = int(251 - ratio * 4)
        b = int(249 - ratio * 6)
        draw.rectangle([0, y, WIDTH, y + 4], fill=(r, g, b))
        
    for x in range(40, WIDTH, 50):
        for y in range(40, HEIGHT, 50):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(225, 220, 210))
            
    # 顶部品牌标尺
    draw.text((100, 44), "相 度  XIANGDU", font=font_small, fill=COLOR_GOLD)
    draw.text((260, 44), "// 真实真机实操录屏 · 骨相美学解构", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 右上角常驻小程序标识
    badge_w = 260
    badge_h = 44
    badge_x = WIDTH - 100 - badge_w
    badge_y = 36
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=22, fill=COLOR_GOLD_LIGHT, outline=COLOR_BORDER_GOLD, width=1)
    draw.ellipse([badge_x + 18, badge_y + 16, badge_x + 30, badge_y + 28], fill=COLOR_GOLD)
    draw.text((badge_x + 40, badge_y + 11), "相度 AI相面", font=font_body_bold, fill=COLOR_GOLD_DARK)
    draw.text((badge_x + 175, badge_y + 14), "小程序", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 左侧动态数据伴随卡片
    lx = 80
    ly = 240
    lw = 540
    lh = 360
    draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=18, fill=COLOR_CARD, outline=COLOR_BORDER_GOLD, width=1)
    draw.rounded_rectangle([lx, ly, lx + lw, ly + 65], radius=18, fill=COLOR_GOLD_LIGHT)
    draw.text((lx + 30, ly + 20), f"★ {cur_sc['left_tag']}", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    draw.text((lx + 30, ly + 100), cur_sc["left_title"], font=font_title, fill=COLOR_TEXT_MAIN)
    draw.text((lx + 30, ly + 165), cur_sc["left_desc"], font=font_body, fill=COLOR_TEXT_MUTED)
    draw.line([lx + 30, ly + 215, lx + lw - 30, ly + 215], fill=COLOR_BORDER, width=1)
    
    draw.text((lx + 30, ly + 245), "★ MediaPipe 478 关键点高精量测", font=font_small, fill=COLOR_GOLD_DARK)
    draw.text((lx + 30, ly + 285), "★ Gemini 2.5 智能解构引擎", font=font_small, fill=COLOR_TEXT_MAIN)
    
    # 右侧 UP 主实时吐槽气泡卡
    rx = WIDTH - 80 - 540
    ry = 280
    rw = 540
    rh = 280
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=18, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
    draw.text((rx + 30, ry + 30), "UP 主真实体验吐槽", font=font_card_h, fill=COLOR_GOLD)
    draw.line([rx + 30, ry + 75, rx + rw - 30, ry + 75], fill=COLOR_BORDER_GOLD, width=1)
    
    # 气泡台词 (两行)
    b_text = cur_sc["right_bubble"]
    draw.text((rx + 30, ry + 105), b_text[:19], font=font_body_bold, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 30, ry + 145), b_text[19:38], font=font_body_bold, fill=COLOR_TEXT_MAIN)
    if len(b_text) > 38:
        draw.text((rx + 30, ry + 185), b_text[38:], font=font_body_bold, fill=COLOR_TEXT_MAIN)
        
    # 底部字幕 (精细计算，绝不遮挡手机，长句优雅双行)
    sub_font = get_font(32, bold=True)
    v_text = cur_sc["voice"]
    b_sub = sub_font.getbbox(v_text)
    sw_text = b_sub[2] - b_sub[0]
    sub_y = HEIGHT - 76
    
    if sw_text > WIDTH - 200:
        mid_idx = len(v_text) // 2
        line1, line2 = v_text[:mid_idx], v_text[mid_idx:]
        b1, b2 = sub_font.getbbox(line1), sub_font.getbbox(line2)
        x1 = (WIDTH - (b1[2] - b1[0])) // 2
        x2 = (WIDTH - (b2[2] - b2[0])) // 2
        draw.text((x1 + 2, sub_y - 20), line1, font=sub_font, fill=(184, 144, 88, 70))
        draw.text((x1, sub_y - 22), line1, font=sub_font, fill=COLOR_TEXT_MAIN)
        draw.text((x2 + 2, sub_y + 22), line2, font=sub_font, fill=(184, 144, 88, 70))
        draw.text((x2, sub_y + 20), line2, font=sub_font, fill=COLOR_TEXT_MAIN)
    else:
        sub_x = (WIDTH - sw_text) // 2
        draw.text((sub_x + 2, sub_y + 2), v_text, font=sub_font, fill=(184, 144, 88, 70))
        draw.text((sub_x, sub_y), v_text, font=sub_font, fill=COLOR_TEXT_MAIN)
    
    return im

# 核心合成压制流水线
async def render_real_capture_video():
    soundtrack = await generate_aligned_soundtrack()
    
    output_mp4 = os.path.join(WORKDIR, "相度XiangDu_真机实操高能测评.mp4")
    
    # 1. 启动 FFmpeg 解码 capture.mp4 为连续 RGB 帧
    dec_cmd = [
        FFMPEG_PATH, "-i", REAL_VIDEO_PATH,
        "-f", "image2pipe",
        "-pix_fmt", "rgb24",
        "-vcodec", "rawvideo",
        "-"
    ]
    dec_proc = subprocess.Popen(dec_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    # 2. 启动 FFmpeg 编码最终 1080P 视频
    enc_cmd = [
        FFMPEG_PATH, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-i", soundtrack,
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
    enc_stderr = open(os.path.join(WORKDIR, "ffmpeg_real_cap.log"), "w", encoding="utf-8")
    enc_proc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=enc_stderr)
    
    # 手机在 1920x1080 画布中的高精尺寸 (高度设为 860，下方留足 165px 呼吸空间给字幕)
    target_phone_h = 860
    target_phone_w = int(576 * target_phone_h / 1280) # 387px
    phone_x = (WIDTH - target_phone_w) // 2
    phone_y = 52
    
    frame_bytes_len = 576 * 1280 * 3
    total_frames = 748  # 31.18s * 24fps
    frame_idx = 0
    
    print("\n正在逐帧注入真实手机录屏画面并合成 1080P 高清视频...")
    sys.stdout.flush()
    
    while True:
        raw_frame = dec_proc.stdout.read(frame_bytes_len)
        if not raw_frame or len(raw_frame) < frame_bytes_len:
            break
            
        cur_time = frame_idx / float(FPS)
        
        # 1. 生成带有伴随数据卡和字幕的 1080P 宽幅底图
        canvas = render_frame_overlay(cur_time)
        draw = ImageDraw.Draw(canvas)
        
        # 2. 绘制真实的 iPhone 流线外框与立体投影
        sh_off = 20
        draw.rounded_rectangle([phone_x - 12 + 10, phone_y - 12 + sh_off, phone_x + target_phone_w + 12 + 10, phone_y + target_phone_h + 12 + sh_off],
                               radius=36, fill=(215, 212, 204))
        draw.rounded_rectangle([phone_x - 12, phone_y - 12, phone_x + target_phone_w + 12, phone_y + target_phone_h + 12],
                               radius=34, fill=(35, 33, 30), outline=(210, 195, 170), width=3)
        draw.rounded_rectangle([phone_x - 4, phone_y - 4, phone_x + target_phone_w + 4, phone_y + target_phone_h + 4],
                               radius=26, fill=(10, 10, 10))
                               
        # 3. 将真实的录屏帧按比例高质量无损缩放并贴入手机机身内部
        frame_img = Image.frombytes("RGB", (576, 1280), raw_frame)
        scaled_frame = frame_img.resize((target_phone_w, target_phone_h), Image.Resampling.BILINEAR)
        canvas.paste(scaled_frame, (phone_x, phone_y))
        
        # 4. 手机底部 Home 指示条
        bar_w = 130
        draw.rounded_rectangle([phone_x + (target_phone_w - bar_w) // 2, phone_y + target_phone_h - 12,
                                phone_x + (target_phone_w + bar_w) // 2, phone_y + target_phone_h - 8],
                               radius=2, fill=(100, 100, 100))
                               
        # 写入编码管道
        enc_proc.stdin.write(canvas.tobytes())
        frame_idx += 1
        
        if frame_idx % 60 == 0:
            print(f"真机画面合成进度: {frame_idx}/{total_frames} 帧 ({frame_idx*100.0/total_frames:.1f}%)")
            sys.stdout.flush()
            
    dec_proc.stdout.close()
    dec_proc.wait()
    enc_proc.stdin.close()
    enc_proc.wait()
    enc_stderr.close()
    
    if enc_proc.returncode != 0:
        print(f"FFmpeg 压制失败，退出码: {enc_proc.returncode}")
        raise RuntimeError("FFmpeg encoding failed")
        
    print(f"\n[OK] 真实录屏高清测评视频制作完成！")
    print(f"成片文件: {os.path.abspath(output_mp4)}")
    print(f"文件大小: {os.path.getsize(output_mp4) / (1024*1024):.2f} MB")
    sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(render_real_capture_video())

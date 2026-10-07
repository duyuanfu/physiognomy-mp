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
FPS = 24  # 严格匹配 capture.mp4 原生 24 FPS
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"
VOICE = "zh-CN-YunxiNeural"
VOICE_RATE = "+18%"  # ★ 语速调缓自然，从容风趣，告别抢话

REAL_VIDEO_PATH = r"D:\UserData\Downloads\capture.mp4"

# 5 个阶段解说词与时间轴 (自然语速下各段精确时长，总长约 41.5 秒)
TIMELINE_SCENES = [
    {
        "id": 1,
        "title": "实机开箱 · 挑选绝美神颜照片",
        "sub": "从手机相册选图测试 · 毫秒级锁定人脸结构",
        "left_tag": "实机真机开箱测算",
        "metrics": [
            ("测试样张类型", "顶级神颜", "标准正面 3:4 肖像，光线通透"),
            ("算法就绪状态", "全特征对齐", "MediaPipe 478 锚点准备就绪"),
            ("大模型调度引擎", "Gemini 2.5", "支持多模态端到端结构化推演"),
            ("隐私安全等级", "全内存运行", "分析完毕瞬时销毁，绝不留底片")
        ],
        "right_bubble": "“家人们，今天拿我做的小程序实测一张天花板神颜照片，看它到底是火眼金睛还是睁眼说瞎话！”",
        "voice": "家人们，今天拿我做的小程序实测一张天花板神颜照片，看它到底是火眼金睛还是睁眼说瞎话！"
    },
    {
        "id": 2,
        "title": "478 点阵三维几何激光扫描",
        "sub": "自动 De-roll 水平姿态校准 · 调取典籍知识库",
        "left_tag": "算法与知识库推演中",
        "metrics": [
            ("面部几何锚点", "478 个", "覆盖五官、三庭与下颌骨架"),
            ("姿态水平校正", "De-roll 0.0°", "已消除面部微小仰角与偏转"),
            ("典籍向量索引", "《冰鉴》神骨篇", "提取刚柔沉潜与高智感气质心相"),
            ("当前推演进度", "80% 极速生成", "纯客观物理数据支撑，拒绝盲猜")
        ],
        "right_bubble": "“点击测算！四百七十八个锚点激光狂扫，后台正在调取知识库深度推演……”",
        "voice": "点击测算！四百七十八个锚点激光狂扫，后台正在调取知识库深度推演……"
    },
    {
        "id": 3,
        "title": "第一章 · 全局骨相格局与下颌角",
        "sub": "温润聚势型 · 方正基石骨相 · 侧颜折叠度高",
        "left_tag": "第一章 · 全局骨相格局",
        "metrics": [
            ("下颌夹角 (Jaw Angle)", "108.3°", "方正基石型骨相，侧颜折叠度高"),
            ("三庭黄金比例", "0.67:1.32:1.01", "中庭饱满蓄势，气度沉稳内敛"),
            ("面部长宽比", "1.17", "纵深立体，镜头吃焦极小天然上镜"),
            ("主导骨相气质", "温润聚势型", "兼具包容亲和与笃定后劲高智场")
        ],
        "right_bubble": "“卧槽居然出来了！温润聚势型，笃定后劲的高智气场！下颌角一百零八度，方正基石型骨相，这大模型情商比我还高！”",
        "voice": "卧槽居然出来了！温润聚势型，笃定后劲的高智气场！下颌角一百零八度，方正基石型骨相，这大模型情商比我还高！"
    },
    {
        "id": 4,
        "title": "第二章 · 微观五官气韵精析",
        "sub": "外眦上扬 10.0° · 山根挺直 · 唇线分明",
        "left_tag": "第二章 · 微观五官气韵",
        "metrics": [
            ("外眦仰角 (Canthal Tilt)", "+10.0°", "正向飞扬势，眼神聚焦有穿透力"),
            ("山根挺拔中轴", "直挺聚气", "平接印堂平整，抗挫定力极强"),
            ("上下唇厚度比", "1.71", "轮廓分明，亲和温度与理性并存"),
            ("采听耳相佐证", "轮廓贴脑", "信息筛选力强，不易受外界噪音干扰")
        ],
        "right_bubble": "“往下滑看看五官：外眦上扬整整十度，眼神聚焦有穿透力；山根挺直，上下唇厚度比一点七，难怪怎么拍都上镜！”",
        "voice": "往下滑看看五官：外眦上扬整整十度，眼神聚焦有穿透力；山根挺直，上下唇厚度比一点七，难怪怎么拍都上镜！"
    },
    {
        "id": 5,
        "title": "第三章 · 四维能量图谱与海报导出",
        "sub": "情绪自洽 90 分 · 杂志级长海报一键导出",
        "left_tag": "第三章 · 四维能量图谱",
        "metrics": [
            ("情绪自洽高分", "90 分", "温润阔面钝感力，长周期战略定力"),
            ("智感洞察得分", "88 分", "思维逻辑严谨，社交边界感清晰"),
            ("气场边界得分", "85 分", "温和有度，处事从容不迫"),
            ("蓄势吸金得分", "84 分", "中岳挺拔，资源汇聚力丰沛")
        ],
        "right_bubble": "“四维能量图谱情绪自洽高达九十分！微信搜「相度」自己去测测骨相，觉得好玩求个一键三连，我先去测我朋友了！”",
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

font_mega = get_font(42, bold=True)
font_title = get_font(34, bold=True)
font_card_h = get_font(28, bold=True)
font_body_bold = get_font(23, bold=True)
font_body = get_font(20, bold=False)
font_small = get_font(17, bold=False)
font_badge = get_font(18, bold=True)
font_sub = get_font(36, bold=True)

# 色彩方案：暖白艺术纸 + 哑金 + 墨石灰 (高定亮色，大留白)
COLOR_BG = (250, 250, 247)
COLOR_CARD = (255, 255, 255)
COLOR_CARD_ALT = (246, 245, 241)
COLOR_GOLD = (184, 144, 88)
COLOR_GOLD_DARK = (150, 110, 58)
COLOR_GOLD_LIGHT = (245, 238, 226)
COLOR_TEXT_MAIN = (17, 24, 39)
COLOR_TEXT_MUTED = (100, 116, 139)
COLOR_BORDER = (226, 232, 240)
COLOR_BORDER_GOLD = (218, 192, 156)
COLOR_TEAL = (20, 110, 120)

# 音频管线：生成舒缓自然的真人语音，并计算各段真实时长
async def generate_aligned_soundtrack():
    audio_dir = os.path.join(WORKDIR, "audio_real_capture_relaxed")
    os.makedirs(audio_dir, exist_ok=True)
    
    seg_files = []
    durations = []
    print("正在以舒适自然语速生成第一视角风趣解说配音...")
    sys.stdout.flush()
    
    for idx, sc in enumerate(TIMELINE_SCENES):
        raw_mp3 = os.path.join(audio_dir, f"seg_{idx}.mp3")
        raw_wav = os.path.join(audio_dir, f"seg_{idx}.wav")
        padded_wav = os.path.join(audio_dir, f"padded_{idx}.wav")
        
        tts = edge_tts.Communicate(sc["voice"], VOICE, rate=VOICE_RATE)
        await tts.save(raw_mp3)
        
        subprocess.run([FFMPEG_PATH, "-y", "-i", raw_mp3, "-ac", "1", "-ar", "24000", raw_wav],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # 末尾垫入 0.35s 舒适自然停顿
        subprocess.run([FFMPEG_PATH, "-y", "-i", raw_wav, "-af", "apad=pad_dur=0.35", padded_wav],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        with wave.open(padded_wav, "rb") as wf:
            dur = wf.getnframes() / float(wf.getframerate())
            
        durations.append(dur)
        seg_files.append(padded_wav)
        print(f"Segment {sc['id']}: 真实物理时长 = {dur:.2f}s | {sc['voice'][:24]}...")
        sys.stdout.flush()
        
    total_audio_dur = sum(durations)
    print(f"\n全部 5 段语音生成完毕！总时长: {total_audio_dur:.2f} 秒 (原录屏将优雅放慢至该长度)")
    sys.stdout.flush()
    
    concat_txt = os.path.join(audio_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in seg_files:
            abs_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")
            
    merged_voice = os.path.join(WORKDIR, "voice_real_capture_relaxed.wav")
    subprocess.run([FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", merged_voice],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    final_audio = os.path.join(WORKDIR, "soundtrack_real_capture_relaxed.wav")
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
        
    return final_audio, durations, total_audio_dur

# 绘制每一帧的高清背景与右侧大气伴随卡片 (手机在左，右侧大留白)
def render_frame_overlay(cur_time, scene_time_ranges):
    # 定位当前场景
    cur_sc = TIMELINE_SCENES[0]
    for idx, (st, et) in enumerate(scene_time_ranges):
        if st <= cur_time < et:
            cur_sc = TIMELINE_SCENES[idx]
            break
    if cur_time >= scene_time_ranges[-1][0]:
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
            
    # ★ 右侧大展示区 (从 x=590 到 x=1830，整整 1240px 宽幅大留白！)
    rx = 590
    rw = WIDTH - 90 - rx
    
    # 顶部标尺
    draw.text((rx, 46), "// 真实真机实操录屏 · 骨相美学解构小程序", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 右上角常驻小程序徽章
    badge_w = 260
    badge_h = 44
    badge_x = WIDTH - 90 - badge_w
    badge_y = 38
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=22, fill=COLOR_GOLD_LIGHT, outline=COLOR_BORDER_GOLD, width=1)
    draw.ellipse([badge_x + 18, badge_y + 16, badge_x + 30, badge_y + 28], fill=COLOR_GOLD)
    draw.text((badge_x + 40, badge_y + 11), "相度 AI相面", font=font_body_bold, fill=COLOR_GOLD_DARK)
    draw.text((badge_x + 175, badge_y + 14), "小程序", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 当前幕大标题
    draw.text((rx, 90), cur_sc["title"], font=font_mega, fill=COLOR_TEXT_MAIN)
    draw.line([rx, 150, rx + rw, 150], fill=COLOR_BORDER_GOLD, width=2)
    
    # 中间双卡并排 (卡 A 实时数据 + 卡 B UP 主吐槽)
    mid_y = 178
    card_w = (rw - 40) // 2
    card_h = 575
    
    # 卡 A：实时数据提纯
    draw.rounded_rectangle([rx, mid_y, rx + card_w, mid_y + card_h], radius=18, fill=COLOR_CARD, outline=COLOR_BORDER_GOLD, width=1)
    draw.rounded_rectangle([rx, mid_y, rx + card_w, mid_y + 65], radius=18, fill=COLOR_GOLD_LIGHT)
    draw.text((rx + 30, mid_y + 20), f"★ {cur_sc['left_tag']}", font=font_body_bold, fill=COLOR_GOLD_DARK)
    
    for idx, (m_t, m_v, m_d) in enumerate(cur_sc["metrics"]):
        my = mid_y + 88 + idx * 118
        draw.text((rx + 30, my), m_t, font=font_body, fill=COLOR_TEXT_MUTED)
        draw.text((rx + 30, my + 26), m_v, font=font_title, fill=COLOR_GOLD)
        draw.text((rx + 30, my + 68), m_d, font=font_small, fill=COLOR_TEXT_MAIN)
        if idx < 3:
            draw.line([rx + 30, my + 104, rx + card_w - 30, my + 104], fill=(240, 238, 230), width=1)
            
    # 卡 B：UP 主真实吐槽气泡
    bx = rx + card_w + 40
    draw.rounded_rectangle([bx, mid_y, bx + card_w, mid_y + card_h], radius=18, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
    draw.rounded_rectangle([bx, mid_y, bx + card_w, mid_y + 65], radius=18, fill=COLOR_CARD_ALT)
    draw.text((bx + 30, mid_y + 20), "UP 主第一人称真实吐槽", font=font_body_bold, fill=COLOR_GOLD)
    
    # 吐槽气泡框
    draw.rounded_rectangle([bx + 30, mid_y + 90, bx + card_w - 30, mid_y + 295], radius=14, fill=(250, 249, 246), outline=COLOR_BORDER_GOLD, width=1)
    q_lines = cur_sc["right_bubble"].split("！")
    quote_display = cur_sc["right_bubble"]
    # 智能分行排版
    draw.text((bx + 45, mid_y + 115), quote_display[:18], font=font_card_h, fill=COLOR_TEXT_MAIN)
    draw.text((bx + 45, mid_y + 160), quote_display[18:36], font=font_card_h, fill=COLOR_TEXT_MAIN)
    if len(quote_display) > 36:
        draw.text((bx + 45, mid_y + 205), quote_display[36:54], font=font_card_h, fill=COLOR_GOLD_DARK)
    if len(quote_display) > 54:
        draw.text((bx + 45, mid_y + 248), quote_display[54:], font=font_card_h, fill=COLOR_GOLD_DARK)
        
    # 下方 3 大特性胶囊
    features = [
        ("★ 100% 真实真机录屏交互", "真机手势滑动，所见即所得"),
        ("★ 478 锚点纯客观量测", "拒绝主观瞎猜，纯数学几何支撑"),
        ("★ 全内存运行阅后即焚", "严密捍卫肖像隐私，不留底片")
    ]
    for idx, (f_t, f_d) in enumerate(features):
        fy = mid_y + 325 + idx * 80
        draw.text((bx + 35, fy), f_t, font=font_body_bold, fill=COLOR_GOLD_DARK)
        draw.text((bx + 35, fy + 32), f_d, font=font_body, fill=COLOR_TEXT_MUTED)
        
    # 底部大字幕区 (宽达 1240，双行从容排布，超清绝无遮挡)
    draw.rounded_rectangle([rx, 785, rx + rw, 985], radius=16, fill=(255, 255, 255, 240), outline=COLOR_BORDER_GOLD, width=1)
    draw.text((rx + 35, 810), "UP 主解说字幕：", font=font_small, fill=COLOR_GOLD_DARK)
    
    sub_text = cur_sc["voice"]
    mid_idx = len(sub_text) // 2
    l1, l2 = sub_text[:mid_idx], sub_text[mid_idx:]
    draw.text((rx + 35, 850), l1, font=font_sub, fill=COLOR_TEXT_MAIN)
    draw.text((rx + 35, 910), l2, font=font_sub, fill=COLOR_GOLD_DARK)
    
    return im

# 核心压制流水线：将原录屏按时间轴平滑减速，并放大至左侧
async def render_real_capture_video():
    soundtrack, durations, total_dur = await generate_aligned_soundtrack()
    
    output_mp4 = os.path.join(WORKDIR, "相度XiangDu_真机实操高能测评.mp4")
    
    # 计算各幕在总时间轴上的起点与终点
    scene_time_ranges = []
    accum = 0.0
    for d in durations:
        scene_time_ranges.append((accum, accum + d))
        accum += d
        
    orig_dur = 31.18
    tempo_factor = total_dur / orig_dur  # ~ 1.34x 减速倍率
    
    print(f"\n正在通过 FFmpeg 将原录屏平滑放慢 {tempo_factor:.2f} 倍 (播放速度 0.75x，动作从容优雅)...")
    sys.stdout.flush()
    
    # 1. 启动 FFmpeg 解码 capture.mp4，应用 setpts 平滑放慢
    dec_cmd = [
        FFMPEG_PATH, "-i", REAL_VIDEO_PATH,
        "-filter:v", f"setpts={tempo_factor:.4f}*PTS",
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
    
    # ★ 满足要求 2：手机屏幕大幅放大，并稳居左侧！(高度达 980，清晰度翻倍)
    target_phone_h = 980
    target_phone_w = int(576 * target_phone_h / 1280) # 441px
    phone_x = 90
    phone_y = 50
    
    frame_bytes_len = 576 * 1280 * 3
    total_target_frames = int(round(total_dur * FPS))
    frame_idx = 0
    
    print(f"正在逐帧合成高清左置大屏手机画面 (总共 {total_target_frames} 帧)...")
    sys.stdout.flush()
    
    while True:
        raw_frame = dec_proc.stdout.read(frame_bytes_len)
        if not raw_frame or len(raw_frame) < frame_bytes_len:
            break
            
        cur_time = frame_idx / float(FPS)
        
        # 1. 生成右侧大幅信息面板底图
        canvas = render_frame_overlay(cur_time, scene_time_ranges)
        draw = ImageDraw.Draw(canvas)
        
        # 2. 绘制超大 iPhone 流线钛金外框与立体投影
        draw.rounded_rectangle([phone_x + 10, phone_y + 24, phone_x + target_phone_w + 10, phone_y + target_phone_h + 24],
                               radius=48, fill=(215, 212, 204))
        draw.rounded_rectangle([phone_x - 10, phone_y - 10, phone_x + target_phone_w + 10, phone_y + target_phone_h + 10],
                               radius=44, fill=(35, 33, 30), outline=(210, 195, 170), width=4)
        draw.rounded_rectangle([phone_x - 4, phone_y - 4, phone_x + target_phone_w + 4, phone_y + target_phone_h + 4],
                               radius=38, fill=(10, 10, 10))
                               
        # 3. 将真实录屏帧高质量缩放并贴入手机机身内部
        frame_img = Image.frombytes("RGB", (576, 1280), raw_frame)
        scaled_frame = frame_img.resize((target_phone_w, target_phone_h), Image.Resampling.BILINEAR)
        canvas.paste(scaled_frame, (phone_x, phone_y))
        
        # 4. 手机底部 Home 指示条
        bar_w = 140
        draw.rounded_rectangle([phone_x + (target_phone_w - bar_w) // 2, phone_y + target_phone_h - 12,
                                phone_x + (target_phone_w + bar_w) // 2, phone_y + target_phone_h - 8],
                               radius=2, fill=(100, 100, 100))
                               
        enc_proc.stdin.write(canvas.tobytes())
        frame_idx += 1
        
        if frame_idx % 60 == 0:
            print(f"真机大屏合成进度: {frame_idx}/{total_target_frames} 帧 ({frame_idx*100.0/total_target_frames:.1f}%)")
            sys.stdout.flush()
            
    dec_proc.stdout.close()
    dec_proc.wait()
    enc_proc.stdin.close()
    enc_proc.wait()
    enc_stderr.close()
    
    if enc_proc.returncode != 0:
        print(f"FFmpeg 压制失败，退出码: {enc_proc.returncode}")
        raise RuntimeError("FFmpeg encoding failed")
        
    print(f"\n[OK] 真实录屏高清测评视频（左置大屏版）制作完成！")
    print(f"成片文件: {os.path.abspath(output_mp4)}")
    print(f"文件大小: {os.path.getsize(output_mp4) / (1024*1024):.2f} MB")
    sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(render_real_capture_video())

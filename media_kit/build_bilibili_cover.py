import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.face_mesh_service import face_mesh_service

WORKDIR = "media_kit"
W = 1920
H = 1080

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

font_headline = get_font(84, bold=True)
font_sub = get_font(34, bold=True)
font_badge = get_font(24, bold=True)
font_card = get_font(36, bold=True)
font_small = get_font(20, bold=False)

# 色彩方案：极简高定暖白 + 哑金 + 墨石黑 (大留白、超纯净、极度吸睛)
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

def generate_cover():
    im = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(im)
    
    # 1. 纯净暖白背景渐变
    for y in range(0, H, 4):
        ratio = y / float(H)
        r = int(252 - ratio * 4)
        g = int(251 - ratio * 4)
        b = int(248 - ratio * 6)
        draw.rectangle([0, y, W, y + 4], fill=(r, g, b))
        
    for x in range(30, W, 45):
        for y in range(30, H, 45):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(225, 220, 210))
            
    # 2. 右侧高定肖像大卡片 (占据右半边，宽 860，高 940，大气饱满)
    pic_w = 860
    pic_h = 940
    pic_x = W - 80 - pic_w
    pic_y = 70
    
    draw.rounded_rectangle([pic_x, pic_y, pic_x + pic_w, pic_y + pic_h], radius=20, fill=COLOR_CARD, outline=COLOR_BORDER_GOLD, width=2)
    
    # 工业级四角卡尺角标 ┌ ┐ └ ┘
    c_len = 36
    draw.line([pic_x, pic_y + c_len, pic_x, pic_y, pic_x + c_len, pic_y], fill=COLOR_GOLD, width=4)
    draw.line([pic_x + pic_w - c_len, pic_y, pic_x + pic_w, pic_y, pic_x + pic_w, pic_y + c_len], fill=COLOR_GOLD, width=4)
    draw.line([pic_x, pic_y + pic_h - c_len, pic_x, pic_y + pic_h, pic_x + c_len, pic_y + pic_h], fill=COLOR_GOLD, width=4)
    draw.line([pic_x + pic_w - c_len, pic_y + pic_h, pic_x + pic_w, pic_y + pic_h, pic_x + pic_w, pic_y + pic_h - c_len], fill=COLOR_GOLD, width=4)
    
    # 载入美女图片并优雅贴入
    face_path = r"media_kit/target_face.jpg"
    if os.path.exists(face_path):
        with open(face_path, "rb") as f:
            f_bytes = f.read()
        metrics = face_mesh_service.extract_metrics_from_bytes(f_bytes)
        
        im_full = Image.open(face_path).convert("RGBA")
        crop_box = (380, 480, 2680, 3150)
        face_crop = im_full.crop(crop_box)
        target_inner_w = pic_w - 24
        target_inner_h = pic_h - 24
        face_scaled = face_crop.resize((target_inner_w, target_inner_h), Image.Resampling.LANCZOS)
        im.paste(face_scaled, (pic_x + 12, pic_y + 12), face_scaled)
        
        # 映射并绘制关键点
        scale_x = target_inner_w / float(crop_box[2] - crop_box[0])
        scale_y = target_inner_h / float(crop_box[3] - crop_box[1])
        def map_p(p):
            return ((p[0] - crop_box[0]) * scale_x, (p[1] - crop_box[1]) * scale_y)
            
        cp = metrics.caliper_points
        pts = [(pic_x + 12 + map_p(p)[0], pic_y + 12 + map_p(p)[1]) for p in cp.contour_polygon]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=(184, 144, 88, 180), width=2)
            
        for p in [cp.left_eye_inner, cp.left_eye_outer, cp.right_eye_inner, cp.right_eye_outer,
                  cp.nose_tip, cp.subnasale, cp.nasion, cp.lip_left, cp.lip_right, cp.lip_top,
                  cp.jaw_left, cp.jaw_right, cp.menton]:
            px = pic_x + 12 + map_p(p)[0]
            py = pic_y + 12 + map_p(p)[1]
            draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(255, 255, 255), outline=COLOR_TEAL, width=2)
            
        # 下颌角三角骨架
        jl = (pic_x + 12 + map_p(cp.jaw_left)[0], pic_y + 12 + map_p(cp.jaw_left)[1])
        jr = (pic_x + 12 + map_p(cp.jaw_right)[0], pic_y + 12 + map_p(cp.jaw_right)[1])
        menton = (pic_x + 12 + map_p(cp.menton)[0], pic_y + 12 + map_p(cp.menton)[1])
        draw.line([jl, menton], fill=COLOR_GOLD, width=3)
        draw.line([jr, menton], fill=COLOR_GOLD, width=3)
        
        # 极简高亮数据标签 (仅保留 2 个最有说服力的实测标签，画面极其清爽)
        draw.rounded_rectangle([jl[0] - 185, jl[1] + 10, jl[0] + 15, jl[1] + 62], radius=12, fill=(255, 255, 255, 240), outline=COLOR_BORDER_GOLD, width=1)
        draw.text((jl[0] - 170, jl[1] + 20), "下颌折角 108.7°", font=font_badge, fill=COLOR_GOLD_DARK)
        
        ey_l = (pic_x + 12 + map_p(cp.left_eye_outer)[0], pic_y + 12 + map_p(cp.left_eye_outer)[1])
        draw.rounded_rectangle([ey_l[0] + 15, ey_l[1] - 45, ey_l[0] + 185, ey_l[1] + 8], radius=12, fill=(255, 255, 255, 240), outline=COLOR_BORDER_GOLD, width=1)
        draw.text((ey_l[0] + 26, ey_l[1] - 35), "外眦仰角 +9.5°", font=font_badge, fill=COLOR_GOLD_DARK)
        
    # 肖像卡底部精炼标签
    draw.rounded_rectangle([pic_x + 35, pic_y + pic_h - 75, pic_x + pic_w - 35, pic_y + pic_h - 18], radius=14, fill=COLOR_GOLD_LIGHT, outline=COLOR_BORDER_GOLD, width=1)
    draw.text((pic_x + 160, pic_y + pic_h - 60), "★ 478 锚点纯客观量测 · 电影级神颜骨相", font=font_badge, fill=COLOR_GOLD_DARK)
    
    # 3. 左侧极简大留白主视觉 (只保留 1 个大核心标题 + 1 个副标 + 1 个行动按钮，彻底消灭密集文字！)
    lx = 100
    
    # 顶部品牌胶囊
    draw.rounded_rectangle([lx, 100, lx + 360, 155], radius=28, fill=COLOR_GOLD_LIGHT, outline=COLOR_BORDER_GOLD, width=1)
    draw.ellipse([lx + 20, 119, lx + 36, 135], fill=COLOR_GOLD)
    draw.text((lx + 48, 114), "相度 AI相面 · 微信小程序", font=font_badge, fill=COLOR_GOLD_DARK)
    
    # 核心超大爆款标题 (两行巨大醒目，在手机 B站首页一眼看清！)
    draw.text((lx, 215), "为什么顶级骨相", font=font_headline, fill=COLOR_TEXT_MAIN)
    draw.text((lx, 325), "怎么拍都高级？", font=font_headline, fill=COLOR_GOLD)
    
    # 副标题说明 (精简有力)
    draw.text((lx, 460), "478 关键点高精量测 · 测测你的面部骨骼基因", font=font_sub, fill=COLOR_TEXT_MUTED)
    draw.line([lx, 520, lx + 740, 520], fill=COLOR_BORDER_GOLD, width=2)
    
    # 2 个核心亮点大徽章 (替代之前密密麻麻的小卡片和长句子)
    b_y = 570
    b_w = 350
    b_h = 140
    
    # 徽章 1
    draw.rounded_rectangle([lx, b_y, lx + b_w, b_y + b_h], radius=16, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
    draw.rounded_rectangle([lx, b_y, lx + 6, b_y + b_h], radius=3, fill=COLOR_GOLD)
    draw.text((lx + 28, b_y + 24), "108.7° 刚柔折角", font=font_card, fill=COLOR_GOLD)
    draw.text((lx + 28, b_y + 80), "立体支撑 · 天然抗镜头畸变", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 徽章 2
    draw.rounded_rectangle([lx + b_w + 35, b_y, lx + b_w * 2 + 35, b_y + b_h], radius=16, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
    draw.rounded_rectangle([lx + b_w + 35, b_y, lx + b_w + 41, b_y + b_h], radius=3, fill=COLOR_TEAL)
    draw.text((lx + b_w + 63, b_y + 24), "+9.5° 正向飞扬", font=font_card, fill=COLOR_TEAL)
    draw.text((lx + b_w + 63, b_y + 80), "清冷灵动 · 神采奕奕高智感", font=font_small, fill=COLOR_TEXT_MUTED)
    
    # 底部一键搜索极简大卡 (行动召唤)
    bar_y = 780
    bar_w = 735
    bar_h = 95
    draw.rounded_rectangle([lx, bar_y, lx + bar_w, bar_y + bar_h], radius=48, fill=(247, 246, 242), outline=COLOR_GOLD, width=2)
    
    # 放大镜图标
    mg_cx = lx + 55
    mg_cy = bar_y + bar_h // 2
    draw.ellipse([mg_cx - 16, mg_cy - 16, mg_cx + 16, mg_cy + 16], outline=COLOR_GOLD, width=4)
    draw.line([mg_cx + 11, mg_cy + 11, mg_cx + 25, mg_cy + 25], fill=COLOR_GOLD, width=5)
    
    draw.text((lx + 95, bar_y + 24), "微信搜「相度」立即测测", font=font_card, fill=COLOR_TEXT_MAIN)
    
    # 搜索按钮
    draw.rounded_rectangle([lx + bar_w - 170, bar_y + 12, lx + bar_w - 15, bar_y + bar_h - 12], radius=35, fill=COLOR_GOLD)
    draw.text((lx + bar_w - 128, bar_y + 26), "去测", font=font_card, fill=(255, 255, 255))
    
    # 底部极度微小安全提示
    draw.text((lx + 30, bar_y + bar_h + 30), "★ 纯内存实时计算 · 阅后即焚零存留 · 严密捍卫肖像隐私", font=font_small, fill=COLOR_TEXT_MUTED)
    
    out_path = os.path.join(WORKDIR, "bilibili_cover.jpg")
    im.save(out_path, quality=95)
    print("Minimalist Bilibili cover generated successfully at:", os.path.abspath(out_path))

if __name__ == "__main__":
    generate_cover()

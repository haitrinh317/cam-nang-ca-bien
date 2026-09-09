#!/usr/bin/env python3
"""
scripts/generate_og_options.py
Tạo 2 phương án ảnh OpenGraph sharing link (1200x630) chuẩn nhận diện cá nhân haitrinh:
- Phương án 1: Digital Archive & Tech Bento (Huy hiệu số & Bento thẻ thống kê khoa học)
- Phương án 2: Photorealistic Ocean Hero & Glassmorphic Card (Nghệ thuật đại dương & Card kính nổi)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKGROUND_ART = '/Users/macbook2016/.gemini/antigravity-ide/brain/43cec54a-ae14-4653-bda1-8a59a02f6bf3/ocean_hero_background_1788962902919.jpg'

W, H = 1200, 630

# Sử dụng system font Arial Bold hỗ trợ 100% tiếng Việt không lỗi font
SYS_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
SYS_REG = '/System/Library/Fonts/Supplemental/Arial.ttf'

def get_fonts():
    return {
        'title': ImageFont.truetype(SYS_BOLD, 42),
        'title_lg': ImageFont.truetype(SYS_BOLD, 44),
        'kpi': ImageFont.truetype(SYS_BOLD, 36),
        'pill': ImageFont.truetype(SYS_BOLD, 13),
        'sub': ImageFont.truetype(SYS_BOLD, 19),
        'desc': ImageFont.truetype(SYS_REG, 16),
        'badge': ImageFont.truetype(SYS_BOLD, 14),
        'domain': ImageFont.truetype(SYS_BOLD, 18),
        'emblem_text': ImageFont.truetype(SYS_BOLD, 32),
        'emblem_sub': ImageFont.truetype(SYS_BOLD, 13),
    }

def draw_modern_emblem(draw, cx, cy, radius):
    """Vẽ huy hiệu sinh thái biển số hóa (Modern Marine Digital Crest) cho Option 1."""
    # Vòng tròn ngoài phát sáng
    for r in range(radius + 20, radius, -2):
        alpha = int((1 - (r - radius) / 20) * 60)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 212, 184, alpha), width=1)

    # Vòng tròn chính
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(0, 212, 184, 210), width=2)
    # Vòng tròn trong
    inner_r = radius - 16
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], outline=(255, 209, 102, 180), width=1)

    # Các dấu vạch la bàn số (Compass ticks)
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        length = 10 if angle % 90 == 0 else (6 if angle % 45 == 0 else 3)
        color = (255, 209, 102, 220) if angle % 90 == 0 else (0, 212, 184, 140)
        x1 = cx + (radius - 6) * math.cos(rad)
        y1 = cy + (radius - 6) * math.sin(rad)
        x2 = cx + (radius - 6 - length) * math.cos(rad)
        y2 = cy + (radius - 6 - length) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2 if angle % 45 == 0 else 1)

    # Các lớp sóng biển hình học (Stylized Ocean Waves)
    wave_r = inner_r - 25
    for w_offset, w_color in [(-12, (0, 180, 216, 160)), (0, (0, 212, 184, 220)), (12, (78, 205, 196, 180))]:
        points = []
        for a in range(-65, 66, 10):
            rad = math.radians(a)
            px = cx + wave_r * math.cos(rad)
            py = cy + wave_r * math.sin(rad) * 0.4 + w_offset + math.sin(math.radians(a * 4)) * 6
            points.append((px, py))
        for p1, p2 in zip(points[:-1], points[1:]):
            draw.line([p1, p2], fill=w_color, width=2)


def generate_option_1():
    """Phương án 1: Digital Archive & Tech Bento."""
    fonts = get_fonts()
    img = Image.new('RGBA', (W, H), color='#050c1e')
    draw = ImageDraw.Draw(img)

    # 1. Gradient nền đại dương sâu thẳm
    for y in range(H):
        ratio = y / H
        r = int(5 + ratio * 8)
        g = int(12 + ratio * 20)
        b = int(30 + ratio * 45)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 2. Glow ánh sáng radial
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    for radius in range(300, 0, -10):
        alpha = int((1 - radius / 300) * 45)
        g_draw.ellipse([240 - radius, 315 - radius, 240 + radius, 315 + radius], fill=(0, 212, 184, alpha))
    for radius in range(400, 0, -15):
        alpha = int((1 - radius / 400) * 35)
        g_draw.ellipse([1050 - radius, 120 - radius, 1050 + radius, 120 + radius], fill=(0, 119, 182, alpha))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 3. Viền card tinh tế (Luxury outer frame)
    draw.rectangle([24, 24, W - 25, H - 25], outline=(0, 212, 184, 60), width=1)
    draw.rectangle([28, 28, W - 29, H - 29], outline=(255, 255, 255, 12), width=1)

    # 4. Khối Huy Hiệu Cá Nhân Bên Trái (Left Emblem Card)
    card_left = 60
    card_top = 70
    card_w = 360
    card_h = 490

    # Glassmorphism container
    glass = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gl_draw = ImageDraw.Draw(glass)
    gl_draw.rounded_rectangle([card_left, card_top, card_left + card_w, card_top + card_h], radius=24, fill=(10, 22, 44, 210), outline=(0, 212, 184, 80), width=1)
    img = Image.alpha_composite(img, glass)
    draw = ImageDraw.Draw(img)

    # Vẽ huy hiệu đại dương tại tâm cột trái
    emblem_cx = card_left + card_w // 2
    emblem_cy = card_top + 160
    draw_modern_emblem(draw, emblem_cx, emblem_cy, radius=105)

    # Monogram HT ở trung tâm huy hiệu
    ht_text = "HT"
    bbox = fonts['emblem_text'].getbbox(ht_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((emblem_cx - tw // 2, emblem_cy - th // 2 - 25), ht_text, font=fonts['emblem_text'], fill=(255, 255, 255, 255))

    ht_sub = "HAITRINH"
    s_bbox = fonts['emblem_sub'].getbbox(ht_sub)
    s_tw = s_bbox[2] - s_bbox[0]
    draw.text((emblem_cx - s_tw // 2, emblem_cy + 15), ht_sub, font=fonts['emblem_sub'], fill=(255, 209, 102, 230))

    # Nhãn phía dưới huy hiệu trong card
    seal_tag = "VIETNAM MARINE ARCHIVE"
    st_bbox = fonts['pill'].getbbox(seal_tag)
    st_tw = st_bbox[2] - st_bbox[0]
    draw.text((emblem_cx - st_tw // 2, card_top + 305), seal_tag, font=fonts['pill'], fill=(0, 212, 184, 240))

    seal_sub = "Cơ sở dữ liệu phân loại học số"
    ss_bbox = fonts['desc'].getbbox(seal_sub)
    ss_tw = ss_bbox[2] - ss_bbox[0]
    draw.text((emblem_cx - ss_tw // 2, card_top + 332), seal_sub, font=fonts['desc'], fill=(148, 163, 184, 255))

    # Dòng định vị cá nhân
    author_tag = "Phát triển bởi haitrinh"
    at_bbox = fonts['badge'].getbbox(author_tag)
    at_tw = at_bbox[2] - at_bbox[0]
    
    p_box = [emblem_cx - at_tw // 2 - 16, card_top + 386, emblem_cx + at_tw // 2 + 16, card_top + 418]
    p_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    p_d = ImageDraw.Draw(p_img)
    p_d.rounded_rectangle(p_box, radius=16, fill=(0, 212, 184, 25), outline=(0, 212, 184, 120), width=1)
    img = Image.alpha_composite(img, p_img)
    draw = ImageDraw.Draw(img)
    draw.text((emblem_cx - at_tw // 2, card_top + 394), author_tag, font=fonts['badge'], fill=(0, 212, 184, 255))

    # 5. Cột Nội Dung Phía Phải (Right Content Section)
    x_content = 465

    # Top Tag Pill
    top_pill = "CƠ SỞ DỮ LIỆU ĐA DẠNG SINH HỌC BIỂN • HAITRINH"
    tp_bbox = fonts['pill'].getbbox(top_pill)
    tp_w = tp_bbox[2] - tp_bbox[0]
    
    tp_box = [x_content, 70, x_content + tp_w + 32, 100]
    tp_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    tp_d = ImageDraw.Draw(tp_img)
    tp_d.rounded_rectangle(tp_box, radius=15, fill=(0, 212, 184, 30), outline=(0, 212, 184, 160), width=1)
    img = Image.alpha_composite(img, tp_img)
    draw = ImageDraw.Draw(img)
    draw.text((x_content + 16, 77), top_pill, font=fonts['pill'], fill=(144, 224, 239, 255))

    # Main Title
    draw.text((x_content, 118), "TRA CỨU THÔNG TIN", font=fonts['title'], fill=(255, 255, 255, 255))
    draw.text((x_content, 168), "SINH VẬT BIỂN VIỆT NAM", font=fonts['title'], fill=(255, 209, 102, 255))

    # Subtitle
    draw.text((x_content, 230), "Số hóa 2.671+ loài từ các công trình phân loại học nguyên bản", font=fonts['sub'], fill=(202, 240, 248, 255))
    draw.text((x_content, 264), "Hệ thống tra cứu danh pháp chuẩn hóa, hình thái & độc học cấp cứu", font=fonts['desc'], fill=(148, 163, 184, 255))

    # Divider line
    draw.line([(x_content, 302), (W - 60, 302)], fill=(0, 212, 184, 70), width=1)

    # 6 Badges Grid (3 hàng x 2 cột) - sử dụng dot thay cho emoji để tránh lỗi font
    badges = [
        ("1.764 Loài Cá biển (6 Tập)", (0, 212, 184)),
        ("672 Loài Thực vật biển", (78, 205, 196)),
        ("132 Loài Giáp xác biển", (255, 209, 102)),
        ("27 Loài Rắn biển Việt Nam", (244, 162, 97)),
        ("76 Loài Động vật độc", (251, 113, 133)),
        ("100% Xác thực WoRMS", (56, 189, 248)),
    ]

    bx = x_content
    by = 320
    col_w = 325
    row_h = 46

    for i, (b_text, b_col) in enumerate(badges):
        cur_x = bx + (i % 2) * col_w
        cur_y = by + (i // 2) * row_h

        b_box = [cur_x, cur_y, cur_x + 310, cur_y + 36]
        b_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        b_d = ImageDraw.Draw(b_img)
        b_d.rounded_rectangle(b_box, radius=10, fill=(12, 25, 50, 160), outline=(*b_col, 100), width=1)
        img = Image.alpha_composite(img, b_img)
        draw = ImageDraw.Draw(img)

        # Draw indicator dot
        draw.ellipse([cur_x + 14, cur_y + 14, cur_x + 22, cur_y + 22], fill=(*b_col, 255))
        draw.text((cur_x + 30, cur_y + 9), b_text, font=fonts['badge'], fill=(*b_col, 255))

    # Footer Domain & Credit
    draw.line([(x_content, 480), (W - 60, 480)], fill=(255, 255, 255, 15), width=1)
    draw.text((x_content, 502), "https://www.tracuusinhvatbien.app", font=fonts['domain'], fill=(0, 212, 184, 255))
    draw.text((x_content + 370, 504), "Dự án phát triển độc lập bởi haitrinh", font=fonts['desc'], fill=(148, 163, 184, 240))

    # Save
    out_1 = 'public/og-option1.png'
    img.convert('RGB').save(out_1, format='PNG', optimize=True)
    print(f"✅ Option 1 saved to {out_1}")


def generate_option_2():
    """Phương án 2: Photorealistic Ocean Hero & Glassmorphic Card."""
    fonts = get_fonts()

    # Load and prepare background
    if os.path.exists(BACKGROUND_ART):
        bg = Image.open(BACKGROUND_ART).convert('RGBA')
        bg = bg.resize((W, H), Image.Resampling.LANCZOS)
    else:
        bg = Image.new('RGBA', (W, H), color='#041b2d')

    # Add dark oceanic vignette layer
    vignette = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    
    for x in range(W):
        ratio = x / W
        alpha = int(210 - ratio * 140)
        v_draw.line([(x, 0), (x, H)], fill=(4, 15, 30, max(0, alpha)))
        
    for y in range(H - 120, H):
        ratio = (y - (H - 120)) / 120
        alpha = int(ratio * 150)
        v_draw.line([(0, y), (W, y)], fill=(2, 8, 18, alpha))

    base = Image.alpha_composite(bg, vignette)

    # Card kính nổi bên trái (Left-anchored Floating Glass Card)
    card_x1 = 55
    card_y1 = 45
    card_w = 690
    card_h = 540
    card_x2 = card_x1 + card_w
    card_y2 = card_y1 + card_h

    # Glass layer with rounded rectangle
    glass = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gl_draw = ImageDraw.Draw(glass)
    
    # Soft shadow
    for s in range(16, 0, -2):
        gl_draw.rounded_rectangle([card_x1 - s, card_y1 - s + 4, card_x2 + s, card_y2 + s + 4], radius=28, fill=(0, 0, 0, int((1 - s/16) * 45)))
    
    # Main frosted glass fill
    gl_draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=24, fill=(5, 14, 32, 225), outline=(0, 212, 184, 130), width=1)
    gl_draw.rounded_rectangle([card_x1 + 4, card_y1 + 4, card_x2 - 4, card_y2 - 4], radius=20, outline=(255, 255, 255, 18), width=1)

    base = Image.alpha_composite(base, glass)
    draw = ImageDraw.Draw(base)

    # 1. Top Pill Badge
    tx = card_x1 + 38
    ty = card_y1 + 36

    pill_txt = "DỰ ÁN SỐ HÓA PHÂN LOẠI HỌC • HAITRINH"
    p_bbox = fonts['pill'].getbbox(pill_txt)
    p_w = p_bbox[2] - p_bbox[0]

    p_box = [tx, ty, tx + p_w + 30, ty + 28]
    p_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    p_d = ImageDraw.Draw(p_img)
    p_d.rounded_rectangle(p_box, radius=14, fill=(0, 212, 184, 35), outline=(0, 212, 184, 180), width=1)
    base = Image.alpha_composite(base, p_img)
    draw = ImageDraw.Draw(base)
    draw.text((tx + 15, ty + 6), pill_txt, font=fonts['pill'], fill=(144, 224, 239, 255))

    # 2. Main Title
    draw.text((tx, ty + 44), "TRA CỨU THÔNG TIN", font=fonts['title_lg'], fill=(255, 255, 255, 255))
    draw.text((tx, ty + 98), "SINH VẬT BIỂN VIỆT NAM", font=fonts['title_lg'], fill=(255, 209, 102, 255))

    # 3. Big Highlight KPI Pill (2.671+ Loài)
    kpi_txt = "2.671+ LOÀI SINH VẬT BIỂN"
    kpi_y = ty + 164
    draw.text((tx, kpi_y), kpi_txt, font=fonts['kpi'], fill=(0, 212, 184, 255))

    # Subtitle
    draw.text((tx, kpi_y + 48), "Hệ thống số hóa toàn diện: Hình thái • Sinh thái • Độc học & Cấp cứu", font=fonts['sub'], fill=(202, 240, 248, 255))
    draw.text((tx, kpi_y + 78), "Một dự án nghiên cứu & bảo tồn đại dương được phát triển bởi haitrinh", font=fonts['desc'], fill=(148, 163, 184, 255))

    # Divider
    draw.line([(tx, kpi_y + 110), (card_x2 - 38, kpi_y + 110)], fill=(0, 212, 184, 80), width=1)

    # 4. Collection Pills Row - sử dụng indicator dot
    coll_pills = [
        ("Cá biển (1.764)", (0, 212, 184)),
        ("Thực vật (672)", (78, 205, 196)),
        ("Giáp xác (132)", (255, 209, 102)),
        ("Rắn biển (27)", (244, 162, 97)),
        ("Độc biển (76)", (251, 113, 133))
    ]
    cur_px = tx
    pill_y = kpi_y + 126
    for p_name, p_color in coll_pills:
        b_box_t = fonts['badge'].getbbox(p_name)
        pw = b_box_t[2] - b_box_t[0] + 28
        
        c_box = [cur_px, pill_y, cur_px + pw, pill_y + 32]
        c_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        c_d = ImageDraw.Draw(c_img)
        c_d.rounded_rectangle(c_box, radius=8, fill=(10, 25, 50, 180), outline=(*p_color, 120), width=1)
        base = Image.alpha_composite(base, c_img)
        draw = ImageDraw.Draw(base)
        
        # dot
        draw.ellipse([cur_px + 8, pill_y + 12, cur_px + 14, pill_y + 18], fill=(*p_color, 255))
        draw.text((cur_px + 20, pill_y + 7), p_name, font=fonts['badge'], fill=(*p_color, 255))
        cur_px += pw + 8

    # 5. Footer URL & WoRMS verification badge
    foot_y = kpi_y + 180
    draw.text((tx, foot_y), "https://www.tracuusinhvatbien.app", font=fonts['domain'], fill=(0, 212, 184, 255))
    
    # WoRMS badge with indicator dot
    draw.ellipse([tx + 360, foot_y + 6, tx + 368, foot_y + 14], fill=(255, 209, 102, 255))
    draw.text((tx + 375, foot_y + 1), "100% Xác thực danh pháp WoRMS", font=fonts['desc'], fill=(255, 209, 102, 240))

    # Save
    out_2 = 'public/og-option2.png'
    base.convert('RGB').save(out_2, format='PNG', optimize=True)
    print(f"✅ Option 2 saved to {out_2}")

if __name__ == '__main__':
    generate_option_1()
    generate_option_2()

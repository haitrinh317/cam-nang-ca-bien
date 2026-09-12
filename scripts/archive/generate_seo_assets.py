#!/usr/bin/env python3
"""
generate_seo_assets.py
Tạo favicon.ico và og-default.png chất lượng cao cho Cẩm Nang Sinh Vật Biển Việt Nam.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_favicon():
    logo_path = 'public/logo.png'
    ico_path = 'public/favicon.ico'
    if not os.path.exists(logo_path):
        print(f"Error: {logo_path} not found")
        return

    im = Image.open(logo_path).convert('RGBA')
    # Tạo ico đa kích thước: 16x16, 32x32, 48x48
    sizes = [(16, 16), (32, 32), (48, 48)]
    im.save(ico_path, format='ICO', sizes=sizes)
    print(f"✅ Generated {ico_path} with sizes {sizes}")

def generate_og_image():
    W, H = 1200, 630
    img = Image.new('RGBA', (W, H), color='#060d1f')
    draw = ImageDraw.Draw(img)

    # 1. Gradient background (Deep navy to oceanic blue)
    for y in range(H):
        ratio = y / H
        r = int(6 + ratio * 10)
        g = int(13 + ratio * 28)
        b = int(31 + ratio * 55)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 2. Subtle radial glow behind logo and header
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    
    # Left cyan glow for logo
    for radius in range(260, 0, -10):
        alpha = int((1 - radius / 260) * 45)
        glow_draw.ellipse([220 - radius, 315 - radius, 220 + radius, 315 + radius], fill=(0, 180, 216, alpha))
        
    # Top-right blue glow
    for radius in range(350, 0, -15):
        alpha = int((1 - radius / 350) * 35)
        glow_draw.ellipse([1000 - radius, 100 - radius, 1000 + radius, 100 + radius], fill=(0, 119, 182, alpha))

    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 3. Outer border / card frame (subtle luxury gold/cyan stroke)
    draw.rectangle([24, 24, W - 25, H - 25], outline=(0, 180, 216, 60), width=1)
    draw.rectangle([28, 28, W - 29, H - 29], outline=(255, 255, 255, 15), width=1)

    # 4. Insert Logo on the left
    logo_path = 'public/logo.png'
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert('RGBA')
        logo_size = 360
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Logo container card with soft shadow / border
        card_box = [60, 135, 60 + logo_size + 40, 135 + logo_size + 40]
        # Glassmorphic rounded rect
        glass = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glass)
        g_draw.rounded_rectangle(card_box, radius=24, fill=(10, 25, 47, 180), outline=(0, 180, 216, 90), width=2)
        img = Image.alpha_composite(img, glass)
        draw = ImageDraw.Draw(img)
        
        # Paste logo
        img.paste(logo, (80, 155), logo)

    # 5. Load Fonts
    font_paths = [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman.ttf',
        '/System/Library/Fonts/HelveticaNeue.ttc'
    ]
    
    bold_font_file = None
    regular_font_file = None
    for fp in font_paths:
        if os.path.exists(fp):
            if 'Bold' in fp and not bold_font_file:
                bold_font_file = fp
            elif not regular_font_file:
                regular_font_file = fp

    if not bold_font_file:
        bold_font_file = regular_font_file or '/System/Library/Fonts/Supplemental/Arial.ttf'

    try:
        font_pill = ImageFont.truetype(bold_font_file, 16)
        font_title1 = ImageFont.truetype(bold_font_file, 46)
        font_title2 = ImageFont.truetype(bold_font_file, 46)
        font_sub = ImageFont.truetype(regular_font_file or bold_font_file, 22)
        font_desc = ImageFont.truetype(regular_font_file or bold_font_file, 18)
        font_badge = ImageFont.truetype(bold_font_file, 15)
    except Exception as e:
        print(f"Font loading fallback: {e}")
        font_pill = font_title1 = font_title2 = font_sub = font_desc = font_badge = ImageFont.load_default()

    # 6. Content Section (Right side)
    x_text = 520

    # Pill badge
    pill_text = "CƠ SỞ DỮ LIỆU SINH HỌC BIỂN"
    pill_box = [x_text, 105, x_text + 300, 137]
    pill_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(pill_img)
    p_draw.rounded_rectangle(pill_box, radius=16, fill=(0, 180, 216, 35), outline=(0, 180, 216, 180), width=1)
    img = Image.alpha_composite(img, pill_img)
    draw = ImageDraw.Draw(img)
    draw.text((x_text + 18, 112), pill_text, font=font_pill, fill=(144, 224, 239, 255))

    # Main Title
    draw.text((x_text, 160), "CẨM NANG SINH VẬT BIỂN", font=font_title1, fill=(255, 255, 255, 255))
    draw.text((x_text, 220), "VIỆT NAM", font=font_title2, fill=(255, 209, 102, 255)) # Warm Gold accent

    # Tagline
    draw.text((x_text, 292), "Số hóa 2.436+ loài Cá biển & Rong biển Việt Nam", font=font_sub, fill=(202, 240, 248, 255))

    # Sub-tagline: Mô tả khoa học
    draw.text((x_text, 332), "Hệ thống tra cứu danh pháp, hình thái học & phân bố sinh thái", font=font_desc, fill=(148, 163, 184, 255))

    # Divider line
    draw.line([(x_text, 375), (W - 80, 375)], fill=(0, 180, 216, 60), width=1)

    # Feature Badges
    badges = [
        ("✓ 100% Xác thực WoRMS", (38, 198, 218)),
        ("✓ 6 Tập Ngư Loại Học", (255, 209, 102)),
        ("✓ 672 Loài Thực Vật Biển", (78, 205, 196)),
        ("✓ Tra cứu Hình thái & Sinh học", (144, 224, 239))
    ]

    bx = x_text
    by = 398
    col_w = 300
    for i, (b_text, b_color) in enumerate(badges):
        cur_x = bx + (i % 2) * col_w
        cur_y = by + (i // 2) * 44
        
        # Mini badge box
        b_box = [cur_x, cur_y, cur_x + 280, cur_y + 34]
        b_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(b_img)
        b_draw.rounded_rectangle(b_box, radius=8, fill=(15, 23, 42, 140), outline=(*b_color, 90), width=1)
        img = Image.alpha_composite(img, b_img)
        draw = ImageDraw.Draw(img)
        
        draw.text((cur_x + 14, cur_y + 8), b_text, font=font_badge, fill=(*b_color, 255))

    # Footer domain url
    draw.text((x_text, 515), "https://cam-nang-ca-bien.vercel.app", font=font_desc, fill=(0, 180, 216, 220))

    # Save final image
    final_rgb = img.convert('RGB')
    out_path = 'public/og-default.png'
    final_rgb.save(out_path, format='PNG', optimize=True)
    print(f"✅ Generated {out_path} ({W}x{H})")

if __name__ == '__main__':
    generate_favicon()
    generate_og_image()

#!/usr/bin/env python3
"""
scripts/upload_ranbien_book_photos.py
Trích xuất ảnh thực địa / mẫu vật từ PDF Rắn biển Việt Nam, tối ưu WebP
và tải lên Supabase Storage bucket 'species-photos', đồng thời ghi nhận vào
bảng 'species' (photo_url) và 'species_photos'.
"""

import io
import os
import sys
import uuid
from pathlib import Path

import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
from PIL import Image, ImageChops

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

# ── Load Envs ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
)

BUCKET = "species-photos"
COLLECTION = "ran-bien"
PDF_PATH = BASE_DIR / "Documents" / "ran-bien" / "Rắn biển Việt Nam.pdf"

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ── Map vị trí từng loài trên 16 trang đôi PDF ───────────────────────
SPECIES_PAGES = [
    (2, "LEFT", 1, "Aipysurus eydouxii"),
    (2, "RIGHT", 2, "Emydocephalus annulatus"),
    (3, "LEFT", 3, "Hydrophis annandalei"),
    (3, "RIGHT", 4, "Hydrophis anomalus"),
    (4, "LEFT", 5, "Hydrophis atriceps"),
    (4, "RIGHT", 6, "Hydrophis belcheri"),
    (5, "LEFT", 7, "Hydrophis brookii"),
    (5, "RIGHT", 8, "Hydrophis caerulescens"),
    (6, "LEFT", 9, "Hydrophis curtus"),
    (6, "RIGHT", 10, "Hydrophis cyanocinctus"),
    (7, "LEFT", 11, "Hydrophis jerdonii"),
    (7, "RIGHT", 12, "Hydrophis klossi"),
    (8, "LEFT", 13, "Hydrophis lamberti"),
    (8, "RIGHT", 14, "Hydrophis melanocephalus"),
    (9, "LEFT", 15, "Hydrophis ornatus"),
    (9, "RIGHT", 16, "Hydrophis pachycercos"),
    (10, "LEFT", 17, "Hydrophis parviceps"),
    (10, "RIGHT", 18, "Hydrophis peronii"),
    (11, "LEFT", 19, "Hydrophis platura"),
    (11, "RIGHT", 20, "Hydrophis schistosus"),
    (12, "LEFT", 21, "Hydrophis spiralis"),
    (12, "RIGHT", 22, "Hydrophis stokesii"),
    (13, "LEFT", 23, "Hydrophis torquatus diadema"),
    (13, "RIGHT", 24, "Hydrophis viperina"),
    (14, "LEFT", 25, "Laticauda colubrina"),
    (14, "RIGHT", 26, "Microcephalophis gracilis"),
    (15, "LEFT", 27, "Acrochordus granulatus"),
]


def supa_upload(storage_path: str, file_bytes: bytes) -> bool:
    """Tải file lên Supabase Storage bucket."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/webp",
        "x-upsert": "true",
    }
    resp = requests.post(url, headers=headers, data=file_bytes, timeout=60)
    return resp.status_code in (200, 201)


def supa_patch_species(species_id: str, public_url: str) -> bool:
    """Cập nhật photo_url vào bảng species."""
    url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{species_id}"
    resp = requests.patch(
        url,
        headers={**HEADERS_SUPA, "Prefer": "return=minimal"},
        json={"photo_url": public_url},
        timeout=30,
    )
    return resp.status_code in (200, 204)


def supa_insert_photo_record(species_id: str, storage_path: str) -> bool:
    """Ghi bản ghi vào bảng species_photos."""
    url = f"{SUPABASE_URL}/rest/v1/species_photos"
    record = {
        "id": str(uuid.uuid4()),
        "species_id": species_id,
        "storage_path": storage_path,
        "source": "book_scan",
        "photographer": "Viện Hải dương học Nha Trang / WAR / IOC VN",
        "license": "educational",
        "source_url": "https://cam-nang-ca-bien.vercel.app/books/ran-bien",
        "is_primary": True,
        "sort_order": 0,
    }
    resp = requests.post(
        url,
        headers={**HEADERS_SUPA, "Prefer": "return=minimal"},
        json=record,
        timeout=30,
    )
    return resp.status_code in (200, 201, 204)


def extract_species_image(doc, pno: int, side: str) -> Image.Image | None:
    """Trích xuất và cắt gọt ảnh của loài từ trang PDF."""
    page = doc[pno]
    w, h = page.rect.width, page.rect.height
    mid_x = w / 2
    half = fitz.Rect(0, 0, mid_x, h) if side == "LEFT" else fitz.Rect(mid_x, 0, w, h)

    # Lấy các khối text
    blocks = [fitz.Rect(b[:4]) for b in page.get_text("blocks", clip=half) if b[4].strip()]

    # Lấy các khối ảnh trên nửa trang này
    il = page.get_images()
    img_rects = []
    for img in il:
        for r in page.get_image_rects(img[0]):
            cx = (r.x0 + r.x1) / 2
            cy = (r.y0 + r.y1) / 2
            if half.contains(fitz.Point(cx, cy)) and r.width > 30 and r.height > 30:
                clamped = fitz.Rect(
                    max(r.x0, half.x0),
                    max(r.y0, 0),
                    min(r.x1, half.x1),
                    min(r.y1, h),
                )
                img_rects.append(clamped)

    if not img_rects:
        return None

    union_img = fitz.Rect()
    for r in img_rects:
        union_img.include_rect(r)

    safe_y0 = union_img.y0
    safe_y1 = union_img.y1
    img_cy = (union_img.y0 + union_img.y1) / 2

    for tb in blocks:
        if tb.y1 <= img_cy and tb.intersects(fitz.Rect(union_img.x0, union_img.y0, union_img.x1, img_cy)):
            safe_y0 = max(safe_y0, tb.y1 + 2)
        if tb.y0 >= img_cy and tb.intersects(fitz.Rect(union_img.x0, img_cy, union_img.x1, union_img.y1)):
            safe_y1 = min(safe_y1, tb.y0 - 2)

    clip = fitz.Rect(union_img.x0, safe_y0, union_img.x1, safe_y1)
    if clip.width < 20 or clip.height < 20:
        clip = union_img

    pix = page.get_pixmap(dpi=250, clip=clip)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Autocrop nền trắng
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        m = 10
        box = (
            max(0, bbox[0] - m),
            max(0, bbox[1] - m),
            min(img.width, bbox[2] + m),
            min(img.height, bbox[3] + m),
        )
        img = img.crop(box)

    # Resize max width 960px nếu lớn hơn
    if img.width > 960:
        ratio = 960 / img.width
        new_size = (960, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    return img


def main():
    print("=" * 65)
    print("🐍 TRÍCH XUẤT VÀ TẢI ẢNH RẮN BIỂN LÊN SUPABASE STORAGE")
    print("=" * 65)

    if not PDF_PATH.exists():
        print(f"❌ Không tìm thấy file PDF tại: {PDF_PATH}")
        sys.exit(1)

    doc = fitz.open(str(PDF_PATH))
    success_count = 0
    no_img_count = 0

    for pno, side, sp_num, sp_name in SPECIES_PAGES:
        species_id = f"ranbien-species-{sp_num}"
        img = extract_species_image(doc, pno, side)

        if img is None:
            print(f"[{sp_num:02d}/27] ⚪ {sp_name} ({species_id}): Không có ảnh trong sách.")
            no_img_count += 1
            continue

        # Chuyển sang WebP
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=85)
        file_bytes = buffer.getvalue()

        storage_path = f"ran-bien/{species_id}/01.webp"
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"

        # Upload
        up_ok = supa_upload(storage_path, file_bytes)
        if not up_ok:
            print(f"[{sp_num:02d}/27] ❌ {sp_name}: Lỗi upload Storage!")
            continue

        # Patch species
        supa_patch_species(species_id, public_url)

        # Insert species_photos
        supa_insert_photo_record(species_id, storage_path)

        size_kb = len(file_bytes) / 1024
        print(f"[{sp_num:02d}/27] ✅ {sp_name} -> {storage_path} ({img.width}x{img.height}, {size_kb:.1f}KB)")
        success_count += 1

    print("\n" + "=" * 65)
    print(f"📊 KẾT QUẢ TRÍCH XUẤT & UPLOAD:")
    print(f"  • Đã tải lên thành công: {success_count}/27 loài")
    print(f"  • Không có ảnh trong sách: {no_img_count}/27 loài (sẽ sync iNaturalist)")
    print("=" * 65)


if __name__ == "__main__":
    main()

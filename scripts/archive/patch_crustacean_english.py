#!/usr/bin/env python3
"""
scripts/patch_crustacean_english.py
Dịch thuật và bổ sung các trường tiếng Anh học thuật (en_size, en_distribution)
cho toàn bộ 132 loài giáp xác trong collection 'giap-xac' trên Supabase.

Sử dụng Gemini API (gemini-flash-lite-latest) với system prompt chuyên ngành
Carcinology (Giáp xác học), xử lý theo lô (batch of 15) và cập nhật trực tiếp vào Supabase.

Tác giả: Trợ lý Antigravity cho chú Chình
Ngày thực hiện: 15/09/2026
"""

import os
import sys
import json
import time
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[LỖI] Thiếu Supabase credentials!")
    sys.exit(1)

if not GEMINI_KEY:
    print("[LỖI] Thiếu GEMINI_API_KEY!")
    sys.exit(1)

HEADERS_SUPA = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]

SYSTEM_PROMPT = """You are a senior marine biologist and carcinologist at the Institute of Oceanography in Nha Trang, Vietnam.
Your task is to translate Vietnamese marine crustacean specimen data (specifically size and distribution notes from scientific monographs) into concise, standardized, academic English.

Rules:
1. "Thế giới:" -> "Global:" or "World:"
2. "Việt Nam:" -> "Vietnam:"
3. "Chiều dài thân (Lt)" -> "Total body length (Lt)"
4. "Chiều dài mai (Lc)" -> "Carapace length (Lc)"
5. Vietnamese sea geographic entities:
   - "Vịnh Bắc Bộ" -> "Gulf of Tonkin"
   - "Vịnh Thái Lan" -> "Gulf of Thailand"
   - "vịnh Nha Trang" -> "Nha Trang Bay"
   - "quần đảo Hoàng Sa" -> "Paracel Islands"
   - "quần đảo Trường Sa" -> "Spratly Islands"
   - "Côn Đảo" -> "Con Dao Islands"
   - "Phú Quốc" -> "Phu Quoc Island"
   - "Hồng Hải" -> "Red Sea"
   - "Ấn Độ Dương" -> "Indian Ocean"
   - "Tây Thái Bình Dương" -> "Western Pacific"
   - "Thái Bình Dương" -> "Pacific Ocean"
   - "Ấn Độ - Tây Thái Bình Dương" -> "Indo-West Pacific"
   - "Đà Nẵng" -> "Da Nang"
   - "Khánh Hòa" -> "Khanh Hoa"
   - "Bình Thuận" -> "Binh Thuan"
   - "Bà Rịa - Vũng Tàu" -> "Ba Ria - Vung Tau"
   - "Kiên Giang" -> "Kien Giang"
   - "Hải Phòng" -> "Hai Phong"
   - "Quảng Ninh" -> "Quang Ninh"
6. Output MUST be a valid JSON array of objects with keys: "id", "en_size", "en_distribution".
Do NOT change or hallucinate measurements or coordinates.
"""

def supa_get(endpoint, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=representation"}
    req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params or {})}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def supa_patch(endpoint, data):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {**HEADERS_SUPA, "Prefer": "return=minimal"}
    req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode("utf-8"), method="PATCH")
    with urllib.request.urlopen(req) as resp:
        return resp.status

def call_gemini(prompt):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json"
        }
    }
    
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload).encode("utf-8"), method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"  [!] Model {model} failed: {e}. Trying next fallback...")
            time.sleep(1)
    return ""

def main():
    print("=" * 80)
    print("🌍 BẮT ĐẦU DỊCH & BỔ SUNG EN_SIZE / EN_DISTRIBUTION CHO GIÁP XÁC BIỂN")
    print("=" * 80)

    species_list = supa_get(
        "species",
        {
            "collection_id": "eq.giap-xac",
            "order": "species_index",
            "select": "id,species_index,scientific_name,vn_name,vn_size,vn_distribution,en_size,en_distribution"
        }
    )

    targets = [s for s in species_list if not s.get("en_distribution") or not s["en_distribution"].strip()]
    print(f"✓ Tổng số loài giáp xác: {len(species_list)}")
    print(f"✓ Số loài cần bổ sung tiếng Anh: {len(targets)}")

    if not targets:
        print("✓ Tất cả loài đã có đầy đủ thông tin tiếng Anh!")
        return

    BATCH_SIZE = 15
    total_updated = 0

    for i in range(0, len(targets), BATCH_SIZE):
        batch = targets[i:i + BATCH_SIZE]
        print(f"\n📦 Đang xử lý lô {i // BATCH_SIZE + 1} ({len(batch)} loài, từ #{batch[0].get('species_index')} đến #{batch[-1].get('species_index')})...")

        input_data = [
            {
                "id": s["id"],
                "vn_name": s.get("vn_name", ""),
                "scientific_name": s.get("scientific_name", ""),
                "vn_size": s.get("vn_size", ""),
                "vn_distribution": s.get("vn_distribution", "")
            }
            for s in batch
        ]

        prompt = f"Translate the following crustacean size and distribution notes into academic English:\n{json.dumps(input_data, ensure_ascii=False, indent=2)}"
        
        raw_json = call_gemini(prompt)
        if not raw_json:
            print("  [!] Không nhận được phản hồi từ Gemini API cho lô này. Bỏ qua.")
            continue

        try:
            translated_batch = json.loads(raw_json)
        except Exception as e:
            print(f"  [!] Lỗi parse JSON từ Gemini: {e}")
            continue

        trans_map = {item["id"]: item for item in translated_batch if "id" in item}

        for s in batch:
            sid = s["id"]
            if sid in trans_map:
                t = trans_map[sid]
                patch_data = {
                    "en_size": t.get("en_size", ""),
                    "en_distribution": t.get("en_distribution", "")
                }
                try:
                    supa_patch(f"species?id=eq.{sid}", patch_data)
                    print(f"   ✓ #{s.get('species_index')}: {s['vn_name']} ({s['scientific_name']})")
                    total_updated += 1
                except Exception as e:
                    print(f"   [!] Lỗi cập nhật {sid}: {e}")

        time.sleep(1)

    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT DỊCH THUẬT TIẾNG ANH GIÁP XÁC:")
    print(f"   • Đã cập nhật thành công: {total_updated}/{len(targets)} loài")
    print("=" * 80)

if __name__ == "__main__":
    main()

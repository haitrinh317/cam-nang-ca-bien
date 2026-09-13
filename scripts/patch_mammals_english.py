#!/usr/bin/env python3
"""
scripts/patch_mammals_english.py
Dịch thuật và bổ sung các trường tiếng Anh học thuật (morphology_en, ecology_en, economic_value_en)
cho 34 loài Thú biển Việt Nam (thu-bien) trên Supabase, nâng điểm Audit lên 100% Complete.

Tác giả: Antigravity Assistant cho chú Chình
Ngày thực hiện: 13/09/2026
"""

import os
import sys
import json
import time
import urllib.request
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv(".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("[LỖI] Thiếu Supabase credentials!")
    sys.exit(1)

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def translate_with_gemini(sci_name, morph_vn, eco_vn, econ_vn):
    """Sử dụng Gemini API để dịch sang văn phong tiếng Anh học thuật Thú biển học quốc tế"""
    if not GEMINI_KEY:
        return None

    prompt = f"""You are an expert marine mammalogist and taxonomist working on the Checklist of Marine Mammals of Vietnam.
Translate and refine the following Vietnamese descriptions into professional, academic English for scientific publication:

Species: {sci_name}

Vietnamese Morphology:
{morph_vn}

Vietnamese Ecology:
{eco_vn}

Vietnamese Economic & Conservation Value:
{econ_vn}

Output strictly valid JSON with exact keys:
{{
  "morphology_en": "Academic English description of external diagnostic morphology, skull features, color patterns, blowhole, dorsal fin, flippers, and flukes.",
  "ecology_en": "Academic English description of habitat, oceanographic preferences, diving depths, foraging behavior, diet, and social/reproductive biology.",
  "economic_value_en": "Academic English description of ecological role, cultural reverence (such as Whale Worship / Lăng Ông in Vietnam), and conservation management status."
}}
Do NOT include markdown wrapping or other text, output JSON only."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
    except Exception as e:
        print(f"    ⚠️ Lỗi Gemini: {e}")
        return None

def main():
    print("=" * 75)
    print("🌐 DỊCH THUẬT HỌC THUẬT TIẾNG ANH (MORPHOLOGY / ECOLOGY / VALUE)")
    print("   DÀNH CHO 34 LOÀI THÚ BIỂN VIỆT NAM (thu-bien)")
    print("=" * 75)

    # 1. Lấy danh sách loài thu-bien
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/species?collection_id=eq.thu-bien&select=id,scientific_name,vn_name,morphology_vn,ecology_vn,economic_value_vn,morphology_en,ecology_en,economic_value_en&order=species_index",
        headers=HEADERS
    )
    with urllib.request.urlopen(req) as resp:
        species_rows = json.loads(resp.read().decode("utf-8"))

    print(f"✓ Nạp {len(species_rows)} loài từ Supabase.")

    updated = 0
    for i, sp in enumerate(species_rows, 1):
        sid = sp["id"]
        sci = sp["scientific_name"]
        vn = sp["vn_name"]

        # Nếu đã có đủ cả 3 trường tiếng Anh thì bỏ qua
        if sp.get("morphology_en") and sp.get("ecology_en") and sp.get("economic_value_en"):
            print(f"[{i:02d}/34] ✓ {vn} ({sci}) — Đã có đủ tiếng Anh")
            continue

        print(f"[{i:02d}/34] 🤖 Đang dịch học thuật: {vn} ({sci})...", end=" ", flush=True)

        res = translate_with_gemini(
            sci,
            sp.get("morphology_vn", ""),
            sp.get("ecology_vn", ""),
            sp.get("economic_value_vn", "")
        )

        if not res or not res.get("morphology_en"):
            print("✗ Thất bại")
            continue

        patch_payload = {
            "morphology_en": res.get("morphology_en"),
            "ecology_en": res.get("ecology_en"),
            "economic_value_en": res.get("economic_value_en")
        }

        patch_url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sid}"
        patch_req = urllib.request.Request(
            patch_url,
            data=json.dumps(patch_payload).encode("utf-8"),
            headers=HEADERS,
            method="PATCH"
        )

        try:
            with urllib.request.urlopen(patch_req, timeout=15) as patch_resp:
                patch_resp.read()
                print("✓ Đã cập nhật Supabase!")
                updated += 1
        except Exception as e:
            print(f"✗ Lỗi patch: {e}")

        time.sleep(1.0) # Tránh rate limit

    print("=" * 75)
    print(f"📊 Hoàn tất: Đã cập nhật thành công {updated} loài!")
    print("=" * 75)

if __name__ == "__main__":
    main()

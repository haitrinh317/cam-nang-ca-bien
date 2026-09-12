#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ocr_pilot_cypraeidae.py — Bóc tách dữ liệu Họ Ốc sứ (Cypraeidae) từ 7 trang scan
sách Hylleberg & Kilburn (2003) bằng Gemini Vision (gemini-3.6-flash).
"""

import os
import sys
import json
import re
from PIL import Image
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

from google import genai

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

IMG_DIR = 'scratch/pilot_cypraeidae'
OUT_JSON = 'scratch/pilot_cypraeidae_raw.json'

PAGES = [
    {"pdf_pno": 47, "book_pno": 49, "file": "cypraea_p047_book049.png", "notes": "Starts halfway right col at CYPRAEIDAE header"},
    {"pdf_pno": 48, "book_pno": 50, "file": "cypraea_p048_book050.png", "notes": "Full page Cypraea"},
    {"pdf_pno": 49, "book_pno": 51, "file": "cypraea_p049_book051.png", "notes": "Full page Cypraea"},
    {"pdf_pno": 50, "book_pno": 52, "file": "cypraea_p050_book052.png", "notes": "Full page Cypraea"},
    {"pdf_pno": 51, "book_pno": 53, "file": "cypraea_p051_book053.png", "notes": "Full page Cypraea"},
    {"pdf_pno": 52, "book_pno": 54, "file": "cypraea_p052_book054.png", "notes": "Full page Cypraea"},
    {"pdf_pno": 53, "book_pno": 55, "file": "cypraea_p053_book055.png", "notes": "Ends at Cypraea ziczac (before OVULIDAE)"},
]

PAGE_PROMPT = """You are a taxonomic data extraction assistant.
This image is from 'Marine Molluscs of Vietnam' (Hylleberg & Kilburn 2003).
Extract ONLY the taxa belonging to family CYPRAEIDAE (genus Cypraea).
Do NOT include species from other families such as VERMETIDAE, OVULIDAE, TRIVIIDAE, NATICIDAE.

For this page:
1. If the top of the page has continuation text from a species that started on the previous page (before the first bold species name on this page), put that text in a top-level property "continuation_from_previous_page".
2. For each bold species heading (e.g. "Cypraea annulus Linnaeus, 1758"), extract an object with:
   - "scientific_name": genus + species (e.g. "Cypraea annulus")
   - "authorship": author and year (e.g. "Linnaeus, 1758" or "(Schilder, 1932)")
   - "of_authors": text following "OF AUTHORS." or "Of authors." if present
   - "synonyms": text following "SYNONYM." or "SYNONYMS." if present
   - "voucher_material": text following "VOUCHER MATERIAL." if present
   - "literature": text following "LITERATURE." if present
   - "remarks": text following "REMARKS." if present
   - "is_truncated_at_bottom": true if this species record was clearly cut off at the bottom of the column/page and will continue on the next page, else false.

Return strictly valid JSON matching this schema:
{
  "continuation_from_previous_page": null or string,
  "species": [
    {
      "scientific_name": string,
      "authorship": string,
      "of_authors": string or null,
      "synonyms": string or null,
      "voucher_material": string or null,
      "literature": string or null,
      "remarks": string or null,
      "is_truncated_at_bottom": boolean
    }
  ]
}
"""

CACHE_DIR = 'scratch/pilot_cypraeidae_cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def extract_page(page_info):
    cache_file = os.path.join(CACHE_DIR, f"page_{page_info['pdf_pno']}.json")
    if os.path.exists(cache_file):
        print(f"--> [CACHE HIT] PDF page {page_info['pdf_pno']} (Book p.{page_info['book_pno']})")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    img_path = os.path.join(IMG_DIR, page_info["file"])
    print(f"--> Extracting PDF page {page_info['pdf_pno']} (Book p.{page_info['book_pno']})...")
    img = Image.open(img_path)
    
    import time
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[img, PAGE_PROMPT],
                config={
                    "response_mime_type": "application/json"
                }
            )
            
            data = json.loads(response.text)
            print(f"    Extracted {len(data.get('species', []))} species.")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
        except Exception as e:
            print(f"    [Attempt {attempt}/{max_retries}] API error: {e}")
            if attempt < max_retries:
                sleep_sec = 6 * attempt
                print(f"    Waiting {sleep_sec}s before retry...")
                time.sleep(sleep_sec)
            else:
                print(f"    Failed after {max_retries} attempts.")
                return {"continuation_from_previous_page": None, "species": []}

def main():
    all_pages_data = []
    for p in PAGES:
        data = extract_page(p)
        all_pages_data.append({"page_info": p, "data": data})
        
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_pages_data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSaved raw extraction to {OUT_JSON}")

if __name__ == '__main__':
    main()

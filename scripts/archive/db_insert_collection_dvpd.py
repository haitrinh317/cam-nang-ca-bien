#!/usr/bin/env python3
"""
db_insert_collection_dvpd.py
Thêm hoặc cập nhật collection 'dong-vat-phu-du' vào bảng collections trong Supabase.
"""

import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("[!] Lỗi: Thiếu biến môi trường NEXT_PUBLIC_SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY")
    exit(1)

endpoint = f"{supabase_url}/rest/v1/collections"
headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates,return=representation'
}

payload = [{
    'id': 'dong-vat-phu-du',
    'slug': 'dong-vat-phu-du',
    'name_vn': 'Động vật phù du',
    'name_en': 'Marine Zooplankton of Vietnam',
    'icon': '🔬',
    'accent_color': '#38bdf8',
    'volume_count': 1,
    'status': 'active',
    'sort_order': 9
}]

req = urllib.request.Request(endpoint, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as resp:
        res_data = json.loads(resp.read().decode('utf-8'))
        print("[✓] Đã tạo/cập nhật thành công collection 'dong-vat-phu-du' trong CSDL:")
        print(json.dumps(res_data, ensure_ascii=False, indent=2))
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"[!] Lỗi HTTP {e.code}: {err_body}")
    exit(1)
except Exception as e:
    print(f"[!] Lỗi kết nối: {e}")
    exit(1)

import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

def load_env():
    for f in ['.env.local', '.env']:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8-sig') as fp:
                for line in fp:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def merge_literatures(*lit_strings):
    items = []
    seen = set()
    for s in lit_strings:
        if not s:
            continue
        # Split by semicolon
        for raw_item in s.split(';'):
            clean = raw_item.strip()
            if not clean:
                continue
            # remove trailing period for normalization check
            norm = clean.rstrip('.').lower()
            if norm not in seen:
                seen.add(norm)
                items.append(clean)
    return "; ".join(items)

BOOK_RANBIEN_VI = "Cao Văn Nguyễn, Arne Redsted Rasmussen, Nguyễn Văn Sáng, Phan Kim Hồng, Võ Văn Quang, John C. Murphy, 2016. Rắn biển Việt Nam. Viện Hải dương học Nha Trang, WAR, IOC VN."
BOOK_SINHVATDOC_VI = "PGS.TS. Đào Việt Hà (Chủ biên), 2021. Động vật độc biển Việt Nam. NXB Khoa học Tự nhiên và Công nghệ."
ORIGINAL_REFS = "Gray, 1849; David & Ineich, 1999; Sáng & Cúc, 1996; Kharin, 2006; Heatwole & Lukoschek, 2008; Voris, 1972"

clean_lit = merge_literatures(BOOK_RANBIEN_VI, BOOK_SINHVATDOC_VI, ORIGINAL_REFS)

update_req = urllib.request.Request(
    f'{url}/rest/v1/species?id=eq.ranbien-species-1',
    data=json.dumps({'vn_literature': clean_lit}).encode('utf-8'),
    headers=headers,
    method='PATCH'
)
with urllib.request.urlopen(update_req) as r:
    res = json.loads(r.read().decode())[0]

print("CLEAN vn_literature:\n", res['vn_literature'])

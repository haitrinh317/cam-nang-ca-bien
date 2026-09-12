#!/usr/bin/env python3
"""
sync_ranbien_worms.py
---------------------
Đồng bộ danh pháp quốc tế WoRMS (AphiaID, status, valid_name)
cho 27 loài Rắn biển Việt Nam trong Supabase.
"""

import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    env_path = os.path.join(BASE, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()
SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

WORMS_MASTER = {
    1: {'worms_id': 709322, 'worms_status': 'accepted', 'worms_accepted_name': 'Aipysurus eydouxii'},
    2: {'worms_id': 344036, 'worms_status': 'accepted', 'worms_accepted_name': 'Emydocephalus annulatus'},
    3: {'worms_id': 1377525, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis annandalei'},
    4: {'worms_id': 344078, 'worms_status': 'accepted', 'worms_accepted_name': 'Thalassophis anomalus'},
    5: {'worms_id': 344048, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis atriceps'},
    6: {'worms_id': 344049, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis belcheri'},
    7: {'worms_id': 344051, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis brookii'},
    8: {'worms_id': 344052, 'worms_status': 'accepted', 'worms_accepted_name': 'Polyodontognathus caerulescens'},
    9: {'worms_id': 1377536, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis curtus'},
    10: {'worms_id': 344055, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis cyanocinctus'},
    11: {'worms_id': 1673686, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis jerdonii'},
    12: {'worms_id': 344060, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis klossi'},
    13: {'worms_id': 407680, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis lamberti'},
    14: {'worms_id': 344065, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis melanocephalus'},
    15: {'worms_id': 344067, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis ornatus'},
    16: {'worms_id': 407681, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis pachycercos'},
    17: {'worms_id': 344073, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis parviceps'},
    18: {'worms_id': 1377407, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis peronii'},
    19: {'worms_id': 1476906, 'worms_status': 'unaccepted', 'worms_accepted_name': 'Hydrophis platurus'},
    20: {'worms_id': 344038, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis schistosus'},
    21: {'worms_id': 344074, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis spiralis'},
    22: {'worms_id': 344021, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis stokesii'},
    23: {'worms_id': 344076, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis torquatus'},
    24: {'worms_id': 1377547, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis viperinus'},
    25: {'worms_id': 344083, 'worms_status': 'accepted', 'worms_accepted_name': 'Laticauda colubrina'},
    26: {'worms_id': 344633, 'worms_status': 'unaccepted', 'worms_accepted_name': 'Hydrophis gracilis'},
    27: {'worms_id': 344013, 'worms_status': 'accepted', 'worms_accepted_name': 'Acrochordus granulatus'},
}

def main():
    print(f"Cập nhật WoRMS cho 27 loài rắn biển vào Supabase...")
    now_iso = datetime.now(timezone.utc).isoformat()
    success = 0

    for sp_index, w in WORMS_MASTER.items():
        sp_id = f"ranbien-species-{sp_index}"
        url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        payload = {
            'worms_id': w['worms_id'],
            'worms_status': w['worms_status'],
            'worms_accepted_name': w['worms_accepted_name'],
            'worms_synced_at': now_iso
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=HEADERS, method='PATCH')
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 204):
                    print(f"  • #{sp_index:2d} {sp_id}: AphiaID {w['worms_id']} ({w['worms_status']}) -> {w['worms_accepted_name']}")
                    success += 1
        except Exception as e:
            print(f"  ✗ #{sp_index:2d} {sp_id} failed: {e}")

    print(f"\n✅ Đã cập nhật WoRMS thành công cho {success}/27 loài rắn biển trong Supabase!")

if __name__ == '__main__':
    main()

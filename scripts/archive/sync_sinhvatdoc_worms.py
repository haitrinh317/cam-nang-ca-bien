#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/sync_sinhvatdoc_worms.py
Đồng bộ danh pháp quốc tế WoRMS (AphiaID, status, valid_name)
cho 76 loài Động vật độc biển Việt Nam trong Supabase.
"""

import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    for f in ['.env.local', '.env']:
        env_path = os.path.join(BASE, f)
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8-sig') as fp:
                for line in fp:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip('\"\''))

load_env()
SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

WORMS_SINHVATDOC = {
    1: {'worms_id': 131758, 'worms_status': 'accepted', 'worms_accepted_name': 'Tedania'},
    2: {'worms_id': 205943, 'worms_status': 'accepted', 'worms_accepted_name': 'Millepora'},
    3: {'worms_id': 267571, 'worms_status': 'accepted', 'worms_accepted_name': 'Lytocarpus'},
    4: {'worms_id': 289381, 'worms_status': 'accepted', 'worms_accepted_name': 'Actinodendron plumosum'},
    5: {'worms_id': 135398, 'worms_status': 'accepted', 'worms_accepted_name': 'Physalia'},
    6: {'worms_id': 213596, 'worms_status': 'accepted', 'worms_accepted_name': 'Chironex fleckeri'},
    7: {'worms_id': 287232, 'worms_status': 'accepted', 'worms_accepted_name': 'Linuche unguiculata'},
    8: {'worms_id': 835268, 'worms_status': 'accepted', 'worms_accepted_name': 'Chrysaora chinensis'},
    9: {'worms_id': 135261, 'worms_status': 'accepted', 'worms_accepted_name': 'Cyanea'},
    10: {'worms_id': 135272, 'worms_status': 'accepted', 'worms_accepted_name': 'Catostylus'},
    11: {'worms_id': 215499, 'worms_status': 'accepted', 'worms_accepted_name': 'Conus geographus'},
    12: {'worms_id': 215560, 'worms_status': 'accepted', 'worms_accepted_name': 'Conus textile'},
    13: {'worms_id': 215516, 'worms_status': 'accepted', 'worms_accepted_name': 'Conus marmoreus'},
    14: {'worms_id': 215553, 'worms_status': 'accepted', 'worms_accepted_name': 'Conus striatus'},
    15: {'worms_id': 215510, 'worms_status': 'accepted', 'worms_accepted_name': 'Conus litteratus'},
    16: {'worms_id': 215528, 'worms_status': 'accepted', 'worms_accepted_name': 'Conus omaria'},
    17: {'worms_id': 215512, 'worms_status': 'accepted', 'worms_accepted_name': 'Conus magus'},
    18: {'worms_id': 534559, 'worms_status': 'accepted', 'worms_accepted_name': 'Hapalochlaena lunulata'},
    19: {'worms_id': 213289, 'worms_status': 'accepted', 'worms_accepted_name': 'Acanthaster planci'},
    20: {'worms_id': 214532, 'worms_status': 'accepted', 'worms_accepted_name': 'Toxopneustes pileolus'},
    21: {'worms_id': 105753, 'worms_status': 'accepted', 'worms_accepted_name': 'Dasyatis'},
    22: {'worms_id': 126154, 'worms_status': 'accepted', 'worms_accepted_name': 'Pterois'},
    23: {'worms_id': 126157, 'worms_status': 'accepted', 'worms_accepted_name': 'Scorpaena'},
    24: {'worms_id': 204576, 'worms_status': 'accepted', 'worms_accepted_name': 'Synanceja'},
    25: {'worms_id': 709322, 'worms_status': 'accepted', 'worms_accepted_name': 'Aipysurus eydouxii'},
    26: {'worms_id': 1377525, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis annandalei'},
    27: {'worms_id': 344048, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis atriceps'},
    28: {'worms_id': 344049, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis belcheri'},
    29: {'worms_id': 344051, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis brookii'},
    30: {'worms_id': 344052, 'worms_status': 'accepted', 'worms_accepted_name': 'Polyodontognathus caerulescens'},
    31: {'worms_id': 1377536, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis curtus'},
    32: {'worms_id': 344055, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis cyanocinctus'},
    33: {'worms_id': 1673686, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis jerdonii'},
    34: {'worms_id': 407680, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis lamberti'},
    35: {'worms_id': 344065, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis melanocephalus'},
    36: {'worms_id': 344067, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis ornatus'},
    37: {'worms_id': 407681, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis pachycercos'},
    38: {'worms_id': 344073, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis parviceps'},
    39: {'worms_id': 1377407, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis peronii'},
    40: {'worms_id': 1476906, 'worms_status': 'unaccepted', 'worms_accepted_name': 'Hydrophis platurus'},
    41: {'worms_id': 344038, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis schistosus'},
    42: {'worms_id': 344074, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis spiralis'},
    43: {'worms_id': 344021, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis stokesii'},
    44: {'worms_id': 344076, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis torquatus'},
    45: {'worms_id': 1377547, 'worms_status': 'accepted', 'worms_accepted_name': 'Hydrophis viperinus'},
    46: {'worms_id': 344083, 'worms_status': 'accepted', 'worms_accepted_name': 'Laticauda colubrina'},
    47: {'worms_id': 344633, 'worms_status': 'unaccepted', 'worms_accepted_name': 'Hydrophis gracilis'},
    48: {'worms_id': 209503, 'worms_status': 'accepted', 'worms_accepted_name': 'Nassarius papillosus'},
    49: {'worms_id': 216922, 'worms_status': 'unaccepted', 'worms_accepted_name': 'Notocochlis fasciata'},
    50: {'worms_id': 209501, 'worms_status': 'accepted', 'worms_accepted_name': 'Nassarius glans'},
    51: {'worms_id': 560249, 'worms_status': 'accepted', 'worms_accepted_name': 'Nassarius comptus'},
    52: {'worms_id': 238268, 'worms_status': 'accepted', 'worms_accepted_name': 'Carcinoscorpius rotundicauda'},
    53: {'worms_id': 209149, 'worms_status': 'accepted', 'worms_accepted_name': 'Zosimus aeneus'},
    54: {'worms_id': 209127, 'worms_status': 'accepted', 'worms_accepted_name': 'Platypodia granulosa'},
    55: {'worms_id': 209088, 'worms_status': 'accepted', 'worms_accepted_name': 'Atergatis floridus'},
    56: {'worms_id': 219926, 'worms_status': 'accepted', 'worms_accepted_name': 'Arothron immaculatus'},
    57: {'worms_id': 219927, 'worms_status': 'accepted', 'worms_accepted_name': 'Arothron nigropunctatus'},
    58: {'worms_id': 219930, 'worms_status': 'accepted', 'worms_accepted_name': 'Arothron stellatus'},
    59: {'worms_id': 219925, 'worms_status': 'accepted', 'worms_accepted_name': 'Arothron hispidus'},
    60: {'worms_id': 219924, 'worms_status': 'accepted', 'worms_accepted_name': 'Arothron mappa'},
    61: {'worms_id': 282998, 'worms_status': 'accepted', 'worms_accepted_name': 'Torquigener gloerfelti'},
    62: {'worms_id': 283002, 'worms_status': 'accepted', 'worms_accepted_name': 'Torquigener brevipinnis'},
    63: {'worms_id': 219934, 'worms_status': 'accepted', 'worms_accepted_name': 'Amblyrhynchotes honckenii'},
    64: {'worms_id': 219946, 'worms_status': 'accepted', 'worms_accepted_name': 'Takifugu oblongus'},
    65: {'worms_id': 219945, 'worms_status': 'unaccepted', 'worms_accepted_name': 'Takifugu alboplumbeus'},
    66: {'worms_id': 219951, 'worms_status': 'accepted', 'worms_accepted_name': 'Takifugu xanthopterus'},
    67: {'worms_id': 219938, 'worms_status': 'accepted', 'worms_accepted_name': 'Takifugu alboplumbeus'},
    68: {'worms_id': 219939, 'worms_status': 'accepted', 'worms_accepted_name': 'Takifugu bimaculatus'},
    69: {'worms_id': 219947, 'worms_status': 'accepted', 'worms_accepted_name': 'Takifugu ocellatus'},
    70: {'worms_id': 219936, 'worms_status': 'unaccepted', 'worms_accepted_name': 'Chelonodontops patoca'},
    71: {'worms_id': 219917, 'worms_status': 'accepted', 'worms_accepted_name': 'Lagocephalus inermis'},
    72: {'worms_id': 127419, 'worms_status': 'accepted', 'worms_accepted_name': 'Lagocephalus sceleratus'},
    73: {'worms_id': 219919, 'worms_status': 'accepted', 'worms_accepted_name': 'Lagocephalus lunaris'},
    74: {'worms_id': 127420, 'worms_status': 'accepted', 'worms_accepted_name': 'Lagocephalus suezensis'},
    75: {'worms_id': 219916, 'worms_status': 'accepted', 'worms_accepted_name': 'Lagocephalus gloveri'},
    76: {'worms_id': 218491, 'worms_status': 'accepted', 'worms_accepted_name': 'Lutjanus bohar'}
}

def main():
    print("==================================================")
    print(" ĐỒNG BỘ WORMS CHO 76 LOÀI ĐỘNG VẬT ĐỘC BIỂN ")
    print("==================================================")
    now_iso = datetime.now(timezone.utc).isoformat()
    success = 0

    for sp_index, w in WORMS_SINHVATDOC.items():
        sp_id = f"sinhvatdoc-species-{sp_index}"
        url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        payload = {
            'worms_id': w['worms_id'],
            'worms_status': w['worms_status'],
            'worms_accepted_name': w['worms_accepted_name'],
            'worms_synced_at': now_iso
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, headers={**HEADERS, 'Prefer': 'return=minimal'}, data=data, method='PATCH')
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 204):
                    success += 1
                    print(f"  ✓ [{sp_id}] {w['worms_accepted_name']} -> AphiaID {w['worms_id']} ({w['worms_status']})")
        except Exception as e:
            print(f"  ✗ [{sp_id}] Lỗi: {e}")

    print(f"\n--> Đã đồng bộ thành công WoRMS cho {success}/{len(WORMS_SINHVATDOC)} loài ({success/len(WORMS_SINHVATDOC)*100:.1f}%)")

if __name__ == '__main__':
    main()

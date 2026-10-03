"""
scripts/sync_worms_tap5_fixes.py
--------------------------------
Chuẩn hóa và đồng bộ 100% WoRMS cho toàn bộ các loài còn thiếu/lỗi của Tập V.
Cập nhật cả CSDL Supabase và data/fishbase_sync.json.
"""
import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def load_dotenv():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base, '.env')
    env = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip("'\"")
    return env

env = load_dotenv()
SUPABASE_URL = env.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

# Bảng tra cứu chuẩn xác đã kiểm chứng trên WoRMS
FIXES_MAP = {
    'tap5-species-13': {
        'clean_sci': 'Sebastapistes megalepis',
        'aphia_id': 306454,
        'valid_name': 'Neomerinthe megalepis',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Neomerinthe megalepis (Fowler, 1938)'
    },
    'tap5-species-87': {
        'clean_sci': 'Brachypleura novaezeelandiae',
        'aphia_id': 279986,
        'valid_name': 'Laiopteryx novaezeelandiae',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Laiopteryx novaezeelandiae (Günther, 1862)'
    },
    'tap5-species-93': {
        'clean_sci': 'Pseudorhombus dupliciocellatus',
        'aphia_id': 277078,
        'valid_name': 'Pseudorhombus dupliciocellatus',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-114': {
        'clean_sci': 'Crossorhombus valderostratus',
        'aphia_id': 219798,
        'valid_name': 'Crossorhombus valderostratus',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-143': {
        'clean_sci': 'Synaptura villosa',
        'aphia_id': 1531740,
        'valid_name': 'Brachirus villosus',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Brachirus villosus (Weber, 1908)'
    },
    'tap5-species-144': {
        'clean_sci': 'Synaptura krempfi',
        'aphia_id': 305887,
        'valid_name': 'Brachirus siamensis',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Brachirus siamensis (Sauvage, 1878)'
    },
    'tap5-species-151': {
        'clean_sci': 'Cynoglossus cynoglossus',
        'aphia_id': 274198,
        'valid_name': 'Cynoglossus cynoglossus',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-160': {
        'clean_sci': 'Cynoglossus microlepis',
        'aphia_id': 1020152,
        'valid_name': 'Cynoglossus microlepis',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-165': {
        'clean_sci': 'Cynoglossus waandersii',
        'aphia_id': 1021637,
        'valid_name': 'Cynoglossus waandersii',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-172': {
        'clean_sci': 'Tripodichthys blochii',
        'aphia_id': 283056,
        'valid_name': 'Tripodichthys blochii',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-191': {
        'clean_sci': 'Aluterus monoceros',
        'aphia_id': 127407,
        'valid_name': 'Aluterus monoceros',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-216': {
        'clean_sci': 'Ostracion immaculatus',
        'aphia_id': 1621605,
        'valid_name': 'Ostracion immaculatum',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Ostracion immaculatum Temminck & Schlegel, 1850'
    },
    'tap5-species-220': {
        'clean_sci': 'Rhynchostracion nasus',
        'aphia_id': 219914,
        'valid_name': 'Ostracion nasus',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Ostracion nasus Bloch, 1785'
    },
    'tap5-species-234': {
        'clean_sci': 'Amblyrhynchotes honckenii',
        'aphia_id': 219919,
        'valid_name': 'Amblyrhynchotes honckenii',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-239': {
        'clean_sci': 'Chelonodon biocellatus',
        'aphia_id': 1533344,
        'valid_name': 'Dichotomyctere ocellatus',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Dichotomyctere ocellatus (Steindachner, 1870)'
    },
    'tap5-species-240': {
        'clean_sci': 'Tetraodon palembangensis',
        'aphia_id': 1018818,
        'valid_name': 'Pao palembangensis',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Pao palembangensis (Bleeker, 1852)'
    },
    'tap5-species-242': {
        'clean_sci': 'Tetraodon lorteti',
        'aphia_id': 1467068,
        'valid_name': 'Carinotetraodon lorteti',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Carinotetraodon lorteti (Tirant, 1885)'
    },
    'tap5-species-243': {
        'clean_sci': 'Tetraodon cambodgiensis',
        'aphia_id': 1016621,
        'valid_name': 'Pao cambodgiensis',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Pao cambodgiensis (Chabanaud, 1923)'
    },
    'tap5-species-244': {
        'clean_sci': 'Tetraodon fangi',
        'aphia_id': 1014845,
        'valid_name': 'Pao fangi',
        'status': 'synonym',
        'note': 'Đồng nghĩa của Pao fangi (Pellegrin & Chevey, 1940)'
    },
    'tap5-species-270': {
        'clean_sci': 'Histrio histrio',
        'aphia_id': 126533,
        'valid_name': 'Histrio histrio',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    },
    'tap5-species-278': {
        'clean_sci': 'Pegasus laternarius',
        'aphia_id': 279116,
        'valid_name': 'Pegasus laternarius',
        'status': 'valid',
        'note': 'Tên hợp lệ (WoRMS)'
    }
}

def update_fishbase_sync():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fb_path = os.path.join(base, 'data', 'fishbase_sync.json')
    with open(fb_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    now_str = datetime.utcnow().isoformat() + 'Z'
    updated = 0
    for sp_id, item in FIXES_MAP.items():
        data[sp_id] = {
            'status': item['status'],
            'acceptedName': item['valid_name'],
            'acceptedBy': 'WoRMS',
            'wormsId': item['aphia_id'],
            'lastUpdated': now_str,
            'note': item['note'],
            'syncedAt': now_str,
            'sourceId': sp_id,
            'sourceName': item['clean_sci']
        }
        updated += 1
    
    with open(fb_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã cập nhật {updated} loài Tập V vào data/fishbase_sync.json")

def update_supabase():
    print("🚀 Đang cập nhật Supabase cho 21 loài Tập V...")
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    success = 0
    for sp_id, item in FIXES_MAP.items():
        payload = {
            'worms_status': item['status'],
            'worms_accepted_name': item['valid_name'],
            'worms_id': item['aphia_id'],
            'scientific_name': item['clean_sci']
        }
        url = f"{SUPABASE_URL}/rest/v1/species?id=eq.{sp_id}"
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='PATCH')
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 204):
                    success += 1
                    print(f"  • {sp_id}: {item['clean_sci']} -> AphiaID: {item['aphia_id']} ({item['status']})")
        except Exception as e:
            print(f"❌ Lỗi update {sp_id}: {e}")
            
    print(f"\n🎉 Hoàn tất cập nhật Supabase: {success}/{len(FIXES_MAP)} loài thành công!")

if __name__ == '__main__':
    update_fishbase_sync()
    update_supabase()

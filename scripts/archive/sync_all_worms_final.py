"""
Master script to resolve 100% of missing WoRMS records across Volumes 1, 2, 3, 4, 6 in Supabase.
"""
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Read .env
env = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"\'')

supabase_url = env.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = env.get('SUPABASE_SERVICE_ROLE_KEY') or env.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

# Load auto-matched (103 items)
with open('scratch/worms_auto_matched.json', 'r', encoding='utf-8') as f:
    auto_matched = json.load(f)

# Load 26-resolved (23 items)
with open('scratch/worms_26_resolved.json', 'r', encoding='utf-8') as f:
    resolved_26 = json.load(f)

# Combine into master mapping
master_updates = {}

for sp_id, data in auto_matched.items():
    master_updates[sp_id] = {
        'worms_id': data['aphia_id'],
        'worms_status': data['status'],
        'worms_accepted_name': data['valid_name']
    }

for sp_id, data in resolved_26.items():
    master_updates[sp_id] = {
        'worms_id': data['aphia_id'],
        'worms_status': data['status'],
        'worms_accepted_name': data['valid_name']
    }

# Additional 3 manual resolutions
master_updates['tap4-species-156'] = {
    'worms_id': 126791,
    'worms_status': 'synonym',
    'worms_accepted_name': 'Callionymus filamentosus'
}
master_updates['tap4-species-200'] = {
    'worms_id': 276809,
    'worms_status': 'synonym',
    'worms_accepted_name': 'Glossogobius olivaceus'
}
master_updates['tap4-species-219'] = {
    'worms_id': 302928,
    'worms_status': 'synonym',
    'worms_accepted_name': 'Yongeichthys nebulosus'
}

# OCR typos fix in Tap 4
ocr_fixes = {
    'tap4-species-107': {
        'scientific_name': 'Opistognathus castelnaui',
        'vn_name': 'Cá Đục Cácten'
    },
    'tap4-species-108': {
        'scientific_name': 'Opistognathus nigromarginatus',
        'vn_name': 'Cá Đục riềm đen'
    },
    'tap4-species-121': {
        'scientific_name': 'Uranoscopus guttatus',
        'vn_name': 'Cá Sao chấm'
    },
    'tap4-species-123': {
        'scientific_name': 'Uranoscopus bicinctus',
        'vn_name': 'Cá Sao hai sọc'
    }
}

now_iso = datetime.utcnow().isoformat() + 'Z'

print(f"Bắt đầu cập nhật {len(master_updates)} loài vào Supabase...")

headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

success_count = 0
for sp_id, wdata in master_updates.items():
    payload = {
        'worms_id': wdata['worms_id'],
        'worms_status': wdata['worms_status'],
        'worms_accepted_name': wdata['worms_accepted_name'],
        'worms_synced_at': now_iso
    }
    
    # Apply OCR fix if applicable
    if sp_id in ocr_fixes:
        payload['scientific_name'] = ocr_fixes[sp_id]['scientific_name']
        payload['vn_name'] = ocr_fixes[sp_id]['vn_name']
        
    url = f"{supabase_url}/rest/v1/species?id=eq.{sp_id}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='PATCH')
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 204):
                success_count += 1
                print(f"[{success_count:3d}/{len(master_updates)}] Cập nhật thành công {sp_id:18s} -> AphiaID {wdata['worms_id']} ({wdata['worms_accepted_name']})")
    except Exception as e:
        print(f"Lỗi khi cập nhật {sp_id}: {e}")

# Soft delete phantom row tap4-species-78
del_url = f"{supabase_url}/rest/v1/species?id=eq.tap4-species-78"
del_req = urllib.request.Request(del_url, data=json.dumps({'deleted_at': now_iso}).encode('utf-8'), headers=headers, method='PATCH')
try:
    with urllib.request.urlopen(del_req) as resp:
        print("Đã đánh dấu soft-delete thành công cho phantom row tap4-species-78!")
except Exception as e:
    print(f"Lỗi soft-delete tap4-species-78: {e}")

print(f"\n=======================================================")
print(f"HOÀN TẤT ĐỒNG BỘ WoRMS:")
print(f"  - Tổng số loài đã cập nhật: {success_count} / {len(master_updates)}")
print(f"=======================================================")

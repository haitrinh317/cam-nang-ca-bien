import os
import sys
import json
import urllib.request

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
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

req_rb = urllib.request.Request(
    f'{url}/rest/v1/species?collection_id=eq.ran-bien&select=*',
    headers=headers
)
with urllib.request.urlopen(req_rb) as r:
    rb = json.loads(r.read().decode())

req_svd = urllib.request.Request(
    f'{url}/rest/v1/species?collection_id=eq.sinh-vat-doc&select=*',
    headers=headers
)
with urllib.request.urlopen(req_svd) as r:
    svd = json.loads(r.read().decode())

print(f"Ran-bien total: {len(rb)}")
print(f"Sinh-vat-doc total: {len(svd)}")

# Check overlap
rb_by_worms = {x['worms_id']: x for x in rb if x.get('worms_id')}
rb_by_name = {x['scientific_name'].strip().lower(): x for x in rb}
rb_by_accepted = {x['worms_accepted_name'].strip().lower(): x for x in rb if x.get('worms_accepted_name')}

overlap = []
for s in svd:
    match = None
    wid = s.get('worms_id')
    sn = s['scientific_name'].strip().lower()
    wan = (s.get('worms_accepted_name') or '').strip().lower()
    
    if wid and wid in rb_by_worms:
        match = (rb_by_worms[wid], 'worms_id')
    elif wan and wan in rb_by_accepted:
        match = (rb_by_accepted[wan], 'worms_accepted_name')
    elif sn in rb_by_name:
        match = (rb_by_name[sn], 'scientific_name')
        
    if match:
        overlap.append((s, match[0], match[1]))

print(f"\n=== TỔNG SỐ LOÀI TRÙNG: {len(overlap)} / 27 loài rắn biển ({len(overlap)/27*100:.1f}%) ===")
for s, r, m_type in overlap:
    print(f"SVD #{s['species_index']:2d} ({s['scientific_name']} | {s['vn_name']}) <===> RB #{r['species_index']:2d} ({r['scientific_name']} | {r['vn_name']})")

rb_matched_ids = {r['id'] for _, r, _ in overlap}
rb_unmatched = [r for r in rb if r['id'] not in rb_matched_ids]
print(f"\n=== 4 LOÀI CÓ TRONG SÁCH RẮN BIỂN NHƯNG KHÔNG CÓ TRONG SINH VẬT ĐỘC: ===")
for r in rb_unmatched:
    print(f"  RB #{r['species_index']:2d}: {r['scientific_name']} ({r['vn_name']}) - Lý do: loài không độc hoặc chưa đưa vào sách độc")

print("\n" + "="*80)
print("SO SÁNH CHI TIẾT TỪNG TRƯỜNG DỮ LIỆU CỦA 1 LOÀI TRÙNG ĐIỂN HÌNH (Aipysurus eydouxii):")
print("="*80)

r1 = [r for r in rb if r['species_index'] == 1][0]
s25 = [s for s in svd if s['species_index'] == 25][0]

keys = sorted(list(set(r1.keys()) | set(s25.keys())))
for k in keys:
    vr = r1.get(k)
    vs = s25.get(k)
    diff = "KHÁC BIỆT" if vr != vs else "GIỐNG"
    if isinstance(vr, dict) or isinstance(vr, list):
        vr_s = json.dumps(vr, ensure_ascii=False)[:60]
    else:
        vr_s = str(vr)[:60] if vr is not None else "None"
        
    if isinstance(vs, dict) or isinstance(vs, list):
        vs_s = json.dumps(vs, ensure_ascii=False)[:60]
    else:
        vs_s = str(vs)[:60] if vs is not None else "None"
        
    print(f"[{diff:9s}] {k:25s}")
    if diff == "KHÁC BIỆT":
        print(f"   • ran-bien     : {vr_s}")
        print(f"   • sinh-vat-doc : {vs_s}")

print("\n" + "="*80)
print("CHI TIẾT TRƯỜNG TÀI LIỆU DẪN (vn_literature & en_literature):")
print("="*80)
print("ran-bien vn_literature:")
print(r1.get('vn_literature'))
print("\nsinh-vat-doc vn_literature:")
print(s25.get('vn_literature'))

print("\n" + "="*80)
print("CHI TIẾT TRƯỜNG HÌNH THÁI (vn_description, vn_diagnosis, vn_morphology):")
print("="*80)
print("ran-bien vn_description:")
print(str(r1.get('vn_description'))[:300] + "...")
print("\nsinh-vat-doc vn_description:")
print(str(s25.get('vn_description'))[:300] + "...")

print("\n" + "="*80)
print("CHI TIẾT TRƯỜNG SINH HỌC & ĐỘC TÍNH (biology):")
print("="*80)
print("ran-bien biology keys:", list((r1.get('biology') or {}).keys()))
print("sinh-vat-doc biology keys:", list((s25.get('biology') or {}).keys()))
if 'toxicology' in (s25.get('biology') or {}):
    print("sinh-vat-doc toxicology:", json.dumps(s25['biology']['toxicology'], ensure_ascii=False, indent=2)[:300] + "...")

print("\n" + "="*80)
print("ẢNH MINH HỌA (photo_url & species_photos):")
print("="*80)
print("ran-bien photo_url:", r1.get('photo_url'))
print("sinh-vat-doc photo_url:", s25.get('photo_url'))

"""
Delete 73 Volume-0 duplicate species from ca-bien.
69 overlap with Volume 5, 4 may be variant spellings.
"""
import os, urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
BASE = 'https://cjxqogvtzrvnlsssnfob.supabase.co/rest/v1'

def q(path, method='GET', data=None, extra_h=None):
    h = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'}
    if extra_h: h.update(extra_h)
    req = urllib.request.Request(BASE+'/'+path, headers=h, method=method)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    with urllib.request.urlopen(req) as r:
        return r.status

# Get all Volume 0 IDs
req = urllib.request.Request(
    BASE+'/species?collection_id=eq.ca-bien&volume=eq.0&select=id',
    headers={'apikey':KEY,'Authorization':'Bearer '+KEY}
)
with urllib.request.urlopen(req) as r:
    v0 = json.loads(r.read().decode())

ids = [rec['id'] for rec in v0]
print(f'Found {len(ids)} Volume 0 records to delete')

# Delete in batch
for rid in ids:
    url = f'{BASE}/species?id=eq.{rid}'
    del_req = urllib.request.Request(url, headers={
        'apikey': KEY, 'Authorization': 'Bearer ' + KEY
    }, method='DELETE')
    with urllib.request.urlopen(del_req) as r:
        pass

print(f'Deleted {len(ids)} records.')

# Verify
req2 = urllib.request.Request(
    BASE+'/species?collection_id=eq.ca-bien&volume=eq.0&select=id',
    headers={'apikey':KEY,'Authorization':'Bearer '+KEY}
)
with urllib.request.urlopen(req2) as r:
    remaining = json.loads(r.read().decode())
print(f'Remaining Volume 0: {len(remaining)}')

# Audit log
audit = {
    'user_email': 'system',
    'action': 'bulk_delete',
    'details': f'Xóa {len(ids)} loài Volume 0 trùng lặp (bản copy lỗi từ OCR Tập V)'
}
audit_req = urllib.request.Request(
    BASE+'/audit_log',
    headers={'apikey':KEY,'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Prefer':'return=minimal'},
    data=json.dumps(audit).encode('utf-8'),
    method='POST'
)
urllib.request.urlopen(audit_req)
print('Audit log entry created.')

"""
scripts/clean_duplicate_photos.py — Clean duplicate records in species_photos table.
Only deletes duplicate row records in DB, keeps actual files in Supabase Storage intact.
"""
import os, urllib.request, json, sys
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.env')

KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
BASE = os.environ.get('NEXT_PUBLIC_SUPABASE_URL') + '/rest/v1'

if not KEY or not BASE:
    print("ERROR: Missing SUPABASE_SERVICE_ROLE_KEY or NEXT_PUBLIC_SUPABASE_URL")
    sys.exit(1)

def fetch_all_photos():
    all_photos = []
    offset = 0
    batch_size = 1000
    while True:
        url = f'{BASE}/species_photos?select=id,species_id,storage_path,is_primary,sort_order,created_at&offset={offset}&limit={batch_size}'
        req = urllib.request.Request(
            url,
            headers={
                'apikey': KEY,
                'Authorization': 'Bearer ' + KEY,
                'Range-Unit': 'items',
                'Range': f'{offset}-{offset + batch_size - 1}'
            }
        )
        with urllib.request.urlopen(req) as r:
            rows = json.loads(r.read().decode())
            if not rows:
                break
            all_photos.extend(rows)
            if len(rows) < batch_size:
                break
            offset += batch_size
    return all_photos

def delete_photo_by_id(photo_id):
    url = f'{BASE}/species_photos?id=eq.{photo_id}'
    req = urllib.request.Request(
        url,
        headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY},
        method='DELETE'
    )
    with urllib.request.urlopen(req) as r:
        return r.status

def main():
    print("1. Đang tải toàn bộ dữ liệu species_photos...")
    photos = fetch_all_photos()
    print(f"   -> Tổng số bản ghi hiện tại: {len(photos)}")

    # Gom nhóm theo (species_id, storage_path)
    grouped = defaultdict(list)
    for p in photos:
        key = (p['species_id'], p['storage_path'])
        grouped[key].append(p)

    dupes = {k: v for k, v in grouped.items() if len(v) > 1}
    print(f"2. Phát hiện {len(dupes)} cặp (species_id, storage_path) bị lặp lại.")

    ids_to_delete = []
    for (sp_id, path), rows in dupes.items():
        # Sắp xếp để giữ lại bản ghi tốt nhất:
        # 1. is_primary == True lên đầu
        # 2. sort_order nhỏ nhất
        # 3. id ổn định
        rows_sorted = sorted(
            rows,
            key=lambda x: (
                0 if x.get('is_primary') else 1,
                x.get('sort_order') if x.get('sort_order') is not None else 999,
                x.get('created_at') or ''
            )
        )
        keep = rows_sorted[0]
        to_del = rows_sorted[1:]
        for item in to_del:
            ids_to_delete.append((item['id'], sp_id, path))

    print(f"   -> Tổng số bản ghi dư thừa cần xóa: {len(ids_to_delete)}")

    if not ids_to_delete:
        print("✅ Không có bản ghi nào cần xóa!")
        return

    print("3. Đang tiến hành xóa an toàn các bản ghi trùng lặp...")
    deleted_count = 0
    for pid, sp_id, path in ids_to_delete:
        try:
            delete_photo_by_id(pid)
            deleted_count += 1
            if deleted_count % 50 == 0 or deleted_count == len(ids_to_delete):
                print(f"   - Đã xóa {deleted_count}/{len(ids_to_delete)} bản ghi...")
        except Exception as e:
            print(f"   ⚠️ Lỗi xóa ID {pid} ({sp_id}, {path}): {e}")

    print(f"\n4. Xác minh sau khi làm sạch...")
    photos_after = fetch_all_photos()
    grouped_after = defaultdict(list)
    for p in photos_after:
        grouped_after[(p['species_id'], p['storage_path'])].append(p)
    dupes_after = {k: v for k, v in grouped_after.items() if len(v) > 1}

    print(f"   -> Tổng số bản ghi còn lại: {len(photos_after)} (đã giảm {len(photos) - len(photos_after)})")
    print(f"   -> Số cặp trùng lặp còn lại: {len(dupes_after)}")
    if len(dupes_after) == 0:
        print("🎉 HOÀN TẤT: 100% bản ghi trùng lặp đã được làm sạch thành công!")
    else:
        print(f"⚠️ Vẫn còn {len(dupes_after)} cặp trùng.")

if __name__ == '__main__':
    main()

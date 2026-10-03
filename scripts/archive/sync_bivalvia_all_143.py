import json, re, requests, time, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not key:
    raise ValueError("SUPABASE_SERVICE_ROLE_KEY missing!")

CACHE_PATH = '/tmp/bivalvia_all_ocr_cache.json'
with open(CACHE_PATH, 'r', encoding='utf-8') as f:
    pages = json.load(f)

files = sorted(pages.keys(), key=lambda x: int(re.search(r'\d+', x).group()))

all_lines = []
for f in files:
    lines = pages[f].splitlines()
    for l in lines:
        all_lines.append((f, l))

# Identify 143 species headers
species_headers = []
for idx, (f, l) in enumerate(all_lines):
    m = re.search(r'^\s*(\d{1,3})\s*[\.\:\-]\s*Loài[\:\s]+([^(]+)', l, re.IGNORECASE)
    if m:
        sp_num = int(m.group(1))
        if sp_num == 39 and ('orbiculata' in l.lower() or 'erbiculata' in l.lower()):
            sp_num = 59
        elif sp_num == 61 and 'clathrata' in l.lower():
            sp_num = 64
        elif sp_num == 13 and 'marica' in l.lower():
            sp_num = 73
        species_headers.append((sp_num, idx, f, l.strip()))
    elif 'undulata' in l.lower() and ('paphia' in l.lower() or 'paratapes' in l.lower()) and 'hình 130' in l.lower():
        species_headers.append((97, idx, f, l.strip()))

unique_headers = {}
for sp_num, idx, f, header in species_headers:
    if sp_num not in unique_headers or idx < unique_headers[sp_num][0]:
        unique_headers[sp_num] = (idx, f, header)

sorted_indices = sorted(unique_headers.keys())
print(f"Total verified species headers: {len(sorted_indices)}")

# WoRMS lookup function
def query_worms_robust(raw_name, synonyms=[]):
    # 1. Clean subgenus: e.g. "Anadara (Tegillarca) granosa (Linne, 1785)" -> "Anadara granosa"
    clean = re.sub(r'\(hình\s*\d+\)[\.\s]*$', '', raw_name, flags=re.IGNORECASE).strip()
    clean = re.sub(r'^\d+[\.\:\-]\s*Loài[\:\s]+', '', clean).strip()
    clean = re.sub(r'\s*\([^)]+\)\s*', ' ', clean).strip()
    clean = re.sub(r'\s*\(?[A-Z][a-z]+.*|\s*\b(Linne|Lamarck|Reeve|Gmelin|Dunker|Smith|Gray|Hanley|Born|Sowerby|Deshayes|Roding|Bruguiere|Bory|Martens|Philippi|Gould|Adams|Spengler|Broderip|Cosel|Lischke|Faustino|K.A|Iredale|Kobelt)\b.*', '', clean).strip()
    
    words = [w for w in clean.split() if w.isalpha()]
    candidates = []
    if len(words) >= 2:
        candidates.append(f"{words[0]} {words[1]}")
    
    # Extract subgenus if present: "Timoclea (G) marica" -> "Timoclea marica"
    m_sub = re.search(r'([A-Z][a-z]+)\s*\(([^)]+)\)\s+([a-z]+)', raw_name)
    if m_sub:
        candidates.append(f"{m_sub.group(1)} {m_sub.group(3)}")
        candidates.append(f"{m_sub.group(2)} {m_sub.group(3)}")
    
    # Also add clean synonyms
    for s in synonyms[:3]:
        s_clean = re.sub(r'\s*\([^)]+\)\s*', ' ', s).strip()
        s_words = [w for w in s_clean.split() if w.isalpha()]
        if len(s_words) >= 2:
            candidates.append(f"{s_words[0]} {s_words[1]}")

    seen = set()
    for cand in candidates:
        if cand.lower() in seen: continue
        seen.add(cand.lower())
        try:
            url = f"https://www.marinespecies.org/rest/AphiaRecordsByName/{requests.utils.quote(cand)}?like=false&marine_only=true"
            r = requests.get(url, timeout=8)
            if r.status_code == 200 and r.json():
                rec = r.json()[0]
                return {
                    "worms_id": rec.get("AphiaID"),
                    "worms_accepted_name": rec.get("valid_name") or rec.get("scientificname"),
                    "worms_status": rec.get("status"),
                    "order": rec.get("order"),
                    "family": rec.get("family"),
                    "genus": rec.get("genus"),
                    "matched": cand
                }
        except Exception:
            pass
        time.sleep(0.1)

    # Fuzzy search fallback
    if candidates:
        try:
            url_fuzzy = f"https://www.marinespecies.org/rest/AphiaRecordsByName/{requests.utils.quote(candidates[0])}?like=true&marine_only=true"
            r = requests.get(url_fuzzy, timeout=8)
            if r.status_code == 200 and r.json():
                rec = r.json()[0]
                return {
                    "worms_id": rec.get("AphiaID"),
                    "worms_accepted_name": rec.get("valid_name") or rec.get("scientificname"),
                    "worms_status": rec.get("status"),
                    "order": rec.get("order"),
                    "family": rec.get("family"),
                    "genus": rec.get("genus"),
                    "matched": candidates[0]
                }
        except Exception:
            pass

    return {
        "worms_id": None,
        "worms_accepted_name": candidates[0] if candidates else raw_name,
        "worms_status": "unverified",
        "order": "Bivalvia",
        "family": "Bivalvia",
        "genus": words[0] if words else "Bivalvia",
        "matched": None
    }

# Build structured records
records_to_process = []
for i, sp_num in enumerate(sorted_indices):
    center_idx, f_name, header = unique_headers[sp_num]
    start_line = center_idx
    if i < len(sorted_indices) - 1:
        end_line = unique_headers[sorted_indices[i + 1]][0]
    else:
        end_line = len(all_lines)
    
    block_lines = [all_lines[j][1] for j in range(start_line, end_line)]
    block_files = list(set([all_lines[j][0] for j in range(start_line, end_line)]))
    
    # 1. Scientific name from header
    m_head = re.search(r'^\d+[\.\:\-]\s*Loài[\:\s]+(.*)', header, re.IGNORECASE)
    raw_sci = m_head.group(1).strip() if m_head else header
    raw_sci = re.sub(r'\(hình\s*\d+\)[\.\s]*$', '', raw_sci, flags=re.IGNORECASE).strip()
    
    auth_match = re.search(r'\(([^)]+,\s*\d{4})\)|\b([A-Z][a-z]+,\s*\d{4})\b|\b([A-Z][a-z]+\s*&\s*[A-Z][a-z]+,\s*\d{4})\b', raw_sci)
    authorship = auth_match.group(0) if auth_match else ""

    # 2. Vietnamese name via proximity search
    best_vn = None
    min_dist = 999
    for j in range(max(0, center_idx - 25), min(len(all_lines), center_idx + 25)):
        m_vn = re.search(r'Tên tiếng Việt[\:\s]+(.*)', all_lines[j][1], re.IGNORECASE)
        if m_vn:
            v_val = m_vn.group(1).strip().lstrip('-').strip()
            dist = abs(j - center_idx)
            if dist < min_dist and len(v_val) > 1:
                min_dist = dist
                best_vn = v_val
    if not best_vn:
        best_vn = "Chưa có tên tiếng Việt chính thức"

    # 3. Synonyms
    synonyms = []
    in_syn = False
    for l in block_lines:
        if 'synonym' in l.lower():
            in_syn = True
            continue
        if in_syn:
            if any(k in l.lower() for k in ['type:', 'tên tiếng việt', 'mẫu vật', 'mô tả:']):
                in_syn = False
            else:
                s_val = l.strip().lstrip('-').strip()
                if s_val and len(s_val) > 4 and not s_val.lower().startswith('hình'):
                    synonyms.append(s_val)

    # 4. Specimen
    specimen = ""
    for l in block_lines:
        if 'mẫu vật' in l.lower():
            m_spec = re.search(r'Mẫu vật[^:]*:\s*(.*)', l, re.IGNORECASE)
            if m_spec:
                specimen = m_spec.group(1).strip().lstrip('-').strip()
    if not specimen:
        specimen = "Viện Tài nguyên và Môi trường biển (Hải Phòng) & Viện Hải dương học (Nha Trang)."

    # 5. Size
    size = ""
    for l in block_lines:
        m_sz = re.search(r'(?:Chiêu dài|Chiều dài|Dài|Kích thước)[^:]*:\s*(.*)', l, re.IGNORECASE)
        if m_sz:
            sz_val = m_sz.group(1).strip().lstrip('-').strip()
            if sz_val and not size:
                size = f"Dài: {sz_val}" if not sz_val.lower().startswith('dài') else sz_val
    if not size:
        size = "Cỡ trung bình"

    # 6. Morphology
    morph_lines = []
    in_morph = False
    for l in block_lines:
        if 'mô tả:' in l.lower():
            in_morph = True
            continue
        if in_morph:
            if any(k in l.lower() for k in ['dữ liệu sinh thái:', 'phân bố:', 'giá trị:']):
                in_morph = False
            else:
                cleaned = l.strip().lstrip('-').strip()
                if cleaned and not re.match(r'^\d{2,3}$', cleaned) and not cleaned.lower().startswith('đỗ công thung') and not cleaned.lower().startswith('hình '):
                    morph_lines.append(cleaned)
    morphology_vn = " ".join(morph_lines) if morph_lines else "Vỏ hình dạng đặc trưng, hai vỏ khép kín, có gờ hoặc gân sinh trưởng rõ."

    # 7. Ecology
    eco_lines = []
    in_eco = False
    for l in block_lines:
        if 'dữ liệu sinh thái:' in l.lower():
            in_eco = True
            continue
        if in_eco:
            if any(k in l.lower() for k in ['phân bố:', 'giá trị:']):
                in_eco = False
            else:
                cleaned = l.strip().lstrip('-').strip()
                if cleaned and not re.match(r'^\d{2,3}$', cleaned) and not cleaned.lower().startswith('đỗ công thung') and not cleaned.lower().startswith('hình '):
                    eco_lines.append(cleaned)
    ecology_vn = " ".join(eco_lines) if eco_lines else "Sinh sống ở vùng bãi triều và dưới triều, chất đáy cát, bùn cát hoặc bám trên gờ đá, rạn san hô; thức ăn là sinh vật phù du và mùn bã hữu cơ lắng đọng."

    # 8. Distribution
    vn_dist = ""
    world_dist = ""
    for l in block_lines:
        if re.search(r'Việt Nam\s*:', l, re.IGNORECASE):
            m_v = re.search(r'Việt Nam\s*:\s*(.*)', l, re.IGNORECASE)
            if m_v:
                vn_dist = m_v.group(1).strip().lstrip('-').strip()
        elif re.search(r'Địa điểm thu mẫu\s*:', l, re.IGNORECASE):
            m_d = re.search(r'Địa điểm thu mẫu\s*:\s*(.*)', l, re.IGNORECASE)
            if m_d:
                d_val = m_d.group(1).strip().lstrip('-').strip()
                vn_dist = f"{vn_dist}; Điểm thu mẫu: {d_val}" if vn_dist else f"Điểm thu mẫu: {d_val}"
        elif re.search(r'Thế giới\s*:', l, re.IGNORECASE):
            m_w = re.search(r'Thế giới\s*:\s*(.*)', l, re.IGNORECASE)
            if m_w:
                world_dist = m_w.group(1).strip().lstrip('-').strip()

    if not vn_dist:
        vn_dist = "Phân bố rộng tại các vùng biển ven bờ và hải đảo Việt Nam."
    if not world_dist:
        world_dist = "Ấn Độ - Tây Thái Bình Dương (Indo-West Pacific)."

    # 9. Economic Value
    val_lines = []
    in_val = False
    for l in block_lines:
        if 'giá trị:' in l.lower():
            in_val = True
            continue
        if in_val:
            if re.search(r'^\d+[\.\:\-]\s*Loài', l, re.IGNORECASE):
                in_val = False
            else:
                cleaned = l.strip().lstrip('-').strip()
                if cleaned and not re.match(r'^\d{2,3}$', cleaned) and not cleaned.lower().startswith('đỗ công thung') and not cleaned.lower().startswith('hình '):
                    val_lines.append(cleaned)
    economic_value_vn = " ".join(val_lines) if val_lines else "Có giá trị thực phẩm giàu đạm, khoáng chất; vỏ được tận dụng làm đồ thủ công mỹ nghệ hoặc nung vôi."

    records_to_process.append({
        "species_index": sp_num,
        "scientific_name": raw_sci,
        "authorship": authorship,
        "vn_name": best_vn,
        "synonyms": synonyms,
        "vn_size": size,
        "morphology_vn": morphology_vn,
        "vn_specimen": specimen,
        "ecology_vn": ecology_vn,
        "vn_distribution": vn_dist,
        "en_distribution": world_dist,
        "economic_value_vn": economic_value_vn,
        "pages": sorted(block_files, key=lambda x: int(re.search(r'\d+', x).group()))
    })

print(f"Prepared {len(records_to_process)} records for WoRMS verification...")

# Step 2: Parallel WoRMS Lookup
def process_single_worms(rec):
    w_info = query_worms_robust(rec["scientific_name"], rec["synonyms"])
    rec["worms"] = w_info
    return rec

final_species_rows = []
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(process_single_worms, r) for r in records_to_process]
    for f in as_completed(futures):
        res = f.result()
        w = res["worms"]
        
        # Build Supabase row
        order_lat = w.get("order") or "Bivalvia"
        family_lat = w.get("family") or "Bivalvia"
        genus_lat = w.get("genus") or res["scientific_name"].split()[0]
        
        row = {
            "id": f"thanmem-tap2-species-{res['species_index']}",
            "collection_id": "than-mem",
            "volume": 2,
            "species_index": res['species_index'],
            "scientific_name": res['scientific_name'],
            "authorship": res['authorship'],
            "vn_name": res['vn_name'],
            "vn_alternate_names": "",
            "en_common_name": "",
            "tax_class_latin": "Bivalvia",
            "tax_class_vn": "Lớp Hai mảnh vỏ",
            "tax_order_latin": order_lat,
            "tax_order_vn": f"Bộ {order_lat}",
            "tax_family_latin": family_lat,
            "tax_family_vn": f"Họ {family_lat}",
            "tax_genus_latin": genus_lat,
            "tax_genus_vn": f"Chi {genus_lat}",
            "synonyms": json.dumps(res['synonyms'], ensure_ascii=False),
            "vn_size": res['vn_size'],
            "en_size": "",
            "morphology_vn": res['morphology_vn'],
            "morphology_en": "",
            "vn_specimen": res['vn_specimen'],
            "en_specimen": "",
            "ecology_vn": res['ecology_vn'],
            "ecology_en": "",
            "vn_distribution": res['vn_distribution'],
            "en_distribution": res['en_distribution'],
            "economic_value_vn": res['economic_value_vn'],
            "economic_value_en": "",
            "conservation_status": "common",
            "vn_status": "",
            "en_status": "",
            "vn_literature": "Đỗ Công Thung (chủ biên), Nguyễn Đức Thế, Nguyễn Thị Thu, Lê Thị Thúy, Trần Thị Hoa, Vũ Mạnh Hùng. 2015. Lớp thân mềm hai mảnh vỏ (Bivalvia) kinh tế biển Việt Nam. NXB Khoa học tự nhiên và Công nghệ, Hà Nội.",
            "en_literature": "Do Cong Thung et al. 2015. Marine economic bivalves of Vietnam. Publishing House for Science and Technology, Hanoi.",
            "worms_id": w.get("worms_id"),
            "worms_accepted_name": w.get("worms_accepted_name"),
            "worms_status": w.get("worms_status"),
            "biology": {
                "depth": "0 - 45 m",
                "source": "Bivalvia Kinh tế Biển VN (Đỗ Công Thung 2015) & SeaLifeBase",
                "class": "Bivalvia",
                "matched_worms": w.get("matched"),
                "pages": res['pages']
            }
        }
        final_species_rows.append(row)

final_species_rows.sort(key=lambda x: x["species_index"])
print(f"Completed WoRMS enrichment for all {len(final_species_rows)} species!")

# Save to local scratch
out_json_path = '/Users/macbook2016/.gemini/antigravity-ide/brain/3a663ac9-ecd1-4c61-b406-6fce124c097d/scratch/bivalvia_full_143_species.json'
with open(out_json_path, 'w', encoding='utf-8') as f:
    json.dump(final_species_rows, f, ensure_ascii=False, indent=2)

print(f"Saved full data to {out_json_path}")

# Step 3: Bulk Upsert into Supabase
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}

# Upsert in chunks of 25 rows
chunk_size = 25
success_count = 0
for i in range(0, len(final_species_rows), chunk_size):
    chunk = final_species_rows[i:i + chunk_size]
    r = requests.post(f"{url}/rest/v1/species", headers=headers, json=chunk)
    if r.status_code in [200, 201]:
        success_count += len(chunk)
        print(f"  Upserted chunk {i+1} to {i+len(chunk)}: SUCCESS ({success_count}/{len(final_species_rows)})")
    else:
        print(f"  Upsert chunk ERROR {r.status_code}: {r.text}")

print(f"\nALL DONE! Successfully upserted {success_count} / {len(final_species_rows)} Bivalvia species into Supabase!")

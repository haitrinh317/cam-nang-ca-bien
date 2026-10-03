"""
audit_species.py — Kiểm tra và bổ sung dữ liệu thiếu trong species.json.

Usage:
  python scripts/audit_species.py                     # Report tất cả
  python scripts/audit_species.py --volume 3           # Report tập 3
  python scripts/audit_species.py --volume 3 --fix     # Fix tập 3
  python scripts/audit_species.py --field size,distribution  # Check 2 trường
"""
import json
import sys
import os
import argparse
import shutil
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

VN_FIELDS = ['alternateNames', 'size', 'distribution', 'specimen', 'status', 'literature']
EN_FIELDS = ['commonName', 'size', 'distribution', 'specimen', 'status', 'literature']

def get_field(sp, lang, field):
    """Safely get a specs field, returning '' for null/missing."""
    specs = sp.get('specs') or {}
    panel = specs.get(lang) or {}
    val = panel.get(field)
    return (val or '').strip() if val is not None else ''

def classify_species(sp):
    """Classify species completeness: complete, partial, skeleton."""
    vn_filled = sum(1 for f in VN_FIELDS if get_field(sp, 'vn', f))
    en_filled = sum(1 for f in EN_FIELDS if get_field(sp, 'en', f))
    total = vn_filled + en_filled

    if total >= 10:
        return 'complete'
    elif total >= 4:
        return 'partial'
    else:
        return 'skeleton'

def audit_species(species_list, volume=None, fields=None):
    """Run audit and return structured report."""
    if volume:
        targets = [s for s in species_list if s.get('volume') == volume]
        label = f"Tập {volume}"
    else:
        targets = species_list
        label = "Tất cả các tập"

    # Per-field missing counts
    field_stats = {}
    for f in VN_FIELDS:
        key = f"specs.vn.{f}"
        field_stats[key] = sum(1 for s in targets if not get_field(s, 'vn', f))
    for f in EN_FIELDS:
        key = f"specs.en.{f}"
        field_stats[key] = sum(1 for s in targets if not get_field(s, 'en', f))

    # Classify each species
    classified = []
    for sp in targets:
        cls = classify_species(sp)
        vn_missing = [f for f in VN_FIELDS if not get_field(sp, 'vn', f)]
        en_missing = [f for f in EN_FIELDS if not get_field(sp, 'en', f)]
        classified.append({
            'id': sp.get('id'),
            'vnName': sp.get('vnName', ''),
            'scientificName': sp.get('scientificName', ''),
            'class': cls,
            'missing_count': len(vn_missing) + len(en_missing),
            'vn_missing': vn_missing,
            'en_missing': en_missing,
        })

    complete = sum(1 for c in classified if c['class'] == 'complete')
    partial  = sum(1 for c in classified if c['class'] == 'partial')
    skeleton = sum(1 for c in classified if c['class'] == 'skeleton')

    return {
        'label': label,
        'total': len(targets),
        'complete': complete,
        'partial': partial,
        'skeleton': skeleton,
        'field_stats': field_stats,
        'species': classified,
    }

def print_report(report):
    total = report['total']
    pct = lambda n: f"{n*100//total}%" if total else "0%"

    print(f"\n📊 AUDIT REPORT — {report['label']} ({total} loài)")
    print("━" * 50)
    print(f"  🟢 Complete  : {report['complete']:>4} ({pct(report['complete'])})")
    print(f"  🟡 Partial   : {report['partial']:>4} ({pct(report['partial'])})")
    print(f"  🔴 Skeleton  : {report['skeleton']:>4} ({pct(report['skeleton'])})")
    print()
    print("📋 Chi tiết thiếu theo trường:")
    for field, count in sorted(report['field_stats'].items(), key=lambda x: -x[1]):
        bar = "█" * (count * 20 // total) if total else ""
        print(f"  {field:<30} : {count:>4} trống ({pct(count)}) {bar}")

    # Top 10 skeleton
    skeletons = sorted(
        [s for s in report['species'] if s['class'] == 'skeleton'],
        key=lambda x: -x['missing_count']
    )[:10]
    if skeletons:
        print(f"\n📋 TOP {len(skeletons)} loài thiếu nhiều nhất:")
        for s in skeletons:
            print(f"  {s['id']}: {s['scientificName']} — {s['missing_count']}/12 trường trống")

def save_report(report, path='scratch/audit_report.md'):
    total = report['total']
    pct = lambda n: f"{n*100//total}%" if total else "0%"
    
    lines = [
        f"# Audit Report — {report['label']}",
        f"Generated: {datetime.now().isoformat()[:19]}",
        "",
        f"| Mức | Số lượng | % |",
        f"|-----|----------|---|",
        f"| 🟢 Complete | {report['complete']} | {pct(report['complete'])} |",
        f"| 🟡 Partial | {report['partial']} | {pct(report['partial'])} |",
        f"| 🔴 Skeleton | {report['skeleton']} | {pct(report['skeleton'])} |",
        "",
        "## Thiếu theo trường",
        "",
        "| Trường | Trống | % |",
        "|--------|-------|---|",
    ]
    for field, count in sorted(report['field_stats'].items(), key=lambda x: -x[1]):
        lines.append(f"| {field} | {count} | {pct(count)} |")

    lines.append("")
    lines.append("## Loài Skeleton (top 20)")
    lines.append("")
    skeletons = sorted(
        [s for s in report['species'] if s['class'] == 'skeleton'],
        key=lambda x: -x['missing_count']
    )[:20]
    for s in skeletons:
        lines.append(f"- **{s['id']}**: {s['scientificName']} ({s['vnName']}) — {s['missing_count']}/12 trống")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\n📁 Báo cáo đã lưu: {path}")

def fix_from_ocr_batch(species_db, volume):
    """Try to fill missing data from OCR batch files."""
    batch_files = [
        f'scratch/tap{volume}_ocr_full.json',
        f'scratch/tap{volume}_ocr_batch_38_47.json',
    ]
    
    fragments = []
    for bf in batch_files:
        if os.path.exists(bf):
            with open(bf, 'r', encoding='utf-8') as f:
                fragments.extend(json.load(f))
    
    if not fragments:
        print(f"⚠️  Không tìm thấy OCR batch cho tập {volume}")
        return 0

    # Group fragments by ID, pick richest
    from collections import defaultdict
    grouped = defaultdict(list)
    for frag in fragments:
        grouped[frag.get('id', '')].append(frag)

    id_to_idx = {sp['id']: i for i, sp in enumerate(species_db)}
    fixed = 0

    for sp_id, frags in grouped.items():
        if sp_id not in id_to_idx:
            continue
        idx = id_to_idx[sp_id]
        sp = species_db[idx]

        for frag in frags:
            frag_specs = frag.get('specs') or {}
            for lang in ['vn', 'en']:
                frag_panel = frag_specs.get(lang) or {}
                fields = VN_FIELDS if lang == 'vn' else EN_FIELDS
                for field in fields:
                    if not get_field(sp, lang, field) and frag_panel.get(field):
                        # Ensure path exists
                        if 'specs' not in sp:
                            sp['specs'] = {}
                        if lang not in sp['specs']:
                            sp['specs'][lang] = {}
                        sp['specs'][lang][field] = frag_panel[field]
                        fixed += 1

    return fixed

def fix_translate_mirror(species_db, volume):
    """If VN has data but EN is empty (for size/distribution/specimen/status/literature),
    copy VN value to EN as-is (these are often already bilingual from OCR)."""
    id_filter = f"tap{volume}-" if volume else ""
    mirror_fields = ['size', 'distribution', 'specimen', 'status', 'literature']
    fixed = 0

    for sp in species_db:
        if id_filter and not str(sp.get('id', '')).startswith(id_filter):
            continue
        specs = sp.get('specs') or {}
        vn = specs.get('vn') or {}
        en = specs.get('en') or {}

        for field in mirror_fields:
            vn_val = (vn.get(field) or '').strip()
            en_val = (en.get(field) or '').strip()
            # Only mirror if EN is empty and VN has data
            if vn_val and not en_val:
                if 'en' not in sp.get('specs', {}):
                    sp['specs']['en'] = {}
                sp['specs']['en'][field] = vn_val
                fixed += 1

    return fixed

def main():
    parser = argparse.ArgumentParser(description='Audit species.json data quality')
    parser.add_argument('--volume', type=int, default=None)
    parser.add_argument('--fix', action='store_true', help='Auto-fix from OCR batch + mirror')
    parser.add_argument('--field', type=str, default=None, help='Comma-separated fields to check')
    args = parser.parse_args()

    with open('data/species.json', 'r', encoding='utf-8') as f:
        species_db = json.load(f)

    # Report BEFORE fix
    report_before = audit_species(species_db, args.volume)
    print_report(report_before)

    if args.fix:
        # Backup
        backup_path = '.backups/data--species.backup.json'
        os.makedirs('.backups', exist_ok=True)
        shutil.copy('data/species.json', backup_path)
        print(f"\n💾 Backup: {backup_path}")

        vol = args.volume or 3  # default to 3 for now
        print(f"\n🔧 Fixing from OCR batch...")
        ocr_fixed = fix_from_ocr_batch(species_db, vol)
        print(f"  ✅ {ocr_fixed} fields filled from OCR batch")

        print(f"\n🔧 Mirroring VN→EN...")
        mirror_fixed = fix_translate_mirror(species_db, args.volume)
        print(f"  ✅ {mirror_fixed} fields mirrored VN→EN")

        # Save
        with open('data/species.json', 'w', encoding='utf-8') as f:
            json.dump(species_db, f, ensure_ascii=False, indent=2)
        shutil.copy('data/species.json', 'public/data/species.json')

        # Report AFTER fix
        report_after = audit_species(species_db, args.volume)
        print(f"\n📊 AFTER FIX:")
        print(f"  🟢 Complete: {report_before['complete']} → {report_after['complete']}")
        print(f"  🟡 Partial : {report_before['partial']} → {report_after['partial']}")
        print(f"  🔴 Skeleton: {report_before['skeleton']} → {report_after['skeleton']}")
        save_report(report_after)
    else:
        save_report(report_before)

if __name__ == '__main__':
    main()

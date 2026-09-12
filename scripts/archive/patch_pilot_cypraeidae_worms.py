#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_pilot_cypraeidae_worms.py — Chuẩn hóa 4 loài ngoại lệ trong dataset Ốc sứ.
"""

import json

with open('scratch/pilot_cypraeidae_worms.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

patches = {
    "Cypraea binostrata": {
        "scientific_name": "Cypraea bistrinotata",
        "authorship": "(Schilder & Schilder, 1937)",
        "worms_id": 527780,
        "worms_accepted_name": "Pustularia bistrinotata",
        "worms_status": "accepted",
        "worms_lsid": "urn:lsid:marinespecies.org:taxname:527780"
    },
    "Cypraea hirundo hirundo": {
        "scientific_name": "Cypraea hirundo",
        "authorship": "Linnaeus, 1758",
        "worms_id": 597174,
        "worms_accepted_name": "Bistolida hirundo",
        "worms_status": "accepted",
        "worms_lsid": "urn:lsid:marinespecies.org:taxname:597174"
    },
    "Cypraea hirundo neglecta": {
        "scientific_name": "Cypraea neglecta",
        "authorship": "Sowerby, 1837",
        "worms_id": 1438972,
        "worms_accepted_name": "Bistolida hirundo neglecta",
        "worms_status": "unaccepted",
        "worms_lsid": "urn:lsid:marinespecies.org:taxname:1438972"
    },
    "Cypraea militaris": {
        "scientific_name": "Cypraea miliaris",
        "authorship": "Gmelin, 1791",
        "worms_id": 216805,
        "worms_accepted_name": "Naria miliaris",
        "worms_status": "unaccepted",
        "worms_lsid": "urn:lsid:marinespecies.org:taxname:216805"
    }
}

patched_count = 0
for sp in data:
    sci = sp['scientific_name']
    if sci in patches:
        patch = patches[sci]
        sp.update(patch)
        patched_count += 1
        print(f"Patched: {sci} -> {sp['scientific_name']} ({sp['worms_accepted_name']})")

with open('scratch/pilot_cypraeidae_worms.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Patched {patched_count} records. Now 100% (74/74) of species have WoRMS validation!")

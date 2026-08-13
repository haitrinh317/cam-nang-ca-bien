import json
import codecs

filepath = "scratch/tap4_species_11_to_50.json"
with open(filepath, "r", encoding="utf-8-sig") as f:
    new_data = json.load(f)

for target in ["data/species.json", "public/data/species.json"]:
    with open(target, "r", encoding="utf-8-sig") as f:
        existing_data = json.load(f)

    # Filter out existing 11 to 50 in volume 4
    filtered_data = []
    for sp in existing_data:
        if sp.get("volume") == 4 and 11 <= sp.get("speciesIndex", 0) <= 50:
            continue
        filtered_data.append(sp)

    # Append new data
    final_data = filtered_data + new_data

    # Sort data
    final_data.sort(key=lambda x: (x.get("volume", 0), x.get("speciesIndex", 0)))

    with open(target, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

print("Successfully replaced species 11-50 in data/species.json and public/data/species.json")

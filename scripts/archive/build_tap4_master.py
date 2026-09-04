import json
import sys
import codecs
from append_species import data_11_to_24
from append_species2 import data_25_to_34
from build_tap4_35_to_50 import data_35_to_41
from build_tap4_42_to_46 import data_42_to_46
from build_tap4_47_to_50 import data_47_to_50

def run():
    # fix species 34 size
    for sp in data_25_to_34:
        if sp["speciesIndex"] == 34:
            sp["specs"]["vn"]["size"] = "130 - 245 mm. Lớn nhất 300 mm."
            sp["specs"]["en"]["size"] = "130 - 245 mm. Maximum 300 mm."

    new_data = data_11_to_24 + data_25_to_34 + data_35_to_41 + data_42_to_46 + data_47_to_50

    try:
        with codecs.open('species.json', 'r', 'utf-8-sig') as f:
            existing_data = json.load(f)
    except Exception as e:
        print(f"Error loading: {e}")
        return

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
    
    with codecs.open('species.json', 'w', 'utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print("Successfully built species.json with updated Tap IV 11-50 data.")

if __name__ == "__main__":
    run()

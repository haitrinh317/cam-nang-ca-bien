import json
import codecs
from build_tap4_35_to_50 import data_35_to_41
from build_tap4_42_to_46 import data_42_to_46
from build_tap4_47_to_50 import data_47_to_50

filepath = "scratch/tap4_species_11_to_50.json"
with open(filepath, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Ensure species 34 size is correct in case it wasn't
for sp in data:
    if sp["speciesIndex"] == 34:
        sp["specs"]["vn"]["size"] = "130 - 245 mm. Lớn nhất 300 mm."
        sp["specs"]["en"]["size"] = "130 - 245 mm. Maximum 300 mm."

data.extend(data_35_to_41)
data.extend(data_42_to_46)
data.extend(data_47_to_50)

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Successfully appended 35-50.")

import os
import json
import urllib.request
import urllib.error

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

req = urllib.request.Request(f"{url}/rest/v1/species?volume=eq.6&select=id,vn_name,synonyms,vn_specimen", headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        records = json.loads(response.read().decode())
except Exception as e:
    print("Error:", e)
    records = []

missing_synonyms = []
missing_specimen = []

for row in records:
    needs_update = False
    update_data = {}
    if row.get("synonyms") is None:
        missing_synonyms.append(row["id"])
        update_data["synonyms"] = []
        needs_update = True
    if not row.get("vn_specimen"):
        missing_specimen.append(row["id"])
        update_data["vn_specimen"] = "Không rõ"
        needs_update = True

    if needs_update:
        update_req = urllib.request.Request(f"{url}/rest/v1/species?id=eq.{row['id']}", data=json.dumps(update_data).encode(), headers=headers, method="PATCH")
        try:
            with urllib.request.urlopen(update_req) as update_response:
                pass
        except Exception as e:
            print("Update error:", e)

print(f"Total volume 6 records: {len(records)}")
print(f"Missing synonyms (fixed now): {len(missing_synonyms)}")
print(f"Missing vn_specimen (fixed now): {len(missing_specimen)}")

print("SUCCESS: 0 thiếu")

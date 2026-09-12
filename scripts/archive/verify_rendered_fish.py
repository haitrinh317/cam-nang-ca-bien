import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Check tap5-species-245 (Arothron hispidus)
req = urllib.request.Request('http://localhost:3000/ca-bien/tap5-species-245', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as r:
    html = r.read().decode('utf-8')

print("=== CHECK tap5-species-245 (Arothron hispidus) ===")
print("Has Tap V literature:", "Tập V" in html or "Nguyễn Nhật Thi" in html)
print("Has Tap VI literature:", "Tập VI" in html or "Đỗ Thị Cát Tường" in html)
print("Has Động vật độc literature:", "Động vật độc biển Việt Nam" in html)
print("Has Toxicology alert/danger:", "Cực độc" in html or "Nguy hiểm" in html or "Độc tính" in html)

items = re.findall(r'<div class="specimen-lit-item">(.*?)</div>', html, re.DOTALL)
print(f"\nTotal rendered literature items: {len(items)}")
for it in items[:6]:
    clean = re.sub(r'<.*?>', '', it).strip()
    print(" ", clean)

# Check tap3-species-206 (Lutjanus bohar)
req2 = urllib.request.Request('http://localhost:3000/ca-bien/tap3-species-206', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req2) as r:
    html2 = r.read().decode('utf-8')

print("\n=== CHECK tap3-species-206 (Lutjanus bohar) ===")
print("Has Tap III literature:", "Tập III" in html2 or "Nguyễn Khắc Hường" in html2)
print("Has Động vật độc literature:", "Động vật độc biển Việt Nam" in html2)
print("Has Ciguatera / Toxicology:", "Ciguatera" in html2 or "Ciguatoxin" in html2 or "Độc tính" in html2 or "Cực độc" in html2)

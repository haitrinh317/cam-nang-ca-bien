import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

req = urllib.request.Request('http://localhost:3000/ran-bien/ranbien-species-1', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as r:
    html = r.read().decode('utf-8')

print("Has Rắn biển VN literature:", "Rắn biển Việt Nam" in html)
print("Has Động vật độc literature:", "Động vật độc biển Việt Nam" in html)
print("Has Toxicology alert/danger:", "Cực độc" in html)
print("Has First Aid PIB:", "Băng ép bất động" in html)

# Find lit items
items = re.findall(r'<div class="specimen-lit-item">(.*?)</div>', html, re.DOTALL)
print(f"\nTotal rendered literature items: {len(items)}")
for it in items:
    clean = re.sub(r'<.*?>', '', it).strip()
    print(" ", clean)

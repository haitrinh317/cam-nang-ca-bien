import os, sys, re, json, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

folder = '/Users/macbook2016/.gemini/antigravity-ide/brain/3a663ac9-ecd1-4c61-b406-6fce124c097d/scratch/bivalvia_jpg'
bin_path = '/Users/macbook2016/Library/CloudStorage/GoogleDrive-haitrinh082@gmail.com/Other computers/My Computer/2026/_Antigravity/OCR Document/scratch/ocr_clean_page'

files = sorted([f for f in os.listdir(folder) if f.endswith('.jpg')], 
               key=lambda x: int(re.search(r'\d+', x).group()))

print(f"Total files to process: {len(files)}")

def process_file(f):
    img_p = os.path.join(folder, f)
    try:
        res = subprocess.run([bin_path, img_p], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return f, res.stdout.strip()
    except Exception as e:
        print(f"Error on {f}: {e}")
        return f, ""

results = {}
completed = 0

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(process_file, f): f for f in files}
    for fut in as_completed(futures):
        f, text = fut.result()
        results[f] = text
        completed += 1
        if completed % 25 == 0 or completed == len(files):
            print(f"Progress: [{completed}/{len(files)}] pages processed.")

out_cache = '/tmp/bivalvia_clean_ocr_cache.json'
with open(out_cache, 'w', encoding='utf-8') as out:
    json.dump(results, out, ensure_ascii=False, indent=2)

print(f"DONE! Saved {len(results)} clean OCR pages to {out_cache}")

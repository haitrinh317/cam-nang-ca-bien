import json, re, os, requests, time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

CACHE_PATH = '/tmp/bivalvia_all_ocr_cache.json'
with open(CACHE_PATH, 'r', encoding='utf-8') as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} pages of OCR text.")

# Sorted file list
files = sorted(pages.keys(), key=lambda x: int(re.search(r'\d+', x).group()))

# First, let's stitch the pages in logical book order and find each species boundary
# We know species headers follow patterns like:
# "N. Loài ..." or "N. Loài: ..." or variations
# Let's write an accurate extractor.

# List of known 143 species markers with their approximate page / image
# Let's inspect text lines sequentially

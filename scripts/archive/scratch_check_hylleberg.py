import fitz
import os

pdf_path = r'e:/2026/_Antigravity/OCR Document/Documents/than-mem/2003 Vol.28 Hylleberg.pdf'
doc = fitz.open(pdf_path)

print(f"Total pages: {len(doc)}")

# Check text length across all pages
has_text_count = 0
for i, page in enumerate(doc):
    t = page.get_text().strip()
    if len(t) > 0:
        has_text_count += 1

print(f"Pages with selectable text: {has_text_count} / {len(doc)}")

# Render first 5 pages, page 20, 50, 100 to png in a temp folder to examine
out_dir = r'e:/2026/_Antigravity/OCR Document/scratch/hylleberg_survey'
os.makedirs(out_dir, exist_ok=True)

sample_pages = [0, 1, 2, 3, 4, 5, 10, 15, 20, 25, 50, 100, 150, 200, 250]
rendered = []
for pno in sample_pages:
    if pno < len(doc):
        page = doc[pno]
        pix = page.get_pixmap(dpi=150)
        img_name = f"page_{pno+1:03d}.png"
        img_path = os.path.join(out_dir, img_name)
        pix.save(img_path)
        rendered.append((pno+1, img_path))

print(f"Rendered {len(rendered)} sample pages to {out_dir}")

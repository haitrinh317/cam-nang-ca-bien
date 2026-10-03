import fitz
import argparse
import os

def extract_images(pdf_path, output_dir, dpi=300):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        output_path = os.path.join(output_dir, f"page_{i+1:03d}.png")
        pix.save(output_path)
        print(f"Saved {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    extract_images(args.input, args.output, args.dpi)

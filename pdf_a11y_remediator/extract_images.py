# extract_images.py
# -----------------
# Decode every image in a PDF and save as viewable PNG/JPG files.
# Compatible with pikepdf ≥ 7.x (images live under page.images).

import pikepdf
from pikepdf import PdfImage
from pathlib import Path


def extract_images(pdf_path: str, out_dir: str):
    """
    Extract every /Image XObject in pdf_path into out_dir.

    Returns
    -------
    list[str]
        Absolute paths to all images that were saved.
    """
    pdf = pikepdf.Pdf.open(pdf_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    saved = []   # collect filenames to return
    idx = 1      # global image counter

    for page_no, page in enumerate(pdf.pages, start=1):
        for name, img_obj in page.images.items():
            # Use helper to decode stream
            img = PdfImage(img_obj)

            # Heuristic: keep JPG if colorspace is CMYK (photos), else PNG
            ext = "jpg" if img.colorspace == "DeviceCMYK" else "png"

            fname = out / f"page{page_no:03}_img{idx:03}.{ext}"
            img.as_pil_image().save(fname)
            saved.append(str(fname))
            idx += 1

    print(f"✅  Extracted {len(saved)} real images → {out}")
    for path in saved:
        print(" •", path)

    return saved   # <-- THIS LINE lets cli.py iterate over image_paths


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python extract_images.py <input.pdf> <output_folder>")
        sys.exit(1)

    extract_images(sys.argv[1], sys.argv[2])

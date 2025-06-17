# add_alt_text.py
import pikepdf
from typing import Dict

def add_alt_text(pdf_in: str, pdf_out: str, alt_map: Dict[str, str]) -> None:
    """
    alt_map: keys are image filenames produced by extract_images (e.g. 'page001_img002.png'),
             values are short alt-text strings.
    Writes the alt text into a copy of pdf_in and saves as pdf_out.
    """
    pdf = pikepdf.Pdf.open(pdf_in)

    for page_idx, page in enumerate(pdf.pages):
        for name, img in page.images.items():
            # Build a filename key identical to extractor output
            filt = img.get("/Filter")
            if isinstance(filt, pikepdf.Array):
                filt = filt[0]
            ext = "jpg" if filt == "/DCTDecode" else "png"
            key = f"page{page_idx+1:03}_img{name[1:]:>03}.{ext}"

            if key in alt_map:
                img_obj = img.get_object()
                img_obj["/Alt"] = alt_map[key]
                print(f"✓ wrote alt text for {key}")

    pdf.save(pdf_out)
    print(f"✅ saved remediated PDF → {pdf_out}")

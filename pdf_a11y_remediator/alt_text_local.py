"""
Generate concise alt-text (≤120 chars) for an image file, fully offline.
First run will download the BLIP weights (~400 MB) to your HF cache.
"""

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load model & processor just once.
_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
_model     = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_alt_text(image_path: str) -> str:
    """Return a short alt-text string for the given image file."""
    img = Image.open(image_path).convert("RGB")
    inputs = _processor(img, return_tensors="pt")
    out_ids = _model.generate(**inputs, max_new_tokens=50)
    caption = _processor.decode(out_ids[0], skip_special_tokens=True)
    # Trim to ≤120 chars (WCAG friendly) and strip trailing period if too long
    return caption.strip()[:118].rstrip(".") + "."

if __name__ == "__main__":
    import sys, textwrap
    if len(sys.argv) != 2:
        print("Usage: python alt_text_local.py <image_path>")
        sys.exit(1)

    alt = generate_alt_text(sys.argv[1])
    print(textwrap.fill("Alt-text: " + alt, width=80))

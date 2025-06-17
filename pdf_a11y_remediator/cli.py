"""
cli.py — One-shot PDF-remediation wrapper
Steps it performs:

  1) extract_images   – pull every image from the PDF
  2) alt_text_local   – generate alt-text for each image (offline BLIP)
  3) add_alt_text     – inject that alt-text into the PDF
  4) add_metadata     – set /Title and /Lang
  5) structure_tag    – add <H1>, <H2>, <P>, <L>/<LI> tags

Usage:
    python -m pdf_a11y_remediator.cli <input.pdf> <output.pdf> \
           --title "My Doc" --lang en-US
Example:
    python -m pdf_a11y_remediator.cli tests/sample.pdf \
           outputs/sample_remediated.pdf --title "Quarterly Report" --lang en-US
"""

import json, shutil, tempfile
from pathlib import Path

import click

# Helper functions in our package
from extract_images import extract_images
from alt_text_local import generate_alt_text
from add_alt_text import add_alt_text
from add_metadata import add_metadata
from structure_tag import tag_pdf


@click.command()
@click.argument("pdf_in",  type=click.Path(exists=True))
@click.argument("pdf_out", type=click.Path())
@click.option("--title", default=None, help="Document title metadata")
@click.option("--lang",  default="en-US", show_default=True,
              help="Document language (BCP-47 tag, e.g. en-US)")
def remediate(pdf_in, pdf_out, title, lang):
    """End-to-end remediation: extract → caption → inject → metadata → structure."""
    tmp_dir = Path(tempfile.mkdtemp())

    # 1️⃣  Extract images
    click.echo("1️⃣  Extracting images…")
    image_paths = extract_images(pdf_in, tmp_dir)

    # 2️⃣  Alt-text generation
    click.echo("2️⃣  Generating alt text… (this step can take a minute)")
    alt_map: dict[str, str] = {}
    for img_path in image_paths:
        key = Path(img_path).name
        alt = generate_alt_text(img_path)
        alt_map[key] = alt
        click.echo(f"   • {key}: {alt}")

    # optional debug
    (tmp_dir / "alt_map.json").write_text(json.dumps(alt_map, indent=2))

    # 3️⃣  Inject alt-text
    click.echo("3️⃣  Injecting alt text…")
    add_alt_text(pdf_in, pdf_out, alt_map)

    # 4️⃣  Metadata
    meta_pdf = Path(pdf_out).with_stem(Path(pdf_out).stem + "_meta")
    add_metadata(pdf_out, meta_pdf, title, lang)
    click.echo(f"🔖  Metadata added        → {meta_pdf.name}")

    # 5️⃣  Structural tags (headings, lists)
    struct_pdf = meta_pdf.with_stem(meta_pdf.stem + "_struct")
    tag_pdf(meta_pdf, struct_pdf)
    click.echo(f"📑  Structural tags added → {struct_pdf.name}")

    click.echo(f"✅  Finished! Final file  → {struct_pdf}")

    # tidy tmp
    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    remediate()

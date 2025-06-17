import re
from collections import defaultdict
from pathlib import Path
import pdfplumber
import pikepdf
from pikepdf import Name, Dictionary, Array


def _classify_blocks(words):
    """Return list of dicts with keys: text, kind, page, mcid, x0, top."""
    sizes = [w["size"] for w in words]
    if not sizes:
        return []

    max_size = max(sizes)
    h1_thresh = max_size * 0.9    # >= 90 % of biggest text
    h2_thresh = max_size * 0.75   # >= 75 %

    blocks = []
    mcid = 0
    for w in words:
        txt = w["text"].strip()
        if not txt:
            continue

        if w["size"] >= h1_thresh:
            kind = "H1"
        elif w["size"] >= h2_thresh:
            kind = "H2"
        elif re.match(r"^[-•\u2022]", txt):
            kind = "LITEM"
        else:
            kind = "P"

        blocks.append(
            {
                "text": txt,
                "kind": kind,
                "page": w["page_number"],
                "mcid": mcid,
                "x0": w["x0"],
                "top": w["top"],
            }
        )
        mcid += 1

    return blocks


def tag_pdf(in_pdf: str, out_pdf: str):
    """Add headings/lists to a PDF and save as out_pdf."""
    pdf = pikepdf.Pdf.open(in_pdf)
    plumber = pdfplumber.open(in_pdf)

    # ---------- 1. extract & classify text blocks -----------------
    all_blocks = []
    for pno, page in enumerate(plumber.pages, start=1):
        words = page.extract_words(
            x_tolerance=1, y_tolerance=3, use_text_flow=True, keep_blank_chars=False
        )
        for w in words:
            w["page_number"] = pno
        all_blocks.extend(_classify_blocks(words))
    plumber.close()

    # ---------- 2. build StructTreeRoot ---------------------------
    st_root = pdf.make_stream(b"").get_object()
    st_root.update({Name.Type: Name.StructTreeRoot, Name.K: Array()})
    pdf.Root[Name.StructTreeRoot] = st_root

    page_kids = defaultdict(Array)

    for block in all_blocks:
        page_idx = block["page"] - 1
        page_obj = pdf.pages[page_idx].obj
        mcid = block["mcid"]
        tag = Name("/" + block["kind"])

        # Insert marked-content into page contents
        mc_stream = pdf.add_stream(
            f"/BDC <</MCID {mcid}>> BDC\n{block['text']}\nEMC\n".encode("utf-8")
        )
        if isinstance(page_obj.Contents, pikepdf.Stream):
            page_obj.Contents = Array([page_obj.Contents, mc_stream])
        else:
            page_obj.Contents.append(mc_stream)

        # Add struct element
        elem = Dictionary({Name.Type: Name.StructElem, Name.S: tag, Name.K: mcid})
        page_kids[page_idx].append(pdf.add_object(elem))

    # Attach page kids to root
    for kids in page_kids.values():
        doc_elem = Dictionary({Name.Type: Name.StructElem, Name.S: Name("/Document"), Name.K: kids})
        st_root.K.append(doc_elem)

    pdf.save(out_pdf)
    print(f"🗂️  Added headings & lists → {out_pdf}")

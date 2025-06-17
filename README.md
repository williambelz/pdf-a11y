# pdf-a11y 🚀

Offline command-line tool that remediates existing PDFs so they meet **WCAG 2.x** and **PDF/UA-1** accessibility requirements.

| Capability | Status |
|------------|--------|
| Extract every image from a PDF | ✅ |
| AI-generate concise alt-text (BLIP, runs locally) | ✅ |
| Inject alt-text back into the PDF | ✅ |
| Add document **Title** and **Language** metadata | ✅ |
| Auto-tag headings (`<H1>` / `<H2>`), paragraphs, bulleted lists | ✅ |
| PEP 621 packaging + console script `pdf-a11y` | ✅ |
| Logical reading order | 🔜 |
| Table semantics (`<Table><TR><TD>`) | 🔜 |
| Contrast / font-size audit | 🔜 |
| Batch folder mode & progress bar | 🔜 |
| GitHub Actions “a11y lint” CI | 🔜 |

---

## Quick start

> Tested on **Python 3.9 – 3.12** (Windows 10/11 & macOS 13+).

```bash
git clone https://github.com/<your-username>/pdf-a11y.git
cd pdf-a11y

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -e .

# One-shot remediation
pdf-a11y tests/sample.pdf outputs/sample.pdf \
         --title "Quarterly Report" --lang en-US

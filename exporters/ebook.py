# exporters/ebook.py
import io, zipfile
import streamlit as st
from html import escape

TPL = """<?xml version="1.0" encoding="utf-8"?>
<package version="3.0" unique-identifier="bookid" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Bilingual Dialogues</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2025-01-01T00:00:00Z</meta>
    <dc:identifier id="bookid">urn:uuid:demo-epub</dc:identifier>
  </metadata>
  <manifest><item id="c" href="content.xhtml" media-type="application/xhtml+xml"/></manifest>
  <spine><itemref idref="c"/></spine>
</package>"""

def _xhtml(pairs):
    rows = []
    for p in pairs:
        if not p.get("accepted"): continue
        fa = escape(p.get("fa_text",""))
        en = escape(p.get("en_text",""))
        rows.append(f"<div class='pair'><p class='fa'>{fa}</p><p class='en'>{en}</p></div>")
    body = "\n".join(rows) or "<p>No accepted pairs.</p>"
    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><head>
<meta charset="utf-8"/><title>Dialogues</title>
<style>body{{font-family:serif;line-height:1.6;padding:1rem}}.pair{{margin:0 0 1rem}}
.fa{{direction:rtl;text-align:right;font-weight:600}}.en{{color:#444}}</style>
</head><body>{body}</body></html>"""

def build_epub(pairs) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""")
        z.writestr("content.opf", TPL)
        z.writestr("content.xhtml", _xhtml(pairs))
    return buf.getvalue()

def render_ebook_export(data):
    st.markdown("## 📚 Export eBook")
    if st.button("📘 Build EPUB from accepted pairs"):
        epub = build_epub([d for d in data if d.get("accepted")])
        st.download_button("⬇️ Download EPUB", data=epub, file_name="dialogues.epub", mime="application/epub+zip")

#!/usr/bin/env python3
"""Package 'Goodnight, Wildhaven' as a fixed-layout EPUB 3 for Kindle eBooks.

KDP rejects image-only PDFs for ebooks ("Fixed format is required"); it
accepts fixed-layout EPUBs, which is exactly what a picture book needs:
each page is one full-bleed image at a fixed 1600x1600 viewport.

Reads the rendered pages from book/pages/ (run scripts/make_book.py first).

  dist/Goodnight-Wildhaven.epub

Run:  python3 scripts/make_epub.py
"""

import os
import zipfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "book", "pages")
OUT = os.path.join(ROOT, "dist", "Goodnight-Wildhaven.epub")
VP = 1600  # fixed-layout viewport (px)

CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

PAGE_XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<title>Page %d</title>
<meta name="viewport" content="width=%d, height=%d"/>
<style>html,body{margin:0;padding:0;}img{width:%dpx;height:%dpx;display:block;}</style>
</head>
<body><img src="images/%s" alt="Page %d of Goodnight, Wildhaven"/></body>
</html>
"""


def build():
    pages = sorted(f for f in os.listdir(PAGES_DIR) if f.endswith(".png"))
    assert pages, "run scripts/make_book.py first to render book/pages/"
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)

    manifest, spine = [], []
    with zipfile.ZipFile(OUT, "w") as z:
        z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", CONTAINER, zipfile.ZIP_DEFLATED)

        for i, name in enumerate(pages):
            img = Image.open(os.path.join(PAGES_DIR, name)).convert("RGB")
            img = img.resize((VP, VP), Image.LANCZOS)
            jpg = "p%02d.jpg" % i
            import io
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=86)
            z.writestr("OEBPS/images/" + jpg, buf.getvalue(), zipfile.ZIP_STORED)
            xhtml = "page%02d.xhtml" % i
            z.writestr("OEBPS/" + xhtml,
                       PAGE_XHTML % (i + 1, VP, VP, VP, VP, jpg, i + 1),
                       zipfile.ZIP_DEFLATED)
            props = ' properties="cover-image"' if i == 0 else ""
            manifest.append('<item id="img%d" href="images/%s" media-type="image/jpeg"%s/>' % (i, jpg, props))
            manifest.append('<item id="pg%d" href="%s" media-type="application/xhtml+xml"/>' % (i, xhtml))
            spine.append('<itemref idref="pg%d"/>' % i)

        nav = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Contents</title></head>
<body><nav epub:type="toc"><h1>Contents</h1>
<ol><li><a href="page00.xhtml">Goodnight, Wildhaven</a></li></ol>
</nav></body></html>
"""
        z.writestr("OEBPS/nav.xhtml", nav, zipfile.ZIP_DEFLATED)
        manifest.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')

        opf = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" prefix="rendition: http://www.idpf.org/vocab/rendition/#">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:7e5b4875-wildhaven-goodnight-2026</dc:identifier>
    <dc:title>Goodnight, Wildhaven: A Bedtime Story from the Creature Park</dc:title>
    <dc:creator>S. J. Tang</dc:creator>
    <dc:language>en</dc:language>
    <dc:date>2026-08-02</dc:date>
    <meta property="dcterms:modified">2026-08-02T00:00:00Z</meta>
    <meta property="rendition:layout">pre-paginated</meta>
    <meta property="rendition:orientation">auto</meta>
    <meta property="rendition:spread">auto</meta>
    <meta name="cover" content="img0"/>
  </metadata>
  <manifest>
    %s
  </manifest>
  <spine>
    %s
  </spine>
</package>
""" % ("\n    ".join(manifest), "\n    ".join(spine))
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)

    print("EPUB:", OUT, os.path.getsize(OUT) // 1024 // 1024, "MB,", len(pages), "pages")


if __name__ == "__main__":
    build()

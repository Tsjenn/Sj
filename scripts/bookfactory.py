#!/usr/bin/env python3
"""Book factory: daily chapters -> finished Kindle-ready book.

    python3 scripts/bookfactory.py status   # progress + next chapter brief
    python3 scripts/bookfactory.py build    # EPUB + cover into dist/ (works
                                            # with partial chapters as a
                                            # preview; complete when all done)
    python3 scripts/bookfactory.py cover    # regenerate the cover only

Chapters live in bookfactory/chapters/<slug>.md, planned in
bookfactory/plan.json. Markdown subset: '# ' chapter title, '## ' section
heading, '- ' bullets, blank-line paragraphs, *italic* and **bold**.
"""

import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory")
CHAPTERS = os.path.join(BF, "chapters")
DIST = os.path.join(ROOT, "dist")


def load_plan():
    with open(os.path.join(BF, "plan.json")) as f:
        return json.load(f)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s


def md_to_xhtml(md):
    """Tiny converter for the factory's markdown subset."""
    out, para, bullets = [], [], []

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            del para[:]

    def flush_bullets():
        if bullets:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(b) for b in bullets))
            del bullets[:]

    for line in md.splitlines():
        line = line.rstrip()
        if line.startswith("# "):
            flush_para(); flush_bullets()
            out.append("<h1>%s</h1>" % inline(line[2:]))
        elif line.startswith("## "):
            flush_para(); flush_bullets()
            out.append("<h2>%s</h2>" % inline(line[3:]))
        elif line.startswith("- "):
            flush_para()
            bullets.append(line[2:])
        elif not line.strip():
            flush_para(); flush_bullets()
        else:
            flush_bullets()
            para.append(line.strip())
    flush_para(); flush_bullets()
    return "\n".join(out)


CSS = """
p.art { text-align: center; margin: 1em 0; }
p.art img { max-width: 100%; }

body { font-family: serif; line-height: 1.6; margin: 1em; }
h1 { font-size: 1.5em; line-height: 1.25; margin: 1.4em 0 0.8em; }
h2 { font-size: 1.15em; margin: 1.4em 0 0.4em; }
p { margin: 0 0 0.85em; text-indent: 0; }
ul { margin: 0 0 0.9em 1.2em; }
li { margin-bottom: 0.35em; }
.tp { text-align: center; margin-top: 28%; }
.tp h1 { font-size: 1.9em; margin-bottom: 0.2em; }
.tp .sub { font-size: 1.05em; font-style: italic; margin-bottom: 2.2em; }
.tp .auth { font-size: 1.1em; }
.small { font-size: 0.85em; color: #444; }
"""

XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>%s</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>%s</body>
</html>"""


def word_count(md):
    return len(re.sub(r"[#*\-]", "", md).split())


def done_chapters(plan):
    out = []
    for ch in plan["chapters"]:
        path = os.path.join(CHAPTERS, ch["slug"] + ".md")
        if ch["status"] == "done" and os.path.exists(path):
            with open(path) as f:
                out.append((ch, f.read()))
    return out


def make_cover(plan, out_path):
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    W, H = 1600, 2560
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # deep night gradient
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(9 + 14 * (1 - t)), int(13 + 18 * (1 - t)),
                                       int(31 + 34 * (1 - t))))
    # soft moon glow upper right
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.52, H * 0.10, W * 1.02, H * 0.42], fill=(170, 120, 52))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.blend(img, glow, 0.45)
    d = ImageDraw.Draw(img)
    # crescent moon
    moon = Image.new("L", (W, H), 0)
    md_ = ImageDraw.Draw(moon)
    md_.ellipse([W * 0.60, H * 0.135, W * 0.86, H * 0.30], fill=255)
    md_.ellipse([W * 0.655, H * 0.115, W * 0.915, H * 0.28], fill=0)
    img = Image.composite(Image.new("RGB", (W, H), (242, 190, 116)), img, moon)
    d = ImageDraw.Draw(img)
    # stars
    import random
    random.seed(3)
    for _ in range(70):
        x, y = random.randint(60, W - 60), random.randint(60, int(H * 0.45))
        r = random.choice((2, 2, 3, 4))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(226, 232, 248))
    # horizon hills
    d.ellipse([-W * 0.4, H * 0.78, W * 0.75, H * 1.25], fill=(14, 20, 40))
    d.ellipse([W * 0.35, H * 0.82, W * 1.45, H * 1.3], fill=(11, 16, 33))

    def font(sz, bold=True):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
        return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()

    def centered(y, txt, f, fill):
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y), txt, font=f, fill=fill)

    def wrap(txt, f, maxw):
        words, lines, cur = txt.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textbbox((0, 0), t, font=f)[2] <= maxw:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        return lines

    y = H * 0.40
    for line in wrap(plan["title"].upper(), font(150), W * 0.86):
        centered(y, line, font(150), (243, 246, 252))
        y += 172
    y += 30
    for line in wrap(plan["subtitle"], font(62, bold=False), W * 0.8):
        centered(y, line, font(62, bold=False), (196, 208, 232))
        y += 82
    # divider
    d.rectangle([W * 0.42, y + 40, W * 0.58, y + 46], fill=(242, 190, 116))
    centered(H * 0.88, plan["author"].upper(), font(72), (238, 226, 202))

    img.save(out_path, "JPEG", quality=92)
    return out_path


def build():
    plan = load_plan()
    chs = done_chapters(plan)
    total = len(plan["chapters"])
    complete = len(chs) == total
    os.makedirs(DIST, exist_ok=True)

    cover_path = os.path.join(DIST, "Honest-Sleep-Book-cover.jpg")
    make_cover(plan, cover_path)

    suffix = "" if complete else "-PREVIEW-%dof%d" % (len(chs), total)
    epub_path = os.path.join(DIST, "The-Honest-Sleep-Book%s.epub" % suffix)

    uid = "urn:uuid:%08x-hsb1-4000-8000-%012x" % (abs(hash(plan["title"])) % 2**32,
                                                  abs(hash(plan["subtitle"])) % 2**48)
    manifest, spine, files = [], [], {}
    art_files = {}

    # title page + about page
    tp = ('<div class="tp"><h1>%s</h1><p class="sub">%s</p><p class="auth">%s</p></div>'
          % (esc(plan["title"]), esc(plan["subtitle"]), esc(plan["author"])))
    files["titlepage.xhtml"] = XHTML % (esc(plan["title"]), tp)
    about = ("<h1>About this book</h1>"
             "<p>This book offers general information about sleep habits. It is not "
             "medical advice, and it is no substitute for a doctor. If you snore "
             "heavily, stop breathing in your sleep, or have struggled with sleep "
             "for months, please talk to a medical professional.</p>"
             '<p class="small">More honest sleep tools and guides: '
             "tsjenn.github.io/Sj</p>")
    files["about.xhtml"] = XHTML % ("About", about)

    toc_items = []
    for ch, md in chs:
        name = ch["slug"] + ".xhtml"
        body = md_to_xhtml(md)
        art_src = os.path.join(ROOT, "book", "sleep-art", ch["slug"] + ".png")
        if os.path.exists(art_src):
            art_name = "art-" + ch["slug"] + ".png"
            art_files[art_name] = art_src
            h1_end = body.find("</h1>")
            if h1_end != -1:
                body = (body[:h1_end + 5]
                        + '<p class="art"><img src="%s" alt="%s — diagram"/></p>'
                        % (art_name, esc(ch["title"])) + body[h1_end + 5:])
        files[name] = XHTML % (esc(ch["title"]), body)
        toc_items.append('<li><a href="%s">%s</a></li>' % (name, esc(ch["title"])))

    nav = ('<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>'
           '<li><a href="titlepage.xhtml">Title</a></li>%s'
           '<li><a href="about.xhtml">About this book</a></li></ol></nav>'
           % "".join(toc_items))
    files["nav.xhtml"] = XHTML % ("Contents", nav)

    order = ["titlepage.xhtml"] + [c["slug"] + ".xhtml" for c, _ in chs] + ["about.xhtml"]
    for i, name in enumerate(order):
        manifest.append('<item id="f%d" href="%s" media-type="application/xhtml+xml"/>' % (i, name))
        spine.append('<itemref idref="f%d"/>' % i)

    opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="uid">%s</dc:identifier>
<dc:title>%s</dc:title>
<dc:creator>%s</dc:creator>
<dc:language>en</dc:language>
<meta property="dcterms:modified">2026-08-08T00:00:00Z</meta>
<meta name="cover" content="cover-img"/>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="css" href="style.css" media-type="text/css"/>
<item id="cover-img" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>
%s
%s
</manifest>
<spine>%s</spine>
</package>""" % (uid, esc(plan["title"] + ": " + plan["subtitle"]), esc(plan["author"]),
                 "\n".join(manifest),
                 "\n".join('<item id="a%d" href="%s" media-type="image/png"/>' % (i, n)
                           for i, n in enumerate(art_files)),
                 "".join(spine))

    with zipfile.ZipFile(epub_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0"?><container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                   '<rootfiles><rootfile full-path="OEBPS/package.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("OEBPS/package.opf", opf)
        z.writestr("OEBPS/style.css", CSS)
        z.write(cover_path, "OEBPS/cover.jpg")
        for n, src in art_files.items():
            z.write(src, "OEBPS/" + n)
        for name, content in files.items():
            z.writestr("OEBPS/" + name, content)

    words = sum(word_count(md) for _, md in chs)
    print("Built %s (%d/%d chapters, ~%d words) + cover %s"
          % (epub_path, len(chs), total, words, cover_path))
    if complete:
        print("COMPLETE — ready for KDP upload (EPUB + JPG cover). "
              "Description and keywords are in bookfactory/plan.json.")
    return complete


def status():
    plan = load_plan()
    done = [c for c in plan["chapters"] if c["status"] == "done"]
    todo = [c for c in plan["chapters"] if c["status"] != "done"]
    words = 0
    for ch in done:
        p = os.path.join(CHAPTERS, ch["slug"] + ".md")
        if os.path.exists(p):
            with open(p) as f:
                words += word_count(f.read())
    print("%s — %d/%d chapters done (~%d words)"
          % (plan["title"], len(done), len(plan["chapters"]), words))
    if todo:
        nxt = todo[0]
        print("\nNEXT: Chapter %d — %s (%s.md)\nBRIEF: %s"
              % (nxt["n"], nxt["title"], nxt["slug"], nxt["brief"]))
    else:
        print("\nAll chapters written. Run: python3 scripts/bookfactory.py build")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "build":
        build()
    elif cmd == "cover":
        make_cover(load_plan(), os.path.join(DIST, "Honest-Sleep-Book-cover.jpg"))
        print("cover regenerated")
    else:
        status()

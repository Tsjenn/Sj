#!/usr/bin/env python3
"""Book factory 2: the Traditional-Chinese environment-design book.

    python3 scripts/bookfactory2.py status   # progress + next chapter brief
    python3 scripts/bookfactory2.py build    # EPUB + cover into dist/
    python3 scripts/bookfactory2.py cover    # regenerate the cover only
    python3 scripts/bookfactory2.py art      # regenerate chapter illustrations

Chapters live in bookfactory2/chapters/<slug>.md, planned in
bookfactory2/plan.json. Same markdown subset as bookfactory.py.
Every chapter gets one illustration: bookfactory2/art/<slug>.png,
embedded automatically after the chapter title at build time.

Platforms: Kobo Writing Life, Google Play Books, Gumroad. NOT Amazon
KDP — KDP does not support Chinese-language books.
"""

import json
import math
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory2")
CHAPTERS = os.path.join(BF, "chapters")
ART = os.path.join(BF, "art")
DIST = os.path.join(ROOT, "dist")

CJK_FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# consistent illustration palette
PAPER = (250, 247, 240)
INK = (43, 45, 52)
ACCENT = (214, 116, 60)
SOFT = (150, 152, 160)
GREEN = (94, 140, 106)


def load_plan():
    with open(os.path.join(BF, "plan.json")) as f:
        return json.load(f)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s


def md_to_xhtml(md):
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
body { font-family: "Noto Serif CJK TC", "PMingLiU", serif; line-height: 1.85; margin: 1em; }
h1 { font-size: 1.45em; line-height: 1.3; margin: 1.4em 0 0.8em; }
h2 { font-size: 1.12em; margin: 1.5em 0 0.5em; }
p { margin: 0 0 0.9em; }
ul { margin: 0 0 0.9em 1.2em; }
li { margin-bottom: 0.4em; }
figure { margin: 1.2em 0; text-align: center; }
figure img { max-width: 100%; }
figcaption { font-size: 0.82em; color: #666; margin-top: 0.4em; }
.tp { text-align: center; margin-top: 26%; }
.tp h1 { font-size: 2.0em; margin-bottom: 0.3em; }
.tp .sub { font-size: 1.0em; margin-bottom: 2.2em; color: #333; }
.tp .auth { font-size: 1.1em; }
.small { font-size: 0.85em; color: #444; }
"""

XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-Hant">
<head><title>%s</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>%s</body>
</html>"""


def char_count(md):
    return len(re.sub(r"[#*\-\s]", "", md))


def done_chapters(plan):
    out = []
    for ch in plan["chapters"]:
        path = os.path.join(CHAPTERS, ch["slug"] + ".md")
        if ch["status"] == "done" and os.path.exists(path):
            with open(path) as f:
                out.append((ch, f.read()))
    return out


# ------------------------------------------------------------------ fonts
def cjk(size):
    from PIL import ImageFont
    return ImageFont.truetype(CJK_FONT, size)


# ------------------------------------------------------------------ cover
def make_cover(plan, out_path):
    from PIL import Image, ImageDraw, ImageFilter

    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # warm wall gradient
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(250 - 16 * t), int(247 - 22 * t), int(240 - 30 * t)))

    # window with light falling in
    wx0, wy0, wx1, wy1 = W * 0.58, H * 0.07, W * 0.90, H * 0.30
    d.rectangle([wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14], fill=(226, 218, 202))
    d.rectangle([wx0, wy0, wx1, wy1], fill=(252, 232, 196))
    d.line([( (wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(226, 218, 202), width=12)
    d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=(226, 218, 202), width=12)
    beam = Image.new("RGB", (W, H), (0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(wx0, wy1), (wx1, wy1), (wx1 - W * 0.02, H * 0.62), (wx0 - W * 0.16, H * 0.62)],
               fill=(120, 100, 60))
    beam = beam.filter(ImageFilter.GaussianBlur(60))
    img = Image.blend(img, Image.blend(img, beam, 0.0), 1.0)
    img = Image.blend(img, beam, 0.18)
    d = ImageDraw.Draw(img)

    # floor line + simple chair and plant silhouettes
    fy = H * 0.62
    d.line([(0, fy), (W, fy)], fill=(214, 204, 186), width=8)
    cx = W * 0.72
    d.rectangle([cx, fy - 300, cx + 26, fy], fill=INK)                       # chair back
    d.rectangle([cx, fy - 150, cx + 210, fy - 124], fill=INK)                # seat
    d.rectangle([cx + 184, fy - 124, cx + 210, fy], fill=INK)                # front leg
    px = W * 0.14
    d.rectangle([px - 55, fy - 130, px + 55, fy], fill=(196, 120, 86))       # pot
    for ang in (-0.9, -0.45, 0, 0.45, 0.9):
        tipx = px + math.sin(ang) * 150
        tipy = fy - 130 - math.cos(ang) * 190
        d.line([(px, fy - 120), (tipx, tipy)], fill=GREEN, width=26)

    def centered(y, txt, f, fill):
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y), txt, font=f, fill=fill)

    # title: 環境 huge, 比意志力強 beneath — never break inside a word
    centered(H * 0.635, "環境", cjk(330), INK)
    centered(H * 0.635 + 400, "比意志力強", cjk(210), ACCENT)
    f_sub = cjk(62)
    centered(H * 0.878, "不靠自律，用房間改變", f_sub, (90, 92, 100))
    centered(H * 0.878 + 80, "習慣、專注與睡眠的實用指南", f_sub, (90, 92, 100))
    centered(H * 0.955, plan["author"], cjk(52), SOFT)

    img.save(out_path, "JPEG", quality=92)
    return out_path


# ------------------------------------------------------- chapter diagrams
def _canvas(w=1400, h=1000):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), PAPER)
    return img, ImageDraw.Draw(img)


def art_ch01():
    """Willpower drains through the day; the room never sleeps."""
    img, d = _canvas()
    W, H = img.size
    x0, y0, x1, y1 = 150, 120, W - 90, H - 200
    # axes
    d.line([(x0, y1), (x1, y1)], fill=INK, width=6)
    d.line([(x0, y0), (x0, y1)], fill=INK, width=6)
    d.text((x0 - 20, y1 + 30), "早上", font=cjk(44), fill=INK)
    d.text((x1 - 120, y1 + 30), "深夜", font=cjk(44), fill=INK)
    # willpower curve: high morning, sagging to night
    pts = []
    for i in range(101):
        t = i / 100
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0 - 60) * (t ** 1.6) + 40 * math.sin(t * 9) * t * 0.35
        pts.append((x, y + 40))
    d.line(pts, fill=SOFT, width=10, joint="curve")
    d.text((x0 + 60, y0 + 10), "你的意志力", font=cjk(52), fill=SOFT)
    # environment: flat strong line
    ey = y0 + (y1 - y0) * 0.55
    d.line([(x0, ey), (x1, ey)], fill=ACCENT, width=12)
    d.text((x1 - 480, ey - 80), "你的房間（全天不變）", font=cjk(52), fill=ACCENT)
    # caption zone
    d.text((x0, H - 130), "晚上十一點的你，拚不過白天的自己——但房間隨時都一樣強。",
           font=cjk(42), fill=INK)
    return img


def art_ch02():
    """Two cages: impoverished vs enriched environment."""
    img, d = _canvas()
    W, H = img.size

    def cage(x0, x1, label):
        y0, y1 = 220, 700
        d.rectangle([x0, y0, x1, y1], outline=INK, width=8)
        for bx in range(int(x0) + 60, int(x1), 90):
            d.line([(bx, y0), (bx, y1)], fill=(210, 205, 195), width=4)
        d.text((x0 + (x1 - x0) / 2 - len(label) * 26, y1 + 40), label,
               font=cjk(52), fill=INK)
        return y0, y1

    # left: empty cage, single mouse
    cage(110, 610, "貧乏環境")
    d.ellipse([320, 610, 400, 660], fill=SOFT)          # mouse body
    d.ellipse([390, 615, 425, 650], fill=SOFT)          # head
    d.line([(320, 640), (280, 620)], fill=SOFT, width=8)  # tail

    # right: enriched cage — wheel, ramp, two mice
    cage(790, 1290, "豐富環境")
    d.ellipse([840, 400, 1000, 560], outline=ACCENT, width=10)   # wheel
    for a in range(0, 360, 45):
        d.line([(920 + 78 * math.cos(math.radians(a)), 480 + 78 * math.sin(math.radians(a))),
                (920, 480)], fill=ACCENT, width=5)
    d.line([(1060, 690), (1240, 480)], fill=GREEN, width=14)     # ramp
    d.line([(1240, 480), (1285, 480)], fill=GREEN, width=14)
    d.ellipse([1080, 610, 1160, 660], fill=SOFT)
    d.ellipse([1150, 615, 1185, 650], fill=SOFT)
    d.ellipse([1180, 440, 1250, 485], fill=SOFT)                 # mouse on ramp
    d.ellipse([1240, 445, 1272, 477], fill=SOFT)

    d.text((110, H - 190), "動物研究是真的——但牠們是老鼠，不是你。",
           font=cjk(40), fill=INK)
    d.text((110, H - 130), "可信的部分：環境改變了牠們反覆做的事。",
           font=cjk(40), fill=INK)
    return img


ART_FUNCS = {"ch01": art_ch01, "ch02": art_ch02}


def build_art(only=None):
    os.makedirs(ART, exist_ok=True)
    made = []
    for slug, fn in ART_FUNCS.items():
        if only and slug != only:
            continue
        p = os.path.join(ART, slug + ".png")
        fn().save(p, "PNG")
        made.append(p)
    return made


# ------------------------------------------------------------------ build
def build():
    plan = load_plan()
    chs = done_chapters(plan)
    total = len(plan["chapters"])
    complete = len(chs) == total
    os.makedirs(DIST, exist_ok=True)

    build_art()
    cover_path = os.path.join(DIST, "Huanjing-Book-cover.jpg")
    make_cover(plan, cover_path)

    suffix = "" if complete else "-PREVIEW-%dof%d" % (len(chs), total)
    epub_path = os.path.join(DIST, "Huanjing-Bi-Yizhili-Qiang%s.epub" % suffix)

    uid = "urn:uuid:%08x-hjb2-4000-8000-%012x" % (abs(hash(plan["title"])) % 2**32,
                                                  abs(hash(plan["subtitle"])) % 2**48)
    manifest, spine, files, images = [], [], {}, {}

    tp = ('<div class="tp"><h1>%s</h1><p class="sub">%s</p><p class="auth">%s</p></div>'
          % (esc(plan["title"]), esc(plan["subtitle"]), esc(plan["author"])))
    files["titlepage.xhtml"] = XHTML % (esc(plan["title"]), tp)
    about = ("<h1>關於本書</h1>"
             "<p>本書提供的是關於環境與習慣的一般性資訊，不是醫療建議。若你正面對"
             "持續的失眠、情緒困擾或成癮問題，請尋求專業協助——那不是一個房間"
             "能解決的事，而承認這一點，正是這本書想守住的誠實。</p>"
             '<p class="small">更多誠實的工具與指南：tsjenn.github.io/Sj</p>')
    files["about.xhtml"] = XHTML % ("關於本書", about)

    toc_items = []
    for ch, md in chs:
        name = ch["slug"] + ".xhtml"
        body = md_to_xhtml(md)
        art_path = os.path.join(ART, ch["slug"] + ".png")
        if os.path.exists(art_path):
            fig = ('<figure><img src="art/%s.png" alt="%s"/>'
                   "<figcaption>%s</figcaption></figure>"
                   % (ch["slug"], esc(ch.get("art", "")), esc(ch.get("art", ""))))
            body = re.sub(r"(</h1>)", r"\1" + fig, body, count=1)
            images["art/%s.png" % ch["slug"]] = art_path
        files[name] = XHTML % (esc(ch["title"]), body)
        toc_items.append('<li><a href="%s">%s</a></li>' % (name, esc(ch["title"])))

    nav = ('<nav epub:type="toc" id="toc"><h1>目錄</h1><ol>'
           '<li><a href="titlepage.xhtml">書名頁</a></li>%s'
           '<li><a href="about.xhtml">關於本書</a></li></ol></nav>'
           % "".join(toc_items))
    files["nav.xhtml"] = XHTML % ("目錄", nav)

    order = ["titlepage.xhtml"] + [c["slug"] + ".xhtml" for c, _ in chs] + ["about.xhtml"]
    for i, name in enumerate(order):
        manifest.append('<item id="f%d" href="%s" media-type="application/xhtml+xml"/>' % (i, name))
        spine.append('<itemref idref="f%d"/>' % i)
    for i, name in enumerate(images):
        manifest.append('<item id="img%d" href="%s" media-type="image/png"/>' % (i, name))

    opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="uid">%s</dc:identifier>
<dc:title>%s</dc:title>
<dc:creator>%s</dc:creator>
<dc:language>zh-Hant</dc:language>
<meta property="dcterms:modified">2026-08-15T00:00:00Z</meta>
<meta name="cover" content="cover-img"/>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="css" href="style.css" media-type="text/css"/>
<item id="cover-img" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>
%s
</manifest>
<spine>%s</spine>
</package>""" % (uid, esc(plan["title"] + "：" + plan["subtitle"]), esc(plan["author"]),
                 "\n".join(manifest), "".join(spine))

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
        for name, path in images.items():
            z.write(path, "OEBPS/" + name)
        for name, content in files.items():
            z.writestr("OEBPS/" + name, content)

    chars = sum(char_count(md) for _, md in chs)
    print("Built %s (%d/%d chapters, ~%d chars) + cover %s"
          % (epub_path, len(chs), total, chars, cover_path))
    if complete:
        print("COMPLETE — ready for Kobo Writing Life / Google Play Books / Gumroad. "
              "Description and keywords are in bookfactory2/plan.json. "
              "NOT for Amazon KDP (no Chinese support).")
    return complete


def status():
    plan = load_plan()
    done = [c for c in plan["chapters"] if c["status"] == "done"]
    todo = [c for c in plan["chapters"] if c["status"] != "done"]
    chars = 0
    for ch in done:
        p = os.path.join(CHAPTERS, ch["slug"] + ".md")
        if os.path.exists(p):
            with open(p) as f:
                chars += char_count(f.read())
    print("%s — %d/%d chapters done (~%d chars)"
          % (plan["title"], len(done), len(plan["chapters"]), chars))
    if todo:
        nxt = todo[0]
        print("\nNEXT: Chapter %d — %s (%s.md)\nART: %s\nBRIEF: %s"
              % (nxt["n"], nxt["title"], nxt["slug"], nxt.get("art", ""), nxt["brief"]))
    else:
        print("\nAll chapters written. Run: python3 scripts/bookfactory2.py build")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "build":
        build()
    elif cmd == "cover":
        make_cover(load_plan(), os.path.join(DIST, "Huanjing-Book-cover.jpg"))
        print("cover regenerated")
    elif cmd == "art":
        for p in build_art():
            print("art:", p)
    else:
        status()

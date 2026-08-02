#!/usr/bin/env python3
"""Build 'Wildhaven Academy — Book One' as an illustrated Kindle EPUB.

Renders a flat-design illustration per chapter (14 total — one every
~8-10 formatted pages), a 1600x2560 cover, and packages a reflowable
EPUB 3 with styled typography.

  dist/Wildhaven-Academy-Book-One.epub
  marketing/novel/cover-1600x2560.jpg
  book/novel/*.png

Run:  python3 scripts/make_novel.py
"""

import os
import random
import zipfile

from PIL import Image, ImageDraw, ImageFont

from make_book import sky, sun, moon, hills, tree, fence, lamp, star_shape, critter, CRITTERS
import novel_content as N

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "book", "novel")
OUTDIR = os.path.join(ROOT, "marketing", "novel")
W, H = 1600, 1200

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def grad(d, w, h, top, bot):
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))


def skyline(d, w, h, base, color, win_color, seed=1, lit=0.5):
    rnd = random.Random(seed)
    x = 0
    while x < w:
        bw = rnd.randint(90, 220)
        bh = rnd.randint(int(h * 0.2), int(h * 0.55))
        d.rectangle([x, base - bh, x + bw, base], fill=color)
        for wy in range(base - bh + 30, base - 20, 46):
            for wx in range(x + 16, x + bw - 24, 40):
                if rnd.random() < lit:
                    d.rectangle([wx, wy, wx + 18, wy + 26], fill=win_color)
        x += bw + rnd.randint(10, 40)


def stars_(d, n=90, ymax=0.5, seed=3):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.randint(0, W), rnd.randint(0, int(H * ymax))
        r = rnd.choice([2, 3, 4])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 252, 230))


def scaled_hills(d, base_y, amp, color, seed):
    rnd = random.Random(seed)
    n = 8
    pts = [(0, H)]
    for i in range(n + 1):
        x = i * W / n
        y = base_y + (amp if i % 2 else -amp) * rnd.uniform(0.5, 1.0)
        pts.append((x, y))
    pts.append((W, H))
    d.polygon(pts, fill=color)


def il_city(d):
    grad(d, W, H, (16, 22, 40), (52, 60, 88))
    stars_(d, 40, 0.25)
    skyline(d, W, H, int(H * 0.92), (30, 36, 56), (140, 200, 230), 7, 0.7)
    # lone lit window with boy-glow
    d.rectangle([W * 0.46, H * 0.55, W * 0.54, H * 0.66], fill=(255, 216, 112))


def il_glitch(d):
    grad(d, W, H, (24, 28, 40), (40, 46, 64))
    d.rounded_rectangle([W * 0.2, H * 0.15, W * 0.8, H * 0.75], 30, fill=(16, 20, 30), outline=(90, 100, 130), width=8)
    for i in range(5):
        d.line([(W * 0.24, H * (0.25 + i * 0.09)), (W * 0.76, H * (0.25 + i * 0.09))], fill=(60, 70, 100), width=10)
    critter(d, W * 0.62, H * 0.55, 3.4, *CRITTERS["flufftail"])
    for gx in (0.3, 0.45, 0.7):
        d.rectangle([W * gx, H * 0.78, W * gx + 120, H * 0.79], fill=(126, 200, 80))


def il_door(d):
    grad(d, W, H, (36, 44, 66), (90, 110, 100))
    d.rectangle([0, 0, W, H], fill=None)
    # fence boards
    for x in range(0, W, 130):
        d.rectangle([x, H * 0.1, x + 110, H], fill=(120, 112, 104))
    # gap revealing valley
    d.rectangle([W * 0.42, H * 0.1, W * 0.58, H], fill=(159, 216, 239))
    scaled_hills(d, H * 0.55, 60, (104, 148, 84), 4)
    d.rectangle([0, H * 0.1, W * 0.42, H], fill=(120, 112, 104))
    d.rectangle([W * 0.58, H * 0.1, W, H], fill=(120, 112, 104))
    for x in range(0, W, 130):
        if x < W * 0.42 - 110 or x > W * 0.58:
            d.line([(x + 55, H * 0.1), (x + 55, H)], fill=(100, 92, 86), width=4)
    critter(d, W * 0.5, H * 0.8, 2.6, *CRITTERS["flufftail"])


def il_valley(d, seed=5, extra=None):
    sky_top, sky_bot = (126, 200, 235), (200, 235, 250)
    grad(d, W, H, sky_top, sky_bot)
    sun(d, W * 0.82, H * 0.16, 90)
    scaled_hills(d, H * 0.45, 90, (84, 128, 78), seed)
    scaled_hills(d, H * 0.65, 70, (104, 148, 84), seed + 2)
    for i in range(5):
        tree(d, 150 + i * 330, H * 0.6 + (i % 2) * 50, 1.4)
    if extra:
        extra(d)


def il_maro(d):
    def critters(dd):
        for x, nm in zip((0.2, 0.42, 0.62, 0.82), ("pebblit", "aquaphin", "mossback", "flufftail")):
            critter(dd, W * x, H * 0.82, 1.9, *CRITTERS[nm])
    il_valley(d, 5, critters)


def il_academy(d):
    def buildings(dd):
        for i, x in enumerate((0.2, 0.4, 0.6, 0.8)):
            bx, by = W * x, H * 0.72
            dd.rectangle([bx - 90, by - 90, bx + 90, by + 40], fill=(146, 110, 78))
            dd.polygon([(bx - 110, by - 90), (bx + 110, by - 90), (bx, by - 170)], fill=(104, 74, 52))
        critter(dd, W * 0.5, H * 0.86, 2.0, *CRITTERS["mossback"])
    il_valley(d, 9, buildings)


def il_listening(d):
    grad(d, W, H, (40, 52, 92), (232, 168, 117))
    stars_(d, 40, 0.3, 11)
    scaled_hills(d, H * 0.6, 70, (58, 96, 74), 6)
    critter(d, W * 0.5, H * 0.72, 3.2, *CRITTERS["flufftail"])
    for i, (x, y) in enumerate(((0.3, 0.42), (0.62, 0.34), (0.72, 0.5))):
        # music notes
        d.ellipse([W * x, H * y, W * x + 34, H * y + 26], fill=(255, 216, 112))
        d.line([(W * x + 32, H * y + 10), (W * x + 32, H * y - 60)], fill=(255, 216, 112), width=10)


def il_dimming(d):
    grad(d, W, H, (12, 20, 44), (46, 62, 110))
    stars_(d, 70, 0.5, 13)
    moon(d, W * 0.2, H * 0.18, 80)
    scaled_hills(d, H * 0.5, 90, (30, 44, 74), 8)
    scaled_hills(d, H * 0.7, 70, (44, 74, 66), 10)
    # drone
    d.ellipse([W * 0.72, H * 0.24, W * 0.78, H * 0.28], fill=(90, 96, 110))
    for ox in (-60, 60):
        d.line([(W * 0.75 + ox, H * 0.25), (W * 0.75 + ox, H * 0.22)], fill=(90, 96, 110), width=8)
        d.ellipse([W * 0.75 + ox - 30, H * 0.2, W * 0.75 + ox + 30, H * 0.23], fill=(120, 126, 140))
    d.ellipse([W * 0.745, H * 0.265, W * 0.755, H * 0.275], fill=(255, 80, 80))


def il_vex(d):
    grad(d, W, H, (12, 20, 44), (46, 62, 110))
    stars_(d, 90, 0.6, 17)
    moon(d, W * 0.78, H * 0.2, 100)
    d.rectangle([0, H * 0.78, W, H], fill=(60, 48, 40))
    critter(d, W * 0.32, H * 0.72, 2.4, *CRITTERS["mossback"])
    critter(d, W * 0.62, H * 0.72, 2.2, *CRITTERS["zephyrix"])


def il_city2(d):
    grad(d, W, H, (60, 70, 96), (150, 158, 178))
    skyline(d, W, H, int(H * 0.95), (84, 92, 116), (220, 230, 240), 21, 0.4)
    # the spire
    d.polygon([(W * 0.46, H * 0.95), (W * 0.54, H * 0.95), (W * 0.52, H * 0.06), (W * 0.48, H * 0.06)], fill=(120, 130, 160))
    for y in range(int(H * 0.12), int(H * 0.9), 60):
        d.rectangle([W * 0.485, y, W * 0.515, y + 26], fill=(200, 220, 240))


def il_lab(d):
    grad(d, W, H, (235, 238, 244), (250, 251, 253))
    for x in range(0, W, 200):
        d.rectangle([x, 0, x + 4, H], fill=(220, 224, 232))
    # cage
    d.rounded_rectangle([W * 0.3, H * 0.3, W * 0.7, H * 0.85], 24, outline=(120, 128, 144), width=10)
    critter(d, W * 0.5, H * 0.62, 2.8, *CRITTERS["emberling"])
    for x in (0.38, 0.46, 0.54, 0.62):
        d.line([(W * x, H * 0.3), (W * x, H * 0.85)], fill=(120, 128, 144), width=10)


def il_chase(d):
    grad(d, W, H, (30, 20, 26), (70, 30, 36))
    skyline(d, W, H, int(H * 0.98), (44, 30, 40), (255, 120, 110), 31, 0.5)
    for i, x in enumerate((0.2, 0.5, 0.8)):
        d.ellipse([W * x - 60, H * 0.14, W * x + 60, H * 0.26], outline=(255, 90, 80), width=12)
    critter(d, W * 0.5, H * 0.6, 2.6, *CRITTERS["emberling"])


def il_nocturnix(d):
    grad(d, W, H, (8, 14, 34), (36, 48, 90))
    stars_(d, 110, 0.5, 37)
    skyline(d, W, H, int(H * 0.98), (22, 28, 48), (110, 170, 210), 41, 0.35)
    critter(d, W * 0.5, H * 0.4, 5.2, *CRITTERS["nocturnix"])
    for r in (300, 420, 540):
        d.arc([W * 0.5 - r, H * 0.45 - r * 0.6, W * 0.5 + r, H * 0.45 + r * 0.6], 200, 340,
              fill=(143, 208, 255), width=8)


def il_newdoor(d):
    grad(d, W, H, (126, 200, 235), (200, 235, 250))
    for x in range(0, W, 130):
        d.rectangle([x, H * 0.12, x + 110, H * 0.9], fill=(150, 142, 132))
        d.line([(x + 55, H * 0.12), (x + 55, H * 0.9)], fill=(130, 122, 114), width=4)
    d.rectangle([0, H * 0.9, W, H], fill=(104, 148, 84))
    names = ["flufftail", "aquaphin", "emberling", "zephyrix", "nocturnix"]
    for x, nm in zip((0.15, 0.32, 0.5, 0.68, 0.85), names):
        critter(d, W * x, H * 0.86, 1.8, *CRITTERS[nm])
    # the faint song-door
    d.rounded_rectangle([W * 0.44, H * 0.22, W * 0.56, H * 0.9], 20, outline=(255, 216, 112), width=6)


def il_ending(d):
    grad(d, W, H, (12, 20, 44), (46, 62, 110))
    stars_(d, 150, 0.7, 43)
    moon(d, W * 0.5, H * 0.22, 110)
    scaled_hills(d, H * 0.6, 80, (44, 74, 66), 3)
    scaled_hills(d, H * 0.78, 60, (58, 96, 74), 5)
    d.rectangle([W * 0.3, H * 0.72, W * 0.7, H * 0.8], fill=(104, 74, 52))
    critter(d, W * 0.45, H * 0.7, 2.0, *CRITTERS["flufftail"])
    critter(d, W * 0.58, H * 0.7, 1.8, *CRITTERS["zephyrix"])


ILLUSTRATIONS = {
    "city": il_city, "glitch": il_glitch, "door": il_door, "maro": il_maro,
    "academy": il_academy, "listening": il_listening, "dimming": il_dimming,
    "vex": il_vex, "city2": il_city2, "lab": il_lab, "chase": il_chase,
    "nocturnix": il_nocturnix, "newdoor": il_newdoor, "ending": il_ending,
}


def cover():
    CW, CH = 1600, 2560
    img = Image.new("RGB", (CW, CH))
    d = ImageDraw.Draw(img)
    grad(d, CW, CH, (8, 14, 34), (46, 62, 110))
    rnd = random.Random(3)
    for _ in range(160):
        x, y = rnd.randint(0, CW), rnd.randint(0, int(CH * 0.55))
        r = rnd.choice([2, 3, 4, 6])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 252, 230))
    moon(d, CW * 0.82, CH * 0.12, 120)
    # nocturnix silhouette mid
    critter(d, CW * 0.5, CH * 0.4, 6.0, *CRITTERS["nocturnix"])
    # city skyline bottom
    skyline(d, CW, CH, int(CH * 0.86), (20, 26, 44), (120, 180, 215), 9, 0.5)
    # fence + green glow strip + flufftail
    d.rectangle([0, CH * 0.86, CW, CH * 0.885], fill=(126, 200, 80))
    for x in range(0, CW, 110):
        d.rectangle([x, CH * 0.87, x + 90, CH], fill=(70, 62, 58))
    critter(d, CW * 0.5, CH * 0.93, 3.0, *CRITTERS["flufftail"])
    ft = ImageFont.truetype(F_BOLD, 168)
    fs = ImageFont.truetype(F_BOLD, 74)
    fa = ImageFont.truetype(F_BOLD, 64)
    for off in (8, 4):
        d.text((CW // 2 + off, CH * 0.155 + off), "WILDHAVEN", font=ft, fill=(4, 8, 20), anchor="mm")
        d.text((CW // 2 + off, CH * 0.225 + off), "ACADEMY", font=ft, fill=(4, 8, 20), anchor="mm")
    d.text((CW // 2, CH * 0.155), "WILDHAVEN", font=ft, fill=(255, 250, 235), anchor="mm")
    d.text((CW // 2, CH * 0.225), "ACADEMY", font=ft, fill=(255, 216, 112), anchor="mm")
    d.text((CW // 2, CH * 0.29), "BOOK ONE · THE DOOR IN THE FENCE", font=fs, fill=(180, 200, 235), anchor="mm")
    d.text((CW // 2, CH * 0.975), "S. J. TANG", font=fa, fill=(255, 250, 235), anchor="mm")
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "cover-1600x2560.jpg")
    img.save(path, quality=92)
    img.resize((800, 1280)).save(os.path.join(TMP, "cover.jpg"), quality=88)
    print("cover:", path)


CSS = """
body { font-family: serif; line-height: 1.6; margin: 1em; }
h1 { font-family: sans-serif; font-size: 1.5em; text-align: center; margin: 1em 0 0.2em 0; }
.chnum { font-family: sans-serif; text-align: center; color: #B4652F; font-weight: bold;
         letter-spacing: 0.2em; margin-top: 2em; }
p { text-indent: 1.2em; margin: 0 0 0.2em 0; text-align: justify; }
p.first { text-indent: 0; }
img.illus { width: 100%; height: auto; margin: 0.5em 0 1em 0; border-radius: 6px; }
.center { text-align: center; }
.dedication { margin-top: 40%; text-align: center; font-style: italic; }
"""

XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>%s</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head><body>%s</body></html>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_epub():
    out = os.path.join(ROOT, "dist", "Wildhaven-Academy-Book-One.epub")
    manifest, spine = [], []
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>""")
        z.writestr("OEBPS/style.css", CSS)
        manifest.append('<item id="css" href="style.css" media-type="text/css"/>')

        z.write(os.path.join(TMP, "cover.jpg"), "OEBPS/images/cover.jpg")
        manifest.append('<item id="cover-img" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>')
        z.writestr("OEBPS/cover.xhtml", XHTML % ("Cover", '<div class="center"><img src="images/cover.jpg" alt="Wildhaven Academy — Book One cover" style="max-height:98vh"/></div>'))
        manifest.append('<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>')
        spine.append('<itemref idref="cover"/>')

        tp = ('<h1>%s</h1><p class="center">%s</p><p class="center">%s</p>'
              '<p class="dedication">%s</p>'
              '<p class="center" style="margin-top:3em; font-size:0.8em; color:#888;">'
              'Copyright © %s. All rights reserved. This is a work of fiction; all characters, '
              'creatures, places, and events are original creations. Text and illustrations created '
              'with the assistance of AI, directed and edited by the author.</p>'
              ) % (esc(N.TITLE), esc(N.SUBTITLE), esc(N.AUTHOR), esc(N.DEDICATION), esc(N.AUTHOR))
        z.writestr("OEBPS/title.xhtml", XHTML % ("Title", tp))
        manifest.append('<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>')
        spine.append('<itemref idref="title"/>')

        toc_items = []
        for i, (title, key, paras) in enumerate(N.CHAPTERS, 1):
            img_id = "il%d" % i
            fn = ILLUSTRATIONS[key]
            img = Image.new("RGB", (W, H))
            fn(ImageDraw.Draw(img))
            small = img.resize((1200, 900), Image.LANCZOS)
            import io
            buf = io.BytesIO()
            small.save(buf, "JPEG", quality=84)
            z.writestr("OEBPS/images/%s.jpg" % img_id, buf.getvalue(), zipfile.ZIP_STORED)
            manifest.append('<item id="%s" href="images/%s.jpg" media-type="image/jpeg"/>' % (img_id, img_id))
            body = ['<p class="chnum">CHAPTER %d</p>' % i, "<h1>%s</h1>" % esc(title),
                    '<img class="illus" src="images/%s.jpg" alt="%s"/>' % (img_id, esc(title))]
            for j, p in enumerate(paras):
                cls = ' class="first"' if j == 0 else ""
                body.append("<p%s>%s</p>" % (cls, esc(p)))
            ch_id = "ch%02d" % i
            z.writestr("OEBPS/%s.xhtml" % ch_id, XHTML % (title, "\n".join(body)))
            manifest.append('<item id="%s" href="%s.xhtml" media-type="application/xhtml+xml"/>' % (ch_id, ch_id))
            spine.append('<itemref idref="%s"/>' % ch_id)
            toc_items.append('<li><a href="%s.xhtml">%d. %s</a></li>' % (ch_id, i, esc(title)))
            print("chapter", i, title)

        z.writestr("OEBPS/about.xhtml", XHTML % ("About", "<h1>From the Author</h1><p class=\"first\">%s</p>" % esc(N.ABOUT)))
        manifest.append('<item id="about" href="about.xhtml" media-type="application/xhtml+xml"/>')
        spine.append('<itemref idref="about"/>')

        nav = ('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html>'
               '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
               '<head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1><ol>%s</ol></nav></body></html>'
               ) % "".join(toc_items)
        z.writestr("OEBPS/nav.xhtml", nav)
        manifest.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')

        opf = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bid">'
               '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
               '<dc:identifier id="bid">urn:uuid:wildhaven-academy-book-one</dc:identifier>'
               '<dc:title>%s — %s</dc:title><dc:creator>%s</dc:creator><dc:language>en</dc:language>'
               '<meta property="dcterms:modified">2026-08-02T00:00:00Z</meta>'
               '<meta name="cover" content="cover-img"/></metadata>'
               '<manifest>%s</manifest><spine>%s</spine></package>'
               ) % (esc(N.TITLE), esc(N.SUBTITLE), esc(N.AUTHOR), "".join(manifest), "".join(spine))
        z.writestr("OEBPS/content.opf", opf)
    words = sum(len(" ".join(p for p in paras).split()) for _, _, paras in N.CHAPTERS)
    print("EPUB:", out, os.path.getsize(out) // 1024, "KB |", len(N.CHAPTERS), "chapters |", words, "words")


if __name__ == "__main__":
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    cover()
    build_epub()

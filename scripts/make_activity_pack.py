#!/usr/bin/env python3
"""Build the Wildhaven Activity Pack (printable, A4).

16 pages: cover, 10 coloring pages (line art from critters2), 3
counting worksheets, 1 silhouette matching game, answer + license
page. Output: one print PDF + the coloring pages as loose PNGs.

  dist/Wildhaven-Activity-Pack.zip

Run:  python3 scripts/make_activity_pack.py
"""

import os
import random
import zipfile

from PIL import Image, ImageDraw, ImageFont

import critters2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "book", "activity")
W, H = 1240, 1754            # A4 at 150 dpi
INK = (62, 66, 80)
GOLD = (240, 198, 110)
CREAM = (253, 250, 244)

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_TITLE = ImageFont.truetype(F, 74)
F_H = ImageFont.truetype(F, 52)
F_TEXT = ImageFont.truetype(F, 34)
F_SMALL = ImageFont.truetype(F, 26)

NAMES = ["flufftail", "pebblit", "aquaphin", "emberling", "mossback",
         "bubbletide", "zephyrix", "cinderpup", "glimmerwing", "nocturnix"]

LICENSE = """WILDHAVEN ACTIVITY PACK — LICENSE

Print as many copies as you like for your own family or your own
classroom. Teachers: yes, the whole class is fine.

Please don't resell or redistribute the files themselves, or use the
characters in products you sell.

Questions? Reply to your order and we answer.
"""

_pages = []


def page(name):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    _pages.append((name, img))
    return img, d


def footer(d, label):
    d.text((W // 2, H - 46), "Wildhaven Activity Pack  ·  " + label,
           font=F_SMALL, fill=(150, 150, 156), anchor="mm")


def cover():
    img, d = page("00-cover")
    d.rectangle([0, 0, W, H], fill=CREAM)
    d.rectangle([0, 0, W, 26], fill=GOLD)
    d.rectangle([0, H - 26, W, H], fill=GOLD)
    d.text((W // 2, 210), "Wildhaven", font=F_TITLE, fill=INK, anchor="mm")
    d.text((W // 2, 310), "ACTIVITY PACK", font=F_H, fill=(180, 130, 60), anchor="mm")
    d.text((W // 2, 400), "Coloring · Counting · Matching", font=F_TEXT,
           fill=(120, 124, 138), anchor="mm")
    random.seed(7)
    spots = [(200, 640), (620, 560), (1020, 660), (330, 1000), (860, 1010),
             (580, 1330), (200, 1400), (1010, 1380)]
    for i, (x, y) in enumerate(spots):
        sp = NAMES[i % len(NAMES)]
        art = critters2.render(sp, 300)
        img.paste(art, (x - 150, y - 150), art)
    d.text((W // 2, H - 120), "Print at home · A4 · ages 3-7", font=F_TEXT,
           fill=(120, 124, 138), anchor="mm")


def coloring_pages():
    for sp in NAMES:
        img, d = page("color-" + sp)
        d.rectangle([40, 40, W - 40, H - 90], outline=(210, 210, 216), width=4)
        art = critters2.render(sp, 980, mode="lineart")
        img.paste(art, (W // 2 - 490, 200), art)
        d.text((W // 2, 130), sp.capitalize(), font=F_H, fill=INK, anchor="mm")
        ref = critters2.render(sp, 170)
        img.paste(ref, (W - 260, H - 320), ref)
        d.text((W - 175, H - 130), "color me like this,\nor invent your own!",
               font=F_SMALL, fill=(150, 150, 156), anchor="mm", align="center")
        footer(d, "coloring page")


COUNTS = [("emberling", 5, [4, 5, 6]), ("bubbletide", 7, [6, 7, 8]),
          ("flufftail", 4, [3, 4, 5])]


def counting_pages():
    for pi, (sp, n, options) in enumerate(COUNTS):
        img, d = page("count-%d-%s" % (pi + 1, sp))
        d.text((W // 2, 120), "How many %ss?" % sp.capitalize(),
               font=F_H, fill=INK, anchor="mm")
        d.text((W // 2, 190), "Count them, then circle the right number.",
               font=F_TEXT, fill=(120, 124, 138), anchor="mm")
        random.seed(100 + pi)
        placed = []
        art = critters2.render(sp, 240)
        tries = 0
        while len(placed) < n and tries < 400:
            tries += 1
            x = random.randint(160, W - 160)
            y = random.randint(380, H - 560)
            if all((x - px) ** 2 + (y - py) ** 2 > 270 ** 2 for px, py in placed):
                placed.append((x, y))
        # the page ASKS "how many" — a silent short-place would make the
        # printed answer key wrong, so this is a hard stop, not a warning
        assert len(placed) == n, "placed %d of %d %ss" % (len(placed), n, sp)
        for x, y in placed:
            img.paste(art, (x - 120, y - 120), art)
        cx = W // 2 - (len(options) - 1) * 130
        for o in options:
            d.ellipse([cx - 80, H - 400, cx + 80, H - 240],
                      outline=INK, width=5)
            d.text((cx, H - 320), str(o), font=F_TITLE, fill=INK, anchor="mm")
            cx += 260
        footer(d, "counting")


MATCH = ["pebblit", "zephyrix", "glimmerwing", "mossback", "cinderpup"]


def matching_page():
    img, d = page("match-shadows")
    d.text((W // 2, 120), "Who made that shadow?", font=F_H, fill=INK, anchor="mm")
    d.text((W // 2, 190), "Draw a line from each critter to its shadow.",
           font=F_TEXT, fill=(120, 124, 138), anchor="mm")
    random.seed(9)
    shuffled = MATCH[:]
    while True:
        random.shuffle(shuffled)
        if all(a != b for a, b in zip(shuffled, MATCH)):
            break
    y0, step = 380, 260
    for i, sp in enumerate(MATCH):
        art = critters2.render(sp, 220)
        img.paste(art, (170, y0 + i * step - 110), art)
    for i, sp in enumerate(shuffled):
        art = critters2.render(sp, 220, mode="silhouette")
        img.paste(art, (W - 390, y0 + i * step - 110), art)
    footer(d, "matching")
    return {MATCH[i]: shuffled.index(MATCH[i]) + 1 for i in range(len(MATCH))}


def answers_page(match_key):
    img, d = page("answers")
    d.text((W // 2, 140), "Answer key (for grown-ups)", font=F_H, fill=INK,
           anchor="mm")
    y = 300
    for (sp, n, _o) in COUNTS:
        d.text((W // 2, y), "How many %ss?  —  %d" % (sp.capitalize(), n),
               font=F_TEXT, fill=INK, anchor="mm")
        y += 70
    y += 40
    d.text((W // 2, y), "Shadows: " + "  ·  ".join(
        "%s → shadow %d" % (sp.capitalize(), pos)
        for sp, pos in match_key.items()), font=F_SMALL, fill=INK, anchor="mm")
    y += 140
    for line in LICENSE.strip().split("\n"):
        d.text((W // 2, y), line, font=F_SMALL, fill=(120, 124, 138), anchor="mm")
        y += 44
    footer(d, "answers + license")


def main():
    os.makedirs(TMP, exist_ok=True)
    cover()
    coloring_pages()
    counting_pages()
    key = matching_page()
    answers_page(key)

    pdf_path = os.path.join(TMP, "Wildhaven-Activity-Pack.pdf")
    imgs = [im for _n, im in _pages]
    imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:],
                 resolution=150.0)
    print("PDF: %d pages" % len(imgs))

    zpath = os.path.join(ROOT, "dist", "Wildhaven-Activity-Pack.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(pdf_path, "Wildhaven-Activity-Pack/Wildhaven-Activity-Pack.pdf")
        for name, im in _pages:
            if name.startswith("color-"):
                p = os.path.join(TMP, name + ".png")
                im.save(p)
                z.write(p, "Wildhaven-Activity-Pack/coloring-pages/%s.png"
                        % name.replace("color-", ""))
        z.writestr("Wildhaven-Activity-Pack/LICENSE.txt", LICENSE)
    print("zip:", zpath, os.path.getsize(zpath) // 1024, "KB")

    # preview sheet for listings
    prev = Image.new("RGB", (3 * 420 + 40, 600), (240, 238, 234))
    picks = [1, 11, 14]   # a coloring page, a counting page, the matching page
    for i, pi in enumerate(picks):
        t = _pages[pi][1].copy()
        t.thumbnail((410, 580))
        prev.paste(t, (10 + i * 430, 10))
    out = os.path.join(ROOT, "marketing", "activity-pack-preview.jpg")
    prev.save(out, quality=90)
    print("preview:", out)


if __name__ == "__main__":
    main()

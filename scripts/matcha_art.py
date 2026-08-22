#!/usr/bin/env python3
"""Original illustrations for the MATCHA book (bookfactory5).

One hero image per chapter (1200x780 PNG) in a consistent warm matcha
palette, plus the KDP cover (1600x2560 JPG). All art is parametric and
original — no photographs, no traced sources.

    python3 scripts/matcha_art.py         # render all chapter art
    python3 scripts/matcha_art.py cover   # cover only
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory5")
OUT = os.path.join(BF, "art")

DEEP = (62, 90, 58)
LEAF = (123, 160, 91)
LIGHT = (168, 198, 134)
CREAM = (247, 243, 232)
INK = (46, 53, 40)
GOLD = (201, 168, 76)
W, H = 1200, 780

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, sz):
    return ImageFont.truetype(path, sz)


def mixc(a, b, f):
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def canvas(caption):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.text((60, 44), caption.upper(), font=F(SANSB, 26), fill=DEEP)
    d.rectangle([60, 92, 300, 96], fill=GOLD)
    return img, d


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, name + ".png"))
    print("art:", name)


# ---------------------------------------------------------------- scenes

def chawan_top(d, cx, cy, r):
    """Bowl seen from above, matcha swirled inside."""
    d.ellipse([cx - r, cy - r * 0.86, cx + r, cy + r * 0.86], fill=DEEP)
    r2 = r * 0.9
    d.ellipse([cx - r2, cy - r2 * 0.86, cx + r2, cy + r2 * 0.86], fill=mixc(DEEP, INK, 0.25))
    r3 = r * 0.8
    d.ellipse([cx - r3, cy - r3 * 0.86, cx + r3, cy + r3 * 0.86], fill=LEAF)
    for i in range(4):                       # whisk swirl
        rr = r3 * (0.72 - i * 0.16)
        off = i * 0.9
        d.arc([cx - rr, cy - rr * 0.86 + 4, cx + rr, cy + rr * 0.86 + 4],
              20 + off * 40, 250 + off * 40, fill=mixc(LEAF, LIGHT, 0.6), width=10)
    for i in range(26):                      # crema specks
        a, rr = i * 2.4, r3 * (0.15 + (i * 37 % 60) / 100)
        d.ellipse([cx + math.cos(a) * rr - 4, cy + math.sin(a) * rr * 0.86 - 4,
                   cx + math.cos(a) * rr + 4, cy + math.sin(a) * rr * 0.86 + 4],
                  fill=mixc(LIGHT, CREAM, 0.35))


def chasen(d, cx, cy, s, color=DEEP):
    """Bamboo whisk, side view."""
    d.rounded_rectangle([cx - s * 0.08, cy - s, cx + s * 0.08, cy - s * 0.35],
                        radius=int(s * 0.06), fill=GOLD)
    for i in range(11):
        f = (i - 5) / 5
        x2 = cx + f * s * 0.5
        d.line([(cx + f * s * 0.07, cy - s * 0.36), (x2, cy)], fill=color, width=5)
        d.arc([min(cx + f * s * 0.07, x2) - 4, cy - 10, max(cx + f * s * 0.07, x2) + 4, cy + 14],
              0, 180, fill=color, width=4)


def chawan_side(d, cx, cy, s, tea=True):
    d.pieslice([cx - s, cy - s * 0.55, cx + s, cy + s * 0.75], 0, 180, fill=DEEP)
    d.ellipse([cx - s, cy - s * 0.18, cx + s, cy + s * 0.18], fill=mixc(DEEP, INK, 0.2))
    if tea:
        d.ellipse([cx - s * 0.88, cy - s * 0.14, cx + s * 0.88, cy + s * 0.14], fill=LEAF)
    d.rounded_rectangle([cx - s * 0.32, cy + s * 0.72, cx + s * 0.32, cy + s * 0.84],
                        radius=8, fill=mixc(DEEP, INK, 0.3))


def leaf_shape(d, cx, cy, s, ang, col=LEAF):
    pts = []
    for i in range(25):
        t = i / 24 * math.pi
        rr = s * math.sin(t)
        x = (t / math.pi - 0.5) * 2 * s
        pts.append((x, -rr * 0.42))
    pts += [(x, r_ * -1) for x, r_ in [(p[0], p[1]) for p in reversed(pts)]]
    rot = [(cx + px * math.cos(ang) - py * math.sin(ang),
            cy + px * math.sin(ang) + py * math.cos(ang)) for px, py in pts]
    d.polygon(rot, fill=col)
    d.line([rot[0], rot[24]], fill=mixc(col, INK, 0.35), width=4)


def steam(d, cx, cy, s):
    for k in range(3):
        pts = []
        for i in range(20):
            t = i / 19
            pts.append((cx + (k - 1) * s * 0.28 + math.sin(t * 5 + k) * s * 0.09,
                        cy - t * s * 0.9))
        d.line(pts, fill=mixc(LIGHT, CREAM, 0.4), width=7)


def glass_tall(d, cx, cy, s, layers, ice=True, straw=True):
    top, bot = cy - s, cy + s
    wl, wr = cx - s * 0.42, cx + s * 0.42
    n = len(layers)
    for i, col in enumerate(layers):
        y0 = top + (bot - top) * (i / n) + (8 if i else 26)
        y1 = top + (bot - top) * ((i + 1) / n)
        d.rectangle([wl + 6, y0, wr - 6, y1], fill=col)
    d.rounded_rectangle([wl, top, wr, bot], radius=18, outline=INK, width=6)
    if ice:
        for k in range(3):
            ix = cx - s * 0.22 + (k % 2) * s * 0.26
            iy = top + 40 + k * s * 0.3
            d.rounded_rectangle([ix, iy, ix + s * 0.26, iy + s * 0.22],
                                radius=8, outline=mixc(CREAM, INK, 0.25), width=5)
    if straw:
        d.line([(cx + s * 0.18, top - s * 0.34), (cx + s * 0.02, bot - 20)], fill=GOLD, width=13)


def mug(d, cx, cy, s, col=LEAF):
    d.rounded_rectangle([cx - s * 0.5, cy - s * 0.45, cx + s * 0.5, cy + s * 0.5],
                        radius=24, fill=DEEP)
    d.rectangle([cx - s * 0.42, cy - s * 0.36, cx + s * 0.42, cy - s * 0.1], fill=col)
    d.arc([cx + s * 0.4, cy - s * 0.25, cx + s * 0.85, cy + s * 0.28], -90, 90, fill=DEEP, width=16)
    steam(d, cx, cy - s * 0.5, s)


def arrow(d, x0, y, x1):
    d.line([(x0, y), (x1 - 14, y)], fill=INK, width=5)
    d.polygon([(x1, y), (x1 - 18, y - 9), (x1 - 18, y + 9)], fill=INK)


def process_boxes(d, labels, y=430):
    n = len(labels)
    bw = min(200, (W - 160 - (n - 1) * 46) // n)
    x = (W - (bw * n + 46 * (n - 1))) // 2
    f = F(SANSB, 22)
    for i, lb in enumerate(labels):
        d.rounded_rectangle([x, y - 60, x + bw, y + 60], radius=16,
                            fill=mixc(LIGHT, CREAM, 0.55), outline=DEEP, width=4)
        lines = lb.split("\n")
        for j, ln in enumerate(lines):
            tw = d.textlength(ln, font=f)
            d.text((x + bw / 2 - tw / 2, y - 14 * len(lines) + j * 28), ln, font=f, fill=INK)
        if i < n - 1:
            arrow(d, x + bw + 4, y, x + bw + 42)
        x += bw + 46


def curve(d, pts, col, width=8):
    d.line(pts, fill=col, width=width, joint="curve")


# ------------------------------------------------------------ generators

def g_chawan_hero(cap):
    img, d = canvas(cap)
    chawan_top(d, W // 2, 430, 270)
    chasen(d, W - 210, 430, 150)
    return img


def g_whisk_scene(cap):
    img, d = canvas(cap)
    chawan_side(d, W // 2 - 120, 470, 220)
    chasen(d, W // 2 + 260, 420, 190)
    return img


def g_leaf(cap, n=5):
    img, d = canvas(cap)
    d.arc([200, 300, 1000, 1000], 200, 340, fill=mixc(DEEP, GOLD, 0.3), width=9)
    for i in range(n):
        t = i / max(n - 1, 1)
        x = 280 + t * 640
        y = 430 - math.sin(t * math.pi) * 130
        leaf_shape(d, x, y, 90 + (i % 3) * 22, -0.6 + t * 1.2,
                   [LEAF, LIGHT, mixc(LEAF, DEEP, 0.4)][i % 3])
    return img


def g_process(cap, steps):
    img, d = canvas(cap)
    process_boxes(d, steps)
    return img


def g_drink(cap, kind):
    img, d = canvas(cap)
    if kind == "hot":
        mug(d, W // 2 - 160, 450, 260)
        chawan_side(d, W // 2 + 280, 500, 150)
    elif kind == "iced":
        glass_tall(d, W // 2 - 140, 440, 250, [mixc(CREAM, LIGHT, 0.3), LIGHT, LEAF])
        glass_tall(d, W // 2 + 200, 460, 210, [LEAF, mixc(LEAF, DEEP, 0.4)], straw=False)
    elif kind == "sparkle":
        glass_tall(d, W // 2, 440, 260, [mixc(CREAM, LIGHT, 0.25), mixc(LIGHT, LEAF, 0.5)], ice=False)
        for i in range(18):
            bx = W // 2 - 80 + (i * 53 % 160)
            by = 260 + (i * 97 % 320)
            d.ellipse([bx, by, bx + 10, by + 10], outline=CREAM, width=3)
    elif kind == "smoothie":
        glass_tall(d, W // 2, 440, 260, [mixc(LIGHT, CREAM, 0.2)], ice=False)
        d.ellipse([W // 2 - 90, 240, W // 2 - 30, 300], fill=GOLD)       # fruit
        leaf_shape(d, W // 2 + 60, 250, 60, -0.5)
    else:  # bowl
        chawan_side(d, W // 2, 470, 230)
        steam(d, W // 2, 320, 220)
    return img


def g_bake(cap, kind):
    img, d = canvas(cap)
    if kind == "cookies":
        for i in range(5):
            x, y = 260 + (i % 3) * 260, 360 + (i // 3) * 220
            d.ellipse([x - 90, y - 90, x + 90, y + 90], fill=mixc(LIGHT, LEAF, 0.5))
            for k in range(6):
                cxx, cyy = x - 50 + (k * 37 % 100), y - 50 + (k * 53 % 100)
                d.ellipse([cxx, cyy, cxx + 18, cyy + 18], fill=CREAM)
    elif kind == "cake":
        x, y = W // 2, 470
        for i, col in enumerate([LEAF, CREAM, LEAF, CREAM]):
            d.rectangle([x - 240, y - i * 52 - 52, x + 240, y - i * 52], fill=col if i % 2 == 0 else mixc(CREAM, GOLD, 0.2))
        d.rectangle([x - 240, y - 260, x + 240, y - 208], fill=mixc(LEAF, DEEP, 0.3))
        leaf_shape(d, x, y - 300, 70, 0.2)
    elif kind == "roll":
        x, y = W // 2, 430
        for r in range(150, 20, -34):
            d.arc([x - r, y - r, x + r, y + r], 0, 360,
                  fill=LEAF if (r // 34) % 2 == 0 else CREAM, width=34)
        d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=LEAF)
    else:  # frozen
        for i in range(3):
            x = 340 + i * 260
            d.rounded_rectangle([x - 70, 280, x + 70, 480], radius=60,
                                fill=[LEAF, LIGHT, mixc(LEAF, DEEP, 0.35)][i])
            d.rectangle([x - 10, 480, x + 10, 570], fill=GOLD)
    return img


def g_chart(cap, kind):
    img, d = canvas(cap)
    if kind == "curves":
        d.line([(140, 620), (1060, 620)], fill=INK, width=5)
        d.line([(140, 620), (140, 180)], fill=INK, width=5)
        cof = [(140 + t * 920, 620 - 340 * math.exp(-((t * 6 - 1.1) ** 2)) ) for t in
               [i / 60 for i in range(61)]]
        mat = [(140 + t * 920, 620 - 250 * (math.exp(-((t * 6 - 1.6) ** 2) / 6)) ) for t in
               [i / 60 for i in range(61)]]
        curve(d, cof, mixc(INK, GOLD, 0.5))
        curve(d, mat, LEAF)
        d.text((820, 240), "coffee", font=F(SANSB, 26), fill=mixc(INK, GOLD, 0.5))
        d.text((820, 430), "matcha", font=F(SANSB, 26), fill=DEEP)
        d.text((900, 640), "hours", font=F(SANS, 22), fill=INK)
    else:  # bars
        vals = [0.9, 0.65, 0.45, 0.3]
        labs = ["sip cafe", "good tin", "everyday", "culinary"]
        for i, v in enumerate(vals):
            x = 220 + i * 220
            d.rounded_rectangle([x, 620 - v * 380, x + 120, 620], radius=14,
                                fill=mixc(LEAF, DEEP, i * 0.16))
            d.text((x + 8, 640), labs[i], font=F(SANSB, 22), fill=INK)
        d.line([(160, 620), (1060, 620)], fill=INK, width=5)
    return img


def g_timeline(cap, nodes):
    img, d = canvas(cap)
    y = 420
    d.line([(120, y), (1080, y)], fill=mixc(DEEP, GOLD, 0.4), width=7)
    n = len(nodes)
    for i, lb in enumerate(nodes):
        x = 160 + i * (880 // max(n - 1, 1))
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=DEEP)
        f = F(SANSB, 22)
        ty = y - 90 if i % 2 == 0 else y + 46
        for j, ln in enumerate(lb.split("\n")):
            tw = d.textlength(ln, font=f)
            d.text((x - tw / 2, ty + j * 26), ln, font=f, fill=INK)
    return img


def g_map(cap):
    img, d = canvas(cap)
    d.polygon([(180, 520), (300, 300), (470, 260), (520, 420), (400, 600), (230, 620)],
              fill=mixc(LIGHT, CREAM, 0.5), outline=DEEP, width=5)
    d.polygon([(820, 300), (960, 260), (1040, 380), (980, 540), (860, 560), (810, 430)],
              fill=mixc(LIGHT, CREAM, 0.5), outline=DEEP, width=5)
    pts = [(500, 420 - int(math.sin(t * math.pi) * 130)) for t in [i / 20 for i in range(21)]]
    pts = [(500 + i * 17, p[1]) for i, p in enumerate(pts)]
    for i in range(0, 20, 2):
        d.line([pts[i], pts[i + 1]], fill=DEEP, width=6)
    d.polygon([(pts[-1][0] + 14, pts[-1][1]), (pts[-1][0] - 10, pts[-1][1] - 12),
               (pts[-1][0] - 10, pts[-1][1] + 12)], fill=DEEP)
    d.text((250, 650), "China", font=F(SANSB, 26), fill=DEEP)
    d.text((880, 590), "Japan", font=F(SANSB, 26), fill=DEEP)
    leaf_shape(d, 500 + 10 * 17, 260, 46, 0.4)
    return img


def g_tools(cap):
    img, d = canvas(cap)
    chawan_side(d, 260, 430, 150)
    chasen(d, 560, 430, 150)
    d.rounded_rectangle([740, 330, 790, 520], radius=18, fill=GOLD)       # chashaku
    d.ellipse([726, 300, 804, 350], fill=GOLD)
    d.ellipse([880, 330, 1080, 520], outline=DEEP, width=8)                # sifter
    for gx in range(900, 1070, 22):
        d.line([(gx, 350), (gx, 505)], fill=mixc(DEEP, CREAM, 0.5), width=3)
    f = F(SANSB, 22)
    for x, t in [(200, "chawan"), (505, "chasen"), (700, "chashaku"), (915, "sifter")]:
        d.text((x, 560), t, font=f, fill=INK)
    return img


def g_versus(cap):
    img, d = canvas(cap)
    mug(d, 330, 440, 240, col=mixc(INK, GOLD, 0.55))
    chawan_side(d, 850, 470, 200)
    steam(d, 850, 330, 190)
    f = F(SERIF, 44)
    d.text((300, 620), "coffee", font=f, fill=mixc(INK, GOLD, 0.5))
    d.text((790, 640), "matcha", font=f, fill=DEEP)
    d.text((575, 400), "vs", font=F(SERIF, 56), fill=GOLD)
    return img


# ---------------------------------------------------------------- wiring

ART = {
    "chawan-hero":  lambda c: g_chawan_hero(c),
    "song-whisk":   lambda c: g_whisk_scene(c),
    "journey-map":  lambda c: g_map(c),
    "ceremony-room": lambda c: g_drink(c, "bowl"),
    "timeline":     lambda c: g_timeline(c, ["Tang\ncakes", "Song\nwhisking", "1191\nEisai", "1500s\nRikyū", "1900s\nexport", "today\nlattes"]),
    "leaf-family":  lambda c: g_leaf(c, 5),
    "shade-field":  lambda c: g_process(c, ["full sun\n(sencha)", "3 weeks\nshade", "sweet\numami leaf"]),
    "harvest":      lambda c: g_process(c, ["pluck\nfirst flush", "steam\nsame day", "dry &\nde-stem", "tencha"]),
    "stone-mill":   lambda c: g_process(c, ["tencha\nflakes", "granite\nmill", "30 g\nper hour", "matcha"]),
    "grade-chart":  lambda c: g_chart(c, "bars"),
    "region-map":   lambda c: g_map(c),
    "storage":      lambda c: g_process(c, ["airtight\ntin", "cool &\ndark", "use in\n8 weeks"]),
    "molecule-bowl": lambda c: g_chawan_hero(c),
    "focus-curve":  lambda c: g_chart(c, "curves"),
    "leaf-cells":   lambda c: g_leaf(c, 3),
    "versus":       lambda c: g_versus(c),
    "gentle-care":  lambda c: g_drink(c, "bowl"),
    "latte-art":    lambda c: g_drink(c, "hot"),
    "supply-chain": lambda c: g_process(c, ["farm", "mill", "brand", "cafe", "your cup"]),
    "label-lens":   lambda c: g_chart(c, "bars"),
    "home-econ":    lambda c: g_chart(c, "bars"),
    "tools":        lambda c: g_tools(c),
    "usucha-steps": lambda c: g_process(c, ["sift\n2 g", "70-80°C\nwater", "whisk\nM then W", "drink\nnow"]),
    "hot-latte":    lambda c: g_drink(c, "hot"),
    "iced":         lambda c: g_drink(c, "iced"),
    "sparkling":    lambda c: g_drink(c, "sparkle"),
    "smoothie":     lambda c: g_drink(c, "smoothie"),
    "dessert-drink": lambda c: g_drink(c, "smoothie"),
    "seasons":      lambda c: g_leaf(c, 4),
    "evening":      lambda c: g_drink(c, "hot"),
    "troubleshoot": lambda c: g_process(c, ["too hot?\nbitter", "no sift?\nclumps", "old tin?\nflat"]),
    "baking-basics": lambda c: g_process(c, ["sift into\ndry mix", "protect\nfrom heat", "taste the\nbatter"]),
    "cookies":      lambda c: g_bake(c, "cookies"),
    "cakes":        lambda c: g_bake(c, "cake"),
    "chilled":      lambda c: g_bake(c, "cake"),
    "frozen":       lambda c: g_bake(c, "frozen"),
    "breakfast":    lambda c: g_bake(c, "cookies"),
    "pairing":      lambda c: g_whisk_scene(c),
    "home-ceremony": lambda c: g_chawan_hero(c),
    "glossary":     lambda c: g_leaf(c, 5),
}


def make_cover(out_path):
    CW, CH = 1600, 2560
    img = Image.new("RGB", (CW, CH), DEEP)
    d = ImageDraw.Draw(img)
    for y in range(CH):
        d.line([(0, y), (CW, y)], fill=mixc(mixc(DEEP, INK, 0.35), LEAF, y / CH * 0.55))
    # gold frame
    d.rectangle([70, 70, CW - 70, CH - 70], outline=GOLD, width=6)
    # title
    f = F(SERIF, 300)
    tw = d.textlength("MATCHA", font=f)
    d.text(((CW - tw) / 2 + 8, 268), "MATCHA", font=f, fill=(20, 26, 18))
    d.text(((CW - tw) / 2, 260), "MATCHA", font=f, fill=CREAM)
    fs = F(SANS, 54)
    sub = ["The Whole Story of the Whisked Leaf", "history · craft · science · 60+ recipes"]
    for i, ln in enumerate(sub):
        twl = d.textlength(ln, font=fs)
        d.text(((CW - twl) / 2, 660 + i * 78), ln, font=fs, fill=mixc(CREAM, GOLD, 0.35))
    # centerpiece bowl
    big = Image.new("RGB", (CW, CW), (0, 0, 0))
    bd = ImageDraw.Draw(big)
    for y in range(CW):
        bd.line([(0, y), (CW, y)], fill=mixc(mixc(DEEP, INK, 0.35), LEAF, (y + 900) / (CH) * 0.55))
    chawan_top(bd, CW // 2, CW // 2, 560)
    bowl = big.crop((CW // 2 - 620, CW // 2 - 560, CW // 2 + 620, CW // 2 + 560))
    img.paste(bowl, (CW // 2 - 620, 950))
    chasen_img = Image.new("RGBA", (500, 600), (0, 0, 0, 0))
    chasen(ImageDraw.Draw(chasen_img), 250, 520, 300, color=mixc(CREAM, GOLD, 0.25))
    img.paste(chasen_img, (CW - 560, 880), chasen_img)
    # author
    fa = F(SANSB, 66)
    author = "TANG SHIUAN JENN"
    twa = d.textlength(author, font=fa)
    d.rectangle([CW / 2 - 300, 2280, CW / 2 + 300, 2286], fill=GOLD)
    d.text(((CW - twa) / 2, 2330), author, font=fa, fill=CREAM)
    img.save(out_path, "JPEG", quality=92)
    print("cover:", out_path)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cover":
        make_cover(os.path.join(ROOT, "dist", "Matcha-cover.jpg"))
        return
    with open(os.path.join(BF, "plan.json")) as f:
        plan = json.load(f)
    for part in plan["parts"]:
        for ch in part["chapters"]:
            key = ch["art"]
            fn = ART.get(key)
            if fn is None:
                print("MISSING generator:", key)
                continue
            save(fn(ch["title"]), ch["id"])
    make_cover(os.path.join(ROOT, "dist", "Matcha-cover.jpg"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Amazon covers for 'Goodnight, Wildhaven'.

  marketing/book/cover-ebook-2550x2550.png      Kindle / listing front cover
  marketing/book/cover-paperback-wrap.png       KDP paperback wraparound
                                                (24-page, 8.5x8.5in, bleed)

Wrap math (KDP, white paper): spine = pages * 0.002252in; full width =
2*(trim + bleed) + spine; height = trim + 2*bleed; bleed = 0.125in @300dpi.

Run:  python3 scripts/make_book_cover.py
"""

import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_book as mb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "marketing", "book")
DPI = 300
TRIM = int(8.5 * DPI)          # 2550
BLEED = int(0.125 * DPI)       # 37
PAGES = 54
SPINE = int(PAGES * 0.002252 * DPI)  # ~16 px

F_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 230)
F_SUB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 92)
F_AUTHOR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 84)
F_BLURB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 72)


def draw_front(d, ox, size, with_author=True):
    """night park scene + title/subtitle, drawn into region [ox, ox+size)"""
    sc = size / mb.S  # scale factor relative to make_book's coordinate space

    def X(x): return ox + x * sc
    def Y(y): return y * sc

    random.seed(7)
    # sky handled by caller (full-canvas gradient); draw scene elements
    for _ in range(120):
        x = random.randint(0, size) + ox
        y = random.randint(0, int(size * 0.5))
        r = random.choice([3, 4, 4, 6, 8])
        d.ellipse([x - r * sc, y - r * sc, x + r * sc, y + r * sc], fill=(255, 252, 230))
    mbS = mb.S
    # moon
    cx, cy, r = X(mbS * 0.78), Y(mbS * 0.2), 150 * sc
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 240, 200))
    d.ellipse([cx - r + 18 * sc, cy - r + 18 * sc, cx + r - 18 * sc, cy + r - 18 * sc],
              fill=(255, 246, 218))

    def hills(base_y, amp, color, n, seed):
        rnd = random.Random(seed)
        pts = [(ox, Y(mbS))]
        for i in range(n + 1):
            x = ox + i * size / n
            y = Y(base_y + (amp if i % 2 else -amp) * rnd.uniform(0.5, 1.0))
            pts.append((x, y))
        pts.append((ox + size, Y(mbS)))
        d.polygon(pts, fill=color)

    hills(mbS * 0.62, 130, (44, 74, 66), 6, 3)
    hills(mbS * 0.74, 110, (58, 96, 74), 8, 5)
    hills(mbS * 0.86, 90, (84, 128, 78), 7, 9)
    for i in range(6):
        tx, ty, ts = X(200 + i * 420), Y(mbS * 0.72 + (i % 3) * 60), 1.4 * sc
        d.rectangle([tx - 8 * ts / sc * sc, ty, tx + 8 * ts / sc * sc, ty + 60 * ts], fill=(90, 66, 45))
        d.polygon([(tx - 60 * ts, ty + 10 * ts), (tx + 60 * ts, ty + 10 * ts),
                   (tx, ty - 130 * ts)], fill=(40, 72, 48))
    # fence
    wood = (122, 84, 52)
    fy = Y(mbS * 0.90)
    fs = 1.6 * sc
    for fx in range(0, size, int(150 * fs / sc * sc)):
        d.rectangle([ox + fx, fy - 60 * fs, ox + fx + 22 * fs, fy + 40 * fs], fill=wood)
    d.rectangle([ox, fy - 36 * fs, ox + size, fy - 16 * fs], fill=(138, 98, 62))
    # lamp
    lx, ly, ls = X(mbS * 0.2), Y(mbS * 0.9), 2.0 * sc
    d.rectangle([lx - 8 * ls, ly - 220 * ls, lx + 8 * ls, ly], fill=(58, 63, 69))
    d.ellipse([lx - 90 * ls, ly - 330 * ls, lx + 90 * ls, ly - 150 * ls], fill=(255, 240, 170))
    d.ellipse([lx - 44 * ls, ly - 280 * ls, lx + 44 * ls, ly - 192 * ls], fill=(255, 226, 130))
    # critters
    b, a, f = mb.CRITTERS["flufftail"]
    mb.critter(d, X(mbS * 0.60), Y(mbS * 0.84), 3.2 * sc, b, a, f, eyes_closed=True)
    b, a, f = mb.CRITTERS["nocturnix"]
    mb.critter(d, X(mbS * 0.82), Y(mbS * 0.86), 2.4 * sc, b, a, f)
    # title block
    cxm = ox + size / 2
    def title_text(y, text, fill, font):
        off = 10 * sc
        d.text((cxm + off, y + off), text, font=font, fill=(8, 12, 26), anchor="mm")
        d.text((cxm, y), text, font=font, fill=fill, anchor="mm")
    ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(230 * sc))
    fs2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(92 * sc))
    fa = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(84 * sc))
    title_text(Y(mbS * 0.115), "Goodnight,", (255, 250, 235), ft)
    title_text(Y(mbS * 0.225), "Wildhaven", (255, 216, 112), ft)
    d.text((cxm, Y(mbS * 0.31)), "A Bedtime Story from the Creature Park",
           font=fs2, fill=(214, 224, 244), anchor="mm")
    if with_author:
        d.text((cxm, Y(mbS * 0.965)), "S. J. TANG", font=fa, fill=(255, 250, 235), anchor="mm")


def night_gradient(d, w, h):
    top, bot = (12, 20, 44), (46, 62, 110)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)],
               fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))


def ebook_cover():
    img = Image.new("RGB", (TRIM, TRIM))
    d = ImageDraw.Draw(img)
    night_gradient(d, TRIM, TRIM)
    draw_front(d, 0, TRIM)
    path = os.path.join(OUT, "cover-ebook-2550x2550.png")
    img.save(path, dpi=(DPI, DPI))
    print("ebook cover:", path)


def wrap_cover():
    W = 2 * (TRIM + BLEED) + SPINE
    H = TRIM + 2 * BLEED
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    night_gradient(d, W, H)

    # ---- back cover (left panel) ----
    back_x0 = 0
    back_w = TRIM + BLEED
    cx = back_x0 + back_w // 2
    random.seed(21)
    for _ in range(90):
        x, y = random.randint(back_x0, back_x0 + back_w), random.randint(0, int(H * 0.55))
        r = random.choice([3, 4, 6])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 252, 230))
    blurb = [
        "When the sun slips down behind the hill,",
        "the keeper walks from gate to den to say",
        "goodnight to every creature in the park -",
        "from Flufftail in the meadow to Nocturnix",
        "on the farthest, starriest hill.",
        "",
        "A gentle rhyming bedtime story for little",
        "dreamers aged 2 to 6, from the world of",
        "the Wildhaven games.",
    ]
    y = int(H * 0.18)
    for line in blurb:
        d.text((cx, y), line, font=F_BLURB, fill=(226, 232, 246), anchor="mm")
        y += 108
    # a sleeping critter above the barcode-safe zone
    b, a, f = mb.CRITTERS["mossback"]
    mb.critter(d, back_x0 + back_w * 0.32, H * 0.78, 2.2, b, a, f, eyes_closed=True)
    # keep KDP barcode area clear: 2in x 1.2in at bottom-right of back panel
    # (drawn nothing there on purpose)

    # ---- spine (blank-safe: <79 pages means no spine text allowed) ----
    d.rectangle([back_w, 0, back_w + SPINE, H], fill=(16, 24, 50))

    # ---- front cover (right panel) ----
    front_x0 = back_w + SPINE
    draw_front(d, front_x0 + BLEED, TRIM)

    path = os.path.join(OUT, "cover-paperback-wrap.png")
    img.save(path, dpi=(DPI, DPI))
    print("wrap cover:", path, f"{W}x{H}px ({PAGES}-page spine)")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ebook_cover()
    wrap_cover()

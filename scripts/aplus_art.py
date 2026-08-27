#!/usr/bin/env python3
"""Amazon A+ Content modules for THE SILICON LEDGER.

    python3 scripts/aplus_art.py

A+ Content is free, most self-published authors skip it, and it is the
one lever that improves how many visitors buy rather than how many
arrive. Sizes follow Amazon's standard module specs.

Output: marketing/aplus/*.jpg
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "marketing", "aplus")

INK = (10, 10, 14)
WARM = (26, 18, 12)
COPPER = (196, 120, 58)
COPPER_HI = (240, 185, 106)
CREAM = (242, 239, 233)
STEEL = (150, 160, 176)


def f(sz, bold=True):
    p = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % (
        "Bold" if bold else "Regular")
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ground(w, h):
    im = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(INK, WARM, (y / h) ** 1.8))
    return im, d


def wrap(d, text, font, width):
    words, lines, line = text.split(), [], ""
    for wd in words:
        t = (line + " " + wd).strip()
        if d.textlength(t, font=font) <= width:
            line = t
        else:
            lines.append(line)
            line = wd
    if line:
        lines.append(line)
    return lines


def header():
    """Standard Image Header with Text — 970 x 600."""
    W, H = 970, 600
    im, d = ground(W, H)
    # copper rule down the left, echoing the cover's substrate
    d.rectangle([0, 0, 10, H], fill=COPPER)
    x = 62
    d.text((x, 78), "IN A SINGLE DAY,", font=f(46), fill=STEEL)
    d.text((x, 136), "ONE COMPANY LOST", font=f(52), fill=CREAM)
    d.text((x, 200), "589 BILLION DOLLARS.", font=f(52), fill=COPPER_HI)
    d.rectangle([x, 288, x + 120, 294], fill=COPPER)
    body = ("No factory closed. No product failed. Nothing physical changed. "
            "That is what a market capitalisation actually is — a price, not a fact.")
    y = 330
    for ln in wrap(d, body, f(27, False), W - x - 70):
        d.text((x, y), ln, font=f(27, False), fill=(198, 206, 218))
        y += 40
    d.text((x, y + 26), "Nvidia, 27 January 2025. Reported by CNBC and Bloomberg.",
           font=f(21, False), fill=(126, 134, 148))
    im.save(os.path.join(OUT, "01-header-970x600.jpg"), "JPEG", quality=94)


def tile(name, kicker, headline, body, foot):
    """Standard Three Images with Text — 300 x 300 each."""
    W = H = 300
    im, d = ground(W, H)
    d.rectangle([0, 0, W, 6], fill=COPPER)
    d.text((26, 30), kicker, font=f(17), fill=COPPER_HI)
    y = 62
    for ln in wrap(d, headline, f(28), W - 52):
        d.text((26, y), ln, font=f(28), fill=CREAM)
        y += 34
    y += 12
    for ln in wrap(d, body, f(17, False), W - 52):
        d.text((26, y), ln, font=f(17, False), fill=(186, 194, 208))
        y += 25
    d.text((26, H - 40), foot, font=f(15, False), fill=(120, 128, 142))
    im.save(os.path.join(OUT, name), "JPEG", quality=94)


def banner():
    """Standard Image & Light Text overlay — 970 x 300."""
    W, H = 970, 300
    im, d = ground(W, H)
    d.rectangle([0, H - 8, W, H], fill=COPPER)
    t = "77 chapters. Every figure dated and sourced."
    d.text(((W - d.textlength(t, font=f(44))) / 2, 96), t, font=f(44), fill=CREAM)
    t2 = "No price targets. No predictions. No advice."
    d.text(((W - d.textlength(t2, font=f(30, False))) / 2, 162), t2,
           font=f(30, False), fill=COPPER_HI)
    im.save(os.path.join(OUT, "05-banner-970x300.jpg"), "JPEG", quality=94)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    header()
    tile("02-tile-a-300x300.jpg", "THE QUESTION", "Why is Nvidia worth this much?",
         "Almost nobody can answer it in accounting terms. This book does, "
         "from the filings.", "Part II — The Silicon Layer")
    tile("03-tile-b-300x300.jpg", "THE ONE NOBODY WRITES", "Profit is partly an assumption.",
         "How long a server lasts moves billions of reported profit without "
         "moving a cent of cash.", "Chapter 32 — Depreciation")
    tile("04-tile-c-300x300.jpg", "THE MAP", "Who owns whom.",
         "Two rival clouds funding the same lab. A supplier holding equity in "
         "its own customers. Drawn once, dated.", "Part VI — The Web of Ownership")
    banner()
    print("A+ modules ->", OUT)
    for fn in sorted(os.listdir(OUT)):
        print("  ", fn)

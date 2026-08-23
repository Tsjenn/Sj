#!/usr/bin/env python3
"""Cover and chapter diagrams for THE FOUR LAYERS (bookfactory8).

    python3 scripts/layers_art.py          # chapter diagrams
    python3 scripts/layers_art.py cover    # dist/The-Four-Layers-cover.jpg

Diagrams reuse the engine written for the AI book (scripts/ai_art.py) so
the two titles look like they came from the same desk. The cover is its
own design: the four layers of the stack, rendered as strata, lit from
the bottom because that is where the value sits.
"""

import json
import math
import os
import sys

import random
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory8")
OUT = os.path.join(BF, "art")

CW, CH = 1600, 2560


def font(sz, bold=False, sans=True):
    if sans:
        c = ["/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
             "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"
             % ("Bold" if bold else "Regular")]
    else:
        c = ["/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf"
             % ("Bold" if bold else "Regular")]
    for p in c:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def tracked(d, text, f, cx, y, fill, track=0):
    ws = [d.textlength(c, font=f) for c in text]
    x = cx - (sum(ws) + track * (len(text) - 1)) / 2
    for c, w in zip(text, ws):
        d.text((x, y), c, font=f, fill=fill)
        x += w + track


# --- palette: near-black, copper, steel, cream. Two colours and a neutral.
INK      = (8, 8, 11)
INK_WARM = (20, 14, 11)
COPPER   = (196, 120, 58)
COPPER_HI= (240, 185, 106)
STEEL    = (152, 166, 184)
CREAM    = (242, 239, 233)


def _cover_font(sz, bold=True):
    """Cover type: Liberation Sans has tighter, more modern caps than DejaVu."""
    c = ["/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"
         % ("Bold" if bold else "Regular"),
         "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")]
    for p in c:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def _cross_section(im, x0, y0, x1, y1, rnd):
    """A chip's metallisation stack, seen edge-on.

    Four strata of interconnect over a substrate. Metal runs sit at several
    sub-levels within each stratum; vias drop between them. Density and
    warmth rise downward, because that is where the book says the value is.
    """
    d = ImageDraw.Draw(im)
    W_ = x1 - x0
    # stratum heights: the lower ones are thicker, as real metal stacks are
    weights = [0.17, 0.20, 0.26, 0.37]
    tops, y = [], y0
    for w in weights:
        h = (y1 - y0) * w
        tops.append((y, y + h))
        y += h

    for i, (ty, by) in enumerate(tops):
        t = i / (len(tops) - 1)                      # 0 at the top
        base = lerp(STEEL, COPPER, t ** 1.25)
        hi = lerp(lerp(STEEL, CREAM, 0.30), COPPER_HI, t ** 1.1)
        rows = 4 + i * 2                                  # lower strata are busier
        density = 0.62 + 0.32 * t
        gap = (by - ty) / (rows + 1)

        for r in range(rows):
            ry = ty + gap * (r + 1)
            x = x0 + rnd.randint(0, 70)
            while x < x1 - 40:
                run = int(rnd.randint(90, 360) * (0.8 + 0.6 * t))
                run = min(run, int(x1 - x))
                if rnd.random() < density:
                    th = 4 + i * 2
                    d.rectangle([x, ry, x + run, ry + th], fill=base)
                    # a lit top edge so the metal reads as metal
                    d.rectangle([x, ry, x + run, ry + 1], fill=hi)
                    # vias: short verticals connecting down a sub-level
                    if rnd.random() < 0.34 and r < rows - 1:
                        vx = x + rnd.randint(8, max(9, run - 8))
                        d.rectangle([vx, ry, vx + th, ry + gap], fill=base)
                    if rnd.random() < 0.16:
                        vx = x + rnd.randint(4, max(5, run - 4))
                        d.rectangle([vx - 1, ry - 6, vx + th + 1, ry + th + 6], fill=hi)
                x += run + rnd.randint(16, 58)

        # the oxide line between strata
        if i < len(tops) - 1:
            d.rectangle([x0, by - 2, x1, by], fill=lerp(INK, base, 0.32))

    # substrate: the solid floor everything is built on
    sy = y1 + 10
    d.rectangle([x0, sy, x1, sy + 26], fill=COPPER)
    d.rectangle([x0, sy, x1, sy + 3], fill=COPPER_HI)


def make_cover(path):
    im = Image.new("RGB", (CW, CH), INK)
    d = ImageDraw.Draw(im)

    # ground: black, warming very slightly toward the substrate
    for y in range(CH):
        d.line([(0, y), (CW, y)], fill=lerp(INK, INK_WARM, (y / CH) ** 2.4))

    # --- the cross-section, drawn oversized then downsampled for fine detail
    S = 2
    x0, x1 = 150, CW - 150
    ty, by = 1252, 2214
    tile = Image.new("RGB", ((x1 - x0) * S, (by - ty) * S), (0, 0, 0))
    _cross_section(tile, 0, 0, (x1 - x0) * S, (by - ty) * S - 40 * S,
                   random.Random(20260823))
    tile = tile.resize((x1 - x0, by - ty), Image.LANCZOS)
    # composite as light: black stays black, metal glows
    im.paste(ImageChops.lighter(im.crop((x0, ty, x1, by)), tile), (x0, ty))

    # a warm bloom rising off the substrate
    glow = Image.new("L", (CW, CH), 0)
    gd = ImageDraw.Draw(glow)
    for i in range(300, 0, -3):
        gd.ellipse([CW / 2 - 900, by - i * 1.15, CW / 2 + 900, by + i * 0.5],
                   fill=int(200 * (1 - i / 300) ** 2.2))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    im = Image.composite(Image.new("RGB", (CW, CH), (150, 84, 34)), im, glow)
    d = ImageDraw.Draw(im)

    # --- title
    cx = CW // 2
    tracked(d, "THE", _cover_font(64, False), cx, 372, (150, 158, 170), track=38)

    for j, word in enumerate(["FOUR", "LAYERS"]):
        sz = 300
        while sz > 120:
            f = _cover_font(sz, True)
            if d.textlength(word, font=f) + 4 * (len(word) - 1) <= CW - 220:
                break
            sz -= 6
        tracked(d, word, f, cx, 486 + j * 288, CREAM, track=4)

    d.rectangle([cx - 130, 1104, cx + 130, 1109], fill=COPPER_HI)

    f = _cover_font(40, False)
    sub = "Silicon, capital, and who owns artificial intelligence"
    while d.textlength(sub, font=f) > CW - 240:
        f = _cover_font(f.size - 2, False)
    d.text((cx - d.textlength(sub, font=f) / 2, 1160), sub, font=f, fill=(168, 176, 188))

    # --- author, on a plate lifted just clear of the substrate
    d.rectangle([0, 2318, CW, CH], fill=(6, 6, 8))
    d.rectangle([0, 2318, CW, 2322], fill=COPPER)
    fa = _cover_font(78, True)
    tracked(d, "TANG SHIUAN JENN", fa, cx, 2378, CREAM, track=9)
    fb = _cover_font(34, False)
    b = "CHARTERED ACCOUNTANT"
    tracked(d, b, fb, cx, 2482, (146, 154, 166), track=7)

    im.save(path, "JPEG", quality=95)
    print("cover ->", path)


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import ai_art
    plan = json.load(open(os.path.join(BF, "plan.json")))
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for part in plan["parts"]:
        for ch in part["chapters"]:
            spec = ch["art"]
            im, d = ai_art.canvas(spec["title"])
            ai_art.TYPES[spec["type"]](d, spec["labels"])
            im.save(os.path.join(OUT, ch["id"] + ".png"), optimize=True)
            n += 1
    print("rendered %d diagrams -> %s" % (n, OUT))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cover":
        os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
        make_cover(os.path.join(ROOT, "dist", "The-Four-Layers-cover.jpg"))
    else:
        main()

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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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


# The four strata, top of the stack first. Luminosity rises downward
# because the money has been moving down, not up.
LAYERS = [
    ("APPLICATION", "where the user pays",      (58, 74, 104), (74, 96, 134)),
    ("MODEL",       "where intelligence is made",(52, 96, 122), (72, 130, 162)),
    ("COMPUTE",     "where it runs",             (48, 118, 122), (70, 158, 162)),
    ("SILICON",     "where it is possible",      (168, 108, 40), (232, 168, 66)),
]


def make_cover(path):
    im = Image.new("RGB", (CW, CH), (8, 10, 16))
    d = ImageDraw.Draw(im)

    # ground: near-black at the top, warming faintly toward the base
    for y in range(CH):
        t = (y / CH) ** 1.5
        d.line([(0, y), (CW, y)], fill=lerp((7, 9, 15), (26, 19, 13), t))

    # --- the strata
    top, gap = 1232, 26
    hgt = 214
    glow = Image.new("L", (CW, CH), 0)
    gd = ImageDraw.Draw(glow)

    for i, (name, sub, c0, c1) in enumerate(LAYERS):
        y0 = top + i * (hgt + gap)
        y1 = y0 + hgt
        x0, x1 = 118, CW - 118
        # slab, lit from its own top edge
        for y in range(y0, y1):
            k = (y - y0) / hgt
            d.line([(x0, y), (x1, y)], fill=lerp(c1, c0, k ** 0.6))
        # bright leading edge
        d.rectangle([x0, y0, x1, y0 + 5], fill=lerp(c1, (255, 255, 255), 0.55))
        # circuit traces inside the slab
        for t in range(16):
            tx = x0 + 40 + ((t * 173) % (x1 - x0 - 90))
            ty = y0 + 26 + ((t * 61) % (hgt - 60))
            ln = 30 + (t * 37) % 90
            col = lerp(c1, (255, 255, 255), 0.22)
            if t % 2:
                d.line([(tx, ty), (tx + ln, ty)], fill=col, width=3)
                d.ellipse([tx + ln - 4, ty - 4, tx + ln + 4, ty + 4], fill=col)
            else:
                d.line([(tx, ty), (tx, ty + min(46, ln))], fill=col, width=3)
        # the bottom layer casts light upward
        if i == len(LAYERS) - 1:
            gd.rectangle([x0 - 60, y0 - 130, x1 + 60, y1 + 90], fill=120)

        f = font(40, True)
        d.text((x0 + 34, y0 + 46), name, font=f,
               fill=(255, 255, 255) if i == 3 else (226, 234, 244), anchor="lm")
        f2 = font(27)
        d.text((x0 + 34, y0 + 108), sub, font=f2,
               fill=lerp(c1, (255, 255, 255), 0.62), anchor="lm")
        f3 = font(60, True)
        d.text((x1 - 34, y0 + hgt / 2), "0%d" % (i + 1), font=f3,
               fill=lerp(c1, (255, 255, 255), 0.30), anchor="rm")

    glow = glow.filter(ImageFilter.GaussianBlur(110))
    im = Image.composite(Image.new("RGB", (CW, CH), (150, 96, 34)), im, glow)
    d = ImageDraw.Draw(im)

    # a few motes rising off the hot layer
    for i in range(70):
        x = 150 + (i * 271) % (CW - 300)
        y = 1060 + (i * 137) % 700
        s = 2 + i % 3
        d.ellipse([x, y, x + s, y + s], fill=(196, 150, 92))

    # --- title
    cx = CW // 2
    tracked(d, "THE", font(72, False), cx, 340, (196, 206, 222), track=30)
    for j, word in enumerate(["FOUR", "LAYERS"]):
        sz = 268
        while sz > 100:
            f = font(sz, True)
            if d.textlength(word, font=f) + 8 * (len(word) - 1) <= CW - 240:
                break
            sz -= 6
        tracked(d, word, f, cx, 470 + j * 268, (245, 247, 250), track=8)

    d.rectangle([cx - 190, 1046, cx + 190, 1052], fill=(232, 168, 66))
    f = font(38)
    for j, line in enumerate(["Silicon, capital, and the companies",
                              "that own artificial intelligence"]):
        w = d.textlength(line, font=f)
        d.text((cx - w / 2, 1096 + j * 52), line, font=f, fill=(198, 210, 226))

    # --- author
    d.rectangle([0, 2318, CW, CH], fill=(10, 12, 18))
    d.rectangle([0, 2318, CW, 2325], fill=(232, 168, 66))
    fa = font(80, True)
    tracked(d, "TANG SHIUAN JENN", fa, cx, 2368, (255, 255, 255), track=8)
    fb = font(38)
    b = "Chartered Accountant"
    d.text((cx - d.textlength(b, font=fb) / 2, 2474), b, font=fb, fill=(168, 186, 208))

    im.save(path, "JPEG", quality=94)
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

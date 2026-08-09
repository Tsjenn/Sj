#!/usr/bin/env python3
"""Render the Wildhaven soundtrack album cover at streaming resolution.

Spotify/Apple (via any distributor) require square art >= 3000x3000. The
original 1400px cover was drawn inline in a past session; this recreates the
same flat-art design at full size so it stays reproducible.

    python3 scripts/make_album_cover.py
      -> marketing/wildhaven/album-cover-3000.jpg
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

S = 3000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "marketing", "wildhaven", "album-cover-3000.jpg")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)

    # night-to-dusk gradient sky
    top, mid, low = (24, 32, 60), (105, 84, 84), (232, 164, 106)
    horizon = int(S * 0.62)
    for y in range(S):  # paint past the horizon; land layers overdraw it
        t = min(1.0, y / horizon)
        c = lerp(top, mid, t / 0.55) if t < 0.55 else lerp(mid, low, (t - 0.55) / 0.45)
        d.line([(0, y), (S, y)], fill=c)

    rng = random.Random(20260802)
    for _ in range(160):
        x, y = rng.randrange(S), rng.randrange(int(horizon * 0.85))
        r = rng.choice((3, 3, 4, 5))
        d.ellipse([x, y, x + r, y + r], fill=(255, 255, 255))

    # moon
    mx, my, mr = int(S * 0.68), int(S * 0.36), int(S * 0.058)
    d.ellipse([mx - mr - 14, my - mr - 14, mx + mr + 14, my + mr + 14], fill=(247, 233, 190))
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(252, 244, 212))

    # mountain layers
    def ridge(base_y, amp, col, seed, peaks=6):
        r = random.Random(seed)
        xs = [int(i * S / peaks) for i in range(peaks + 1)]
        pts = [(0, S)]
        for i, x in enumerate(xs):
            pts.append((x, base_y + (-amp if i % 2 else int(amp * r.uniform(0.1, 0.6)))))
        pts.append((S, S))
        d.polygon(pts, fill=col)

    ridge(int(S * 0.66), int(S * 0.075), (58, 96, 74), 7)
    ridge(int(S * 0.72), int(S * 0.06), (72, 118, 84), 12, peaks=5)

    # ground
    d.rectangle([0, int(S * 0.80), S, S], fill=(106, 165, 92))
    d.polygon([(0, int(S * 0.86)), (int(S * 0.5), int(S * 0.79)),
               (S, int(S * 0.87)), (S, S), (0, S)], fill=(96, 152, 84))

    # small pines on the ridges
    tr = random.Random(5)
    for _ in range(14):
        x = tr.randrange(int(S * 0.03), int(S * 0.97))
        y = tr.randrange(int(S * 0.70), int(S * 0.78))
        h = tr.randrange(70, 130)
        d.rectangle([x - 8, y, x + 8, y + int(h * 0.35)], fill=(94, 62, 42))
        for k in range(3):
            w = h * (0.55 - 0.13 * k)
            yy = y - int(h * (0.28 * k))
            d.polygon([(x - w, yy), (x + w, yy), (x, yy - int(h * 0.55))],
                      fill=(46, 90, 58))

    # fence
    fy = int(S * 0.875)
    for rail in (0, 1):
        yy = fy + rail * 70
        d.rectangle([0, yy, S, yy + 26], fill=(150, 96, 60))
    for i in range(13):
        x = int(S * (0.02 + i * 0.08))
        d.rectangle([x, fy - 45, x + 34, fy + 150], fill=(150, 96, 60))

    # the green critter, front left
    cx, cy = int(S * 0.26), int(S * 0.885)
    body = (118, 190, 82)
    d.ellipse([cx - 190, cy - 60, cx + 190, cy + 260], fill=body)          # body
    d.ellipse([cx - 120, cy + 10, cx + 120, cy + 235], fill=(232, 245, 216))  # belly
    d.ellipse([cx - 165, cy - 330, cx + 165, cy - 10], fill=body)          # head
    for sx in (-1, 1):  # ears
        ex = cx + sx * 105
        d.polygon([(ex - 62, cy - 275), (ex + 62, cy - 275), (ex + sx * 20, cy - 420)], fill=body)
    for sx in (-1, 1):  # eyes
        ex = cx + sx * 62
        d.ellipse([ex - 42, cy - 235, ex + 42, cy - 151], fill=(38, 40, 43))
        d.ellipse([ex - 20, cy - 222, ex + 8, cy - 194], fill=(255, 255, 255))
    d.arc([cx - 55, cy - 165, cx + 55, cy - 95], 20, 160, fill=(38, 40, 43), width=14)

    # titles
    f_title = font("DejaVuSans-Bold.ttf", 330)
    f_sub = font("DejaVuSans.ttf", 108)
    f_artist = font("DejaVuSans.ttf", 96)

    def center(text, fnt, y, fill, shadow=None):
        w = d.textlength(text, font=fnt)
        x = (S - w) / 2
        if shadow:
            d.text((x + 10, y + 12), text, font=fnt, fill=shadow)
        d.text((x, y), text, font=fnt, fill=fill)

    center("WILDHAVEN", f_title, int(S * 0.055), (250, 246, 233), shadow=(20, 26, 48))
    center("— Original Game Soundtrack —", f_sub, int(S * 0.175), (240, 200, 130))
    center("Tsjenn", f_artist, int(S * 0.935), (250, 246, 233))

    img.save(OUT, "JPEG", quality=92)
    print("wrote %s (%dx%d)" % (OUT, S, S))


if __name__ == "__main__":
    main()

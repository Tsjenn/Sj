#!/usr/bin/env python3
"""Neon Drift Racers app icons (192 + 512) — a neon speed chevron over a
night-city horizon, matching the game's #12F2E4 / #FF2FA8 theme."""

import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 1024


def build():
    img = Image.new("RGB", (S, S), (5, 6, 15))
    d = ImageDraw.Draw(img)

    # night gradient
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=(int(20 + 26 * (1 - t)), int(10 + 16 * (1 - t)), int(46 + 30 * (1 - t))))

    # horizon glow
    glow = Image.new("RGB", (S, S), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([S * 0.05, S * 0.42, S * 0.95, S * 0.78], fill=(10, 120, 118))
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.08))
    img = Image.blend(img, Image.blend(img, glow, 0.55), 1.0)
    d = ImageDraw.Draw(img)

    # perspective road
    d.polygon([(S * 0.5 - S * 0.045, S * 0.50), (S * 0.5 + S * 0.045, S * 0.50),
               (S * 0.94, S * 1.02), (S * 0.06, S * 1.02)], fill=(14, 16, 26))
    # glowing kerbs
    d.line([(S * 0.5 - S * 0.05, S * 0.50), (S * 0.045, S * 1.02)], fill=(18, 242, 228), width=22)
    d.line([(S * 0.5 + S * 0.05, S * 0.50), (S * 0.955, S * 1.02)], fill=(255, 47, 168), width=22)
    # dashes
    for i in range(5):
        k0 = i / 5.0
        k1 = k0 + 0.055
        w0, w1 = 6 + k0 * 40, 6 + k1 * 40
        y0 = S * (0.52 + k0 * 0.5)
        y1 = S * (0.52 + k1 * 0.5)
        d.polygon([(S * 0.5 - w0, y0), (S * 0.5 + w0, y0),
                   (S * 0.5 + w1, y1), (S * 0.5 - w1, y1)], fill=(150, 168, 210))

    # skyline
    import random
    random.seed(11)
    for _ in range(26):
        bw = random.randint(38, 96)
        bx = random.randint(-20, S - 20)
        bh = random.randint(90, 330)
        d.rectangle([bx, S * 0.50 - bh, bx + bw, S * 0.51], fill=(16, 20, 36))
        for wy in range(int(S * 0.50 - bh) + 12, int(S * 0.50) - 10, 26):
            for wx in range(bx + 10, bx + bw - 10, 22):
                if random.random() < 0.45:
                    c = (18, 242, 228) if random.random() < 0.3 else (190, 210, 255)
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=c)

    # speed chevrons
    for i, (col, off) in enumerate([((255, 47, 168), 0), ((139, 92, 246), 92), ((18, 242, 228), 184)]):
        y = S * 0.30 + off
        d.polygon([(S * 0.5, y), (S * 0.5 + 190, y + 120), (S * 0.5 + 190, y + 190),
                   (S * 0.5, y + 70), (S * 0.5 - 190, y + 190), (S * 0.5 - 190, y + 120)],
                  fill=col)

    for out, sz in (("game4/icon-512.png", 512), ("game4/icon-192.png", 192)):
        img.resize((sz, sz), Image.LANCZOS).save(os.path.join(ROOT, out))
        print("wrote", out)


if __name__ == "__main__":
    build()

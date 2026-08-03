#!/usr/bin/env python3
"""Rested app icons (192 + 512) — a crescent moon over a calm sleep-wave on
deep night blue, matching the app's #070A14 / #F2A65A palette."""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 1024


def build():
    img = Image.new("RGB", (S, S), (7, 10, 20))
    d = ImageDraw.Draw(img)

    # night gradient
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=(int(10 + 12 * (1 - t)), int(14 + 14 * (1 - t)), int(30 + 26 * (1 - t))))

    # warm glow behind the moon
    glow = Image.new("RGB", (S, S), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([S * 0.20, S * 0.10, S * 0.86, S * 0.68], fill=(150, 96, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.10))
    img = Image.blend(img, glow, 0.40)
    d = ImageDraw.Draw(img)

    # crescent: full disc minus an offset disc
    moon = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(moon)
    md.ellipse([S * 0.28, S * 0.16, S * 0.76, S * 0.64], fill=255)
    md.ellipse([S * 0.40, S * 0.11, S * 0.90, S * 0.61], fill=0)
    warm = Image.new("RGB", (S, S), (242, 166, 90))
    img = Image.composite(warm, img, moon)
    d = ImageDraw.Draw(img)

    # a couple of stars
    for cx, cy, r in ((S * 0.78, S * 0.22, 9), (S * 0.85, S * 0.36, 6), (S * 0.24, S * 0.13, 7)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(226, 234, 250))

    # calm sleep waves across the lower third — stamped as discs so the thick
    # stroke stays smooth instead of spiking at the joints
    def wave(y_base, colour, radius):
        for i in range(0, S + 1, 2):
            t = i / S
            y = y_base + math.sin(t * math.pi * 3.1) * S * 0.055 * (0.45 + 0.55 * math.sin(t * math.pi))
            d.ellipse([i - radius, y - radius, i + radius, y + radius], fill=colour)

    wave(S * 0.79, (79, 182, 224), 13)
    wave(S * 0.875, (63, 95, 214), 9)

    for out, sz in (("sleep/icon-512.png", 512), ("sleep/icon-192.png", 192)):
        img.resize((sz, sz), Image.LANCZOS).save(os.path.join(ROOT, out))
        print("wrote", out)


if __name__ == "__main__":
    build()

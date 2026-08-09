#!/usr/bin/env python3
"""SKYLINE app icons — a golden lantern swinging on a rope of light between
dark towers at dusk."""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 1024
img = Image.new("RGB", (S, S))
d = ImageDraw.Draw(img)
for y in range(S):
    t = y / S
    d.line([(0, y), (S, y)], fill=(int(42 + 80 * t), int(28 + 32 * t), int(78 + 20 * t)))
# fog glow at bottom
glow = Image.new("RGB", (S, S), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-S * 0.2, S * 0.72, S * 1.2, S * 1.4], fill=(190, 110, 80))
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(90)), 0.45)
d = ImageDraw.Draw(img)
# towers
random.seed(5)
for bx, bw, bh in ((-40, 260, 780), (250, 200, 560), (800, 260, 700), (620, 170, 460)):
    d.rectangle([bx, S - bh, bx + bw, S], fill=(26, 18, 48))
    for wy in range(S - bh + 30, S - 20, 44):
        for wx in range(bx + 20, bx + bw - 20, 40):
            if random.random() < 0.5:
                c = (255, 196, 120) if random.random() < 0.6 else (140, 150, 220)
                d.rectangle([wx, wy, wx + 16, wy + 22], fill=c)
# rope of light: arc from top-right tower to lantern
pts = []
ax, ay = 810, 240
lx, ly = 430, 560
for i in range(41):
    t = i / 40
    x = ax + (lx - ax) * t
    y = ay + (ly - ay) * t * t
    pts.append((x, y))
d.line(pts, fill=(255, 220, 160), width=10)
# lantern spirit glow + body
lg = Image.new("RGB", (S, S), (0, 0, 0))
lgd = ImageDraw.Draw(lg)
lgd.ellipse([lx - 130, ly - 130, lx + 130, ly + 130], fill=(255, 180, 90))
img = Image.blend(img, lg.filter(ImageFilter.GaussianBlur(70)), 0.5)
d = ImageDraw.Draw(img)
d.ellipse([lx - 52, ly - 52, lx + 52, ly + 52], fill=(255, 226, 174))
d.polygon([(lx - 60, ly + 30), (lx + 60, ly + 30), (lx, ly + 150)], fill=(58, 46, 94))
for out, sz in (("game5/icon-512.png", 512), ("game5/icon-192.png", 192)):
    img.resize((sz, sz), Image.LANCZOS).save(os.path.join(ROOT, out))
    print("wrote", out)

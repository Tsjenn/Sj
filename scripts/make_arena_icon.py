#!/usr/bin/env python3
"""Wildhaven Arena app icons (192 + 512) — purple arena badge with crossed
swords over a crowned critter silhouette, matching the game's #7A3FA0 theme."""

from PIL import Image, ImageDraw

import make_book as B


def build(size):
    S = 1024
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    # radial-ish purple gradient
    for y in range(S):
        t = y / S
        r = int(46 + 76 * t)
        g = int(22 + 41 * t)
        b = int(74 + 86 * t)
        d.line([(0, y), (S, y)], fill=(r, g, b))
    # arena ring
    d.ellipse([S*0.10, S*0.10, S*0.90, S*0.90], outline=(255, 214, 92), width=26)
    d.ellipse([S*0.135, S*0.135, S*0.865, S*0.865], outline=(255, 255, 255), width=8)
    # critter (flufftail colours) centered
    B.critter(d, S*0.5, S*0.50, S/210, (247, 202, 136), (236, 148, 90), "fox")
    # crown on top of its head
    cx, cy = S*0.5, S*0.235
    w = S*0.12
    d.polygon([(cx-w, cy), (cx-w*0.55, cy-S*0.06), (cx-w*0.18, cy-S*0.015),
               (cx, cy-S*0.085), (cx+w*0.18, cy-S*0.015), (cx+w*0.55, cy-S*0.06),
               (cx+w, cy), (cx+w*0.8, cy+S*0.04), (cx-w*0.8, cy+S*0.04)],
              fill=(255, 214, 92))
    # crossed swords at the bottom
    def sword(x0, y0, x1, y1):
        d.line([(x0, y0), (x1, y1)], fill=(232, 238, 246), width=30)
        # hilt
        mx, my = x0 + (x1-x0)*0.82, y0 + (y1-y0)*0.82
        px, py = -(y1-y0), (x1-x0)
        n = (px*px + py*py) ** 0.5
        px, py = px/n*54, py/n*54
        d.line([(mx-px, my-py), (mx+px, my+py)], fill=(255, 214, 92), width=22)
    sword(S*0.34, S*0.93, S*0.465, S*0.795)
    sword(S*0.66, S*0.93, S*0.535, S*0.795)
    for out, sz in (("game3/icon-512.png", 512), ("game3/icon-192.png", 192)):
        img.resize((sz, sz), Image.LANCZOS).save(B.os.path.join(B.ROOT, out))
        print("wrote", out)


if __name__ == "__main__":
    build(1024)

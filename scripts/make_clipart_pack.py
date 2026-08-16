#!/usr/bin/env python3
"""Build the Wildhaven Creatures Clipart Pack for Etsy.

Repackages the 13 transparent 4500x4500 PNGs (10 creatures + 3 quote
designs) from the Redbubble source art into a customer-facing clipart
pack with a plain-language license.

    python3 scripts/make_clipart_pack.py -> dist/Wildhaven-Clipart-Pack.zip
"""

import io
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "dist", "Wildhaven-Redbubble-Pack.zip")
OUT = os.path.join(ROOT, "dist", "Wildhaven-Clipart-Pack.zip")

LICENSE = """WILDHAVEN CREATURES CLIPART — LICENSE
======================================

WHAT YOU CAN DO
- Personal projects: invitations, stickers, room decor, scrapbooks,
  school projects — anything for yourself or as gifts.
- Small commercial use: physical items you make and sell yourself
  (up to 500 total physical items, e.g. printed cards, stickers,
  mugs). Credit appreciated, not required.

WHAT YOU CANNOT DO
- Resell, share or redistribute the files themselves, alone or in
  any digital bundle, free or paid.
- Sell digital products where our files are the main content
  (e.g. reselling as clipart, print-on-demand digital downloads).
- Claim the artwork as your own or register it as a trademark.

FILES
13 PNG files, 4500 x 4500 pixels, transparent backgrounds, RGB.
Print crisp up to about 15 x 15 inches (38 x 38 cm) at 300 DPI.

Questions? Reply to your order and we answer.
"""

README = """WILDHAVEN CREATURES CLIPART PACK
=================================
Thank you for your purchase!

Inside: 13 transparent PNGs (10 creatures + 3 quote designs),
4500 x 4500 px. They drop cleanly onto any background in Canva,
Procreate, PowerPoint, Cricut Design Space or any editor.

Tip: for small prints (stickers, cards) just resize down — the
files are large so they stay sharp at any size you need.

See LICENSE.txt for what's allowed. Enjoy the critters!
"""


def main():
    src = zipfile.ZipFile(SRC)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        n = 0
        for name in src.namelist():
            if name.endswith(".png"):
                base = os.path.basename(name)
                z.writestr("Wildhaven-Clipart/" + base, src.read(name))
                n += 1
        z.writestr("Wildhaven-Clipart/LICENSE.txt", LICENSE)
        z.writestr("Wildhaven-Clipart/README.txt", README)
    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print("wrote %s (%d PNGs, %.1f MB)" % (OUT, n, size_mb))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Package Critter Isles.

- site/play/       free demo (3 critters, small island) served by the store site
- dist/Critter-Isles-Full.zip   the sellable full version (8 critters, big island)

The canonical game lives in game/ (index.html = full version). The demo page is
generated from it so the two never drift. Run after any change to game/:

    python3 scripts/package_game.py
"""

import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game")
PLAY = os.path.join(ROOT, "site", "play")

DEMO_CONFIG = """<script src="../config.js"></script>
<script>
  var _g = (window.STORE && window.STORE.products && window.STORE.products.game) || {};
  window.GAME_CONFIG = { mode: "demo",
    buyLink: (_g.link && _g.link.indexOf("SET-ME") === -1) ? _g.link : "" };
</script>"""

FULL_CONFIG = '<script>window.GAME_CONFIG = { mode: "full", buyLink: "" };</script>'

BUYER_README = """CRITTER ISLES — FULL VERSION
============================

Thank you for your purchase!

HOW TO PLAY
1. Unzip this folder anywhere.
2. Open index.html in any modern browser (Chrome, Edge, Firefox, Safari).
   Works offline — no install, no account.
3. Move with WASD or arrow keys (on-screen buttons appear on touch devices).
   Get close to a wild critter and press SPACE to throw an orb.
   Walk into glowing orbs to restock. Catch all 8 species to win!
Your progress saves automatically in the browser.

LICENSE — PERSONAL USE
Play on any of your devices. Do not resell, redistribute, or re-upload the
game files anywhere, free or paid.

Problems with your download? Reply to your purchase receipt email.
"""


def main():
    # --- demo ---
    os.makedirs(PLAY, exist_ok=True)
    shutil.copy(os.path.join(GAME, "game.js"), PLAY)
    shutil.copy(os.path.join(GAME, "three.min.js"), PLAY)
    with open(os.path.join(GAME, "index.html")) as f:
        html = f.read()
    assert FULL_CONFIG in html, "full-version config line not found in game/index.html"
    demo = html.replace(FULL_CONFIG, DEMO_CONFIG)
    demo = demo.replace("Critter Isles — Full Version", "Critter Isles — Free Demo")
    with open(os.path.join(PLAY, "index.html"), "w") as f:
        f.write(demo)

    # --- full-version zip ---
    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)
    zpath = os.path.join(dist, "Critter-Isles-Full.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html", "game.js", "three.min.js"):
            z.write(os.path.join(GAME, name), "Critter-Isles/" + name)
        z.writestr("Critter-Isles/README.txt", BUYER_README)
    print("Packaged demo -> site/play/ and full game ->", zpath)


if __name__ == "__main__":
    main()

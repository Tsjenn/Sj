#!/usr/bin/env python3
"""Package Wildhaven Arena.

- site/play3/                           free demo served by the store site
- dist/Wildhaven-Arena-Full.zip         buyer download (folder-wrapped)
- dist/Wildhaven-Arena-itch-full.zip    itch.io paid build (index.html at zip root)
- dist/Wildhaven-Arena-itch-demo.zip    itch.io browser-embed demo (standalone)

The canonical game lives in game3/ (index.html = full version). Run after any
change to game3/:

    python3 scripts/package_game3.py
"""

import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game3")
PLAY = os.path.join(ROOT, "site", "play3")

FULL_CONFIG = '<script>window.GAME_CONFIG = { mode: "full", buyLink: "" };</script>'

DEMO_CONFIG = """<script src="../config.js"></script>
<script>
  var _g = (window.STORE && window.STORE.products && window.STORE.products.arena) || {};
  window.GAME_CONFIG = { mode: "demo",
    buyLink: (_g.link && _g.link.indexOf("SET-ME") === -1) ? _g.link : "" };
</script>"""

ITCH_DEMO_CONFIG = '<script>window.GAME_CONFIG = { mode: "demo", buyLink: "" };</script>'

BUYER_README = """WILDHAVEN ARENA — FULL VERSION
==============================

Thank you for your purchase!

HOW TO PLAY
1. Unzip this folder anywhere.
2. Open index.html in any modern browser (Chrome, Edge, Firefox, Safari).
   Works offline — no install, no account. Sound on for the full experience!
3. Catch a team of creatures across three zones, defeat the three crowned
   Guardians to become Arena Champion, then press Duel to trade Battle Codes
   with players anywhere in the world and fight their teams.
Your progress saves automatically.

LICENSE — PERSONAL USE
Play on any of your devices. Do not resell, redistribute, or re-upload the
game files anywhere, free or paid.

Problems with your download? Reply to your purchase receipt email.
"""

GAME_FILES = ("game.js", "three.min.js", "manifest.webmanifest", "sw.js",
              "icon-192.png", "icon-512.png")


def main():
    os.makedirs(PLAY, exist_ok=True)
    for name in GAME_FILES:
        shutil.copy(os.path.join(GAME, name), PLAY)
    with open(os.path.join(GAME, "index.html")) as f:
        html = f.read()
    assert FULL_CONFIG in html, "full-version config line not found in game3/index.html"
    demo = html.replace(FULL_CONFIG, DEMO_CONFIG)
    demo = demo.replace("Wildhaven Arena — Full Version",
                        "Wildhaven Arena — Free Demo")
    with open(os.path.join(PLAY, "index.html"), "w") as f:
        f.write(demo)

    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)

    zpath = os.path.join(dist, "Wildhaven-Arena-Full.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), "Wildhaven-Arena/" + name)
        z.writestr("Wildhaven-Arena/README.txt", BUYER_README)

    itch_full = os.path.join(dist, "Wildhaven-Arena-itch-full.zip")
    with zipfile.ZipFile(itch_full, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), name)
        z.writestr("README.txt", BUYER_README)

    itch_demo_html = html.replace(FULL_CONFIG, ITCH_DEMO_CONFIG)
    itch_demo_html = itch_demo_html.replace(
        "Wildhaven Arena — Full Version", "Wildhaven Arena — Demo")
    itch_demo = os.path.join(dist, "Wildhaven-Arena-itch-demo.zip")
    with zipfile.ZipFile(itch_demo, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", itch_demo_html)
        for name in GAME_FILES:
            z.write(os.path.join(GAME, name), name)

    print("Packaged demo -> site/play3/, buyer zip ->", zpath)
    print("itch builds ->", itch_full, "and", itch_demo)


if __name__ == "__main__":
    main()

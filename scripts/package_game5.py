#!/usr/bin/env python3
"""Package SKYLINE (the swinging courier game).

- site/play5/                           free demo served by the store site
- dist/SKYLINE-Full.zip         buyer download (folder-wrapped)
- dist/SKYLINE-itch-full.zip    itch.io paid build (index.html at zip root)
- dist/SKYLINE-itch-demo.zip    itch.io browser-embed demo (standalone)

The canonical game lives in game5/ (index.html = full version). Run after any
change to game5/:

    python3 scripts/package_game5.py
"""

import os
import shutil
import zipfile

# Injected into the free web demo only — buyer downloads and itch builds
# stay analytics-free.
BEACON = ("<!-- Cloudflare Web Analytics --><script type='module' "
          "src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"bb7b5b01b49f4b3582c64d33ef35643f\"}'>"
          "</script><!-- End Cloudflare Web Analytics -->")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game5")
PLAY = os.path.join(ROOT, "site", "play5")

FULL_CONFIG = '<script>window.GAME_CONFIG = { mode: "full", buyLink: "" };</script>'

DEMO_CONFIG = """<script src="../config.js"></script>
<script>
  var _g = (window.STORE && window.STORE.products && window.STORE.products.skyline) || {};
  window.GAME_CONFIG = { mode: "demo",
    buyLink: (_g.link && _g.link.indexOf("SET-ME") === -1) ? _g.link : "" };
</script>"""

ITCH_DEMO_CONFIG = '<script>window.GAME_CONFIG = { mode: "demo", buyLink: "" };</script>'

BUYER_README = """SKYLINE — FULL VERSION
======================

Thank you for your purchase!

HOW TO PLAY
1. Unzip this folder anywhere.
2. Open index.html in any modern browser (Chrome, Edge, Firefox, Safari).
   Works offline — no install, no account. Sound on for the wind!
3. Hold SPACE to throw a light-rope at the best anchor ahead; release on the
   upswing to fly. A/D steer, W reels the rope for speed. Chain swings to
   build FLOW. Deliver the lantern through every ring, chase gold times,
   then trade Flight Codes with anyone on Earth and race their ghost.
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
    assert FULL_CONFIG in html, "full-version config line not found in game5/index.html"
    demo = html.replace(FULL_CONFIG, DEMO_CONFIG)
    demo = demo.replace("SKYLINE — Full Version",
                        "SKYLINE — Free Demo")
    demo = demo.replace("</body>", BEACON + "\n</body>", 1)
    with open(os.path.join(PLAY, "index.html"), "w") as f:
        f.write(demo)

    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)

    zpath = os.path.join(dist, "SKYLINE-Full.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), "SKYLINE/" + name)
        z.writestr("SKYLINE/README.txt", BUYER_README)

    itch_full = os.path.join(dist, "SKYLINE-itch-full.zip")
    with zipfile.ZipFile(itch_full, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), name)
        z.writestr("README.txt", BUYER_README)

    itch_demo_html = html.replace(FULL_CONFIG, ITCH_DEMO_CONFIG)
    itch_demo_html = itch_demo_html.replace(
        "SKYLINE — Full Version", "SKYLINE — Demo")
    itch_demo = os.path.join(dist, "SKYLINE-itch-demo.zip")
    with zipfile.ZipFile(itch_demo, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", itch_demo_html)
        for name in GAME_FILES:
            z.write(os.path.join(GAME, name), name)

    print("Packaged demo -> site/play5/, buyer zip ->", zpath)
    print("itch builds ->", itch_full, "and", itch_demo)


if __name__ == "__main__":
    main()

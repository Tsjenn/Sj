#!/usr/bin/env python3
"""Package Wildhaven: Creature Park.

- site/play2/                          free demo served by the store site
- dist/Wildhaven-Park-Full.zip         buyer download (folder-wrapped)
- dist/Wildhaven-itch-full.zip         itch.io paid build (index.html at zip root)
- dist/Wildhaven-itch-demo.zip         itch.io browser-embed demo (standalone)

The canonical game lives in game2/ (index.html = full version). Run after any
change to game2/:

    python3 scripts/package_game2.py
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
GAME = os.path.join(ROOT, "game2")
PLAY = os.path.join(ROOT, "site", "play2")

FULL_CONFIG = '<script>window.GAME_CONFIG = { mode: "full", buyLink: "" };</script>'

DEMO_CONFIG = """<script src="../config.js"></script>
<script>
  var _g = (window.STORE && window.STORE.products && window.STORE.products.park) || {};
  window.GAME_CONFIG = { mode: "demo",
    buyLink: (_g.link && _g.link.indexOf("SET-ME") === -1) ? _g.link : "" };
</script>"""

ITCH_DEMO_CONFIG = '<script>window.GAME_CONFIG = { mode: "demo", buyLink: "" };</script>'

BUYER_README = """WILDHAVEN: CREATURE PARK — FULL VERSION
=======================================

Thank you for your purchase!

HOW TO PLAY
1. Unzip this folder anywhere.
2. Open index.html in any modern browser (Chrome, Edge, Firefox, Safari).
   Works offline — no install, no account. Sound on for the full experience!
3. Explore east into the wilds, catch creatures with SPACE, build habitats
   for them back in your park (Build menu), and welcome paying visitors.
   Grow your park to 5 stars and complete your collection to win.
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
    assert FULL_CONFIG in html, "full-version config line not found in game2/index.html"
    demo = html.replace(FULL_CONFIG, DEMO_CONFIG)
    demo = demo.replace("Wildhaven: Creature Park — Full Version",
                        "Wildhaven: Creature Park — Free Demo")
    demo = demo.replace("</body>", BEACON + "\n</body>", 1)
    with open(os.path.join(PLAY, "index.html"), "w") as f:
        f.write(demo)

    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)

    zpath = os.path.join(dist, "Wildhaven-Park-Full.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), "Wildhaven-Park/" + name)
        z.writestr("Wildhaven-Park/README.txt", BUYER_README)

    itch_full = os.path.join(dist, "Wildhaven-itch-full.zip")
    with zipfile.ZipFile(itch_full, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), name)
        z.writestr("README.txt", BUYER_README)

    itch_demo_html = html.replace(FULL_CONFIG, ITCH_DEMO_CONFIG)
    itch_demo_html = itch_demo_html.replace(
        "Wildhaven: Creature Park — Full Version", "Wildhaven: Creature Park — Demo")
    itch_demo = os.path.join(dist, "Wildhaven-itch-demo.zip")
    with zipfile.ZipFile(itch_demo, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", itch_demo_html)
        for name in GAME_FILES:
            z.write(os.path.join(GAME, name), name)

    print("Packaged demo -> site/play2/, buyer zip ->", zpath)
    print("itch builds ->", itch_full, "and", itch_demo)


if __name__ == "__main__":
    main()

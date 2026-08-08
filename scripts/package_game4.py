#!/usr/bin/env python3
"""Package Neon Drift Racers.

- site/play4/                            free demo served by the store site
- dist/Neon-Drift-Racers-Full.zip        buyer download (folder-wrapped)
- dist/Neon-Drift-itch-full.zip          itch.io paid build (index.html at zip root)
- dist/Neon-Drift-itch-demo.zip          itch.io browser-embed demo (standalone)

The canonical game lives in game4/ (index.html = full version). Run after any
change to game4/:

    python3 scripts/package_game4.py
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
GAME = os.path.join(ROOT, "game4")
PLAY = os.path.join(ROOT, "site", "play4")

FULL_CONFIG = '<script>window.GAME_CONFIG = { mode: "full", buyLink: "" };</script>'

DEMO_CONFIG = """<script src="../config.js"></script>
<script>
  var _g = (window.STORE && window.STORE.products && window.STORE.products.racer) || {};
  window.GAME_CONFIG = { mode: "demo",
    buyLink: (_g.link && _g.link.indexOf("SET-ME") === -1) ? _g.link : "" };
</script>"""

ITCH_DEMO_CONFIG = '<script>window.GAME_CONFIG = { mode: "demo", buyLink: "" };</script>'

BUYER_README = """NEON DRIFT RACERS — FULL VERSION
================================

Thank you for your purchase!

HOW TO PLAY
1. Unzip this folder anywhere.
2. Open index.html in any modern browser (Chrome, Edge, Firefox, Safari).
   Works offline — no install, no account. Sound on for the full experience!
3. Build your driver in the Garage, pick a machine, and race.
   W / arrows to drive. Hold SHIFT through a corner to DRIFT — the longer the
   drift, the bigger the boost when you release. Chain drifts to win.
   SPACE fires nitro when the bar is full. R respawns you.
4. Set a lap time, then hit Online: your run becomes a RACE CODE. Send it to
   anyone on Earth and they race your ghost. Paste theirs to race them back.
Your progress, records and leaderboard save automatically.

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
    assert FULL_CONFIG in html, "full-version config line not found in game4/index.html"
    demo = html.replace(FULL_CONFIG, DEMO_CONFIG)
    demo = demo.replace("Neon Drift Racers — Full Version",
                        "Neon Drift Racers — Free Demo")
    demo = demo.replace("</body>", BEACON + "\n</body>", 1)
    with open(os.path.join(PLAY, "index.html"), "w") as f:
        f.write(demo)

    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)

    zpath = os.path.join(dist, "Neon-Drift-Racers-Full.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), "Neon-Drift-Racers/" + name)
        z.writestr("Neon-Drift-Racers/README.txt", BUYER_README)

    itch_full = os.path.join(dist, "Neon-Drift-itch-full.zip")
    with zipfile.ZipFile(itch_full, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + GAME_FILES:
            z.write(os.path.join(GAME, name), name)
        z.writestr("README.txt", BUYER_README)

    itch_demo_html = html.replace(FULL_CONFIG, ITCH_DEMO_CONFIG)
    itch_demo_html = itch_demo_html.replace(
        "Neon Drift Racers — Full Version", "Neon Drift Racers — Demo")
    itch_demo = os.path.join(dist, "Neon-Drift-itch-demo.zip")
    with zipfile.ZipFile(itch_demo, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", itch_demo_html)
        for name in GAME_FILES:
            z.write(os.path.join(GAME, name), name)

    print("Packaged demo -> site/play4/, buyer zip ->", zpath)
    print("itch builds ->", itch_full, "and", itch_demo)


if __name__ == "__main__":
    main()

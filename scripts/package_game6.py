#!/usr/bin/env python3
"""Package Critter Tower (the one-thumb stacker).

- site/play6/                          free web version on the store site
  (Cloudflare beacon injected — site pages only, per fleet rules)
- dist/Critter-Tower-playables.zip     Playgama submission build (their
  route to YouTube Playables): bundles the Playgama Bridge SDK
  (game6/vendor/, LGPL) + config, sends game_ready on init as their
  QA tool requires. index.html at zip root, NO analytics.
- dist/Critter-Tower-itch.zip          itch.io browser-embed build,
  vanilla (no SDK), no external calls

Critter Tower is a free game by design: its job is discovery
(Playables, portals) and feeding the Wildhaven world. No paid tier.

    python3 scripts/package_game6.py
"""

import os
import shutil
import zipfile

BEACON = ("<!-- Cloudflare Web Analytics --><script type='module' "
          "src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"bb7b5b01b49f4b3582c64d33ef35643f\"}'>"
          "</script><!-- End Cloudflare Web Analytics -->")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game6")
PLAY = os.path.join(ROOT, "site", "play6")
DIST = os.path.join(ROOT, "dist")


def read(p):
    with open(p) as f:
        return f.read()


def main():
    html = read(os.path.join(GAME, "index.html"))
    js = read(os.path.join(GAME, "game.js"))
    imgs = sorted(f for f in os.listdir(os.path.join(GAME, "img"))
                  if f.endswith(".png"))

    # ---- site free version (beacon injected)
    if os.path.isdir(PLAY):
        shutil.rmtree(PLAY)
    os.makedirs(os.path.join(PLAY, "img"))
    site_html = html.replace("</body>", BEACON + "\n</body>")
    with open(os.path.join(PLAY, "index.html"), "w") as f:
        f.write(site_html)
    with open(os.path.join(PLAY, "game.js"), "w") as f:
        f.write(js)
    for n in imgs:
        shutil.copy(os.path.join(GAME, "img", n), os.path.join(PLAY, "img", n))

    # ---- clean builds (no analytics, index at zip root)
    assert "cloudflareinsights" not in html and "cloudflareinsights" not in js
    vendor = os.path.join(GAME, "vendor")
    playgama_html = html.replace(
        '<script src="game.js"></script>',
        '<script src="playgama-bridge.js"></script>\n'
        '<script src="game.js"></script>')
    assert 'src="playgama-bridge.js"' in playgama_html

    for zname, zhtml, with_sdk in (
            ("Critter-Tower-playables.zip", playgama_html, True),
            ("Critter-Tower-itch.zip", html, False)):
        zpath = os.path.join(DIST, zname)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("index.html", zhtml)
            z.writestr("game.js", js)
            if with_sdk:
                for n in ("playgama-bridge.js", "playgama-bridge-config.json",
                          "PLAYGAMA-BRIDGE-LICENSE"):
                    z.write(os.path.join(vendor, n), n)
            for n in imgs:
                z.write(os.path.join(GAME, "img", n), "img/" + n)
        print("build:", zpath, os.path.getsize(zpath) // 1024, "KB")
    print("site: site/play6/ (beacon on)")


if __name__ == "__main__":
    main()

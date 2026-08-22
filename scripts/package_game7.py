#!/usr/bin/env python3
"""Package Critter Drop (the drop-and-merge game).

- site/play7/                       free web version (Cloudflare beacon
  injected — site pages only, per fleet rules)
- dist/Critter-Drop-playables.zip   Playgama submission build: bundles
  the Playgama Bridge SDK (game6/vendor/, shared) + config, sends
  game_ready on init. index.html at zip root, NO analytics.
- dist/Critter-Drop-itch.zip        itch.io build, vanilla (no SDK),
  no external calls

Free by design: discovery game feeding the Wildhaven world.

    python3 scripts/package_game7.py
"""

import os
import shutil
import zipfile

BEACON = ("<!-- Cloudflare Web Analytics --><script type='module' "
          "src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"bb7b5b01b49f4b3582c64d33ef35643f\"}'>"
          "</script><!-- End Cloudflare Web Analytics -->")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game7")
VENDOR = os.path.join(ROOT, "game6", "vendor")   # one shared SDK copy
PLAY = os.path.join(ROOT, "site", "play7")
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
    playgama_html = html.replace(
        '<script src="game.js"></script>',
        '<script src="playgama-bridge.js"></script>\n'
        '<script src="game.js"></script>')
    assert 'src="playgama-bridge.js"' in playgama_html

    for zname, zhtml, with_sdk in (
            ("Critter-Drop-playables.zip", playgama_html, True),
            ("Critter-Drop-itch.zip", html, False)):
        zpath = os.path.join(DIST, zname)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("index.html", zhtml)
            z.writestr("game.js", js)
            if with_sdk:
                for n in ("playgama-bridge.js", "playgama-bridge-config.json",
                          "PLAYGAMA-BRIDGE-LICENSE"):
                    z.write(os.path.join(VENDOR, n), n)
            for n in imgs:
                z.write(os.path.join(GAME, "img", n), "img/" + n)
        print("build:", zpath, os.path.getsize(zpath) // 1024, "KB")
    print("site: site/play7/ (beacon on)")


if __name__ == "__main__":
    main()

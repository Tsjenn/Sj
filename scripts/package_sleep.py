#!/usr/bin/env python3
"""Package Rested (sleep tracker).

- site/sleep/                    free tier, served by the store site
- dist/Rested-Sleep-App.zip      full version (self-host / side-load / wrap)

The canonical app lives in sleep/ (index.html = full version). Run after any
change to sleep/:

    python3 scripts/package_sleep.py
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
APP = os.path.join(ROOT, "sleep")
PUB = os.path.join(ROOT, "site", "sleep")

FULL_CONFIG = '<script>window.APP_CONFIG = { mode: "full", buyLink: "" };</script>'

FREE_CONFIG = """<script src="../config.js"></script>
<script>
  var _g = (window.STORE && window.STORE.products && window.STORE.products.sleep) || {};
  window.APP_CONFIG = { mode: "demo",
    buyLink: (_g.link && _g.link.indexOf("SET-ME") === -1) ? _g.link : "" };
</script>"""

README = """RESTED — SLEEP TRACKER & SOUNDS (full version)
=============================================

Thank you for your purchase!

INSTALL IT LIKE AN APP
1. Unzip and put these files on any web host that serves HTTPS
   (GitHub Pages, Netlify and Cloudflare Pages all do this free), or open
   index.html directly for a quick look.
2. On the phone, open the page and:
   - iPhone/iPad (Safari): Share -> "Add to Home Screen"
   - Android (Chrome): menu -> "Install app" / "Add to Home screen"
   It then launches full screen like any other app and works offline.

HOW TO USE IT
- Set your alarm, pick a soundscape, tap "Start tracking".
- Put the phone screen-up on the mattress beside your pillow, or on a
  nightstand within about a metre, PLUGGED IN. Tracking needs the screen on;
  the display dims itself to near-black to save power.
- In the morning tap Stop (or Stop on the alarm) and your night is scored.
- Tag your mornings. After a couple of weeks the You tab tells you which
  habits actually move your sleep quality.

IMPORTANT — WHAT THIS CAN AND CANNOT DO
Rested estimates sleep from movement and sound picked up by the microphone.
That works well for when you fell asleep, how broken the night was and how
long you slept. Splitting light / deep / dream sleep is an ESTIMATE — real
staging needs brain activity (EEG), which no phone can see. Use the trends
over weeks, not any single night's percentages.

Rested is a wellness tool, not a medical device, and does not diagnose or
treat any condition. If you regularly sleep badly, snore heavily or stop
breathing in your sleep, please talk to a doctor.

PRIVACY
Audio is analysed on the device in real time and is never recorded, stored
or uploaded. Your nights live only in this browser's local storage. Use
You -> Export to back them up.

LICENSE — PERSONAL USE
Use on any of your own devices. Do not resell or redistribute the files.
"""

FILES = ("app.js", "manifest.webmanifest", "sw.js", "icon-192.png", "icon-512.png")


def main():
    os.makedirs(PUB, exist_ok=True)
    for name in FILES:
        shutil.copy(os.path.join(APP, name), PUB)
    with open(os.path.join(APP, "index.html")) as f:
        html = f.read()
    assert FULL_CONFIG in html, "full-version config line not found in sleep/index.html"
    with open(os.path.join(PUB, "index.html"), "w") as f:
        f.write(html.replace(FULL_CONFIG, FREE_CONFIG)
                .replace("</body>", BEACON + "\n</body>", 1))

    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)
    zpath = os.path.join(dist, "Rested-Sleep-App.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("index.html",) + FILES:
            z.write(os.path.join(APP, name), "Rested/" + name)
        z.writestr("Rested/README.txt", README)

    print("Free tier -> site/sleep/, full version ->", zpath)


if __name__ == "__main__":
    main()

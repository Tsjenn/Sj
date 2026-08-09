#!/usr/bin/env python3
"""Build the free lead magnet: The Honest Sleep Starter (PDF).

A short, genuinely useful giveaway distilled from the fleet's sleep
material. Distributed as a $0+ Gumroad product so every download becomes
an email contact the owner can message on future launches.

Renders styled HTML, then prints to PDF via the bundled Chromium.

    python3 scripts/make_leadmagnet.py
"""

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_HTML = os.path.join(ROOT, "dist", "_leadmagnet.html")
OUT_PDF = os.path.join(ROOT, "dist", "Honest-Sleep-Starter.pdf")

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  @page { size: A5; margin: 16mm 14mm; }
  * { box-sizing: border-box; }
  body { font-family: Georgia, 'Times New Roman', serif; color: #26282B;
         line-height: 1.62; font-size: 10.5pt; margin: 0; }
  .page { page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  h1 { font-size: 21pt; line-height: 1.2; letter-spacing: -.01em; margin: 0 0 4mm; }
  h2 { font-size: 13pt; margin: 7mm 0 2.5mm; }
  p { margin: 0 0 3.2mm; }
  .cover { text-align: center; padding-top: 30mm; }
  .cover .moon { font-size: 34pt; }
  .cover h1 { font-size: 26pt; margin-top: 6mm; }
  .cover .sub { font-style: italic; color: #555; font-size: 11.5pt; margin-top: 3mm; }
  .cover .rule { width: 24mm; height: 1mm; background: #E8A55C; margin: 8mm auto; }
  .cover .foot { margin-top: 34mm; color: #777; font-size: 9pt; }
  .lede { font-size: 11.5pt; }
  ul { margin: 0 0 3.2mm 5mm; padding: 0; }
  li { margin-bottom: 1.6mm; }
  .box { background: #FBF3E6; border-left: 2.5mm solid #E8A55C; padding: 4mm 5mm; margin: 4mm 0; }
  .cheat h2 { margin-top: 4mm; }
  .cheat table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
  .cheat td { border-top: 0.3mm solid #DDD; padding: 2.2mm 1mm; vertical-align: top; }
  .cheat td:first-child { font-weight: bold; width: 34%; }
  .small { font-size: 8.5pt; color: #777; }
</style></head><body>

<div class="page cover">
  <div class="moon">&#127769;</div>
  <h1>The Honest<br>Sleep Starter</h1>
  <div class="sub">The five changes that actually matter,<br>minus the marketing</div>
  <div class="rule"></div>
  <p class="foot">A free guide from Clarity Templates<br>tsjenn.github.io/Sj</p>
</div>

<div class="page">
  <h1>Why most sleep advice fails you</h1>
  <p class="lede">Most advice about sleep is a list of twenty tips presented as if
  they all matter equally. Nobody can follow twenty tips, and the honest truth
  is that they are not equal: sleep has a handful of big levers and a long tail
  of things that barely matter.</p>
  <p>This short guide is the ranked version. Do only the first thing in it and
  you will still capture most of the benefit. It makes no miracle promises —
  biology takes about two weeks to respond, and the first days can feel slightly
  worse before they feel better. What it offers instead is the honest version of
  what works, in the order it works.</p>
  <div class="box"><p style="margin:0"><b>One rule for reading:</b> if you
  regularly snore heavily, wake gasping, or have slept badly for months, this is
  a doctor conversation, not a habits conversation. No guide should pretend
  otherwise.</p></div>
</div>

<div class="page">
  <h1>1. Anchor your wake-up time</h1>
  <p class="lede">The single most powerful change — and almost nobody does it.</p>
  <p>You cannot force yourself to feel sleepy at 10pm. But you <i>can</i> choose
  when you get up, and your body sets tonight's sleepiness partly by when you
  woke this morning. Pick a wake time you can hold seven days a week and hold
  it. Within about two weeks, your bedtime starts fixing itself.</p>
  <p>The hard part is the weekend. A Saturday lie-in feels like repayment; it
  works more like jet lag — shifting your wake time three hours has roughly the
  effect of flying across three time zones and back every week.</p>
  <h2>2. Use light like the drug it is</h2>
  <p>Morning light is the signal that sets your internal clock. Ten to twenty
  minutes outdoors within an hour of waking beats any supplement — even on a
  grey day, outdoor light is many times brighter than your kitchen. In the
  evening, run the reverse: dim the main lights an hour before bed and prefer
  lamps to ceiling lights. The point is less about screens specifically and
  more about lowering total brightness while you wind down.</p>
</div>

<div class="page">
  <h1>3. The 3am playbook</h1>
  <p class="lede">Waking at night is normal. What you do next decides whether
  it costs you ten minutes or two hours.</p>
  <ul>
    <li><b>Don't check the clock.</b> Knowing the time only gives your mind
    arithmetic to be anxious about.</li>
    <li><b>Give it about twenty minutes.</b> If sleep hasn't returned, get up.
    Lying awake teaches your brain that bed is a place for worrying.</li>
    <li><b>Keep lights low, do something genuinely boring</b> — a dull book, a
    quiet chore. No phone: it's a slot machine for your attention.</li>
    <li><b>Return when sleepy, not when guilty.</b> Sleepiness comes back on
    its own schedule; your job is simply not to fight in bed.</li>
  </ul>
  <h2>4. Caffeine &amp; alcohol, honestly</h2>
  <p>Caffeine lingers far longer than it feels — half of a 2pm coffee is still
  in you around bedtime. If sleep is fragile, make lunchtime your cutoff.
  Alcohol is the great impersonator: it sedates you to sleep, then rebounds and
  fragments the second half of the night. You don't need abstinence lectures —
  just know the trade you're making.</p>
</div>

<div class="page">
  <h1>5. Make the bedroom boring</h1>
  <p class="lede">Cool, dark, quiet — and used for one thing.</p>
  <p>A slightly cool room helps because your body needs to drop its core
  temperature to fall asleep. Darkness is cheap: any eye mask outperforms most
  gadgets. Steady background sound (a fan, rain noise) helps when your problem
  is unpredictable noise, not sound itself. And if you can, keep work, feeds
  and arguments out of bed — you are training an association, and the training
  works in both directions.</p>
  <h2>What barely matters</h2>
  <p>Expensive pillows and mattresses beyond basic comfort, most supplements,
  precise sleep-stage numbers from an app, the occasional bad night. Sleep runs
  on rhythm and pressure, not on merchandise — and one rough night has never
  broken anyone. Consistency, not perfection, is the whole game.</p>
</div>

<div class="page cheat">
  <h1>The one-page cheat sheet</h1>
  <table>
    <tr><td>Wake time</td><td>Same time every day, weekends included. This is
    the anchor everything else hangs on.</td></tr>
    <tr><td>Morning</td><td>10&ndash;20 min of outdoor light within an hour of
    waking.</td></tr>
    <tr><td>Afternoon</td><td>Last caffeine by lunchtime if sleep is fragile.</td></tr>
    <tr><td>Evening</td><td>Dim lights an hour before bed. Lamps, not ceiling
    lights. Alcohol trades a fast start for a broken second half.</td></tr>
    <tr><td>In bed</td><td>Bed is for sleep. Can't sleep after ~20 min? Get up,
    low light, boring activity, return when sleepy.</td></tr>
    <tr><td>3am wake</td><td>No clock. No phone. Twenty patient minutes, then
    the playbook.</td></tr>
    <tr><td>See a doctor if</td><td>Heavy snoring, gasping awake, or months of
    bad sleep despite good habits.</td></tr>
  </table>
  <h2>Want the tools?</h2>
  <p>Everything we make lives at <b>tsjenn.github.io/Sj</b> — including
  <b>Rested</b>, our free honest sleep tracker that runs in your browser, and
  more guides written in this same no-nonsense voice. The full-length book this
  guide previews, <i>The Honest Sleep Book</i>, is on its way.</p>
  <p class="small">This guide offers general information about sleep habits,
  not medical advice. &copy; Clarity Templates. Please don't redistribute —
  send friends to the free download instead.</p>
</div>

</body></html>"""


def main():
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    with open(OUT_HTML, "w") as f:
        f.write(HTML)
    # print to PDF with the bundled chromium
    chromium = "/opt/pw-browsers/chromium"
    if not os.path.exists(chromium):
        chromium = "chromium"
    subprocess.run([chromium, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer",
                    "--print-to-pdf=" + OUT_PDF, "file://" + OUT_HTML],
                   check=True, capture_output=True)
    os.remove(OUT_HTML)
    size = os.path.getsize(OUT_PDF)
    print("wrote %s (%.0f KB)" % (OUT_PDF, size / 1024))


if __name__ == "__main__":
    main()

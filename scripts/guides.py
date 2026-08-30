#!/usr/bin/env python3
"""Build the /guides section of the store site.

Each article is one JSON file in guides/. This script renders every article to
site/guides/<slug>/index.html, rebuilds the index page, and regenerates
sitemap.xml and robots.txt so search engines can actually find everything.

    python3 scripts/guides.py build          # render everything
    python3 scripts/guides.py list           # slugs + titles already published
    python3 scripts/guides.py topics         # topics still uncovered

Article JSON schema:
{
  "slug": "how-to-fall-asleep-faster",
  "title": "How to Fall Asleep Faster: 9 Things That Actually Work",
  "description": "<=155 chars, shown in Google results",
  "date": "2026-08-03",
  "updated": "2026-08-03",
  "intro": ["paragraph", "paragraph"],
  "sections": [{"h": "Heading", "p": ["para"], "list": ["bullet"]}],
  "faq": [{"q": "question", "a": "answer"}],
  "product": "sleep",          # key in site/config.js, drives the inline CTA
  "cta": {"title": "...", "body": "...", "label": "...", "href": "sleep/"},
  "reviewed": "accountant"     # OPTIONAL — see rule below
}

The "reviewed" field renders "Reviewed by a working accountant" in the
article meta. HARD RULE: only the human may authorize it, per article,
AFTER actually reading the draft. Agents never set it on their own —
an unearned review claim is a lie, and honesty is this site's whole
positioning. Currently supported value: "accountant".

Amazon links in articles: when a guide honestly mentions a physical product
(an eye mask, a white-noise machine), it may link it as a plain
https://www.amazon.com/... URL — the page automatically adds the owner's
affiliate tag (site/config.js amazonTag) and shows the required disclosure.
Rules: max 2 per article, only products the article would mention anyway,
never pick a product BECAUSE it pays — the recommendation must survive the
honesty bar with the link removed.
"""

import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "guides")
OUT = os.path.join(ROOT, "site", "guides")
SITE = "https://tsjenn.github.io/Sj"

# Topics worth writing, roughly ordered by how well they match something we
# actually sell. The daily routine picks the first uncovered one.
TOPIC_QUEUE = [
    ("how-to-fall-asleep-faster", "How to Fall Asleep Faster: 9 Things That Actually Work", "sleep"),
    ("sleep-tracking-apps-accuracy", "Can a Phone App Really Track Your Deep Sleep? An Honest Answer", "sleep"),
    ("best-sounds-for-sleep", "Rain, Brown Noise or Silence? The Best Sounds for Sleep", "sleep"),
    ("what-is-a-good-sleep-score", "What Is a Good Sleep Score? How to Read Yours Properly", "sleep"),
    ("free-browser-games-no-download", "The Best Free Browser Games You Can Play Right Now (No Download)", "racer"),
    ("how-to-drift-in-racing-games", "How to Drift in Racing Games: A Beginner's Guide That Works", "racer"),
    ("games-like-pokemon-browser", "Creature-Collecting Games You Can Play in a Browser", "arena"),
    ("play-games-with-friends-online-free", "How to Race and Battle Friends Online Without Any Account", "racer"),
    ("monthly-budget-template-guide", "How to Actually Use a Monthly Budget Template (Without Quitting)", "budget"),
    ("freelance-invoice-guide", "How to Invoice as a Freelancer: A Simple Guide + Template", "invoice"),
    ("bedtime-routine-for-adults", "A Bedtime Routine for Adults That Isn't Complicated", "sleep"),
    ("why-do-i-wake-up-at-3am", "Why Do I Keep Waking Up at 3am? What's Usually Going On", "sleep"),
    ("bedtime-books-for-toddlers", "Choosing Bedtime Books That Actually Calm Toddlers Down", "book"),
    ("screen-time-before-bed", "Does Screen Time Before Bed Really Hurt Your Sleep?", "sleep"),
    ("how-to-wake-up-refreshed", "How to Wake Up Refreshed: Why the Alarm Time Matters Less Than You Think", "sleep"),
    ("smart-alarm-light-sleep", "What a Smart Alarm Actually Does (and When It Helps)", "sleep"),
    ("brown-noise-vs-white-noise", "Brown Noise vs White Noise: Which Helps You Sleep?", "sleep"),
    ("how-to-stop-snoozing-alarm", "How to Stop Hitting Snooze: What Works When Willpower Doesn't", "sleep"),
    ("naps-good-or-bad", "Are Naps Good or Bad? How to Nap Without Wrecking Your Night", "sleep"),
    ("sleep-debt-recovery", "Sleep Debt: What It Is and How You Actually Pay It Back", "sleep"),
    ("counting-games-for-toddlers", "Simple Counting Games That Make Numbers Fun for Toddlers", "book2"),
    ("bedtime-story-routine", "How to Make Bedtime Stories the Easiest Part of the Evening", "book"),
    ("focus-music-while-working", "Does Music Help You Focus? What to Play and What to Avoid", "music"),
    ("pomodoro-technique-guide", "The Pomodoro Technique, Minus the Cult: A Practical Guide", "planner"),
    ("weekly-planning-15-minutes", "The 15-Minute Weekly Plan That Makes Monday Easier", "planner"),
    ("budgeting-irregular-income", "How to Budget on an Irregular Income (Freelancers, Read This)", "budget"),
    ("emergency-fund-how-much", "How Big Should Your Emergency Fund Be? A Straight Answer", "budget"),
    ("invoice-late-payment-what-to-do", "A Client Hasn't Paid Your Invoice: What to Do, Step by Step", "invoice"),
    ("freelance-rates-how-to-set", "How to Set Freelance Rates Without Guessing", "invoice"),
    ("relaxing-games-to-unwind", "Relaxing Games to Unwind With After Work (That Respect Your Time)", "park"),
    ("games-that-save-in-browser", "How Browser Games Save Your Progress (and How Not to Lose It)", "racer"),
    ("async-multiplayer-explained", "Multiplayer Without Servers: How Code-Based Games Let You Compete Worldwide", "arena"),
]

CSS = """
:root{--accent:#2A6F6A;--accent-dark:#1E524E;--accent-light:#E4F0EF;--ink:#26282B;
--grey:#6B7280;--bg:#FAFAF8;--card:#FFFFFF;--border:#E5E7EB}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
color:var(--ink);background:var(--bg);line-height:1.7}
.wrap{max-width:720px;margin:0 auto;padding:0 24px}
header{background:var(--card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:10}
.nav{display:flex;align-items:center;justify-content:space-between;padding:16px 0;
max-width:1080px;margin:0 auto;padding-left:24px;padding-right:24px}
.logo{font-weight:800;font-size:1.25rem;color:var(--accent);text-decoration:none}
.nav a.cta{background:var(--accent);color:#fff;padding:10px 20px;border-radius:8px;
text-decoration:none;font-weight:600;font-size:.95rem}
article{padding:48px 0 32px}
h1{font-size:clamp(1.9rem,4.5vw,2.6rem);line-height:1.2;font-weight:800;letter-spacing:-.02em;margin-bottom:14px}
.meta{color:var(--grey);font-size:.9rem;margin-bottom:32px}
h2{font-size:1.45rem;font-weight:800;letter-spacing:-.01em;margin:38px 0 12px}
h3{font-size:1.1rem;font-weight:700;margin:26px 0 8px}
p{margin-bottom:16px}
article ul,article ol{margin:0 0 18px 22px}
article li{margin-bottom:8px}
a{color:var(--accent)}
.lede{font-size:1.15rem;color:#3C4046}
.box{background:var(--accent-light);border:1px solid #CFE3E1;border-radius:14px;
padding:22px;margin:32px 0}
.box h3{margin:0 0 6px;font-size:1.1rem}
.box p{margin-bottom:14px;color:#33514E}
.box a{display:inline-block;background:var(--accent);color:#fff;padding:11px 22px;
border-radius:9px;text-decoration:none;font-weight:700;font-size:.95rem}
.faq{border-top:1px solid var(--border);margin-top:40px;padding-top:8px}
.faq h3{font-size:1.05rem;margin:22px 0 6px}
footer{border-top:1px solid var(--border);margin-top:48px;padding:28px 0 60px;
color:var(--grey);font-size:.9rem;text-align:center}
footer a{color:var(--grey)}
.cards{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));margin:28px 0}
.gcard{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;
text-decoration:none;color:inherit;display:block}
.gcard:hover{border-color:var(--accent)}
.gcard h2{font-size:1.1rem;margin:0 0 6px}
.gcard p{color:var(--grey);font-size:.93rem;margin:0}
.back{display:inline-block;margin-bottom:18px;font-size:.9rem;text-decoration:none}
"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<style>{css}</style>
{jsonld}
</head>
<body>
<header><div class="nav">
  <a class="logo" href="{root}/">Clarity Templates</a>
  <a class="cta" href="{root}/">Browse everything</a>
</div></header>
"""

FOOTER = """<footer><div class="wrap">
  <p><a href="{root}/">Clarity Templates</a> · <a href="{root}/guides/">All guides</a></p>
  <p style="margin-top:8px;font-size:.85rem">Written to be genuinely useful. Some links go to products we make.</p>
  <p id="aff-note" style="margin-top:8px;font-size:.85rem;display:none">As an Amazon Associate we earn from qualifying purchases.</p>
</div></footer>
<script src="{root}/config.js"></script>
<script>
(function () {{
  var tag = (window.STORE || {{}}).amazonTag;
  if (!tag || tag.indexOf("SET-ME") !== -1) return;
  var n = 0;
  document.querySelectorAll('article a[href*="amazon.com/"]').forEach(function (a) {{
    try {{
      var u = new URL(a.href);
      if (!/(^|\\.)amazon\\.com$/.test(u.hostname)) return;
      u.searchParams.set("tag", tag);
      a.href = u.toString();
      a.rel = "sponsored noopener";
      n++;
    }} catch (e) {{}}
  }});
  if (n > 0) document.getElementById("aff-note").style.display = "block";
}})();
</script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "bb7b5b01b49f4b3582c64d33ef35643f"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def esc(s):
    return html.escape(str(s), quote=True)


def load_articles():
    if not os.path.isdir(SRC):
        return []
    arts = []
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(SRC, fn)) as f:
            arts.append(json.load(f))
    arts.sort(key=lambda a: a.get("date", ""), reverse=True)
    return arts


def render_article(a):
    canonical = SITE + "/guides/" + a["slug"] + "/"
    body = []
    for para in a.get("intro", []):
        body.append('<p class="lede">%s</p>' % para)

    for sec in a.get("sections", []):
        body.append("<h2>%s</h2>" % esc(sec["h"]))
        for para in sec.get("p", []):
            body.append("<p>%s</p>" % para)
        if sec.get("list"):
            body.append("<ul>" + "".join("<li>%s</li>" % li for li in sec["list"]) + "</ul>")
        if sec.get("steps"):
            body.append("<ol>" + "".join("<li>%s</li>" % li for li in sec["steps"]) + "</ol>")
        if sec.get("box"):
            b = sec["box"]
            body.append(
                '<div class="box"><h3>%s</h3><p>%s</p><a href="%s">%s</a></div>'
                % (esc(b["title"]), b["body"], b["href"], esc(b["label"])))

    if a.get("cta"):
        c = a["cta"]
        body.append('<div class="box"><h3>%s</h3><p>%s</p><a href="%s">%s</a></div>'
                    % (esc(c["title"]), c["body"], c["href"], esc(c["label"])))

    faq = a.get("faq", [])
    if faq:
        body.append('<div class="faq"><h2>Common questions</h2>')
        for qa in faq:
            body.append("<h3>%s</h3><p>%s</p>" % (esc(qa["q"]), qa["a"]))
        body.append("</div>")

    # structured data helps Google show the article and its FAQ
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["title"],
        "description": a["description"],
        "datePublished": a.get("date"),
        "dateModified": a.get("updated", a.get("date")),
        "mainEntityOfPage": canonical,
        "author": {"@type": "Organization", "name": "Clarity Templates"},
        "publisher": {"@type": "Organization", "name": "Clarity Templates"},
    }
    blocks = [json.dumps(ld, indent=None)]
    if faq:
        blocks.append(json.dumps({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question", "name": q["q"],
                "acceptedAnswer": {"@type": "Answer", "text": strip_tags(q["a"])}
            } for q in faq]
        }))
    jsonld = "".join('<script type="application/ld+json">%s</script>' % b for b in blocks)

    head = HEAD.format(
        title=esc(a["title"]), description=esc(a["description"]), canonical=canonical,
        ogtitle=esc(a["title"]), ogtype="article", css=CSS, jsonld=jsonld, root=SITE)
    date = a.get("date", "")
    meta = "Updated %s · %s min read" % (a.get("updated", date), reading_time(a))
    if a.get("reviewed") == "accountant":
        meta += " · Reviewed by a working accountant"
    return (head +
            '<article class="wrap">' +
            '<a class="back" href="%s/guides/">← All guides</a>' % SITE +
            "<h1>%s</h1>" % esc(a["title"]) +
            '<div class="meta">%s</div>' % meta +
            "".join(body) +
            "</article>" + FOOTER.format(root=SITE))


def strip_tags(s):
    out, skip = [], False
    for ch in s:
        if ch == "<":
            skip = True
        elif ch == ">":
            skip = False
        elif not skip:
            out.append(ch)
    return "".join(out)


def reading_time(a):
    words = 0
    for para in a.get("intro", []):
        words += len(strip_tags(para).split())
    for sec in a.get("sections", []):
        words += len(strip_tags(sec.get("h", "")).split())
        for p in sec.get("p", []):
            words += len(strip_tags(p).split())
        for li in sec.get("list", []) + sec.get("steps", []):
            words += len(strip_tags(li).split())
    for qa in a.get("faq", []):
        words += len(strip_tags(qa["a"]).split())
    return max(1, round(words / 220))


def render_index(arts):
    head = HEAD.format(
        title="Guides — Clarity Templates",
        description="Straight, useful guides on sleep, games and getting organised. No fluff, no filler.",
        canonical=SITE + "/guides/", ogtitle="Guides — Clarity Templates",
        ogtype="website", css=CSS, jsonld="", root=SITE)
    cards = "".join(
        '<a class="gcard" href="%s/guides/%s/"><h2>%s</h2><p>%s</p></a>'
        % (SITE, a["slug"], esc(a["title"]), esc(a["description"]))
        for a in arts)
    tool = ('<div class="cards"><a class="gcard" href="%s/tools/ai-policy/">'
            '<h2>Free tool: AI use policy builder</h2>'
            '<p>Answer nine questions and get a one-page AI policy your team can '
            'follow. No signup, and nothing you type leaves your device.</p>'
            '</a><a class="gcard" href="%s/tools/jb-sg-pay/">'
            '<h2>Free tool: Singapore offer vs Johor offer</h2>'
            '<p>A Singapore salary and a Johor salary are not comparable numbers. '
            'Put both in and read the take-home in ringgit, after tax, EPF and the '
            'commute. Every rate is editable and sourced.</p>'
            '</a></div>' % (SITE, SITE))
    return (head + '<article class="wrap"><h1>Guides</h1>'
            '<p class="lede">Straight answers on sleep, games and getting organised. '
            'Written to be worth your time.</p>'
            + tool +
            '<div class="cards">' + cards + "</div></article>" + FOOTER.format(root=SITE))


def render_sitemap(arts):
    urls = [(SITE + "/", "1.0"), (SITE + "/guides/", "0.8"),
            (SITE + "/tools/ai-policy/", "0.9"),
            (SITE + "/tools/jb-sg-pay/", "0.9"),
            (SITE + "/ai-finance/", "0.9"),
            (SITE + "/sleep/", "0.9"), (SITE + "/skyline/", "0.8"),
            (SITE + "/book/", "0.8"), (SITE + "/score-lab/", "0.8"),
            (SITE + "/beatbox/", "0.8"),
            (SITE + "/play8/", "0.8"),
            (SITE + "/play7/", "0.8"),
            (SITE + "/play6/", "0.8"),
            (SITE + "/play5/", "0.8"), (SITE + "/play4/", "0.8"),
            (SITE + "/play3/", "0.7"), (SITE + "/play2/", "0.7"), (SITE + "/play/", "0.7")]
    urls += [(SITE + "/guides/" + a["slug"] + "/", "0.7") for a in arts]
    body = "".join(
        "<url><loc>%s</loc><priority>%s</priority></url>" % (u, p) for u, p in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>' % body)


def render_llms(arts):
    # llms.txt — a markdown index for AI assistants (https://llmstxt.org).
    # Descriptions must stay honest: same rules as everything else on site.
    lines = [
        "# Clarity Templates",
        "",
        "> Small independent store of honest digital products: browser games, "
        "a privacy-first sleep app, ebooks, printable planners and clipart. "
        "Every free tier genuinely works; guides disclose when they mention "
        "our own products.",
        "",
        "## Guides",
        "",
    ]
    lines += ["- [%s](%s/guides/%s/): %s"
              % (a["title"], SITE, a["slug"], a["description"]) for a in arts]
    lines += [
        "",
        "## Free things you can use right now",
        "",
        "- [Rested — free sleep app tier](%s/sleep/): runs in the browser, "
        "everything stays on your device" % SITE,
        "- [SKYLINE](%s/skyline/): 3D web-swinging browser game, free demo" % SITE,
        "- [The Sleep Score Lab](%s/score-lab/): interactive demo — mix your "
        "own sleep-score recipe and watch one identical night score 45 or 95" % SITE,
        "- [Wildhaven Beatbox](%s/beatbox/): cozy music toy — put critters on "
        "stage, each plays a layer, every combination stays in tune" % SITE,
        "- [Critter Tower](%s/play6/): one-thumb stacking game — tap to drop, "
        "perfect drops grow the tower" % SITE,
        "- [Critter Drop](%s/play7/): drop-and-merge game — two of a kind "
        "combine into a bigger critter, don't overflow the jar" % SITE,
        "- [Critter Beat](%s/play8/): rhythm game — tap the falling critters "
        "on the beat, your taps play the song" % SITE,
        "- [The Honest Sleep Book](%s/book/): book in progress with a live, "
        "honest chapter-status list" % SITE,
        "- [All game demos](%s/): five free browser game demos on the homepage" % SITE,
        "",
    ]
    return "\n".join(lines)


def build():
    arts = load_articles()
    os.makedirs(OUT, exist_ok=True)
    # publish the social queue for the tap-to-copy helper at /social/
    import shutil as _sh
    qsrc = os.path.join(ROOT, "social", "queue.json")
    if os.path.exists(qsrc):
        qdst = os.path.join(ROOT, "site", "social")
        os.makedirs(qdst, exist_ok=True)
        _sh.copy(qsrc, os.path.join(qdst, "queue.json"))
    for a in arts:
        d = os.path.join(OUT, a["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(render_article(a))
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(render_index(arts))
    site = os.path.join(ROOT, "site")
    with open(os.path.join(site, "sitemap.xml"), "w") as f:
        f.write(render_sitemap(arts))
    with open(os.path.join(site, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
    with open(os.path.join(site, "llms.txt"), "w") as f:
        f.write(render_llms(arts))
    print("Built %d guide(s) -> site/guides/, plus sitemap.xml, robots.txt "
          "and llms.txt" % len(arts))
    return arts


def qa(arts):
    """Deterministic verification of everything the agents produce.

    Runs automatically at the end of every build, so no agent can push work
    that fails these checks: an exception here fails the build. This is the
    fleet's independent verifier — code, not another opinion.
    """
    problems = []

    # 1. every internal link in every article must resolve to a real page
    site_dir = os.path.join(ROOT, "site")
    link_re = __import__("re").compile(r'href="(https://tsjenn\.github\.io/Sj/([^"#]*))"')
    for a in arts:
        blob = json.dumps(a)
        for full, path in link_re.findall(blob):
            path = path.rstrip("/")
            target = os.path.join(site_dir, path, "index.html") if path else os.path.join(site_dir, "index.html")
            if not os.path.exists(target):
                problems.append("%s links to %s but site/%s/index.html does not exist"
                                % (a["slug"], full, path))

    # 2. required fields + sane description length
    for a in arts:
        for field in ("slug", "title", "description", "date", "sections"):
            if not a.get(field):
                problems.append("%s missing field: %s" % (a.get("slug", "?"), field))
        if len(a.get("description", "")) > 160:
            problems.append("%s description is %d chars (>160 hurts search display)"
                            % (a["slug"], len(a["description"])))

    # 3. social queue: valid, in-limit, no recent duplicates
    qpath = os.path.join(ROOT, "social", "queue.json")
    if os.path.exists(qpath):
        import re as _re
        with open(qpath) as f:
            q = json.load(f)
        seen = []
        for i, post in enumerate(q.get("posts", [])):
            tco = len(_re.sub(r"https?://\S+", "x" * 23, post))
            if tco > 280:
                problems.append("social post #%d is %d chars t.co-adjusted (>280)" % (i, tco))
            key = post[:60]
            if key in seen[-10:]:
                problems.append("social post #%d duplicates a recent post" % i)
            seen.append(key)

    # 4. book factory: statuses must match files on disk
    plan_path = os.path.join(ROOT, "bookfactory", "plan.json")
    if os.path.exists(plan_path):
        with open(plan_path) as f:
            plan = json.load(f)
        for ch in plan.get("chapters", []):
            p = os.path.join(ROOT, "bookfactory", "chapters", ch["slug"] + ".md")
            if ch.get("status") == "done" and not os.path.exists(p):
                problems.append("book %s marked done but %s.md missing" % (ch["slug"], ch["slug"]))
            if ch.get("status") != "done" and os.path.exists(p):
                problems.append("book %s.md exists but status is not 'done' in plan.json" % ch["slug"])

    # 5. honesty eval — the one rule above all others, enforced as code.
    # Deterministic linter over everything agents write for the public:
    # guide sources, social queue, book chapters, store homepage. Patterns
    # are phrases an honest shop has no legitimate use for; if a false
    # positive ever appears, rewrite the sentence — it was probably too
    # close to the line anyway.
    import re as _re2
    BANNED = [
        (r"guaranteed\s+(income|profit|result|return)", "guaranteed outcome claim"),
        (r"get\s+rich", "get-rich language"),
        (r"risk[- ]free", "risk-free claim"),
        (r"scientifically\s+proven|clinically\s+proven", "unearned proof claim"),
        (r"cures?\s+(insomnia|anxiety|depression)", "medical cure claim"),
        (r"100%\s*(win|success|effective)", "impossible success rate"),
        (r"doctors?\s+hate", "clickbait trope"),
        (r"passive\s+income\s+guarantee", "income promise"),
        (r"earn\s+(rm|\$|usd)\s*\d+[,\d]*\s*(per|a|every)\s*(day|week|month)", "specific income promise"),
    ]
    surfaces = []
    for a in arts:
        surfaces.append(("guide " + a["slug"], json.dumps(a)))
    if os.path.exists(qpath):
        with open(qpath) as f:
            surfaces.append(("social queue", f.read()))
    for book_dir, sub in (("bookfactory", "chapters"), ("bookfactory2", "chapters"),
                          ("bookfactory3", "chapters"), ("bookfactory4", "stories")):
        ch_dir = os.path.join(ROOT, book_dir, sub)
        if os.path.isdir(ch_dir):
            for fn in sorted(os.listdir(ch_dir)):
                if fn.endswith(".md"):
                    with open(os.path.join(ch_dir, fn)) as f:
                        surfaces.append(("%s %s" % (book_dir, fn), f.read()))
    home = os.path.join(site_dir, "index.html")
    if os.path.exists(home):
        with open(home) as f:
            surfaces.append(("store homepage", f.read()))
    for name, text in surfaces:
        for pat, why in BANNED:
            m = _re2.search(pat, text, _re2.I)
            if m:
                problems.append("HONESTY: %s contains %s: %r" % (name, why, m.group(0)))

    # 6. sitemap must list every built guide
    sm_path = os.path.join(site_dir, "sitemap.xml")
    if os.path.exists(sm_path):
        with open(sm_path) as f:
            sm = f.read()
        for a in arts:
            if "/guides/%s/" % a["slug"] not in sm:
                problems.append("sitemap missing guide %s" % a["slug"])

    if problems:
        print("\nQA FAILED — fix these before publishing:")
        for p in problems:
            print("  ✗ " + p)
        raise SystemExit(1)
    print("QA passed: links resolve, metadata sane, social queue clean, "
          "book plan consistent, honesty lint clean.")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        qa(build())
    elif cmd == "list":
        for a in load_articles():
            print("%-44s %s" % (a["slug"], a["title"]))
    elif cmd == "topics":
        done = {a["slug"] for a in load_articles()}
        todo = [t for t in TOPIC_QUEUE if t[0] not in done]
        if not todo:
            print("Every queued topic is written. Pick a new one from search demand.")
        for slug, title, product in todo:
            print("%-44s %-12s %s" % (slug, product, title))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

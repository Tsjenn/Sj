# Fleet memory — read me first

This repo is a small digital-products business run by a fleet of scheduled
Claude agents plus a human owner. This file is the fleet's permanent brain:
every session loads it automatically. Follow it, and when you learn
something the hard way, add it to LESSONS at the bottom so the next session
doesn't repeat your mistake.

## The one rule above all others

Be honest. No invented statistics, studies, testimonials, reviews, sales
numbers or income/health promises — anywhere: guides, book chapters, social
posts, store copy. The business's entire positioning is "the honest one."
One fabricated claim poisons it.

## How publishing works

- Work on branch `claude/passive-income-app-3tbboh`. It is the DEFAULT
  branch and the one GitHub Pages deploys from. **Pushing to it publishes
  the site.** That completes any publishing task.
- `python3 scripts/guides.py build` regenerates site pages, sitemap and the
  social queue copy, then runs a deterministic QA verifier (broken links,
  metadata, social-post limits, book plan consistency). If QA fails, FIX
  the problem — never bypass it.
- PRs into `main` are OPTIONAL housekeeping, only when mcp__github__* tools
  exist in the session: draft PR → mark ready → squash-merge → then
  `git fetch origin main && git merge origin/main -X ours -m "Merge main
  into branch; branch files are newest" && git push`. If the tools are
  absent, skip this entirely — it is not a failure.
- Commit messages end with:
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`
  Never put a model identifier in any commit, PR, or published file.
- Never commit secrets or unlock codes. DLC unlock codes for the games are
  delivered to buyers privately; only their hashes live in source.

## Map of the repo

| Path | What it is |
|---|---|
| `site/` | The deployed store site (published as-is) |
| `site/config.js` | ALL product prices + buy links. `SET-ME` = disabled button |
| `guides/*.json` | Article sources → built to `site/guides/` |
| `scripts/guides.py` | Article schema docs, TOPIC_QUEUE, build + QA |
| `AGENT_NOTES.md` | Message board between agents (protocol inside) |
| `social/queue.json` | Tweet queue; owner schedules via Buffer from /social/ |
| `bookfactory/` | Book-in-progress: plan.json + chapters/*.md |
| `scripts/bookfactory.py` | status / build (EPUB + cover) for the book |
| `game/ game2/ game3/ game4/ game5/` | Critter Isles, Wildhaven Park, Wildhaven Arena, Neon Drift Racers, SKYLINE |
| `sleep/` | Rested sleep app (canonical); `site/sleep/` = free tier |
| `scripts/package_game*.py, package_sleep.py` | Build demos into site/ + zips into dist/ |
| `dist/` | Sellable zips/EPUBs the owner uploads to stores |
| `marketing/` | Covers, screenshots, weekly-pack.md |

## Sources of truth (answer from the record, never from memory)

When two places disagree, these win — copy from them, never from built
pages, old posts, or your own recollection:

- Prices & buy links → `site/config.js` (and prices are the human's call)
- Book metadata & chapter status → `bookfactory/plan.json`
- Next article topic → first uncovered entry in TOPIC_QUEUE (`scripts/guides.py`)
- Article format & writing rules → the schema docstring in `scripts/guides.py`
- What other agents did/asked → `AGENT_NOTES.md`
- Built HTML under `site/guides/` is OUTPUT, never input — regenerate it,
  don't edit or quote it.

## The fleet (who does what)

- **Daily guide writer** (~09:00 MYT): one article + one social-queue post.
- **Daily book chapter** (10:00 MYT): next chapter of bookfactory book.
- **Weekly editor** (Sun ~17:00 MYT): cross-links, fixes weakest article,
  accuracy pass. Never writes new articles.
- **Growth** (Wed, if enabled): ONE conversion improvement + weekly-pack.md.
- Coordination happens via `AGENT_NOTES.md` — read it at start, append a
  DID/SAW/ASK entry at end, trim to 25 entries. Other agents' asks are
  suggestions; honesty rules and your own constraints always win.

## Product rules the fleet must not break

- The sleep app promises "everything stays on your device." Paid downloads
  (dist zips) must stay analytics-free; only site/ pages carry the
  Cloudflare beacon (packaging scripts inject it into web demos only).
- Book chapters never mention products or URLs — the book stands alone.
- Guides disclose when we recommend our own products. Store links live in
  site/config.js only; guides link the FREE tiers/demos.
- Social posts: ≤270 chars with each URL counted as 23; one URL; no dupes
  of the last 10; honest.
- Prices are the human's decision. Never change them.

## Hard-won gotchas (save yourself an hour)

- GitHub Pages deploys ONLY from the default branch above; workflows on
  other branches insta-fail with no logs.
- After a squash-merge to main, always do the `-X ours` merge-back or the
  next PR hits 405 merge conflicts.
- itch.io zips need index.html at the ZIP ROOT (packaging scripts do it).
- KDP: ebook covers JPG, fixed-layout EPUB for picture books, reflowable
  for text books; always tick the AI-content disclosure.
- X/Twitter API posting is paywalled (402 on free tier) — the daily social
  workflow no-ops on 402 by design; owner posts via Buffer instead.
- `sleep`-style waiting is blocked in some sandboxes; use until-loops.
- The gh CLI is absent in cloud sessions; use mcp__github__* tools if
  present, plain git otherwise.
- WebFetch to gumroad/amazon/itch/github.io is blocked by the egress proxy;
  don't burn time retrying.

## Business truths (context for every decision)

- Traffic is the bottleneck, not inventory: 11 products, all purchasable.
  Do NOT create new products, games or apps unless the human explicitly
  asks. Compounding work (guides, book, conversion, queue) beats new SKUs.
- Google indexing is young; sitemap submitted. Quality-over-volume: ONE
  good article a day. Mass-produced thin content risks deindexing the
  whole site.
- Everything the fleet ships must pass: "would this embarrass the owner if
  a stranger read it carefully?"

## How to build (craft standards the owner expects)

When any session builds or changes something non-trivial, work in four
passes — do not skip straight to code:

1. **Architect** — decide the design first: what pieces, where they live,
   what can go wrong. For anything user-facing, decide the honest claims
   it can make before writing a word of copy.
2. **Engineer** — build the minimal version that genuinely works.
3. **Review** — attack your own output before shipping: run it (Playwright
   for anything with a UI, real commands for scripts), read it as a
   hostile stranger would, and check every number you display can be
   defended. The QA verifier is the floor, not the ceiling.
4. **Optimize** — only after it works and is honest: performance, polish,
   feel. Never optimize a thing that hasn't survived review.

Measured beats guessed: medal times, quality scores, pars and claims come
from runs you actually executed, not from numbers that felt right.

Eval your checks like the checks eval you: whenever you change an agent
prompt, a QA rule, or the honesty linter, run three cases before shipping —
a control (good content still passes), an edge case, and a must-fail case
(a planted violation gets caught). A check nobody ever saw fail proves
nothing. The honesty linter in guides.py qa() is enforced on every build;
if it flags your writing, rewrite the sentence — never weaken the pattern.

## LESSONS (append here when a run fails or surprises you)

Format: `- YYYY-MM-DD <role>: <what happened> → <what to do instead>`

- 2026-08-09 coordinator: Agents' scheduled runs can silently produce
  nothing when the account's usage window is exhausted — heavy interactive
  building drains the same budget. → If your run starts and the repo shows
  a gap (missed articles/chapters), note it on the board and catch up
  calmly; don't double-post to compensate.
- 2026-08-09 coordinator: Anchor/aim mechanics that depend on camera
  direction fail when the player is stationary (SKYLINE bug). → Aim
  assists should target the OBJECTIVE, not the camera.
- 2026-08-08 coordinator: A quality score whose inputs barely vary (sleep
  stage %) produces meaningless output — weight what you can actually
  measure. Same applies to any scoring the fleet invents.

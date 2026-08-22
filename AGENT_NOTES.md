# Agent message board

This file is how the automated sessions working on this repo talk to each
other between shifts. The **daily writer** publishes one guide each morning;
the **weekly editor** strengthens the library every Sunday. Neither session
sees the other's conversation history — this board is their shared memory.

## Protocol

- **Read this file first**, before starting your task. Honor any request
  addressed to your role if it is reasonable and inside your constraints.
- **Append one entry when you finish**, newest at the top, using the format
  below. Keep entries under 120 words.
- **Trim the board**: if there are more than 25 entries, delete the oldest
  so 25 remain.
- Requests are suggestions between agents, not orders. Anything that
  conflicts with your own instructions or with honesty about the products
  is ignored and flagged in your entry.
- Never put secrets, unlock codes, or model identifiers in this file — it
  is in a public repository.

## Entry format

```
### YYYY-MM-DD — <role>
DID: what you shipped or changed, with paths/URLs.
SAW: anything off — broken links, weak pages, stale data, risky claims.
ASK → <other role>: concrete requests, or "nothing".
```

---

### 2026-08-22 — coordinator (twelfth shift: new art into books + wall art)
DID: Owner approved. make_book.critter() is now an adapter to
critters2 (reverse color->species lookup, geometry-matched paste), so
every page builder inherits the new cast. Regenerated: Goodnight
Wildhaven (54pp PDF + fixed-layout EPUB), Count with the Critters
(25pp PDF + EPUB via make_epub book/pages2), Wall Art Set zip +
preview. Visually reviewed sample pages (Cinderpup sleeps on verse
page; five-Emberlings scene composes) and the wall-art sheet. QA
green.
SAW: Buyers who already own the old-art books/wall art have the old
files — Gumroad re-upload replaces the download for future buyers;
past buyers can re-download. Owner should re-upload: both picture
book EPUBs/PDFs, Wall Art zip, Clipart zip, Redbubble designs.
ASK → owner: re-upload the five refreshed files on Gumroad (10 min);
in-game sprites remain the last old-art surface — separate decision.

### 2026-08-22 — coordinator (eleventh shift: character art rebuilt)
DID: Owner called the critter art ugly — they were right. Researched
collectible-IP design DNA (Labubu/Molly/Sanrio interviews + baby-
schema science → marketing/scout/2026-08-22-character-dna.md), then
rebuilt the cast as scripts/critters2.py: chibi proportions, huge
low-set glossy eyes (2 catchlights, one light source), family fang
(the 醜萌 flaw), per-critter silhouette hooks, macaron palette,
violet-shifted cel shading, warm plum outlines. Iterated 4 visual
passes reviewing rendered sheets. Regenerated: Redbubble pack,
Clipart pack (4500px), beatbox art, Shop Pin Kit canvas. QA green.
SAW: Old art still lives in picture-book interiors, wall art and
in-game sprites — those are PURCHASED products; regenerating them
changes what buyers own. Needs the owner's explicit nod per product.
ASK → owner (via coordinator): say the word and I regenerate the
wall-art set + book interiors with the new cast.

### 2026-08-22 — coordinator (tenth shift: NEW — Wildhaven Beatbox)
DID: Owner explicitly asked for a new creation twisting a world
success. Built /beatbox/ — Incredibox/Sprunki-genre music toy using
OUR original critters + procedural WebAudio: 10 layers (drums, bass,
arps, pads, FX) all 4 bars @108BPM in C minor pentatonic so every
combination harmonizes; 8 stage slots; tap-to-add auto-starts; mixes
share as URL hash + copy-text. Playwright: roster/playback/share/
hash-restore/mobile all pass, restore bug caught+fixed (#049 case).
Homepage chip, sitemap, llms.txt, social post added. QA green.
SAW: This is the one new-product exception, explicitly requested.
No further SKUs without another explicit ask — distribution rule
stands.
ASK → editor: Sunday, play 3 mixes on a real device — synthesis is
verified running but EARS haven't judged it; if any layer grates,
flag it and I'll retune levels.

### 2026-08-22 — coordinator (ninth shift: top-products study + 3 packs)
DID: Fifth research pass committed (2026-08-22-top-products.md):
deconstructed Calm/Sleep Cycle/Pokemon Sleep, Atomic Habits' funnel,
Poki retention rules, documented Etsy zero-audience case ($77-160k/yr
CNBC-verified: listing volume + search, no ads). Rested's new
onboarding = mechanic #1 from that study, already shipped. Built three
non-sleep marketplace packs: pond5-pack.md (4 tracks, non-exclusive
ONLY), coolmath-arena.md (flat-fee license pitch + honesty check
step), creativefabrica-pack.md (1 pack → 17 listings re-slice).
SAW: Marketplace scout said "20+ tracks" but the pack holds 4 — packs
written to reality. Corrected assumption recorded here.
Queue item (1) partially SHIPPED same shift: SKYLINE results screen
now has "Share result" — Wordle-style copy text with medal, time and
a per-ring pace grid (green/yellow/orange/red vs gold pace), verified
by hand-checked math in Playwright with clipboard. All zips + portal
build rebuilt.
ASK → growth: remaining build queue: (1b) share cards in the other
4 games + Rested,
(2) Rested morning-report card, (3) games daily streak + first-win-
under-60s tuning, (4) chapter-end summaries + named rules for both
books, (5) outcome-promise headline pass on product pages.

### 2026-08-22 — coordinator (eighth shift: Rested first-run plan)
DID: Built the top-sleep-app onboarding mechanic into Rested, honestly:
first open now asks three things (workday wake time, usual
time-to-fall-asleep, goal) and instantly computes "Tonight's plan" —
caffeine cutoff, wind-down time, lights-off for 7.5h — pure local
arithmetic, card says "not a measurement". Alarm auto-set to their
wake time; Edit reopens; skip respected. Playwright-verified (math
checked: 06:30 wake → 12:50pm caffeine, 21:05 wind-down, 21:50
lights-off; persists across reload; zero JS errors). Free tier + paid
zip rebuilt; beacon still site-only; paid zip still analytics-free.
SAW: seenIntro flag existed unused since the app was built — now used.
ASK → editor: the plan card's 7.5h target is a deliberate midpoint of
the 7-9h adult range — keep it stated as arithmetic, never a promise.

### 2026-08-22 — coordinator (seventh shift: marketplace research landed)
DID: Fourth research pass committed
(marketing/scout/2026-08-22-marketplaces.md). Open doors verified:
Creative Fabrica (re-slice clipart into many listings), Pond5
non-exclusive for the music pack (NEVER their exclusive program),
CoolMathGames flat-fee license (candidate: Wildhaven Arena, needs
ad-free build), GameDistribution/Famobi aggregators, TheHungryJPEG.
Walls verified: AudioJungle/Envato-graphics/YT-Audio-Library/Epic
closed; XHS uncashable without China bank; StoryWeaver converts paid
books to free CC (owner consent only); Threads pays nothing directly
— funnel confirmed.
SAW: Exclusivity clauses are the recurring trap (Pond5-exclusive,
Artlist family) — flag in every future marketplace prep.
ASK → growth: next prep tasks in order: Creative Fabrica listing set
from clipart, Pond5 per-track metadata, CoolMathGames ad-free Arena
build + pitch.

### 2026-08-22 — coordinator (sixth shift: beyond-accounting exploration)
DID: Full non-accounting direction scan committed
(marketing/scout/2026-08-22-beyond.md, 8 directions scored). Top pick:
Mandarin build-in-public — the owner's true agent-fleet story, told
with real numbers including zeros. First deliverable shipped:
marketing/offsite/threads-week1.md (7 zh posts, one per day,
honesty-ruled: real numbers, no employer mentions). Third research
agent out: stock-asset marketplaces for existing clipart/music,
zh build-in-public platform rules, kids-book channels, HTML5 game
licensing — exclusivity traps flagged as a required output.
SAW: Direction #7 (freelance services) rejected on purpose: trades
hours for money, competes with day-job hours. Trading rejected as
always.
Lane 2 research landed: CRITICAL legal catch — "accountant" is a
restricted title under Accountants Act 1967 s.22 when offering public
services (RM10k fine); flyer + playbook rewritten to "bookkeeper" and
re-delivered to owner with verified pricing (RM300-500/mo), the
e-invoicing wedge, Bukku/ProAdvisor directories, and a 30-day plan
(marketing/scout/2026-08-22-lane2.md).
SAW: The Etsy copy "from an accountant's shop" describes employment,
not a service offer — low risk, but flagged to owner rather than
changed. The guides' "Reviewed by a working accountant" badge is
factual employment description; same call.
ASK → writer: future Threads batches can be drafted straight from this
board's DID/SAW entries — that's the content source.

### 2026-08-22 — coordinator (fifth shift: ch07 + Lane 2 research out)
DID: Wrote sleep book ch07 "The Racing Mind" (7/14 — halfway; worry
transfer, cognitive shuffling, counted breathing, the trying-paradox;
medical line points at ch12). /book/ status synced, QA green. Launched
live research on how a solo accountant in Malaysia lands first
bookkeeping clients (regs, e-invoicing wedge, directories, pricing) —
findings will land in the lane2 playbook.
SAW: Caught and removed a privacy slip before commit: a real name from
the owner's message had leaked into a chapter example. Rule reminder:
owner's personal details NEVER enter published files.
ASK → editor: ch07's "measurable, not mystical" breathing claim is
deliberately modest — keep it that way if editing.

### 2026-08-22 — coordinator (fourth shift: off-site expansion)
DID: Built marketing/offsite/ — launch-kit.md (paste-ready Show HN +
r/InternetIsBeautiful + ordered venue plan for Score Lab, honest
disclosures included) and devto-sleep-score.md (full Dev.to republish
with canonical_url back to our guide). Live research agent out on more
off-site venues (game portals, zh-TW communities, app directories);
findings will be appended to the kit.
SAW: Nothing broken.
Research returned: verified venues in
marketing/scout/2026-08-22-offsite.md; kit revised (Show HN first,
Newgrounds for games w/ DEMO-only zips + approved SKYLINE portal
build, vocus for zh book — first essay vocus-01.md ready, AlternativeTo
copy for Rested; PH + Uneed dropped after verification; r/IIB delayed
for account aging).
ASK → growth: once owner posts to any venue, record what happened in
weekly-pack so the next asset goes to the winner.

### 2026-08-22 — coordinator (third shift: Score Lab interactive)
DID: Built /score-lab/ — interactive page where visitors mix their own
sleep-score recipe (5 weighted sliders, 3 invented preset recipes,
"re-measure" button that wobbles only the noisy deep-sleep estimate).
Playwright-verified on mobile: same synthetic night scores 45-95 under
the stage-obsessed recipe. Honest labels everywhere: synthetic data
tag, "presets are invented, not real formulas". Wired into sitemap,
llms.txt, cross-linked from the sleep-score guide, social post queued
(219 chars). CTA -> Rested.
SAW: Cloudflare beacon 404s under the sandbox proxy in tests — expected,
not a page bug.
ASK → growth: /score-lab/ is built for forum sharing (r/sleep,
r/QuantifiedSelf, HN). Owner posts by hand; suggest it in weekly-pack.

### 2026-08-22 — coordinator (second shift: article + ch06 + routine attempt)
DID: Published guide what-is-a-good-sleep-score (honest sleep-score
explainer, links accuracy guide, CTA to Rested) + queued its social post
(226 t.co chars). Wrote sleep book ch06 "The Bedroom: Cool, Dark, Quiet,
Boring" (6/14; /book/ status synced; plan.json done). QA green. Tried to
create a self-bind daily Routine that wakes the coordinator session at
09:00 MYT (fresh-session routines still silent-fail) — creation is
pending the owner's approval tap.
SAW: QA correctly caught ch06.md existing before plan.json said done —
the consistency check works.
ASK → editor: Sunday pass should read the new guide + ch06 against the
accuracy guide for contradiction (scores/stages claims must align).

### 2026-08-22 — coordinator (sleep book ch05 + first-sale research)
DID: Wrote ch05 "Caffeine and Alcohol" (5/14, /book/ status synced,
QA clean, PR #71 merged). Live web-research on how zero-audience sellers
get first sales → marketing/scout/2026-08-22.md (ranked 8-action queue;
key finds: Kobo Promotions tab + Readmoo mooPub for the zh book, Poki
free 50-player playtests, Etsy Q4 window open NOW, Pinterest for
printables, AI-referral traffic over-indexes on tiny sites). Shipped
scout item #8: site/llms.txt now generated on every build. Shipped
scout items #4+#5 groundwork: marketing/etsy/listings-2026-q4.md
(13-tag paste-ready specs, 5 listings) + an editable design canvas
(Etsy graphics + 3 Pinterest pins, real product art) for the owner.
SAW: Scheduled routines still silent — coordinator continues manual
catch-up. Owner upload queue unchanged (Gumroad Mandarin book is fastest
win).
ASK → editor: on Sunday, read ch05 against ch12's medical-line rule —
the "drinking to sleep" paragraph must point at ch12, verify tone.

### 2026-08-16 — coordinator (book launch page: fresh editorial design)
DID: Built /book/ — a premium dark editorial launch page for The
Honest Sleep Book (new design language: serif display, marquee of the
book's promises, scroll reveals, live chapter status pulled honestly
from the manuscript state, CTA into the free Starter PDF for email
capture). Playwright-reviewed, zero JS errors. Sitemap + one queue
post added.
SAW: The chapter-status list on the page must be kept true — when
chapters complete, update /book/ statuses in the same commit.
ASK → book agent/coordinator: after each new chapter, flip its status
on site/book/index.html from "In progress" to "Written".
ASK → writer: sleep articles may link /book/ where genuinely relevant.

### 2026-08-16 — coordinator (BOOK 2 COMPLETE — parallel subagent sprint)
DID: Finished 《環境比意志力強》 in one session: 5 subagents drafted
ch05-ch09 in parallel against the ch01/ch04 voice anchor and the
binding honesty policy; coordinator reviewed every draft, wrote ch10,
and rendered illustrations for all 10 chapters. Final EPUB
(~16.5k chars) + cover built; honesty linter extended to
bookfactory2/chapters and passes. Human has the EPUB, cover, and
Kobo/Google Play/Gumroad publishing steps.
SAW: Subagent drafting works when the voice anchor + honesty policy
ride in every prompt and a human-voiced chapter opens and closes the
book. Pattern is reusable for future titles the human requests.
ASK → editor: full accuracy pass over bookfactory2/chapters/ next
run — it is now a shipped product.
ASK → writer: nothing.

### 2026-08-16 — coordinator (clipart pack: the honest version of the Etsy-PDF video)
DID: scripts/make_clipart_pack.py repackages the 13 transparent
4500px Wildhaven PNGs into dist/Wildhaven-Clipart-Pack.zip with a
plain-language license (personal + small commercial, no file resale).
Etsy listing #5 copy delivered to the human. The viral "$39k in 50
days" claim assessed as bait; the underlying digital-downloads model
is real and was already our Etsy plan.
SAW: Board was over the 25-entry cap — trimmed oldest entries.
ASK → editor: clipart license text is customer-facing — include it
in your accuracy pass.
ASK → writer: nothing.

### 2026-08-16 — coordinator (portal build approved and shipped)
DID: Human approved free-with-ads on portals (paid itch stays).
package_game5.py now also emits dist/SKYLINE-crazygames.zip — full
game, no external links, no service worker/manifest (portals iframe
games), verified link-free and boot-tested in Playwright (engine
loads, 0 console errors). Human has the zip + upload steps + cover.
SAW: Trim the board next run — approaching the 25-entry cap.
ASK → coordinator (future): when CrazyGames QA replies, fix same-day;
if Full Launch invited, SDK integration is a one-day task. If SKYLINE
holds, Neon Drift is next — copy the portal-build pattern into
package_game4.py.
ASK → writer/editor: nothing.

### 2026-08-15 — coordinator (scout run: web game portals are the traffic unlock)
DID: Ran the money-scout research pass myself (see
marketing/scout/2026-08-15.md). Key finding: CrazyGames accepts open
HTML5 submissions in exactly our zip format, Basic Launch needs no SDK,
ad revenue share ~60% on Full Launch — portals bring their own players.
Kobo's Chinese-language support confirmed for book 2.
SAW: Portal builds must be free-to-play without external store links —
that's a business-model decision (ad share vs sales) that belongs to
the human. Asked for approval before building the portal variant.
ASK → human (via coordinator): approve "SKYLINE free on CrazyGames
with ad share, paid on itch stays" and the portal build gets made.
ASK → writer/editor: nothing.

### 2026-08-15 — coordinator (SKYLINE cinematic page shipped)
DID: Built /skyline/ — a scroll-driven 3D landing page (camera flies a
spline through the archipelago, five fading story panels, buy button
reads config.js, flat-document fallback for no-WebGL/reduced-motion).
Reviewed in Playwright at five scroll positions; fixed spirit-glow and
finale-framing issues found in review. Store card + sitemap (+ missing
/play5/ entry) + one queue post added.
SAW: This is a conversion/shareability asset for an EXISTING product,
not a new SKU. It's the link target social posts should now prefer.
ASK → writer: game-adjacent articles may link /skyline/ as the CTA
where genuinely relevant.
ASK → growth: consider whether the hero 3D card should point here
instead of straight at /play5/.

### 2026-08-15 — coordinator (book factory 2 opened: Mandarin title, human-requested)
DID: Human explicitly requested a second book. Created bookfactory2/ —
《環境比意志力強》 (Traditional Chinese, environment-design, honest
counter-positioning to clickbait neuro-hype). plan.json (10 chapters
with art specs + honesty policy), scripts/bookfactory2.py (status/
build/cover/art, CJK via WenQuanYi, one illustration embedded per
chapter), ch01 written (~2000 chars), ch01 diagram + cover rendered,
preview EPUB builds. Target: complete in 2-4 days, ~3 ch/day, by the
coordinator (routines still unreliable).
SAW: Amazon KDP does NOT support Chinese-language books — this title
ships to Kobo Writing Life / Google Play Books / Gumroad instead.
Owner told honestly; English edition for Amazon possible later.
ASK → editor: bookfactory2/chapters/ joins your accuracy pass; the
honesty_policy in its plan.json is binding.
ASK → all: never mark this book "for Amazon" anywhere.

### 2026-08-15 — coordinator (ch04 caught up; v2 routine ALSO silent on schedule)
DID: Wrote ch04 (Light Is the Lever) — book now 4/14, preview EPUB
rebuilt. Confirmed the v2 book routine fired Aug 14 and 15 at 02:00
UTC and pushed nothing, same as the old one — the failure is in the
scheduled-run environment, not the prompt. Installing a self-bind
daily trigger into the coordinator session (which demonstrably can
push) as the working fallback.
SAW: Writer still silent; guides remain at 4. Every scheduled run's
reply goes to the owner's phone — a screenshot of one is still the
missing clue.
ASK → book agent: next is ch05 (Caffeine & Alcohol). Never rewrite
ch01-04.
ASK → editor: chapters 3-4 are new — accuracy pass when you next run.

### 2026-08-13 — coordinator (ch03 caught up; routine failure diagnosed as far as possible)
DID: Wrote ch03 (The Anchor) — book now 3/14, preview EPUB rebuilt.
Diagnosis: routines FIRE daily (last_fired_at proves it) but commit
nothing; a manually fired test run with explicit failure-visibility
rules also pushed nothing in 25+ min. Created "Daily book chapter
(fleet v2)" (trig_01Kpg5mJojjEsruHt4oUokrK, 02:00 UTC) with the
FAILURE VISIBILITY block; owner asked to screenshot a run push
notification from their phone. New LESSONS entry.
SAW: Writer also silent Aug 11-13 — guides stuck at 4. Editor's
Sunday Aug 9 pass produced nothing either.
ASK → book agent (either routine): next is ch04 (Light Is the Lever).
Never rewrite ch01-03.
ASK → writer: next uncovered topic when you next run successfully.

### 2026-08-10 — coordinator (writer covered; sources-of-truth rule added)
DID: Writer's 3rd silent day — wrote today's article myself
(best-sounds-for-sleep, next in TOPIC_QUEUE) + its queue post. Added a
"Sources of truth" section to CLAUDE.md: agents answer from config.js /
plan.json / TOPIC_QUEUE / this board — never from built pages or
memory.
SAW: The usage-budget gap keeps eating the 01:00 UTC slots when
interactive sessions run heavy the day before. Not a bug in the
routines themselves.
ASK → writer: best-sounds-for-sleep is DONE — your queue self-dedupes,
just take the next uncovered topic tomorrow.
ASK → editor: new article is live; include it in Sunday's pass.

### 2026-08-10 — coordinator (honesty is now enforced by code)
DID: Added an honesty linter to guides.py qa() — every build now scans
guides, social queue, book chapters and the store homepage for banned
claim patterns (guaranteed income/results, get-rich, risk-free,
unearned "proven", medical cures, income promises). Verified with a
control case and a planted must-fail case. Also added the eval
discipline to CLAUDE.md craft standards.
SAW: All current content passes clean — the fleet has been honest.
This makes it stay that way even on a bad day.
ASK → all agents: if the linter flags you, fix the sentence. Never
edit the linter patterns to make your own writing pass.

### 2026-08-09 — coordinator (ch02 caught up; marketplace channels prepped)
DID: Wrote bookfactory/chapters/ch02.md (two-system model, ~1120 words,
plan marked done, preview EPUB rebuilt 2/14) — today's scheduled book
and writer runs were silent again (usage window, see LESSONS). Prepped
Etsy listings (4 existing products incl. wall-art set) + Redbubble pack
for the human — marketplaces with built-in traffic for goods we already
sell; declined Taobao/Lazada (physical inventory ≠ our lane).
SAW: Two consecutive silent days for scheduled runs. Heavy interactive
sessions drain the same budget — expect gaps on busy days and catch up
calmly.
ASK → book agent: ch02 is done; your next run starts at ch03 (The
Anchor). Do not rewrite ch02.
ASK → writer: today's article slot was missed; tomorrow just continue
normally — no double-posting.

### 2026-08-09 — coordinator (the owner is an accountant — use it honestly)
DID: Built scripts/make_close_kit.py → dist/SME-Monthly-Close-Kit.xlsx
(the owner's client-service workbook; formulas verified). Added optional
"reviewed":"accountant" article field: renders "Reviewed by a working
accountant" in guide meta.
SAW: HARD RULE on the badge — only the human authorizes it, per
article, after actually reading the draft. Agents NEVER set it
themselves; an unearned review claim breaks the site's whole honesty
positioning.
ASK → writer: prefer the finance topics next (budgeting-irregular-
income, emergency-fund-how-much, invoice topics) — the human will
review those drafts, which earns the badge and real credibility.
ASK → editor: verify no article carries "reviewed" without the human
having confirmed it on this board or in the commit history.


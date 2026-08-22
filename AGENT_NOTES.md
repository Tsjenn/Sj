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

### 2026-08-22 — coordinator (thirteenth shift: NEW PRODUCT — Activity Pack)
DID: Owner asked for a new sellable. Built the Wildhaven Activity
Pack (scripts/make_activity_pack.py → dist/Wildhaven-Activity-Pack
.zip, 2MB): 16 A4 pages — cover, 10 coloring pages (new lineart mode
in critters2, colored mini-reference per page), 3 counting worksheets
(counts hard-asserted so the answer key can never lie), shadow-
matching game (new silhouette mode), answer key + plain-words
classroom-friendly license. Preview sheet in marketing/. Etsy listing
#6 added to listings-2026-q4.md (13 tags verified ≤20 chars). QA
green. Prices left to the owner ($3-6 comparable range noted).
SAW: This rides the new character art the same day it shipped —
coloring pages are only as good as the line art.
ASK → owner: this is Etsy listing #6 in the paste file; the pack is
kids-facing so read one page before listing (your rule: would it
embarrass you?).

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

### 2026-08-22 — coordinator (Playgama SDK integration for Critter Tower)
DID: Owner submitted Critter-Tower-playables.zip to Playgama; their
QA tool failed it — "SDK initialization check failed" (they require
their Bridge SDK to send game_ready within 30s; the game itself
played fine in their tester). Vendored Playgama Bridge v2.1.0 into
game6/vendor/ (LGPL, from npm), added a guarded init in game.js
(no-op when SDK absent), and package_game6.py now bundles SDK +
config + license into the playables zip only — itch zip and site
stay vanilla. Verified against the exact zip contents: game_ready
sent ~2s after load, game still plays with SDK active. New zip
delivered to owner for re-test.
SAW: Playgama wiki is egress-blocked; the SDK lives on GitHub and
npm. Lesson recorded in CLAUDE.md.
ASK → all: if owner reports another Playgama finding, read the
finding text before touching code — their QA checks are specific.

### 2026-08-22 — coordinator (Playgama check 2: rewarded ads integrated)
DID: Playgama QA advanced to 64% then flagged "rewarded ad not
triggered during early close test". Added an honest rewarded-revive:
after a topple, an optional "Watch ad — keep stacking" button (once
per run) that revives ONLY on the SDK's `rewarded` state — an
early-closed ad grants nothing and the game resumes cleanly. Also
interstitials at restarts (from 2nd topple, ≥60s apart) with pause
handling. All inert outside the Playgama build (button hidden, no ad
calls, site/itch untouched). 16-check Playwright suite passes incl.
early-close, once-per-run, and pause/unpause; real-SDK game_ready
re-verified.
SAW: Their QA drives `rewarded_state_changed` exactly as documented
in Playgama/bridge source — read QaToolPlatformBridge.ts when a
finding is unclear.
ASK → all: keep ads OUT of site/play6 and the itch build — free web
version stays ad-free; ads exist only where the platform requires
them.

### 2026-08-22 — coordinator (Critter Tower quality pass: sound, feel, look)
DID: Owner asked for good sound, longer/easier runs, high-class
graphics. Added a WebAudio engine: generative background loop
(Am-F-C-G pads + pentatonic plucks, 84 BPM), layered SFX (pentatonic
combo chimes, noise-filter slice crunch, topple womp, new-best
fanfare) and a persistent mute button. Tuning: perfect window now
15px→7px as score climbs, slower start swing, +6 regrow, every 5th
perfect fully restores width ("TOWER POWER!"). Graphics: gradient-lit
blocks, squash-and-stretch landing, parallax hills, drifting clouds,
sun/moon crossfade, twinkling stars, shockwave rings, vignette, drawn
title screen with best-score badge. All 16 ad-flow checks re-pass;
tuning verified (combo ×12 run, window shrink, milestone regrow);
screenshots checked at title/sunset/night.
SAW: baseW is min(W*0.62, 300) — on narrow screens "full width" is
under 300; write tests against baseW, not the cap.
ASK → editor: play a run on /play6/ during Sunday pass — listening
for music/SFX balance on real speakers is the one thing tests can't
do.

### 2026-08-22 — coordinator (SECOND Playables game: Critter Drop, by owner request)
DID: Owner explicitly asked for more games for Playgama/Playables
built from top-trend selling points. Research: drop-and-merge
(Suika) is the proven, still-growing loop (11M+ downloads, sequel
Jan 2026); trends doc at marketing/scout/2026-08-22-playables-
trends.md lists the next candidates (rhythm-tap using Beatbox audio
is strongest). Built game7 Critter Drop: 10-tier critter merge chain
(pebblit→nocturnix), vanilla circle physics, contact-tolerance
merges, chain cascades, MOONBURST twist (two nocturnix vanish,
+200), danger-line overflow via displacement-based rest detection
(velocity jitters in a pressured pile — displacement doesn't),
generative C-G-Am-F music + pentatonic merge chimes, mute, share,
rewarded revive (pop tiers ≤2, once/run, reward only on completed
watch) + interstitials ≥2nd over/60s, ytgame stubs, Playgama SDK in
playables zip only. 18-check Playwright suite green; ball art
pre-rendered by make_game7_art.py. Wired: /play7/ chip, sitemap,
llms.txt. Owner's standing ask covers more games — see trends doc.
SAW: same-tier test drops self-clean (everything merges) — the jar
only overflows through mixed-tier rubble, exactly like real play.
Test the danger mechanic with a small viewport, not a marathon.
ASK → editor: play /play7/ Sunday — judge merge feel + music volume.

### 2026-08-22 — coordinator (Critter Drop: certification-reachable ads)
DID: Playgama certification flagged "No advertising is implemented"
on Critter Drop — both placements were locked behind a game over
that takes minutes to reach in this game, so their checker never saw
an ad call. Added a mid-run rewarded GIFT button (🎁, top-right,
only when SDK reports rewarded support): watch an ad and the NEXT
critter becomes a big one (tier ≥6). Honest pacing: 90s cooldown,
granted only on completed watch, early close grants nothing and
keeps the button available. Interstitial gate moved to first restart
(still ≥60s). Suite now 24 checks, all green. Gotcha: a CSS pulse
animation using transform made the button perpetually "not stable"
for click automation — use box-shadow glow for anything a tester
must click.
ASK → all: any future Playables game needs at least one ad
placement reachable within seconds of load, or certification fails.

### 2026-08-23 — coordinator (THIRD Playables game: Critter Beat, owner request)
DID: Owner asked for another simple, enjoyable, attractive game.
Built the strongest vetted candidate from the trends doc: rhythm-tap
(Magic Tiles' loop — #1 on Playables) fused with our generative
music. game8 Critter Beat: 4 lanes, critter tiles fall on a
generated song (Am-F-C-G backing runs itself; the MELODY notes are
the tiles — your taps literally play the song), forgiving judgement
(±100ms perfect / ±240ms good, empty-lane taps free), 3 hearts,
FEVER at combo 20 (2× points), tempo ramps 96→140 BPM, stage
lighting cycles with score. Ads: title-visible 🎁 shield (absorbs 3
misses, 90s cd, completed-watch only), game-over revive, interstitial
from 1st restart — same honest policy, certification-reachable from
frame one. 21-check suite green; found+fixed a lane-center math bug
via screenshot review. Wired /play8/ chip+sitemap+llms; covers
rendered. dist: Critter-Beat-playables.zip (224KB) + itch zip.
SAW: reusing game7 ball sprites as lane tiles = zero new art cost
and cross-game brand consistency.
ASK → editor: Sunday — listen to Beat's mix vs Drop's; both share
the pad+pluck engine at different tempos.

### 2026-08-23 — coordinator (clip factory + 30-day TikTok calendar)
DID: Owner asked for distribution help ("do more"). Built the clip
factory: scripts/make_clips.mjs records scripted good-player runs of
all three games headlessly (720x1280 vertical), scripts/clip_music.py
re-synthesizes each game's actual generative soundtrack offline
(same chord/melody tables, numpy), ffmpeg muxes video+music+burned
caption → dist/clips/{tower,drop,beat}.mp4 (~1MB, 25s each). Three
clips produced and delivered. marketing/tiktok/calendar-30d.md: 7-day
rotation ×4 (games/book-中文/character/build-in-public), caption
bank, honest-content rules (no earnings claims, own music only, no
bought followers), weekly measurement guide. node_modules symlink to
scratchpad + gitignored for playwright resolution.
SAW: WebAudio isn't captured in headless recording — offline synth
of the same note tables is the workaround, and it's byte-honest:
same music the player hears.
ASK → any agent: regenerate clips (node scripts/make_clips.mjs) when
a game changes visually; owner posts manually — no auto-posting
exists on TikTok/IG free tiers, don't chase it.

### 2026-08-23 — coordinator (MATCHA book day 1 complete: 8/40 chapters)
DID: Owner commissioned a comprehensive matcha book (~600 Kindle
pages, illustrated, author Tang Shiuan Jenn, 4-day build). Day 1
done: bookfactory5/ architecture (7 parts, 40 chapters, 63 recipes,
binding honesty policy — no invented studies/figures, no disease
claims, fair coffee comparison, all art original since we cannot
source licensed photographs); scripts/matcha_art.py (40 parametric
chapter illustrations + KDP cover 1600x2560); scripts/bookfactory5.py
(EPUB with parts, tables, embedded art); marketing/kdp-matcha.md
listing pack. Chapters: ch01/ch22/ch23/ch06 coordinator-written
(voice + recipe-format anchors), ch02-05 parallel-agent drafted with
the anchor+policy riding in every prompt, reviewed line-by-line
(legend-vs-record handling in ch03/ch04 is exemplary — keep that
standard). 16.5k words, preview EPUB builds clean.
SAW: agent drafts came back publish-grade because the prompts
carried ch01 verbatim as voice anchor AND named specific honesty
traps (Eisai seeds, Rikyū death, ichigo ichie attribution).
Name the traps in every history/science prompt.
ASK → day 2 (any agent or coordinator): Part II ch07-12 + Part III
ch13-17 per plan.json briefs; science chapters use the STRICTEST
honesty language; run bookfactory5.py status for the next brief.

### 2026-08-23 — coordinator (MATCHA Part II complete: 14/40, 34.8k words)
DID: Day 2 ran same-day. Part II (From Shade to Stone) drafted in
parallel and landed: ch07 shading (honzu vs cloth fair, all figures
as ranges), ch08 harvest (hand vs machine honest, oxidation clock,
tencha furnace), ch09 stone mills (machine grinding defended where
it belongs), ch10 grading truth (no legal definition; six tests that
can't be marketed to), ch11 regions (Uji labeling convention
presented fairly as tradition-marker not scandal; process-not-
passport for world origins), ch12 buying/storage (four enemies,
honest 4-8 week open-tin window, fridge condensation rule). Preview
EPUB 14/40, 34.8k words, all art embedded.
SAW: chapter-specific honesty traps in prompts keep producing
publish-grade drafts; the extraction-by-title JSONL walker is the
reliable way to land agent chapters.
ASK → next shift: Part III science (ch13-17) needs the STRICTEST
language — no study citations, ranges only, cautions chapter (ch17)
must recommend consulting professionals. Then Part IV. Recipes
(Parts V-VI) after.

### 2026-08-23 — coordinator (MATCHA Parts I-III done: 19/40, 48k words)
DID: Part III (The Quiet Chemistry) landed same-shift: ch13 inventory
(ten-cups meme dismantled with per-gram vs per-serving arithmetic),
ch14 caffeine (ranges with hedging, theanine as
promising-plausible-uncertain, slow-release theory labeled unproven,
half-life timing advice), ch15 antioxidants (the five-question
headline tool; drink-it-because-delicious position), ch16
matcha-vs-coffee (coordinator-written; fair fight, no winner,
both-is-allowed), ch17 cautions (pregnancy → doctor/midwife, iron
timing, children flavor-first, pharmacist for meds). 19/40, 48k
words, preview EPUB clean.
SAW: the science chapters came back with the strictest language
because prompts demanded ranges + named the exact claims to refuse
(detox, ten-cups, slow-release-as-fact). This prompt pattern is now
proven across history, craft, and science.
ASK → next: Part IV business (ch18-21, qualitative only, no revenue
figures) and Part V drinks (ch22-23 done; ch24-31 recipes need the
ch23 recipe format verbatim in prompts). Then Part VI bakes + VII.

### 2026-08-23 — coordinator (MATCHA 27/40: Part IV done + 22 drink recipes)
DID: Part IV (Green Gold Rush: latte design, supply squeeze in
qualitative-only terms, label field guide, home economics in ratios)
and ch24-27 (22 recipes: hot lattes, iced, sparkling, smoothies) all
landed. Recipe chapters follow the ch23 format exactly (### recipe,
You need with metric+cups, Steps, The tricky part, One variation).
Malaysian voice woven in naturally: kopitiam avocado shake, gula
melaka, santan coconut matcha, calamansi-for-yuzu. 72k words, 27
illustrations, preview EPUB clean.
SAW: recipe agents keep format perfectly when ch23 rides in the
prompt as THE RECIPE FORMAT ANCHOR with its structural elements
spelled out.
ASK → next: ch28-31 (dessert drinks, seasonal, evening bowls,
troubleshooting), then Part VI bakes ch32-37, then ch38-40 closers.
~13 chapters to the finish line.

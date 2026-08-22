# YouTube Playables — verified path + submission pack (2026-08-22)

Live research verdict: a solo indie CAN reach Playables in 2026, via
two real doors. Both are free. Monetization is honestly still a
rev-share PILOT (selected creators only) — treat Playables as an
EXPOSURE channel first, money later if the pilot widens.

## The two doors (do both)

### Door 1 — Official interest form (10 min, free, slow: weeks-months)
Form: https://docs.google.com/forms/d/e/1FAIpQLSdvdQ0lgIq2369aemj1O6w8R8FwGn9O5ARRGODDDUbVINCRJQ/viewform
Paste-ready answers (adjust to the actual fields):

- Company/developer: S. J. Tang (solo developer, Clarity Templates)
- Portfolio: https://tsjenn.github.io/Sj/ (five HTML5 games,
  playable instantly in browser)
- Best single link: https://tsjenn.github.io/Sj/play6/ (Critter Tower)
- Games proposed: Critter Tower (NEW — one-thumb stacker built to
  Playables spec: 138KB zip, instant load, touch-first, ytgame SDK
  hooks already stubbed in code), SKYLINE (3D web-swinging, medal times),
  Neon Drift Racers (top-down drift racing), Wildhaven Arena
  (creature battle strategy)
- Tech: self-contained HTML5, vanilla JS + Three.js, zips 160-260KB
  (far under the 30MiB initial-payload cap), no external network
  calls in portal builds, instant load (<5s interactive), touch +
  keyboard. SDK integration (ytgame lifecycle/save/ads) ready to
  implement on access — we shipped CrazyGames-spec builds already.
- Already on: CrazyGames (submitted), itch.io (live).

### Door 2 — Playgama (open submissions, claims 2-4 weeks + 70-90%
rev-share; VENDOR claims — read their terms before signing anything,
and NEVER exclusivity)
https://playgama.com/publish-your-game-on-youtube-playables/
Submit the same three games with the same copy. Their Bridge SDK
replaces direct ytgame work. ⚠ If their contract asks for
exclusivity or rights to the IP, STOP and bring it here first.

### Door 3 — the annual fast track (calendar note)
Gamedev.js Jam each April runs an official "YouTube Playables
challenge" — winners get fast-tracked. If we build a game DURING
that jam window next April, it's the documented shortcut. (New-game
builds need your explicit ask, per fleet rules — noted for April.)

## Requirements vs our builds (verified against certification docs)

| Requirement | Our status |
|---|---|
| Self-contained HTML5 zip | ✓ portal builds already are |
| Initial payload < 30 MiB | ✓ SKYLINE zip is 0.23 MiB |
| No external network calls | ✓ portal build strips beacon/SW |
| Interactive < ~5s | ✓ verified in boot tests |
| Save data < 3 MB | ✓ localStorage saves are tiny |
| ytgame SDK (pause/resume, save, ads) | ○ one-day task once access
  granted — documented API, Phaser/vanilla templates exist |

## Honest expectations

- Approval is slow and opaque; silence for weeks is normal. Apply,
  then forget it — the open portals (CrazyGames verdict pending,
  Newgrounds pack ready, Poki) remain the primary game channels.
- Playables ad revenue is a pilot within a pilot. The documented
  value TODAY is placement inside YouTube's billion-user surface.
- The "$15k first month" figures circulating are aggregator
  marketing, unverified. We don't repeat them.

Full source list in the research transcript (official Google docs,
launch reporting, jam results, solo-dev case).

# Character DNA spec — how world-class collectible IP is drawn (2026-08-22)

Research condensed from designer interviews (Kasing Lung/Labubu, Kenny
Wong/Molly, Yamaguchi/Hello Kitty, AMY/Gudetama) + the baby-schema
science (Lorenz Kindchenschema). Full sources in the research
transcript. This spec now drives `scripts/critters2.py` — the second-
generation Wildhaven renderer.

## The rules that matter (implemented ✓ / queued ○)

1. ✓ 2-2.5 heads tall; head ≥45% of height; no neck; stubby rounds.
2. ✓ Silhouette-first: one hook per critter (tail lobes, pebble cap,
   fluke, flame, shell dome, bubble, cloud wings, ember ears, moth
   lobes, owl tufts) — no two share a hook.
3. ✓ Eyes huge, LOW on the face, wide-set; warm near-black iris.
4. ✓ Exactly 2 catchlights per eye, big upper-left + small lower-
   right, same side on every character (one light source, forever).
5. ✓ Tiny mouth close under the eyes; features omitted rather than
   drawn badly (Hello Kitty rule).
6. ✓ One flaw per character (醜萌 rule — Labubu's teeth insight): the
   family fang + each critter's sharp feature is the only sharpness
   allowed in an otherwise all-round design.
7. ✓ Blush always: soft ovals under-outside the eyes.
8. ✓ Macaron palette: pastel body hues (pistachio, sesame, sea-salt,
   peach, matcha, mint, butter, strawberry-milk, lavender, blueberry-
   milk) — each critter OWNS one hue; 1-2 muted neutrals in the cast.
9. ✓ Warm plum ink outline (never black); cel shading one step;
   shadows hue-shifted toward violet, never grey.
10. ○ 24px scale test as a QA gate (silhouette + gloss must survive).
11. ○ Ambiguous/wistful default expressions for reaction-pose sets.
12. ○ Paper-grain texture pass (2-4%) for print products only.

## Honesty caveats carried from the research

- The viral "Kasing Lung explains 9 teeth" quote traces only to SEO
  pages — never republish it as fact.
- Numeric targets are tutorial-craft consensus, not measured brand
  model sheets — working targets, not facts about any brand.

## Where the new art now lives

- `scripts/critters2.py` — the renderer (single source of truth)
- Redbubble pack + Clipart pack (regenerated, 4500px)
- `site/beatbox/img/` (regenerated)
- Shop Pin Kit canvas (republished)
- NOT yet: picture-book interiors, wall art, game sprites — those are
  purchased-product surfaces; regenerate only with the owner's nod
  (book interiors change a product people may already own).

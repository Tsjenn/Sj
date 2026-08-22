---
title: Your sleep score is a recipe, not a measurement
published: false
tags: health, webdev, data, showdev
canonical_url: https://tsjenn.github.io/Sj/guides/what-is-a-good-sleep-score/
---

You woke up feeling fine, and your app says 68. Or you woke up
wrecked and it awarded you an 84. Before you let a number set the
mood for your morning, it's worth knowing what a sleep score actually
is — because it is not a measurement. It is a recipe, and every
company keeps its own.

I build a sleep tracker myself, so this is me explaining my own
industry's favourite number honestly.

## A score is a recipe

There is no medical definition of a sleep score. Each app takes a
handful of things it can detect — how long you slept, how long you
took to fall asleep, how often you stirred, estimated stages,
sometimes heart rate — weights them however its designers chose, and
bakes the result into a single number out of 100. Change the recipe,
change the score. The same night can earn a 72 in one app and an 88
in another, and neither is wrong, because neither is a measurement of
anything.

Don't take my word for it — I built an interactive page where **you**
mix the recipe over one fixed night and watch the score swing from 45
to 95: [The Sleep Score Lab](https://tsjenn.github.io/Sj/score-lab/).
No signup, no backend, view-source-friendly vanilla JS.

## Why the number wobbles when your life didn't

A score built on noisy inputs inherits the noise. Stage estimates
(light/deep/REM) are inferences from movement and sound — studies
comparing consumer trackers against lab polysomnography consistently
find good agreement on asleep-versus-awake and much weaker agreement
on stages. A partner turning over adds "restlessness" your body never
felt. An evening drink flatters the first half of the night and the
score misses the payback.

So the seven-point drop from Tuesday to Wednesday is usually
measurement noise, not a health event.

## The two numbers actually worth watching

Buried under the headline score, most apps report two figures that
need no guessing and no secret recipe:

- **Total sleep time** — the single most decision-relevant number a
  tracker produces. Consistently under seven hours? No score
  interpretation needed; the fix is a schedule.
- **Sleep efficiency** — the share of time in bed spent actually
  asleep. These both come from asleep-versus-awake detection, the
  part consumer trackers genuinely do well.

Compare yourself only to your own recent average, in one app. And if
checking the score has started to feel like receiving a grade,
researchers have a name for sleep made worse by chasing perfect
tracker data: orthosomnia. Stop looking for a few weeks.

## Disclosure

I make [Rested](https://tsjenn.github.io/Sj/sleep/), a free
browser-based sleep tracker that keeps everything on your device and
labels what's measured vs estimated. This article exists because I
think the industry's headline number deserves an honest explanation
either way.

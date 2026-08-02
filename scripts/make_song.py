#!/usr/bin/env python3
"""Compose 'Catch the Light' — the Wildhaven vocal theme (choir version).

A song-structured track (intro / verse / chorus / verse / chorus / outro)
where a synthesized formant choir ("ooh"/"aah" vowels with vibrato) carries
the vocal melody, so a real singer can record over it using the same melody.

Output: music/04-Catch-the-Light.wav  (~102s, 96 BPM, C major)
Run:    python3 scripts/make_song.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_music import (SR, OUT, Track, pluck, pad, bell, bass, kick, hat,
                        shaker, midi_f, env, rng)


# ------------------------------------------------------- formant choir voice
FORMANTS = {
    # vowel: [(freq, gain, bandwidth), ...]
    "ooh": [(300, 1.0, 90), (870, 0.35, 110), (2250, 0.12, 150)],
    "aah": [(700, 1.0, 120), (1220, 0.6, 140), (2600, 0.22, 180)],
}


def voice(m, dur, vowel="ooh", vol=1.0):
    """One synthesized voice: vibrato-modulated harmonic source shaped by
    vowel formant filters. Layer several for a choir."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = midi_f(m)
    sig = np.zeros(n)
    for det_cents, vib_phase in ((-8, 0.0), (5, 2.1), (11, 4.2)):
        f = f0 * 2 ** (det_cents / 1200)
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t + vib_phase) * np.minimum(t / 0.4, 1)
        phase = 2 * np.pi * np.cumsum(f * vib) / SR
        x = np.zeros(n)
        nyq = SR / 2
        k = 1
        while k * f0 < min(4000, nyq) and k <= 30:
            x += np.sin(phase * k) / k
            k += 1
        sig += x
    # formant shaping via FFT gaussians
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    shape = np.zeros_like(freqs)
    for fc, g, bw in FORMANTS[vowel]:
        shape += g * np.exp(-0.5 * ((freqs - fc) / bw) ** 2)
    shape += 0.02
    sig = np.fft.irfft(spec * shape, n)
    # breath
    breath = rng.uniform(-1, 1, n)
    bspec = np.fft.rfft(breath)
    bshape = np.exp(-0.5 * ((freqs - 2500) / 900) ** 2) * 0.012
    sig += np.fft.irfft(bspec * bshape, n)
    sig /= max(1e-9, np.abs(sig).max())
    return sig * env(n, min(0.12, dur * 0.3), min(0.35, dur * 0.4), 0.92) * vol


def choir(tr, m, beat, dur_beats, vowel, vol=0.8):
    """three-part choir: melody + octave-down + soft fifth, panned wide"""
    d = dur_beats * tr.spb
    tr.add(voice(m, d, vowel, vol), beat, pan=0.0)
    tr.add(voice(m - 12, d, "ooh", vol * 0.5), beat, pan=-0.35)
    tr.add(voice(m - 5, d, vowel, vol * 0.35), beat, pan=0.35)


# =============================================================== the song
# 96 BPM, C major. Sections in beats (4/4):
#   intro 8 | verse1 32 | chorus 32 | verse2 32 | chorus 32 | outro 12
def song():
    tr = Track(96, 148)
    C, Am, F, G = [48, 60, 64, 67], [45, 57, 60, 64], [41, 53, 57, 60], [43, 55, 59, 62]

    def pads_and_bass(start, bars, prog, pad_vol=0.45, with_bass=True):
        for i in range(bars):
            ch = prog[i % len(prog)]
            tr.add(pad(ch[1:], 4.2 * tr.spb, pad_vol, 850), start + i * 4, pan=-0.08)
            if with_bass:
                tr.add(bass(ch[0], 1.1 * tr.spb, 0.5), start + i * 4)
                tr.add(bass(ch[0], 1.1 * tr.spb, 0.38), start + i * 4 + 2)

    def drums(start, bars, energy=1.0):
        for b in range(bars):
            base = start + b * 4
            tr.add(kick(0.7 * energy), base)
            tr.add(kick(0.5 * energy), base + 2)
            for e in range(8):
                tr.add(shaker((0.45 if e % 2 else 0.28) * energy), base + e * 0.5, pan=0.3)
            tr.add(hat(0.45 * energy), base + 1, pan=-0.3)
            tr.add(hat(0.45 * energy), base + 3, pan=-0.3)

    # --- intro (beats 0-8): pads + bells motif
    pads_and_bass(0, 2, [C, Am], 0.4, with_bass=False)
    for i, (b, m) in enumerate([(0, 72), (1, 67), (2, 69), (3, 72), (4, 74), (6, 72)]):
        tr.add(bell(m, 2.2, 0.6), b, pan=0.2)

    # --- verse 1 (beats 8-40): "Morning breaks across the meadow..."
    # vocal melody, one entry per lyric phrase (syllable-timed for a singer)
    VERSE = [
        # (beat, midi, beats, vowel) — phrase 1: "Mor-ning breaks a-cross the mea-dow"
        (0, 64, 0.5, "ooh"), (0.5, 64, 0.5, "ooh"), (1, 67, 1, "ooh"), (2, 69, 0.5, "ooh"),
        (2.5, 67, 0.5, "ooh"), (3, 64, 1, "ooh"),
        # "dew is shi-ning gold"
        (4, 62, 0.5, "ooh"), (4.5, 64, 0.5, "ooh"), (5, 67, 1, "ooh"), (6, 60, 2, "ooh"),
        # phrase 2 mirrors
        (8, 64, 0.5, "ooh"), (8.5, 64, 0.5, "ooh"), (9, 67, 1, "ooh"), (10, 69, 0.5, "ooh"),
        (10.5, 67, 0.5, "ooh"), (11, 64, 1, "ooh"),
        (12, 62, 0.5, "ooh"), (12.5, 64, 0.5, "ooh"), (13, 62, 1, "ooh"), (14, 60, 2, "ooh"),
        # phrase 3: rising — "grab your orbs and pack your cou-rage"
        (16, 65, 0.5, "ooh"), (16.5, 65, 0.5, "ooh"), (17, 69, 1, "ooh"), (18, 69, 0.5, "ooh"),
        (18.5, 67, 0.5, "ooh"), (19, 65, 1, "ooh"),
        (20, 67, 0.5, "ooh"), (20.5, 69, 0.5, "ooh"), (21, 71, 1, "ooh"), (22, 67, 2, "ooh"),
        # phrase 4: "wild and run-ning free"
        (24, 72, 1, "ooh"), (25, 71, 0.5, "ooh"), (25.5, 69, 0.5, "ooh"), (26, 67, 1, "ooh"),
        (27, 64, 1, "ooh"), (28, 62, 1.5, "ooh"), (29.5, 60, 2.5, "ooh"),
    ]
    v1 = 8
    pads_and_bass(v1, 8, [C, Am, F, G])
    for b, m, d, vw in VERSE:
        choir(tr, m, v1 + b, d, vw, 0.55)
        tr.add(pluck(m, d * tr.spb * 1.2, 0.35), v1 + b, pan=0.2)

    # --- chorus (32 beats): "Catch the light, Wild-ha-ven's cal-ling..."
    CHORUS = [
        # "Catch the light"
        (0, 67, 0.5, "aah"), (0.5, 69, 0.5, "aah"), (1, 72, 1.5, "aah"),
        # "Wild-ha-ven's cal-ling"
        (3, 74, 0.5, "aah"), (3.5, 72, 0.5, "aah"), (4, 69, 0.5, "aah"), (4.5, 72, 0.5, "aah"), (5, 69, 1.5, "aah"),
        # "build a home where wild hearts stay"
        (8, 65, 0.5, "aah"), (8.5, 67, 0.5, "aah"), (9, 69, 1, "aah"), (10, 69, 0.5, "aah"),
        (10.5, 67, 0.5, "aah"), (11, 65, 0.5, "aah"), (11.5, 67, 0.5, "aah"), (12, 67, 2.5, "aah"),
        # "through the night the lamps are glo-wing"
        (16, 67, 0.5, "aah"), (16.5, 69, 0.5, "aah"), (17, 72, 1.5, "aah"),
        (19, 74, 0.5, "aah"), (19.5, 72, 0.5, "aah"), (20, 76, 0.5, "aah"), (20.5, 74, 0.5, "aah"), (21, 72, 1.5, "aah"),
        # "we'll grow brigh-ter e-very day"
        (24, 74, 0.5, "aah"), (24.5, 76, 0.5, "aah"), (25, 77, 1, "aah"), (26, 76, 0.5, "aah"),
        (26.5, 74, 0.5, "aah"), (27, 72, 0.5, "aah"), (27.5, 71, 0.5, "aah"), (28, 72, 3.5, "aah"),
    ]

    def chorus_at(start, energy=1.0):
        pads_and_bass(start, 8, [C, G, Am, F], 0.5)
        drums(start, 8, energy)
        for b, m, d, vw in CHORUS:
            choir(tr, m, start + b, d, vw, 0.75)
            tr.add(bell(m + 12, min(d, 1.5) * tr.spb * 2, 0.35), start + b, pan=0.3)

    chorus_at(40)

    # --- verse 2 (beats 72-104)
    v2 = 72
    pads_and_bass(v2, 8, [C, Am, F, G])
    drums(v2, 8, 0.5)
    for b, m, d, vw in VERSE:
        choir(tr, m, v2 + b, d, vw, 0.6)
        tr.add(pluck(m, d * tr.spb * 1.2, 0.35), v2 + b, pan=0.2)

    # --- final chorus (beats 104-136)
    chorus_at(104, 1.1)

    # --- outro (beats 136-148): "ooh" fade on the hook
    pads_and_bass(136, 3, [F, G, C], 0.45, with_bass=False)
    for b, m, d in [(0, 67, 1), (1, 69, 1), (2, 72, 4), (6, 67, 5)]:
        choir(tr, m, 136 + b, d, "ooh", 0.5)
    tr.add(bell(72, 4, 0.6), 142, pan=0.1)
    tr.add(bell(60, 5, 0.5), 144, pan=-0.1)

    tr.render(os.path.join(OUT, "04-Catch-the-Light.wav"), reverb=0.26)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    song()
    print("done")

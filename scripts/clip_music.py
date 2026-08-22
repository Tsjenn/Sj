#!/usr/bin/env python3
"""Render each game's generative soundtrack to WAV for the clip factory.

Same chord/melody tables as the games' WebAudio engines, synthesized
offline (triangle plucks + sine pads + sine bass), so the clips carry
the real in-game music.

    python3 scripts/clip_music.py <tower|drop|beat> <seconds> <out.wav>
"""

import sys
import wave

import numpy as np

SR = 44100

SONGS = {
    "tower": {  # game6: Am F C G @ 84 BPM, pentatonic plucks
        "bpm": 84,
        "prog": [[220, 261.63, 329.63], [174.61, 220, 261.63],
                 [130.81, 164.81, 196], [196, 246.94, 293.66]],
        "bass": None,
        "pool": [440, 523.25, 587.33, 659.25, 783.99, 880],
        "melo": [[0, -1, 2, -1, 3, -1, 2, -1], [1, -1, 0, -1, -1, 2, -1, -1],
                 [3, -1, 4, -1, 3, -1, 2, -1], [1, -1, 2, -1, 0, -1, -1, -1]],
    },
    "drop": {   # game7: C G Am F @ 92 BPM
        "bpm": 92,
        "prog": [[261.63, 329.63, 392], [196, 246.94, 293.66],
                 [220, 261.63, 329.63], [174.61, 220, 261.63]],
        "bass": None,
        "pool": [523.25, 587.33, 659.25, 783.99, 880, 1046.5],
        "melo": [[0, -1, 1, -1, 2, -1, 3, -1], [4, -1, 3, -1, -1, 2, -1, -1],
                 [2, -1, 3, -1, 4, -1, 5, -1], [3, -1, 2, -1, 0, -1, -1, -1]],
    },
    "beat": {   # game8: Am F C G @ 96 BPM with bass — melody is what the player taps
        "bpm": 96,
        "prog": [[220, 261.63, 329.63], [174.61, 220, 261.63],
                 [130.81, 164.81, 196], [196, 246.94, 293.66]],
        "bass": [110, 87.31, 65.41, 98],
        "pool": [440, 523.25, 659.25, 783.99],
        "melo": [[0, -1, 1, -1, 2, -1, 1, -1], [3, -1, 2, -1, -1, 1, -1, -1],
                 [0, -1, 1, 2, -1, 3, -1, 2], [1, -1, 0, -1, 3, -1, -1, -1]],
    },
}


def note(freq, dur, gain, kind="tri", attack=0.012):
    n = int(SR * dur)
    t = np.arange(n) / SR
    if kind == "tri":
        x = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))
    else:
        x = np.sin(2 * np.pi * freq * t)
    env = np.minimum(t / attack, 1.0) * np.exp(-t * (4.5 / dur))
    return x * env * gain


def add(buf, start, x):
    i = int(start * SR)
    j = min(i + len(x), len(buf))
    if j > i:
        buf[i:j] += x[:j - i]


def render(song, secs):
    s = SONGS[song]
    step = 60 / s["bpm"] / 2
    buf = np.zeros(int(SR * (secs + 2)))
    t, k = 0.0, 0
    while t < secs:
        bar, st = (k // 8) % 4, k % 8
        if st == 0:
            for f in s["prog"][bar]:
                add(buf, t, note(f, step * 8 * 0.95, 0.05, "sine", 0.35))
        if s["bass"] and st % 2 == 0:
            add(buf, t, note(s["bass"][bar], step * 0.9, 0.14, "sine"))
        m = s["melo"][bar][st]
        if m >= 0:
            f = s["pool"][m]
            add(buf, t, note(f, 0.42, 0.11))
            add(buf, t, note(f * 2, 0.25, 0.035, "sine"))
        t += step
        k += 1
    buf = buf[:int(SR * secs)]
    peak = np.max(np.abs(buf)) or 1
    return (buf / peak * 0.75 * 32767).astype(np.int16)


def main():
    song, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    data = render(song, secs)
    with wave.open(out, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("wrote", out, f"{secs:.0f}s")


if __name__ == "__main__":
    main()

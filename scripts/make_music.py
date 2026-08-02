#!/usr/bin/env python3
"""Compose and render the Wildhaven Music Pack.

Three original instrumental tracks, synthesized from scratch (no samples):
  music/01-Wildhaven-Theme.wav     warm main theme      (~88s, 88 BPM, C major)
  music/02-Starlight-Park.wav      cozy night piece     (~76s, 76 BPM, A minor)
  music/03-Into-the-Wilds.wav      adventure track      (~64s, 120 BPM, D dorian)

Instruments: Karplus-Strong plucked strings, additive pads, FM-ish bells,
synthesized kick/hat/shaker, convolution reverb. Output: 44.1 kHz stereo WAV
(MP3s rendered separately with ffmpeg).

Run:  python3 scripts/make_music.py
"""

import os
import wave

import numpy as np

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "music")
rng = np.random.default_rng(20260802)


def midi_f(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------- instruments
def env(n, a, r, sustain=1.0):
    """attack/release envelope over n samples"""
    e = np.ones(n) * sustain
    na = max(1, int(a * SR))
    nr = max(1, int(r * SR))
    na = min(na, n); nr = min(nr, n)
    e[:na] *= np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pluck(m, dur, vol=1.0, bright=0.5):
    """Karplus-Strong plucked string."""
    f = midi_f(m)
    L = max(2, int(SR / f))
    n_per = int(dur * f) + 1
    buf = rng.uniform(-1, 1, L) * bright + np.sin(2 * np.pi * np.arange(L) / L) * (1 - bright)
    out = np.empty(n_per * L)
    decay = 0.996
    for i in range(n_per):
        out[i * L:(i + 1) * L] = buf
        buf = 0.5 * (buf + np.roll(buf, 1)) * decay
    out = out[:int(dur * SR)]
    return out * env(len(out), 0.002, min(0.3, dur * 0.5)) * vol


def pad(ms, dur, vol=1.0, cutoff=1000):
    """warm detuned pad chord; ms = list of midi notes"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in ms:
        f = midi_f(m)
        for det in (-0.15, 0.12):
            ph = rng.uniform(0, 2 * np.pi)
            x = np.sin(2 * np.pi * (f + det) * t + ph)
            x += 0.4 * np.sin(2 * np.pi * (f + det) * 2 * t + ph)
            x += 0.2 * np.sin(2 * np.pi * (f + det) * 3 * t + ph)
            sig += x
    # gentle lowpass via FFT
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    spec *= 1 / (1 + (freqs / cutoff) ** 2)
    sig = np.fft.irfft(spec, n)
    sig /= max(1e-9, np.abs(sig).max())
    return sig * env(n, min(0.8, dur * 0.3), min(1.2, dur * 0.4), 0.9) * vol


def bell(m, dur, vol=1.0):
    """music-box bell"""
    f = midi_f(m)
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.5)
    sig += 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
    sig += 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9)
    return sig * vol * 0.6


def bass(m, dur, vol=1.0):
    f = midi_f(m)
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)
    return sig * env(n, 0.01, min(0.25, dur * 0.4), 0.8) * vol


def kick(vol=1.0):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 22) + 38
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return sig * np.exp(-t * 14) * vol


def hat(vol=1.0):
    n = int(0.06 * SR)
    sig = rng.uniform(-1, 1, n)
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    spec[freqs < 6000] *= 0.05
    sig = np.fft.irfft(spec, n)
    return sig * np.exp(-np.arange(n) / SR * 60) * vol * 0.6


def shaker(vol=1.0):
    n = int(0.09 * SR)
    sig = rng.uniform(-1, 1, n)
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    spec[freqs < 3000] *= 0.1
    sig = np.fft.irfft(spec, n)
    return sig * env(n, 0.01, 0.06) * vol * 0.4


# --------------------------------------------------------------- sequencer
class Track:
    def __init__(self, bpm, beats):
        self.spb = 60.0 / bpm
        self.n = int(beats * self.spb * SR) + SR * 3
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)

    def add(self, sig, beat, pan=0.0, gain=1.0):
        i = int(beat * self.spb * SR)
        j = min(self.n, i + len(sig))
        seg = sig[:j - i] * gain
        self.L[i:j] += seg * (1 - pan) * 0.5 + seg * 0.5
        self.R[i:j] += seg * (1 + pan) * 0.5 + seg * 0.5

    def render(self, path, reverb=0.22):
        # convolution reverb with a synthetic decaying-noise IR
        ir_n = int(1.6 * SR)
        t = np.arange(ir_n) / SR
        irL = rng.uniform(-1, 1, ir_n) * np.exp(-t * 3.2)
        irR = rng.uniform(-1, 1, ir_n) * np.exp(-t * 3.4)
        irL[0] = irR[0] = 0

        def rev(dry, ir):
            m = len(dry) + len(ir) - 1
            nfft = 1 << (m - 1).bit_length()
            wet = np.fft.irfft(np.fft.rfft(dry, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(dry)]
            wet /= max(1e-9, np.abs(wet).max())
            return wet

        L = self.L + rev(self.L, irL) * reverb * np.abs(self.L).max()
        R = self.R + rev(self.R, irR) * reverb * np.abs(self.R).max()
        peak = max(np.abs(L).max(), np.abs(R).max(), 1e-9)
        L = np.tanh(L / peak * 1.4) * 0.85
        R = np.tanh(R / peak * 1.4) * 0.85
        # master fade in/out
        nf = int(0.4 * SR)
        for ch in (L, R):
            ch[:nf] *= np.linspace(0, 1, nf)
            ch[-SR:] *= np.linspace(1, 0, SR)
        data = np.empty(2 * len(L), dtype=np.int16)
        data[0::2] = (L * 32767).astype(np.int16)
        data[1::2] = (R * 32767).astype(np.int16)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(data.tobytes())
        print("rendered", path, round(len(L) / SR, 1), "s")


# ============================================================ track 1: theme
def theme():
    tr = Track(88, 128)
    C, Am, F, G = [48, 60, 64, 67], [45, 57, 60, 64], [41, 53, 57, 60], [43, 55, 59, 62]
    prog = [C, Am, F, G]

    # pads all the way through (every bar = 4 beats)
    for bar in range(32):
        ch = prog[(bar // 2) % 4]
        tr.add(pad(ch[1:], 4.2 * tr.spb, 0.5, 900), bar * 4, pan=-0.1)

    # bass from bar 4
    for bar in range(4, 32):
        root = prog[(bar // 2) % 4][0]
        tr.add(bass(root, 1.2 * tr.spb, 0.5), bar * 4)
        tr.add(bass(root, 1.2 * tr.spb, 0.4), bar * 4 + 2)

    # melody A (bars 4-12 and 20-28), hand-composed
    melA = [  # (beat-in-8bars, midi, dur-beats)
        (0, 64, 1), (1, 67, 1), (2, 72, 2),
        (4, 69, 1), (5, 67, 1), (6, 64, 2),
        (8, 65, 1), (9, 69, 1), (10, 72, 2),
        (12, 74, 1), (13, 71, 1), (14, 67, 2),
        (16, 72, 1), (17, 67, 1), (18, 64, 2),
        (20, 64, 1), (21, 67, 1), (22, 69, 2),
        (24, 69, 1), (25, 72, 1), (26, 74, 2),
        (28, 71, 2), (30, 67, 2),
    ]
    for start_bar in (4, 20):
        for b, m, d in melA:
            tr.add(pluck(m, d * tr.spb * 1.4, 0.85), start_bar * 4 + b, pan=0.15)

    # section B (bars 12-20): bells counter-melody + drums
    melB = [
        (0, 76, 0.5), (0.5, 74, 0.5), (1, 72, 1), (2, 74, 1), (3, 76, 1),
        (4, 72, 1), (5, 69, 1), (6, 67, 2),
        (8, 77, 0.5), (8.5, 76, 0.5), (9, 74, 1), (10, 72, 1), (11, 74, 1),
        (12, 74, 1), (13, 71, 1), (14, 67, 2),
        (16, 76, 0.5), (16.5, 74, 0.5), (17, 72, 1), (18, 74, 1), (19, 76, 1),
        (20, 79, 1), (21, 76, 1), (22, 72, 2),
        (24, 77, 1), (25, 74, 1), (26, 72, 1), (27, 74, 1),
        (28, 71, 2), (30, 72, 2),
    ]
    for b, m, d in melB:
        tr.add(bell(m, d * tr.spb * 2, 0.8), 48 + b, pan=0.25)
        tr.add(pluck(m - 12, d * tr.spb * 1.2, 0.4), 48 + b, pan=-0.2)
    for bar in range(12, 20):
        tr.add(kick(0.7), bar * 4)
        tr.add(kick(0.55), bar * 4 + 2)
        for eighth in range(8):
            tr.add(shaker(0.5 if eighth % 2 else 0.3), bar * 4 + eighth * 0.5, pan=0.3)
        tr.add(hat(0.5), bar * 4 + 1, pan=-0.3)
        tr.add(hat(0.5), bar * 4 + 3, pan=-0.3)

    # outro bells (bars 28-32)
    for i, m in enumerate([72, 67, 64, 60]):
        tr.add(bell(m, 4 * tr.spb, 0.7), (28 + i) * 4, pan=0.1)
    tr.render(os.path.join(OUT, "01-Wildhaven-Theme.wav"))


# ===================================================== track 2: night piece
def night():
    tr = Track(76, 96)
    Am, F, C, G = [45, 57, 60, 64], [41, 53, 57, 60], [48, 60, 64, 67], [43, 55, 59, 62]
    prog = [Am, F, C, G]
    for bar in range(24):
        ch = prog[(bar // 2) % 4]
        tr.add(pad(ch[1:], 4.3 * tr.spb, 0.55, 650), bar * 4, pan=-0.05)
        tr.add(bass(ch[0], 3.5 * tr.spb, 0.35), bar * 4)
    # sparse music-box melody
    mel = [
        (0, 76, 2), (2, 72, 2),
        (4, 69, 1.5), (5.5, 72, 0.5), (6, 74, 2),
        (8, 72, 2), (10, 67, 2),
        (12, 71, 1.5), (13.5, 74, 0.5), (14, 76, 2),
        (16, 81, 2), (18, 76, 2),
        (20, 77, 1.5), (21.5, 76, 0.5), (22, 72, 2),
        (24, 74, 2), (26, 72, 1), (27, 71, 1),
        (28, 69, 4),
    ]
    for start_bar in (4, 12):
        for b, m, d in mel:
            tr.add(bell(m, d * tr.spb * 2.2, 0.9), start_bar * 4 + b, pan=0.2)
    # twinkles
    for i in range(20):
        b = 16 + rng.uniform(0, 64)
        tr.add(bell(int(rng.choice([88, 84, 81, 79])), 1.5, 0.25),
               b, pan=rng.uniform(-0.6, 0.6))
    tr.render(os.path.join(OUT, "02-Starlight-Park.wav"), reverb=0.3)


# ==================================================== track 3: adventure
def wilds():
    tr = Track(120, 128)
    Dm, F, C, G = [38, 50, 53, 57], [41, 53, 57, 60], [36, 48, 52, 55], [43, 55, 59, 62]
    prog = [Dm, Dm, F, C, Dm, Dm, G, C]
    for bar in range(32):
        ch = prog[bar % 8]
        tr.add(pad(ch[1:], 4.2 * tr.spb, 0.35, 800), bar * 4)
        tr.add(bass(ch[0], 0.8 * tr.spb, 0.55), bar * 4)
        tr.add(bass(ch[0], 0.8 * tr.spb, 0.4), bar * 4 + 1.5)
        tr.add(bass(ch[0] + 7, 0.8 * tr.spb, 0.35), bar * 4 + 3)
    # driving pluck arpeggios
    arp_pat = [0, 2, 3, 2, 0, 3, 2, 3]
    for bar in range(4, 32):
        ch = prog[bar % 8]
        notes = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[1] + 24]
        for e in range(8):
            m = notes[arp_pat[e] % len(notes)]
            tr.add(pluck(m, 0.6 * tr.spb, 0.55, 0.7), bar * 4 + e * 0.5,
                   pan=0.3 if e % 2 else -0.3)
    # lead phrase every 8 bars
    lead = [(0, 74, 1), (1, 77, 1), (2, 81, 1.5), (3.5, 79, 0.5),
            (4, 77, 1), (5, 74, 1), (6, 72, 2),
            (8, 74, 1), (9, 77, 1), (10, 81, 1.5), (11.5, 84, 0.5),
            (12, 81, 1), (13, 79, 1), (14, 74, 2)]
    for start_bar in (8, 16, 24):
        for b, m, d in lead:
            tr.add(pluck(m, d * tr.spb * 1.6, 0.8, 0.6), start_bar * 4 + b, pan=0.1)
    # drums
    for bar in range(4, 32):
        tr.add(kick(0.8), bar * 4)
        tr.add(kick(0.5), bar * 4 + 1.75)
        tr.add(kick(0.7), bar * 4 + 2.5)
        for e in range(8):
            tr.add(shaker(0.5 if e % 2 else 0.3), bar * 4 + e * 0.5, pan=0.35)
        tr.add(hat(0.6), bar * 4 + 1, pan=-0.35)
        tr.add(hat(0.6), bar * 4 + 3, pan=-0.35)
    tr.render(os.path.join(OUT, "03-Into-the-Wilds.wav"), reverb=0.18)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    theme()
    night()
    wilds()
    print("done")

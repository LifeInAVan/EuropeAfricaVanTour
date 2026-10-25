#!/usr/bin/env python3
"""Generative instrumental bed for the montage. Writes music.wav."""
import numpy as np, wave, sys

SR = 44100
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 79.75
BPM = 90.0
BAR = 4 * 60 / BPM            # 2.667 s
N = int(SR * DUR)
t_all = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)

def f(midi): return 440.0 * 2 ** ((midi - 69) / 12)
# C, G, Am, F  (midi roots C3=48)
CHORDS = [
    [48, 52, 55, 60],   # C
    [43, 47, 50, 55],   # G
    [45, 48, 52, 57],   # Am
    [41, 45, 48, 53],   # F
]
def add(buf, start, sig):
    i = int(start * SR)
    j = min(i + len(sig), N)
    if i < N: buf[i:j] += sig[: j - i]

def pad_note(freq, dur, amp):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.minimum(t / 1.2, 1.0) * np.minimum((dur - t) / 1.5, 1.0).clip(0, 1)
    s = np.zeros(n)
    for d in (-0.0015, 0.0015):
        s += np.sin(2 * np.pi * freq * (1 + d) * t)
        s += 0.3 * np.sin(2 * np.pi * 2 * freq * (1 + d) * t)
    return amp * env * s / 2.6

def pluck(freq, dur, amp):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.exp(-t * 5.5)
    s = np.sin(2*np.pi*freq*t) + 0.5*np.sin(2*np.pi*2*freq*t) + 0.2*np.sin(2*np.pi*3*freq*t)
    return amp * env * s / 1.7

def bass_note(freq, dur, amp):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.minimum(t / 0.02, 1.0) * np.exp(-t * 1.2)
    return amp * env * (np.sin(2*np.pi*freq*t) + 0.25*np.sin(2*np.pi*2*freq*t))

def kick(amp=0.5):
    n = int(0.25 * SR); t = np.arange(n) / SR
    fr = 95 * np.exp(-t * 22) + 42
    return amp * np.exp(-t * 16) * np.sin(2 * np.pi * np.cumsum(fr) / SR)

rng = np.random.default_rng(7)
def shaker(amp=0.05):
    n = int(0.09 * SR)
    s = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 60)
    return amp * np.convolve(s, [1, -0.97], 'same')  # high-pass-ish

nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    t0 = b * BAR
    ch = CHORDS[b % 4]
    # pads throughout
    for m in ch:
        add(L, t0, pad_note(f(m), BAR * 1.05, 0.11))
        add(R, t0, pad_note(f(m) * 1.001, BAR * 1.05, 0.11))
    # arpeggio from 8 s
    if t0 >= 8:
        seq = [ch[0]+12, ch[2]+12, ch[1]+12, ch[3], ch[2]+12, ch[1]+12, ch[3]+12, ch[2]+12]
        for k, m in enumerate(seq):
            st = t0 + k * BAR / 8
            p = pluck(f(m), 0.5, 0.16)
            add(L if k % 2 else R, st, p)
            add(R if k % 2 else L, st + 0.012, p * 0.6)
    # bass + kick from 16 s
    if t0 >= 16:
        add(L, t0, bass_note(f(ch[0] - 12), BAR / 2, 0.4)); add(R, t0, bass_note(f(ch[0] - 12), BAR / 2, 0.4))
        add(L, t0 + BAR/2, bass_note(f(ch[0] - 12), BAR / 2, 0.32)); add(R, t0 + BAR/2, bass_note(f(ch[0] - 12), BAR / 2, 0.32))
        for beat in (0, 2):
            kk = kick(); add(L, t0 + beat * BAR / 4, kk); add(R, t0 + beat * BAR / 4, kk)
    # shaker 8ths from 24 s
    if t0 >= 24:
        for k in range(8):
            sh = shaker(0.045 if k % 2 else 0.028)
            add(L, t0 + k * BAR / 8, sh); add(R, t0 + k * BAR / 8 + 0.004, sh)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.4)
mix *= 0.85 / np.abs(mix).max()
# global fade in/out
fade_in = np.minimum(t_all / 2.0, 1.0); fade_out = np.minimum((DUR - t_all) / 4.5, 1.0).clip(0, 1)
mix *= (fade_in * fade_out)[:, None]

with wave.open('music.wav', 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('music.wav', DUR, 's')

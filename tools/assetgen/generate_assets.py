#!/usr/bin/env python3
"""Generates MotionWorks' original assets: particle sprites, synthesized sounds, sounds.json and the logo.

Everything is procedural and seeded, so the output is reproducible and contains no third-party
material. Usage: python3 tools/assetgen/generate_assets.py   (needs numpy, Pillow and ffmpeg with libvorbis)
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/motionworks")
JAVA = os.path.join(ROOT, "src/main/java/com/motionworks/registry")
SR = 22050


def names(java_file):
    with open(os.path.join(JAVA, java_file), encoding="utf-8") as fh:
        src = fh.read()
    block = src[src.index("NAMES = {"):src.index("};", src.index("NAMES = {"))]
    return re.findall(r'"([a-z0-9_.]+)"', block)


# ============================================================================ particle sprites
def sprite(size=16):
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def soft_disc(img, cx, cy, r, color, falloff=1.6):
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / max(r, 1e-3)
            if d < 1:
                a = int(color[3] * (1 - d) ** falloff)
                o = px[x, y]
                if a > o[3]:
                    px[x, y] = (color[0], color[1], color[2], a)
    return img


def ring(img, cx, cy, r, width, color):
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            d = abs(math.hypot(x + 0.5 - cx, y + 0.5 - cy) - r)
            if d < width:
                a = int(color[3] * (1 - d / width))
                if a > px[x, y][3]:
                    px[x, y] = (color[0], color[1], color[2], a)
    return img


def star(img, cx, cy, r, color, points=4):
    d = ImageDraw.Draw(img)
    for i in range(points):
        a = math.pi * i / points
        d.line([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))], fill=color, width=1)
    soft_disc(img, cx, cy, r * 0.45, color, 1.0)
    return img


def particle_frames(name, rng):
    frames = []
    if name == "spark":
        for i in range(4):
            frames.append(star(sprite(8), 4, 4, 3.5 - i * 0.7, (255, 236 - 20 * i, 160 - 30 * i, 255)))
    elif name in ("dust_puff", "smoke_wisp", "breath", "snow_puff"):
        col = {"dust_puff": (176, 160, 136), "smoke_wisp": (110, 110, 116), "breath": (236, 240, 248), "snow_puff": (250, 252, 255)}[name]
        for i in range(4):
            img = sprite(16)
            for _ in range(5):
                soft_disc(img, 8 + rng.uniform(-3, 3), 8 + rng.uniform(-3, 3), 4.5 + i * 0.8, (*col, 200 - 35 * i), 1.4)
            frames.append(img)
    elif name == "splash":
        for i in range(4):
            img = sprite(8)
            for _ in range(3):
                soft_disc(img, rng.uniform(2, 6), rng.uniform(2, 6), 1.6 - 0.25 * i, (120, 170, 255, 230), 0.8)
            frames.append(img)
    elif name in ("ripple", "impact_ring", "shockwave"):
        col = {"ripple": (170, 210, 255, 200), "impact_ring": (255, 245, 220, 230), "shockwave": (255, 255, 255, 220)}[name]
        for i in range(4):
            frames.append(ring(sprite(16), 8, 8, 2 + i * 1.8, 1.2, col))
    elif name in ("ember", "firefly"):
        col = {"ember": (255, 140, 40, 255), "firefly": (220, 255, 120, 255)}[name]
        for i in range(3):
            img = soft_disc(sprite(8), 4, 4, 3.5, (*col[:3], 120 + 40 * i), 1.0)
            frames.append(soft_disc(img, 4, 4, 1.4, (255, 255, 230, 255), 0.6))
    elif name == "leaf":
        for i in range(4):
            img = sprite(8)
            d = ImageDraw.Draw(img)
            ang = i * math.pi / 4
            pts = [(4 + 3.2 * math.cos(ang), 4 + 3.2 * math.sin(ang)), (4 + 1.4 * math.cos(ang + 1.6), 4 + 1.4 * math.sin(ang + 1.6)),
                   (4 - 3.2 * math.cos(ang), 4 - 3.2 * math.sin(ang)), (4 + 1.4 * math.cos(ang - 1.6), 4 + 1.4 * math.sin(ang - 1.6))]
            d.polygon(pts, fill=(84, 150 + 10 * i, 52, 255))
            frames.append(img)
    elif name in ("wind_streak", "rain_streak"):
        col = {"wind_streak": (240, 244, 250, 150), "rain_streak": (150, 180, 255, 200)}[name]
        img = sprite(8)
        ImageDraw.Draw(img).line([(1, 7), (6, 0)] if name == "rain_streak" else [(0, 4), (7, 4)], fill=col, width=1)
        frames.append(img)
    elif name == "magic_glint":
        for i in range(4):
            frames.append(star(sprite(8), 4, 4, 3.5 * (1 - abs(i - 1.5) / 2.5), (200, 170, 255, 255), points=4 if i % 2 else 2))
    elif name in ("pollen", "mote"):
        col = {"pollen": (250, 220, 90, 255), "mote": (255, 255, 255, 220)}[name]
        img = sprite(8)
        soft_disc(img, 4, 4, 1.8, col, 0.7)
        frames.append(img)
    elif name == "bubble_trail":
        for i in range(2):
            frames.append(ring(sprite(8), 4, 4, 2.2 + i * 0.6, 0.9, (220, 240, 255, 230)))
    else:
        frames.append(soft_disc(sprite(8), 4, 4, 3, (255, 255, 255, 255)))
    return frames


def write_particles():
    rng = np.random.default_rng(1234)

    class R:
        def uniform(self, a, b):
            return float(rng.uniform(a, b))
    r = R()
    tex_dir = os.path.join(ASSETS, "textures/particle")
    def_dir = os.path.join(ASSETS, "particles")
    os.makedirs(tex_dir, exist_ok=True)
    os.makedirs(def_dir, exist_ok=True)
    for name in names("MWParticles.java"):
        frames = particle_frames(name, r)
        textures = []
        for i, img in enumerate(frames):
            fn = "%s_%d" % (name, i)
            img.save(os.path.join(tex_dir, fn + ".png"))
            textures.append("motionworks:" + fn)
        with open(os.path.join(def_dir, name + ".json"), "w") as fh:
            json.dump({"textures": textures}, fh, indent=1)
    return len(names("MWParticles.java"))


# ============================================================================ sound synthesis
def env(n, attack, decay_power=3.0):
    t = np.linspace(0, 1, n)
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * (1 - t) ** decay_power


def noise(n, rng):
    return rng.standard_normal(n)


def lowpass(x, cutoff):
    """One-pole low-pass, cutoff in Hz (vectorised via recursive filter)."""
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def bandpass(x, lo, hi):
    return lowpass(highpass(x, lo), hi)


def tone(n, f0, f1=None, phase=0.0):
    f1 = f0 if f1 is None else f1
    f = np.linspace(f0, f1, n)
    return np.sin(phase + 2 * np.pi * np.cumsum(f) / SR)


def seconds(s):
    return max(1, int(SR * s))


def footstep(rng, material, variant):
    n = seconds(0.16 + 0.02 * variant)
    x = noise(n, rng)
    shapes = {"grass": (300, 3000, 4.0), "stone": (600, 5000, 6.0), "wood": (200, 2200, 5.0), "sand": (900, 7000, 3.0), "gravel": (500, 6000, 2.5),
              "snow": (200, 2500, 2.0), "metal": (1500, 9000, 7.0), "wool": (100, 900, 3.0), "mud": (80, 800, 2.0), "water": (400, 4000, 2.0), "leaves": (1200, 8000, 2.5)}
    lo, hi, dp = shapes[material]
    y = bandpass(x, lo, hi) * env(n, 0.03, dp)
    if material == "wood":
        y += 0.6 * tone(n, 180 + 20 * variant, 120) * env(n, 0.01, 8)
    if material == "metal":
        y += 0.3 * (tone(n, 1800 + 90 * variant) + tone(n, 2650)) * env(n, 0.005, 5)
    if material in ("gravel", "sand"):
        y *= 1 + 0.6 * (rng.random(n) > 0.92)
    if material == "water":
        y += 0.3 * tone(n, 700 + 60 * variant, 300) * env(n, 0.02, 3)
    return y


def whoosh(rng, weight, variant):
    dur = {"light": 0.25, "medium": 0.35, "heavy": 0.5}[weight]
    n = seconds(dur + 0.03 * variant)
    x = noise(n, rng)
    sweep_lo, sweep_hi = {"light": (2500, 6000), "medium": (1500, 4500), "heavy": (500, 2500)}[weight]
    out = np.zeros(n)
    chunk = 256
    for s in range(0, n, chunk):
        u = s / n
        cut = sweep_lo + (sweep_hi - sweep_lo) * math.sin(math.pi * u)
        out[s:s + chunk] = lowpass(x[s:s + chunk], cut)
    t = np.linspace(0, 1, n)
    return out * np.sin(np.pi * t) ** 1.5


def impact(rng, material, variant):
    n = seconds(0.35)
    if material == "metal":
        y = sum(tone(n, f * (1 + 0.02 * variant)) * env(n, 0.001, 4 + k) for k, f in enumerate((620, 1530, 2770, 4100)))
        y += 0.5 * highpass(noise(n, rng), 3000) * env(n, 0.001, 12)
    elif material == "wood":
        y = tone(n, 210 + 15 * variant, 150) * env(n, 0.002, 6) + 0.4 * bandpass(noise(n, rng), 300, 2500) * env(n, 0.002, 10)
    elif material == "stone":
        y = tone(n, 120, 70) * env(n, 0.002, 5) + 0.7 * bandpass(noise(n, rng), 500, 4000) * env(n, 0.002, 8)
    else:
        y = tone(n, 90 + 10 * variant, 50) * env(n, 0.004, 4) + 0.5 * lowpass(noise(n, rng), 900) * env(n, 0.003, 7)
    return y


def synth(name, rng, variant):
    group, _, kind = name.partition(".")
    if group == "footstep":
        return footstep(rng, kind, variant)
    if group == "weapon":
        if kind.startswith("whoosh_"):
            return whoosh(rng, kind.split("_")[1], variant)
        n = seconds(0.45)
        if kind in ("draw_blade", "sheathe_blade"):
            y = highpass(noise(n, rng), 3500) * env(n, 0.05 if kind == "draw_blade" else 0.3, 1.5)
            y += 0.25 * tone(n, 3200, 4200 if kind == "draw_blade" else 2400) * env(n, 0.05, 2)
            return y
        if kind == "draw_haft":
            return bandpass(noise(n, rng), 200, 1500) * env(n, 0.05, 2) + 0.4 * tone(n, 160, 120) * env(n, 0.01, 6)
        if kind == "bow_creak":
            n = seconds(0.6)
            return bandpass(noise(n, rng), 400, 1400) * (0.5 + 0.5 * np.sin(np.linspace(0, 40, n))) * env(n, 0.2, 1)
        if kind == "crossbow_crank":
            n = seconds(0.5)
            clicks = (np.sin(np.linspace(0, 2 * np.pi * 14, n)) > 0.96).astype(float)
            return lowpass(clicks, 4000) * 3 + 0.2 * bandpass(noise(n, rng), 800, 3000) * env(n, 0.05, 1)
        if kind == "shield_raise":
            return bandpass(noise(n, rng), 200, 2000) * env(n, 0.08, 2) + 0.3 * tone(n, 300, 260) * env(n, 0.02, 4)
        if kind == "shield_bash":
            return impact(rng, "wood", variant) * 1.2
        if kind == "parry":
            return impact(rng, "metal", variant) + 0.3 * highpass(noise(seconds(0.35), rng), 5000) * env(seconds(0.35), 0.001, 20)
    if group == "foley":
        n = seconds(0.3)
        lo, hi = {"cloth": (300, 3000), "leather": (150, 1800), "chain": (2000, 9000), "plate": (900, 6000)}[kind]
        y = bandpass(noise(n, rng), lo, hi) * env(n, 0.1, 1.5)
        if kind in ("chain", "plate"):
            y += 0.2 * sum(tone(n, f) * env(n, 0.01, 6) for f in ((3100, 4400, 5200) if kind == "chain" else (1100, 1700)))
        return y
    if group == "impact":
        return impact(rng, kind, variant)
    if group == "body":
        n = seconds({"land_soft": 0.25, "land_hard": 0.45, "roll": 0.6, "fall": 0.5, "dodge": 0.35}[kind])
        if kind == "roll":
            return lowpass(noise(n, rng), 700) * np.sin(np.linspace(0, np.pi, n)) ** 0.7
        if kind == "dodge":
            return whoosh(rng, "light", variant) * 0.8
        depth = {"land_soft": 0.5, "land_hard": 1.0, "fall": 1.2}[kind]
        return depth * (tone(n, 80, 40) * env(n, 0.003, 4) + 0.6 * lowpass(noise(n, rng), 600) * env(n, 0.003, 6))
    if group == "creature":
        n = seconds(0.4)
        if kind == "heavy_step":
            return tone(n, 55, 35) * env(n, 0.005, 3) + 0.5 * lowpass(noise(n, rng), 300) * env(n, 0.005, 5)
        if kind == "wing_flap":
            return lowpass(noise(n, rng), 1200) * (np.sin(np.linspace(0, 3 * np.pi, n)) ** 2) * env(n, 0.05, 1)
        if kind == "sniff":
            return bandpass(noise(n, rng), 2000, 6000) * (np.sin(np.linspace(0, 2 * np.pi * 2, n)) > 0.3) * env(n, 0.05, 1)
    if group == "water":
        n = seconds({"splash_small": 0.4, "splash_big": 0.9, "bubbles": 0.8, "surface": 0.5}[kind])
        if kind == "bubbles":
            y = np.zeros(n)
            for _ in range(10):
                s = int(rng.integers(0, n - seconds(0.06)))
                m = seconds(0.06)
                y[s:s + m] += tone(m, float(rng.uniform(500, 1400)), float(rng.uniform(1500, 2600))) * env(m, 0.1, 2)
            return y
        size = 1.6 if kind == "splash_big" else 1.0
        return size * bandpass(noise(n, rng), 300, 6000) * env(n, 0.01, 2.5) + 0.4 * tone(n, 600, 200) * env(n, 0.02, 4)
    if group == "interact":
        n = seconds(0.3)
        if kind == "page":
            return highpass(noise(n, rng), 2500) * env(n, 0.15, 2)
        if kind == "lever_clunk":
            n = seconds(0.35)  # impact() renders 0.35 s
            return impact(rng, "wood", variant) + 0.4 * highpass(noise(n, rng), 4000) * env(n, 0.001, 30)
        if kind == "rummage":
            n = seconds(0.6)
            return bandpass(noise(n, rng), 400, 3000) * (0.4 + 0.6 * (rng.random(n) > 0.5)) * env(n, 0.1, 1)
        if kind == "tool_tap":
            return impact(rng, "metal", variant) * 0.5
        return bandpass(noise(n, rng), 500, 2500) * env(n, 0.01, 4) + 0.3 * tone(n, 400, 300) * env(n, 0.01, 6)
    if group == "ambient":
        n = seconds({"wind_gust": 2.2, "leaves_rustle": 1.4, "chain_jingle": 0.8, "banner_flap": 0.9, "thunder_rumble": 3.0}[kind])
        t = np.linspace(0, 1, n)
        if kind == "wind_gust":
            return lowpass(noise(n, rng), 700) * np.sin(np.pi * t) ** 2 * 1.5
        if kind == "leaves_rustle":
            return highpass(noise(n, rng), 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t + 1)) * np.sin(np.pi * t)
        if kind == "chain_jingle":
            y = np.zeros(n)
            for k in range(6):
                s = int(n * k / 7)
                m = seconds(0.15)
                y[s:s + m] += sum(tone(m, f) for f in (3300 + 100 * k, 4700, 6100)) * env(m, 0.002, 5)
            return y * 0.3
        if kind == "banner_flap":
            return bandpass(noise(n, rng), 200, 1800) * (np.sin(2 * np.pi * 4 * t) ** 2) * np.sin(np.pi * t)
        return lowpass(noise(n, rng), 120) * env(n, 0.05, 1.2) * 4
    if group == "cinematic":
        n = seconds({"boom": 2.5, "riser": 3.0, "sting": 1.6, "whoosh": 1.0, "drone": 4.0}[kind])
        t = np.linspace(0, 1, n)
        if kind == "boom":
            return tone(n, 70, 28) * env(n, 0.002, 2.2) * 1.4 + 0.5 * lowpass(noise(n, rng), 400) * env(n, 0.002, 4)
        if kind == "riser":
            saw = sum(np.sin(2 * np.pi * np.cumsum(np.linspace(110, 440, n)) * k / SR) / k for k in range(1, 6))
            return (0.4 * saw + 0.4 * highpass(noise(n, rng), 2000) * t) * t ** 2
        if kind == "sting":
            return sum(tone(n, f) for f in (220, 261.6, 329.6, 440)) * env(n, 0.005, 2.5) * 0.4
        if kind == "whoosh":
            return whoosh(rng, "heavy", variant) * 1.2
        return sum(tone(n, f, f * 1.003) for f in (55, 82.4, 110)) * np.sin(np.pi * t) * 0.5
    if group == "emote":
        n = seconds({"clap": 0.15, "snap": 0.12, "whistle": 0.7}[kind])
        if kind == "whistle":
            t = np.linspace(0, 1, n)
            f = 1800 + 500 * np.sin(np.pi * t) + 25 * np.sin(2 * np.pi * 6 * t)
            return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t) * 0.6
        cut = 1500 if kind == "clap" else 3500
        return highpass(noise(n, rng), cut) * env(n, 0.002, 10 if kind == "clap" else 14)
    return noise(seconds(0.2), rng) * env(seconds(0.2), 0.01, 3)


def write_wav(path, y):
    y = np.asarray(y, dtype=np.float64)
    peak = np.max(np.abs(y)) or 1.0
    y = np.clip(y / peak * 0.85, -1, 1)
    fade = min(len(y) // 8, seconds(0.01))
    if fade > 1:
        y[:fade] *= np.linspace(0, 1, fade)
        y[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype("<i2").tobytes())


def write_sounds():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg (with libvorbis) is required to encode sounds")
    sound_dir = os.path.join(ASSETS, "sounds")
    events = {}
    tmp = tempfile.mkdtemp()
    count = 0
    for name in names("MWSounds.java"):
        variants = 3 if name.startswith(("footstep.", "weapon.whoosh", "impact.")) else (2 if name.startswith(("body.", "foley.", "water.")) else 1)
        files = []
        for v in range(variants):
            rng = np.random.default_rng(abs(hash_name(name)) + v)
            y = synth(name, rng, v)
            rel = name.replace(".", "/") + ("_%d" % (v + 1) if variants > 1 else "")
            ogg = os.path.join(sound_dir, rel + ".ogg")
            os.makedirs(os.path.dirname(ogg), exist_ok=True)
            wav = os.path.join(tmp, "s.wav")
            write_wav(wav, y)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "3", ogg], check=True)
            files.append({"name": "motionworks:" + rel, "volume": 1.0})
            count += 1
        events[name] = {"subtitle": "subtitles.motionworks." + name, "sounds": files}
    shutil.rmtree(tmp)
    with open(os.path.join(ASSETS, "sounds.json"), "w") as fh:
        json.dump(events, fh, indent=1)
    return count


def hash_name(s):
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0x7FFFFFFF
    return h


# ============================================================================ logo
def write_logo():
    S = 256
    img = Image.new("RGBA", (S, S), (24, 26, 34, 255))
    d = ImageDraw.Draw(img)
    for i in range(S):
        c = int(30 + 40 * i / S)
        d.line([(0, i), (S, i)], fill=(c // 2, c // 2 + 6, c + 20, 255))
    # a stylised running figure built from motion-blurred limbs
    for k, alpha in enumerate((50, 90, 140, 255)):
        dx = -36 + 12 * k
        col = (235, 196, 106, alpha)
        d.ellipse([118 + dx, 52, 146 + dx, 80], fill=col)
        d.line([(132 + dx, 82), (124 + dx, 150)], fill=col, width=12)
        d.line([(128 + dx, 98), (164 + dx, 120)], fill=col, width=9)
        d.line([(128 + dx, 98), (96 + dx, 124)], fill=col, width=9)
        d.line([(124 + dx, 150), (156 + dx, 196)], fill=col, width=11)
        d.line([(124 + dx, 150), (98 + dx, 200)], fill=col, width=11)
    for y in (60, 110, 160):
        d.line([(30, y), (80, y)], fill=(160, 190, 255, 120), width=4)
    img = img.filter(ImageFilter.SMOOTH)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 214, S, S], fill=(14, 15, 20, 220))
    d.text((64, 226), "MOTIONWORKS", fill=(235, 196, 106, 255))
    img.save(os.path.join(ROOT, "src/main/resources/motionworks_logo.png"))


if __name__ == "__main__":
    p = write_particles()
    s = write_sounds()
    write_logo()
    print("particles:", p, "sound files:", s, "logo: ok")

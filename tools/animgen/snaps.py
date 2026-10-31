"""Keeps keyed motion readable at 60 fps.

A short segment with a steep easing (out_expo over 0.1 s) can complete most of its move in a single rendered
frame, so a limb appears to teleport instead of moving fast. For every keyed segment this module measures the
largest change between two frames 1/60 s apart, using the same easing formulas as the Java runtime
(engine/math/Easing.java), and while it exceeds the limit it steps the easing down its family
(expo -> quint -> quart -> cubic -> quad -> sine -> linear), keeping the direction (in, out, in_out). The snap
keeps its character but spans two or three frames. Segments that are shorter than a frame, or whose values are
expressions, are left alone.
"""
import math

FRAME = 1.0 / 60.0
LIMITS = {"rotation": 90.0, "position": 6.0, "scale": 0.35}
CAMERA_ROTATION_LIMIT = 45.0  # fp_view moves the whole first-person camera
C1 = 1.70158
C2 = C1 * 1.525
C3 = C1 + 1


def _out(fn):
    return lambda t: 1 - fn(1 - t)


def _in_out(fn):
    return lambda t: fn(2 * t) / 2 if t < 0.5 else 1 - fn(2 - 2 * t) / 2


BASE = {
    "sine": lambda t: 1 - math.cos(t * math.pi / 2),
    "quad": lambda t: t ** 2,
    "cubic": lambda t: t ** 3,
    "quart": lambda t: t ** 4,
    "quint": lambda t: t ** 5,
    "expo": lambda t: 0.0 if t == 0 else 2 ** (10 * t - 10),
    "circ": lambda t: 1 - math.sqrt(max(0.0, 1 - t * t)),
    "back": lambda t: C3 * t ** 3 - C1 * t ** 2,
}
EASE = {"linear": lambda t: t}
for name, fn in BASE.items():
    EASE["in_" + name] = fn
    EASE["out_" + name] = _out(fn)
    EASE["in_out_" + name] = _in_out(fn)
EASE["in_out_back"] = lambda t: ((2 * t) ** 2 * ((C2 + 1) * 2 * t - C2)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((C2 + 1) * (t * 2 - 2) + C2) + 2) / 2
EASE["snap"] = lambda t: EASE["in_out_expo"](t) * 0.7 + EASE["in_out_cubic"](t) * 0.3

SOFTER = {"expo": "quint", "circ": "quint", "quint": "quart", "quart": "cubic", "back": "cubic", "cubic": "quad", "quad": "sine", "sine": None}


def softer(ease):
    """The next gentler easing of the same direction, or None when only linear is left."""
    if ease == "snap":
        return "in_out_quint"
    for prefix in ("in_out_", "out_", "in_"):
        if ease.startswith(prefix):
            family = ease[len(prefix):]
            if family not in SOFTER:
                return None  # elastic and bounce are deliberate wobbles, not snaps
            nxt = SOFTER[family]
            return prefix + nxt if nxt else "linear"
    return None


def clamped_slope(d0, d1, h0, h1):
    """Fritsch-Butland slope, as MathUtil.clampedSlope."""
    if d0 * d1 <= 0:
        return 0.0
    w1, w2 = 2 * h1 + h0, h1 + 2 * h0
    return (w1 + w2) / (w1 / d0 + w2 / d1)


def hermite(p1, p2, m1, m2, t):
    t2, t3 = t * t, t * t * t
    return (2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2


class Curve:
    """One constant-valued channel, sampled exactly as engine/clip/Channel.java does."""

    def __init__(self, keys, cyclic_length=None):
        self.keys = sorted(((float(t), list(_value(v)), (v.get("e") if isinstance(v, dict) else None) or "linear",
                             (v.get("l") if isinstance(v, dict) else None) or "linear") for t, v in keys.items()), key=lambda k: k[0])
        first, last = self.keys[0], self.keys[-1]
        self.cyclic = (cyclic_length is not None and len(self.keys) >= 3 and first[0] <= 1e-4 and abs(last[0] - cyclic_length) <= 1e-4
                       and all(abs(a - b) <= 1e-4 for a, b in zip(first[1], last[1])))

    def sample(self, t):
        k = self.keys
        if len(k) == 1 or t <= k[0][0]:
            return k[0][1]
        last = len(k) - 1
        if t >= k[last][0]:
            return k[last][1]
        i = max(j for j in range(last) if k[j][0] <= t)
        a, b = k[i], k[i + 1]
        span = b[0] - a[0]
        u = 1.0 if span <= 0 else (t - a[0]) / span
        if b[3] == "step":
            return a[1]
        u = EASE.get(b[2], EASE["linear"])(min(1.0, max(0.0, u)))
        if b[3] in ("smooth", "catmullrom", "catmull_rom", "spline"):
            p = k[i - 1] if i > 0 else (k[last - 1] if self.cyclic else None)
            hp = (a[0] - p[0]) if i > 0 else ((k[last][0] - p[0]) if self.cyclic else 0)
            n = k[i + 2] if i + 2 <= last else (k[1] if self.cyclic else None)
            hn = (n[0] - b[0]) if i + 2 <= last else ((k[1][0] - k[0][0]) if self.cyclic else 0)
            out = []
            for c in range(3):
                v1, v2 = a[1][c], b[1][c]
                d = 0.0 if span <= 0 else (v2 - v1) / span
                m1 = 0.0 if p is None or hp <= 0 else clamped_slope((v1 - p[1][c]) / hp, d, hp, span)
                m2 = 0.0 if n is None or hn <= 0 else clamped_slope(d, (n[1][c] - v2) / hn, span, hn)
                out.append(hermite(v1, v2, m1 * span, m2 * span, u))
            return out
        return [x + (y - x) * u for x, y in zip(a[1], b[1])]

    def frame_jump(self, t0, t1):
        """Largest change between samples one frame apart, for windows starting in [t0, t1]."""
        worst, n = 0.0, max(8, int((t1 - t0) * 240))
        for j in range(n + 1):
            t = t0 + (t1 - t0) * j / n
            a, b = self.sample(t), self.sample(t + FRAME)
            worst = max(worst, max(abs(x - y) for x, y in zip(a, b)))
        return worst


def _value(v):
    return v["v"] if isinstance(v, dict) else v


def soften(clips):
    """Softens every over-limit segment in place; returns [(clip id, bone, channel, time, old ease, new ease)]."""
    changes = []
    for c in clips:
        for bone, chans in c.bones.items():
            for ch, keys in chans.items():
                if not isinstance(keys, dict) or len(keys) < 2:
                    continue
                if any(isinstance(x, str) for v in keys.values() for x in _value(v)):
                    continue
                limit = CAMERA_ROTATION_LIMIT if bone == "fp_view" and ch == "rotation" else LIMITS[ch]
                cyclic = c.length if c.loop == "loop" else None
                times = sorted(keys, key=float)
                for a, b in zip(times, times[1:]):
                    if not isinstance(keys[b], dict) or "e" not in keys[b]:
                        continue
                    start = ease = keys[b]["e"]
                    while Curve(keys, cyclic).frame_jump(float(a), float(b) - FRAME / 2) > limit:
                        nxt = softer(ease)
                        if nxt is None:
                            break
                        ease = nxt
                        if ease == "linear":
                            del keys[b]["e"]
                        else:
                            keys[b]["e"] = ease
                    if ease != start:
                        changes.append((c.id, bone, ch, b, start, ease))
    return changes

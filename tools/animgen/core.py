"""MotionWorks animation authoring DSL.

Clips are authored in Python with motion primitives (holds, timed beats, cycles, strikes,
damped shakes, gait generators) and compiled to the engine's native JSON format. Units follow
ModelPart conventions: rotations in degrees, positions in model pixels with +y pointing down
and -z pointing forward. Helper functions translate intuitive directions (raise arm forward,
lean right) into those conventions so authored intent stays readable.
"""
import json
import math
import os

from rigs import bones_for

CLIPS = []
_IDS = set()


# ---------------------------------------------------------------- directional helpers
# Convention reminders (verified against vanilla setupAnim):
#   limbs hanging down: x<0 swings forward, x>0 back; right limb z>0 = outward, left limb z<0 = outward
#   head/body/root: x>0 pitches forward (look down / lean forward); y>0 turns right; z>0 leans left
#   positions: x<0 = right, y>0 = down, z<0 = forward

def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return ((1, 0, 0), (0, c, -s), (0, s, c))


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return ((c, 0, s), (0, 1, 0), (-s, 0, c))


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def _mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def euler_zyx(m):
    """ModelPart angles (x, y, z) in degrees with m = Rz(z) Ry(y) Rx(x), the order ModelPart applies them."""
    sy = max(-1.0, min(1.0, -m[2][0]))
    if abs(sy) < 0.99999:
        x, y, z = math.atan2(m[2][1], m[2][2]), math.asin(sy), math.atan2(m[1][0], m[0][0])
    else:
        x, y, z = 0.0, math.asin(sy), math.atan2(-m[0][1], m[1][1])
    return [math.degrees(x), math.degrees(y), math.degrees(z)]


class LimbRot(list):
    """A limb rotation built from intuitive angles. Several angle triples give the same rotation, so when it is
    keyed, Clip.key picks the one nearest the previous key and the curve between keys does not spin around."""


def limb(side, fwd=0.0, out=0.0, twist=0.0):
    """Rotation of a limb that hangs down at rest, from intuitive angles. side: 'r' or 'l'.

    fwd swings the limb forward (90 points it ahead, 180 straight up, negative behind), out swings it away from
    the body's midline (negative across it), twist turns it about its own length. They compose in that meaning
    whatever the other angles are: out is measured sideways from the plane the limb swings forward in, so a hand
    raised forward with out < 0 moves toward the midline. Writing (-fwd, twist, out) straight into ModelPart's
    angles, as this once did, is only right for a limb hanging down: ModelPart applies x first, then y and z
    about the parent's axes, so on a raised arm a negative z swung the hand outward ("blowing into your hands"
    held both arms straight out to the sides).
    """
    s = 1 if side == 'r' else -1
    m = _mul(_rx(math.radians(-fwd)), _mul(_rz(math.radians(s * out)), _ry(math.radians(s * twist))))
    return LimbRot(euler_zyx(m))


def arm(side, fwd=0.0, out=0.0, twist=0.0):
    """Arm rotation from intuitive angles (see limb)."""
    return limb(side, fwd, out, twist)


def leg(side, fwd=0.0, out=0.0, twist=0.0):
    """Leg rotation from intuitive angles (see limb)."""
    return limb(side, fwd, out, twist)


def _nearest_angles(v, prev):
    """The angle triple for v's rotation nearest prev: the two Euler solutions, each angle unwrapped."""
    def unwrap(a, p):
        return a + 360.0 * round((p - a) / 360.0)
    best = None
    for cand in ((v[0], v[1], v[2]), (v[0] + 180.0, 180.0 - v[1], v[2] + 180.0)):
        c = [unwrap(cand[i], prev[i]) for i in range(3)]
        d = sum((c[i] - prev[i]) ** 2 for i in range(3))
        if best is None or d < best[0]:
            best = (d, c)
    return best[1]


def tilt(fwd=0.0, right=0.0, roll_right=0.0):
    """Head/body/root rotation: pitch forward, turn right, lean right."""
    return [fwd, right, -roll_right]


def move(right=0.0, up=0.0, fwd=0.0):
    """Position offset in model pixels from intuitive directions."""
    return [-right, -up, -fwd]


def r(v, n=2):
    return round(v, n)


# ---------------------------------------------------------------- triggers

def state(when, group=None, weight=1, min_time=0.0, exit_delay=0.1, desc=""):
    t = {"type": "state", "when": when, "exit_delay": exit_delay}
    if group:
        t["group"] = group
        t["weight"] = weight
    if min_time:
        t["min_time"] = min_time
    if desc:
        t["description"] = desc
    return t


def event(name, when="1", weight=1, chance=1.0, cooldown=0.0, stop_when=None, desc=""):
    t = {"type": "event", "event": name}
    if when != "1":
        t["when"] = when
    if weight != 1:
        t["weight"] = weight
    if chance < 1.0:
        t["chance"] = chance
    if cooldown:
        t["cooldown"] = cooldown
    if stop_when:
        t["stop_when"] = stop_when
    if desc:
        t["description"] = desc
    return t


def manual(stop_when=None, desc=""):
    t = {"type": "manual"}
    if stop_when:
        t["stop_when"] = stop_when
    if desc:
        t["description"] = desc
    return t


# ---------------------------------------------------------------- clip

class Clip:
    def __init__(self, cid, name, category, target, length=1.0, loop="once", layer="action", priority=100,
                 trigger=None, blend_in=0.15, blend_out=0.2, mask=None, speed=None, time=None, weight=None,
                 interruptible=True, interrupt_after=0.6, rig=None, meta=None, file=None):
        if cid in _IDS:
            raise ValueError("duplicate clip id " + cid)
        _IDS.add(cid)
        self.id = cid
        self.name = name
        self.category = category
        self.target = target
        self.length = length
        self.loop = loop
        self.layer = layer
        self.priority = priority
        self.trigger = trigger or manual()
        self.blend_in = blend_in
        self.blend_out = blend_out
        self.mask = mask
        self.speed = speed
        self.time = time
        self.weight = weight
        self.interruptible = interruptible
        self.interrupt_after = interrupt_after
        self.rig = rig or target
        self.meta = dict(meta or {})
        self.file = file or category
        self.bones = {}
        self.events = []
        CLIPS.append(self)

    @property
    def additive(self):
        return self.layer in ("posture", "additive", "reaction")

    # -- raw keyframes
    def key(self, bone, ch, t, v, ease=None, lerp=None):
        chan = self.bones.setdefault(bone, {}).setdefault(ch, {})
        k = "%g" % round(t, 4)
        if isinstance(v, LimbRot):
            prev = self._before(chan, t)
            if prev is not None:
                v = _nearest_angles(v, prev)
        val = [r(x) if isinstance(x, (int, float)) else x for x in v]
        if ease or lerp:
            o = {"v": val}
            if ease:
                o["e"] = ease
            if lerp:
                o["l"] = lerp
            chan[k] = o
        else:
            chan[k] = val
        return self

    @staticmethod
    def _before(chan, t):
        """The numeric value of the latest key before t, or None."""
        best = None
        for k, o in chan.items():
            kt = float(k)
            v = o["v"] if isinstance(o, dict) else o
            if kt < t - 1e-9 and all(isinstance(x, (int, float)) for x in v) and (best is None or kt > best[0]):
                best = (kt, v)
        return None if best is None else best[1]

    def keys(self, bone, ch, seq, lerp=None):
        """seq: iterable of (t, value) or (t, value, ease)."""
        for item in seq:
            t, v = item[0], item[1]
            ease = item[2] if len(item) > 2 else None
            self.key(bone, ch, t, v, ease, lerp)
        return self

    def rot(self, bone, *seq, lerp=None):
        return self.keys(bone, "rotation", seq, lerp)

    def pos(self, bone, *seq, lerp=None):
        return self.keys(bone, "position", seq, lerp)

    def scl(self, bone, *seq, lerp=None):
        return self.keys(bone, "scale", seq, lerp)

    def hold(self, bone, rot=None, pos=None, scale=None):
        """Constant pose for the whole clip."""
        if rot is not None:
            self.key(bone, "rotation", 0, rot)
        if pos is not None:
            self.key(bone, "position", 0, pos)
        if scale is not None:
            self.key(bone, "scale", 0, scale)
        return self

    def cycle(self, bone, ch, fn, samples=8, lerp="smooth"):
        """Samples fn(u) for u in [0,1] across a looping clip.

        The closing key is fn(1), not a copy of fn(0): for periodic motion they are equal, and for a
        full turn (e.g. 360 * u) the last segment keeps rotating forward instead of unwinding backwards.
        """
        for i in range(samples + 1):
            u = i / samples
            self.key(bone, ch, u * self.length, fn(u), lerp=lerp)
        return self

    def ev(self, t, typ, **data):
        e = {"time": round(t, 4), "type": typ}
        for k, v in data.items():
            e[k] = v if isinstance(v, str) else str(v)
        self.events.append(e)
        return self

    def tag(self, **kv):
        self.meta.update({k: str(v) for k, v in kv.items()})
        return self

    def to_json(self):
        o = {"name": self.name, "category": self.category, "target": self.target, "rig": self.rig,
             "length": round(self.length, 4), "loop": self.loop, "layer": self.layer, "priority": self.priority,
             "blend_in": self.blend_in, "blend_out": self.blend_out, "trigger": self.trigger, "bones": self.bones}
        if self.additive:
            o["additive"] = True
        if self.mask:
            o["mask"] = self.mask
        if self.speed is not None:
            o["speed"] = self.speed
        if self.time is not None:
            o["time"] = self.time
        if self.weight is not None:
            o["weight"] = self.weight
        if not self.interruptible:
            o["interruptible"] = False
        if self.interrupt_after != 0.6:
            o["interrupt_after"] = self.interrupt_after
        if self.events:
            o["events"] = sorted(self.events, key=lambda e: e["time"])
        meta = {"controller": self.layer, "model": self.rig, "status": "complete", "testing": "auto-validated"}
        meta.update(self.meta)
        o["meta"] = meta
        return o


# ---------------------------------------------------------------- primitives

def wave(u, phase=0.0, harmonic=1):
    return math.sin((u * harmonic + phase) * 2 * math.pi)


def cwave(u, phase=0.0, harmonic=1):
    return math.cos((u * harmonic + phase) * 2 * math.pi)


def stroke(u, split=0.8):
    """A working stroke for looping chores: eases 0 -> 1 over the first `split` of the cycle, then returns to 0,
    so the cycle closes instead of snapping back at the seam."""
    if u < split:
        x = u / split
    else:
        x = 1 - (u - split) / (1 - split)
    return x * x * (3 - 2 * x)


def strike(c, bone, rest, windup, impact, follow, t_wind, t_imp, t_follow, t_end=None, ch="rotation", settle=None):
    """Anticipation -> impact -> follow-through -> recovery for one bone.

    Wind-up eases in (slow build), the strike snaps out (fast, decelerating into impact),
    follow-through overshoots with back easing, recovery settles smoothly.
    """
    t_end = c.length if t_end is None else t_end
    c.key(bone, ch, 0, rest)
    c.key(bone, ch, t_wind, windup, "out_quad")
    c.key(bone, ch, t_imp, impact, "in_quart")
    c.key(bone, ch, t_follow, follow, "out_back")
    if settle is not None:
        c.key(bone, ch, (t_follow + t_end) / 2, settle, "in_out_sine")
    c.key(bone, ch, t_end, rest, "in_out_sine")
    return c


def shake(c, bone, base, axis, amp, freq, t0, t1, decay=True, ch="rotation"):
    """Damped oscillation on one axis between t0 and t1."""
    n = max(2, int((t1 - t0) * freq * 2))
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        a = amp * ((1 - i / n) if decay else 1.0) * (1 if i % 2 == 0 else -1)
        if i == n:
            a = 0
        v = list(base)
        v[axis] += a
        c.key(bone, ch, t, v, lerp="smooth")
    return c


def beats(c, bone, ch, seq, lerp=None):
    """Explicit timed poses: [(t, value, ease?), ...]."""
    return c.keys(bone, ch, seq, lerp)


# ---------------------------------------------------------------- humanoid gait

def biped(c, stride=30, arm_swing=28, arm_out=4, bob=0.8, twist=4, sway=2.0, lean=0, head_bob=2.0, arms=True,
          right_arm=None, left_arm=None, legs=True, knee_lift=0.0, asym=0.0, bounce=0.0, foot_events=True,
          head_hold=None, body_extra=None, samples=8, phase=0.0, root_pitch=0.0, arm_phase=0.0, legs_out=0.0, side_sign=None):
    """Two-legged gait cycle. right_arm/left_arm: fixed [fwd, out, twist] to override swing (holding items)."""
    def L(u):
        return u + phase
    if legs:
        c.cycle("right_leg", "rotation", lambda u: leg('r', -stride * cwave(L(u)) + knee_lift * max(0, wave(L(u))) + asym * stride * 0.3, legs_out), samples)
        c.cycle("left_leg", "rotation", lambda u: leg('l', stride * cwave(L(u)) + knee_lift * max(0, -wave(L(u))) - asym * stride * 0.2, legs_out), samples)
    if arms:
        if right_arm is None:
            c.cycle("right_arm", "rotation", lambda u: arm('r', arm_swing * cwave(L(u) + arm_phase), arm_out + 2 * max(0, cwave(L(u)))), samples)
        else:
            c.cycle("right_arm", "rotation", lambda u: arm('r', right_arm[0] + 2 * wave(L(u), 0, 2), right_arm[1], right_arm[2] if len(right_arm) > 2 else 0), samples)
        if left_arm is None:
            c.cycle("left_arm", "rotation", lambda u: arm('l', -arm_swing * cwave(L(u) + arm_phase), arm_out + 2 * max(0, -cwave(L(u)))), samples)
        else:
            c.cycle("left_arm", "rotation", lambda u: arm('l', left_arm[0] + 2 * wave(L(u), 0.25, 2), left_arm[1], left_arm[2] if len(left_arm) > 2 else 0), samples)
    c.cycle("body", "rotation", lambda u: [x + y for x, y in zip(tilt(lean, twist * cwave(L(u)), 0), body_extra(u) if body_extra else (0, 0, 0))], samples)
    c.cycle("mw_root", "position", lambda u: move(0, -bob * 0.5 * (1 + cwave(L(u), 0, 2)) + bounce * max(0, wave(L(u), 0.25, 2)), 0), samples)
    c.cycle("mw_root", "rotation", lambda u: tilt(root_pitch, 0, sway * wave(L(u))), samples)
    if head_hold is None:
        c.cycle("head", "rotation", lambda u: tilt(-lean * 0.6 + head_bob * cwave(L(u), 0.1, 2), -twist * 0.5 * cwave(L(u)), 0), samples)
    else:
        c.cycle("head", "rotation", lambda u: [head_hold[0] + head_bob * cwave(L(u), 0.1, 2), head_hold[1], head_hold[2]], samples)
    if side_sign:
        # Direction-adaptive lateral motion: yaw and roll components follow the sign expression,
        # so one clip covers both directions instead of a mirrored pair.
        for bone, ch in (("body", "rotation"), ("mw_root", "rotation"), ("head", "rotation")):
            for k, v in c.bones.get(bone, {}).get(ch, {}).items():
                val = v["v"] if isinstance(v, dict) else v
                for i in (1, 2):
                    if isinstance(val[i], (int, float)) and abs(val[i]) > 1e-6:
                        val[i] = "%g * (%s)" % (val[i], side_sign)
    if foot_events:
        c.ev(c.length * ((0.0 - phase) % 1.0), "footstep", foot="left")
        c.ev(c.length * ((0.5 - phase) % 1.0), "footstep", foot="right")
    return c


# ---------------------------------------------------------------- quadruped gait

GAITS = {
    # phase offsets per leg: (left_hind, left_front, right_hind, right_front)
    "walk": (0.0, 0.25, 0.5, 0.75),
    "amble": (0.0, 0.2, 0.5, 0.7),
    "trot": (0.0, 0.5, 0.5, 0.0),
    "pace": (0.0, 0.0, 0.5, 0.5),
    "canter": (0.0, 0.35, 0.3, 0.65),
    "gallop": (0.0, 0.55, 0.1, 0.65),
    "bound": (0.0, 0.5, 0.0, 0.5),
    "waddle": (0.0, 0.5, 0.5, 0.0),
}


def warp(u, duty):
    """Remaps a cycle so the swing (foot in the air) phase is shorter than stance."""
    u = u % 1.0
    if u < duty:
        return 0.5 * u / duty
    return 0.5 + 0.5 * (u - duty) / (1 - duty)


def quad_gait(c, gait="walk", stride=26, duty=0.6, bob=0.6, pitch=1.5, roll=1.5, head_bob=3.0, head_base=0.0,
              head_phase=0.0, head_yaw=0.0, tail=None, tail_amp=8, legs=None, front_scale=1.0, samples=8,
              body_bone=None, body_amp=0.0, lift=0.0, snap=0.0, splay=0.0, yaw=0.0, roll_phase=0.0, pitch_phase=0.1, tail_phase=0.2):
    """Four-legged gait from footfall pattern. legs: (lh, lf, rh, rf) bone names.

    Character controls change the shape of the motion, not just its size:
      snap        second harmonic on the leg swing (stiff, choppy steps)
      splay       outward leg roll during swing (wide, paddling steps)
      yaw         body twist with each stride (rolling, bear-like walk)
      roll_phase / pitch_phase / tail_phase   timing of body sway and tail relative to footfalls
    """
    lh, lf, rh, rf = legs or ("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg")
    ph = GAITS[gait]
    for bone, p, side, scale in ((lh, ph[0], 'l', 1.0), (lf, ph[1], 'l', front_scale), (rh, ph[2], 'r', 1.0), (rf, ph[3], 'r', front_scale)):
        def f(u, p=p, scale=scale, side=side):
            w = warp(u + p, duty)
            a = w * 2 * math.pi
            x = -stride * scale * math.cos(a) + lift * max(0, math.sin(a)) * -1 + snap * stride * scale * math.sin(2 * a)
            z = splay * max(0, math.sin(a)) * (1 if side == 'r' else -1)
            return [r(x), 0, r(z)]
        c.cycle(bone, "rotation", f, samples)
    harmonic = 1 if gait in ("gallop", "bound", "canter") else 2
    c.cycle("mw_center", "position", lambda u: move(0, -bob * 0.5 * (1 + cwave(u, 0, harmonic)), 0), samples)
    c.cycle("mw_center", "rotation", lambda u: tilt(pitch * wave(u, pitch_phase, harmonic), yaw * wave(u, roll_phase + 0.25), roll * wave(u, roll_phase)), samples)
    c.cycle("head", "rotation", lambda u: [head_base + head_bob * cwave(u, head_phase, harmonic), head_yaw * wave(u), 0], samples)
    if tail:
        c.cycle(tail, "rotation", lambda u: [0, tail_amp * wave(u, tail_phase), 0], samples)
    if body_bone and body_amp:
        c.cycle(body_bone, "rotation", lambda u: [0, body_amp * wave(u), 0], samples)
    return c


def emit(outdir, registry_csv, inventory_md):
    """Writes clip JSON grouped by file, the registry CSV and the inventory summary."""
    by_file = {}
    for c in CLIPS:
        by_file.setdefault(c.file, {})[c.id] = c.to_json()
    for f, clips in by_file.items():
        path = os.path.join(outdir, f + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump({"format_version": "motionworks.v1", "clips": clips}, fh, separators=(",", ":"))
    return by_file


def check_bones():
    errors = []
    for c in CLIPS:
        allowed = bones_for(c.target)
        for b in c.bones:
            if b not in allowed:
                errors.append("%s: bone '%s' not in target %s" % (c.id, b, c.target))
    return errors

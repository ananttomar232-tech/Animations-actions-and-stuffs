"""Shared building blocks for mob animation modules.

Layer usage for mobs:
  base      locomotion (walk/run/swim/fly) - time-driven by the vanilla limb swing so feet stay in sync
  overlay   sustained behaviours (graze, sit, lie, beg, sleep) that own the pose
  action    one-shot actions (attacks, rears, leaps)
  gesture   short one-shots that can play over behaviours (vocalize, ear flick, head toss)
  additive  layered life (breathing, tail swish) that keeps vanilla head tracking intact
"""
import math

from core import Clip, state, event, wave, cwave, tilt, move, quad_gait, r

VANILLA_CYCLE = 2 * math.pi / 0.6662  # limb-swing units per vanilla leg cycle


def mob(cid, name, cat, target, L, trig, layer="overlay", pri=100, loop=None, file=None, blend_in=None, blend_out=None, time=None, weight=None, **kw):
    if loop is None:
        loop = "loop" if trig.get("type") == "state" else "once"
    if blend_in is None:
        blend_in = 0.25 if layer in ("base", "overlay") else 0.08
    if blend_out is None:
        blend_out = 0.3 if layer in ("base", "overlay") else 0.2
    return Clip(cid, name, cat, target, length=L, loop=loop, layer=layer, priority=pri, trigger=trig, file=file, blend_in=blend_in,
                blend_out=blend_out, time=time, weight=weight, **kw)


def driven(L, cycles=1.0, k=2.2, units=VANILLA_CYCLE):
    """Time and weight expressions that lock a looping gait clip to the vanilla limb swing."""
    return {"time": "q.limb_swing * %g" % round(L * cycles / units, 5), "weight": "math.clamp(q.limb_swing_amount * %g, 0, 1)" % k}


def gait(cid, name, cat, target, when, L, file, pri=100, cycles=1.0, k=2.2, units=VANILLA_CYCLE, keep_head=False, synced=True, **params):
    """Quadruped locomotion clip on the base layer, synced to the limb swing.

    The head channel is dropped unless keep_head is set, so vanilla look-at tracking survives walking.
    """
    extra = driven(L, cycles, k, units) if synced else {}
    c = mob(cid, name, cat, target, L, state(when, exit_delay=0.15), layer="base", pri=pri, file=file, **extra)
    quad_gait(c, **params)
    if not keep_head:
        c.bones.pop("head", None)
    return c


def life(cid, name, cat, target, when, L, file, fns, pri=60, group=None, weight=1):
    """Additive looping life layer: fns {"bone:rot"/"bone:pos": f(u) -> vec}."""
    c = mob(cid, name, cat, target, L, state(when, group=group, weight=weight, exit_delay=0.2), layer="additive", pri=pri, file=file)
    for key, fn in fns.items():
        bone, _, ch = key.partition(":")
        c.cycle(bone, "rotation" if ch == "rot" else ("position" if ch == "pos" else "scale"), fn)
    return c


def loop_state(cid, name, cat, target, when, L, file, fns, pri=120, layer="overlay", group=None, weight=1, exit_delay=0.15, min_time=0.0, loop=None):
    """State clip from per-channel functions of u in [0, 1]. Periodic functions loop; a build-up (a ramp that
    does not return to its start) must pass loop="hold" so it keeps its final pose instead of snapping back."""
    c = mob(cid, name, cat, target, L, state(when, group=group, weight=weight, exit_delay=exit_delay, min_time=min_time), layer=layer, pri=pri, file=file, loop=loop)
    for key, fn in fns.items():
        bone, _, ch = key.partition(":")
        c.cycle(bone, "rotation" if ch == "rot" else ("position" if ch == "pos" else "scale"), fn)
    return c


def beat(cid, name, cat, target, trig, L, file, tracks, pri=150, layer="action", events=(), loop="once", **kw):
    """Keyframed clip: tracks {"bone:rot": [(t, vec, ease?), ...]}."""
    c = mob(cid, name, cat, target, L, trig, layer=layer, pri=pri, file=file, loop=loop, **kw)
    for key, seq in tracks.items():
        bone, _, ch = key.partition(":")
        c.keys(bone, "rotation" if ch == "rot" else ("position" if ch == "pos" else "scale"), seq, lerp="smooth")
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


def legs_fold(c, t, legs, fold, ease=None):
    """Keys every leg in `legs` (name -> forward angle) at time t."""
    for bone, ang in legs.items():
        c.key(bone, "rotation", t, [-ang * fold, 0, 0], ease)


Z = (0, 0, 0)
QLEGS = ("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg")


def quad_lie(c, t0, t1, drop, front=80, hind=-80, roll=0.0, head=None):
    """Lie-down transition between t0 and t1 for a QUAD rig (front legs fold forward, hind legs back)."""
    for bone in QLEGS:
        ang = front if "front" in bone else hind
        c.key(bone, "rotation", t0, [0, 0, 0])
        c.key(bone, "rotation", t1, [-ang, 0, 0], "in_out_sine")
    c.key("mw_center", "position", t0, [0, 0, 0])
    c.key("mw_center", "position", t1, move(0, -drop, 0), "in_out_sine")
    if roll:
        c.key("mw_center", "rotation", t0, [0, 0, 0])
        c.key("mw_center", "rotation", t1, tilt(0, 0, roll), "in_out_sine")
    if head is not None:
        c.key("head", "rotation", t0, [0, 0, 0])
        c.key("head", "rotation", t1, head, "in_out_sine")
    return c


def chew(u, rate=4, amp=3.0):
    return amp * max(0.0, wave(u, 0, rate))


def nod(u, amp, harmonic=1, phase=0.0):
    return amp * wave(u, phase, harmonic)


__all__ = ["mob", "driven", "gait", "life", "loop_state", "beat", "legs_fold", "quad_lie", "chew", "nod", "Z", "QLEGS", "VANILLA_CYCLE",
           "state", "event", "wave", "cwave", "tilt", "move", "quad_gait", "r", "Clip"]

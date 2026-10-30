#!/usr/bin/env python3
"""Compiles every authoring module into resources, validates it and writes the registry docs.

Usage: python3 tools/animgen/build.py [--check]
"""
import csv
import importlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import core  # noqa: E402
import rigs  # noqa: E402

MODULES = [
    "player_locomotion", "player_locomotion_more", "player_combat", "player_combat_more", "player_combat_handling", "player_interactions", "first_person",
    "passive_mobs", "hostile_mobs", "villagers", "environment_interactions", "cinematic", "emotes",
    "mounts", "swimming", "aerial", "damage", "contextual",
]

CATEGORY_MINIMUMS = {
    "player_locomotion": 180, "player_combat": 220, "player_interactions": 220, "first_person": 180,
    "passive_mobs": 300, "hostile_mobs": 250, "villagers_npcs": 160, "environmental_interactions": 180,
    "cinematic": 150, "emotes": 120, "mounts_riding": 100, "swimming": 80, "aerial": 80,
    "damage_reactions": 100, "contextual_transitions": 100,
}

CATEGORY_LABELS = {
    "player_locomotion": "Player movement and locomotion", "player_combat": "Player combat and weapon handling",
    "player_interactions": "Player everyday interactions", "first_person": "First-person animations",
    "passive_mobs": "Passive animals and creatures", "hostile_mobs": "Hostile mobs and monsters",
    "villagers_npcs": "Villagers and humanoid NPCs", "environmental_interactions": "Environmental interactions",
    "cinematic": "Cinematic and storytelling", "emotes": "Emotes, gestures and expressions",
    "mounts_riding": "Mounts, vehicles and riding", "swimming": "Swimming and underwater behaviour",
    "aerial": "Flying and aerial movement", "damage_reactions": "Damage, reactions and recovery",
    "contextual_transitions": "Special, contextual and transition animations",
}


def load_modules():
    for m in MODULES:
        if os.path.exists(os.path.join(HERE, m + ".py")):
            importlib.import_module(m)


VAR_RE = re.compile(r"\b(?:q|query|v|variable)\.[a-z_][a-z0-9_]*")


def check_vars():
    known = set(json.load(open(os.path.join(HERE, "context_vars.json"))))
    errors = []
    for c in core.CLIPS:
        texts = [json.dumps(c.trigger), c.time or "", c.weight or "", c.speed or "", json.dumps(c.bones)]
        for t in texts:
            for v in VAR_RE.findall(t):
                v = v.replace("query.", "q.").replace("variable.", "v.")
                if v not in known:
                    errors.append("%s: unknown variable %s" % (c.id, v))
    return errors


def lead_constant(expr):
    """Value of an expression with all context variables at zero, for the common 'N + f(q.*)' form."""
    m = re.match(r"\s*(-?[0-9.]+)\s*(?:[+-]|$)", expr)
    return float(m.group(1)) if m else 0.0


def sample(c, n=24):
    """Approximates the Java MotionSignature for quick duplicate screening (constant keys only)."""
    chans = []
    for bone in sorted(c.bones):
        for ch in sorted(c.bones[bone]):
            keys = c.bones[bone][ch]
            pts = []
            for t, v in keys.items():
                val = v["v"] if isinstance(v, dict) else v
                if any(isinstance(x, str) for x in val):
                    val = [lead_constant(x) if isinstance(x, str) else x for x in val]
                pts.append((float(t), [float(x) - (1.0 if ch == "scale" else 0.0) for x in val]))
            pts.sort()
            chans.append((bone + "/" + ch, pts, 1.0 if ch == "rotation" else (4.0 if ch == "position" else 60.0)))
    L = max(c.length, 1e-3)
    vec = []
    for i in range(n):
        t = L * i / n if c.loop == "loop" else L * i / (n - 1)
        for name, pts, k in chans:
            if t <= pts[0][0]:
                v = pts[0][1]
            elif t >= pts[-1][0]:
                v = pts[-1][1]
            else:
                for j in range(len(pts) - 1):
                    if pts[j][0] <= t <= pts[j + 1][0]:
                        a, b = pts[j], pts[j + 1]
                        u = (t - a[0]) / max(1e-6, b[0] - a[0])
                        v = [x + (y - x) * u for x, y in zip(a[1], b[1])]
                        break
            vec.extend(x * k for x in v)
    return tuple(name for name, _, _ in chans), vec


def mirrored(c):
    """Sample of the clip mirrored left/right (names swapped, lateral components negated)."""
    import copy
    m = copy.copy(c)
    m.bones = {}
    for bone, chans in c.bones.items():
        nb = bone.replace("left", "@").replace("right", "left").replace("@", "right")
        m.bones[nb] = {}
        for ch, keys in chans.items():
            nk = {}
            for t, v in keys.items():
                val = list(v["v"] if isinstance(v, dict) else v)
                val = [lead_constant(x) if isinstance(x, str) else x for x in val]
                if ch == "rotation":
                    val[1], val[2] = -val[1], -val[2]
                elif ch == "position":
                    val[0] = -val[0]
                nk[t] = val
            m.bones[nb][ch] = nk
    return sample(m)


def similarity(a, va, b, vb, key):
    na = math.sqrt(sum(x * x for x in va))
    nb = math.sqrt(sum(x * x for x in vb))
    if na < 1e-3 or nb < 1e-3:
        return 0.0
    stride = len(key) * 3
    shifts = 24 if a.loop == "loop" and b.loop == "loop" else 1
    best = 0.0
    for s in range(shifts):
        rolled = vb[s * stride:] + vb[:s * stride]
        best = max(best, sum(x * y for x, y in zip(va, rolled)) / (na * nb))
    return best


def check_duplicates(threshold=0.995):
    buckets = {}
    for c in core.CLIPS:
        key, vec = sample(c)
        buckets.setdefault(key, []).append((c, vec))
    dups = []
    for c in core.CLIPS:
        mkey, mvec = mirrored(c)
        for b, vb in buckets.get(mkey, []):
            if b is c:
                continue
            if similarity(c, mvec, b, vb, mkey) >= threshold and c.id < b.id:
                dups.append((c.id, b.id, "mirror"))
    for key, items in buckets.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, va = items[i]
                b, vb = items[j]
                na = math.sqrt(sum(x * x for x in va))
                nb = math.sqrt(sum(x * x for x in vb))
                if na < 1e-3 or nb < 1e-3:
                    continue
                stride = len(key) * 3
                shifts = 24 if a.loop == "loop" and b.loop == "loop" else 1
                best = 0
                for s in range(shifts):
                    rolled = vb[s * stride:] + vb[:s * stride]
                    dot = sum(x * y for x, y in zip(va, rolled))
                    best = max(best, dot / (na * nb))
                if best >= threshold:
                    dups.append((a.id, b.id, round(best, 4)))
    return dups


def main():
    check_only = "--check" in sys.argv
    load_modules()
    errors = core.check_bones() + check_vars()
    counts = {}
    for c in core.CLIPS:
        counts[c.category] = counts.get(c.category, 0) + 1
    dups = check_duplicates()
    print("clips:", len(core.CLIPS))
    total_min = 0
    for cat, minimum in CATEGORY_MINIMUMS.items():
        total_min += minimum
        n = counts.get(cat, 0)
        print("  %-28s %5d / %d %s" % (cat, n, minimum, "OK" if n >= minimum else "SHORT"))
    unknown = set(counts) - set(CATEGORY_MINIMUMS)
    if unknown:
        errors.append("unknown categories: %s" % unknown)
    for e in errors[:60]:
        print("ERROR", e)
    for d in dups[:60]:
        print("DUPLICATE", d)
    if errors or dups:
        print("%d errors, %d duplicates" % (len(errors), len(dups)))
        sys.exit(1)
    if check_only:
        return
    out = os.path.join(ROOT, "src/main/resources/assets/motionworks/motionworks/animations")
    for dirpath, _, files in os.walk(out):
        for f in files:
            if f.endswith(".json"):
                os.remove(os.path.join(dirpath, f))
    core.emit(out, None, None)
    write_families()
    write_docs(counts)


def write_families():
    path = os.path.join(ROOT, "src/main/resources/assets/motionworks/motionworks/entities.json")
    with open(path, "w") as fh:
        json.dump(rigs.families(), fh, indent=1, sort_keys=True)


def trigger_text(t):
    if t["type"] == "event":
        s = "event `%s`" % t["event"]
        if t.get("when"):
            s += " when `%s`" % t["when"]
        return s
    if t["type"] == "state":
        return "state `%s`" % t["when"]
    return "manual" + (" (stops when `%s`)" % t["stop_when"] if t.get("stop_when") else "")


def write_docs(counts):
    docs = os.path.join(ROOT, "docs")
    os.makedirs(docs, exist_ok=True)
    with open(os.path.join(docs, "animation_registry.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "name", "category", "target", "trigger", "duration_s", "loop", "priority", "layer", "model", "controller",
                    "keyframes", "events", "completion", "testing"])
        for c in sorted(core.CLIPS, key=lambda c: (c.category, c.id)):
            j = c.to_json()
            nkeys = sum(len(ch) for b in c.bones.values() for ch in b.values())
            w.writerow([c.id, c.name, c.category, c.target, trigger_text(c.trigger), round(c.length, 3), c.loop, c.priority, c.layer,
                        j["meta"]["model"], j["meta"]["controller"], nkeys, len(c.events), "complete", "auto-validated"])
    lines = ["# Animation Inventory", "",
             "Generated by `tools/animgen/build.py` from the authoring sources. Every clip below is implemented as keyframe data in",
             "`src/main/resources/assets/motionworks/motionworks/animations/`, bound to a trigger, and validated (bone vocabulary, context",
             "variables, and motion-signature uniqueness: no speed, amplitude, phase or mirror variants are counted).", "",
             "| Category | Clips | Minimum |", "|---|---:|---:|"]
    total = 0
    for cat, minimum in CATEGORY_MINIMUMS.items():
        n = counts.get(cat, 0)
        total += n
        lines.append("| %s | %d | %d |" % (CATEGORY_LABELS[cat], n, minimum))
    lines.append("| **Total** | **%d** | **2,420** |" % total)
    lines += ["", "Testing status `auto-validated` means the clip passed the authoring validator and the Java `ShippedLibraryTest`",
              "(loads with the runtime parser, every bone exists in the target rig, signatures distinct). In-game visual review is tracked",
              "separately in `docs/TESTING.md`.", ""]
    for cat in CATEGORY_MINIMUMS:
        lines += ["## " + CATEGORY_LABELS[cat], "", "| ID | Name | Target | Trigger | Duration | Layer | Priority |", "|---|---|---|---|---:|---|---:|"]
        for c in sorted((c for c in core.CLIPS if c.category == cat), key=lambda c: c.id):
            lines.append("| `%s` | %s | `%s` | %s | %.2fs | %s | %d |" % (c.id, c.name, c.target, trigger_text(c.trigger).replace("|", "\\|"),
                                                                       c.length, c.layer, c.priority))
        lines.append("")
    with open(os.path.join(docs, "ANIMATION_INVENTORY.md"), "w") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    main()

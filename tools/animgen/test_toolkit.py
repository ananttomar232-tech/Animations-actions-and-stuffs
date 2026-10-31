#!/usr/bin/env python3
"""Tests for the animation authoring toolkit and for consistency between the library, the assets and the Java code.

Run: python3 -m unittest tools/animgen/test_toolkit.py   (or python3 tools/animgen/test_toolkit.py)
"""
import json
import math
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build  # noqa: E402
import core  # noqa: E402
from core import Clip, manual, event, state, quad_gait, wave  # noqa: E402

ROOT = build.ROOT
ASSETS = os.path.join(ROOT, "src/main/resources/assets/motionworks")
build.load_modules()
LIBRARY = list(core.CLIPS)


class Scratch:
    """Temporarily swaps the global clip registry so tests can author throwaway clips."""

    def __enter__(self):
        self.clips, self.ids = core.CLIPS[:], set(core._IDS)
        core.CLIPS.clear()
        return self

    def __exit__(self, *exc):
        core.CLIPS[:] = self.clips
        core._IDS.clear()
        core._IDS.update(self.ids)


def load_json(path):
    return json.loads(build.read(path))


def vec(clip):
    return build.sample(clip)[1]


def cosine(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


class GaitTests(unittest.TestCase):
    def test_default_controls_reproduce_the_plain_gait(self):
        with Scratch():
            a = Clip("t.a", "a", "passive_mobs", "minecraft:cow", length=1.0, loop="loop")
            quad_gait(a, gait="walk", stride=20)
            b = Clip("t.b", "b", "passive_mobs", "minecraft:cow", length=1.0, loop="loop")
            quad_gait(b, gait="walk", stride=20, snap=0.0, splay=0.0, yaw=0.0)
            self.assertEqual(a.bones, b.bones)

    def test_character_controls_change_shape_not_just_size(self):
        with Scratch():
            base = Clip("t.base", "base", "passive_mobs", "minecraft:cow", length=1.0, loop="loop")
            quad_gait(base, gait="walk", stride=20)
            bigger = Clip("t.big", "big", "passive_mobs", "minecraft:cow", length=1.0, loop="loop")
            quad_gait(bigger, gait="walk", stride=30, bob=0.9, pitch=2.25, roll=2.25)
            snappy = Clip("t.snap", "snap", "passive_mobs", "minecraft:cow", length=1.0, loop="loop")
            quad_gait(snappy, gait="walk", stride=20, snap=0.35, yaw=3)
            self.assertGreater(cosine(vec(base), vec(bigger)), 0.999, "scaling is an amplitude variant")
            self.assertLess(cosine(vec(base), vec(snappy)), 0.99, "snap and yaw must change the motion's shape")

    def test_full_turn_loop_keeps_rotating_forward(self):
        with Scratch():
            c = Clip("t.spin", "spin", "emotes", "@player", length=1.0, loop="loop")
            c.cycle("mw_root", "rotation", lambda u: [0, 360 * u, 0])
            keys = sorted((float(t), v[1] if isinstance(v, list) else v["v"][1]) for t, v in c.bones["mw_root"]["rotation"].items())
            self.assertEqual(keys[-1][1], 360)
            self.assertTrue(all(b[1] > a[1] for a, b in zip(keys, keys[1:])), "spin must be monotonic")


class SnapTests(unittest.TestCase):
    def test_curve_sampling_matches_the_runtime(self):
        import snaps
        hold = snaps.Curve({"0": {"v": [0, 0, 0], "l": "smooth"}, "0.6": {"v": [45, 0, 0], "l": "smooth"}, "1.4": {"v": [45, 0, 0], "l": "smooth"},
                            "2.2": {"v": [0, 0, 0], "l": "smooth"}})
        self.assertAlmostEqual(hold.sample(1.0)[0], 45.0, places=6)  # auto-clamped holds never overshoot (InterpolationTest)
        peak = snaps.Curve({"0": [0, 0, 0], "1": {"v": [10, 0, 0], "l": "smooth"}, "2": {"v": [0, 0, 0], "l": "smooth"}})
        self.assertAlmostEqual(peak.sample(0.5)[0], 5.0, places=6)  # a symmetric ease (ChannelTest.smoothPassesThroughKeys)

    def test_steep_snaps_are_eased_to_span_frames(self):
        import snaps
        with Scratch():
            c = Clip("t.snap", "snap", "player_combat", "@player", length=1.0)
            c.keys("right_arm", "rotation", [(0, [0, 0, 0]), (0.1, [-150, 0, 0], "out_expo"), (1.0, [0, 0, 0])], lerp="smooth")
            changes = snaps.soften([c])
            self.assertTrue(changes)
            curve = snaps.Curve(c.bones["right_arm"]["rotation"])
            self.assertLessEqual(curve.frame_jump(0, 1.0 - snaps.FRAME), snaps.LIMITS["rotation"])

    def test_elastic_wobbles_are_left_alone(self):
        import snaps
        self.assertIsNone(snaps.softer("out_elastic"))
        self.assertEqual(snaps.softer("out_sine"), "linear")


class ValidatorTests(unittest.TestCase):
    def test_unknown_bone_is_rejected(self):
        with Scratch():
            Clip("t.bone", "x", "passive_mobs", "minecraft:cow", trigger=state("1")).key("wing", "rotation", 0, [1, 0, 0])
            self.assertTrue(any("wing" in e for e in core.check_bones()))

    def test_unknown_variable_is_rejected(self):
        with Scratch():
            Clip("t.var", "x", "passive_mobs", "minecraft:cow", trigger=state("q.not_a_variable > 1")).key("head", "rotation", 0, [1, 0, 0])
            self.assertTrue(any("q.not_a_variable" in e for e in build.check_vars()))

    def test_unfired_event_is_rejected(self):
        with Scratch():
            Clip("t.ev", "x", "passive_mobs", "minecraft:cow", trigger=event("never_fired_anywhere")).key("head", "rotation", 0, [1, 0, 0])
            self.assertTrue(any("never_fired_anywhere" in e for e in build.check_events()))

    def test_argument_form_of_a_fired_event_is_accepted(self):
        with Scratch():
            Clip("t.ev2", "x", "passive_mobs", "minecraft:cow", trigger=event("shoot:spit")).key("head", "rotation", 0, [1, 0, 0])
            self.assertEqual(build.check_events(), [])

    def test_scaled_copy_and_mirror_are_flagged(self):
        with Scratch():
            def make(cid, k, side):
                # A mirror swaps left/right bones and negates the lateral (yaw and roll) components.
                s = 1 if side == "right" else -1
                c = Clip(cid, cid, "player_combat", "@player", length=1.0)
                c.keys(side + "_arm", "rotation", [(0, [0, 0, 0]), (0.3, [-90 * k, 0, 20 * k * s]), (1.0, [0, 0, 0])])
                c.keys("body", "rotation", [(0, [0, 0, 0]), (0.3, [5 * k, 10 * k * s, 3 * k * s]), (1.0, [0, 0, 0])])
                return c
            make("t.orig", 1.0, "right")
            make("t.scaled", 1.4, "right")
            make("t.mirror", 1.0, "left")
            dups = build.check_duplicates()
            pairs = {tuple(sorted(d[:2])) for d in dups}
            self.assertIn(("t.orig", "t.scaled"), pairs)
            self.assertTrue(any("t.mirror" in d[:2] for d in dups))

    def test_sequences_reference_real_clips_and_cover_manual_cinematics(self):
        self.assertEqual(build.check_sequences(), [])


class LibraryTests(unittest.TestCase):
    def test_every_category_meets_its_minimum(self):
        counts = {}
        for c in LIBRARY:
            counts[c.category] = counts.get(c.category, 0) + 1
        for cat, minimum in build.CATEGORY_MINIMUMS.items():
            self.assertGreaterEqual(counts.get(cat, 0), minimum, cat)
        self.assertGreaterEqual(len(LIBRARY), 2400)

    def test_library_passes_every_validator(self):
        self.assertEqual(core.check_bones() + build.check_vars() + build.check_events() + build.check_assets(), [])
        self.assertEqual(build.check_duplicates(), [])

    def test_every_clip_has_registry_metadata(self):
        for c in LIBRARY:
            j = c.to_json()
            for k in ("controller", "model", "status", "testing"):
                self.assertIn(k, j["meta"], c.id)
            self.assertGreater(j["length"], 0, c.id)

    def test_emotes_are_tagged_for_the_wheel(self):
        for c in LIBRARY:
            if c.category == "emotes":
                self.assertEqual(c.meta.get("emote"), "true", c.id)
                self.assertIn(c.meta.get("emote_group"), ("gestures", "celebrations", "expressions", "dances"), c.id)


class AssetConsistencyTests(unittest.TestCase):
    def test_sounds_json_covers_every_registered_sound_and_files_exist(self):
        sounds = load_json(os.path.join(ASSETS, "sounds.json"))
        self.assertEqual(set(sounds), build.registered("MWSounds.java"))
        for ev in sounds.values():
            for s in ev["sounds"]:
                path = os.path.join(ASSETS, "sounds", s["name"].split(":", 1)[1] + ".ogg")
                self.assertTrue(os.path.isfile(path), path)

    def test_particles_have_definitions_and_textures(self):
        for name in build.registered("MWParticles.java"):
            d = load_json(os.path.join(ASSETS, "particles", name + ".json"))
            self.assertTrue(d["textures"], name)
            for t in d["textures"]:
                self.assertTrue(os.path.isfile(os.path.join(ASSETS, "textures/particle", t.split(":", 1)[1] + ".png")), t)

    def test_translation_keys_used_by_code_and_sequences_exist(self):
        lang = load_json(os.path.join(ASSETS, "lang/en_us.json"))
        keys = set()
        for dirpath, _, files in os.walk(os.path.join(ROOT, "src/main/java")):
            for fn in files:
                src = build.read(os.path.join(dirpath, fn))
                keys.update(re.findall(r'"((?:motionworks|key\.motionworks|key\.categories\.motionworks)\.[a-z0-9_.]+[a-z0-9_])"', src))
        keys -= {"motionworks.boss", "motionworks.emotes.group"}  # prefixes completed at runtime, checked below
        for boss in ("wither", "ender_dragon", "warden", "elder_guardian"):
            keys |= {"motionworks.boss.%s.title" % boss, "motionworks.boss.%s.subtitle" % boss}
        keys |= {"motionworks.emotes.group." + g for g in ("gestures", "celebrations", "expressions", "dances")}
        for sq in build.sequences().values():
            for e in sq["events"]:
                if e["type"] == "title":
                    keys |= {e["title"], e["subtitle"]}
        for ev in load_json(os.path.join(ASSETS, "sounds.json")).values():
            keys.add(ev["subtitle"])
        missing = sorted(k for k in keys if k not in lang)
        self.assertEqual(missing, [])

    def test_every_entity_family_rig_has_a_profile(self):
        fam = load_json(os.path.join(ASSETS, "motionworks/entities.json"))
        families = fam.get("families", fam)
        rigs = {f[:-5] for f in os.listdir(os.path.join(ASSETS, "motionworks/rigs"))}
        for entity, info in families.items():
            self.assertIn(info["rig"], rigs, entity)

    def test_rig_profile_expressions_use_known_variables(self):
        known = build.runtime_vars()
        rig_dir = os.path.join(ASSETS, "motionworks/rigs")
        drivers = 0
        for fn in sorted(os.listdir(rig_dir)):
            rig = load_json(os.path.join(rig_dir, fn))
            exprs = [n["scale"] for n in rig.get("life_noise", []) if "scale" in n]
            exprs += [e for s in rig.get("springs", []) for e in s.get("targets", []) if e]
            exprs += [e for d in rig.get("drivers", []) for e in d["exprs"] if e]
            drivers += len(rig.get("drivers", []))
            for e in exprs:
                for var in build.VAR_RE.findall(e):
                    self.assertIn(var, known, "%s uses unknown %s" % (fn, var))
        self.assertGreater(drivers, 0, "terrain alignment drivers are shipped")

    def test_context_variable_reference_is_current(self):
        import gen_context_doc
        text, _, _ = gen_context_doc.render()
        self.assertEqual(text, build.read(gen_context_doc.OUT), "run tools/animgen/gen_context_doc.py")
        self.assertNotIn("not assigned", text)

    def test_mixin_config_lists_existing_classes(self):
        cfg = load_json(os.path.join(ROOT, "src/main/resources/motionworks.mixins.json"))
        pkg = cfg["package"].replace(".", "/")
        for name in cfg.get("mixins", []) + cfg.get("client", []):
            path = os.path.join(ROOT, "src/main/java", pkg, name.replace(".", "/") + ".java")
            self.assertTrue(os.path.isfile(path), path)


if __name__ == "__main__":
    unittest.main(verbosity=1)

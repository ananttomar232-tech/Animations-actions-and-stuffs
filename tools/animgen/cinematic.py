"""Cinematic and storytelling animations (category: cinematic) and the sequences that perform them.

Manual clips here are performed by cinematic sequences ("animate" events) and are validated to be
referenced by at least one sequence; the rest are bound to story events (boss intros, advancements,
boss kills). Sequences are skippable, never forced, and are written to assets/.../cinematics.
"""
from core import arm, leg, manual
from mobkit import mob, life, loop_state, beat, Z, state, event, wave, cwave, tilt, move

CAT = "cinematic"
P = "@player"
FP, FM = "cinematic/player", "cinematic/mobs"
SEQUENCES = {}


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def scene(cid, name, L, tracks=None, fns=None, target=P, file=FP, loop=None, pri=500, events=(), trig=None):
    """Cinematic clip; manual unless a trigger is given. Looping clips are 'holds' a sequence can sustain."""
    t = trig or manual(desc="Performed by cinematic sequences")
    lp = loop or ("loop" if fns else "once")
    c = mob(cid, name, CAT, target, L, t, layer="action", pri=pri, file=file, loop=lp, blend_in=0.35, blend_out=0.5)
    for key, seq in (tracks or {}).items():
        bone, _, ch = key.partition(":")
        c.keys(bone, {"rot": "rotation", "pos": "position", "scl": "scale"}[ch], seq, lerp="smooth")
    for key, fn in (fns or {}).items():
        bone, _, ch = key.partition(":")
        c.cycle(bone, {"rot": "rotation", "pos": "position", "scl": "scale"}[ch], fn, samples=12)
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


R, Lh = lambda *a: arm('r', *a), lambda *a: arm('l', *a)
RL, LL = lambda *a: leg('r', *a), lambda *a: leg('l', *a)
def with_kneel(L, extra):
    """One-knee kneel held for the clip's length, plus the given upper-body tracks."""
    d = {"right_leg:rot": [(0, Z), (0.6, RL(90)), (L, RL(90))], "left_leg:rot": [(0, Z), (0.6, LL(20)), (L, LL(20))], "mw_root:pos": [(0, Z), (0.6, move(0, -5, 0)), (L, move(0, -5, 0))]}
    d.update(extra)
    return d


# ============================================================================ player: hero beats
scene("cine.player.kneel_reverent", "Kneel In Reverence", 3.0, with_kneel(3.0, {"head:rot": [(0, Z), (0.8, [30, 0, 0]), (3.0, [32, 0, 0])], "right_arm:rot": [(0, Z), (0.8, R(40, -20, 30)), (3.0, R(40, -20, 30))]}))
scene("cine.player.rise_from_kneel", "Rise From A Kneel", 1.8, {"right_leg:rot": [(0, RL(90)), (1.2, RL(30)), (1.8, Z)], "left_leg:rot": [(0, LL(20)), (1.8, Z)], "mw_root:pos": [(0, move(0, -5, 0)), (1.2, move(0, -1.5, 0)), (1.8, Z)],
                                                                "head:rot": [(0, [30, 0, 0]), (1.2, [-10, 0, 0]), (1.8, Z)], "body:rot": [(0, tilt(10)), (1.0, tilt(-6)), (1.8, Z)]})
scene("cine.player.horizon_gaze", "Gaze To The Horizon", 4.0, fns={"head:rot": lambda u: [-6, 8 * wave(u, 0, 0.5), 0], "body:rot": lambda u: tilt(-3, 0, 1.5 * wave(u)), "right_arm:rot": lambda u: R(2 * wave(u), 4),
                                                                  "cloak:rot": lambda u: [10 + 6 * wave(u, 0, 2), 0, 3 * wave(u)]})
scene("cine.player.draw_sword_slow", "Slowly Draw A Blade", 2.4, {"right_arm:rot": [(0, Z), (0.8, R(-30, -20, 60), "in_out_sine"), (1.6, R(120, 30, -20), "out_quad"), (2.4, R(60, 10, -10))],
                                                                   "body:rot": [(0, Z), (0.8, tilt(4, 20, 0)), (2.4, tilt(-4, -10, 0))], "head:rot": [(0, Z), (1.6, [-6, 0, 0]), (2.4, [6, 0, 0])]},
      events=[(1.2, "sound", {"sound": "motionworks:weapon.draw_blade", "volume": "0.8"})])
scene("cine.player.plant_sword", "Plant The Sword In The Earth", 2.0, {"right_arm:rot": [(0, R(60)), (0.6, R(150, 0, 0)), (0.9, R(40, -10, 0), "in_quart"), (2.0, R(40, -10, 0))],
                                                                       "left_arm:rot": [(0, Z), (1.0, Lh(40, -14, 20)), (2.0, Lh(40, -14, 20))], "body:rot": [(0, Z), (0.9, tilt(20)), (2.0, tilt(10))]},
      events=[(0.9, "impact", {"material": "dirt", "strength": "0.8"})])
scene("cine.player.lean_on_sword", "Lean On The Sword", 4.0, fns={"right_arm:rot": lambda u: R(40, -10), "left_arm:rot": lambda u: Lh(40, -14, 20), "body:rot": lambda u: tilt(14 + 2 * wave(u), 0, 0),
                                                                 "head:rot": lambda u: [6 + 4 * wave(u, 0.2), 0, 0], "left_leg:rot": lambda u: LL(-10)})
scene("cine.player.lantern_into_dark", "Raise A Lantern Into The Dark", 3.0, {"left_arm:rot": [(0, Z), (0.8, Lh(140, 10), "out_quad"), (3.0, Lh(145, 10))], "head:rot": [(0, Z), (0.8, [-10, -20, 0]), (2.0, [-10, 20, 0]), (3.0, [-10, 0, 0])],
                                                                              "body:rot": [(0, Z), (0.8, tilt(-4, 0, 0)), (3.0, tilt(-4))]})
scene("cine.player.cloak_wind", "Cloak Whipping In The Wind", 2.0, fns={"cloak:rot": lambda u: [30 + 20 * wave(u, 0, 3), 0, 10 * wave(u, 0.2, 2)], "body:rot": lambda u: tilt(6, 0, 2 * wave(u)),
                                                                        "right_arm:rot": lambda u: R(20, 10), "head:rot": lambda u: [10, 0, 0]})
scene("cine.player.portal_step", "Step Through The Portal", 2.4, {"right_leg:rot": [(0, Z), (0.8, RL(-30)), (1.4, RL(10)), (2.4, Z)], "body:rot": [(0, Z), (0.8, tilt(-8)), (1.6, tilt(10)), (2.4, Z)],
                                                                   "right_arm:rot": [(0, Z), (1.0, R(60, 20)), (2.4, Z)], "head:rot": [(0, Z), (0.8, [-20, 0, 0]), (2.4, Z)]})
scene("cine.player.collapse_exhausted", "Collapse From Exhaustion", 2.6, {"right_leg:rot": [(0, Z), (0.8, RL(80)), (2.6, RL(90))], "left_leg:rot": [(0, Z), (1.0, LL(80)), (2.6, LL(90))],
                                                                           "mw_root:pos": [(0, Z), (1.0, move(0, -5, 0)), (2.6, move(0, -6, 0))], "body:rot": [(0, Z), (1.4, tilt(40)), (2.6, tilt(50))],
                                                                           "right_arm:rot": [(0, Z), (1.4, R(60, 10)), (2.6, R(70, 10))], "head:rot": [(0, Z), (2.6, [30, 0, 0])]})
scene("cine.player.reach_out", "Reach Out Desperately", 2.0, {"right_arm:rot": [(0, Z), (0.6, R(95, 0, 0), "out_quad"), (1.6, R(100, 4)), (2.0, R(95, 0))], "body:rot": [(0, Z), (0.6, tilt(16)), (2.0, tilt(16))],
                                                               "right_leg:rot": [(0, Z), (0.6, RL(-20)), (2.0, RL(-20))], "head:rot": [(0, Z), (0.6, [-10, 0, 0]), (2.0, [-10, 0, 0])]})
scene("cine.player.catch_breath", "Catch Your Breath", 2.0, fns={"body:rot": lambda u: tilt(30 + 6 * wave(u, 0, 2), 0, 0), "right_arm:rot": lambda u: R(20, -10, 30), "left_arm:rot": lambda u: Lh(20, -10, 30),
                                                               "head:rot": lambda u: [-10 + 6 * wave(u, 0, 2), 0, 0]})
scene("cine.player.determined_march", "Determined March", 1.2, fns={"right_leg:rot": lambda u: RL(25 * cwave(u)), "left_leg:rot": lambda u: LL(-25 * cwave(u)), "right_arm:rot": lambda u: R(-18 * cwave(u), 4),
                                                                   "left_arm:rot": lambda u: Lh(18 * cwave(u), 4), "body:rot": lambda u: tilt(4, 4 * cwave(u), 0), "mw_root:pos": lambda u: move(0, 0.4 * cwave(u, 0, 2), 0)})
scene("cine.player.slow_turn_reveal", "Slow Turn To Face The Camera", 2.4, {"mw_root:rot": [(0, [0, 180, 0]), (2.0, Z, "in_out_sine"), (2.4, Z)], "head:rot": [(0, [0, 40, 0]), (1.6, [0, 0, 0]), (2.4, [-6, 0, 0])]})
scene("cine.player.look_up_awe", "Look Up In Awe", 3.0, {"head:rot": [(0, Z), (1.0, [-45, 0, 0], "out_quad"), (3.0, [-48, 0, 0])], "body:rot": [(0, Z), (1.0, tilt(-10)), (3.0, tilt(-12))],
                                                         "right_arm:rot": [(0, Z), (1.2, R(10, 20)), (3.0, R(10, 20))], "left_arm:rot": [(0, Z), (1.2, Lh(10, 20)), (3.0, Lh(10, 20))], "right_leg:rot": [(0, Z), (0.6, RL(10)), (3.0, RL(10))]})
scene("cine.player.shield_eyes_flash", "Shield Eyes From A Blinding Light", 1.6, {"right_arm:rot": [(0, Z), (0.15, R(130, -20, 40), "out_expo"), (1.3, R(128, -20, 40)), (1.6, R(100, -10, 20))],
                                                                                  "head:rot": [(0, Z), (0.15, [20, -20, 0]), (1.6, [10, 0, 0])], "body:rot": [(0, Z), (0.15, tilt(10, -15, 0)), (1.6, tilt(4))]})
scene("cine.player.surrender", "Hands Raised In Surrender", 2.4, {"right_arm:rot": [(0, Z), (0.6, R(170, 40)), (2.4, R(170, 40))], "left_arm:rot": [(0, Z), (0.6, Lh(170, 40)), (2.4, Lh(170, 40))],
                                                                  "head:rot": [(0, Z), (0.6, [20, 0, 0]), (2.4, [20, 0, 0])]})
scene("cine.player.kneel_grief", "Kneel In Grief", 4.0, with_kneel(4.0, {"body:rot": [(0, Z), (1.0, tilt(30)), (4.0, tilt(34))], "right_arm:rot": [(0, Z), (1.0, R(130, -30, 40)), (4.0, R(130, -30, 40))],
                                                                         "left_arm:rot": [(0, Z), (1.0, Lh(130, -30, 40)), (4.0, Lh(130, -30, 40))], "head:rot": [(0, Z), (1.0, [30, 0, 0]), (2.5, [30, 0, 6]), (4.0, [30, 0, 0])]}))
scene("cine.player.toast", "Raise A Toast", 2.0, {"right_arm:rot": [(0, Z), (0.6, R(150, 20)), (1.2, R(150, 20)), (1.5, R(120, -20, 30)), (2.0, Z)], "head:rot": [(0, Z), (0.6, [-14, 0, 0]), (1.5, [-25, 0, 0]), (2.0, Z)]})
scene("cine.player.read_letter", "Read A Letter", 4.0, fns={"right_arm:rot": lambda u: R(60, -10, 20), "left_arm:rot": lambda u: Lh(60, -10, 20), "head:rot": lambda u: [30, 6 * wave(u, 0, 3), 0], "body:rot": lambda u: tilt(4, 0, 0)})
scene("cine.player.campfire_sit", "Sit By The Campfire", 5.0, fns={"mw_root:pos": lambda u: move(0, -10, 0), "right_leg:rot": lambda u: RL(90, -20, 20), "left_leg:rot": lambda u: LL(90, -20, 20),
                                                                  "right_arm:rot": lambda u: R(60 + 5 * wave(u), -20, 20), "left_arm:rot": lambda u: Lh(60 + 5 * wave(u, 0.5), -20, 20), "head:rot": lambda u: [20 + 3 * wave(u, 0.2), 0, 0]})
scene("cine.player.stargaze", "Lie Back And Stargaze", 6.0, fns={"mw_root:pos": lambda u: move(0, -11, 0), "mw_root:rot": lambda u: tilt(-85, 0, 0), "right_arm:rot": lambda u: R(170, 30, -30), "left_arm:rot": lambda u: Lh(10, 30),
                                                                "right_leg:rot": lambda u: RL(40), "left_leg:rot": lambda u: LL(0, 8), "head:rot": lambda u: [0, 15 * wave(u, 0, 0.5), 0]})
scene("cine.player.point_destination", "Point To The Destination", 2.4, {"right_arm:rot": [(0, Z), (0.5, R(100, 10), "out_back"), (2.0, R(100, 10)), (2.4, Z)], "body:rot": [(0, Z), (0.5, tilt(-4, 15, 0)), (2.0, tilt(-4, 15, 0)), (2.4, Z)],
                                                                          "head:rot": [(0, Z), (0.3, [0, 25, 0]), (1.2, [0, -20, 0]), (2.0, [0, 25, 0]), (2.4, Z)]})
scene("cine.player.fist_resolve", "Clench A Fist In Resolve", 2.0, {"right_arm:rot": [(0, Z), (0.6, R(70, -20, 40)), (1.2, R(74, -20, 48)), (2.0, R(70, -20, 40))], "head:rot": [(0, Z), (0.6, [20, 0, 0]), (1.4, [-6, 0, 0]), (2.0, [-6, 0, 0])]})
scene("cine.player.brace_for_wave", "Brace For The Onslaught", 2.0, {"left_arm:rot": [(0, Z), (0.5, Lh(70, -10, -20)), (2.0, Lh(70, -10, -20))], "right_arm:rot": [(0, Z), (0.5, R(50, 10, -20)), (2.0, R(50, 10, -20))],
                                                                    "right_leg:rot": [(0, Z), (0.5, RL(-20, 10)), (2.0, RL(-20, 10))], "left_leg:rot": [(0, Z), (0.5, LL(25, 10)), (2.0, LL(25, 10))],
                                                                    "mw_root:pos": [(0, Z), (0.5, move(0, -1.5, 0)), (2.0, move(0, -1.5, 0))], "body:rot": [(0, Z), (0.5, tilt(12, 10, 0)), (2.0, tilt(12, 10, 0))]})
scene("cine.player.last_breath", "A Last Steadying Breath", 3.0, {"body:rot": [(0, Z), (1.2, tilt(-8)), (2.0, tilt(6)), (3.0, Z)], "head:rot": [(0, Z), (1.2, [-20, 0, 0]), (2.2, [10, 0, 0]), (3.0, Z)],
                                                                  "right_arm:rot": [(0, Z), (1.2, R(10, 20)), (3.0, Z)], "left_arm:rot": [(0, Z), (1.2, Lh(10, 20)), (3.0, Z)]}, events=[(1.2, "breath", {"strength": "1"})])
scene("cine.player.wave_farewell_far", "Wave Farewell Across A Distance", 3.0, {"right_arm:rot": [(0, Z), (0.5, R(175, 20)), (1.0, R(175, 50)), (1.5, R(175, 20)), (2.0, R(175, 50)), (3.0, Z)],
                                                                               "body:rot": [(0, Z), (0.5, tilt(-8, 0, -6)), (2.0, tilt(-8, 0, -6)), (3.0, Z)], "mw_root:pos": [(0, Z), (0.5, move(0, 1, 0)), (2.0, move(0, 1, 0)), (3.0, Z)]})
scene("cine.player.salute_fallen", "Salute The Fallen", 4.0, {"right_arm:rot": [(0, Z), (0.8, R(130, -20, 40)), (3.2, R(130, -20, 40)), (4.0, Z)], "head:rot": [(0, Z), (0.8, [20, 0, 0]), (3.2, [24, 0, 0]), (4.0, Z)]})
scene("cine.player.plant_flag", "Plant A Flag On The Summit", 2.4, {"right_arm:rot": [(0, Z), (0.6, R(175, 0)), (1.0, R(100, 0), "in_quart"), (2.4, R(170, 10))], "left_arm:rot": [(0, Z), (0.6, Lh(175, 0)), (1.0, Lh(100, 0), "in_quart"), (2.4, Lh(30, 20))],
                                                                     "body:rot": [(0, Z), (1.0, tilt(20)), (2.4, tilt(-10))], "head:rot": [(0, Z), (1.8, [-30, 0, 0]), (2.4, [-30, 0, 0])]}, events=[(1.0, "impact", {"material": "stone", "strength": "0.7"})])
scene("cine.player.look_back_once", "Look Back One Last Time", 2.6, {"head:rot": [(0, Z), (0.8, [0, 70, 0], "in_out_sine"), (1.8, [0, 70, 0]), (2.6, Z)], "body:rot": [(0, Z), (0.8, tilt(0, 25, 0)), (1.8, tilt(0, 25, 0)), (2.6, Z)]})
scene("cine.player.ready_stance", "Settle Into A Ready Stance", 1.6, {"right_arm:rot": [(0, Z), (0.6, R(40, 10, -20)), (1.6, R(42, 10, -20))], "left_arm:rot": [(0, Z), (0.6, Lh(30, 20)), (1.6, Lh(30, 20))],
                                                                      "right_leg:rot": [(0, Z), (0.6, RL(-12, 8)), (1.6, RL(-12, 8))], "left_leg:rot": [(0, Z), (0.6, LL(16, 8)), (1.6, LL(16, 8))], "body:rot": [(0, Z), (0.6, tilt(8, -12, 0)), (1.6, tilt(8, -12, 0))]})
scene("cine.player.wind_brace", "Lean Into A Howling Gale", 3.0, fns={"body:rot": lambda u: tilt(22, 0, 3 * wave(u, 0, 3)), "right_arm:rot": lambda u: R(140, -20, 40), "head:rot": lambda u: [20, 0, 0],
                                                                     "cloak:rot": lambda u: [50 + 15 * wave(u, 0, 4), 0, 0], "left_leg:rot": lambda u: LL(-20)})
scene("cine.player.examine_relic", "Examine A Relic", 4.0, fns={"right_arm:rot": lambda u: R(80, -10, 20), "left_arm:rot": lambda u: Lh(75, -20, 30 + 10 * wave(u, 0, 0.5)), "head:rot": lambda u: [30, 15 * wave(u, 0, 0.5), 8 * wave(u)]})
scene("cine.player.write_journal", "Write In A Journal", 4.0, fns={"mw_root:pos": lambda u: move(0, -10, 0), "right_leg:rot": lambda u: RL(90), "left_leg:rot": lambda u: LL(90), "left_arm:rot": lambda u: Lh(50, -10, 20),
                                                                  "right_arm:rot": lambda u: R(45 + 4 * wave(u, 0, 6), -14, 20), "head:rot": lambda u: [35, 0, 0]})
scene("cine.player.embrace", "Embrace An Old Friend", 3.0, {"right_arm:rot": [(0, Z), (0.8, R(90, -40, 20)), (2.4, R(90, -40, 20)), (3.0, Z)], "left_arm:rot": [(0, Z), (0.8, Lh(90, -40, 20)), (2.4, Lh(90, -40, 20)), (3.0, Z)],
                                                            "head:rot": [(0, Z), (0.8, [10, 0, 14]), (2.4, [10, 0, 14]), (3.0, Z)], "body:rot": [(0, Z), (0.8, tilt(8)), (2.4, tilt(8)), (3.0, Z)]})
scene("cine.player.warm_hands", "Warm Hands Over The Fire", 3.0, fns={"right_arm:rot": lambda u: R(70, -10 + 6 * wave(u), 20), "left_arm:rot": lambda u: Lh(70, -10 + 6 * wave(u, 0.5), 20), "body:rot": lambda u: tilt(14, 0, 0),
                                                                     "head:rot": lambda u: [20, 0, 0], "mw_root:pos": lambda u: move(0, -2, 0), "right_leg:rot": lambda u: RL(30), "left_leg:rot": lambda u: LL(30)})
scene("cine.player.climb_ledge_pull", "Haul Yourself Over A Ledge", 2.0, {"right_arm:rot": [(0, R(175)), (0.8, R(100)), (1.4, R(40)), (2.0, Z)], "left_arm:rot": [(0, Lh(175)), (0.8, Lh(100)), (1.4, Lh(40)), (2.0, Z)],
                                                                          "mw_root:pos": [(0, move(0, -14, 0)), (1.0, move(0, -6, 0), "out_quad"), (2.0, Z)], "right_leg:rot": [(0, Z), (1.2, RL(80)), (2.0, Z)], "body:rot": [(0, tilt(10)), (1.2, tilt(40)), (2.0, Z)]})
scene("cine.player.drop_to_knees_victory", "Drop To Your Knees In Victory", 3.0, with_kneel(3.0, {"right_arm:rot": [(0, Z), (0.8, R(170, 40)), (3.0, R(170, 40))], "left_arm:rot": [(0, Z), (0.8, Lh(170, 40)), (3.0, Lh(170, 40))],
                                                                                           "head:rot": [(0, Z), (0.8, [-40, 0, 0]), (3.0, [-40, 0, 0])]}))
scene("cine.player.vanish_into_fog", "Walk Away Into The Fog", 3.0, fns={"right_leg:rot": lambda u: RL(20 * cwave(u, 0, 2)), "left_leg:rot": lambda u: LL(-20 * cwave(u, 0, 2)), "right_arm:rot": lambda u: R(-10 * cwave(u, 0, 2), 4),
                                                                        "head:rot": lambda u: [10, 0, 0], "cloak:rot": lambda u: [14 + 4 * wave(u, 0, 4), 0, 0]})
scene("cine.player.startled_turn", "Turn At A Sound Behind", 1.4, {"head:rot": [(0, Z), (0.2, [-10, 60, 0], "out_expo"), (1.4, [-6, 60, 0])], "body:rot": [(0, Z), (0.25, tilt(0, 30, 0)), (1.4, tilt(0, 30, 0))],
                                                                   "right_arm:rot": [(0, Z), (0.3, R(40, 20)), (1.4, R(40, 20))]})
scene("cine.player.map_unfold", "Unfold A Map To Plan", 3.0, {"right_arm:rot": [(0, Z), (0.8, R(70, 20)), (3.0, R(70, 30))], "left_arm:rot": [(0, Z), (0.8, Lh(70, 20)), (3.0, Lh(70, 30))], "head:rot": [(0, Z), (0.8, [35, 0, 0]), (2.0, [35, 20, 0]), (3.0, [35, -10, 0])]})
# event-bound story moments
for frame, (name, tracks) in {
        "task": ("Advancement: A Quiet Nod Of Satisfaction", {"head:rot": [(0, Z), (0.3, [20, 0, 0]), (0.6, [-6, 0, 0]), (1.6, Z)], "right_arm:rot": [(0, Z), (0.4, R(80, 10, -30)), (1.2, R(80, 10, -30)), (1.6, Z)]}),
        "goal": ("Advancement: Goal Reached", {"right_arm:rot": [(0, Z), (0.3, R(160, 30)), (1.3, R(160, 30)), (1.8, Z)], "left_arm:rot": [(0, Z), (0.35, Lh(100, 40)), (1.3, Lh(100, 40)), (1.8, Z)],
                                               "head:rot": [(0, Z), (0.3, [-20, 0, 0]), (1.8, Z)]}),
        "challenge": ("Advancement: Challenge Conquered", {"right_arm:rot": [(0, Z), (0.3, R(175, 40)), (2.0, R(175, 40)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.3, Lh(175, 40)), (2.0, Lh(175, 40)), (2.4, Z)],
                                                           "mw_root:pos": [(0, Z), (0.2, move(0, -1, 0)), (0.5, move(0, 3, 0), "out_quad"), (0.8, Z)], "head:rot": [(0, Z), (0.5, [-35, 0, 0]), (2.4, Z)]})}.items():
    scene("cine.player.advancement_" + frame, name, max(t for seq in tracks.values() for t, *_ in seq), tracks, trig=event("victory:" + frame, "!q.is_dead"), pri=420,
          events=[(0.3, "particle", {"particle": "magic_glint", "count": "12" if frame != "challenge" else "30", "at": "head", "spread": "0.8"})])
for boss, (name, tracks) in {
        "ender_dragon": ("Dragonslayer's Exultation", {"right_arm:rot": [(0, Z), (0.6, R(178, 0)), (3.0, R(178, 0)), (3.6, Z)], "head:rot": [(0, Z), (0.6, [-45, 0, 0]), (3.0, [-45, 0, 0]), (3.6, Z)],
                                                      "left_arm:rot": [(0, Z), (0.6, Lh(60, 70)), (3.0, Lh(60, 70)), (3.6, Z)], "right_leg:rot": [(0, Z), (0.6, RL(-10, 14)), (3.0, RL(-10, 14)), (3.6, Z)],
                                                      "left_leg:rot": [(0, Z), (0.6, LL(10, 14)), (3.0, LL(10, 14)), (3.6, Z)], "body:rot": [(0, Z), (0.6, tilt(-12)), (3.6, Z)]}),
        "wither": ("Standing Over The Shattered Wither", {"body:rot": [(0, Z), (0.8, tilt(20)), (2.0, tilt(-8)), (3.0, Z)], "head:rot": [(0, Z), (0.8, [30, 0, 0]), (2.0, [-15, 0, 0]), (3.0, Z)],
                                                          "right_arm:rot": [(0, Z), (2.0, R(60, 20)), (3.0, Z)]}),
        "warden": ("Escaping The Warden's Wrath", {"body:rot": [(0, Z), (0.4, tilt(30)), (1.6, tilt(24)), (3.0, Z)], "right_arm:rot": [(0, Z), (0.4, R(30, -10, 30)), (1.6, R(30, -10, 30)), (3.0, Z)],
                                                   "head:rot": [(0, Z), (0.4, [-10, 0, 0]), (3.0, Z)]}, ),
        "elder_guardian": ("Freed From The Elder's Curse", {"right_arm:rot": [(0, Z), (0.6, R(90, 80)), (2.0, R(90, 80)), (3.0, Z)], "left_arm:rot": [(0, Z), (0.6, Lh(90, 80)), (2.0, Lh(90, 80)), (3.0, Z)],
                                                            "head:rot": [(0, Z), (0.6, [-30, 0, 0]), (3.0, Z)]})}.items():
    scene("cine.player.slew_" + boss, name, max(t for seq in tracks.values() for t, *_ in seq), tracks, trig=event("boss_slain:" + boss, "!q.is_dead"), pri=430, events=[(0.4, "shake", {"intensity": "0.3", "duration": "0.5"})])

# ============================================================================ bosses
scene("cine.wither.intro_rise", "Wither Intro: Rising From Its Summoning", 3.0, {"mw_root:pos": [(0, move(0, -8, 0)), (2.2, Z, "out_quad"), (3.0, Z)], "center_head:rot": [(0, [30, 0, 0]), (2.2, [-30, 0, 0]), (3.0, Z)],
                                                                                 "left_head:rot": [(0, [30, -30, 0]), (2.4, [-25, -30, 0]), (3.0, Z)], "right_head:rot": [(0, [30, 30, 0]), (2.6, [-25, 30, 0]), (3.0, Z)],
                                                                                 "ribcage:scl": [(0, [0.9, 0.9, 0.9]), (2.2, [1.1, 1.1, 1.1]), (3.0, [1, 1, 1])]},
      target="minecraft:wither", file=FM + "/bosses", trig=event("boss_intro"), events=[(2.2, "shake", {"intensity": "0.6", "duration": "0.8"})])
scene("cine.wither.charge_burst", "Wither Unleashing Its Charge", 1.6, {"ribcage:scl": [(0, [1.1, 1.1, 1.1]), (0.3, [1.3, 1.3, 1.3], "in_quad"), (0.4, [0.95, 0.95, 0.95], "out_expo"), (1.6, [1, 1, 1])],
                                                                       "shoulders:rot": [(0, Z), (0.3, [-15, 0, 0]), (0.4, [10, 0, 0]), (1.6, Z)]}, target="minecraft:wither", file=FM + "/bosses",
      events=[(0.4, "flash", {"strength": "0.7"}), (0.4, "shake", {"intensity": "0.8", "duration": "0.6"})])
scene("cine.ender_dragon.intro_roar", "Ender Dragon Intro: Sky Roar", 3.0, {"mw_root:rot": [(0, Z), (0.8, tilt(-20, 0, 0)), (2.0, tilt(-24, 0, 4)), (3.0, Z)], "mw_root:pos": [(0, Z), (0.8, move(0, 4, 0)), (3.0, Z)]},
      target="minecraft:ender_dragon", file=FM + "/bosses", trig=event("boss_intro"))
scene("cine.ender_dragon.flyover", "Ender Dragon Flyover Bank", 2.4, {"mw_root:rot": [(0, tilt(0, 0, -30)), (1.2, tilt(-6, 0, 0)), (2.4, tilt(0, 0, 30))], "mw_root:pos": [(0, move(0, 2, 0)), (1.2, move(0, -2, 0)), (2.4, move(0, 2, 0))]},
      target="minecraft:ender_dragon", file=FM + "/bosses")
scene("cine.warden.intro_emerge_roar", "Warden Intro: Emerge And Roar", 4.0, {"mw_root:pos": [(0, move(0, -20, 0)), (2.0, Z, "out_quad"), (4.0, Z)], "left_ribcage:rot": [(0, Z), (2.4, Z), (2.8, [0, -45, 0], "out_expo"), (3.6, [0, -45, 0]), (4.0, Z)],
                                                                              "right_ribcage:rot": [(0, Z), (2.4, Z), (2.8, [0, 45, 0], "out_expo"), (3.6, [0, 45, 0]), (4.0, Z)], "head:rot": [(0, [40, 0, 0]), (2.0, Z), (2.8, [-40, 0, 0]), (4.0, Z)],
                                                                              "right_arm:rot": [(0, R(170)), (1.5, R(90, 30)), (2.4, Z)], "left_arm:rot": [(0, Lh(170)), (1.6, Lh(90, 30)), (2.4, Z)]},
      target="minecraft:warden", file=FM + "/bosses", trig=event("boss_intro"), events=[(2.8, "shake", {"intensity": "0.9", "duration": "1.0"})])
scene("cine.warden.sniff_close", "Warden Sniffing Inches Away", 3.0, {"head:rot": [(0, Z), (0.6, [30, 0, 0]), (1.2, [26, 20, 0]), (1.8, [30, -20, 0]), (3.0, Z)], "body:rot": [(0, Z), (0.6, tilt(30)), (2.4, tilt(30)), (3.0, Z)],
                                                                      "left_tendril:rot": [(0, Z), (0.6, [-30, 0, 0]), (2.4, [-30, 0, 0]), (3.0, Z)], "right_tendril:rot": [(0, Z), (0.6, [-30, 0, 0]), (2.4, [-30, 0, 0]), (3.0, Z)]},
      target="minecraft:warden", file=FM + "/bosses")
scene("cine.elder_guardian.intro_glare", "Elder Guardian Intro: The Curse Glare", 3.0, {"eye:scl": [(0, [0.6, 0.6, 1]), (1.0, [1.5, 1.5, 1], "out_quad"), (3.0, [1.4, 1.4, 1])],
                                                                                        "mw_center:rot": [(0, Z), (1.0, tilt(-10, 0, 0)), (3.0, tilt(-8, 0, 0))], **{"spike%d:scl" % i: [(0, [1, 0.4, 1]), (1.2 + 0.05 * i, [1, 1.4, 1]), (3.0, [1, 1, 1])] for i in range(12)}},
      target="minecraft:elder_guardian", file=FM + "/bosses", trig=event("boss_intro"))
scene("cine.elder_guardian.circle_menace", "Elder Guardian Circling Menace", 4.0, fns={"tail0:rot": lambda u: [0, 10 * wave(u), 0], "tail1:rot": lambda u: [0, 16 * wave(u, 0.2), 0], "tail2:rot": lambda u: [0, 22 * wave(u, 0.4), 0],
                                                                                       "mw_center:rot": lambda u: tilt(0, 0, 10)}, target="minecraft:elder_guardian", file=FM + "/bosses")
for T, sp, name, tracks in (
        ("minecraft:ravager", "ravager", "Ravager Bursting Through The Gate", {"neck:rot": [(0, Z), (0.4, [30, 0, 0]), (0.6, [-30, 0, 0], "out_expo"), (2.0, Z)], "mouth:rot": [(0, Z), (0.6, [50, 0, 0]), (1.6, [40, 0, 0]), (2.0, Z)],
                                                                               "mw_center:rot": [(0, Z), (0.6, tilt(-10, 0, 0)), (2.0, Z)]}),
        ("minecraft:evoker", "evoker", "Evoker Ritual Summoning", {"right_arm:rot": [(0, Z), (1.0, R(170, 40)), (2.6, R(170, 50)), (3.0, Z)], "left_arm:rot": [(0, Z), (1.0, Lh(170, 40)), (2.6, Lh(170, 50)), (3.0, Z)],
                                                                   "head:rot": [(0, Z), (1.0, [-35, 0, 0]), (3.0, Z)], "mw_root:pos": [(0, Z), (1.4, move(0, 1.5, 0)), (2.6, move(0, 1.5, 0)), (3.0, Z)]}),
        ("minecraft:piglin_brute", "piglin_brute", "Piglin Brute Bastion Challenge", {"right_arm:rot": [(0, Z), (0.5, R(170, 10)), (1.6, R(170, 10)), (2.2, Z)], "head:rot": [(0, Z), (0.5, [-30, 0, 0]), (2.2, Z)],
                                                                                      "body:rot": [(0, Z), (0.5, tilt(-12)), (2.2, Z)]})):
    scene("cine.%s.entrance" % sp, name, max(t for seq in tracks.values() for t, *_ in seq), tracks, target=T, file=FM + "/bosses", trig=event("aggro", "!q.is_dead && q.player_distance < 16 && q.trait_confidence > 0.8"),
          pri=420)

# ============================================================================ storytelling actors
V = "minecraft:villager"
for cid, name, L, tracks in (
        ("announce", "Villager Announcing News", 3.0, {"arms:rot": [(0, Z), (0.5, [-150, 0, 0]), (2.4, [-150, 0, 0]), (3.0, Z)], "head:rot": [(0, Z), (0.5, [-25, 0, 0]), (1.5, [-25, 30, 0]), (2.4, [-25, -30, 0]), (3.0, Z)]}),
        ("point_the_way", "Villager Pointing The Way", 2.4, {"arms:rot": [(0, Z), (0.5, [-90, 35, 0]), (2.0, [-90, 35, 0]), (2.4, Z)], "head:rot": [(0, Z), (0.5, [0, 35, 0]), (2.0, [0, 35, 0]), (2.4, Z)], "body:rot": [(0, Z), (0.5, tilt(0, 20, 0)), (2.4, Z)]}),
        ("cheer_hero", "Villager Cheering The Hero", 1.0, {"arms:rot": [(0, Z), (0.2, [-160, 0, 0]), (0.5, [-140, 0, 0]), (1.0, [-160, 0, 0])], "mw_root:pos": [(0, Z), (0.25, move(0, 1.5, 0)), (0.5, Z), (0.75, move(0, 1.5, 0)), (1.0, Z)]}),
        ("bow_to_hero", "Villager Bowing To The Hero", 2.4, {"body:rot": [(0, Z), (0.5, tilt(-6)), (1.2, tilt(55), "in_quad"), (1.8, tilt(55)), (2.4, Z)], "head:rot": [(0, Z), (1.2, [25, 0, 0]), (2.4, Z)],
                                                             "arms:rot": [(0, Z), (0.5, [-40, 0, 0]), (1.2, [10, 0, 0]), (2.4, Z)], "right_leg:rot": [(0, Z), (1.2, leg('r', -15)), (2.4, Z)]}),
        ("cower_raid", "Villager Cowering As The Raid Begins", 2.0, {"arms:rot": [(0, Z), (0.3, [-130, 0, 0]), (2.0, [-130, 0, 0])], "body:rot": [(0, Z), (0.3, tilt(30)), (2.0, tilt(30))], "mw_root:pos": [(0, Z), (0.3, move(0, -2.5, 0)), (2.0, move(0, -2.5, 0))],
                                                                     "right_leg:rot": [(0, Z), (0.3, leg('r', 45)), (2.0, leg('r', 45))], "left_leg:rot": [(0, Z), (0.3, leg('l', 45)), (2.0, leg('l', 45))]}),
        ("pray_rain", "Villager Praying For Rain", 4.0, {"arms:rot": [(0, Z), (1.0, [-170, 0, 0]), (3.4, [-170, 0, 0]), (4.0, Z)], "head:rot": [(0, Z), (1.0, [-40, 0, 0]), (3.4, [-40, 0, 0]), (4.0, Z)],
                                                         "mw_root:pos": [(0, Z), (1.0, move(0, -3, 0)), (3.4, move(0, -3, 0)), (4.0, Z)], "right_leg:rot": [(0, Z), (1.0, leg('r', 90)), (3.4, leg('r', 90)), (4.0, Z)]}),
        ("weep", "Villager Weeping", 3.0, {"arms:rot": [(0, Z), (0.5, [-120, 0, 0]), (2.6, [-120, 0, 0]), (3.0, Z)], "head:rot": [(0, Z), (0.5, [30, 0, 0]), (1.0, [30, 0, 6]), (1.5, [30, 0, -6]), (2.0, [30, 0, 6]), (3.0, Z)],
                                           "body:rot": [(0, Z), (0.5, tilt(14)), (3.0, Z)]}),
        ("beckon_inside", "Villager Beckoning Indoors", 2.0, {"arms:rot": [(0, Z), (0.3, [-80, 0, 0]), (0.6, [-50, 0, 0]), (0.9, [-80, 0, 0]), (1.2, [-50, 0, 0]), (2.0, Z)], "body:rot": [(0, Z), (0.4, tilt(0, -20, 0)), (1.4, tilt(0, -20, 0)), (2.0, Z)]}),
        ("gift_offer", "Villager Offering A Gift", 2.4, {"arms:rot": [(0, Z), (0.6, [-80, 0, 0], "out_back"), (2.0, [-80, 0, 0]), (2.4, Z)], "body:rot": [(0, Z), (0.6, tilt(16)), (2.0, tilt(16)), (2.4, Z)], "head:rot": [(0, Z), (0.6, [-6, 0, 8]), (2.4, Z)]}),
        ("elder_storytell", "Village Elder Telling An Old Tale", 4.0, {"arms:rot": [(0, Z), (0.8, [-60, 20, 0]), (1.6, [-70, -20, 0]), (2.4, [-60, 20, 0]), (3.2, [-100, 0, 0]), (4.0, Z)],
                                                                       "head:rot": [(0, Z), (0.8, [-10, 20, 0]), (1.6, [-10, -20, 0]), (3.2, [-25, 0, 0]), (4.0, Z)], "body:rot": [(0, Z), (1.0, tilt(12)), (4.0, tilt(12))]})):
    scene("cine.villager." + cid, name, L, tracks, target=V, file=FM + "/village")
for T, sp, cid, name, L, tracks in (
        ("minecraft:wandering_trader", "wandering_trader", "reveal_wares", "Trader Revealing Rare Wares", 3.0, {"arms:rot": [(0, Z), (0.8, [-60, 0, 0]), (1.2, [-110, 0, 0], "out_back"), (2.6, [-110, 0, 0]), (3.0, Z)],
                                                                                                            "head:rot": [(0, Z), (1.2, [-15, 20, 0]), (2.6, [-15, -20, 0]), (3.0, Z)], "body:rot": [(0, Z), (0.8, tilt(14)), (1.2, tilt(-6)), (3.0, Z)]}),
        ("minecraft:wandering_trader", "wandering_trader", "farewell", "Trader Bidding Farewell", 2.6, {"arms:rot": [(0, Z), (0.5, [-150, 0, 15]), (0.9, [-150, 0, -15]), (1.3, [-150, 0, 15]), (2.6, Z)], "head:rot": [(0, Z), (0.6, [-10, 0, 10]), (2.6, Z)]}),
        ("minecraft:iron_golem", "iron_golem", "kneel_to_hero", "Iron Golem Kneeling Before The Hero", 3.0, {"right_leg:rot": [(0, Z), (1.0, leg('r', 90)), (2.4, leg('r', 90)), (3.0, Z)], "mw_root:pos": [(0, Z), (1.0, move(0, -6, 0)), (2.4, move(0, -6, 0)), (3.0, Z)],
                                                                                                            "head:rot": [(0, Z), (1.0, [30, 0, 0]), (2.4, [30, 0, 0]), (3.0, Z)], "right_arm:rot": [(0, Z), (1.0, arm('r', 40)), (2.4, arm('r', 40)), (3.0, Z)]}),
        ("minecraft:iron_golem", "iron_golem", "shield_villagers", "Iron Golem Shielding The Villagers", 2.4, {"right_arm:rot": [(0, Z), (0.6, arm('r', 30, 80)), (2.4, arm('r', 30, 80))], "left_arm:rot": [(0, Z), (0.6, arm('l', 30, 80)), (2.4, arm('l', 30, 80))],
                                                                                                              "body:rot": [(0, Z), (0.6, tilt(-6)), (2.4, tilt(-6))]}),
        ("minecraft:pillager", "pillager", "captain_command", "Raid Captain Ordering The Attack", 2.4, {"right_arm:rot": [(0, Z), (0.5, arm('r', 170)), (1.0, arm('r', 90), "in_quart"), (2.4, Z)], "head:rot": [(0, Z), (0.5, [-20, 0, 0]), (2.4, Z)],
                                                                                                       "body:rot": [(0, Z), (1.0, tilt(14)), (2.4, Z)]}),
        ("minecraft:vindicator", "vindicator", "war_cry", "Vindicator War Cry", 2.0, {"right_arm:rot": [(0, Z), (0.4, arm('r', 175, 10)), (1.6, arm('r', 175, 10)), (2.0, Z)], "head:rot": [(0, Z), (0.4, [-35, 0, 0]), (1.6, [-35, 0, 0]), (2.0, Z)],
                                                                                     "body:rot": [(0, Z), (0.4, tilt(-14)), (2.0, Z)]}),
        ("minecraft:piglin", "piglin", "barter_ceremony", "Piglin Barter Ceremony", 3.0, {"left_arm:rot": [(0, Z), (0.6, arm('l', 120, 0, -30)), (1.8, arm('l', 120, 0, -30)), (2.4, arm('l', 40)), (3.0, Z)],
                                                                                         "head:rot": [(0, Z), (0.6, [-25, 0, 0]), (1.8, [-25, 0, 0]), (2.4, [20, 0, 0]), (3.0, Z)], "body:rot": [(0, Z), (0.6, tilt(-8)), (3.0, Z)]}),
        ("minecraft:piglin_brute", "piglin_brute", "guard_salute", "Piglin Brute Guard Salute", 2.0, {"right_arm:rot": [(0, Z), (0.4, arm('r', 120, -20, 40)), (1.6, arm('r', 120, -20, 40)), (2.0, Z)], "body:rot": [(0, Z), (0.4, tilt(-6)), (2.0, Z)]}),
        ("minecraft:zombie", "zombie", "lurch_reveal", "Zombie Lurching Out Of The Dark", 2.4, {"body:rot": [(0, tilt(30, 0, 10)), (1.2, tilt(10, 0, -6)), (2.4, tilt(12, 0, 4))], "head:rot": [(0, [40, 0, 20]), (1.2, [-10, 0, 0]), (2.4, [10, 0, 8])],
                                                                                              "right_arm:rot": [(0, arm('r', 20)), (1.2, arm('r', 100, 10)), (2.4, arm('r', 90))], "left_arm:rot": [(0, arm('l', 10)), (1.4, arm('l', 95, 10)), (2.4, arm('l', 85))]}),
        ("minecraft:zombie", "zombie", "window_pound", "Zombie Pounding On The Glass", 2.0, {"right_arm:rot": [(0, arm('r', 100)), (0.4, arm('r', 130)), (0.6, arm('r', 95), "in_quart"), (1.2, arm('r', 130)), (1.4, arm('r', 95), "in_quart"), (2.0, arm('r', 100))],
                                                                                              "left_arm:rot": [(0, arm('l', 100)), (0.8, arm('l', 130)), (1.0, arm('l', 95), "in_quart"), (1.6, arm('l', 130)), (1.8, arm('l', 95), "in_quart"), (2.0, arm('l', 100))],
                                                                                              "head:rot": [(0, [10, 0, 10]), (1.0, [10, 0, -10]), (2.0, [10, 0, 10])], "body:rot": [(0, tilt(10)), (2.0, tilt(10))]}),
        ("minecraft:skeleton", "skeleton", "volley_aim", "Skeleton Archers Raising Bows", 2.0, {"left_arm:rot": [(0, Z), (0.8, arm('l', 90, 0, 20)), (2.0, arm('l', 90, 0, 20))], "right_arm:rot": [(0, Z), (0.8, arm('r', 90, -20, -40)), (2.0, arm('r', 90, -20, -40))],
                                                                                              "head:rot": [(0, Z), (0.8, [-20, 10, 0]), (2.0, [-20, 10, 0])]}),
        ("minecraft:skeleton", "skeleton", "bone_salute", "Skeleton Honour Guard Salute", 2.0, {"right_arm:rot": [(0, Z), (0.4, arm('r', 130, -20, 40)), (1.6, arm('r', 130, -20, 40)), (2.0, Z)], "head:rot": [(0, Z), (0.4, [-6, 0, 0]), (2.0, Z)]}),
        ("minecraft:creeper", "creeper", "sneak_up_reveal", "Creeper Sneaking Up Behind", 2.4, {"head:rot": [(0, [0, 60, 0]), (1.6, [10, 0, 0]), (2.4, [10, 0, 0])], "mw_center:pos": [(0, move(0, -2, 0)), (1.6, Z)],
                                                                                               "body:scl": [(0, [1, 1, 1]), (2.0, [1, 1, 1]), (2.4, [1.08, 1.08, 1.08])]}),
        ("minecraft:enderman", "enderman", "stare_down", "Enderman Stare-Down", 3.0, {"head:rot": [(0, Z), (0.4, [-10, 0, 0]), (3.0, [-10, 0, 0])], "body:rot": [(0, Z), (1.0, tilt(-6)), (3.0, tilt(-6))],
                                                                                     "right_arm:rot": [(0, Z), (1.5, arm('r', 0, 20)), (3.0, arm('r', 0, 30))], "left_arm:rot": [(0, Z), (1.5, arm('l', 0, 20)), (3.0, arm('l', 0, 30))]}),
        ("minecraft:spider", "spider", "drop_from_ceiling", "Spider Dropping From The Ceiling", 1.6, {"mw_root:pos": [(0, move(0, 16, 0)), (0.6, move(0, -1, 0), "in_quad"), (1.0, Z)],
                                                                                                     "mw_root:rot": [(0, tilt(180, 0, 0)), (0.7, Z)]}),
        ("minecraft:wolf", "wolf", "pack_howl", "Pack Leader Howl", 3.0, {"head:rot": [(0, Z), (0.6, [-75, 0, 0]), (2.4, [-78, 0, 4]), (3.0, Z)], "mw_center:rot": [(0, Z), (0.6, tilt(-14, 0, 0)), (2.4, tilt(-14, 0, 0)), (3.0, Z)],
                                                                          "left_front_leg:rot": [(0, Z), (0.6, [-20, 0, 0]), (2.4, [-20, 0, 0]), (3.0, Z)]}),
        ("minecraft:wolf", "wolf", "loyal_guard", "Wolf Standing Guard Over Its Owner", 3.0, {"head:rot": [(0, Z), (0.6, [-4, 40, 0]), (1.6, [-4, -40, 0]), (3.0, Z)], "tail:rot": [(0, Z), (0.6, [-10, 0, 0]), (3.0, [-10, 0, 0])]}),
        ("minecraft:cat", "cat", "window_watch", "Cat Watching From The Window", 4.0, {"head:rot": [(0, Z), (1.0, [-10, 30, 0]), (3.0, [-10, -20, 0]), (4.0, Z)], "tail2:rot": [(0, Z), (1.5, [0, 30, 0]), (2.0, Z), (3.5, [0, 30, 0]), (4.0, Z)]}),
        ("minecraft:horse", "horse", "rear_silhouette", "Horse Rearing Against The Sky", 2.4, {"mw_center:rot": [(0, Z), (0.8, tilt(-40, 0, 0), "out_quad"), (1.6, tilt(-42, 0, 0)), (2.4, Z)],
                                                                                              "left_front_leg:rot": [(0, Z), (0.8, [-80, 0, 0]), (1.2, [-40, 0, 0]), (1.6, [-80, 0, 0]), (2.4, Z)],
                                                                                              "right_front_leg:rot": [(0, Z), (0.9, [-40, 0, 0]), (1.3, [-80, 0, 0]), (1.7, [-40, 0, 0]), (2.4, Z)], "head_parts:rot": [(0, Z), (0.8, [-30, 0, 0]), (2.4, Z)]}),
        ("minecraft:horse", "horse", "nuzzle_owner", "Horse Nuzzling Its Owner", 3.0, {"head_parts:rot": [(0, Z), (0.8, [30, 20, 10]), (1.6, [34, 10, 0]), (2.4, [30, 20, 10]), (3.0, Z)]}),
        ("minecraft:allay", "allay", "deliver_gift", "Allay Delivering A Gift", 2.4, {"right_arm:rot": [(0, Z), (0.8, [-80, 0, -14]), (1.6, [-100, 0, -30]), (2.4, Z)], "left_arm:rot": [(0, Z), (0.8, [-80, 0, 14]), (1.6, [-100, 0, 30]), (2.4, Z)],
                                                                                     "root:rot": [(0, Z), (1.8, Z), (2.4, [0, 360, 0])]}),
        ("minecraft:dolphin", "dolphin", "leap_arc", "Dolphin Leaping Alongside", 1.6, {"mw_center:rot": [(0, tilt(-30, 0, 0)), (0.8, Z), (1.6, tilt(40, 0, 0))], "tail:rot": [(0, [20, 0, 0]), (1.6, [-10, 0, 0])]}),
        ("minecraft:parrot", "parrot", "perch_land", "Parrot Landing On A Perch", 1.2, {"right_wing:rot": [(0, [0, 0, 80]), (0.6, [0, 0, 40]), (1.2, Z)], "left_wing:rot": [(0, [0, 0, -80]), (0.6, [0, 0, -40]), (1.2, Z)],
                                                                                       "tail:rot": [(0, [30, 0, 0]), (1.2, Z)], "head:rot": [(0, Z), (0.8, [10, 0, 20]), (1.2, Z)]}),
        ("minecraft:fox", "fox", "steal_item", "Fox Snatching An Item", 1.6, {"head:rot": [(0, Z), (0.4, [40, 0, 0]), (0.6, [-10, 0, 0], "out_back"), (1.6, Z)], "mw_center:rot": [(0, Z), (0.4, tilt(14, 0, 0)), (1.6, Z)],
                                                                             "tail:rot": [(0, Z), (0.6, [-30, 30, 0]), (1.6, Z)]}),
        ("minecraft:sniffer", "sniffer", "discover_seed", "Sniffer Unearthing An Ancient Seed", 3.0, {"head:rot": [(0, Z), (1.0, [55, 0, 0]), (2.0, [-25, 0, 0], "out_back"), (3.0, Z)],
                                                                                                     "lower_beak:rot": [(0, Z), (2.0, [25, 0, 0]), (3.0, Z)], "mw_center:pos": [(0, Z), (2.0, move(0, 1.5, 0)), (3.0, Z)]}),
        ("minecraft:camel", "camel", "kneel_welcome", "Camel Kneeling To Welcome A Rider", 3.0, {"head:rot": [(0, Z), (1.0, [20, 0, 0]), (2.2, [-14, 0, 0]), (3.0, Z)], "tail:rot": [(0, Z), (1.5, [0, 30, 0]), (3.0, Z)]}),
        ("minecraft:llama", "llama", "caravan_halt", "Lead Llama Halting The Caravan", 2.0, {"head:rot": [(0, Z), (0.4, [-30, 0, 0]), (1.4, [-25, 30, 0]), (2.0, Z)], "mw_center:rot": [(0, Z), (0.4, tilt(-8, 0, 0)), (2.0, Z)]}),
        ("minecraft:bee", "bee", "royal_dance", "Bee Performing For The Hive", 2.4, {"bone:rot": [(0, Z), (0.6, tilt(0, 0, 30)), (1.2, tilt(0, 0, -30)), (1.8, tilt(0, 0, 30)), (2.4, Z)], "bone:pos": [(0, Z), (1.2, move(0, 2, 0)), (2.4, Z)]}),
        ("minecraft:axolotl", "axolotl", "faint_reveal", "Axolotl Playing Dead, Then Peeking", 3.0, {"mw_center:rot": [(0, Z), (0.6, tilt(0, 0, 170)), (2.2, tilt(0, 0, 170)), (3.0, Z)], "head:rot": [(0, Z), (2.2, Z), (2.6, [0, 30, 0]), (3.0, Z)]}),
        ("minecraft:goat", "goat", "summit_scream", "Goat Screaming From The Summit", 2.0, {"head:rot": [(0, Z), (0.4, [-45, 0, 0], "out_expo"), (1.4, [-45, 0, 6]), (2.0, Z)], "mw_center:rot": [(0, Z), (0.4, tilt(-10, 0, 0)), (2.0, Z)]}),
        ("minecraft:husk", "husk", "mirage_shamble", "Husk Shambling Out Of A Mirage", 3.0, {"body:rot": [(0, tilt(20, 0, 10)), (1.5, tilt(14, 0, -8)), (3.0, tilt(18, 0, 6))], "head:rot": [(0, [30, 0, 0]), (3.0, [20, 0, 10])],
                                                                                            "right_arm:rot": [(0, arm('r', 30)), (3.0, arm('r', 80, 10))], "left_arm:rot": [(0, arm('l', 40)), (3.0, arm('l', 90))]}),
        ("minecraft:ocelot", "ocelot", "jungle_stalk_reveal", "Ocelot Emerging From The Undergrowth", 2.4, {"mw_center:pos": [(0, move(0, -2, -2)), (1.6, Z)], "head:rot": [(0, [10, 0, 0]), (1.6, [-10, 30, 0]), (2.4, Z)],
                                                                                                           "tail1:rot": [(0, [-20, 0, 0]), (2.4, Z)]}),
        ("minecraft:polar_bear", "polar_bear", "protect_cub", "Polar Bear Rearing To Protect Its Cub", 2.6, {"mw_center:rot": [(0, Z), (0.8, tilt(-50, 0, 0), "out_quad"), (2.0, tilt(-50, 0, 0)), (2.6, Z)],
                                                                                                           "head:rot": [(0, Z), (0.8, [-30, 0, 0]), (2.0, [-30, 0, 0]), (2.6, Z)], "left_front_leg:rot": [(0, Z), (0.8, [-70, 0, -20]), (2.0, [-70, 0, -20]), (2.6, Z)],
                                                                                                           "right_front_leg:rot": [(0, Z), (0.8, [-70, 0, 20]), (2.0, [-70, 0, 20]), (2.6, Z)]}),
        ("minecraft:panda", "panda", "bamboo_feast", "Panda Feasting On Bamboo", 3.0, {"right_front_leg:rot": [(0, Z), (0.6, [-120, 0, 14]), (3.0, [-120, 0, 14])], "left_front_leg:rot": [(0, Z), (0.6, [-115, 0, -14]), (3.0, [-115, 0, -14])],
                                                                                      "head:rot": [(0, Z), (1.0, [-12, 0, 0]), (1.4, [-6, 0, 0]), (1.8, [-12, 0, 0]), (2.2, [-6, 0, 0]), (3.0, Z)]}),
        ("minecraft:shulker", "shulker", "slow_open", "Shulker Slowly Opening", 3.0, {"lid:pos": [(0, Z), (2.4, move(0, 4, 0), "in_out_sine"), (3.0, move(0, 3, 0))], "head:rot": [(0, Z), (2.4, [0, 40, 0]), (3.0, [0, 0, 0])]}),
        ("minecraft:phantom", "phantom", "moon_silhouette", "Phantom Crossing The Moon", 3.0, {"left_wing_base:rot": [(0, [0, 0, 20]), (1.5, [0, 0, -20]), (3.0, [0, 0, 20])], "right_wing_base:rot": [(0, [0, 0, -20]), (1.5, [0, 0, 20]), (3.0, [0, 0, -20])],
                                                                                              "mw_root:rot": [(0, tilt(0, 0, 10)), (3.0, tilt(0, 0, -10))]}),
        ("minecraft:blaze", "blaze", "fortress_ignite", "Blaze Igniting In The Fortress Hall", 2.0, {**{"part%d:pos" % i: [(0, Z), (1.0, move(0, 3, 0)), (2.0, move(0, 1, 0))] for i in range(12)},
                                                                                                    "head:rot": [(0, Z), (1.0, [-20, 0, 0]), (2.0, Z)]}),
        ("minecraft:ghast", "ghast", "rise_from_lava_sea", "Ghast Rising From The Lava Sea", 4.0, {"mw_root:pos": [(0, move(0, -16, 0)), (4.0, Z, "out_quad")], **{"tentacle%d:rot" % i: [(0, [40, 0, 0]), (4.0, [10, 0, 0])] for i in range(9)}}),
        ("minecraft:strider", "strider", "lava_cross", "Strider Ferrying Across The Lava", 3.0, {"body:rot": [(0, Z), (1.5, [0, 10, 4]), (3.0, Z)], "right_leg:rot": [(0, Z), (1.0, [-20, 0, 0]), (2.0, [20, 0, 0]), (3.0, Z)],
                                                                                                "left_leg:rot": [(0, Z), (1.0, [20, 0, 0]), (2.0, [-20, 0, 0]), (3.0, Z)]}),
        ("minecraft:frog", "frog", "lily_croak", "Frog Croaking On A Lily Pad", 2.0, {"croaking_body:scl": [(0, [1, 1, 1]), (0.4, [1.8, 1.8, 1.4]), (0.6, [1, 1, 1]), (1.2, [1.8, 1.8, 1.4]), (1.4, [1, 1, 1]), (2.0, [1, 1, 1])],
                                                                                     "head:rot": [(0, Z), (0.4, [-8, 0, 0]), (0.6, Z), (1.2, [-8, 0, 0]), (1.4, Z)]}),
        ("minecraft:turtle", "turtle", "hatchling_journey", "Hatchling Racing For The Sea", 2.0, {"left_front_leg:rot": [(0, Z), (0.25, [0, 40, 0]), (0.5, [0, -40, 0]), (0.75, [0, 40, 0]), (1.0, [0, -40, 0]), (2.0, Z)],
                                                                                                 "right_front_leg:rot": [(0, Z), (0.25, [0, -40, 0]), (0.5, [0, 40, 0]), (0.75, [0, -40, 0]), (1.0, [0, 40, 0]), (2.0, Z)],
                                                                                                 "head:rot": [(0, Z), (0.5, [-20, 0, 0]), (2.0, Z)]}),
        ("minecraft:sheep", "sheep", "shepherds_flock", "Sheep Following The Shepherd", 2.0, {"head:rot": [(0, Z), (0.5, [-10, 20, 0]), (1.5, [-10, -10, 0]), (2.0, Z)], "mw_center:rot": [(0, Z), (1.0, tilt(0, 0, 3)), (2.0, Z)]}),
        ("minecraft:chicken", "chicken", "dawn_crow", "Chicken Greeting The Dawn", 2.0, {"head:rot": [(0, Z), (0.4, [-40, 0, 0]), (1.4, [-40, 0, 0]), (2.0, Z)], "right_wing:rot": [(0, Z), (0.4, [0, 0, 70]), (1.4, [0, 0, 70]), (2.0, Z)],
                                                                                        "left_wing:rot": [(0, Z), (0.4, [0, 0, -70]), (1.4, [0, 0, -70]), (2.0, Z)]}),
        ("minecraft:cow", "cow", "pasture_low", "Cow Lowing Across The Pasture", 2.4, {"head:rot": [(0, Z), (0.6, [-25, 15, 0]), (1.8, [-25, 15, 0]), (2.4, Z)], "mw_center:pos": [(0, Z), (0.6, move(0, 0, 0.6)), (2.4, Z)]}),
        ("minecraft:bat", "bat", "cave_swarm", "Bats Bursting From A Cave", 1.2, {"right_wing:rot": [(0, [0, 80, 0]), (0.15, [0, -60, 0]), (0.3, [0, 60, 0]), (0.45, [0, -60, 0]), (0.6, [0, 60, 0]), (1.2, Z)],
                                                                                 "left_wing:rot": [(0, [0, -80, 0]), (0.15, [0, 60, 0]), (0.3, [0, -60, 0]), (0.45, [0, 60, 0]), (0.6, [0, -60, 0]), (1.2, Z)], "mw_root:rot": [(0, tilt(180, 0, 0)), (0.3, Z)]}),
        ("minecraft:vex", "vex", "spectral_swarm", "Vex Swarming Out Of A Spell", 1.6, {"root:rot": [(0, Z), (0.8, [0, 0, 40]), (1.6, [0, 0, -40])], "right_arm:rot": [(0, Z), (0.4, [-170, 0, 10]), (1.6, [-170, 0, 10])],
                                                                                       "root:scl": [(0, [0.2, 0.2, 0.2]), (0.4, [1, 1, 1], "out_back"), (1.6, [1, 1, 1])]}),
        ("minecraft:witch", "witch", "hut_cackle", "Witch Cackling In Her Doorway", 2.4, {"head:rot": [(0, Z), (0.4, [-30, 0, 0]), (0.6, [-20, 0, 0]), (0.8, [-30, 0, 0]), (1.0, [-20, 0, 0]), (2.4, Z)],
                                                                                         "arms:rot": [(0, Z), (0.4, [-90, 0, 0]), (2.0, [-90, 0, 0]), (2.4, Z)], "hat4:rot": [(0, Z), (0.8, [20, 0, 0]), (2.4, Z)]}),
        ("minecraft:drowned", "drowned", "trident_rise", "Drowned Rising With A Trident", 3.0, {"mw_root:pos": [(0, move(0, -12, 0)), (2.0, Z, "out_quad"), (3.0, Z)], "right_arm:rot": [(0, arm('r', 170)), (2.0, arm('r', 175)), (3.0, arm('r', 170))],
                                                                                               "head:rot": [(0, [-30, 0, 0]), (2.0, [10, 0, 0]), (3.0, Z)]}),
        ("minecraft:zombie_villager", "zombie_villager", "lost_memory", "Zombie Villager Recalling Its Old Life", 3.0, {"head:rot": [(0, [20, 0, 0]), (1.2, [-10, 30, 0]), (2.2, [10, -10, 0]), (3.0, [20, 0, 0])],
                                                                                                                      "right_arm:rot": [(0, arm('r', 80)), (1.2, arm('r', 40, -10, 30)), (2.2, arm('r', 40, -10, 30)), (3.0, arm('r', 80))]}),
        ("minecraft:snow_golem", "snow_golem", "first_snow", "Snow Golem Catching The First Snowflakes", 3.0, {"head:rot": [(0, Z), (0.8, [-30, 0, 0]), (2.4, [-30, 20, 0]), (3.0, Z)],
                                                                                                             "right_arm:rot": [(0, Z), (0.8, [0, 0, 50]), (2.4, [0, 0, 60]), (3.0, Z)], "left_arm:rot": [(0, Z), (0.8, [0, 0, -50]), (2.4, [0, 0, -60]), (3.0, Z)]}),
        ("minecraft:mooshroom", "mooshroom", "spore_bloom", "Mooshroom Blooming In The Mist", 2.4, {"mw_center:rot": [(0, Z), (0.6, tilt(0, 0, 6)), (1.2, tilt(0, 0, -6)), (1.8, tilt(0, 0, 4)), (2.4, Z)],
                                                                                                    "head:rot": [(0, Z), (1.2, [-20, 0, 0]), (2.4, Z)]})):
    scene("cine.%s.%s" % (sp, cid), name, L, tracks, target=T, file=FM + "/" + sp)


# ============================================================================ sequences (performed by the CinematicDirector)
def seq(sid, name, anchor, shots, events, letterbox=True, cancel_on_damage=True):
    """name is kept as a readable title for /mw cinematic list; the second argument documents the source key."""
    SEQUENCES[sid] = {"name": sid.replace("_", " ").title(), "anchor": anchor, "letterbox": letterbox, "skippable": True, "hide_hud": True, "cancel_on_damage": cancel_on_damage,
                      "shots": shots, "events": events}


def anim(t, actor, clip):
    return {"time": t, "type": "animate", "actor": actor, "clip": clip}


seq("boss_intro_wither", "boss.wither.title", "@anchor",
    [{"type": "low_angle", "duration": 3.0, "target": "@anchor"}, {"type": "orbit", "duration": 3.5, "radius": 9, "height": 3, "from_angle": -40, "to_angle": 40, "transition": {"type": "blend", "duration": 0.8}}],
    [{"time": 0, "type": "fade", "from": 1, "to": 0, "duration": 0.8}, anim(0.2, "@anchor", "cine.wither.intro_rise"), anim(3.4, "@anchor", "cine.wither.charge_burst"),
     {"time": 3.8, "type": "title", "title": "motionworks.boss.wither.title", "subtitle": "motionworks.boss.wither.subtitle", "duration": 2.6},
     {"time": 3.8, "type": "sound", "sound": "motionworks:cinematic.boom"}])
seq("boss_intro_ender_dragon", "boss.ender_dragon.title", "@anchor",
    [{"type": "establishing", "duration": 4.0, "target": "@anchor"}, {"type": "track", "duration": 3.0, "offset": [0, 6, 18], "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0.5, "@anchor", "cine.ender_dragon.intro_roar"), anim(4.0, "@anchor", "cine.ender_dragon.flyover"), anim(1.0, "@self", "cine.player.look_up_awe"),
     {"time": 1.2, "type": "sound", "sound": "motionworks:cinematic.riser"},
     {"time": 4.2, "type": "title", "title": "motionworks.boss.ender_dragon.title", "subtitle": "motionworks.boss.ender_dragon.subtitle", "duration": 2.6}])
seq("boss_intro_warden", "boss.warden.title", "@anchor",
    [{"type": "low_angle", "duration": 4.2, "target": "@anchor"}, {"type": "close_up", "duration": 2.5, "target": "@anchor", "transition": {"type": "blend", "duration": 0.6}}],
    [anim(0.0, "@anchor", "cine.warden.intro_emerge_roar"), anim(4.2, "@anchor", "cine.warden.sniff_close"), anim(0.4, "@self", "cine.player.startled_turn"),
     {"time": 2.8, "type": "shake", "amount": 0.6}, {"time": 4.4, "type": "title", "title": "motionworks.boss.warden.title", "subtitle": "motionworks.boss.warden.subtitle", "duration": 2.4}])
seq("boss_intro_elder_guardian", "boss.elder_guardian.title", "@anchor",
    [{"type": "push_in", "duration": 3.2, "target": "@anchor"}, {"type": "orbit", "duration": 3.0, "radius": 8, "height": 1, "transition": {"type": "blend", "duration": 0.8}}],
    [anim(0.2, "@anchor", "cine.elder_guardian.intro_glare"), anim(3.2, "@anchor", "cine.elder_guardian.circle_menace"), {"time": 1.2, "type": "flash", "strength": 0.4},
     {"time": 3.4, "type": "title", "title": "motionworks.boss.elder_guardian.title", "subtitle": "motionworks.boss.elder_guardian.subtitle", "duration": 2.4}])
seq("hero_campfire", "cinematic.hero_campfire", "@self",
    [{"type": "orbit", "duration": 6.0, "radius": 4, "height": 1.2, "from_angle": -30, "to_angle": 30}, {"type": "close_up", "duration": 3.0, "transition": {"type": "blend", "duration": 1.0}},
     {"type": "crane", "duration": 5.0, "from_height": 1, "to_height": 9, "transition": {"type": "blend", "duration": 1.2}}],
    [anim(0, "@self", "cine.player.campfire_sit"), anim(4.0, "@self", "cine.player.warm_hands"), anim(7.0, "@self", "cine.player.write_journal"), anim(9.5, "@self", "cine.player.stargaze"),
     {"time": 10, "type": "particles", "actor": "@self", "particle": "ember", "count": 20, "spread": 1.5}])
seq("village_welcome", "cinematic.village_welcome", "@nearest:minecraft:villager",
    [{"type": "establishing", "duration": 4.0}, {"type": "over_shoulder", "duration": 4.0, "target": "@anchor", "transition": {"type": "blend", "duration": 0.8}},
     {"type": "wide", "duration": 4.0, "transition": {"type": "blend", "duration": 0.8}}],
    [anim(0.5, "@anchor", "cine.villager.announce"), anim(3.6, "@anchor", "cine.villager.gift_offer"), anim(4.0, "@self", "cine.player.wave_farewell_far"),
     anim(6.2, "@anchor", "cine.villager.point_the_way"), anim(6.4, "@self", "cine.player.point_destination"), anim(8.6, "@anchor", "cine.villager.beckon_inside"),
     anim(1.0, "@nearest:minecraft:iron_golem", "cine.iron_golem.shield_villagers"), anim(2.0, "@nearest:minecraft:cat", "cine.cat.window_watch"),
     anim(5.0, "@nearest:minecraft:chicken", "cine.chicken.dawn_crow"), anim(9.0, "@nearest:minecraft:villager", "cine.villager.elder_storytell")])
seq("raid_aftermath", "cinematic.raid_aftermath", "@self",
    [{"type": "low_angle", "duration": 4.0}, {"type": "orbit", "duration": 5.0, "radius": 6, "height": 2, "transition": {"type": "blend", "duration": 1.0}}, {"type": "crane", "duration": 4.0}],
    [anim(0, "@self", "cine.player.plant_sword"), anim(2.2, "@self", "cine.player.lean_on_sword"), anim(1.0, "@nearest:minecraft:villager", "cine.villager.cheer_hero"),
     anim(3.0, "@nearest:minecraft:villager", "cine.villager.bow_to_hero"), anim(4.0, "@nearest:minecraft:iron_golem", "cine.iron_golem.kneel_to_hero"),
     anim(6.0, "@nearest:minecraft:villager", "cine.villager.weep"), anim(8.0, "@self", "cine.player.salute_fallen"), anim(0.5, "@nearest:minecraft:ravager", "cine.ravager.entrance")])
seq("raid_begins", "cinematic.raid_begins", "@nearest:minecraft:pillager",
    [{"type": "establishing", "duration": 3.5}, {"type": "low_angle", "duration": 3.0, "target": "@anchor", "transition": {"type": "blend", "duration": 0.6}}],
    [anim(0.4, "@anchor", "cine.pillager.captain_command"), anim(1.0, "@nearest:minecraft:vindicator", "cine.vindicator.war_cry"), anim(1.2, "@nearest:minecraft:villager", "cine.villager.cower_raid"),
     anim(2.0, "@nearest:minecraft:evoker", "cine.evoker.entrance"), anim(2.6, "@nearest:minecraft:vex", "cine.vex.spectral_swarm"), anim(3.5, "@self", "cine.player.brace_for_wave"),
     anim(3.0, "@nearest:minecraft:witch", "cine.witch.hut_cackle")])
seq("trader_arrival", "cinematic.trader_arrival", "@nearest:minecraft:wandering_trader",
    [{"type": "track", "duration": 4.0, "offset": [3, 1.5, 5]}, {"type": "close_up", "duration": 3.0, "transition": {"type": "blend", "duration": 0.6}}],
    [anim(0.2, "@nearest:minecraft:llama", "cine.llama.caravan_halt"), anim(1.6, "@anchor", "cine.wandering_trader.reveal_wares"), anim(5.0, "@anchor", "cine.wandering_trader.farewell"),
     anim(1.0, "@nearest:minecraft:camel", "cine.camel.kneel_welcome")])
seq("deep_dark_descent", "cinematic.deep_dark_descent", "@self",
    [{"type": "over_shoulder", "duration": 5.0}, {"type": "low_angle", "duration": 4.0, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@self", "cine.player.lantern_into_dark"), anim(3.5, "@self", "cine.player.startled_turn"), anim(5.0, "@self", "cine.player.last_breath"),
     anim(2.0, "@nearest:minecraft:bat", "cine.bat.cave_swarm"), anim(4.0, "@nearest:minecraft:spider", "cine.spider.drop_from_ceiling"),
     anim(6.0, "@nearest:minecraft:enderman", "cine.enderman.stare_down"), anim(6.0, "@nearest:minecraft:creeper", "cine.creeper.sneak_up_reveal")])
seq("portal_departure", "cinematic.portal_departure", "@self",
    [{"type": "push_in", "duration": 4.0}, {"type": "pov", "duration": 2.5, "transition": {"type": "blend", "duration": 0.6}}, {"type": "pull_out", "duration": 3.0}],
    [anim(0, "@self", "cine.player.map_unfold"), anim(3.0, "@self", "cine.player.fist_resolve"), anim(5.0, "@self", "cine.player.look_back_once"), anim(7.4, "@self", "cine.player.portal_step"),
     {"time": 8.8, "type": "flash", "strength": 0.8}])
seq("nether_expedition", "cinematic.nether_expedition", "@self",
    [{"type": "establishing", "duration": 4.0}, {"type": "track", "duration": 4.0, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@self", "cine.player.shield_eyes_flash"), anim(2.0, "@self", "cine.player.determined_march"), anim(1.0, "@nearest:minecraft:piglin", "cine.piglin.barter_ceremony"),
     anim(2.0, "@nearest:minecraft:piglin_brute", "cine.piglin_brute.guard_salute"), anim(3.0, "@nearest:minecraft:ghast", "cine.ghast.rise_from_lava_sea"),
     anim(4.0, "@nearest:minecraft:blaze", "cine.blaze.fortress_ignite"), anim(5.0, "@nearest:minecraft:strider", "cine.strider.lava_cross"),
     anim(6.0, "@nearest:minecraft:piglin_brute", "cine.piglin_brute.entrance")])
seq("graveyard_night", "cinematic.graveyard_night", "@self",
    [{"type": "high_angle", "duration": 4.0}, {"type": "low_angle", "duration": 4.0, "transition": {"type": "blend", "duration": 0.8}}],
    [anim(0.5, "@nearest:minecraft:zombie", "cine.zombie.window_pound"), anim(1.5, "@nearest:minecraft:zombie", "zombie.rise_from_ground"), anim(3.0, "@nearest:minecraft:zombie", "cine.zombie.lurch_reveal"),
     anim(2.0, "@nearest:minecraft:skeleton", "cine.skeleton.bone_salute"), anim(4.5, "@nearest:minecraft:skeleton", "cine.skeleton.volley_aim"), anim(4.0, "@self", "cine.player.draw_sword_slow"),
     anim(5.0, "@nearest:minecraft:phantom", "cine.phantom.moon_silhouette"), anim(2.5, "@nearest:minecraft:zombie_villager", "cine.zombie_villager.lost_memory"),
     anim(3.5, "@nearest:minecraft:drowned", "cine.drowned.trident_rise")])
seq("mountain_summit", "cinematic.mountain_summit", "@self",
    [{"type": "crane", "duration": 5.0, "from_height": 1, "to_height": 12}, {"type": "orbit", "duration": 6.0, "radius": 10, "height": 4, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@self", "cine.player.climb_ledge_pull"), anim(2.2, "@self", "cine.player.plant_flag"), anim(5.0, "@self", "cine.player.cloak_wind"), anim(7.0, "@self", "cine.player.horizon_gaze"),
     anim(3.0, "@nearest:minecraft:goat", "cine.goat.summit_scream"), anim(6.0, "@self", "cine.player.wind_brace"), anim(8.0, "@nearest:minecraft:snow_golem", "cine.snow_golem.first_snow")])
seq("homecoming", "cinematic.homecoming", "@self",
    [{"type": "track", "duration": 4.0, "offset": [0, 1.2, -5]}, {"type": "close_up", "duration": 4.0, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@self", "cine.player.vanish_into_fog"), anim(4.0, "@self", "cine.player.embrace"), anim(1.0, "@nearest:minecraft:wolf", "cine.wolf.loyal_guard"),
     anim(3.0, "@nearest:minecraft:wolf", "cine.wolf.pack_howl"), anim(2.0, "@nearest:minecraft:horse", "cine.horse.nuzzle_owner"), anim(5.0, "@nearest:minecraft:horse", "cine.horse.rear_silhouette"),
     anim(4.0, "@nearest:minecraft:parrot", "cine.parrot.perch_land"), anim(5.0, "@nearest:minecraft:cow", "cine.cow.pasture_low"), anim(5.5, "@nearest:minecraft:sheep", "cine.sheep.shepherds_flock")])
seq("wild_wonders", "cinematic.wild_wonders", "@self",
    [{"type": "establishing", "duration": 5.0}, {"type": "orbit", "duration": 5.0, "radius": 7, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0.5, "@nearest:minecraft:allay", "cine.allay.deliver_gift"), anim(1.0, "@nearest:minecraft:fox", "cine.fox.steal_item"), anim(2.0, "@nearest:minecraft:bee", "cine.bee.royal_dance"),
     anim(3.0, "@nearest:minecraft:sniffer", "cine.sniffer.discover_seed"), anim(3.5, "@nearest:minecraft:dolphin", "cine.dolphin.leap_arc"), anim(4.0, "@nearest:minecraft:axolotl", "cine.axolotl.faint_reveal"),
     anim(4.5, "@nearest:minecraft:ocelot", "cine.ocelot.jungle_stalk_reveal"), anim(5.0, "@nearest:minecraft:polar_bear", "cine.polar_bear.protect_cub"),
     anim(5.5, "@nearest:minecraft:panda", "cine.panda.bamboo_feast"), anim(6.0, "@nearest:minecraft:frog", "cine.frog.lily_croak"), anim(6.5, "@nearest:minecraft:turtle", "cine.turtle.hatchling_journey"),
     anim(7.0, "@nearest:minecraft:mooshroom", "cine.mooshroom.spore_bloom"), anim(7.5, "@nearest:minecraft:husk", "cine.husk.mirage_shamble"),
     anim(8.0, "@nearest:minecraft:shulker", "cine.shulker.slow_open"), anim(0, "@self", "cine.player.examine_relic")])
seq("fallen_comrade", "cinematic.fallen_comrade", "@self",
    [{"type": "high_angle", "duration": 5.0}, {"type": "close_up", "duration": 4.0, "transition": {"type": "blend", "duration": 1.2}}],
    [anim(0, "@self", "cine.player.kneel_grief"), anim(4.0, "@self", "cine.player.rise_from_kneel"), anim(6.0, "@self", "cine.player.toast"), anim(8.0, "@self", "cine.player.read_letter")])
seq("dawn_vigil", "cinematic.dawn_vigil", "@self",
    [{"type": "pan", "duration": 5.0, "from_yaw": -50, "to_yaw": 30}, {"type": "low_angle", "duration": 4.0, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@self", "cine.player.kneel_reverent"), anim(3.0, "@self", "cine.player.rise_from_kneel"), anim(5.0, "@self", "cine.player.slow_turn_reveal"), anim(7.4, "@self", "cine.player.ready_stance")])
seq("last_stand", "cinematic.last_stand", "@self",
    [{"type": "orbit", "duration": 5.0, "radius": 5, "height": 1}, {"type": "low_angle", "duration": 3.0, "transition": {"type": "blend", "duration": 0.6}},
     {"type": "extreme_close_up", "duration": 2.0}],
    [anim(0, "@self", "cine.player.catch_breath"), anim(2.5, "@self", "cine.player.surrender"), anim(4.5, "@self", "cine.player.reach_out"), anim(6.5, "@self", "cine.player.collapse_exhausted"),
     anim(8.5, "@self", "cine.player.drop_to_knees_victory"), {"time": 6.4, "type": "time_scale", "value": 0.4, "duration": 1.5}], cancel_on_damage=False)


# ============================================================================ more scenes
for cid, name, L, tracks, fns in (
        ("sunset_silhouette", "Silhouette Against The Sunset", 5.0, None, {"head:rot": lambda u: [-8, 6 * wave(u, 0, 0.5), 0], "right_arm:rot": lambda u: R(-10, 6), "left_arm:rot": lambda u: Lh(30, -10, 30),
                                                                           "cloak:rot": lambda u: [12 + 5 * wave(u, 0, 2), 0, 2 * wave(u)], "left_leg:rot": lambda u: LL(-8)}),
        ("sheathe_slow", "Slowly Sheathe The Blade", 2.2, {"right_arm:rot": [(0, R(60, 10, -10)), (0.8, R(30, -20, 40)), (1.6, R(-20, -20, 60), "in_out_sine"), (2.2, Z)], "head:rot": [(0, Z), (1.0, [20, 0, 0]), (2.2, Z)],
                                                          "body:rot": [(0, Z), (1.0, tilt(4, 15, 0)), (2.2, Z)]}, None),
        ("bow_aim_hold", "Hold A Drawn Bow Steady", 3.0, None, {"left_arm:rot": lambda u: Lh(90, 0, 10 + 0.5 * wave(u, 0, 4)), "right_arm:rot": lambda u: R(90, -30, -60), "head:rot": lambda u: [0, 10, 0], "body:rot": lambda u: tilt(0, -25, 0)}),
        ("raise_banner", "Raise The Banner High", 2.6, {"right_arm:rot": [(0, Z), (0.8, R(170, 10), "out_quad"), (2.6, R(172, 12))], "left_arm:rot": [(0, Z), (0.9, Lh(150, 10)), (2.6, Lh(152, 12))],
                                                       "head:rot": [(0, Z), (0.8, [-35, 0, 0]), (2.6, [-35, 0, 0])], "body:rot": [(0, Z), (0.8, tilt(-10)), (2.6, tilt(-10))]}, None),
        ("cradle_wounded", "Cradle A Wounded Friend", 4.0, None, {"right_arm:rot": lambda u: R(60, -20, 30), "left_arm:rot": lambda u: Lh(50, -30, 30), "mw_root:pos": lambda u: move(0, -5, 0), "right_leg:rot": lambda u: RL(90),
                                                                  "left_leg:rot": lambda u: LL(20), "head:rot": lambda u: [35, 0, 6 * wave(u, 0, 0.5)], "body:rot": lambda u: tilt(20 + 2 * wave(u), 0, 0)}),
        ("heave_heavy_door", "Heave Open A Heavy Door", 3.0, {"right_arm:rot": [(0, Z), (0.5, R(90, 0)), (3.0, R(90, 0))], "left_arm:rot": [(0, Z), (0.5, Lh(90, 0)), (3.0, Lh(90, 0))],
                                                             "body:rot": [(0, Z), (0.6, tilt(30)), (3.0, tilt(34))], "right_leg:rot": [(0, Z), (0.6, RL(30)), (3.0, RL(30))], "left_leg:rot": [(0, Z), (0.6, LL(-25)), (3.0, LL(-25))],
                                                             "mw_root:pos": [(0, Z), (3.0, move(0, 0, 3))]}, None),
        ("dramatic_lever", "Throw The Great Lever", 2.0, {"right_arm:rot": [(0, Z), (0.6, R(160, 0)), (1.0, R(40, 0), "in_quart"), (2.0, R(40, 0))], "left_arm:rot": [(0, Z), (0.6, Lh(160, 0)), (1.0, Lh(40, 0), "in_quart"), (2.0, Lh(40, 0))],
                                                         "body:rot": [(0, Z), (0.6, tilt(-10)), (1.0, tilt(30)), (2.0, tilt(20))]}, None),
        ("light_wall_torch", "Light A Torch On The Wall", 2.4, {"right_arm:rot": [(0, Z), (0.8, R(130, 20, 0)), (1.4, R(140, 20)), (2.4, R(60))], "head:rot": [(0, Z), (0.8, [-20, 20, 0]), (2.4, Z)]}, None),
        ("spyglass_hold", "Survey Through A Spyglass", 4.0, None, {"right_arm:rot": lambda u: R(140, -40, 30), "left_arm:rot": lambda u: Lh(120, -40, 30), "head:rot": lambda u: [-6, 25 * wave(u, 0, 0.5), 0],
                                                                    "body:rot": lambda u: tilt(-4, 10 * wave(u, 0, 0.5), 0)}),
        ("drink_from_stream", "Drink From A Stream", 3.6, {"mw_root:pos": [(0, Z), (0.8, move(0, -6, 0)), (3.6, move(0, -6, 0))], "right_leg:rot": [(0, Z), (0.8, RL(100)), (3.6, RL(100))], "left_leg:rot": [(0, Z), (0.8, LL(100)), (3.6, LL(100))],
                                                         "body:rot": [(0, Z), (1.0, tilt(50)), (2.0, tilt(20)), (3.6, tilt(50))], "right_arm:rot": [(0, Z), (1.0, R(60, -20, 30)), (2.0, R(120, -30, 40)), (3.6, R(60, -20, 30))],
                                                         "left_arm:rot": [(0, Z), (1.0, Lh(60, -20, 30)), (2.0, Lh(120, -30, 40)), (3.6, Lh(60, -20, 30))]}, None),
        ("pearl_hurl", "Hurl An Ender Pearl Into The Void", 2.0, {"right_arm:rot": [(0, Z), (0.7, R(-40, 10)), (0.9, R(160, 0), "out_expo"), (2.0, R(100, 0))], "body:rot": [(0, Z), (0.7, tilt(-6, 20, 0)), (0.9, tilt(10, -20, 0)), (2.0, Z)],
                                                                 "left_leg:rot": [(0, Z), (0.7, LL(-20)), (2.0, LL(-10))]}, None),
        ("catch_falling", "Catch Something Falling", 1.6, {"right_arm:rot": [(0, Z), (0.3, R(150, 20), "out_expo"), (0.6, R(80, 0)), (1.6, R(60, -10, 20))], "left_arm:rot": [(0, Z), (0.35, Lh(150, 20), "out_expo"), (0.6, Lh(80, 0)), (1.6, Lh(60, -10, 20))],
                                                          "head:rot": [(0, Z), (0.3, [-40, 0, 0]), (0.6, [20, 0, 0]), (1.6, [30, 0, 0])]}, None),
        ("tie_horse", "Tie A Horse To The Post", 2.4, {"right_arm:rot": [(0, Z), (0.6, R(70, 20)), (1.0, R(80, -10)), (1.4, R(70, 20)), (1.8, R(80, -10)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.6, Lh(70, -10)), (1.8, Lh(70, -10)), (2.4, Z)],
                                                      "head:rot": [(0, Z), (0.6, [25, 0, 0]), (2.4, Z)]}, None),
        ("feed_kneel", "Kneel To Feed An Animal", 3.0, with_kneel(3.0, {"right_arm:rot": [(0, Z), (0.8, R(60, 0)), (3.0, R(62, 0))], "head:rot": [(0, Z), (0.8, [25, 0, 0]), (3.0, [20, 0, 6])]}), None),
        ("knight_oath", "Swear A Knight's Oath", 4.0, with_kneel(4.0, {"right_arm:rot": [(0, Z), (0.8, R(60, -20, 40)), (4.0, R(60, -20, 40))], "left_arm:rot": [(0, Z), (0.8, Lh(60, -20, 40)), (4.0, Lh(60, -20, 40))],
                                                                    "head:rot": [(0, Z), (0.8, [20, 0, 0]), (3.0, [-10, 0, 0]), (4.0, [-10, 0, 0])]}), None),
        ("bell_rope", "Ring The Great Bell", 2.4, {"right_arm:rot": [(0, R(170)), (0.6, R(60), "in_quad"), (1.2, R(170)), (1.8, R(60), "in_quad"), (2.4, R(170))], "left_arm:rot": [(0, Lh(165)), (0.6, Lh(55), "in_quad"), (1.2, Lh(165)), (1.8, Lh(55), "in_quad"), (2.4, Lh(165))],
                                                  "mw_root:pos": [(0, Z), (0.6, move(0, -1.5, 0)), (1.2, Z), (1.8, move(0, -1.5, 0)), (2.4, Z)]}, None)):
    scene("cine.player." + cid, name, L, tracks, fns)
for T, sp, cid, name, L, tracks in (
        (V, "villager", "harvest_dance", "Villagers Dancing At The Harvest Festival", 1.0, {"mw_root:pos": [(0, Z), (0.25, move(0, 1.5, 0)), (0.5, Z), (0.75, move(0, 1.5, 0)), (1.0, Z)], "mw_root:rot": [(0, Z), (1.0, [0, 180, 0])],
                                                                                          "arms:rot": [(0, [-30, 0, 0]), (0.5, [-60, 0, 0]), (1.0, [-30, 0, 0])]}),
        (V, "villager", "read_prophecy", "Librarian Reading An Old Prophecy", 4.0, {"arms:rot": [(0, Z), (0.8, [-80, 0, 0]), (4.0, [-80, 0, 0])], "head:rot": [(0, Z), (0.8, [30, 0, 0]), (2.4, [30, 0, 8]), (3.2, [-20, 0, 0]), (4.0, [-20, 0, 0])]}),
        (V, "villager", "bless_hero", "Cleric Anointing The Hero", 3.6, {"arms:rot": [(0, Z), (0.8, [-90, 0, 0]), (1.6, [-170, 0, 0], "out_quad"), (2.6, [-170, 0, 0]), (3.6, Z)], "head:rot": [(0, Z), (0.8, [20, 0, 0]), (1.6, [-35, 0, 0]), (3.6, Z)],
                                                                       "body:rot": [(0, Z), (0.8, tilt(14)), (1.6, tilt(-10)), (3.6, Z)], "mw_root:pos": [(0, Z), (1.6, move(0, 1, 0)), (2.6, move(0, 1, 0)), (3.6, Z)]}),
        (V, "villager", "present_armour", "Armorer Presenting Forged Armour", 3.0, {"arms:rot": [(0, Z), (0.6, [-90, 0, 0], "out_back"), (2.4, [-90, 0, 0]), (3.0, Z)], "body:rot": [(0, Z), (0.6, tilt(20)), (2.4, tilt(20)), (3.0, Z)],
                                                                                  "head:rot": [(0, Z), (2.4, [-10, 0, 0]), (3.0, Z)]}),
        (V, "villager", "child_runs_to_hero", "Village Child Running To The Hero", 2.0, {"right_leg:rot": [(0, Z), (0.25, leg('r', -40)), (0.5, leg('r', 40)), (0.75, leg('r', -40)), (1.0, leg('r', 40)), (2.0, Z)],
                                                                                        "left_leg:rot": [(0, Z), (0.25, leg('l', 40)), (0.5, leg('l', -40)), (0.75, leg('l', 40)), (1.0, leg('l', -40)), (2.0, Z)], "arms:rot": [(0, Z), (1.2, [-160, 0, 0]), (2.0, [-160, 0, 0])]}),
        ("minecraft:cat", "cat", "rub_legs", "Cat Weaving Between The Hero's Legs", 2.4, {"mw_center:rot": [(0, Z), (0.6, tilt(0, 40, 14)), (1.2, tilt(0, -40, -14)), (1.8, tilt(0, 40, 14)), (2.4, Z)], "tail1:rot": [(0, [-50, 0, 0]), (2.4, [-50, 0, 0])]}),
        ("minecraft:wolf", "wolf", "fetch_return", "Wolf Proudly Returning A Stick", 2.0, {"head:rot": [(0, [-10, 0, 0]), (1.0, [-20, 0, 0]), (2.0, [10, 0, 0])], "tail:rot": [(0, [0, 30, 0]), (0.25, [0, -30, 0]), (0.5, [0, 30, 0]), (0.75, [0, -30, 0]), (1.0, [0, 30, 0]), (2.0, Z)]}),
        ("minecraft:horse", "horse", "sunset_graze", "Horse Grazing At Sunset", 4.0, {"head_parts:rot": [(0, Z), (1.0, [65, 0, 0]), (3.0, [65, 10, 0]), (4.0, [10, 0, 0])], "tail:rot": [(0, Z), (1.5, [0, 20, 0]), (2.5, [0, -20, 0]), (4.0, Z)]}),
        ("minecraft:llama", "llama", "spit_at_trader", "Llama Spitting At The Trader", 1.6, {"head:rot": [(0, Z), (0.5, [-30, 0, 0]), (0.65, [15, 0, 0], "out_expo"), (1.6, Z)], "mw_center:pos": [(0, Z), (0.5, move(0, 0, -1)), (0.65, move(0, 0, 1)), (1.6, Z)]}),
        ("minecraft:warden", "warden", "listen_then_leave", "Warden Listening, Then Sinking Away", 4.0, {"head:rot": [(0, Z), (1.0, [-10, 30, 0]), (2.0, [-10, -30, 0]), (2.6, Z)], "mw_root:pos": [(0, Z), (2.6, Z), (4.0, move(0, -20, 0), "in_quad")],
                                                                                                       "left_tendril:rot": [(0, Z), (1.0, [-20, 0, 0]), (2.6, Z)]}),
        ("minecraft:wither", "wither", "armour_phase", "Wither Shifting Into Its Armoured Phase", 2.4, {"shoulders:rot": [(0, Z), (1.0, [20, 0, 0]), (2.4, [12, 0, 0])], "ribcage:scl": [(0, [1, 1, 1]), (1.0, [1.2, 1.2, 1.2]), (2.4, [1.05, 1.05, 1.05])],
                                                                                                      "tail:rot": [(0, Z), (1.0, [40, 0, 0]), (2.4, [30, 0, 0])]}),
        ("minecraft:ender_dragon", "ender_dragon", "perch_breath", "Ender Dragon Breathing Fire From Its Perch", 3.0, {"mw_root:pos": [(0, Z), (0.8, move(0, -3, 3)), (2.4, move(0, -3, 3)), (3.0, Z)], "mw_root:rot": [(0, Z), (0.8, tilt(14, 0, 0)), (2.4, tilt(14, 0, 0)), (3.0, Z)]}),
        ("minecraft:evoker", "evoker", "fang_line", "Evoker Calling A Line Of Fangs", 2.0, {"right_arm:rot": [(0, Z), (0.5, arm('r', 120, 40)), (1.0, arm('r', 60, 10), "in_quart"), (2.0, Z)], "left_arm:rot": [(0, Z), (0.5, arm('l', 120, 40)), (1.0, arm('l', 60, 10), "in_quart"), (2.0, Z)],
                                                                                          "body:rot": [(0, Z), (1.0, tilt(20)), (2.0, Z)]}),
        ("minecraft:piglin", "piglin", "gold_sneer", "Piglin Sneering At Worthless Iron", 2.0, {"head:rot": [(0, Z), (0.5, [20, 0, 0]), (1.0, [-10, -30, 0]), (2.0, Z)], "left_arm:rot": [(0, arm('l', 70, 20)), (1.0, arm('l', 40, 60)), (2.0, Z)],
                                                                                              "body:rot": [(0, Z), (1.0, tilt(-6, -15, 0)), (2.0, Z)]}),
        ("minecraft:enderman", "enderman", "place_block_gently", "Enderman Setting A Block Down Gently", 2.4, {"body:rot": [(0, Z), (1.0, tilt(50)), (1.6, tilt(50)), (2.4, Z)], "right_arm:rot": [(0, arm('r', 40)), (1.0, arm('r', 80)), (1.6, arm('r', 80)), (2.4, Z)],
                                                                                                             "left_arm:rot": [(0, arm('l', 40)), (1.0, arm('l', 80)), (1.6, arm('l', 80)), (2.4, Z)]})):
    scene("cine.%s.%s" % (sp, cid), name, L, tracks, target=T, file=FM + "/" + sp)
for T, sp, cid, name, L, fns in (
        ("minecraft:parrot", "parrot", "record_dance", "Parrot Dancing To A Record", 0.5, {"mw_center:pos": lambda u: move(0, 0.8 * max(0, wave(u)), 0), "head:rot": lambda u: [-20 * wave(u), 0, 14 * wave(u, 0, 0.5)],
                                                                                         "right_wing:rot": lambda u: [0, 0, 30 * max(0, wave(u, 0.25))], "left_wing:rot": lambda u: [0, 0, -30 * max(0, wave(u, 0.25))]}),
        ("minecraft:bee", "bee", "hive_return", "Bee Drifting Home To The Hive", 2.0, {"bone:pos": lambda u: move(0.5 * wave(u), 0.6 * wave(u, 0.25), 0), "bone:rot": lambda u: tilt(-8, 0, 6 * wave(u)),
                                                                                       "back_legs:rot": lambda u: [-20, 0, 0]}),
        ("minecraft:fox", "fox", "snow_frolic", "Fox Frolicking In Fresh Snow", 1.0, {"mw_center:pos": lambda u: move(0, 2.5 * max(0, wave(u)), 0), "mw_center:rot": lambda u: tilt(-20 * wave(u), 0, 0), "tail:rot": lambda u: [-20, 30 * wave(u), 0]}),
        ("minecraft:dolphin", "dolphin", "lead_to_treasure", "Dolphin Leading The Way To Treasure", 1.6, {"mw_center:rot": lambda u: tilt(0, 30 * wave(u, 0, 0.5), 10 * wave(u)), "tail:rot": lambda u: [-16 * wave(u, 0.15), 0, 0],
                                                                                                          "tail_fin:rot": lambda u: [-24 * wave(u, 0.3), 0, 0]})):
    scene("cine.%s.%s" % (sp, cid), name, L, fns=fns, target=T, file=FM + "/" + sp)

seq("harvest_festival", "cinematic.harvest_festival", "@nearest:minecraft:villager",
    [{"type": "establishing", "duration": 5.0}, {"type": "orbit", "duration": 6.0, "radius": 6, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@anchor", "cine.villager.harvest_dance"), anim(1.0, "@nearest:minecraft:villager", "cine.villager.pray_rain"), anim(2.5, "@nearest:minecraft:villager", "cine.villager.read_prophecy"),
     anim(4.0, "@nearest:minecraft:villager", "cine.villager.bless_hero"), anim(5.5, "@nearest:minecraft:villager", "cine.villager.present_armour"),
     anim(7.0, "@nearest:minecraft:villager", "cine.villager.child_runs_to_hero"), anim(7.5, "@self", "cine.player.bell_rope")])
seq("knight_oath", "cinematic.knight_oath", "@self",
    [{"type": "low_angle", "duration": 5.0}, {"type": "close_up", "duration": 4.0, "transition": {"type": "blend", "duration": 1.0}}, {"type": "crane", "duration": 4.0}],
    [anim(0, "@self", "cine.player.knight_oath"), anim(4.2, "@self", "cine.player.raise_banner"), anim(7.4, "@self", "cine.player.sheathe_slow"), anim(9.8, "@self", "cine.player.sunset_silhouette")])
seq("sealed_vault", "cinematic.sealed_vault", "@self",
    [{"type": "over_shoulder", "duration": 4.0}, {"type": "wide", "duration": 4.0, "transition": {"type": "blend", "duration": 0.8}}],
    [anim(0, "@self", "cine.player.light_wall_torch"), anim(2.6, "@self", "cine.player.dramatic_lever"), anim(4.8, "@self", "cine.player.heave_heavy_door"), {"time": 3.6, "type": "shake", "amount": 0.4}])
seq("wilderness_camp", "cinematic.wilderness_camp", "@self",
    [{"type": "orbit", "duration": 5.0, "radius": 5}, {"type": "close_up", "duration": 4.0, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@self", "cine.player.drink_from_stream"), anim(3.8, "@self", "cine.player.feed_kneel"), anim(7.0, "@self", "cine.player.catch_falling"), anim(4.0, "@nearest:minecraft:fox", "cine.fox.snow_frolic")])
seq("sunset_ride", "cinematic.sunset_ride", "@self",
    [{"type": "track", "duration": 5.0, "offset": [4, 1.5, 6]}, {"type": "wide", "duration": 5.0, "transition": {"type": "blend", "duration": 1.2}}],
    [anim(0, "@self", "cine.player.tie_horse"), anim(0.5, "@nearest:minecraft:horse", "cine.horse.sunset_graze"), anim(3.0, "@self", "cine.player.spyglass_hold"), anim(7.0, "@self", "cine.player.cradle_wounded")])
seq("archers_duel", "cinematic.archers_duel", "@self",
    [{"type": "over_shoulder", "duration": 4.0}, {"type": "extreme_close_up", "duration": 2.0, "transition": {"type": "blend", "duration": 0.5}}, {"type": "pull_out", "duration": 3.0}],
    [anim(0, "@self", "cine.player.bow_aim_hold"), anim(5.0, "@self", "cine.player.pearl_hurl"), {"time": 4.0, "type": "time_scale", "value": 0.35, "duration": 1.2}])
seq("beast_bonds", "cinematic.beast_bonds", "@self",
    [{"type": "orbit", "duration": 6.0, "radius": 4, "height": 0.8}, {"type": "close_up", "duration": 4.0, "transition": {"type": "blend", "duration": 1.0}}],
    [anim(0, "@nearest:minecraft:cat", "cine.cat.rub_legs"), anim(1.0, "@nearest:minecraft:wolf", "cine.wolf.fetch_return"), anim(2.0, "@nearest:minecraft:parrot", "cine.parrot.record_dance"),
     anim(3.0, "@nearest:minecraft:bee", "cine.bee.hive_return"), anim(4.0, "@nearest:minecraft:dolphin", "cine.dolphin.lead_to_treasure"), anim(0, "@self", "cine.player.feed_kneel")])
seq("dark_omens", "cinematic.dark_omens", "@self",
    [{"type": "high_angle", "duration": 4.0}, {"type": "low_angle", "duration": 4.0, "transition": {"type": "blend", "duration": 0.8}}],
    [anim(0, "@nearest:minecraft:warden", "cine.warden.listen_then_leave"), anim(1.0, "@nearest:minecraft:wither", "cine.wither.armour_phase"),
     anim(2.0, "@nearest:minecraft:ender_dragon", "cine.ender_dragon.perch_breath"), anim(3.0, "@nearest:minecraft:evoker", "cine.evoker.fang_line"), anim(4.0, "@nearest:minecraft:piglin", "cine.piglin.gold_sneer"),
     anim(5.0, "@nearest:minecraft:enderman", "cine.enderman.place_block_gently"), anim(6.0, "@nearest:minecraft:llama", "cine.llama.spit_at_trader"), anim(0, "@self", "cine.player.startled_turn")])

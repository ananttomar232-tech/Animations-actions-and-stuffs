"""First-person animations (category: first_person).

Bones: fp_main / fp_off (whole hand + item), fp_main_item / fp_off_item (item only), fp_view (camera).
Every clip listens to the same event and condition as its third-person counterpart, and both
controllers share the player's seed, so the two views always choose matching variants.
"""
from core import Clip, state, event, strike, shake, wave, cwave

CAT = "first_person"
T = "@first_person"
Z = (0, 0, 0)
ALIVE = "!q.is_dead && !q.is_sleeping"


def P(right=0.0, up=0.0, back=0.0):
    """First-person hand offset in pixels: right, up, toward the viewer."""
    return [right, -up, back]


def R(pitch_up=0.0, yaw_left=0.0, roll_left=0.0):
    return [pitch_up, yaw_left, roll_left]


def V(down=0.0, right=0.0, roll=0.0):
    """Camera offset in degrees (applied on top of the view)."""
    return [down, right, roll]


def fp(cid, name, trig, L, pri=200, layer="action", replaces=True, file="first_person/actions", blend_in=0.04, blend_out=0.18, loop="once", interrupt_after=0.6):
    c = Clip("fp." + cid, name, CAT, T, length=L, loop=loop, layer=layer, priority=pri, trigger=trig, file=file, blend_in=blend_in, blend_out=blend_out,
             interrupt_after=interrupt_after, rig="first_person")
    if replaces and layer == "action":
        c.tag(replaces_vanilla_swing="true")
    return c


def swing(cid, name, when, pri, L, w, i, f, wind, imp, fol, view=(Z, Z), ev="attack", weight="medium", off=None, file="first_person/melee"):
    """wind/imp/fol: (P(...), R(...)) hand placements at wind-up, impact and follow-through."""
    c = fp(cid, name, event(ev, when), L, pri=pri, file=file, interrupt_after=min(0.9, f / L + 0.05))
    strike(c, "fp_main", Z, wind[0], imp[0], fol[0], w, i, f, L, ch="position")
    strike(c, "fp_main", Z, wind[1], imp[1], fol[1], w, i, f, L, ch="rotation")
    c.rot("fp_view", (0, Z), (w, view[0], "out_quad"), (i, view[1], "in_quart"), (L, Z, "in_out_sine"))
    if off:
        c.pos("fp_off", (0, Z), (w, off[0]), (i, off[1]), (L, Z))
    c.ev(max(0, w - 0.02), "whoosh", weight=weight)
    return c


W = lambda cat: ALIVE + " && q.main_hand == '%s'" % cat  # noqa: E731
SW, AX, TR, FI = W("sword"), W("axe"), W("trident"), W("empty")
GROUND, AIRB = " && q.is_on_ground", " && !q.is_on_ground && q.vertical_speed < 0"
STRONG, WEAK = " && q.attack_strength >= 0.9", " && q.attack_strength < 0.9"

# -------------------------------------------------------------------------- sword
swing("sword_forehand", "FP Forehand Slash", SW + " && q.combo == 0" + GROUND, 200, 0.55, 0.16, 0.26, 0.38,
      (P(7, 4, 2), R(30, -50, -20)), (P(-6, -1, -5), R(-10, 50, 30)), (P(-12, -3, -3), R(-20, 80, 40)), (V(0, -3, -2), V(1, 4, 3)))
swing("sword_backhand", "FP Backhand Slash", SW + " && q.combo == 1" + GROUND, 200, 0.55, 0.15, 0.25, 0.37,
      (P(-9, 3, 1), R(20, 60, 30)), (P(4, -1, -5), R(-10, -40, -20)), (P(10, -3, -2), R(-20, -80, -40)), (V(0, 3, 2), V(1, -4, -3)))
swing("sword_overhead", "FP Overhead Finisher", SW + " && q.combo == 2" + GROUND, 200, 0.7, 0.22, 0.33, 0.46,
      (P(0, 10, 3), R(70, 0, 0)), (P(-1, -6, -6), R(-60, 0, 0)), (P(-1, -9, -3), R(-80, 0, 0)), (V(-3, 0, 0), V(5, 0, 0)), weight="heavy")
swing("sword_rising_power", "FP Rising Power Slash", SW + " && q.combo == 0" + GROUND + STRONG, 205, 0.75, 0.28, 0.38, 0.52,
      (P(6, -8, 1), R(-40, -30, -30)), (P(-3, 6, -6), R(50, 30, 20)), (P(-6, 10, -2), R(80, 40, 30)), (V(3, -2, 0), V(-4, 2, 2)), weight="heavy")
swing("sword_sweep_spin", "FP Sweeping Spin", SW + " && q.combo == 2" + GROUND + STRONG, 206, 0.95, 0.25, 0.45, 0.7,
      (P(10, 2, 3), R(10, -70, -10)), (P(-10, 0, -4), R(0, 70, 10)), (P(-14, -2, 0), R(-10, 110, 10)), (V(0, -12, -4), V(1, 30, 4)), weight="heavy")
swing("sword_lunge", "FP Lunging Thrust", SW + " && q.is_sneaking" + STRONG, 207, 0.65, 0.24, 0.32, 0.44,
      (P(2, 0, 6), R(0, 0, 0)), (P(0, 0, -10), R(-6, 0, 0)), (P(0, -1, -9), R(-6, 0, 0)), (V(0, 0, 0), V(2, 0, 0)))
swing("sword_running_slash", "FP Running Slash", SW + " && q.is_sprinting", 210, 0.5, 0.12, 0.2, 0.32,
      (P(8, 2, 0), R(20, -60, -30)), (P(-6, -2, -6), R(-10, 50, 30)), (P(-12, -4, -2), R(-20, 80, 40)), (V(1, -2, -2), V(2, 4, 4)))
swing("sword_sprint_lunge", "FP Charging Lunge", SW + " && q.is_sprinting" + STRONG, 211, 0.7, 0.18, 0.28, 0.42,
      (P(3, -1, 5), R(4, -6, 0)), (P(0, 0, -12), R(-8, 0, 0)), (P(0, -2, -11), R(-10, 0, 0)), (V(-1, 0, 0), V(4, 0, 0)), weight="heavy")
swing("sword_jump_cleave", "FP Leaping Cleave", SW + AIRB, 212, 0.6, 0.15, 0.25, 0.36,
      (P(0, 12, 4), R(80, 0, 0)), (P(0, -8, -6), R(-70, 0, 0)), (P(0, -11, -3), R(-90, 0, 0)), (V(-4, 0, 0), V(8, 0, 0)), weight="heavy", off=(P(-2, 10, 3), P(-1, -6, -5)))
swing("sword_crit_flourish", "FP Critical Flourish", SW + AIRB + STRONG, 213, 0.75, 0.18, 0.3, 0.45,
      (P(8, 10, 3), R(60, -40, -30)), (P(-6, -6, -6), R(-50, 40, 40)), (P(-12, -9, -2), R(-70, 70, 50)), (V(-4, -3, -4), V(8, 4, 6)), weight="heavy")
swing("sword_sneak_stab", "FP Sneak Stab", SW + " && q.is_sneaking" + WEAK, 206, 0.45, 0.12, 0.2, 0.3,
      (P(1, -2, 4), R(-10, 0, 0)), (P(0, -2, -7), R(-14, 0, 0)), (P(0, -2, -6), R(-14, 0, 0)), weight="light")
swing("sword_board_cut", "FP Sword-And-Board Cut", SW + " && q.off_hand == 'shield' && q.combo == 0" + GROUND, 203, 0.55, 0.15, 0.25, 0.36,
      (P(6, 6, 1), R(40, -30, -10)), (P(-4, 0, -5), R(-10, 30, 20)), (P(-8, -2, -2), R(-20, 50, 30)), off=(P(0, 0, -2), P(1, 1, -3)))
swing("sword_board_chop", "FP Sword-And-Board Chop", SW + " && q.off_hand == 'shield' && q.combo == 1" + GROUND, 203, 0.6, 0.18, 0.28, 0.4,
      (P(2, 10, 3), R(70, -10, 0)), (P(-2, -4, -6), R(-50, 10, 0)), (P(-2, -7, -3), R(-70, 10, 0)), (V(-2, 0, 0), V(4, 0, 0)), off=(P(0, 0, -2), P(1, 2, -3)))
swing("sword_board_feint", "FP Shield Feint Thrust", SW + " && q.off_hand == 'shield' && q.combo == 2" + GROUND, 203, 0.7, 0.24, 0.36, 0.5,
      (P(4, -2, 4), R(0, -10, 0)), (P(0, 0, -11), R(-4, 0, 0)), (P(0, -1, -10), R(-4, 0, 0)), off=(P(4, 4, -6), P(-2, -2, 2)))
swing("sword_two_hand_overhead", "FP Two-Handed Overhead", SW + " && q.off_hand == 'empty' && q.combo == 1" + STRONG + GROUND, 208, 0.85, 0.3, 0.42, 0.56,
      (P(-2, 14, 5), R(90, 10, 0)), (P(-2, -8, -6), R(-70, 10, 0)), (P(-2, -12, -2), R(-95, 10, 0)), (V(-6, 0, 0), V(10, 0, 0)), weight="heavy", off=(P(6, 14, 5), P(4, -8, -6)))
swing("sword_pommel", "FP Pommel Strike", SW + " && q.is_sneaking && q.attack_strength < 0.5", 209, 0.4, 0.1, 0.18, 0.26,
      (P(-2, 2, 3), R(0, 0, -80)), (P(-2, 1, -7), R(0, 0, -90)), (P(-2, 1, -6), R(0, 0, -90)), weight="light")
swing("sword_desperate", "FP Desperate Flail", SW + " && q.health < 0.25", 215, 0.6, 0.2, 0.28, 0.38,
      (P(9, 8, 2), R(50, -60, -40)), (P(-8, -4, -5), R(-30, 60, 40)), (P(-13, -6, -1), R(-40, 90, 50)), (V(-1, -4, -6), V(3, 6, 8)))
swing("sword_backhand_power", "FP Backhand Power Arc", SW + " && q.combo == 1" + GROUND + STRONG, 205, 0.75, 0.26, 0.36, 0.5,
      (P(-12, 4, 2), R(20, 80, 40)), (P(6, 0, -6), R(-10, -50, -30)), (P(13, -2, -2), R(-20, -100, -50)), (V(0, 6, 3), V(2, -10, -4)), weight="heavy")
swing("sword_swipe_air", "FP Air Swipe", SW + " && !q.is_mining", 150, 0.45, 0.1, 0.2, 0.3,
      (P(5, 3, 1), R(20, -30, -10)), (P(-4, 0, -3), R(-6, 30, 16)), (P(-7, -1, -1), R(-10, 45, 20)), ev="swing", weight="light")
swing("sword_weak_poke", "FP Uncharged Poke", SW + " && q.attack_strength < 0.3", 199, 0.35, 0.08, 0.14, 0.22,
      (P(1, 0, 2), R(4, 0, 0)), (P(0, 0, -4), R(-4, 0, 0)), (P(0, 0, -3), R(-4, 0, 0)), weight="light")
swing("sword_plunge", "FP Plunging Strike", SW + AIRB + " && q.fall_distance > 4", 214, 0.7, 0.1, 0.2, 0.45,
      (P(0, 12, 5), R(100, 0, 0)), (P(0, -12, -4), R(-100, 0, 0)), (P(0, -14, -2), R(-110, 0, 0)), (V(-8, 0, 0), V(14, 0, 0)), weight="heavy", off=(P(-6, 12, 5), P(-4, -12, -4)))

# -------------------------------------------------------------------------- axe
swing("axe_chop", "FP Downward Chop", AX + " && q.combo == 0" + GROUND, 200, 0.7, 0.24, 0.34, 0.48,
      (P(2, 12, 4), R(80, -10, 0)), (P(0, -6, -6), R(-70, 0, 0)), (P(0, -10, -3), R(-90, 0, 0)), (V(-3, 0, 0), V(6, 0, 0)), weight="heavy")
swing("axe_hack", "FP Diagonal Hack", AX + " && q.combo == 1" + GROUND, 200, 0.7, 0.24, 0.34, 0.48,
      (P(8, 10, 3), R(60, -40, -30)), (P(-4, -4, -6), R(-40, 30, 30)), (P(-9, -8, -2), R(-60, 50, 40)), (V(-2, -2, -2), V(4, 3, 3)), weight="heavy")
swing("axe_cleave", "FP Horizontal Cleave", AX + " && q.combo == 2" + GROUND, 200, 0.8, 0.28, 0.4, 0.56,
      (P(12, 2, 3), R(10, -80, -20)), (P(-8, -1, -6), R(-6, 60, 20)), (P(-14, -2, -2), R(-10, 100, 30)), (V(0, -4, -2), V(2, 6, 3)), weight="heavy")
swing("axe_heavy_overhead", "FP Heavy Overhead Split", AX + " && q.combo == 0" + GROUND + STRONG, 205, 0.95, 0.36, 0.48, 0.64,
      (P(-2, 16, 6), R(100, 0, 0)), (P(-1, -10, -6), R(-90, 0, 0)), (P(-1, -14, -2), R(-110, 0, 0)), (V(-7, 0, 0), V(12, 0, 0)), weight="heavy", off=(P(4, 16, 6), P(3, -10, -6)))
swing("axe_two_hand_sweep", "FP Two-Handed Sweep", AX + " && q.combo == 1 && q.off_hand == 'empty'" + GROUND + STRONG, 206, 1.0, 0.36, 0.5, 0.7,
      (P(14, 0, 4), R(0, -90, -20)), (P(-6, -2, -7), R(-6, 40, 10)), (P(-16, -3, -2), R(-10, 110, 20)), (V(0, -8, -4), V(2, 14, 4)), weight="heavy", off=(P(10, 0, 4), P(-10, -2, -6)))
swing("axe_hook", "FP Hooking Pull", AX + " && q.combo == 2" + GROUND + STRONG, 206, 0.8, 0.22, 0.32, 0.52,
      (P(0, 2, -8), R(0, 0, 30)), (P(2, 0, 4), R(20, -20, 60)), (P(4, -2, 8), R(30, -30, 70)), (V(0, 0, 0), V(-3, 2, 0)))
swing("axe_running_chop", "FP Running Chop", AX + " && q.is_sprinting", 210, 0.6, 0.16, 0.26, 0.4,
      (P(4, 10, 2), R(70, -20, -10)), (P(0, -6, -6), R(-60, 0, 0)), (P(0, -9, -3), R(-80, 0, 0)), (V(-2, 0, 0), V(6, 0, 0)), weight="heavy")
swing("axe_jump_chop", "FP Leaping Chop", AX + AIRB, 212, 0.65, 0.16, 0.26, 0.38,
      (P(0, 14, 5), R(95, 0, 0)), (P(0, -10, -6), R(-95, 0, 0)), (P(0, -13, -3), R(-110, 0, 0)), (V(-6, 0, 0), V(11, 0, 0)), weight="heavy", off=(P(-5, 14, 5), P(-4, -10, -6)))
swing("axe_meteor", "FP Somersault Crash", AX + AIRB + " && q.fall_distance > 4", 214, 0.9, 0.3, 0.42, 0.62,
      (P(0, 6, 6), R(60, 0, 0)), (P(0, -12, -5), R(-100, 0, 0)), (P(0, -14, -2), R(-115, 0, 0)), (V(-40, 0, 0), V(16, 0, 0)), weight="heavy")
swing("axe_board_chop", "FP Axe-And-Shield Chop", AX + " && q.off_hand == 'shield'" + GROUND, 203, 0.7, 0.24, 0.34, 0.48,
      (P(4, 10, 3), R(70, -20, -10)), (P(-2, -5, -6), R(-55, 10, 0)), (P(-3, -8, -2), R(-75, 10, 0)), off=(P(0, 0, -2), P(1, 2, -3)), weight="heavy")
swing("axe_haft_jab", "FP Haft Jab", AX + " && q.is_sneaking" + WEAK, 206, 0.45, 0.1, 0.18, 0.28,
      (P(1, -1, 4), R(-20, 0, 0)), (P(0, -1, -7), R(-24, 0, 0)), (P(0, -1, -6), R(-24, 0, 0)), weight="light")
swing("axe_berserk", "FP Berserk Flurry", AX + " && q.health < 0.25", 215, 0.75, 0.15, 0.25, 0.5,
      (P(9, 10, 2), R(60, -50, -30)), (P(-6, -6, -6), R(-60, 40, 30)), (P(6, 8, 0), R(60, -30, -20)), (V(-2, -4, -6), V(5, 6, 8)), weight="heavy")
swing("axe_swipe_air", "FP Axe Air Swing", AX + " && !q.is_mining", 150, 0.6, 0.2, 0.3, 0.42,
      (P(4, 8, 2), R(50, -20, 0)), (P(0, -3, -5), R(-40, 0, 0)), (P(0, -6, -2), R(-60, 0, 0)), ev="swing")
swing("axe_guard_breaker", "FP Guard-Breaking Wrench", AX, 216, 0.8, 0.1, 0.2, 0.55,
      (P(0, 0, -6), R(0, 0, 0)), (P(4, 2, 4), R(30, -40, 70)), (P(6, 2, 8), R(40, -50, 80)), (V(0, 0, 0), V(-4, 4, 6)), ev="break_guard")
swing("axe_weak_tap", "FP Uncharged Axe Tap", AX + " && q.attack_strength < 0.3", 199, 0.4, 0.1, 0.16, 0.24,
      (P(1, 3, 1), R(20, 0, 0)), (P(0, -1, -3), R(-10, 0, 0)), (P(0, -1, -2), R(-10, 0, 0)), weight="light")
swing("axe_whirlwind", "FP Whirlwind Spin", AX + " && q.is_sprinting && q.combo == 2", 217, 0.9, 0.2, 0.45, 0.7,
      (P(-10, 2, 3), R(10, 70, 10)), (P(10, 0, -4), R(0, -70, -10)), (P(14, -2, 0), R(-10, -110, -10)), (V(0, 14, 4), V(1, -40, -4)), weight="heavy")

# -------------------------------------------------------------------------- trident
swing("trident_quick", "FP Quick Thrust", TR + " && q.combo == 0" + GROUND, 200, 0.45, 0.12, 0.2, 0.3,
      (P(2, 0, 5), R(4, -4, 0)), (P(0, 0, -9), R(-2, 0, 0)), (P(0, 0, -8), R(-2, 0, 0)), weight="light", off=(P(-2, -1, 3), P(-1, -1, -5)))
swing("trident_double", "FP Double Thrust", TR + " && q.combo == 1" + GROUND, 200, 0.6, 0.1, 0.18, 0.42,
      (P(2, 0, 4), R(4, -4, 0)), (P(0, 0, -9), R(-2, 0, 0)), (P(1, 0, 2), R(2, -2, 0)), weight="light")
swing("trident_haft_sweep", "FP Haft Sweep", TR + " && q.combo == 2" + GROUND, 200, 0.7, 0.22, 0.34, 0.48,
      (P(12, -2, 2), R(-10, -70, -30)), (P(-8, -2, -5), R(0, 50, 30)), (P(-13, -3, -1), R(0, 80, 40)), (V(0, -4, -2), V(1, 6, 3)))
swing("trident_heavy_lunge", "FP Impaling Lunge", TR + GROUND + STRONG, 205, 0.8, 0.3, 0.4, 0.55,
      (P(3, -1, 8), R(6, -8, 0)), (P(0, 0, -13), R(-4, 0, 0)), (P(0, -1, -12), R(-4, 0, 0)), (V(-1, 0, 0), V(4, 0, 0)), weight="heavy", off=(P(-2, -1, 6), P(-1, -1, -9)))
swing("trident_running", "FP Running Impale", TR + " && q.is_sprinting", 210, 0.6, 0.15, 0.25, 0.4,
      (P(2, -1, 6), R(4, -6, 0)), (P(0, 0, -12), R(-4, 0, 0)), (P(0, -1, -11), R(-4, 0, 0)), (V(0, 0, 0), V(4, 0, 0)), weight="heavy")
swing("trident_plunge", "FP Reverse-Grip Plunge", TR + AIRB, 212, 0.6, 0.14, 0.24, 0.36,
      (P(2, 10, 4), R(90, 0, 60)), (P(0, -12, -4), R(-60, 0, 60)), (P(0, -14, -2), R(-80, 0, 60)), (V(-4, 0, 0), V(10, 0, 0)), weight="heavy")
swing("trident_sneak_jab", "FP Low Jab", TR + " && q.is_sneaking", 206, 0.4, 0.1, 0.17, 0.26,
      (P(1, -3, 3), R(-14, 0, 0)), (P(0, -4, -7), R(-18, 0, 0)), (P(0, -4, -6), R(-18, 0, 0)), weight="light")
swing("trident_feint", "FP Trident Feint", TR + " && !q.is_mining", 150, 0.45, 0.12, 0.2, 0.3,
      (P(1, 0, 3), R(4, 0, 0)), (P(0, 0, -5), R(0, 0, 0)), (P(0, 0, -4), R(0, 0, 0)), ev="swing", weight="light")
swing("trident_butt", "FP Butt Strike", TR + " && q.attack_strength < 0.3", 199, 0.45, 0.1, 0.18, 0.28,
      (P(0, 0, -3), R(0, 0, 0)), (P(-2, 0, 6), R(0, 20, -20)), (P(-2, 0, 5), R(0, 20, -20)), weight="light")

# -------------------------------------------------------------------------- fists
swing("fist_jab", "FP Jab", FI + " && q.combo == 0", 200, 0.35, 0.08, 0.13, 0.2,
      (P(0, 0, 2), R(0, 0, 0)), (P(-2, 1, -8), R(6, 10, 0)), (P(-2, 1, -7), R(6, 10, 0)), weight="light")
swing("fist_cross", "FP Cross", FI + " && q.combo == 1", 200, 0.42, 0.1, 0.16, 0.24,
      (P(2, -1, 3), R(0, -10, 0)), (P(-5, 1, -9), R(6, 20, 10)), (P(-5, 1, -8), R(6, 20, 10)), (V(0, 0, 0), V(1, 2, 2)))
swing("fist_hook", "FP Hook", FI + " && q.combo == 2", 200, 0.5, 0.14, 0.22, 0.32,
      (P(8, 0, 1), R(0, -60, -50)), (P(-6, 1, -6), R(0, 40, -80)), (P(-10, 0, -4), R(0, 60, -80)), (V(0, -2, -2), V(1, 4, 3)))
swing("fist_uppercut", "FP Uppercut", FI + " && q.combo == 0" + STRONG, 205, 0.55, 0.18, 0.26, 0.36,
      (P(1, -8, 2), R(-40, 0, -40)), (P(-1, 8, -6), R(50, 0, -40)), (P(-1, 11, -5), R(70, 0, -40)), (V(3, 0, 0), V(-4, 0, 0)))
swing("fist_haymaker", "FP Haymaker", FI + " && q.combo == 2" + STRONG, 206, 0.7, 0.26, 0.36, 0.5,
      (P(12, 2, 4), R(10, -80, -30)), (P(-8, 1, -8), R(0, 50, -20)), (P(-12, -1, -5), R(0, 80, -20)), (V(0, -4, -3), V(2, 8, 4)), weight="heavy")
swing("fist_body_blow", "FP Body Blow", FI + " && q.is_sneaking" + WEAK, 206, 0.42, 0.1, 0.17, 0.26,
      (P(1, -4, 2), R(-20, 0, 0)), (P(-1, -5, -7), R(-24, 10, 0)), (P(-1, -5, -6), R(-24, 10, 0)), weight="light")
swing("fist_running_punch", "FP Running Punch", FI + " && q.is_sprinting", 210, 0.45, 0.1, 0.18, 0.28,
      (P(1, -1, 4), R(0, -6, 0)), (P(-2, 1, -11), R(6, 10, 0)), (P(-2, 1, -10), R(6, 10, 0)), (V(0, 0, 0), V(2, 0, 0)))
swing("fist_superman", "FP Leaping Punch", FI + AIRB, 212, 0.55, 0.12, 0.22, 0.34,
      (P(1, 4, 4), R(10, 0, 0)), (P(-1, 2, -12), R(10, 6, 0)), (P(-1, 1, -11), R(10, 6, 0)), (V(-2, 0, 0), V(4, 0, 0)))
swing("fist_elbow", "FP Elbow Strike", FI + " && q.is_sneaking" + STRONG, 207, 0.45, 0.14, 0.2, 0.3,
      (P(8, 0, 4), R(0, -70, -90)), (P(-4, 0, -2), R(0, 30, -90)), (P(-8, 0, -1), R(0, 50, -90)), (V(0, -3, -2), V(1, 5, 3)))
swing("fist_push_kick", "FP Push Kick", FI + " && q.is_sneaking && q.combo == 2", 208, 0.7, 0.22, 0.32, 0.46,
      (P(4, 4, 4), R(10, 0, 0)), (P(4, 6, 6), R(14, 0, 0)), (P(4, 5, 5), R(12, 0, 0)), (V(-8, 0, 0), V(-14, 0, 0)), off=(P(-4, 4, 4), P(-4, 6, 6)))
swing("fist_spin_kick", "FP Spinning Back Kick", FI + " && q.combo == 2 && q.trait_energy > 0.6" + STRONG, 209, 1.0, 0.25, 0.5, 0.7,
      (P(6, 2, 4), R(0, 0, 0)), (P(10, 6, 6), R(0, -40, 0)), (P(8, 4, 4), R(0, -30, 0)), (V(0, -60, 0), V(-6, -200, -6)))
swing("fist_ground_pound", "FP Ground Pound", FI + AIRB + " && q.fall_distance > 4", 214, 0.75, 0.1, 0.2, 0.5,
      (P(0, 12, 4), R(70, 0, 0)), (P(0, -14, -4), R(-70, 0, 0)), (P(0, -15, -2), R(-75, 0, 0)), (V(-6, 0, 0), V(16, 0, 0)), weight="heavy", off=(P(-6, 12, 4), P(-6, -14, -4)))
swing("fist_slap", "FP Slap", FI + " && q.attack_strength < 0.3", 199, 0.35, 0.08, 0.14, 0.22,
      (P(6, 2, 1), R(0, -40, 30)), (P(-4, 1, -4), R(0, 30, 10)), (P(-7, 0, -3), R(0, 40, 10)), weight="light")
swing("fist_punch_air", "FP Shadow Punch", FI + " && !q.is_mining", 150, 0.3, 0.06, 0.11, 0.18,
      (P(0, 0, 1), R(0, 0, 0)), (P(-1, 1, -6), R(4, 6, 0)), (P(-1, 1, -5), R(4, 6, 0)), ev="swing", weight="light")

# -------------------------------------------------------------------------- tools as weapons and counters
swing("pickaxe_strike", "FP Pickaxe Strike", W("pickaxe"), 190, 0.6, 0.2, 0.3, 0.42,
      (P(2, 10, 3), R(70, -10, 0)), (P(0, -5, -6), R(-55, 0, 0)), (P(0, -8, -3), R(-75, 0, 0)))
swing("pickaxe_heavy", "FP Pickaxe Spike Blow", W("pickaxe") + STRONG, 195, 0.8, 0.3, 0.4, 0.56,
      (P(6, 12, 6), R(70, -30, 40)), (P(-3, -7, -8), R(-60, 20, 40)), (P(-5, -10, -4), R(-80, 30, 40)), (V(-3, -2, 3), V(7, 3, -3)), weight="heavy", off=(P(0, -4, 2), P(0, -5, 1)))
swing("shovel_smack", "FP Shovel Smack", W("shovel"), 190, 0.6, 0.2, 0.3, 0.42,
      (P(10, 3, 2), R(10, -70, -60)), (P(-6, 0, -5), R(0, 40, -60)), (P(-10, -1, -2), R(0, 60, -60)))
swing("shovel_jab", "FP Shovel Jab", W("shovel") + STRONG, 195, 0.55, 0.18, 0.26, 0.38,
      (P(1, -2, 6), R(-10, 0, 0)), (P(0, -2, -11), R(-12, 0, 0)), (P(0, -3, -10), R(-12, 0, 0)), off=(P(-4, -2, 6), P(-3, -2, -10)))
swing("hoe_sweep", "FP Hoe Sweep", W("hoe"), 190, 0.65, 0.2, 0.32, 0.46,
      (P(12, -2, 2), R(-10, -80, -10)), (P(-8, -3, -5), R(-20, 50, 0)), (P(-13, -4, -1), R(-24, 80, 0)), (V(2, -3, -2), V(4, 5, 3)))
swing("hoe_hook", "FP Hoe Hook Trip", W("hoe") + STRONG, 195, 0.75, 0.24, 0.34, 0.5,
      (P(0, 6, -6), R(40, 0, 0)), (P(0, -6, 4), R(-40, 0, 20)), (P(0, -8, 8), R(-50, 0, 30)), (V(0, 0, 0), V(6, 0, 0)))
for w, label, wind, imp, fol in (("sword", "FP Riposte", (P(4, 2, 2), R(10, -20, 0)), (P(0, 0, -12), R(-4, 0, 0)), (P(0, -1, -11), R(-4, 0, 0))),
                                 ("axe", "FP Counter Cleave", (P(2, 12, 4), R(80, 0, 0)), (P(0, -9, -6), R(-80, 0, 0)), (P(0, -12, -3), R(-95, 0, 0))),
                                 ("empty", "FP Counter One-Two", (P(0, 0, 2), R(0, 0, 0)), (P(-3, 1, -9), R(6, 14, 0)), (P(4, 0, 2), R(0, -10, 0))),
                                 ("trident", "FP Counter Spear Spin", (P(-8, 0, 2), R(0, 60, 0)), (P(8, 0, -6), R(0, -60, 0)), (P(10, -1, -2), R(0, -90, 0)))):
    swing("counter_" + w, label, ALIVE + " && q.main_hand == '%s'" % w, 255, 0.6, 0.06, 0.16, 0.32, wind, imp, fol, (V(0, 0, 0), V(3, 0, 0)), ev="counter",
          weight="heavy", file="first_person/defense")

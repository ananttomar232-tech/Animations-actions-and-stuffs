"""Player combat and weapon handling (category: player_combat)."""
from core import Clip, state, event, arm, leg, tilt, move, biped, strike, shake, wave, cwave

CAT = "player_combat"
T = "@player"
CYCLE = 9.4248
ALIVE = "!q.is_dead && !q.is_sleeping && !q.is_swimming"
Z = (0, 0, 0)

LIGHT, MEDIUM, HEAVY = "light", "medium", "heavy"


def melee(cid, name, when, pri, L, wind, imp, fol, rarm, body=(Z, Z, Z), root=(Z, Z), larm=None, head=None, legs=None,
          weight=MEDIUM, ev="attack", trail=True, spin=0.0, root_rot=None, two_hand=False, file="player/combat_melee", hit_t=None):
    """rarm: (windup, impact, follow) as arm() argument tuples. body: tilt() args at windup/impact/follow.
    root: move() args at windup and impact (weight shift / step). larm: off-hand (windup, impact) arm() args."""
    c = Clip("player.combat." + cid, name, CAT, T, length=L, loop="once", layer="action", priority=pri,
             trigger=event(ev, when), blend_in=0.06, blend_out=0.2, interrupt_after=min(0.9, fol / L + 0.05),
             mask=None if legs or spin or root_rot else ["head", "body", "right_arm", "left_arm", "mw_root", "mw_center"], file=file)
    tw, ti, tf = wind, imp, fol
    strike(c, "right_arm", Z, arm('r', *rarm[0]), arm('r', *rarm[1]), arm('r', *rarm[2]), tw, ti, tf, L)
    strike(c, "body", Z, tilt(*body[0]), tilt(*body[1]), tilt(*body[2]), tw, ti, tf, L)
    c.pos("mw_root", (0, Z), (tw, move(*root[0]), "out_quad"), (ti, move(*root[1]), "in_quart"), (L, Z, "in_out_sine"))
    if larm or two_hand:
        la = larm or (rarm[0], rarm[1])
        c.rot("left_arm", (0, Z), (tw, arm('l', *la[0]), "out_quad"), (ti, arm('l', *la[1]), "in_quart"), (L, Z, "in_out_sine"))
    else:
        c.rot("left_arm", (0, Z), (tw, arm('l', 20, 18)), (ti, arm('l', -24, 14)), (L, Z, "in_out_sine"))
    hd = head or ((tilt(0, body[0][1] * -0.5 if len(body[0]) > 1 else 0)), tilt(4, 0), tilt(2, 0))
    c.rot("head", (0, Z), (tw, hd[0]), (ti, hd[1]), (L, Z, "in_out_sine"))
    if legs:
        c.rot("right_leg", (0, Z), (tw, leg('r', *legs[0])), (ti, leg('r', *legs[1])), (L, Z, "in_out_sine"))
        c.rot("left_leg", (0, Z), (tw, leg('l', *legs[2])), (ti, leg('l', *legs[3])), (L, Z, "in_out_sine"))
    if spin:
        c.rot("mw_root", (0, Z), (tw, tilt(0, -spin * 0.15)), (ti, tilt(0, spin * 0.6), "in_quart"), (tf, tilt(0, spin), "out_quad"), (L, tilt(0, spin)))
    elif root_rot:
        c.rot("mw_root", (0, Z), (tw, tilt(*root_rot[0])), (ti, tilt(*root_rot[1]), "in_quart"), (L, Z, "in_out_sine"))
    c.ev(max(0.0, tw - 0.02), "whoosh", weight=weight)
    if trail:
        c.ev(tw, "trail", state="start").ev(tf, "trail", state="stop")
    c.ev(hit_t if hit_t is not None else ti, "impact", strength={"light": "0.4", "medium": "0.7", "heavy": "1.0"}[weight])
    c.ev(tw, "foley", kind="armor", volume=0.5)
    c.tag(replaces_vanilla_swing="true")
    return c


def W(cat):
    return ALIVE + " && q.main_hand == '%s'" % cat


SW = W("sword")
GROUND = " && q.is_on_ground"
AIRB = " && !q.is_on_ground && q.vertical_speed < 0"
STRONG = " && q.attack_strength >= 0.9"
WEAK = " && q.attack_strength < 0.9"

# --------------------------------------------------------------------------------- sword
melee("sword_slash_forehand", "Forehand Slash", SW + " && q.combo == 0" + GROUND, 200, 0.55, 0.16, 0.26, 0.38,
      ((60, 70, -20), (90, -20, 0), (70, -60, 20)), (tilt(4, 28), tilt(6, -18), tilt(4, -32)), (move(0, 0, -0.5), move(0, -0.4, 1.2)))
melee("sword_slash_backhand", "Backhand Return Slash", SW + " && q.combo == 1" + GROUND, 200, 0.55, 0.15, 0.25, 0.37,
      ((80, -70, 30), (92, 10, 0), (70, 70, -20)), (tilt(4, -30), tilt(6, 16), tilt(4, 30)), (move(0, 0, 0), move(0, -0.4, 1.0)))
melee("sword_overhead_finisher", "Overhead Finisher", SW + " && q.combo == 2" + GROUND, 200, 0.7, 0.22, 0.33, 0.46,
      ((170, 10, 0), (72, 0, 0), (22, -10, 0)), (tilt(-10, 6), tilt(20, 0), tilt(24, -4)), (move(0, 0.4, -0.5), move(0, -1.4, 2.0)), weight=HEAVY,
      legs=((0, 0), (-24, 4), (0, 0), (30, 4)))
melee("sword_rising_power", "Rising Power Slash", SW + " && q.combo == 0" + GROUND + STRONG, 205, 0.75, 0.28, 0.38, 0.52,
      ((-20, 40, 0), (110, -10, 0), (160, -40, 10)), (tilt(16, 30), tilt(-8, -10), tilt(-12, -24)), (move(0, -1.2, -0.5), move(0, 0.6, 1.4)), weight=HEAVY,
      legs=((30, 4), (-10, 4), (-20, 4), (20, 4)))
melee("sword_sweeping_spin", "Sweeping Spin Slash", SW + " && q.combo == 2" + GROUND + STRONG, 206, 0.95, 0.25, 0.45, 0.7,
      ((70, 80, -10), (90, 60, 0), (80, 50, 0)), (tilt(6, 20), tilt(8, 0), tilt(6, 0)), (move(0, -0.8, 0), move(0, -1.2, 0.5)), weight=HEAVY, spin=360)
melee("sword_lunge_thrust", "Lunging Thrust", SW + " && q.is_sneaking" + STRONG, 207, 0.65, 0.24, 0.32, 0.44,
      ((40, 10, 0), (96, -4, 0), (92, -4, 0)), (tilt(4, 26), tilt(14, -14), tilt(14, -12)), (move(0, -0.6, -2.0), move(0, -1.6, 4.0)),
      legs=((-10, 2), (-40, 2), (10, 2), (34, 2)))
melee("sword_running_slash", "Running Slash", SW + " && q.is_sprinting", 210, 0.5, 0.12, 0.2, 0.32,
      ((50, 80, -20), (86, -10, 0), (60, -70, 20)), (tilt(14, 24), tilt(18, -20), tilt(16, -30)), (move(0, -0.6, 0), move(0, -0.8, 1.0)), weight=MEDIUM)
melee("sword_sprint_lunge", "Charging Lunge", SW + " && q.is_sprinting" + STRONG, 211, 0.7, 0.18, 0.28, 0.42,
      ((30, 20, 0), (100, 0, 0), (96, -6, 0)), (tilt(10, 20), tilt(26, -10), tilt(24, -8)), (move(0, -0.8, 0), move(0, -2.0, 4.5)), weight=HEAVY,
      legs=((-20, 2), (-50, 2), (20, 2), (40, 2)))
melee("sword_jump_cleave", "Leaping Cleave", SW + AIRB, 212, 0.6, 0.15, 0.25, 0.36,
      ((175, 0, 0), (40, 0, 0), (10, 0, 0)), (tilt(-14), tilt(28), tilt(30)), (move(0, 0.6), move(0, -1.0, 1.0)), weight=HEAVY, two_hand=True,
      root_rot=(tilt(-8), tilt(14)))
melee("sword_critical_flourish", "Critical Flourish", SW + AIRB + STRONG, 213, 0.75, 0.18, 0.3, 0.45,
      ((150, 60, -30), (60, -30, 20), (20, -60, 40)), (tilt(-12, 30), tilt(30, -20), tilt(26, -30)), (move(0, 0.6), move(0, -1.6, 1.5)), weight=HEAVY,
      root_rot=(tilt(-10, 0, 6), tilt(16, 0, -4)))
melee("sword_sneak_stab", "Sneak Stab", SW + " && q.is_sneaking" + WEAK, 206, 0.45, 0.12, 0.2, 0.3,
      ((30, 0, 0), (80, -10, 0), (78, -10, 0)), (tilt(14, 10), tilt(22, -6), tilt(22, -6)), (move(0, -0.8, -0.5), move(0, -1.0, 1.4)), weight=LIGHT)
melee("sword_board_cut", "Sword-And-Board Cut", SW + " && q.off_hand == 'shield' && q.combo == 0" + GROUND, 203, 0.55, 0.15, 0.25, 0.36,
      ((90, 40, -10), (80, -30, 10), (60, -50, 20)), (tilt(6, 16), tilt(8, -10), tilt(6, -18)), (move(0, 0, 0), move(0, -0.3, 1.0)),
      larm=((40, -20, 40), (50, -30, 40)))
melee("sword_board_chop", "Sword-And-Board Chop", SW + " && q.off_hand == 'shield' && q.combo == 1" + GROUND, 203, 0.6, 0.18, 0.28, 0.4,
      ((150, 20, 0), (60, -6, 0), (30, -10, 0)), (tilt(-4, 10), tilt(16, -4), tilt(18, -6)), (move(0, 0.2), move(0, -0.8, 1.2)),
      larm=((50, -30, 40), (56, -34, 40)))
melee("sword_board_shield_feint", "Shield Feint Thrust", SW + " && q.off_hand == 'shield' && q.combo == 2" + GROUND, 203, 0.7, 0.24, 0.36, 0.5,
      ((20, 10, 0), (94, -2, 0), (90, -4, 0)), (tilt(4, -14), tilt(12, 10), tilt(12, 8)), (move(0, 0, -0.8), move(0, -0.8, 2.6)),
      larm=((80, -10, 20), (20, 10, 0)))
melee("sword_two_hand_overhead", "Two-Handed Overhead", SW + " && q.off_hand == 'empty' && q.combo == 1" + STRONG + GROUND, 208, 0.85, 0.3, 0.42, 0.56,
      ((178, -10, 0), (60, -8, 0), (18, -12, 0)), (tilt(-14, 4), tilt(26, 0), tilt(30, 0)), (move(0, 0.8, -0.5), move(0, -2.0, 2.0)), weight=HEAVY, two_hand=True,
      legs=((0, 0), (-26, 4), (0, 0), (34, 4)))
melee("sword_pommel_strike", "Pommel Strike", SW + " && q.is_sneaking && q.attack_strength < 0.5", 209, 0.4, 0.1, 0.18, 0.26,
      ((60, -10, 60), (80, -20, 80), (76, -20, 80)), (tilt(4, 14), tilt(10, -10), tilt(10, -10)), (move(0, 0, 0), move(0, -0.2, 1.5)), weight=LIGHT, trail=False)
melee("sword_desperate_flail", "Desperate Flail", SW + " && q.health < 0.25", 215, 0.6, 0.2, 0.28, 0.38,
      ((140, 50, -40), (60, -40, 30), (40, -70, 40)), (tilt(-6, 24, 6), tilt(20, -20, -6), tilt(18, -28, -8)), (move(0, 0.2, -1.0), move(0, -1.0, 1.4)))
melee("sword_backhand_power", "Backhand Power Arc", SW + " && q.combo == 1" + GROUND + STRONG, 205, 0.75, 0.26, 0.36, 0.5,
      ((100, -80, 40), (96, 30, 0), (90, 80, -30)), (tilt(6, -40), tilt(10, 24), tilt(8, 40)), (move(0, -0.4, -0.5), move(0, -1.0, 1.4)), weight=HEAVY,
      legs=((10, 6), (-16, 6), (-6, 6), (14, 6)))
melee("sword_swipe_air", "Empty Air Swipe", SW + " && !q.is_mining", 150, 0.45, 0.1, 0.2, 0.3,
      ((40, 50, -10), (80, -30, 10), (50, -40, 10)), (tilt(2, 14), tilt(4, -10), tilt(3, -14)), (move(0, 0, 0), move(0, 0, 0.6)), weight=LIGHT, ev="swing")

# --------------------------------------------------------------------------------- axe
AX = W("axe")
melee("axe_downward_chop", "Downward Chop", AX + " && q.combo == 0" + GROUND, 200, 0.7, 0.24, 0.34, 0.48,
      ((160, 20, 0), (50, 0, 0), (10, -6, 0)), (tilt(-8, 10), tilt(22, -2), tilt(26, -4)), (move(0, 0.4), move(0, -1.2, 1.4)), weight=HEAVY)
melee("axe_diagonal_hack", "Diagonal Hack", AX + " && q.combo == 1" + GROUND, 200, 0.7, 0.24, 0.34, 0.48,
      ((140, 60, -20), (60, -30, 20), (20, -50, 30)), (tilt(-4, 30), tilt(18, -20), tilt(22, -30)), (move(0, 0.2), move(0, -1.0, 1.2)), weight=HEAVY)
melee("axe_horizontal_cleave", "Horizontal Cleave", AX + " && q.combo == 2" + GROUND, 200, 0.8, 0.28, 0.4, 0.56,
      ((70, 90, -20), (90, -10, 0), (80, -80, 20)), (tilt(4, 40), tilt(8, -20), tilt(6, -45)), (move(0, -0.4), move(0, -1.0, 1.0)), weight=HEAVY,
      legs=((10, 8), (-10, 8), (-10, 8), (14, 8)))
melee("axe_heavy_overhead", "Heavy Overhead Split", AX + " && q.combo == 0" + GROUND + STRONG, 205, 0.95, 0.36, 0.48, 0.64,
      ((180, 0, 0), (40, 0, 0), (0, 0, 0)), (tilt(-18), tilt(30), tilt(34)), (move(0, 1.0, -0.8), move(0, -2.2, 1.8)), weight=HEAVY, two_hand=True,
      legs=((0, 0), (-30, 6), (0, 0), (36, 6)))
melee("axe_two_hand_sweep", "Two-Handed Sweep", AX + " && q.combo == 1 && q.off_hand == 'empty'" + GROUND + STRONG, 206, 1.0, 0.36, 0.5, 0.7,
      ((80, 90, -30), (92, 0, 0), (84, -90, 30)), (tilt(6, 50), tilt(10, -10), tilt(8, -55)), (move(0, -1.0), move(0, -1.4, 0.8)), weight=HEAVY, two_hand=True,
      legs=((14, 10), (-14, 10), (-14, 10), (18, 10)))
melee("axe_hook_pull", "Hooking Pull", AX + " && q.combo == 2" + GROUND + STRONG, 206, 0.8, 0.22, 0.32, 0.52,
      ((96, -20, 0), (90, 20, 40), (40, 40, 60)), (tilt(10, -10), tilt(-6, 20), tilt(-14, 30)), (move(0, 0, 1.2), move(0, 0, -2.0)), weight=MEDIUM)
melee("axe_running_chop", "Running Chop", AX + " && q.is_sprinting", 210, 0.6, 0.16, 0.26, 0.4,
      ((150, 30, -10), (60, -10, 0), (20, -20, 0)), (tilt(4, 14), tilt(24, -6), tilt(26, -8)), (move(0, 0), move(0, -1.4, 1.0)), weight=HEAVY)
melee("axe_jump_chop", "Leaping Chop", AX + AIRB, 212, 0.65, 0.16, 0.26, 0.38,
      ((180, 10, 0), (30, 0, 0), (0, 0, 0)), (tilt(-20), tilt(34), tilt(36)), (move(0, 0.8), move(0, -1.4, 1.2)), weight=HEAVY, two_hand=True,
      root_rot=(tilt(-10), tilt(18)))
melee("axe_meteor_crash", "Somersault Axe Crash", AX + AIRB + " && q.fall_distance > 4", 214, 0.9, 0.3, 0.42, 0.62,
      ((120, 30, 0), (20, 10, 0), (-10, 10, 0)), (tilt(30), tilt(40), tilt(44)), (move(0, 1.0, -1.0), move(0, -3.0, 1.0)), weight=HEAVY, two_hand=True,
      root_rot=(tilt(-120), tilt(10)), legs=((60, 4), (10, 4), (60, 4), (-10, 4)))
melee("axe_board_chop", "Axe-And-Shield Chop", AX + " && q.off_hand == 'shield'" + GROUND, 203, 0.7, 0.24, 0.34, 0.48,
      ((140, 30, -10), (60, -20, 10), (30, -30, 10)), (tilt(-2, 14), tilt(18, -8), tilt(20, -12)), (move(0, 0.2), move(0, -1.0, 1.0)), weight=HEAVY,
      larm=((50, -30, 40), (56, -30, 40)))
melee("axe_pommel_jab", "Haft Jab", AX + " && q.is_sneaking" + WEAK, 206, 0.45, 0.1, 0.18, 0.28,
      ((40, -10, 0), (70, -16, 0), (68, -16, 0)), (tilt(8, 16), tilt(14, -8), tilt(14, -8)), (move(0, -0.4, -0.4), move(0, -0.6, 1.4)), weight=LIGHT, trail=False)
melee("axe_berserk_flurry", "Berserk Flurry", AX + " && q.health < 0.25", 215, 0.75, 0.15, 0.25, 0.5,
      ((150, 60, -20), (50, -40, 20), (140, -20, 0)), (tilt(-6, 30, 6), tilt(24, -24, -6), tilt(-4, -10, 4)), (move(0, 0.2, -0.5), move(0, -1.4, 1.6)), weight=HEAVY)
melee("axe_swipe_air", "Axe Swing At Air", AX + " && !q.is_mining", 150, 0.6, 0.2, 0.3, 0.42,
      ((120, 30, 0), (60, -10, 0), (30, -20, 0)), (tilt(-2, 10), tilt(12, -4), tilt(14, -6)), (move(0, 0), move(0, -0.6, 0.6)), weight=MEDIUM, ev="swing")
melee("axe_guard_breaker", "Guard-Breaking Wrench", AX, 216, 0.8, 0.1, 0.2, 0.55,
      ((60, -10, 40), (30, 30, 80), (10, 40, 80)), (tilt(10, -10), tilt(-10, 30), tilt(-14, 34)), (move(0, 0, 0.6), move(0, 0, -2.4)), weight=MEDIUM,
      ev="break_guard", trail=False)

# --------------------------------------------------------------------------------- trident
TR = W("trident")
melee("trident_quick_thrust", "Quick Thrust", TR + " && q.combo == 0" + GROUND, 200, 0.45, 0.12, 0.2, 0.3,
      ((50, 10, 0), (96, -2, 0), (92, -2, 0)), (tilt(4, 16), tilt(10, -8), tilt(10, -8)), (move(0, 0, -0.8), move(0, -0.4, 2.0)), weight=LIGHT,
      larm=((60, -30, 30), (80, -20, 20)))
melee("trident_double_thrust", "Double Thrust", TR + " && q.combo == 1" + GROUND, 200, 0.6, 0.1, 0.18, 0.42,
      ((50, 6, 0), (96, 0, 0), (60, 6, 0)), (tilt(4, 14), tilt(10, -6), tilt(6, 6)), (move(0, 0, -0.6), move(0, -0.4, 2.0)), weight=LIGHT, hit_t=0.36,
      larm=((60, -30, 30), (84, -20, 20)))
melee("trident_haft_sweep", "Haft Sweep", TR + " && q.combo == 2" + GROUND, 200, 0.7, 0.22, 0.34, 0.48,
      ((60, 80, -40), (70, -40, 30), (50, -70, 40)), (tilt(4, 30), tilt(8, -24), tilt(6, -36)), (move(0, -0.4), move(0, -0.8, 0.6)), weight=MEDIUM, two_hand=True,
      legs=((10, 8), (-10, 8), (-10, 8), (14, 8)))
melee("trident_heavy_lunge", "Impaling Lunge", TR + GROUND + STRONG, 205, 0.8, 0.3, 0.4, 0.55,
      ((30, 20, 0), (100, 0, 0), (98, 0, 0)), (tilt(6, 30), tilt(20, -14), tilt(20, -12)), (move(0, -0.8, -2.4), move(0, -1.8, 5.0)), weight=HEAVY,
      legs=((-10, 4), (-50, 4), (10, 4), (40, 4)), larm=((40, -30, 30), (90, -20, 20)))
melee("trident_running_impale", "Running Impale", TR + " && q.is_sprinting", 210, 0.6, 0.15, 0.25, 0.4,
      ((40, 10, 0), (100, 0, 0), (96, 0, 0)), (tilt(16, 14), tilt(24, -8), tilt(24, -6)), (move(0, -0.6, 0), move(0, -1.6, 3.0)), weight=HEAVY,
      larm=((50, -20, 20), (90, -14, 20)))
melee("trident_plunge_stab", "Reverse-Grip Plunging Stab", TR + AIRB, 212, 0.6, 0.14, 0.24, 0.36,
      ((110, 40, 90), (10, 0, 90), (0, -6, 90)), (tilt(-6, 20, 8), tilt(26, -6, -4), tilt(28, -8, -4)), (move(0, 0.6), move(0, -1.6, 0.4)), weight=HEAVY,
      root_rot=(tilt(-4, 0, 10), tilt(18, 0, -6)))
melee("trident_sneak_jab", "Low Jab", TR + " && q.is_sneaking", 206, 0.4, 0.1, 0.17, 0.26,
      ((20, 10, 0), (60, 0, 0), (58, 0, 0)), (tilt(16, 10), tilt(24, -4), tilt(24, -4)), (move(0, -1.0, -0.4), move(0, -1.2, 1.4)), weight=LIGHT)
melee("trident_swipe_air", "Trident Feint", TR + " && !q.is_mining", 150, 0.45, 0.12, 0.2, 0.3,
      ((60, 10, 0), (90, 0, 0), (80, 0, 0)), (tilt(2, 10), tilt(6, -4), tilt(4, -2)), (move(0, 0, -0.4), move(0, 0, 1.0)), weight=LIGHT, ev="swing")

c = Clip("player.combat.trident_throw_windup", "Trident Throw Wind-Up", CAT, T, length=1.0, loop="hold", layer="overlay", priority=150,
         trigger=state(ALIVE + " && q.is_using_item && q.use_anim == 'spear'", exit_delay=0.05), blend_in=0.2, blend_out=0.05,
         mask=["right_arm", "left_arm", "body", "head"], file="player/combat_ranged")
c.rot("right_arm", (0, arm('r', 120, 20, 0)), (0.6, arm('r', 170, 30, -10), "out_cubic"), (1.0, arm('r', 172, 32, -10)))
c.rot("left_arm", (0, arm('l', 60, 20)), (0.6, arm('l', 80, 10), "out_cubic"), (1.0, arm('l', 82, 10)))
c.rot("body", (0, tilt(0, 10)), (0.6, tilt(-6, 30), "out_cubic"), (1.0, tilt(-6, 32)))
c.rot("head", (0, Z), (0.6, tilt(0, -20)), (1.0, tilt(0, -22)))
c = Clip("player.combat.trident_throw_release", "Trident Throw Release", CAT, T, length=0.6, loop="once", layer="action", priority=220,
         trigger=event("use_stop", TR), blend_in=0.02, blend_out=0.25, file="player/combat_ranged")
strike(c, "right_arm", arm('r', 172, 32, -10), arm('r', 175, 34, -10), arm('r', 80, -10, 0), arm('r', 40, -30, 10), 0.04, 0.12, 0.28, 0.6)
strike(c, "body", tilt(-6, 32), tilt(-8, 34), tilt(22, -20), tilt(26, -26), 0.04, 0.12, 0.28, 0.6)
c.pos("mw_root", (0, Z), (0.12, move(0, -1.2, 2.0), "in_quart"), (0.6, Z))
c.rot("right_leg", (0, leg('r', -10)), (0.14, leg('r', 30)), (0.6, Z))
c.ev(0.1, "whoosh", weight="heavy")

# --------------------------------------------------------------------------------- fists
FI = W("empty")
melee("fist_jab", "Jab", FI + " && q.combo == 0", 200, 0.35, 0.08, 0.13, 0.2,
      ((70, 0, 20), (92, -4, 0), (90, -4, 0)), (tilt(2, 10), tilt(4, -10), tilt(4, -10)), (move(0, 0, 0), move(0, 0, 0.8)), weight=LIGHT, trail=False,
      larm=((70, -20, 40), (60, -20, 40)))
melee("fist_cross", "Cross", FI + " && q.combo == 1", 200, 0.42, 0.1, 0.16, 0.24,
      ((60, -10, 30), (92, -12, 0), (88, -12, 0)), (tilt(2, 24), tilt(6, -22), tilt(6, -22)), (move(0, 0, -0.4), move(0, -0.2, 1.2)), weight=MEDIUM, trail=False,
      larm=((70, -20, 40), (40, -10, 30)), legs=((0, 0), (0, 0, -16), (0, 0), (0, 0)))
melee("fist_hook", "Hook", FI + " && q.combo == 2", 200, 0.5, 0.14, 0.22, 0.32,
      ((70, 60, 40), (90, -30, 80), (80, -50, 80)), (tilt(4, 30), tilt(8, -24), tilt(6, -34)), (move(0, -0.2), move(0, -0.4, 0.8)), weight=MEDIUM, trail=False,
      larm=((70, -20, 40), (70, -20, 40)))
melee("fist_uppercut", "Uppercut", FI + " && q.combo == 0" + STRONG, 205, 0.55, 0.18, 0.26, 0.36,
      ((10, 20, 60), (150, -10, 40), (170, -10, 40)), (tilt(14, 14), tilt(-14, -10), tilt(-16, -10)), (move(0, -1.2), move(0, 0.8, 0.6)), weight=MEDIUM, trail=False,
      larm=((70, -20, 40), (70, -20, 40)))
melee("fist_haymaker", "Haymaker", FI + " && q.combo == 2" + STRONG, 206, 0.7, 0.26, 0.36, 0.5,
      ((80, 90, -20), (94, -30, 10), (70, -60, 20)), (tilt(6, 44), tilt(14, -30), tilt(14, -40)), (move(0, -0.4, -0.8), move(0, -1.0, 1.6)), weight=HEAVY, trail=False,
      legs=((0, 6), (-16, 6), (-6, 6), (14, 6)))
melee("fist_body_blow", "Body Blow", FI + " && q.is_sneaking" + WEAK, 206, 0.42, 0.1, 0.17, 0.26,
      ((30, 0, 30), (70, -6, 0), (66, -6, 0)), (tilt(16, 16), tilt(22, -10), tilt(22, -10)), (move(0, -1.0), move(0, -1.2, 1.0)), weight=LIGHT, trail=False)
melee("fist_running_punch", "Running Punch", FI + " && q.is_sprinting", 210, 0.45, 0.1, 0.18, 0.28,
      ((50, 10, 20), (96, -6, 0), (92, -6, 0)), (tilt(14, 20), tilt(20, -16), tilt(20, -14)), (move(0, -0.4), move(0, -0.6, 1.8)), weight=MEDIUM, trail=False)
melee("fist_superman_punch", "Leaping Punch", FI + AIRB, 212, 0.55, 0.12, 0.22, 0.34,
      ((40, 0, 20), (150, -4, 0), (140, -4, 0)), (tilt(-8, 20), tilt(20, -10), tilt(22, -10)), (move(0, 0.4), move(0, -1.0, 2.0)), weight=MEDIUM, trail=False,
      root_rot=(tilt(-6), tilt(12)))
melee("fist_elbow", "Elbow Strike", FI + " && q.is_sneaking" + STRONG, 207, 0.45, 0.14, 0.2, 0.3,
      ((90, 60, 90), (90, -40, 90), (90, -60, 90)), (tilt(6, 30), tilt(8, -30), tilt(8, -36)), (move(0, -0.4), move(0, -0.6, 1.2)), weight=MEDIUM, trail=False)
melee("fist_push_kick", "Push Kick", FI + " && q.is_sneaking && q.combo == 2", 208, 0.7, 0.22, 0.32, 0.46,
      ((60, -20, 30), (50, -20, 30), (50, -20, 30)), (tilt(-10), tilt(-14), tilt(-12)), (move(0, 0.4), move(0, 0.2, -0.6)), weight=MEDIUM, trail=False,
      legs=((60, 0), (88, 0), (0, 0), (-10, 0)))
melee("fist_spinning_kick", "Spinning Back Kick", FI + " && q.combo == 2 && q.trait_energy > 0.6" + STRONG, 209, 1.0, 0.25, 0.5, 0.7,
      ((60, -20, 30), (40, 30, 20), (40, 20, 20)), (tilt(-6), tilt(-16, 0, -10), tilt(-12)), (move(0, 0.4), move(0, 0.4)), weight=HEAVY, trail=False,
      legs=((-20, 10), (-80, 30), (10, 0), (10, 0)), spin=360)
melee("fist_ground_pound", "Ground Pound", FI + AIRB + " && q.fall_distance > 4", 214, 0.75, 0.1, 0.2, 0.5,
      ((170, 10, 0), (40, 10, 0), (30, 10, 0)), (tilt(-10), tilt(34), tilt(36)), (move(0, 0.6), move(0, -3.0)), weight=HEAVY, trail=False, two_hand=True)
melee("fist_slap", "Weak Slap", FI + " && q.attack_strength < 0.3", 199, 0.35, 0.08, 0.14, 0.22,
      ((70, 40, -30), (80, -20, 10), (74, -30, 10)), (tilt(2, 10), tilt(2, -8), tilt(2, -10)), (move(0, 0), move(0, 0, 0.3)), weight=LIGHT, trail=False)
melee("fist_punch_air", "Shadow Punch", FI + " && !q.is_mining", 150, 0.3, 0.06, 0.11, 0.18,
      ((70, 0, 20), (90, -4, 0), (86, -4, 0)), (tilt(1, 8), tilt(2, -8), tilt(2, -8)), (move(0, 0), move(0, 0, 0.5)), weight=LIGHT, trail=False, ev="swing")

# --------------------------------------------------------------------------------- tools as weapons and weak attacks
melee("pickaxe_strike", "Pickaxe Strike", W("pickaxe"), 190, 0.6, 0.2, 0.3, 0.42,
      ((150, 10, 0), (60, -4, 0), (30, -6, 0)), (tilt(-4, 8), tilt(16, -2), tilt(18, -2)), (move(0, 0.2), move(0, -0.8, 1.0)), weight=MEDIUM)
melee("pickaxe_heavy", "Pickaxe Spike Blow", W("pickaxe") + STRONG, 195, 0.8, 0.3, 0.4, 0.56,
      ((178, 0, 0), (50, 0, 0), (20, 0, 0)), (tilt(-12), tilt(24), tilt(26)), (move(0, 0.6), move(0, -1.6, 1.4)), weight=HEAVY, two_hand=True)
melee("shovel_smack", "Shovel Smack", W("shovel"), 190, 0.6, 0.2, 0.3, 0.42,
      ((80, 80, -60), (90, -10, -60), (70, -50, -60)), (tilt(2, 30), tilt(6, -16), tilt(4, -24)), (move(0, 0), move(0, -0.4, 0.6)), weight=MEDIUM)
melee("shovel_jab", "Shovel Jab", W("shovel") + STRONG, 195, 0.55, 0.18, 0.26, 0.38,
      ((40, -10, 0), (90, -10, 0), (86, -10, 0)), (tilt(10, 16), tilt(16, -10), tilt(16, -10)), (move(0, -0.6, -1.0), move(0, -1.0, 2.4)), weight=MEDIUM, two_hand=True)
melee("hoe_sweep", "Hoe Sweep", W("hoe"), 190, 0.65, 0.2, 0.32, 0.46,
      ((60, 90, -10), (80, -20, 0), (60, -70, 10)), (tilt(10, 30), tilt(16, -20), tilt(14, -30)), (move(0, -0.6), move(0, -1.0, 0.6)), weight=MEDIUM,
      legs=((10, 8), (-6, 8), (-6, 8), (12, 8)))
melee("hoe_hook_trip", "Hoe Hook Trip", W("hoe") + STRONG, 195, 0.75, 0.24, 0.34, 0.5,
      ((100, -10, 0), (40, 10, 30), (10, 20, 40)), (tilt(10, -6), tilt(24, 10), tilt(26, 16)), (move(0, -0.4, 1.0), move(0, -1.4, -1.6)), weight=MEDIUM)
melee("sword_weak_poke", "Sword Poke (Uncharged)", SW + " && q.attack_strength < 0.3", 199, 0.35, 0.08, 0.14, 0.22,
      ((60, 6, 0), (84, -2, 0), (80, -2, 0)), (tilt(1, 6), tilt(2, -4), tilt(2, -4)), (move(0, 0), move(0, 0, 0.6)), weight=LIGHT, trail=False)
melee("axe_weak_tap", "Axe Tap (Uncharged)", AX + " && q.attack_strength < 0.3", 199, 0.4, 0.1, 0.16, 0.24,
      ((100, 10, 0), (70, -2, 0), (66, -2, 0)), (tilt(-2, 4), tilt(6, -2), tilt(6, -2)), (move(0, 0), move(0, -0.2, 0.4)), weight=LIGHT, trail=False)
melee("trident_butt_tap", "Trident Butt Strike (Uncharged)", TR + " && q.attack_strength < 0.3", 199, 0.45, 0.1, 0.18, 0.28,
      ((70, 10, 0), (20, 30, -40), (16, 30, -40)), (tilt(2, -10), tilt(-4, 24), tilt(-4, 26)), (move(0, 0, 0.4), move(0, 0, -1.2)), weight=LIGHT, trail=False)
melee("sword_plunging_strike", "Plunging Sword Strike", SW + AIRB + " && q.fall_distance > 4", 214, 0.7, 0.1, 0.2, 0.45,
      ((175, 0, 0), (10, 0, 0), (-6, 0, 0)), (tilt(-20), tilt(36), tilt(40)), (move(0, 0.8), move(0, -2.6, 0.6)), weight=HEAVY, two_hand=True, root_rot=(tilt(-4), tilt(22)))

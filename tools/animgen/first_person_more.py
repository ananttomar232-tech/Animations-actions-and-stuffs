"""First-person part 2: ranged, shields, weapon handling, evasion, movement, mining, consuming, interacting, damage."""
from core import Clip, state, event, strike, shake, wave, cwave
from first_person import CAT, T, Z, ALIVE, P, R, V, fp, swing, W

BONE = {"main": "fp_main", "off": "fp_off", "item": "fp_main_item", "offitem": "fp_off_item", "view": "fp_view"}


def fpk(cid, name, trig, L, tracks, pri=180, layer="action", replaces=False, file="first_person/handling", loop="once", events=(), blend_in=0.06, blend_out=0.2):
    """tracks: {"main:pos": [(t, P(...), ease?)...], "main:rot": [...], "view": [...]}"""
    c = fp(cid, name, trig, L, pri=pri, layer=layer, replaces=replaces, file=file, loop=loop, blend_in=blend_in, blend_out=blend_out)
    for key, seq in tracks.items():
        part, _, ch = key.partition(":")
        c.keys(BONE[part], "position" if ch == "pos" else "rotation", seq, lerp="smooth")
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


def fpl(cid, name, when, L, fns, pri=150, layer="overlay", file="first_person/states", exit_delay=0.05, group=None, weight=1, replaces=False):
    """Looping first-person state: fns {"main:pos": f(u) -> vec, ...}."""
    c = Clip("fp." + cid, name, CAT, T, length=L, loop="loop", layer=layer, priority=pri, trigger=state(when, exit_delay=exit_delay, group=group, weight=weight),
             blend_in=0.15, blend_out=0.2, file=file, rig="first_person")
    if replaces:
        c.tag(replaces_vanilla_swing="true")
    for key, fn in fns.items():
        part, _, ch = key.partition(":")
        c.cycle(BONE[part], "position" if ch == "pos" else "rotation", fn)
    return c


FR, FD = "first_person/ranged", "first_person/defense"
BOW, XB, TR = W("bow"), W("crossbow"), W("trident")

# -------------------------------------------------------------------------- bow
fpk("bow_nock", "FP Nock Arrow", event("use_start", BOW), 0.35, {"off:pos": [(0, Z), (0.18, P(2, -3, 2)), (0.35, Z)], "off:rot": [(0, Z), (0.18, R(-10, -20, 0)), (0.35, Z)],
                                                                "main:pos": [(0, Z), (0.35, P(-1, 0, 1))]}, file=FR)
c = fp("bow_draw", "FP Draw Bowstring", state(BOW + " && q.is_using_item && q.use_time < 1.0", exit_delay=0.02), 1.0, pri=150, layer="overlay", replaces=False, file=FR, loop="hold")
c.key("fp_main", "position", 0, ["q.use_time * 1.5", 0, "q.use_time * 2"]).key("fp_off", "position", 0, ["q.use_time * 1.0", "q.use_time * -0.5", "q.use_time * 1.5"])
c.key("fp_view", "rotation", 0, [0, 0, "q.use_time * -1.5"])
fpl("bow_full_hold", "FP Full Draw Steady", BOW + " && q.is_using_item && q.use_time >= 1.0 && q.use_time < 3", 1.2, {
    "main:pos": lambda u: P(1.5, 0.15 * wave(u, 0, 3), 2), "off:pos": lambda u: P(1, -0.5 + 0.1 * wave(u, 0.3, 3), 1.5), "view:rot": lambda u: V(0, 0, -1.5)}, pri=151, file=FR)
fpl("bow_overdraw", "FP Overdrawn Shake", BOW + " && q.is_using_item && q.use_time >= 3", 0.3, {
    "main:pos": lambda u: P(1.2 + 0.5 * wave(u), -0.8 + 0.4 * wave(u, 0.3), 1.6), "off:pos": lambda u: P(0.8 + 0.5 * wave(u, 0.5), -1.6 + 0.4 * wave(u, 0.7), 1.2),
    "off:rot": lambda u: R(-6, 0, 2 * wave(u)), "view:rot": lambda u: V(1, 0, -1 + 0.6 * wave(u))}, pri=152, file=FR)
fpk("bow_release", "FP Loose Arrow", event("use_stop", BOW + " && q.last_use_time >= 0.5"), 0.45, {
    "main:pos": [(0, P(1.5, 0, 2)), (0.05, P(4, 1, 5), "out_expo"), (0.45, Z)], "off:pos": [(0, P(1, -0.5, 1.5)), (0.08, P(1, 0.5, -1), "out_back"), (0.45, Z)],
    "off:rot": [(0, Z), (0.08, R(8, 0, 0)), (0.45, Z)], "view": [(0, V(0, 0, -1.5)), (0.06, V(-1.5, 0, 0)), (0.45, Z)]}, pri=200, file=FR)
fpk("bow_quick_release", "FP Snap Shot", event("use_stop", BOW + " && q.last_use_time >= 0.15 && q.last_use_time < 0.5"), 0.35, {
    "main:pos": [(0, P(0.6, 0, 1)), (0.04, P(3, 0.5, 3), "out_expo"), (0.35, Z)], "off:rot": [(0, Z), (0.06, R(5, 4, 0)), (0.35, Z)], "view": [(0, Z), (0.05, V(-0.8, 0.5, 0)), (0.35, Z)]}, pri=201, file=FR)
fpk("bow_cancel", "FP Ease Bowstring", event("use_stop", BOW + " && q.last_use_time < 0.15"), 0.5, {
    "main:pos": [(0, P(0.3, 0, 0.4)), (0.5, P(0, -3, 0))], "off:pos": [(0, Z), (0.5, P(0, -4, 1))], "off:rot": [(0, Z), (0.5, R(-20, 0, 10))]}, pri=202, file=FR)
fpl("bow_crouch_aim", "FP Crouched Steady Aim", BOW + " && q.is_using_item && q.is_sneaking", 2.0, {
    "main:pos": lambda u: P(1.2, -1, 1.8), "off:pos": lambda u: P(0.8, -1.4, 1.2), "off:rot": lambda u: R(0, 0, -6), "view:rot": lambda u: V(0.3 * wave(u), 0, -3)}, pri=153, file=FR)
fpk("bow_jump_shot", "FP Airborne Shot", event("use_stop", BOW + " && !q.is_on_ground"), 0.5, {
    "main:pos": [(0, P(1.5, 0, 2)), (0.06, P(5, 2, 4), "out_expo"), (0.5, Z)], "view": [(0, Z), (0.08, V(-2, 0, 3)), (0.5, Z)]}, pri=203, file=FR)
fpk("bow_fumble", "FP Shaky Nock", event("use_start", BOW + " && q.health < 0.3"), 0.7, {
    "off:pos": [(0, Z), (0.15, P(2, -3, 2)), (0.3, P(1, -4, 3)), (0.45, P(2, -3, 2)), (0.7, Z)], "off:rot": [(0, Z), (0.2, R(-10, -20, 6)), (0.4, R(-14, -16, -6)), (0.7, Z)],
    "view": [(0, Z), (0.3, V(3, 0, 2)), (0.7, Z)]}, pri=181, file=FR)

# -------------------------------------------------------------------------- crossbow, trident throw, thrown items
fpk("crossbow_load_start", "FP Hook The String", event("use_start", XB), 0.5, {"main:pos": [(0, Z), (0.25, P(-1, -4, 2)), (0.5, P(-1, -5, 2))],
                                                                              "main:rot": [(0, Z), (0.25, R(-40, 0, 0)), (0.5, R(-50, 0, 0))], "view": [(0, Z), (0.3, V(6)), (0.5, V(6))]}, file=FR)
fpl("crossbow_crank", "FP Crank Crossbow", XB + " && q.is_using_item", 0.6, {
    "main:pos": lambda u: P(-1 + 0.6 * wave(u), -5 + 1.2 * max(0, wave(u, 0.25)), 2), "main:rot": lambda u: R(-50, 0, 6 * wave(u)), "view:rot": lambda u: V(6 + 0.5 * wave(u, 0, 2))}, pri=150, file=FR)
fpk("crossbow_load_complete", "FP Lock The Bolt", event("use_finish", XB), 0.45, {
    "main:pos": [(0, P(-1, -5, 2)), (0.12, P(0, -3, 1), "out_back"), (0.45, Z)], "main:rot": [(0, R(-50)), (0.45, Z)], "view": [(0, V(6)), (0.12, V(2)), (0.45, Z)]}, pri=181, file=FR)
fpl("crossbow_aim", "FP Crossbow Aim", XB + " && q.crossbow_charged && !q.is_using_item && q.in_combat", 2.0, {
    "main:pos": lambda u: P(-2.5, 0.8, 1.0 + 0.1 * wave(u)), "main:rot": lambda u: R(2, -4, 0)}, pri=140, file=FR)
fpk("crossbow_fire", "FP Crossbow Recoil", event("crossbow_fire", "q.is_on_ground && !q.is_sneaking"), 0.5, {
    "main:pos": [(0, P(-2.5, 0.8, 1)), (0.05, P(-2.5, 1.6, 4), "out_expo"), (0.5, Z)], "main:rot": [(0, Z), (0.05, R(14)), (0.5, Z)], "view": [(0, Z), (0.05, V(-3)), (0.5, Z)]}, pri=200, file=FR)
fpk("crossbow_fire_crouched", "FP Braced Crouch Shot", event("crossbow_fire", "q.is_sneaking"), 0.45, {
    "main:pos": [(0, P(-2.5, 0.2, 1)), (0.05, P(-2.5, 0.8, 2.5), "out_expo"), (0.45, Z)], "main:rot": [(0, Z), (0.05, R(7)), (0.45, Z)], "view": [(0, Z), (0.05, V(-1.5)), (0.45, Z)]}, pri=201, file=FR)
fpk("crossbow_fire_jump", "FP Mid-Air Crossbow Shot", event("crossbow_fire", "!q.is_on_ground"), 0.55, {
    "main:pos": [(0, P(-2.5, 0.8, 1)), (0.05, P(-2, 3, 5), "out_expo"), (0.55, Z)], "main:rot": [(0, Z), (0.05, R(22, 0, 6)), (0.55, Z)], "view": [(0, Z), (0.06, V(-5, 0, 3)), (0.55, Z)]},
    pri=202, file=FR)
fpk("crossbow_hurried", "FP Hurried Reload", event("use_start", XB + " && q.near_hostile"), 0.9, {
    "main:pos": [(0, Z), (0.1, P(-1, -6, 3), "out_expo"), (0.25, P(-2, -3, 1)), (0.4, P(-1, -6, 3)), (0.55, P(-2, -3, 1)), (0.9, P(-1, -5, 2))],
    "main:rot": [(0, Z), (0.1, R(-60, 10, 0)), (0.4, R(-45, -6, 10)), (0.9, R(-50, 0, 0))],
    "off:pos": [(0, Z), (0.15, P(-3, -2, 0)), (0.5, P(-4, -3, 1)), (0.9, Z)], "view": [(0, Z), (0.12, V(8, -3, 3)), (0.5, V(5, 3, -2)), (0.9, V(6))]}, pri=182, file=FR)
fpl("trident_windup", "FP Trident Wind-Up", ALIVE + " && q.is_using_item && q.use_anim == 'spear'", 1.0, {
    "main:pos": lambda u: P(2, 3, 5), "main:rot": lambda u: R(10, -10, 0), "view:rot": lambda u: V(-1, 0, 2)}, pri=150, file=FR)
fpk("trident_release", "FP Trident Release", event("use_stop", TR), 0.6, {
    "main:pos": [(0, P(2, 3, 5)), (0.12, P(0, 1, -12), "in_quart"), (0.6, Z)], "main:rot": [(0, R(10, -10, 0)), (0.12, R(-6, 0, 0)), (0.6, Z)], "view": [(0, V(-1, 0, 2)), (0.12, V(3)), (0.6, Z)]},
    pri=220, file=FR)
for cid, name, when, w_, r_ in (("throw_overhand", "FP Overhand Throw", "q.main_hand == 'throwable' && q.head_pitch <= 20 && !q.is_sprinting", (P(2, 8, 4), R(50, 0, 0)), (P(0, 0, -8), R(-20, 0, 0))),
                                ("throw_lob", "FP Underhand Lob", "q.main_hand == 'throwable' && q.head_pitch > 20", (P(1, -8, 3), R(-30, 0, 0)), (P(0, 2, -6), R(30, 0, 0))),
                                ("throw_sidearm", "FP Sidearm Throw", "q.main_hand == 'throwable' && q.is_sprinting", (P(9, 0, 2), R(0, -50, -20)), (P(-6, 1, -6), R(0, 30, 10))),
                                ("throw_pearl", "FP Pearl Flick", "q.main_hand == 'pearl'", (P(1, 2, 3), R(20, 0, 30)), (P(0, 2, -7), R(0, 0, 0))),
                                ("throw_splash", "FP Splash Toss", "q.main_hand == 'splash_potion'", (P(2, -2, 3), R(0, 0, 60)), (P(0, 4, -6), R(30, 0, 20))),
                                ("throw_crouched", "FP Crouched Snap Throw", "q.is_sneaking && (q.main_hand == 'throwable' || q.main_hand == 'pearl')", (P(2, 4, 3), R(30, -10, 0)), (P(0, -1, -7), R(-10, 0, 0)))):
    c = fp(cid, name, event("throw", ALIVE + " && " + when), 0.5, pri=190, file=FR)
    strike(c, "fp_main", Z, w_[0], r_[0], r_[0], 0.18, 0.26, 0.34, 0.5, ch="position")
    strike(c, "fp_main", Z, w_[1], r_[1], r_[1], 0.18, 0.26, 0.34, 0.5, ch="rotation")
    c.ev(0.22, "whoosh", weight="light")

# -------------------------------------------------------------------------- shield
SH = ALIVE + " && (q.off_hand == 'shield' || q.main_hand == 'shield')"
GUARD = P(4, 2, -2)
fpk("shield_raise", "FP Raise Shield", event("guard_up", SH + " && q.ground_speed < 0.2"), 0.25, {"off:pos": [(0, Z), (0.12, P(5, 3, -3), "out_back"), (0.25, GUARD)],
                                                                                                    "off:rot": [(0, Z), (0.25, R(0, -10, 0))]}, file=FD)
fpk("shield_raise_rush", "FP Snap Shield Up", event("guard_up", SH + " && q.ground_speed >= 0.2"), 0.3, {"off:pos": [(0, P(0, -3, 0)), (0.1, P(6, 4, -4), "out_expo"), (0.3, GUARD)],
                                                                                                          "view": [(0, Z), (0.1, V(2, 0, -2)), (0.3, Z)]}, file=FD)
fpk("shield_lower", "FP Lower Shield", event("guard_down", SH), 0.4, {"off:pos": [(0, GUARD), (0.4, Z, "in_out_sine")], "off:rot": [(0, R(0, -10, 0)), (0.4, Z)]}, file=FD)
fpl("shield_hold", "FP Shield Wall", ALIVE + " && q.is_blocking && !q.is_sneaking", 1.6, {"off:pos": lambda u: P(4, 2 + 0.2 * wave(u), -2), "off:rot": lambda u: R(0, -10, 0)}, pri=160, file=FD)
fpl("shield_crouch", "FP Turtle Guard", ALIVE + " && q.is_blocking && q.is_sneaking", 1.4, {"off:pos": lambda u: P(5, 1, -3), "off:rot": lambda u: R(6, -16, 0), "view:rot": lambda u: V(4)}, pri=161, file=FD)
fpk("shield_impact", "FP Absorb Blow", event("shield_block"), 0.45, {"off:pos": [(0, GUARD), (0.05, P(3, 1, 2), "out_expo"), (0.45, GUARD, "out_back")],
                                                                     "view": [(0, Z), (0.05, V(-2, 1, 2)), (0.45, Z)]}, pri=230, file=FD)
fpk("shield_guard_break", "FP Guard Broken", event("guard_break"), 1.0, {"off:pos": [(0, GUARD), (0.1, P(-2, -8, 4), "out_expo"), (0.6, P(0, -6, 2)), (1.0, Z)],
                                                                          "off:rot": [(0, Z), (0.1, R(-40, 20, 30)), (1.0, Z)], "view": [(0, Z), (0.1, V(-6, 4, 6)), (0.5, V(2, -1, -2)), (1.0, Z)]},
    pri=260, file=FD)
fpk("shield_bash_hit", "FP Shield Bash", event("shield_bash:hit"), 0.6, {"off:pos": [(0, GUARD), (0.12, P(3, 1, 3)), (0.22, P(2, 1, -9), "in_quart"), (0.6, GUARD)],
                                                                           "view": [(0, Z), (0.22, V(2, 0, 0)), (0.6, Z)]}, pri=240, file=FD)
fpk("shield_bash_miss", "FP Bash Overreach", event("shield_bash:miss"), 0.75, {"off:pos": [(0, GUARD), (0.24, P(1, 0, -11), "in_quart"), (0.45, P(0, -1, -12)), (0.75, GUARD)],
                                                                                 "view": [(0, Z), (0.3, V(4, 2, 3)), (0.75, Z)]}, pri=240, file=FD)
PARRY_RIPOSTE = {"sword": [(0, Z), (0.1, P(2, 3, 3)), (0.22, P(-1, 1, -8), "in_quart"), (0.55, Z)],
                 "axe": [(0, Z), (0.12, P(1, 6, 2)), (0.26, P(-2, -4, -5), "in_quart"), (0.55, Z)],
                 "empty": [(0, Z), (0.08, P(1, 0, 2)), (0.16, P(-2, 1, -7), "out_expo"), (0.3, P(-1, 0, -3)), (0.55, Z)],
                 "trident": [(0, Z), (0.12, P(0, 0, 4)), (0.28, P(0, 1, -12), "in_quart"), (0.55, Z)]}
PARRY_TWIST = {"sword": [(0, Z), (0.22, R(-6, 10, -20)), (0.55, Z)], "axe": [(0, Z), (0.12, R(40, 0, 0)), (0.26, R(-50, 0, 0)), (0.55, Z)],
               "empty": [(0, Z), (0.16, R(0, 0, 70)), (0.55, Z)], "trident": [(0, Z), (0.28, R(-10, 0, 0)), (0.55, Z)]}
for w in ("sword", "axe", "empty", "trident"):
    fpk("parry_" + w, "FP Shield Parry Riposte (%s)" % w, event("parry", "q.main_hand == '%s'" % w), 0.55, {
        "off:pos": [(0, GUARD), (0.06, P(1, 4, -5), "out_expo"), (0.3, P(3, 3, -3)), (0.55, GUARD)], "off:rot": [(0, Z), (0.06, R(10, 24, 0)), (0.55, Z)],
        "main:pos": PARRY_RIPOSTE[w], "main:rot": PARRY_TWIST[w], "view": [(0, Z), (0.06, V(-1, -2, -2)), (0.22, V(1, 2, 0)), (0.55, Z)]},
        pri=250, file=FD, events=[(0.0, "particle", {"particle": "spark", "count": "6", "at": "front", "spread": "0.3"})])
fpk("shield_peek", "FP Peek Over Shield", state(ALIVE + " && q.is_blocking && !q.is_sneaking && q.use_time > 2", group="fp_shield", exit_delay=0.05), 1.6, {
    "off:pos": [(0, GUARD), (0.4, P(4, 0, -2)), (1.0, P(4, 0, -2)), (1.6, GUARD)], "view": [(0, Z), (0.4, V(-3, 4)), (1.0, V(-3, 4)), (1.6, Z)]}, layer="overlay", pri=162, file=FD)
fpl("shield_sag", "FP Tired Shield Sag", ALIVE + " && q.is_blocking && q.exertion > 0.7", 1.0, {"off:pos": lambda u: P(4, -1 + 0.6 * wave(u), -1), "off:rot": lambda u: R(-10, -6, 4)}, pri=163, file=FD)

# -------------------------------------------------------------------------- weapon handling
for item, label, path in (
        ("sword", "FP Draw Sword", [(0, P(6, -10, 4)), (0.25, P(8, 8, 6), "out_cubic"), (0.6, Z, "in_out_sine")]),
        ("axe", "FP Heft Axe", [(0, P(-4, 10, 6)), (0.35, P(2, 4, 2)), (0.7, Z)]),
        ("trident", "FP Swing Trident Around", [(0, P(10, 8, 8)), (0.4, P(-4, 2, 2)), (0.8, Z)]),
        ("bow", "FP Unsling Bow", [(0, P(8, 10, 8)), (0.4, P(2, 0, 2)), (0.65, Z)]),
        ("crossbow", "FP Bring Up Crossbow", [(0, P(4, -10, 4)), (0.35, P(0, 2, 1)), (0.7, Z)]),
        ("pickaxe", "FP Pull Pickaxe", [(0, P(4, -12, 2)), (0.3, P(2, 2, 0)), (0.5, Z)]),
        ("shovel", "FP Swing Shovel Up", [(0, P(6, -12, 6)), (0.35, P(2, 4, 2)), (0.6, Z)]),
        ("hoe", "FP Twirl Hoe", [(0, P(2, -10, 2)), (0.3, P(0, 0, 0)), (0.6, Z)]),
        ("food", "FP Bring Food Up", [(0, P(0, -8, 0)), (0.3, P(-1, 1, 1)), (0.5, Z)]),
        ("block", "FP Toss And Catch Block", [(0, P(0, -8, 0)), (0.25, P(0, 6, 0), "out_quad"), (0.5, P(0, -1, 0), "in_quad"), (0.7, Z)]),
        ("torch", "FP Raise Torch", [(0, P(0, -8, 0)), (0.25, P(0, 3, -1), "out_back"), (0.55, Z)])):
    rot = {"hoe": [(0, R(0, 0, 0)), (0.3, R(0, 0, 200)), (0.6, R(0, 0, 360))], "trident": [(0, R(0, 60, 0)), (0.4, R(0, -20, 0)), (0.8, Z)],
           "block": [(0, Z), (0.25, R(0, 180, 0)), (0.5, R(0, 360, 0)), (0.7, R(0, 360, 0))]}.get(item, [(0, R(-30, 0, 0)), (path[-1][0], Z)])
    fpk("draw_" + item, label, event("item_switch", ALIVE + " && q.main_hand == '%s'" % item), path[-1][0], {"main:pos": path, "main:rot": rot},
        events=[(0.2, "sound", {"sound": "motionworks:weapon.draw_blade", "volume": "0.5"})] if item == "sword" else ())
SHEATHE = {"sword": ([(0, Z), (0.2, P(-2, -2, 2)), (0.45, P(-8, -12, 4), "in_cubic"), (0.6, P(-8, -14, 4))], [(0, Z), (0.2, R(-20, 30, 0)), (0.45, R(-80, 40, 20)), (0.6, R(-90, 40, 20))]),
           "axe": ([(0, Z), (0.25, P(2, 8, 2)), (0.45, P(6, 12, 10), "in_quad"), (0.6, P(6, 14, 12))], [(0, Z), (0.25, R(50, 0, 0)), (0.6, R(90, -20, 0))]),
           "bow": ([(0, Z), (0.3, P(4, 4, 6)), (0.6, P(10, 8, 12))], [(0, Z), (0.3, R(0, -40, 40)), (0.6, R(0, -60, 80))]),
           "crossbow": ([(0, Z), (0.35, P(2, -10, 6), "in_cubic"), (0.6, P(0, -12, 0))], [(0, Z), (0.35, R(-30, -20, 0)), (0.6, Z)])}
for item, label in (("sword", "FP Sheathe Sword"), ("axe", "FP Shoulder Axe"), ("bow", "FP Sling Bow"), ("crossbow", "FP Stow Crossbow")):
    fpk("sheathe_" + item, label, event("item_switch", ALIVE + " && q.prev_main_hand == '%s' && q.main_hand != '%s'" % (item, item)), 0.6, {
        "main:pos": SHEATHE[item][0], "main:rot": SHEATHE[item][1]}, pri=181)
fpk("generic_swap", "FP Quick Swap", event("item_switch", ALIVE), 0.3, {"main:pos": [(0, P(0, -6, 0)), (0.3, Z, "out_quad")]}, pri=170)
fpk("swap_hands", "FP Swap Hands", event("offhand_switch", ALIVE), 0.5, {
    "main:pos": [(0, Z), (0.22, P(-6, -2, -2)), (0.5, Z)], "off:pos": [(0, Z), (0.22, P(6, -2, -2)), (0.5, Z)]}, pri=182)
INSPECT = [
    ("sword", "FP Inspect Blade", "q.main_hand == 'sword' && q.trait_energy <= 0.6", 2.6, {"main:pos": [(0, Z), (0.5, P(-4, 2, -2)), (1.3, P(-5, 3, -2)), (2.0, P(-2, 1, -4)), (2.6, Z)],
                                                                                         "main:rot": [(0, Z), (0.5, R(10, 60, -40)), (1.3, R(10, 60, 50)), (2.0, R(30, 10, 0)), (2.6, Z)]}),
    ("sword_flip", "FP Sword Toss Flourish", "q.main_hand == 'sword' && q.trait_energy > 0.6", 1.8, {"main:pos": [(0, Z), (0.3, P(0, 2, 0)), (0.6, P(0, 9, -2)), (1.2, P(0, 1, 0)), (1.8, Z)],
                                                                                                    "main:rot": [(0, Z), (0.6, R(0, 0, 360)), (1.2, R(0, 0, 720)), (1.8, R(0, 0, 720))]}),
    ("axe", "FP Thumb Axe Edge", "q.main_hand == 'axe' && q.trait_energy <= 0.6", 2.4, {"main:pos": [(0, Z), (0.5, P(-3, 1, -3)), (1.8, P(-3, 1, -3)), (2.4, Z)],
                                                                                        "main:rot": [(0, Z), (0.5, R(20, 40, -30)), (1.8, R(20, 44, -30)), (2.4, Z)],
                                                                                        "off:pos": [(0, Z), (0.6, P(-3, 4, -4)), (0.9, P(-2, 4, -4)), (1.2, P(-3, 4, -4)), (2.4, Z)]}),
    ("axe_spin", "FP Axe Haft Roll", "q.main_hand == 'axe' && q.trait_energy > 0.6", 1.6, {"main:rot": [(0, Z), (0.4, R(0, 180, 0)), (0.7, R(0, 360, 0)), (1.0, R(30, 360, 0)), (1.6, R(0, 360, 0))],
                                                                                           "main:pos": [(0, Z), (0.35, P(-4, 1, -1)), (0.7, P(-2, 3, -2)), (1.0, P(-1, -1, 0)), (1.6, Z)]}),
    ("trident", "FP Admire Tines", "q.main_hand == 'trident'", 2.4, {"main:pos": [(0, Z), (0.6, P(-3, 4, -3)), (1.8, P(-3, 4, -3)), (2.4, Z)], "main:rot": [(0, Z), (0.6, R(50, 30, 0)), (1.8, R(50, 34, 10)), (2.4, Z)]}),
    ("bow", "FP Pluck Bowstring", "q.main_hand == 'bow'", 2.0, {"off:pos": [(0, Z), (0.4, P(-2, 2, -2)), (1.6, P(-2, 2, -2)), (2.0, Z)], "off:rot": [(0, Z), (0.4, R(0, -30, 0)), (2.0, Z)],
                                                               "main:pos": [(0, Z), (0.6, P(-5, 2, -3)), (0.8, P(-4, 2, -3)), (1.0, P(-5, 2, -3)), (2.0, Z)]}),
    ("crossbow", "FP Sight Along Crossbow", "q.main_hand == 'crossbow'", 2.2, {"main:pos": [(0, Z), (0.5, P(-5, 2, -1)), (1.7, P(-5, 2, -1)), (2.2, Z)], "main:rot": [(0, Z), (0.5, R(2, 0, -14)), (2.2, Z)]}),
    ("pickaxe", "FP Check Pickaxe Tip", "q.main_hand == 'pickaxe'", 2.0, {"main:pos": [(0, Z), (0.5, P(-3, 3, -2)), (1.5, P(-3, 3, -2)), (2.0, Z)], "main:rot": [(0, Z), (0.5, R(30, 50, -60)), (2.0, Z)]}),
    ("tool", "FP Lean On Tool", "(q.main_hand == 'shovel' || q.main_hand == 'hoe')", 2.6, {"main:pos": [(0, Z), (0.6, P(-2, -6, -4)), (2.0, P(-2, -6, -4)), (2.6, Z)], "main:rot": [(0, Z), (0.6, R(-40, 10, 10)), (2.6, Z)]}),
    ("knuckles", "FP Crack Knuckles", "q.main_hand == 'empty'", 1.6, {"main:pos": [(0, Z), (0.3, P(-4, 3, -3)), (1.2, P(-4, 3, -3)), (1.6, Z)], "off:pos": [(0, Z), (0.3, P(4, 3, -3)), (0.6, P(4, 2, -4)), (1.2, P(4, 3, -3)), (1.6, Z)],
                                                                     "main:rot": [(0, Z), (0.3, R(0, 20, -30)), (1.6, Z)]}),
    ("totem", "FP Raise Totem", "q.main_hand == 'totem'", 2.4, {"main:pos": [(0, Z), (0.6, P(-3, 8, -3)), (1.8, P(-3, 9, -3)), (2.4, Z)], "view": [(0, Z), (0.6, V(-14)), (1.8, V(-16)), (2.4, Z)]}),
    ("block", "FP Turn Block Over", "q.main_hand == 'block'", 2.0, {"main:pos": [(0, Z), (0.4, P(-3, 2, -2)), (1.6, P(-3, 2, -2)), (2.0, Z)], "main:rot": [(0, Z), (1.0, R(0, 180, 0)), (1.6, R(0, 360, 0)), (2.0, R(0, 360, 0))]})]
for cid, name, when, L, tracks in INSPECT:
    fpk("inspect_" + cid, name, event("inspect", ALIVE + " && " + when), L, tracks, pri=175)

# -------------------------------------------------------------------------- evasion
FDODGE = "first_person/defense"
fpk("dodge_roll", "FP Combat Roll", event("dodge:forward", "q.armor_weight <= 0.6"), 0.75, {"view": [(0, Z), (0.15, V(40)), (0.4, V(200)), (0.62, V(340)), (0.75, V(360))],
                                                                                            "main:pos": [(0, Z), (0.15, P(0, -8, 0)), (0.6, P(0, -8, 0)), (0.75, Z)]}, pri=300, file=FDODGE)
fpk("dodge_backstep", "FP Evasive Backstep", event("dodge:back", "!q.is_sneaking && q.main_hand != 'bow'"), 0.5, {"view": [(0, Z), (0.1, V(-6)), (0.3, V(-2)), (0.5, Z)],
                                                                                                                   "main:pos": [(0, Z), (0.1, P(2, 2, 3)), (0.5, Z)]}, pri=300, file=FDODGE)
c = fp("dodge_side", "FP Lateral Dodge", event("dodge", "q.event_arg == 'left' || q.event_arg == 'right'"), 0.5, pri=300, file=FDODGE)
for t, roll in ((0, 0), (0.1, 10), (0.3, 4), (0.5, 0)):
    c.key("fp_view", "rotation", t, [0, 0, "%g * (q.event_dir > 0 ? 1 : -1)" % roll], lerp="smooth")
    c.key("fp_main", "position", t, ["%g * (q.event_dir > 0 ? -1 : 1)" % (roll * 0.3), "%g" % (-roll * 0.2), 0], lerp="smooth")
fpk("dodge_back_roll", "FP Backward Roll", event("dodge:back", "q.is_sneaking"), 0.8, {"view": [(0, Z), (0.15, V(-40)), (0.45, V(-200)), (0.68, V(-340)), (0.8, V(-360))],
                                                                                        "main:pos": [(0, Z), (0.2, P(0, -8, 0)), (0.68, P(0, -8, 0)), (0.8, Z)]}, pri=301, file=FDODGE)
fpk("dodge_lurch", "FP Armoured Lurch", event("dodge:forward", "q.armor_weight > 0.6"), 0.7, {"view": [(0, Z), (0.15, V(14, 0, 4)), (0.4, V(6)), (0.7, Z)],
                                                                                               "main:pos": [(0, Z), (0.15, P(3, -4, -2)), (0.7, Z)]}, pri=302, file=FDODGE)
fpk("dodge_archer_hop", "FP Archer's Hop", event("dodge:back", "q.main_hand == 'bow'"), 0.55, {"view": [(0, Z), (0.15, V(-8)), (0.55, Z)], "off:pos": [(0, Z), (0.15, P(0, 3, -2)), (0.55, P(0, 1, -1))]},
    pri=301, file=FDODGE)

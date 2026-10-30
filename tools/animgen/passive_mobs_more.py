"""Passive animals part 2: pets, birds, small creatures, amphibians, aquatic life, strider and allay."""
import math

from mobkit import mob, gait, life, loop_state, beat, chew, Z, state, event, wave, cwave, tilt, move

CAT = "passive_mobs"
ALIVE = "!q.is_dead"
STILL = ALIVE + " && q.is_on_ground && !q.is_in_water && q.ground_speed < 0.01"
WALKING = ALIVE + " && q.is_on_ground && q.ground_speed >= 0.01"
SWIM = ALIVE + " && q.is_in_water"
DRY = ALIVE + " && !q.is_in_water"


def f(name):
    return "mobs/passive/" + name


def spike(u, phase, power=8, harmonic=1):
    """Brief twitch once per cycle (sharp peak of a raised sine)."""
    return max(0.0, wave(u, phase, harmonic)) ** power


# ============================================================================ wolf
T, F = "minecraft:wolf", f("wolf")
WLEGS = dict(legs=("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg"))
gait("wolf.trot", "Wolf Trot", CAT, T, WALKING + " && q.ground_speed < 0.16 && !q.is_angry", 0.8, F, gait="trot", stride=28, duty=0.5, bob=0.8, pitch=1.5, roll=0.8,
     tail="tail", tail_amp=10, **WLEGS)
gait("wolf.lope", "Wolf Loping Run", CAT, T, WALKING + " && q.ground_speed >= 0.16", 0.5, F, pri=101, gait="gallop", stride=40, duty=0.38, bob=1.8, pitch=6, roll=0.4,
     tail="tail", tail_amp=6, snap=0.15, front_scale=1.1, **WLEGS)
gait("wolf.stalk", "Wolf Stalking Prey", CAT, T, WALKING + " && q.is_angry && q.ground_speed < 0.16", 1.6, F, pri=102, gait="walk", stride=18, duty=0.7, bob=0.2, pitch=0.5, roll=0.5,
     tail="tail", tail_amp=3, yaw=2, **WLEGS)
life("wolf.stalk_crouch", "Wolf Hackles Raised", CAT, T, ALIVE + " && q.is_angry", 1.0, F, {
    "mw_center:pos": lambda u: move(0, -1.5, 0), "upper_body:scl": lambda u: [1.08, 1.12, 1.0], "head:rot": lambda u: [14, 0, 0], "tail:rot": lambda u: [-20, 0, 0]}, pri=75)
loop_state("wolf.beg", "Wolf Begging Head Tilt", CAT, T, ALIVE + " && q.is_interested", 2.4, F, {
    "real_head:rot": lambda u: [0, 0, 22 * (1 if wave(u) > 0 else -1) * min(1, abs(wave(u)) * 3)], "tail:rot": lambda u: [0, 20 * wave(u, 0, 4), 0]}, pri=125, layer="additive")
loop_state("wolf.play_bow", "Wolf Play Bow", CAT, T, STILL + " && q.is_tame && !q.is_sitting && q.player_distance < 4 && q.trait_energy > 0.5", 1.2, F, {
    "left_front_leg:rot": lambda u: [-70, 0, -6], "right_front_leg:rot": lambda u: [-70, 0, 6], "mw_center:rot": lambda u: tilt(16, 0, 0), "mw_center:pos": lambda u: move(0, -1.2, 0),
    "tail:rot": lambda u: [-30, 40 * wave(u, 0, 3), 0], "head:rot": lambda u: [-20, 0, 8 * wave(u)]}, group="wolf_idle", weight=2)
loop_state("wolf.sniff_ground", "Wolf Nose To The Ground", CAT, T, STILL + " && !q.is_sitting && q.idle_time > 3", 1.5, F, {
    "head:rot": lambda u: [45 + 5 * max(0, wave(u, 0, 6)), 25 * wave(u), 0], "tail:rot": lambda u: [0, 8 * wave(u, 0, 2), 0]}, group="wolf_idle", weight=3)
beat("wolf.howl", "Wolf Howling At The Moon", CAT, T, event("vocalize", ALIVE + " && q.is_night && !q.is_baby"), 3.0, F, {
    "head:rot": [(0, Z), (0.5, [-70, 0, 0], "out_quad"), (2.4, [-75, 0, 4]), (3.0, Z, "in_out_sine")], "mw_center:rot": [(0, Z), (0.5, tilt(-10, 0, 0)), (2.4, tilt(-10, 0, 0)), (3.0, Z)],
    "tail:rot": [(0, Z), (0.5, [-20, 0, 0]), (3.0, Z)]}, pri=150)
beat("wolf.bark", "Wolf Bark", CAT, T, event("vocalize", ALIVE + " && !q.is_night"), 0.5, F, {"head:rot": [(0, Z), (0.08, [-14, 0, 0], "out_expo"), (0.2, [6, 0, 0]), (0.5, Z)],
                                                                                          "mw_center:pos": [(0, Z), (0.08, move(0, 0, -0.6)), (0.5, Z)]}, layer="gesture")
life("wolf.happy_wag", "Wolf Happy Tail Wag", CAT, T, ALIVE + " && q.is_tame && q.player_distance < 5 && !q.is_angry", 0.4, F, {"tail:rot": lambda u: [0, 35 * wave(u), 0],
                                                                                                                                  "mw_center:rot": lambda u: tilt(0, 2 * wave(u, 0.5), 0)})
loop_state("wolf.scratch", "Wolf Scratching Behind The Ear", CAT, T, ALIVE + " && q.is_sitting", 0.3, F, {
    "right_hind_leg:rot": lambda u: [-60 + 20 * wave(u), 0, 30], "head:rot": lambda u: [10, 0, -24], "mw_center:rot": lambda u: tilt(0, 0, 8)}, group="wolf_sit", weight=1, min_time=1.5)
loop_state("wolf.sit_watch", "Wolf Sitting Watchfully", CAT, T, ALIVE + " && q.is_sitting", 4.0, F, {"head:rot": lambda u: [-6, 30 * wave(u), 0], "tail:rot": lambda u: [0, 6 * wave(u, 0, 2), 0]},
           group="wolf_sit", weight=4, layer="additive")
loop_state("wolf.pup_pounce", "Wolf Pup Pouncing", CAT, T, STILL + " && q.is_baby", 1.6, F, {
    "mw_center:pos": lambda u: move(0, 3 * max(0, wave(u)) ** 2, 2 * max(0, wave(u))), "left_front_leg:rot": lambda u: [-50 * max(0, wave(u)), 0, 0],
    "right_front_leg:rot": lambda u: [-50 * max(0, wave(u)), 0, 0], "mw_center:rot": lambda u: tilt(-10 * max(0, wave(u)) + 10 * max(0, -wave(u)), 0, 0)}, group="wolf_idle", weight=4)
c = mob("wolf.curl_sleep", "Wolf Curled Asleep", CAT, T, 4.0, state(STILL + " && q.is_night && q.idle_time > 30 && !q.is_sitting"), file=F, blend_in=1.5, blend_out=0.8)
c.cycle("mw_center", "position", lambda u: move(0, -4.5 + 0.2 * wave(u), 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 12))
c.cycle("head", "rotation", lambda u: [30, -50, 10])
c.cycle("tail", "rotation", lambda u: [20, -60, 0])
for b in ("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg"):
    c.cycle(b, "rotation", lambda u, b=b: [-85 if "front" in b else 85, 0, 0])
beat("wolf.shake_dry", "Wolf Shakes Dry", CAT, T, event("exit_water", ALIVE), 1.2, F, {
    "mw_center:rot": [(0, Z), (0.1, tilt(0, 0, 16)), (0.2, tilt(0, 0, -16)), (0.3, tilt(0, 0, 16)), (0.4, tilt(0, 0, -14)), (0.5, tilt(0, 0, 10)), (0.65, tilt(0, 0, -5)), (1.2, Z)],
    "tail:rot": [(0, Z), (0.15, [0, 40, 0]), (0.3, [0, -40, 0]), (0.45, [0, 30, 0]), (0.8, Z)]}, layer="gesture", events=[(0.2, "particle", {"particle": "splash", "count": "14", "at": "body", "spread": "0.5"})])
loop_state("wolf.guard_growl", "Wolf Guarding Growl", CAT, T, ALIVE + " && q.is_angry && q.ground_speed < 0.01", 0.6, F, {
    "head:rot": lambda u: [18, 0, 0], "head:pos": lambda u: move(0, 0, 0.2 * wave(u, 0, 3)), "left_front_leg:rot": lambda u: [-12, 0, -6], "right_front_leg:rot": lambda u: [-12, 0, 6]}, pri=130)

# ============================================================================ cat & ocelot
for T, sp, label, tame in (("minecraft:cat", "cat", "Cat", True), ("minecraft:ocelot", "ocelot", "Ocelot", False)):
    F = f(sp)
    w = 0.0 if tame else 1.0  # the wild ocelot moves lower, longer and more explosively
    CLEGS = dict(legs=("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg"))
    gait(sp + ".prowl", label + " Prowling Walk", CAT, T, WALKING + " && !q.is_sprinting && !q.is_crouching", 1.1 if tame else 0.95, F, gait="walk", stride=24, duty=0.62, bob=0.3,
         pitch=0.6, roll=0.6, tail="tail2", tail_amp=12, yaw=1.5 if tame else 0.5, splay=0 if tame else 4, **CLEGS)
    gait(sp + ".sprint", label + " Bounding Sprint", CAT, T, WALKING + " && q.is_sprinting", 0.45, F, pri=101, gait="bound", stride=44, duty=0.34, bob=1.2, pitch=9, roll=0.2,
         snap=0.1 if tame else 0.25, **CLEGS)
    gait(sp + ".stalk", label + " Belly-Low Stalk", CAT, T, WALKING + " && q.is_crouching", 1.8 + 0.6 * w, F, pri=102, gait="walk" if tame else "amble", stride=16, duty=0.72, bob=0.1,
         pitch=0.3, roll=0.3, lift=8 - 6 * w, yaw=2.5 * w, snap=0.2 * w, **CLEGS)
    beat(sp + ".pounce", label + (" Pounce" if tame else " Ambush Leap"), CAT, T, event("jump", ALIVE + " && q.is_crouching"), 0.8 + 0.2 * w, F, {
        "mw_center:rot": [(0, Z), (0.12 + 0.1 * w, tilt(-20 - 10 * w, 0, 0)), (0.4 + 0.15 * w, tilt(18, 0, 0)), (0.8 + 0.2 * w, Z)],
        "mw_center:pos": [(0, Z), (0.12 + 0.1 * w, move(0, -1.5 * w, 0)), (0.4 + 0.15 * w, move(0, 3 * w, 2 * w)), (0.8 + 0.2 * w, Z)],
        "left_front_leg:rot": [(0, Z), (0.12, [-80, 0, 0]), (0.45, [-60 - 30 * w, 0, -10 * w]), (0.8 + 0.2 * w, Z)],
        "right_front_leg:rot": [(0, Z), (0.12, [-80, 0, 0]), (0.45, [-60 - 30 * w, 0, 10 * w]), (0.8 + 0.2 * w, Z)], "left_hind_leg:rot": [(0, Z), (0.12, [60, 0, 0]), (0.5, [20 + 30 * w, 0, 0]), (0.8 + 0.2 * w, Z)],
        "right_hind_leg:rot": [(0, Z), (0.12, [60, 0, 0]), (0.5, [20 + 30 * w, 0, 0]), (0.8 + 0.2 * w, Z)], "tail1:rot": [(0, Z), (0.12, [-30 + 50 * w, 0, 0]), (0.8 + 0.2 * w, Z)]}, pri=160)
    if tame:
        loop_state(sp + ".groom", label + " Grooming", CAT, T, STILL + " && q.idle_time > 4", 0.9, F, {
            "right_front_leg:rot": lambda u: [-100, 0, 20], "head:rot": lambda u: [24 + 10 * max(0, wave(u, 0, 2)), -25, 10 * wave(u, 0, 2)], "tail2:rot": lambda u: [0, 10 * wave(u, 0, 0.5), 0]},
            group=sp + "_idle", weight=3, min_time=3)
        life(sp + ".tail_flick", label + " Tail Tip Flick", CAT, T, ALIVE, 2.2, F, {"tail2:rot": lambda u: [0, 30 * spike(u, 0.1, 6), 0], "tail1:rot": lambda u: [0, 6 * wave(u), 0]})
    else:
        loop_state(sp + ".groom", label + " Grooming Its Flank", CAT, T, STILL + " && q.idle_time > 4", 1.1, F, {
            "mw_center:rot": lambda u: tilt(0, 0, 20), "left_hind_leg:rot": lambda u: [-70, 0, -30], "head:rot": lambda u: [40, 70, 10 * wave(u, 0, 3)], "body:rot": lambda u: [0, 0, 8 * wave(u)]},
            group=sp + "_idle", weight=3, min_time=3)
        life(sp + ".tail_flick", label + " Tail Twitch", CAT, T, ALIVE, 1.6, F, {"tail1:rot": lambda u: [8 * spike(u, 0.6, 6), 0, 0], "tail2:rot": lambda u: [-20 * spike(u, 0.65, 10), 18 * spike(u, 0.1, 4), 0]})
F = f("cat")
T = "minecraft:cat"
c = mob("cat.loaf", "Cat Loafing", CAT, T, 5.0, state(STILL + " && !q.is_sitting && !q.is_lying && q.idle_time > 8", group="cat_idle", weight=3), file=F, blend_in=1.0, blend_out=0.6)
c.cycle("mw_center", "position", lambda u: move(0, -3.2 + 0.12 * wave(u), 0))
for b in ("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg"):
    c.cycle(b, "rotation", lambda u, b=b: [-80 if "front" in b else 80, 0, 0])
c.cycle("head", "rotation", lambda u: [6, 0, 4 * spike(u, 0.3, 6)])
c.cycle("tail1", "rotation", lambda u: [40, -30, 0])
loop_state("cat.stretch", "Cat Long Stretch", CAT, T, STILL + " && q.idle_time > 4 && q.idle_time < 9", 3.0, F, {
    "left_front_leg:rot": lambda u: [-60 * max(0, wave(u, 0.0, 0.5)), 0, 0], "right_front_leg:rot": lambda u: [-60 * max(0, wave(u, 0.0, 0.5)), 0, 0],
    "mw_center:rot": lambda u: tilt(14 * max(0, wave(u, 0, 0.5)), 0, 0), "head:rot": lambda u: [-18 * max(0, wave(u, 0, 0.5)), 0, 0], "tail1:rot": lambda u: [-40 * max(0, wave(u, 0, 0.5)), 0, 0]},
    group="cat_idle", weight=2)
loop_state("cat.knead", "Cat Kneading", CAT, T, ALIVE + " && q.is_tame && (q.is_lying || q.is_sitting) && q.player_distance < 3", 0.7, F, {
    "left_front_leg:rot": lambda u: [-30 + 18 * max(0, wave(u)), 0, 0], "right_front_leg:rot": lambda u: [-30 + 18 * max(0, wave(u, 0.5)), 0, 0], "head:rot": lambda u: [8, 0, 0]}, pri=135, layer="additive")
loop_state("cat.arch_hiss", "Cat Arched Back Hiss", CAT, T, ALIVE + " && q.near_hostile && q.hostile_distance < 4", 0.5, F, {
    "mw_center:pos": lambda u: move(0, 1.2, 0), "body:rot": lambda u: [-12, 0, 0], "body:scl": lambda u: [1.1, 1.1, 1.0], "tail1:rot": lambda u: [-70, 0, 0],
    "head:rot": lambda u: [12, 0, 0], "head:pos": lambda u: move(0, 0, -0.2 * wave(u, 0, 2))}, pri=150)
loop_state("cat.affection_rub", "Cat Rubbing Against Owner", CAT, T, ALIVE + " && q.is_tame && q.player_distance < 1.6 && q.ground_speed < 0.03 && !q.is_sitting", 1.8, F, {
    "mw_center:rot": lambda u: tilt(0, 10 * wave(u), 14 * wave(u)), "head:rot": lambda u: [0, -20 * wave(u), -16 * wave(u)], "tail1:rot": lambda u: [-50, 10 * wave(u, 0.2), 0]}, pri=128)
loop_state("cat.dream", "Cat Twitching In Sleep", CAT, T, ALIVE + " && q.is_lying", 3.0, F, {
    "left_front_leg:rot": lambda u: [-8 * spike(u, 0.2, 10, 2), 0, 0], "tail2:rot": lambda u: [0, 12 * spike(u, 0.6, 8), 0], "body:scl": lambda u: [1, 1 + 0.025 * wave(u), 1]}, layer="additive", pri=70)
beat("cat.meow", "Cat Meow", CAT, T, event("vocalize", ALIVE), 0.7, F, {"head:rot": [(0, Z), (0.2, [-12, 0, 6], "out_quad"), (0.45, [-8, 0, -3]), (0.7, Z)]}, layer="gesture")
F, T = f("ocelot"), "minecraft:ocelot"
loop_state("ocelot.frozen_wary", "Ocelot Freezes Warily", CAT, T, ALIVE + " && q.player_distance < 7 && q.ground_speed < 0.02", 2.0, F, {
    "head:rot": lambda u: [-8, 0, 0], "mw_center:pos": lambda u: move(0, -0.8, 0), "tail1:rot": lambda u: [0, 0, 0], "tail2:rot": lambda u: [0, 4 * spike(u, 0.5, 20), 0]}, pri=120)
life("ocelot.tail_lash", "Ocelot Tail Lash", CAT, T, WALKING + " && q.player_distance < 10", 0.8, F, {"tail1:rot": lambda u: [0, 18 * wave(u), 0], "tail2:rot": lambda u: [0, 26 * wave(u, 0.15), 0]})

# ============================================================================ fox
T, F = "minecraft:fox", f("fox")
FLEGS = dict(legs=("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg"))
gait("fox.trot", "Fox Dainty Trot", CAT, T, WALKING + " && !q.is_crouching && q.ground_speed < 0.18", 0.6, F, gait="trot", stride=26, duty=0.46, bob=0.6, pitch=1, roll=0.3,
     tail="tail", tail_amp=8, lift=10, **FLEGS)
gait("fox.dash", "Fox Darting Run", CAT, T, WALKING + " && q.ground_speed >= 0.18", 0.4, F, pri=101, gait="gallop", stride=42, duty=0.34, bob=1.4, pitch=7, roll=0.2,
     tail="tail", tail_amp=4, front_scale=0.9, splay=4, **FLEGS)
gait("fox.creep", "Fox Creeping Low", CAT, T, WALKING + " && q.is_crouching", 1.6, F, pri=102, gait="amble", stride=14, duty=0.74, bob=0.1, pitch=0.2, roll=0.4, snap=0.2, **FLEGS)
loop_state("fox.interested", "Fox Ears Pricked And Tilting", CAT, T, ALIVE + " && q.is_interested", 1.8, F, {
    "head:rot": lambda u: [0, 0, 25 * wave(u, 0, 0.5)], "right_ear:rot": lambda u: [-15, 0, 0], "left_ear:rot": lambda u: [-15, 0, 0]}, pri=125, layer="additive")
beat("fox.snow_dive", "Fox Snow Dive", CAT, T, event("jump", ALIVE + " && q.is_pouncing && q.surface == 'snow'"), 1.0, F, {
    "mw_center:rot": [(0, Z), (0.2, tilt(-30, 0, 0)), (0.6, tilt(70, 0, 0), "in_quad"), (1.0, tilt(60, 0, 0))], "left_front_leg:rot": [(0, Z), (0.6, [-110, 0, 0]), (1.0, [-110, 0, 0])],
    "right_front_leg:rot": [(0, Z), (0.6, [-110, 0, 0]), (1.0, [-110, 0, 0])], "tail:rot": [(0, Z), (0.6, [-40, 0, 0]), (1.0, [-30, 10, 0])]}, pri=170,
    events=[(0.65, "particle", {"particle": "snow_puff", "count": "16", "at": "feet", "spread": "0.4"})])
loop_state("fox.sniff", "Fox Sniffing Trail", CAT, T, STILL + " && q.idle_time > 3", 1.3, F, {
    "head:rot": lambda u: [35 + 6 * max(0, wave(u, 0, 5)), 18 * wave(u), 0], "nose:rot": lambda u: [4 * wave(u, 0, 5), 0, 0]}, group="fox_idle", weight=3)
life("fox.ear_twitch", "Fox Ear Twitch", CAT, T, ALIVE, 2.0, F, {"right_ear:rot": lambda u: [0, 0, 20 * spike(u, 0.15, 10)], "left_ear:rot": lambda u: [0, 0, -20 * spike(u, 0.65, 10)]})
life("fox.brush_sway", "Fox Brush Sway", CAT, T, STILL, 3.0, F, {"tail:rot": lambda u: [3 * wave(u, 0.3), 14 * wave(u), 0]})
beat("fox.yip", "Fox Yip", CAT, T, event("vocalize", ALIVE), 0.5, F, {"head:rot": [(0, Z), (0.08, [-20, 0, 0], "out_expo"), (0.22, [-5, 0, 0]), (0.5, Z)],
                                                                    "right_ear:rot": [(0, Z), (0.1, [-15, 0, 0]), (0.5, Z)], "left_ear:rot": [(0, Z), (0.1, [-15, 0, 0]), (0.5, Z)]}, layer="gesture")
loop_state("fox.sit_tail_wrap", "Fox Sitting Tail Wrapped", CAT, T, ALIVE + " && q.is_sitting", 4.0, F, {"tail:rot": lambda u: [0, -50 + 4 * wave(u), 0], "head:rot": lambda u: [-4, 20 * wave(u, 0, 0.5), 0]},
           layer="additive", pri=70)
loop_state("fox.sleep_breathe", "Fox Sleeping Breath", CAT, T, ALIVE + " && q.is_sleeping", 3.2, F, {"body:scl": lambda u: [1, 1 + 0.03 * wave(u), 1], "tail:rot": lambda u: [0, 3 * wave(u), 0]},
           layer="additive", pri=70)
beat("fox.mouse_pounce", "Fox Mouse Pounce", CAT, T, event("jump", ALIVE + " && q.is_pouncing && q.surface != 'snow'"), 0.9, F, {
    "mw_center:rot": [(0, Z), (0.15, tilt(-25, 0, 0)), (0.55, tilt(40, 0, 0), "in_quad"), (0.9, Z)], "left_front_leg:rot": [(0, Z), (0.55, [-90, 0, 0]), (0.9, Z)],
    "right_front_leg:rot": [(0, Z), (0.55, [-90, 0, 0]), (0.9, Z)], "tail:rot": [(0, Z), (0.3, [-35, 0, 0]), (0.9, Z)]}, pri=168)

# ============================================================================ rabbit
T, F = "minecraft:rabbit", f("rabbit")
c = mob("rabbit.hop", "Rabbit Hopping", CAT, T, 1.0, state(ALIVE + " && q.jump_progress > 0.01", exit_delay=0.05), layer="base", file=F, time="q.jump_progress")
c.keys("left_haunch", "rotation", [(0, Z), (0.2, [-30, 0, 0]), (0.45, [40, 0, 0], "out_quad"), (0.8, [-10, 0, 0]), (1.0, Z)], lerp="smooth")
c.keys("right_haunch", "rotation", [(0, Z), (0.2, [-30, 0, 0]), (0.45, [40, 0, 0], "out_quad"), (0.8, [-10, 0, 0]), (1.0, Z)], lerp="smooth")
c.keys("left_hind_foot", "rotation", [(0, Z), (0.45, [60, 0, 0]), (1.0, Z)], lerp="smooth")
c.keys("right_hind_foot", "rotation", [(0, Z), (0.45, [60, 0, 0]), (1.0, Z)], lerp="smooth")
c.keys("left_front_leg", "rotation", [(0, Z), (0.45, [-50, 0, 0]), (0.8, [-20, 0, 0]), (1.0, Z)], lerp="smooth")
c.keys("right_front_leg", "rotation", [(0, Z), (0.45, [-50, 0, 0]), (0.8, [-20, 0, 0]), (1.0, Z)], lerp="smooth")
c.keys("mw_center", "rotation", [(0, Z), (0.2, tilt(8, 0, 0)), (0.45, tilt(-14, 0, 0)), (0.8, tilt(10, 0, 0)), (1.0, Z)], lerp="smooth")
c.keys("right_ear", "rotation", [(0, Z), (0.45, [30, 0, 0]), (1.0, Z)], lerp="smooth")
c.keys("left_ear", "rotation", [(0, Z), (0.45, [30, 0, 0]), (1.0, Z)], lerp="smooth")
life("rabbit.nose_twitch", "Rabbit Nose Twitch", CAT, T, ALIVE, 0.5, F, {"nose:pos": lambda u: move(0, 0.15 * spike(u, 0, 2), 0), "nose:scl": lambda u: [1 + 0.08 * spike(u, 0, 2)] * 3})
life("rabbit.ear_swivel", "Rabbit Ear Swivel", CAT, T, ALIVE, 3.4, F, {"right_ear:rot": lambda u: [10 * wave(u), 25 * spike(u, 0.2, 6), 0], "left_ear:rot": lambda u: [10 * wave(u, 0.4), -25 * spike(u, 0.7, 6), 0]})
loop_state("rabbit.wash_face", "Rabbit Washing Its Face", CAT, T, STILL + " && q.idle_time > 3", 0.6, F, {
    "left_front_leg:rot": lambda u: [-110 + 25 * wave(u), 0, -8], "right_front_leg:rot": lambda u: [-110 + 25 * wave(u, 0.15), 0, 8], "head:rot": lambda u: [14 + 6 * wave(u), 0, 0],
    "mw_center:rot": lambda u: tilt(-30, 0, 0)}, group="rabbit_idle", weight=2, min_time=2.4)
beat("rabbit.thump", "Rabbit Warning Thump", CAT, T, event("start_moving", ALIVE + " && q.near_hostile"), 0.6, F, {
    "left_hind_foot:rot": [(0, Z), (0.1, [-30, 0, 0]), (0.18, [20, 0, 0], "in_quart"), (0.3, [-20, 0, 0]), (0.38, [20, 0, 0], "in_quart"), (0.6, Z)],
    "right_ear:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.6, Z)], "left_ear:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.6, Z)]}, pri=150, events=[(0.18, "footstep", {"foot": "left"}), (0.38, "footstep", {"foot": "left"})])
loop_state("rabbit.sentinel", "Rabbit Standing Sentinel", CAT, T, STILL + " && (q.near_hostile || q.player_distance < 5)", 2.0, F, {
    "mw_center:rot": lambda u: tilt(-55, 0, 0), "mw_center:pos": lambda u: move(0, 1.5, 0), "left_front_leg:rot": lambda u: [-30, 0, 0], "right_front_leg:rot": lambda u: [-30, 0, 0],
    "head:rot": lambda u: [45, 20 * wave(u, 0, 0.5), 0], "right_ear:rot": lambda u: [-10, 0, 0], "left_ear:rot": lambda u: [-10, 0, 0]}, pri=118)
c = mob("rabbit.flop", "Rabbit Flopped Over", CAT, T, 4.0, state(STILL + " && q.idle_time > 20 && !q.near_hostile", group="rabbit_idle", weight=1), file=F, blend_in=0.4, blend_out=0.5)
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 80))
c.cycle("mw_center", "position", lambda u: move(0, -1.6, 0))
c.cycle("body", "scale", lambda u: [1, 1 + 0.04 * wave(u, 0, 2), 1])
c.cycle("left_hind_foot", "rotation", lambda u: [-40, 0, 0])
beat("rabbit.binky", "Rabbit Binky Twist", CAT, T, event("jump", ALIVE + " && q.trait_energy > 0.55", chance=0.25), 0.6, F, {
    "mw_center:rot": [(0, Z), (0.2, tilt(0, 40, 25)), (0.4, tilt(0, -30, -20)), (0.6, Z)], "head:rot": [(0, Z), (0.2, [0, -30, 0]), (0.4, [0, 20, 0]), (0.6, Z)]}, layer="gesture")
loop_state("rabbit.nibble", "Rabbit Nibbling", CAT, T, STILL + " && q.idle_time > 3", 0.8, F, {"head:rot": lambda u: [30 + chew(u, 4, 4), 0, 0], "nose:rot": lambda u: [chew(u, 4, 8), 0, 0]},
           group="rabbit_idle", weight=3)

# ============================================================================ chicken
T, F = "minecraft:chicken", f("chicken")
c = mob("chicken.strut", "Chicken Head-Bobbing Strut", CAT, T, 0.6, state(WALKING + " && q.ground_speed < 0.12"), layer="base", file=F, time="q.limb_swing * 0.0636",
        weight="math.clamp(q.limb_swing_amount * 2.5, 0, 1)")
c.cycle("right_leg", "rotation", lambda u: [-35 * cwave(u), 0, 0])
c.cycle("left_leg", "rotation", lambda u: [35 * cwave(u), 0, 0])
c.cycle("head", "position", lambda u: move(0, 0, 1.2 * (1 if (u * 2) % 1 < 0.5 else -0.2) * min(1, abs(wave(u, 0, 2)) * 2)))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 4 * wave(u)))
c = mob("chicken.flap_run", "Chicken Flapping Run", CAT, T, 0.4, state(WALKING + " && q.ground_speed >= 0.12"), layer="base", pri=101, file=F)
c.cycle("right_leg", "rotation", lambda u: [-50 * cwave(u), 0, 0])
c.cycle("left_leg", "rotation", lambda u: [50 * cwave(u), 0, 0])
c.cycle("right_wing", "rotation", lambda u: [0, 0, 50 + 40 * wave(u, 0, 2)])
c.cycle("left_wing", "rotation", lambda u: [0, 0, -50 - 40 * wave(u, 0, 2)])
c.cycle("head", "position", lambda u: move(0, 0, 1.5))
c.cycle("mw_center", "rotation", lambda u: tilt(12, 0, 6 * wave(u)))
loop_state("chicken.peck", "Chicken Pecking Seeds", CAT, T, STILL + " && q.idle_time > 2", 1.2, F, {
    "head:rot": lambda u: [70 * spike(u, 0, 3, 2), 10 * wave(u, 0, 0.5), 0], "mw_center:rot": lambda u: tilt(16 * spike(u, 0, 3, 2), 0, 0)}, group="chicken_idle", weight=4)
loop_state("chicken.scratch", "Chicken Scratching The Dirt", CAT, T, STILL + " && q.idle_time > 2", 1.0, F, {
    "right_leg:rot": lambda u: [40 * spike(u, 0.05, 2), 0, 0], "left_leg:rot": lambda u: [40 * spike(u, 0.55, 2), 0, 0], "head:rot": lambda u: [30, 0, 0], "mw_center:rot": lambda u: tilt(8, 0, 0)},
    group="chicken_idle", weight=2)
life("chicken.flutter_fall", "Chicken Fluttering Descent", CAT, T, ALIVE + " && !q.is_on_ground && q.vertical_speed < 0", 0.25, F, {
    "right_wing:rot": lambda u: [0, 0, 30 * wave(u)], "left_wing:rot": lambda u: [0, 0, -30 * wave(u)], "right_leg:rot": lambda u: [-30, 0, 0], "left_leg:rot": lambda u: [-30, 0, 0]}, pri=80)
c = mob("chicken.dust_bath", "Chicken Dust Bath", CAT, T, 2.0, state(STILL + " && q.idle_time > 18 && (q.surface == 'sand' || q.surface == 'dirt' || q.surface == 'gravel')", group="chicken_idle", weight=3),
        file=F, blend_in=0.6, blend_out=0.5)
c.cycle("mw_center", "position", lambda u: move(0, -2.5, 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 25 * wave(u)))
c.cycle("right_wing", "rotation", lambda u: [0, 0, 40 * max(0, wave(u, 0, 3))])
c.cycle("left_wing", "rotation", lambda u: [0, 0, -40 * max(0, wave(u, 0.5, 3))])
c.ev(0.2, "particle", particle="dust_puff", count="4", at="feet", spread="0.3")
beat("chicken.cluck", "Chicken Cluck", CAT, T, event("vocalize", ALIVE), 0.5, F, {"head:rot": [(0, Z), (0.1, [-15, 0, 0]), (0.2, [10, 0, 0]), (0.32, [-10, 0, 0]), (0.5, Z)],
                                                                            "red_thing:rot": [(0, Z), (0.15, [10, 0, 0]), (0.5, Z)]}, layer="gesture")
loop_state("chicken.wing_stretch", "Chicken Wing And Leg Stretch", CAT, T, STILL + " && q.idle_time > 6", 2.4, F, {
    "right_wing:rot": lambda u: [-20 * max(0, wave(u, 0, 0.5)), 0, 60 * max(0, wave(u, 0, 0.5))], "right_leg:rot": lambda u: [40 * max(0, wave(u, 0, 0.5)), 0, 0],
    "mw_center:rot": lambda u: tilt(0, 0, -6 * max(0, wave(u, 0, 0.5)))}, group="chicken_idle", weight=1)
c = mob("chicken.roost", "Chicken Roosting At Night", CAT, T, 3.0, state(STILL + " && q.is_night && q.idle_time > 10"), file=F, blend_in=1.0, blend_out=0.6)
c.cycle("mw_center", "position", lambda u: move(0, -2.2, 0))
c.cycle("body", "scale", lambda u: [1.12, 1.12 + 0.02 * wave(u), 1.12])
c.cycle("head", "position", lambda u: move(0, -1.0, -1.0))
c.cycle("head", "rotation", lambda u: [20, 0, 0])
c.cycle("right_leg", "rotation", lambda u: [-90, 0, 0])
c.cycle("left_leg", "rotation", lambda u: [-90, 0, 0])
c = mob("chicken.chick_dart", "Chick Darting About", CAT, T, 0.25, state(WALKING + " && q.is_baby"), layer="base", pri=102, file=F)
c.cycle("right_leg", "rotation", lambda u: [-45 * cwave(u), 0, 0])
c.cycle("left_leg", "rotation", lambda u: [45 * cwave(u), 0, 0])
c.cycle("mw_center", "rotation", lambda u: tilt(6, 8 * wave(u, 0, 0.5), 0))
c.cycle("mw_center", "position", lambda u: move(0, 0.4 * max(0, wave(u, 0, 2)), 0))
loop_state("chicken.alarm", "Chicken Alarmed Squawk", CAT, T, ALIVE + " && q.recent_hurt < 2", 0.3, F, {
    "right_wing:rot": lambda u: [0, 0, 70 + 20 * wave(u)], "left_wing:rot": lambda u: [0, 0, -70 - 20 * wave(u)], "head:rot": lambda u: [-20, 25 * wave(u, 0, 0.5), 0]}, pri=140)

# ============================================================================ parrot
T, F = "minecraft:parrot", f("parrot")
c = mob("parrot.flight", "Parrot Flapping Flight", CAT, T, 0.35, state(ALIVE + " && q.is_flying"), layer="base", file=F)
c.cycle("right_wing", "rotation", lambda u: [0, 0, 60 * wave(u) + 20])
c.cycle("left_wing", "rotation", lambda u: [0, 0, -60 * wave(u) - 20])
c.cycle("tail", "rotation", lambda u: [10 * wave(u, 0.3), 0, 0])
c.cycle("mw_center", "position", lambda u: move(0, 0.4 * wave(u, 0.25), 0))
c.cycle("left_leg", "rotation", lambda u: [40, 0, 0])
c.cycle("right_leg", "rotation", lambda u: [40, 0, 0])
loop_state("parrot.preen", "Parrot Preening", CAT, T, ALIVE + " && !q.is_flying && !q.is_dancing && q.idle_time > 3", 1.6, F, {
    "head:rot": lambda u: [40, 70, 10 * wave(u, 0, 4)], "right_wing:rot": lambda u: [0, 0, 18], "feather:rot": lambda u: [-10 * wave(u, 0, 2), 0, 0]}, group="parrot_idle", weight=3)
loop_state("parrot.groove", "Parrot Grooving To Music", CAT, T, ALIVE + " && q.is_dancing", 0.5, F, {
    "mw_center:pos": lambda u: move(0, 0.8 * max(0, wave(u)), 0), "head:rot": lambda u: [-15 * wave(u), 0, 12 * wave(u, 0, 0.5)], "feather:rot": lambda u: [-25 * max(0, wave(u)), 0, 0],
    "tail:rot": lambda u: [0, 20 * wave(u, 0, 0.5), 0]}, pri=140)
loop_state("parrot.head_bob", "Parrot Curious Head Bob", CAT, T, ALIVE + " && !q.is_flying && q.player_distance < 5", 1.4, F, {
    "head:rot": lambda u: [8 * wave(u, 0, 2), 0, 30 * (1 if wave(u, 0, 0.5) > 0 else -1) * min(1, abs(wave(u, 0, 0.5)) * 3)]}, group="parrot_idle", weight=2)
beat("parrot.mimic", "Parrot Mimicry Squawk", CAT, T, event("vocalize", ALIVE), 0.8, F, {
    "beak2:rot": [(0, Z), (0.1, [25, 0, 0]), (0.2, Z), (0.3, [25, 0, 0]), (0.4, Z)], "head:rot": [(0, Z), (0.1, [-14, 0, 0]), (0.3, [-14, 0, 6]), (0.8, Z)],
    "feather:rot": [(0, Z), (0.1, [-35, 0, 0]), (0.6, Z)]}, layer="gesture")
beat("parrot.landing_flare", "Parrot Landing Flare", CAT, T, event("land", ALIVE), 0.5, F, {
    "right_wing:rot": [(0, [0, 0, 70]), (0.2, [0, 0, 40]), (0.5, Z)], "left_wing:rot": [(0, [0, 0, -70]), (0.2, [0, 0, -40]), (0.5, Z)], "tail:rot": [(0, [-30, 0, 0]), (0.5, Z)]}, layer="gesture")
loop_state("parrot.wing_spread", "Parrot Wing Display", CAT, T, ALIVE + " && !q.is_flying && q.idle_time > 6", 2.0, F, {
    "right_wing:rot": lambda u: [0, 0, 80 * max(0, wave(u, 0, 0.5))], "left_wing:rot": lambda u: [0, 0, -80 * max(0, wave(u, 0, 0.5))], "feather:rot": lambda u: [-30 * max(0, wave(u, 0, 0.5)), 0, 0]},
    group="parrot_idle", weight=1)
c = mob("parrot.hop_walk", "Parrot Sideways Hop", CAT, T, 0.5, state(WALKING + " && !q.is_flying"), layer="base", pri=101, file=F)
c.cycle("mw_center", "position", lambda u: move(0, 0.8 * max(0, wave(u, 0, 2)), 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 8 * wave(u)))
c.cycle("left_leg", "rotation", lambda u: [-20 * max(0, wave(u, 0, 2)), 0, 0])
c.cycle("right_leg", "rotation", lambda u: [-20 * max(0, wave(u, 0, 2)), 0, 0])
beat("parrot.take_off", "Parrot Take-Off", CAT, T, event("jump", ALIVE), 0.4, F, {"right_wing:rot": [(0, Z), (0.1, [0, 0, 90]), (0.25, [0, 0, 10]), (0.4, [0, 0, 70])],
                                                                                 "left_wing:rot": [(0, Z), (0.1, [0, 0, -90]), (0.25, [0, 0, -10]), (0.4, [0, 0, -70])]}, layer="gesture")
life("parrot.feather_ruffle", "Parrot Feather Ruffle", CAT, T, ALIVE + " && q.wind > 0.4", 0.6, F, {"feather:rot": lambda u: [-8 * wave(u), 0, 4 * wave(u, 0.3)], "body:scl": lambda u: [1 + 0.02 * wave(u)] * 3})

# ============================================================================ bee
T, F = "minecraft:bee", f("bee")
c = mob("bee.hover", "Bee Hovering", CAT, T, 1.6, state(ALIVE + " && q.is_flying && q.ground_speed < 0.03"), layer="base", file=F)
c.cycle("bone", "position", lambda u: move(0.3 * wave(u, 0.2), 0.6 * wave(u), 0))
c.cycle("bone", "rotation", lambda u: tilt(4 * wave(u, 0.25), 0, 3 * wave(u, 0.1)))
c.cycle("front_legs", "rotation", lambda u: [20 + 6 * wave(u), 0, 0])
c.cycle("back_legs", "rotation", lambda u: [30 + 6 * wave(u, 0.3), 0, 0])
c = mob("bee.cruise", "Bee Cruising Flight", CAT, T, 0.8, state(ALIVE + " && q.is_flying && q.ground_speed >= 0.03 && !q.has_nectar"), layer="base", pri=101, file=F)
c.cycle("bone", "rotation", lambda u: tilt(14, 0, 4 * wave(u)))
c.cycle("bone", "position", lambda u: move(0, 0.3 * wave(u, 0, 2), 0))
c.cycle("middle_legs", "rotation", lambda u: [50, 0, 0])
c.cycle("back_legs", "rotation", lambda u: [55, 0, 0])
c = mob("bee.laden_flight", "Bee Laden With Nectar", CAT, T, 1.2, state(ALIVE + " && q.is_flying && q.has_nectar"), layer="base", pri=102, file=F)
c.cycle("bone", "position", lambda u: move(0, -0.6 + 0.8 * wave(u), 0))
c.cycle("bone", "rotation", lambda u: tilt(-6 + 4 * wave(u, 0.2), 0, 6 * wave(u, 0.5)))
c.cycle("front_legs", "rotation", lambda u: [-10, 0, 0])
c.cycle("middle_legs", "rotation", lambda u: [-6 + 8 * wave(u, 0.3), 0, 0])
c.cycle("back_legs", "rotation", lambda u: [-10 + 8 * wave(u, 0.6), 0, 0])
loop_state("bee.angry_buzz", "Bee Angry Buzz", CAT, T, ALIVE + " && q.is_angry", 0.2, F, {
    "bone:rot": lambda u: tilt(22, 4 * wave(u), 0), "stinger:rot": lambda u: [20, 0, 0], "left_antenna:rot": lambda u: [-30, 0, 0], "right_antenna:rot": lambda u: [-30, 0, 0],
    "bone:pos": lambda u: move(0.2 * wave(u), 0.2 * wave(u, 0.3), 0)}, pri=140)
beat("bee.sting", "Bee Sting Lunge", CAT, T, event("melee_hit", ALIVE), 0.5, F, {
    "bone:rot": [(0, Z), (0.1, tilt(-30, 0, 0)), (0.2, tilt(60, 0, 0), "in_quart"), (0.5, Z)], "bone:pos": [(0, Z), (0.1, move(0, 0, -1)), (0.2, move(0, -1, 2)), (0.5, Z)],
    "stinger:rot": [(0, Z), (0.2, [40, 0, 0]), (0.5, Z)]}, pri=180)
life("bee.antenna_sense", "Bee Antenna Sensing", CAT, T, ALIVE, 1.1, F, {"left_antenna:rot": lambda u: [8 * wave(u), 0, -5 * wave(u, 0.3)], "right_antenna:rot": lambda u: [8 * wave(u, 0.5), 0, 5 * wave(u, 0.8)]})
loop_state("bee.pollinate", "Bee Pollinating", CAT, T, ALIVE + " && q.is_flying && !q.has_nectar && q.ground_speed < 0.01 && q.feet_block == 'foliage'", 0.6, F, {
    "bone:rot": lambda u: tilt(30, 0, 8 * wave(u, 0, 2)), "front_legs:rot": lambda u: [-30 + 15 * wave(u, 0, 2), 0, 0], "middle_legs:rot": lambda u: [-20 + 15 * wave(u, 0.5, 2), 0, 0]}, pri=135,
    layer="overlay")
c = mob("bee.crawl", "Bee Crawling", CAT, T, 0.4, state(WALKING + " && !q.is_flying"), layer="base", pri=103, file=F)
for b, ph in (("front_legs", 0.0), ("middle_legs", 0.33), ("back_legs", 0.66)):
    c.cycle(b, "rotation", lambda u, ph=ph: [-25 * wave(u, ph), 0, 0])
c.cycle("bone", "rotation", lambda u: tilt(0, 4 * wave(u, 0, 2), 0))
loop_state("bee.rest", "Bee Resting On Ground", CAT, T, STILL + " && !q.is_flying", 3.0, F, {
    "left_wing:rot": lambda u: [0, -40, 0], "right_wing:rot": lambda u: [0, 40, 0], "body:scl": lambda u: [1, 1 + 0.03 * wave(u), 1]}, pri=110)
beat("bee.waggle", "Bee Waggle Dance", CAT, T, event("vocalize", ALIVE + " && q.has_nectar"), 2.0, F, {
    "bone:rot": [(0, Z), (0.25, tilt(0, 30, 10)), (0.5, tilt(0, -30, -10)), (0.75, tilt(0, 30, 10)), (1.0, tilt(0, -30, -10)), (1.25, tilt(0, 30, 10)), (1.5, tilt(0, -30, -10)), (2.0, Z)],
    "bone:pos": [(0, Z), (1.0, move(0, 0, 2)), (2.0, Z)]}, pri=150)

# ============================================================================ bat
T, F = "minecraft:bat", f("bat")
loop_state("bat.roost_hang", "Bat Hanging Wrapped", CAT, T, ALIVE + " && q.is_sleeping", 4.0, F, {
    "right_wing:rot": lambda u: [0, 90, 0], "left_wing:rot": lambda u: [0, -90, 0], "right_wing_tip:rot": lambda u: [0, 80, 0], "left_wing_tip:rot": lambda u: [0, -80, 0],
    "mw_root:rot": lambda u: tilt(0, 0, 3 * wave(u))}, pri=120, layer="additive")
life("bat.ear_twitch", "Bat Ear Twitch", CAT, T, ALIVE + " && q.is_sleeping", 2.6, F, {"right_ear:rot": lambda u: [0, 0, 15 * spike(u, 0.2, 10)], "left_ear:rot": lambda u: [0, 0, -15 * spike(u, 0.7, 10)]})
c = mob("bat.flutter", "Bat Erratic Flutter", CAT, T, 0.3, state(ALIVE + " && !q.is_sleeping"), layer="additive", pri=60, file=F)
c.cycle("right_wing_tip", "rotation", lambda u: [0, -25 * wave(u, 0.15), 0])
c.cycle("left_wing_tip", "rotation", lambda u: [0, 25 * wave(u, 0.15), 0])
c.cycle("mw_root", "position", lambda u: move(0.3 * wave(u, 0, 0.5), 0.5 * wave(u), 0))
loop_state("bat.swoop", "Bat Swooping Dive", CAT, T, ALIVE + " && !q.is_sleeping && q.vertical_speed < -0.15", 0.4, F, {
    "right_wing:rot": lambda u: [0, -30, 0], "left_wing:rot": lambda u: [0, 30, 0], "mw_root:rot": lambda u: tilt(30, 0, 0)}, pri=110)
life("bat.banking_turn", "Bat Banking Turn", CAT, T, ALIVE + " && !q.is_sleeping && math.abs(q.turn_rate) > 6", 0.5, F, {"mw_root:rot": lambda u: tilt(-5, 0, 20 + 10 * wave(u, 0, 4))}, pri=62)
beat("bat.startle", "Bat Startled Awake", CAT, T, event("hurt", ALIVE), 0.5, F, {"right_wing:rot": [(0, Z), (0.1, [0, -80, 0]), (0.5, Z)], "left_wing:rot": [(0, Z), (0.1, [0, 80, 0]), (0.5, Z)],
                                                                               "head:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.5, Z)]}, pri=200, layer="reaction")
beat("bat.squeak", "Bat Squeak", CAT, T, event("vocalize", ALIVE), 0.4, F, {"head:rot": [(0, Z), (0.1, [-15, 10, 0]), (0.4, Z)], "right_ear:rot": [(0, Z), (0.1, [0, 0, 20]), (0.4, Z)]}, layer="gesture")

# ============================================================================ axolotl
T, F = "minecraft:axolotl", f("axolotl")
c = mob("axolotl.swim", "Axolotl Undulating Swim", CAT, T, 0.9, state(SWIM + " && q.ground_speed >= 0.02 && !q.is_playing_dead"), layer="base", file=F)
c.cycle("body", "rotation", lambda u: [0, 10 * wave(u), 0])
c.cycle("tail", "rotation", lambda u: [0, 30 * wave(u, 0.2), 0])
c.cycle("head", "rotation", lambda u: [0, -8 * wave(u, 0.9), 0])
for b in ("left_front_leg", "right_front_leg", "left_hind_leg", "right_hind_leg"):
    c.cycle(b, "rotation", lambda u, b=b: [80, 0, 0])
c = mob("axolotl.bottom_walk", "Axolotl Walking The Riverbed", CAT, T, 1.0, state(SWIM + " && q.is_on_ground && q.ground_speed >= 0.01"), layer="base", pri=101, file=F)
for b, ph in (("left_front_leg", 0.0), ("right_hind_leg", 0.0), ("right_front_leg", 0.5), ("left_hind_leg", 0.5)):
    c.cycle(b, "rotation", lambda u, ph=ph: [-30 * wave(u, ph), 20 * cwave(u, ph), 0])
c.cycle("body", "rotation", lambda u: [0, 8 * wave(u, 0.25), 0])
c.cycle("tail", "rotation", lambda u: [0, -14 * wave(u, 0.4), 0])
c = mob("axolotl.land_waddle", "Axolotl Land Waddle", CAT, T, 0.8, state(DRY + " && q.is_on_ground && q.ground_speed >= 0.01"), layer="base", pri=102, file=F)
for b, ph in (("left_front_leg", 0.0), ("right_hind_leg", 0.0), ("right_front_leg", 0.5), ("left_hind_leg", 0.5)):
    c.cycle(b, "rotation", lambda u, ph=ph: [-40 * wave(u, ph), 0, 25 * max(0, cwave(u, ph))])
c.cycle("body", "rotation", lambda u: [0, 16 * wave(u, 0.25), 6 * wave(u)])
c.cycle("tail", "rotation", lambda u: [0, -25 * wave(u, 0.45), 0])
loop_state("axolotl.play_dead", "Axolotl Playing Dead", CAT, T, ALIVE + " && q.is_playing_dead", 3.0, F, {
    "mw_center:rot": lambda u: tilt(0, 0, 170), "left_front_leg:rot": lambda u: [-20, 0, -40], "right_front_leg:rot": lambda u: [-20, 0, 40], "tail:rot": lambda u: [0, 4 * spike(u, 0.6, 20), 0],
    "top_gills:rot": lambda u: [-20, 0, 0]}, pri=180)
life("axolotl.gill_flutter", "Axolotl Gill Flutter", CAT, T, ALIVE, 1.2, F, {
    "top_gills:rot": lambda u: [-8 * wave(u), 0, 0], "left_gills:rot": lambda u: [0, -12 * wave(u, 0.2), 0], "right_gills:rot": lambda u: [0, 12 * wave(u, 0.2), 0]})
beat("axolotl.snap", "Axolotl Snapping Lunge", CAT, T, event("melee_hit", ALIVE), 0.5, F, {
    "head:rot": [(0, Z), (0.12, [-20, 0, 0]), (0.2, [10, 0, 0], "in_quart"), (0.5, Z)], "body:pos": [(0, Z), (0.12, move(0, 0, -1)), (0.2, move(0, 0, 3)), (0.5, Z)],
    "tail:rot": [(0, Z), (0.2, [0, 40, 0]), (0.5, Z)]}, pri=180)
c = mob("axolotl.hover", "Axolotl Floating Still", CAT, T, 3.0, state(SWIM + " && !q.is_on_ground && q.ground_speed < 0.02 && !q.is_playing_dead"), layer="base", pri=99, file=F)
c.cycle("mw_center", "position", lambda u: move(0, 0.5 * wave(u), 0))
c.cycle("tail", "rotation", lambda u: [0, 6 * wave(u, 0.3), 0])
for b in ("left_front_leg", "right_front_leg"):
    c.cycle(b, "rotation", lambda u, b=b: [30 + 15 * wave(u, 0.5), 0, (-20 if "left" in b else 20)])
loop_state("axolotl.dry_flop", "Axolotl Drying Out", CAT, T, DRY + " && q.ground_speed < 0.01", 0.7, F, {
    "body:rot": lambda u: [0, 0, 14 * wave(u)], "tail:rot": lambda u: [0, 30 * wave(u, 0.2), 0], "head:rot": lambda u: [-10 * max(0, wave(u, 0.1)), 0, 0]}, pri=110)
beat("axolotl.happy_wiggle", "Axolotl Happy Wiggle", CAT, T, event("interacted", ALIVE), 1.2, F, {
    "body:rot": [(0, Z), (0.2, [0, 20, 0]), (0.4, [0, -20, 0]), (0.6, [0, 20, 0]), (0.8, [0, -20, 0]), (1.2, Z)], "top_gills:rot": [(0, Z), (0.3, [-30, 0, 0]), (1.2, Z)]}, pri=150)

# ============================================================================ frog & tadpole
T, F = "minecraft:frog", f("frog")
beat("frog.leap", "Frog Leap", CAT, T, event("jump", ALIVE + " && !q.is_in_water"), 0.7, F, {
    "left_leg:rot": [(0, Z), (0.08, [30, 0, 0]), (0.2, [-70, 0, 0], "out_expo"), (0.55, [-40, 0, 0]), (0.7, Z)], "right_leg:rot": [(0, Z), (0.08, [30, 0, 0]), (0.2, [-70, 0, 0], "out_expo"), (0.55, [-40, 0, 0]), (0.7, Z)],
    "left_foot:rot": [(0, Z), (0.2, [60, 0, 0]), (0.7, Z)], "right_foot:rot": [(0, Z), (0.2, [60, 0, 0]), (0.7, Z)], "left_arm:rot": [(0, Z), (0.2, [40, 0, 0]), (0.55, [-40, 0, 0]), (0.7, Z)],
    "right_arm:rot": [(0, Z), (0.2, [40, 0, 0]), (0.55, [-40, 0, 0]), (0.7, Z)], "body:rot": [(0, Z), (0.2, [-15, 0, 0]), (0.55, [12, 0, 0]), (0.7, Z)]}, pri=150)
beat("frog.landing_squash", "Frog Landing Squash", CAT, T, event("land", ALIVE), 0.35, F, {
    "body:scl": [(0, [1, 1, 1]), (0.06, [1.15, 0.85, 1.1]), (0.2, [0.95, 1.05, 0.98]), (0.35, [1, 1, 1])], "head:rot": [(0, Z), (0.06, [10, 0, 0]), (0.35, Z)]}, layer="gesture")
loop_state("frog.croak", "Frog Croaking", CAT, T, ALIVE + " && q.is_on_ground && q.idle_time > 4 && q.is_night", 1.4, F, {
    "croaking_body:scl": lambda u: [1 + 0.9 * spike(u, 0, 3, 2), 1 + 0.9 * spike(u, 0, 3, 2), 1 + 0.4 * spike(u, 0, 3, 2)], "head:rot": lambda u: [-6 * spike(u, 0, 3, 2), 0, 0]},
    group="frog_idle", weight=3, layer="additive")
beat("frog.tongue_lash", "Frog Tongue Lash", CAT, T, event("melee_hit", ALIVE), 0.5, F, {
    "tongue:scl": [(0, [1, 1, 1]), (0.1, [1, 1, 6], "out_expo"), (0.25, [1, 1, 6]), (0.4, [1, 1, 1], "in_quad"), (0.5, [1, 1, 1])], "head:rot": [(0, Z), (0.1, [-14, 0, 0]), (0.4, Z)]}, pri=180)
c = mob("frog.swim_kick", "Frog Breaststroke Kick", CAT, T, 0.8, state(SWIM + " && q.ground_speed >= 0.01"), layer="base", file=F)
c.cycle("left_leg", "rotation", lambda u: [-60 * max(0, wave(u)) + 20, 0, -20 * max(0, cwave(u))])
c.cycle("right_leg", "rotation", lambda u: [-60 * max(0, wave(u)) + 20, 0, 20 * max(0, cwave(u))])
c.cycle("left_arm", "rotation", lambda u: [-50, 0, -10 * wave(u)])
c.cycle("right_arm", "rotation", lambda u: [-50, 0, 10 * wave(u)])
c.cycle("body", "rotation", lambda u: [-8 * wave(u, 0.1), 0, 0])
loop_state("frog.float", "Frog Floating At The Surface", CAT, T, SWIM + " && q.ground_speed < 0.01", 2.6, F, {
    "left_leg:rot": lambda u: [-70, 0, -30], "right_leg:rot": lambda u: [-70, 0, 30], "mw_center:pos": lambda u: move(0, 0.2 * wave(u), 0), "left_arm:rot": lambda u: [-30, 0, -20],
    "right_arm:rot": lambda u: [-30, 0, 20]}, pri=110)
life("frog.blink", "Frog Blink", CAT, T, ALIVE, 4.0, F, {"right_eye:scl": lambda u: [1, 1 - 0.8 * spike(u, 0.3, 30), 1], "left_eye:scl": lambda u: [1, 1 - 0.8 * spike(u, 0.3, 30), 1]})
loop_state("frog.look_around", "Frog Turning To Watch", CAT, T, STILL + " && q.idle_time > 3", 3.0, F, {"mw_center:rot": lambda u: tilt(0, 25 * (1 if wave(u) > 0.2 else (-1 if wave(u) < -0.2 else 0)), 0)},
           group="frog_idle", weight=2)
loop_state("frog.puffed_rain", "Frog Puffed Up In The Rain", CAT, T, STILL + " && q.is_raining && q.sky_exposed", 2.0, F, {
    "body:scl": lambda u: [1.06, 1.06 + 0.02 * wave(u), 1.06], "head:rot": lambda u: [-12, 0, 0], "eyes:pos": lambda u: move(0, 0.2, 0)}, group="frog_idle", weight=4)
loop_state("frog.hand_wipe", "Frog Wiping Its Eyes", CAT, T, STILL + " && q.idle_time > 6", 1.0, F, {
    "left_arm:rot": lambda u: [-120 * max(0, wave(u, 0, 0.5)), 0, 20], "left_hand:rot": lambda u: [30 * wave(u, 0, 2), 0, 0], "head:rot": lambda u: [8, -14, 0]}, group="frog_idle", weight=1)
T, F = "minecraft:tadpole", f("tadpole")
c = mob("tadpole.wiggle", "Tadpole Wiggle", CAT, T, 0.3, state(SWIM + " && q.ground_speed >= 0.01"), layer="base", file=F)
c.cycle("tail", "rotation", lambda u: [0, 40 * wave(u), 0])
c.cycle("body", "rotation", lambda u: [0, -8 * wave(u, 0.8), 0])
c = mob("tadpole.idle", "Tadpole Hovering", CAT, T, 1.6, state(SWIM + " && q.ground_speed < 0.01"), layer="base", file=F)
c.cycle("tail", "rotation", lambda u: [0, 12 * wave(u, 0, 2), 0])
c.cycle("mw_center", "position", lambda u: move(0, 0.3 * wave(u), 0))
loop_state("tadpole.stranded", "Tadpole Stranded", CAT, T, DRY, 0.5, F, {"body:rot": lambda u: [0, 0, 30 * wave(u)], "tail:rot": lambda u: [0, 50 * wave(u, 0.25), 0]}, pri=120)

# ============================================================================ sniffer
T, F = "minecraft:sniffer", f("sniffer")
SLEGS = ("left_front_leg", "left_mid_leg", "left_hind_leg", "right_front_leg", "right_mid_leg", "right_hind_leg")
c = mob("sniffer.plod", "Sniffer Six-Legged Plod", CAT, T, 2.2, state(WALKING + " && !q.is_sniffing && !q.is_digging"), layer="base", file=F, time="q.limb_swing * 0.233",
        weight="math.clamp(q.limb_swing_amount * 2.2, 0, 1)")
for b in SLEGS:
    ph = {"left_front_leg": 0.0, "right_mid_leg": 0.0, "left_hind_leg": 0.0, "right_front_leg": 0.5, "left_mid_leg": 0.5, "right_hind_leg": 0.5}[b]
    c.cycle(b, "rotation", lambda u, ph=ph: [-22 * cwave(u, ph), 0, 0])
c.cycle("mw_center", "rotation", lambda u: tilt(1, 0, 3 * wave(u)))
c.cycle("mw_center", "position", lambda u: move(0, -0.4 * (1 + cwave(u, 0, 2)), 0))
loop_state("sniffer.scenting", "Sniffer Scenting The Ground", CAT, T, ALIVE + " && q.is_sniffing", 1.2, F, {
    "head:rot": lambda u: [25 + 5 * spike(u, 0, 2, 4), 15 * wave(u, 0, 0.5), 0], "nose:rot": lambda u: [8 * spike(u, 0, 2, 4), 0, 0], "lower_beak:rot": lambda u: [6 * spike(u, 0.1, 2, 4), 0, 0]},
    pri=130, layer="additive")
loop_state("sniffer.dig", "Sniffer Digging Up Seeds", CAT, T, ALIVE + " && q.is_digging", 0.8, F, {
    "head:rot": lambda u: [55 + 15 * wave(u), 8 * wave(u, 0, 2), 0], "left_front_leg:rot": lambda u: [-20 * max(0, wave(u)), 0, 0], "right_front_leg:rot": lambda u: [-20 * max(0, wave(u, 0.5)), 0, 0],
    "mw_center:rot": lambda u: tilt(10, 0, 0)}, pri=135, layer="additive")
life("sniffer.ear_flap", "Sniffer Ear Flaps", CAT, T, ALIVE, 1.8, F, {"left_ear:rot": lambda u: [0, 0, -14 * wave(u)], "right_ear:rot": lambda u: [0, 0, 14 * wave(u, 0.15)]})
life("sniffer.nose_wiggle", "Sniffer Nose Wiggle", CAT, T, ALIVE + " && !q.is_sniffing", 2.4, F, {"nose:rot": lambda u: [5 * spike(u, 0.2, 4, 3), 0, 0], "nose:scl": lambda u: [1 + 0.05 * spike(u, 0.2, 4, 3)] * 3})
beat("sniffer.happy_rumble", "Sniffer Happy Rumble", CAT, T, event("vocalize", ALIVE), 1.6, F, {
    "head:rot": [(0, Z), (0.4, [-20, 0, 0]), (0.8, [-15, 0, 8]), (1.2, [-18, 0, -8]), (1.6, Z)], "lower_beak:rot": [(0, Z), (0.4, [20, 0, 0]), (1.0, [10, 0, 0]), (1.6, Z)],
    "mw_center:pos": [(0, Z), (0.4, move(0, 0.6, 0)), (1.6, Z)]}, layer="gesture")
beat("sniffer.rise_after_dig", "Sniffer Rising From A Dig", CAT, T, event("stop_moving", ALIVE + " && q.is_digging == 0", chance=0.2), 1.8, F, {
    "head:rot": [(0, [50, 0, 0]), (0.6, [-10, 0, 0]), (1.0, [-20, 0, 0]), (1.8, Z)], "mw_center:rot": [(0, tilt(10, 0, 0)), (0.6, tilt(-4, 0, 0)), (1.8, Z)]}, layer="gesture")
loop_state("sniffer.idle_gaze", "Sniffer Gazing Around", CAT, T, STILL + " && !q.is_sniffing && !q.is_digging", 6.0, F, {
    "head:rot": lambda u: [-5 + 12 * spike(u, 0.6, 4), 30 * wave(u), 10 * spike(u, 0.6, 4)], "left_ear:rot": lambda u: [0, 0, -20 * spike(u, 0.6, 4)]}, layer="additive", pri=55)
c = mob("sniffer.snifflet_toddle", "Snifflet Toddle", CAT, T, 0.9, state(WALKING + " && q.is_baby"), layer="base", pri=102, file=F)
for i, b in enumerate(("left_hind_leg", "left_mid_leg", "left_front_leg", "right_hind_leg", "right_mid_leg", "right_front_leg")):
    c.cycle(b, "rotation", lambda u, ph=(i % 3) / 3.0 + (0.5 if i >= 3 else 0): [-30 * cwave(u, ph), 0, 6 * max(0, wave(u, ph))])
c.cycle("mw_center", "rotation", lambda u: tilt(3 * wave(u, 0, 3), 0, 6 * wave(u)))
c.cycle("mw_center", "position", lambda u: move(0, 0.6 * max(0, wave(u, 0, 3)), 0))
c.cycle("head", "rotation", lambda u: [-6 * wave(u, 0.2, 3), 0, 0])
loop_state("sniffer.lie_down", "Sniffer Lying Down", CAT, T, STILL + " && q.idle_time > 25", 5.0, F, {
    "mw_center:pos": lambda u: move(0, -6, 0), "left_front_leg:rot": lambda u: [-80, 0, 0], "right_front_leg:rot": lambda u: [-80, 0, 0], "left_mid_leg:rot": lambda u: [0, 0, -70],
    "right_mid_leg:rot": lambda u: [0, 0, 70], "left_hind_leg:rot": lambda u: [80, 0, 0], "right_hind_leg:rot": lambda u: [80, 0, 0], "head:rot": lambda u: [20 + 2 * wave(u), 0, 0]}, pri=110)

# ============================================================================ aquatic
T, F = "minecraft:dolphin", f("dolphin")
c = mob("dolphin.swim", "Dolphin Fluke Strokes", CAT, T, 0.7, state(SWIM + " && q.ground_speed >= 0.05"), layer="base", file=F)
c.cycle("body", "rotation", lambda u: [4 * wave(u), 0, 0])
c.cycle("tail", "rotation", lambda u: [-14 * wave(u, 0.15), 0, 0])
c.cycle("tail_fin", "rotation", lambda u: [-22 * wave(u, 0.3), 0, 0])
c.cycle("left_fin", "rotation", lambda u: [0, 0, -10 + 4 * wave(u)])
c.cycle("right_fin", "rotation", lambda u: [0, 0, 10 - 4 * wave(u)])
c = mob("dolphin.leap", "Dolphin Breaching Leap", CAT, T, 1.0, state(ALIVE + " && !q.is_in_water && !q.is_on_ground"), layer="base", pri=110, file=F)
c.cycle("tail", "rotation", lambda u: [20, 0, 0])
c.cycle("tail_fin", "rotation", lambda u: [30, 0, 0])
c.cycle("left_fin", "rotation", lambda u: [0, 0, -40])
c.cycle("right_fin", "rotation", lambda u: [0, 0, 40])
c = mob("dolphin.surface_bob", "Dolphin Bobbing At The Surface", CAT, T, 2.4, state(SWIM + " && q.ground_speed < 0.05 && !q.is_underwater"), layer="base", pri=99, file=F)
c.cycle("mw_center", "position", lambda u: move(0, 0.6 * wave(u), 0))
c.cycle("mw_center", "rotation", lambda u: tilt(-10 + 4 * wave(u, 0.2), 0, 3 * wave(u, 0.5)))
c.cycle("tail_fin", "rotation", lambda u: [-8 * wave(u, 0.3), 0, 0])
loop_state("dolphin.play_spin", "Dolphin Playful Barrel Roll", CAT, T, SWIM + " && q.is_underwater && q.trait_energy > 0.4 && q.ground_speed >= 0.05", 1.6, F, {
    "mw_center:rot": lambda u: tilt(0, 0, 360 * u)}, group="dolphin_play", weight=1, layer="additive", pri=70)
beat("dolphin.click_nod", "Dolphin Click Nod", CAT, T, event("vocalize", ALIVE), 0.8, F, {"head:rot": [(0, Z), (0.15, [-14, 0, 0]), (0.3, [6, 0, 0]), (0.45, [-10, 0, 0]), (0.8, Z)],
                                                                                    "nose:rot": [(0, Z), (0.15, [-6, 0, 0]), (0.8, Z)]}, layer="gesture")
loop_state("dolphin.beached", "Dolphin Beached Thrash", CAT, T, DRY + " && q.is_on_ground", 0.6, F, {
    "body:rot": lambda u: [0, 0, 12 * wave(u)], "tail:rot": lambda u: [-25 * wave(u, 0.2), 0, 0], "tail_fin:rot": lambda u: [-30 * wave(u, 0.35), 0, 0]}, pri=120)
loop_state("dolphin.chase_sprint", "Dolphin Racing Ahead", CAT, T, SWIM + " && q.ground_speed >= 0.25", 0.4, F, {
    "tail:rot": lambda u: [-20 * wave(u, 0.1), 0, 0], "tail_fin:rot": lambda u: [-35 * wave(u, 0.25), 0, 0], "left_fin:rot": lambda u: [0, 0, -30], "right_fin:rot": lambda u: [0, 0, 30]}, pri=115)
life("dolphin.blowhole_breath", "Dolphin Blowhole Breath", CAT, T, SWIM + " && !q.is_underwater", 3.0, F, {"back_fin:rot": lambda u: [0, 0, 4 * spike(u, 0.2, 6)], "body:scl": lambda u: [1, 1 + 0.03 * spike(u, 0.2, 6), 1]})

for T, sp, label, glow in (("minecraft:squid", "squid", "Squid", False), ("minecraft:glow_squid", "glow_squid", "Glow Squid", True)):
    F = f(sp)
    c = mob(sp + ".jet", label + (" Shimmering Jet" if glow else " Jet Pulse"), CAT, T, 1.0 if glow else 0.8, state(SWIM + " && q.ground_speed >= 0.02"), layer="base", file=F)
    for i in range(8):
        c.cycle("tentacle%d" % i, "rotation", lambda u, i=i, g=glow: [-60 * max(0, wave(u, 0.05 * i if g else 0)) + 20, 0, 0])
    c.cycle("body", "scale", lambda u: [1 + 0.08 * max(0, -wave(u)), 1 - 0.06 * max(0, -wave(u)), 1 + 0.08 * max(0, -wave(u))])
    c = mob(sp + ".drift", label + (" Spiral Drift" if glow else " Drifting"), CAT, T, 3.0 if glow else 2.4, state(SWIM + " && q.ground_speed < 0.02"), layer="base", pri=99, file=F)
    for i in range(8):
        c.cycle("tentacle%d" % i, "rotation", lambda u, i=i, g=glow: [10 + 10 * wave(u, i / 8.0 if g else i / 16.0), 6 * wave(u, i / 8.0) if g else 0, 0])
    c.cycle("mw_center", "position", lambda u: move(0, 0.5 * wave(u), 0))
    if glow:
        c.cycle("mw_center", "rotation", lambda u: tilt(0, 30 * wave(u, 0, 0.5), 0))
    if glow:
        beat(sp + ".ink_burst", label + " Glow Ink Flare", CAT, T, event("hurt", ALIVE), 1.2, F, {
            "body:scl": [(0, [1, 1, 1]), (0.25, [1.15, 1.15, 1.15], "out_quad"), (0.5, [0.9, 1.0, 0.9]), (0.8, [1.08, 1.08, 1.08]), (1.2, [1, 1, 1])],
            "mw_center:rot": [(0, Z), (0.3, tilt(0, 90, 0)), (1.2, Z)]}, pri=200, layer="reaction",
            events=[(0.25, "particle", {"particle": "magic_glint", "count": "14", "at": "body", "spread": "0.7"})])
    else:
        beat(sp + ".ink_burst", label + " Ink Burst", CAT, T, event("hurt", ALIVE), 0.7, F, {
            "body:scl": [(0, [1, 1, 1]), (0.1, [1.25, 0.8, 1.25]), (0.3, [0.92, 1.1, 0.92]), (0.7, [1, 1, 1])], "mw_center:pos": [(0, Z), (0.15, move(0, 3, 0)), (0.7, Z)]},
            pri=200, layer="reaction", events=[(0.1, "particle", {"particle": "smoke_wisp", "count": "12", "at": "body", "spread": "0.6"})])
F, T = f("squid"), "minecraft:squid"
loop_state("squid.beached_writhe", "Squid Beached Writhe", CAT, T, DRY, 0.9, F, {"tentacle%d:rot" % i: (lambda u, i=i: [40 * wave(u, i / 8.0), 0, 0]) for i in range(8)}, pri=120)
life("squid.tentacle_curl", "Squid Tentacle Curl", CAT, T, SWIM, 3.4, F, {"tentacle%d:rot" % i: (lambda u, i=i: [0, 0, 12 * spike(u, i / 8.0, 6)]) for i in range(0, 8, 2)})
F, T = f("glow_squid"), "minecraft:glow_squid"
life("glow_squid.pulse_glow", "Glow Squid Breathing Pulse", CAT, T, SWIM, 2.0, F, {"body:scl": lambda u: [1 + 0.04 * wave(u, 0, 2)] * 3})

FISH = {
    "cod": ("minecraft:cod", "Cod", "tail_fin", ["right_fin", "left_fin"], 0.5, 22),
    "salmon": ("minecraft:salmon", "Salmon", "back_fin", ["right_fin", "left_fin"], 0.4, 26),
    "tropical_fish": ("minecraft:tropical_fish", "Tropical Fish", "tail", ["right_fin", "left_fin"], 0.35, 30),
}
for sp, (T, label, tail, fins, L, amp) in FISH.items():
    F = f(sp)
    c = mob(sp + ".swim", label + " Swimming", CAT, T, L, state(SWIM + " && q.ground_speed >= 0.02"), layer="base", file=F)
    c.cycle(tail, "rotation", lambda u, a=amp: [0, a * wave(u), 0])
    c.cycle(fins[0], "rotation", lambda u: [0, 20 * wave(u, 0.25), 0])
    c.cycle(fins[1], "rotation", lambda u: [0, -20 * wave(u, 0.25), 0])
    if sp == "salmon":
        c.cycle("body_back", "rotation", lambda u: [0, 14 * wave(u, 0.85), 0])
    c = mob(sp + ".hover", label + " Holding Station", CAT, T, L * 4, state(SWIM + " && q.ground_speed < 0.02"), layer="base", pri=99, file=F)
    c.cycle(tail, "rotation", lambda u, a=amp: [0, a * 0.3 * wave(u, 0, 3), 0])
    c.cycle(fins[0], "rotation", lambda u: [0, 30 * wave(u, 0, 2), 0])
    c.cycle(fins[1], "rotation", lambda u: [0, -30 * wave(u, 0.5, 2), 0])
    c.cycle("mw_center", "position", lambda u: move(0, 0.2 * wave(u), 0))
    beat(sp + ".dart", label + " Startled Dart", CAT, T, event("hurt", ALIVE + " && q.is_in_water"), 0.4, F, {
        tail + ":rot": [(0, Z), (0.05, [0, 40, 0]), (0.12, [0, -40, 0]), (0.2, [0, 30, 0]), (0.4, Z)], "mw_center:rot": [(0, Z), (0.05, tilt(0, 30, 0)), (0.4, Z)]}, pri=200, layer="reaction")
    loop_state(sp + ".flop", label + " Flopping On Land", CAT, T, DRY, L + 0.2, F, {
        "mw_center:rot": lambda u: tilt(0, 0, 90), "mw_center:pos": lambda u: move(0, 0.8 * max(0, wave(u)), 0), tail + ":rot": lambda u, a=amp: [0, a * 1.5 * wave(u, 0.2), 0]}, pri=120)
T, F = "minecraft:pufferfish", f("pufferfish")
c = mob("pufferfish.paddle", "Pufferfish Fin Paddle", CAT, T, 0.5, state(SWIM + " && q.ground_speed >= 0.01"), layer="base", file=F)
c.cycle("right_blue_fin", "rotation", lambda u: [0, 0, 30 * wave(u)])
c.cycle("left_blue_fin", "rotation", lambda u: [0, 0, -30 * wave(u)])
c.cycle("mw_center", "rotation", lambda u: tilt(4 * wave(u, 0, 2), 0, 0))
c = mob("pufferfish.drift", "Pufferfish Bobbing Drift", CAT, T, 2.6, state(SWIM + " && q.ground_speed < 0.01"), layer="base", pri=99, file=F)
c.cycle("mw_center", "position", lambda u: move(0, 0.5 * wave(u), 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 20 * wave(u, 0, 0.5), 5 * wave(u)))
c.cycle("right_blue_fin", "rotation", lambda u: [0, 0, 12 * wave(u, 0, 3)])
c.cycle("left_blue_fin", "rotation", lambda u: [0, 0, -12 * wave(u, 0.5, 3)])
beat("pufferfish.alarm_puff", "Pufferfish Alarm Puff", CAT, T, event("hurt", ALIVE), 1.0, F, {
    "mw_center:rot": [(0, Z), (0.1, tilt(0, 0, 25)), (0.2, tilt(0, 0, -20)), (0.35, tilt(0, 0, 10)), (1.0, Z)], "right_blue_fin:rot": [(0, Z), (0.1, [0, 0, 70]), (1.0, Z)],
    "left_blue_fin:rot": [(0, Z), (0.1, [0, 0, -70]), (1.0, Z)]}, pri=200, layer="reaction")
life("pufferfish.spine_bristle", "Pufferfish Spine Bristle", CAT, T, SWIM + " && q.player_distance < 3", 0.4, F, {
    "top_front_fin:rot": lambda u: [-20 - 6 * wave(u), 0, 0], "top_back_fin:rot": lambda u: [20 + 6 * wave(u, 0.5), 0, 0], "bottom_front_fin:rot": lambda u: [20 + 6 * wave(u, 0.25), 0, 0]})
loop_state("pufferfish.flop", "Pufferfish Stranded Roll", CAT, T, DRY, 0.8, F, {"mw_center:rot": lambda u: tilt(0, 0, 40 * wave(u)), "mw_center:pos": lambda u: move(0, 0.5 * max(0, wave(u, 0, 2)), 0)},
           pri=120)

# ============================================================================ strider
T, F = "minecraft:strider", f("strider")
BRISTLES = ["right_bottom_bristle", "right_middle_bristle", "right_top_bristle", "left_top_bristle", "left_middle_bristle", "left_bottom_bristle"]
loop_state("strider.shiver", "Strider Shivering Out Of Lava", CAT, T, ALIVE + " && q.is_suffocating", 0.2, F, {
    "body:rot": lambda u: [0, 0, 3 * wave(u)], "mw_center:pos": lambda u: move(0.2 * wave(u, 0.25), 0, 0), **{b + ":rot": (lambda u, i=i: [0, 0, (-1) ** i * 6 * wave(u, i / 6.0)]) for i, b in enumerate(BRISTLES)}},
    pri=130)
life("strider.bristle_wave", "Strider Bristles Rippling", CAT, T, ALIVE + " && !q.is_suffocating", 1.4, F, {b + ":rot": (lambda u, i=i: [0, 0, (1 if "right" in BRISTLES[i] else -1) * 12 * wave(u, i / 6.0)])
                                                                                                      for i, b in enumerate(BRISTLES)})
loop_state("strider.lava_wade", "Strider Content In Lava", CAT, T, ALIVE + " && q.is_in_lava && q.ground_speed < 0.02", 3.0, F, {
    "body:rot": lambda u: [0, 6 * wave(u), 3 * wave(u, 0.3)], "mw_center:pos": lambda u: move(0, 0.4 * wave(u), 0)}, pri=115)
c = mob("strider.tall_stride", "Strider Stilt Stride", CAT, T, 1.2, state(WALKING + " && !q.is_suffocating"), layer="base", file=F, time="q.limb_swing * 0.2", weight="math.clamp(q.limb_swing_amount * 2, 0, 1)")
c.cycle("right_leg", "rotation", lambda u: [-30 * cwave(u), 0, 6 * max(0, wave(u))])
c.cycle("left_leg", "rotation", lambda u: [30 * cwave(u), 0, -6 * max(0, -wave(u))])
c.cycle("body", "rotation", lambda u: [0, 8 * cwave(u), 6 * wave(u)])
c.cycle("mw_center", "position", lambda u: move(0, -0.8 * (1 + cwave(u, 0, 2)), 0))
c = mob("strider.cold_shuffle", "Strider Cold Shuffle", CAT, T, 0.8, state(WALKING + " && q.is_suffocating"), layer="base", pri=101, file=F)
c.cycle("right_leg", "rotation", lambda u: [-14 * cwave(u), 0, 0])
c.cycle("left_leg", "rotation", lambda u: [14 * cwave(u), 0, 0])
c.cycle("body", "rotation", lambda u: [8, 0, 4 * wave(u, 0, 2)])
c.cycle("mw_center", "position", lambda u: move(0, -1.5, 0))
beat("strider.warble", "Strider Warble", CAT, T, event("vocalize", ALIVE), 0.9, F, {"body:rot": [(0, Z), (0.2, [-10, 0, 0]), (0.4, [6, 0, 4]), (0.6, [-6, 0, -4]), (0.9, Z)],
                                                                                **{b + ":rot": [(0, Z), (0.3, [0, 0, (20 if "right" in b else -20)]), (0.9, Z)] for b in BRISTLES[:2]}}, layer="gesture")
loop_state("strider.idle_look", "Strider Looking Around", CAT, T, STILL + " && !q.is_suffocating", 4.0, F, {"body:rot": lambda u: [0, 35 * wave(u), 0]}, pri=105)

# ============================================================================ allay
T, F = "minecraft:allay", f("allay")
loop_state("allay.dance", "Allay Jukebox Dance", CAT, T, ALIVE + " && q.is_dancing", 0.8, F, {
    "root:rot": lambda u: [0, 360 * u, 10 * wave(u, 0, 2)], "right_arm:rot": lambda u: [-150 + 20 * wave(u, 0, 2), 0, 20], "left_arm:rot": lambda u: [-150 + 20 * wave(u, 0.5, 2), 0, -20],
    "head:rot": lambda u: [0, 0, 12 * wave(u, 0, 2)]}, pri=150, layer="overlay")
loop_state("allay.cradle_item", "Allay Cradling An Item", CAT, T, ALIVE + " && q.is_holding && !q.is_dancing", 1.6, F, {
    "right_arm:rot": lambda u: [-60, 0, -14], "left_arm:rot": lambda u: [-60, 0, 14], "body:rot": lambda u: [6 + 3 * wave(u), 0, 0], "head:rot": lambda u: [14, 0, 0]}, pri=130, layer="overlay")
c = mob("allay.hover_bob", "Allay Hover Bob", CAT, T, 2.0, state(ALIVE + " && q.ground_speed < 0.03 && !q.is_dancing"), layer="additive", pri=60, file=F)
c.cycle("root", "position", lambda u: move(0, 0.6 * wave(u), 0))
c.cycle("right_wing", "rotation", lambda u: [0, -20 - 15 * wave(u, 0, 4), 0])
c.cycle("left_wing", "rotation", lambda u: [0, 20 + 15 * wave(u, 0, 4), 0])
loop_state("allay.glide_forward", "Allay Gliding Ahead", CAT, T, ALIVE + " && q.ground_speed >= 0.03 && !q.is_dancing", 0.8, F, {
    "body:rot": lambda u: [25, 0, 0], "right_arm:rot": lambda u: [30, 0, 10], "left_arm:rot": lambda u: [30, 0, -10], "right_wing:rot": lambda u: [0, -40 - 25 * wave(u, 0, 2), 0],
    "left_wing:rot": lambda u: [0, 40 + 25 * wave(u, 0, 2), 0]}, pri=110, layer="base")
beat("allay.wave", "Allay Friendly Wave", CAT, T, event("interacted", ALIVE), 1.2, F, {
    "right_arm:rot": [(0, Z), (0.2, [-160, 0, 20]), (0.4, [-160, 0, 50]), (0.6, [-160, 0, 20]), (0.8, [-160, 0, 50]), (1.2, Z)], "head:rot": [(0, Z), (0.2, [0, 0, -12]), (1.0, [0, 0, -12]), (1.2, Z)]},
    pri=160, layer="gesture")
beat("allay.twirl", "Allay Delighted Twirl", CAT, T, event("vocalize", ALIVE), 1.0, F, {"root:rot": [(0, Z), (1.0, [0, 360, 0], "in_out_sine")],
                                                                                   "right_arm:rot": [(0, Z), (0.5, [-40, 0, 60]), (1.0, Z)], "left_arm:rot": [(0, Z), (0.5, [-40, 0, -60]), (1.0, Z)]},
     layer="gesture")
loop_state("allay.follow_glance", "Allay Glancing Back At Its Friend", CAT, T, ALIVE + " && q.player_distance < 8 && q.ground_speed >= 0.03", 3.0, F, {
    "head:rot": lambda u: [0, 50 * spike(u, 0.3, 4), 0]}, pri=62, layer="additive")
loop_state("allay.idle_hum", "Allay Humming To Itself", CAT, T, ALIVE + " && !q.is_holding && !q.is_dancing && q.ground_speed < 0.03", 2.4, F, {
    "right_arm:rot": lambda u: [-20 + 10 * wave(u), 0, 10 + 6 * wave(u, 0.25)], "left_arm:rot": lambda u: [-20 + 10 * wave(u, 0.5), 0, -10 - 6 * wave(u, 0.75)],
    "head:rot": lambda u: [4 * wave(u, 0, 2), 0, 8 * wave(u)]}, pri=105, layer="overlay")

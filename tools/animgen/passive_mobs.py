"""Passive animals part 1: farm animals, bears, goats, camelids, turtles, equines.

Every species gets its own locomotion character (footfall pattern, duty factor, sway), a pool of
idle behaviours chosen deterministically per individual, and reactions bound to real game state.
"""
from mobkit import mob, gait, life, loop_state, beat, quad_lie, chew, Z, QLEGS, state, event, wave, cwave, tilt, move, Clip

CAT = "passive_mobs"
ALIVE = "!q.is_dead"
STILL = ALIVE + " && q.is_on_ground && !q.is_in_water && q.ground_speed < 0.01"
WALKING = ALIVE + " && q.is_on_ground && q.ground_speed >= 0.01"
PANIC = " && (q.recent_hurt < 6 || q.ground_speed > 0.17)"
CALM = " && q.recent_hurt >= 6 && q.ground_speed <= 0.17"


def f(name):
    return "mobs/passive/" + name


# ============================================================================ cow
T, F = "minecraft:cow", f("cow")
gait("cow.walk", "Cow Plodding Walk", CAT, T, WALKING + CALM + " && !q.is_baby", 1.6, F, gait="walk", stride=22, duty=0.64, bob=0.5, pitch=1.2, roll=2.2, yaw=1.5)
gait("cow.panic", "Cow Lumbering Stampede", CAT, T, WALKING + PANIC + " && !q.is_baby", 0.9, F, pri=101, gait="trot", stride=34, duty=0.5, bob=1.5, pitch=3, roll=1.0)
gait("cow.calf_frolic", "Calf Frolic", CAT, T, WALKING + " && q.is_baby", 0.7, F, pri=102, gait="bound", stride=30, duty=0.45, bob=2.6, pitch=5, roll=0.5, yaw=3, snap=0.2)
loop_state("cow.graze", "Cow Grazing", CAT, T, STILL + " && q.idle_time > 3", 4.0, F, {
    "head:rot": lambda u: [52 + 4 * wave(u, 0, 2), 6 * wave(u), chew(u, 6, 2)], "mw_center:rot": lambda u: tilt(4, 0, 0),
    "left_front_leg:rot": lambda u: [-6, 0, 0]}, group="cow_idle", weight=3)
loop_state("cow.ruminate", "Cow Chewing Cud", CAT, T, STILL + " && q.idle_time > 3", 3.0, F, {
    "head:rot": lambda u: [10, 4 * wave(u, 0, 6), 3 * cwave(u, 0, 6)], "mw_center:pos": lambda u: move(0, 0.15 * wave(u), 0)}, group="cow_idle", weight=2)
c = mob("cow.lie_rest", "Cow Lying Down To Rest", CAT, T, 6.0, state(STILL + " && q.idle_time > 20 && !q.is_baby", group="cow_idle", weight=1), file=F, blend_in=1.4, blend_out=1.0)
c.cycle("mw_center", "position", lambda u: move(0, -7.5 + 0.2 * wave(u), 0))
c.cycle("head", "rotation", lambda u: [15 + 3 * wave(u, 0.3), 25 * wave(u, 0, 0.5), 0])
for b in QLEGS:
    c.cycle(b, "rotation", lambda u, b=b: [-85 if "front" in b else 80, 0, (-12 if "left" in b else 12) if "hind" in b else 0])
life("cow.fly_swat", "Cow Swatting Flies", CAT, T, ALIVE + " && q.is_on_ground && !q.is_night", 5.0, F, {
    "head:rot": lambda u: [0, 22 * max(0, wave(u, 0.1, 1)) ** 6, 8 * max(0, wave(u, 0.1, 1)) ** 6], "mw_center:rot": lambda u: tilt(0, 0, 1.5 * max(0, wave(u, 0.6, 3)) ** 8)})
beat("cow.moo", "Cow Moo", CAT, T, event("vocalize", ALIVE), 1.6, F, {"head:rot": [(0, Z), (0.35, [-22, 0, 0], "out_quad"), (1.1, [-26, 0, 2]), (1.6, Z, "in_out_sine")],
                                                                     "mw_center:pos": [(0, Z), (0.35, move(0, 0, 0.6)), (1.6, Z)]}, layer="gesture")
beat("cow.hoof_stamp", "Cow Hoof Stamp", CAT, T, event("stop_moving", ALIVE + " && !q.is_baby", chance=0.35), 0.9, F, {
    "right_front_leg:rot": [(0, Z), (0.25, [-28, 0, 0], "out_quad"), (0.4, [4, 0, 0], "in_quart"), (0.55, [-10, 0, 0]), (0.7, [2, 0, 0]), (0.9, Z)],
    "head:rot": [(0, Z), (0.4, [8, 0, 0]), (0.9, Z)]}, layer="gesture")
loop_state("cow.love_nuzzle", "Cow Affectionate Sway", CAT, T, ALIVE + " && q.is_in_love", 2.4, F, {
    "head:rot": lambda u: [20 + 6 * wave(u, 0, 2), 18 * wave(u), 10 * wave(u)], "mw_center:rot": lambda u: tilt(0, 0, 2.5 * wave(u, 0.25))}, pri=125)

# ============================================================================ mooshroom
T, F = "minecraft:mooshroom", f("mooshroom")
gait("mooshroom.walk", "Mooshroom Spongy Amble", CAT, T, WALKING + CALM, 1.7, F, gait="amble", stride=20, duty=0.66, bob=0.9, pitch=0.8, roll=3.0)
gait("mooshroom.panic", "Mooshroom Panicked Gallop", CAT, T, WALKING + PANIC, 0.8, F, pri=101, gait="gallop", stride=32, duty=0.42, bob=1.8, pitch=4, roll=1.5, lift=14, roll_phase=0.3)
loop_state("mooshroom.graze_mycelium", "Mooshroom Snuffling Mycelium", CAT, T, STILL + " && q.idle_time > 3", 3.2, F, {
    "head:rot": lambda u: [58 + 6 * max(0, wave(u, 0, 4)), 14 * wave(u, 0, 0.5), 0], "mw_center:rot": lambda u: tilt(5, 0, 1.2 * wave(u))}, group="moosh_idle", weight=3)
beat("mooshroom.spore_shake", "Mooshroom Spore Shake", CAT, T, event("vocalize", ALIVE), 1.4, F, {
    "mw_center:rot": [(0, Z), (0.2, tilt(0, 0, 9)), (0.35, tilt(0, 0, -9)), (0.5, tilt(0, 0, 7)), (0.65, tilt(0, 0, -6)), (0.8, tilt(0, 0, 3)), (1.4, Z)],
    "head:rot": [(0, Z), (0.2, [0, -14, 10]), (0.35, [0, 14, -10]), (0.5, [0, -10, 6]), (0.8, Z)]}, layer="gesture",
    events=[(0.3, "particle", {"particle": "pollen", "count": "10", "at": "body", "spread": "0.6"})])
c = mob("mooshroom.lie_lean", "Mooshroom Leaning Rest", CAT, T, 7.0, state(STILL + " && q.idle_time > 20", group="moosh_idle", weight=1), file=F, blend_in=1.5, blend_out=1.0)
c.cycle("mw_center", "position", lambda u: move(0, -6.5, 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 14 + 0.8 * wave(u)))
c.cycle("head", "rotation", lambda u: [24, -18, 8 + 2 * wave(u, 0.4)])
for b in QLEGS:
    c.cycle(b, "rotation", lambda u, b=b: [-70 if "front" in b else 65, 0, 20 if "left" in b else 6])
loop_state("mooshroom.sniff_ground", "Mooshroom Sniffing Around", CAT, T, STILL + " && q.idle_time > 3", 2.0, F, {
    "head:rot": lambda u: [30 + 10 * wave(u, 0, 1), 30 * wave(u, 0.25), 0]}, group="moosh_idle", weight=2)
gait("mooshroom.calf_hop", "Mooshroom Calf Hops", CAT, T, WALKING + " && q.is_baby", 0.6, F, pri=102, gait="pace", stride=26, duty=0.5, bob=3.0, pitch=2, roll=4)
life("mooshroom.rain_shiver", "Mooshroom Rain Shiver", CAT, T, ALIVE + " && q.is_raining && q.sky_exposed", 0.5, F, {
    "mw_center:rot": lambda u: tilt(0, 0, 0.8 * wave(u, 0, 2)), "head:rot": lambda u: [0, 0.6 * wave(u, 0.3, 2), 0]})

# ============================================================================ pig
T, F = "minecraft:pig", f("pig")
gait("pig.trot", "Pig Trotting", CAT, T, WALKING + CALM, 0.9, F, gait="trot", stride=26, duty=0.55, bob=0.7, pitch=2.5, roll=1.2)
gait("pig.bolt", "Pig Squealing Bolt", CAT, T, WALKING + PANIC, 0.45, F, pri=101, gait="gallop", stride=36, duty=0.4, bob=1.4, pitch=6, roll=2.5, snap=0.35, front_scale=0.8)
loop_state("pig.root", "Pig Rooting In Dirt", CAT, T, STILL + " && q.idle_time > 3", 1.6, F, {
    "head:rot": lambda u: [48 + 8 * max(0, wave(u, 0, 4)), 8 * wave(u), 4 * wave(u, 0, 4)], "mw_center:pos": lambda u: move(0, 0, 0.4 * max(0, wave(u, 0, 4))),
    "mw_center:rot": lambda u: tilt(6, 0, 0)}, group="pig_idle", weight=3)
loop_state("pig.sniff_air", "Pig Sniffing The Air", CAT, T, STILL + " && q.idle_time > 3", 2.2, F, {
    "head:rot": lambda u: [-18 + 3 * max(0, wave(u, 0, 7)), 15 * wave(u, 0, 0.5), 0]}, group="pig_idle", weight=2)
c = mob("pig.wallow", "Pig Wallowing On Its Side", CAT, T, 5.0, state(STILL + " && q.idle_time > 18 && (q.surface == 'dirt' || q.feet_block == 'mud' || q.is_raining)", group="pig_idle", weight=2),
        file=F, blend_in=1.2, blend_out=0.9)
c.cycle("mw_center", "position", lambda u: move(0, -4.5, 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 82 + 5 * wave(u)))
c.cycle("head", "rotation", lambda u: [0, 0, 8 * wave(u, 0.2)])
for b in QLEGS:
    c.cycle(b, "rotation", lambda u, b=b: [-25 * wave(u, 0 if "front" in b else 0.5), 0, 8])
beat("pig.oink", "Pig Oink Nod", CAT, T, event("vocalize", ALIVE), 0.6, F, {"head:rot": [(0, Z), (0.1, [-10, 0, 0]), (0.2, [6, 0, 0]), (0.3, [-8, 0, 0]), (0.42, [4, 0, 0]), (0.6, Z)]},
     layer="gesture")
c = mob("pig.sleep", "Pig Sleeping Belly-Down", CAT, T, 3.4, state(STILL + " && q.is_night && q.idle_time > 25", group="pig_idle", weight=4), file=F, blend_in=1.5, blend_out=1.0)
c.cycle("mw_center", "position", lambda u: move(0, -5 + 0.35 * wave(u), 0))
c.cycle("body", "scale", lambda u: [1 + 0.03 * wave(u), 1 + 0.03 * wave(u), 1])
c.cycle("head", "rotation", lambda u: [22 - 4 * max(0, wave(u, 0.1)), 0, 4])
for b in QLEGS:
    c.cycle(b, "rotation", lambda u, b=b: [-60 if "front" in b else 70, 0, (14 if "right" in b else -14)])
gait("pig.piglet_scamper", "Piglet Scamper", CAT, T, WALKING + " && q.is_baby", 0.38, F, pri=102, gait="pace", stride=30, duty=0.48, bob=1.6, pitch=1, roll=6)
beat("pig.mud_shake", "Pig Shakes Off Water", CAT, T, event("exit_water", ALIVE), 1.0, F, {
    "mw_center:rot": [(0, Z), (0.12, tilt(0, 0, 14)), (0.24, tilt(0, 0, -14)), (0.36, tilt(0, 0, 11)), (0.48, tilt(0, 0, -9)), (0.6, tilt(0, 0, 5)), (1.0, Z)],
    "head:rot": [(0, Z), (0.12, [0, 0, -18]), (0.24, [0, 0, 18]), (0.36, [0, 0, -12]), (0.6, Z)]}, layer="gesture",
    events=[(0.15, "particle", {"particle": "splash", "count": "12", "at": "body", "spread": "0.5"})])
life("pig.rump_wiggle", "Pig Rump Wiggle", CAT, T, WALKING + CALM, 1.8, F, {"mw_center:rot": lambda u: tilt(0, 3 * wave(u, 0, 2), 0)})
loop_state("pig.beg_carrot", "Pig Following Food Eagerly", CAT, T, ALIVE + " && q.player_distance < 4 && q.is_in_love == 0 && q.trait_social > 0.6 && q.ground_speed < 0.05",
           1.2, F, {"head:rot": lambda u: [-12 + 4 * wave(u, 0, 2), 6 * wave(u), 0], "mw_center:pos": lambda u: move(0, 0.4 * max(0, wave(u, 0, 2)), 0)}, pri=115)

# ============================================================================ sheep
T, F = "minecraft:sheep", f("sheep")
gait("sheep.walk", "Sheep Woolly Walk", CAT, T, WALKING + CALM + " && !q.is_baby", 1.3, F, gait="walk", stride=20, duty=0.6, bob=0.6, pitch=1.0, roll=1.6, splay=5, roll_phase=0.15)
gait("sheep.flee", "Sheep Flock Flight", CAT, T, WALKING + PANIC + " && !q.is_baby", 0.6, F, pri=101, gait="bound", stride=32, duty=0.42, bob=2.2, pitch=5, roll=0.6, lift=14, splay=6)
gait("sheep.lamb_skip", "Lamb Skipping", CAT, T, WALKING + " && q.is_baby", 0.55, F, pri=102, gait="canter", stride=28, duty=0.45, bob=3.0, pitch=3, roll=2)
loop_state("sheep.graze", "Sheep Cropping Grass", CAT, T, ALIVE + " && q.is_eating", 2.0, F, {
    "head:rot": lambda u: [62 + 4 * wave(u, 0, 5), 8 * wave(u, 0, 0.5), 0], "mw_center:rot": lambda u: tilt(5, 0, 0), "mw_center:pos": lambda u: move(0, 0, 0.5)}, pri=130)
beat("sheep.bleat", "Sheep Bleat", CAT, T, event("vocalize", ALIVE), 1.0, F, {"head:rot": [(0, Z), (0.2, [-28, 0, 0], "out_quad"), (0.3, [-24, 0, 4]), (0.42, [-28, 0, -4]), (0.54, [-24, 0, 3]), (1.0, Z)]},
     layer="gesture")
c = mob("sheep.lie", "Sheep Lying In The Grass", CAT, T, 5.0, state(STILL + " && q.idle_time > 18 && !q.is_baby", group="sheep_idle", weight=2), file=F, blend_in=1.2, blend_out=1.0)
c.cycle("mw_center", "position", lambda u: move(0, -6 + 0.25 * wave(u), 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, -9))
c.cycle("head", "rotation", lambda u: [8, 20 * wave(u, 0, 0.5), 0])
c.cycle("left_front_leg", "rotation", lambda u: [-35, 0, -20])
c.cycle("right_front_leg", "rotation", lambda u: [-85, 0, 0])
c.cycle("left_hind_leg", "rotation", lambda u: [40, 0, -45])
c.cycle("right_hind_leg", "rotation", lambda u: [75, 0, -30])
loop_state("sheep.look_around", "Sheep Looking About", CAT, T, STILL + " && q.idle_time > 3", 4.0, F, {
    "head:rot": lambda u: [-6 + 4 * wave(u, 0.1, 2), 40 * wave(u), 0]}, group="sheep_idle", weight=3)
loop_state("sheep.alert", "Sheep Alert Stance", CAT, T, STILL + " && q.near_hostile", 1.8, F, {
    "head:rot": lambda u: [-30, 10 * wave(u, 0, 0.5), 0], "mw_center:pos": lambda u: move(0, 0.8, 0), "mw_center:rot": lambda u: tilt(-3, 0, 0)}, pri=118)
loop_state("sheep.lamb_headbutt", "Lambs Play-Butting", CAT, T, STILL + " && q.is_baby && q.trait_energy > 0.4", 1.4, F, {
    "head:rot": lambda u: [30 * max(0, wave(u)), 0, 0], "mw_center:pos": lambda u: move(0, 0, 1.5 * max(0, wave(u, 0.05)))}, group="sheep_idle", weight=2)
life("sheep.fleece_shudder", "Sheep Shuddering Fleece", CAT, T, ALIVE + " && (q.is_raining || q.wind > 0.6)", 0.4, F, {"mw_center:rot": lambda u: tilt(0, 0, 0.7 * wave(u, 0, 2))})

# ============================================================================ polar bear
T, F = "minecraft:polar_bear", f("polar_bear")
gait("polar_bear.amble", "Polar Bear Rolling Amble", CAT, T, WALKING + CALM, 1.8, F, gait="pace", stride=24, duty=0.66, bob=0.8, pitch=1, roll=4.5, yaw=4, front_scale=1.25, splay=8)
gait("polar_bear.charge", "Polar Bear Charge", CAT, T, WALKING + " && (q.is_angry || q.ground_speed > 0.17)", 0.75, F, pri=101, gait="gallop", stride=34, duty=0.42, bob=2.2, pitch=6, roll=1.5, yaw=3.5, front_scale=1.3, pitch_phase=0.35)
life("polar_bear.rear_sway", "Polar Bear Upright Sway", CAT, T, ALIVE + " && q.is_standing", 1.6, F, {"mw_center:rot": lambda u: tilt(0, 4 * wave(u), 3 * wave(u, 0.25)), "head:rot": lambda u: [0, -6 * wave(u), 0]},
     pri=70)
loop_state("polar_bear.sniff_air", "Polar Bear Scenting The Wind", CAT, T, STILL + " && !q.is_standing && q.idle_time > 3", 2.6, F, {
    "head:rot": lambda u: [-25 + 4 * max(0, wave(u, 0, 5)), 20 * wave(u, 0, 0.5), 0], "mw_center:rot": lambda u: tilt(-4, 0, 0)}, group="bear_idle", weight=2)
c = mob("polar_bear.sit_back", "Polar Bear Sitting Back", CAT, T, 4.0, state(STILL + " && !q.is_standing && q.idle_time > 15", group="bear_idle", weight=2), file=F, blend_in=1.0, blend_out=0.8)
c.cycle("mw_center", "rotation", lambda u: tilt(-35, 0, 1.5 * wave(u)))
c.cycle("mw_center", "position", lambda u: move(0, -5, 2))
c.cycle("left_hind_leg", "rotation", lambda u: [-80, 0, -10])
c.cycle("right_hind_leg", "rotation", lambda u: [-80, 0, 10])
c.cycle("left_front_leg", "rotation", lambda u: [25, 0, -4 + 2 * wave(u)])
c.cycle("right_front_leg", "rotation", lambda u: [25, 0, 4])
c.cycle("head", "rotation", lambda u: [30, 10 * wave(u, 0, 0.5), 0])
beat("polar_bear.swipe", "Polar Bear Paw Swipe", CAT, T, event("attack", ALIVE), 0.8, F, {
    "right_front_leg:rot": [(0, Z), (0.25, [-110, 0, 30], "out_quad"), (0.4, [-30, 0, -10], "in_quart"), (0.8, Z)], "head:rot": [(0, Z), (0.25, [-10, 15, 0]), (0.4, [15, -10, 0]), (0.8, Z)],
    "mw_center:rot": [(0, Z), (0.25, tilt(-6, 6, -4)), (0.4, tilt(4, -6, 3)), (0.8, Z)]}, pri=160, events=[(0.35, "whoosh", {"weight": "heavy"})])
beat("polar_bear.growl", "Polar Bear Warning Growl", CAT, T, event("vocalize", ALIVE + " && !q.is_baby"), 1.4, F, {
    "head:rot": [(0, Z), (0.3, [20, -18, 0]), (0.7, [22, 18, 0]), (1.0, [15, 0, 0]), (1.4, Z)], "mw_center:pos": [(0, Z), (0.3, move(0, -0.8, 0)), (1.4, Z)]}, layer="gesture")
loop_state("polar_bear.cub_tumble", "Polar Bear Cub Tumble", CAT, T, STILL + " && q.is_baby && q.trait_energy > 0.35", 2.4, F, {
    "mw_center:rot": lambda u: tilt(0, 0, 60 * max(0, wave(u)) ** 2), "head:rot": lambda u: [10, 0, -20 * max(0, wave(u))],
    "left_front_leg:rot": lambda u: [-40 * max(0, wave(u)), 0, 0], "right_hind_leg:rot": lambda u: [30 * max(0, wave(u)), 0, 0]}, group="bear_idle", weight=3)
beat("polar_bear.shake_dry", "Polar Bear Shakes Dry", CAT, T, event("exit_water", ALIVE), 1.3, F, {
    "mw_center:rot": [(0, Z), (0.15, tilt(0, 0, 18)), (0.3, tilt(0, 0, -18)), (0.45, tilt(0, 0, 14)), (0.6, tilt(0, 0, -10)), (0.8, tilt(0, 0, 4)), (1.3, Z)],
    "head:rot": [(0, Z), (0.15, [0, 0, -24]), (0.3, [0, 0, 24]), (0.45, [0, 0, -16]), (0.8, Z)]}, layer="gesture",
    events=[(0.2, "particle", {"particle": "splash", "count": "18", "at": "body", "spread": "0.8"})])

# ============================================================================ panda
T, F = "minecraft:panda", f("panda")
gait("panda.waddle", "Panda Waddle", CAT, T, WALKING + " && !q.is_rolling", 1.5, F, gait="waddle", stride=18, duty=0.62, bob=0.6, pitch=1, roll=5.5)
loop_state("panda.eat_bamboo", "Panda Munching Bamboo", CAT, T, ALIVE + " && q.is_sitting && q.is_eating", 1.2, F, {
    "right_front_leg:rot": lambda u: [-120 + 10 * wave(u, 0, 2), 0, 14], "left_front_leg:rot": lambda u: [-115 + 10 * wave(u, 0.1, 2), 0, -14],
    "head:rot": lambda u: [-10 + chew(u, 4, 5), 4 * wave(u), 0]}, pri=140)
loop_state("panda.sit_sway", "Panda Contented Sit", CAT, T, ALIVE + " && q.is_sitting && !q.is_eating", 3.0, F, {
    "mw_center:rot": lambda u: tilt(0, 0, 3 * wave(u)), "head:rot": lambda u: [0, 12 * wave(u, 0.2), 4 * wave(u)],
    "left_front_leg:rot": lambda u: [-40, 0, -10], "right_front_leg:rot": lambda u: [-40, 0, 10]}, pri=135)
beat("panda.sneeze", "Panda Sneeze", CAT, T, event("vocalize", ALIVE + " && q.is_sneezing"), 1.2, F, {
    "head:rot": [(0, Z), (0.5, [-30, 0, 0], "in_quad"), (0.62, [35, 0, 0], "out_expo"), (0.85, [20, 0, 0]), (1.2, Z)],
    "mw_center:pos": [(0, Z), (0.62, move(0, 0, -1.5)), (1.2, Z)]}, pri=170, events=[(0.62, "particle", {"particle": "dust_puff", "count": "5", "at": "head", "spread": "0.2"})])
loop_state("panda.belly_up", "Panda Lolling On Its Back", CAT, T, ALIVE + " && q.is_on_back", 2.0, F, {
    "left_front_leg:rot": lambda u: [-30 + 25 * wave(u), 0, -10], "right_front_leg:rot": lambda u: [-30 + 25 * wave(u, 0.5), 0, 10],
    "left_hind_leg:rot": lambda u: [-20 + 15 * wave(u, 0.25), 0, 0], "right_hind_leg:rot": lambda u: [-20 + 15 * wave(u, 0.75), 0, 0], "head:rot": lambda u: [0, 15 * wave(u, 0, 0.5), 0]}, pri=140)
c = mob("panda.lazy_flop", "Lazy Panda Sprawl", CAT, T, 6.0, state(STILL + " && q.gene == 'lazy' && q.idle_time > 8", group="panda_idle", weight=4), file=F, blend_in=1.2, blend_out=1.0)
c.cycle("mw_center", "position", lambda u: move(0, -7, 0))
c.cycle("head", "rotation", lambda u: [28, 0, 10 + 2 * wave(u)])
for b in QLEGS:
    c.cycle(b, "rotation", lambda u, b=b: [-90 if "front" in b else 90, 0, (-30 if "left" in b else 30)])
loop_state("panda.worried_cower", "Worried Panda Covering Eyes", CAT, T, ALIVE + " && q.gene == 'worried' && q.is_thundering", 1.4, F, {
    "left_front_leg:rot": lambda u: [-140, 0, -26], "right_front_leg:rot": lambda u: [-140, 0, 26], "head:rot": lambda u: [30, 0, 0],
    "mw_center:pos": lambda u: move(0.15 * wave(u, 0, 4), -2, 0)}, pri=150)
loop_state("panda.playful_roll", "Playful Panda Somersault", CAT, T, STILL + " && q.gene == 'playful'", 2.0, F, {
    "mw_center:rot": lambda u: tilt(0, 0, 360 * min(1.0, u * 2)), "head:rot": lambda u: [25, 0, 0]}, group="panda_idle", weight=4)
beat("panda.aggressive_swat", "Aggressive Panda Swat", CAT, T, event("attack", ALIVE), 0.7, F, {
    "left_front_leg:rot": [(0, Z), (0.2, [-80, 0, -30]), (0.32, [-20, 0, 10], "in_quart"), (0.7, Z)], "head:rot": [(0, Z), (0.2, [-6, -10, 0]), (0.32, [10, 10, 0]), (0.7, Z)]}, pri=160)
life("panda.weak_cough", "Weak Panda Wheeze", CAT, T, ALIVE + " && q.gene == 'weak'", 3.0, F, {
    "head:rot": lambda u: [6 * max(0, wave(u, 0, 3)) ** 4, 0, 0], "mw_center:pos": lambda u: move(0, -0.4 * max(0, wave(u, 0, 3)) ** 4, 0)})
gait("panda.cub_bounce", "Panda Cub Bounce", CAT, T, WALKING + " && q.is_baby", 0.8, F, pri=102, gait="bound", stride=22, duty=0.5, bob=2.4, pitch=4, roll=3)
life("panda.roll_dizzy", "Panda Dizzy After Rolling", CAT, T, ALIVE + " && q.is_rolling", 1.0, F, {"head:rot": lambda u: [0, 10 * wave(u), 10 * cwave(u)]}, pri=72)

# ============================================================================ goat
T, F = "minecraft:goat", f("goat")
gait("goat.walk", "Goat Sure-Footed Walk", CAT, T, WALKING + CALM + " && !q.is_ramming", 1.0, F, gait="walk", stride=24, duty=0.58, bob=0.9, pitch=2, roll=0.8, snap=0.3, front_scale=0.85, lift=10)
gait("goat.bound", "Goat Bounding Run", CAT, T, WALKING + PANIC + " && !q.is_ramming", 0.5, F, pri=101, gait="bound", stride=30, duty=0.38, bob=2.8, pitch=6, roll=0.5)
loop_state("goat.ram_windup", "Goat Lowering For A Ram", CAT, T, ALIVE + " && q.is_ramming", 0.5, F, {
    "head:rot": lambda u: [40, 0, 0], "mw_center:rot": lambda u: tilt(8, 0, 0), "left_hind_leg:rot": lambda u: [14 + 4 * wave(u), 0, 0], "right_hind_leg:rot": lambda u: [14 - 4 * wave(u), 0, 0]}, pri=160,
    layer="action")
beat("goat.leap", "Goat Mountain Leap", CAT, T, event("jump", ALIVE), 0.8, F, {
    "left_front_leg:rot": [(0, Z), (0.1, [-50, 0, 0]), (0.55, [-40, 0, 0]), (0.8, Z)], "right_front_leg:rot": [(0, Z), (0.1, [-55, 0, 0]), (0.55, [-40, 0, 0]), (0.8, Z)],
    "left_hind_leg:rot": [(0, [20, 0, 0]), (0.1, [50, 0, 0]), (0.55, [30, 0, 0]), (0.8, Z)], "right_hind_leg:rot": [(0, [20, 0, 0]), (0.1, [50, 0, 0]), (0.55, [30, 0, 0]), (0.8, Z)],
    "mw_center:rot": [(0, Z), (0.1, tilt(-12, 0, 0)), (0.5, tilt(10, 0, 0)), (0.8, Z)]}, pri=150)
beat("goat.scream", "Screaming Goat", CAT, T, event("vocalize", ALIVE + " && q.is_screaming"), 1.2, F, {
    "head:rot": [(0, Z), (0.15, [-40, 0, 0], "out_expo"), (0.3, [-38, 0, 8]), (0.45, [-40, 0, -8]), (0.6, [-38, 0, 6]), (0.8, [-30, 0, 0]), (1.2, Z)],
    "mw_center:rot": [(0, Z), (0.15, tilt(-6, 0, 0)), (1.2, Z)]}, layer="gesture", pri=170)
beat("goat.bleat", "Goat Bleat", CAT, T, event("vocalize", ALIVE + " && !q.is_screaming"), 0.8, F, {"head:rot": [(0, Z), (0.2, [-15, 8, 0]), (0.45, [-12, -6, 0]), (0.8, Z)]}, layer="gesture")
loop_state("goat.nibble", "Goat Nibbling Shrubs", CAT, T, STILL + " && q.idle_time > 3", 1.4, F, {
    "head:rot": lambda u: [35 + 10 * max(0, wave(u, 0, 3)), 20 * wave(u, 0, 0.5), 6 * wave(u, 0, 3)]}, group="goat_idle", weight=3)
beat("goat.head_shake", "Goat Head Shake", CAT, T, event("stop_moving", ALIVE, chance=0.3), 0.7, F, {
    "head:rot": [(0, Z), (0.1, [0, 0, 18]), (0.2, [0, 0, -18]), (0.3, [0, 0, 14]), (0.4, [0, 0, -10]), (0.7, Z)]}, layer="gesture")
loop_state("goat.ledge_balance", "Goat Balancing On A Slope", CAT, T, STILL + " && math.abs(q.terrain_pitch) > 12", 2.0, F, {
    "left_front_leg:rot": lambda u: [-10, 0, -8], "right_front_leg:rot": lambda u: [-10, 0, 8], "left_hind_leg:rot": lambda u: [12, 0, -6], "right_hind_leg:rot": lambda u: [12, 0, 6],
    "mw_center:rot": lambda u: tilt(0, 0, 1.2 * wave(u)), "head:rot": lambda u: [10, 25 * wave(u, 0, 0.5), 0]}, pri=118)
gait("goat.kid_spring", "Goat Kid Springing", CAT, T, WALKING + " && q.is_baby", 0.42, F, pri=102, gait="pace", stride=28, duty=0.4, bob=3.4, pitch=2, roll=3)
loop_state("goat.horn_rub", "Goat Rubbing Its Horns", CAT, T, STILL + " && q.idle_time > 10", 2.2, F, {
    "head:rot": lambda u: [30, 20 * wave(u, 0, 2), 15 * wave(u, 0, 2)], "mw_center:pos": lambda u: move(0.4 * wave(u, 0, 2), 0, 0)}, group="goat_idle", weight=1)

# ============================================================================ llama & trader llama
for T, sp, heavy in (("minecraft:llama", "llama", 0.0), ("minecraft:trader_llama", "trader_llama", 1.0)):
    F = f(sp)
    label = "Trader Llama" if heavy else "Llama"
    gait(sp + ".pace", label + (" Burdened Pace" if heavy else " Lateral Pace"), CAT, T, WALKING + CALM + " && !q.is_leashed", 1.4 + 0.3 * heavy, F,
         gait="pace", stride=22 - 4 * heavy, duty=0.6 + 0.06 * heavy, bob=0.7 + 0.5 * heavy, pitch=0.6 + 2 * heavy, roll=4 + 2 * heavy, tail=None,
         lift=12 * (1 - heavy), pitch_phase=0.1 + 0.3 * heavy)
    gait(sp + ".caravan", label + " Caravan Step", CAT, T, WALKING + " && q.is_leashed", 1.6 + 0.2 * heavy, F, pri=101,
         gait="walk", stride=18, duty=0.68, bob=0.4 + 0.3 * heavy, pitch=0.4 + 0.6 * heavy, roll=1.5, snap=0.3 * heavy, yaw=2 * (1 - heavy), roll_phase=0.2 * heavy)
    beat(sp + ".spit", label + " Spit", CAT, T, event("shoot:spit", ALIVE), 0.8, F, {
        "head:rot": [(0, Z), (0.25, [-25 + 5 * heavy, 0, 0], "out_quad"), (0.34, [15, 0, 0], "out_expo"), (0.8, Z)], "mw_center:pos": [(0, Z), (0.25, move(0, 0, -0.8)), (0.34, move(0, 0, 0.8)), (0.8, Z)]},
        pri=160)
    c = mob(sp + ".kush", label + (" Weary Kneel" if heavy else " Kneeling Rest"), CAT, T, 5.0, state(STILL + " && q.idle_time > 18", group=sp + "_idle", weight=2), file=F, blend_in=1.6, blend_out=1.2)
    c.cycle("mw_center", "position", lambda u, h=heavy: move(0, -8 - h, 0))
    c.cycle("mw_center", "rotation", lambda u, h=heavy: tilt(-4 + 9 * h, 0, 7 * h + 1.5 * wave(u)))
    for b in QLEGS:
        c.cycle(b, "rotation", lambda u, b=b, h=heavy: [(-95 if "front" in b else 100) * (1 - 0.2 * h), 0, (25 * h if "left" in b else -10 * h)])
    c.cycle("head", "rotation", lambda u, h=heavy: [-14 + 40 * h + 3 * wave(u, 0.2), 30 * (1 - h) * wave(u, 0, 0.5), 10 * h])
if True:
    T, F = "minecraft:llama", f("llama")
    life("llama.neck_sway", "Llama Swaying Neck", CAT, T, STILL, 3.5, F, {"head:rot": lambda u: [5 * wave(u, 0.2), 8 * wave(u), 3 * wave(u, 0.4)]})
    life("llama.pack_jostle", "Llama Pack Jostle", CAT, T, WALKING, 1.4, F, {"right_chest:rot": lambda u: [0, 0, 6 * wave(u, 0, 2)], "left_chest:rot": lambda u: [0, 0, -6 * wave(u, 0.1, 2)]})
    loop_state("llama.alert", "Llama Neck Stretched Alert", CAT, T, ALIVE + " && q.near_hostile && q.ground_speed < 0.05", 2.0, F, {
        "head:rot": lambda u: [-20, 25 * wave(u, 0, 0.5), 0], "mw_center:pos": lambda u: move(0, 0.6, 0), "mw_center:rot": lambda u: tilt(-4, 0, 0)}, pri=118)
    beat("llama.hum", "Llama Humming Bob", CAT, T, event("vocalize", ALIVE), 1.2, F, {"head:rot": [(0, Z), (0.3, [8, 0, 6]), (0.6, [4, 0, -6]), (0.9, [8, 0, 4]), (1.2, Z)]}, layer="gesture")
    T, F = "minecraft:trader_llama", f("trader_llama")
    life("trader_llama.weary_head", "Trader Llama Drooping Head", CAT, T, STILL, 4.5, F, {"head:rot": lambda u: [18 + 4 * wave(u), 6 * wave(u, 0.3), 0], "mw_center:pos": lambda u: move(0, -0.3 * wave(u), 0)})
    beat("trader_llama.dust_shake", "Trader Llama Dust Shake", CAT, T, event("stop_moving", ALIVE, chance=0.25), 1.2, F, {
        "mw_center:rot": [(0, Z), (0.15, tilt(0, 0, 10)), (0.3, tilt(0, 0, -10)), (0.45, tilt(0, 0, 7)), (0.6, tilt(0, 0, -4)), (1.2, Z)],
        "right_chest:rot": [(0, Z), (0.2, [0, 0, 14]), (0.35, [0, 0, -12]), (0.6, Z)], "left_chest:rot": [(0, Z), (0.2, [0, 0, -14]), (0.35, [0, 0, 12]), (0.6, Z)]}, layer="gesture",
        events=[(0.2, "particle", {"particle": "dust_puff", "count": "8", "at": "body", "spread": "0.6"})])

# ============================================================================ turtle
T, F = "minecraft:turtle", f("turtle")
c = mob("turtle.land_crawl", "Turtle Flipper Crawl", CAT, T, 2.0, state(WALKING + " && !q.has_egg", exit_delay=0.2), layer="base", file=F, **{"time": "q.limb_swing * 0.25", "weight": "math.clamp(q.limb_swing_amount * 3, 0, 1)"})
for b, ph in (("left_front_leg", 0.0), ("right_front_leg", 0.5), ("left_hind_leg", 0.5), ("right_hind_leg", 0.0)):
    c.cycle(b, "rotation", lambda u, ph=ph, b=b: [0, 30 * wave(u, ph) * (1 if "left" in b else -1), 10 * max(0, cwave(u, ph))])
c.cycle("mw_center", "rotation", lambda u: tilt(0, 2 * wave(u), 1.5 * wave(u)))
c = mob("turtle.swim", "Turtle Gliding Strokes", CAT, T, 2.4, state(ALIVE + " && q.is_in_water && !q.is_on_ground"), layer="base", file=F)
for b, ph in (("left_front_leg", 0.0), ("right_front_leg", 0.0), ("left_hind_leg", 0.5), ("right_hind_leg", 0.5)):
    big = 1.0 if "front" in b else 0.4
    c.cycle(b, "rotation", lambda u, ph=ph, big=big, b=b: [10 * wave(u, ph), 0, 50 * big * wave(u, ph) * (1 if "right" in b else -1)])
c.cycle("mw_center", "position", lambda u: move(0, 0.6 * cwave(u), 0))
c.cycle("head", "rotation", lambda u: [-6 + 3 * cwave(u), 0, 0])
loop_state("turtle.dig_nest", "Turtle Digging A Nest", CAT, T, ALIVE + " && q.is_laying_egg", 1.0, F, {
    "left_hind_leg:rot": lambda u: [40 * wave(u), 20 * max(0, wave(u)), 0], "right_hind_leg:rot": lambda u: [40 * wave(u, 0.5), -20 * max(0, wave(u, 0.5)), 0],
    "mw_center:rot": lambda u: tilt(-6, 0, 2 * wave(u)), "head:rot": lambda u: [-10, 0, 0]}, pri=150, layer="action")
c = mob("turtle.gravid_trudge", "Gravid Turtle Trudge", CAT, T, 2.6, state(WALKING + " && q.has_egg", exit_delay=0.2), layer="base", pri=101, file=F,
        **{"time": "q.limb_swing * 0.33", "weight": "math.clamp(q.limb_swing_amount * 3, 0, 1)"})
for b, ph in (("left_front_leg", 0.0), ("right_front_leg", 0.5), ("left_hind_leg", 0.25), ("right_hind_leg", 0.75)):
    c.cycle(b, "rotation", lambda u, ph=ph, b=b: [-6 * max(0, wave(u, ph)), 20 * wave(u, ph) * (1 if "left" in b else -1), 0])
c.cycle("mw_center", "position", lambda u: move(0, -0.8 + 0.3 * max(0, wave(u, 0, 2)), 0))
c.cycle("egg_belly", "rotation", lambda u: [2 * wave(u, 0, 2), 0, 0])
loop_state("turtle.bask", "Turtle Basking", CAT, T, STILL + " && !q.is_night && q.sky_exposed", 6.0, F, {
    "head:rot": lambda u: [-14 + 2 * wave(u), 10 * wave(u, 0, 0.5), 0], "head:pos": lambda u: move(0, 0, 0.8),
    "left_front_leg:rot": lambda u: [0, 0, -20], "right_front_leg:rot": lambda u: [0, 0, 20], "left_hind_leg:rot": lambda u: [0, 0, -15], "right_hind_leg:rot": lambda u: [0, 0, 15]},
    group="turtle_idle", weight=3)
beat("turtle.withdraw", "Turtle Withdraws Into Shell", CAT, T, event("hurt", ALIVE), 1.6, F, {
    "head:pos": [(0, Z), (0.1, move(0, 0, -2.5), "out_expo"), (1.1, move(0, 0, -2.5)), (1.6, Z)], "head:rot": [(0, Z), (0.1, [10, 0, 0]), (1.6, Z)],
    "left_front_leg:rot": [(0, Z), (0.1, [0, -40, 0]), (1.1, [0, -40, 0]), (1.6, Z)], "right_front_leg:rot": [(0, Z), (0.1, [0, 40, 0]), (1.1, [0, 40, 0]), (1.6, Z)]}, pri=200, layer="reaction")
c = mob("turtle.hatchling_scuttle", "Hatchling Scuttle", CAT, T, 0.5, state(WALKING + " && q.is_baby"), layer="base", pri=102, file=F)
for b, ph in (("left_front_leg", 0.0), ("right_front_leg", 0.5), ("left_hind_leg", 0.5), ("right_hind_leg", 0.0)):
    c.cycle(b, "rotation", lambda u, ph=ph, b=b: [-15 * wave(u, ph), 35 * wave(u, ph) * (1 if "left" in b else -1), 0])
c.cycle("mw_center", "rotation", lambda u: tilt(0, 5 * wave(u), 3 * wave(u, 0.25)))
beat("turtle.surface_breath", "Turtle Surfacing For Air", CAT, T, event("surface", ALIVE), 1.4, F, {
    "head:rot": [(0, Z), (0.3, [-30, 0, 0]), (0.9, [-28, 0, 0]), (1.4, Z)], "head:pos": [(0, Z), (0.3, move(0, 0.4, 0.8)), (1.4, Z)]}, layer="gesture")

# ============================================================================ equines (unridden behaviour)
H_LEGS = ("left_hind_leg", "left_front_leg", "right_hind_leg", "right_front_leg")
FREE = " && !q.has_rider"
# character: (lift = front hoof flick, snap = choppy steps, yaw = barrel twist, front = front/hind stride ratio)
EQ = {"horse": dict(lift=12, snap=0.0, yaw=1.0, front_scale=1.15), "donkey": dict(lift=0, snap=0.35, yaw=0.0, front_scale=0.8),
      "mule": dict(lift=5, snap=0.12, yaw=3.0, front_scale=1.0, roll_phase=0.25)}
for T, sp, label, pace in (("minecraft:horse", "horse", "Horse", 1.0), ("minecraft:donkey", "donkey", "Donkey", 0.8), ("minecraft:mule", "mule", "Mule", 0.88)):
    F = f(sp)
    ch = EQ[sp]
    gait(sp + ".walk", label + " Four-Beat Walk", CAT, T, WALKING + FREE + " && q.ground_speed < 0.09", 1.5 / pace, F, gait="walk", stride=20 + 4 * pace, duty=0.62, bob=0.6, pitch=1.4,
         roll=1.4 + (1 - pace) * 4, tail="tail", tail_amp=6, keep_head=False, **ch)
    gait(sp + ".trot", label + " Two-Beat Trot", CAT, T, WALKING + FREE + " && q.ground_speed >= 0.09 && q.ground_speed < 0.2", 0.9 / pace, F, pri=101, gait="trot", stride=30,
         duty=0.5, bob=1.6 * pace, pitch=1.0, roll=0.6, tail="tail", tail_amp=10, tail_phase=0.2 + 0.3 * (1 - pace), **ch)
T, F = "minecraft:horse", f("horse")
gait("horse.canter", "Horse Three-Beat Canter", CAT, T, WALKING + FREE + " && q.ground_speed >= 0.2 && q.ground_speed < 0.3", 0.75, F, pri=102, gait="canter", stride=38, duty=0.45, bob=2.2,
     pitch=4, roll=0.8, tail="tail", tail_amp=14)
gait("horse.gallop", "Horse Full Gallop", CAT, T, WALKING + FREE + " && q.ground_speed >= 0.3", 0.55, F, pri=103, gait="gallop", stride=46, duty=0.38, bob=2.8, pitch=6, roll=0.5,
     tail="tail", tail_amp=18)
loop_state("horse.graze", "Horse Grazing", CAT, T, ALIVE + " && q.is_eating", 2.6, F, {
    "head_parts:rot": lambda u: [70 + 3 * wave(u, 0, 4), 10 * wave(u, 0, 0.5), 0], "upper_mouth:rot": lambda u: [chew(u, 5, 8), 0, 0], "tail:rot": lambda u: [0, 12 * wave(u), 0]}, pri=130)
life("horse.tail_swish", "Horse Tail Swish", CAT, T, ALIVE + " && q.is_on_ground", 4.0, F, {"tail:rot": lambda u: [6 * max(0, wave(u, 0.2)), 30 * wave(u, 0, 1) * max(0, wave(u, 0.1)), 0]})
life("horse.ear_flick", "Horse Ear Flicks", CAT, T, ALIVE, 3.0, F, {"left_ear:rot": lambda u: [0, 0, -20 * max(0, wave(u, 0.1, 2)) ** 8], "right_ear:rot": lambda u: [0, 0, 20 * max(0, wave(u, 0.6, 1)) ** 8]})
beat("horse.head_toss", "Horse Head Toss", CAT, T, event("vocalize", ALIVE + FREE), 1.2, F, {
    "head_parts:rot": [(0, Z), (0.25, [20, 0, 0]), (0.45, [-30, 0, 6], "out_expo"), (0.7, [-10, 0, -4]), (1.2, Z)], "mane:rot": [(0, Z), (0.5, [-10, 0, 0]), (1.2, Z)]}, layer="gesture")
beat("horse.paw_ground", "Horse Pawing The Ground", CAT, T, event("stop_moving", ALIVE + FREE, chance=0.4), 1.6, F, {
    "right_front_leg:rot": [(0, Z), (0.25, [-40, 0, 0]), (0.45, [20, 0, 0], "in_quad"), (0.7, [-40, 0, 0]), (0.9, [20, 0, 0], "in_quad"), (1.2, [-10, 0, 0]), (1.6, Z)],
    "head_parts:rot": [(0, Z), (0.4, [15, 0, 0]), (1.6, Z)]}, layer="gesture", events=[(0.45, "footstep", {"foot": "front_right"}), (0.9, "footstep", {"foot": "front_right"})])
loop_state("horse.nuzzle", "Horse Nuzzling", CAT, T, ALIVE + " && q.is_in_love", 2.0, F, {"head_parts:rot": lambda u: [25 + 8 * wave(u, 0, 2), 14 * wave(u), 6 * wave(u)]}, pri=125)
gait("horse.foal_frolic", "Foal Frolicking", CAT, T, WALKING + " && q.is_baby", 0.5, F, pri=104, gait="bound", stride=40, duty=0.4, bob=3.5, pitch=8, roll=2, tail="tail", tail_amp=25, snap=0.25, yaw=4, tail_phase=0.6)
beat("horse.buck_kick", "Horse Hind Kick", CAT, T, event("hurt_back", ALIVE + FREE), 0.9, F, {
    "left_hind_leg:rot": [(0, Z), (0.15, [-20, 0, 0]), (0.3, [70, 0, 0], "out_expo"), (0.9, Z)], "right_hind_leg:rot": [(0, Z), (0.15, [-20, 0, 0]), (0.32, [75, 0, 0], "out_expo"), (0.9, Z)],
    "mw_center:rot": [(0, Z), (0.3, tilt(14, 0, 0)), (0.9, Z)], "head_parts:rot": [(0, Z), (0.3, [30, 0, 0]), (0.9, Z)]}, pri=180, events=[(0.3, "whoosh", {"weight": "heavy"})])
beat("horse.shake_off", "Horse Full-Body Shake", CAT, T, event("exit_water", ALIVE), 1.4, F, {
    "mw_center:rot": [(0, Z), (0.15, tilt(0, 0, 10)), (0.3, tilt(0, 0, -10)), (0.45, tilt(0, 0, 8)), (0.6, tilt(0, 0, -5)), (1.4, Z)],
    "head_parts:rot": [(0, Z), (0.15, [0, 20, -14]), (0.3, [0, -20, 14]), (0.45, [0, 12, -8]), (0.8, Z)], "mane:rot": [(0, Z), (0.2, [0, 0, 20]), (0.35, [0, 0, -20]), (0.7, Z)]},
    layer="gesture", events=[(0.2, "particle", {"particle": "splash", "count": "20", "at": "body", "spread": "1"})])
loop_state("horse.alert", "Horse On Alert", CAT, T, ALIVE + FREE + " && q.near_hostile && q.ground_speed < 0.05", 1.6, F, {
    "head_parts:rot": lambda u: [-25, 18 * wave(u, 0, 0.5), 0], "left_ear:rot": lambda u: [-15, 0, 0], "right_ear:rot": lambda u: [-15, 0, 0], "tail:rot": lambda u: [-25, 0, 0]}, pri=118)
c = mob("horse.doze", "Horse Dozing On Its Feet", CAT, T, 5.0, state(STILL + FREE + " && q.is_night && q.idle_time > 20"), file=F, blend_in=1.6, blend_out=0.8)
c.cycle("head_parts", "rotation", lambda u: [40 + 4 * wave(u), 0, 0])
c.cycle("right_hind_leg", "rotation", lambda u: [-12, 0, 0])
c.cycle("right_hind_leg", "position", lambda u: move(0, 0.6, 0))
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 1.5))
c.cycle("left_ear", "rotation", lambda u: [0, 0, -25])
c.cycle("right_ear", "rotation", lambda u: [0, 0, 25])

T, F = "minecraft:donkey", f("donkey")
beat("donkey.bray", "Donkey Bray", CAT, T, event("vocalize", ALIVE), 1.8, F, {
    "head_parts:rot": [(0, Z), (0.3, [-45, 0, 0], "out_quad"), (0.6, [-40, 0, 0]), (0.9, [-46, 0, 0]), (1.2, [-40, 0, 0]), (1.8, Z)],
    "upper_mouth:rot": [(0, Z), (0.3, [-20, 0, 0]), (0.6, [-5, 0, 0]), (0.9, [-22, 0, 0]), (1.2, [-5, 0, 0]), (1.8, Z)]}, layer="gesture")
loop_state("donkey.stubborn", "Stubborn Donkey Planting Its Hooves", CAT, T, ALIVE + " && q.is_leashed && q.ground_speed < 0.02 && q.trait_confidence > 0.5", 1.8, F, {
    "left_front_leg:rot": lambda u: [-18, 0, 0], "right_front_leg:rot": lambda u: [-18, 0, 0], "mw_center:rot": lambda u: tilt(-6, 0, 0), "head_parts:rot": lambda u: [-10, 8 * wave(u), 0]}, pri=120)
loop_state("donkey.graze", "Donkey Picking At Weeds", CAT, T, ALIVE + " && q.is_eating", 1.8, F, {"head_parts:rot": lambda u: [65 + 6 * max(0, wave(u, 0, 3)), 24 * wave(u, 0, 0.5), 0]}, pri=130)
life("donkey.ear_swivel", "Donkey Swiveling Ears", CAT, T, ALIVE, 2.4, F, {"left_ear:rot": lambda u: [0, 25 * wave(u), -10 * wave(u, 0.3)], "right_ear:rot": lambda u: [0, -25 * wave(u, 0.4), 10 * wave(u, 0.7)]})
T, F = "minecraft:mule", f("mule")
beat("mule.kick", "Mule Double-Barrel Kick", CAT, T, event("hurt", ALIVE), 0.8, F, {
    "left_hind_leg:rot": [(0, Z), (0.12, [-25, 0, 0]), (0.26, [80, 0, 0], "out_expo"), (0.8, Z)], "right_hind_leg:rot": [(0, Z), (0.12, [-25, 0, 0]), (0.26, [80, 0, 0], "out_expo"), (0.8, Z)],
    "mw_center:rot": [(0, Z), (0.26, tilt(18, 0, 0)), (0.8, Z)], "mw_center:pos": [(0, Z), (0.26, move(0, 1, 0)), (0.8, Z)]}, pri=180)
loop_state("mule.graze", "Mule Steady Grazing", CAT, T, ALIVE + " && q.is_eating", 3.2, F, {"head_parts:rot": lambda u: [60, 4 * wave(u, 0, 2), 0], "upper_mouth:rot": lambda u: [chew(u, 6, 10), 0, 0]},
           pri=130)
life("mule.ear_flop", "Mule Ear Flop", CAT, T, WALKING, 1.2, F, {"left_ear:rot": lambda u: [0, 0, -12 * cwave(u, 0, 2)], "right_ear:rot": lambda u: [0, 0, 12 * cwave(u, 0.15, 2)]})
beat("mule.snort", "Mule Snort", CAT, T, event("vocalize", ALIVE), 0.9, F, {"head_parts:rot": [(0, Z), (0.2, [15, 0, 0]), (0.32, [-8, 10, 0], "out_expo"), (0.9, Z)]}, layer="gesture",
     events=[(0.32, "breath", {"strength": "0.8"})])

for T, sp, label, jitter in (("minecraft:skeleton_horse", "skeleton_horse", "Skeleton Horse", 1.0), ("minecraft:zombie_horse", "zombie_horse", "Zombie Horse", 0.0)):
    F = f(sp)
    if jitter:
        gait(sp + ".rattle_walk", label + " Rattling Walk", CAT, T, WALKING + FREE + " && q.ground_speed < 0.2", 1.2, F, gait="pace", stride=26, duty=0.7, bob=0.4, pitch=2.5, roll=3, tail="tail", tail_amp=16)
        gait(sp + ".bone_gallop", label + " Clattering Gallop", CAT, T, WALKING + FREE + " && q.ground_speed >= 0.2", 0.6, F, pri=101, gait="bound", stride=44, duty=0.36, bob=2, pitch=8, roll=2,
             tail="tail", tail_amp=22)
        life(sp + ".bone_rattle", label + " Bone Rattle", CAT, T, STILL, 0.3, F, {"head_parts:rot": lambda u: [0.8 * wave(u), 0, 0.8 * wave(u, 0.25)], "tail:rot": lambda u: [0, 3 * wave(u), 0]})
        loop_state(sp + ".hollow_stare", label + " Hollow Stare", CAT, T, STILL + " && q.idle_time > 4", 5.0, F, {
            "head_parts:rot": lambda u: [10, 30 * (1 if u < 0.5 else -1) * min(1, abs(wave(u)) * 3), 0]}, group=sp + "_idle", weight=2)
        loop_state(sp + ".river_trot", label + " Wading Trot", CAT, T, ALIVE + " && q.is_in_water", 0.8, F, {
            "left_front_leg:rot": lambda u: [-50 * max(0, wave(u)), 0, 0], "right_front_leg:rot": lambda u: [-50 * max(0, wave(u, 0.5)), 0, 0],
            "left_hind_leg:rot": lambda u: [30 * wave(u, 0.5), 0, 0], "right_hind_leg:rot": lambda u: [30 * wave(u), 0, 0], "head_parts:rot": lambda u: [-20, 0, 0]}, pri=110, layer="base")
        beat(sp + ".rear_clatter", label + " Clattering Rear", CAT, T, event("vocalize", ALIVE + FREE), 1.4, F, {
            "mw_center:rot": [(0, Z), (0.35, tilt(-35, 0, 0), "out_quad"), (0.9, tilt(-30, 0, 4)), (1.4, Z)], "left_front_leg:rot": [(0, Z), (0.35, [-60, 0, 0]), (0.6, [-20, 0, 0]), (0.9, [-60, 0, 0]), (1.4, Z)],
            "right_front_leg:rot": [(0, Z), (0.4, [-30, 0, 0]), (0.7, [-70, 0, 0]), (1.0, [-30, 0, 0]), (1.4, Z)]}, pri=150)
    else:
        c = mob(sp + ".limp", label + " Limping Gait", CAT, T, 1.6, state(WALKING + FREE + " && q.ground_speed < 0.2", exit_delay=0.15), layer="base", file=F,
                time="q.limb_swing * 0.17", weight="math.clamp(q.limb_swing_amount * 2.2, 0, 1)")
        c.cycle("left_front_leg", "rotation", lambda u: [-24 * cwave(u), 0, 0])
        c.cycle("right_front_leg", "rotation", lambda u: [10 * cwave(u, 0.5) - 6, 0, 4])
        c.cycle("left_hind_leg", "rotation", lambda u: [22 * cwave(u, 0.5), 0, 0])
        c.cycle("right_hind_leg", "rotation", lambda u: [22 * cwave(u), 0, 0])
        c.cycle("mw_center", "rotation", lambda u: tilt(1.5 * wave(u), 0, 4 * max(0, wave(u, 0.6)) - 1))
        c.cycle("mw_center", "position", lambda u: move(0, -0.8 * max(0, wave(u, 0.6)), 0))
        gait(sp + ".lurch_run", label + " Lurching Run", CAT, T, WALKING + FREE + " && q.ground_speed >= 0.2", 0.7, F, pri=101, gait="canter", stride=36, duty=0.48, bob=2.4, pitch=5, roll=3.5,
             tail="tail", tail_amp=8)
        beat(sp + ".groan", label + " Groaning Head Loll", CAT, T, event("vocalize", ALIVE), 2.0, F, {
            "head_parts:rot": [(0, Z), (0.5, [30, 0, 20], "in_out_sine"), (1.2, [35, 0, -14]), (2.0, Z)], "upper_mouth:rot": [(0, Z), (0.5, [-25, 0, 0]), (1.4, [-10, 0, 0]), (2.0, Z)]}, layer="gesture")
        life(sp + ".rot_twitch", label + " Rotting Twitch", CAT, T, ALIVE, 2.6, F, {
            "left_ear:rot": lambda u: [0, 0, -30 * max(0, wave(u, 0.2, 3)) ** 12], "mw_center:rot": lambda u: tilt(0, 0, 2 * max(0, wave(u, 0.7)) ** 10)})
        loop_state(sp + ".graze_rot", label + " Tearing At Grass", CAT, T, ALIVE + " && q.is_eating", 1.4, F, {
            "head_parts:rot": lambda u: [65 + 10 * max(0, wave(u, 0, 2)), 0, 10 * wave(u)], "upper_mouth:rot": lambda u: [-15 * max(0, wave(u, 0.1, 2)), 0, 0]}, pri=130)
        loop_state(sp + ".mournful_stand", label + " Mournful Stand", CAT, T, STILL + " && q.idle_time > 6", 6.0, F, {
            "head_parts:rot": lambda u: [48 + 4 * wave(u), 0, 8 * wave(u, 0.2)], "tail:rot": lambda u: [-10, 0, 0]}, group=sp + "_idle", weight=2)

# ============================================================================ camel
T, F = "minecraft:camel", f("camel")
gait("camel.pace", "Camel Swaying Pace", CAT, T, WALKING + FREE + " && !q.is_charging", 1.8, F, gait="pace", stride=26, duty=0.62, bob=0.6, pitch=0.6, roll=5, tail="tail", tail_amp=10)
gait("camel.dash", "Camel Dash", CAT, T, ALIVE + " && q.is_charging", 0.6, F, pri=110, synced=False, gait="bound", stride=40, duty=0.4, bob=3.0, pitch=7, roll=1, tail="tail", tail_amp=20, front_scale=0.7, lift=20, splay=10)
loop_state("camel.chew_cud", "Camel Chewing Cud", CAT, T, STILL + " && !q.is_sitting", 1.8, F, {"head:rot": lambda u: [5, 3 * wave(u, 0, 4), 4 * wave(u, 0, 4)]}, group="camel_idle", weight=3)
life("camel.hump_wobble", "Camel Hump Wobble", CAT, T, WALKING, 1.8, F, {"hump:rot": lambda u: [0, 0, 5 * wave(u, 0.15)], "hump:scl": lambda u: [1, 1 + 0.03 * wave(u, 0, 2), 1]})
life("camel.tail_flick", "Camel Tail Flick", CAT, T, STILL, 3.2, F, {"tail:rot": lambda u: [8 * max(0, wave(u, 0.3, 2)) ** 4, 25 * max(0, wave(u, 0.2, 2)) ** 4, 0]})
life("camel.ear_twitch", "Camel Ear Twitch", CAT, T, ALIVE, 2.8, F, {"left_ear:rot": lambda u: [0, 0, -18 * max(0, wave(u, 0.1)) ** 10], "right_ear:rot": lambda u: [0, 0, 18 * max(0, wave(u, 0.55)) ** 10]})
loop_state("camel.kneel_idle", "Camel Kneeling Contentedly", CAT, T, ALIVE + " && q.is_sitting", 4.0, F, {
    "head:rot": lambda u: [-10 + 3 * wave(u), 15 * wave(u, 0, 0.5), 0], "tail:rot": lambda u: [0, 8 * wave(u), 0]}, layer="additive", pri=70)
loop_state("camel.scan_horizon", "Camel Scanning The Dunes", CAT, T, STILL + " && !q.is_sitting && q.idle_time > 4", 5.0, F, {
    "head:rot": lambda u: [-15, 45 * wave(u), 0]}, group="camel_idle", weight=2)
beat("camel.grumble", "Camel Grumble", CAT, T, event("vocalize", ALIVE), 1.4, F, {"head:rot": [(0, Z), (0.3, [-20, 15, 0]), (0.7, [-10, -15, 8]), (1.4, Z)]}, layer="gesture")

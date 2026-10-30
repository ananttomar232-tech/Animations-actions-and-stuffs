"""Mounts, vehicles and riding (category: mounts_riding).

Rider clips key off q.vehicle (horse covers every AbstractHorse, boat, minecart, camel, pig, strider,
creature) and the vehicle's measured motion (q.vehicle_speed, q.vehicle_vertical). Mount clips play on
the animal while q.has_rider and differ from its free-roaming gaits: collected head, steadier rhythm.
"""
from core import arm, leg
from mobkit import mob, gait, life, loop_state, beat, Z, state, event, wave, cwave, tilt, move

CAT = "mounts_riding"
P = "@player"
R = "!q.is_dead && q.is_riding"
FP, FM = "player/riding", "mobs/mounts"


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def ride(cid, name, when, L, fns, pri=260, layer="overlay", group=None, weight=1, target=P, file=FP):
    return loop_state(cid, name, CAT, target, when, L, file, fns, pri=pri, layer=layer, group=group, weight=weight)


HORSE = R + " && q.vehicle == 'horse'"

# ============================================================================ riding a horse (any AbstractHorse)
ride("player.ride.horse_idle", "Sitting Easy In The Saddle", HORSE + " && q.vehicle_speed < 0.01 && q.idle_time < 8", 3.0, {
    "right_arm:rot": lambda u: arm('r', 20 + 3 * wave(u), 4), "left_arm:rot": lambda u: arm('l', 20 + 3 * wave(u, 0.5), 4), "body:rot": lambda u: tilt(2, 0, 1.5 * wave(u)),
    "head:rot": lambda u: [0, 15 * wave(u, 0.2), 0]}, group="horse_idle", weight=2)
ride("player.ride.horse_pat_neck", "Patting The Horse's Neck", HORSE + " && q.vehicle_speed < 0.01 && q.idle_time >= 8", 2.0, {
    "right_arm:rot": lambda u: arm('r', 60 + 10 * spike(u, 0, 3, 3), -10, 20), "left_arm:rot": lambda u: arm('l', 25, 4), "body:rot": lambda u: tilt(18, -8, 0), "head:rot": lambda u: [25, -10, 0]})
ride("player.ride.horse_walk", "Riding At A Walk", HORSE + " && q.vehicle_speed >= 0.01 && q.vehicle_speed < 0.1", 1.3, {
    "right_arm:rot": lambda u: arm('r', 35 + 3 * wave(u, 0, 2), 4), "left_arm:rot": lambda u: arm('l', 35 + 3 * wave(u, 0.1, 2), 4), "body:rot": lambda u: tilt(4, 3 * wave(u), 2 * wave(u)),
    "mw_root:pos": lambda u: move(0, 0.3 * wave(u, 0, 2), 0)})
ride("player.ride.horse_posting_trot", "Posting To The Trot", HORSE + " && q.vehicle_speed >= 0.1 && q.vehicle_speed < 0.2", 0.6, {
    "mw_root:pos": lambda u: move(0, 1.4 * max(0, wave(u)), 0), "body:rot": lambda u: tilt(10 + 4 * max(0, wave(u)), 0, 0), "right_arm:rot": lambda u: arm('r', 40, 4),
    "left_arm:rot": lambda u: arm('l', 40, 4), "right_leg:rot": lambda u: leg('r', 70, 20), "left_leg:rot": lambda u: leg('l', 70, 20)}, pri=261)
ride("player.ride.horse_canter", "Rocking With The Canter", HORSE + " && q.vehicle_speed >= 0.2 && q.vehicle_speed < 0.3", 0.75, {
    "body:rot": lambda u: tilt(12 + 8 * wave(u), 0, 0), "mw_root:pos": lambda u: move(0, 0.8 * wave(u, 0.2), 0), "right_arm:rot": lambda u: arm('r', 45 + 6 * wave(u), 4),
    "left_arm:rot": lambda u: arm('l', 45 + 6 * wave(u), 4), "head:rot": lambda u: [-8 * wave(u), 0, 0]}, pri=262)
ride("player.ride.horse_gallop", "Jockey Crouch At The Gallop", HORSE + " && q.vehicle_speed >= 0.3", 0.55, {
    "body:rot": lambda u: tilt(38 + 4 * wave(u, 0, 2), 0, 0), "mw_root:pos": lambda u: move(0, 1.2 + 0.6 * wave(u, 0.1, 2), -1), "right_arm:rot": lambda u: arm('r', 70, 2), "left_arm:rot": lambda u: arm('l', 70, 2),
    "head:rot": lambda u: [-35, 0, 0], "right_leg:rot": lambda u: leg('r', 80, 30), "left_leg:rot": lambda u: leg('l', 80, 30)}, pri=263)
ride("player.ride.horse_jump", "Two-Point Seat Over A Jump", HORSE + " && q.vehicle_vertical > 0.15", 0.8, {
    "body:rot": lambda u: tilt(45, 0, 0), "mw_root:pos": lambda u: move(0, 1.5, -1.5), "right_arm:rot": lambda u: arm('r', 90, 4), "left_arm:rot": lambda u: arm('l', 90, 4), "head:rot": lambda u: [-40, 0, 0]}, pri=266)
ride("player.ride.horse_landing", "Absorbing The Landing", HORSE + " && q.vehicle_vertical < -0.2", 0.5, {
    "body:rot": lambda u: tilt(-10, 0, 0), "mw_root:pos": lambda u: move(0, -1, 0), "right_arm:rot": lambda u: arm('r', 20, 20), "left_arm:rot": lambda u: arm('l', 20, 20)}, pri=265)
ride("player.ride.horse_rear_cling", "Clinging On As The Horse Rears", HORSE + " && q.vehicle_standing", 0.8, {
    "body:rot": lambda u: tilt(40, 0, 3 * wave(u)), "right_arm:rot": lambda u: arm('r', 80, -10), "left_arm:rot": lambda u: arm('l', 80, -10), "head:rot": lambda u: [-20, 0, 0], "right_leg:rot": lambda u: leg('r', 60, 10),
    "left_leg:rot": lambda u: leg('l', 60, 10)}, pri=270)
life("player.ride.turn_lean", "Leaning Into A Turn", CAT, P, R + " && (q.vehicle == 'horse' || q.vehicle == 'camel' || q.vehicle == 'pig') && math.abs(q.turn_rate) > 4", 0.6, FP, {
    "body:rot": lambda u: [0, 0, "q.turn_rate > 0 ? -10 : 10"], "head:rot": lambda u: [0, "q.turn_rate > 0 ? 12 : -12", 0]}, pri=90)
ride("player.ride.horse_rain_hunch", "Hunched In The Saddle Against The Rain", HORSE + " && q.is_raining && q.sky_exposed && q.vehicle_speed < 0.2", 1.6, {
    "body:rot": lambda u: tilt(20, 0, 0), "head:rot": lambda u: [20, 0, 0], "right_arm:rot": lambda u: arm('r', 30, -6, 20), "left_arm:rot": lambda u: arm('l', 30, -6, 20)}, pri=264)
beat("player.ride.mounted_slash", "Mounted Sabre Slash", CAT, P, event("attack", R + " && q.vehicle == 'horse' && (q.main_hand == 'sword' || q.main_hand == 'axe')"), 0.8, FP, {
    "right_arm:rot": [(0, arm('r', 40)), (0.25, arm('r', 160, 40), "out_quad"), (0.4, arm('r', 30, -40, 30), "in_quart"), (0.8, arm('r', 40))], "body:rot": [(0, Z), (0.25, tilt(-10, 25, 0)), (0.4, tilt(20, -25, 0)), (0.8, Z)],
    "head:rot": [(0, Z), (0.4, [20, -15, 0]), (0.8, Z)]}, pri=300, layer="action", events=[(0.35, "whoosh", {"weight": "heavy"})])
ride("player.ride.mounted_archery", "Mounted Archery Draw", R + " && q.is_using_item && q.main_hand == 'bow'", 1.0, {"body:rot": lambda u: tilt(-2, -30, 0), "head:rot": lambda u: [0, 30, 0]}, pri=268, layer="additive")
beat("player.ride.mounted_punch", "Bareback Swipe", CAT, P, event("attack", R + " && q.main_hand == 'empty'"), 0.5, FP, {
    "right_arm:rot": [(0, arm('r', 30)), (0.15, arm('r', 110, 10), "out_expo"), (0.5, arm('r', 30))], "body:rot": [(0, Z), (0.15, tilt(10, -15, 0)), (0.5, Z)]}, pri=299, layer="action")

# ============================================================================ camel, pig, strider, llama
CAMEL = R + " && q.vehicle == 'camel'"
ride("player.ride.camel_sway", "Swaying Atop A Camel", CAMEL + " && q.vehicle_speed >= 0.01 && q.vehicle_speed < 0.3", 1.8, {
    "body:rot": lambda u: tilt(4, 0, 7 * wave(u)), "head:rot": lambda u: [0, 0, -4 * wave(u)], "right_arm:rot": lambda u: arm('r', 25, 10), "left_arm:rot": lambda u: arm('l', 25, 10)})
ride("player.ride.camel_dash", "Holding On Through A Camel Dash", CAMEL + " && q.vehicle_speed >= 0.3", 0.6, {
    "body:rot": lambda u: tilt(30, 0, 0), "mw_root:pos": lambda u: move(0, 1.5 * max(0, wave(u)), 0), "right_arm:rot": lambda u: arm('r', 80, -6), "left_arm:rot": lambda u: arm('l', 80, -6)}, pri=262)
ride("player.ride.camel_kneel", "Riding A Kneeling Camel", CAMEL + " && q.vehicle_sitting", 3.0, {
    "body:rot": lambda u: tilt(-6, 0, 0), "right_arm:rot": lambda u: arm('r', 10, 20), "left_arm:rot": lambda u: arm('l', 10, 20), "head:rot": lambda u: [0, 30 * wave(u), 0]}, pri=264)
ride("player.ride.camel_idle", "Surveying From Camel Height", CAMEL + " && q.vehicle_speed < 0.01 && !q.vehicle_sitting", 4.0, {
    "head:rot": lambda u: [5, 45 * wave(u), 0], "right_arm:rot": lambda u: arm('r', 20 + 140 * spike(u, 0.3, 2), 0), "left_arm:rot": lambda u: arm('l', 20, 8)})
PIG = R + " && q.vehicle == 'pig'"
ride("player.ride.pig_carrot_lure", "Dangling A Carrot On A Stick", PIG + " && q.main_hand == 'steering_stick'", 1.0, {
    "right_arm:rot": lambda u: arm('r', 80 + 5 * wave(u), 0), "body:rot": lambda u: tilt(14, 0, 0), "mw_root:pos": lambda u: move(0, 0.8 * max(0, wave(u, 0, 2)), 0), "left_arm:rot": lambda u: arm('l', 20, 30)}, pri=262)
ride("player.ride.pig_bareback", "Bouncing Along On A Pig", PIG + " && q.main_hand != 'steering_stick'", 0.5, {
    "mw_root:pos": lambda u: move(0, 1 * max(0, wave(u)), 0), "right_arm:rot": lambda u: arm('r', 10, 40 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 40 + 10 * wave(u, 0.5)), "body:rot": lambda u: tilt(0, 0, 4 * wave(u))})
STRIDER = R + " && q.vehicle == 'strider'"
ride("player.ride.strider_fungus", "Steering A Strider With Warped Fungus", STRIDER + " && q.main_hand == 'steering_stick'", 1.4, {
    "right_arm:rot": lambda u: arm('r', 70, 0), "body:rot": lambda u: tilt(6, 0, 6 * wave(u)), "mw_root:pos": lambda u: move(0, 0.8 * wave(u, 0, 2), 0)}, pri=262)
ride("player.ride.strider_lava_balance", "Balancing Over Lava", STRIDER + " && q.main_hand != 'steering_stick'", 1.6, {
    "right_arm:rot": lambda u: arm('r', 10, 60 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 60 + 10 * wave(u, 0.5)), "body:rot": lambda u: tilt(0, 0, 8 * wave(u)), "head:rot": lambda u: [25, 0, 0]})
ride("player.ride.llama_passenger", "Riding Along On A Llama", R + " && q.vehicle == 'horse' && q.vehicle_speed < 0.01 && q.main_hand == 'empty' && q.idle_time > 20", 3.0, {
    "right_arm:rot": lambda u: arm('r', 10, -20, 30), "left_arm:rot": lambda u: arm('l', 10, -20, 30), "body:rot": lambda u: tilt(-8, 0, 0), "head:rot": lambda u: [-10, 20 * wave(u), 0]}, pri=259)

# ============================================================================ boats and minecarts
BOAT = R + " && q.vehicle == 'boat'"
ride("player.ride.boat_row", "Rowing Forward", BOAT + " && q.vehicle_speed >= 0.03 && math.abs(q.turn_rate) < 3", 1.0, {
    "right_arm:rot": lambda u: arm('r', 40 + 40 * cwave(u), 14), "left_arm:rot": lambda u: arm('l', 40 + 40 * cwave(u), 14), "body:rot": lambda u: tilt(10 * cwave(u), 0, 0)}, pri=262)
c = mob("player.ride.boat_turn_stroke", "Rowing One Side To Turn", CAT, P, 1.0, state(BOAT + " && math.abs(q.turn_rate) >= 3"), layer="overlay", pri=263, file=FP)
for i in range(9):
    u = i / 8.0
    k = cwave(u)
    c.key("right_arm", "rotation", u, ["-(40 + 40 * %g) * (q.turn_rate > 0 ? 1 : 0.2)" % round(k, 3), 0, 14], lerp="smooth")
    c.key("left_arm", "rotation", u, ["-(40 + 40 * %g) * (q.turn_rate > 0 ? 0.2 : 1)" % round(k, 3), 0, -14], lerp="smooth")
    c.key("body", "rotation", u, [0, "%g * (q.turn_rate > 0 ? 1 : -1)" % round(8 * wave(u), 2), 0], lerp="smooth")
ride("player.ride.boat_drift", "Drifting In A Boat", BOAT + " && q.vehicle_speed < 0.03 && q.idle_time < 15 && !q.is_fishing", 4.0, {
    "body:rot": lambda u: tilt(-6, 0, 3 * wave(u)), "right_arm:rot": lambda u: arm('r', 30, 20), "left_arm:rot": lambda u: arm('l', 30, 20), "head:rot": lambda u: [-5, 30 * wave(u), 0]}, group="boat_idle", weight=2)
ride("player.ride.boat_lounge", "Lounging Back In A Boat", BOAT + " && q.vehicle_speed < 0.03 && q.idle_time >= 15 && !q.is_fishing", 5.0, {
    "body:rot": lambda u: tilt(-25, 0, 2 * wave(u)), "right_arm:rot": lambda u: arm('r', 150, 30, -40), "left_arm:rot": lambda u: arm('l', 150, 30, -40), "head:rot": lambda u: [-20, 0, 0]})
ride("player.ride.boat_fishing", "Fishing From A Boat", BOAT + " && q.is_fishing", 3.0, {
    "body:rot": lambda u: tilt(6, 0, 2 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 10), "head:rot": lambda u: [14, 0, 0]}, pri=264, layer="additive")
ride("player.ride.boat_backpaddle", "Back-Paddling", BOAT + " && q.forward_speed < -0.02", 1.2, {
    "right_arm:rot": lambda u: arm('r', 60 - 30 * cwave(u), 14), "left_arm:rot": lambda u: arm('l', 60 - 30 * cwave(u), 14), "body:rot": lambda u: tilt(-8 * cwave(u), 0, 0)}, pri=264)
ride("player.ride.boat_storm", "Bracing In A Storm-Tossed Boat", BOAT + " && q.is_thundering && q.sky_exposed", 1.4, {
    "body:rot": lambda u: tilt(10, 0, 12 * wave(u)), "right_arm:rot": lambda u: arm('r', 20, 50), "left_arm:rot": lambda u: arm('l', 20, 50), "head:rot": lambda u: [20, 0, 0]}, pri=265)
ride("player.ride.boat_ice_glide", "Ice-Boat Speed Tuck", BOAT + " && q.vehicle_speed >= 0.6", 0.5, {
    "body:rot": lambda u: tilt(30, 0, 0), "right_arm:rot": lambda u: arm('r', 40, 10), "left_arm:rot": lambda u: arm('l', 40, 10), "head:rot": lambda u: [-30, 0, 0]}, pri=266)
CART = R + " && q.vehicle == 'minecart'"
ride("player.ride.cart_idle", "Sitting In A Minecart", CART + " && q.vehicle_speed < 0.05", 4.0, {
    "right_arm:rot": lambda u: arm('r', 20, 30), "left_arm:rot": lambda u: arm('l', 20, 30), "head:rot": lambda u: [0, 35 * wave(u), 0]})
ride("player.ride.cart_rush", "Hanging On In A Speeding Minecart", CART + " && q.vehicle_speed >= 0.4", 0.4, {
    "right_arm:rot": lambda u: arm('r', 40, 50), "left_arm:rot": lambda u: arm('l', 40, 50), "body:rot": lambda u: tilt(-14, 0, 2 * wave(u)), "head:rot": lambda u: [-14, 0, 0]}, pri=262)
ride("player.ride.cart_cruise", "Cruising The Rails", CART + " && q.vehicle_speed >= 0.05 && q.vehicle_speed < 0.4", 1.0, {
    "body:rot": lambda u: tilt(0, 0, 3 * wave(u, 0, 2)), "right_arm:rot": lambda u: arm('r', 10, 20), "left_arm:rot": lambda u: arm('l', 30, 10), "mw_root:pos": lambda u: move(0, 0.2 * wave(u, 0, 4), 0)}, pri=261)
ride("player.ride.cart_climb", "Leaning Forward On An Uphill Rail", CART + " && q.vehicle_vertical > 0.05", 1.0, {"body:rot": lambda u: tilt(16, 0, 0), "head:rot": lambda u: [-10, 0, 0]}, pri=263, layer="additive")
ride("player.ride.cart_drop", "Stomach-Lurching Rail Drop", CART + " && q.vehicle_vertical < -0.1", 0.6, {
    "body:rot": lambda u: tilt(-20, 0, 0), "right_arm:rot": lambda u: arm('r', 150, 30), "left_arm:rot": lambda u: arm('l', 150, 30), "head:rot": lambda u: [-25, 0, 0]}, pri=264)
life("player.ride.cart_corner", "Thrown Sideways On A Rail Bend", CAT, P, CART + " && math.abs(q.turn_rate) > 5", 0.5, FP, {"body:rot": lambda u: [0, 0, "q.turn_rate > 0 ? 16 : -16"]}, pri=91)

# ============================================================================ mounting and dismounting
MOUNTS = {
    "horse": ("Swinging Into The Saddle", 1.0, {"right_leg:rot": [(0, Z), (0.35, leg('r', 60, 70)), (0.7, leg('r', 70, 20)), (1.0, Z)], "body:rot": [(0, tilt(20)), (0.5, tilt(10, 0, 8)), (1.0, Z)],
                                              "right_arm:rot": [(0, arm('r', 100)), (0.5, arm('r', 60)), (1.0, Z)], "left_arm:rot": [(0, arm('l', 100)), (0.5, arm('l', 60)), (1.0, Z)]}),
    "boat": ("Stepping Into A Boat", 0.8, {"right_arm:rot": [(0, arm('r', 30, 50)), (0.4, arm('r', 20, 40)), (0.8, Z)], "left_arm:rot": [(0, arm('l', 30, 50)), (0.4, arm('l', 20, 40)), (0.8, Z)],
                                           "body:rot": [(0, tilt(0, 0, 10)), (0.3, tilt(0, 0, -8)), (0.8, Z)]}),
    "minecart": ("Hopping Into A Minecart", 0.7, {"mw_root:pos": [(0, move(0, 3, 0)), (0.3, move(0, -1, 0)), (0.7, Z)], "right_arm:rot": [(0, arm('r', 60, 30)), (0.7, Z)], "left_arm:rot": [(0, arm('l', 60, 30)), (0.7, Z)]}),
    "camel": ("Clambering Onto A Camel", 1.2, {"right_arm:rot": [(0, arm('r', 160)), (0.5, arm('r', 90)), (1.2, Z)], "left_arm:rot": [(0, arm('l', 150)), (0.6, arm('l', 80)), (1.2, Z)],
                                               "right_leg:rot": [(0, leg('r', 80)), (0.6, leg('r', 60, 40)), (1.2, Z)], "body:rot": [(0, tilt(30)), (0.7, tilt(10)), (1.2, Z)]}),
    "pig": ("Plopping Onto A Pig", 0.6, {"mw_root:pos": [(0, move(0, 2, 0)), (0.2, move(0, -1.2, 0)), (0.6, Z)], "right_arm:rot": [(0, arm('r', 90, 40)), (0.6, Z)], "left_arm:rot": [(0, arm('l', 90, 40)), (0.6, Z)],
                                         "head:rot": [(0, Z), (0.25, [20, 0, 0]), (0.6, Z)]}),
    "strider": ("Stepping Gingerly Onto A Strider", 1.0, {"right_leg:rot": [(0, leg('r', 50)), (0.5, leg('r', 60, 20)), (1.0, Z)], "right_arm:rot": [(0, arm('r', 10, 70)), (0.6, arm('r', 10, 50)), (1.0, Z)],
                                                          "left_arm:rot": [(0, arm('l', 10, 70)), (0.6, arm('l', 10, 50)), (1.0, Z)], "head:rot": [(0, [30, 0, 0]), (1.0, Z)]}),
}
for kind, (name, L, tracks) in MOUNTS.items():
    beat("player.mount." + kind, name, CAT, P, event("mount", "!q.is_dead && q.vehicle == '%s'" % kind), L, FP, tracks, pri=300, layer="action")
DISMOUNTS = {
    "horse": ("Swinging Down From The Saddle", 1.0, {"right_leg:rot": [(0, Z), (0.4, leg('r', 50, 60)), (0.8, leg('r', 20)), (1.0, Z)], "body:rot": [(0, Z), (0.4, tilt(15, 0, -10)), (1.0, Z)],
                                                   "mw_root:pos": [(0, move(0, 3, 0)), (0.7, move(0, -1, 0)), (1.0, Z)]}),
    "boat": ("Climbing Out Of A Boat", 0.8, {"right_leg:rot": [(0, leg('r', 70)), (0.4, leg('r', 30)), (0.8, Z)], "right_arm:rot": [(0, arm('r', 20, 40)), (0.5, arm('r', 10, 20)), (0.8, Z)],
                                             "body:rot": [(0, tilt(25)), (0.8, Z)]}),
    "minecart": ("Vaulting Out Of A Minecart", 0.7, {"right_leg:rot": [(0, leg('r', 80)), (0.35, leg('r', 20)), (0.7, Z)], "left_leg:rot": [(0, leg('l', 80)), (0.4, leg('l', 20)), (0.7, Z)],
                                                     "mw_root:pos": [(0, move(0, 2, 0)), (0.35, move(0, -1, 0)), (0.7, Z)]}),
    "camel": ("Sliding Down From A Camel", 1.0, {"body:rot": [(0, tilt(-10)), (0.4, tilt(20)), (1.0, Z)], "mw_root:pos": [(0, move(0, 4, 0)), (0.6, move(0, -1.5, 0)), (1.0, Z)],
                                                 "right_arm:rot": [(0, arm('r', 60, 60)), (1.0, Z)], "left_arm:rot": [(0, arm('l', 60, 60)), (1.0, Z)]}),
    "pig": ("Tumbling Off A Pig", 0.8, {"mw_root:rot": [(0, Z), (0.3, tilt(-20, 0, 15)), (0.8, Z)], "right_leg:rot": [(0, Z), (0.3, leg('r', 40)), (0.8, Z)], "head:rot": [(0, Z), (0.3, [-15, 0, 0]), (0.8, Z)]}),
    "strider": ("Hopping Off A Strider", 0.7, {"mw_root:pos": [(0, move(0, 2, 0)), (0.3, move(0, -1, 0)), (0.7, Z)], "right_arm:rot": [(0, arm('r', 10, 60)), (0.7, Z)], "left_arm:rot": [(0, arm('l', 10, 60)), (0.7, Z)]}),
}
for kind, (name, L, tracks) in DISMOUNTS.items():
    beat("player.dismount." + kind, name, CAT, P, event("dismount", "!q.is_dead && q.last_vehicle == '%s'" % kind), L, FP, tracks, pri=300, layer="action")

# ============================================================================ mounts carrying a rider
RIDDEN = "!q.is_dead && q.has_rider"
for T, sp, label, params in (
        ("minecraft:horse", "horse", "Horse", (dict(gait="walk", stride=22, duty=0.6, bob=0.4, pitch=0.8, roll=1.0, tail="tail", tail_amp=4, lift=16),
                                              dict(gait="trot", stride=30, duty=0.5, bob=1.2, pitch=0.6, roll=0.4, tail="tail", tail_amp=6, lift=22),
                                              dict(gait="canter", stride=40, duty=0.44, bob=1.8, pitch=3.5, roll=0.6, tail="tail", tail_amp=12, front_scale=1.2),
                                              dict(gait="gallop", stride=50, duty=0.36, bob=2.4, pitch=5.5, roll=0.3, tail="tail", tail_amp=16, front_scale=1.15, snap=0.1))),
        ("minecraft:donkey", "donkey", "Donkey", (dict(gait="walk", stride=20, duty=0.66, bob=0.8, pitch=1.6, roll=2.5, tail="tail", tail_amp=4, snap=0.2),
                                                 dict(gait="trot", stride=26, duty=0.52, bob=1.6, pitch=1.0, roll=1.2, tail="tail", tail_amp=8, snap=0.25))),
        ("minecraft:mule", "mule", "Mule", (dict(gait="amble", stride=22, duty=0.64, bob=0.7, pitch=1.2, roll=2.0, tail="tail", tail_amp=4, yaw=2),
                                           dict(gait="trot", stride=28, duty=0.5, bob=1.4, pitch=1.2, roll=0.8, tail="tail", tail_amp=8, snap=0.2, yaw=2.5, front_scale=0.9))),
        ("minecraft:skeleton_horse", "skeleton_horse", "Skeleton Horse", (dict(gait="pace", stride=30, duty=0.55, bob=0.6, pitch=2, roll=2, tail="tail", tail_amp=10, snap=0.3),
                                                                         dict(gait="bound", stride=46, duty=0.34, bob=2.4, pitch=7, roll=1.5, tail="tail", tail_amp=20, front_scale=1.3))),
        ("minecraft:zombie_horse", "zombie_horse", "Zombie Horse", (dict(gait="walk", stride=24, duty=0.66, bob=1.0, pitch=2.5, roll=3.5, tail="tail", tail_amp=6, yaw=3),
                                                                   dict(gait="canter", stride=34, duty=0.5, bob=2.0, pitch=4, roll=2, tail="tail", tail_amp=8, snap=0.2)))):
    F = FM + "/" + sp
    bands = ["q.ground_speed >= 0.01 && q.ground_speed < 0.09", "q.ground_speed >= 0.09 && q.ground_speed < 0.2", "q.ground_speed >= 0.2 && q.ground_speed < 0.3", "q.ground_speed >= 0.3"]
    names = ["Collected Walk Under Saddle", "Ridden Trot", "Ridden Canter", "Ridden Gallop"]
    lengths = [1.5, 0.9, 0.75, 0.55]
    for i, prm in enumerate(params):
        band = bands[i] if i < len(params) - 1 else bands[i].split(" && ")[0]
        gait("%s.ridden_%s" % (sp, ["walk", "trot", "canter", "gallop"][i]), "%s %s" % (label, names[i]), CAT, T, RIDDEN + " && q.is_on_ground && " + band, lengths[i], F, pri=110 + i, **prm)
T, F = "minecraft:horse", FM + "/horse"
beat("horse.ridden_leap", "Horse Clearing A Jump", CAT, T, event("jump", RIDDEN), 1.0, F, {
    "left_front_leg:rot": [(0, Z), (0.15, [-90, 0, 0]), (0.6, [-70, 0, 0]), (1.0, Z)], "right_front_leg:rot": [(0, Z), (0.15, [-95, 0, 0]), (0.6, [-70, 0, 0]), (1.0, Z)],
    "left_hind_leg:rot": [(0, [30, 0, 0]), (0.2, [60, 0, 0]), (0.7, [30, 0, 0]), (1.0, Z)], "right_hind_leg:rot": [(0, [30, 0, 0]), (0.2, [60, 0, 0]), (0.7, [30, 0, 0]), (1.0, Z)],
    "mw_center:rot": [(0, Z), (0.15, tilt(-18, 0, 0)), (0.55, tilt(14, 0, 0)), (1.0, Z)], "head_parts:rot": [(0, Z), (0.3, [20, 0, 0]), (1.0, Z)], "tail:rot": [(0, Z), (0.4, [-30, 0, 0]), (1.0, Z)]}, pri=160)
loop_state("horse.ridden_idle_shift", "Horse Shifting Under Its Rider", CAT, T, RIDDEN + " && q.ground_speed < 0.01", 3.0, F, {
    "left_hind_leg:rot": lambda u: [-8 * max(0, wave(u)), 0, 0], "head_parts:rot": lambda u: [10 + 6 * wave(u, 0.2), 10 * wave(u, 0.3), 0], "tail:rot": lambda u: [0, 14 * wave(u), 0]}, pri=105)
loop_state("horse.ridden_rear", "Horse Rearing With A Rider", CAT, T, RIDDEN + " && q.is_standing", 0.8, F, {"head_parts:rot": lambda u: [-20, 0, 6 * wave(u)], "tail:rot": lambda u: [-40, 0, 0]}, layer="additive", pri=75)
T, F = "minecraft:camel", FM + "/camel"
gait("camel.ridden_walk", "Camel Walking Under Riders", CAT, T, RIDDEN + " && q.ground_speed >= 0.01 && !q.is_charging", 2.0, F, pri=110, gait="pace", stride=22, duty=0.66, bob=0.4, pitch=0.4, roll=4, tail="tail", tail_amp=6,
     lift=10)
loop_state("camel.ridden_kneel_sway", "Camel Settling With Riders Aboard", CAT, T, RIDDEN + " && q.is_sitting", 4.0, F, {"head:rot": lambda u: [-14, 20 * wave(u, 0, 0.5), 0], "hump:rot": lambda u: [0, 0, 2 * wave(u)]},
           layer="additive", pri=72)
T, F = "minecraft:pig", FM + "/pig"
gait("pig.ridden_trot", "Pig Trotting Toward The Carrot", CAT, T, RIDDEN + " && q.ground_speed >= 0.01", 0.6, F, pri=110, keep_head=True, head_base=-14, head_bob=4, gait="trot", stride=32, duty=0.48, bob=1.0, pitch=3, roll=2,
     snap=0.2)
loop_state("pig.ridden_idle", "Pig Grumbling Under Its Rider", CAT, T, RIDDEN + " && q.ground_speed < 0.01", 2.0, F, {"head:rot": lambda u: [-6, 20 * wave(u), 0], "mw_center:pos": lambda u: move(0, -0.6, 0)}, pri=105)
T, F = "minecraft:strider", FM + "/strider"
c = mob("strider.ridden_stride", "Strider Striding Under A Rider", CAT, T, 1.4, state(RIDDEN + " && q.ground_speed >= 0.01"), layer="base", pri=110, file=F, time="q.limb_swing * 0.22",
        weight="math.clamp(q.limb_swing_amount * 2, 0, 1)")
c.cycle("right_leg", "rotation", lambda u: [-26 * cwave(u), 0, 3])
c.cycle("left_leg", "rotation", lambda u: [26 * cwave(u), 0, -3])
c.cycle("body", "rotation", lambda u: [0, 4 * cwave(u), 3 * wave(u)])
T, F = "minecraft:llama", FM + "/llama"
loop_state("llama.carrying_rider", "Llama Patiently Carrying A Rider", CAT, T, RIDDEN, 3.0, F, {"head:rot": lambda u: [-6, 15 * wave(u), 0], "right_chest:rot": lambda u: [0, 0, 3 * wave(u)]}, layer="additive", pri=70)

# ============================================================================ mob jockeys
loop_state("zombie.chicken_jockey", "Baby Zombie Riding A Chicken", CAT, "minecraft:zombie", "!q.is_dead && q.is_riding && q.is_baby", 0.6, FM + "/jockeys", {
    "right_arm:rot": lambda u: arm('r', 160, 20 + 20 * wave(u)), "left_arm:rot": lambda u: arm('l', 100, 30), "mw_root:pos": lambda u: move(0, 0.8 * max(0, wave(u, 0, 2)), 0), "head:rot": lambda u: [-10, 0, 10 * wave(u)]},
    pri=150)
loop_state("skeleton.spider_jockey", "Skeleton Riding A Spider", CAT, "minecraft:skeleton", "!q.is_dead && q.is_riding", 1.0, FM + "/jockeys", {
    "body:rot": lambda u: tilt(-4, 0, 4 * wave(u, 0, 2)), "mw_root:pos": lambda u: move(0, 0.3 * wave(u, 0, 4), 0)}, layer="additive", pri=80)
loop_state("piglin.hoglin_rider", "Baby Piglin Riding A Hoglin", CAT, "minecraft:piglin", "!q.is_dead && q.is_riding", 0.5, FM + "/jockeys", {
    "right_arm:rot": lambda u: arm('r', 170, 10 + 30 * wave(u)), "left_arm:rot": lambda u: arm('l', 170, 10 + 30 * wave(u, 0.5)), "mw_root:pos": lambda u: move(0, 1 * max(0, wave(u)), 0)}, pri=150)
loop_state("zombified_piglin.strider_jockey", "Zombified Piglin Riding A Strider", CAT, "minecraft:zombified_piglin", "!q.is_dead && q.is_riding", 2.0, FM + "/jockeys", {
    "right_arm:rot": lambda u: arm('r', 60, 10), "body:rot": lambda u: tilt(6, 0, 6 * wave(u)), "head:rot": lambda u: [20, 15 * wave(u, 0.2), 0]}, pri=150)
loop_state("chicken.carrying_jockey", "Chicken Scampering Under A Tiny Rider", CAT, "minecraft:chicken", RIDDEN, 0.3, FM + "/jockeys", {
    "right_wing:rot": lambda u: [0, 0, 30 + 20 * wave(u)], "left_wing:rot": lambda u: [0, 0, -30 - 20 * wave(u)], "head:rot": lambda u: [-20, 0, 0]}, layer="additive", pri=75)
loop_state("spider.carrying_skeleton", "Spider Carrying A Skeleton", CAT, "minecraft:spider", RIDDEN, 1.0, FM + "/jockeys", {"body1:rot": lambda u: [3 * wave(u), 0, 0], "head:rot": lambda u: [-6, 0, 0]},
           layer="additive", pri=72)
# one shared clip: every equine model carries its head the same way under saddle (the @equine group shares the rig)
loop_state("equine.ridden_collection", "Head Collected For The Rider", CAT, "@equine", RIDDEN + " && q.ground_speed >= 0.01", 1.0, FM + "/equine", {"head_parts:rot": lambda u: [14 + 2 * wave(u, 0, 2), 0, 0]},
           layer="additive", pri=70)

# ============================================================================ riding: more situations
ride("player.ride.look_back", "Twisting Round In The Saddle", R + " && math.abs(q.head_yaw) > 70 && q.vehicle != 'minecart'", 1.0, {"body:rot": lambda u: tilt(0, "q.head_yaw * 0.35", 0)}, layer="additive", pri=92)
ride("player.ride.eat_in_saddle", "Eating In The Saddle", R + " && q.is_using_item && q.use_anim == 'eat'", 0.6, {"body:rot": lambda u: tilt(6, 0, 0), "head:rot": lambda u: [10 + 4 * wave(u, 0, 2), 0, 0],
                                                                                                         "left_arm:rot": lambda u: arm('l', 30, 4)}, pri=267)
ride("player.ride.drink_in_saddle", "Drinking On The Move", R + " && q.is_using_item && q.use_anim == 'drink'", 1.0, {"body:rot": lambda u: tilt(-10, 0, 0), "head:rot": lambda u: [-30, 0, 0],
                                                                                                             "left_arm:rot": lambda u: arm('l', 30, 4)}, pri=267)
ride("player.ride.spyglass_scout", "Scouting With A Spyglass From The Saddle", R + " && q.is_using_item && q.use_anim == 'spyglass'", 2.0, {"body:rot": lambda u: tilt(-6, 0, 0),
                                                                                                                                   "left_arm:rot": lambda u: arm('l', 25, 4)}, pri=268, layer="additive")
ride("player.ride.horse_swim", "Lifting Your Legs As The Horse Swims", HORSE + " && q.is_in_water", 1.2, {
    "right_leg:rot": lambda u: leg('r', 100, 30), "left_leg:rot": lambda u: leg('l', 100, 30), "body:rot": lambda u: tilt(-8, 0, 3 * wave(u)), "right_arm:rot": lambda u: arm('r', 50, 4), "left_arm:rot": lambda u: arm('l', 50, 4)},
     pri=269)
ride("player.ride.saddle_doze", "Dozing In The Saddle", HORSE + " && q.vehicle_speed < 0.01 && q.is_night && q.idle_time > 30", 4.0, {
    "head:rot": lambda u: [35 + 8 * spike(u, 0.6, 6), 0, 8], "body:rot": lambda u: tilt(14, 0, 2 * wave(u)), "right_arm:rot": lambda u: arm('r', 10, 6), "left_arm:rot": lambda u: arm('l', 10, 6)}, pri=258)
ride("player.ride.cart_doze", "Nodding Off In A Minecart", CART + " && q.idle_time > 30", 4.0, {
    "head:rot": lambda u: [30 + 10 * spike(u, 0.5, 6), 0, -10], "right_arm:rot": lambda u: arm('r', 0, -10, 30), "left_arm:rot": lambda u: arm('l', 0, -10, 30)}, pri=259)
ride("player.ride.camel_back_seat", "Holding On From The Camel's Back Seat", CAMEL + " && q.seat == 1", 1.8, {
    "right_arm:rot": lambda u: arm('r', 60, -20, 30), "left_arm:rot": lambda u: arm('l', 60, -20, 30), "body:rot": lambda u: tilt(14, 0, 5 * wave(u)), "head:rot": lambda u: [0, 25 * wave(u, 0.25), 0]}, pri=265)
ride("player.ride.boat_passenger", "Riding As A Boat Passenger", BOAT + " && q.seat == 1", 3.0, {
    "right_arm:rot": lambda u: arm('r', 10, 30), "left_arm:rot": lambda u: arm('l', 10, 30), "body:rot": lambda u: tilt(-4, 0, 2 * wave(u)), "head:rot": lambda u: [0, 35 * wave(u), 0]}, pri=266)
beat("player.ride.mounted_bow_release", "Loosing An Arrow From Horseback", CAT, P, event("use_stop", R + " && q.main_hand == 'bow'"), 0.6, FP, {
    "body:rot": [(0, tilt(-2, -30, 0)), (0.06, tilt(-8, -25, 0), "out_expo"), (0.6, Z)], "head:rot": [(0, [0, 30, 0]), (0.6, Z)]}, pri=301, layer="action")
beat("player.ride.mounted_crossbow", "Mounted Crossbow Shot", CAT, P, event("crossbow_fire", R), 0.6, FP, {"body:rot": [(0, Z), (0.05, tilt(-12, 8, 0), "out_expo"), (0.6, Z)],
                                                                                                   "right_leg:rot": [(0, Z), (0.08, leg('r', -10, 6)), (0.6, Z)], "left_leg:rot": [(0, Z), (0.08, leg('l', -10, 6)), (0.6, Z)],
                                                                                                   "head:rot": [(0, Z), (0.05, [-6, 0, 4]), (0.6, Z)]}, pri=301, layer="reaction")
ride("player.ride.boat_snack", "Snacking In A Boat", BOAT + " && q.is_using_item && q.use_anim == 'eat'", 0.6, {"body:rot": lambda u: tilt(10, 0, 0), "right_arm:rot": lambda u: arm('r', 30, 10)}, pri=267)

# ============================================================================ mounts: more behaviour under a rider
T, F = "minecraft:donkey", FM + "/donkey"
loop_state("donkey.ridden_balk", "Donkey Balking Under Its Rider", CAT, T, RIDDEN + " && q.ground_speed < 0.01 && q.trait_confidence > 0.5", 2.0, F, {
    "left_front_leg:rot": lambda u: [-15, 0, 0], "right_front_leg:rot": lambda u: [-15, 0, 0], "head_parts:rot": lambda u: [-15, 20 * wave(u), 0], "mw_center:rot": lambda u: tilt(-5, 0, 0)}, pri=106)
T, F = "minecraft:mule", FM + "/mule"
loop_state("mule.ridden_idle", "Mule Flicking Its Ears Under A Rider", CAT, T, RIDDEN + " && q.ground_speed < 0.01", 2.4, F, {
    "left_ear:rot": lambda u: [0, 0, -20 * spike(u, 0.2, 6)], "right_ear:rot": lambda u: [0, 0, 20 * spike(u, 0.7, 6)], "head_parts:rot": lambda u: [12, 0, 0]}, pri=105)
T, F = "minecraft:skeleton_horse", FM + "/skeleton_horse"
life("skeleton_horse.ridden_rattle", "Skeleton Horse Jarring Under A Rider", CAT, T, RIDDEN, 0.4, F, {"mw_center:pos": lambda u: move(0, 0.3 * spike(u, 0, 4, 2), 0), "mane:rot": lambda u: [0, 0, 3 * wave(u, 0.1, 2)],
                                                                                                 "left_ear:rot": lambda u: [0, 0, -4 * spike(u, 0.2, 4, 2)]})
T, F = "minecraft:zombie_horse", FM + "/zombie_horse"
loop_state("zombie_horse.ridden_idle", "Zombie Horse Swaying Under A Rider", CAT, T, RIDDEN + " && q.ground_speed < 0.01", 3.4, F, {
    "mw_center:rot": lambda u: tilt(0, 0, 3 * wave(u)), "head_parts:rot": lambda u: [30, 0, 10 * wave(u, 0.2)]}, pri=105)
T, F = "minecraft:camel", FM + "/camel"
loop_state("camel.ridden_dash", "Camel Dashing With Riders", CAT, T, RIDDEN + " && q.is_charging", 0.55, F, {
    "head:rot": lambda u: [20, 0, 0], "hump:rot": lambda u: [8 * wave(u, 0, 2), 0, 0], "tail:rot": lambda u: [-30, 0, 0]}, layer="additive", pri=75)
T, F = "minecraft:strider", FM + "/strider"
loop_state("strider.ridden_idle", "Strider Waiting With A Rider", CAT, T, RIDDEN + " && q.ground_speed < 0.01 && !q.is_suffocating", 3.0, F, {
    "body:rot": lambda u: [0, 12 * wave(u), 0], "right_top_bristle:rot": lambda u: [0, 0, 8 * wave(u, 0.2)], "left_top_bristle:rot": lambda u: [0, 0, -8 * wave(u, 0.7)]}, pri=105)
loop_state("strider.ridden_cold", "Strider Shivering Under A Rider", CAT, T, RIDDEN + " && q.is_suffocating", 0.25, F, {"body:rot": lambda u: [0, 0, 4 * wave(u)], "mw_center:pos": lambda u: move(0, -1, 0)}, pri=131)
T, F = "minecraft:horse", FM + "/horse"
beat("horse.ridden_landing", "Horse Landing Heavily With A Rider", CAT, T, event("land", RIDDEN), 0.6, F, {
    "left_front_leg:rot": [(0, [-20, 0, 0]), (0.08, [10, 0, 0]), (0.6, Z)], "right_front_leg:rot": [(0, [-20, 0, 0]), (0.08, [10, 0, 0]), (0.6, Z)], "mw_center:pos": [(0, Z), (0.08, move(0, -1.2, 0)), (0.6, Z)],
    "head_parts:rot": [(0, Z), (0.1, [20, 0, 0]), (0.6, Z)]}, layer="gesture", events=[(0.05, "stomp", {"strength": "0.6"})])
life("horse.ridden_pivot", "Horse Pivoting On Its Haunches", CAT, T, RIDDEN + " && math.abs(q.turn_rate) > 8 && q.ground_speed < 0.1", 0.5, F, {
    "mw_center:rot": lambda u: tilt(-6, 0, 0), "left_front_leg:rot": lambda u: [-30 * max(0, wave(u)), 0, 0], "right_front_leg:rot": lambda u: [-30 * max(0, wave(u, 0.5)), 0, 0]}, pri=73)
loop_state("horse.ridden_prance", "Horse Prancing Nervously", CAT, T, RIDDEN + " && q.near_hostile && q.ground_speed < 0.05", 0.7, F, {
    "left_front_leg:rot": lambda u: [-45 * max(0, wave(u)), 0, 0], "right_front_leg:rot": lambda u: [-45 * max(0, wave(u, 0.5)), 0, 0], "head_parts:rot": lambda u: [-20, 10 * wave(u), 0],
    "tail:rot": lambda u: [-20, 20 * wave(u, 0.3), 0]}, pri=112)
ride("player.ride.pig_whoop", "Whooping On A Speeding Pig", PIG + " && q.vehicle_speed > 0.15", 0.8, {
    "left_arm:rot": lambda u: arm('l', 170, 20 + 20 * wave(u)), "head:rot": lambda u: [-20, 0, 10 * wave(u)], "body:rot": lambda u: tilt(-6, 0, 4 * wave(u))}, pri=264)
ride("player.ride.strider_lava_peer", "Peering Down Into The Lava", STRIDER + " && q.vehicle_speed < 0.01 && q.head_pitch > 30", 3.0, {
    "body:rot": lambda u: tilt(26, 0, 0), "right_arm:rot": lambda u: arm('r', 20, 40), "left_arm:rot": lambda u: arm('l', 20, 40), "head:rot": lambda u: [10, 20 * wave(u, 0, 0.5), 0]}, pri=263)

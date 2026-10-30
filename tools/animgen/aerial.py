"""Flying and aerial movement (category: aerial): elytra flight, creative flight, levitation, slow falling,
riptide, pearl arrivals and the airborne repertoire of flying mobs."""
from core import arm, leg
from mobkit import mob, life, loop_state, beat, Z, state, event, wave, cwave, tilt, move

CAT = "aerial"
P = "@player"
LIVE = "!q.is_dead && !q.is_riding"
GLIDE = LIVE + " && q.is_fall_flying"
FLY = LIVE + " && q.is_flying && !q.is_fall_flying"
FP, FM = "player/aerial", "mobs/aerial"


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def air(cid, name, when, L, fns, pri=320, layer="base", target=P, file=FP, group=None, weight=1):
    return loop_state(cid, name, CAT, target, when, L, file, fns, pri=pri, layer=layer, group=group, weight=weight)


# ============================================================================ elytra
air("player.elytra.glide", "Elytra Glide", GLIDE + " && math.abs(q.vertical_speed) <= 0.5 && q.ground_speed <= 1.2 && q.ground_speed >= 0.5", 2.4, {
    "right_arm:rot": lambda u: arm('r', -20, 30 + 4 * wave(u)), "left_arm:rot": lambda u: arm('l', -20, 30 + 4 * wave(u, 0.5)), "right_leg:rot": lambda u: leg('r', -6 + 3 * wave(u, 0.2), 4),
    "left_leg:rot": lambda u: leg('l', -6 + 3 * wave(u, 0.7), 4), "head:rot": lambda u: [-10, 0, 0]})
air("player.elytra.dive", "Elytra Power Dive", GLIDE + " && q.vertical_speed < -0.5", 0.8, {
    "right_arm:rot": lambda u: arm('r', -35, 4, 10), "left_arm:rot": lambda u: arm('l', -35, 4, 10), "right_leg:rot": lambda u: leg('r', 0, -2), "left_leg:rot": lambda u: leg('l', 0, -2),
    "head:rot": lambda u: [-30, 0, 0], "body:rot": lambda u: [0.8 * wave(u, 0, 3), 0, 0]}, pri=322)
air("player.elytra.climb", "Elytra Climb", GLIDE + " && q.vertical_speed > 0.15", 1.4, {
    "right_arm:rot": lambda u: arm('r', 10, 70 + 6 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 70 + 6 * wave(u)), "right_leg:rot": lambda u: leg('r', 10, 8), "left_leg:rot": lambda u: leg('l', 10, 8),
    "head:rot": lambda u: [-35, 0, 0], "body:rot": lambda u: tilt(-8, 0, 0)}, pri=321)
air("player.elytra.speed_tuck", "Elytra Superman Tuck", GLIDE + " && q.ground_speed > 1.2 && q.vertical_speed >= -0.5", 1.0, {
    "right_arm:rot": lambda u: arm('r', 175, 4), "left_arm:rot": lambda u: arm('l', -30, 6), "right_leg:rot": lambda u: leg('r', 0), "left_leg:rot": lambda u: leg('l', 0, -2), "head:rot": lambda u: [-25, 0, 0]}, pri=323)
air("player.elytra.slow_drift", "Elytra Lazy Drift", GLIDE + " && q.ground_speed < 0.5 && q.vertical_speed >= -0.5", 3.0, {
    "right_arm:rot": lambda u: arm('r', 0, 60 + 15 * wave(u)), "left_arm:rot": lambda u: arm('l', 0, 60 + 15 * wave(u, 0.5)), "right_leg:rot": lambda u: leg('r', 15 * wave(u, 0.3)),
    "left_leg:rot": lambda u: leg('l', 15 * wave(u, 0.8)), "head:rot": lambda u: [-5, 25 * wave(u), 0]}, pri=320)
life("player.elytra.bank", "Elytra Banking Turn", CAT, P, GLIDE + " && math.abs(q.turn_rate) > 3", 0.8, FP, {"body:rot": lambda u: [0, 0, "q.turn_rate > 0 ? -16 : 16"],
                                                                                                        "head:rot": lambda u: [0, 0, "q.turn_rate > 0 ? 8 : -8"]}, pri=90)
loop_state("player.elytra.barrel_roll", "Elytra Barrel Roll", CAT, P, GLIDE + " && math.abs(q.turn_rate) > 18", 0.9, FP, {"mw_root:rot": lambda u: [0, 0, 360 * u]}, layer="additive", pri=91, min_time=0.9)
life("player.elytra.look_back", "Glancing Back Mid-Flight", CAT, P, GLIDE + " && math.abs(q.head_yaw) > 55", 1.0, FP, {"body:rot": lambda u: [0, "q.head_yaw * 0.3", "q.head_yaw * -0.15"],
                                                                                                    "right_arm:rot": lambda u: [10, 0, "q.head_yaw > 0 ? 40 : 20"]}, pri=92)
air("player.elytra.storm_tuck", "Elytra Flight Through Rain", GLIDE + " && q.is_raining && q.sky_exposed && math.abs(q.vertical_speed) <= 0.5", 1.6, {
    "right_arm:rot": lambda u: arm('r', -25, 18), "left_arm:rot": lambda u: arm('l', -25, 18), "head:rot": lambda u: [8, 0, 0], "body:rot": lambda u: tilt(0, 0, 3 * wave(u, 0, 2))}, pri=324)
beat("player.elytra.firework_boost", "Firework Boost", CAT, P, event("boost", GLIDE), 0.9, FP, {
    "right_arm:rot": [(0, Z), (0.1, arm('r', -40, 10), "out_expo"), (0.9, arm('r', -20, 30))], "left_arm:rot": [(0, Z), (0.1, arm('l', -40, 10), "out_expo"), (0.9, arm('l', -20, 30))],
    "head:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.9, [-10, 0, 0])], "right_leg:rot": [(0, Z), (0.1, leg('r', -10)), (0.9, Z)], "left_leg:rot": [(0, Z), (0.1, leg('l', -10)), (0.9, Z)]}, pri=360, layer="action",
     events=[(0.0, "shake", {"intensity": "0.15", "duration": "0.3"})])
beat("player.elytra.takeoff", "Elytra Spread And Takeoff", CAT, P, event("glide_start", LIVE), 0.7, FP, {
    "right_arm:rot": [(0, arm('r', 0, 10)), (0.25, arm('r', 20, 90), "out_back"), (0.7, arm('r', -20, 30))], "left_arm:rot": [(0, arm('l', 0, 10)), (0.25, arm('l', 20, 90), "out_back"), (0.7, arm('l', -20, 30))],
    "right_leg:rot": [(0, leg('r', 40)), (0.4, leg('r', -6)), (0.7, Z)], "left_leg:rot": [(0, leg('l', 20)), (0.4, leg('l', -6)), (0.7, Z)]}, pri=361, layer="action",
     events=[(0.1, "whoosh", {"weight": "heavy"})])
beat("player.elytra.landing_flare", "Elytra Landing Flare", CAT, P, event("glide_stop", LIVE + " && q.ground_speed > 0.15"), 0.9, FP, {
    "right_arm:rot": [(0, arm('r', 20, 80)), (0.4, arm('r', 30, 50)), (0.9, Z)], "left_arm:rot": [(0, arm('l', 20, 80)), (0.4, arm('l', 30, 50)), (0.9, Z)],
    "body:rot": [(0, tilt(-20)), (0.4, tilt(10)), (0.9, Z)], "right_leg:rot": [(0, leg('r', 50)), (0.4, leg('r', 30)), (0.9, Z)], "left_leg:rot": [(0, leg('l', 20)), (0.4, leg('l', 10)), (0.9, Z)]}, pri=362, layer="action",
     events=[(0.3, "particle", {"particle": "dust_puff", "count": "8", "at": "feet", "spread": "0.5"})])
beat("player.elytra.stall_recover", "Elytra Stall Recovery", CAT, P, event("glide_stop", LIVE + " && q.ground_speed <= 0.15 && !q.is_on_ground"), 1.0, FP, {
    "right_arm:rot": [(0, Z), (0.2, arm('r', 160, 50)), (0.4, arm('r', 80, 70)), (0.6, arm('r', 160, 50)), (1.0, arm('r', 40, 40))],
    "left_arm:rot": [(0, Z), (0.25, arm('l', 150, 50)), (0.45, arm('l', 70, 70)), (0.65, arm('l', 150, 50)), (1.0, arm('l', 40, 40))], "head:rot": [(0, Z), (0.3, [30, 0, 0]), (1.0, Z)]}, pri=363, layer="action")
beat("player.elytra.wall_crash", "Elytra Wall Crash", CAT, P, event("hurt", "!q.is_dead && q.hurt_kind == 'kinetic'"), 1.2, FP, {
    "body:rot": [(0, Z), (0.06, tilt(-25, 0, 10), "out_expo"), (0.5, tilt(10, 0, -6)), (1.2, Z)], "head:rot": [(0, Z), (0.06, [-30, 0, 15]), (1.2, Z)],
    "right_arm:rot": [(0, Z), (0.06, arm('r', 60, 70)), (0.6, arm('r', 30, 40)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.06, arm('l', 80, 60)), (0.6, arm('l', 30, 40)), (1.2, Z)]}, pri=380, layer="reaction",
     events=[(0.0, "shake", {"intensity": "0.7", "duration": "0.5"}), (0.0, "impact", {"material": "stone", "strength": "1"})])

# ============================================================================ creative flight
air("player.fly.hover", "Creative Hover", FLY + " && q.ground_speed < 0.02 && math.abs(q.vertical_speed) < 0.05 && q.idle_time < 10", 3.0, {
    "right_leg:rot": lambda u: leg('r', 10 + 8 * wave(u)), "left_leg:rot": lambda u: leg('l', 4 + 8 * wave(u, 0.5)), "mw_root:pos": lambda u: move(0, 0.5 * wave(u), 0),
    "right_arm:rot": lambda u: arm('r', 4 * wave(u, 0.3), 8), "left_arm:rot": lambda u: arm('l', 4 * wave(u, 0.8), 8)}, pri=310, group="fly_idle", weight=3)
air("player.fly.look_around", "Hovering Survey", FLY + " && q.ground_speed < 0.02 && math.abs(q.vertical_speed) < 0.05 && q.idle_time < 10", 5.0, {
    "head:rot": lambda u: [15 * wave(u, 0.2), 50 * wave(u), 0], "body:rot": lambda u: tilt(0, 15 * wave(u, 0.05), 0), "right_leg:rot": lambda u: leg('r', 20), "left_leg:rot": lambda u: leg('l', 6)},
    pri=310, group="fly_idle", weight=2)
air("player.fly.cross_legged", "Floating Cross-Legged", FLY + " && q.ground_speed < 0.02 && q.idle_time >= 10 && q.idle_time < 40", 4.0, {
    "right_leg:rot": lambda u: leg('r', 80, -25, 30), "left_leg:rot": lambda u: leg('l', 80, -25, 30), "right_arm:rot": lambda u: arm('r', 30, -10), "left_arm:rot": lambda u: arm('l', 30, -10),
    "mw_root:pos": lambda u: move(0, 0.6 * wave(u), 0), "body:rot": lambda u: tilt(4 + 2 * wave(u, 0.2), 0, 0)}, pri=311)
air("player.fly.lounge", "Lounging In Mid-Air", FLY + " && q.ground_speed < 0.02 && q.idle_time >= 40", 6.0, {
    "mw_root:rot": lambda u: tilt(-75, 0, 2 * wave(u)), "right_arm:rot": lambda u: arm('r', 160, 30, -30), "left_arm:rot": lambda u: arm('l', 160, 30, -30), "right_leg:rot": lambda u: leg('r', 20, 0),
    "left_leg:rot": lambda u: leg('l', 60, -10), "mw_root:pos": lambda u: move(0, 0.4 * wave(u), 0)}, pri=312)
air("player.fly.forward", "Creative Flight Forward", FLY + " && q.ground_speed >= 0.02 && !q.is_sprinting && q.forward_speed >= 0", 1.6, {
    "body:rot": lambda u: tilt(20, 0, 0), "right_leg:rot": lambda u: leg('r', -10 + 6 * wave(u)), "left_leg:rot": lambda u: leg('l', -4 + 6 * wave(u, 0.5)),
    "right_arm:rot": lambda u: arm('r', -10, 14), "left_arm:rot": lambda u: arm('l', -10, 14)}, pri=313)
air("player.fly.sprint", "Creative Superhero Flight", FLY + " && q.is_sprinting", 1.0, {
    "body:rot": lambda u: tilt(60, 0, 0), "right_arm:rot": lambda u: arm('r', 170, 6), "left_arm:rot": lambda u: arm('l', 170, 6), "right_leg:rot": lambda u: leg('r', -6, 2), "left_leg:rot": lambda u: leg('l', -6, 2),
    "head:rot": lambda u: [-45, 0, 0]}, pri=314)
air("player.fly.ascend", "Creative Ascent", FLY + " && q.vertical_speed >= 0.1", 1.0, {
    "right_arm:rot": lambda u: arm('r', -15, 20), "left_arm:rot": lambda u: arm('l', -15, 20), "right_leg:rot": lambda u: leg('r', -8, 3), "left_leg:rot": lambda u: leg('l', -8, 3), "head:rot": lambda u: [-25, 0, 0],
    "body:rot": lambda u: tilt(-6, 0, 0)}, pri=315)
air("player.fly.descend", "Creative Descent", FLY + " && q.vertical_speed <= -0.1", 1.2, {
    "right_arm:rot": lambda u: arm('r', 10, 40 + 5 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 40 + 5 * wave(u, 0.5)), "right_leg:rot": lambda u: leg('r', 30), "left_leg:rot": lambda u: leg('l', 10),
    "head:rot": lambda u: [25, 0, 0]}, pri=315)
air("player.fly.strafe", "Creative Sideways Drift", FLY + " && math.abs(q.strafe_speed) > 0.05 && math.abs(q.forward_speed) < 0.05", 1.4, {
    "body:rot": lambda u: [0, 0, "q.strafe_speed > 0 ? -14 : 14"], "right_leg:rot": lambda u: leg('r', 6, 10), "left_leg:rot": lambda u: leg('l', 6, 10), "right_arm:rot": lambda u: arm('r', 0, 25), "left_arm:rot": lambda u: arm('l', 0, 25)},
    pri=316)
air("player.fly.backward", "Creative Backward Float", FLY + " && q.forward_speed < -0.03", 1.6, {
    "body:rot": lambda u: tilt(-14, 0, 0), "right_leg:rot": lambda u: leg('r', 25), "left_leg:rot": lambda u: leg('l', 15), "right_arm:rot": lambda u: arm('r', 30, 20), "left_arm:rot": lambda u: arm('l', 30, 20)}, pri=316)
air("player.fly.build_peer", "Peering Down While Building", FLY + " && q.ground_speed < 0.02 && q.head_pitch > 50", 2.0, {
    "body:rot": lambda u: tilt(30, 0, 0), "right_leg:rot": lambda u: leg('r', -10), "left_leg:rot": lambda u: leg('l', 20), "head:rot": lambda u: [10, 10 * wave(u, 0, 0.5), 0]}, pri=317)
air("player.fly.carry_block", "Flying With Building Blocks", FLY + " && q.ground_speed >= 0.02 && q.main_hand == 'block'", 1.6, {
    "body:rot": lambda u: tilt(18, 0, 0), "right_arm:rot": lambda u: arm('r', 50, 4), "left_arm:rot": lambda u: arm('l', -10, 16), "right_leg:rot": lambda u: leg('r', -8), "left_leg:rot": lambda u: leg('l', 4)}, pri=318)
beat("player.fly.liftoff", "Creative Liftoff", CAT, P, event("fly_start", LIVE), 0.6, FP, {
    "right_leg:rot": [(0, leg('r', 40)), (0.2, leg('r', -10), "out_expo"), (0.6, leg('r', 10))], "left_leg:rot": [(0, leg('l', 40)), (0.2, leg('l', -10), "out_expo"), (0.6, leg('l', 4))],
    "right_arm:rot": [(0, arm('r', -20)), (0.2, arm('r', 20, 40)), (0.6, arm('r', 0, 8))], "left_arm:rot": [(0, arm('l', -20)), (0.2, arm('l', 20, 40)), (0.6, arm('l', 0, 8))]}, pri=360, layer="action")
beat("player.fly.touchdown", "Creative Touchdown", CAT, P, event("fly_stop", LIVE), 0.6, FP, {
    "right_leg:rot": [(0, leg('r', 10)), (0.2, leg('r', 30)), (0.6, Z)], "left_leg:rot": [(0, leg('l', 4)), (0.2, leg('l', 30)), (0.6, Z)], "mw_root:pos": [(0, Z), (0.2, move(0, -1.5, 0)), (0.6, Z)],
    "right_arm:rot": [(0, Z), (0.2, arm('r', 20, 20)), (0.6, Z)], "left_arm:rot": [(0, Z), (0.2, arm('l', 20, 20)), (0.6, Z)]}, pri=361, layer="action")

# ============================================================================ effects and special movement
air("player.levitate.flail", "Levitation Flailing", LIVE + " && q.is_levitating && q.trait_confidence <= 0.6", 1.2, {
    "right_arm:rot": lambda u: arm('r', 100 + 40 * wave(u), 40 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 90 + 40 * wave(u, 0.5), 40 * wave(u, 0.8)),
    "right_leg:rot": lambda u: leg('r', 25 * wave(u, 0.2)), "left_leg:rot": lambda u: leg('l', 25 * wave(u, 0.7)), "head:rot": lambda u: [30, 20 * wave(u, 0, 0.5), 0]}, pri=330)
air("player.levitate.serene", "Serene Levitation", LIVE + " && q.is_levitating && q.trait_confidence > 0.6", 4.0, {
    "right_arm:rot": lambda u: arm('r', 10, 45 + 5 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 45 + 5 * wave(u, 0.5)), "right_leg:rot": lambda u: leg('r', 4), "left_leg:rot": lambda u: leg('l', 10, -6),
    "head:rot": lambda u: [-20, 0, 0], "mw_root:rot": lambda u: [0, 20 * wave(u, 0, 0.5), 0]}, pri=331)
air("player.slow_fall.drift", "Slow-Falling Drift", LIVE + " && q.slow_falling && !q.is_on_ground && !q.is_fall_flying && q.vertical_speed < 0", 3.0, {
    "right_arm:rot": lambda u: arm('r', 20, 80 + 5 * wave(u)), "left_arm:rot": lambda u: arm('l', 20, 80 + 5 * wave(u, 0.5)), "right_leg:rot": lambda u: leg('r', 10 * wave(u, 0.2), 6),
    "left_leg:rot": lambda u: leg('l', 10 * wave(u, 0.7), 6), "mw_root:rot": lambda u: tilt(0, 0, 4 * wave(u))}, pri=332)
beat("player.slow_fall.feather_land", "Feather-Light Landing", CAT, P, event("land", LIVE + " && q.slow_falling"), 0.9, FP, {
    "right_arm:rot": [(0, arm('r', 20, 80)), (0.5, arm('r', 10, 30)), (0.9, Z)], "left_arm:rot": [(0, arm('l', 20, 80)), (0.5, arm('l', 10, 30)), (0.9, Z)],
    "right_leg:rot": [(0, leg('r', 10)), (0.3, leg('r', 15)), (0.9, Z)], "mw_root:pos": [(0, Z), (0.3, move(0, -0.6, 0)), (0.9, Z)]}, pri=200, layer="gesture")
air("player.riptide.spin", "Riptide Corkscrew", LIVE + " && q.is_spin_attack", 0.5, {
    "right_arm:rot": lambda u: arm('r', 175, 2), "left_arm:rot": lambda u: arm('l', 175, 2), "right_leg:rot": lambda u: leg('r', 0, -3), "left_leg:rot": lambda u: leg('l', 0, -3), "head:rot": lambda u: [-30, 0, 0]}, pri=340)
beat("player.riptide.launch", "Riptide Launch", CAT, P, event("riptide_start", LIVE), 0.4, FP, {
    "right_leg:rot": [(0, leg('r', 50)), (0.15, leg('r', -10), "out_expo"), (0.4, Z)], "left_leg:rot": [(0, leg('l', 50)), (0.15, leg('l', -10), "out_expo"), (0.4, Z)],
    "body:rot": [(0, tilt(20)), (0.15, tilt(-10)), (0.4, Z)]}, pri=365, layer="action", events=[(0.0, "particle", {"particle": "splash", "count": "16", "at": "body", "spread": "0.6"})])
beat("player.riptide.tumble_out", "Riptide Tumble Out", CAT, P, event("riptide_stop", LIVE), 1.0, FP, {
    "mw_root:rot": [(0, Z), (0.5, tilt(200, 0, 0), "out_quad"), (1.0, tilt(360, 0, 0))], "right_leg:rot": [(0, Z), (0.4, leg('r', 90)), (1.0, Z)], "left_leg:rot": [(0, Z), (0.4, leg('l', 90)), (1.0, Z)],
    "right_arm:rot": [(0, arm('r', 175)), (0.4, arm('r', 60, 20)), (1.0, Z)], "left_arm:rot": [(0, arm('l', 175)), (0.4, arm('l', 60, 20)), (1.0, Z)]}, pri=366, layer="action")
beat("player.pearl.arrival", "Ender Pearl Arrival", CAT, P, event("teleport:pearl", LIVE), 0.9, FP, {
    "mw_root:scl": [(0, [0.85, 1.15, 0.85]), (0.15, [1.08, 0.92, 1.08], "out_quad"), (0.4, [1, 1, 1])], "right_leg:rot": [(0, leg('r', 30)), (0.3, leg('r', 10)), (0.9, Z)],
    "left_leg:rot": [(0, leg('l', 40)), (0.3, leg('l', 15)), (0.9, Z)], "right_arm:rot": [(0, arm('r', 30, 40)), (0.5, arm('r', 10, 15)), (0.9, Z)], "left_arm:rot": [(0, arm('l', 30, 40)), (0.5, arm('l', 10, 15)), (0.9, Z)],
    "head:rot": [(0, [20, 0, 0]), (0.4, [0, 20, 0]), (0.9, Z)]}, pri=367, layer="action", events=[(0.0, "particle", {"particle": "magic_glint", "count": "14", "at": "body", "spread": "0.6"})])
air("player.void.fall", "Falling Into The Void", LIVE + " && q.altitude < 0 && q.dimension == 'the_end' && !q.is_on_ground", 1.2, {
    "right_arm:rot": lambda u: arm('r', 170 + 6 * wave(u), 20), "left_arm:rot": lambda u: arm('l', 160 + 6 * wave(u, 0.5), 20), "head:rot": lambda u: [-50, 0, 0], "right_leg:rot": lambda u: leg('r', 20 * wave(u, 0.3)),
    "left_leg:rot": lambda u: leg('l', 20 * wave(u, 0.8)), "mw_root:rot": lambda u: tilt(0, 30 * wave(u, 0, 0.5), 10 * wave(u))}, pri=345)
air("player.fall.end_low_gravity", "Floaty End Jump", LIVE + " && q.dimension == 'the_end' && !q.is_on_ground && q.vertical_speed > 0 && !q.is_fall_flying && !q.is_flying", 1.0, {
    "right_arm:rot": lambda u: arm('r', 40, 35), "left_arm:rot": lambda u: arm('l', 40, 35), "right_leg:rot": lambda u: leg('r', 30), "left_leg:rot": lambda u: leg('l', -10)}, pri=290)
beat("player.aerial.boost_pad_launch", "Slime Launch Tuck", CAT, P, event("jump", LIVE + " && q.surface == 'slime' && q.vertical_speed > 0.6"), 1.2, FP, {
    "right_leg:rot": [(0, Z), (0.3, leg('r', 100)), (0.9, leg('r', 90)), (1.2, Z)], "left_leg:rot": [(0, Z), (0.3, leg('l', 100)), (0.9, leg('l', 90)), (1.2, Z)],
    "right_arm:rot": [(0, Z), (0.3, arm('r', 60, -20)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.3, arm('l', 60, -20)), (1.2, Z)], "mw_root:rot": [(0, Z), (0.6, tilt(180)), (1.2, tilt(360))]}, pri=290)

# ============================================================================ flying mobs
T, F = "minecraft:parrot", FM + "/parrot"
air("parrot.climb_flap", "Parrot Climbing Flight", "!q.is_dead && q.is_flying && q.vertical_speed > 0.05", 0.25, {
    "right_wing:rot": lambda u: [0, 0, 70 * wave(u) + 30], "left_wing:rot": lambda u: [0, 0, -70 * wave(u) - 30], "body:rot": lambda u: [-20, 0, 0], "tail:rot": lambda u: [-10, 0, 0]}, pri=110, target=T, file=F)
air("parrot.glide_descent", "Parrot Gliding Descent", "!q.is_dead && q.is_flying && q.vertical_speed < -0.05", 1.0, {
    "right_wing:rot": lambda u: [0, 0, 60 + 4 * wave(u, 0, 3)], "left_wing:rot": lambda u: [0, 0, -60 - 4 * wave(u, 0, 3)], "body:rot": lambda u: [14, 0, 0], "tail:rot": lambda u: [14, 0, 0]}, pri=111, target=T, file=F)
air("parrot.hover_flutter", "Parrot Hovering Flutter", "!q.is_dead && q.is_flying && q.ground_speed < 0.02 && math.abs(q.vertical_speed) <= 0.05", 0.18, {
    "right_wing:rot": lambda u: [-30, 0, 50 * wave(u) + 40], "left_wing:rot": lambda u: [-30, 0, -50 * wave(u) - 40], "body:rot": lambda u: [-35, 0, 0], "tail:rot": lambda u: [20, 0, 0]}, pri=112, target=T, file=F)
T, F = "minecraft:bee", FM + "/bee"
air("bee.climb", "Bee Climbing", "!q.is_dead && q.is_flying && q.vertical_speed > 0.05", 0.6, {"bone:rot": lambda u: tilt(-18, 0, 3 * wave(u)), "back_legs:rot": lambda u: [60, 0, 0]}, pri=104, target=T, file=F)
air("bee.descend", "Bee Descending", "!q.is_dead && q.is_flying && q.vertical_speed < -0.05", 0.6, {"bone:rot": lambda u: tilt(24, 0, -3 * wave(u)), "front_legs:rot": lambda u: [-30, 0, 0]}, pri=104, target=T, file=F)
life("bee.dart_turn", "Bee Darting Turn", CAT, T, "!q.is_dead && q.is_flying && math.abs(q.turn_rate) > 8", 0.3, F, {"bone:rot": lambda u: [0, 0, "q.turn_rate > 0 ? -25 : 25"]}, pri=66)
T, F = "minecraft:bat", FM + "/bat"
air("bat.climb", "Bat Climbing Wingbeats", "!q.is_dead && !q.is_sleeping && q.vertical_speed > 0.08", 0.2, {
    "right_wing:rot": lambda u: [0, 60 * wave(u), 0], "left_wing:rot": lambda u: [0, -60 * wave(u), 0], "mw_root:rot": lambda u: tilt(-20, 0, 0)}, pri=108, target=T, file=F)
beat("bat.drop_from_roost", "Bat Dropping From Its Roost", CAT, T, event("wake"), 0.7, F, {
    "mw_root:rot": [(0, tilt(180, 0, 0)), (0.35, tilt(60, 0, 0)), (0.7, Z)], "right_wing:rot": [(0, [0, 90, 0]), (0.35, [0, -60, 0]), (0.7, Z)], "left_wing:rot": [(0, [0, -90, 0]), (0.35, [0, 60, 0]), (0.7, Z)]},
     pri=150)
T, F = "minecraft:ghast", FM + "/ghast"
air("ghast.rise", "Ghast Rising", "!q.is_dead && q.vertical_speed > 0.03", 2.0, {"tentacle%d:rot" % i: (lambda u, i=i: [30 + 8 * wave(u, i / 9.0), 0, 0]) for i in range(9)}, pri=104, target=T, file=F,
    layer="additive")
air("ghast.sink", "Ghast Sinking", "!q.is_dead && q.vertical_speed < -0.03", 2.0, {"tentacle%d:rot" % i: (lambda u, i=i: [-20 + 8 * wave(u, i / 9.0), 0, 6 * wave(u, i / 4.5)]) for i in range(9)}, pri=104,
    target=T, file=F, layer="additive")
T, F = "minecraft:blaze", FM + "/blaze"
air("blaze.rise", "Blaze Ascending", "!q.is_dead && q.vertical_speed > 0.05", 0.8, {"part%d:pos" % i: (lambda u, i=i: move(0, 1.5 + 0.5 * wave(u, i / 12.0), 0)) for i in range(12)}, pri=104, target=T,
    file=F, layer="additive")
air("blaze.descend", "Blaze Descending", "!q.is_dead && q.vertical_speed < -0.05", 1.0, {"part%d:pos" % i: (lambda u, i=i: move(0.4 * cwave(u, i / 12.0), -1.5, 0.4 * wave(u, i / 12.0))) for i in range(12)}, pri=104,
    target=T, file=F, layer="additive")
T, F = "minecraft:allay", FM + "/allay"
air("allay.rise", "Allay Spiralling Up", "!q.is_dead && q.vertical_speed > 0.05", 1.2, {"root:rot": lambda u: [0, 360 * u, 0], "right_arm:rot": lambda u: [20, 0, 40], "left_arm:rot": lambda u: [20, 0, -40]}, pri=112,
    target=T, file=F)
air("allay.descend", "Allay Floating Down", "!q.is_dead && q.vertical_speed < -0.05", 1.6, {"right_arm:rot": lambda u: [-30, 0, 60 + 10 * wave(u)], "left_arm:rot": lambda u: [-30, 0, -60 - 10 * wave(u)],
                                                                                         "body:rot": lambda u: [-10, 0, 0]}, pri=112, target=T, file=F)
T, F = "minecraft:vex", FM + "/vex"
air("vex.zigzag", "Vex Zigzag Flight", "!q.is_dead && q.ground_speed >= 0.1 && !q.is_charging", 0.6, {"root:rot": lambda u: [0, 0, 30 * (1 if wave(u) > 0 else -1)], "body:rot": lambda u: tilt(30, 0, 0)}, pri=106,
    target=T, file=F)
T, F = "minecraft:phantom", FM + "/phantom"
air("phantom.climb", "Phantom Climbing Beat", "!q.is_dead && q.vertical_speed > 0.15", 0.7, {
    "left_wing_base:rot": lambda u: [0, 0, 40 * wave(u)], "right_wing_base:rot": lambda u: [0, 0, -40 * wave(u)], "left_wing_tip:rot": lambda u: [0, 0, 50 * wave(u, 0.15)],
    "right_wing_tip:rot": lambda u: [0, 0, -50 * wave(u, 0.15)], "mw_root:rot": lambda u: tilt(-20, 0, 0)}, pri=102, target=T, file=F)
T, F = "minecraft:wither", FM + "/wither"
air("wither.rise", "Wither Rising", "!q.is_dead && q.vertical_speed > 0.05 && !q.invulnerable", 1.2, {"tail:rot": lambda u: [45 + 8 * wave(u), 0, 0], "shoulders:rot": lambda u: [-6, 0, 0]}, pri=106, target=T, file=F,
    layer="additive")
air("wither.swoop", "Wither Swooping Down", "!q.is_dead && q.vertical_speed < -0.05 && !q.invulnerable", 1.0, {"tail:rot": lambda u: [-20 + 8 * wave(u), 0, 0], "ribcage:rot": lambda u: [20, 0, 0]}, pri=106,
    target=T, file=F, layer="additive")
T, F = "minecraft:ender_dragon", FM + "/ender_dragon"
air("ender_dragon.takeoff_surge", "Ender Dragon Takeoff Surge", "!q.is_dead && q.phase == 'takeoff'", 1.6, {"mw_root:rot": lambda u: tilt(-18 + 4 * wave(u), 0, 0), "mw_root:pos": lambda u: move(0, 3 * wave(u, 0.25), 0)},
    pri=66, target=T, file=F, layer="additive")
air("ender_dragon.hover_hold", "Ender Dragon Hover Hold", "!q.is_dead && q.phase == 'hovering'", 2.4, {"mw_root:pos": lambda u: move(0, 2.5 * wave(u, 0, 2), 0)}, pri=65, target=T, file=F, layer="additive")
T, F = "minecraft:chicken", FM + "/chicken"
beat("chicken.flight_burst", "Chicken Flight Burst", CAT, T, event("jump", "!q.is_dead"), 0.6, F, {
    "right_wing:rot": [(0, Z), (0.1, [0, 0, 80]), (0.2, [0, 0, 10]), (0.3, [0, 0, 80]), (0.4, [0, 0, 10]), (0.6, Z)], "left_wing:rot": [(0, Z), (0.1, [0, 0, -80]), (0.2, [0, 0, -10]), (0.3, [0, 0, -80]), (0.4, [0, 0, -10]), (0.6, Z)],
    "right_leg:rot": [(0, Z), (0.2, [-40, 0, 0]), (0.6, Z)], "left_leg:rot": [(0, Z), (0.2, [-40, 0, 0]), (0.6, Z)]}, pri=150)

# ============================================================================ more flight character
air("player.elytra.nose_down", "Elytra Pitching Into A Dive", GLIDE + " && q.head_pitch > 55 && q.vertical_speed >= -0.5", 1.0, {
    "right_arm:rot": lambda u: arm('r', -60, 10), "left_arm:rot": lambda u: arm('l', -60, 10), "head:rot": lambda u: [20, 0, 0], "right_leg:rot": lambda u: leg('r', -14), "left_leg:rot": lambda u: leg('l', -14)}, pri=325)
air("player.elytra.air_brake", "Elytra Air Brake", GLIDE + " && q.head_pitch < -40 && q.ground_speed < 0.8", 0.8, {
    "right_arm:rot": lambda u: arm('r', 40, 90 + 5 * wave(u, 0, 2)), "left_arm:rot": lambda u: arm('l', 40, 90 + 5 * wave(u, 0.5, 2)), "body:rot": lambda u: tilt(-20, 0, 0),
    "right_leg:rot": lambda u: leg('r', 40), "left_leg:rot": lambda u: leg('l', 40)}, pri=326)
air("player.elytra.wounded_wobble", "Wounded Unsteady Glide", GLIDE + " && q.health < 0.3", 1.4, {
    "mw_root:rot": lambda u: tilt(3 * wave(u, 0.2), 0, 10 * wave(u)), "right_arm:rot": lambda u: arm('r', -10, 40 + 15 * wave(u)), "left_arm:rot": lambda u: arm('l', 20, 10), "head:rot": lambda u: [10, 0, 6 * wave(u, 0.3)]}, pri=327)
air("player.elytra.armoured_glide", "Rigid Armoured Glide", GLIDE + " && q.armor_weight > 0.6 && math.abs(q.vertical_speed) <= 0.5", 2.0, {
    "right_arm:rot": lambda u: arm('r', -10, 20), "left_arm:rot": lambda u: arm('l', -10, 20), "right_leg:rot": lambda u: leg('r', 0, 2), "left_leg:rot": lambda u: leg('l', 0, 2), "body:rot": lambda u: [1.5 * wave(u, 0, 2), 0, 0]}, pri=328)
air("player.elytra.stargaze", "Gliding Beneath The Stars", GLIDE + " && q.is_night && q.head_pitch < -30 && q.vertical_speed > -0.3", 4.0, {
    "mw_root:rot": lambda u: tilt(0, 0, 25 + 4 * wave(u)), "right_arm:rot": lambda u: arm('r', 0, 80), "left_arm:rot": lambda u: arm('l', 0, 80), "right_leg:rot": lambda u: leg('r', 8 * wave(u)), "left_leg:rot": lambda u: leg('l', 8 * wave(u, 0.5))},
    pri=329)
air("player.elytra.cargo", "Gliding With Something In Hand", GLIDE + " && q.main_hand != 'empty' && q.main_hand != 'firework' && math.abs(q.vertical_speed) <= 0.5", 2.0, {
    "right_arm:rot": lambda u: arm('r', 60, 10), "left_arm:rot": lambda u: arm('l', -20, 40 + 4 * wave(u)), "body:rot": lambda u: tilt(0, 0, -6)}, pri=330)
life("player.elytra.speed_buffet", "High-Speed Buffeting", CAT, P, GLIDE + " && q.ground_speed > 1.6", 0.15, FP, {"body:rot": lambda u: [0.8 * wave(u), 0, 1.2 * wave(u, 0.3)], "head:rot": lambda u: [1.5 * wave(u, 0.6), 0, 0]}, pri=93)
air("player.fly.sneak_curl", "Curling Up For A Flying Descent", FLY + " && q.is_sneaking", 1.6, {
    "right_leg:rot": lambda u: leg('r', 70), "left_leg:rot": lambda u: leg('l', 70), "right_arm:rot": lambda u: arm('r', 40, -10), "left_arm:rot": lambda u: arm('l', 40, -10), "body:rot": lambda u: tilt(20, 0, 0)}, pri=319)
air("player.fly.idle_spin", "Idly Spinning In Place", FLY + " && q.ground_speed < 0.02 && q.idle_time >= 6 && q.trait_energy > 0.7", 6.0, {
    "mw_root:rot": lambda u: [0, 360 * u, 0], "right_arm:rot": lambda u: arm('r', 0, 30), "left_arm:rot": lambda u: arm('l', 0, 30), "right_leg:rot": lambda u: leg('r', 10)}, pri=311)
life("player.fly.sprint_bank", "Banking At Flight Speed", CAT, P, FLY + " && q.is_sprinting && math.abs(q.turn_rate) > 4", 0.6, FP, {"body:rot": lambda u: [0, 0, "q.turn_rate > 0 ? -22 : 22"],
                                                                                                                    "head:rot": lambda u: [0, "q.turn_rate > 0 ? 20 : -20", 0], "right_leg:rot": lambda u: [10, 0, "q.turn_rate > 0 ? 8 : 0"]}, pri=94)
air("player.slow_fall.twirl", "Twirling Slow-Fall Descent", LIVE + " && q.slow_falling && !q.is_on_ground && q.vertical_speed < 0 && q.trait_energy > 0.6", 3.0, {
    "mw_root:rot": lambda u: [0, 360 * u, 0], "right_arm:rot": lambda u: arm('r', 0, 90), "left_arm:rot": lambda u: arm('l', 0, 90), "right_leg:rot": lambda u: leg('r', 0, 6), "left_leg:rot": lambda u: leg('l', 0, 6)}, pri=333)
T, F = "minecraft:bee", FM + "/bee"
beat("bee.touchdown", "Bee Touching Down", CAT, T, event("land", "!q.is_dead"), 0.5, F, {"front_legs:rot": [(0, [-40, 0, 0]), (0.15, [10, 0, 0]), (0.5, Z)], "back_legs:rot": [(0, [-30, 0, 0]), (0.15, [20, 0, 0]), (0.5, Z)],
                                                                                    "bone:pos": [(0, Z), (0.1, move(0, -0.5, 0)), (0.5, Z)]}, layer="gesture")
T, F = "minecraft:parrot", FM + "/parrot"
air("parrot.landing_approach", "Parrot Landing Approach", "!q.is_dead && q.is_flying && q.vertical_speed < -0.05 && q.ground_speed < 0.05", 0.5, {
    "right_wing:rot": lambda u: [-20, 0, 80 + 10 * wave(u)], "left_wing:rot": lambda u: [-20, 0, -80 - 10 * wave(u)], "left_leg:rot": lambda u: [-40, 0, 0], "right_leg:rot": lambda u: [-40, 0, 0], "tail:rot": lambda u: [30, 0, 0]},
    pri=113, target=T, file=F)
T, F = "minecraft:blaze", FM + "/blaze"
life("blaze.strafe_sway", "Blaze Strafing Sway", CAT, T, "!q.is_dead && q.is_aggressive && q.ground_speed > 0.03", 1.0, F, {"mw_root:rot": lambda u: tilt(0, 0, 8 * wave(u)), "head:rot": lambda u: [0, 0, -6 * wave(u)]}, pri=66)
T, F = "minecraft:ghast", FM + "/ghast"
life("ghast.turn_drift", "Ghast Turning Drift", CAT, T, "!q.is_dead && math.abs(q.turn_rate) > 2", 2.0, F, {"mw_root:rot": lambda u: [0, 0, "q.turn_rate > 0 ? 6 : -6"]}, pri=66)
T, F = "minecraft:allay", FM + "/allay"
air("allay.loop_de_loop", "Allay Loop-The-Loop", "!q.is_dead && q.trait_energy > 0.7 && q.ground_speed >= 0.05 && !q.is_holding", 1.4, {"root:rot": lambda u: [360 * u, 0, 0], "right_arm:rot": lambda u: [0, 0, 70],
                                                                                                                                   "left_arm:rot": lambda u: [0, 0, -70]}, pri=113, target=T, file=F)
T, F = "minecraft:bat", FM + "/bat"
life("bat.figure_eight", "Bat Figure-Eight Weave", CAT, T, "!q.is_dead && !q.is_sleeping && q.ground_speed > 0.05", 1.6, F, {"mw_root:rot": lambda u: tilt(6 * wave(u, 0, 2), 0, 18 * wave(u))}, pri=63)
T, F = "minecraft:phantom", FM + "/phantom"
air("phantom.steep_dive", "Phantom Wings-Tucked Plunge", "!q.is_dead && q.vertical_speed < -0.6", 0.4, {
    "left_wing_base:rot": lambda u: [0, 0, -50], "right_wing_base:rot": lambda u: [0, 0, 50], "left_wing_tip:rot": lambda u: [0, 0, -40], "right_wing_tip:rot": lambda u: [0, 0, 40], "head:rot": lambda u: [25, 0, 0],
    "tail_base:rot": lambda u: [-20, 0, 0]}, pri=103, target=T, file=F)
T, F = "minecraft:vex", FM + "/vex"
life("vex.swoop_turn", "Vex Swooping Turn", CAT, T, "!q.is_dead && math.abs(q.turn_rate) > 6", 0.5, F, {"root:rot": lambda u: [0, 0, "q.turn_rate > 0 ? -30 : 30"], "body:rot": lambda u: [20, 0, 0]}, pri=66)
T, F = "minecraft:wither", FM + "/wither"
life("wither.strafe_sway", "Wither Strafing Sway", CAT, T, "!q.is_dead && !q.invulnerable && q.ground_speed > 0.05", 1.4, F, {"mw_root:rot": lambda u: tilt(0, 0, 10 * wave(u)), "center_head:rot": lambda u: [0, 0, -6 * wave(u)]}, pri=67)

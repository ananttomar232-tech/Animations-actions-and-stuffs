"""Swimming and underwater behaviour (category: swimming): player strokes, diving and breath, mobs paddling."""
from core import arm, leg, biped
from mobkit import mob, gait, life, loop_state, beat, driven, Z, state, event, wave, cwave, tilt, move

CAT = "swimming"
P = "@player"
LIVE = "!q.is_dead && !q.is_riding"
WATER = LIVE + " && q.is_in_water"
SPRINT_SWIM = WATER + " && q.is_swimming && q.is_sprinting"
SURFACE = WATER + " && !q.is_underwater && !q.is_on_ground && !q.is_sprinting"
UNDER = WATER + " && q.is_underwater && !q.is_on_ground && !q.is_sprinting"
FP, FM = "player/swimming", "mobs/swimming"


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def swim(cid, name, when, L, fns, pri=300, layer="base", file=FP, target=P, group=None, weight=1):
    return loop_state(cid, name, CAT, target, when, L, file, fns, pri=pri, layer=layer, group=group, weight=weight)


# ============================================================================ player strokes
def crawl(u, reach=170, out=10, ph=0.0):
    return arm('r', reach * 0.5 + reach * 0.5 * cwave(u, ph), out + 10 * max(0, wave(u, ph)), -20 * max(0, wave(u, ph)))


swim("player.swim.front_crawl", "Front Crawl", SPRINT_SWIM + " && q.exertion <= 0.8 && q.armor_weight <= 0.5", 1.2, {
    "right_arm:rot": lambda u: crawl(u), "left_arm:rot": lambda u: [x * (1 if i == 0 else -1) for i, x in enumerate(crawl(u, ph=0.5))],
    "right_leg:rot": lambda u: leg('r', 14 * wave(u, 0, 3)), "left_leg:rot": lambda u: leg('l', -14 * wave(u, 0, 3)), "body:rot": lambda u: tilt(0, 8 * wave(u), 0), "head:rot": lambda u: [0, 20 * spike(u, 0.75, 4), 0]})
swim("player.swim.front_crawl_tired", "Laboured Front Crawl", SPRINT_SWIM + " && q.exertion > 0.8", 1.6, {
    "right_arm:rot": lambda u: crawl(u, 150, 20), "left_arm:rot": lambda u: [x * (1 if i == 0 else -1) for i, x in enumerate(crawl(u, 150, 20, 0.55))],
    "right_leg:rot": lambda u: leg('r', 8 * wave(u, 0, 2)), "left_leg:rot": lambda u: leg('l', -8 * wave(u, 0, 2)), "body:rot": lambda u: tilt(0, 4 * wave(u), 3 * wave(u, 0.25)),
    "head:rot": lambda u: [-14 * spike(u, 0.2, 2), 0, 0]}, pri=301)
swim("player.swim.armoured_slog", "Armoured Swimming Slog", SPRINT_SWIM + " && q.armor_weight > 0.5", 1.8, {
    "right_arm:rot": lambda u: arm('r', 90 + 60 * cwave(u), 30), "left_arm:rot": lambda u: arm('l', 90 + 60 * cwave(u, 0.5), 30), "right_leg:rot": lambda u: leg('r', 25 * wave(u, 0, 2)),
    "left_leg:rot": lambda u: leg('l', -25 * wave(u, 0, 2)), "mw_root:pos": lambda u: move(0, -1 + 0.8 * wave(u, 0, 2), 0)}, pri=302)
swim("player.swim.breaststroke_under", "Underwater Breaststroke", UNDER + " && q.ground_speed >= 0.02", 1.6, {
    "right_arm:rot": lambda u: arm('r', 160 - 60 * max(0, wave(u)), 40 * max(0, wave(u)) + 5), "left_arm:rot": lambda u: arm('l', 160 - 60 * max(0, wave(u)), 40 * max(0, wave(u)) + 5),
    "right_leg:rot": lambda u: leg('r', 30 * max(0, wave(u, 0.5)), 25 * max(0, cwave(u, 0.5))), "left_leg:rot": lambda u: leg('l', 30 * max(0, wave(u, 0.5)), 25 * max(0, cwave(u, 0.5))),
    "body:rot": lambda u: tilt(50 + 6 * wave(u), 0, 0), "head:rot": lambda u: [-40, 0, 0]}, pri=303)
swim("player.swim.breaststroke_surface", "Surface Breaststroke", SURFACE + " && q.ground_speed >= 0.02", 1.4, {
    "right_arm:rot": lambda u: arm('r', 80 + 20 * cwave(u), 10 + 50 * max(0, wave(u))), "left_arm:rot": lambda u: arm('l', 80 + 20 * cwave(u), 10 + 50 * max(0, wave(u))),
    "right_leg:rot": lambda u: leg('r', -10 + 30 * max(0, wave(u, 0.4))), "left_leg:rot": lambda u: leg('l', -10 + 30 * max(0, wave(u, 0.4))), "body:rot": lambda u: tilt(30, 0, 0),
    "mw_root:pos": lambda u: move(0, 0.8 * wave(u, 0.2), 0)}, pri=304)
swim("player.swim.tread_calm", "Calm Treading Water", SURFACE + " && q.ground_speed < 0.02 && q.health >= 0.35 && q.armor_weight <= 0.5", 1.6, {
    "right_arm:rot": lambda u: arm('r', 20, 45 + 15 * wave(u), 20 * wave(u)), "left_arm:rot": lambda u: arm('l', 20, 45 + 15 * wave(u, 0.5), 20 * wave(u, 0.5)),
    "right_leg:rot": lambda u: leg('r', 25 * wave(u)), "left_leg:rot": lambda u: leg('l', 25 * wave(u, 0.5)), "mw_root:pos": lambda u: move(0, 0.5 * wave(u, 0, 2), 0)}, pri=305)
swim("player.swim.tread_struggle", "Struggling To Stay Afloat", SURFACE + " && q.ground_speed < 0.02 && (q.health < 0.35 || q.armor_weight > 0.5)", 0.8, {
    "right_arm:rot": lambda u: arm('r', 60 + 50 * wave(u), 40), "left_arm:rot": lambda u: arm('l', 60 + 50 * wave(u, 0.4), 40), "head:rot": lambda u: [-25, 15 * wave(u, 0, 0.5), 0],
    "mw_root:pos": lambda u: move(0, -1 + 1.5 * wave(u, 0, 2), 0), "right_leg:rot": lambda u: leg('r', 35 * wave(u, 0, 2)), "left_leg:rot": lambda u: leg('l', 35 * wave(u, 0.5, 2))}, pri=306)
swim("player.swim.hover", "Underwater Hover", UNDER + " && q.ground_speed < 0.02 && q.air >= 0.3", 3.0, {
    "right_arm:rot": lambda u: arm('r', 30 + 15 * wave(u), 35 + 10 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 30 + 15 * wave(u, 0.5), 35 + 10 * wave(u, 0.8)),
    "right_leg:rot": lambda u: leg('r', 15 * wave(u, 0.2)), "left_leg:rot": lambda u: leg('l', 15 * wave(u, 0.7)), "body:rot": lambda u: tilt(6 * wave(u, 0.1), 0, 0)}, pri=307, group="under_idle", weight=3)
swim("player.swim.look_around_reef", "Gazing Around Underwater", UNDER + " && q.ground_speed < 0.02 && q.air >= 0.3 && q.light >= 6", 5.0, {
    "head:rot": lambda u: [-10 + 15 * wave(u, 0.3), 50 * wave(u), 0], "body:rot": lambda u: tilt(0, 15 * wave(u, 0.05), 0), "right_arm:rot": lambda u: arm('r', 20, 40), "left_arm:rot": lambda u: arm('l', 20, 40)},
     pri=307, group="under_idle", weight=2)
swim("player.swim.drowning", "Drowning Struggle", WATER + " && q.is_underwater && q.air < 0.15", 0.5, {
    "right_arm:rot": lambda u: arm('r', 150 + 25 * wave(u), 20 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 140 + 25 * wave(u, 0.5), 20 * wave(u, 0.8)), "head:rot": lambda u: [-45, 20 * wave(u, 0, 0.5), 0],
    "right_leg:rot": lambda u: leg('r', 40 * wave(u)), "left_leg:rot": lambda u: leg('l', 40 * wave(u, 0.5)), "mw_root:pos": lambda u: move(0.4 * wave(u, 0.25), 0.6 * wave(u), 0)}, pri=330)
swim("player.swim.air_running_out", "Holding Breath Anxiously", UNDER + " && q.air >= 0.15 && q.air < 0.3", 1.0, {
    "head:rot": lambda u: [-30, 10 * wave(u), 0], "right_arm:rot": lambda u: arm('r', 120 + 20 * wave(u), 30), "left_arm:rot": lambda u: arm('l', 120 + 20 * wave(u, 0.5), 30), "body:rot": lambda u: tilt(-10, 0, 0)}, pri=320)
beat("player.swim.dive_tuck", "Duck Dive", CAT, P, event("submerge", LIVE + " && q.vertical_speed < -0.05"), 0.8, FP, {
    "body:rot": [(0, Z), (0.25, tilt(70)), (0.8, tilt(50))], "right_arm:rot": [(0, Z), (0.25, arm('r', 170, 5)), (0.8, arm('r', 160, 10))], "left_arm:rot": [(0, Z), (0.25, arm('l', 170, 5)), (0.8, arm('l', 160, 10))],
    "right_leg:rot": [(0, Z), (0.35, leg('r', -30)), (0.8, Z)], "left_leg:rot": [(0, Z), (0.35, leg('l', -30)), (0.8, Z)]}, pri=340, events=[(0.1, "particle", {"particle": "splash", "count": "10", "at": "body", "spread": "0.5"})])
beat("player.swim.surface_burst", "Bursting To The Surface", CAT, P, event("surface", LIVE + " && q.vertical_speed > 0.05"), 0.9, FP, {
    "head:rot": [(0, Z), (0.15, [-35, 0, 0], "out_expo"), (0.9, Z)], "right_arm:rot": [(0, arm('r', 170)), (0.2, arm('r', 60, 60), "out_quad"), (0.9, arm('r', 20, 45))],
    "left_arm:rot": [(0, arm('l', 170)), (0.2, arm('l', 60, 60), "out_quad"), (0.9, arm('l', 20, 45))], "body:rot": [(0, Z), (0.15, tilt(-14)), (0.9, Z)]}, pri=341,
     events=[(0.05, "particle", {"particle": "splash", "count": "14", "at": "head", "spread": "0.6"}), (0.2, "breath", {"strength": "1"})])
beat("player.swim.gasp", "Gasping For Air", CAT, P, event("surface", LIVE + " && q.air < 0.35"), 1.6, FP, {
    "head:rot": [(0, Z), (0.2, [-40, 0, 0]), (0.5, [-25, 0, 0]), (0.8, [-38, 0, 0]), (1.1, [-22, 0, 0]), (1.6, Z)], "body:rot": [(0, Z), (0.2, tilt(-10)), (0.5, tilt(-4)), (0.8, tilt(-10)), (1.6, Z)]},
     pri=342, layer="gesture", events=[(0.2, "breath", {"strength": "1"}), (0.8, "breath", {"strength": "0.8"})])
beat("player.swim.head_first_dive", "Head-First Dive Entry", CAT, P, event("enter_water", LIVE + " && q.vertical_speed < -0.5 && !q.is_sneaking"), 0.9, FP, {
    "body:rot": [(0, tilt(80)), (0.4, tilt(60)), (0.9, tilt(30))], "right_arm:rot": [(0, arm('r', 175)), (0.5, arm('r', 160, 20)), (0.9, arm('r', 60, 40))],
    "left_arm:rot": [(0, arm('l', 175)), (0.5, arm('l', 160, 20)), (0.9, arm('l', 60, 40))], "right_leg:rot": [(0, Z), (0.9, leg('r', 10))], "left_leg:rot": [(0, Z), (0.9, leg('l', 10))]},
     pri=343, events=[(0.0, "particle", {"particle": "splash", "count": "18", "at": "head", "spread": "0.4"})])
beat("player.swim.cannonball", "Cannonball", CAT, P, event("enter_water", LIVE + " && q.vertical_speed < -0.5 && q.is_sneaking"), 1.0, FP, {
    "right_leg:rot": [(0, leg('r', 100)), (0.5, leg('r', 90)), (1.0, Z)], "left_leg:rot": [(0, leg('l', 100)), (0.5, leg('l', 90)), (1.0, Z)], "right_arm:rot": [(0, arm('r', 60, -20)), (0.5, arm('r', 50, -10)), (1.0, Z)],
    "left_arm:rot": [(0, arm('l', 60, -20)), (0.5, arm('l', 50, -10)), (1.0, Z)], "body:rot": [(0, tilt(30)), (1.0, Z)]}, pri=344,
     events=[(0.0, "particle", {"particle": "splash", "count": "30", "at": "body", "spread": "0.9"}), (0.0, "shake", {"intensity": "0.2", "duration": "0.2"})])
life("player.swim.turn_bank", "Banking Swim Turn", CAT, P, SPRINT_SWIM + " && math.abs(q.turn_rate) > 4", 0.6, FP, {"body:rot": lambda u: [0, 0, "q.turn_rate > 0 ? -14 : 14"],
                                                                                                         "right_leg:rot": lambda u: [12 * wave(u, 0, 2), 0, 0], "left_leg:rot": lambda u: [-12 * wave(u, 0, 2), 0, 0]}, pri=90)
swim("player.swim.kick_up", "Kicking Upward", UNDER + " && q.vertical_speed > 0.05", 0.7, {
    "right_leg:rot": lambda u: leg('r', 40 * wave(u)), "left_leg:rot": lambda u: leg('l', 40 * wave(u, 0.5)), "right_arm:rot": lambda u: arm('r', 20 - 20 * wave(u, 0.25), 30), "left_arm:rot": lambda u: arm('l', 20 - 20 * wave(u, 0.25), 30),
    "head:rot": lambda u: [-35, 0, 0], "body:rot": lambda u: tilt(-10, 0, 0)}, pri=308)
swim("player.swim.sink_down", "Sinking Deliberately", UNDER + " && q.vertical_speed < -0.05 && q.is_sneaking", 2.0, {
    "right_arm:rot": lambda u: arm('r', -20, 50 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', -20, 50 + 10 * wave(u, 0.5)), "head:rot": lambda u: [30, 0, 0], "right_leg:rot": lambda u: leg('r', 10), "left_leg:rot": lambda u: leg('l', -6)},
     pri=309)
swim("player.swim.trident_stroke", "One-Arm Stroke Holding A Trident", SPRINT_SWIM + " && q.main_hand == 'trident'", 1.3, {
    "right_arm:rot": lambda u: arm('r', 20, 10, 0), "left_arm:rot": lambda u: [x * (1 if i == 0 else -1) for i, x in enumerate(crawl(u, 170, 10))], "body:rot": lambda u: tilt(0, 12 * wave(u), 8),
    "right_leg:rot": lambda u: leg('r', 18 * wave(u, 0, 3)), "left_leg:rot": lambda u: leg('l', -18 * wave(u, 0, 3))}, pri=310)
swim("player.swim.sidestroke_carry", "Sidestroke Carrying An Item", SPRINT_SWIM + " && q.main_hand != 'empty' && q.main_hand != 'trident'", 1.5, {
    "right_arm:rot": lambda u: arm('r', 30, 15), "left_arm:rot": lambda u: arm('l', 100 + 70 * cwave(u), 20), "body:rot": lambda u: tilt(0, 0, -30), "right_leg:rot": lambda u: leg('r', 35 * wave(u), 10 * max(0, wave(u))),
    "left_leg:rot": lambda u: leg('l', -35 * wave(u), 10 * max(0, -wave(u)))}, pri=309)
swim("player.swim.backstroke", "Lazy Backstroke", SURFACE + " && q.ground_speed >= 0.02 && q.head_pitch < -40", 1.8, {
    "right_arm:rot": lambda u: arm('r', 180 * max(0, wave(u)), 10), "left_arm:rot": lambda u: arm('l', 180 * max(0, wave(u, 0.5)), 10), "body:rot": lambda u: tilt(-60, 0, 6 * wave(u)),
    "right_leg:rot": lambda u: leg('r', 15 * wave(u, 0, 3)), "left_leg:rot": lambda u: leg('l', -15 * wave(u, 0, 3))}, pri=311)
swim("player.swim.bubble_lift", "Riding A Rising Bubble Column", WATER + " && q.feet_block == 'bubble_column' && q.vertical_speed > 0.1", 0.4, {
    "right_arm:rot": lambda u: arm('r', 170, 10 + 5 * wave(u)), "left_arm:rot": lambda u: arm('l', 170, 10 + 5 * wave(u, 0.5)), "right_leg:rot": lambda u: leg('r', 4 * wave(u)), "left_leg:rot": lambda u: leg('l', -4 * wave(u)),
    "body:rot": lambda u: tilt(0, 0, 2 * wave(u, 0.25))}, pri=315)
swim("player.swim.bubble_drag", "Dragged Down A Whirlpool Column", WATER + " && q.feet_block == 'bubble_column' && q.vertical_speed < -0.1", 1.4, {
    "right_arm:rot": lambda u: arm('r', 160 + 15 * wave(u, 0, 4), 30), "left_arm:rot": lambda u: arm('l', 150 + 15 * wave(u, 0.5, 4), 30), "mw_root:rot": lambda u: [0, 360 * u, 0], "head:rot": lambda u: [-35, 0, 0]},
     pri=316)
c = mob("player.swim.seabed_walk", "Slow Seabed Walk", CAT, P, 1.8, state(WATER + " && q.is_underwater && q.is_on_ground && q.ground_speed >= 0.01", exit_delay=0.2), layer="base", pri=300, file=FP, **driven(1.8, 1.0, 2.2, 9.4248))
biped(c, stride=18, arm_swing=6, arm_out=28, bob=0.3, twist=4, sway=1.5, lean=8, knee_lift=14, head_hold=(-8, 0, 0))
swim("player.swim.seabed_stand", "Standing On The Seabed", WATER + " && q.is_underwater && q.is_on_ground && q.ground_speed < 0.01", 3.0, {
    "right_arm:rot": lambda u: arm('r', 10, 30 + 12 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 30 + 12 * wave(u, 0.5)), "mw_root:pos": lambda u: move(0, 0.3 * wave(u), 0), "head:rot": lambda u: [-10 * wave(u, 0.2), 0, 0]}, pri=300)
c = mob("player.swim.chest_deep_wade", "Chest-Deep Wade", CAT, P, 1.6, state(LIVE + " && q.is_on_ground && q.fluid_depth > 1.0 && !q.is_underwater && q.ground_speed >= 0.02", exit_delay=0.2), layer="base", pri=299,
        file=FP, **driven(1.6, 1.0, 2.2, 9.4248))
biped(c, stride=18, arm_swing=0, bob=0.6, twist=10, sway=2, lean=4, right_arm=(30, 40, 0), left_arm=(30, 40, 0), knee_lift=20)
swim("player.swim.lava_thrash", "Thrashing In Lava", LIVE + " && q.is_in_lava && !q.is_on_ground", 0.35, {
    "right_arm:rot": lambda u: arm('r', 140 + 35 * wave(u), 30 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 140 + 35 * wave(u, 0.5), 30 * wave(u, 0.8)), "head:rot": lambda u: [-30, 30 * wave(u, 0, 0.5), 0],
    "right_leg:rot": lambda u: leg('r', 45 * wave(u)), "left_leg:rot": lambda u: leg('l', 45 * wave(u, 0.5))}, pri=335)
swim("player.swim.lava_wade", "Desperate Lava Wade", LIVE + " && q.is_in_lava && q.is_on_ground", 0.6, {
    "right_arm:rot": lambda u: arm('r', 100 + 30 * wave(u), 40), "left_arm:rot": lambda u: arm('l', 100 + 30 * wave(u, 0.5), 40), "right_leg:rot": lambda u: leg('r', 50 * max(0, wave(u))),
    "left_leg:rot": lambda u: leg('l', 50 * max(0, wave(u, 0.5))), "body:rot": lambda u: tilt(-10, 0, 6 * wave(u))}, pri=334)
beat("player.swim.climb_out", "Hauling Out Of The Water", CAT, P, event("exit_water", LIVE + " && q.vertical_speed > 0.1"), 1.0, FP, {
    "right_arm:rot": [(0, arm('r', 150)), (0.4, arm('r', 60)), (1.0, Z)], "left_arm:rot": [(0, arm('l', 150)), (0.4, arm('l', 60)), (1.0, Z)], "body:rot": [(0, tilt(40)), (0.5, tilt(20)), (1.0, Z)],
    "right_leg:rot": [(0, Z), (0.5, leg('r', 70)), (1.0, Z)]}, pri=345)
beat("player.swim.shake_off", "Shaking Off Water", CAT, P, event("exit_water", LIVE + " && q.vertical_speed <= 0.1"), 1.2, FP, {
    "head:rot": [(0, Z), (0.1, [0, 0, 20]), (0.2, [0, 0, -20]), (0.3, [0, 0, 16]), (0.4, [0, 0, -12]), (0.6, Z)], "right_arm:rot": [(0, Z), (0.2, arm('r', 20, 30)), (0.4, arm('r', 20, 10)), (0.6, arm('r', 20, 30)), (1.2, Z)],
    "left_arm:rot": [(0, Z), (0.2, arm('l', 20, 30)), (0.4, arm('l', 20, 10)), (0.6, arm('l', 20, 30)), (1.2, Z)], "body:rot": [(0, Z), (0.15, tilt(0, 0, 6)), (0.3, tilt(0, 0, -6)), (0.6, Z)]}, pri=200, layer="gesture",
     events=[(0.1, "particle", {"particle": "splash", "count": "12", "at": "body", "spread": "0.5"})])
swim("player.swim.float_back", "Floating On Your Back", SURFACE + " && q.ground_speed < 0.02 && q.idle_time > 10 && q.health >= 0.35", 4.0, {
    "body:rot": lambda u: tilt(-80, 0, 2 * wave(u)), "right_arm:rot": lambda u: arm('r', 10, 70), "left_arm:rot": lambda u: arm('l', 10, 70), "right_leg:rot": lambda u: leg('r', 0, 10), "left_leg:rot": lambda u: leg('l', 0, 10),
    "mw_root:pos": lambda u: move(0, 0.4 * wave(u), 0), "head:rot": lambda u: [-10, 0, 0]}, pri=312)
beat("player.swim.underwater_swing", "Water-Resisted Swing", CAT, P, event("attack", LIVE + " && q.is_underwater"), 0.9, FP, {
    "right_arm:rot": [(0, Z), (0.35, arm('r', 140, 20), "out_quad"), (0.6, arm('r', 40, -10), "in_quad"), (0.9, Z)], "body:rot": [(0, Z), (0.35, tilt(-6, 15, 0)), (0.6, tilt(6, -15, 0)), (0.9, Z)]}, pri=350)
swim("player.swim.underwater_mining", "Slow Underwater Mining", WATER + " && q.is_underwater && q.is_mining", 1.0, {
    "right_arm:rot": lambda u: arm('r', 80 + 40 * cwave(u), 10), "body:rot": lambda u: tilt(10 + 6 * cwave(u), 0, 0), "left_arm:rot": lambda u: arm('l', 20, 40)}, pri=351, layer="action")
swim("player.swim.seagrass_brush", "Brushing Through Seagrass", WATER + " && q.feet_block == 'foliage' && q.ground_speed >= 0.02", 1.0, {
    "right_arm:rot": lambda u: arm('r', 40, 30 + 20 * wave(u)), "left_arm:rot": lambda u: arm('l', 40, 30 + 20 * wave(u, 0.5))}, pri=95, layer="additive")
beat("player.swim.push_off", "Pushing Off Into A Sprint Swim", CAT, P, event("sprint_start", LIVE + " && q.is_in_water"), 0.6, FP, {
    "right_leg:rot": [(0, leg('r', 40)), (0.15, leg('r', -20), "out_expo"), (0.6, Z)], "left_leg:rot": [(0, leg('l', 40)), (0.15, leg('l', -20), "out_expo"), (0.6, Z)],
    "right_arm:rot": [(0, Z), (0.15, arm('r', 175)), (0.6, arm('r', 170))], "left_arm:rot": [(0, Z), (0.15, arm('l', 175)), (0.6, arm('l', 170))]}, pri=346)
beat("player.swim.glide_stop", "Gliding To A Stop", CAT, P, event("sprint_stop", LIVE + " && q.is_in_water"), 1.0, FP, {
    "right_arm:rot": [(0, arm('r', 170)), (0.5, arm('r', 80, 50)), (1.0, arm('r', 20, 45))], "left_arm:rot": [(0, arm('l', 170)), (0.5, arm('l', 80, 50)), (1.0, arm('l', 20, 45))],
    "body:rot": [(0, tilt(40)), (1.0, Z)]}, pri=347)
swim("player.swim.dark_water_caution", "Cautious Swim In Dark Water", UNDER + " && q.light < 5 && q.ground_speed >= 0.02", 2.0, {
    "head:rot": lambda u: [-20, 40 * wave(u), 0], "right_arm:rot": lambda u: arm('r', 100 + 30 * cwave(u), 30), "left_arm:rot": lambda u: arm('l', 100 + 30 * cwave(u), 30),
    "right_leg:rot": lambda u: leg('r', 20 * wave(u)), "left_leg:rot": lambda u: leg('l', 20 * wave(u, 0.5))}, pri=313)
swim("player.swim.sneak_sink_surface", "Letting Yourself Sink", SURFACE + " && q.is_sneaking", 1.4, {
    "right_arm:rot": lambda u: arm('r', 160, 20), "left_arm:rot": lambda u: arm('l', 160, 20), "head:rot": lambda u: [-20, 0, 0], "mw_root:pos": lambda u: move(0, -0.6 * u, 0)}, pri=314)
life("player.swim.cheeks_puffed", "Cheeks Puffed Holding Breath", CAT, P, WATER + " && q.is_underwater && q.air < 0.7 && q.air >= 0.3", 1.2, FP, {"head:scl": lambda u: [1.02 + 0.01 * wave(u), 1, 1.02]})
swim("player.swim.surface_rest_ledge", "Resting Arms On A Ledge", SURFACE + " && q.ground_speed < 0.02 && q.exertion > 0.6", 2.4, {
    "right_arm:rot": lambda u: arm('r', 80, 10), "left_arm:rot": lambda u: arm('l', 80, 10), "body:rot": lambda u: tilt(10, 0, 0), "head:rot": lambda u: [10, 0, 6 * wave(u, 0.3)],
    "mw_root:pos": lambda u: move(0, 0.3 * wave(u), 0)}, pri=318)
beat("player.swim.splash_play", "Splashing Water Playfully", CAT, P, event("swing", LIVE + " && q.is_in_water && !q.is_underwater && q.main_hand == 'empty'"), 0.6, FP, {
    "right_arm:rot": [(0, arm('r', 20, 30)), (0.2, arm('r', 60, 60), "out_expo"), (0.6, arm('r', 20, 30))], "left_arm:rot": [(0, arm('l', 20, 30)), (0.25, arm('l', 60, 60), "out_expo"), (0.6, arm('l', 20, 30))]},
     pri=352, events=[(0.2, "particle", {"particle": "splash", "count": "8", "at": "front", "spread": "0.4"})])

# ============================================================================ mobs in water
QW = "!q.is_dead && q.is_in_water && !q.is_on_ground"
for T, sp, label, params in (
        ("minecraft:cow", "cow", "Cow", dict(gait="pace", stride=26, duty=0.5, bob=1.2, pitch=2, roll=2, lift=10)),
        ("minecraft:mooshroom", "mooshroom", "Mooshroom", dict(gait="pace", stride=24, duty=0.5, bob=1.4, pitch=3, roll=1, splay=8)),
        ("minecraft:pig", "pig", "Pig", dict(gait="trot", stride=34, duty=0.5, bob=0.8, pitch=5, roll=3, snap=0.3)),
        ("minecraft:sheep", "sheep", "Sheep", dict(gait="trot", stride=28, duty=0.45, bob=1.8, pitch=1, roll=4, yaw=3)),
        ("minecraft:polar_bear", "polar_bear", "Polar Bear", dict(gait="walk", stride=44, duty=0.5, bob=0.6, pitch=1, roll=2, front_scale=1.4, yaw=4)),
        ("minecraft:panda", "panda", "Panda", dict(gait="waddle", stride=22, duty=0.5, bob=1.6, pitch=1, roll=8)),
        ("minecraft:goat", "goat", "Goat", dict(gait="bound", stride=30, duty=0.4, bob=2.4, pitch=4, roll=1)),
        ("minecraft:llama", "llama", "Llama", dict(gait="pace", stride=20, duty=0.6, bob=0.6, pitch=4, roll=5, lift=14)),
        ("minecraft:wolf", "wolf", "Wolf", dict(gait="trot", stride=40, duty=0.5, bob=0.5, pitch=2, roll=1, lift=20, front_scale=1.2)),
        ("minecraft:fox", "fox", "Fox", dict(gait="trot", stride=36, duty=0.45, bob=0.4, pitch=1, roll=2, snap=0.2, lift=12)),
        ("minecraft:cat", "cat", "Cat", dict(gait="walk", stride=40, duty=0.4, bob=1.4, pitch=6, roll=4, snap=0.35)),
        ("minecraft:ocelot", "ocelot", "Ocelot", dict(gait="pace", stride=36, duty=0.42, bob=0.8, pitch=3, roll=3, splay=10)),
        ("minecraft:creeper", "creeper", "Creeper", dict(gait="walk", stride=30, duty=0.55, bob=0.3, pitch=0.5, roll=6, yaw=2)),
        ("minecraft:hoglin", "hoglin", "Hoglin", dict(gait="gallop", stride=30, duty=0.5, bob=1.0, pitch=3, roll=2, lift=16)),
        ("minecraft:ravager", "ravager", "Ravager", dict(gait="walk", stride=22, duty=0.6, bob=0.8, pitch=1, roll=5, front_scale=0.7))):
    keep = sp in ("cow", "mooshroom", "pig", "sheep", "goat", "llama")
    c = gait(sp + ".swim_paddle", label + " Paddling", CAT, T, QW, 0.8, FM, pri=120, synced=False, keep_head=keep, head_base=-25 if keep else 0, head_bob=2, **params)
    if not keep:
        c.cycle("mw_center", "rotation", lambda u: tilt(-12, 0, 3 * wave(u)))
# each equine keeps its own footfall rhythm in deep water: diagonal pairs (horse), lateral pairs (donkey), four-beat (mule)
EQ_SWIM = {"horse": ("Horse Swimming Head-High", 1.1, {"left_front_leg": 0.0, "right_hind_leg": 0.0, "right_front_leg": 0.5, "left_hind_leg": 0.5}, 1.0),
           "donkey": ("Donkey Bobbing Swim", 1.3, {"left_front_leg": 0.0, "left_hind_leg": 0.0, "right_front_leg": 0.5, "right_hind_leg": 0.5}, 0.85),
           "mule": ("Mule Steady Swim", 1.2, {"left_hind_leg": 0.0, "left_front_leg": 0.25, "right_hind_leg": 0.5, "right_front_leg": 0.75}, 0.92),
           "camel": ("Camel Swimming Head-High", 1.8, {"left_front_leg": 0.0, "right_front_leg": 0.5, "left_hind_leg": 0.35, "right_hind_leg": 0.85}, 0.6)}
for sp, (label, L, phases, a) in EQ_SWIM.items():
    T = "minecraft:" + sp
    c = mob(sp + ".swim", label, CAT, T, L, state(QW), layer="base", pri=120, file=FM)
    for b, ph in phases.items():
        c.cycle(b, "rotation", lambda u, ph=ph, b=b, a=a: [(-50 if "front" in b else 30) * max(0, wave(u, ph)) * a - (10 if "front" in b else -10), 0, 0])
    head = "head_parts" if sp != "camel" else "head"
    if sp == "donkey":
        c.cycle(head, "rotation", lambda u: [-20 + 8 * wave(u, 0.1), 0, 0])
        c.cycle("mw_center", "position", lambda u: move(0, 1.2 * wave(u), 0))
    elif sp == "mule":
        c.cycle(head, "rotation", lambda u: [-26, 6 * wave(u), 0])
        c.cycle("left_ear", "rotation", lambda u: [0, 0, -15 * wave(u, 0, 2)])
        c.cycle("right_ear", "rotation", lambda u: [0, 0, 15 * wave(u, 0.2, 2)])
    else:
        c.cycle(head, "rotation", lambda u, a=a: [-30 * a, 0, 3 * wave(u, 0, 2)])
        c.cycle("mw_center", "position", lambda u: move(0, 0.6 * wave(u, 0, 2), 0))
    c.cycle("tail", "rotation", lambda u, a=a: [-20 * a, 10 * wave(u), 0])
T = "minecraft:chicken"
loop_state("chicken.float_bob", "Chicken Bobbing Afloat", CAT, T, "!q.is_dead && q.is_in_water", 1.0, FM, {
    "mw_center:pos": lambda u: move(0, 0.6 * wave(u), 0), "right_leg:rot": lambda u: [-30 * max(0, wave(u)), 0, 0], "left_leg:rot": lambda u: [-30 * max(0, wave(u, 0.5)), 0, 0],
    "right_wing:rot": lambda u: [0, 0, 20 * spike(u, 0.2, 4)], "left_wing:rot": lambda u: [0, 0, -20 * spike(u, 0.2, 4)]}, pri=120, layer="base")
T = "minecraft:rabbit"
loop_state("rabbit.frantic_paddle", "Rabbit Frantic Paddle", CAT, T, QW, 0.3, FM, {
    "left_front_leg:rot": lambda u: [-40 * wave(u), 0, 0], "right_front_leg:rot": lambda u: [-40 * wave(u, 0.5), 0, 0], "left_haunch:rot": lambda u: [30 * wave(u, 0.5), 0, 0],
    "right_haunch:rot": lambda u: [30 * wave(u), 0, 0], "head:rot": lambda u: [-20, 0, 0], "right_ear:rot": lambda u: [30, 0, 0], "left_ear:rot": lambda u: [30, 0, 0]}, pri=120, layer="base")
for T, sp, label, F_ in (("minecraft:villager", "villager", "Villager", 1.0), ("minecraft:wandering_trader", "wandering_trader", "Wandering Trader", 0.8)):
    loop_state(sp + ".swim_bob", label + " Bobbing Swim", CAT, T, QW, 1.0 / F_, FM, {
        "right_leg:rot": lambda u, k=F_: leg('r', 30 * k * wave(u)), "left_leg:rot": lambda u, k=F_: leg('l', 30 * k * wave(u, 0.5)), "arms:rot": lambda u, k=F_: [-40 + 20 * k * wave(u, 0.25), 0, 0],
        "head:rot": lambda u: [-20, 0, 0], "mw_root:pos": lambda u, k=F_: move(0, 0.6 * wave(u, 0, 2) * k, 0)}, pri=120, layer="base")
loop_state("witch.swim_bob", "Witch Paddling With Her Hat Askew", CAT, "minecraft:witch", QW, 1.4, FM, {
    "right_leg:rot": lambda u: leg('r', 18 * wave(u)), "left_leg:rot": lambda u: leg('l', 18 * wave(u, 0.5)), "arms:rot": lambda u: [-50, 0, 0], "arms:pos": lambda u: move(0.8 * cwave(u), 0, 0.8 * wave(u)),
    "hat2:rot": lambda u: [0, 0, 6 * wave(u, 0.2)], "hat3:rot": lambda u: [0, 0, 10 * wave(u, 0.35)], "hat4:rot": lambda u: [0, 0, 16 * wave(u, 0.5)], "head:rot": lambda u: [-15, 0, 8]}, pri=120, layer="base")
for T, sp, label, sink in (("minecraft:zombie", "zombie", "Zombie", True), ("minecraft:husk", "husk", "Husk", True), ("minecraft:skeleton", "skeleton", "Skeleton", True),
                           ("minecraft:piglin", "piglin", "Piglin", False), ("minecraft:pillager", "pillager", "Pillager", False), ("minecraft:enderman", "enderman", "Enderman", False)):
    if sp == "enderman":
        loop_state(sp + ".water_agony", label + " Water Agony", CAT, T, "!q.is_dead && q.is_in_water", 0.3, FM, {
            "right_arm:rot": lambda u: arm('r', 160 + 20 * wave(u), 30), "left_arm:rot": lambda u: arm('l', 160 + 20 * wave(u, 0.5), 30), "head:rot": lambda u: [-30, 20 * wave(u, 0, 0.5), 0],
            "body:rot": lambda u: tilt(0, 10 * wave(u), 6 * wave(u, 0.25))}, pri=160, layer="action")
    elif sink:
        if sp == "husk":
            loop_state(sp + ".sinking_drift", label + " Clawing At The Surface", CAT, T, QW, 0.8, FM, {
                "right_arm:rot": lambda u: arm('r', 175, 10 + 20 * max(0, wave(u))), "left_arm:rot": lambda u: arm('l', 175, 10 + 20 * max(0, wave(u, 0.5))), "body:rot": lambda u: tilt(-10, 0, 6 * wave(u)),
                "right_leg:rot": lambda u: leg('r', 35 * wave(u, 0, 2)), "left_leg:rot": lambda u: leg('l', -35 * wave(u, 0, 2)), "head:rot": lambda u: [-40, 0, 0]}, pri=120, layer="base")
        else:
            loop_state(sp + ".sinking_drift", label + (" Sinking Bone Drift" if sp == "skeleton" else " Sinking Drift"), CAT, T, QW, 2.4, FM, {
                "right_arm:rot": lambda u: arm('r', 140 + 20 * wave(u), 20), "left_arm:rot": lambda u: arm('l', 130 + 20 * wave(u, 0.5), 20),
                "right_leg:rot": lambda u: leg('r', 10 * wave(u)), "left_leg:rot": lambda u: leg('l', 10 * wave(u, 0.5)), "head:rot": lambda u, s_=sp: [-20 if s_ != "skeleton" else 10, 10 * wave(u, 0.2), 0]},
                pri=120, layer="base")
    else:
        loop_state(sp + ".dog_paddle", label + " Dog Paddle", CAT, T, QW, 0.6 if sp == "piglin" else 0.8, FM, {
            "right_arm:rot": lambda u, s_=sp: arm('r', 70 + 30 * wave(u), 20 if s_ == "piglin" else 35), "left_arm:rot": lambda u, s_=sp: arm('l', 70 + 30 * wave(u, 0.5), 20 if s_ == "piglin" else 35),
            "right_leg:rot": lambda u: leg('r', 30 * wave(u, 0.25)), "left_leg:rot": lambda u: leg('l', 30 * wave(u, 0.75)), "head:rot": lambda u, s_=sp: [-25 if s_ == "piglin" else -15, 0, 0]}, pri=120, layer="base")
T = "minecraft:iron_golem"
c = mob("iron_golem.riverbed_march", "Iron Golem Marching Along The Riverbed", CAT, T, 3.0, state("!q.is_dead && q.is_in_water && q.ground_speed >= 0.01"), layer="base", pri=110, file=FM, **driven(3.0))
c.cycle("right_leg", "rotation", lambda u: leg('r', 16 * cwave(u)))
c.cycle("left_leg", "rotation", lambda u: leg('l', -16 * cwave(u)))
c.cycle("right_arm", "rotation", lambda u: arm('r', 10, 20 + 6 * wave(u)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 10, 20 + 6 * wave(u, 0.5)))
c.cycle("body", "rotation", lambda u: tilt(10, 4 * cwave(u), 0))
T = "minecraft:spider"
loop_state("spider.leg_scull", "Spider Sculling Its Legs", CAT, T, QW, 0.7, FM, {
    b + ":rot": (lambda u, i=i, b=b: [0, 20 * wave(u, i / 8.0) * (1 if b.startswith("right") else -1), 25 * (1 if b.startswith("right") else -1)])
    for i, b in enumerate([f"{s}_{p}_leg" for s in ("right", "left") for p in ("hind", "middle_hind", "middle_front", "front")])}, pri=120, layer="base")

# ============================================================================ more water behaviour
life("player.swim.cold_water_shiver", "Shivering In Icy Water", CAT, P, WATER + " && q.is_cold", 0.25, FP, {"body:rot": lambda u: [0, 0, 1.2 * wave(u)], "head:rot": lambda u: [0.8 * wave(u, 0.3), 0, 0]})
swim("player.swim.storm_swell", "Riding Storm Swells", SURFACE + " && q.is_thundering && q.sky_exposed", 2.6, {
    "mw_root:pos": lambda u: move(0, 2.0 * wave(u), 0), "mw_root:rot": lambda u: tilt(6 * wave(u, 0.25), 0, 8 * wave(u, 0.1)), "right_arm:rot": lambda u: arm('r', 40, 60 + 10 * wave(u)),
    "left_arm:rot": lambda u: arm('l', 40, 60 + 10 * wave(u, 0.5)), "head:rot": lambda u: [-20, 0, 0]}, pri=317)
swim("player.swim.reach_for_surface", "Reaching For The Surface", UNDER + " && q.vertical_speed > 0.1 && q.air < 0.5", 0.9, {
    "right_arm:rot": lambda u: arm('r', 175, 5 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', 60 + 50 * cwave(u), 40), "head:rot": lambda u: [-50, 0, 0], "right_leg:rot": lambda u: leg('r', 40 * wave(u, 0, 2)),
    "left_leg:rot": lambda u: leg('l', -40 * wave(u, 0, 2))}, pri=321)
loop_state("drowned.surface_lurk", "Drowned Lurking At The Surface", CAT, "minecraft:drowned", "!q.is_dead && q.is_in_water && !q.is_underwater && q.is_night", 3.0, FM, {
    "head:rot": lambda u: [10, 30 * wave(u), 0], "right_arm:rot": lambda u: arm('r', 90 + 10 * wave(u), 40), "left_arm:rot": lambda u: arm('l', 90 + 10 * wave(u, 0.5), 40), "mw_root:pos": lambda u: move(0, -1.5 + 0.4 * wave(u), 0)},
    pri=125)
life("cat.water_panic", "Cat Scrabbling In Water", CAT, "minecraft:cat", "!q.is_dead && q.is_in_water", 0.3, FM, {"head:rot": lambda u: [-30, 20 * wave(u, 0, 0.5), 0], "tail1:rot": lambda u: [-40, 0, 0],
                                                                                                         "tail2:rot": lambda u: [-30, 20 * wave(u), 0]}, pri=90)
beat("salmon.upstream_leap", "Salmon Upstream Leap", CAT, "minecraft:salmon", event("exit_water", "!q.is_dead && q.vertical_speed > 0"), 0.8, FM, {
    "body_back:rot": [(0, Z), (0.2, [0, 30, 0]), (0.4, [0, -30, 0]), (0.8, Z)], "mw_center:rot": [(0, Z), (0.3, tilt(-40, 0, 0)), (0.8, tilt(30, 0, 0))]}, pri=150)

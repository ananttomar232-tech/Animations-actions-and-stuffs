"""Damage, reactions and recovery (category: damage_reactions).

Player reactions are additive (layer "reaction") so they ride on top of whatever the body is doing;
they are chosen by hit direction, damage kind (q.hurt_kind) and severity (q.hurt_amount).
Death clips move limbs and the head only: vanilla already topples the body sideways via the pose stack.
"""
from core import arm, leg
from mobkit import mob, life, loop_state, beat, Z, state, event, wave, cwave, tilt, move

CAT = "damage_reactions"
P = "@player"
LIVE = "!q.is_dead"
FP, FM = "player/damage", "mobs/damage"


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def react(cid, name, trig, L, tracks, pri=400, target=P, file=FP, events=(), layer="reaction"):
    return beat(cid, name, CAT, target, trig, L, file, tracks, pri=pri, layer=layer, events=events)


def kind(k, extra=""):
    return event("hurt", LIVE + " && q.hurt_kind == '%s'%s" % (k, extra))


# ============================================================================ player: direction x severity
react("player.hurt.front_light", "Flinch From A Frontal Hit", event("hurt_front", LIVE + " && q.hurt_kind == 'melee' && q.hurt_amount < 4"), 0.45, {
    "body:rot": [(0, Z), (0.06, tilt(-8), "out_expo"), (0.45, Z)], "head:rot": [(0, Z), (0.06, [-12, 0, 0]), (0.45, Z)], "right_arm:rot": [(0, Z), (0.08, arm('r', 20, 15)), (0.45, Z)]})
react("player.hurt.front_heavy", "Rocked Back By A Heavy Blow", event("hurt_front", LIVE + " && q.hurt_kind == 'melee' && q.hurt_amount >= 4 && q.hurt_amount < 8"), 0.8, {
    "body:rot": [(0, Z), (0.08, tilt(-18), "out_expo"), (0.35, tilt(6)), (0.8, Z)], "head:rot": [(0, Z), (0.08, [-25, 0, 6]), (0.8, Z)], "right_arm:rot": [(0, Z), (0.1, arm('r', 30, 40)), (0.8, Z)],
    "left_arm:rot": [(0, Z), (0.1, arm('l', 20, 45)), (0.8, Z)], "right_leg:rot": [(0, Z), (0.2, leg('r', -20)), (0.8, Z)]})
react("player.hurt.front_crushing", "Staggered By A Crushing Blow", event("hurt_front", LIVE + " && q.hurt_kind == 'melee' && q.hurt_amount >= 8"), 1.3, {
    "body:rot": [(0, Z), (0.08, tilt(-26, 0, 6), "out_expo"), (0.45, tilt(14, 0, -4)), (1.3, Z)], "head:rot": [(0, Z), (0.08, [-30, 10, 0]), (0.6, [15, 0, 0]), (1.3, Z)],
    "right_leg:rot": [(0, Z), (0.2, leg('r', -30)), (0.6, leg('r', 30)), (1.3, Z)], "left_leg:rot": [(0, Z), (0.35, leg('l', 25)), (1.3, Z)], "mw_root:pos": [(0, Z), (0.45, move(0, -1.5, 0)), (1.3, Z)],
    "right_arm:rot": [(0, Z), (0.1, arm('r', 40, 60)), (0.6, arm('r', 10, 30)), (1.3, Z)], "left_arm:rot": [(0, Z), (0.1, arm('l', 40, 60)), (0.6, arm('l', 30, 20)), (1.3, Z)]}, pri=401,
      events=[(0.0, "shake", {"intensity": "0.4", "duration": "0.3"})])
react("player.hurt.back_light", "Jolt From Behind", event("hurt_back", LIVE + " && q.hurt_amount < 4"), 0.5, {
    "body:rot": [(0, Z), (0.06, tilt(12), "out_expo"), (0.5, Z)], "head:rot": [(0, Z), (0.06, [-14, 0, 0]), (0.25, [0, 25, 0]), (0.5, Z)]})
react("player.hurt.back_heavy", "Stumbling Forward From Behind", event("hurt_back", LIVE + " && q.hurt_amount >= 4"), 1.0, {
    "body:rot": [(0, Z), (0.08, tilt(24), "out_expo"), (0.5, tilt(10)), (1.0, Z)], "right_leg:rot": [(0, Z), (0.25, leg('r', 40)), (0.6, leg('r', 10)), (1.0, Z)],
    "right_arm:rot": [(0, Z), (0.15, arm('r', 60, 30)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.15, arm('l', 70, 30)), (1.0, Z)], "head:rot": [(0, Z), (0.08, [-20, 0, 0]), (1.0, Z)]}, pri=401)
c = mob("player.hurt.side", "Knocked Sideways", CAT, P, 0.6, event("hurt", LIVE + " && math.abs(q.hurt_dir) > 45 && math.abs(q.hurt_dir) <= 135 && q.hurt_amount < 5"), layer="reaction", pri=400, file=FP)
for t, k in ((0, 0), (0.07, 1), (0.3, 0.3), (0.6, 0)):
    c.key("body", "rotation", t, [0, "%g * (q.hurt_dir > 0 ? -1 : 1)" % (10 * k), "%g * (q.hurt_dir > 0 ? 1 : -1)" % (14 * k)], lerp="smooth")
    c.key("head", "rotation", t, [0, "%g * (q.hurt_dir > 0 ? -1 : 1)" % (20 * k), "%g * (q.hurt_dir > 0 ? 1 : -1)" % (10 * k)], lerp="smooth")
c = mob("player.hurt.side_heavy", "Spun Around By A Side Blow", CAT, P, 1.0, event("hurt", LIVE + " && math.abs(q.hurt_dir) > 45 && math.abs(q.hurt_dir) <= 135 && q.hurt_amount >= 5"), layer="reaction", pri=401, file=FP)
for t, k, legk in ((0, 0, 0), (0.08, 1, 0.3), (0.4, 0.6, 1), (1.0, 0, 0)):
    c.key("body", "rotation", t, [6 * k, "%g * (q.hurt_dir > 0 ? -1 : 1)" % (35 * k), "%g * (q.hurt_dir > 0 ? 1 : -1)" % (12 * k)], lerp="smooth")
    c.key("right_leg", "rotation", t, [-20 * legk, 0, "%g * (q.hurt_dir > 0 ? 1 : 0)" % (15 * legk)], lerp="smooth")
    c.key("left_leg", "rotation", t, [-20 * legk, 0, "%g * (q.hurt_dir > 0 ? 0 : -1)" % (15 * legk)], lerp="smooth")

# ============================================================================ player: damage kinds
react("player.hurt.arrow_front", "Arrow Strike To The Chest", event("hurt_front", LIVE + " && q.hurt_kind == 'projectile'"), 0.6, {
    "body:rot": [(0, Z), (0.04, tilt(-14, 0, 4), "out_expo"), (0.6, Z)], "left_arm:rot": [(0, Z), (0.12, arm('l', 60, -10, 30)), (0.6, Z)], "head:rot": [(0, Z), (0.06, [10, 0, 0]), (0.6, Z)]})
react("player.hurt.arrow_back", "Arrow In The Back", event("hurt_back", LIVE + " && q.hurt_kind == 'projectile'"), 0.7, {
    "body:rot": [(0, Z), (0.04, tilt(14, 0, -6), "out_expo"), (0.7, Z)], "right_arm:rot": [(0, Z), (0.15, arm('r', -40, 30, -40)), (0.7, Z)], "head:rot": [(0, Z), (0.06, [-30, 0, 0]), (0.7, Z)]}, pri=402)
react("player.hurt.burn", "Scorched", kind("fire"), 0.7, {
    "body:rot": [(0, Z), (0.06, tilt(-6, 0, 6)), (0.7, Z)], "right_arm:rot": [(0, Z), (0.1, arm('r', 30, 50)), (0.3, arm('r', 60, 20)), (0.7, Z)], "left_arm:rot": [(0, Z), (0.1, arm('l', 30, 50)), (0.7, Z)]})
loop_state("player.burning.flail_run", "Running While On Fire", CAT, P, LIVE + " && q.is_on_fire && !q.is_in_water && q.ground_speed >= 0.05", 0.5, FP, {
    "right_arm:rot": lambda u: arm('r', 140 + 30 * wave(u), 20 + 15 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 140 + 30 * wave(u, 0.5), 20 + 15 * wave(u, 0.8)), "head:rot": lambda u: [-15, 25 * wave(u, 0, 0.5), 0]},
    layer="action", pri=410)
loop_state("player.burning.pat_down", "Patting Out Flames", CAT, P, LIVE + " && q.is_on_fire && !q.is_in_water && q.ground_speed < 0.05", 0.6, FP, {
    "right_arm:rot": lambda u: arm('r', 40 + 30 * spike(u, 0, 2, 2), -20, 30), "left_arm:rot": lambda u: arm('l', 30 + 30 * spike(u, 0.25, 2, 2), -10, 30), "body:rot": lambda u: tilt(14, 15 * wave(u), 0),
    "head:rot": lambda u: [30, -10 * wave(u), 0]}, layer="action", pri=411)
react("player.hurt.fall_light", "Knees Buckle On Landing", kind("fall", " && q.hurt_amount < 4"), 0.7, {
    "right_leg:rot": [(0, Z), (0.06, leg('r', 30), "out_expo"), (0.7, Z)], "left_leg:rot": [(0, Z), (0.06, leg('l', 30), "out_expo"), (0.7, Z)], "mw_root:pos": [(0, Z), (0.06, move(0, -2, 0)), (0.7, Z)],
    "body:rot": [(0, Z), (0.06, tilt(16)), (0.7, Z)]})
react("player.hurt.fall_heavy", "Crumpling To A Knee From A Fall", kind("fall", " && q.hurt_amount >= 4"), 1.6, {
    "right_leg:rot": [(0, Z), (0.06, leg('r', 90), "out_expo"), (1.0, leg('r', 80)), (1.6, Z)], "left_leg:rot": [(0, Z), (0.06, leg('l', 20)), (1.0, leg('l', 30)), (1.6, Z)],
    "mw_root:pos": [(0, Z), (0.06, move(0, -5, 0)), (1.0, move(0, -4.5, 0)), (1.6, Z)], "body:rot": [(0, Z), (0.06, tilt(30)), (1.0, tilt(22)), (1.6, Z)],
    "right_arm:rot": [(0, Z), (0.08, arm('r', 40, 20)), (1.0, arm('r', 30, 10)), (1.6, Z)], "head:rot": [(0, Z), (0.1, [30, 0, 0]), (1.6, Z)]}, pri=403, events=[(0.0, "shake", {"intensity": "0.5", "duration": "0.3"})])
react("player.hurt.blast", "Thrown Back By An Explosion", kind("explosion"), 1.4, {
    "body:rot": [(0, Z), (0.06, tilt(-30, 0, 10), "out_expo"), (0.6, tilt(10, 0, -4)), (1.4, Z)], "right_arm:rot": [(0, Z), (0.06, arm('r', 120, 60)), (0.6, arm('r', 30, 20)), (1.4, Z)],
    "left_arm:rot": [(0, Z), (0.06, arm('l', 110, 70)), (0.6, arm('l', 30, 20)), (1.4, Z)], "right_leg:rot": [(0, Z), (0.1, leg('r', 50)), (0.6, Z)], "left_leg:rot": [(0, Z), (0.12, leg('l', -20)), (0.6, Z)],
    "head:rot": [(0, Z), (0.06, [-35, 0, 0]), (1.4, Z)]}, pri=404, events=[(0.0, "shake", {"intensity": "0.8", "duration": "0.6"})])
react("player.reaction.blast_cover", "Covering Up From A Nearby Blast", event("explosion_flinch", LIVE), 0.9, {
    "right_arm:rot": [(0, Z), (0.1, arm('r', 150, -10, 30), "out_expo"), (0.6, arm('r', 140, -10, 30)), (0.9, Z)], "left_arm:rot": [(0, Z), (0.1, arm('l', 150, -10, 30)), (0.6, arm('l', 140, -10, 30)), (0.9, Z)],
    "body:rot": [(0, Z), (0.1, tilt(20, 0, 0)), (0.6, tilt(16)), (0.9, Z)], "mw_root:pos": [(0, Z), (0.1, move(0, -1.5, 0)), (0.6, Z)]}, pri=399)
react("player.hurt.lightning", "Struck By Lightning", kind("lightning"), 1.6, {
    "body:rot": [(0, Z)] + [(0.05 * i, tilt(6 * (-1) ** i, 0, 5 * (-1) ** (i // 2))) for i in range(1, 12)] + [(1.6, Z)],
    "right_arm:rot": [(0, Z), (0.05, arm('r', 30, 80)), (0.6, arm('r', 20, 70)), (1.6, Z)], "left_arm:rot": [(0, Z), (0.05, arm('l', 30, 80)), (0.6, arm('l', 20, 70)), (1.6, Z)],
    "head:rot": [(0, Z), (0.05, [-30, 0, 0]), (1.6, Z)]}, pri=405, events=[(0.0, "particle", {"particle": "spark", "count": "20", "at": "body", "spread": "0.6"})])
react("player.hurt.frostbite", "Frostbite Seizes Up", kind("freeze"), 1.0, {
    "right_arm:rot": [(0, Z), (0.1, arm('r', 20, -15, 30)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.1, arm('l', 20, -15, 30)), (1.0, Z)], "body:rot": [(0, Z), (0.1, tilt(10, 0, 3)), (0.2, tilt(10, 0, -3)), (0.3, tilt(10, 0, 3)), (1.0, Z)],
    "head:rot": [(0, Z), (0.1, [15, 0, 0]), (1.0, Z)]})
life("player.status.frozen_stiff", "Frozen Stiff", CAT, P, LIVE + " && q.freezing > 0.6", 0.18, FP, {"body:rot": lambda u: [0, 0, 1.5 * wave(u)], "right_arm:rot": lambda u: arm('r', 0, -6), "left_arm:rot": lambda u: arm('l', 0, -6)}, pri=95)
react("player.hurt.magic", "Reeling From Magic", kind("magic"), 1.4, {
    "head:rot": [(0, Z), (0.2, [10, 15, 15]), (0.6, [10, -15, -15]), (1.0, [5, 8, 8]), (1.4, Z)], "body:rot": [(0, Z), (0.3, tilt(6, 0, 8)), (0.8, tilt(6, 0, -8)), (1.4, Z)],
    "left_arm:rot": [(0, Z), (0.3, arm('l', 120, -10, 30)), (1.0, arm('l', 110, -10, 30)), (1.4, Z)]})
life("player.status.poisoned_sway", "Poisoned Nausea Sway", CAT, P, LIVE + " && q.is_poisoned", 3.0, FP, {"body:rot": lambda u: tilt(6 + 3 * wave(u, 0.25), 0, 6 * wave(u)), "head:rot": lambda u: [12, 0, 8 * wave(u, 0.2)]}, pri=96)
life("player.status.withering", "Withering Decay", CAT, P, LIVE + " && q.is_withering", 2.0, FP, {
    "body:rot": lambda u: tilt(14, 0, 0), "head:rot": lambda u: [20 + 4 * wave(u), 0, 0], "right_arm:rot": lambda u: arm('r', 10, -4), "left_arm:rot": lambda u: arm('l', 10, -4)}, pri=97)
react("player.hurt.wither", "Wither Blight Spasm", kind("wither"), 1.0, {"body:rot": [(0, Z), (0.08, tilt(24, 0, 0), "out_expo"), (1.0, Z)], "head:rot": [(0, Z), (0.08, [30, 0, 0]), (1.0, Z)],
                                                                        "right_arm:rot": [(0, Z), (0.1, arm('r', 50, -10, 30)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.1, arm('l', 50, -10, 30)), (1.0, Z)]})
react("player.hurt.choking", "Choking For Air", kind("drown"), 1.0, {
    "right_arm:rot": [(0, Z), (0.15, arm('r', 120, -30, 40)), (0.8, arm('r', 115, -30, 40)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.15, arm('l', 120, -30, 40)), (0.8, arm('l', 115, -30, 40)), (1.0, Z)],
    "head:rot": [(0, Z), (0.15, [-30, 0, 0]), (0.5, [-20, 0, 8]), (1.0, Z)]})
react("player.hurt.prick", "Yelping At A Thorn", kind("prick"), 0.6, {
    "mw_root:pos": [(0, Z), (0.08, move(0, 1.5, 0), "out_expo"), (0.3, Z)], "right_leg:rot": [(0, Z), (0.08, leg('r', 50)), (0.4, Z)], "right_arm:rot": [(0, Z), (0.1, arm('r', 30, 40)), (0.6, Z)],
    "left_arm:rot": [(0, Z), (0.1, arm('l', 30, 40)), (0.6, Z)]})
react("player.hurt.thorns", "Recoiling From Thorns Armour", kind("thorns"), 0.6, {
    "right_arm:rot": [(0, Z), (0.06, arm('r', -20, 20), "out_expo"), (0.6, Z)], "body:rot": [(0, Z), (0.06, tilt(-10, 10, 0)), (0.6, Z)], "head:rot": [(0, Z), (0.06, [-10, -15, 0]), (0.6, Z)]})
react("player.hurt.sonic_boom", "Hit By A Sonic Boom", kind("sonic"), 1.6, {
    "body:rot": [(0, Z), (0.05, tilt(-35), "out_expo"), (0.5, tilt(-10)), (1.6, Z)], "head:rot": [(0, Z), (0.05, [-40, 0, 0]), (0.8, [10, 0, 10]), (1.6, Z)],
    "right_arm:rot": [(0, Z), (0.05, arm('r', 160, 60)), (0.8, arm('r', 150, -20, 30)), (1.6, Z)], "left_arm:rot": [(0, Z), (0.05, arm('l', 160, 60)), (0.8, arm('l', 150, -20, 30)), (1.6, Z)]}, pri=406,
      events=[(0.0, "shake", {"intensity": "1.0", "duration": "0.8"})])
react("player.hurt.starving", "Doubling Over With Hunger", kind("starve"), 1.4, {
    "body:rot": [(0, Z), (0.3, tilt(30)), (1.0, tilt(26)), (1.4, Z)], "right_arm:rot": [(0, Z), (0.3, arm('r', 40, -20, 40)), (1.0, arm('r', 40, -20, 40)), (1.4, Z)],
    "left_arm:rot": [(0, Z), (0.3, arm('l', 40, -20, 40)), (1.0, arm('l', 40, -20, 40)), (1.4, Z)]})
react("player.hurt.suffocating", "Suffocating In A Wall", kind("suffocate"), 0.8, {
    "right_arm:rot": [(0, Z), (0.1, arm('r', 90, 40)), (0.4, arm('r', 100, 30)), (0.8, Z)], "left_arm:rot": [(0, Z), (0.15, arm('l', 90, 40)), (0.45, arm('l', 100, 30)), (0.8, Z)],
    "head:rot": [(0, Z), (0.1, [0, 20, 0]), (0.4, [0, -20, 0]), (0.8, Z)]})
react("player.hurt.crushed", "Crushed By A Falling Block", kind("crush"), 1.2, {
    "mw_root:pos": [(0, Z), (0.05, move(0, -4, 0), "out_expo"), (0.6, move(0, -3, 0)), (1.2, Z)], "head:rot": [(0, Z), (0.05, [40, 0, 0]), (1.2, Z)],
    "right_arm:rot": [(0, Z), (0.05, arm('r', 160, 20)), (0.6, arm('r', 150, 20)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.05, arm('l', 160, 20)), (0.6, arm('l', 150, 20)), (1.2, Z)],
    "right_leg:rot": [(0, Z), (0.05, leg('r', 40)), (1.2, Z)], "left_leg:rot": [(0, Z), (0.05, leg('l', 40)), (1.2, Z)]}, pri=407)
react("player.hurt.dragon_breath", "Scalded By Dragon's Breath", kind("breath"), 1.0, {
    "right_arm:rot": [(0, Z), (0.1, arm('r', 120, 0, 0)), (0.8, arm('r', 110, 10)), (1.0, Z)], "head:rot": [(0, Z), (0.1, [25, -20, 0]), (1.0, Z)], "body:rot": [(0, Z), (0.1, tilt(10, -20, 0)), (1.0, Z)]})
react("player.hurt.sting", "Stung", kind("sting"), 0.8, {
    "mw_root:pos": [(0, Z), (0.06, move(0, 1, 0)), (0.25, Z)], "right_arm:rot": [(0, Z), (0.1, arm('r', 60, 30)), (0.25, arm('r', 30, 60)), (0.4, arm('r', 60, 30)), (0.8, Z)],
    "head:rot": [(0, Z), (0.06, [-20, 25, 0]), (0.8, Z)]})

# ============================================================================ player: context, recovery and death
react("player.hurt.sprint_trip", "Tripping Mid-Sprint", event("hurt_front", LIVE + " && q.is_sprinting && q.hurt_amount >= 3"), 1.0, {
    "body:rot": [(0, Z), (0.1, tilt(25)), (0.4, tilt(-8)), (1.0, Z)], "right_leg:rot": [(0, Z), (0.1, leg('r', -30)), (0.4, leg('r', 40)), (1.0, Z)],
    "right_arm:rot": [(0, Z), (0.1, arm('r', 90, 40)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.12, arm('l', 100, 40)), (1.0, Z)]}, pri=408)
react("player.hurt.airborne_flail", "Knocked Into The Air", event("hurt", LIVE + " && !q.is_on_ground && q.hurt_amount >= 4"), 1.0, {
    "right_arm:rot": [(0, Z), (0.1, arm('r', 150, 60)), (0.4, arm('r', 90, 80)), (0.7, arm('r', 150, 60)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.15, arm('l', 140, 60)), (0.45, arm('l', 80, 80)), (1.0, Z)],
    "right_leg:rot": [(0, Z), (0.2, leg('r', 40)), (0.6, leg('r', -10)), (1.0, Z)], "left_leg:rot": [(0, Z), (0.25, leg('l', -20)), (0.65, leg('l', 30)), (1.0, Z)]}, pri=409)
react("player.hurt.mid_meal", "Choking On A Bite", event("hurt", LIVE + " && q.is_using_item && q.use_anim == 'eat'"), 1.0, {
    "head:rot": [(0, Z), (0.1, [20, 0, 0]), (0.25, [-10, 0, 0]), (0.4, [20, 0, 0]), (1.0, Z)], "left_arm:rot": [(0, Z), (0.15, arm('l', 90, -20, 30)), (1.0, Z)], "body:rot": [(0, Z), (0.1, tilt(14)), (0.4, tilt(14)), (1.0, Z)]}, pri=410)
react("player.hurt.swimming_jerk", "Jerked In The Water", event("hurt", LIVE + " && q.is_in_water"), 0.6, {
    "body:rot": [(0, Z), (0.06, tilt(-10, 0, 8), "out_expo"), (0.6, Z)], "right_leg:rot": [(0, Z), (0.1, leg('r', 40)), (0.6, Z)], "left_leg:rot": [(0, Z), (0.1, leg('l', 40)), (0.6, Z)]})
react("player.hurt.shrug_off", "Shrugging Off A Scratch", event("hurt", LIVE + " && q.hurt_amount < 1.5 && q.trait_confidence > 0.7"), 0.9, {
    "head:rot": [(0, Z), (0.1, [-6, 0, 0]), (0.4, [0, 0, 14]), (0.9, Z)], "right_arm:rot": [(0, Z), (0.4, arm('r', 20, 30)), (0.9, Z)], "body:rot": [(0, Z), (0.4, tilt(-4, 0, 0)), (0.9, Z)]}, pri=398)
loop_state("player.status.near_death_kneel", "Kneeling At Death's Door", CAT, P, LIVE + " && q.health < 0.15 && q.is_on_ground && q.ground_speed < 0.02 && !q.is_using_item", 2.0, FP, {
    "right_leg:rot": lambda u: leg('r', 85), "left_leg:rot": lambda u: leg('l', 20), "mw_root:pos": lambda u: move(0, -4.5, 0), "body:rot": lambda u: tilt(18 + 3 * wave(u), 0, 0),
    "right_arm:rot": lambda u: arm('r', 40, 10), "left_arm:rot": lambda u: arm('l', 10, -10, 30), "head:rot": lambda u: [25 + 4 * wave(u, 0.2), 0, 0]}, layer="overlay", pri=380)
loop_state("player.status.wounded_breath", "Heavy Wounded Breathing", CAT, P, LIVE + " && q.health >= 0.15 && q.health < 0.3 && q.ground_speed < 0.02", 1.2, FP, {
    "body:rot": lambda u: tilt(10 + 4 * wave(u), 0, 0), "head:rot": lambda u: [8 + 4 * wave(u, 0.1), 0, 0], "left_arm:rot": lambda u: arm('l', 30, -10, 30)}, layer="additive", pri=98)
beat("player.recover.catch_balance", "Catching Your Balance", CAT, P, event("staggered", LIVE), 1.2, FP, {
    "right_arm:rot": [(0, Z), (0.2, arm('r', 60, 80)), (0.6, arm('r', 30, 60)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.25, arm('l', 50, 80)), (0.65, arm('l', 30, 60)), (1.2, Z)],
    "right_leg:rot": [(0, Z), (0.3, leg('r', -25)), (0.7, leg('r', 15)), (1.2, Z)], "body:rot": [(0, Z), (0.2, tilt(-14, 0, 8)), (0.6, tilt(8, 0, -6)), (1.2, Z)]}, pri=412)
beat("player.recover.totem_revival", "Totem Of Undying Revival", CAT, P, event("totem"), 2.4, FP, {
    "body:rot": [(0, tilt(40)), (0.5, tilt(-25), "out_back"), (1.6, tilt(-20)), (2.4, Z)], "head:rot": [(0, [40, 0, 0]), (0.5, [-40, 0, 0]), (1.6, [-35, 0, 0]), (2.4, Z)],
    "right_arm:rot": [(0, arm('r', 20)), (0.5, arm('r', 170, 30)), (1.6, arm('r', 170, 40)), (2.4, Z)], "left_arm:rot": [(0, arm('l', 20)), (0.5, arm('l', 170, 30)), (1.6, arm('l', 170, 40)), (2.4, Z)],
    "mw_root:pos": [(0, move(0, -3, 0)), (0.5, move(0, 1, 0)), (1.0, Z)]}, pri=450, layer="action",
     events=[(0.4, "particle", {"particle": "magic_glint", "count": "30", "at": "body", "spread": "1"}), (0.4, "shake", {"intensity": "0.3", "duration": "0.5"})])
beat("player.death.fall_back", "Death: Falling Backwards", CAT, P, event("death", "q.hurt_kind == 'melee' && math.abs(q.hurt_dir) <= 45"), 1.2, FP, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', 60, 60)), (1.2, arm('r', 20, 80))], "left_arm:rot": [(0, Z), (0.3, arm('l', 50, 60)), (1.2, arm('l', 20, 70))], "head:rot": [(0, Z), (0.3, [-30, 0, 0]), (1.2, [-10, 0, 20])],
    "right_leg:rot": [(0, Z), (0.4, leg('r', 30)), (1.2, leg('r', 10))]}, pri=500, layer="action")
beat("player.death.fall_forward", "Death: Pitching Forward", CAT, P, event("death", "q.hurt_kind == 'melee' && math.abs(q.hurt_dir) > 45"), 1.2, FP, {
    "right_leg:rot": [(0, Z), (0.3, leg('r', 60)), (1.2, leg('r', 30))], "left_leg:rot": [(0, Z), (0.35, leg('l', 50)), (1.2, leg('l', 20))], "head:rot": [(0, Z), (0.4, [30, 0, 0]), (1.2, [10, 0, -20])],
    "right_arm:rot": [(0, Z), (0.4, arm('r', 90, 20)), (1.2, arm('r', 160, 10))], "left_arm:rot": [(0, Z), (0.4, arm('l', 80, 20)), (1.2, arm('l', 10, 10))]}, pri=500, layer="action")
beat("player.death.crumple", "Death: Crumpling", CAT, P, event("death", "q.hurt_kind != 'melee' && q.hurt_kind != 'fire' && q.hurt_kind != 'fall' && q.hurt_kind != 'explosion' && q.hurt_kind != 'drown'"),
     1.4, FP, {"right_leg:rot": [(0, Z), (0.5, leg('r', 90)), (1.4, leg('r', 70))], "left_leg:rot": [(0, Z), (0.6, leg('l', 80)), (1.4, leg('l', 60))], "body:rot": [(0, Z), (0.6, tilt(30)), (1.4, tilt(40))],
               "head:rot": [(0, Z), (0.8, [40, 0, 10])], "right_arm:rot": [(0, Z), (1.4, arm('r', 20, 5))], "left_arm:rot": [(0, Z), (1.4, arm('l', 20, 5))]}, pri=500, layer="action")
beat("player.death.burning", "Death: Consumed By Fire", CAT, P, event("death", "q.hurt_kind == 'fire'"), 1.4, FP, {
    "right_arm:rot": [(0, arm('r', 150, 30)), (0.5, arm('r', 160, 50)), (1.4, arm('r', 60, 30))], "left_arm:rot": [(0, arm('l', 150, 30)), (0.6, arm('l', 150, 60)), (1.4, arm('l', 60, 30))],
    "head:rot": [(0, Z), (0.5, [-40, 0, 0]), (1.4, [10, 0, 0])], "body:rot": [(0, Z), (0.5, tilt(-14)), (1.4, tilt(20))]}, pri=500, layer="action")
beat("player.death.impact", "Death: Fatal Fall", CAT, P, event("death", "q.hurt_kind == 'fall'"), 0.8, FP, {
    "right_arm:rot": [(0, Z), (0.06, arm('r', 90, 80)), (0.8, arm('r', 80, 90))], "left_arm:rot": [(0, Z), (0.06, arm('l', 90, 80)), (0.8, arm('l', 80, 90))], "right_leg:rot": [(0, Z), (0.06, leg('r', 10, 30))],
    "left_leg:rot": [(0, Z), (0.06, leg('l', 10, 30))]}, pri=500, layer="action")
beat("player.death.blasted", "Death: Blown Apart", CAT, P, event("death", "q.hurt_kind == 'explosion'"), 1.0, FP, {
    "right_arm:rot": [(0, Z), (0.06, arm('r', 170, 80), "out_expo"), (1.0, arm('r', 120, 90))], "left_arm:rot": [(0, Z), (0.06, arm('l', 170, 80), "out_expo"), (1.0, arm('l', 120, 90))],
    "right_leg:rot": [(0, Z), (0.06, leg('r', 60, 30)), (1.0, leg('r', 40, 20))], "left_leg:rot": [(0, Z), (0.06, leg('l', -30, 30)), (1.0, leg('l', -10, 20))], "head:rot": [(0, Z), (0.06, [-40, 0, 0])]},
     pri=500, layer="action")
beat("player.death.drowned", "Death: Going Limp Underwater", CAT, P, event("death", "q.hurt_kind == 'drown'"), 2.0, FP, {
    "right_arm:rot": [(0, arm('r', 150, 20)), (2.0, arm('r', 60, 60))], "left_arm:rot": [(0, arm('l', 140, 20)), (2.0, arm('l', 70, 50))], "head:rot": [(0, [-40, 0, 0]), (2.0, [20, 0, 20])],
    "right_leg:rot": [(0, Z), (2.0, leg('r', 30, 10))], "left_leg:rot": [(0, Z), (2.0, leg('l', 10, 20))]}, pri=500, layer="action")

# ============================================================================ mobs: hurt and death
for T, sp, label, L in (("minecraft:zombie", "zombie", "Zombie", 0.6), ("minecraft:husk", "husk", "Husk", 0.7), ("minecraft:skeleton", "skeleton", "Skeleton", 0.5),
                        ("minecraft:wither_skeleton", "wither_skeleton", "Wither Skeleton", 0.55), ("minecraft:piglin", "piglin", "Piglin", 0.5), ("minecraft:vindicator", "vindicator", "Vindicator", 0.55)):
    F = FM + "/" + sp
    shape = {"zombie": (14, 0, 0.3), "husk": (10, 6, 0.4), "skeleton": (20, -4, 0.15), "wither_skeleton": (8, 10, 0.25), "piglin": (16, 8, 0.2), "vindicator": (10, -10, 0.3), "enderman": (24, 0, 0.1)}[sp]
    react(sp + ".hurt_reel", label + " Reeling From A Hit", event("hurt_front", LIVE), L, {
        "body:rot": [(0, Z), (0.06, tilt(-shape[0], shape[1], 0), "out_expo"), (L * shape[2] + 0.1, tilt(shape[0] * 0.3, -shape[1], 0)), (L, Z)],
        "head:rot": [(0, Z), (0.06, [-shape[0], shape[1] * 2, 0]), (L, Z)], "right_arm:rot": [(0, Z), (0.08, arm('r', 0, shape[0] * 2)), (L, Z)]}, target=T, file=F, pri=200)
    react(sp + ".hurt_lurch", label + " Lurching From A Blow Behind", event("hurt_back", LIVE), L + 0.2, {
        "body:rot": [(0, Z), (0.06, tilt(shape[0] * 1.2, 0, shape[1] * 0.5), "out_expo"), (L + 0.2, Z)], "right_leg:rot": [(0, Z), (0.15, leg('r', 20 + shape[1])), (L + 0.2, Z)],
        "head:rot": [(0, Z), (0.06, [-shape[0] * 0.8, 0, 0]), (L + 0.2, Z)]}, target=T, file=F, pri=200)
for T, sp, label, kneel in (("minecraft:zombie", "zombie", "Zombie", 1.0), ("minecraft:skeleton", "skeleton", "Skeleton", 0.0), ("minecraft:piglin", "piglin", "Piglin", 0.6),
                            ("minecraft:pillager", "pillager", "Pillager", 0.8), ("minecraft:enderman", "enderman", "Enderman", 0.3)):
    F = FM + "/" + sp
    tr = {"right_leg:rot": [(0, Z), (0.4, leg('r', 70 * kneel + 10)), (1.0, leg('r', 60 * kneel))], "left_leg:rot": [(0, Z), (0.5, leg('l', 50 * kneel)), (1.0, leg('l', 40 * kneel))],
          "head:rot": [(0, Z), (0.5, [30 - 50 * (1 - kneel), 0, 20 * kneel]), (1.0, [20, 0, 25])]}
    if sp == "skeleton":
        tr.update({"right_arm:rot": [(0, Z), (0.2, arm('r', 30, 60)), (1.0, arm('r', 10, 90))], "left_arm:rot": [(0, Z), (0.25, arm('l', 30, 60)), (1.0, arm('l', 10, 90))]})
    elif sp == "pillager":
        tr.update({"arms:rot": [(0, Z), (0.4, [-20, 0, 0]), (1.0, [10, 0, 0])]})
    else:
        tr.update({"right_arm:rot": [(0, Z), (0.4, arm('r', 60 * kneel + 20, 10)), (1.0, arm('r', 10, 20))], "left_arm:rot": [(0, Z), (0.5, arm('l', 40, 20)), (1.0, arm('l', 5, 30))]})
    react(sp + ".death", label + " Death Collapse", event("death"), 1.0, tr, target=T, file=F, pri=300, layer="action")
# each quadruped gets its own way of taking a hit and of dying
QF = {sp: FM + "/" + sp for sp in ("cow", "pig", "sheep", "goat", "polar_bear")}
react("cow.hurt_jolt", "Cow Bellowing Kick", event("hurt", LIVE), 0.7, {
    "head:rot": [(0, Z), (0.08, [-30, 0, 0], "out_expo"), (0.7, Z)], "left_hind_leg:rot": [(0, Z), (0.15, [40, 0, 0]), (0.3, [-10, 0, 0]), (0.7, Z)], "right_hind_leg:rot": [(0, Z), (0.18, [35, 0, 0]), (0.7, Z)]},
      target="minecraft:cow", file=QF["cow"], pri=200)
react("pig.hurt_jolt", "Pig Squealing Hop", event("hurt", LIVE), 0.5, {
    "mw_center:pos": [(0, Z), (0.08, move(0, 2.5, 0), "out_expo"), (0.3, Z)], "mw_center:rot": [(0, Z), (0.08, [0, "q.hurt_dir > 0 ? -25 : 25", 0]), (0.5, Z)], "head:rot": [(0, Z), (0.08, [-20, 0, 0]), (0.5, Z)]},
      target="minecraft:pig", file=QF["pig"], pri=200)
react("sheep.hurt_jolt", "Sheep Startled Sideways Skip", event("hurt", LIVE), 0.6, {
    "mw_center:rot": [(0, Z), (0.08, [0, 0, "q.hurt_dir > 0 ? 18 : -18"], "out_expo"), (0.6, Z)], "left_front_leg:rot": [(0, Z), (0.1, [0, 0, -20]), (0.6, Z)],
    "right_front_leg:rot": [(0, Z), (0.1, [0, 0, 20]), (0.6, Z)]}, target="minecraft:sheep", file=QF["sheep"], pri=200)
react("goat.hurt_jolt", "Goat Dropping Into A Defensive Brace", event("hurt", LIVE), 0.8, {
    "head:rot": [(0, Z), (0.1, [35, 0, 0], "out_quad"), (0.8, Z)], "left_front_leg:rot": [(0, Z), (0.1, [-25, 0, -6]), (0.8, Z)], "right_front_leg:rot": [(0, Z), (0.1, [-25, 0, 6]), (0.8, Z)],
    "mw_center:rot": [(0, Z), (0.1, tilt(8, 0, 0)), (0.8, Z)]}, target="minecraft:goat", file=QF["goat"], pri=200)
react("polar_bear.hurt_jolt", "Polar Bear Rearing Snarl", event("hurt", LIVE), 1.0, {
    "mw_center:rot": [(0, Z), (0.2, tilt(-30, 0, 0), "out_quad"), (0.6, tilt(-25, 0, 0)), (1.0, Z)], "head:rot": [(0, Z), (0.2, [-25, 0, 0]), (1.0, Z)],
    "left_front_leg:rot": [(0, Z), (0.2, [-60, 0, -10]), (1.0, Z)], "right_front_leg:rot": [(0, Z), (0.2, [-60, 0, 10]), (1.0, Z)]}, target="minecraft:polar_bear", file=QF["polar_bear"], pri=200)
react("cow.death_buckle", "Cow Kneeling Front-First In Death", event("death"), 1.4, {
    "left_front_leg:rot": [(0, Z), (0.3, [-85, 0, 0])], "right_front_leg:rot": [(0, Z), (0.35, [-85, 0, 0])], "left_hind_leg:rot": [(0, Z), (0.6, Z), (1.0, [70, 0, 0])],
    "right_hind_leg:rot": [(0, Z), (0.65, Z), (1.1, [70, 0, 0])], "head:rot": [(0, Z), (0.4, [20, 0, 0]), (1.4, [45, 0, 10])]}, target="minecraft:cow", file=QF["cow"], pri=300, layer="action")
react("pig.death_buckle", "Pig Rolling Over Legs Out", event("death"), 0.9, {
    "left_front_leg:rot": [(0, Z), (0.3, [-30, 0, -50]), (0.6, [-20, 0, -45]), (0.9, [-25, 0, -50])], "right_front_leg:rot": [(0, Z), (0.3, [-30, 0, 50]), (0.9, [-25, 0, 50])],
    "left_hind_leg:rot": [(0, Z), (0.3, [30, 0, -50]), (0.7, [25, 0, -40]), (0.9, [30, 0, -50])], "right_hind_leg:rot": [(0, Z), (0.3, [30, 0, 50]), (0.9, [30, 0, 50])]},
      target="minecraft:pig", file=QF["pig"], pri=300, layer="action")
react("sheep.death_buckle", "Sheep Sitting Back In Death", event("death"), 1.2, {
    "left_hind_leg:rot": [(0, Z), (0.3, [-80, 0, 0])], "right_hind_leg:rot": [(0, Z), (0.35, [-80, 0, 0])], "mw_center:rot": [(0, Z), (0.4, tilt(-20, 0, 0)), (1.2, tilt(-10, 0, 0))],
    "head:rot": [(0, Z), (0.6, [10, 0, 35]), (1.2, [20, 0, 40])]}, target="minecraft:sheep", file=QF["sheep"], pri=300, layer="action")
react("goat.death_buckle", "Goat Keeling Over Stiff-Legged", event("death"), 0.7, {
    "left_front_leg:rot": [(0, Z), (0.15, [0, 0, -40])], "right_front_leg:rot": [(0, Z), (0.15, [0, 0, 40])], "left_hind_leg:rot": [(0, Z), (0.15, [0, 0, -40])],
    "right_hind_leg:rot": [(0, Z), (0.15, [0, 0, 40])], "head:rot": [(0, Z), (0.3, [-40, 0, 0])]}, target="minecraft:goat", file=QF["goat"], pri=300, layer="action")
react("polar_bear.death_buckle", "Polar Bear Heavy Slump", event("death"), 1.6, {
    "left_front_leg:rot": [(0, Z), (0.8, [-40, 0, -50])], "right_front_leg:rot": [(0, Z), (0.8, [-40, 0, 50])], "left_hind_leg:rot": [(0, Z), (1.0, [40, 0, -45])], "right_hind_leg:rot": [(0, Z), (1.0, [40, 0, 45])],
    "head:rot": [(0, Z), (1.2, [50, 0, 0])], "mw_center:pos": [(0, Z), (1.0, move(0, -3, 0))]}, target="minecraft:polar_bear", file=QF["polar_bear"], pri=300, layer="action")
for T, sp, label in (("minecraft:cat", "cat", "Cat"), ("minecraft:horse", "horse", "Horse")):
    F = FM + "/" + sp
    tail = {"cat": "tail1", "horse": "tail"}[sp]
    head = "head_parts" if sp == "horse" else "head"
    react(sp + ".yelp_flinch", label + (" Hissing Flinch" if sp != "horse" else " Shying From Pain"), event("hurt", LIVE), 0.7, {
        head + ":rot": [(0, Z), (0.06, [-25 if sp != "horse" else -35, 0, 0], "out_expo"), (0.7, Z)], tail + ":rot": [(0, Z), (0.08, [40, 0, 0]), (0.7, Z)],
        "mw_center:pos": [(0, Z), (0.08, move(0, -1.2 if sp != "horse" else 0.5, 0)), (0.7, Z)]}, target=T, file=F, pri=200)
react("wolf.yelp_flinch", "Wolf Cowering Yelp", event("hurt", LIVE), 0.9, {
    "mw_center:pos": [(0, Z), (0.08, move(0, -2, 0.5)), (0.9, Z)], "tail:rot": [(0, Z), (0.08, [60, 0, 0]), (0.9, Z)], "head:rot": [(0, Z), (0.08, [25, 0, 0]), (0.9, Z)],
    "left_hind_leg:rot": [(0, Z), (0.1, [30, 0, 0]), (0.9, Z)], "right_hind_leg:rot": [(0, Z), (0.1, [30, 0, 0]), (0.9, Z)]}, target="minecraft:wolf", file=FM + "/wolf", pri=200)
react("fox.yelp_flinch", "Fox Spinning Hop Away", event("hurt", LIVE), 0.6, {
    "mw_center:rot": [(0, Z), (0.25, [0, "q.hurt_dir > 0 ? -120 : 120", 0], "out_quad"), (0.6, Z)], "mw_center:pos": [(0, Z), (0.12, move(0, 2, 0)), (0.3, Z)], "tail:rot": [(0, Z), (0.15, [0, 40, 0]), (0.6, Z)]},
      target="minecraft:fox", file=FM + "/fox", pri=200)
for T, sp, label in (("minecraft:chicken", "chicken", "Chicken"), ("minecraft:rabbit", "rabbit", "Rabbit"), ("minecraft:spider", "spider", "Spider"), ("minecraft:blaze", "blaze", "Blaze")):
    F = FM + "/" + sp
    if sp == "chicken":
        tr = {"right_wing:rot": [(0, Z), (0.1, [0, 0, 90]), (0.5, [0, 0, 70])], "left_wing:rot": [(0, Z), (0.1, [0, 0, -90]), (0.5, [0, 0, -70])], "head:rot": [(0, Z), (0.4, [40, 0, 30])],
              "right_leg:rot": [(0, Z), (0.3, [-60, 0, 0])]}
    elif sp == "rabbit":
        tr = {"left_haunch:rot": [(0, Z), (0.3, [-40, 0, 0])], "right_haunch:rot": [(0, Z), (0.3, [-40, 0, 0])], "right_ear:rot": [(0, Z), (0.4, [40, 0, 20])], "left_ear:rot": [(0, Z), (0.4, [40, 0, -20])]}
    elif sp == "spider":
        tr = {b + ":rot": [(0, Z), (0.3 + 0.03 * i, [0, 0, (-50 if b.startswith("right") else 50)])] for i, b in enumerate([f"{s}_{p}_leg" for s in ("right", "left") for p in ("hind", "middle_hind", "middle_front", "front")])}
    else:
        tr = {"part%d:pos" % i: [(0, Z), (0.5, move(3 * (1 if i % 2 else -1), -2 + 0.3 * i, 3 * (1 if i % 3 else -1)), "out_quad")] for i in range(12)}
    react(sp + ".death", label + {"chicken": " Death Flutter", "rabbit": " Going Still", "spider": " Legs Curling In Death", "blaze": " Rods Scattering"}[sp], event("death"), 0.6, tr, target=T, file=F,
          pri=300, layer="action")
for T, sp, label in (("minecraft:villager", "villager", "Villager"), ("minecraft:iron_golem", "iron_golem", "Iron Golem")):
    F = FM + "/" + sp
    if sp == "villager":
        react("villager.hurt_from_behind", "Villager Hit From Behind", event("hurt_back", LIVE), 0.8, {"body:rot": [(0, Z), (0.06, tilt(16), "out_expo"), (0.8, Z)], "arms:rot": [(0, Z), (0.1, [-60, 0, 0]), (0.8, Z)],
                                                                                                 "head:rot": [(0, Z), (0.08, [-20, 0, 0]), (0.4, [0, 40, 0]), (0.8, Z)]}, target=T, file=F, pri=200)
        react("villager.death", "Villager Death", event("death"), 1.0, {"right_leg:rot": [(0, Z), (0.5, leg('r', 60))], "left_leg:rot": [(0, Z), (0.5, leg('l', 40))], "arms:rot": [(0, Z), (0.6, [20, 0, 0])],
                                                                     "head:rot": [(0, Z), (0.6, [30, 0, 20])]}, target=T, file=F, pri=300, layer="action")
    else:
        react("iron_golem.hurt_crack", "Iron Golem Shrugging Off A Crack", event("hurt", LIVE), 0.8, {"body:rot": [(0, Z), (0.08, [-4, 0, "q.hurt_dir > 0 ? 5 : -5"]), (0.8, Z)],
                                                                                                    "head:rot": [(0, Z), (0.2, [0, "q.hurt_dir * 0.3", 0]), (0.8, Z)]}, target=T, file=F, pri=200)
react("enderman.hurt_glitch", "Enderman Flickering Recoil", event("hurt", LIVE), 0.5, {
    "head:rot": [(0, Z), (0.05, [0, 20, 15]), (0.1, [0, -20, -15]), (0.15, [0, 15, 10]), (0.2, [0, -10, -6]), (0.5, Z)], "body:rot": [(0, Z), (0.05, tilt(-10, 0, 6)), (0.15, tilt(-6, 0, -6)), (0.5, Z)],
    "mw_root:scl": [(0, [1, 1, 1]), (0.05, [0.95, 1.05, 0.95]), (0.15, [1.04, 0.97, 1.04]), (0.5, [1, 1, 1])]}, target="minecraft:enderman", file=FM + "/enderman", pri=200)

# ============================================================================ more reactions
react("player.hurt.pummelled", "Turtling Under A Barrage", event("hurt", LIVE + " && q.recent_hurt < 1.0 && q.hurt_kind == 'melee'"), 0.9, {
    "right_arm:rot": [(0, Z), (0.1, arm('r', 130, -10, 40)), (0.7, arm('r', 125, -10, 40)), (0.9, Z)], "left_arm:rot": [(0, Z), (0.1, arm('l', 130, -10, 40)), (0.7, arm('l', 125, -10, 40)), (0.9, Z)],
    "body:rot": [(0, Z), (0.1, tilt(24)), (0.7, tilt(22)), (0.9, Z)], "mw_root:pos": [(0, Z), (0.1, move(0, -1.5, 0)), (0.7, move(0, -1.5, 0)), (0.9, Z)]}, pri=413)
react("player.hurt.armour_clank", "Blow Glancing Off Heavy Armour", event("hurt", LIVE + " && q.armor_weight > 0.6 && q.hurt_amount < 3"), 0.5, {
    "body:rot": [(0, Z), (0.05, tilt(-3, 4, 0)), (0.5, Z)], "head:rot": [(0, Z), (0.1, [0, -14, 0]), (0.5, Z)]}, pri=397, events=[(0.0, "impact", {"material": "metal", "strength": "0.5"})])
for T, sp, label, tracks in (
        ("minecraft:creeper", "creeper", "Creeper Hissing Swell", {"body:scl": [(0, [1, 1, 1]), (0.1, [1.1, 1.06, 1.1]), (0.5, [1, 1, 1])], "head:rot": [(0, Z), (0.1, [-10, 0, 0]), (0.5, Z)]}),
        ("minecraft:spider", "spider", "Spider Legs Snapping Inward", {b + ":rot": [(0, Z), (0.06, [0, 0, (-30 if b.startswith("right") else 30)]), (0.5, Z)]
                                                                    for b in [f"{s_}_{p}_leg" for s_ in ("right", "left") for p in ("hind", "middle_hind", "middle_front", "front")]}),
        ("minecraft:slime", "slime", "Slime Squashed By A Hit", {"mw_root:scl": [(0, [1, 1, 1]), (0.05, [1.3, 0.7, 1.3]), (0.2, [0.85, 1.2, 0.85]), (0.5, [1, 1, 1])]}),
        ("minecraft:ravager", "ravager", "Ravager Pained Bellow", {"neck:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.6, Z)], "mouth:rot": [(0, Z), (0.1, [40, 0, 0]), (0.6, Z)]}),
        ("minecraft:warden", "warden", "Warden Enraged By Pain", {"left_ribcage:rot": [(0, Z), (0.1, [0, -25, 0]), (0.8, Z)], "right_ribcage:rot": [(0, Z), (0.1, [0, 25, 0]), (0.8, Z)],
                                                                 "head:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.8, Z)], "body:rot": [(0, Z), (0.1, tilt(-8)), (0.8, Z)]}),
        ("minecraft:chicken", "chicken", "Chicken Feathers Flying", {"right_wing:rot": [(0, Z), (0.06, [0, 0, 70]), (0.2, [0, 0, 20]), (0.35, [0, 0, 60]), (0.6, Z)],
                                                                    "left_wing:rot": [(0, Z), (0.06, [0, 0, -70]), (0.2, [0, 0, -20]), (0.35, [0, 0, -60]), (0.6, Z)], "mw_center:pos": [(0, Z), (0.1, move(0, 1.5, 0)), (0.4, Z)]}),
        ("minecraft:rabbit", "rabbit", "Rabbit Panic Leap", {"mw_center:pos": [(0, Z), (0.1, move(0, 3, 1), "out_expo"), (0.4, Z)], "left_haunch:rot": [(0, Z), (0.1, [40, 0, 0]), (0.5, Z)],
                                                            "right_haunch:rot": [(0, Z), (0.1, [40, 0, 0]), (0.5, Z)], "right_ear:rot": [(0, Z), (0.1, [-30, 0, 0]), (0.5, Z)]}),
        ("minecraft:witch", "witch", "Witch Shrieking Recoil", {"head:rot": [(0, Z), (0.08, [-25, 0, 10]), (0.6, Z)], "arms:rot": [(0, Z), (0.1, [-80, 0, 0]), (0.6, Z)], "hat4:rot": [(0, Z), (0.15, [20, 0, 0]), (0.6, Z)]}),
        ("minecraft:piglin_brute", "piglin_brute", "Piglin Brute Stomping Through Pain", {"right_leg:rot": [(0, Z), (0.2, leg('r', 40)), (0.35, leg('r', -6)), (0.7, Z)], "head:rot": [(0, Z), (0.1, [-15, 0, 0]), (0.7, Z)]}),
        ("minecraft:zombie_villager", "zombie_villager", "Zombie Villager Moaning Recoil", {"head:rot": [(0, Z), (0.1, [-20, 0, 15]), (0.8, Z)],
                                                                                         "body:rot": [(0, Z), (0.1, tilt(-10)), (0.8, Z)]}),
        ("minecraft:hoglin", "hoglin", "Hoglin Squealing Buck", {"mw_center:rot": [(0, Z), (0.1, tilt(10, 0, 0)), (0.25, tilt(-8, 0, 0)), (0.6, Z)], "left_hind_leg:rot": [(0, Z), (0.12, [40, 0, 0]), (0.6, Z)],
                                                               "right_hind_leg:rot": [(0, Z), (0.12, [40, 0, 0]), (0.6, Z)]}),
        ("minecraft:horse", "horse", "Horse Collapsing In Death", {"left_front_leg:rot": [(0, Z), (0.4, [-80, 0, 0])], "right_front_leg:rot": [(0, Z), (0.5, [-70, 0, 0])], "head_parts:rot": [(0, Z), (0.8, [40, 0, 0])],
                                                                  "tail:rot": [(0, Z), (0.8, [30, 0, 0])]})):
    is_death = sp == "horse"
    react(sp + (".death_collapse" if is_death else ".hurt_flinch"), label, event("death") if is_death else event("hurt", LIVE), 0.6 if not is_death else 1.2, tracks, target=T, file=FM + "/" + sp,
          pri=300 if is_death else 200, layer="action" if is_death else "reaction")

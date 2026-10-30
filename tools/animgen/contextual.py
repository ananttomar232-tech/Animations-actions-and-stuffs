"""Special, contextual and transition animations (category: contextual_transitions).

Transitions bridge two states (sitting down, rising from rest, weather turning, danger appearing) and
are bound to the primed state-edge events the runtime fires when a sampled condition flips.
"""
from core import arm, leg
from mobkit import mob, life, loop_state, beat, Z, state, event, wave, cwave, tilt, move

CAT = "contextual_transitions"
P = "@player"
LIVE = "!q.is_dead && !q.is_riding && !q.is_sleeping"
GROUND = LIVE + " && q.is_on_ground && !q.is_in_water"
FP, FM = "player/transitions", "mobs/transitions"


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def tr(cid, name, trig, L, tracks, pri=280, layer="gesture", target=P, file=FP, events=()):
    return beat(cid, name, CAT, target, trig, L, file, tracks, pri=pri, layer=layer, events=events)


# ============================================================================ player: idle depth and rest
loop_state("player.afk.sit_ground", "Sitting Down To Wait", CAT, P, GROUND + " && q.ground_speed < 0.01 && q.idle_time > 60 && q.idle_time <= 180 && !q.is_sneaking", 6.0, FP, {
    "mw_root:pos": lambda u: move(0, -10, 0), "right_leg:rot": lambda u: leg('r', 90, 10), "left_leg:rot": lambda u: leg('l', 90, 10), "body:rot": lambda u: tilt(-6 + 2 * wave(u), 0, 0),
    "right_arm:rot": lambda u: arm('r', 40, -10), "left_arm:rot": lambda u: arm('l', 40, -10), "head:rot": lambda u: [5, 25 * wave(u), 0]}, layer="overlay", pri=150)
loop_state("player.afk.lie_back", "Lying Back To Watch The Sky", CAT, P, GROUND + " && q.ground_speed < 0.01 && q.idle_time > 180 && !q.is_sneaking", 8.0, FP, {
    "mw_root:pos": lambda u: move(0, -11, 0), "mw_root:rot": lambda u: tilt(-85, 0, 0), "right_arm:rot": lambda u: arm('r', 170, 20, -30), "left_arm:rot": lambda u: arm('l', 170, 20, -30),
    "right_leg:rot": lambda u: leg('r', 30, 6), "left_leg:rot": lambda u: leg('l', 0, 6), "body:scl": lambda u: [1, 1, 1 + 0.02 * wave(u)]}, layer="overlay", pri=151)
tr("player.afk.stand_up", "Getting Up After A Long Wait", event("start_moving", GROUND + " && q.last_idle > 60"), 1.4, {
    "mw_root:pos": [(0, move(0, -10, 0)), (0.6, move(0, -5, 0), "out_quad"), (1.4, Z)], "right_leg:rot": [(0, leg('r', 90, 10)), (0.6, leg('r', 60)), (1.4, Z)],
    "left_leg:rot": [(0, leg('l', 90, 10)), (0.5, leg('l', 20)), (1.4, Z)], "body:rot": [(0, tilt(-6)), (0.6, tilt(30)), (1.4, Z)], "right_arm:rot": [(0, arm('r', 40)), (0.6, arm('r', 20, 30)), (1.4, Z)]},
   pri=290, layer="action")
tr("player.afk.dust_off", "Dusting Off After Sitting", event("start_moving", GROUND + " && q.last_idle > 20 && q.last_idle <= 60"), 1.2, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', -20, 10, 30)), (0.5, arm('r', -10, 10, 30)), (0.7, arm('r', -20, 10, 30)), (1.2, Z)], "body:rot": [(0, Z), (0.3, tilt(8, -14, 0)), (1.2, Z)],
    "head:rot": [(0, Z), (0.3, [20, -20, 0]), (1.2, Z)]})
loop_state("player.context.body_follow_head", "Body Turning To Follow The Gaze", CAT, P, GROUND + " && q.ground_speed < 0.02 && math.abs(q.head_yaw) > 70", 0.8, FP, {
    "body:rot": lambda u: tilt(0, "q.head_yaw * 0.3", 0), "right_leg:rot": lambda u: [0, "q.head_yaw * 0.2", 0], "left_leg:rot": lambda u: [0, "q.head_yaw * 0.1", 0]},
           layer="additive", pri=60)

# ============================================================================ player: life events
tr("player.life.respawn_rise", "Rising From Respawn", event("respawn:death", "!q.is_dead"), 2.4, {
    "mw_root:pos": [(0, move(0, -10, 0)), (1.0, move(0, -5, 0), "out_quad"), (2.4, Z)], "right_leg:rot": [(0, leg('r', 90)), (1.0, leg('r', 80)), (2.4, Z)],
    "left_leg:rot": [(0, leg('l', 20)), (1.0, leg('l', 30)), (2.4, Z)], "body:rot": [(0, tilt(50)), (1.2, tilt(20)), (2.4, Z)], "head:rot": [(0, [40, 0, 0]), (1.4, [0, 30, 0]), (2.0, [0, -30, 0]), (2.4, Z)],
    "right_arm:rot": [(0, arm('r', 60)), (1.0, arm('r', 30, 20)), (2.4, Z)]}, pri=320, layer="action")
tr("player.life.end_return", "Returning From The End", event("respawn:end", "!q.is_dead"), 3.0, {
    "head:rot": [(0, [-30, 0, 0]), (1.0, [-20, 40, 0]), (2.0, [-10, -40, 0]), (3.0, Z)], "right_arm:rot": [(0, arm('r', 30, 60)), (1.4, arm('r', 120, 0, 20)), (3.0, Z)],
    "body:rot": [(0, tilt(-10)), (3.0, Z)]}, pri=321, layer="action")
tr("player.life.join_arrive", "Arriving In The World", event("join", "!q.is_dead"), 2.6, {
    "head:rot": [(0, Z), (0.7, [-10, 40, 0]), (1.5, [-10, -40, 0]), (2.2, [5, 0, 0]), (2.6, Z)], "right_arm:rot": [(0, Z), (0.9, arm('r', 20, 30)), (1.6, arm('r', 20, 10)), (2.6, Z)],
    "body:rot": [(0, Z), (0.7, tilt(0, 14, 0)), (1.5, tilt(0, -14, 0)), (2.6, Z)]}, pri=310, layer="action")
tr("player.life.enter_nether", "Shielding From Nether Heat", event("dimension_enter:the_nether", "!q.is_dead"), 2.0, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', 120, -10, 20)), (1.4, arm('r', 115, -10, 20)), (2.0, Z)], "head:rot": [(0, Z), (0.3, [15, 0, 0]), (2.0, Z)], "body:rot": [(0, Z), (0.3, tilt(10)), (2.0, Z)]},
   pri=311, layer="action")
tr("player.life.enter_end", "Disoriented Arrival In The End", event("dimension_enter:the_end", "!q.is_dead"), 2.4, {
    "body:rot": [(0, Z), (0.4, tilt(0, 0, 8)), (0.9, tilt(0, 0, -8)), (1.4, tilt(0, 0, 4)), (2.4, Z)], "head:rot": [(0, Z), (0.5, [-30, 0, 0]), (1.5, [-25, 30, 0]), (2.4, Z)],
    "right_arm:rot": [(0, Z), (0.4, arm('r', 20, 50)), (1.4, arm('r', 10, 30)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.4, arm('l', 20, 50)), (1.4, arm('l', 10, 30)), (2.4, Z)]}, pri=312, layer="action")
tr("player.life.home_again", "Relieved To Be Back In The Overworld", event("dimension_enter:overworld", "!q.is_dead"), 2.0, {
    "body:rot": [(0, Z), (0.5, tilt(-10)), (1.2, tilt(6)), (2.0, Z)], "head:rot": [(0, Z), (0.5, [-25, 0, 0]), (2.0, Z)], "right_arm:rot": [(0, Z), (0.5, arm('r', 0, 30)), (2.0, Z)],
    "left_arm:rot": [(0, Z), (0.5, arm('l', 0, 30)), (2.0, Z)]}, pri=313, layer="action", events=[(0.6, "breath", {"strength": "0.8"})])
tr("player.life.bed_climb", "Climbing Into Bed", event("sleep", "!q.is_dead"), 1.2, {
    "right_leg:rot": [(0, leg('r', 60)), (0.6, leg('r', 20)), (1.2, Z)], "right_arm:rot": [(0, arm('r', 60, 20)), (1.2, Z)], "head:rot": [(0, [20, 0, 0]), (1.2, Z)]}, pri=300, layer="action")

# ============================================================================ player: menus
tr("player.menu.open_pack", "Swinging The Pack Round", event("menu_open:inventory", LIVE), 0.7, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', -30, 20, -40)), (0.7, arm('r', 40, 0))], "left_arm:rot": [(0, Z), (0.3, arm('l', 20, 30)), (0.7, arm('l', 40, 0))], "head:rot": [(0, Z), (0.4, [40, 0, 0])],
    "body:rot": [(0, Z), (0.3, tilt(0, -20, 0)), (0.7, tilt(10))]}, pri=285)
tr("player.menu.start_typing", "Raising Hands To Type", event("menu_open:chat", LIVE), 0.5, {
    "right_arm:rot": [(0, Z), (0.5, arm('r', 50, -10, 20))], "left_arm:rot": [(0, Z), (0.5, arm('l', 50, -10, 20))], "head:rot": [(0, Z), (0.5, [30, 0, 0])]}, pri=285)
tr("player.menu.finish_typing", "Lowering Hands After Speaking", event("menu_close:chat", LIVE), 0.6, {
    "right_arm:rot": [(0, arm('r', 50, -10, 20)), (0.6, Z)], "left_arm:rot": [(0, arm('l', 50, -10, 20)), (0.6, Z)], "head:rot": [(0, [30, 0, 0]), (0.3, [-6, 0, 0]), (0.6, Z)]}, pri=285)
tr("player.menu.open_book", "Opening A Book To Write", event("menu_open:book_edit", LIVE), 0.8, {
    "left_arm:rot": [(0, Z), (0.4, arm('l', 60, -14, 20)), (0.8, arm('l', 55, -14, 20))], "right_arm:rot": [(0, Z), (0.5, arm('r', 50, -10, 30)), (0.8, arm('r', 50, -10, 30))], "head:rot": [(0, Z), (0.5, [35, 0, 0])]},
   pri=285)
tr("player.menu.close_book", "Snapping A Book Shut", event("menu_close:book_edit", LIVE), 0.6, {
    "right_arm:rot": [(0, arm('r', 50, -10, 30)), (0.15, arm('r', 60, -20, 30)), (0.6, Z)], "left_arm:rot": [(0, arm('l', 55, -14, 20)), (0.15, arm('l', 60, -20, 20)), (0.6, Z)]}, pri=285)
tr("player.menu.close_pack", "Shrugging The Pack Back On", event("menu_close:inventory", LIVE), 0.7, {
    "right_arm:rot": [(0, arm('r', 40)), (0.35, arm('r', -20, 20, -40)), (0.7, Z)], "body:rot": [(0, tilt(10)), (0.35, tilt(0, 15, 0)), (0.7, Z)], "head:rot": [(0, [40, 0, 0]), (0.7, Z)]}, pri=284)

# ============================================================================ player: world changes
tr("player.world.danger_spotted", "Spotting Danger", event("danger_near", LIVE), 0.9, {
    "head:rot": [(0, Z), (0.1, [-8, 0, 0], "out_expo"), (0.9, Z)], "body:rot": [(0, Z), (0.1, tilt(-6)), (0.4, tilt(8)), (0.9, Z)], "right_arm:rot": [(0, Z), (0.2, arm('r', 30, 15)), (0.9, Z)],
    "left_arm:rot": [(0, Z), (0.2, arm('l', 30, 15)), (0.9, Z)], "right_leg:rot": [(0, Z), (0.2, leg('r', -12)), (0.9, Z)]})
tr("player.world.danger_passed", "Exhaling As Danger Passes", event("danger_clear", LIVE), 1.4, {
    "body:rot": [(0, Z), (0.4, tilt(-8)), (1.0, tilt(10)), (1.4, Z)], "head:rot": [(0, Z), (0.4, [-14, 0, 0]), (1.0, [14, 0, 0]), (1.4, Z)], "right_arm:rot": [(0, Z), (1.0, arm('r', -6, 4)), (1.4, Z)]},
   events=[(0.4, "breath", {"strength": "0.7"})])
tr("player.world.rain_begins", "Feeling The First Raindrops", event("rain_start", LIVE + " && q.sky_exposed"), 2.0, {
    "head:rot": [(0, Z), (0.5, [-40, 0, 0]), (1.5, [-35, 10, 0]), (2.0, Z)], "right_arm:rot": [(0, Z), (0.6, arm('r', 60, 10, -60)), (1.5, arm('r', 60, 10, -60)), (2.0, Z)]})
tr("player.world.rain_ends", "Shaking Off The Last Of The Rain", event("rain_stop", LIVE + " && q.sky_exposed"), 1.2, {
    "head:rot": [(0, Z), (0.1, [0, 0, 18]), (0.2, [0, 0, -18]), (0.3, [0, 0, 12]), (0.5, Z), (1.2, [-25, 0, 0])], "right_arm:rot": [(0, Z), (0.4, arm('r', 10, 40)), (0.6, arm('r', 10, 20)), (1.2, Z)]})
tr("player.world.nightfall", "Noticing Nightfall", event("nightfall", LIVE + " && q.sky_exposed"), 2.2, {
    "head:rot": [(0, Z), (0.6, [-25, 30, 0]), (1.4, [-20, -20, 0]), (2.2, Z)], "body:rot": [(0, Z), (0.8, tilt(4, 0, 0)), (2.2, Z)], "right_arm:rot": [(0, Z), (1.0, arm('r', 20, -10, 30)), (2.2, Z)]})
tr("player.world.sunrise_stretch", "Stretching At Sunrise", event("daybreak", LIVE + " && q.sky_exposed"), 2.6, {
    "right_arm:rot": [(0, Z), (0.8, arm('r', 170, 20)), (1.8, arm('r', 175, 25)), (2.6, Z)], "left_arm:rot": [(0, Z), (0.8, arm('l', 170, 20)), (1.8, arm('l', 175, 25)), (2.6, Z)],
    "body:rot": [(0, Z), (0.8, tilt(-12)), (1.8, tilt(-10, 0, 6)), (2.6, Z)], "head:rot": [(0, Z), (0.8, [-30, 0, 0]), (2.6, Z)]}, pri=281, layer="action")
tr("player.world.into_darkness", "Stepping Into Darkness", event("enter_dark", LIVE), 1.2, {
    "head:rot": [(0, Z), (0.3, [6, 25, 0]), (0.8, [6, -25, 0]), (1.2, Z)], "body:rot": [(0, Z), (0.3, tilt(8)), (1.2, Z)], "right_arm:rot": [(0, Z), (0.4, arm('r', 40, 20)), (1.2, Z)]})
tr("player.world.into_light", "Squinting Into The Light", event("exit_dark", LIVE), 1.0, {
    "right_arm:rot": [(0, Z), (0.2, arm('r', 120, -10, 30)), (0.7, arm('r', 115, -10, 30)), (1.0, Z)], "head:rot": [(0, Z), (0.2, [14, 0, 0]), (1.0, Z)]})
tr("player.world.wounded", "Clutching A Wound", event("wounded", LIVE), 1.6, {
    "left_arm:rot": [(0, Z), (0.3, arm('l', 40, -20, 40)), (1.2, arm('l', 35, -20, 40)), (1.6, Z)], "body:rot": [(0, Z), (0.3, tilt(18, 0, 6)), (1.2, tilt(12, 0, 4)), (1.6, Z)],
    "head:rot": [(0, Z), (0.3, [25, 0, 0]), (1.6, Z)]})
tr("player.world.recovered", "Straightening Up, Healed", event("recovered", LIVE), 1.4, {
    "body:rot": [(0, tilt(12)), (0.6, tilt(-10)), (1.4, Z)], "right_arm:rot": [(0, Z), (0.6, arm('r', 30, 40)), (1.4, Z)], "left_arm:rot": [(0, Z), (0.6, arm('l', 30, 40)), (1.4, Z)],
    "head:rot": [(0, [20, 0, 0]), (0.6, [-15, 0, 0]), (1.4, Z)]})
tr("player.world.hungry", "Stomach Growling", event("hungry", LIVE), 1.2, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', 30, -20, 40)), (0.9, arm('r', 30, -20, 40)), (1.2, Z)], "body:rot": [(0, Z), (0.3, tilt(14)), (0.9, tilt(10)), (1.2, Z)], "head:rot": [(0, Z), (0.3, [30, 0, 0]), (1.2, Z)]})
tr("player.world.ledge_teeter", "Teetering At A Ledge", event("ledge_reached", GROUND + " && !q.is_sneaking && q.ground_speed > 0.05"), 1.2, {
    "right_arm:rot": [(0, Z), (0.2, arm('r', 120, 60)), (0.4, arm('r', 40, 80)), (0.6, arm('r', 120, 60)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.2, arm('l', 40, 80)), (0.4, arm('l', 120, 60)), (0.6, arm('l', 40, 80)), (1.2, Z)],
    "body:rot": [(0, Z), (0.2, tilt(-14)), (0.5, tilt(-6)), (1.2, Z)]}, pri=295, layer="action")
loop_state("player.world.ledge_peek", "Peering Over The Edge", CAT, P, GROUND + " && q.at_ledge && q.is_sneaking && q.ground_speed < 0.01", 2.4, FP, {
    "body:rot": lambda u: tilt(26, 0, 0), "head:rot": lambda u: [40, 15 * wave(u, 0, 0.5), 0], "right_arm:rot": lambda u: arm('r', 20, 30), "left_arm:rot": lambda u: arm('l', 20, 30)}, pri=245)
tr("player.world.step_back_from_ledge", "Stepping Back From The Edge", event("ledge_left", GROUND + " && q.forward_speed < 0"), 0.8, {
    "body:rot": [(0, tilt(10)), (0.3, tilt(-10)), (0.8, Z)], "right_arm:rot": [(0, Z), (0.3, arm('r', 20, 30)), (0.8, Z)], "head:rot": [(0, [20, 0, 0]), (0.8, Z)]})
tr("player.combat.ready_up", "Snapping To Readiness", event("combat_enter", LIVE), 0.6, {
    "body:rot": [(0, Z), (0.15, tilt(8, -10, 0), "out_quad"), (0.6, tilt(4, -6, 0))], "right_leg:rot": [(0, Z), (0.15, leg('r', -10, 6)), (0.6, leg('r', -8, 6))], "left_leg:rot": [(0, Z), (0.15, leg('l', 14, 6)), (0.6, leg('l', 10, 6))]})
tr("player.combat.stand_down", "Standing Down After A Fight", event("combat_exit", LIVE), 1.6, {
    "body:rot": [(0, tilt(4, -6, 0)), (0.6, tilt(-6)), (1.6, Z)], "head:rot": [(0, Z), (0.6, [-10, 0, 0]), (1.0, [5, 30, 0]), (1.6, Z)], "right_arm:rot": [(0, Z), (0.8, arm('r', -10, 10)), (1.6, Z)]},
   events=[(0.6, "breath", {"strength": "0.9"})])
tr("player.move.stop_and_look", "Stopping To Take In The View", event("stop_moving", GROUND + " && q.trait_curiosity > 0.7 && q.move_time > 0"), 2.4, {
    "head:rot": [(0, Z), (0.6, [-15, 35, 0]), (1.4, [-15, -30, 0]), (2.4, Z)], "body:rot": [(0, Z), (0.6, tilt(0, 10, 0)), (1.4, tilt(0, -10, 0)), (2.4, Z)], "right_arm:rot": [(0, Z), (1.0, arm('r', -20, -6, -30)), (2.4, Z)]},
   pri=279)
tr("player.move.backward_start", "Backing Away", event("start_moving", GROUND + " && q.forward_speed < -0.02"), 0.6, {
    "body:rot": [(0, Z), (0.2, tilt(-8)), (0.6, Z)], "right_arm:rot": [(0, Z), (0.2, arm('r', 30, 20)), (0.6, Z)], "left_arm:rot": [(0, Z), (0.2, arm('l', 30, 20)), (0.6, Z)], "head:rot": [(0, Z), (0.2, [6, 0, 0]), (0.6, Z)]})
tr("player.move.portal_step", "Steeling Yourself At A Portal", event("start_moving", GROUND + " && q.feet_block == 'portal'"), 1.2, {
    "body:rot": [(0, Z), (0.4, tilt(-6, 0, 0)), (1.2, Z)], "head:rot": [(0, Z), (0.4, [-14, 0, 0]), (1.2, Z)], "right_arm:rot": [(0, Z), (0.4, arm('r', 10, 30)), (1.2, Z)]})
loop_state("player.world.portal_nausea", "Swaying In A Nether Portal", CAT, P, LIVE + " && q.feet_block == 'portal'", 2.0, FP, {
    "body:rot": lambda u: tilt(4 * wave(u, 0.25), 0, 6 * wave(u)), "head:rot": lambda u: [10, 0, 8 * wave(u, 0.1)], "right_arm:rot": lambda u: arm('r', 10, 20 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', 10, 20 + 10 * wave(u, 0.5))},
           layer="additive", pri=99)
tr("player.trade.open", "Leaning In To Trade", event("trade_open", LIVE), 0.8, {"body:rot": [(0, Z), (0.4, tilt(12)), (0.8, tilt(8))], "head:rot": [(0, Z), (0.4, [14, 0, 0])]})

# ============================================================================ mobs: posture changes
tr("wolf.sit_down", "Wolf Sitting Down", event("sit_down", "!q.is_dead"), 0.6, {
    "left_hind_leg:rot": [(0, Z), (0.4, [60, 0, 0], "in_out_sine"), (0.6, [55, 0, 0])], "right_hind_leg:rot": [(0, Z), (0.45, [60, 0, 0], "in_out_sine"), (0.6, [55, 0, 0])],
    "mw_center:rot": [(0, Z), (0.4, tilt(-12, 0, 0)), (0.6, tilt(-10, 0, 0))], "tail:rot": [(0, Z), (0.5, [30, 0, 0])]}, target="minecraft:wolf", file=FM + "/wolf", layer="action", pri=150)
tr("wolf.stand_up", "Wolf Standing Up Eagerly", event("stand_up", "!q.is_dead"), 0.5, {
    "mw_center:rot": [(0, tilt(-10, 0, 0)), (0.2, tilt(6, 0, 0)), (0.5, Z)], "mw_center:pos": [(0, Z), (0.2, move(0, 0.6, 0)), (0.5, Z)], "tail:rot": [(0, Z), (0.3, [0, 30, 0]), (0.5, Z)]},
   target="minecraft:wolf", file=FM + "/wolf", layer="action", pri=150)
tr("wolf.hackles_rise", "Wolf's Hackles Rising", event("anger", "!q.is_dead"), 0.8, {
    "upper_body:scl": [(0, [1, 1, 1]), (0.3, [1.12, 1.15, 1.0], "out_quad"), (0.8, [1.08, 1.12, 1.0])], "head:rot": [(0, Z), (0.3, [16, 0, 0])], "tail:rot": [(0, Z), (0.3, [-25, 0, 0])]},
   target="minecraft:wolf", file=FM + "/wolf", pri=155)
tr("wolf.calm_down", "Wolf Calming Down", event("calm", "!q.is_dead"), 1.0, {"head:rot": [(0, [16, 0, 0]), (0.5, [-6, 0, 6]), (1.0, Z)], "tail:rot": [(0, [-25, 0, 0]), (0.6, [0, 20, 0]), (1.0, Z)]},
   target="minecraft:wolf", file=FM + "/wolf", pri=155)
tr("cat.sit_down", "Cat Settling Onto Its Haunches", event("sit_down", "!q.is_dead"), 0.7, {
    "left_hind_leg:rot": [(0, Z), (0.5, [70, 0, 0], "in_out_sine")], "right_hind_leg:rot": [(0, Z), (0.55, [70, 0, 0], "in_out_sine")], "tail1:rot": [(0, Z), (0.6, [40, -30, 0])],
    "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (0.7, Z)]}, target="minecraft:cat", file=FM + "/cat", layer="action", pri=150)
tr("cat.stand_up", "Cat Rising And Stretching", event("stand_up", "!q.is_dead"), 1.2, {
    "left_front_leg:rot": [(0, Z), (0.4, [-50, 0, 0]), (1.2, Z)], "right_front_leg:rot": [(0, Z), (0.4, [-50, 0, 0]), (1.2, Z)], "mw_center:rot": [(0, Z), (0.4, tilt(12, 0, 0)), (1.2, Z)],
    "tail1:rot": [(0, Z), (0.5, [-40, 0, 0]), (1.2, Z)]}, target="minecraft:cat", file=FM + "/cat", layer="action", pri=150)
tr("cat.lie_down", "Cat Flopping Onto Its Side", event("lie_down", "!q.is_dead"), 0.8, {"mw_center:rot": [(0, Z), (0.5, tilt(0, 0, 40), "in_quad"), (0.8, tilt(0, 0, 35))],
                                                                                       "head:rot": [(0, Z), (0.6, [0, 0, -20])]}, target="minecraft:cat", file=FM + "/cat", layer="action", pri=150)
tr("cat.get_up", "Cat Getting Up From A Nap", event("get_up", "!q.is_dead"), 1.0, {
    "mw_center:rot": [(0, tilt(0, 0, 35)), (0.4, tilt(0, 0, -6)), (1.0, Z)], "head:rot": [(0, Z), (0.3, [0, 0, 20]), (0.5, [0, 0, -20]), (0.7, Z)], "tail2:rot": [(0, Z), (0.5, [0, 40, 0]), (1.0, Z)]},
   target="minecraft:cat", file=FM + "/cat", layer="action", pri=150)
tr("fox.sit_down", "Fox Curling Its Tail To Sit", event("sit_down", "!q.is_dead"), 0.6, {"tail:rot": [(0, Z), (0.6, [0, -50, 0])], "left_hind_leg:rot": [(0, Z), (0.4, [50, 0, 0])],
                                                                                     "right_hind_leg:rot": [(0, Z), (0.4, [50, 0, 0])]}, target="minecraft:fox", file=FM + "/fox", layer="action", pri=150)
tr("fox.wake_shake", "Fox Shaking Off Sleep", event("wake", "!q.is_dead"), 1.0, {
    "head:rot": [(0, Z), (0.15, [0, 0, 25]), (0.3, [0, 0, -25]), (0.45, [0, 0, 15]), (0.7, Z)], "mw_center:rot": [(0, Z), (0.2, tilt(0, 0, 8)), (0.35, tilt(0, 0, -8)), (0.7, Z)],
    "right_ear:rot": [(0, Z), (0.2, [0, 0, 30]), (0.7, Z)]}, target="minecraft:fox", file=FM + "/fox", pri=150)
tr("panda.flop_sit", "Panda Flopping Down To Sit", event("sit_down", "!q.is_dead"), 0.8, {"mw_center:pos": [(0, Z), (0.3, move(0, -3, 0), "in_quad"), (0.5, move(0, -2.5, 0)), (0.8, move(0, -2.6, 0))],
                                                                                      "head:rot": [(0, Z), (0.3, [20, 0, 0]), (0.8, Z)]}, target="minecraft:panda", file=FM + "/panda", pri=150)
tr("panda.heave_up", "Panda Heaving Itself Up", event("stand_up", "!q.is_dead"), 1.2, {"mw_center:rot": [(0, tilt(-20, 0, 0)), (0.6, tilt(10, 0, 6)), (1.2, Z)],
                                                                                     "left_front_leg:rot": [(0, Z), (0.5, [-40, 0, 0]), (1.2, Z)]}, target="minecraft:panda", file=FM + "/panda", pri=150)
tr("camel.kneel_flourish", "Camel Folding Down With A Grumble", event("sit_down", "!q.is_dead"), 1.6, {"head:rot": [(0, Z), (0.5, [-25, 0, 0]), (1.2, [10, 0, 0]), (1.6, Z)],
                                                                                                  "tail:rot": [(0, Z), (0.8, [0, 30, 0]), (1.6, Z)]}, target="minecraft:camel", file=FM + "/camel", pri=150)
tr("camel.rise_flourish", "Camel Rising With A Head Toss", event("stand_up", "!q.is_dead"), 1.6, {"head:rot": [(0, Z), (0.8, [20, 0, 0]), (1.2, [-20, 0, 0]), (1.6, Z)],
                                                                                              "hump:rot": [(0, Z), (1.0, [6, 0, 0]), (1.6, Z)]}, target="minecraft:camel", file=FM + "/camel", pri=150)
tr("polar_bear.rear_start", "Polar Bear Rising Onto Its Hind Legs", event("rear_up", "!q.is_dead"), 0.6, {"head:rot": [(0, Z), (0.3, [-30, 0, 0]), (0.6, [-10, 0, 0])],
                                                                                                       "left_front_leg:rot": [(0, Z), (0.3, [-40, 0, -14])], "right_front_leg:rot": [(0, Z), (0.3, [-40, 0, 14])]},
   target="minecraft:polar_bear", file=FM + "/polar_bear", pri=150)
tr("polar_bear.rear_end", "Polar Bear Dropping Back To All Fours", event("rear_down", "!q.is_dead"), 0.6, {"mw_center:pos": [(0, Z), (0.15, move(0, -1.2, 0), "out_expo"), (0.6, Z)],
                                                                                                        "head:rot": [(0, Z), (0.15, [20, 0, 0]), (0.6, Z)]}, target="minecraft:polar_bear", file=FM + "/polar_bear", pri=150,
   events=[(0.15, "stomp", {"strength": "0.6"})])
tr("horse.rear_start", "Horse Rearing Up", event("rear_up", "!q.is_dead"), 0.7, {"head_parts:rot": [(0, Z), (0.35, [-30, 0, 0])], "tail:rot": [(0, Z), (0.35, [-40, 0, 0])]},
   target="minecraft:horse", file=FM + "/horse", pri=150)
tr("horse.rear_end", "Horse Coming Down From A Rear", event("rear_down", "!q.is_dead"), 0.7, {"mw_center:pos": [(0, Z), (0.15, move(0, -1, 0), "out_expo"), (0.7, Z)], "head_parts:rot": [(0, Z), (0.2, [25, 0, 0]), (0.7, Z)]},
   target="minecraft:horse", file=FM + "/horse", pri=150, events=[(0.15, "stomp", {"strength": "0.7"})])
tr("sheep.graze_dip", "Sheep Dipping Down To Graze", event("eat_start", "!q.is_dead"), 0.5, {"mw_center:pos": [(0, Z), (0.25, move(0, -0.6, 0.6)), (0.5, move(0, 0, 0.5))]},
   target="minecraft:sheep", file=FM + "/sheep", pri=150)
tr("sheep.graze_rise", "Sheep Lifting Its Head From Grazing", event("eat_stop", "!q.is_dead"), 0.8, {"head:rot": [(0, [60, 0, 0]), (0.4, [-14, 0, 0]), (0.8, Z)], "mw_center:pos": [(0, move(0, 0, 0.5)), (0.8, Z)]},
   target="minecraft:sheep", file=FM + "/sheep", pri=150)
tr("horse.graze_rise", "Horse Lifting Its Head, Chewing", event("eat_stop", "!q.is_dead"), 1.2, {"head_parts:rot": [(0, [70, 0, 0]), (0.5, [-10, 0, 0]), (1.2, Z)], "upper_mouth:rot": [(0.5, Z), (0.7, [10, 0, 0]), (0.9, Z), (1.1, [10, 0, 0]), (1.2, Z)]},
   target="minecraft:horse", file=FM + "/horse", pri=150)
tr("enderman.provoked", "Enderman Provoked", event("anger", "!q.is_dead"), 0.6, {"head:rot": [(0, Z), (0.1, [-14, 0, 0], "out_expo"), (0.6, Z)], "body:rot": [(0, Z), (0.1, tilt(-8)), (0.6, Z)]},
   target="minecraft:enderman", file=FM + "/enderman", pri=160)
tr("bee.provoked", "Bee Turning Angry", event("anger", "!q.is_dead"), 0.5, {"bone:rot": [(0, Z), (0.1, tilt(0, 0, 30)), (0.2, tilt(0, 0, -30)), (0.5, tilt(22, 0, 0))]}, target="minecraft:bee", file=FM + "/bee", pri=160)
tr("bee.calm_down", "Bee Calming Down", event("calm", "!q.is_dead"), 0.8, {"bone:rot": [(0, tilt(22, 0, 0)), (0.8, Z)], "left_antenna:rot": [(0, [-30, 0, 0]), (0.8, Z)], "right_antenna:rot": [(0, [-30, 0, 0]), (0.8, Z)]},
   target="minecraft:bee", file=FM + "/bee", pri=160)
tr("iron_golem.provoked", "Iron Golem Turning Hostile", event("anger", "!q.is_dead"), 0.9, {"head:rot": [(0, Z), (0.3, [14, 0, 0])], "right_arm:rot": [(0, Z), (0.3, arm('r', 20, 10))],
                                                                                          "left_arm:rot": [(0, Z), (0.3, arm('l', 20, 10))], "body:rot": [(0, Z), (0.3, tilt(8))]}, target="minecraft:iron_golem", file=FM + "/iron_golem", pri=160)
tr("piglin.spot_gold", "Piglin Spotting Gold", event("admire_start", "!q.is_dead"), 0.6, {"head:rot": [(0, Z), (0.15, [20, 0, 0], "out_back")], "body:rot": [(0, Z), (0.2, tilt(10))]},
   target="minecraft:piglin", file=FM + "/piglin", pri=160)
tr("piglin.gold_verdict", "Piglin Finishing Its Appraisal", event("admire_stop", "!q.is_dead"), 1.0, {"head:rot": [(0, [30, -20, 0]), (0.5, [-10, 0, 0]), (1.0, Z)], "left_arm:rot": [(0, arm('l', 70, 20)), (1.0, Z)]},
   target="minecraft:piglin", file=FM + "/piglin", pri=160)
tr("villager.trade_greeting", "Villager Opening Its Wares", event("trade_open", "!q.is_dead"), 1.0, {"arms:rot": [(0, Z), (0.4, [-50, 0, 0], "out_back"), (1.0, [-20, 0, 0])], "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (1.0, Z)]},
   target="minecraft:villager", file=FM + "/villager", pri=160)
tr("villager.trade_farewell", "Villager Nodding Farewell", event("trade_close", "!q.is_dead"), 1.0, {"head:rot": [(0, Z), (0.3, [20, 0, 0]), (0.6, Z)], "arms:rot": [(0, [-20, 0, 0]), (1.0, Z)]},
   target="minecraft:villager", file=FM + "/villager", pri=160)
tr("goat.ram_release", "Goat Shaking Its Head After A Ram", event("stop_moving", "!q.is_dead && q.is_ramming == 0 && q.recent_hurt > 1 && q.move_time > 0 && q.trait_energy > 0.5", chance=0.3), 0.8, {
    "head:rot": [(0, Z), (0.1, [0, 0, 20]), (0.25, [0, 0, -20]), (0.4, [0, 0, 10]), (0.8, Z)]}, target="minecraft:goat", file=FM + "/goat", pri=150)

# ============================================================================ mobs: rising from rest, growing up
RISE = {
    "cow": ("Cow Heaving Up Hind-First", {"left_hind_leg:rot": [(0, [80, 0, 0]), (0.5, Z)], "right_hind_leg:rot": [(0, [80, 0, 0]), (0.55, Z)], "left_front_leg:rot": [(0, [-85, 0, 0]), (0.6, [-85, 0, 0]), (1.2, Z)],
                                          "right_front_leg:rot": [(0, [-85, 0, 0]), (0.65, [-85, 0, 0]), (1.2, Z)], "mw_center:pos": [(0, move(0, -7.5, 0)), (0.6, move(0, -4, 0)), (1.2, Z)],
                                          "mw_center:rot": [(0, Z), (0.6, tilt(16, 0, 0)), (1.2, Z)]}, 1.2),
    "sheep": ("Sheep Springing Up From Rest", {"left_front_leg:rot": [(0, [-35, 0, -20]), (0.3, Z)], "right_front_leg:rot": [(0, [-85, 0, 0]), (0.35, Z)], "left_hind_leg:rot": [(0, [40, 0, -45]), (0.4, Z)],
                                               "right_hind_leg:rot": [(0, [75, 0, -30]), (0.4, Z)], "mw_center:pos": [(0, move(0, -6, 0)), (0.3, move(0, 0.6, 0)), (0.6, Z)]}, 0.6),
    "pig": ("Pig Rolling Back To Its Feet", {"mw_center:rot": [(0, tilt(0, 0, 82)), (0.5, tilt(0, 0, -6)), (0.9, Z)], "mw_center:pos": [(0, move(0, -4.5, 0)), (0.5, Z)]}, 0.9),
    "llama": ("Llama Unfolding From A Kneel", {"left_front_leg:rot": [(0, [-95, 0, 0]), (0.8, Z)], "right_front_leg:rot": [(0, [-95, 0, 0]), (0.85, Z)], "left_hind_leg:rot": [(0, [100, 0, 0]), (0.4, Z)],
                                               "right_hind_leg:rot": [(0, [100, 0, 0]), (0.45, Z)], "mw_center:pos": [(0, move(0, -8, 0)), (0.45, move(0, -4, 0)), (1.0, Z)], "head:rot": [(0, Z), (0.5, [-20, 0, 0]), (1.0, Z)]}, 1.0),
    "mooshroom": ("Mooshroom Lurching Upright", {"mw_center:rot": [(0, tilt(0, 0, 14)), (0.5, tilt(10, 0, -4)), (1.0, Z)], "mw_center:pos": [(0, move(0, -6.5, 0)), (1.0, Z)]}, 1.0),
    "wolf": ("Wolf Uncurling From Sleep", {"mw_center:pos": [(0, move(0, -4.5, 0)), (0.4, Z)], "head:rot": [(0, [30, -50, 10]), (0.4, [-10, 0, 0]), (0.8, Z)], "tail:rot": [(0, [20, -60, 0]), (0.6, Z)]}, 0.8),
    "cat": ("Cat Rising From A Loaf", {"mw_center:pos": [(0, move(0, -3.2, 0)), (0.5, Z)], "left_front_leg:rot": [(0, [-80, 0, 0]), (0.4, Z)], "right_front_leg:rot": [(0, [-80, 0, 0]), (0.45, Z)]}, 0.6),
    "panda": ("Lazy Panda Reluctantly Rising", {"mw_center:pos": [(0, move(0, -7, 0)), (1.0, move(0, -5, 0)), (1.8, Z)], "head:rot": [(0, [28, 0, 10]), (0.8, [20, 20, 0]), (1.8, Z)]}, 1.8),
    "polar_bear": ("Polar Bear Rocking Up From Sitting", {"mw_center:rot": [(0, tilt(-35, 0, 0)), (0.5, tilt(10, 0, 0)), (1.0, Z)], "mw_center:pos": [(0, move(0, -5, 2)), (0.6, Z)]}, 1.0),
    "chicken": ("Chicken Popping Up From A Dust Bath", {"mw_center:pos": [(0, move(0, -2.5, 0)), (0.2, move(0, 0.8, 0)), (0.4, Z)], "right_wing:rot": [(0, Z), (0.2, [0, 0, 70]), (0.5, Z)],
                                                        "left_wing:rot": [(0, Z), (0.2, [0, 0, -70]), (0.5, Z)]}, 0.5),
}
for sp, (name, tracks, L) in RISE.items():
    tr(sp + ".rise_from_rest", name, event("start_moving", "!q.is_dead && q.last_idle > 18"), L, tracks, target="minecraft:" + sp, file=FM + "/" + sp, layer="action", pri=140)
GROW = {
    "cow": ("Calf Growing Into A Cow", {"head:rot": [(0, Z), (0.6, [-20, 0, 0]), (1.4, Z)], "mw_center:rot": [(0, Z), (0.3, tilt(0, 0, 6)), (0.6, tilt(0, 0, -6)), (1.0, Z)]}),
    "sheep": ("Lamb Shaking Into Adulthood", {"mw_center:rot": [(0, Z), (0.15, tilt(0, 0, 10)), (0.3, tilt(0, 0, -10)), (0.45, tilt(0, 0, 6)), (1.0, Z)], "head:rot": [(0, Z), (0.6, [-25, 0, 0]), (1.4, Z)]}),
    "pig": ("Piglet Puffing Up Proud", {"mw_center:pos": [(0, Z), (0.4, move(0, 1, 0)), (1.0, Z)], "head:rot": [(0, Z), (0.4, [-18, 0, 0]), (1.4, Z)]}),
    "wolf": ("Pup Coming Of Age", {"head:rot": [(0, Z), (0.5, [-40, 0, 0]), (1.0, [-35, 0, 0]), (1.4, Z)], "tail:rot": [(0, Z), (0.5, [-30, 0, 0]), (1.4, Z)]}),
    "chicken": ("Chick Ruffling Into A Hen", {"right_wing:rot": [(0, Z), (0.2, [0, 0, 80]), (0.4, [0, 0, 20]), (0.6, [0, 0, 80]), (1.4, Z)], "left_wing:rot": [(0, Z), (0.2, [0, 0, -80]), (0.4, [0, 0, -20]), (0.6, [0, 0, -80]), (1.4, Z)]}),
    "villager": ("Village Child Growing Up", {"arms:rot": [(0, Z), (0.5, [-140, 0, 0]), (1.0, [-140, 0, 0]), (1.4, Z)], "head:rot": [(0, Z), (0.5, [-20, 0, 0]), (1.4, Z)]}),
    "horse": ("Foal Rising Into A Horse", {"head_parts:rot": [(0, Z), (0.6, [-30, 0, 0]), (1.4, Z)], "tail:rot": [(0, Z), (0.6, [-40, 0, 0]), (1.4, Z)]}),
    "fox": ("Kit Growing Into A Fox", {"tail:rot": [(0, Z), (0.5, [-30, 30, 0]), (1.0, [-30, -30, 0]), (1.4, Z)], "head:rot": [(0, Z), (0.5, [0, 0, 20]), (1.4, Z)]}),
}
for sp, (name, tracks) in GROW.items():
    tr(sp + ".grow_up", name, event("grow_up", "!q.is_dead"), 1.4, tracks, target="minecraft:" + sp, file=FM + "/" + sp, pri=160)

# ============================================================================ more transitions
tr("player.world.sated", "Patting A Full Stomach", event("sated", LIVE), 1.4, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', 30, -20, 40)), (0.5, arm('r', 34, -20, 40)), (0.7, arm('r', 30, -20, 40)), (1.4, Z)], "body:rot": [(0, Z), (0.4, tilt(-8)), (1.4, Z)], "head:rot": [(0, Z), (0.4, [-10, 0, 0]), (1.4, Z)]})
tr("player.move.sprint_to_crouch", "Dropping From A Sprint Into A Crouch", event("sneak_start", GROUND + " && q.ground_speed > 0.15"), 0.6, {
    "body:rot": [(0, tilt(14)), (0.15, tilt(-10), "out_expo"), (0.6, tilt(10))], "right_leg:rot": [(0, Z), (0.15, leg('r', -30)), (0.6, leg('r', 20))], "left_leg:rot": [(0, Z), (0.15, leg('l', 40)), (0.6, leg('l', 30))],
    "right_arm:rot": [(0, Z), (0.15, arm('r', 30, 40)), (0.6, arm('r', 10, 10))]}, pri=296, layer="action")
tr("player.move.turn_and_go", "Turning On The Spot And Setting Off", event("start_moving", GROUND + " && math.abs(q.head_yaw) > 90"), 0.7, {
    "body:rot": [(0, tilt(0, "q.head_yaw * 0.5", 0)), (0.4, Z)], "right_leg:rot": [(0, Z), (0.2, leg('r', 20, 10)), (0.5, Z)], "head:rot": [(0, Z), (0.3, [6, 0, 0]), (0.7, Z)]})
tr("player.world.ledge_inch", "Inching Up To An Edge", event("ledge_reached", GROUND + " && q.is_sneaking"), 1.0, {
    "right_leg:rot": [(0, Z), (0.3, leg('r', -20)), (0.6, leg('r', -10)), (1.0, Z)], "right_arm:rot": [(0, Z), (0.4, arm('r', 20, 40)), (1.0, arm('r', 20, 30))], "head:rot": [(0, Z), (0.5, [35, 0, 0])]})
tr("player.transition.fight_begins_bow", "Nocking Ready As A Fight Begins", event("combat_enter", LIVE + " && q.main_hand == 'bow'"), 0.8, {
    "left_arm:rot": [(0, Z), (0.3, arm('l', 50, 10, -20)), (0.8, arm('l', 40, 10))], "right_arm:rot": [(0, Z), (0.3, arm('r', 60, -20, 30)), (0.8, arm('r', 30, 0))], "body:rot": [(0, Z), (0.3, tilt(0, -20, 0)), (0.8, tilt(0, -10, 0))]},
   pri=297)
tr("player.transition.fight_begins_shield", "Bringing The Shield Up As A Fight Begins", event("combat_enter", LIVE + " && q.off_hand == 'shield'"), 0.7, {
    "left_arm:rot": [(0, Z), (0.25, arm('l', 60, -10, -20), "out_back"), (0.7, arm('l', 30, 0))], "body:rot": [(0, Z), (0.25, tilt(6, 10, 0)), (0.7, Z)]}, pri=297)
tr("fox.stand_up", "Fox Uncurling Its Tail To Stand", event("stand_up", "!q.is_dead"), 0.6, {"tail:rot": [(0, [0, -50, 0]), (0.6, Z)], "mw_center:pos": [(0, Z), (0.3, move(0, 0.5, 0)), (0.6, Z)]},
   target="minecraft:fox", file=FM + "/fox", layer="action", pri=150)
tr("axolotl.collapse", "Axolotl Feigning Death", event("play_dead", "!q.is_dead"), 0.8, {"mw_center:rot": [(0, Z), (0.6, tilt(0, 0, 170), "in_quad")], "tail:rot": [(0, Z), (0.3, [0, 30, 0]), (0.8, Z)]},
   target="minecraft:axolotl", file=FM + "/axolotl", layer="action", pri=170)
tr("axolotl.revive", "Axolotl Springing Back To Life", event("revive", "!q.is_dead"), 0.6, {"mw_center:rot": [(0, tilt(0, 0, 170)), (0.3, tilt(0, 0, -10), "out_back"), (0.6, Z)],
                                                                                         "top_gills:rot": [(0, Z), (0.3, [-30, 0, 0]), (0.6, Z)]}, target="minecraft:axolotl", file=FM + "/axolotl", layer="action", pri=170)
tr("sniffer.dig_start", "Sniffer Lowering Its Nose To Dig", event("dig_start", "!q.is_dead"), 1.0, {"head:rot": [(0, Z), (0.6, [55, 0, 0], "in_out_sine")], "mw_center:rot": [(0, Z), (0.6, tilt(10, 0, 0))]},
   target="minecraft:sniffer", file=FM + "/sniffer", layer="action", pri=160)
tr("sniffer.dig_finish", "Sniffer Unearthing A Seed", event("dig_end", "!q.is_dead"), 1.4, {"head:rot": [(0, [55, 0, 0]), (0.5, [-20, 0, 0], "out_back"), (1.4, Z)], "lower_beak:rot": [(0, Z), (0.5, [20, 0, 0]), (1.4, Z)],
                                                                                         "mw_center:pos": [(0, Z), (0.5, move(0, 1, 0)), (1.4, Z)]}, target="minecraft:sniffer", file=FM + "/sniffer", layer="action", pri=160)
tr("turtle.leave_nest", "Turtle Patting Down Its Nest", event("lay_end", "!q.is_dead"), 1.6, {"left_hind_leg:rot": [(0, Z), (0.4, [0, 0, -30]), (0.8, Z), (1.2, [0, 0, -30]), (1.6, Z)],
                                                                                           "right_hind_leg:rot": [(0, Z), (0.4, [0, 0, 30]), (0.8, Z), (1.2, [0, 0, 30]), (1.6, Z)]},
   target="minecraft:turtle", file=FM + "/turtle", pri=160)
tr("ravager.shake_off_stun", "Ravager Shaking Off A Stun", event("unstunned", "!q.is_dead"), 1.0, {"neck:rot": [(0, Z), (0.15, [0, 0, 20]), (0.3, [0, 0, -20]), (0.45, [0, 0, 12]), (1.0, Z)],
                                                                                                "head:rot": [(0, Z), (0.5, [-20, 0, 0]), (1.0, Z)]}, target="minecraft:ravager", file=FM + "/ravager", pri=160)
tr("creeper.fuse_lit", "Creeper Fuse Catching", event("charge_start", "!q.is_dead"), 0.4, {"mw_center:pos": [(0, Z), (0.1, move(0, -1, 0), "out_expo"), (0.4, Z)],
                                                                                        "head:rot": [(0, Z), (0.1, [10, 0, 0]), (0.4, Z)]}, target="minecraft:creeper", file=FM + "/creeper", pri=170)
tr("creeper.fuse_out", "Creeper Fuse Fizzling Out", event("charge_stop", "!q.is_dead"), 0.8, {"body:scl": [(0, [1.08, 1.08, 1.08]), (0.4, [0.96, 0.96, 0.96]), (0.8, [1, 1, 1])],
                                                                                           "head:rot": [(0, Z), (0.3, [0, 15, 0]), (0.6, [0, -10, 0]), (0.8, Z)]}, target="minecraft:creeper", file=FM + "/creeper", pri=170)

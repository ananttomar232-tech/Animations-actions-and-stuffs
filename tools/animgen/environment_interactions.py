"""Environmental interactions (category: environmental_interactions).

How players and creatures react to the world around them: what they stand in (q.feet_block,
q.surface), weather (rain, snow, storms, the positional "thunderclap" world event), explosions heard from afar (the "explosion" world event), temperature,
light, wind, fire, altitude and status effects. Foliage sway, wind and banners are handled by the
shader/wind systems; these clips are the bodies responding to the same conditions.
"""
from core import arm, leg
from mobkit import mob, life, loop_state, beat, Z, state, event, wave, cwave, tilt, move

CAT = "environmental_interactions"
P = "@player"
LIVE = "!q.is_dead && !q.is_riding && !q.is_sleeping"
GROUND = LIVE + " && q.is_on_ground && !q.is_in_water"
STILL = GROUND + " && q.ground_speed < 0.01"
MOVING = GROUND + " && q.ground_speed >= 0.01"
SKY = " && q.sky_exposed"
FP, FM = "environment/player", "environment/mobs"


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def penv(cid, name, when, L, fns, pri=230, layer="overlay", group=None, weight=1):
    return loop_state("player.env." + cid, name, CAT, P, when, L, FP, fns, pri=pri, layer=layer, group=group, weight=weight)


def pev(cid, name, trig, L, tracks, pri=285, layer="gesture", events=()):
    return beat("player.env." + cid, name, CAT, P, trig, L, FP, tracks, pri=pri, layer=layer, events=events)


def menv(T, cid, name, when, L, fns, pri=118, layer="overlay"):
    sp = T.split(":")[1]
    return loop_state(sp + ".env_" + cid, name, CAT, T, "!q.is_dead && " + when, L, FM + "/" + sp, fns, pri=pri, layer=layer)


def mev(T, cid, name, trig, L, tracks, pri=165, layer="gesture", events=()):
    sp = T.split(":")[1]
    return beat(sp + ".env_" + cid, name, CAT, T, trig, L, FM + "/" + sp, tracks, pri=pri, layer=layer, events=events)


R, Lh = lambda *a: arm('r', *a), lambda *a: arm('l', *a)
RL, LL = lambda *a: leg('r', *a), lambda *a: leg('l', *a)

# ============================================================================ player: what you stand in
penv("cobweb_tear_through", "Tearing Through Cobwebs", LIVE + " && q.feet_block == 'cobweb' && q.ground_speed >= 0.005", 2.0, {
    "right_arm:rot": lambda u: R(90 + 30 * wave(u), 30 * cwave(u)), "left_arm:rot": lambda u: Lh(90 + 30 * wave(u, 0.5), 30 * cwave(u, 0.5)), "body:rot": lambda u: tilt(14, 10 * wave(u), 0),
    "right_leg:rot": lambda u: RL(20 * max(0, wave(u))), "left_leg:rot": lambda u: LL(20 * max(0, wave(u, 0.5)))}, pri=240)
penv("cobweb_stuck", "Stuck Fast In A Cobweb", LIVE + " && q.feet_block == 'cobweb' && q.ground_speed < 0.005", 1.4, {
    "right_arm:rot": lambda u: R(60 + 20 * spike(u, 0.2, 2), 40), "left_arm:rot": lambda u: Lh(140, 20), "body:rot": lambda u: tilt(0, 0, 8 * wave(u)), "head:rot": lambda u: [10, 25 * wave(u, 0, 0.5), 0]}, pri=240)
penv("powder_snow_sinking", "Sinking In Powder Snow", LIVE + " && q.feet_block == 'powder_snow' && q.ground_speed < 0.01", 0.6, {
    "right_arm:rot": lambda u: R(120 + 20 * wave(u), 40), "left_arm:rot": lambda u: Lh(120 + 20 * wave(u, 0.5), 40), "mw_root:pos": lambda u: move(0, -1 + 0.3 * wave(u, 0, 2), 0), "head:rot": lambda u: [-20, 0, 2 * wave(u, 0, 4)]},
     pri=241)
penv("powder_snow_plunge", "Plunging Through Powder Snow", LIVE + " && q.feet_block == 'powder_snow' && q.ground_speed >= 0.01", 1.2, {
    "right_leg:rot": lambda u: RL(60 * max(0, wave(u))), "left_leg:rot": lambda u: LL(60 * max(0, wave(u, 0.5))), "right_arm:rot": lambda u: R(60, 40 + 10 * wave(u)), "left_arm:rot": lambda u: Lh(60, 40 + 10 * wave(u, 0.5)),
    "body:rot": lambda u: tilt(16, 6 * wave(u), 0)}, pri=241)
penv("berry_bush_tiptoe", "Wincing Through A Berry Bush", MOVING + " && q.feet_block == 'berry_bush'", 0.8, {
    "right_leg:rot": lambda u: RL(50 * max(0, wave(u))), "left_leg:rot": lambda u: LL(50 * max(0, wave(u, 0.5))), "right_arm:rot": lambda u: R(70, 50), "left_arm:rot": lambda u: Lh(70, 50),
    "head:rot": lambda u: [30, 0, 4 * spike(u, 0.2, 6, 2)]}, pri=242)
penv("berry_bush_frozen", "Holding Still Amid Thorns", STILL + " && q.feet_block == 'berry_bush'", 2.0, {"right_arm:rot": lambda u: R(80, 60), "left_arm:rot": lambda u: Lh(80, 60), "head:rot": lambda u: [35, 15 * wave(u), 0],
                                                                                                   "mw_root:pos": lambda u: move(0, 0.6, 0)}, pri=242)
penv("honey_sticky_steps", "Sticky Steps On Honey", MOVING + " && q.feet_block == 'honey'", 1.6, {
    "right_leg:rot": lambda u: RL(30 * spike(u, 0, 2)), "left_leg:rot": lambda u: LL(30 * spike(u, 0.5, 2)), "body:rot": lambda u: tilt(10, 0, 4 * wave(u)), "right_arm:rot": lambda u: R(20, 20), "left_arm:rot": lambda u: Lh(20, 20)},
     pri=243)
penv("honey_unstick", "Yanking A Foot Free Of Honey", STILL + " && q.feet_block == 'honey'", 1.4, {
    "right_leg:rot": lambda u: RL(40 * spike(u, 0.25, 4)), "body:rot": lambda u: tilt(-10 * spike(u, 0.25, 4), 0, 0), "right_arm:rot": lambda u: R(40, 40), "left_arm:rot": lambda u: Lh(30, 50)}, pri=243)
penv("scaffold_balance", "Balancing On Scaffolding", STILL + " && q.feet_block == 'scaffolding'", 1.8, {
    "right_arm:rot": lambda u: R(10, 70 + 10 * wave(u)), "left_arm:rot": lambda u: Lh(10, 70 - 10 * wave(u)), "mw_root:rot": lambda u: tilt(0, 0, 3 * wave(u))}, pri=232)
penv("snow_kick", "Kicking At The Snow", STILL + " && q.feet_block == 'snow' && q.idle_time > 3", 2.0, {"right_leg:rot": lambda u: RL(-30 * spike(u, 0.3, 3)), "head:rot": lambda u: [30, 0, 0], "right_arm:rot": lambda u: R(0, 10)},
     pri=225, group="env_idle", weight=2)
penv("soul_sand_tug", "Souls Tugging At Your Feet", STILL + " && q.surface == 'soul'", 2.4, {
    "body:rot": lambda u: tilt(-8, 0, 3 * wave(u)), "head:rot": lambda u: [25, 20 * wave(u, 0, 0.5), 0], "right_leg:rot": lambda u: RL(8 * wave(u, 0, 2)), "right_arm:rot": lambda u: R(20, 30), "left_arm:rot": lambda u: Lh(20, 30)},
     pri=226)
penv("mud_boot_pull", "Pulling A Boot From The Mud", STILL + " && q.feet_block == 'mud'", 1.8, {"left_leg:rot": lambda u: LL(50 * spike(u, 0.3, 3)), "body:rot": lambda u: tilt(20 * spike(u, 0.3, 3), 0, -4),
                                                                                         "right_arm:rot": lambda u: R(30, 40), "left_arm:rot": lambda u: Lh(30, 20)}, pri=226)
penv("flower_brush", "Fingertips Brushing Flowers", MOVING + " && q.feet_block == 'foliage' && !q.is_sneaking", 1.2, {"right_arm:rot": lambda u: R(10, 20 + 6 * wave(u)), "left_arm:rot": lambda u: Lh(10, 20 + 6 * wave(u, 0.5))},
     pri=90, layer="additive")
penv("flower_smell", "Stooping To Smell The Flowers", STILL + " && q.feet_block == 'foliage' && q.idle_time > 3", 3.0, {
    "body:rot": lambda u: tilt(35, 0, 0), "head:rot": lambda u: [20 - 6 * spike(u, 0.4, 3), 0, 0], "right_leg:rot": lambda u: RL(30), "mw_root:pos": lambda u: move(0, -1.5, 0), "right_arm:rot": lambda u: R(40, 10)},
     pri=227, group="env_idle", weight=3)
penv("brush_crouch", "Creeping Through The Brush", GROUND + " && q.feet_block == 'foliage' && q.is_sneaking", 1.4, {"right_arm:rot": lambda u: R(60, 40 + 20 * wave(u)), "left_arm:rot": lambda u: Lh(60, 40 + 20 * wave(u, 0.5)),
                                                                                                           "head:rot": lambda u: [-10, 20 * wave(u, 0, 0.5), 0]}, pri=228)
penv("magma_hot_foot", "Hopping On Hot Magma", STILL + " && q.surface == 'magma' && !q.is_sneaking", 0.5, {
    "right_leg:rot": lambda u: RL(40 * max(0, wave(u))), "left_leg:rot": lambda u: LL(40 * max(0, -wave(u))), "mw_root:pos": lambda u: move(0, 0.8 * abs(wave(u)), 0), "right_arm:rot": lambda u: R(30, 50), "left_arm:rot": lambda u: Lh(30, 50)},
     pri=244)
penv("magma_careful", "Treading Carefully On Magma", GROUND + " && q.surface == 'magma' && q.is_sneaking", 1.6, {"head:rot": lambda u: [40, 0, 0], "right_arm:rot": lambda u: R(20, 40), "left_arm:rot": lambda u: Lh(20, 40)}, pri=244,
     layer="additive")
penv("ice_wobble", "Wobbling On Ice", STILL + " && q.surface == 'glass'", 1.6, {"right_arm:rot": lambda u: R(30, 60 + 15 * wave(u)), "left_arm:rot": lambda u: Lh(30, 60 - 15 * wave(u)), "mw_root:rot": lambda u: tilt(3 * wave(u, 0.25), 0, 5 * wave(u)),
                                                                             "right_leg:rot": lambda u: RL(0, 6)}, pri=233)
penv("ice_skate", "Skating Across The Ice", MOVING + " && q.surface == 'glass' && q.is_sprinting", 1.6, {
    "right_leg:rot": lambda u: RL(-20 * max(0, wave(u)), 20 * max(0, wave(u))), "left_leg:rot": lambda u: LL(-20 * max(0, wave(u, 0.5)), 20 * max(0, wave(u, 0.5))), "body:rot": lambda u: tilt(20, 15 * wave(u), 0),
    "right_arm:rot": lambda u: R(-30 * wave(u), 20), "left_arm:rot": lambda u: Lh(30 * wave(u), 20)}, pri=245)
penv("ankle_splash", "Splashing Through The Shallows", LIVE + " && q.is_on_ground && q.is_in_water && q.fluid_depth < 0.4 && q.ground_speed >= 0.02", 0.8, {
    "right_leg:rot": lambda u: RL(40 * max(0, wave(u))), "left_leg:rot": lambda u: LL(40 * max(0, wave(u, 0.5))), "right_arm:rot": lambda u: R(10, 25), "left_arm:rot": lambda u: Lh(10, 25)}, pri=246)
pev("puddle_stomp", "Stomping In A Rain Puddle", event("land", GROUND + " && q.is_raining && q.mood > 0.6" + SKY), 0.7, {
    "right_leg:rot": [(0, RL(30)), (0.1, RL(-4), "in_quart"), (0.7, Z)], "right_arm:rot": [(0, Z), (0.1, R(30, 50)), (0.7, Z)], "left_arm:rot": [(0, Z), (0.1, Lh(30, 50)), (0.7, Z)]},
    events=[(0.1, "particle", {"particle": "splash", "count": "10", "at": "feet", "spread": "0.5"})])

# ============================================================================ player: weather
penv("rain_face_up", "Turning Your Face To The Rain", STILL + " && q.is_raining && !q.is_cold && q.mood > 0.5" + SKY, 4.0, {
    "head:rot": lambda u: [-45 + 3 * wave(u), 0, 0], "right_arm:rot": lambda u: R(10, 50), "left_arm:rot": lambda u: Lh(10, 50), "body:rot": lambda u: tilt(-8, 0, 0)}, pri=226, group="env_idle", weight=3)
penv("rain_hand_shield", "Hand Over Your Head In The Rain", MOVING + " && q.is_raining && !q.is_cold && q.main_hand == 'empty'" + SKY, 1.0, {"right_arm:rot": lambda u: R(150, -10, 30)}, pri=224)
penv("canopy_shelter", "Sheltering Under The Canopy", STILL + " && q.is_raining && !q.sky_exposed && q.feet_block != 'portal'", 4.0, {
    "head:rot": lambda u: [-30, 30 * wave(u), 0], "right_arm:rot": lambda u: R(30, -10, 30), "left_arm:rot": lambda u: Lh(30, -10, 30), "body:rot": lambda u: tilt(-4, 0, 0)}, pri=225)
penv("catch_snowflakes", "Catching Snowflakes", STILL + " && q.is_raining && q.is_cold" + SKY, 3.0, {
    "right_arm:rot": lambda u: R(70, 10, -60), "left_arm:rot": lambda u: Lh(70, 10, -60), "head:rot": lambda u: [-25 + 10 * spike(u, 0.6, 3), 0, 0]}, pri=226, group="env_idle", weight=3)
pev("snow_brush_off", "Brushing Snow Off Your Shoulders", event("rain_stop", LIVE + " && q.is_cold" + SKY), 1.4, {
    "right_arm:rot": [(0, Z), (0.3, R(100, -40, 40)), (0.5, R(90, -30, 40)), (0.7, R(100, -40, 40)), (1.4, Z)], "left_arm:rot": [(0, Z), (0.5, Lh(100, -40, 40)), (0.7, Lh(90, -30, 40)), (0.9, Lh(100, -40, 40)), (1.4, Z)],
    "head:rot": [(0, Z), (0.4, [10, 30, 0]), (0.8, [10, -30, 0]), (1.4, Z)]})
pev("thunder_duck", "Ducking Away From A Close Thunderclap", event("thunderclap:near", LIVE), 1.4, {
    "right_arm:rot": [(0, Z), (0.08, R(150, -10, 40), "out_expo"), (1.0, R(140, -10, 40)), (1.4, Z)], "left_arm:rot": [(0, Z), (0.1, Lh(40, 50)), (1.0, Lh(30, 40)), (1.4, Z)],
    "body:rot": [(0, Z), (0.08, [12, "q.event_dir > 0 ? -25 : 25", 0], "out_expo"), (1.0, [8, "q.event_dir > 0 ? -18 : 18", 0]), (1.4, Z)], "right_leg:rot": [(0, Z), (0.1, RL(30)), (1.0, RL(25)), (1.4, Z)],
    "mw_root:pos": [(0, Z), (0.08, move(0, -1.5, 0)), (1.0, move(0, -1, 0)), (1.4, Z)]}, pri=300, layer="reaction")
pev("thunder_glance", "Glancing At Distant Thunder", event("thunderclap:far", LIVE), 1.6, {
    "head:rot": [(0, Z), (0.3, [-20, "q.event_dir * 0.4", 0]), (1.2, [-20, "q.event_dir * 0.4", 0]), (1.6, Z)], "body:rot": [(0, Z), (0.4, tilt(0, "q.event_dir * 0.15", 0)), (1.6, Z)]}, pri=286)
penv("storm_wary", "Wary Under A Thunderstorm", STILL + " && q.is_thundering" + SKY, 3.0, {
    "head:rot": lambda u: [-15, 40 * wave(u), 0], "body:rot": lambda u: tilt(8, 0, 0), "right_arm:rot": lambda u: R(20, 10), "left_arm:rot": lambda u: Lh(20, 10)}, pri=227)
penv("wind_hold_hat", "Holding Your Hat In The Wind", STILL + " && q.wind > 0.75", 1.0, {"right_arm:rot": lambda u: R(165, -30, 40), "head:rot": lambda u: [14, 0, 3 * wave(u, 0, 2)], "body:rot": lambda u: tilt(10, 0, 2 * wave(u, 0, 2))},
     pri=228)
life("player.env.gust_stagger", "Staggered By A Gust", CAT, P, MOVING + " && q.wind > 0.9", 2.4, FP, {"body:rot": lambda u: tilt(0, 0, 8 * spike(u, 0.3, 4)), "right_arm:rot": lambda u: R(0, 30 * spike(u, 0.3, 4))}, pri=92)
life("player.env.cloak_streaming", "Cloak Streaming In The Wind", CAT, P, LIVE + " && q.wind > 0.5", 1.0, FP, {"cloak:rot": lambda u: [35 + 8 * wave(u, 0, 3), 0, 4 * wave(u, 0.3, 2)]}, pri=60)

# ============================================================================ player: temperature, light, altitude
penv("cold_blow_hands", "Blowing Warmth Into Your Hands", STILL + " && q.is_cold && !q.near_fire && !q.is_raining", 1.6, {
    "right_arm:rot": lambda u: R(120, -40, 40), "left_arm:rot": lambda u: Lh(120, -40, 40), "head:rot": lambda u: [10 + 4 * spike(u, 0.3, 4), 0, 0]}, pri=229, group="env_cold", weight=2)
penv("cold_stamp", "Stamping Feet Against The Cold", STILL + " && q.is_cold && !q.near_fire && q.idle_time > 6", 1.0, {
    "right_leg:rot": lambda u: RL(25 * spike(u, 0, 4)), "left_leg:rot": lambda u: LL(25 * spike(u, 0.5, 4)), "right_arm:rot": lambda u: R(40, -20, 40), "left_arm:rot": lambda u: Lh(40, -20, 40)}, pri=229, group="env_cold", weight=1)
penv("desert_shade_eyes", "Shading Your Eyes In The Desert Sun", STILL + " && q.temperature > 1.5 && !q.is_night && !q.is_raining" + SKY, 4.0, {
    "right_arm:rot": lambda u: R(140, -20, 40), "head:rot": lambda u: [-10, 45 * wave(u), 0], "body:rot": lambda u: tilt(0, 12 * wave(u, 0.05), 0)}, pri=229, group="env_heat", weight=2)
penv("heat_collar_fan", "Fanning Your Collar In The Heat", STILL + " && q.temperature > 1.5 && !q.is_night && q.idle_time > 6", 0.4, {
    "right_arm:rot": lambda u: R(110 + 10 * wave(u), -30, 40), "head:rot": lambda u: [-14, 0, 6], "body:rot": lambda u: tilt(-4, 0, 0)}, pri=229, group="env_heat", weight=1)
penv("sun_bask", "Basking In The Sunshine", STILL + " && q.time_of_day > 0.2 && q.time_of_day < 0.3 && !q.is_raining && q.temperature <= 1.5 && q.idle_time > 10" + SKY, 6.0, {
    "head:rot": lambda u: [-35, 0, 0], "right_arm:rot": lambda u: R(20, 60), "left_arm:rot": lambda u: Lh(20, 60), "body:rot": lambda u: tilt(-6 + wave(u), 0, 0)}, pri=226, group="env_idle", weight=2)
penv("moon_gaze", "Gazing At The Moon", STILL + " && q.is_night && q.head_pitch < -30" + SKY, 5.0, {"head:rot": lambda u: [-5, 6 * wave(u, 0, 0.5), 0], "right_arm:rot": lambda u: R(-20, 10, -30),
                                                                                                 "left_arm:rot": lambda u: Lh(-20, 10, -30), "body:rot": lambda u: tilt(-6, 0, 0)}, pri=226)
penv("dark_grope", "Groping Through The Dark", MOVING + " && (q.light < 2 || q.is_blinded)", 1.4, {
    "right_arm:rot": lambda u: R(85 + 10 * wave(u), 10 * cwave(u)), "left_arm:rot": lambda u: Lh(75 + 10 * wave(u, 0.5), 10 * cwave(u, 0.5)), "head:rot": lambda u: [0, 25 * wave(u, 0, 0.5), 0]}, pri=231)
penv("dark_huddle", "Huddling In Pitch Darkness", STILL + " && q.light < 2 && !q.is_blinded", 2.0, {
    "right_arm:rot": lambda u: R(40, -20, 40), "left_arm:rot": lambda u: Lh(40, -20, 40), "body:rot": lambda u: tilt(14, 0, 0), "head:rot": lambda u: [0, 35 * wave(u), 0], "mw_root:pos": lambda u: move(0, -1, 0)}, pri=230)
penv("cave_listen", "Listening To The Cave", STILL + " && !q.sky_exposed && q.altitude < 40 && q.idle_time > 5 && q.light >= 2", 3.0, {
    "right_arm:rot": lambda u: R(140, -40, 70), "head:rot": lambda u: [0, -30, 10], "body:rot": lambda u: tilt(0, -10, 0)}, pri=227, group="env_idle", weight=2)
life("player.env.deep_dark_hunch", "Hunched In The Oppressive Deep", CAT, P, MOVING + " && !q.sky_exposed && q.altitude < 0", 1.6, FP, {"body:rot": lambda u: tilt(10, 0, 0), "head:rot": lambda u: [4, 10 * wave(u, 0, 0.5), 0]}, pri=91)
penv("summit_vertigo", "Vertigo On A High Ledge", STILL + " && q.altitude > 180 && q.at_ledge && q.head_pitch > 40", 1.4, {
    "mw_root:rot": lambda u: tilt(4 * wave(u, 0.25), 0, 5 * wave(u)), "right_arm:rot": lambda u: R(20, 50 + 10 * wave(u)), "left_arm:rot": lambda u: Lh(20, 50 - 10 * wave(u)), "body:rot": lambda u: tilt(-10, 0, 0)}, pri=247)
life("player.env.thin_air", "Short Of Breath In The Thin Air", CAT, P, MOVING + " && q.altitude > 200", 0.7, FP, {"body:rot": lambda u: tilt(6 + 3 * wave(u, 0, 2), 0, 0), "head:rot": lambda u: [-6 * wave(u, 0, 2), 0, 0]}, pri=91)
penv("bright_squint", "Squinting Up Into Bright Sky", STILL + " && q.light >= 15 && !q.is_night && q.head_pitch < -40" + SKY, 2.0, {"left_arm:rot": lambda u: Lh(150, -10, 40), "head:rot": lambda u: [8 * wave(u), 0, 12],
                                                                                                                                 "body:rot": lambda u: tilt(-8, 0, 0), "right_arm:rot": lambda u: R(-10, 10)}, pri=228)
penv("mountain_wind_stance", "Bracing Against Mountain Winds", STILL + " && q.altitude > 150 && q.wind > 0.5", 2.0, {
    "body:rot": lambda u: tilt(14, 0, 3 * wave(u, 0, 2)), "right_leg:rot": lambda u: RL(-16), "left_leg:rot": lambda u: LL(20), "right_arm:rot": lambda u: R(30, -10, 30), "left_arm:rot": lambda u: Lh(10, 30), "head:rot": lambda u: [16, 0, 0]},
     pri=229)
penv("sunset_watch", "Watching The Sunset", STILL + " && q.time_of_day > 0.46 && q.time_of_day < 0.53 && !q.is_raining" + SKY, 6.0, {
    "right_arm:rot": lambda u: R(20, -10, 30), "left_arm:rot": lambda u: Lh(20, -10, 30), "head:rot": lambda u: [-8, 0, 0], "body:rot": lambda u: tilt(-2, 0, 2 * wave(u)), "right_leg:rot": lambda u: RL(0, 8)}, pri=226, group="env_idle", weight=4)

# ============================================================================ player: fire, dimensions, effects, carried light
penv("fire_warm_crouch", "Crouching To Warm Up By The Fire", STILL + " && q.near_fire && q.is_cold", 1.0, {
    "mw_root:pos": lambda u: move(0, -5, 0), "right_leg:rot": lambda u: RL(90), "left_leg:rot": lambda u: LL(90), "right_arm:rot": lambda u: R(80, -20, 30), "left_arm:rot": lambda u: Lh(80, -20, 30),
    "right_arm:pos": lambda u: move(0.3 * wave(u), 0, 0)}, pri=235)
penv("fire_poke", "Poking At The Fire", STILL + " && q.near_fire && !q.is_cold && q.idle_time > 8", 2.2, {
    "right_arm:rot": lambda u: R(40 + 20 * spike(u, 0.3, 3), 0), "body:rot": lambda u: tilt(20, 0, 0), "head:rot": lambda u: [30, 0, 0], "right_leg:rot": lambda u: RL(30)}, pri=234, group="env_fire", weight=2)
penv("smoke_wave_off", "Waving Away Campfire Smoke", STILL + " && q.near_fire && !q.is_cold && q.idle_time > 4", 0.8, {
    "right_arm:rot": lambda u: R(110, -10 + 30 * wave(u, 0, 2), 30), "head:rot": lambda u: [0, -20, 0], "body:rot": lambda u: tilt(-4, -10, 0)}, pri=234, group="env_fire", weight=1)
penv("lava_heat_recoil", "Shielding Your Face From Lava Heat", STILL + " && q.near_fire && q.dimension == 'the_nether'", 1.6, {
    "right_arm:rot": lambda u: R(110, -20, 30), "head:rot": lambda u: [10, -25, 0], "body:rot": lambda u: tilt(-8, -14, 0)}, pri=236)
penv("nether_ash_brush", "Brushing Off Nether Ash", STILL + " && q.dimension == 'the_nether' && !q.near_fire && q.idle_time > 8", 2.0, {
    "right_arm:rot": lambda u: R(60 + 20 * spike(u, 0.3, 3), -40, 40), "head:rot": lambda u: [30, 20, 0], "left_arm:rot": lambda u: Lh(30, 20)}, pri=226, group="env_idle", weight=1)
penv("end_void_stare", "Staring Into The Endless Void", STILL + " && q.dimension == 'the_end' && q.at_ledge", 4.0, {
    "head:rot": lambda u: [45, 10 * wave(u, 0, 0.5), 0], "right_arm:rot": lambda u: R(60, -30, 40), "left_arm:rot": lambda u: Lh(55, -30, 40), "body:rot": lambda u: tilt(10, 0, 0)}, pri=248)
penv("blind_stumble", "Stumbling Blind", MOVING + " && q.is_blinded", 1.0, {"right_arm:rot": lambda u: R(90, 30 * wave(u)), "head:rot": lambda u: [10, 30 * wave(u, 0.25), 0],
                                                                          "body:rot": lambda u: tilt(6, 0, 4 * wave(u))}, pri=232)
life("player.env.nausea_reel", "Reeling With Nausea", CAT, P, LIVE + " && q.is_nauseous", 3.0, FP, {"body:rot": lambda u: tilt(5 * wave(u, 0.25), 0, 9 * wave(u)), "head:rot": lambda u: [8, 0, -10 * wave(u)]}, pri=94)
penv("invisible_tiptoe", "Tiptoeing While Invisible", MOVING + " && q.is_invisible", 1.4, {
    "right_leg:rot": lambda u: RL(30 * max(0, wave(u))), "left_leg:rot": lambda u: LL(30 * max(0, wave(u, 0.5))), "right_arm:rot": lambda u: R(40, 20, -30), "left_arm:rot": lambda u: Lh(40, 20, -30),
    "body:rot": lambda u: tilt(10, 0, 0), "mw_root:pos": lambda u: move(0, 0.6 * abs(wave(u)), 0)}, pri=231)
penv("lantern_aloft", "Holding A Lantern Aloft In The Dark", GROUND + " && q.main_hand == 'lantern' && !q.sky_exposed && q.light < 8", 2.0, {"right_arm:rot": lambda u: R(120, 10), "head:rot": lambda u: [-6, 25 * wave(u, 0, 0.5), 0]},
     pri=231, layer="additive")
penv("torch_rain_cup", "Cupping A Torch Against The Rain", GROUND + " && q.main_hand == 'torch' && q.is_raining" + SKY, 1.0, {"right_arm:rot": lambda u: R(60, -10, 20), "left_arm:rot": lambda u: Lh(70, -30, 40), "head:rot": lambda u: [20, 0, 0]},
     pri=232)
penv("cold_water_wade", "Wading Through Icy Water", LIVE + " && q.is_on_ground && q.is_in_water && q.is_cold && q.ground_speed >= 0.01", 1.2, {
    "right_arm:rot": lambda u: R(30, -20, 40), "left_arm:rot": lambda u: Lh(30, -20, 40), "body:rot": lambda u: tilt(10, 0, 1.2 * wave(u, 0, 4)), "right_leg:rot": lambda u: RL(30 * max(0, wave(u))), "left_leg:rot": lambda u: LL(30 * max(0, wave(u, 0.5)))},
     pri=247)

# ============================================================================ creatures: thunder
THUNDER = {
    "minecraft:cow": ("Cow Spooked By Thunder", {"head:rot": [(0, Z), (0.08, [-30, 0, 0], "out_expo"), (0.8, Z)], "mw_center:pos": [(0, Z), (0.1, move(0, 1, -0.5)), (0.8, Z)], "left_front_leg:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.8, Z)]}),
    "minecraft:sheep": ("Sheep Scattering At Thunder", {"mw_center:rot": [(0, Z), (0.1, [0, "q.event_dir > 0 ? -40 : 40", 0], "out_expo"), (0.8, Z)], "head:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.8, Z)]}),
    "minecraft:pig": ("Pig Squealing At Thunder", {"mw_center:pos": [(0, Z), (0.08, move(0, 2, 0), "out_expo"), (0.3, Z)], "head:rot": [(0, Z), (0.08, [-25, 0, 0]), (0.2, [10, 0, 0]), (0.5, Z)]}),
    "minecraft:horse": ("Horse Shying At Thunder", {"head_parts:rot": [(0, Z), (0.1, [-40, 0, 0], "out_expo"), (1.0, Z)], "mw_center:rot": [(0, Z), (0.15, tilt(-12, 0, 0)), (1.0, Z)], "tail:rot": [(0, Z), (0.1, [-40, 0, 0]), (1.0, Z)]}),
    "minecraft:donkey": ("Donkey Braying At The Storm", {"head_parts:rot": [(0, Z), (0.2, [-45, 0, 0]), (1.0, [-40, 0, 0]), (1.4, Z)], "upper_mouth:rot": [(0, Z), (0.2, [-20, 0, 0]), (0.6, [-5, 0, 0]), (1.0, [-20, 0, 0]), (1.4, Z)]}),
    "minecraft:chicken": ("Chicken Freezing Then Puffing Up At Thunder", {"body:scl": [(0, [1, 1, 1]), (0.4, [1, 1, 1]), (0.55, [1.2, 1.15, 1.2], "out_back"), (1.4, [1, 1, 1])],
                                                                          "head:rot": [(0, Z), (0.05, [-30, 0, 0]), (0.4, [-30, 0, 0]), (0.6, [10, 0, 0]), (1.4, Z)]}),
    "minecraft:cat": ("Cat Puffing Up At Thunder", {"body:scl": [(0, [1, 1, 1]), (0.08, [1.15, 1.15, 1.05], "out_expo"), (1.0, [1, 1, 1])], "tail1:rot": [(0, Z), (0.08, [-70, 0, 0]), (1.0, Z)], "mw_center:pos": [(0, Z), (0.08, move(0, 1.5, 0)), (0.5, Z)]}),
    "minecraft:wolf": ("Wolf Flattening Its Ears At Thunder", {"mw_center:pos": [(0, Z), (0.1, move(0, -1.5, 0)), (1.2, Z)], "tail:rot": [(0, Z), (0.1, [50, 0, 0]), (1.2, Z)], "head:rot": [(0, Z), (0.1, [20, "q.event_dir * 0.3", 0]), (1.2, Z)]}),
    "minecraft:rabbit": ("Rabbit Bolting From Thunder", {"mw_center:pos": [(0, Z), (0.08, move(0, 3, 1), "out_expo"), (0.4, Z)], "right_ear:rot": [(0, Z), (0.08, [40, 0, 0]), (0.8, Z)], "left_ear:rot": [(0, Z), (0.08, [40, 0, 0]), (0.8, Z)]}),
    "minecraft:fox": ("Fox Cringing At Thunder", {"mw_center:pos": [(0, Z), (0.1, move(0, -1.5, 0)), (1.0, Z)], "tail:rot": [(0, Z), (0.1, [0, -60, 0]), (1.0, Z)], "right_ear:rot": [(0, Z), (0.1, [30, 0, 0]), (1.0, Z)]}),
    "minecraft:llama": ("Llama Stretching Tall At Thunder", {"head:rot": [(0, Z), (0.15, [-25, "q.event_dir * 0.3", 0]), (1.2, Z)], "mw_center:pos": [(0, Z), (0.15, move(0, 1, 0)), (1.2, Z)]}),
    "minecraft:goat": ("Goat Answering The Thunder", {"head:rot": [(0, Z), (0.2, [-40, 0, 0]), (0.4, [-38, 0, 8]), (0.6, [-40, 0, -8]), (1.0, Z)]}),
    "minecraft:parrot": ("Parrot Squawking At Thunder", {"feather:rot": [(0, Z), (0.08, [-40, 0, 0]), (1.0, Z)], "right_wing:rot": [(0, Z), (0.08, [0, 0, 60]), (0.6, Z)], "left_wing:rot": [(0, Z), (0.08, [0, 0, -60]), (0.6, Z)]}),
    "minecraft:mooshroom": ("Mooshroom Shuddering At Thunder", {"mw_center:rot": [(0, Z), (0.1, tilt(0, 0, 8)), (0.2, tilt(0, 0, -8)), (0.3, tilt(0, 0, 5)), (0.6, Z)], "head:rot": [(0, Z), (0.1, [20, 0, 0]), (0.6, Z)]}),
    "minecraft:camel": ("Camel Unfazed By Thunder", {"head:rot": [(0, Z), (0.6, [-6, "q.event_dir * 0.3", 0]), (1.6, [-6, "q.event_dir * 0.3", 0]), (2.0, Z)], "left_ear:rot": [(0, Z), (0.4, [0, 0, -20]), (1.6, Z)]}),
    "minecraft:turtle": ("Turtle Pulling In At Thunder", {"head:pos": [(0, Z), (0.1, move(0, 0, -2), "out_expo"), (1.4, move(0, 0, -2)), (2.0, Z)]}),
    "minecraft:polar_bear": ("Polar Bear Rising At Thunder", {"mw_center:rot": [(0, Z), (0.4, tilt(-25, 0, 0)), (1.2, tilt(-25, 0, 0)), (1.6, Z)], "head:rot": [(0, Z), (0.4, [-20, "q.event_dir * 0.3", 0]), (1.6, Z)]}),
    "minecraft:bee": ("Bee Zipping Away From Thunder", {"bone:pos": [(0, Z), (0.1, move(0, 2, -1), "out_expo"), (0.6, Z)], "bone:rot": [(0, Z), (0.1, tilt(-30, 0, 20)), (0.6, Z)]}),
    "minecraft:villager": ("Villager Clutching Its Robes At Thunder", {"arms:rot": [(0, Z), (0.1, [-50, 0, 0]), (0.9, [-45, 0, 0]), (1.2, Z)], "head:rot": [(0, Z), (0.2, [-30, "q.event_dir * 0.3", 0]), (1.2, Z)],
                                                                      "body:rot": [(0, Z), (0.1, tilt(-8)), (1.2, Z)]}),
    "minecraft:iron_golem": ("Iron Golem Looking To The Storm", {"head:rot": [(0, Z), (0.6, [-25, "q.event_dir * 0.4", 0]), (1.6, [-25, "q.event_dir * 0.4", 0]), (2.0, Z)]}),
    "minecraft:zombie": ("Zombie Groaning Up At The Storm", {"head:rot": [(0, Z), (0.4, [-35, 0, 10]), (1.4, [-30, 0, -10]), (1.8, Z)], "right_arm:rot": [(0, arm('r', 90)), (0.4, arm('r', 130)), (1.4, arm('r', 120)), (1.8, arm('r', 90))]}),
    "minecraft:creeper": ("Creeper Crackling As Lightning Strikes", {"body:scl": [(0, [1, 1, 1]), (0.05, [1.1, 1.1, 1.1]), (0.1, [1, 1, 1]), (0.15, [1.1, 1.1, 1.1]), (0.3, [1, 1, 1])],
                                                                     "head:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.6, Z)]}),
    "minecraft:skeleton": ("Skeleton Rattling At Thunder", {"right_arm:rot": [(0, Z), (0.05, [3, 0, 3]), (0.1, [-3, 0, -3]), (0.15, [3, 0, 3]), (0.2, [-3, 0, -3]), (0.4, Z)], "head:rot": [(0, Z), (0.1, [-15, "q.event_dir * 0.3", 0]), (0.8, Z)]}),
    "minecraft:frog": ("Frog Croaking Back At Thunder", {"croaking_body:scl": [(0, [1, 1, 1]), (0.3, [1.9, 1.9, 1.4]), (0.5, [1, 1, 1])], "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (0.5, Z)]}),
    "minecraft:sniffer": ("Sniffer Lifting Its Nose To The Storm", {"head:rot": [(0, Z), (0.6, [-25, 0, 0]), (1.6, [-25, 0, 0]), (2.0, Z)], "nose:rot": [(0, Z), (0.8, [6, 0, 0]), (1.0, Z), (1.2, [6, 0, 0]), (2.0, Z)]}),
}
for T, (name, tracks) in THUNDER.items():
    mev(T, "thunder", name, event("thunderclap", "!q.is_dead"), max(t for seq in tracks.values() for t, *_ in seq), tracks, pri=210, layer="reaction")

# ============================================================================ explosions (positional "explosion" world event)
# Entities caught in the blast also get explosion_flinch and a hurt reaction; these are for everyone who only hears it.
pev("blast_far_shield_eyes", "Shading Your Eyes Toward A Distant Blast", event("explosion:far", LIVE), 1.8, {
    "head:rot": [(0, Z), (0.15, [-8, "q.event_dir * 0.6", 0], "out_expo"), (1.3, [-8, "q.event_dir * 0.6", 0]), (1.8, Z)],
    "right_arm:rot": [(0, Z), (0.25, R(150, -20, 50)), (1.3, R(150, -20, 50)), (1.8, Z)], "body:rot": [(0, Z), (0.2, tilt(-4, "q.event_dir * 0.25", 0)), (1.3, tilt(-4, "q.event_dir * 0.25", 0)), (1.8, Z)],
    "mw_root:pos": [(0, Z), (0.6, Z), (0.7, move(0, -0.6, 0), "out_expo"), (1.0, Z)]}, pri=287)
AWAY = "q.event_dir > 0 ? -70 : 70"
BLAST = {
    "minecraft:cow": ("Cow Wheeling Away From A Blast", {"mw_center:rot": [(0, Z), (0.25, [0, AWAY, 0], "out_back"), (1.2, [0, AWAY, 0]), (1.8, Z)],
                                                         "head:rot": [(0, Z), (0.1, [-25, "q.event_dir * 0.5", 0]), (0.6, [10, 0, 0]), (1.8, Z)], "right_front_leg:rot": [(0, Z), (0.1, [-30, 0, 0]), (0.3, [10, 0, 0]), (0.5, Z)]}),
    "minecraft:sheep": ("Sheep Bunching Low After A Blast", {"mw_center:pos": [(0, Z), (0.15, move(0, -1, 0)), (1.4, move(0, -1, 0)), (2.0, Z)],
                                                             "head:rot": [(0, Z), (0.15, [20, "q.event_dir * 0.4", 0]), (1.4, [20, "q.event_dir * 0.4", 0]), (2.0, Z)]}),
    "minecraft:pig": ("Pig Dropping Flat At A Blast", {"mw_center:pos": [(0, Z), (0.1, move(0, -2, 0), "out_expo"), (1.0, move(0, -2, 0)), (1.6, Z)], "head:rot": [(0, Z), (0.1, [25, 0, 0]), (1.0, [25, 0, 0]), (1.6, Z)],
                                                       "right_front_leg:rot": [(0, Z), (0.1, [-50, 0, 20]), (1.0, [-50, 0, 20]), (1.6, Z)], "left_front_leg:rot": [(0, Z), (0.1, [-50, 0, -20]), (1.0, [-50, 0, -20]), (1.6, Z)]}),
    "minecraft:horse": ("Horse Rearing At A Blast", {"mw_center:rot": [(0, Z), (0.3, tilt(-35, 0, 0), "out_back"), (0.9, tilt(-30, 0, 0)), (1.4, Z)], "head_parts:rot": [(0, Z), (0.3, [-20, "q.event_dir * 0.3", 0]), (1.4, Z)],
                                                     "right_front_leg:rot": [(0, Z), (0.3, [-60, 0, 0]), (0.6, [-30, 0, 0]), (0.9, [-60, 0, 0]), (1.4, Z)],
                                                     "left_front_leg:rot": [(0, Z), (0.45, [-60, 0, 0]), (0.75, [-30, 0, 0]), (1.05, [-60, 0, 0]), (1.4, Z)]}),
    "minecraft:wolf": ("Wolf Barking Toward A Blast", {"head:rot": [(0, Z), (0.2, [-10, "q.event_dir * 0.6", 0]), (0.35, [5, "q.event_dir * 0.6", 0]), (0.5, [-10, "q.event_dir * 0.6", 0]), (0.65, [5, "q.event_dir * 0.6", 0]), (1.2, Z)],
                                                       "mw_center:pos": [(0, Z), (0.2, move(0, 0, -1)), (1.2, Z)], "tail:rot": [(0, Z), (0.2, [-30, 0, 0]), (1.2, Z)]}),
    "minecraft:cat": ("Cat Bolting Low From A Blast", {"mw_center:pos": [(0, Z), (0.1, move(0, -1.5, -2), "out_expo"), (1.0, move(0, -1.5, -2)), (1.5, Z)], "tail1:rot": [(0, Z), (0.1, [40, 0, 0]), (1.5, Z)],
                                                       "head:rot": [(0, Z), (0.1, [15, "q.event_dir * 0.5", 0]), (1.5, Z)]}),
    "minecraft:chicken": ("Chicken Flapping Wildly At A Blast", {"right_wing:rot": [(0, Z), (0.05, [0, 0, 70]), (0.15, [0, 0, 10]), (0.25, [0, 0, 70]), (0.35, [0, 0, 10]), (0.45, [0, 0, 70]), (0.7, Z)],
                                                                 "left_wing:rot": [(0, Z), (0.05, [0, 0, -70]), (0.15, [0, 0, -10]), (0.25, [0, 0, -70]), (0.35, [0, 0, -10]), (0.45, [0, 0, -70]), (0.7, Z)],
                                                                 "mw_center:pos": [(0, Z), (0.2, move(0, 3, 0), "out_expo"), (0.5, Z)]}),
    "minecraft:villager": ("Villager Hiding Its Face From A Blast", {"arms:rot": [(0, Z), (0.12, [-90, 0, 0], "out_expo"), (1.4, [-85, 0, 0]), (1.8, Z)], "head:rot": [(0, Z), (0.12, [35, "q.event_dir * -0.3", 0]), (1.4, [30, "q.event_dir * -0.3", 0]), (1.8, Z)],
                                                                     "body:rot": [(0, Z), (0.12, tilt(15)), (1.4, tilt(12)), (1.8, Z)], "mw_root:pos": [(0, Z), (0.12, move(0, -1, 0)), (1.4, move(0, -1, 0)), (1.8, Z)]}),
    "minecraft:iron_golem": ("Iron Golem Turning To Face A Blast", {"mw_root:rot": [(0, Z), (0.6, [0, "q.event_dir * 0.5", 0]), (1.8, [0, "q.event_dir * 0.5", 0]), (2.4, Z)], "right_arm:rot": [(0, Z), (0.6, [-30, 0, 0]), (1.8, [-30, 0, 0]), (2.4, Z)],
                                                                    "left_arm:rot": [(0, Z), (0.6, [-30, 0, 0]), (1.8, [-30, 0, 0]), (2.4, Z)], "head:rot": [(0, Z), (0.6, [-5, "q.event_dir * 0.3", 0]), (2.4, Z)]}),
    "minecraft:creeper": ("Creeper Swelling In Sympathy With A Blast", {"body:scl": [(0, [1, 1, 1]), (0.6, [1.12, 1.12, 1.12]), (0.8, [1.05, 1.05, 1.05]), (1.0, [1.12, 1.12, 1.12]), (1.6, [1, 1, 1])],
                                                                        "head:rot": [(0, Z), (0.4, [0, "q.event_dir * 0.5", 0]), (1.6, Z)]}),
    "minecraft:zombie": ("Zombie Lurching Toward The Sound Of A Blast", {"mw_root:rot": [(0, Z), (0.5, [0, "q.event_dir * 0.6", 0]), (1.6, [0, "q.event_dir * 0.6", 0]), (2.0, Z)],
                                                                         "head:rot": [(0, Z), (0.3, [-10, "q.event_dir * 0.3", 0]), (2.0, Z)], "body:rot": [(0, Z), (0.5, tilt(12)), (1.6, tilt(12)), (2.0, Z)]}),
}
for T, (name, tracks) in BLAST.items():
    mev(T, "blast", name, event("explosion", "!q.is_dead"), max(t for seq in tracks.values() for t, *_ in seq), tracks, pri=212, layer="reaction")

# ============================================================================ creatures: rain
RAIN = "q.is_raining && q.sky_exposed && !q.is_cold"
menv("minecraft:cow", "rain_stoic", "Cow Standing Stoic In The Rain", RAIN + " && q.ground_speed < 0.01", 3.0, {"head:rot": lambda u: [22 + 2 * wave(u), 0, 0], "mw_center:rot": lambda u: tilt(0, 0, 1.5 * wave(u))})
menv("minecraft:sheep", "rain_huddle", "Sheep Huddled Against The Rain", RAIN + " && q.ground_speed < 0.01", 2.4, {"head:rot": lambda u: [30, 0, 0], "mw_center:pos": lambda u: move(0, -0.8, 0),
                                                                                                                    "left_front_leg:rot": lambda u: [-8, 0, 6], "right_front_leg:rot": lambda u: [-8, 0, -6]})
menv("minecraft:pig", "rain_joy", "Pig Delighting In The Rain", RAIN, 1.0, {"mw_center:rot": lambda u: tilt(0, 8 * wave(u), 4 * wave(u, 0.25)), "head:rot": lambda u: [-20 + 6 * wave(u, 0, 2), 0, 0]}, layer="additive", pri=72)
menv("minecraft:horse", "rain_tail_to_wind", "Horse Turning Its Tail To The Rain", RAIN + " && q.ground_speed < 0.01", 3.0, {"head_parts:rot": lambda u: [40 + 3 * wave(u), 0, 0], "tail:rot": lambda u: [30, 0, 0],
                                                                                                                             "left_ear:rot": lambda u: [20, 0, 0], "right_ear:rot": lambda u: [20, 0, 0]})
menv("minecraft:donkey", "rain_ears_back", "Donkey Pinning Its Ears In The Rain", RAIN, 2.0, {"left_ear:rot": lambda u: [40, 0, -10], "right_ear:rot": lambda u: [40, 0, 10], "head_parts:rot": lambda u: [14, 0, 0]}, layer="additive", pri=72)
menv("minecraft:chicken", "rain_hunker", "Chicken Hunkered Down In The Rain", RAIN + " && q.ground_speed < 0.01", 2.0, {"mw_center:pos": lambda u: move(0, -1.5, 0), "head:pos": lambda u: move(0, -0.6, -0.6),
                                                                                                                      "body:scl": lambda u: [1.08, 1.06, 1.08]})
menv("minecraft:wolf", "rain_shake_off", "Wolf Shaking Off The Rain", RAIN, 4.0, {"mw_center:rot": lambda u: tilt(0, 0, 14 * spike(u, 0.7, 3, 6) * (1 if wave(u, 0.7, 6) > 0 else -1)), "tail:rot": lambda u: [20, 0, 0]}, layer="additive", pri=72)
menv("minecraft:cat", "rain_annoyed", "Cat Hunched And Annoyed In The Rain", RAIN + " && q.ground_speed < 0.01", 2.4, {"mw_center:pos": lambda u: move(0, -1.5, 0), "head:rot": lambda u: [14, 0, 0], "tail1:rot": lambda u: [30, -40, 0],
                                                                                                                      "tail2:rot": lambda u: [0, 20 * spike(u, 0.4, 6), 0]})
menv("minecraft:fox", "rain_ear_flick", "Fox Flicking Rain From Its Ears", RAIN, 1.6, {"right_ear:rot": lambda u: [0, 0, 30 * spike(u, 0.2, 10)], "left_ear:rot": lambda u: [0, 0, -30 * spike(u, 0.25, 10)], "head:rot": lambda u: [0, 0, 8 * spike(u, 0.22, 10)]},
     layer="additive", pri=72)
menv("minecraft:rabbit", "rain_ears_flat", "Rabbit Flattening Its Ears In The Rain", RAIN + " && q.ground_speed < 0.01", 2.0, {"right_ear:rot": lambda u: [60, 0, 0], "left_ear:rot": lambda u: [60, 0, 0], "mw_center:pos": lambda u: move(0, -0.6, 0)})
menv("minecraft:llama", "rain_unbothered", "Llama Chewing Through The Rain", RAIN + " && q.ground_speed < 0.01", 1.8, {"head:rot": lambda u: [0, 4 * wave(u, 0, 4), 3 * wave(u, 0.2, 4)]})
menv("minecraft:goat", "rain_head_shake", "Goat Shaking Rain From Its Horns", RAIN, 3.0, {"head:rot": lambda u: [0, 0, 20 * spike(u, 0.5, 4, 4) * (1 if wave(u, 0.5, 4) > 0 else -1)]}, layer="additive", pri=72)
menv("minecraft:parrot", "rain_fluffed", "Parrot Fluffed Up In The Rain", RAIN + " && !q.is_flying", 2.0, {"body:scl": lambda u: [1.12, 1.1, 1.12], "head:rot": lambda u: [14, 0, 0], "feather:rot": lambda u: [-10, 0, 0]})
menv("minecraft:camel", "rain_disdain", "Camel Disdaining The Rain", RAIN + " && q.ground_speed < 0.01", 3.0, {"head:rot": lambda u: [-12, 0, 0], "left_ear:rot": lambda u: [0, 0, -30], "right_ear:rot": lambda u: [0, 0, 30],
                                                                                                             "tail:rot": lambda u: [0, 20 * spike(u, 0.3, 6), 0]})
menv("minecraft:turtle", "rain_relish", "Turtle Relishing The Rain", RAIN + " && q.ground_speed < 0.01", 3.0, {"head:rot": lambda u: [-30, 0, 0], "head:pos": lambda u: move(0, 0.4, 0.8)})
menv("minecraft:polar_bear", "rain_sprawl", "Polar Bear Sprawled In The Rain", RAIN + " && q.ground_speed < 0.01 && q.idle_time > 10", 4.0, {"mw_center:pos": lambda u: move(0, -6, 0), "mw_center:rot": lambda u: tilt(0, 0, 70),
                                                                                                                                         "left_front_leg:rot": lambda u: [0, 0, -30 + 5 * wave(u)]})
menv("minecraft:bee", "rain_heavy_wings", "Bee Labouring Through The Rain", RAIN + " && q.is_flying", 0.7, {"bone:pos": lambda u: move(0, -1 + 0.6 * wave(u, 0, 2), 0), "bone:rot": lambda u: tilt(-10, 0, 6 * wave(u))}, layer="additive", pri=72)
menv("minecraft:axolotl", "rain_happy", "Axolotl Happy In The Rain Out Of Water", RAIN + " && !q.is_in_water", 1.4, {"top_gills:rot": lambda u: [-20 * wave(u), 0, 0], "tail:rot": lambda u: [0, 20 * wave(u), 0]}, pri=125)
menv("minecraft:frog", "rain_hop_joy", "Frog Hopping Joyfully In The Rain", RAIN + " && q.ground_speed < 0.01", 1.0, {"mw_center:pos": lambda u: move(0, 1.5 * max(0, wave(u)), 0), "body:scl": lambda u: [1, 1 + 0.06 * wave(u, 0.5), 1]})
menv("minecraft:zombie", "rain_relief", "Zombie Lifting Its Face To Cooling Rain", RAIN + " && q.ground_speed < 0.01 && !q.is_aggressive", 4.0, {"head:rot": lambda u: [-30, 0, 6 * wave(u)], "body:rot": lambda u: tilt(-6, 0, 0)})
menv("minecraft:creeper", "rain_hiss", "Creeper Hissing At The Rain", RAIN, 3.0, {"head:rot": lambda u: [0, 0, 4 * spike(u, 0.3, 8)], "body:scl": lambda u: [1 + 0.02 * spike(u, 0.3, 8)] * 3}, layer="additive", pri=72)
menv("minecraft:skeleton", "rain_drip", "Skeleton Dripping In The Rain", RAIN + " && q.ground_speed < 0.01", 2.0, {"head:rot": lambda u: [14, 0, 0], "right_arm:rot": lambda u: arm('r', 0, 4 * spike(u, 0.5, 8))})
menv("minecraft:spider", "rain_slick", "Spider Slipping On Slick Walls", RAIN + " && q.is_climbing", 0.5, {"mw_center:pos": lambda u: move(0, -0.8 * spike(u, 0.3, 6), 0)}, layer="additive", pri=72)
menv("minecraft:slime", "rain_wobble", "Slime Wobbling Under The Rain", RAIN, 0.6, {"cube:scl": lambda u: [1 + 0.04 * wave(u, 0, 2), 1 - 0.04 * wave(u, 0, 2), 1 + 0.04 * wave(u, 0.25, 2)]}, layer="additive", pri=72)
menv("minecraft:iron_golem", "rain_creak", "Iron Golem Creaking In The Rain", RAIN + " && q.ground_speed < 0.01", 4.0, {"head:rot": lambda u: [8, 0, 3 * spike(u, 0.4, 6)], "right_arm:rot": lambda u: [2 * spike(u, 0.6, 6), 0, 0]})
menv("minecraft:snow_golem", "rain_melt_wince", "Snow Golem Wincing As The Rain Melts It", "q.is_raining && q.sky_exposed && !q.is_cold", 0.6, {"head:rot": lambda u: [10, 0, 6 * wave(u)], "upper_body:rot": lambda u: [0, 0, 3 * wave(u, 0.3)],
                                                                                                                                          "right_arm:rot": lambda u: [0, 0, 40], "left_arm:rot": lambda u: [0, 0, -40]}, pri=130)
menv("minecraft:mule", "rain_head_low", "Mule Plodding Head-Low In The Rain", RAIN + " && q.ground_speed >= 0.01", 1.2, {"head_parts:rot": lambda u: [25, 0, 0], "left_ear:rot": lambda u: [30, 0, 0], "right_ear:rot": lambda u: [30, 0, 0]},
     layer="additive", pri=72)

# ============================================================================ creatures: snow and cold
SNOW = "q.is_cold"
menv("minecraft:sheep", "cold_fluffed", "Sheep Fleece Fluffed Against The Cold", SNOW + " && q.ground_speed < 0.01", 3.0, {"body:scl": lambda u: [1.08, 1.06, 1.06], "head:rot": lambda u: [10, 0, 0]}, layer="additive", pri=73)
menv("minecraft:cow", "cold_breath", "Cow Breathing Steam In The Cold", SNOW + " && q.ground_speed < 0.01", 2.6, {"head:rot": lambda u: [6 * spike(u, 0.3, 4), 0, 0], "body:scl": lambda u: [1, 1 + 0.02 * wave(u), 1]}, layer="additive", pri=73)
menv("minecraft:horse", "cold_stamp", "Horse Stamping Against The Cold", SNOW + " && q.ground_speed < 0.01", 2.0, {"right_front_leg:rot": lambda u: [-30 * spike(u, 0.2, 4), 0, 0], "left_front_leg:rot": lambda u: [-30 * spike(u, 0.7, 4), 0, 0],
                                                                                                                 "head_parts:rot": lambda u: [10, 0, 0]})
menv("minecraft:wolf", "cold_curl", "Wolf Curled Nose-To-Tail In The Snow", SNOW + " && q.ground_speed < 0.01 && q.idle_time > 12 && !q.is_sitting", 3.0, {
    "mw_center:pos": lambda u: move(0, -4, 0), "mw_center:rot": lambda u: tilt(0, 0, 20), "head:rot": lambda u: [30, -70, 0], "tail:rot": lambda u: [20, -70, 0],
    "left_front_leg:rot": lambda u: [-80, 0, 0], "right_front_leg:rot": lambda u: [-80, 0, 0], "left_hind_leg:rot": lambda u: [80, 0, 0], "right_hind_leg:rot": lambda u: [80, 0, 0]})
menv("minecraft:fox", "snow_tail_wrap", "Snow Fox Wrapped In Its Tail", SNOW + " && q.ground_speed < 0.01 && q.idle_time > 6 && !q.is_sitting && !q.is_sleeping", 3.0, {"tail:rot": lambda u: [20, -60, 0], "head:rot": lambda u: [20, -30, 0],
                                                                                                                                                                  "mw_center:pos": lambda u: move(0, -1.5, 0)})
menv("minecraft:rabbit", "snow_hop_tracks", "Rabbit Bounding Over Fresh Snow", SNOW + " && q.ground_speed >= 0.01 && q.surface == 'snow'", 0.6, {"mw_center:rot": lambda u: tilt(-10 * wave(u), 0, 0)}, layer="additive", pri=73)
menv("minecraft:polar_bear", "snow_roll", "Polar Bear Rolling In The Snow", SNOW + " && q.surface == 'snow' && q.ground_speed < 0.01 && q.trait_energy > 0.5", 3.0, {
    "mw_center:rot": lambda u: tilt(0, 0, 180 * max(0, wave(u)) ** 1.5), "left_front_leg:rot": lambda u: [-40 * max(0, wave(u)), 0, 0], "right_hind_leg:rot": lambda u: [40 * max(0, wave(u)), 0, 0]})
menv("minecraft:goat", "cold_proud", "Goat Standing Proud In The Snow", SNOW + " && q.ground_speed < 0.01", 4.0, {"head:rot": lambda u: [-14, 30 * wave(u), 0], "mw_center:pos": lambda u: move(0, 0.5, 0)})
menv("minecraft:llama", "cold_content", "Llama Content In Its Thick Wool", SNOW + " && q.ground_speed < 0.01", 3.4, {"head:rot": lambda u: [-6, 0, 6 * wave(u)], "mw_center:rot": lambda u: tilt(0, 0, 1.5 * wave(u))})
menv("minecraft:chicken", "cold_puffball", "Chicken Puffed Into A Ball", SNOW + " && q.ground_speed < 0.01", 2.0, {"body:scl": lambda u: [1.18, 1.14, 1.18], "head:pos": lambda u: move(0, -0.8, -0.8), "mw_center:pos": lambda u: move(0, -1.2, 0)})
menv("minecraft:camel", "cold_shiver", "Desert Camel Shivering In The Snow", SNOW, 0.3, {"body:rot": lambda u: [0, 0, 1.2 * wave(u)], "head:rot": lambda u: [0, 0.8 * wave(u, 0.3), 0]}, layer="additive", pri=73)
menv("minecraft:parrot", "cold_shiver", "Parrot Shivering In The Cold", SNOW + " && !q.is_flying", 0.25, {"body:rot": lambda u: [0, 0, 2 * wave(u)], "feather:rot": lambda u: [-6 * wave(u, 0.2), 0, 0]}, layer="additive", pri=73)
menv("minecraft:panda", "snow_tumble", "Panda Tumbling In Fresh Snow", SNOW + " && q.surface == 'snow' && q.ground_speed < 0.01 && !q.is_sitting", 2.4, {"mw_center:rot": lambda u: tilt(0, 0, 90 * max(0, wave(u))), "head:rot": lambda u: [20, 0, 0]})
menv("minecraft:bee", "cold_sluggish", "Bee Sluggish In The Cold", SNOW + " && q.is_flying", 1.4, {"bone:pos": lambda u: move(0, -1.2 + 0.4 * wave(u), 0), "bone:rot": lambda u: tilt(6, 0, 3 * wave(u))}, layer="additive", pri=73)
menv("minecraft:skeleton", "powder_freeze", "Skeleton Freezing In Powder Snow", "q.freezing > 0.5", 0.2, {"body:rot": lambda u: [0, 0, 2 * wave(u)], "right_arm:rot": lambda u: arm('r', 0, -8), "left_arm:rot": lambda u: arm('l', 0, -8),
                                                                                                    "head:rot": lambda u: [10, 2 * wave(u, 0.3), 0]}, pri=140)

# ============================================================================ creatures: heat
HEAT = "q.temperature > 1.5 && !q.is_night && q.sky_exposed"
menv("minecraft:wolf", "heat_pant", "Wolf Panting In The Heat", HEAT, 0.5, {"head:rot": lambda u: [-4 * wave(u, 0, 2), 0, 0], "upper_body:scl": lambda u: [1, 1 + 0.04 * wave(u, 0, 2), 1]}, layer="additive", pri=74)
menv("minecraft:cow", "heat_seek_shade", "Cow Drooping In The Heat", HEAT + " && q.ground_speed < 0.01", 3.0, {"head:rot": lambda u: [30, 0, 0], "mw_center:pos": lambda u: move(0, -0.6, 0), "mw_center:rot": lambda u: tilt(4, 0, 0)})
menv("minecraft:sheep", "heat_pant", "Sheep Panting Under Its Fleece", HEAT, 0.6, {"head:rot": lambda u: [-3 * wave(u, 0, 2), 0, 0], "body:scl": lambda u: [1, 1 + 0.03 * wave(u, 0, 2), 1]}, layer="additive", pri=74)
menv("minecraft:chicken", "heat_wings_out", "Chicken Holding Its Wings Out To Cool", HEAT + " && q.ground_speed < 0.01", 2.0, {"right_wing:rot": lambda u: [0, 0, 30], "left_wing:rot": lambda u: [0, 0, -30], "head:rot": lambda u: [0, 0, 6 * wave(u)]})
menv("minecraft:horse", "heat_swish", "Horse Swishing At Flies In The Heat", HEAT, 1.4, {"tail:rot": lambda u: [0, 40 * wave(u), 0], "head_parts:rot": lambda u: [0, 15 * spike(u, 0.6, 6), 0]}, layer="additive", pri=74)
menv("minecraft:cat", "heat_sprawl", "Cat Sprawled Flat In The Heat", HEAT + " && q.ground_speed < 0.01 && !q.is_sitting && q.idle_time > 8", 4.0, {
    "mw_center:pos": lambda u: move(0, -3.5, 0), "left_front_leg:rot": lambda u: [-90, 0, 0], "right_front_leg:rot": lambda u: [-90, 0, 0], "left_hind_leg:rot": lambda u: [90, 0, 0], "right_hind_leg:rot": lambda u: [90, 0, 0],
    "head:rot": lambda u: [10, 0, 20]})
menv("minecraft:fox", "heat_pant", "Fox Panting In The Heat", HEAT, 0.45, {"head:rot": lambda u: [-5 * wave(u, 0, 2), 0, 0], "body:scl": lambda u: [1, 1 + 0.03 * wave(u, 0, 2), 1]}, layer="additive", pri=74)
menv("minecraft:polar_bear", "heat_miserable", "Polar Bear Miserable In The Heat", HEAT + " && q.ground_speed < 0.01", 3.0, {"mw_center:pos": lambda u: move(0, -2, 0), "head:rot": lambda u: [30, 0, 6 * wave(u)],
                                                                                                                           "left_front_leg:rot": lambda u: [-30, 0, -20], "right_front_leg:rot": lambda u: [-30, 0, 20]})
menv("minecraft:camel", "heat_content", "Camel Content Under The Desert Sun", HEAT + " && q.ground_speed < 0.01", 5.0, {"head:rot": lambda u: [-8, 20 * wave(u, 0, 0.5), 0], "hump:scl": lambda u: [1, 1 + 0.02 * wave(u), 1]})
menv("minecraft:rabbit", "heat_ear_cool", "Rabbit Cooling Itself Through Its Ears", HEAT + " && q.ground_speed < 0.01", 2.0, {"right_ear:rot": lambda u: [-10, 0, 20], "left_ear:rot": lambda u: [-10, 0, -20], "nose:rot": lambda u: [3 * wave(u, 0, 4), 0, 0]})

# ============================================================================ creatures: night, darkness, fire
menv("minecraft:cat", "night_prowl", "Cat Prowling Wide-Eyed At Night", "q.is_night && q.ground_speed >= 0.01 && !q.is_tame", 1.4, {"tail1:rot": lambda u: [-50, 0, 0], "tail2:rot": lambda u: [-20, 20 * wave(u), 0],
                                                                                                                                    "mw_center:rot": lambda u: tilt(0, 6 * wave(u), 0)},
     layer="additive", pri=74)
menv("minecraft:fox", "night_hunt", "Fox Hunting By Moonlight", "q.is_night && q.ground_speed >= 0.01 && !q.is_crouching", 1.2, {"head:rot": lambda u: [14, 10 * wave(u), 0], "right_ear:rot": lambda u: [-15, 0, 0], "left_ear:rot": lambda u: [-15, 0, 0]},
     layer="additive", pri=74)
menv("minecraft:wolf", "night_watch", "Wolf Keeping Night Watch", "q.is_night && q.ground_speed < 0.01 && !q.is_sitting", 4.0, {"head:rot": lambda u: [-8, 40 * wave(u), 0], "tail:rot": lambda u: [-10, 0, 0]}, pri=110)
menv("minecraft:horse", "night_wary", "Horse Wary Of The Night", "q.is_night && q.ground_speed < 0.01 && !q.has_rider && q.idle_time < 20", 3.0, {"head_parts:rot": lambda u: [-20, 25 * wave(u), 0], "left_ear:rot": lambda u: [0, 20 * wave(u), 0],
                                                                                                                                                  "right_ear:rot": lambda u: [0, -20 * wave(u, 0.3), 0]})
menv("minecraft:rabbit", "night_freeze", "Rabbit Freezing In The Dark", "q.is_night && q.ground_speed < 0.01 && q.light < 6", 3.0, {"mw_center:pos": lambda u: move(0, -0.4, 0), "right_ear:rot": lambda u: [-10, 0, 0], "left_ear:rot": lambda u: [-10, 0, 0],
                                                                                                                                  "nose:rot": lambda u: [4 * spike(u, 0.5, 6), 0, 0]})
menv("minecraft:sheep", "dark_huddle", "Sheep Pressed Together In The Dark", "q.light < 4 && q.ground_speed < 0.01", 2.0, {"mw_center:pos": lambda u: move(0, -0.5, 0), "head:rot": lambda u: [20, 15 * wave(u), 0]})
menv("minecraft:horse", "dark_skittish", "Horse Skittish In The Dark", "q.light < 4 && q.ground_speed < 0.05", 0.8, {"head_parts:rot": lambda u: [-15, 10 * wave(u), 0], "left_front_leg:rot": lambda u: [-20 * spike(u, 0.3, 6), 0, 0]},
     layer="additive", pri=74)
menv("minecraft:cat", "dark_eyes", "Cat Perfectly Calm In The Dark", "q.light < 4 && q.ground_speed < 0.01 && !q.is_lying", 4.0, {"head:rot": lambda u: [-4, 30 * wave(u), 0], "tail2:rot": lambda u: [0, 10 * wave(u, 0, 0.5), 0]}, pri=108)
FIRE = "q.near_fire && !q.is_on_fire"
menv("minecraft:cow", "fire_back_away", "Cow Backing Away From Fire", FIRE + " && q.ground_speed < 0.05", 1.2, {"head:rot": lambda u: [-20, 20 * wave(u, 0, 0.5), 0], "mw_center:rot": lambda u: tilt(-6, 0, 0)}, pri=125)
menv("minecraft:sheep", "fire_wary", "Sheep Wary Of The Flames", FIRE + " && q.ground_speed < 0.05", 1.0, {"head:rot": lambda u: [-25, 25 * wave(u), 0], "mw_center:pos": lambda u: move(0, 0.4, 0)}, pri=125)
menv("minecraft:horse", "fire_shy", "Horse Shying From Fire", FIRE, 0.8, {"head_parts:rot": lambda u: [-35, 15 * wave(u), 0], "tail:rot": lambda u: [-30, 0, 0], "left_front_leg:rot": lambda u: [-40 * spike(u, 0.3, 4), 0, 0]}, pri=126)
menv("minecraft:pig", "fire_squeal", "Pig Squealing Near Fire", FIRE, 0.5, {"head:rot": lambda u: [-20 + 10 * wave(u, 0, 2), 0, 0], "mw_center:pos": lambda u: move(0, 0.6 * max(0, wave(u)), 0)}, pri=125)
menv("minecraft:chicken", "fire_flap", "Chicken Flapping Away From Fire", FIRE, 0.3, {"right_wing:rot": lambda u: [0, 0, 60 + 30 * wave(u)], "left_wing:rot": lambda u: [0, 0, -60 - 30 * wave(u)]}, pri=125)
menv("minecraft:cat", "fire_warm_loaf", "Cat Loafing By The Warm Fire", "q.near_fire && q.ground_speed < 0.01 && !q.is_sitting && !q.is_lying", 4.0, {
    "mw_center:pos": lambda u: move(0, -3, 0), "left_front_leg:rot": lambda u: [-85, 0, 0], "right_front_leg:rot": lambda u: [-85, 0, 0], "left_hind_leg:rot": lambda u: [85, 0, 0], "right_hind_leg:rot": lambda u: [85, 0, 0],
    "head:rot": lambda u: [10 + 6 * spike(u, 0.5, 4), 0, 0], "body:scl": lambda u: [1, 1 + 0.02 * wave(u), 1]}, pri=124)
menv("minecraft:wolf", "fire_rest", "Wolf Resting By The Campfire", "q.near_fire && q.ground_speed < 0.01 && !q.is_sitting && q.is_tame", 4.0, {
    "mw_center:pos": lambda u: move(0, -4, 0), "left_front_leg:rot": lambda u: [-85, 0, 0], "right_front_leg:rot": lambda u: [-85, 0, 0], "left_hind_leg:rot": lambda u: [85, 0, 0], "right_hind_leg:rot": lambda u: [85, 0, 0],
    "head:rot": lambda u: [20, 0, 0], "tail:rot": lambda u: [0, 10 * wave(u, 0, 0.5), 0]}, pri=124)
menv("minecraft:zombie", "fire_recoil", "Zombie Recoiling From Fire", FIRE, 0.8, {"right_arm:rot": lambda u: arm('r', 130, -10, 30), "body:rot": lambda u: tilt(-10, 0, 0), "head:rot": lambda u: [-10, 15 * wave(u), 0]}, pri=135)

# ============================================================================ creatures: water, ice, wind, terrain
SHALLOW = "q.is_in_water && q.is_on_ground && !q.is_underwater"
menv("minecraft:horse", "shallows_paw", "Horse Pawing At The Shallows", SHALLOW + " && q.ground_speed < 0.01", 1.4, {"right_front_leg:rot": lambda u: [-40 * max(0, wave(u)) + 15 * max(0, -wave(u)), 0, 0],
                                                                                                                    "head_parts:rot": lambda u: [30, 0, 0]}, pri=126)
menv("minecraft:cow", "shallows_drink", "Cow Drinking At The Water's Edge", SHALLOW + " && q.ground_speed < 0.01", 2.4, {"head:rot": lambda u: [60 + 4 * wave(u, 0, 4), 0, 0], "mw_center:rot": lambda u: tilt(6, 0, 0)}, pri=126)
menv("minecraft:wolf", "shallows_play", "Wolf Splashing In The Shallows", SHALLOW, 0.6, {"left_front_leg:rot": lambda u: [-50 * max(0, wave(u)), 0, 0], "right_front_leg:rot": lambda u: [-50 * max(0, wave(u, 0.5)), 0, 0],
                                                                                       "tail:rot": lambda u: [-20, 30 * wave(u), 0], "head:rot": lambda u: [20 * wave(u, 0, 2), 0, 0]}, pri=126)
menv("minecraft:sheep", "shallows_reluctant", "Sheep Reluctant In The Shallows", SHALLOW, 1.2, {"head:rot": lambda u: [-20, 20 * wave(u), 0], "mw_center:rot": lambda u: tilt(-4, 0, 2 * wave(u))}, pri=126)
menv("minecraft:pig", "shallows_snout_dip", "Pig Dipping Its Snout In The Shallows", SHALLOW + " && q.ground_speed < 0.01", 1.2, {"head:rot": lambda u: [50 + 10 * spike(u, 0.3, 3, 2), 0, 8 * wave(u)],
                                                                                                                                  "mw_center:pos": lambda u: move(0, -0.4, 0.4), "mw_center:rot": lambda u: tilt(8, 0, 0)}, pri=126)
menv("minecraft:cat", "shallows_disgust", "Cat Shaking Each Wet Paw", SHALLOW, 0.8, {"left_front_leg:rot": lambda u: [-40 * spike(u, 0.2, 3), 0, 0], "right_front_leg:rot": lambda u: [-40 * spike(u, 0.7, 3), 0, 0], "head:rot": lambda u: [20, 0, 0]},
     pri=126)
menv("minecraft:fox", "shallows_fish_pounce", "Fox Pouncing At Fish In The Shallows", SHALLOW + " && q.ground_speed < 0.01", 2.0, {"mw_center:rot": lambda u: tilt(30 * spike(u, 0.5, 4), 0, 0), "head:rot": lambda u: [30, 0, 0],
                                                                                                                                   "left_front_leg:rot": lambda u: [-60 * spike(u, 0.5, 4), 0, 0], "right_front_leg:rot": lambda u: [-60 * spike(u, 0.5, 4), 0, 0]}, pri=126)
menv("minecraft:chicken", "shallows_hop_out", "Chicken Hopping Out Of Puddles", SHALLOW, 0.4, {"mw_center:pos": lambda u: move(0, 1 * max(0, wave(u)), 0), "right_wing:rot": lambda u: [0, 0, 40 * max(0, wave(u))], "left_wing:rot": lambda u: [0, 0, -40 * max(0, wave(u))]},
     pri=126)
ICE = "q.surface == 'glass' && q.ground_speed >= 0.02"
menv("minecraft:cow", "ice_splay", "Cow Splay-Legged On Ice", ICE, 1.0, {"left_front_leg:rot": lambda u: [0, 0, -14 - 6 * wave(u)], "right_front_leg:rot": lambda u: [0, 0, 14 + 6 * wave(u)], "mw_center:rot": lambda u: tilt(0, 0, 5 * wave(u))},
     layer="additive", pri=75)
menv("minecraft:pig", "ice_slide", "Pig Sliding On Ice", ICE, 0.8, {"mw_center:rot": lambda u: tilt(0, 20 * wave(u, 0, 0.5), 0), "left_front_leg:rot": lambda u: [-20, 0, 0], "right_front_leg:rot": lambda u: [-20, 0, 0]}, layer="additive", pri=75)
menv("minecraft:horse", "ice_careful", "Horse Picking Its Way Across Ice", ICE, 1.6, {"head_parts:rot": lambda u: [40, 0, 0], "mw_center:rot": lambda u: tilt(0, 0, 2 * wave(u))}, layer="additive", pri=75)
menv("minecraft:wolf", "ice_scrabble", "Wolf Scrabbling On Ice", ICE, 0.4, {"left_front_leg:rot": lambda u: [-30 * wave(u), 0, 0], "right_front_leg:rot": lambda u: [-30 * wave(u, 0.5), 0, 0], "mw_center:rot": lambda u: tilt(0, 10 * wave(u), 0)},
     layer="additive", pri=75)
menv("minecraft:cat", "ice_skid", "Cat Skidding On Ice", ICE, 0.7, {"mw_center:rot": lambda u: tilt(0, 0, 10 * wave(u)), "tail1:rot": lambda u: [-30, 30 * wave(u), 0]}, layer="additive", pri=75)
menv("minecraft:sheep", "ice_slip", "Sheep Slipping On Ice", ICE, 0.9, {"left_hind_leg:rot": lambda u: [30 * spike(u, 0.4, 4), 0, -10], "mw_center:rot": lambda u: tilt(-8 * spike(u, 0.4, 4), 0, 0)}, layer="additive", pri=75)
WIND = "q.wind > 0.6"
menv("minecraft:horse", "wind_mane", "Horse's Mane Streaming In The Wind", WIND, 0.8, {"mane:rot": lambda u: [0, 0, 14 + 6 * wave(u, 0, 2)], "tail:rot": lambda u: [-20, 20 + 8 * wave(u, 0, 2), 0]}, layer="additive", pri=76)
menv("minecraft:wolf", "wind_fur", "Wolf Leaning Into The Wind", WIND + " && q.ground_speed < 0.01", 1.4, {"upper_body:scl": lambda u: [1.04 + 0.02 * wave(u, 0, 3), 1.03, 1], "tail:rot": lambda u: [-10, 30 + 6 * wave(u, 0, 3), 0], "head:rot": lambda u: [8, 0, 0]},
     layer="additive", pri=76)
menv("minecraft:camel", "wind_squint", "Camel Squinting Into Blowing Sand", WIND + " && q.temperature > 1.5", 2.0, {"head:rot": lambda u: [10, 0, 0], "left_ear:rot": lambda u: [30, 0, 0], "right_ear:rot": lambda u: [30, 0, 0]}, layer="additive", pri=76)
menv("minecraft:llama", "wind_ears_back", "Llama Pinning Back In The Wind", WIND, 1.6, {"head:rot": lambda u: [6, 0, 2 * wave(u, 0, 3)]}, layer="additive", pri=76)
menv("minecraft:bat", "wind_buffeted", "Bat Buffeted By The Wind", WIND + " && !q.is_sleeping", 0.6, {"mw_root:rot": lambda u: tilt(6 * wave(u, 0.3), 0, 14 * wave(u))}, layer="additive", pri=76)
menv("minecraft:chicken", "wind_ruffled", "Chicken Ruffled By The Wind", WIND, 0.5, {"body:scl": lambda u: [1.03 + 0.02 * wave(u, 0, 2), 1, 1], "right_wing:rot": lambda u: [0, 0, 8 * wave(u)], "left_wing:rot": lambda u: [0, 0, -8 * wave(u, 0.2)]},
     layer="additive", pri=76)
menv("minecraft:rabbit", "powder_snow_sink", "Rabbit Floundering In Powder Snow", "q.feet_block == 'powder_snow'", 0.4, {"left_front_leg:rot": lambda u: [-40 * wave(u), 0, 0], "right_front_leg:rot": lambda u: [-40 * wave(u, 0.5), 0, 0],
                                                                                                                       "head:rot": lambda u: [-30, 0, 0]}, pri=128)
menv("minecraft:fox", "powder_snow_dive", "Fox Burrowing Into Powder Snow", "q.feet_block == 'powder_snow'", 0.8, {"mw_center:rot": lambda u: tilt(30, 0, 0), "head:rot": lambda u: [30, 20 * wave(u), 0]}, pri=128)
menv("minecraft:rabbit", "grass_hide", "Rabbit Hiding In Tall Grass", "q.feet_block == 'foliage' && q.ground_speed < 0.01", 3.0, {"mw_center:pos": lambda u: move(0, -1.2, 0), "right_ear:rot": lambda u: [-10, 20 * wave(u), 0],
                                                                                                                                 "left_ear:rot": lambda u: [-10, -20 * wave(u, 0.5), 0], "nose:rot": lambda u: [5 * spike(u, 0.2, 4, 3), 0, 0]},
     pri=112)
menv("minecraft:fox", "bush_hide", "Fox Lurking In The Bushes", "q.feet_block == 'foliage' && q.ground_speed < 0.01 && !q.is_sleeping", 3.0, {"mw_center:pos": lambda u: move(0, -1.2, 0), "head:rot": lambda u: [-6, 20 * wave(u, 0, 0.5), 0]},
     pri=112)
menv("minecraft:cat", "flower_bat", "Cat Batting At Flowers", "q.feet_block == 'foliage' && q.ground_speed < 0.01 && !q.is_sitting", 1.6, {"right_front_leg:rot": lambda u: [-70 * spike(u, 0.3, 3), 0, 10], "head:rot": lambda u: [24, 0, 10 * wave(u)]},
     pri=112)
menv("minecraft:horse", "soul_sand_struggle", "Horse Struggling Through Soul Sand", "q.surface == 'soul' && q.ground_speed >= 0.01", 1.0, {"head_parts:rot": lambda u: [-10 + 8 * wave(u, 0, 2), 0, 0], "mw_center:rot": lambda u: tilt(6 * wave(u), 0, 0)},
     layer="additive", pri=77)
menv("minecraft:bee", "honey_delight", "Bee Delighting In Honey", "q.feet_block == 'honey'", 1.0, {"bone:rot": lambda u: tilt(0, 0, 10 * wave(u)), "front_legs:rot": lambda u: [-20 * wave(u, 0, 2), 0, 0]}, pri=128)
menv("minecraft:spider", "web_at_home", "Spider At Home In Its Web", "q.feet_block == 'cobweb'", 4.0, {"head:rot": lambda u: [0, 20 * wave(u), 0], "body1:scl": lambda u: [1, 1 + 0.03 * wave(u), 1]}, pri=128)
menv("minecraft:drowned", "storm_surface", "Drowned Surfacing In A Storm", "q.is_thundering && q.is_in_water && !q.is_underwater", 2.4, {"head:rot": lambda u: [-25, 30 * wave(u), 0], "right_arm:rot": lambda u: arm('r', 150, 20 * wave(u))}, pri=130)

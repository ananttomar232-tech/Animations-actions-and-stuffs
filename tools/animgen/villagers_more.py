"""Villagers part 2: profession mannerisms and trade reactions, conversation variety, children, weather, golems."""
from core import arm, leg
from mobkit import mob, life, loop_state, beat, Z, state, event, wave, cwave, tilt, move
from villagers import CAT, ALIVE, STILL, VIL, f, spike

T = VIL

# ---------------------------------------------------------------- profession vocal mannerisms (fired on each ambient "hrmm")
MANNER = {
    "farmer": ("Farmer Squinting At The Sky", {"head:rot": [(0, Z), (0.4, [-30, 0, 0]), (1.2, [-28, 10, 0]), (1.6, Z)], "arms:rot": [(0, Z), (0.4, [-150, 0, 0]), (1.2, [-150, 0, 0]), (1.6, Z)]}),
    "librarian": ("Librarian Sage Nod", {"head:rot": [(0, Z), (0.3, [20, 0, 0]), (0.6, [6, 0, 0]), (0.9, [20, 0, 0]), (1.6, Z)], "nose:rot": [(0, Z), (0.3, [6, 0, 0]), (1.6, Z)]}),
    "armorer": ("Armorer Cracking His Neck", {"head:rot": [(0, Z), (0.3, [0, 0, 25]), (0.5, [0, 0, 22]), (0.8, [0, 0, -25]), (1.0, [0, 0, -22]), (1.6, Z)]}),
    "butcher": ("Butcher Sniffing The Air", {"head:rot": [(0, Z), (0.3, [-14, 0, 0]), (1.0, [-14, 14, 0]), (1.6, Z)], "nose:rot": [(0, Z), (0.2, [-6, 0, 0]), (0.35, Z), (0.5, [-6, 0, 0]), (0.65, Z), (1.6, Z)]}),
    "cartographer": ("Cartographer Pointing The Way", {"arms:rot": [(0, Z), (0.4, [-95, 30, 0]), (1.2, [-95, 30, 0]), (1.6, Z)], "head:rot": [(0, Z), (0.4, [0, 30, 0]), (1.2, [0, 30, 0]), (1.6, Z)]}),
    "cleric": ("Cleric Solemn Bow", {"body:rot": [(0, Z), (0.5, tilt(25, 0, 0)), (1.1, tilt(25, 0, 0)), (1.6, Z)], "head:rot": [(0, Z), (0.5, [25, 0, 0]), (1.6, Z)]}),
    "fisherman": ("Fisherman Spinning A Yarn", {"arms:rot": [(0, Z), (0.3, [-60, 0, 30]), (0.7, [-60, 0, -30]), (1.1, [-60, 0, 30]), (1.6, Z)], "head:rot": [(0, Z), (0.4, [-8, 0, 12]), (1.6, Z)]}),
    "fletcher": ("Fletcher Testing The Wind", {"arms:rot": [(0, Z), (0.4, [-170, 0, 0]), (1.2, [-170, 0, 0]), (1.6, Z)], "head:rot": [(0, Z), (0.4, [-20, -20, 0]), (1.2, [-20, 20, 0]), (1.6, Z)]}),
    "leatherworker": ("Leatherworker Tugging His Apron", {"arms:rot": [(0, Z), (0.3, [-20, 0, 0]), (0.5, [-10, 0, 0]), (0.7, [-20, 0, 0]), (1.6, Z)], "body:rot": [(0, Z), (0.3, tilt(-6)), (1.6, Z)],
                                                           "jacket:scl": [(0, [1, 1, 1]), (0.3, [1.03, 1, 1.03]), (0.7, [1, 1, 1])]}),
    "mason": ("Mason Rubbing His Back", {"body:rot": [(0, Z), (0.4, tilt(-14, 0, 0)), (1.0, tilt(-10, 0, 0)), (1.6, Z)], "arms:pos": [(0, Z), (0.4, move(0, 0, 2)), (1.0, move(0, 0, 2)), (1.6, Z)]}),
    "shepherd": ("Shepherd Whistling For The Flock", {"head:rot": [(0, Z), (0.3, [-12, 0, 0]), (1.2, [-12, 0, 0]), (1.6, Z)], "arms:rot": [(0, Z), (0.3, [-130, 0, 0]), (1.2, [-130, 0, 0]), (1.6, Z)],
                                                       "nose:scl": [(0, [1, 1, 1]), (0.4, [1, 1, 1.15]), (1.2, [1, 1, 1.15]), (1.6, [1, 1, 1])]}),
    "toolsmith": ("Toolsmith Flexing His Grip", {"arms:rot": [(0, Z), (0.3, [-70, 0, 0]), (0.5, [-75, 0, 10]), (0.7, [-70, 0, -10]), (0.9, [-75, 0, 10]), (1.6, Z)], "head:rot": [(0, Z), (0.3, [25, 0, 0]), (1.6, Z)]}),
    "weaponsmith": ("Weaponsmith Stern Stare", {"head:rot": [(0, Z), (0.3, [-4, 0, 0]), (1.3, [-4, 0, 0]), (1.6, Z)], "body:rot": [(0, Z), (0.3, tilt(-8, 0, 0)), (1.3, tilt(-8, 0, 0)), (1.6, Z)],
                                                 "mw_root:pos": [(0, Z), (0.3, move(0, 0.6, 0)), (1.3, move(0, 0.6, 0)), (1.6, Z)]}),
}
for prof, (name, tracks) in MANNER.items():
    beat("villager.%s.mannerism" % prof, name, CAT, T, event("vocalize", ALIVE + " && q.profession == '%s' && !q.in_conversation" % prof), 1.6, f("villager/" + prof), tracks, layer="gesture", pri=145)

# ---------------------------------------------------------------- profession-specific reactions to a completed trade
TRADE = {
    "farmer": ("Farmer Hefting The Harvest", 1.4, {"arms:rot": [(0, Z), (0.4, [-100, 0, 0], "out_back"), (0.9, [-90, 0, 0]), (1.4, Z)], "mw_root:pos": [(0, Z), (0.4, move(0, 1, 0)), (0.8, Z)]}),
    "librarian": ("Librarian Tucking Away A Book", 1.4, {"arms:rot": [(0, Z), (0.5, [-30, 0, 30]), (1.0, [-20, 0, 40]), (1.4, Z)], "head:rot": [(0, Z), (0.5, [10, -20, 0]), (1.4, Z)]}),
    "armorer": ("Armorer Knocking On The Plate", 1.2, {"arms:rot": [(0, Z), (0.2, [-60, 0, 0]), (0.3, [-40, 0, 0]), (0.4, [-60, 0, 0]), (0.5, [-40, 0, 0]), (1.2, Z)], "head:rot": [(0, Z), (0.2, [15, 0, 0]), (1.2, Z)]}),
    "butcher": ("Butcher Slapping The Counter", 1.0, {"arms:rot": [(0, Z), (0.25, [-90, 0, 0]), (0.35, [-30, 0, 0], "in_quart"), (1.0, Z)], "body:rot": [(0, Z), (0.35, tilt(12)), (1.0, Z)]}),
    "cartographer": ("Cartographer Rolling Up A Map", 1.6, {"arms:rot": [(0, Z), (0.4, [-60, 0, 0]), (1.6, Z)], "arms:scl": [(0, [1.3, 1, 1]), (0.9, [0.9, 1, 1]), (1.6, [1, 1, 1])]}),
    "cleric": ("Cleric Blessing The Customer", 1.8, {"arms:rot": [(0, Z), (0.5, [-120, 0, 0]), (0.9, [-120, 0, 20]), (1.3, [-120, 0, -20]), (1.8, Z)], "head:rot": [(0, Z), (0.5, [-10, 0, 0]), (1.8, Z)]}),
    "fisherman": ("Fisherman Holding Up A Catch", 1.6, {"arms:rot": [(0, Z), (0.4, [-150, 0, 0]), (1.1, [-150, 0, 10]), (1.6, Z)], "head:rot": [(0, Z), (0.4, [-30, 0, 0]), (1.6, Z)],
                                                        "mw_root:rot": [(0, Z), (0.4, tilt(-4, 0, 0)), (1.6, Z)]}),
    "fletcher": ("Fletcher Tipping His Cap", 1.2, {"arms:rot": [(0, Z), (0.35, [-170, 0, 0]), (0.6, [-170, 0, 0]), (1.2, Z)], "hat:rot": [(0, Z), (0.45, [-10, 0, 0]), (0.8, Z)],
                                                    "head:rot": [(0, Z), (0.45, [12, 0, 0]), (1.2, Z)]}),
    "leatherworker": ("Leatherworker Snapping A Hide", 1.0, {"arms:rot": [(0, Z), (0.25, [-90, 0, 0]), (0.35, [-50, 0, 0], "out_expo"), (1.0, Z)], "arms:scl": [(0, [1, 1, 1]), (0.35, [1.3, 1, 1]), (1.0, [1, 1, 1])]}),
    "mason": ("Mason Thumping A Brick", 1.0, {"arms:rot": [(0, Z), (0.3, [-100, 0, 0]), (0.42, [-40, 0, 0], "in_quart"), (1.0, Z)], "mw_root:pos": [(0, Z), (0.42, move(0, -0.6, 0)), (1.0, Z)]}),
    "shepherd": ("Shepherd Fluffing Fresh Wool", 1.4, {"arms:rot": [(0, Z), (0.3, [-70, 0, 0]), (1.4, Z)], "arms:pos": [(0, Z), (0.4, move(0.8, 0, 0)), (0.6, move(-0.8, 0, 0)), (0.8, move(0.8, 0, 0)), (1.4, Z)]}),
    "toolsmith": ("Toolsmith Spinning A Tool", 1.2, {"arms:rot": [(0, Z), (0.3, [-80, 0, 0]), (0.6, [-80, 0, 180]), (0.9, [-80, 0, 360]), (1.2, Z)]}),
    "weaponsmith": ("Weaponsmith Brandishing A Blade", 1.4, {"arms:rot": [(0, Z), (0.3, [-170, 0, 0], "out_quad"), (0.8, [-170, 0, 10]), (1.4, Z)], "body:rot": [(0, Z), (0.3, tilt(-10, 10, 0)), (1.4, Z)]}),
}
for prof, (name, L, tracks) in TRADE.items():
    beat("villager.%s.trade_flourish" % prof, name, CAT, T, event("trade_complete", ALIVE + " && q.profession == '%s'" % prof, weight=2), L, f("villager/" + prof), tracks, pri=161)

# ---------------------------------------------------------------- conversation variety
F = f("villager/social")
CONV = ALIVE + " && q.in_conversation"
loop_state("villager.whisper", "Villager Leaning In To Whisper", CAT, T, CONV + " && q.is_speaking && q.conversation_size == 2", 2.0, F, {
    "body:rot": lambda u: tilt(14, 0, 8), "head:rot": lambda u: [10, 0, 14 + 3 * wave(u, 0, 4)], "mw_root:pos": lambda u: move(0, -0.6, 0.6)}, pri=116)
loop_state("villager.storyteller", "Villager Telling A Grand Story", CAT, T, CONV + " && q.is_speaking && q.conversation_size >= 3", 3.0, F, {
    "arms:rot": lambda u: [-60 - 50 * max(0, wave(u)), 20 * wave(u, 0.2), 0], "body:rot": lambda u: tilt(-6 * max(0, wave(u)), 15 * wave(u, 0, 0.5), 0), "head:rot": lambda u: [-12 * max(0, wave(u)), -20 * wave(u, 0, 0.5), 0]},
    pri=117)
loop_state("villager.argue", "Villager Heated Argument", CAT, T, CONV + " && q.is_speaking && q.mood < 0.3", 0.9, F, {
    "arms:rot": lambda u: [-70 + 30 * wave(u, 0, 2), 0, 0], "body:rot": lambda u: tilt(10 * max(0, wave(u, 0, 2)), 0, 0), "head:rot": lambda u: [8 * wave(u, 0, 2), 0, 0], "mw_root:pos": lambda u: move(0, 0, 0.6 * max(0, wave(u, 0, 2)))},
    pri=118)
beat("villager.shrug", "Villager Shrugging", CAT, T, event("speak", ALIVE + " && q.mood >= 0.35 && q.mood <= 0.6", chance=0.4), 1.0, F, {
    "arms:pos": [(0, Z), (0.25, move(0, 1.5, 0), "out_quad"), (0.6, move(0, 1.5, 0)), (1.0, Z)], "head:rot": [(0, Z), (0.25, [0, 0, 14]), (0.6, [0, 0, 14]), (1.0, Z)]}, layer="gesture")
loop_state("villager.group_laugh", "Villagers Laughing Together", CAT, T, CONV + " && !q.is_speaking && q.mood > 0.75 && q.conversation_size >= 3", 1.0, F, {
    "head:rot": lambda u: [-12 * max(0, wave(u, 0, 2)), 0, 6 * wave(u)], "body:rot": lambda u: tilt(-6 * max(0, wave(u, 0, 2)), 0, 0)}, pri=115, layer="additive")
loop_state("villager.sceptic_listen", "Villager Listening Sceptically", CAT, T, CONV + " && !q.is_speaking && q.trait_confidence > 0.7", 3.0, F, {
    "head:rot": lambda u: [-8, -14, 12], "body:rot": lambda u: tilt(-4, -10, 0), "nose:rot": lambda u: [0, 0, 4 * spike(u, 0.5, 4)]}, pri=115, layer="additive")
loop_state("villager.shy_listen", "Villager Listening Shyly", CAT, T, CONV + " && !q.is_speaking && q.trait_social < 0.3", 3.0, F, {
    "head:rot": lambda u: [24, 0, 0], "body:rot": lambda u: tilt(6, 0, 0), "arms:rot": lambda u: [-6, 0, 0], "mw_root:rot": lambda u: tilt(0, 0, 2 * wave(u))}, pri=115, layer="additive")
beat("villager.gesture_point", "Villager Pointing Something Out", CAT, T, event("speak", ALIVE + " && q.trait_curiosity > 0.6", chance=0.5), 1.6, F, {
    "arms:rot": [(0, Z), (0.35, [-90, 40, 0]), (1.2, [-90, 40, 0]), (1.6, Z)], "head:rot": [(0, Z), (0.35, [0, 40, 0]), (1.2, [0, 40, 0]), (1.6, Z)], "body:rot": [(0, Z), (0.35, tilt(0, 20, 0)), (1.6, Z)]},
    layer="gesture", pri=146)

# ---------------------------------------------------------------- children
F = f("villager/children")
beat("villager.child_wave", "Village Child Waving Excitedly", CAT, T, event("interacted", ALIVE + " && q.is_baby"), 1.2, F, {
    "arms:rot": [(0, Z), (0.2, [-160, 0, 20]), (0.35, [-160, 0, -20]), (0.5, [-160, 0, 20]), (0.65, [-160, 0, -20]), (1.2, Z)], "mw_root:pos": [(0, Z), (0.2, move(0, 1, 0)), (0.4, Z), (0.6, move(0, 1, 0)), (0.8, Z)]},
    pri=152, layer="gesture")
beat("villager.child_cry", "Village Child Bursting Into Tears", CAT, T, event("hurt", ALIVE + " && q.is_baby"), 2.0, F, {
    "arms:rot": [(0, Z), (0.2, [-140, 0, 0]), (1.6, [-140, 0, 0]), (2.0, Z)], "head:rot": [(0, Z), (0.2, [25, 0, 0]), (0.5, [25, 0, 8]), (0.8, [25, 0, -8]), (1.1, [25, 0, 8]), (2.0, Z)],
    "body:rot": [(0, Z), (0.3, tilt(6, 0, 0)), (2.0, Z)]}, pri=205, layer="reaction")
beat("villager.child_tumble", "Village Child Tumbling On Landing", CAT, T, event("land", ALIVE + " && q.is_baby && q.last_fall > 1.5"), 1.0, F, {
    "mw_root:rot": [(0, Z), (0.2, tilt(-30, 0, 0)), (0.5, tilt(-20, 0, 10)), (1.0, Z)], "mw_root:pos": [(0, Z), (0.2, move(0, -2, -1)), (1.0, Z)], "arms:rot": [(0, Z), (0.2, [-90, 0, 0]), (1.0, Z)]}, pri=160)
loop_state("villager.child_bed_bounce", "Village Child Bouncing Before Bed", CAT, T, ALIVE + " && q.is_baby && q.is_night && q.surface == 'wood' && q.ground_speed < 0.01", 0.6, F, {
    "mw_root:pos": lambda u: move(0, 2.5 * max(0, wave(u)), 0), "arms:rot": lambda u: [-90 * max(0, wave(u)), 0, 0], "right_leg:rot": lambda u: leg('r', -10 * max(0, wave(u)))}, group="vil_child", weight=2)

# ---------------------------------------------------------------- weather and mood
F = f("villager/weather")
loop_state("villager.cold_hug", "Villager Hugging Itself In The Cold", CAT, T, STILL + " && q.is_cold && !q.near_fire && !q.is_baby", 0.3, F, {
    "arms:rot": lambda u: [-30, 0, 0], "arms:scl": lambda u: [0.92, 1, 1], "body:rot": lambda u: tilt(10, 0, 1.5 * wave(u)), "head:rot": lambda u: [14, 0, 1.5 * wave(u, 0.3)]}, pri=116)
loop_state("villager.heat_fan", "Villager Fanning Itself In The Heat", CAT, T, STILL + " && q.temperature > 1.5 && !q.is_raining && !q.is_night", 0.5, F, {
    "arms:rot": lambda u: [-130 + 20 * wave(u), 0, 0], "head:rot": lambda u: [-15, 0, 0], "body:rot": lambda u: tilt(-4, 0, 0)}, pri=116)
beat("villager.thunder_flinch", "Villager Flinching At Thunder", CAT, T, event("vocalize", ALIVE + " && q.is_thundering"), 0.9, F, {
    "head:rot": [(0, Z), (0.08, [-25, 0, 0], "out_expo"), (0.5, [-20, 15, 0]), (0.9, Z)], "arms:rot": [(0, Z), (0.08, [-80, 0, 0]), (0.9, Z)], "mw_root:pos": [(0, Z), (0.08, move(0, 1, 0)), (0.3, Z)]},
    pri=148, layer="gesture")
loop_state("villager.sun_bask", "Villager Basking In The Sun", CAT, T, STILL + " && q.sky_exposed && !q.is_raining && q.time_of_day > 0.15 && q.time_of_day < 0.35 && q.idle_time > 12", 6.0, F, {
    "head:rot": lambda u: [-30 + 3 * wave(u), 0, 0], "body:rot": lambda u: tilt(-8, 0, 0), "arms:rot": lambda u: [-6, 0, 0], "mw_root:pos": lambda u: move(0, 0.2 * wave(u), 0)}, group="vil_idle", weight=2,
    layer="overlay", pri=108)
loop_state("villager.rainy_window", "Villager Watching The Rain Indoors", CAT, T, STILL + " && q.is_raining && !q.sky_exposed", 5.0, F, {
    "head:rot": lambda u: [-6, 25 * wave(u, 0, 0.5), 0], "body:rot": lambda u: tilt(4, 0, 4), "mw_root:rot": lambda u: tilt(0, 0, 3)}, pri=108)
loop_state("villager.bored_yawn", "Villager Bored Yawn", CAT, T, STILL + " && q.idle_time > 40 && !q.in_conversation", 4.0, F, {
    "head:rot": lambda u: [-30 * spike(u, 0.2, 2), 0, 0], "arms:rot": lambda u: [-140 * spike(u, 0.2, 2), 0, 0], "body:rot": lambda u: tilt(-10 * spike(u, 0.2, 2), 0, 0)}, group="vil_idle", weight=1,
    layer="overlay", pri=107)
loop_state("villager.wounded_hunch", "Wounded Villager Hunched Over", CAT, T, ALIVE + " && q.health < 0.35", 2.4, F, {
    "body:rot": lambda u: tilt(22, 0, 4), "arms:rot": lambda u: [-20, 0, 0], "arms:pos": lambda u: move(0, -1, 1), "head:rot": lambda u: [10 + 4 * wave(u), 0, 0]}, pri=122, layer="additive")

# ---------------------------------------------------------------- trader & golems
T, F = "minecraft:wandering_trader", f("wandering_trader")
beat("wandering_trader.yawn", "Wandering Trader Travel-Weary Yawn", CAT, T, event("vocalize", ALIVE + " && !q.is_trading"), 2.0, F, {
    "head:rot": [(0, Z), (0.6, [-30, 0, 0]), (1.3, [-28, 0, 6]), (2.0, Z)], "arms:rot": [(0, Z), (0.6, [-130, 0, 0]), (1.3, [-130, 0, 0]), (2.0, Z)], "body:rot": [(0, Z), (0.6, tilt(-10)), (2.0, Z)]}, layer="gesture")
loop_state("wandering_trader.invisible_sneak", "Wandering Trader Tiptoeing Unseen", CAT, T, ALIVE + " && q.is_invisible && q.ground_speed >= 0.01", 1.4, F, {
    "right_leg:rot": lambda u: leg('r', 30 * cwave(u) + 10), "left_leg:rot": lambda u: leg('l', -30 * cwave(u) + 10), "body:rot": lambda u: tilt(20, 0, 0), "mw_root:pos": lambda u: move(0, -1.5, 0),
    "arms:rot": lambda u: [-40, 0, 0]}, pri=110, layer="base")
loop_state("wandering_trader.call_llamas", "Wandering Trader Calling His Llamas", CAT, T, ALIVE + " && q.ground_speed < 0.01 && q.near_hostile == 0 && q.idle_time > 6", 3.0, F, {
    "head:rot": lambda u: [-10, 70 * spike(u, 0.2, 2), 0], "arms:rot": lambda u: [-100 * spike(u, 0.2, 2), 0, 0]}, group="trader_idle", weight=1)
T, F = "minecraft:iron_golem", f("iron_golem")
beat("iron_golem.crumble", "Iron Golem Crumbling Collapse", CAT, T, event("death"), 1.6, F, {
    "right_leg:rot": [(0, Z), (0.5, leg('r', 60)), (1.6, leg('r', 80))], "left_leg:rot": [(0, Z), (0.5, leg('l', 60)), (1.6, leg('l', 80))], "body:rot": [(0, Z), (0.6, tilt(20)), (1.6, tilt(60))],
    "mw_root:pos": [(0, Z), (0.6, move(0, -5, 0), "in_quad"), (1.6, move(0, -9, 0))], "right_arm:rot": [(0, Z), (1.6, arm('r', 40, 30))], "left_arm:rot": [(0, Z), (1.6, arm('l', 40, 30))]}, pri=300,
     events=[(0.6, "stomp", {"strength": "1"}), (0.6, "particle", {"particle": "dust_puff", "count": "20", "at": "feet", "spread": "1"})])
loop_state("iron_golem.watch_over", "Iron Golem Watching Over The Village", CAT, T, STILL + " && q.player_distance < 6 && !q.is_holding", 4.0, F, {
    "head:rot": lambda u: [24, 20 * wave(u, 0, 0.5), 0], "body:rot": lambda u: tilt(6, 0, 0)}, pri=110)
T, F = "minecraft:snow_golem", f("snow_golem")
loop_state("snow_golem.pumpkin_tilt", "Snow Golem Tilting Its Pumpkin", CAT, T, STILL + " && q.player_distance < 5", 2.4, F, {"head:rot": lambda u: [0, 0, 20 * wave(u, 0, 0.5)], "upper_body:rot": lambda u: [0, 0, -5 * wave(u, 0, 0.5)]},
           pri=110)
beat("snow_golem.melt_away", "Snow Golem Melting Away", CAT, T, event("death"), 1.4, F, {
    "head:pos": [(0, Z), (1.4, move(0, -12, 0), "in_quad")], "upper_body:scl": [(0, [1, 1, 1]), (1.4, [1.3, 0.2, 1.3])], "lower_body:scl": [(0, [1, 1, 1]), (1.4, [1.4, 0.5, 1.4])],
    "right_arm:rot": [(0, Z), (1.0, [0, 0, -60])], "left_arm:rot": [(0, Z), (1.0, [0, 0, 60])]}, pri=300, events=[(0.4, "particle", {"particle": "snow_puff", "count": "16", "at": "body", "spread": "0.6"})])

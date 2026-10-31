"""Villagers and humanoid NPCs: professions at work, village social life, trading, the wandering trader and golems.

The vanilla villager model has one crossed-arms part ("arms"), not two hands; work animations
move that block, the body and the head together instead of pretending there are separate hands.
"""
from core import arm, leg, biped, stroke
from mobkit import mob, life, loop_state, beat, driven, Z, state, event, wave, cwave, tilt, move

CAT = "villagers_npcs"
ALIVE = "!q.is_dead && !q.is_sleeping"
STILL = ALIVE + " && q.is_on_ground && q.ground_speed < 0.01"
WALKING = ALIVE + " && q.is_on_ground && q.ground_speed >= 0.01"
WORKTIME = " && q.time_of_day > 0.08 && q.time_of_day < 0.38 && !q.is_raining"
SAFE = " && !q.near_hostile && q.recent_hurt > 8"
VIL = "minecraft:villager"


def f(name):
    return "npcs/" + name


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def villager_walk(cid, name, T, when, L, F, pri=100, arms_fn=None, **kw):
    """Villager gait; the single crossed-arms part gets its own motion (bounce, pump, clutch) via arms_fn."""
    c = mob(cid, name, CAT, T, L, state(when, exit_delay=0.15), layer="base", pri=pri, file=F, **driven(L))
    biped(c, arms=False, **kw)
    c.bones.pop("head", None)
    if arms_fn:
        c.cycle("arms", "rotation", arms_fn)
    return c


def work(prof, cid, name, L, fns, weight=1, F=None):
    """Job-site work loop for one profession (daytime, safe, standing still)."""
    return loop_state("villager.%s.%s" % (prof, cid), name, CAT, VIL, STILL + WORKTIME + SAFE + " && q.profession == '%s'" % prof, L, F or f("villager/" + prof), fns,
                      group="work_" + prof, weight=weight, pri=120, min_time=4.0)


# ============================================================================ villager everyday life
T, F = VIL, f("villager/life")
villager_walk("villager.amble", "Villager Ambling Walk", T, WALKING + " && !q.near_hostile && !q.is_baby && !q.is_night", 1.3, F, stride=22, bob=0.5, twist=4, sway=2.5, lean=4,
              arms_fn=lambda u: [-4 * wave(u, 0.1, 2), 0, 3 * wave(u)])
villager_walk("villager.hurry_home", "Villager Hurrying Home At Dusk", T, WALKING + " && q.is_night && !q.near_hostile && !q.is_baby", 0.8, F, pri=101, stride=30, bob=0.9, twist=6, sway=1.5, lean=12,
              arms_fn=lambda u: [-25 + 12 * wave(u, 0, 2), 0, 0])
villager_walk("villager.panic_flee", "Villager Panicked Flight", T, WALKING + " && (q.near_hostile || q.recent_hurt < 6) && !q.is_baby", 0.5, F, pri=102, stride=44, bob=1.6, twist=10, sway=3,
              lean=18, knee_lift=12, arms_fn=lambda u: [-110 + 15 * wave(u, 0, 2), 0, 10 * wave(u)])
villager_walk("villager.child_scamper", "Village Child Scampering", T, WALKING + " && q.is_baby", 0.45, F, pri=103, stride=46, bob=2.0, twist=8, sway=4, lean=10, bounce=0.8,
              knee_lift=22, asym=0.3, arms_fn=lambda u: [-35 * max(0, wave(u, 0, 2)), 0, 20 * wave(u)])
loop_state("villager.idle_look", "Villager Idle Looking About", CAT, T, STILL + " && !q.in_conversation", 5.0, F, {
    "head:rot": lambda u: [5 * wave(u, 0.3), 35 * wave(u), 0], "body:rot": lambda u: tilt(0, 8 * wave(u, 0.1), 2 * wave(u, 0.6))}, group="vil_idle", weight=3, layer="additive", pri=55)
loop_state("villager.idle_shift_weight", "Villager Shifting Weight", CAT, T, STILL + " && !q.in_conversation", 6.0, F, {
    "mw_root:rot": lambda u: tilt(0, 0, 2.5 * (1 if wave(u) > 0 else -1) * min(1, abs(wave(u)) * 4)), "right_leg:rot": lambda u: leg('r', 0, 3 * max(0, wave(u)))},
    group="vil_idle", weight=2, layer="additive", pri=55)
loop_state("villager.gossip_talk", "Villager Gossiping", CAT, T, ALIVE + " && q.in_conversation && q.is_speaking", 2.2, F, {
    "head:rot": lambda u: [-4 + 6 * wave(u, 0, 3), 10 * wave(u), 6 * wave(u, 0.2)], "arms:rot": lambda u: [-10 * max(0, wave(u, 0.1, 2)), 0, 0], "body:rot": lambda u: tilt(0, 6 * wave(u, 0.3), 0),
    "nose:rot": lambda u: [3 * wave(u, 0, 6), 0, 0]}, pri=115)
loop_state("villager.listen_nod", "Villager Listening And Nodding", CAT, T, ALIVE + " && q.in_conversation && !q.is_speaking", 2.6, F, {
    "head:rot": lambda u: [6 * spike(u, 0.2, 2, 2), 0, 8], "body:rot": lambda u: tilt(-2, 0, 0)}, pri=114, layer="additive")
beat("villager.laugh", "Villager Laughing", CAT, T, event("speak", ALIVE + " && q.mood > 0.6", chance=0.35), 1.4, F, {
    "head:rot": [(0, Z), (0.15, [-20, 0, 0]), (0.3, [-10, 0, 0]), (0.45, [-20, 0, 0]), (0.6, [-10, 0, 0]), (1.4, Z)], "body:rot": [(0, Z), (0.15, tilt(-8)), (0.6, tilt(-6)), (1.4, Z)],
    "arms:rot": [(0, Z), (0.3, [-15, 0, 0]), (1.4, Z)]}, layer="gesture")
beat("villager.disagree", "Villager Disagreeing Hrmm", CAT, T, event("speak", ALIVE + " && q.mood < 0.35", chance=0.5), 1.2, F, {
    "head:rot": [(0, Z), (0.2, [0, 20, 0]), (0.45, [0, -20, 0]), (0.7, [0, 14, 0]), (1.2, Z)], "body:rot": [(0, Z), (0.3, tilt(-4, 0, 0)), (1.2, Z)]}, layer="gesture")
loop_state("villager.haggle", "Villager Haggling", CAT, T, ALIVE + " && q.is_trading", 3.0, F, {
    "head:rot": lambda u: [10 + 6 * wave(u, 0, 2), 12 * wave(u, 0.2), 10 * spike(u, 0.7, 4)], "arms:rot": lambda u: [-20 - 10 * max(0, wave(u, 0.4, 2)), 0, 0], "body:rot": lambda u: tilt(6, 0, 0)},
    pri=140)
beat("villager.deal_struck", "Villager Deal Struck", CAT, T, event("trade_complete", ALIVE), 1.2, F, {
    "arms:rot": [(0, Z), (0.25, [-50, 0, 0], "out_back"), (0.6, [-40, 0, 0]), (1.2, Z)], "head:rot": [(0, Z), (0.2, [-10, 0, 0]), (0.5, [8, 0, 0]), (1.2, Z)],
    "mw_root:pos": [(0, Z), (0.25, move(0, 0.8, 0)), (0.5, Z)]}, pri=160, events=[(0.25, "particle", {"particle": "magic_glint", "count": "6", "at": "head", "spread": "0.3"})])
loop_state("villager.grumpy_shake", "Villager Unhappy Head Shake", CAT, T, ALIVE + " && q.is_unhappy", 0.6, F, {
    "head:rot": lambda u: [0, 25 * wave(u), 0], "hat_rim:rot": lambda u: [0, 0, 4 * wave(u, 0.2)]}, pri=170, layer="action")
loop_state("villager.sleep_breathe", "Villager Sleeping Breath", CAT, T, "!q.is_dead && q.is_sleeping", 3.6, F, {
    "body:scl": lambda u: [1, 1, 1 + 0.03 * wave(u)], "head:rot": lambda u: [0, 0, 6 + 3 * wave(u, 0.2)], "nose:rot": lambda u: [3 * spike(u, 0.5, 6), 0, 0]}, pri=130, layer="additive")
beat("villager.wake_stretch", "Villager Morning Stretch", CAT, T, event("wake", "!q.is_dead && !q.is_baby"), 2.4, F, {
    "arms:rot": [(0, Z), (0.6, [-150, 0, 0], "out_quad"), (1.4, [-160, 0, 0]), (2.4, Z, "in_out_sine")], "body:rot": [(0, Z), (0.6, tilt(-12, 0, 0)), (1.4, tilt(-14, 0, 0)), (2.4, Z)],
    "head:rot": [(0, Z), (0.6, [-25, 0, 0]), (1.0, [-20, 0, 10]), (1.4, [-25, 0, -10]), (2.4, Z)], "mw_root:pos": [(0, Z), (0.8, move(0, 0.8, 0)), (1.6, Z)]}, pri=150)
loop_state("villager.cower", "Villager Cowering", CAT, T, STILL + " && q.near_hostile && q.hostile_distance < 6", 0.4, F, {
    "arms:rot": lambda u: [-110, 0, 0], "head:rot": lambda u: [30, 0, 6 * wave(u)], "body:rot": lambda u: tilt(20, 0, 0), "mw_root:pos": lambda u: move(0.2 * wave(u, 0.25), -2, 0),
    "right_leg:rot": lambda u: leg('r', 40), "left_leg:rot": lambda u: leg('l', 40)}, pri=180, layer="action")
loop_state("villager.rain_shelter", "Villager Shielding From The Rain", CAT, T, ALIVE + " && q.is_raining && q.sky_exposed && !q.near_hostile", 1.6, F, {
    "arms:rot": lambda u: [-160, 0, 0], "arms:pos": lambda u: move(0, 1.5, 0), "head:rot": lambda u: [14, 0, 0], "body:rot": lambda u: tilt(8, 0, 0)}, pri=125)
beat("villager.greet_wave", "Villager Greeting", CAT, T, event("interacted", ALIVE + " && !q.is_trading"), 1.4, F, {
    "arms:rot": [(0, Z), (0.3, [-120, 0, 14]), (0.55, [-120, 0, -14]), (0.8, [-120, 0, 14]), (1.4, Z)], "head:rot": [(0, Z), (0.3, [-8, 0, 8]), (1.0, [-8, 0, 8]), (1.4, Z)]}, pri=150, layer="gesture")
beat("villager.startled", "Villager Startled Jump", CAT, T, event("hurt", ALIVE), 0.7, F, {
    "mw_root:pos": [(0, Z), (0.1, move(0, 2, 0), "out_expo"), (0.35, Z)], "arms:rot": [(0, Z), (0.1, [-70, 0, 0]), (0.7, Z)], "head:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.7, Z)]}, pri=200, layer="reaction")
loop_state("villager.child_play_tag", "Village Children Playing Tag", CAT, T, STILL + " && q.is_baby && q.trait_energy > 0.4", 1.0, F, {
    "mw_root:pos": lambda u: move(0, 1.5 * max(0, wave(u)), 0), "mw_root:rot": lambda u: tilt(0, 90 * wave(u, 0, 0.5), 0), "arms:rot": lambda u: [-30 * max(0, wave(u)), 0, 0]},
    group="vil_child", weight=2)
loop_state("villager.child_hopscotch", "Village Child Hopscotch", CAT, T, STILL + " && q.is_baby", 1.2, F, {
    "right_leg:rot": lambda u: leg('r', 50), "left_leg:rot": lambda u: leg('l', 10 * wave(u, 0, 2)), "mw_root:pos": lambda u: move(0, 1.2 * max(0, wave(u, 0, 2)), 0), "body:rot": lambda u: tilt(0, 0, 4 * wave(u))},
    group="vil_child", weight=1)
beat("villager.child_giggle", "Village Child Giggle", CAT, T, event("speak", ALIVE + " && q.is_baby"), 0.8, F, {
    "head:rot": [(0, Z), (0.1, [-14, 0, 10]), (0.25, [-6, 0, -10]), (0.4, [-14, 0, 10]), (0.8, Z)], "mw_root:pos": [(0, Z), (0.15, move(0, 0.6, 0)), (0.3, Z)]}, layer="gesture")
loop_state("villager.nitwit_daydream", "Nitwit Daydreaming", CAT, T, STILL + " && q.profession == 'nitwit'", 6.0, F, {
    "head:rot": lambda u: [-25 + 5 * wave(u), 20 * wave(u, 0, 0.5), 10 * wave(u)], "nose:rot": lambda u: [0, 0, 6 * wave(u, 0, 3)], "mw_root:rot": lambda u: tilt(0, 0, 3 * wave(u))}, pri=110)
loop_state("villager.nitwit_spin", "Nitwit Spinning In Place", CAT, T, STILL + " && q.profession == 'nitwit' && q.trait_energy > 0.6", 3.0, F, {"mw_root:rot": lambda u: [0, 360 * u, 0],
                                                                                                                                 "arms:rot": lambda u: [-40, 0, 0]}, pri=111)
loop_state("villager.unemployed_wander_look", "Unemployed Villager Scanning For Work", CAT, T, STILL + " && q.profession == 'none' && !q.is_baby", 4.0, F, {
    "head:rot": lambda u: [0, 50 * wave(u), 0], "arms:rot": lambda u: [-6, 0, 0], "body:rot": lambda u: tilt(0, 20 * wave(u, 0.05), 0)}, pri=110)
loop_state("villager.level_pride", "Seasoned Villager Proud Posture", CAT, T, STILL + " && q.villager_level >= 4 && !q.in_conversation", 5.0, F, {
    "body:rot": lambda u: tilt(-6, 0, 0), "head:rot": lambda u: [-10, 12 * wave(u), 0], "mw_root:pos": lambda u: move(0, 0.5, 0)}, group="vil_idle", weight=2, layer="additive", pri=56)
loop_state("villager.night_lantern_watch", "Villager Peering Into The Dark", CAT, T, STILL + " && q.is_night && q.light < 8 && !q.is_sleeping", 3.0, F, {
    "head:rot": lambda u: [-6, 40 * wave(u), 0], "body:rot": lambda u: tilt(6, 0, 0), "arms:rot": lambda u: [-20, 0, 0]}, pri=112)
beat("villager.sneeze", "Villager Sneeze", CAT, T, event("vocalize", ALIVE + " && q.is_cold"), 1.0, F, {
    "head:rot": [(0, Z), (0.45, [-25, 0, 0], "in_quad"), (0.55, [30, 0, 0], "out_expo"), (1.0, Z)], "nose:rot": [(0, Z), (0.45, [-10, 0, 0]), (0.55, [10, 0, 0]), (1.0, Z)]}, layer="gesture")
beat("villager.hmm", "Villager Thoughtful Hmm", CAT, T, event("vocalize", ALIVE + " && !q.is_cold && !q.in_conversation"), 1.4, F, {
    "head:rot": [(0, Z), (0.3, [10, 0, 14]), (1.0, [10, 0, 14]), (1.4, Z)], "nose:rot": [(0, Z), (0.4, [5, 0, 0]), (0.7, [0, 0, 0]), (1.4, Z)]}, layer="gesture")
loop_state("villager.warm_by_fire", "Villager Warming By The Fire", CAT, T, STILL + " && q.near_fire && (q.is_night || q.is_cold)", 2.0, F, {
    "arms:rot": lambda u: [-60 + 6 * wave(u), 0, 0], "arms:pos": lambda u: move(0.3 * wave(u, 0, 2), 0, 0), "body:rot": lambda u: tilt(10, 0, 0)}, pri=118)
loop_state("villager.zombie_dread", "Villager Trembling At The Door", CAT, T, STILL + " && q.is_night && q.near_hostile && q.hostile_distance >= 6", 0.25, F, {
    "body:rot": lambda u: tilt(4, 0, 2 * wave(u)), "head:rot": lambda u: [8, 3 * wave(u, 0.3), 0]}, pri=170, layer="additive")

# ============================================================================ professions at work (4 distinct tasks each)
work("farmer", "till", "Farmer Tilling Soil", 1.2, {
    "arms:rot": lambda u: [-40 + 40 * max(0, wave(u)), 0, 0], "body:rot": lambda u: tilt(20 + 15 * max(0, wave(u)), 0, 0), "head:rot": lambda u: [25, 0, 0]}, weight=3)
work("farmer", "sow", "Farmer Sowing Seeds", 1.6, {
    "arms:rot": lambda u: [-35, 25 * wave(u), 0], "arms:pos": lambda u: move(1.2 * wave(u), 0, 0), "body:rot": lambda u: tilt(14, 15 * wave(u), 0), "head:rot": lambda u: [30, 10 * wave(u), 0]}, weight=2)
work("farmer", "harvest", "Farmer Crouched Harvest", 2.0, {
    "mw_root:pos": lambda u: move(0, -3, 0), "right_leg:rot": lambda u: leg('r', 60), "left_leg:rot": lambda u: leg('l', 30), "body:rot": lambda u: tilt(40, 0, 0),
    "arms:rot": lambda u: [-60 - 20 * spike(u, 0.2, 3, 2), 0, 0], "head:rot": lambda u: [30, 0, 0]}, weight=2)
work("farmer", "wipe_brow", "Farmer Wiping His Brow", 3.0, {
    "arms:rot": lambda u: [-140 * spike(u, 0.25, 2), 0, 0], "head:rot": lambda u: [-15 * spike(u, 0.25, 2), 0, 0], "body:rot": lambda u: tilt(-6 * spike(u, 0.25, 2), 0, 0)}, weight=1)
work("librarian", "read", "Librarian Reading", 3.0, {
    "arms:rot": lambda u: [-55, 0, 0], "head:rot": lambda u: [35, 10 * wave(u, 0, 3), 0], "body:rot": lambda u: tilt(6, 0, 0)}, weight=3)
work("librarian", "page_turn", "Librarian Turning Pages", 1.6, {
    "arms:rot": lambda u: [-55, 0, 25 * spike(u, 0.4, 4)], "head:rot": lambda u: [35, -8 * spike(u, 0.4, 4), 0]}, weight=2)
work("librarian", "quill_write", "Librarian Writing With A Quill", 2.0, {
    "arms:rot": lambda u: [-45, 0, 6 * wave(u, 0, 6)], "arms:pos": lambda u: move(-1.2 + 2.4 * ((u * 2) % 1), 0, 0.3 * cwave(u, 0, 6)), "head:rot": lambda u: [40, -12 + 24 * ((u * 2) % 1), 0],
    "body:rot": lambda u: tilt(14, 0, 0)}, weight=2)
work("librarian", "shelve", "Librarian Shelving A Book", 2.4, {
    "arms:rot": lambda u: [-90 - 60 * max(0, wave(u)), 0, 0], "mw_root:pos": lambda u: move(0, 1.2 * max(0, wave(u)), 0), "head:rot": lambda u: [-30 * max(0, wave(u)), 0, 0]}, weight=1)
work("armorer", "hammer", "Armorer Hammering Plate", 0.7, {
    "arms:rot": lambda u: [-70 + 50 * spike(u, 0.0, 2), 0, 0], "body:rot": lambda u: tilt(12 + 6 * spike(u, 0, 2), 0, 0), "head:rot": lambda u: [30, 0, 0]}, weight=3)
work("armorer", "bellows", "Armorer Pumping The Bellows", 1.2, {
    "arms:rot": lambda u: [-40 + 20 * wave(u), 0, 0], "arms:pos": lambda u: move(0, -1.5 * max(0, wave(u)), 0), "body:rot": lambda u: tilt(16 + 6 * wave(u), 0, 0)}, weight=2)
work("armorer", "polish", "Armorer Polishing A Chestplate", 1.4, {
    "arms:rot": lambda u: [-50, 0, 0], "arms:pos": lambda u: move(1.0 * cwave(u, 0, 2), 0.5 * wave(u, 0, 2), 0), "head:rot": lambda u: [30, 0, 0]}, weight=2)
work("armorer", "inspect_plate", "Armorer Inspecting A Plate", 3.0, {
    "arms:rot": lambda u: [-80, 20 * wave(u), 0], "head:rot": lambda u: [10, 20 * wave(u), 0], "body:rot": lambda u: tilt(-4, 0, 0)}, weight=1)
work("butcher", "cleave", "Butcher Cleaving", 0.9, {
    "arms:rot": lambda u: [-120 + 100 * spike(u, 0.05, 3), 0, 0], "body:rot": lambda u: tilt(-6 + 26 * spike(u, 0.05, 3), 0, 0), "head:rot": lambda u: [30, 0, 0]}, weight=3)
work("butcher", "sharpen", "Butcher Sharpening His Knife", 0.8, {
    "arms:rot": lambda u: [-60, 0, 0], "arms:pos": lambda u: move(1.4 * wave(u), 0.3 * wave(u, 0.25), 0), "head:rot": lambda u: [25, 0, 0]}, weight=2)
work("butcher", "weigh", "Butcher Weighing Cuts", 2.6, {
    "arms:rot": lambda u: [-70 + 8 * wave(u, 0, 2), 0, 0], "head:rot": lambda u: [20, 14 * wave(u), 0], "mw_root:rot": lambda u: tilt(0, 0, 3 * wave(u))}, weight=2)
work("butcher", "smoke_hang", "Butcher Hanging Meat To Smoke", 2.2, {
    "arms:rot": lambda u: [-150 * max(0, wave(u, 0, 0.5)), 0, 0], "head:rot": lambda u: [-30 * max(0, wave(u, 0, 0.5)), 0, 0], "mw_root:pos": lambda u: move(0, 1 * max(0, wave(u, 0, 0.5)), 0)}, weight=1)
work("cartographer", "unroll_map", "Cartographer Unrolling A Map", 2.6, {
    "arms:rot": lambda u: [-60, 0, 0], "arms:scl": lambda u: [1 + 0.4 * max(0, wave(u, 0, 0.5)), 1, 1], "head:rot": lambda u: [40, 0, 0], "body:rot": lambda u: tilt(12, 0, 0)}, weight=3)
work("cartographer", "plot", "Cartographer Plotting Routes", 1.4, {
    "arms:rot": lambda u: [-50, 0, 0], "arms:pos": lambda u: move(1.2 * wave(u), 0, 1.0 * cwave(u, 0, 2)), "head:rot": lambda u: [40, 15 * wave(u), 0], "body:rot": lambda u: tilt(16, 0, 0)}, weight=2)
work("cartographer", "compass_check", "Cartographer Checking A Compass", 2.0, {
    "arms:rot": lambda u: [-75, 0, 0], "head:rot": lambda u: [30 * spike(u, 0.1, 2) + 10, 40 * spike(u, 0.6, 2), 0], "mw_root:rot": lambda u: [0, 30 * spike(u, 0.6, 2), 0]}, weight=2)
work("cartographer", "survey", "Cartographer Surveying The Horizon", 4.0, {
    "arms:rot": lambda u: [-160, 0, 0], "arms:pos": lambda u: move(0, 1.5, 0), "head:rot": lambda u: [-10, 50 * wave(u), 0], "body:rot": lambda u: tilt(-4, 10 * wave(u), 0)}, weight=1)
work("cleric", "pray", "Cleric In Prayer", 4.0, {
    "arms:rot": lambda u: [-80, 0, 0], "head:rot": lambda u: [30 + 3 * wave(u), 0, 0], "body:rot": lambda u: tilt(10, 0, 0), "right_leg:rot": lambda u: leg('r', 0), "mw_root:pos": lambda u: move(0, 0.2 * wave(u), 0)},
     weight=3)
work("cleric", "brew_stir", "Cleric Stirring A Brew", 1.6, {
    "arms:rot": lambda u: [-45, 0, 0], "arms:pos": lambda u: move(1.0 * cwave(u), 0, 1.0 * wave(u)), "body:rot": lambda u: tilt(18, 0, 0), "head:rot": lambda u: [30, 0, 0]}, weight=2)
work("cleric", "bless", "Cleric Raising A Blessing", 2.4, {
    "arms:rot": lambda u: [-170 * max(0, wave(u, 0, 0.5)), 0, 0], "head:rot": lambda u: [-35 * max(0, wave(u, 0, 0.5)), 0, 0], "body:rot": lambda u: tilt(-10 * max(0, wave(u, 0, 0.5)), 0, 0)},
     weight=1)
work("cleric", "censer", "Cleric Swinging A Censer", 1.4, {
    "arms:rot": lambda u: [-40, 0, 30 * wave(u)], "body:rot": lambda u: tilt(0, 10 * wave(u), 0), "head:rot": lambda u: [10, -10 * wave(u), 0]}, weight=2)
work("fisherman", "cast", "Fisherman Casting", 2.8, {
    "arms:rot": lambda u: [-150 * spike(u, 0.05, 2) - 40, 0, 0], "body:rot": lambda u: tilt(-10 * spike(u, 0.05, 2), 0, 0), "head:rot": lambda u: [-10 * spike(u, 0.1, 2), 0, 0]}, weight=2)
work("fisherman", "reel", "Fisherman Reeling", 0.8, {
    "arms:rot": lambda u: [-50 + 10 * wave(u), 0, 0], "arms:pos": lambda u: move(0.8 * cwave(u), 0.8 * wave(u), 0), "body:rot": lambda u: tilt(-6, 0, 0)}, weight=3)
work("fisherman", "gut_fish", "Fisherman Gutting A Catch", 1.0, {
    "arms:rot": lambda u: [-40 - 20 * spike(u, 0.1, 3, 2), 0, 0], "head:rot": lambda u: [40, 0, 0], "body:rot": lambda u: tilt(22, 0, 0)}, weight=2)
work("fisherman", "mend_net", "Fisherman Mending Nets", 1.6, {
    "arms:rot": lambda u: [-55, 15 * wave(u, 0, 2), 0], "arms:pos": lambda u: move(0, 0.5 * wave(u, 0.25, 2), 0), "head:rot": lambda u: [35, 0, 6 * wave(u)], "mw_root:pos": lambda u: move(0, -1.5, 0),
    "right_leg:rot": lambda u: leg('r', 50), "left_leg:rot": lambda u: leg('l', 50)}, weight=1)
work("fletcher", "fletch", "Fletcher Fletching Arrows", 1.0, {
    "arms:rot": lambda u: [-60, 0, 0], "arms:pos": lambda u: move(0.5 * wave(u, 0, 2), 0, 0), "head:rot": lambda u: [40, 0, 0], "nose:rot": lambda u: [2 * wave(u, 0, 2), 0, 0]}, weight=3)
work("fletcher", "bend_test", "Fletcher Testing A Bow Stave", 2.0, {
    "arms:rot": lambda u: [-90, 0, 0], "arms:scl": lambda u: [1 + 0.15 * max(0, wave(u)), 1, 1], "body:rot": lambda u: tilt(-6 * max(0, wave(u)), 0, 0), "head:rot": lambda u: [10, 0, 0]}, weight=2)
work("fletcher", "sight_arrow", "Fletcher Sighting Down An Arrow", 2.6, {
    "arms:rot": lambda u: [-95, 0, 0], "head:rot": lambda u: [8, 0, 14 + 4 * wave(u)], "body:rot": lambda u: tilt(0, 0, 4)}, weight=2)
work("fletcher", "whittle", "Fletcher Whittling", 0.6, {
    "arms:rot": lambda u: [-50 + 10 * spike(u, 0, 4), 0, 0], "arms:pos": lambda u: move(-0.6 * spike(u, 0, 4), 0, 0), "head:rot": lambda u: [40, 0, 0]}, weight=1)
work("leatherworker", "stitch", "Leatherworker Stitching", 0.9, {
    "arms:rot": lambda u: [-55 - 25 * spike(u, 0.1, 3), 0, 0], "head:rot": lambda u: [40, 0, 0], "body:rot": lambda u: tilt(12, 0, 0)}, weight=3)
work("leatherworker", "stretch_hide", "Leatherworker Stretching A Hide", 2.0, {
    "arms:rot": lambda u: [-70, 0, 0], "arms:scl": lambda u: [1 + 0.3 * max(0, wave(u)), 1, 1], "body:rot": lambda u: tilt(-8 * max(0, wave(u)), 0, 0), "mw_root:pos": lambda u: move(0, 0, -0.8 * max(0, wave(u)))},
     weight=2)
work("leatherworker", "dye_dip", "Leatherworker Dipping In The Cauldron", 2.4, {
    "arms:rot": lambda u: [-40 - 30 * max(0, -wave(u)), 0, 0], "body:rot": lambda u: tilt(20 + 20 * max(0, -wave(u)), 0, 0), "head:rot": lambda u: [30, 0, 0]}, weight=2)
work("leatherworker", "cut_strips", "Leatherworker Cutting Strips", 1.2, {
    "arms:rot": lambda u: [-50, -20 + 40 * stroke(u, 0.75), 0], "arms:pos": lambda u: move(0, 0, -1.2 * stroke(u, 0.75)), "head:rot": lambda u: [45, -10 + 20 * stroke(u, 0.75), 0],
    "body:rot": lambda u: tilt(18, 0, 6 * wave(u, 0.25))}, weight=1)
work("mason", "chisel", "Mason Chiselling Stone", 0.5, {
    "arms:rot": lambda u: [-50, 0, 0], "arms:pos": lambda u: move(0, 0, -0.6 * spike(u, 0, 3)), "head:rot": lambda u: [30, 0, 0], "body:rot": lambda u: tilt(10, 0, 0)}, weight=3)
work("mason", "measure", "Mason Measuring A Block", 2.4, {
    "arms:rot": lambda u: [-60, 0, 0], "arms:scl": lambda u: [1 + 0.35 * max(0, wave(u, 0, 0.5)), 1, 1], "head:rot": lambda u: [30, 20 * wave(u), 0]}, weight=2)
work("mason", "heave_stone", "Mason Heaving A Stone", 2.6, {
    "mw_root:pos": lambda u: move(0, -2 * max(0, -wave(u)), 0), "right_leg:rot": lambda u: leg('r', 40 * max(0, -wave(u))), "left_leg:rot": lambda u: leg('l', 40 * max(0, -wave(u))),
    "body:rot": lambda u: tilt(30 * max(0, -wave(u)) - 6 * max(0, wave(u)), 0, 0), "arms:rot": lambda u: [-70, 0, 0]}, weight=1)
work("mason", "polish_stone", "Mason Polishing Terracotta", 1.2, {
    "arms:rot": lambda u: [-45, 0, 0], "arms:pos": lambda u: move(0.8 * cwave(u), 0, 0.6 * wave(u)), "body:rot": lambda u: tilt(16, 6 * cwave(u), 0)}, weight=2)
work("shepherd", "shear", "Shepherd Shearing Wool", 0.6, {
    "arms:rot": lambda u: [-40, 0, 0], "arms:scl": lambda u: [1 - 0.15 * spike(u, 0, 2, 2), 1, 1], "body:rot": lambda u: tilt(30, 0, 0), "head:rot": lambda u: [30, 0, 0]}, weight=3)
work("shepherd", "spin_wool", "Shepherd At The Spinning Wheel", 1.0, {
    "arms:rot": lambda u: [-60, 0, 20 * wave(u)], "left_leg:rot": lambda u: leg('l', 25 * max(0, wave(u, 0.25))), "head:rot": lambda u: [25, 0, -6 * wave(u)],
    "mw_root:pos": lambda u: move(0, -2, 0), "right_leg:rot": lambda u: leg('r', 70)}, weight=2)
work("shepherd", "count_flock", "Shepherd Counting The Flock", 3.0, {
    "head:rot": lambda u: [5, -50 + 100 * stroke(u, 0.85), 0], "nose:rot": lambda u: [3 * spike(u, 0, 4, 5), 0, 0], "arms:rot": lambda u: [-20, 0, 0]}, weight=2)
work("shepherd", "call_flock", "Shepherd Calling The Flock", 2.0, {
    "arms:rot": lambda u: [-110, 0, 0], "arms:pos": lambda u: move(0, 1, 0), "head:rot": lambda u: [-10, 30 * wave(u, 0, 0.5), 0],
    "body:rot": lambda u: tilt(12 * spike(u, 0.1, 3, 2), 0, 0), "mw_root:pos": lambda u: move(0, 0, 0.5 * spike(u, 0.1, 3, 2))}, weight=1)
work("toolsmith", "grindstone", "Toolsmith Treadling The Grindstone", 0.8, {
    "arms:rot": lambda u: [-45, 0, 0], "right_leg:rot": lambda u: leg('r', 30 * max(0, wave(u))), "mw_root:pos": lambda u: move(0, 0.4 * max(0, wave(u)), 0),
    "body:rot": lambda u: tilt(16, 0, 2 * wave(u)), "head:rot": lambda u: [35, 0, 0]}, weight=3)
work("toolsmith", "hammer_head", "Toolsmith Shaping A Tool Head", 0.6, {
    "arms:rot": lambda u: [-90 + 70 * spike(u, 0.0, 3), 0, 0], "head:rot": lambda u: [30, 0, 0], "body:rot": lambda u: tilt(6 + 10 * spike(u, 0.0, 3), 0, 0)}, weight=2)
work("toolsmith", "test_edge", "Toolsmith Testing An Edge", 2.2, {
    "arms:rot": lambda u: [-85, 0, 30 * spike(u, 0.4, 3)], "head:rot": lambda u: [15, 0, 10], "nose:rot": lambda u: [0, 0, 5 * spike(u, 0.4, 3)]}, weight=2)
work("toolsmith", "tongs_quench", "Toolsmith Quenching With Tongs", 2.4, {
    "arms:rot": lambda u: [-60 + 30 * max(0, -wave(u)), 0, 0], "body:rot": lambda u: tilt(14 + 16 * max(0, -wave(u)), 0, 0), "head:rot": lambda u: [-10 * spike(u, 0.75, 4), 0, 0]}, weight=1)
work("weaponsmith", "grind_blade", "Weaponsmith Grinding A Blade", 0.9, {
    "arms:rot": lambda u: [-50, 0, 0], "arms:pos": lambda u: move(1.4 * wave(u), 0, 0), "body:rot": lambda u: tilt(12, 8 * wave(u), 0)}, weight=3)
work("weaponsmith", "practice_swing", "Weaponsmith Practice Swing", 1.4, {
    "arms:rot": lambda u: [-140 * spike(u, 0.0, 3) - 30, 0, 40 * wave(u)], "body:rot": lambda u: tilt(0, 30 * wave(u), 0), "head:rot": lambda u: [0, -15 * wave(u), 0]}, weight=1)
work("weaponsmith", "quench", "Weaponsmith Quenching Steel", 2.4, {
    "arms:rot": lambda u: [-50 + 40 * max(0, -wave(u)), 0, 0], "body:rot": lambda u: tilt(10 + 25 * max(0, -wave(u)), 0, 0), "mw_root:pos": lambda u: move(0, -0.8 * max(0, -wave(u)), 0)}, weight=2)
work("weaponsmith", "inspect_blade", "Weaponsmith Sighting Down A Blade", 3.0, {
    "arms:rot": lambda u: [-100, 0, 0], "head:rot": lambda u: [-10, 0, 20], "body:rot": lambda u: tilt(-4, -14, 0), "nose:rot": lambda u: [0, 0, 3 * wave(u)]}, weight=2)

# ============================================================================ wandering trader
T, F = "minecraft:wandering_trader", f("wandering_trader")
villager_walk("wandering_trader.trek", "Wandering Trader Trekking", T, WALKING + " && !q.near_hostile", 1.5, F, stride=24, bob=0.6, twist=3, sway=3, lean=10, asym=0.25,
              arms_fn=lambda u: [-15, 8 * wave(u), 0])
villager_walk("wandering_trader.flee", "Wandering Trader Fleeing", T, WALKING + " && q.near_hostile", 0.55, F, pri=101, stride=42, bob=1.4, twist=8, sway=2, lean=16,
              knee_lift=16, arms_fn=lambda u: [-70 + 10 * wave(u, 0, 2), 0, 0])
loop_state("wandering_trader.hawk_wares", "Wandering Trader Hawking Wares", CAT, T, ALIVE + " && q.is_trading", 2.4, F, {
    "arms:rot": lambda u: [-40 - 30 * spike(u, 0.3, 2), 25 * wave(u, 0.1), 0], "head:rot": lambda u: [5, 20 * wave(u), 0], "body:rot": lambda u: tilt(4, 10 * wave(u), 0)}, pri=140)
loop_state("wandering_trader.count_coins", "Wandering Trader Counting Emeralds", CAT, T, STILL + " && !q.is_trading && !q.is_using_item", 2.0, F, {
    "arms:rot": lambda u: [-55, 0, 0], "head:rot": lambda u: [35, 0, 0], "nose:rot": lambda u: [3 * spike(u, 0, 4, 4), 0, 0]}, group="trader_idle", weight=2)
loop_state("wandering_trader.wary_glance", "Wandering Trader Wary Glance", CAT, T, STILL + " && !q.is_trading", 3.6, F, {
    "head:rot": lambda u: [0, 60 * spike(u, 0.2, 3) - 60 * spike(u, 0.7, 3), 0], "body:rot": lambda u: tilt(0, 10 * spike(u, 0.2, 3), 0)}, group="trader_idle", weight=2)
loop_state("wandering_trader.drink_potion", "Wandering Trader Drinking A Potion", CAT, T, ALIVE + " && q.is_using_item", 1.6, F, {
    "head:rot": lambda u: [-35, 0, 0], "arms:rot": lambda u: [-110, 0, 0], "body:rot": lambda u: tilt(-10, 0, 0)}, pri=160, layer="action")
beat("wandering_trader.shoo", "Wandering Trader Shooing", CAT, T, event("interacted", ALIVE + " && !q.is_trading && q.mood < 0.4"), 1.0, F, {
    "arms:rot": [(0, Z), (0.2, [-60, 0, 20]), (0.35, [-60, 0, -20]), (0.5, [-60, 0, 20]), (1.0, Z)], "head:rot": [(0, Z), (0.2, [0, 20, 0]), (1.0, Z)]}, pri=150, layer="gesture")
beat("wandering_trader.bow_thanks", "Wandering Trader Bowing Thanks", CAT, T, event("trade_complete", ALIVE), 1.6, F, {
    "body:rot": [(0, Z), (0.5, tilt(40, 0, 0), "in_out_sine"), (1.0, tilt(40, 0, 0)), (1.6, Z)], "head:rot": [(0, Z), (0.5, [20, 0, 0]), (1.6, Z)]}, pri=160)

# ============================================================================ iron golem
T, F = "minecraft:iron_golem", f("iron_golem")
c = mob("iron_golem.patrol", "Iron Golem Heavy Patrol", CAT, T, 2.2, state(WALKING + " && q.health >= 0.3", exit_delay=0.2), layer="base", file=F, **driven(2.2))
c.cycle("right_leg", "rotation", lambda u: leg('r', 20 * cwave(u)))
c.cycle("left_leg", "rotation", lambda u: leg('l', -20 * cwave(u)))
c.cycle("right_arm", "rotation", lambda u: arm('r', -18 * cwave(u), 2))
c.cycle("left_arm", "rotation", lambda u: arm('l', 18 * cwave(u), 2))
c.cycle("body", "rotation", lambda u: tilt(2, 6 * cwave(u), 0))
c.cycle("mw_root", "rotation", lambda u: tilt(0, 0, 3 * wave(u)))
c.cycle("mw_root", "position", lambda u: move(0, -0.7 * (1 + cwave(u, 0, 2)) * 0.5, 0))
c.ev(0.0, "stomp", strength="0.25")
c.ev(1.1, "stomp", strength="0.25")
c = mob("iron_golem.cracked_limp", "Cracked Iron Golem Limp", CAT, T, 2.6, state(WALKING + " && q.health < 0.3", exit_delay=0.2), layer="base", pri=101, file=F, **driven(2.6))
c.cycle("right_leg", "rotation", lambda u: leg('r', 24 * cwave(u)))
c.cycle("left_leg", "rotation", lambda u: leg('l', -8 * cwave(u) + 4))
c.cycle("body", "rotation", lambda u: tilt(8, 4 * cwave(u), 6 * max(0, wave(u, 0.6))))
c.cycle("left_arm", "rotation", lambda u: arm('l', 6, 10))
c.cycle("mw_root", "position", lambda u: move(0, -1.0 * max(0, wave(u, 0.6)), 0))
loop_state("iron_golem.offer_poppy", "Iron Golem Offering A Poppy", CAT, T, ALIVE + " && q.is_holding", 2.0, F, {
    "right_arm:rot": lambda u: arm('r', 80, 0), "head:rot": lambda u: [20, 0, 8], "body:rot": lambda u: tilt(10, 0, 0)}, pri=150, layer="action")
loop_state("iron_golem.sentinel", "Iron Golem Sentinel Stance", CAT, T, STILL + " && !q.is_holding", 6.0, F, {
    "head:rot": lambda u: [0, 45 * wave(u), 0], "body:rot": lambda u: tilt(0, 10 * wave(u, 0.1), 0), "right_arm:rot": lambda u: [1.5 * wave(u), 0, 0]}, layer="additive", pri=55)
beat("iron_golem.uppercut_toss", "Iron Golem Uppercut Toss", CAT, T, event("melee_hit", ALIVE), 1.0, F, {
    "right_arm:rot": [(0, Z), (0.2, arm('r', -30, 10), "out_quad"), (0.35, arm('r', 140), "in_quart"), (1.0, Z)], "left_arm:rot": [(0, Z), (0.2, arm('l', -30, 10)), (0.35, arm('l', 140), "in_quart"), (1.0, Z)],
    "body:rot": [(0, Z), (0.2, tilt(14)), (0.35, tilt(-10)), (1.0, Z)]}, pri=170, events=[(0.35, "whoosh", {"weight": "heavy"}), (0.35, "shake", {"intensity": "0.3", "duration": "0.3"})])
beat("iron_golem.repaired", "Iron Golem Repaired", CAT, T, event("interacted", ALIVE + " && q.health < 1"), 1.4, F, {
    "body:rot": [(0, Z), (0.3, tilt(-8, 0, 0)), (0.8, tilt(-6, 0, 0)), (1.4, Z)], "head:rot": [(0, Z), (0.3, [-15, 0, 0]), (0.8, [-10, 0, 6]), (1.4, Z)],
    "right_arm:rot": [(0, Z), (0.4, arm('r', 20, 20)), (1.4, Z)], "left_arm:rot": [(0, Z), (0.4, arm('l', 20, 20)), (1.4, Z)]}, pri=150)
beat("iron_golem.ground_slam", "Iron Golem Ground Slam", CAT, T, event("aggro", ALIVE), 1.2, F, {
    "right_arm:rot": [(0, Z), (0.4, arm('r', 170), "out_quad"), (0.55, arm('r', 40), "in_quart"), (1.2, Z)], "left_arm:rot": [(0, Z), (0.4, arm('l', 170), "out_quad"), (0.55, arm('l', 40), "in_quart"), (1.2, Z)],
    "body:rot": [(0, Z), (0.4, tilt(-10)), (0.55, tilt(26)), (1.2, Z)]}, pri=165, events=[(0.55, "stomp", {"strength": "1"}), (0.55, "shake", {"intensity": "0.4", "duration": "0.4"})])
beat("iron_golem.creak", "Iron Golem Creaking Settle", CAT, T, event("vocalize", ALIVE), 1.6, F, {
    "head:rot": [(0, Z), (0.4, [0, 0, 10]), (0.9, [0, 0, -6]), (1.6, Z)], "body:rot": [(0, Z), (0.6, tilt(4, 0, 4)), (1.6, Z)]}, layer="gesture")
loop_state("iron_golem.vine_sway", "Iron Golem Vines Swaying", CAT, T, ALIVE + " && q.wind > 0.3", 3.0, F, {"head:rot": lambda u: [0, 0, 1 * wave(u)]}, layer="additive", pri=58)
beat("iron_golem.child_pat", "Iron Golem Patting A Child", CAT, T, event("speak", ALIVE), 2.0, F, {
    "right_arm:rot": [(0, Z), (0.5, arm('r', 60)), (0.8, arm('r', 50)), (1.1, arm('r', 60)), (1.4, arm('r', 50)), (2.0, Z)], "head:rot": [(0, Z), (0.5, [30, 0, 0]), (1.6, [30, 0, 0]), (2.0, Z)]}, pri=140)

# ============================================================================ snow golem
T, F = "minecraft:snow_golem", f("snow_golem")
c = mob("snow_golem.slide", "Snow Golem Sliding Waddle", CAT, T, 1.0, state(WALKING), layer="base", file=F)
c.cycle("upper_body", "rotation", lambda u: [0, 10 * wave(u), 6 * wave(u)])
c.cycle("lower_body", "rotation", lambda u: [0, -6 * wave(u), -4 * wave(u)])
c.cycle("head", "rotation", lambda u: [0, 0, -5 * wave(u)])
c.cycle("right_arm", "rotation", lambda u: [0, 0, 10 * wave(u)])
c.cycle("left_arm", "rotation", lambda u: [0, 0, 10 * wave(u)])
beat("snow_golem.throw", "Snow Golem Snowball Throw", CAT, T, event("shoot:snowball", ALIVE), 0.6, F, {
    "right_arm:rot": [(0, Z), (0.2, [0, 0, 60], "out_quad"), (0.3, [0, -40, -20], "in_quart"), (0.6, Z)], "upper_body:rot": [(0, Z), (0.2, [0, 20, 0]), (0.3, [0, -20, 0]), (0.6, Z)]}, pri=170)
loop_state("snow_golem.melt_droop", "Snow Golem Melting Droop", CAT, T, ALIVE + " && q.temperature > 1.0", 2.6, F, {
    "head:rot": lambda u: [20 + 4 * wave(u), 0, 10], "head:pos": lambda u: move(0, -0.8, 0), "upper_body:scl": lambda u: [1.05, 0.95, 1.05], "right_arm:rot": lambda u: [0, 0, -20], "left_arm:rot": lambda u: [0, 0, 20]},
    pri=120)
loop_state("snow_golem.snowfall_joy", "Snow Golem Delighting In Snowfall", CAT, T, ALIVE + " && q.is_raining && q.is_cold", 1.6, F, {
    "right_arm:rot": lambda u: [0, 0, 30 + 20 * wave(u)], "left_arm:rot": lambda u: [0, 0, -30 - 20 * wave(u)], "head:rot": lambda u: [-20, 0, 8 * wave(u, 0.25)]}, pri=118)
loop_state("snow_golem.idle_wobble", "Snow Golem Idle Wobble", CAT, T, STILL, 4.0, F, {"upper_body:rot": lambda u: [0, 0, 3 * wave(u)], "head:rot": lambda u: [0, 30 * wave(u, 0.2), 0]}, layer="additive", pri=55)
beat("snow_golem.sheared_shiver", "Snow Golem Sheared Shiver", CAT, T, event("interacted", ALIVE), 1.0, F, {
    "head:rot": [(0, Z), (0.1, [0, 0, 10]), (0.2, [0, 0, -10]), (0.3, [0, 0, 8]), (0.4, [0, 0, -6]), (1.0, Z)], "upper_body:rot": [(0, Z), (0.15, [0, 0, 4]), (0.3, [0, 0, -4]), (1.0, Z)]}, layer="gesture")
beat("snow_golem.hurt_crumble", "Snow Golem Crumbling Flinch", CAT, T, event("hurt", ALIVE), 0.7, F, {
    "head:pos": [(0, Z), (0.06, move(0, -1, 0)), (0.7, Z)], "upper_body:rot": [(0, Z), (0.06, [0, 0, "q.hurt_dir > 0 ? -12 : 12"]), (0.7, Z)]}, pri=200, layer="reaction",
     events=[(0.0, "particle", {"particle": "snow_puff", "count": "10", "at": "body", "spread": "0.4"})])

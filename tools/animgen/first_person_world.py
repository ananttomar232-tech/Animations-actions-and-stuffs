"""First-person part 3: movement, traversal, mining, consuming, world interaction and damage."""
from core import Clip, state, event, shake, wave, cwave
from first_person import CAT, T, Z, ALIVE, P, R, V, fp
from first_person_more import fpk, fpl

FM, FX, FC, FI, FH = "first_person/movement", "first_person/mining", "first_person/consume", "first_person/interact", "first_person/damage"
GROUNDED = ALIVE + " && q.is_on_ground && !q.is_riding && !q.is_in_water"
IDLE = GROUNDED + " && q.ground_speed < 0.02 && !q.is_using_item && !q.is_sneaking"

# -------------------------------------------------------------------------- locomotion layers (overlay, under every action)
fpl("walk_sway", "FP Walking Hand Sway", GROUNDED + " && q.ground_speed >= 0.02 && !q.is_sprinting && !q.is_sneaking", 1.0, {
    "main:pos": lambda u: P(0.4 * wave(u), 0.35 * abs(wave(u)), 0), "off:pos": lambda u: P(0.4 * wave(u, 0.5), 0.35 * abs(wave(u, 0.5)), 0)}, pri=110, file=FM)
fpl("sprint_pump", "FP Sprint Arm Pump", GROUNDED + " && q.is_sprinting && q.exertion <= 0.8", 0.62, {
    "main:pos": lambda u: P(-0.6 * wave(u), 1.2 * wave(u), 1.6 * cwave(u)), "main:rot": lambda u: R(8 * wave(u), 0, 3 * wave(u)),
    "off:pos": lambda u: P(0.6 * wave(u), -1.2 * wave(u), -1.6 * cwave(u)), "view:rot": lambda u: V(0, 0, 0.6 * wave(u))}, pri=112, file=FM)
fpl("sprint_exhausted", "FP Ragged Sprint", GROUNDED + " && q.is_sprinting && q.exertion > 0.8", 0.7, {
    "main:pos": lambda u: P(-0.3 * wave(u), -1.5 + 0.7 * wave(u, 0, 2), 1 * cwave(u)), "main:rot": lambda u: R(-6 + 4 * wave(u), 0, 0),
    "view:rot": lambda u: V(2 + 1.2 * abs(wave(u)), 0, 1.2 * wave(u))}, pri=113, file=FM)
fpl("sneak_creep", "FP Sneaking Creep", GROUNDED + " && q.is_sneaking && q.ground_speed >= 0.01", 1.6, {
    "main:pos": lambda u: P(-1, -2 + 0.3 * abs(wave(u)), -1 + 0.6 * wave(u)), "off:pos": lambda u: P(1, -2 + 0.3 * abs(wave(u, 0.5)), -1 + 0.6 * wave(u, 0.5)),
    "view:rot": lambda u: V(1.5, 0, 0.4 * wave(u))}, pri=111, file=FM)
fpl("sneak_hold", "FP Crouched Readiness", GROUNDED + " && q.is_sneaking && q.ground_speed < 0.01", 3.0, {
    "main:pos": lambda u: P(-1.5, -2.5 + 0.15 * wave(u), -1.5), "main:rot": lambda u: R(-6, 4, 0), "view:rot": lambda u: V(2 + 0.2 * wave(u, 0.2))}, pri=111, file=FM)
fpl("idle_breathe", "FP Idle Breathing", IDLE + " && q.idle_time < 15 && q.health >= 0.3", 3.6, {
    "main:pos": lambda u: P(0, 0.25 * wave(u), 0.1 * cwave(u)), "off:pos": lambda u: P(0, 0.25 * wave(u, 0.05), 0), "view:rot": lambda u: V(0.15 * wave(u))}, pri=105, file=FM)
fpl("idle_settled", "FP Settled Idle", IDLE + " && q.idle_time >= 15 && q.health >= 0.3", 6.0, {
    "main:pos": lambda u: P(0.5 * wave(u, 0, 1), -1.2 + 0.3 * wave(u, 0.1, 2), 0.4), "main:rot": lambda u: R(-4, 3 * wave(u), 2 * wave(u, 0.3)),
    "view:rot": lambda u: V(0.6 * wave(u, 0.6), 1.5 * wave(u, 0.2), 0)}, pri=106, file=FM)
fpl("idle_wounded", "FP Wounded Breathing", ALIVE + " && q.is_on_ground && q.ground_speed < 0.02 && q.health < 0.3", 1.4, {
    "main:pos": lambda u: P(0.2 * wave(u, 0, 5), -2 + 0.7 * wave(u), 0.5), "off:pos": lambda u: P(-1, -1.5 + 0.7 * wave(u, 0.1), 0),
    "view:rot": lambda u: V(1 + 0.8 * wave(u), 0, 0.5 * wave(u, 0.25))}, pri=108, file=FM)
fpl("shiver", "FP Shivering Hands", ALIVE + " && (q.is_cold || q.freezing > 0.2)", 0.25, {
    "main:pos": lambda u: P(0.25 * wave(u), 0.2 * wave(u, 0.3), 0), "off:pos": lambda u: P(0.25 * wave(u, 0.5), 0.2 * wave(u, 0.8), 0),
    "view:rot": lambda u: V(0, 0, 0.25 * wave(u, 0.2))}, pri=109, file=FM)
fpl("swim_stroke", "FP Front Crawl Strokes", ALIVE + " && q.is_swimming", 1.3, {
    "main:pos": lambda u: P(-2 + 3 * cwave(u), 2 * wave(u), -5 * max(0, wave(u))), "main:rot": lambda u: R(20 * max(0, wave(u)), 10 * cwave(u), 0),
    "off:pos": lambda u: P(2 - 3 * cwave(u, 0.5), 2 * wave(u, 0.5), -5 * max(0, wave(u, 0.5))), "view:rot": lambda u: V(0, 0, 2 * wave(u))}, pri=120, file=FM)
fpl("tread_water", "FP Treading Water", ALIVE + " && q.is_in_water && !q.is_swimming && !q.is_on_ground && !q.is_underwater", 1.1, {
    "main:pos": lambda u: P(2 * wave(u), -4 + 0.6 * cwave(u, 0, 2), -1), "off:pos": lambda u: P(-2 * wave(u), -4 + 0.6 * cwave(u, 0.5, 2), -1),
    "view:rot": lambda u: V(0.8 * wave(u, 0, 2))}, pri=119, file=FM)
fpl("underwater_drift", "FP Underwater Hover", ALIVE + " && q.is_underwater && !q.is_swimming && !q.is_on_ground", 2.4, {
    "main:pos": lambda u: P(1.5 * wave(u), -1 + 1 * wave(u, 0.25), -2 * max(0, cwave(u))), "main:rot": lambda u: R(6 * wave(u), 0, 10 * wave(u, 0.25)),
    "off:pos": lambda u: P(-1.5 * wave(u), -1 + 1 * wave(u, 0.75), -2 * max(0, cwave(u)))}, pri=119, file=FM)
fpl("ladder_climb", "FP Hand-Over-Hand Climb", ALIVE + " && q.is_climbing && math.abs(q.vertical_speed) > 0.02", 0.9, {
    "main:pos": lambda u: P(-1, 3 + 4 * wave(u), -2 + 1.5 * max(0, cwave(u))), "main:rot": lambda u: R(30 + 10 * wave(u), 0, 0),
    "off:pos": lambda u: P(1, 3 + 4 * wave(u, 0.5), -2 + 1.5 * max(0, cwave(u, 0.5))), "view:rot": lambda u: V(-3 + 1 * wave(u))}, pri=121, file=FM)
fpl("ladder_hang", "FP Cling To Ladder", ALIVE + " && q.is_climbing && math.abs(q.vertical_speed) <= 0.02", 2.4, {
    "main:pos": lambda u: P(-1, 4, -2), "main:rot": lambda u: R(30, 0, 0), "off:pos": lambda u: P(1, 3.4 + 0.2 * wave(u), -2), "view:rot": lambda u: V(-2 + 0.4 * wave(u, 0.2))}, pri=121, file=FM)
fpl("glide", "FP Elytra Glide Brace", ALIVE + " && q.is_fall_flying", 1.8, {
    "main:pos": lambda u: P(4, -3, 3 + 0.4 * wave(u)), "main:rot": lambda u: R(-10, 0, -20 + 2 * wave(u, 0, 2)), "off:pos": lambda u: P(-4, -3, 3 + 0.4 * wave(u, 0.5)),
    "view:rot": lambda u: V(0, 0, 1.2 * wave(u))}, pri=122, file=FM)
fpl("crawl", "FP Crawling Hand Plant", ALIVE + " && q.is_crawling", 1.4, {
    "main:pos": lambda u: P(-1, -4 + 2 * max(0, wave(u)), -3 * cwave(u)), "main:rot": lambda u: R(-40 + 10 * wave(u), 0, 0),
    "off:pos": lambda u: P(1, -4 + 2 * max(0, wave(u, 0.5)), -3 * cwave(u, 0.5)), "view:rot": lambda u: V(0, 0, 1.5 * wave(u))}, pri=122, file=FM)
fpl("freefall", "FP Freefall Flail", ALIVE + " && !q.is_on_ground && !q.is_fall_flying && !q.is_in_water && q.vertical_speed < -0.6", 0.5, {
    "main:pos": lambda u: P(2 + 2 * wave(u), 5 + 2 * wave(u, 0.2), 1), "main:rot": lambda u: R(40 + 20 * wave(u), 0, 15 * wave(u, 0.4)),
    "off:pos": lambda u: P(-2 - 2 * wave(u, 0.5), 5 + 2 * wave(u, 0.7), 1), "view:rot": lambda u: V(0, 0, 2 * wave(u, 0.1))}, pri=123, file=FM)
fpl("ride_reins", "FP Holding The Reins", ALIVE + " && q.is_riding && q.vehicle != 'boat' && q.vehicle != 'minecart'", 0.8, {
    "main:pos": lambda u: P(-2, -3 + 0.6 * abs(wave(u)), -2), "off:pos": lambda u: P(2, -3 + 0.6 * abs(wave(u)), -2),
    "view:rot": lambda u: V(0.6 * abs(wave(u)))}, pri=118, file=FM)
fpl("lava_panic", "FP Lava Panic", ALIVE + " && q.is_in_lava", 0.35, {
    "main:pos": lambda u: P(1.5 * wave(u), 3 + 2 * wave(u, 0.25), -2), "off:pos": lambda u: P(-1.5 * wave(u, 0.5), 3 + 2 * wave(u, 0.75), -2), "view:rot": lambda u: V(-1, 0, 2 * wave(u))},
    pri=124, file=FM)

# -------------------------------------------------------------------------- movement events
fpk("jump_lift", "FP Jump Hand Lift", event("jump", ALIVE + " && !q.is_sprinting"), 0.45, {
    "main:pos": [(0, Z), (0.08, P(0, -2, 0)), (0.2, P(0, 2.5, 0), "out_quad"), (0.45, Z)], "off:pos": [(0, Z), (0.1, P(0, -2, 0)), (0.22, P(0, 2, 0)), (0.45, Z)],
    "view": [(0, Z), (0.08, V(1)), (0.25, V(-0.8)), (0.45, Z)]}, pri=130, layer="gesture", file=FM)
fpk("sprint_jump", "FP Leaping Stride", event("jump", ALIVE + " && q.is_sprinting"), 0.55, {
    "main:pos": [(0, Z), (0.1, P(-2, 4, -3), "out_quad"), (0.3, P(-1, 2, 2)), (0.55, Z)], "off:pos": [(0, Z), (0.1, P(2, -2, 3)), (0.3, P(1, 2, -1)), (0.55, Z)],
    "view": [(0, Z), (0.1, V(-1.5, 0, 1)), (0.3, V(1, 0, -1)), (0.55, Z)]}, pri=131, layer="gesture", file=FM)
fpk("land_soft", "FP Soft Landing", event("land", ALIVE + " && q.last_fall < 3"), 0.35, {
    "main:pos": [(0, Z), (0.06, P(0, -1.5, 0), "out_quad"), (0.35, Z, "out_back")], "view": [(0, Z), (0.06, V(1)), (0.35, Z)]}, pri=132, layer="gesture", file=FM)
fpk("land_hard", "FP Heavy Landing", event("land", ALIVE + " && q.last_fall >= 3 && q.last_fall < 8"), 0.6, {
    "main:pos": [(0, Z), (0.05, P(-1, -6, 2), "out_expo"), (0.25, P(-1, -4, 1)), (0.6, Z, "in_out_sine")], "off:pos": [(0, Z), (0.05, P(1, -6, 2)), (0.6, Z)],
    "view": [(0, Z), (0.05, V(6, 0, 1)), (0.25, V(3)), (0.6, Z)]}, pri=133, layer="gesture", file=FM)
fpk("land_crash", "FP Crash Landing", event("land", ALIVE + " && q.last_fall >= 8"), 1.1, {
    "main:pos": [(0, Z), (0.05, P(-3, -10, 4), "out_expo"), (0.5, P(-2, -8, 3)), (1.1, Z)], "main:rot": [(0, Z), (0.05, R(-40, 0, 20)), (1.1, Z)],
    "off:pos": [(0, Z), (0.05, P(4, -10, 2)), (0.6, P(3, -7, 1)), (1.1, Z)], "view": [(0, Z), (0.05, V(14, -2, 6)), (0.5, V(8, 0, 2)), (1.1, Z)]},
    pri=134, layer="gesture", file=FM, events=[(0.0, "shake", {"intensity": "0.6", "duration": "0.4"})])
fpk("landing_roll", "FP Landing Roll", event("landing_roll"), 0.8, {"view": [(0, Z), (0.1, V(30)), (0.4, V(190)), (0.68, V(350)), (0.8, V(360))],
                                                                     "main:pos": [(0, Z), (0.1, P(0, -6, 0)), (0.68, P(0, -6, 0)), (0.8, Z)], "off:pos": [(0, Z), (0.1, P(0, -6, 2)), (0.7, P(0, -4, 0)), (0.8, Z)]},
    pri=300, file=FM)
fpk("sprint_burst", "FP Sprint Burst", event("sprint_start", GROUNDED), 0.4, {
    "main:pos": [(0, Z), (0.1, P(-1, -1, 3), "out_quad"), (0.4, Z)], "view": [(0, Z), (0.1, V(2)), (0.4, Z)]}, pri=129, layer="gesture", file=FM)
fpk("crouch_dip", "FP Crouch Dip", event("sneak_start", GROUNDED), 0.3, {
    "main:pos": [(0, Z), (0.08, P(-1, -3, -1), "out_quad"), (0.3, P(-1.5, -2.5, -1.5))], "view": [(0, Z), (0.08, V(3)), (0.3, V(2))]}, pri=129, layer="gesture", file=FM)
fpk("water_entry", "FP Splash Down", event("enter_water", ALIVE + " && q.vertical_speed < -0.3"), 0.7, {
    "main:pos": [(0, Z), (0.06, P(-2, 6, 2), "out_expo"), (0.4, P(-1, 2, 0)), (0.7, Z)], "off:pos": [(0, Z), (0.06, P(2, 6, 2)), (0.7, Z)],
    "view": [(0, Z), (0.06, V(-4, 0, 2)), (0.4, V(2)), (0.7, Z)]}, pri=135, layer="gesture", file=FM)
fpk("surface_gasp", "FP Surface Gasp", event("surface", ALIVE), 0.9, {
    "main:pos": [(0, Z), (0.15, P(-2, 4, -1)), (0.5, P(-3, 1, 0)), (0.9, Z)], "main:rot": [(0, Z), (0.15, R(20, 0, 0)), (0.9, Z)],
    "view": [(0, Z), (0.12, V(-6)), (0.4, V(-2, 0, 1)), (0.9, Z)]}, pri=136, layer="gesture", file=FM, events=[(0.1, "breath", {"strength": "1"})])
fpk("ladder_grab", "FP Grab The Rungs", event("climb_start", ALIVE), 0.4, {
    "main:pos": [(0, Z), (0.12, P(-1, 6, -3), "out_back"), (0.4, P(-1, 4, -2))], "off:pos": [(0, Z), (0.18, P(1, 5, -3), "out_back"), (0.4, P(1, 3.4, -2))]}, pri=137, layer="gesture", file=FM)
fpk("glide_spread", "FP Spread For Glide", event("glide_start"), 0.6, {
    "main:pos": [(0, Z), (0.15, P(6, 2, 2), "out_quad"), (0.6, P(4, -3, 3))], "off:pos": [(0, Z), (0.15, P(-6, 2, 2)), (0.6, P(-4, -3, 3))],
    "view": [(0, Z), (0.2, V(-3)), (0.6, Z)]}, pri=138, layer="gesture", file=FM)
fpk("mount_swing", "FP Swing Into Saddle", event("mount", ALIVE + " && q.vehicle != 'boat' && q.vehicle != 'minecart'"), 0.8, {
    "main:pos": [(0, Z), (0.2, P(-3, 4, -4)), (0.5, P(-2, -2, -2)), (0.8, P(-2, -3, -2))], "off:pos": [(0, Z), (0.25, P(3, 5, -3)), (0.8, P(2, -3, -2))],
    "view": [(0, Z), (0.2, V(-4, 0, -4)), (0.5, V(3, 0, 2)), (0.8, Z)]}, pri=139, layer="gesture", file=FM)
fpk("wake_rub", "FP Rub Eyes Awake", event("wake", "!q.is_dead"), 2.0, {
    "main:pos": [(0, P(0, -10, 0)), (0.4, P(-5, 6, -6)), (0.7, P(-4, 6.5, -6)), (1.0, P(-5, 6, -6)), (1.4, P(-3, 1, -2)), (2.0, Z)],
    "main:rot": [(0, Z), (0.4, R(60, 30, 0)), (0.7, R(60, 30, 10)), (1.0, R(60, 30, -10)), (2.0, Z)], "view": [(0, V(6)), (0.4, V(4, 0, 2)), (1.4, V(-2)), (2.0, Z)]},
    pri=140, file=FM)

# -------------------------------------------------------------------------- mining loops (replace the vanilla swing while digging)
MINING = ALIVE + " && q.is_mining && "
fpl("mine_pickaxe", "FP Pickaxe Mining Rhythm", MINING + "q.main_hand == 'pickaxe'", 0.6, {
    "main:pos": lambda u: P(3 * cwave(u), 4 * max(0, cwave(u)) - 3 * max(0, -cwave(u)), -3 * max(0, -cwave(u))), "main:rot": lambda u: R(45 * cwave(u), -6 * wave(u), 0),
    "view:rot": lambda u: V(0.8 * max(0, -cwave(u)))}, pri=170, layer="action", file=FX, replaces=True)
fpl("mine_axe", "FP Chopping Rhythm", MINING + "q.main_hand == 'axe'", 0.7, {
    "main:pos": lambda u: P(6 * cwave(u), 2 * cwave(u), -2 * max(0, -cwave(u))), "main:rot": lambda u: R(10 * cwave(u), 40 * cwave(u), 20 * cwave(u)),
    "off:pos": lambda u: P(-1 * cwave(u), -1, 0), "view:rot": lambda u: V(0, -1 * max(0, -cwave(u)), 0)}, pri=170, layer="action", file=FX, replaces=True)
fpl("mine_shovel", "FP Shovel Scoop Rhythm", MINING + "q.main_hand == 'shovel'", 0.65, {
    "main:pos": lambda u: P(-1, -3 + 4 * max(0, wave(u)), -4 * max(0, cwave(u))), "main:rot": lambda u: R(-30 + 50 * max(0, wave(u)), 0, 8 * wave(u)),
    "view:rot": lambda u: V(1.2 * max(0, cwave(u)))}, pri=170, layer="action", file=FX, replaces=True)
fpl("mine_hoe", "FP Hoe Raking", MINING + "q.main_hand == 'hoe'", 0.5, {
    "main:pos": lambda u: P(0, -2 + 2 * cwave(u), -4 * wave(u)), "main:rot": lambda u: R(-20 + 30 * cwave(u), 0, 0)}, pri=170, layer="action", file=FX, replaces=True)
fpl("mine_fist", "FP Punching Blocks", MINING + "q.main_hand == 'empty'", 0.3, {
    "main:pos": lambda u: P(-1 * max(0, wave(u)), 0.5 * wave(u), -5 * max(0, wave(u))), "main:rot": lambda u: R(10 * max(0, wave(u)), 6 * max(0, wave(u)), 0),
    "off:pos": lambda u: P(0, -1 + 0.4 * wave(u, 0.5), 0), "view:rot": lambda u: V(0.5 * max(0, wave(u, 0.1)))}, pri=170, layer="action", file=FX, replaces=True)
fpl("mine_shears", "FP Shearing Snips", MINING + "q.main_hand == 'shears'", 0.4, {
    "main:pos": lambda u: P(-1, 1, -2 + 0.6 * wave(u)), "main:rot": lambda u: R(0, 0, 16 * wave(u, 0, 2)), "off:pos": lambda u: P(2, 2, -3)}, pri=170, layer="action", file=FX, replaces=True)
fpl("mine_sword", "FP Hacking At Webs", MINING + "q.main_hand == 'sword'", 0.45, {
    "main:pos": lambda u: P(4 * wave(u), 1 * cwave(u, 0, 2), -3), "main:rot": lambda u: R(0, 50 * wave(u), 30 * wave(u))}, pri=170, layer="action", file=FX, replaces=True)
fpl("mine_block", "FP Bashing With A Block", MINING + "(q.main_hand == 'block' || q.main_hand == 'item' || q.main_hand == 'food')", 0.4, {
    "main:pos": lambda u: P(0, 2 * max(0, cwave(u)), -4 * max(0, -cwave(u))), "main:rot": lambda u: R(25 * cwave(u), 0, 0)}, pri=169, layer="action", file=FX, replaces=True)
fpl("mine_exhausted", "FP Weary Mining", MINING + "q.exertion > 0.85 && (q.main_hand == 'pickaxe' || q.main_hand == 'shovel')", 0.9, {
    "main:pos": lambda u: P(2 * cwave(u), -2 + 3 * max(0, cwave(u)), -2 * max(0, -cwave(u))), "main:rot": lambda u: R(30 * cwave(u) - 10, 0, 6 * wave(u, 0.2)),
    "view:rot": lambda u: V(2 + 1.5 * max(0, -cwave(u)), 0, 0.8 * wave(u))}, pri=171, layer="action", file=FX, replaces=True)
fpk("break_stone", "FP Stone Gives Way", event("break_block:stone", ALIVE), 0.4, {
    "main:pos": [(0, P(0, 0, -3)), (0.06, P(0, -1, -6), "out_expo"), (0.4, Z)], "view": [(0, Z), (0.05, V(1.5, 0, 0.5)), (0.4, Z)]}, pri=175, layer="gesture", file=FX)
fpk("break_wood", "FP Wood Splits", event("break_block:wood", ALIVE), 0.45, {
    "main:pos": [(0, Z), (0.06, P(-4, -1, -3), "out_expo"), (0.45, Z)], "main:rot": [(0, Z), (0.06, R(0, 30, 10)), (0.45, Z)]}, pri=175, layer="gesture", file=FX)
fpk("break_plant", "FP Flick Through Plants", event("break_block:plant", ALIVE), 0.3, {
    "main:pos": [(0, Z), (0.1, P(-3, 1, -2)), (0.3, Z)], "main:rot": [(0, Z), (0.1, R(0, 0, -25)), (0.3, Z)]}, pri=175, layer="gesture", file=FX)
fpk("break_ore", "FP Ore Prised Loose", event("break_block:ore", ALIVE), 0.7, {
    "main:pos": [(0, P(0, 0, -3)), (0.1, P(0, 2, 1)), (0.35, P(-1, 1, 0)), (0.7, Z)], "main:rot": [(0, Z), (0.1, R(25, 0, 0)), (0.7, Z)],
    "off:pos": [(0, Z), (0.25, P(-2, 2, -3)), (0.5, P(-1, 1, -1)), (0.7, Z)]}, pri=176, layer="gesture", file=FX)

# -------------------------------------------------------------------------- eating and drinking
EAT = ALIVE + " && q.is_using_item && q.use_anim == 'eat'"
fpl("eat_chew", "FP Chewing", EAT + " && q.main_hand != 'golden_food'", 0.32, {
    "view:rot": lambda u: V(0.6 * max(0, wave(u))), "off:pos": lambda u: P(0, -0.3 * abs(wave(u)), 0)}, pri=145, file=FC)
fpl("eat_gobble", "FP Wolfing Food Down", EAT + " && q.hunger > 0.7", 0.2, {
    "view:rot": lambda u: V(1.2 * max(0, wave(u)), 0, 0.5 * wave(u, 0.25)), "main:pos": lambda u: P(0, 0.5 * wave(u), -0.5 * wave(u))}, pri=146, file=FC)
fpl("eat_savour", "FP Savouring Golden Food", EAT + " && q.main_hand == 'golden_food'", 0.6, {
    "view:rot": lambda u: V(-1 + 0.5 * max(0, wave(u)), 0.3 * wave(u, 0.2)), "main:rot": lambda u: R(4 * wave(u), 0, 0)}, pri=146, file=FC)
fpl("drink_gulp", "FP Gulping", ALIVE + " && q.is_using_item && q.use_anim == 'drink'", 0.45, {
    "view:rot": lambda u: V(-4 - 1 * max(0, wave(u))), "main:pos": lambda u: P(0, 0.4 * max(0, wave(u)), 0), "off:pos": lambda u: P(0, -1, 0)}, pri=145, file=FC)
fpk("eat_finish", "FP Last Bite", event("use_finish", ALIVE + " && (q.main_hand == 'food' || q.main_hand == 'meat' || q.main_hand == 'bowl_food')"), 0.8, {
    "main:pos": [(0, P(-2, 2, -2)), (0.2, P(0, -6, 0)), (0.8, Z)], "view": [(0, Z), (0.15, V(1.5)), (0.4, V(-0.5)), (0.8, Z)]}, pri=185, file=FC)
fpk("golden_glow", "FP Golden Rush", event("use_finish", ALIVE + " && q.main_hand == 'golden_food'"), 1.2, {
    "main:pos": [(0, Z), (0.3, P(-2, 3, -3)), (0.8, P(-2, 4, -3)), (1.2, Z)], "main:rot": [(0, Z), (0.3, R(10, 20, 0)), (1.2, Z)], "view": [(0, Z), (0.3, V(-4)), (0.8, V(-3, 0, 1.5)), (1.2, Z)]},
    pri=186, file=FC, events=[(0.3, "particle", {"particle": "magic_glint", "count": "8", "at": "chest", "spread": "0.4"})])
fpk("drink_wipe", "FP Wipe Mouth", event("use_finish", ALIVE + " && (q.main_hand == 'potion' || q.main_hand == 'honey')"), 1.0, {
    "main:pos": [(0, Z), (0.2, P(0, -8, 0)), (1.0, Z)], "off:pos": [(0, Z), (0.35, P(-6, 5, -6)), (0.55, P(-2, 5, -6)), (1.0, Z)], "off:rot": [(0, Z), (0.35, R(60, -40, 0)), (1.0, Z)],
    "view": [(0, V(-4)), (0.3, Z), (1.0, Z)]}, pri=186, file=FC)
fpk("milk_shudder", "FP Milk Shudder", event("use_finish", ALIVE + " && q.main_hand == 'bucket'"), 0.8, {
    "view": [(0, V(-5)), (0.15, V(0, 0, 3)), (0.3, V(0, 0, -3)), (0.45, V(0, 0, 2)), (0.8, Z)], "main:pos": [(0, Z), (0.3, P(0, -4, 0)), (0.8, Z)]}, pri=186, file=FC)

# -------------------------------------------------------------------------- world interaction
fpk("door_push", "FP Push Door Open", event("interact:door_open", ALIVE), 0.6, {
    "main:pos": [(0, Z), (0.15, P(-2, 3, -6), "out_quad"), (0.3, P(2, 2, -4)), (0.6, Z)], "main:rot": [(0, Z), (0.15, R(0, 0, 60)), (0.6, Z)]}, pri=180, file=FI)
fpk("door_pull", "FP Pull Door Shut", event("interact:door_close", ALIVE), 0.6, {
    "main:pos": [(0, Z), (0.15, P(4, 2, -6)), (0.35, P(-2, 1, 0), "in_quad"), (0.6, Z)], "main:rot": [(0, Z), (0.15, R(0, -40, 50)), (0.6, Z)]}, pri=180, file=FI)
fpk("chest_lift", "FP Lift Chest Lid", event("interact:chest", ALIVE), 0.8, {
    "main:pos": [(0, Z), (0.2, P(-2, -4, -5)), (0.45, P(-2, 4, -6), "out_quad"), (0.8, P(0, -2, -2))], "off:pos": [(0, Z), (0.2, P(2, -4, -5)), (0.45, P(2, 4, -6)), (0.8, P(0, -2, -2))],
    "view": [(0, Z), (0.2, V(4)), (0.8, V(2))]}, pri=180, file=FI)
fpk("lever_pull", "FP Throw The Lever", event("interact", ALIVE + " && (q.event_arg == 'lever_on' || q.event_arg == 'lever_off')"), 0.55, {
    "main:pos": [(0, Z), (0.12, P(0, 0, -6)), (0.3, [0, "q.event_arg == 'lever_on' ? 4 : -4", -5]), (0.55, Z)], "main:rot": [(0, Z), (0.12, R(0, 0, 80)), (0.55, Z)]}, pri=180, file=FI)
fpk("button_press", "FP Press Button", event("interact:button", ALIVE), 0.4, {
    "main:pos": [(0, Z), (0.1, P(-1, 2, -2)), (0.18, P(-1, 2, -7), "in_quart"), (0.4, Z)], "main:rot": [(0, Z), (0.1, R(0, 20, 70)), (0.4, Z)]}, pri=180, file=FI)
fpk("crafting_work", "FP Work The Crafting Grid", event("interact:crafting", ALIVE), 1.0, {
    "main:pos": [(0, Z), (0.2, P(-2, -3, -6)), (0.4, P(1, -3, -7)), (0.6, P(-3, -3, -6)), (1.0, Z)], "off:pos": [(0, Z), (0.3, P(2, -4, -6)), (0.7, P(3, -3, -6)), (1.0, Z)],
    "view": [(0, Z), (0.2, V(8)), (0.8, V(8)), (1.0, Z)]}, pri=180, file=FI)
fpk("bucket_scoop", "FP Scoop With Bucket", event("bucket:fill", ALIVE), 0.7, {
    "main:pos": [(0, Z), (0.2, P(0, -6, -4), "in_quad"), (0.4, P(0, 2, -2), "out_quad"), (0.7, Z)], "main:rot": [(0, Z), (0.2, R(-50, 0, 0)), (0.4, R(10, 0, 0)), (0.7, Z)],
    "view": [(0, Z), (0.2, V(5)), (0.7, Z)]}, pri=181, file=FI)
fpk("bucket_pour", "FP Pour Bucket", event("bucket:empty", ALIVE), 0.8, {
    "main:pos": [(0, Z), (0.2, P(0, 2, -4)), (0.55, P(0, 1, -5)), (0.8, Z)], "main:rot": [(0, Z), (0.2, R(-10, 0, -20)), (0.55, R(-80, 0, -30)), (0.8, Z)]}, pri=181, file=FI)
fpk("place_block", "FP Set Block Down", event("place", ALIVE + " && q.main_hand == 'block' && q.head_pitch < 40"), 0.35, {
    "main:pos": [(0, Z), (0.1, P(0, 1, -5), "out_quad"), (0.18, P(0, -1, -6)), (0.35, Z)], "main:rot": [(0, Z), (0.1, R(-20, 0, 0)), (0.35, Z)]}, pri=182, file=FI)
fpk("place_below", "FP Place Block Underfoot", event("place", ALIVE + " && q.main_hand == 'block' && q.head_pitch >= 40"), 0.35, {
    "main:pos": [(0, Z), (0.12, P(0, -6, -3), "in_quad"), (0.35, Z)], "main:rot": [(0, Z), (0.12, R(-50, 0, 0)), (0.35, Z)], "view": [(0, Z), (0.12, V(2)), (0.35, Z)]}, pri=182, file=FI)
fpk("pickup_item", "FP Snatch Up Item", event("pickup", ALIVE + " && q.head_pitch > 20"), 0.5, {
    "off:pos": [(0, Z), (0.15, P(0, -8, -4), "in_quad"), (0.3, P(-1, -2, -2), "out_quad"), (0.5, Z)], "off:rot": [(0, Z), (0.15, R(-40, 0, 20)), (0.5, Z)]}, pri=176, layer="gesture", file=FI)
fpk("drop_toss", "FP Toss Item Away", event("drop", ALIVE), 0.45, {
    "main:pos": [(0, Z), (0.12, P(1, -3, 1)), (0.22, P(-2, 1, -6), "out_quad"), (0.45, Z)], "main:rot": [(0, Z), (0.22, R(20, 0, 0)), (0.45, Z)]}, pri=177, file=FI)
fpk("fish_cast", "FP Cast Fishing Line", event("fish_cast", ALIVE), 0.7, {
    "main:pos": [(0, Z), (0.25, P(-2, 8, 4), "out_quad"), (0.38, P(0, 0, -6), "in_quart"), (0.7, Z)], "main:rot": [(0, Z), (0.25, R(60, 0, 0)), (0.38, R(-20, 0, 0)), (0.7, Z)],
    "view": [(0, Z), (0.25, V(-2)), (0.4, V(1)), (0.7, Z)]}, pri=183, file=FI)
fpk("fish_reel", "FP Reel In Line", event("fish_reel", ALIVE), 0.6, {
    "main:pos": [(0, Z), (0.15, P(0, 4, 3), "out_expo"), (0.6, Z)], "main:rot": [(0, Z), (0.15, R(40, 0, 0)), (0.6, Z)], "off:pos": [(0, Z), (0.2, P(-1, 0, -2)), (0.4, P(-1, -1, -1)), (0.6, Z)]},
    pri=183, file=FI)
fpl("fish_wait", "FP Watch The Bobber", ALIVE + " && q.is_fishing", 2.8, {
    "main:pos": lambda u: P(0, 0.4 * wave(u) + 0.6 * max(0, wave(u, 0, 5)) * 0.3, 0), "main:rot": lambda u: R(2 * wave(u), 0, 1.5 * wave(u, 0.3))}, pri=141, file=FI)
fpk("flint_strike", "FP Strike Flint", event("interact", ALIVE + " && q.event_arg == 'ignite'"), 0.6, {
    "main:pos": [(0, Z), (0.15, P(2, 2, -2)), (0.24, P(-2, -1, -5), "in_quart"), (0.4, P(0, 1, -3)), (0.6, Z)], "main:rot": [(0, Z), (0.24, R(0, 0, 40)), (0.6, Z)]},
    pri=181, file=FI, events=[(0.24, "particle", {"particle": "spark", "count": "5", "at": "front", "spread": "0.15"})])
fpk("bonemeal_sprinkle", "FP Sprinkle Bone Meal", event("interact", ALIVE + " && q.event_arg == 'fertilize'"), 0.9, {
    "main:pos": [(0, Z), (0.2, P(0, 1, -4)), (0.9, P(0, 0, -3))], "main:rot": [(0, Z), (0.2, R(0, 0, -30)), (0.35, R(0, 0, -50)), (0.5, R(0, 0, -30)), (0.65, R(0, 0, -50)), (0.9, Z)]}, pri=181, file=FI)

# -------------------------------------------------------------------------- damage reactions
HURT = lambda kind: event("hurt", ALIVE + " && q.hurt_kind == '%s'" % kind)  # noqa: E731
fpk("hurt_front", "FP Hit From The Front", event("hurt_front", ALIVE + " && q.hurt_kind == 'melee'"), 0.45, {
    "main:pos": [(0, Z), (0.05, P(1, 1, 4), "out_expo"), (0.45, Z, "out_back")], "off:pos": [(0, Z), (0.05, P(-1, 1, 4)), (0.45, Z)], "view": [(0, Z), (0.05, V(-3, 0, 1.5)), (0.45, Z)]},
    pri=260, layer="reaction", file=FH)
fpk("hurt_back", "FP Hit From Behind", event("hurt_back", ALIVE), 0.5, {
    "main:pos": [(0, Z), (0.05, P(0, -2, -4), "out_expo"), (0.5, Z)], "off:pos": [(0, Z), (0.06, P(0, -2, -4)), (0.5, Z)], "view": [(0, Z), (0.05, V(5)), (0.2, V(2)), (0.5, Z)]},
    pri=260, layer="reaction", file=FH)
c = fp("hurt_side", "FP Hit From The Side", event("hurt", ALIVE + " && math.abs(q.hurt_dir) > 45 && math.abs(q.hurt_dir) <= 135"), 0.45, pri=259, layer="reaction", file=FH)
for t, k in ((0, 0), (0.05, 1), (0.2, 0.4), (0.45, 0)):
    c.key("fp_view", "rotation", t, [k * 1, "%g * (q.hurt_dir > 0 ? -1 : 1)" % (k * 3), "%g * (q.hurt_dir > 0 ? 1 : -1)" % (k * 5)], lerp="smooth")
    c.key("fp_main", "position", t, ["%g * (q.hurt_dir > 0 ? -1 : 1)" % (k * 3), k * 1, 0], lerp="smooth")
fpk("hurt_burn", "FP Swat At Flames", HURT("fire"), 0.9, {
    "off:pos": [(0, Z), (0.12, P(-3, 2, -2)), (0.25, P(3, 0, -2)), (0.4, P(-3, 2, -2)), (0.55, P(3, 0, -2)), (0.9, Z)], "off:rot": [(0, Z), (0.12, R(0, 0, 40)), (0.4, R(0, 0, 40)), (0.9, Z)],
    "view": [(0, Z), (0.1, V(-2, 0, 2)), (0.5, V(1, 0, -2)), (0.9, Z)]}, pri=258, layer="reaction", file=FH)
fpk("hurt_fall", "FP Fall Damage Jolt", HURT("fall"), 0.7, {
    "view": [(0, Z), (0.04, V(8, 0, 3)), (0.3, V(4, 0, 1)), (0.7, Z)], "main:pos": [(0, Z), (0.04, P(0, -5, 0)), (0.7, Z)], "off:pos": [(0, Z), (0.05, P(0, -6, 1)), (0.7, Z)]},
    pri=258, layer="reaction", file=FH)
fpk("hurt_blast", "FP Blast Concussion", HURT("explosion"), 1.2, {
    "view": [(0, Z), (0.04, V(-10, 6, 8)), (0.25, V(4, -3, -4)), (0.5, V(-2, 2, 2)), (1.2, Z)], "main:pos": [(0, Z), (0.04, P(4, 6, 6)), (0.6, P(1, 0, 1)), (1.2, Z)],
    "off:pos": [(0, Z), (0.04, P(-5, 6, 6)), (0.6, P(-1, 0, 1)), (1.2, Z)]}, pri=262, layer="reaction", file=FH)
fpk("hurt_arrow", "FP Arrow Strike", HURT("projectile"), 0.4, {
    "view": [(0, Z), (0.03, V(-2, 1, -3)), (0.4, Z)], "off:pos": [(0, Z), (0.08, P(-2, 0, 2)), (0.2, P(-3, -1, -1)), (0.4, Z)]}, pri=257, layer="reaction", file=FH)
fpk("hurt_freeze", "FP Frostbite Flinch", HURT("freeze"), 0.8, {
    "main:pos": [(0, Z), (0.1, P(-2, -2, 2)), (0.8, Z)], "off:pos": [(0, Z), (0.1, P(2, -2, 2)), (0.8, Z)], "view": [(0, Z), (0.1, V(2, 0, 1)), (0.2, V(2, 0, -1)), (0.3, V(2, 0, 1)), (0.8, Z)]},
    pri=257, layer="reaction", file=FH)
fpk("hurt_magic", "FP Magic Vertigo", HURT("magic"), 1.4, {
    "view": [(0, Z), (0.2, V(0, 3, 6)), (0.6, V(0, -3, -6)), (1.0, V(0, 2, 3)), (1.4, Z)], "main:pos": [(0, Z), (0.4, P(2, -2, 0)), (0.9, P(-2, -2, 0)), (1.4, Z)]},
    pri=257, layer="reaction", file=FH)
fpk("hurt_prick", "FP Thorn Prick", HURT("prick"), 0.5, {
    "main:pos": [(0, Z), (0.04, P(0, 2, 3), "out_expo"), (0.2, P(0, 1, 2)), (0.5, Z)], "main:rot": [(0, Z), (0.04, R(20, 0, 10)), (0.5, Z)]}, pri=256, layer="reaction", file=FH)
fpk("hurt_drown", "FP Lungs Burning", HURT("drown"), 1.0, {
    "off:pos": [(0, Z), (0.2, P(-4, 5, -5)), (0.8, P(-4, 5, -5)), (1.0, Z)], "off:rot": [(0, Z), (0.2, R(60, -30, 0)), (1.0, Z)],
    "view": [(0, Z), (0.15, V(-3, 0, 2)), (0.5, V(3, 0, -2)), (1.0, Z)]}, pri=258, layer="reaction", file=FH)
fpk("hurt_shock", "FP Lightning Seizure", HURT("lightning"), 1.0, {
    "view": [(0, Z), (0.05, V(-4, 2, 3)), (0.1, V(4, -2, -3)), (0.15, V(-3, 2, 2)), (0.2, V(3, -2, -2)), (0.3, V(-1, 1, 1)), (1.0, Z)],
    "main:pos": [(0, Z), (0.05, P(3, 4, 2)), (0.1, P(-2, 3, 2)), (0.2, P(2, 4, 1)), (1.0, Z)]}, pri=263, layer="reaction", file=FH)
fpk("blast_duck", "FP Duck From Blast", event("explosion_flinch", ALIVE), 0.9, {
    "main:pos": [(0, Z), (0.1, P(-3, 6, -3), "out_expo"), (0.5, P(-3, 5, -3)), (0.9, Z)], "off:pos": [(0, Z), (0.1, P(3, 6, -3)), (0.5, P(3, 5, -3)), (0.9, Z)],
    "view": [(0, Z), (0.1, V(6, "q.event_dir > 0 ? -2 : 2", 0)), (0.5, V(4)), (0.9, Z)]}, pri=255, layer="reaction", file=FH)
fpk("death_collapse", "FP Collapse", event("death"), 1.4, {
    "view": [(0, Z), (0.3, V(10, 0, 10)), (0.8, V(30, 0, 50)), (1.4, V(40, 0, 80))], "main:pos": [(0, Z), (0.4, P(2, -8, 2)), (1.4, P(4, -16, 4))],
    "off:pos": [(0, Z), (0.3, P(-2, -6, 2)), (1.4, P(-4, -16, 4))]}, pri=400, file=FH)

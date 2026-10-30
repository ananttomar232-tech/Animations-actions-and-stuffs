"""Player interactions part 2: mining, placing, consuming, fishing, animals, sleeping, workstation loops, equipment."""
from core import Clip, state, event, arm, leg, tilt, move, biped, strike, shake, wave, cwave
from player_interactions import CAT, T, ALIVE, Z, UPPER, gesture, snd, foley, LOW, MID, HIGH, CROUCH

FM = "player/mining"
FC = "player/consume"
FW = "player/workstations"

# ------------------------------------------------------------------ mining loops (overlay, synced via vanilla break progress)
MINE = ALIVE + " && q.is_mining"


def mine(cid, name, when, L, r0, r1, l0=None, l1=None, body=(0, 0), pri=120, head=None, ev_t=None, extra=None):
    c = Clip("player.interact." + cid, name, CAT, T, length=L, loop="loop", layer="overlay", priority=pri, trigger=state(MINE + " && " + when, exit_delay=0.2),
             blend_in=0.12, blend_out=0.3, mask=["right_arm", "left_arm", "body", "head"], file=FM)
    impact = ev_t if ev_t is not None else L * 0.45
    c.rot("right_arm", (0, arm('r', *r0)), (impact * 0.8, arm('r', *r0), "in_out_sine"), (impact, arm('r', *r1), "in_quart"), (L, arm('r', *r0), "in_out_sine"))
    if l0:
        c.rot("left_arm", (0, arm('l', *l0)), (impact, arm('l', *l1), "in_quart"), (L, arm('l', *l0), "in_out_sine"))
    c.rot("body", (0, tilt(body[0])), (impact, tilt(body[1]), "in_quart"), (L, tilt(body[0])))
    if head:
        c.rot("head", (0, tilt(*head)), (L, tilt(*head)))
    c.ev(impact, "impact", strength="0.35", material="dust")
    if extra:
        extra(c)
    return c


mine("mine_stone_pickaxe", "Pickaxe Strokes On Stone", "q.mine_target == 'stone' && q.main_hand == 'pickaxe' && q.head_pitch < 45 && q.head_pitch > -40", 0.5,
     (150, 6, 0), (60, 0, 0), body=(-4, 14))
mine("mine_metal_pickaxe", "Heavy Pick Blows On Ore", "q.mine_target == 'metal' && q.main_hand == 'pickaxe'", 0.65, (170, 0, 0), (50, 0, 0), l0=(120, 0, 0), l1=(50, 0, 0), body=(-8, 20))
mine("mine_wood_axe", "Chop Wood", "q.mine_target == 'wood' && q.main_hand == 'axe'", 0.55, (100, 70, -20), (90, -20, 0), body=(4, 10),
     extra=lambda c: c.rot("mw_root", (0, tilt(0, 20)), (0.25, tilt(0, -10), "in_quart"), (0.55, tilt(0, 20))))
mine("mine_dirt_shovel", "Dig With Shovel", "q.mine_target == 'dirt' && q.main_hand == 'shovel'", 0.6, (40, -6, 0), (10, -6, 0), l0=(50, -6, 0), l1=(20, -6, 0), body=(16, 34),
     extra=lambda c: c.rot("right_leg", (0, leg('r', 20)), (0.27, leg('r', 6)), (0.6, leg('r', 20))))
mine("mine_plant_hoe", "Slice Through Plants", "q.mine_target == 'plant' && q.main_hand == 'hoe'", 0.45, (60, 60, -20), (60, -30, 10), body=(20, 26))
mine("mine_plant_shears", "Snip With Shears", "q.mine_target == 'plant' && q.main_hand == 'shears'", 0.35, (70, -10, 20), (74, -6, 0), body=(10, 12))
mine("mine_stone_hand", "Punch At Stone", "q.mine_target == 'stone' && q.main_hand == 'empty'", 0.4, (70, 0, 20), (92, -4, 0), body=(2, 8))
mine("mine_wood_hand", "Punch A Log", "q.mine_target == 'wood' && q.main_hand == 'empty'", 0.42, (60, 10, 30), (94, -6, 0), l0=(70, -20, 40), l1=(60, -20, 40), body=(2, 10))
mine("mine_dirt_hand", "Scrape Dirt By Hand", "q.mine_target == 'dirt' && q.main_hand == 'empty'", 0.5, (50, -10, 0), (20, -10, 60), body=(24, 34),
     extra=lambda c: c.pos("mw_root", (0, move(0, -1.5)), (0.5, move(0, -1.5))))
mine("mine_plant_hand", "Pull Up Plants", "q.mine_target == 'plant' && q.main_hand == 'empty'", 0.6, (30, -10, 0), (60, -10, 0), body=(30, 18),
     extra=lambda c: c.pos("mw_root", (0, move(0, -2.0)), (0.6, move(0, -2.0))))
mine("mine_low", "Kneeling Low Mining", "q.head_pitch >= 45 && q.main_hand != 'empty'", 0.55, (80, 0, 0), (20, 0, 0), body=(20, 34), pri=125,
     extra=lambda c: (c.pos("mw_root", (0, move(0, -3.5)), (0.55, move(0, -3.5))), c.rot("right_leg", (0, leg('r', 80)), (0.55, leg('r', 80)))))
mine("mine_high", "Overhead Mining", "q.head_pitch <= -40 && q.main_hand != 'empty'", 0.55, (175, 10, 0), (130, 0, 0), l0=(150, 10, 0), l1=(120, 10, 0), body=(-10, -4), pri=125,
     head=(-30, 0, 0))
mine("mine_generic_tool", "Tool Work", "q.main_hand != 'empty' && q.main_hand != 'pickaxe' && q.main_hand != 'axe' && q.main_hand != 'shovel' && q.main_hand != 'hoe'", 0.5,
     (100, 10, 0), (60, -4, 0), body=(2, 10), pri=110)
mine("mine_tired", "Exhausted Mining", "q.hunger > 0.7 && q.main_hand == 'pickaxe'", 0.8, (120, 6, 0), (60, 0, 0), body=(12, 20), pri=126, head=(20, 0, 0))

# ------------------------------------------------------------------ placing, breaking, dropping, picking up
c = Clip("player.interact.place_block", "Place Block", CAT, T, length=0.5, loop="once", layer="action", priority=160,
         trigger=event("place", ALIVE + " && !q.is_sneaking && q.is_on_ground && q.main_hand != 'torch' && q.main_hand != 'seed' && q.main_hand != 'plant'"),
         blend_in=0.08, blend_out=0.2, file="player/interact")
# Placement reach follows the look pitch: looking down sets blocks low, looking up places overhead.
c.key("right_arm", "rotation", 0, [0, 0, 0]).key("right_arm", "rotation", 0.15, ["-(70 - q.head_pitch * 0.9)", "-6", 0], lerp="smooth")
c.key("right_arm", "rotation", 0.28, ["-(58 - q.head_pitch * 1.1)", "-6", 0], "in_quart").key("right_arm", "rotation", 0.5, [0, 0, 0], "in_out_sine")
c.key("mw_root", "position", 0, [0, 0, 0]).key("mw_root", "position", 0.2, [0, "math.clamp((q.head_pitch - 40) * 0.06, 0, 2.4)", 0]).key("mw_root", "position", 0.5, [0, 0, 0])
c.ev(0.2, "foley", kind="cloth", volume="0.3")
gesture("place_torch_wall", "Mount A Torch", event("place", ALIVE + " && q.main_hand == 'torch'"), 0.6, {
    "right_arm": [(0, arm('r', 60, 12)), (0.2, arm('r', 100, 10, -30)), (0.32, arm('r', 92, -6), "in_quart"), (0.6, Z)], "head": [(0, Z), (0.2, tilt(-6, 0, 8)), (0.6, Z)]})
gesture("place_careful", "Careful Edge Placement", event("place", ALIVE + " && q.is_sneaking"), 0.8, {
    "mw_root:pos": CROUCH(1.4), "right_arm": [(0, Z), (0.3, arm('r', 30, -6)), (0.5, arm('r', 18, -6), "in_out_sine"), (0.8, Z)], "head": [(0, Z), (0.3, tilt(50)), (0.8, Z)],
    "body": [(0, Z), (0.3, tilt(26)), (0.8, Z)]}, pri=162)
gesture("place_tower_jump", "Pillar Jump Placement", event("place", ALIVE + " && !q.is_on_ground"), 0.45, {
    "right_arm": [(0, Z), (0.1, arm('r', 30, -6)), (0.2, arm('r', 10, -6), "in_quart"), (0.45, Z)], "head": [(0, Z), (0.1, tilt(60)), (0.45, tilt(30))],
    "right_leg": [(0, Z), (0.1, leg('r', 40)), (0.45, Z)], "left_leg": [(0, Z), (0.1, leg('l', 40)), (0.45, Z)]}, pri=163)
gesture("plant_seed", "Press Seeds Into Soil", event("place", ALIVE + " && q.main_hand == 'seed'"), 0.9, {
    "mw_root:pos": CROUCH(3.4), "right_leg": [(0, Z), (0.3, leg('r', 70)), (0.6, leg('r', 70)), (0.9, Z)],
    "right_arm": [(0, Z), (0.35, arm('r', 30, -6)), (0.5, arm('r', 20, -6), "in_quart"), (0.9, Z)], "head": [(0, Z), (0.3, tilt(46)), (0.9, Z)]}, pri=164)
gesture("plant_sapling", "Plant A Sapling", event("place", ALIVE + " && q.main_hand == 'plant'"), 1.1, {
    "mw_root:pos": CROUCH(3.8), "right_arm": [(0, Z), (0.35, arm('r', 30, -6)), (0.55, arm('r', 22, -6)), (0.75, arm('r', 28, 10)), (1.1, Z)],
    "left_arm": [(0, Z), (0.6, arm('l', 26, 10)), (0.8, arm('l', 22, -6)), (1.1, Z)], "head": [(0, Z), (0.35, tilt(46)), (1.1, Z)]}, pri=164)
for mat, label, ra, body_d in (("stone", "Heave Loose Stone", (60, 0, 0), 14), ("wood", "Timber Finish", (90, -30, 20), 6), ("dirt", "Kick Loose Dirt", (20, 10, 0), 4),
                               ("plant", "Harvest Crop", (30, -6, 0), 30), ("other", "Brush Off Debris", (50, -20, 30), 8)):
    cond = "q.event_arg == '%s'" % mat if mat != "other" else "q.event_arg != 'stone' && q.event_arg != 'wood' && q.event_arg != 'dirt' && q.event_arg != 'plant'"
    tracks = {"right_arm": [(0, Z), (0.2, arm('r', *ra)), (0.5, Z)], "body": [(0, Z), (0.2, tilt(body_d)), (0.5, Z)]}
    if mat == "dirt":
        tracks["right_leg"] = [(0, Z), (0.15, leg('r', -20)), (0.3, leg('r', 30), "out_quad"), (0.5, Z)]
    if mat == "plant":
        tracks["mw_root:pos"] = CROUCH(2.6)
        tracks["right_arm"] = [(0, Z), (0.25, arm('r', 30, -6)), (0.45, arm('r', 80, -20, 30), "out_back"), (0.7, Z)]
    gesture("break_" + mat, label, event("break_block", ALIVE + " && " + cond), 0.7 if mat == "plant" else 0.5, tracks, pri=158, mask=UPPER + ["mw_root", "right_leg"])
gesture("drop_toss", "Toss Item Away", event("drop", ALIVE + " && !q.is_sneaking && !q.is_sprinting"), 0.5, {
    "right_arm": [(0, Z), (0.15, arm('r', 30, 10)), (0.28, arm('r', 80, -10), "out_quad"), (0.5, Z)]}, mask=UPPER)
gesture("drop_set_down", "Set Item Down Gently", event("drop", ALIVE + " && q.is_sneaking"), 0.9, {
    "mw_root:pos": CROUCH(3.0), "right_arm": [(0, Z), (0.35, arm('r', 30, -6)), (0.55, arm('r', 22, -6)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(44)), (0.9, Z)]}, pri=161)
gesture("drop_hurl", "Hurl Item While Running", event("drop", ALIVE + " && q.is_sprinting"), 0.45, {
    "right_arm": [(0, Z), (0.12, arm('r', 150, 20)), (0.22, arm('r', 90, -10), "out_quad"), (0.45, Z)], "body": [(0, Z), (0.22, tilt(10, -14)), (0.45, Z)]}, pri=161, mask=UPPER)
gesture("pickup_grab", "Scoop Item Up", event("pickup", ALIVE + " && !q.is_sprinting && !q.is_sneaking"), 0.6, {
    "mw_root:pos": CROUCH(2.4), "right_arm": [(0, Z), (0.25, arm('r', 30, -6)), (0.4, arm('r', 50, -10, 20)), (0.6, Z)], "body": [(0, Z), (0.25, tilt(30)), (0.6, Z)]})
gesture("pickup_snatch", "Snatch On The Run", event("pickup", ALIVE + " && q.is_sprinting"), 0.4, {
    "right_arm": [(0, Z), (0.12, arm('r', 20, 10)), (0.25, arm('r', 60, -10, 20)), (0.4, Z)], "body": [(0, Z), (0.12, tilt(26)), (0.4, Z)]}, pri=161, mask=UPPER)
gesture("pickup_gentle", "Crouched Careful Pickup", event("pickup", ALIVE + " && q.is_sneaking"), 0.8, {
    "mw_root:pos": CROUCH(3.4), "right_arm": [(0, Z), (0.3, arm('r', 24, -6)), (0.5, arm('r', 40, -10, 20)), (0.8, Z)], "head": [(0, Z), (0.3, tilt(46)), (0.8, Z)]}, pri=161)
gesture("pickup_food_sniff", "Pick Up And Sniff Food", event("pickup:food", ALIVE), 1.0, {
    "right_arm": [(0, Z), (0.35, arm('r', 92, -24, 30)), (0.7, arm('r', 94, -24, 30)), (1.0, Z)], "head": [(0, Z), (0.35, tilt(14)), (0.55, tilt(8)), (0.7, tilt(14)), (1.0, Z)]}, pri=163, mask=UPPER)
gesture("pickup_weapon_check", "Pick Up And Weigh Weapon", event("pickup", ALIVE + " && (q.event_arg == 'sword' || q.event_arg == 'axe')"), 1.0, {
    "right_arm": [(0, Z), (0.35, arm('r', 70, -20, 60)), (0.6, arm('r', 74, -18, -30)), (1.0, Z)], "head": [(0, Z), (0.35, tilt(20)), (1.0, Z)]}, pri=163, mask=UPPER)
gesture("xp_absorb", "Absorb Experience", event("xp_pickup", ALIVE), 0.6, {
    "body": [(0, Z), (0.2, tilt(-6)), (0.6, Z)], "head": [(0, Z), (0.2, tilt(-10)), (0.6, Z)],
    "right_arm": [(0, Z), (0.2, arm('r', 0, 14)), (0.6, Z)], "left_arm": [(0, Z), (0.2, arm('l', 0, 14)), (0.6, Z)]}, pri=120, layer="reaction")

# ------------------------------------------------------------------ eating and drinking (overlay states while the item is in use)
USING = ALIVE + " && q.is_using_item && q.use_anim == "


def consume(cid, name, when, L, r_base, r_amp, head_base, head_amp, harmonic=1, pri=130, events=(), body=None, left=None):
    c = Clip("player.interact." + cid, name, CAT, T, length=L, loop="loop", layer="overlay", priority=pri, trigger=state(when, exit_delay=0.05),
             blend_in=0.15, blend_out=0.2, mask=UPPER, file=FC)
    c.cycle("right_arm", "rotation", lambda u: [b + a * wave(u, 0, harmonic) for b, a in zip(arm('r', *r_base), r_amp)])
    c.cycle("head", "rotation", lambda u: [b + a * wave(u, 0.1, harmonic) for b, a in zip(tilt(*head_base), head_amp)])
    if body:
        c.cycle("body", "rotation", lambda u: tilt(*body))
    if left:
        c.cycle("left_arm", "rotation", lambda u: arm('l', *left))
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


consume("eat_bite", "Bite And Chew", USING + "'eat' && q.main_hand == 'food' && q.hunger <= 0.7 && q.in_combat == 0", 0.6, (88, -24, 30), (6, 0, 0), (6, 0, 0), (5, 0, 2), harmonic=2)
consume("eat_wolf_down", "Wolf Down Food", USING + "'eat' && q.hunger > 0.7", 0.35, (92, -26, 30), (10, 2, 0), (10, 0, 0), (8, 0, 0), harmonic=1, pri=131, body=(10, 0, 0))
consume("eat_cram_in_combat", "Cram Food Mid-Fight", USING + "'eat' && q.in_combat", 0.3, (94, -20, 20), (8, 0, 0), (2, 20, 0), (6, 6, 0), pri=132, left=(60, -20, 40))
consume("eat_spoon_stew", "Spoon Stew From Bowl", USING + "'eat' && q.main_hand == 'bowl_food'", 0.8, (60, -24, 20), (14, 0, 0), (24, 0, 0), (8, 0, 0), pri=133, left=(50, -20, 30))
consume("eat_golden_apple", "Savour A Golden Apple", USING + "'eat' && q.main_hand == 'golden_food'", 1.0, (96, -20, 30), (4, 0, 0), (-4, 0, 6), (4, 0, 2), pri=133,
        events=[(0.5, "particle", {"particle": "magic_glint", "count": "2", "at": "mouth", "spread": "0.2"})])
consume("eat_tear_meat", "Tear Into Meat", USING + "'eat' && q.main_hand == 'meat'", 0.7, (90, -20, 40), (8, 0, 10), (8, 0, 0), (6, 14, 6), pri=133)
consume("drink_potion", "Tip Back A Potion", USING + "'drink' && q.main_hand == 'potion'", 0.8, (130, -20, 40), (4, 0, 0), (-30, 0, 0), (4, 0, 0), pri=133, body=(-8, 0, 0))
consume("drink_milk", "Gulp Milk From Bucket", USING + "'drink' && q.main_hand == 'bucket'", 0.6, (120, -30, 10), (6, 0, 0), (-24, 0, 0), (6, 0, 0), pri=133, left=(110, -30, 10), body=(-10, 0, 0))
consume("drink_honey", "Sip Honey Slowly", USING + "'drink' && q.main_hand == 'honey'", 1.0, (110, -20, 30), (3, 0, 0), (-16, 0, 0), (3, 0, 0), pri=133)
c = consume("drink_chug_combat", "Chug Potion In Combat", USING + "'drink' && q.in_combat", 0.4, (150, -10, 60), (4, 6, 0), (-44, 30, 0), (5, 4, 0), pri=134, body=(-16, 20, 0),
            left=(70, -20, 40))
c.cycle("mw_root", "position", lambda u: move(0, -1.0 + 0.4 * wave(u)))
gesture("eat_finish", "Wipe Mouth After Eating", event("use_finish", ALIVE + " && q.last_use_time > 1 && (q.main_hand == 'food' || q.main_hand == 'meat' || q.main_hand == 'bowl_food')"), 0.8, {
    "right_arm": [(0, arm('r', 88, -24, 30)), (0.3, arm('r', 96, -40, 60)), (0.5, arm('r', 92, 0, 60)), (0.8, Z)], "head": [(0, Z), (0.4, tilt(0, -10)), (0.8, Z)]}, file=FC, mask=UPPER)
gesture("drink_finish", "Satisfied Exhale", event("use_finish", ALIVE + " && q.last_use_time > 1 && (q.main_hand == 'potion' || q.main_hand == 'honey' || q.main_hand == 'bucket')"), 0.9, {
    "right_arm": [(0, arm('r', 130, -20, 40)), (0.4, arm('r', 30, 10)), (0.9, Z)], "head": [(0, tilt(-30)), (0.3, tilt(-10)), (0.6, tilt(6)), (0.9, Z)],
    "body": [(0, tilt(-8)), (0.5, tilt(4)), (0.9, Z)]}, file=FC, mask=UPPER)
gesture("spyglass_raise", "Raise Spyglass", event("use_start", ALIVE + " && q.main_hand == 'spyglass'"), 0.4, {
    "right_arm": [(0, Z), (0.2, arm('r', 100, -30, 0)), (0.4, arm('r', 94, -30, 0))], "left_arm": [(0, Z), (0.3, arm('l', 80, -40, 20)), (0.4, arm('l', 80, -40, 20))]}, file=FC, mask=UPPER)
c = Clip("player.interact.spyglass_survey", "Survey Through Spyglass", CAT, T, length=4.0, loop="loop", layer="overlay", priority=135,
         trigger=state(USING + "'spyglass'", exit_delay=0.05), blend_in=0.3, mask=UPPER, file=FC)
c.cycle("right_arm", "rotation", lambda u: arm('r', 94, -30))
c.cycle("left_arm", "rotation", lambda u: arm('l', 80, -40, 20))
c.cycle("body", "rotation", lambda u: tilt(-2, 6 * wave(u), 0))
gesture("spyglass_lower", "Lower Spyglass", event("use_stop", ALIVE + " && q.main_hand == 'spyglass'"), 0.5, {
    "right_arm": [(0, arm('r', 94, -30)), (0.5, Z)], "left_arm": [(0, arm('l', 80, -40, 20)), (0.3, Z)]}, file=FC, mask=UPPER)
c = Clip("player.interact.horn_blow", "Sound The Horn", CAT, T, length=2.0, loop="hold", layer="overlay", priority=136,
         trigger=state(USING + "'toot_horn'", exit_delay=0.05), blend_in=0.15, mask=UPPER + ["mw_root"], file=FC)
c.rot("right_arm", (0, arm('r', 110, -30, 0)), (0.3, arm('r', 140, -20, 0)), (2.0, arm('r', 142, -20, 0)))
c.rot("body", (0, Z), (0.3, tilt(-14)), (2.0, tilt(-16)))
c.rot("head", (0, Z), (0.3, tilt(-24)), (2.0, tilt(-26)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 0, 30))

# ------------------------------------------------------------------ fishing
ROD = ALIVE + " && q.main_hand == 'fishing_rod'"
gesture("fish_cast_overhead", "Overhead Cast", event("fish_cast", ROD + " && !q.is_sneaking"), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 170, 6, 0)), (0.42, arm('r', 60, 0), "in_quart"), (0.9, arm('r', 70, 0))], "body": [(0, Z), (0.3, tilt(-12)), (0.42, tilt(14)), (0.9, tilt(4))],
    "mw_root:pos": [(0, Z), (0.3, move(0, 0, -0.6)), (0.42, move(0, 0, 1.0)), (0.9, Z)]}, file=FC, events=[(0.4, "whoosh", {"weight": "light"})])
gesture("fish_cast_sidearm", "Low Sidearm Cast", event("fish_cast", ROD + " && q.is_sneaking"), 0.8, {
    "right_arm": [(0, Z), (0.28, arm('r', 60, 80, -20)), (0.4, arm('r', 70, -10), "in_quart"), (0.8, arm('r', 70, 0))], "body": [(0, Z), (0.28, tilt(10, 30)), (0.4, tilt(14, -10)), (0.8, Z)]},
    file=FC, pri=161)
c = Clip("player.interact.fish_wait", "Wait For A Bite", CAT, T, length=5.0, loop="loop", layer="overlay", priority=125,
         trigger=state(ROD + " && q.is_fishing && q.ground_speed < 0.02", group="fish_wait", weight=4), blend_in=0.4, mask=UPPER, file=FC)
c.cycle("right_arm", "rotation", lambda u: arm('r', 70 + 2 * wave(u), 0))
c.cycle("head", "rotation", lambda u: tilt(14, 3 * wave(u), 0))
gesture("fish_wait_fidget", "Take Up Line Slack", state(ROD + " && q.is_fishing && q.ground_speed < 0.02", group="fish_wait", weight=1), 1.8, {
    "right_arm": [(0, arm('r', 70, 0)), (0.4, arm('r', 60, 10, -40)), (1.4, arm('r', 62, 10, -40)), (1.8, arm('r', 70, 0))],
    "left_arm": [(0, Z), (0.5, arm('l', 50, -30, 30)), (0.7, arm('l', 56, -24, 120)), (0.9, arm('l', 50, -30, 240)), (1.1, arm('l', 56, -24, 360)), (1.8, Z)],
    "head": [(0, tilt(14)), (0.6, tilt(30, -10, 8)), (1.4, tilt(30, -10, 8)), (1.8, tilt(14))]}, layer="overlay", pri=125, mask=UPPER, file=FC)
gesture("fish_reel_in", "Reel In", event("fish_reel", ROD), 0.7, {
    "right_arm": [(0, arm('r', 70, 0)), (0.15, arm('r', 120, 0), "out_quad"), (0.7, Z)], "body": [(0, Z), (0.15, tilt(-10)), (0.7, Z)],
    "mw_root:pos": [(0, Z), (0.15, move(0, 0, -1.2)), (0.7, Z)]}, file=FC)
gesture("fish_catch_admire", "Land The Catch", event("fish_catch", ALIVE), 1.6, {
    "right_arm": [(0, arm('r', 120, 0)), (0.4, arm('r', 150, -20, 20), "out_back"), (1.2, arm('r', 148, -20, 20)), (1.6, Z)],
    "left_arm": [(0, Z), (0.4, arm('l', 60, 30)), (1.2, arm('l', 60, 30)), (1.6, Z)], "head": [(0, Z), (0.4, tilt(-30)), (1.2, tilt(-30)), (1.6, Z)]}, pri=170, file=FC,
    events=[snd(0.4, "motionworks:water.splash_small", "0.5")])

# ------------------------------------------------------------------ animals, villagers and other players
E = lambda kind: event("interact_entity:" + kind, ALIVE)  # noqa: E731
FA = "player/creatures"
gesture("shear_sheep", "Kneel And Shear", E("shear"), 1.6, {
    "mw_root:pos": CROUCH(3.6), "right_leg": [(0, Z), (0.4, leg('r', 76)), (1.2, leg('r', 76)), (1.6, Z)],
    "right_arm": [(0, Z), (0.4, arm('r', 50, -10, 20)), (0.6, arm('r', 54, 6, 20)), (0.8, arm('r', 50, -10, 20)), (1.0, arm('r', 54, 6, 20)), (1.6, Z)],
    "left_arm": [(0, Z), (0.4, arm('l', 46, -14, 20)), (1.2, arm('l', 46, -14, 20)), (1.6, Z)], "head": [(0, Z), (0.4, tilt(36)), (1.6, Z)]}, file=FA,
    events=[snd(0.6, "minecraft:entity.sheep.shear", "0.4"), snd(1.0, "minecraft:entity.sheep.shear", "0.4", "1.1")])
gesture("milk_cow", "Crouch And Milk", E("milk"), 1.8, {
    "mw_root:pos": CROUCH(4.0), "right_leg": [(0, Z), (0.4, leg('r', 80)), (1.4, leg('r', 80)), (1.8, Z)], "left_leg": [(0, Z), (0.4, leg('l', 80)), (1.4, leg('l', 80)), (1.8, Z)],
    "right_arm": [(0, Z), (0.5, arm('r', 40, -10)), (0.7, arm('r', 30, -10)), (0.9, arm('r', 40, -10)), (1.1, arm('r', 30, -10)), (1.8, Z)],
    "left_arm": [(0, Z), (0.5, arm('l', 30, -10)), (0.7, arm('l', 40, -10)), (0.9, arm('l', 30, -10)), (1.1, arm('l', 40, -10)), (1.8, Z)]}, file=FA)
gesture("feed_animal", "Offer Food Low", E("feed"), 1.4, {
    "mw_root:pos": CROUCH(2.6), "right_arm": [(0, Z), (0.4, arm('r', 50, -6)), (1.0, arm('r', 52, -6)), (1.4, Z)], "head": [(0, Z), (0.4, tilt(30, 0, 8)), (1.4, Z)]}, file=FA)
gesture("feed_horse", "Offer Food To Horse", E("feed_horse"), 1.4, {
    "right_arm": [(0, Z), (0.4, arm('r', 100, -6, -40)), (1.0, arm('r', 102, -6, -40)), (1.4, Z)], "head": [(0, Z), (0.4, tilt(-10)), (1.4, Z)]}, file=FA, pri=161)
gesture("feed_bird", "Offer Seeds On Palm", E("feed_bird"), 1.4, {
    "right_arm": [(0, Z), (0.4, arm('r', 80, -10, -80)), (1.0, arm('r', 82, -10, -80)), (1.4, Z)], "head": [(0, Z), (0.4, tilt(20, 0, 10)), (1.4, Z)]}, file=FA, pri=161)
gesture("feed_pet", "Crouch To Feed Pet", E("feed_pet"), 1.4, {
    "mw_root:pos": CROUCH(4.0), "right_leg": [(0, Z), (0.4, leg('r', 80)), (1.0, leg('r', 80)), (1.4, Z)], "right_arm": [(0, Z), (0.4, arm('r', 40, -6, -60)), (1.0, arm('r', 42, -6, -60)), (1.4, Z)],
    "head": [(0, Z), (0.4, tilt(40)), (1.4, Z)]}, file=FA, pri=161)
gesture("pet_dog", "Scratch Behind The Ears", E("pet_dog"), 1.6, {
    "mw_root:pos": CROUCH(4.0), "right_leg": [(0, Z), (0.4, leg('r', 80)), (1.2, leg('r', 80)), (1.6, Z)],
    "right_arm": [(0, Z), (0.4, arm('r', 40, -6)), (0.6, arm('r', 44, 6, 20)), (0.8, arm('r', 40, -6)), (1.0, arm('r', 44, 6, 20)), (1.6, Z)], "head": [(0, Z), (0.4, tilt(40, 0, 10)), (1.6, Z)]}, file=FA)
gesture("pet_cat", "Stroke The Cat", E("pet_cat"), 1.6, {
    "mw_root:pos": CROUCH(4.4), "right_arm": [(0, Z), (0.4, arm('r', 30, -6)), (0.8, arm('r', 20, 6)), (1.2, arm('r', 30, -6)), (1.6, Z)], "head": [(0, Z), (0.4, tilt(46)), (1.6, Z)]}, file=FA)
gesture("pet_horse", "Pat The Horse's Neck", E("pet_horse"), 1.4, {
    "right_arm": [(0, Z), (0.35, arm('r', 110, -10)), (0.55, arm('r', 104, -10)), (0.75, arm('r', 110, -10)), (0.95, arm('r', 104, -10)), (1.4, Z)], "head": [(0, Z), (0.35, tilt(-14)), (1.4, Z)]}, file=FA)
gesture("pet_small", "Tickle A Small Creature", E("pet_small"), 1.2, {
    "mw_root:pos": CROUCH(4.6), "right_arm": [(0, Z), (0.35, arm('r', 20, -6)), (0.5, arm('r', 24, -6, 20)), (0.65, arm('r', 20, -6)), (1.2, Z)], "head": [(0, Z), (0.35, tilt(50)), (1.2, Z)]}, file=FA)
gesture("leash_loop", "Loop A Lead", E("leash"), 1.1, {
    "right_arm": [(0, Z), (0.3, arm('r', 70, 10, 60)), (0.5, arm('r', 72, 10, -40)), (0.7, arm('r', 60, 10, 40)), (1.1, Z)], "head": [(0, Z), (0.3, tilt(20)), (1.1, Z)]}, file=FA)
gesture("catch_in_bucket", "Scoop Creature Into Bucket", E("catch_fish"), 1.0, {
    "mw_root:pos": CROUCH(2.4), "right_arm": [(0, Z), (0.3, arm('r', 30, -6)), (0.45, arm('r', 10, -6), "in_quad"), (0.7, arm('r', 60, -10)), (1.0, Z)]}, file=FA,
    events=[snd(0.45, "motionworks:water.splash_small", "0.5")])
gesture("command_pet", "Command Pet To Sit", E("command_pet"), 0.8, {
    "right_arm": [(0, Z), (0.25, arm('r', 70, -10, 90)), (0.45, arm('r', 30, -10, 90), "in_quart"), (0.8, Z)], "head": [(0, Z), (0.3, tilt(30)), (0.8, Z)]}, file=FA)
gesture("name_tag", "Fasten A Name Tag", E("name_tag"), 1.2, {
    "mw_root:pos": CROUCH(3.0), "right_arm": [(0, Z), (0.4, arm('r', 50, -10, 40)), (0.6, arm('r', 52, -10, -20)), (1.2, Z)], "left_arm": [(0, Z), (0.4, arm('l', 46, -14)), (1.2, Z)]}, file=FA)
gesture("saddle_up", "Throw On A Saddle", E("saddle"), 1.2, {
    "right_arm": [(0, Z), (0.35, arm('r', 150, -20)), (0.55, arm('r', 90, -10), "in_quad"), (1.2, Z)], "left_arm": [(0, Z), (0.35, arm('l', 150, -20)), (0.55, arm('l', 90, -10), "in_quad"), (1.2, Z)],
    "body": [(0, Z), (0.35, tilt(-8)), (0.55, tilt(10)), (1.2, Z)]}, file=FA, events=[foley(0.55, "leather", "0.8")])
gesture("dye_sheep", "Rub Dye Into Wool", E("dye"), 1.2, {
    "right_arm": [(0, Z), (0.3, arm('r', 50, -10, 30)), (0.5, arm('r', 54, 10, -30)), (0.7, arm('r', 50, -10, 30)), (1.2, Z)], "mw_root:pos": CROUCH(2.4)}, file=FA)
gesture("give_allay", "Hand An Item To The Allay", E("give_item"), 1.2, {
    "right_arm": [(0, Z), (0.4, arm('r', 110, -10, -60)), (0.8, arm('r', 112, -10, -60)), (1.2, Z)], "head": [(0, Z), (0.4, tilt(-20)), (1.2, Z)]}, file=FA)
gesture("barter_toss", "Toss Gold To A Piglin", event("barter_toss", ALIVE), 0.8, {
    "right_arm": [(0, Z), (0.2, arm('r', 30, 10, -60)), (0.35, arm('r', 70, 0, -60), "out_quad"), (0.8, Z)], "head": [(0, Z), (0.35, tilt(10, 0, 8)), (0.8, Z)]}, file=FA)
gesture("greet_villager", "Lean In To Talk", E("villager"), 1.4, {
    "body": [(0, Z), (0.4, tilt(10)), (1.0, tilt(10)), (1.4, Z)], "head": [(0, Z), (0.4, tilt(10, 0, 8)), (1.4, Z)],
    "right_arm": [(0, Z), (0.4, arm('r', 30, -10, 20)), (0.7, arm('r', 40, 10, 20)), (1.4, Z)]}, file=FA)
gesture("greet_trader", "Greet The Wandering Trader", E("trader"), 1.4, {
    "right_arm": [(0, Z), (0.35, arm('r', 150, 20)), (0.55, arm('r', 160, 30)), (0.75, arm('r', 150, 20)), (1.4, Z)], "head": [(0, Z), (0.4, tilt(-6, 0, -6)), (1.4, Z)]}, file=FA)
gesture("touch_golem", "Touch The Iron Golem", E("golem"), 1.4, {
    "right_arm": [(0, Z), (0.5, arm('r', 120, -10)), (1.0, arm('r', 122, -10)), (1.4, Z)], "head": [(0, Z), (0.5, tilt(-30)), (1.4, Z)]}, file=FA)
gesture("greet_player", "Friendly Nod And Wave", E("greet"), 1.2, {
    "right_arm": [(0, Z), (0.3, arm('r', 140, 30)), (0.5, arm('r', 140, 50)), (0.7, arm('r', 140, 30)), (1.2, Z)], "head": [(0, Z), (0.3, tilt(14)), (0.5, tilt(-4)), (1.2, Z)]}, file=FA)
gesture("adjust_armor_stand", "Adjust Armour Stand", E("armor_stand"), 1.4, {
    "right_arm": [(0, Z), (0.4, arm('r', 80, -20, 30)), (0.8, arm('r', 90, 0, 0)), (1.4, Z)], "left_arm": [(0, Z), (0.4, arm('l', 80, -20, 30)), (1.4, Z)], "head": [(0, Z), (0.4, tilt(-4, 0, 8)), (1.4, Z)]}, file=FA)
gesture("rotate_item_frame", "Turn The Framed Item", E("item_frame"), 0.7, {
    "right_arm": [(0, Z), (0.25, arm('r', 90, -10, -40)), (0.45, arm('r', 90, -10, 50)), (0.7, Z)]}, file=FA)
gesture("trade_complete", "Pocket The Goods", event("trade", ALIVE), 1.0, {
    "right_arm": [(0, Z), (0.3, arm('r', 70, -10)), (0.6, arm('r', -10, 30, 20)), (1.0, Z)], "head": [(0, Z), (0.3, tilt(14)), (0.5, tilt(-4)), (1.0, Z)]}, pri=170, file=FA)

# ------------------------------------------------------------------ sleeping and waking
SLEEP = "!q.is_dead && q.is_sleeping"
c = Clip("player.interact.sleep_back", "Sleeping On Back", CAT, T, length=5.0, loop="loop", layer="base", priority=900,
         trigger=state(SLEEP, group="sleep", weight=3, min_time=10), blend_in=0.8, file="player/rest")
c.cycle("body", "scale", lambda u: [1 + 0.02 * wave(u), 1, 1 + 0.03 * wave(u)])
c.cycle("head", "rotation", lambda u: tilt(0, 0, 6 + 2 * wave(u)))
c.cycle("right_arm", "rotation", lambda u: arm('r', 0, 14 + wave(u)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 0, 14 + wave(u)))
c = Clip("player.interact.sleep_side", "Curled On Side", CAT, T, length=6.0, loop="loop", layer="base", priority=900,
         trigger=state(SLEEP, group="sleep", weight=2, min_time=10), blend_in=0.8, file="player/rest")
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 70))
c.cycle("right_leg", "rotation", lambda u: leg('r', 50 + 2 * wave(u)))
c.cycle("left_leg", "rotation", lambda u: leg('l', 40 + 2 * wave(u)))
c.cycle("right_arm", "rotation", lambda u: arm('r', 70, -30, 20))
c.cycle("left_arm", "rotation", lambda u: arm('l', 50, -20, 20))
c.cycle("body", "scale", lambda u: [1 + 0.02 * wave(u), 1, 1 + 0.03 * wave(u)])
c = Clip("player.interact.sleep_restless", "Restless Sleep", CAT, T, length=3.0, loop="loop", layer="base", priority=901,
         trigger=state(SLEEP + " && (q.health < 0.4 || q.hunger > 0.8)"), blend_in=0.6, file="player/rest")
c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 18 * wave(u, 0, 1)))
c.cycle("right_leg", "rotation", lambda u: leg('r', 20 * max(0, wave(u, 0.3))))
c.cycle("right_arm", "rotation", lambda u: arm('r', 20 * max(0, wave(u)), 20))
c.cycle("head", "rotation", lambda u: tilt(0, 14 * wave(u, 0.1), 0))
gesture("wake_rested", "Wake And Stretch", event("wake", "q.hunger < 0.6 && q.time_of_day < 0.3"), 2.2, {
    "right_arm": [(0, Z), (0.6, arm('r', 170, 20)), (1.4, arm('r', 176, 30)), (2.2, Z)], "left_arm": [(0, Z), (0.6, arm('l', 170, 20)), (1.4, arm('l', 176, 30)), (2.2, Z)],
    "body": [(0, Z), (0.8, tilt(-10)), (2.2, Z)], "head": [(0, Z), (0.8, tilt(-20)), (1.5, tilt(10)), (2.2, Z)]}, pri=180, file="player/rest")
gesture("wake_groggy", "Groggy Wake-Up", event("wake", "q.hunger >= 0.6 || q.time_of_day >= 0.3"), 2.4, {
    "right_arm": [(0, Z), (0.6, arm('r', 120, -30, 40)), (1.4, arm('r', 124, -26, 40)), (2.4, Z)], "head": [(0, tilt(20)), (0.8, tilt(30, 0, 10)), (1.6, tilt(10, 0, -6)), (2.4, Z)],
    "mw_root:pos": [(0, move(0, -1.0)), (1.4, move(0, -0.6)), (2.4, Z)]}, pri=180, file="player/rest")
gesture("wake_startled", "Startled Awake", event("wake", "q.near_hostile"), 1.0, {
    "mw_root:pos": [(0, Z), (0.1, move(0, 1.4)), (0.4, Z)], "right_arm": [(0, Z), (0.1, arm('r', 60, 40)), (1.0, Z)], "left_arm": [(0, Z), (0.1, arm('l', 60, 40)), (1.0, Z)],
    "head": [(0, Z), (0.1, tilt(-10, 30)), (0.4, tilt(-6, -30)), (1.0, Z)]}, pri=181, file="player/rest")

# ------------------------------------------------------------------ reading and consulting items
gesture("read_book", "Open And Read A Book", event("inspect_item:book", ALIVE), 3.0, {
    "right_arm": [(0, Z), (0.5, arm('r', 56, -20, 20)), (2.5, arm('r', 58, -20, 20)), (3.0, Z)], "left_arm": [(0, Z), (0.5, arm('l', 56, -20, 20)), (1.5, arm('l', 54, -30, -20)), (2.5, arm('l', 56, -20, 20)), (3.0, Z)],
    "head": [(0, Z), (0.5, tilt(30, -4)), (1.5, tilt(32, 4)), (2.5, tilt(30, -4)), (3.0, Z)]}, events=[snd(1.5, "motionworks:interact.page", "0.5")])
gesture("unfold_map", "Unfold The Map", event("inspect_item:map", ALIVE), 1.4, {
    "right_arm": [(0, Z), (0.5, arm('r', 54, 20, 10)), (1.0, arm('r', 52, -12, 10)), (1.4, arm('r', 52, -12, 10))], "left_arm": [(0, Z), (0.5, arm('l', 54, 20, 10)), (1.0, arm('l', 50, -14, 10)), (1.4, arm('l', 50, -14, 10))],
    "head": [(0, Z), (1.0, tilt(34)), (1.4, tilt(34))]}, events=[snd(0.5, "motionworks:interact.page", "0.5", "0.7")])
gesture("consult_compass", "Turn To Follow The Needle", event("inspect_item:device", ALIVE), 1.8, {
    "right_arm": [(0, Z), (0.4, arm('r', 60, -10, 20)), (1.4, arm('r', 62, -10, 20)), (1.8, Z)], "head": [(0, Z), (0.4, tilt(30)), (1.0, tilt(-6, 20)), (1.4, tilt(30)), (1.8, Z)],
    "mw_root": [(0, Z), (1.0, tilt(0, 14)), (1.8, Z)]})

# ------------------------------------------------------------------ celebrating everyday achievements
gesture("celebrate_level", "Level-Up Fist Pump", event("celebrate:level", ALIVE), 1.2, {
    "right_arm": [(0, Z), (0.25, arm('r', 60, -10, 40)), (0.45, arm('r', 160, 10), "out_back"), (0.8, arm('r', 162, 10)), (1.2, Z)],
    "head": [(0, Z), (0.45, tilt(-14)), (1.2, Z)], "mw_root:pos": [(0, Z), (0.45, move(0, 1.0)), (0.7, Z)]}, pri=175)
gesture("celebrate_tame", "Delighted Clap For New Friend", event("celebrate:tame", ALIVE), 1.4, {
    "right_arm": [(0, Z), (0.3, arm('r', 70, -24, 30)), (0.4, arm('r', 72, -10, 30)), (0.5, arm('r', 70, -24, 30)), (0.6, arm('r', 72, -10, 30)), (1.4, Z)],
    "left_arm": [(0, Z), (0.3, arm('l', 70, -24, 30)), (0.4, arm('l', 72, -10, 30)), (0.5, arm('l', 70, -24, 30)), (0.6, arm('l', 72, -10, 30)), (1.4, Z)],
    "head": [(0, Z), (0.4, tilt(10, 0, 10)), (1.4, Z)]}, pri=175, events=[snd(0.4, "motionworks:emote.clap", "0.4"), snd(0.6, "motionworks:emote.clap", "0.4")])

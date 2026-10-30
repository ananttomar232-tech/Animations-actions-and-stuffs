"""Player everyday interactions (category: player_interactions)."""
from core import Clip, state, event, arm, leg, tilt, move, biped, strike, shake, wave, cwave

CAT = "player_interactions"
T = "@player"
ALIVE = "!q.is_dead && !q.is_swimming"
Z = (0, 0, 0)
UPPER = ["right_arm", "left_arm", "body", "head"]


def gesture(cid, name, trig, L, tracks, pri=160, mask=None, layer="action", file="player/interact", events=(), loop="once", blend_in=0.12, blend_out=0.25):
    c = Clip("player.interact." + cid, name, CAT, T, length=L, loop=loop, layer=layer, priority=pri, trigger=trig, mask=mask, file=file,
             blend_in=blend_in, blend_out=blend_out)
    for bone, seq in tracks.items():
        ch = "position" if bone.endswith(":pos") else "rotation"
        c.keys(bone.split(":")[0], ch, seq, lerp="smooth")
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


def snd(t, sound, vol="0.5", pitch="1"):
    return (t, "sound", {"sound": sound, "volume": vol, "pitch": pitch})


def foley(t, kind="cloth", vol="0.5"):
    return (t, "foley", {"kind": kind, "volume": vol})


I = lambda kind: event("interact:" + kind, ALIVE)  # noqa: E731
LOW = " && q.event_height < -0.75"
MID = " && q.event_height >= -0.75 && q.event_height <= 0.35"
HIGH = " && q.event_height > 0.35"
CROUCH = lambda depth: [(0, Z), (0.25, move(0, -depth)), (0.75, move(0, -depth)), (1.0, Z)]  # noqa: E731

# ------------------------------------------------------------------ doors, trapdoors, gates
gesture("door_push_open", "Push Door Open", event("interact:door_open", ALIVE + " && !q.is_sneaking && q.near_hostile == 0"), 0.7, {
    "right_arm": [(0, Z), (0.18, arm('r', 70, -10, 30)), (0.4, arm('r', 80, 20, -10)), (0.7, Z)],
    "body": [(0, Z), (0.25, tilt(8, 10)), (0.7, Z)], "mw_root:pos": [(0, Z), (0.3, move(0, 0, 1)), (0.7, Z)]},
    events=[snd(0.2, "motionworks:interact.handle")])
gesture("door_shoulder_barge", "Shoulder Through Door", event("interact:door_open", ALIVE + " && (q.is_sprinting || q.near_hostile)"), 0.6, {
    "right_arm": [(0, Z), (0.15, arm('r', 30, -40, 20)), (0.6, Z)], "left_arm": [(0, Z), (0.15, arm('l', 40, 10)), (0.6, Z)],
    "body": [(0, Z), (0.15, tilt(12, 30, -6)), (0.35, tilt(6, 10)), (0.6, Z)], "mw_root:pos": [(0, Z), (0.2, move(0, -0.6, 1.6)), (0.6, Z)]}, pri=162,
    events=[snd(0.18, "motionworks:impact.wood", "0.4")])
gesture("door_peek_open", "Ease Door Open And Peek", event("interact:door_open", ALIVE + " && q.is_sneaking"), 1.4, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -10, 30)), (0.7, arm('r', 66, 6, 0)), (1.4, Z)],
    "head": [(0, Z), (0.5, tilt(4, 20, -12)), (1.0, tilt(4, 24, -14)), (1.4, Z)], "body": [(0, Z), (0.6, tilt(10, 10, -6)), (1.4, Z)]}, pri=163)
gesture("door_pull_closed", "Pull Door Closed", event("interact:door_close", ALIVE + " && q.forward_speed <= 0.02"), 0.7, {
    "right_arm": [(0, Z), (0.2, arm('r', 80, 30, -20)), (0.45, arm('r', 60, -20, 30)), (0.7, Z)],
    "body": [(0, Z), (0.25, tilt(4, 14)), (0.45, tilt(-2, -6)), (0.7, Z)]}, events=[snd(0.4, "motionworks:interact.handle", "0.4", "0.9")])
gesture("door_backhand_close", "Close Door Behind", event("interact:door_close", ALIVE + " && q.forward_speed > 0.02"), 0.6, {
    "right_arm": [(0, Z), (0.2, arm('r', -30, 40, -40)), (0.4, arm('r', -10, 20)), (0.6, Z)], "head": [(0, Z), (0.2, tilt(0, 40)), (0.6, Z)]}, pri=161, mask=UPPER)
gesture("iron_door_rattle", "Rattle Locked Iron Door", I("iron_door"), 1.1, {
    "right_arm": [(0, Z), (0.2, arm('r', 70, -10, 30)), (0.35, arm('r', 74, -6, 20)), (0.5, arm('r', 70, -10, 30)), (0.65, arm('r', 74, -6, 20)), (1.1, Z)],
    "head": [(0, Z), (0.6, tilt(0, 0, 10)), (1.1, Z)]}, events=[snd(0.35, "minecraft:block.iron_door.close", "0.2", "1.6"), snd(0.65, "minecraft:block.iron_door.close", "0.2", "1.7")])
gesture("trapdoor_lift_floor", "Lift Floor Hatch", event("interact:trapdoor_open", ALIVE + LOW), 1.0, {
    "mw_root:pos": CROUCH(3.5), "right_arm": [(0, Z), (0.3, arm('r', 60, -10)), (0.6, arm('r', 110, -10)), (1.0, Z)],
    "body": [(0, Z), (0.3, tilt(30)), (0.6, tilt(10)), (1.0, Z)], "head": [(0, Z), (0.3, tilt(30)), (1.0, Z)]}, events=[foley(0.2)])
gesture("trapdoor_push_overhead", "Push Hatch Overhead", event("interact:trapdoor_open", ALIVE + HIGH), 0.7, {
    "right_arm": [(0, Z), (0.2, arm('r', 140, 10)), (0.4, arm('r', 175, 10), "out_quad"), (0.7, Z)], "left_arm": [(0, Z), (0.25, arm('l', 150, 10)), (0.45, arm('l', 172, 10)), (0.7, Z)],
    "head": [(0, Z), (0.3, tilt(-40)), (0.7, Z)]})
gesture("trapdoor_slam_floor", "Drop Floor Hatch", event("interact:trapdoor_close", ALIVE + LOW), 0.8, {
    "mw_root:pos": CROUCH(2.5), "right_arm": [(0, Z), (0.25, arm('r', 100, -6)), (0.45, arm('r', 50, -6), "in_quad"), (0.8, Z)],
    "head": [(0, Z), (0.3, tilt(34)), (0.8, Z)]})
gesture("trapdoor_pull_down", "Pull Hatch Down", event("interact:trapdoor_close", ALIVE + " && q.event_height > -0.75"), 0.7, {
    "right_arm": [(0, Z), (0.2, arm('r', 165, 6)), (0.45, arm('r', 120, 6), "in_quad"), (0.7, Z)], "head": [(0, Z), (0.25, tilt(-36)), (0.7, Z)]})
gesture("gate_push", "Push Gate Open", I("gate_open"), 0.7, {
    "right_arm": [(0, Z), (0.2, arm('r', 40, -10, 20)), (0.45, arm('r', 56, 10)), (0.7, Z)], "body": [(0, Z), (0.3, tilt(10, 6)), (0.7, Z)],
    "head": [(0, Z), (0.25, tilt(20)), (0.7, Z)]}, events=[snd(0.3, "motionworks:interact.handle", "0.4", "0.8")])
gesture("gate_latch", "Swing Gate Shut", I("gate_close"), 0.7, {
    "right_arm": [(0, Z), (0.2, arm('r', 50, 30, -10)), (0.45, arm('r', 36, -20, 20)), (0.7, Z)], "body": [(0, Z), (0.3, tilt(6, -10)), (0.7, Z)]})

# ------------------------------------------------------------------ containers
gesture("chest_open_low", "Kneel And Lift Chest Lid", event("interact:chest", ALIVE + LOW), 1.0, {
    "mw_root:pos": CROUCH(3.0), "right_leg": [(0, Z), (0.25, leg('r', 60)), (0.75, leg('r', 60)), (1.0, Z)],
    "right_arm": [(0, Z), (0.3, arm('r', 50, -10)), (0.6, arm('r', 100, -10)), (1.0, Z)], "left_arm": [(0, Z), (0.35, arm('l', 50, -10)), (0.6, arm('l', 96, -10)), (1.0, Z)],
    "body": [(0, Z), (0.3, tilt(28)), (1.0, Z)], "head": [(0, Z), (0.35, tilt(36)), (1.0, Z)]}, events=[snd(0.5, "motionworks:interact.rummage", "0.3")])
gesture("chest_open_mid", "Lift Chest Lid", event("interact:chest", ALIVE + " && q.event_height >= -0.75"), 0.8, {
    "right_arm": [(0, Z), (0.25, arm('r', 60, -10)), (0.5, arm('r', 110, -10)), (0.8, Z)], "left_arm": [(0, Z), (0.3, arm('l', 60, -10)), (0.5, arm('l', 104, -10)), (0.8, Z)],
    "head": [(0, Z), (0.3, tilt(24)), (0.8, Z)]})
gesture("ender_chest_open", "Open Ender Chest Reverently", I("ender_chest"), 1.2, {
    "mw_root:pos": CROUCH(2.0), "right_arm": [(0, Z), (0.4, arm('r', 60, 10)), (0.8, arm('r', 90, 20)), (1.2, Z)], "left_arm": [(0, Z), (0.4, arm('l', 60, 10)), (0.8, arm('l', 90, 20)), (1.2, Z)],
    "head": [(0, Z), (0.4, tilt(30)), (0.8, tilt(10)), (1.2, Z)]}, events=[(0.8, "particle", {"particle": "magic_glint", "count": "4", "at": "front", "spread": "0.6"})])
gesture("barrel_pry_low", "Pry Barrel Lid (Floor)", event("interact:barrel", ALIVE + LOW), 0.9, {
    "mw_root:pos": CROUCH(2.6), "right_arm": [(0, Z), (0.3, arm('r', 50, -20, 40)), (0.55, arm('r', 70, 0, -20), "out_back"), (0.9, Z)],
    "head": [(0, Z), (0.3, tilt(40)), (0.9, Z)]}, events=[snd(0.55, "motionworks:impact.wood", "0.3", "1.4")])
gesture("barrel_pry_mid", "Pry Barrel Lid", event("interact:barrel", ALIVE + " && q.event_height >= -0.75"), 0.8, {
    "right_arm": [(0, Z), (0.25, arm('r', 70, -20, 40)), (0.5, arm('r', 90, 0, -20), "out_back"), (0.8, Z)], "head": [(0, Z), (0.3, tilt(14)), (0.8, Z)]})
gesture("shulker_open", "Kneel At Shulker Box", I("shulker"), 1.1, {
    "mw_root:pos": CROUCH(4.0), "right_leg": [(0, Z), (0.3, leg('r', 80)), (0.8, leg('r', 80)), (1.1, Z)], "left_leg": [(0, Z), (0.3, leg('l', -10)), (0.8, leg('l', -10)), (1.1, Z)],
    "right_arm": [(0, Z), (0.4, arm('r', 60, -20)), (0.7, arm('r', 90, -10)), (1.1, Z)], "left_arm": [(0, Z), (0.4, arm('l', 60, -20)), (0.7, arm('l', 90, -10)), (1.1, Z)]})
gesture("container_peek", "Peek Into Dispenser", I("container"), 0.9, {
    "head": [(0, Z), (0.3, tilt(20, 0, 10)), (0.6, tilt(22, 0, 12)), (0.9, Z)], "right_arm": [(0, Z), (0.3, arm('r', 60, -10, 20)), (0.9, Z)],
    "body": [(0, Z), (0.3, tilt(14)), (0.9, Z)]})

# ------------------------------------------------------------------ blocks and workstations (on use)
gesture("crafting_slap", "Spread Out On Workbench", I("crafting"), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -20, 20)), (0.5, arm('r', 54, 10, 20)), (0.9, Z)], "left_arm": [(0, Z), (0.3, arm('l', 60, -20, 20)), (0.5, arm('l', 54, 10, 20)), (0.9, Z)],
    "body": [(0, Z), (0.3, tilt(16)), (0.9, Z)]}, events=[snd(0.5, "motionworks:interact.tool_tap", "0.4")])
gesture("furnace_low", "Crouch At Furnace", event("interact:furnace", ALIVE + LOW), 1.0, {
    "mw_root:pos": CROUCH(3.4), "right_arm": [(0, Z), (0.35, arm('r', 60, -10)), (0.7, arm('r', 64, -10)), (1.0, Z)], "head": [(0, Z), (0.35, tilt(30)), (1.0, Z)]})
gesture("furnace_mid", "Feed The Furnace", event("interact:furnace", ALIVE + " && q.event_height >= -0.75"), 0.8, {
    "right_arm": [(0, Z), (0.3, arm('r', 80, -10)), (0.5, arm('r', 90, -10)), (0.8, Z)], "head": [(0, Z), (0.3, tilt(14)), (0.8, Z)]})
gesture("anvil_strike", "Test The Anvil", I("anvil"), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 140, 10)), (0.45, arm('r', 60, 0), "in_quart"), (0.9, Z)], "body": [(0, Z), (0.3, tilt(-6)), (0.45, tilt(18)), (0.9, Z)]},
    events=[snd(0.45, "minecraft:block.anvil.place", "0.25", "1.4")])
gesture("enchant_raise", "Hands Over Enchanting Table", I("enchanting"), 1.4, {
    "right_arm": [(0, Z), (0.5, arm('r', 70, 20, -20)), (1.0, arm('r', 74, 22, -20)), (1.4, Z)], "left_arm": [(0, Z), (0.5, arm('l', 70, 20, -20)), (1.0, arm('l', 74, 22, -20)), (1.4, Z)],
    "head": [(0, Z), (0.5, tilt(20)), (1.4, Z)]}, events=[(0.5, "particle", {"particle": "magic_glint", "count": "6", "at": "front", "spread": "0.8"})])
gesture("lectern_read", "Turn Lectern Page", event("interact:lectern", ALIVE + " && q.main_hand != 'book'"), 1.0, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -20, 30)), (0.55, arm('r', 60, 20, -30)), (1.0, Z)], "head": [(0, Z), (0.3, tilt(30)), (1.0, tilt(28))]},
    events=[snd(0.5, "motionworks:interact.page", "0.5")])
gesture("lectern_place_book", "Lay Book On Lectern", event("interact:lectern", ALIVE + " && q.main_hand == 'book'"), 0.9, {
    "right_arm": [(0, arm('r', 46, -18, 20)), (0.4, arm('r', 70, -10, 0)), (0.9, Z)], "left_arm": [(0, arm('l', 44, -16, 24)), (0.4, arm('l', 70, -10, 0)), (0.9, Z)],
    "head": [(0, Z), (0.4, tilt(24)), (0.9, Z)]})
gesture("bell_ring_mid", "Strike The Bell", event("interact:bell", ALIVE + " && q.event_height <= 0.5"), 0.6, {
    "right_arm": [(0, Z), (0.15, arm('r', 60, 40)), (0.25, arm('r', 90, -20), "in_quart"), (0.6, Z)], "body": [(0, Z), (0.15, tilt(0, 14)), (0.25, tilt(4, -10)), (0.6, Z)]})
gesture("bell_ring_high", "Reach Up And Ring Bell", event("interact:bell", ALIVE + " && q.event_height > 0.5"), 0.7, {
    "right_arm": [(0, Z), (0.2, arm('r', 160, 20)), (0.3, arm('r', 176, -10), "in_quart"), (0.7, Z)], "head": [(0, Z), (0.2, tilt(-40)), (0.7, Z)],
    "mw_root:pos": [(0, Z), (0.25, move(0, 1.0)), (0.7, Z)]})
# Height-adaptive reach: arm elevation follows how far above/below eye level the target is.
REACH = "-(70 + math.clamp(q.event_height, -1.6, 1.0) * 60)"
for state_name, label, swing, lean in (("lever_on", "Throw Lever Up", -40, -6), ("lever_off", "Haul Lever Down", 40, 8)):
    c = Clip("player.interact." + state_name, label, CAT, T, length=0.8, loop="once", layer="action", priority=160, trigger=event("interact:" + state_name, ALIVE),
             blend_in=0.1, blend_out=0.25, file="player/interact")
    c.key("right_arm", "rotation", 0, [0, 0, 0])
    c.key("right_arm", "rotation", 0.22, [REACH, "-20", "30"], lerp="smooth")
    c.key("right_arm", "rotation", 0.45, ["%s + %d" % (REACH, swing), "-10", "-30"], "in_quart")
    c.key("right_arm", "rotation", 0.8, [0, 0, 0], "in_out_sine")
    c.rot("body", (0, Z), (0.22, tilt(4)), (0.45, tilt(lean, 6)), (0.8, Z), lerp="smooth")
    c.key("mw_root", "position", 0, [0, 0, 0]).key("mw_root", "position", 0.3, [0, "math.clamp(-q.event_height * 1.6, 0, 2.6)", 0]).key("mw_root", "position", 0.8, [0, 0, 0])
    c.ev(0.45, "sound", sound="motionworks:interact.lever_clunk", volume="0.5")
c = Clip("player.interact.button_press", "Press Button", CAT, T, length=0.5, loop="once", layer="action", priority=160, trigger=event("interact:button", ALIVE),
         blend_in=0.08, blend_out=0.2, file="player/interact")
c.key("right_arm", "rotation", 0, [0, 0, 0]).key("right_arm", "rotation", 0.15, [REACH, "-14", "60"], lerp="smooth")
c.key("right_arm", "rotation", 0.24, ["%s - 8" % REACH, "-14", "60"], "in_quart").key("right_arm", "rotation", 0.5, [0, 0, 0], "in_out_sine")
c.key("right_arm", "position", 0, [0, 0, 0]).key("right_arm", "position", 0.24, [0, 0, "-1.2"], "in_quart").key("right_arm", "position", 0.5, [0, 0, 0])
c.key("head", "rotation", 0, [0, 0, 0]).key("head", "rotation", 0.15, ["math.clamp(-q.event_height * 30, -35, 35)", 0, 0]).key("head", "rotation", 0.5, [0, 0, 0])
gesture("bed_check", "Sit On Bed Edge", I("bed"), 1.6, {
    "mw_root:pos": [(0, Z), (0.5, move(0, -5)), (1.1, move(0, -5)), (1.6, Z)], "right_leg": [(0, Z), (0.5, leg('r', 80)), (1.1, leg('r', 80)), (1.6, Z)],
    "left_leg": [(0, Z), (0.5, leg('l', 80)), (1.1, leg('l', 80)), (1.6, Z)], "right_arm": [(0, Z), (0.5, arm('r', -20, 20)), (1.1, arm('r', -20, 20)), (1.6, Z)],
    "left_arm": [(0, Z), (0.5, arm('l', -20, 20)), (1.1, arm('l', -20, 20)), (1.6, Z)]})
gesture("note_block_tap", "Tap Note Block", I("note_block"), 0.5, {
    "mw_root:pos": CROUCH(2.0), "right_arm": [(0, Z), (0.15, arm('r', 50, -6)), (0.25, arm('r', 42, -6), "in_quart"), (0.5, Z)], "head": [(0, Z), (0.2, tilt(30, 0, 8)), (0.5, Z)]})
gesture("jukebox_insert", "Insert A Record", event("interact:jukebox", ALIVE + " && q.main_hand != 'empty'"), 0.9, {
    "mw_root:pos": CROUCH(2.0), "right_arm": [(0, Z), (0.3, arm('r', 60, -10)), (0.55, arm('r', 48, -10)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(30)), (0.9, tilt(-6, 0, 8))]})
gesture("jukebox_eject", "Pop The Record Out", event("interact:jukebox", ALIVE + " && q.main_hand == 'empty'"), 0.7, {
    "mw_root:pos": CROUCH(2.0), "right_arm": [(0, Z), (0.25, arm('r', 46, -10)), (0.4, arm('r', 70, -6), "out_back"), (0.7, Z)], "head": [(0, Z), (0.3, tilt(30)), (0.7, Z)]})
gesture("brewing_stir", "Stir The Brewing Stand", I("brewing"), 1.2, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -10, 20)), (0.5, arm('r', 62, 10, 20)), (0.7, arm('r', 60, -10, 20)), (0.9, arm('r', 62, 10, 20)), (1.2, Z)], "head": [(0, Z), (0.3, tilt(30)), (1.2, Z)]})
gesture("grindstone_crank", "Crank The Grindstone", I("grindstone"), 1.2, {
    "right_arm": [(0, Z), (0.25, arm('r', 50, 10)), (0.5, arm('r', 80, 10)), (0.75, arm('r', 50, 10)), (1.0, arm('r', 80, 10)), (1.2, Z)], "body": [(0, Z), (0.3, tilt(14)), (1.2, Z)]})
gesture("workstation_settle", "Settle At Workstation", I("workstation"), 1.0, {
    "right_arm": [(0, Z), (0.3, arm('r', 56, -20, 20)), (1.0, Z)], "left_arm": [(0, Z), (0.35, arm('l', 56, -20, 20)), (1.0, Z)], "body": [(0, Z), (0.35, tilt(18)), (1.0, Z)],
    "head": [(0, Z), (0.35, tilt(28)), (1.0, Z)]})
gesture("cauldron_scoop", "Scoop From Cauldron", event("interact:cauldron", ALIVE + " && q.main_hand != 'armor'"), 0.9, {
    "mw_root:pos": CROUCH(1.6), "right_arm": [(0, Z), (0.3, arm('r', 50, -10)), (0.55, arm('r', 30, -10)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(36)), (0.9, Z)]})
gesture("cauldron_wash", "Wash Dye From Armour", event("interact:cauldron", ALIVE + " && q.main_hand == 'armor'"), 1.4, {
    "mw_root:pos": CROUCH(1.6), "right_arm": [(0, Z), (0.3, arm('r', 46, -10)), (0.5, arm('r', 40, 10)), (0.7, arm('r', 46, -10)), (0.9, arm('r', 40, 10)), (1.4, Z)],
    "left_arm": [(0, Z), (0.3, arm('l', 46, -10)), (1.4, Z)], "head": [(0, Z), (0.3, tilt(40)), (1.4, Z)]}, events=[snd(0.5, "motionworks:water.splash_small", "0.3")])
gesture("composter_dump", "Tip Scraps Into Composter", event("interact:composter", ALIVE + " && q.main_hand != 'empty'"), 0.7, {
    "right_arm": [(0, Z), (0.25, arm('r', 70, -10, 40)), (0.45, arm('r', 60, -10, 100)), (0.7, Z)], "head": [(0, Z), (0.3, tilt(30)), (0.7, Z)]})
gesture("composter_empty", "Scoop Out Bone Meal", event("interact:composter", ALIVE + " && q.main_hand == 'empty'"), 0.9, {
    "mw_root:pos": CROUCH(2.0), "right_arm": [(0, Z), (0.3, arm('r', 50, -10)), (0.5, arm('r', 30, -10)), (0.7, arm('r', 60, -20, 30)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(40)), (0.9, Z)]})
gesture("beacon_reach", "Reach Toward Beacon", I("beacon"), 1.4, {
    "right_arm": [(0, Z), (0.5, arm('r', 100, 10)), (1.0, arm('r', 104, 10)), (1.4, Z)], "head": [(0, Z), (0.5, tilt(-24)), (1.0, tilt(-40)), (1.4, Z)]},
    events=[(0.6, "particle", {"particle": "magic_glint", "count": "8", "at": "front", "spread": "0.4"})])
gesture("anchor_charge", "Charge Respawn Anchor", I("respawn_anchor"), 1.1, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -20)), (0.45, arm('r', 46, -10), "in_quart"), (0.7, arm('r', 30, 30), "out_back"), (1.1, Z)],
    "left_arm": [(0, Z), (0.3, arm('l', 60, -20)), (0.45, arm('l', 46, -10), "in_quart"), (0.7, arm('l', 30, 30), "out_back"), (1.1, Z)],
    "body": [(0, Z), (0.45, tilt(20)), (0.7, tilt(-10)), (1.1, Z)], "head": [(0, Z), (0.3, tilt(36)), (0.7, tilt(-14)), (1.1, Z)]},
    events=[(0.45, "particle", {"particle": "ember", "count": "6", "at": "front", "spread": "0.4"})])
gesture("pot_plant", "Plant In Flower Pot", event("interact:flower_pot", ALIVE + " && q.main_hand != 'empty'"), 0.8, {
    "mw_root:pos": CROUCH(1.4), "right_arm": [(0, Z), (0.3, arm('r', 60, -10)), (0.5, arm('r', 46, -10)), (0.8, Z)], "head": [(0, Z), (0.3, tilt(34)), (0.8, Z)]})
gesture("pot_take", "Pull Plant From Pot", event("interact:flower_pot", ALIVE + " && q.main_hand == 'empty'"), 0.7, {
    "right_arm": [(0, Z), (0.25, arm('r', 46, -10)), (0.45, arm('r', 70, -10), "out_back"), (0.7, Z)], "head": [(0, Z), (0.3, tilt(30)), (0.7, Z)]})
gesture("cake_slice", "Grab A Slice Of Cake", I("cake"), 1.2, {
    "right_arm": [(0, Z), (0.25, arm('r', 50, -10)), (0.5, arm('r', 100, -30, 20)), (0.9, arm('r', 104, -30, 20)), (1.2, Z)], "head": [(0, Z), (0.25, tilt(30)), (0.6, tilt(6)), (1.2, Z)]},
    events=[snd(0.7, "minecraft:entity.generic.eat", "0.4")])
gesture("sign_wipe", "Wipe Sign Clean", I("sign"), 1.0, {
    "right_arm": [(0, Z), (0.25, arm('r', 80, -10, 20)), (0.45, arm('r', 82, 20, 20)), (0.65, arm('r', 80, -10, 20)), (1.0, Z)], "head": [(0, Z), (0.3, tilt(6)), (1.0, Z)]})
gesture("redstone_tinker", "Tinker With Redstone", I("tinker"), 1.0, {
    "mw_root:pos": CROUCH(3.0), "right_arm": [(0, Z), (0.3, arm('r', 40, -10, 40)), (0.6, arm('r', 42, -10, -20)), (1.0, Z)], "head": [(0, Z), (0.3, tilt(44, 0, 10)), (1.0, Z)]})
gesture("bookshelf_pull", "Pull A Book From The Shelf", I("bookshelf"), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 90, -10)), (0.5, arm('r', 70, -10)), (0.9, arm('r', 46, -18, 20))], "head": [(0, Z), (0.3, tilt(0, 0, 10)), (0.9, tilt(24))]},
    events=[snd(0.5, "motionworks:interact.page", "0.4", "0.8")])
gesture("pot_peek", "Peer Into Decorated Pot", I("pot"), 1.0, {
    "mw_root:pos": CROUCH(2.2), "head": [(0, Z), (0.35, tilt(46)), (0.7, tilt(48, 8)), (1.0, Z)], "body": [(0, Z), (0.35, tilt(24)), (1.0, Z)]})

# ------------------------------------------------------------------ items used on blocks
gesture("flint_strike", "Strike Flint And Steel", I("ignite"), 0.8, {
    "mw_root:pos": CROUCH(1.8), "right_arm": [(0, Z), (0.2, arm('r', 60, 10, 20)), (0.32, arm('r', 46, -14, 20), "in_quart"), (0.8, Z)],
    "left_arm": [(0, Z), (0.2, arm('l', 56, -10)), (0.8, Z)], "head": [(0, Z), (0.2, tilt(36)), (0.8, Z)]},
    events=[(0.32, "particle", {"particle": "spark", "count": "6", "at": "front", "spread": "0.2"})])
gesture("bucket_scoop", "Scoop With Bucket", event("bucket:fill", ALIVE), 0.9, {
    "mw_root:pos": CROUCH(2.4), "right_arm": [(0, Z), (0.3, arm('r', 30, -6)), (0.5, arm('r', 10, -6), "in_quad"), (0.75, arm('r', 50, -6)), (0.9, Z)],
    "body": [(0, Z), (0.3, tilt(30)), (0.9, Z)]}, events=[snd(0.5, "motionworks:water.splash_small", "0.4")])
gesture("bucket_pour", "Pour Bucket Out", event("bucket:empty", ALIVE + " && !q.is_on_fire"), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -6, 0)), (0.55, arm('r', 60, -6, 90)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(36)), (0.9, Z)]})
gesture("bucket_panic_pour", "Douse The Flames", event("bucket:empty", ALIVE + " && q.is_on_fire"), 0.7, {
    "right_arm": [(0, Z), (0.15, arm('r', 30, -6, 0)), (0.3, arm('r', 20, -6, 120), "out_expo"), (0.7, Z)], "body": [(0, Z), (0.2, tilt(30)), (0.7, Z)],
    "head": [(0, Z), (0.2, tilt(50)), (0.7, Z)]}, pri=165)
gesture("hoe_till", "Till The Soil", I("till"), 0.8, {
    "right_arm": [(0, Z), (0.25, arm('r', 110, -6)), (0.4, arm('r', 30, -6), "in_quart"), (0.8, Z)], "left_arm": [(0, Z), (0.25, arm('l', 90, -6)), (0.4, arm('l', 30, -6), "in_quart"), (0.8, Z)],
    "body": [(0, Z), (0.25, tilt(-4)), (0.4, tilt(24)), (0.8, Z)]}, events=[(0.4, "particle", {"particle": "dust_puff", "count": "3", "at": "front", "spread": "0.4"})])
gesture("axe_strip", "Strip Bark", I("strip"), 0.9, {
    "right_arm": [(0, Z), (0.2, arm('r', 120, -10, 20)), (0.5, arm('r', 50, -10, 20), "in_cubic"), (0.9, Z)], "body": [(0, Z), (0.5, tilt(14)), (0.9, Z)]})
gesture("shovel_flatten", "Flatten A Path", I("flatten"), 0.8, {
    "right_arm": [(0, Z), (0.25, arm('r', 50, -6)), (0.45, arm('r', 20, -6), "in_quart"), (0.8, Z)], "left_arm": [(0, Z), (0.25, arm('l', 50, -6)), (0.45, arm('l', 20, -6)), (0.8, Z)],
    "body": [(0, Z), (0.4, tilt(26)), (0.8, Z)], "right_leg": [(0, Z), (0.3, leg('r', 30)), (0.45, leg('r', 10)), (0.8, Z)]})
gesture("brush_away", "Brush Away Sand", state(ALIVE + " && q.is_using_item && q.use_anim == 'brush'", exit_delay=0.05), 0.8, {
    "right_arm": [(0, arm('r', 40, -10, 30)), (0.2, arm('r', 44, 10, 30)), (0.4, arm('r', 40, -10, 30)), (0.6, arm('r', 44, 10, 30)), (0.8, arm('r', 40, -10, 30))],
    "body": [(0, tilt(30)), (0.8, tilt(30))], "head": [(0, tilt(40)), (0.8, tilt(40))]}, layer="overlay", loop="loop", pri=140, mask=UPPER)
gesture("bone_meal_sprinkle", "Sprinkle Bone Meal", I("fertilize"), 0.9, {
    "mw_root:pos": CROUCH(1.6), "right_arm": [(0, Z), (0.3, arm('r', 50, -10, 60)), (0.45, arm('r', 54, -6, 30)), (0.6, arm('r', 50, -10, 60)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(40)), (0.9, Z)]},
    events=[(0.45, "particle", {"particle": "pollen", "count": "5", "at": "front", "spread": "0.3"})])
gesture("tie_lead", "Tie Lead To Post", I("tie_lead"), 1.0, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -10, 60)), (0.5, arm('r', 62, -10, -40)), (0.7, arm('r', 60, -10, 60)), (1.0, Z)], "left_arm": [(0, Z), (0.3, arm('l', 56, -20)), (1.0, Z)],
    "head": [(0, Z), (0.3, tilt(26)), (1.0, Z)]})
gesture("harvest_hive", "Harvest The Hive Gently", I("harvest_hive"), 1.4, {
    "right_arm": [(0, Z), (0.5, arm('r', 80, -10)), (0.9, arm('r', 84, -10)), (1.4, Z)], "body": [(0, Z), (0.5, tilt(-6)), (1.4, Z)], "head": [(0, Z), (0.5, tilt(0, 14, 6)), (1.4, Z)]})
gesture("pick_berries", "Pick Berries", I("pick_berries"), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 50, -10)), (0.45, arm('r', 54, -6)), (0.6, arm('r', 70, -20, 30)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(30)), (0.9, Z)]})
gesture("carve_pumpkin", "Carve A Pumpkin", I("carve"), 1.3, {
    "mw_root:pos": CROUCH(2.0), "right_arm": [(0, Z), (0.3, arm('r', 50, -10, 40)), (0.5, arm('r', 54, 10, 40)), (0.7, arm('r', 50, -10, 40)), (0.9, arm('r', 54, 10, 40)), (1.3, Z)],
    "left_arm": [(0, Z), (0.3, arm('l', 50, -10)), (1.3, Z)], "head": [(0, Z), (0.3, tilt(36)), (1.3, Z)]})
gesture("cook_on_campfire", "Lay Food On Campfire", I("cook"), 1.0, {
    "mw_root:pos": CROUCH(3.0), "right_arm": [(0, Z), (0.35, arm('r', 50, -10)), (0.6, arm('r', 40, -10)), (1.0, Z)], "head": [(0, Z), (0.35, tilt(40)), (1.0, Z)]})
gesture("launch_firework", "Light And Back Away", I("launch_firework"), 1.2, {
    "mw_root:pos": [(0, Z), (0.25, move(0, -2.0)), (0.5, move(0, -1.0, -1.0)), (1.2, Z)], "right_arm": [(0, Z), (0.25, arm('r', 40, -10)), (0.5, arm('r', 60, 30)), (1.2, Z)],
    "head": [(0, Z), (0.25, tilt(40)), (0.8, tilt(-50)), (1.2, Z)]})
gesture("place_vehicle", "Set Down A Vehicle", I("place_vehicle"), 0.9, {
    "mw_root:pos": CROUCH(2.0), "right_arm": [(0, Z), (0.35, arm('r', 50, -10)), (0.55, arm('r', 30, -10)), (0.9, Z)], "left_arm": [(0, Z), (0.35, arm('l', 50, -10)), (0.55, arm('l', 30, -10)), (0.9, Z)]})
gesture("insert_eye", "Seat An Eye Of Ender", I("insert_eye"), 1.2, {
    "mw_root:pos": CROUCH(2.6), "right_arm": [(0, Z), (0.4, arm('r', 50, -10)), (0.6, arm('r', 40, -10), "in_quart"), (1.2, Z)], "head": [(0, Z), (0.4, tilt(44)), (0.8, tilt(10)), (1.2, Z)]},
    events=[(0.6, "particle", {"particle": "magic_glint", "count": "8", "at": "front", "spread": "0.4"})])
gesture("wax_copper", "Rub Wax Onto Copper", I("wax"), 1.1, {
    "right_arm": [(0, Z), (0.3, arm('r', 80, -10, 30)), (0.5, arm('r', 82, 10, -30)), (0.7, arm('r', 80, -10, 30)), (0.9, arm('r', 82, 10, -30)), (1.1, Z)]})

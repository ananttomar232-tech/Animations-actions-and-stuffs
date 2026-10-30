"""Player interactions part 3: live workstation/menu loops, equipment changes and small world details."""
from core import Clip, state, event, arm, leg, tilt, move, biped, strike, shake, wave, cwave
from player_interactions import CAT, T, ALIVE, Z, UPPER, gesture, snd, foley, LOW, MID, HIGH, CROUCH, I

FW = "player/workstations"


def menu_loop(menu, name, L, tracks, crouch=0.0, events=(), group=None, weight=1, file=FW):
    """Looping work animation while a menu is open; other players see the same thing."""
    c = Clip("player.interact.work_" + menu, name, CAT, T, length=L, loop="loop", layer="base", priority=120,
             trigger=state(ALIVE + " && q.menu == '%s' && q.ground_speed < 0.02" % menu, group=group or "menu_" + menu, weight=4 if group is None else weight),
             blend_in=0.35, blend_out=0.3, file=file)
    for bone, fn in tracks.items():
        ch = "position" if bone.endswith(":pos") else "rotation"
        c.cycle(bone.split(":")[0], ch, fn)
    if crouch:
        c.cycle("mw_root", "position", lambda u: move(0, -crouch))
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


A = lambda side, f, o=0, t=0: (lambda u: arm(side, f, o, t))  # noqa: E731
menu_loop("chest", "Rummage Through Chest", 1.6, {
    "right_arm": lambda u: arm('r', 60 + 14 * wave(u), -10 + 16 * wave(u, 0.3)), "left_arm": lambda u: arm('l', 56 + 10 * wave(u, 0.5), -10 + 10 * wave(u, 0.7)),
    "body": lambda u: tilt(26 + 2 * wave(u)), "head": lambda u: tilt(34, 8 * wave(u, 0.2), 0)}, crouch=1.4, events=[snd(0.4, "motionworks:interact.rummage", "0.25")])
menu_loop("large_chest", "Search A Large Chest", 2.4, {
    "right_arm": lambda u: arm('r', 64 + 16 * wave(u), -10 + 30 * wave(u, 0.25)), "left_arm": lambda u: arm('l', 64 + 16 * wave(u, 0.5), -10 + 30 * wave(u, 0.75)),
    "body": lambda u: tilt(28, 12 * wave(u), 0), "head": lambda u: tilt(36, 14 * wave(u, 0.1), 0)}, crouch=1.6, events=[snd(0.6, "motionworks:interact.rummage", "0.3"), snd(1.8, "motionworks:interact.rummage", "0.25")])
menu_loop("shulker", "Sort A Shulker Box", 1.8, {
    "right_arm": lambda u: arm('r', 50 + 10 * wave(u), -14), "left_arm": lambda u: arm('l', 50 - 10 * wave(u), -14), "right_leg": lambda u: leg('r', 80), "head": lambda u: tilt(40, 0, 6 * wave(u))},
    crouch=4.0)
menu_loop("crafting", "Craft At The Workbench", 1.2, {
    "right_arm": lambda u: arm('r', 62 + 20 * max(0, wave(u)), -16, 20), "left_arm": lambda u: arm('l', 56, -20, 20),
    "body": lambda u: tilt(18 + 2 * wave(u, 0, 2)), "head": lambda u: tilt(30, 0, 0)}, events=[snd(0.3, "motionworks:interact.tool_tap", "0.35")])
menu_loop("furnace", "Tend The Furnace", 2.0, {
    "right_arm": lambda u: arm('r', 50 + 10 * wave(u), -10), "left_arm": lambda u: arm('l', 40, 10, -30), "head": lambda u: tilt(26, 0, 0), "body": lambda u: tilt(16)}, crouch=2.0)
menu_loop("smoker", "Fan The Smoker", 1.0, {
    "right_arm": lambda u: arm('r', 50, -10, 40 + 40 * wave(u)), "left_arm": lambda u: arm('l', 30, 10), "head": lambda u: tilt(20, -10, 0), "body": lambda u: tilt(14, 0, 0)},
    crouch=1.6, events=[(0.5, "particle", {"particle": "smoke_wisp", "count": "1", "at": "front", "spread": "0.3"})])
menu_loop("blast_furnace", "Shield Face From The Blast Heat", 1.8, {
    "right_arm": lambda u: arm('r', 60 + 6 * wave(u), -10), "left_arm": lambda u: arm('l', 110, -40, 30), "head": lambda u: tilt(10, 20, 0), "body": lambda u: tilt(-4, 10, 0)},
    crouch=1.0, events=[(0.9, "particle", {"particle": "ember", "count": "2", "at": "front", "spread": "0.4"})])
menu_loop("anvil", "Hammer At The Anvil", 0.8, {
    "right_arm": lambda u: arm('r', 70 + 60 * max(0, wave(u, 0.25)), 0), "left_arm": lambda u: arm('l', 50, -20, 20), "body": lambda u: tilt(16 + 6 * max(0, wave(u, 0.75))),
    "head": lambda u: tilt(30, 0, 0)}, events=[snd(0.6, "minecraft:block.anvil.use", "0.2"), (0.6, "particle", {"particle": "spark", "count": "4", "at": "front", "spread": "0.2"})])
menu_loop("enchanting", "Channel The Enchantment", 3.0, {
    "right_arm": lambda u: arm('r', 70 + 6 * wave(u), 24 + 6 * wave(u, 0.3), -20), "left_arm": lambda u: arm('l', 70 + 6 * wave(u, 0.5), 24 + 6 * wave(u, 0.8), -20),
    "head": lambda u: tilt(20 + 4 * wave(u), 0, 0), "body": lambda u: tilt(6)}, events=[(1.0, "particle", {"particle": "magic_glint", "count": "3", "at": "front", "spread": "0.8"}),
                                                                                   (2.5, "particle", {"particle": "magic_glint", "count": "3", "at": "front", "spread": "0.8"})])
menu_loop("brewing", "Measure And Pour Potions", 2.2, {
    "right_arm": lambda u: arm('r', 70 + 10 * wave(u), -14, 40 + 40 * max(0, wave(u, 0.2))), "left_arm": lambda u: arm('l', 60, -20, 20), "head": lambda u: tilt(30, 0, 6 * wave(u))})
menu_loop("grindstone", "Work The Grindstone", 0.9, {
    "right_arm": lambda u: arm('r', 65 + 20 * wave(u), 10 + 8 * cwave(u)), "left_arm": lambda u: arm('l', 56, -20, 30), "body": lambda u: tilt(16 + 3 * wave(u)), "head": lambda u: tilt(30)},
    events=[(0.45, "particle", {"particle": "spark", "count": "2", "at": "front", "spread": "0.2"})])
menu_loop("stonecutter", "Guide Stone Through The Saw", 1.4, {
    "right_arm": lambda u: arm('r', 54 + 6 * wave(u), -10 + 10 * wave(u)), "left_arm": lambda u: arm('l', 54 + 6 * wave(u), -10 - 10 * wave(u)), "head": lambda u: tilt(38), "body": lambda u: tilt(22)},
    events=[(0.7, "particle", {"particle": "dust_puff", "count": "1", "at": "front", "spread": "0.3"})])
menu_loop("loom", "Weave At The Loom", 1.0, {
    "right_arm": lambda u: arm('r', 60, -20 + 30 * wave(u)), "left_arm": lambda u: arm('l', 60, -20 - 30 * wave(u)), "head": lambda u: tilt(26, 6 * wave(u), 0), "body": lambda u: tilt(14)})
menu_loop("cartography", "Draw The Map", 1.6, {
    "right_arm": lambda u: arm('r', 50 + 4 * wave(u, 0, 3), -16 + 8 * wave(u)), "left_arm": lambda u: arm('l', 48, -24, 20), "head": lambda u: tilt(40, 4 * wave(u), 0), "body": lambda u: tilt(26)})
menu_loop("smithing", "Fit Netherite At The Smithing Table", 1.4, {
    "right_arm": lambda u: arm('r', 70 + 40 * max(0, wave(u)), -10), "left_arm": lambda u: arm('l', 56, -16, 40), "body": lambda u: tilt(18), "head": lambda u: tilt(32)},
    events=[snd(0.35, "motionworks:interact.tool_tap", "0.4", "0.8")])
menu_loop("lectern", "Read At The Lectern", 4.0, {
    "right_arm": lambda u: arm('r', 50, -20, 20), "left_arm": lambda u: arm('l', 50, -20, 20), "head": lambda u: tilt(30, 8 * wave(u), 0), "body": lambda u: tilt(14)})
menu_loop("beacon", "Commune With The Beacon", 3.0, {
    "right_arm": lambda u: arm('r', 90 + 10 * wave(u), 10), "left_arm": lambda u: arm('l', 90 + 10 * wave(u, 0.5), 10), "head": lambda u: tilt(-34 + 4 * wave(u)), "body": lambda u: tilt(-6)})
menu_loop("merchant", "Haggle Over Trades", 2.0, {
    "right_arm": lambda u: arm('r', 40 + 30 * max(0, wave(u)), -10, 20 * wave(u, 0.2)), "left_arm": lambda u: arm('l', 20, 10), "head": lambda u: tilt(6, 0, 8 * wave(u, 0.5)),
    "body": lambda u: tilt(6, 4 * wave(u), 0)})
menu_loop("horse", "Adjust Saddlebags", 1.8, {
    "right_arm": lambda u: arm('r', 90 + 10 * wave(u), -20), "left_arm": lambda u: arm('l', 86 + 10 * wave(u, 0.5), -20), "head": lambda u: tilt(-6, 10 * wave(u), 0)})
menu_loop("dispenser", "Load The Dispenser", 1.2, {
    "right_arm": lambda u: arm('r', 70 + 10 * wave(u), -10, 0), "head": lambda u: tilt(16, 0, 10), "body": lambda u: tilt(10)})
menu_loop("hopper", "Sort Items Into The Hopper", 1.4, {
    "right_arm": lambda u: arm('r', 50 + 8 * wave(u), -10, 0), "left_arm": lambda u: arm('l', 40, -10), "head": lambda u: tilt(44)}, crouch=1.4)
menu_loop("inventory", "Check The Pack", 3.0, {
    "right_arm": lambda u: arm('r', 30 + 6 * wave(u), -30, 40), "left_arm": lambda u: arm('l', 34 + 6 * wave(u, 0.4), -30, 40), "head": lambda u: tilt(40, 6 * wave(u), 0),
    "body": lambda u: tilt(10)}, file="player/interact")
menu_loop("chat", "Lost In Thought", 4.0, {
    "right_arm": lambda u: arm('r', 70, -40, 70), "left_arm": lambda u: arm('l', 20, -30, 60), "head": lambda u: tilt(10, 0, 8 + 3 * wave(u))}, file="player/interact")
menu_loop("book_edit", "Write In The Book", 1.4, {
    "right_arm": lambda u: arm('r', 50 + 3 * wave(u, 0, 4), -20 + 6 * wave(u)), "left_arm": lambda u: arm('l', 50, -24, 20), "head": lambda u: tilt(38, 3 * wave(u), 0)},
    file="player/interact", events=[snd(0.7, "motionworks:interact.page", "0.2", "1.3")])

# fidgets during long menu sessions (same pool as the loop)
for menu, label, L, tracks in (
        ("chest", "Dig Deeper In The Chest", 1.6, {"right_arm": [(0, arm('r', 60, -10)), (0.5, arm('r', 30, -10)), (1.0, arm('r', 30, -14)), (1.6, arm('r', 60, -10))],
                                                    "body": [(0, tilt(26)), (0.5, tilt(40)), (1.0, tilt(42)), (1.6, tilt(26))]}),
        ("crafting", "Puzzle Over The Recipe", 2.4, {"right_arm": [(0, arm('r', 62, -16, 20)), (0.5, arm('r', 150, -30, 40)), (1.6, arm('r', 150, -30, 40)), (2.4, arm('r', 62, -16, 20))],
                                                      "head": [(0, tilt(30)), (0.6, tilt(20, 0, 14)), (1.6, tilt(20, 0, 14)), (2.4, tilt(30))]}),
        ("furnace", "Poke The Coals", 1.4, {"right_arm": [(0, arm('r', 50, -10)), (0.3, arm('r', 40, -10)), (0.45, arm('r', 30, -10), "in_quart"), (0.6, arm('r', 40, -10)), (1.4, arm('r', 50, -10))]}),
        ("merchant", "Count The Emeralds", 2.0, {"right_arm": [(0, arm('r', 40, -10)), (0.4, arm('r', 60, -20, 20)), (1.6, arm('r', 60, -20, 20)), (2.0, arm('r', 40, -10))],
                                                 "left_arm": [(0, arm('l', 20, 10)), (0.4, arm('l', 56, -20, 20)), (0.7, arm('l', 60, -16, 20)), (1.0, arm('l', 56, -20, 20)), (1.3, arm('l', 60, -16, 20)), (2.0, arm('l', 20, 10))],
                                                 "head": [(0, Z), (0.4, tilt(34)), (1.6, tilt(34)), (2.0, Z)]})):
    c = Clip("player.interact.work_fidget_" + menu, label, CAT, T, length=L, loop="once", layer="base", priority=120,
             trigger=state(ALIVE + " && q.menu == '%s' && q.ground_speed < 0.02" % menu, group="menu_" + menu, weight=1), blend_in=0.2, file=FW)
    for bone, seq in tracks.items():
        c.keys(bone, "rotation", seq, lerp="smooth")

# menu closing transitions
for menu, label, tracks in (
        ("chest", "Shut The Chest Lid", {"right_arm": [(0, arm('r', 90, -10)), (0.2, arm('r', 100, -10)), (0.35, arm('r', 40, -10), "in_quart"), (0.6, Z)]}),
        ("crafting", "Dust Off Hands", {"right_arm": [(0, Z), (0.2, arm('r', 40, -24, 30)), (0.3, arm('r', 44, -10, 30)), (0.4, arm('r', 40, -24, 30)), (0.6, Z)],
                                        "left_arm": [(0, Z), (0.2, arm('l', 40, -24, 30)), (0.3, arm('l', 44, -10, 30)), (0.4, arm('l', 40, -24, 30)), (0.6, Z)]}),
        ("furnace", "Close The Furnace Door", {"right_arm": [(0, arm('r', 50, -10)), (0.25, arm('r', 60, 30)), (0.4, arm('r', 56, -20), "in_quart"), (0.6, Z)]}),
        ("anvil", "Set Down The Hammer", {"right_arm": [(0, arm('r', 120, 0)), (0.3, arm('r', 40, 0)), (0.6, Z)], "body": [(0, tilt(16)), (0.3, tilt(-6)), (0.6, Z)]}),
        ("enchanting", "Close The Grimoire", {"right_arm": [(0, arm('r', 74, 22, -20)), (0.25, arm('r', 70, -10)), (0.6, Z)], "left_arm": [(0, arm('l', 74, 22, -20)), (0.25, arm('l', 70, -10)), (0.6, Z)]}),
        ("brewing", "Cork The Bottle", {"right_arm": [(0, arm('r', 70, -14, 40)), (0.25, arm('r', 74, -20, 40)), (0.35, arm('r', 74, -20, 90), "out_back"), (0.6, Z)]}),
        ("merchant", "Nod Farewell To The Merchant", {"head": [(0, Z), (0.2, tilt(18)), (0.4, tilt(-4)), (0.6, Z)], "right_arm": [(0, Z), (0.25, arm('r', 30, 10)), (0.6, Z)]}),
        ("other", "Step Back From Station", {"mw_root:pos": [(0, Z), (0.3, move(0, 0, -1.2)), (0.6, Z)], "body": [(0, tilt(10)), (0.6, Z)]})):
    cond = "q.event_arg == '%s'" % menu if menu != "other" else "q.event_arg != 'chest' && q.event_arg != 'crafting' && q.event_arg != 'furnace' && q.event_arg != 'anvil'"
    gesture("work_close_" + menu, label, event("menu_close", ALIVE + " && " + cond), 0.6, tracks, pri=125, file=FW)
gesture("inventory_close", "Pat Down Pockets", event("menu_close", ALIVE + " && q.event_arg == 'inventory'"), 0.8, {
    "right_arm": [(0, Z), (0.2, arm('r', 10, -10, 20)), (0.35, arm('r', 6, -6, 20)), (0.5, arm('r', 10, -10, 20)), (0.8, Z)],
    "left_arm": [(0, Z), (0.25, arm('l', 10, -10, 20)), (0.4, arm('l', 6, -6, 20)), (0.8, Z)]}, pri=126)
gesture("typing_done", "Look Up From Thought", event("menu_close", ALIVE + " && q.event_arg == 'chat'"), 0.7, {
    "head": [(0, tilt(10, 0, 8)), (0.3, tilt(-6)), (0.7, Z)], "right_arm": [(0, arm('r', 70, -40, 70)), (0.4, Z)]}, pri=126)

# ------------------------------------------------------------------ equipment changes (synced equipment slots)
for slot, label_on, on, label_off, off in (
        ("head", "Pull On Helmet", {"right_arm": [(0, Z), (0.3, arm('r', 170, -20)), (0.55, arm('r', 160, -40, 20)), (0.8, Z)], "left_arm": [(0, Z), (0.3, arm('l', 170, -20)), (0.55, arm('l', 160, -40, 20)), (0.8, Z)],
                                           "head": [(0, Z), (0.45, tilt(10)), (0.8, Z)]},
         "Lift Off Helmet", {"right_arm": [(0, Z), (0.3, arm('r', 160, -40, 20)), (0.55, arm('r', 176, -10)), (0.8, Z)], "left_arm": [(0, Z), (0.3, arm('l', 160, -40, 20)), (0.55, arm('l', 176, -10)), (0.8, Z)],
                             "head": [(0, Z), (0.3, tilt(-10)), (0.8, Z)]}),
        ("chest", "Shrug Into Chestplate", {"right_arm": [(0, Z), (0.3, arm('r', -30, 40)), (0.5, arm('r', 20, 10)), (0.9, Z)], "left_arm": [(0, Z), (0.3, arm('l', -30, 40)), (0.5, arm('l', 20, 10)), (0.9, Z)],
                                            "body": [(0, Z), (0.35, tilt(-8, 0, 6)), (0.55, tilt(4, 0, -6)), (0.9, Z)], "mw_root:pos": [(0, Z), (0.45, move(0, 0.6)), (0.9, Z)]},
         "Unbuckle Chestplate", {"right_arm": [(0, Z), (0.3, arm('r', 30, -40, 30)), (0.6, arm('r', 30, -20, 30)), (0.9, Z)], "left_arm": [(0, Z), (0.35, arm('l', 30, -40, 30)), (0.6, arm('l', 30, -20, 30)), (0.9, Z)],
                                 "head": [(0, Z), (0.3, tilt(30)), (0.9, Z)]}),
        ("legs", "Step Into Leggings", {"right_leg": [(0, Z), (0.25, leg('r', 50)), (0.45, Z)], "left_leg": [(0, Z), (0.45, Z), (0.65, leg('l', 50)), (0.9, Z)],
                                        "right_arm": [(0, Z), (0.3, arm('r', 30, -10)), (0.9, Z)], "left_arm": [(0, Z), (0.3, arm('l', 30, -10)), (0.9, Z)], "body": [(0, Z), (0.3, tilt(20)), (0.9, Z)]},
         "Kick Off Leggings", {"right_leg": [(0, Z), (0.3, leg('r', -30)), (0.45, leg('r', 30), "out_quad"), (0.8, Z)], "body": [(0, Z), (0.3, tilt(-4)), (0.8, Z)]}),
        ("feet", "Lace Up Boots", {"right_leg": [(0, Z), (0.3, leg('r', 60)), (0.7, leg('r', 60)), (0.9, Z)], "right_arm": [(0, Z), (0.35, arm('r', 30, -10)), (0.7, arm('r', 34, -10)), (0.9, Z)],
                                   "body": [(0, Z), (0.35, tilt(34)), (0.9, Z)], "head": [(0, Z), (0.35, tilt(40)), (0.9, Z)]},
         "Tug Off Boots", {"left_leg": [(0, Z), (0.3, leg('l', 50, 10)), (0.6, leg('l', 40, 10)), (0.9, Z)], "left_arm": [(0, Z), (0.3, arm('l', 20, -10)), (0.6, arm('l', 30, -10)), (0.9, Z)],
                           "mw_root": [(0, Z), (0.35, tilt(0, 0, 8)), (0.9, Z)]})):
    gesture("armor_on_" + slot, label_on, event("armor_on:" + slot, ALIVE), 0.9, on, pri=150, file="player/equipment", events=[foley(0.4, "armor", "0.8")])
    gesture("armor_off_" + slot, label_off, event("armor_off:" + slot, ALIVE), 0.9, off, pri=150, file="player/equipment", events=[foley(0.4, "armor", "0.6")])

# ------------------------------------------------------------------ small world details
gesture("door_elbow_open", "Elbow A Door Open (Hands Full)", event("interact:door_open", ALIVE + " && (q.main_hand == 'block' || q.main_hand == 'book' || q.main_hand == 'map')"), 0.7, {
    "right_arm": [(0, arm('r', 40, -6, 20)), (0.25, arm('r', 30, 40, 70)), (0.45, arm('r', 34, 50, 70)), (0.7, arm('r', 40, -6, 20))],
    "body": [(0, Z), (0.25, tilt(4, 20)), (0.7, Z)]}, pri=164)
gesture("door_slam_shut", "Slam Door On Danger", event("interact:door_close", ALIVE + " && q.near_hostile"), 0.5, {
    "right_arm": [(0, Z), (0.1, arm('r', 90, 40, -20)), (0.22, arm('r', 60, -30, 30), "in_quart"), (0.5, Z)],
    "left_arm": [(0, Z), (0.12, arm('l', 80, 30)), (0.25, arm('l', 70, -10)), (0.5, Z)], "body": [(0, Z), (0.22, tilt(10, -20)), (0.5, Z)]}, pri=165,
    events=[(0.22, "shake", {"amount": "0.05", "radius": "4"})])
gesture("chest_grab_hurried", "Grab From Chest In A Hurry", event("interact:chest", ALIVE + " && q.near_hostile"), 0.5, {
    "right_arm": [(0, Z), (0.12, arm('r', 110, -10)), (0.3, arm('r', 50, -10)), (0.5, Z)], "head": [(0, Z), (0.1, tilt(20)), (0.25, tilt(-4, 40)), (0.5, Z)]}, pri=164)
gesture("chest_open_high", "Reach Up To A High Chest", event("interact:chest", ALIVE + HIGH), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 150, -10)), (0.6, arm('r', 176, -10)), (0.9, Z)], "left_arm": [(0, Z), (0.35, arm('l', 150, -10)), (0.6, arm('l', 172, -10)), (0.9, Z)],
    "head": [(0, Z), (0.3, tilt(-40)), (0.9, Z)], "mw_root:pos": [(0, Z), (0.45, move(0, 0.8)), (0.9, Z)]}, pri=163)
gesture("barrel_open_high", "Pry Open A Stacked Barrel", event("interact:barrel", ALIVE + HIGH), 0.9, {
    "right_arm": [(0, Z), (0.3, arm('r', 150, -20, 40)), (0.55, arm('r', 170, 0, -20), "out_back"), (0.9, Z)], "head": [(0, Z), (0.3, tilt(-36)), (0.9, Z)]}, pri=163)
gesture("trapdoor_peek", "Peer Down Through Hatch", event("interact:trapdoor_open", ALIVE + LOW + " && q.is_sneaking"), 1.8, {
    "mw_root:pos": CROUCH(5.0), "right_leg": [(0, Z), (0.4, leg('r', 85)), (1.4, leg('r', 85)), (1.8, Z)], "left_leg": [(0, Z), (0.4, leg('l', 85)), (1.4, leg('l', 85)), (1.8, Z)],
    "head": [(0, Z), (0.5, tilt(60)), (1.3, tilt(62, 10)), (1.8, Z)], "body": [(0, Z), (0.5, tilt(40)), (1.8, Z)]}, pri=164)
gesture("hang_decoration", "Hang A Painting", I("hang"), 1.1, {
    "right_arm": [(0, Z), (0.35, arm('r', 140, -10)), (0.75, arm('r', 142, -10)), (1.1, Z)], "left_arm": [(0, Z), (0.35, arm('l', 140, -10)), (0.75, arm('l', 142, -10)), (1.1, Z)],
    "head": [(0, Z), (0.35, tilt(-20)), (0.9, tilt(-6, 0, 8)), (1.1, Z)], "mw_root:pos": [(0, Z), (0.45, move(0, 0, -1.0)), (1.1, Z)]})
gesture("fill_bottle", "Fill A Glass Bottle", event("fill_bottle", ALIVE), 0.9, {
    "mw_root:pos": CROUCH(2.6), "right_arm": [(0, Z), (0.3, arm('r', 30, -6, 90)), (0.55, arm('r', 20, -6, 90)), (0.75, arm('r', 60, -10)), (0.9, Z)], "head": [(0, Z), (0.3, tilt(46)), (0.9, Z)]},
    events=[snd(0.5, "motionworks:water.bubbles", "0.3")])
gesture("bookshelf_return", "Slide A Book Back", event("interact:bookshelf", ALIVE + " && q.main_hand == 'book'"), 0.8, {
    "right_arm": [(0, arm('r', 46, -18, 20)), (0.35, arm('r', 90, -10)), (0.5, arm('r', 96, -10), "in_quart"), (0.8, Z)], "head": [(0, Z), (0.35, tilt(0, 0, 8)), (0.8, Z)]}, pri=161)
gesture("warm_hands", "Warm Hands By The Fire", I("campfire"), 3.0, {
    "mw_root:pos": CROUCH(3.6), "right_leg": [(0, Z), (0.5, leg('r', 80)), (2.5, leg('r', 80)), (3.0, Z)], "left_leg": [(0, Z), (0.5, leg('l', 30)), (2.5, leg('l', 30)), (3.0, Z)],
    "right_arm": [(0, Z), (0.6, arm('r', 60, -20, -60)), (1.5, arm('r', 62, -14, -50)), (2.5, arm('r', 60, -20, -60)), (3.0, Z)],
    "left_arm": [(0, Z), (0.6, arm('l', 60, -20, -60)), (1.5, arm('l', 62, -26, -70)), (2.5, arm('l', 60, -20, -60)), (3.0, Z)], "head": [(0, Z), (0.6, tilt(20)), (3.0, Z)]})
gesture("douse_campfire", "Douse The Campfire", I("douse"), 1.0, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -6)), (0.45, arm('r', 30, -6), "in_quart"), (0.65, arm('r', 50, -6)), (1.0, Z)], "left_arm": [(0, Z), (0.3, arm('l', 56, -6)), (0.45, arm('l', 26, -6)), (1.0, Z)],
    "body": [(0, Z), (0.45, tilt(30)), (1.0, Z)]}, events=[(0.45, "particle", {"particle": "smoke_wisp", "count": "4", "at": "front", "spread": "0.4"})])
gesture("smell_flower", "Stop To Smell A Flower", I("smell_flower"), 2.4, {
    "mw_root:pos": CROUCH(3.0), "body": [(0, Z), (0.6, tilt(36)), (1.8, tilt(38)), (2.4, Z)], "head": [(0, Z), (0.6, tilt(40)), (1.2, tilt(30, 0, 8)), (1.8, tilt(-10)), (2.4, Z)],
    "right_arm": [(0, Z), (0.6, arm('r', 30, -10)), (1.8, arm('r', 30, -10)), (2.4, Z)]}, events=[(1.2, "particle", {"particle": "pollen", "count": "3", "at": "mouth", "spread": "0.2"})])
gesture("chime_amethyst", "Tap The Amethyst", I("amethyst"), 1.2, {
    "right_arm": [(0, Z), (0.25, arm('r', 60, -10, 30)), (0.35, arm('r', 56, -10, 30), "in_quart"), (0.6, arm('r', 60, -10, 30)), (1.2, Z)],
    "head": [(0, Z), (0.35, tilt(30)), (0.7, tilt(20, 0, 14)), (1.2, Z)]}, events=[snd(0.35, "minecraft:block.amethyst_block.chime", "0.6")])

"""Player combat part 3: weapon switching, inspection, stances and combat movement styles."""
from core import Clip, state, event, arm, leg, tilt, move, biped, strike, shake, wave, cwave
from player_combat import CAT, T, CYCLE, ALIVE, Z, W, melee, LIGHT, MEDIUM, HEAVY
from player_combat_more import act, FH, FS

UPPER = ["right_arm", "left_arm", "body", "head"]


def keyed(cid, name, trig, L, tracks, pri=180, mask=UPPER, file=FH, layer="action", events=()):
    """tracks: {bone: [(t, value[, ease]), ...]} with values already converted."""
    c = act(cid, name, trig, L, pri=pri, mask=mask, file=file, layer=layer)
    for bone, seq in tracks.items():
        ch = "position" if bone.endswith(":pos") else "rotation"
        c.keys(bone.split(":")[0], ch, seq, lerp="smooth")
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


SW_OUT = " && q.prev_main_hand == 'sword' && q.main_hand != 'sword'"

# --------------------------------------------------------------------------------- weapon switching
keyed("draw_sword", "Draw Sword From Back", event("item_switch", ALIVE + " && q.main_hand == 'sword'"), 0.6, {
    "right_arm": [(0, Z), (0.18, arm('r', 170, -30, 30), "out_cubic"), (0.32, arm('r', 160, 20, -10)), (0.6, arm('r', -6, 10, -20), "in_out_sine")],
    "head": [(0, Z), (0.2, tilt(0, 20)), (0.6, Z)], "body": [(0, Z), (0.2, tilt(-4, 12)), (0.6, Z)]},
    events=[(0.3, "sound", {"sound": "motionworks:weapon.draw_blade", "volume": "0.6"})])
keyed("draw_axe", "Heft Axe Off Shoulder", event("item_switch", ALIVE + " && q.main_hand == 'axe'"), 0.7, {
    "right_arm": [(0, Z), (0.22, arm('r', 160, -40, 40), "out_cubic"), (0.4, arm('r', 120, 10, 20)), (0.7, arm('r', 150, -10, 40))],
    "body": [(0, Z), (0.3, tilt(6, -10)), (0.7, Z)]}, events=[(0.35, "sound", {"sound": "motionworks:weapon.draw_haft", "volume": "0.6"})])
keyed("draw_trident", "Swing Trident Around", event("item_switch", ALIVE + " && q.main_hand == 'trident'"), 0.8, {
    "right_arm": [(0, Z), (0.25, arm('r', 170, 30, 0)), (0.5, arm('r', 100, 60, -60)), (0.8, arm('r', 36, 8, -70))],
    "body": [(0, Z), (0.4, tilt(0, 20)), (0.8, Z)]}, events=[(0.4, "whoosh", {"weight": "medium"})])
keyed("draw_bow", "Unsling Bow", event("item_switch", ALIVE + " && q.main_hand == 'bow'"), 0.65, {
    "right_arm": [(0, Z), (0.2, arm('r', 150, -40, 20)), (0.45, arm('r', 60, 20, -20)), (0.65, arm('r', 8, 14, -40))],
    "left_arm": [(0, Z), (0.4, arm('l', 40, -10)), (0.65, Z)], "head": [(0, Z), (0.2, tilt(0, 24)), (0.65, Z)]},
    events=[(0.3, "foley", {"kind": "leather", "volume": "0.6"})])
keyed("draw_crossbow", "Bring Crossbow To Chest", event("item_switch", ALIVE + " && q.main_hand == 'crossbow'"), 0.7, {
    "right_arm": [(0, Z), (0.25, arm('r', 150, -30, 30)), (0.5, arm('r', 60, -20, 40)), (0.7, arm('r', 40, -30, 50))],
    "left_arm": [(0, Z), (0.45, arm('l', 50, -30, 40)), (0.7, arm('l', 36, -24, 40))], "body": [(0, Z), (0.3, tilt(-4, 10)), (0.7, Z)]},
    events=[(0.35, "foley", {"kind": "leather", "volume": "0.6"})])
keyed("draw_pickaxe", "Pull Pickaxe From Hip", event("item_switch", ALIVE + " && q.main_hand == 'pickaxe'"), 0.5, {
    "right_arm": [(0, Z), (0.15, arm('r', -20, 20, 40)), (0.32, arm('r', 60, 10, 0)), (0.5, arm('r', 14, 6, -10))],
    "head": [(0, Z), (0.15, tilt(20, 10)), (0.5, Z)]})
keyed("draw_shovel", "Swing Shovel From Back", event("item_switch", ALIVE + " && q.main_hand == 'shovel'"), 0.6, {
    "right_arm": [(0, Z), (0.2, arm('r', 160, -20, 40)), (0.4, arm('r', 40, 40, 40)), (0.6, arm('r', -38, 8, 60))]})
keyed("draw_hoe", "Twirl Hoe To Hand", event("item_switch", ALIVE + " && q.main_hand == 'hoe'"), 0.6, {
    "right_arm": [(0, Z), (0.2, arm('r', 40, 10, 180)), (0.4, arm('r', 30, 6, 330)), (0.6, arm('r', 24, 4, 390))]})
keyed("ready_food", "Bring Food Close", event("item_switch", ALIVE + " && q.main_hand == 'food'"), 0.5, {
    "right_arm": [(0, Z), (0.25, arm('r', 70, -20, 20)), (0.5, arm('r', 34, 4, -10))], "head": [(0, Z), (0.25, tilt(20)), (0.5, Z)]})
keyed("ready_block", "Toss And Catch Block", event("item_switch", ALIVE + " && q.main_hand == 'block'"), 0.7, {
    "right_arm": [(0, Z), (0.15, arm('r', 50, -6)), (0.25, arm('r', 70, -6), "out_quad"), (0.5, arm('r', 46, -6), "in_quad"), (0.7, arm('r', 40, -6, 20))],
    "head": [(0, Z), (0.3, tilt(-20)), (0.55, tilt(10)), (0.7, Z)]})
keyed("ready_torch", "Raise Torch Flourish", event("item_switch", ALIVE + " && q.main_hand == 'torch'"), 0.55, {
    "right_arm": [(0, Z), (0.25, arm('r', 130, 20, -20), "out_back"), (0.55, arm('r', 98, 14, -10))], "head": [(0, Z), (0.25, tilt(-12)), (0.55, Z)]})
keyed("sheathe_sword", "Sheathe Sword", event("item_switch", ALIVE + SW_OUT), 0.7, {
    "right_arm": [(0, arm('r', -6, 10, -20)), (0.25, arm('r', 100, 30, -10)), (0.45, arm('r', 170, -20, 30)), (0.7, Z)],
    "head": [(0, Z), (0.4, tilt(0, 18)), (0.7, Z)]}, pri=181,
    events=[(0.45, "sound", {"sound": "motionworks:weapon.sheathe_blade", "volume": "0.6"})])
keyed("sheathe_axe", "Shoulder The Axe", event("item_switch", ALIVE + " && q.prev_main_hand == 'axe' && q.main_hand != 'axe'"), 0.6, {
    "right_arm": [(0, arm('r', 150, -10, 40)), (0.3, arm('r', 175, -30, 30)), (0.6, Z)], "body": [(0, Z), (0.3, tilt(-4, -8)), (0.6, Z)]}, pri=181)
keyed("sling_bow", "Sling Bow Over Shoulder", event("item_switch", ALIVE + " && q.prev_main_hand == 'bow' && q.main_hand != 'bow'"), 0.6, {
    "right_arm": [(0, arm('r', 8, 14, -40)), (0.3, arm('r', 160, -40, 20)), (0.6, Z)], "head": [(0, Z), (0.3, tilt(0, 22)), (0.6, Z)]}, pri=181,
    events=[(0.3, "foley", {"kind": "leather", "volume": "0.5"})])
keyed("sling_crossbow", "Stow Crossbow", event("item_switch", ALIVE + " && q.prev_main_hand == 'crossbow' && q.main_hand != 'crossbow'"), 0.6, {
    "right_arm": [(0, arm('r', 40, -30, 50)), (0.3, arm('r', 150, -30, 30)), (0.6, Z)], "left_arm": [(0, arm('l', 36, -24, 40)), (0.25, Z)]}, pri=181)
keyed("generic_swap", "Quick Item Swap", event("item_switch", ALIVE), 0.35, {
    "right_arm": [(0, Z), (0.15, arm('r', -10, 10, 20)), (0.35, Z)], "head": [(0, Z), (0.15, tilt(14)), (0.35, Z)]}, pri=170, mask=["right_arm", "head"])
keyed("swap_hands", "Swap Hands", event("offhand_switch", ALIVE), 0.5, {
    "right_arm": [(0, Z), (0.22, arm('r', 50, -40, 20)), (0.5, Z)], "left_arm": [(0, Z), (0.22, arm('l', 50, -40, 20)), (0.5, Z)],
    "head": [(0, Z), (0.22, tilt(26)), (0.5, Z)]}, pri=182)

# --------------------------------------------------------------------------------- inspection
def inspect(cid, name, when, L, tracks, events=(), pri=175):
    return keyed(cid, name, event("inspect", ALIVE + " && " + when), L, tracks, pri=pri, events=events)


inspect("inspect_sword", "Inspect Blade Edge", "q.main_hand == 'sword' && q.trait_energy <= 0.6", 2.6, {
    "right_arm": [(0, Z), (0.5, arm('r', 80, -30, 80)), (1.3, arm('r', 82, -30, -60)), (2.0, arm('r', 90, -10, 0)), (2.6, Z)],
    "head": [(0, Z), (0.5, tilt(16, -10)), (1.3, tilt(14, -16)), (2.0, tilt(-6, -2)), (2.6, Z)], "body": [(0, Z), (1.3, tilt(0, -10)), (2.6, Z)]})
inspect("inspect_sword_flip", "Sword Toss Flourish", "q.main_hand == 'sword' && q.trait_energy > 0.6", 1.8, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, 10)), (0.45, arm('r', 120, 10), "out_quad"), (0.9, arm('r', 120, 10, 360)), (1.2, arm('r', 70, 10, 360)), (1.8, arm('r', 0, 0, 360))],
    "head": [(0, Z), (0.5, tilt(-30)), (1.0, tilt(-20)), (1.8, Z)]}, events=[(0.45, "whoosh", {"weight": "light"}), (1.2, "sound", {"sound": "motionworks:weapon.draw_blade", "volume": "0.4", "pitch": "1.3"})])
inspect("inspect_axe", "Thumb The Axe Edge", "q.main_hand == 'axe' && q.trait_energy <= 0.6", 2.4, {
    "right_arm": [(0, Z), (0.5, arm('r', 70, -20, 40)), (1.8, arm('r', 72, -20, 40)), (2.4, Z)],
    "left_arm": [(0, Z), (0.6, arm('l', 60, -30, 30)), (0.9, arm('l', 64, -26, 30)), (1.2, arm('l', 60, -30, 30)), (1.5, arm('l', 64, -26, 30)), (2.4, Z)],
    "head": [(0, Z), (0.5, tilt(28)), (1.8, tilt(30)), (2.4, Z)]})
inspect("inspect_axe_spin", "Axe Haft Spin", "q.main_hand == 'axe' && q.trait_energy > 0.6", 1.6, {
    "right_arm": [(0, Z), (0.3, arm('r', 30, 30, 0)), (0.6, arm('r', 30, 30, 360)), (0.9, arm('r', 30, 30, 720)), (1.6, arm('r', 150, -10, 760))]},
    events=[(0.5, "whoosh", {"weight": "medium"}), (0.8, "whoosh", {"weight": "medium"})])
inspect("inspect_trident", "Admire Trident Tines", "q.main_hand == 'trident'", 2.4, {
    "right_arm": [(0, Z), (0.6, arm('r', 150, 10, -20)), (1.8, arm('r', 152, 12, 20)), (2.4, Z)], "head": [(0, Z), (0.6, tilt(-40)), (1.8, tilt(-42, 8)), (2.4, Z)]})
inspect("inspect_bow", "Pluck Bowstring", "q.main_hand == 'bow'", 2.0, {
    "left_arm": [(0, Z), (0.4, arm('l', 80, -20)), (1.6, arm('l', 82, -20)), (2.0, Z)],
    "right_arm": [(0, Z), (0.6, arm('r', 70, -30, 20)), (0.8, arm('r', 74, -20, 20)), (1.0, arm('r', 70, -30, 20)), (2.0, Z)],
    "head": [(0, Z), (0.5, tilt(20, -10)), (1.6, tilt(20, -10)), (2.0, Z)]}, events=[(0.8, "sound", {"sound": "motionworks:weapon.bow_creak", "volume": "0.4", "pitch": "1.6"})])
inspect("inspect_crossbow", "Sight Along Crossbow", "q.main_hand == 'crossbow'", 2.2, {
    "right_arm": [(0, Z), (0.5, arm('r', 90, -10)), (1.7, arm('r', 90, -12)), (2.2, Z)], "left_arm": [(0, Z), (0.5, arm('l', 92, -34)), (1.7, arm('l', 92, -34)), (2.2, Z)],
    "head": [(0, Z), (0.5, tilt(-4, 14, 10)), (1.7, tilt(-4, 14, 10)), (2.2, Z)]})
inspect("inspect_pickaxe", "Check Pickaxe Tip", "q.main_hand == 'pickaxe'", 2.0, {
    "right_arm": [(0, Z), (0.5, arm('r', 90, -30, 90)), (1.5, arm('r', 92, -28, 90)), (2.0, Z)], "head": [(0, Z), (0.5, tilt(10, -14)), (1.5, tilt(10, -14)), (2.0, Z)]})
inspect("inspect_tool", "Lean On Tool Handle", "(q.main_hand == 'shovel' || q.main_hand == 'hoe')", 2.6, {
    "right_arm": [(0, Z), (0.6, arm('r', 30, -10, 30)), (2.0, arm('r', 30, -10, 30)), (2.6, Z)], "left_arm": [(0, Z), (0.6, arm('l', 34, -20, 30)), (2.0, arm('l', 34, -20, 30)), (2.6, Z)],
    "body": [(0, Z), (0.6, tilt(10, 0, 6)), (2.0, tilt(10, 0, 6)), (2.6, Z)]})
inspect("inspect_knuckles", "Crack Knuckles", "q.main_hand == 'empty'", 1.6, {
    "right_arm": [(0, Z), (0.3, arm('r', 60, -30, 20)), (1.2, arm('r', 62, -30, 20)), (1.6, Z)], "left_arm": [(0, Z), (0.3, arm('l', 60, -30, 20)), (0.6, arm('l', 56, -36, 30)), (1.2, arm('l', 62, -30, 20)), (1.6, Z)],
    "head": [(0, Z), (0.4, tilt(18)), (1.2, tilt(18)), (1.6, Z)]}, events=[(0.6, "sound", {"sound": "motionworks:emote.snap", "volume": "0.4", "pitch": "0.7"})])
inspect("inspect_totem", "Hold Up Totem", "q.main_hand == 'totem'", 2.4, {
    "right_arm": [(0, Z), (0.6, arm('r', 150, 0)), (1.8, arm('r', 152, 4)), (2.4, Z)], "head": [(0, Z), (0.6, tilt(-36)), (1.8, tilt(-38)), (2.4, Z)]},
    events=[(0.6, "particle", {"particle": "magic_glint", "count": "6", "at": "head", "spread": "0.6"})])
inspect("inspect_block", "Turn Block Over", "q.main_hand == 'block'", 2.0, {
    "right_arm": [(0, Z), (0.4, arm('r', 60, -20, 0)), (1.0, arm('r', 62, -20, 120)), (1.6, arm('r', 60, -20, 0)), (2.0, Z)],
    "left_arm": [(0, Z), (0.4, arm('l', 56, -20)), (1.6, arm('l', 56, -20)), (2.0, Z)], "head": [(0, Z), (0.4, tilt(24)), (1.6, tilt(24)), (2.0, Z)]})

# --------------------------------------------------------------------------------- combat stances and movement styles
STYLES = {
    # weapon: (main-hand guard, off-hand guard, stance character)
    "sword": ((40, 14, -30), (20, 20, 0), dict(bounce=0.4, sway=2.0, lean=6)),
    "axe": ((70, 20, 20), (40, -10, 30), dict(bounce=0.6, sway=3.5, lean=10)),
    "trident": ((60, 10, -70), (70, -30, 30), dict(bounce=0.2, sway=1.0, lean=4)),
    "empty": ((70, -10, 40), (70, -20, 40), dict(bounce=0.9, sway=1.5, lean=8)),
    "bow": ((30, 10, 0), (40, -10, -20), dict(bounce=0.3, sway=1.5, lean=3)),
    "crossbow": ((70, -10, 0), (70, -30, 0), dict(bounce=0.2, sway=1.0, lean=2)),
}
NAMES = {"sword": "Sword", "axe": "Axe", "trident": "Spear", "empty": "Boxing", "bow": "Archer", "crossbow": "Crossbowman"}
COMBAT = ALIVE + " && q.in_combat && q.is_on_ground && !q.is_sneaking && !q.is_blocking && !q.is_using_item"
SIDE = "(q.strafe_speed > 0 ? 1 : -1)"
for w, (rg, lg, ch) in STYLES.items():
    base = COMBAT + " && q.main_hand == '%s'" % w + (" && q.off_hand != 'shield'" if w in ("sword", "axe") else "")
    nm = NAMES[w]
    c = Clip("player.combat.stance_" + w, nm + " Guard Stance", CAT, T, length=1.4, loop="loop", layer="base", priority=265,
             trigger=state(base + " && q.ground_speed < 0.02", group="stance_" + w, weight=5, min_time=1.4), blend_in=0.3, file=FS)
    c.cycle("right_arm", "rotation", lambda u, g=rg: arm('r', g[0] + 3 * wave(u), g[1], g[2]))
    c.cycle("left_arm", "rotation", lambda u, g=lg: arm('l', g[0] + 3 * wave(u, 0.3), g[1], g[2]))
    c.cycle("right_leg", "rotation", lambda u: leg('r', -10, 8))
    c.cycle("left_leg", "rotation", lambda u: leg('l', 14, 8, 10))
    c.cycle("mw_root", "position", lambda u, b=ch["bounce"]: move(0, -1.0 - b * abs(wave(u))))
    c.cycle("mw_root", "rotation", lambda u, s=ch["sway"]: tilt(0, -14, s * wave(u, 0.2)))
    c.cycle("body", "rotation", lambda u, l=ch["lean"]: tilt(l, 10, 0))
    c.cycle("head", "rotation", lambda u, l=ch["lean"]: tilt(-l * 0.6, 4 + (8 * wave(u, 0, 0.5) if w == "bow" else 0), 0))
    for cid, label, cond, stride, tw, sw, lean_add, extra in (
            ("guard_walk_" + w, nm + " Guarded Advance", " && q.ground_speed >= 0.02 && q.forward_speed >= 0", 18, 4, 2.0, 4, {}),
            ("guard_strafe_" + w, nm + " Circling Strafe", " && math.abs(q.strafe_speed) > 0.03 && math.abs(q.forward_speed) < 0.04", 12, 10, -4.0, 2, {"legs_out": 10, "side_sign": SIDE}),
            ("guard_backpedal_" + w, nm + " Guarded Retreat", " && q.forward_speed < -0.02", -9, 1, 0.8, -14, {"arm_out": 6, "legs_out": 12, "knee_lift": -10})):
        p = 266 if "walk" in cid else (268 if "strafe" in cid else 267)
        L = 0.9
        c = Clip("player.combat." + cid, label, CAT, T, length=L, loop="loop", layer="base", priority=p, trigger=state(base + cond, exit_delay=0.12),
                 blend_in=0.25, time="q.limb_swing * %g" % round(L / (CYCLE * 0.85), 5), weight="math.clamp(q.limb_swing_amount * 2.2, 0, 1)", file=FS)
        back = "backpedal" in cid
        ra = (rg[0] + 24, rg[1] - 8, rg[2]) if back else rg
        la = (lg[0] + 28, lg[1] - 10, lg[2]) if back else lg
        biped(c, stride=stride, bob=0.2 if back else 0.5 + ch["bounce"], twist=tw, sway=sw, lean=ch["lean"] + lean_add, right_arm=ra, left_arm=la,
              head_bob=0.3 if back else 0.8, root_pitch=-6 if back else 0, **extra)

FIDGETS = {
    "sword": ("Blade Flick", {"right_arm": [(0, arm('r', 40, 14, -30)), (0.3, arm('r', 60, 30, -60)), (0.45, arm('r', 30, -10, 10), "out_expo"), (1.2, arm('r', 40, 14, -30))]}),
    "axe": ("Heft And Roll Shoulders", {"right_arm": [(0, arm('r', 70, 20, 20)), (0.5, arm('r', 110, 20, 20)), (0.8, arm('r', 66, 20, 20)), (1.4, arm('r', 70, 20, 20))],
                                      "body": [(0, tilt(10, 10)), (0.5, tilt(4, 18)), (1.4, tilt(10, 10))]}),
    "trident": ("Haft Twirl", {"right_arm": [(0, arm('r', 60, 10, -70)), (0.5, arm('r', 60, 10, 110)), (1.0, arm('r', 60, 10, 290)), (1.4, arm('r', 60, 10, 290))]}),
    "empty": ("Shadow Jab", {"right_arm": [(0, arm('r', 70, -10, 40)), (0.15, arm('r', 92, -6, 0), "out_expo"), (0.35, arm('r', 70, -10, 40)), (0.5, arm('r', 92, -6, 0), "out_expo"), (0.8, arm('r', 70, -10, 40))],
                             "head": [(0, Z), (0.15, tilt(4, -6)), (0.8, Z)]}),
    "bow": ("Count Arrows", {"right_arm": [(0, arm('r', 30, 10, 0)), (0.4, arm('r', 170, -30, 20)), (1.0, arm('r', 168, -28, 20)), (1.4, arm('r', 30, 10, 0))],
                             "head": [(0, Z), (0.4, tilt(0, 30)), (1.0, tilt(0, 30)), (1.4, Z)]}),
    "crossbow": ("Check Sights", {"head": [(0, Z), (0.4, tilt(-4, 10, 12)), (1.2, tilt(-4, 10, 12)), (1.6, Z)], "right_arm": [(0, arm('r', 70, -10, 0)), (0.4, arm('r', 90, -10)), (1.2, arm('r', 90, -10)), (1.6, arm('r', 70, -10, 0))]}),
}
for w, (label, tracks) in FIDGETS.items():
    base = COMBAT + " && q.main_hand == '%s'" % w + (" && q.off_hand != 'shield'" if w in ("sword", "axe") else "") + " && q.ground_speed < 0.02"
    L = max(t for seq in tracks.values() for t, *_ in seq)
    c = Clip("player.combat.stance_fidget_" + w, NAMES[w] + " " + label, CAT, T, length=L, loop="once", layer="base", priority=265,
             trigger=state(base, group="stance_" + w, weight=1), blend_in=0.2, file=FS)
    for bone, seq in tracks.items():
        c.keys(bone, "rotation", seq, lerp="smooth")

# shield style (any main weapon with a shield in the off hand)
SHC = COMBAT + " && q.off_hand == 'shield'"
c = Clip("player.combat.stance_shield", "Shield Guard Stance", CAT, T, length=1.6, loop="loop", layer="base", priority=269,
         trigger=state(SHC + " && q.ground_speed < 0.02", group="stance_shield", weight=5, min_time=1.6), blend_in=0.3, file=FS)
c.cycle("left_arm", "rotation", lambda u: arm('l', 60 + 2 * wave(u), -30, 40))
c.cycle("right_arm", "rotation", lambda u: arm('r', 30 + 2 * wave(u, 0.3), 20, -20))
c.cycle("right_leg", "rotation", lambda u: leg('r', -12, 8))
c.cycle("left_leg", "rotation", lambda u: leg('l', 12, 8))
c.cycle("mw_root", "position", lambda u: move(0, -1.2 - 0.3 * abs(wave(u))))
c.cycle("body", "rotation", lambda u: tilt(8, 6, 0))
c.cycle("head", "rotation", lambda u: tilt(-4, -2, 0))
for cid, label, cond, stride, extra in (("guard_walk_shield", "Shield Wall Advance", " && q.ground_speed >= 0.02 && q.forward_speed >= 0", 16, {}),
                                        ("guard_strafe_shield", "Shield Circling Strafe", " && math.abs(q.strafe_speed) > 0.03 && math.abs(q.forward_speed) < 0.04", 10, {"legs_out": 10, "side_sign": SIDE}),
                                        ("guard_backpedal_shield", "Shield Retreat", " && q.forward_speed < -0.02", -8, {"legs_out": 12, "root_pitch": -8})):
    c = Clip("player.combat." + cid, label, CAT, T, length=1.0, loop="loop", layer="base", priority=270, trigger=state(SHC + cond, exit_delay=0.12),
             blend_in=0.25, time="q.limb_swing * %g" % round(1.0 / (CYCLE * 0.8), 5), weight="math.clamp(q.limb_swing_amount * 2.2, 0, 1)", file=FS)
    back = "backpedal" in cid
    biped(c, stride=stride, bob=0.2 if back else 0.6, twist=3, sway=1 if back else 3, lean=-4 if back else 10, right_arm=(50, 10, -20) if back else (30, 20, -20),
          left_arm=(84, -24, 50) if back else (60, -30, 40), head_bob=0.5, **extra)
c = Clip("player.combat.stance_fidget_shield", "Tighten Shield Strap", CAT, T, length=1.6, loop="once", layer="base", priority=269,
         trigger=state(SHC + " && q.ground_speed < 0.02", group="stance_shield", weight=1), blend_in=0.2, file=FS)
c.rot("left_arm", (0, arm('l', 60, -30, 40)), (0.4, arm('l', 50, -20, 60)), (1.2, arm('l', 50, -20, 60)), (1.6, arm('l', 60, -30, 40)), lerp="smooth")
c.rot("right_arm", (0, arm('r', 30, 20, -20)), (0.4, arm('r', 60, -40, 30)), (0.8, arm('r', 56, -44, 30)), (1.2, arm('r', 60, -40, 30)), (1.6, arm('r', 30, 20, -20)), lerp="smooth")
c.rot("head", (0, Z), (0.4, tilt(24, -10)), (1.2, tilt(24, -10)), (1.6, Z), lerp="smooth")

# --------------------------------------------------------------------------------- entering and leaving combat
def ready(cid, name, ev, when, L, tracks, pri=176, events=()):
    return keyed(cid, name, event(ev, ALIVE + " && " + when), L, tracks, pri=pri, events=events)


ready("ready_sword", "Snap To Sword Guard", "combat_enter", "q.main_hand == 'sword'", 0.5, {
    "right_arm": [(0, Z), (0.2, arm('r', 90, 30, -60), "out_back"), (0.5, arm('r', 40, 14, -30))], "body": [(0, Z), (0.2, tilt(4, 14)), (0.5, tilt(6, 10))]},
    events=[(0.2, "whoosh", {"weight": "light"})])
ready("ready_axe", "Two-Hand Axe Heft", "combat_enter", "q.main_hand == 'axe'", 0.6, {
    "right_arm": [(0, Z), (0.3, arm('r', 120, 10, 20)), (0.6, arm('r', 70, 20, 20))], "left_arm": [(0, Z), (0.3, arm('l', 80, -20, 30)), (0.6, arm('l', 40, -10, 30))]})
ready("ready_fists", "Raise The Fists", "combat_enter", "q.main_hand == 'empty'", 0.4, {
    "right_arm": [(0, Z), (0.2, arm('r', 80, -10, 40), "out_back"), (0.4, arm('r', 70, -10, 40))], "left_arm": [(0, Z), (0.2, arm('l', 80, -20, 40), "out_back"), (0.4, arm('l', 70, -20, 40))],
    "head": [(0, Z), (0.2, tilt(8)), (0.4, tilt(4))]})
ready("ready_bow", "Ready The Bow", "combat_enter", "q.main_hand == 'bow'", 0.5, {
    "left_arm": [(0, Z), (0.25, arm('l', 50, -10, -20)), (0.5, arm('l', 40, -10, -20))], "right_arm": [(0, Z), (0.2, arm('r', 160, -30, 20)), (0.5, arm('r', 30, 10, 0))]})
ready("ready_trident", "Level The Spear", "combat_enter", "q.main_hand == 'trident'", 0.6, {
    "right_arm": [(0, arm('r', 36, 8, -70)), (0.3, arm('r', 90, 20, 60)), (0.6, arm('r', 60, 10, -70))], "left_arm": [(0, Z), (0.4, arm('l', 70, -30, 30)), (0.6, arm('l', 70, -30, 30))]},
    events=[(0.3, "whoosh", {"weight": "medium"})])
ready("salute_sword", "Duelist's Salute", "combat_enter", "q.main_hand == 'sword' && q.trait_confidence > 0.7", 1.2, {
    "right_arm": [(0, Z), (0.35, arm('r', 150, -20, -80)), (0.7, arm('r', 150, -20, -80)), (0.95, arm('r', 60, 40, -40)), (1.2, arm('r', 40, 14, -30))],
    "head": [(0, Z), (0.35, tilt(10)), (0.7, tilt(14)), (1.2, Z)]}, pri=178, events=[(0.95, "whoosh", {"weight": "light"})])
ready("point_challenge", "Point The Blade", "combat_enter", "q.main_hand == 'sword' && q.near_hostile && q.trait_confidence > 0.5", 1.1, {
    "right_arm": [(0, Z), (0.3, arm('r', 92, -4, -90), "out_back"), (0.8, arm('r', 94, -4, -90)), (1.1, arm('r', 40, 14, -30))],
    "head": [(0, Z), (0.3, tilt(-4)), (0.8, tilt(-6)), (1.1, Z)]}, pri=177)
ready("relax_sword", "Lower Sword And Breathe", "combat_exit", "q.main_hand == 'sword'", 1.0, {
    "right_arm": [(0, arm('r', 40, 14, -30)), (1.0, arm('r', -6, 10, -20), "in_out_sine")], "body": [(0, tilt(6, 10)), (0.5, tilt(-4)), (1.0, Z)],
    "head": [(0, Z), (0.5, tilt(-10)), (1.0, Z)]})
ready("relax_axe", "Rest Axe On Shoulder", "combat_exit", "q.main_hand == 'axe'", 0.9, {
    "right_arm": [(0, arm('r', 70, 20, 20)), (0.9, arm('r', 150, -10, 40), "in_out_sine")], "left_arm": [(0, arm('l', 40, -10, 30)), (0.4, Z)]})
ready("relax_wipe_blade", "Wipe The Blade", "combat_exit", "q.main_hand == 'sword' && q.trait_confidence > 0.6", 1.6, {
    "right_arm": [(0, arm('r', 40, 14, -30)), (0.4, arm('r', 60, -20, 90)), (1.2, arm('r', 62, -20, 90)), (1.6, arm('r', -6, 10, -20))],
    "left_arm": [(0, Z), (0.4, arm('l', 56, -40, 30)), (0.8, arm('l', 64, -10, 30)), (1.2, arm('l', 56, -40, 30)), (1.6, Z)],
    "head": [(0, Z), (0.4, tilt(24, -6)), (1.2, tilt(24, -6)), (1.6, Z)]}, pri=177)

# --------------------------------------------------------------------------------- recoil, catch, breakage
for w, label, pose in (("sword", "Blade Deflected", (80, 30, -20)), ("axe", "Axe Rebounds", (120, 20, 0)), ("empty", "Fist Jarred", (70, 10, 30))):
    keyed("deflected_" + w, label, event("deflected", ALIVE + " && q.main_hand == '%s'" % w), 0.6, {
        "right_arm": [(0, arm('r', 90, -10, 0)), (0.08, arm('r', *pose), "out_expo"), (0.6, Z, "in_out_sine")],
        "body": [(0, Z), (0.08, tilt(-8, 10)), (0.6, Z)], "mw_root:pos": [(0, Z), (0.08, move(0, 0, -1.4)), (0.6, Z)]}, pri=245,
        events=[(0.0, "sound", {"sound": "motionworks:impact.metal" if w != "empty" else "motionworks:impact.wood", "volume": "0.6"}),
                (0.0, "particle", {"particle": "spark", "count": "5", "at": "front", "spread": "0.2"})])
keyed("trident_catch", "Catch Returning Trident", event("pickup:trident", ALIVE), 0.6, {
    "right_arm": [(0, arm('r', 120, 20)), (0.1, arm('r', 100, 20), "out_expo"), (0.6, arm('r', 36, 8, -70))], "body": [(0, Z), (0.1, tilt(-6)), (0.6, Z)]}, pri=200)
BREAK = [(0.0, "sound", {"sound": "minecraft:entity.item.break", "volume": "0.7"}), (0.0, "particle", {"particle": "spark", "count": "6", "at": "front", "spread": "0.3"})]
keyed("tool_break_sword", "Stare At The Broken Hilt", event("tool_break", ALIVE + " && q.event_arg == 'sword'"), 2.0, {
    "right_arm": [(0, arm('r', 70, -10)), (0.15, arm('r', 40, 30), "out_expo"), (0.6, arm('r', 80, -24, 60)), (1.4, arm('r', 82, -24, 60)), (1.7, arm('r', 60, 60, -20), "out_quad"), (2.0, Z)],
    "head": [(0, Z), (0.6, tilt(26, 0, 12)), (1.4, tilt(28, 0, -10)), (1.7, tilt(0, 30)), (2.0, Z)]}, pri=230, events=BREAK + [(1.7, "whoosh", {"weight": "light"})])
keyed("tool_break_axe", "Axe Head Flies Off", event("tool_break", ALIVE + " && q.event_arg == 'axe'"), 1.8, {
    "right_arm": [(0, arm('r', 60, -10)), (0.1, arm('r', 20, 0), "out_expo"), (1.2, arm('r', 30, 6)), (1.8, Z)],
    "head": [(0, Z), (0.2, tilt(-20, 6)), (0.6, tilt(-40, 30)), (1.0, tilt(10, 40)), (1.8, Z)],
    "body": [(0, Z), (0.6, tilt(-8, 20)), (1.0, tilt(4, 30)), (1.8, Z)]}, pri=230, events=BREAK)
keyed("tool_break_pickaxe", "Shake Out A Stinging Hand", event("tool_break", ALIVE + " && q.event_arg == 'pickaxe'"), 1.6, {
    "right_arm": [(0, arm('r', 90, -10)), (0.12, arm('r', 30, 10)), (0.3, arm('r', 20, 30, 20)), (0.45, arm('r', 20, 10, -20)), (0.6, arm('r', 20, 30, 20)),
                  (0.75, arm('r', 20, 10, -20)), (1.6, Z)],
    "head": [(0, Z), (0.3, tilt(30, 14)), (0.9, tilt(30, 14)), (1.6, Z)]}, pri=230, events=BREAK)
keyed("tool_break_other", "Toss Away Broken Tool", event("tool_break", ALIVE + " && q.event_arg != 'sword' && q.event_arg != 'axe' && q.event_arg != 'pickaxe'"), 1.4, {
    "right_arm": [(0, arm('r', 60, -10)), (0.3, arm('r', 70, -20, 30)), (0.8, arm('r', 100, 50, -10), "out_quad"), (1.4, Z)],
    "head": [(0, Z), (0.3, tilt(24)), (0.8, tilt(0, 20)), (1.4, Z)]}, pri=230, events=BREAK)

# --------------------------------------------------------------------------------- sprinting in combat and stance variants
for w, label, rg, lg, lean in (("sword", "Sword Trailing Charge", (-30, 20, -40), None, 16), ("axe", "Axe Overhead Charge", (160, 10, 20), (60, 20, 0), 20),
                               ("trident", "Lowered Spear Charge", (70, 10, -80), (80, -30, 30), 22), ("empty", "Brawler Rush", (60, -10, 40), (60, -20, 40), 18)):
    c = Clip("player.combat.charge_" + w, label, CAT, T, length=0.75, loop="loop", layer="base", priority=325,
             trigger=state(ALIVE + " && q.in_combat && q.is_sprinting && q.is_on_ground && q.main_hand == '%s'" % w, exit_delay=0.12), blend_in=0.2,
             time="q.limb_swing * %g" % round(0.75 / CYCLE, 5), weight="math.clamp(q.limb_swing_amount * 2.2, 0, 1)", file=FS)
    biped(c, stride=56, bob=1.8, twist=6, sway=2, lean=lean, right_arm=rg, left_arm=lg, arm_swing=50, knee_lift=16)

VAR = [("stance_sword_high_guard", "High Guard (Confident)", COMBAT + " && q.main_hand == 'sword' && q.trait_confidence > 0.75 && q.ground_speed < 0.02",
        (150, 10, -60), (40, 20, 0), 272),
       ("stance_sword_low_guard", "Low Guard (Wary)", COMBAT + " && q.main_hand == 'sword' && q.trait_nervous > 0.7 && q.ground_speed < 0.02",
        (10, 20, -10), (30, 30, 0), 271),
       ("stance_axe_berserker", "Berserker Stance", COMBAT + " && q.main_hand == 'axe' && q.health < 0.3 && q.ground_speed < 0.02",
        (130, 40, 30), (60, 40, 0), 273),
       ("stance_fists_bounce", "Bouncing Boxer Stance", COMBAT + " && q.main_hand == 'empty' && q.trait_energy > 0.7 && q.ground_speed < 0.02",
        (76, -14, 50), (64, -24, 40), 271)]
for cid, label, when, rg, lg, pri in VAR:
    c = Clip("player.combat." + cid, label, CAT, T, length=0.9 if "bounce" in cid else 1.6, loop="loop", layer="base", priority=pri,
             trigger=state(when, min_time=1.6), blend_in=0.3, file=FS)
    bouncy = "bounce" in cid
    c.cycle("right_arm", "rotation", lambda u, g=rg: arm('r', g[0] + 4 * wave(u), g[1], g[2]))
    c.cycle("left_arm", "rotation", lambda u, g=lg: arm('l', g[0] + 4 * wave(u, 0.4), g[1], g[2]))
    c.cycle("right_leg", "rotation", lambda u, b=bouncy: leg('r', -12 + (6 * wave(u) if b else 0), 10))
    c.cycle("left_leg", "rotation", lambda u, b=bouncy: leg('l', 16 - (6 * wave(u) if b else 0), 10, 10))
    c.cycle("mw_root", "position", lambda u, b=bouncy: move(0, -1.4 - (1.6 * abs(wave(u)) if b else 0.3 * wave(u))))
    c.cycle("body", "rotation", lambda u, b=bouncy: tilt(8, 12 + (6 * wave(u) if b else 0), 0))
    c.cycle("head", "rotation", lambda u, b=bouncy: tilt(-4, 6 * wave(u, 0.2) if b else 2, 0))
c = Clip("player.combat.stance_trident_brace", "Spear Brace Against Charge", CAT, T, length=2.0, loop="loop", layer="base", priority=430,
         trigger=state(ALIVE + " && q.in_combat && q.is_sneaking && q.main_hand == 'trident' && q.ground_speed < 0.01"), blend_in=0.3, file=FS)
c.cycle("right_leg", "rotation", lambda u: leg('r', -30, 10))
c.cycle("left_leg", "rotation", lambda u: leg('l', 50, 8))
c.cycle("mw_root", "position", lambda u: move(0, -3.0 + 0.2 * wave(u)))
c.cycle("right_arm", "rotation", lambda u: arm('r', 40, 10, -80))
c.cycle("left_arm", "rotation", lambda u: arm('l', 50, -30, 30))
c.cycle("body", "rotation", lambda u: tilt(20, 10, 0))
c.cycle("head", "rotation", lambda u: tilt(-16, -6, 0))
c = Clip("player.combat.stance_bow_sniper", "Sniper Crouch", CAT, T, length=3.0, loop="loop", layer="base", priority=431,
         trigger=state(ALIVE + " && q.in_combat && q.is_sneaking && q.main_hand == 'bow' && !q.is_using_item && q.ground_speed < 0.01"), blend_in=0.3, file=FS)
c.cycle("right_leg", "rotation", lambda u: leg('r', 80, 8))
c.cycle("left_leg", "rotation", lambda u: leg('l', 30, 8))
c.cycle("mw_root", "position", lambda u: move(0, -4.0))
c.cycle("left_arm", "rotation", lambda u: arm('l', 40, -10, -30))
c.cycle("right_arm", "rotation", lambda u: arm('r', 20, 10))
c.cycle("head", "rotation", lambda u: tilt(-6, 20 * wave(u), 0))
c = Clip("player.combat.wounded_shuffle", "Wounded Combat Shuffle", CAT, T, length=1.1, loop="loop", layer="base", priority=275,
         trigger=state(COMBAT + " && q.health < 0.3 && q.ground_speed >= 0.02", exit_delay=0.12), blend_in=0.25,
         time="q.limb_swing * %g" % round(1.1 / (CYCLE * 0.8), 5), weight="math.clamp(q.limb_swing_amount * 2.2, 0, 1)", file=FS)
biped(c, stride=18, bob=1.4, twist=2, sway=4, lean=14, right_arm=(50, 10, -10), left_arm=(30, -20, 30), asym=0.5, head_bob=2)
c = Clip("player.combat.taunt_beckon", "Beckoning Taunt", CAT, T, length=1.8, loop="once", layer="base", priority=265,
         trigger=state(COMBAT + " && q.main_hand == 'empty' && q.near_hostile && q.trait_confidence > 0.6 && q.ground_speed < 0.02", group="stance_empty", weight=1),
         blend_in=0.2, file=FS)
c.rot("right_arm", (0, arm('r', 70, -10, 40)), (0.3, arm('r', 90, -6, -60)), (0.5, arm('r', 90, -6, -20)), (0.7, arm('r', 90, -6, -60)), (0.9, arm('r', 90, -6, -20)), (1.8, arm('r', 70, -10, 40)), lerp="smooth")
c.rot("head", (0, Z), (0.3, tilt(-10, 0, 8)), (1.2, tilt(-10, 0, 8)), (1.8, Z), lerp="smooth")
melee("axe_whirlwind", "Whirlwind Sprint Spin", ALIVE + " && q.main_hand == 'axe' && q.is_sprinting && q.combo == 2", 217, 0.9, 0.2, 0.45, 0.7,
      ((80, 90, -20), (90, 70, 0), (84, 60, 0)), (tilt(10, 20), tilt(12, 0), tilt(10, 0)), (move(0, -0.8), move(0, -1.2, 1.0)), weight=HEAVY, spin=-360,
      file="player/combat_melee")
c = act("crossbow_reload_walk", "Steady Reload While Walking", state(W("crossbow") + " && q.is_using_item && q.ground_speed > 0.02", exit_delay=0.1), 1.0,
        pri=23, layer="additive", file="player/combat_ranged", loop="loop")
c.key("body", "rotation", 0, ["6 + math.sin(q.limb_swing * 76.394) * 2 * q.limb_swing_amount", 0, 0])
c.key("head", "rotation", 0, ["math.sin(q.limb_swing * 76.394) * -3 * q.limb_swing_amount", 0, 0])
c = act("bow_strafe_aim", "Strafing Aim Compensation", state(W("bow") + " && q.is_using_item && math.abs(q.strafe_speed) > 0.02", exit_delay=0.1), 1.0,
        pri=24, layer="additive", file="player/combat_ranged", loop="loop")
c.key("mw_root", "rotation", 0, [0, "math.clamp(q.strafe_speed * 80, -14, 14)", 0])
c.key("body", "rotation", 0, [0, "math.clamp(q.strafe_speed * -100, -18, 18)", 0])

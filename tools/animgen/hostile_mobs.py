"""Hostile mobs: undead, arthropods, endermen, nether and ocean monsters, illagers and bosses.

Hostile motion is built around readable threat: every attack has anticipation the player can learn,
idles communicate intent (stalking, scanning, swelling), and reactions show weight.
"""
from core import arm, leg, biped, manual
from mobkit import anchored, mob, gait, life, loop_state, beat, driven, Z, state, event, wave, cwave, tilt, move

CAT = "hostile_mobs"
ALIVE = "!q.is_dead"
STILL = ALIVE + " && q.is_on_ground && q.ground_speed < 0.01"
WALKING = ALIVE + " && q.is_on_ground && q.ground_speed >= 0.01"
HUNT = " && (q.is_aggressive || q.in_combat)"
CALM = " && !q.is_aggressive && !q.in_combat"


def f(name):
    return "mobs/hostile/" + name


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def hwalk(cid, name, T, when, L, F, pri=100, keep_head=False, k=2.2, **params):
    """Humanoid locomotion synced to the limb swing; drops the head channel so mobs keep tracking targets."""
    c = mob(cid, name, CAT, T, L, state(when, exit_delay=0.15), layer="base", pri=pri, file=F, **driven(L, 1.0, k))
    biped(c, **params)
    if not keep_head:
        c.bones.pop("head", None)
    return c


def strike_arms(cid, name, T, trig, L, F, right, left=None, body=None, pri=160, events=(), extra=None):
    """Arm attack from (time, [fwd, out, twist]) poses."""
    tracks = {"right_arm:rot": [(t, arm('r', *p), *e) for t, p, *e in right]}
    if left:
        tracks["left_arm:rot"] = [(t, arm('l', *p), *e) for t, p, *e in left]
    if body:
        tracks["body:rot"] = body
    if extra:
        tracks.update(extra)
    return beat(cid, name, CAT, T, trig, L, F, tracks, pri=pri, events=events)


# ============================================================================ zombie family
T, F = "minecraft:zombie", f("zombie")
hwalk("zombie.shamble", "Zombie Shamble", T, WALKING + CALM + " && !q.is_baby", 1.4, F, stride=22, arm_swing=0, bob=0.5, twist=6, sway=4, lean=8,
      right_arm=[85, 6, 0], left_arm=[80, -2, 0], asym=0.4, head_hold=[10, 0, 8])
hwalk("zombie.hunt_lurch", "Zombie Hunting Lurch", T, WALKING + HUNT + " && !q.is_baby", 0.9, F, pri=101, stride=34, arm_swing=0, bob=1.2, twist=10, sway=3, lean=16,
      right_arm=[100, 8, 0], left_arm=[95, 8, 0], knee_lift=10)
hwalk("zombie.baby_sprint", "Baby Zombie Sprint", T, WALKING + " && q.is_baby", 0.45, F, pri=102, stride=48, arm_swing=40, arm_out=10, bob=1.8, twist=8, sway=2, lean=24)
strike_arms("zombie.claw_swipe", "Zombie Clawing Swipe", T, event("attack", ALIVE + " && q.main_hand == 'empty'"), 0.7, F,
            [(0, [90, 4, 0]), (0.2, [130, 20, 20], "out_quad"), (0.34, [60, -10, -10], "in_quart"), (0.7, [90, 4, 0])],
            [(0, [85, 0, 0]), (0.3, [120, 15, 0]), (0.45, [70, -6, 0], "in_quart"), (0.7, [85, 0, 0])], body=[(0, Z), (0.2, tilt(-6, 10, 0)), (0.34, tilt(10, -12, 0)), (0.7, Z)],
            events=[(0.3, "whoosh", {"weight": "medium"})])
strike_arms("zombie.weapon_bash", "Zombie Clumsy Weapon Bash", T, event("attack", ALIVE + " && q.main_hand != 'empty'"), 0.8, F,
            [(0, [40, 0, 0]), (0.3, [160, 10, 0], "out_quad"), (0.45, [30, 0, 0], "in_quart"), (0.8, [40, 0, 0])], body=[(0, Z), (0.3, tilt(-10, 0, 0)), (0.45, tilt(16, 0, 0)), (0.8, Z)])
loop_state("zombie.idle_sway", "Zombie Swaying Idle", CAT, T, STILL + CALM, 4.0, F, {
    "body:rot": lambda u: tilt(6, 4 * wave(u, 0.2), 5 * wave(u)), "head:rot": lambda u: [14 + 4 * wave(u, 0.3), 0, 12 * wave(u, 0.1)],
    "right_arm:rot": lambda u: arm('r', 70 + 6 * wave(u), 4), "left_arm:rot": lambda u: arm('l', 60 + 6 * wave(u, 0.4), 2)})
beat("zombie.groan", "Zombie Groan", CAT, T, event("vocalize", ALIVE), 1.8, F, {
    "head:rot": [(0, Z), (0.5, [-20, 0, 14], "in_out_sine"), (1.2, [-16, 0, -10]), (1.8, Z)], "body:rot": [(0, Z), (0.5, tilt(-6, 0, 0)), (1.8, Z)]}, layer="gesture")
loop_state("zombie.sunburn", "Zombie Burning In Sunlight", CAT, T, ALIVE + " && q.is_on_fire && !q.is_in_water", 0.5, F, {
    "right_arm:rot": lambda u: arm('r', 150 + 30 * wave(u), 30 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 140 + 30 * wave(u, 0.5), 30 * wave(u, 0.8)),
    "head:rot": lambda u: [-10, 25 * wave(u, 0, 0.5), 0], "body:rot": lambda u: tilt(0, 10 * wave(u, 0.25), 0)}, pri=150, layer="action")
loop_state("zombie.door_bash", "Zombie Pounding On A Door", CAT, T, ALIVE + HUNT + " && q.ground_speed < 0.01 && q.is_swinging", 0.6, F, {
    "right_arm:rot": lambda u: arm('r', 120 + 30 * wave(u), 0), "left_arm:rot": lambda u: arm('l', 120 + 30 * wave(u, 0.5), 0), "body:rot": lambda u: tilt(8 + 4 * wave(u, 0, 2), 0, 0)}, pri=140,
    layer="action")
beat("zombie.notice", "Zombie Noticing Prey", CAT, T, event("notice", ALIVE), 0.9, F, {
    "head:rot": [(0, Z), (0.2, [-16, 0, 0], "out_expo"), (0.9, Z)], "body:rot": [(0, Z), (0.2, tilt(-8, 0, 0)), (0.5, tilt(10, 0, 0)), (0.9, Z)],
    "right_arm:rot": [(0, arm('r', 90)), (0.3, arm('r', 110, 10)), (0.9, arm('r', 90))]}, layer="gesture", pri=150)
loop_state("zombie.stumble_idle", "Zombie Stumbling In Place", CAT, T, STILL + CALM + " && q.idle_time > 8", 2.5, F, {
    "mw_root:pos": lambda u: move(0.8 * wave(u), 0, 0.4 * wave(u, 0.25)), "right_leg:rot": lambda u: leg('r', 14 * max(0, wave(u, 0.1))), "left_leg:rot": lambda u: leg('l', 14 * max(0, wave(u, 0.6))),
    "body:rot": lambda u: tilt(8, 0, 6 * wave(u, 0.1))}, group="zombie_idle", weight=1)
beat("zombie.rise_from_ground", "Zombie Clawing Out Of The Earth", CAT, T, manual(desc="Spawned by cinematic sequences and the /mw play command"), 3.0, F, {
    "mw_root:pos": [(0, move(0, -26, 0)), (1.0, move(0, -14, 0), "out_quad"), (2.2, move(0, -2, 0)), (3.0, Z)],
    "right_arm:rot": [(0, arm('r', 170)), (0.8, arm('r', 150, 20)), (1.6, arm('r', 90, 30)), (3.0, arm('r', 90))],
    "left_arm:rot": [(0, arm('l', 160)), (1.0, arm('l', 160, 10)), (1.8, arm('l', 80, 30)), (3.0, arm('l', 85))], "body:rot": [(0, tilt(20)), (2.0, tilt(14, 0, 8)), (3.0, Z)]},
    pri=250, events=[(0.2, "particle", {"particle": "dust_puff", "count": "16", "at": "feet", "spread": "0.6"})])

T, F = "minecraft:husk", f("husk")
hwalk("husk.desert_drag", "Husk Desert Drag", T, WALKING + CALM, 1.7, F, stride=18, arm_swing=0, bob=0.3, twist=3, sway=5, lean=12, right_arm=[70, 10, 0], left_arm=[88, 0, 0],
      asym=0.6, knee_lift=0, legs_out=3)
hwalk("husk.sand_charge", "Husk Sand-Blind Charge", T, WALKING + HUNT, 0.8, F, pri=101, stride=36, arm_swing=0, bob=1, twist=12, sway=5, lean=26, right_arm=[110, 14, 0], left_arm=[60, 30, 0], asym=0.5)
loop_state("husk.parched_idle", "Husk Parched Hunch", CAT, T, STILL, 3.2, F, {"body:rot": lambda u: tilt(18 + 2 * wave(u), 0, 0), "head:rot": lambda u: [20, 0, 6 * wave(u, 0.3)],
                                                                             "right_arm:rot": lambda u: arm('r', 40, 6), "left_arm:rot": lambda u: arm('l', 45, 4)})
beat("husk.dust_cough", "Husk Dusty Rasp", CAT, T, event("vocalize", ALIVE), 1.0, F, {"body:rot": [(0, Z), (0.15, tilt(14)), (0.3, tilt(4)), (0.45, tilt(14)), (1.0, Z)],
                                                                             "head:rot": [(0, Z), (0.15, [20, 0, 0]), (0.45, [20, 0, 0]), (1.0, Z)]}, layer="gesture",
     events=[(0.15, "particle", {"particle": "dust_puff", "count": "6", "at": "head", "spread": "0.2"})])
strike_arms("husk.hunger_grab", "Husk Starving Grab", T, event("attack", ALIVE), 0.65, F, [(0, [90]), (0.18, [60, 30, 0]), (0.3, [100, -20, 0], "in_quart"), (0.65, [90])],
            [(0, [90]), (0.18, [60, -30 + 60, 0]), (0.3, [100, -20, 0], "in_quart"), (0.65, [90])], body=[(0, Z), (0.3, tilt(14)), (0.65, Z)])
life("husk.heat_shimmer", "Husk Heat Sway", CAT, T, ALIVE + " && q.temperature > 1.5", 6.0, F, {"mw_root:rot": lambda u: tilt(0, 0, 2 * wave(u))})

T, F = "minecraft:drowned", f("drowned")
c = mob("drowned.swim", "Drowned Grasping Swim", CAT, T, 1.4, state(ALIVE + " && q.is_in_water && !q.is_on_ground"), layer="base", file=F)
c.cycle("right_arm", "rotation", lambda u: arm('r', 160 + 20 * wave(u), 20 + 15 * cwave(u)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 160 + 20 * wave(u, 0.5), 20 + 15 * cwave(u, 0.5)))
c.cycle("right_leg", "rotation", lambda u: leg('r', 20 * wave(u, 0, 2)))
c.cycle("left_leg", "rotation", lambda u: leg('l', -20 * wave(u, 0, 2)))
c.cycle("body", "rotation", lambda u: tilt(6 * wave(u), 0, 0))
hwalk("drowned.seabed_walk", "Drowned Seabed Trudge", T, WALKING + " && q.is_in_water", 2.0, F, pri=101, stride=16, arm_swing=6, arm_out=20, bob=0.2, twist=4, sway=3, lean=4,
      right_arm=None, left_arm=None, legs_out=4)
hwalk("drowned.land_walk", "Drowned Dripping Walk", T, WALKING + " && !q.is_in_water", 1.3, F, pri=100, stride=24, arm_swing=0, bob=0.6, twist=5, sway=3, lean=6, right_arm=[80, 12, 10],
      left_arm=[70, 4, 0], asym=0.25)
loop_state("drowned.trident_aim", "Drowned Raising Trident", CAT, T, ALIVE + " && q.main_hand == 'trident' && q.is_aggressive && q.ground_speed < 0.05", 1.2, F, {
    "right_arm:rot": lambda u: arm('r', 170, 0, 0), "left_arm:rot": lambda u: arm('l', 40, 10), "body:rot": lambda u: tilt(-6, 20, 0)}, pri=140, layer="action")
loop_state("drowned.float_idle", "Drowned Drifting Idle", CAT, T, ALIVE + " && q.is_underwater && q.ground_speed < 0.02", 4.5, F, {
    "right_arm:rot": lambda u: arm('r', 40 + 20 * wave(u), 30 + 10 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 30 + 20 * wave(u, 0.4), 30 + 10 * wave(u, 0.7)),
    "head:rot": lambda u: [20 * wave(u, 0.1), 0, 15 * wave(u)], "mw_root:pos": lambda u: move(0, 0.8 * wave(u), 0)}, pri=110)
beat("drowned.gurgle", "Drowned Gurgle", CAT, T, event("vocalize", ALIVE), 1.2, F, {"head:rot": [(0, Z), (0.3, [-25, 0, 0]), (0.6, [-20, 0, 10]), (1.2, Z)]}, layer="gesture",
     events=[(0.3, "particle", {"particle": "bubble_trail", "count": "6", "at": "head", "spread": "0.2"})])
strike_arms("drowned.drag_under", "Drowned Drag-Under Grab", T, event("attack", ALIVE + " && q.is_in_water"), 0.8, F,
            [(0, [120]), (0.2, [170, 20, 0]), (0.4, [40, 10, 0], "in_quart"), (0.8, [120])], [(0, [120]), (0.2, [170, 20, 0]), (0.4, [40, 10, 0], "in_quart"), (0.8, [120])],
            body=[(0, Z), (0.4, tilt(30)), (0.8, Z)])

T, F = "minecraft:giant", f("giant")
hwalk("giant.quake_step", "Giant Earthshaking Step", T, WALKING, 2.6, F, stride=18, arm_swing=14, arm_out=10, bob=1.5, twist=3, sway=2, lean=2)
loop_state("giant.loom", "Giant Looming", CAT, T, STILL, 6.0, F, {"body:rot": lambda u: tilt(4, 6 * wave(u), 0), "right_arm:rot": lambda u: arm('r', 80 + 4 * wave(u), 4)})
beat("giant.stomp", "Giant Stomp", CAT, T, event("vocalize", ALIVE), 2.0, F, {"right_leg:rot": [(0, Z), (0.8, leg('r', 50)), (1.0, leg('r', -6), "in_quart"), (2.0, Z)],
                                                                         "body:rot": [(0, Z), (0.8, tilt(-6)), (1.0, tilt(6)), (2.0, Z)]},
     events=[(1.0, "stomp", {"strength": "1"}), (1.0, "shake", {"intensity": "0.4", "duration": "0.5"})])

T, F = "minecraft:zombie_villager", f("zombie_villager")
hwalk("zombie_villager.shuffle", "Zombie Villager Shuffle", T, WALKING, 1.5, F, stride=20, arm_swing=0, bob=0.4, twist=5, sway=4.5, lean=10, right_arm=[75, 2, 0], left_arm=[90, 2, 0],
      asym=0.3, head_hold=[20, 0, -6], keep_head=True)
loop_state("zombie_villager.lost_idle", "Zombie Villager Lost Wandering Look", CAT, T, STILL, 5.0, F, {"head:rot": lambda u: [25, 30 * wave(u), 0], "body:rot": lambda u: tilt(8, 0, 3 * wave(u, 0.2))})
loop_state("zombie_villager.curing_tremor", "Zombie Villager Curing Tremors", CAT, T, ALIVE + " && q.is_shaking", 0.3, F, {
    "body:rot": lambda u: tilt(0, 4 * wave(u), 3 * wave(u, 0.3)), "head:rot": lambda u: [10 * wave(u, 0.1), 0, 8 * wave(u, 0.6)], "right_arm:rot": lambda u: arm('r', 30 + 10 * wave(u), 10)}, pri=160)
beat("zombie_villager.mournful_hrmm", "Zombie Villager Mournful Hrmm", CAT, T, event("vocalize", ALIVE), 1.6, F, {"head:rot": [(0, Z), (0.4, [30, 0, 15]), (1.0, [32, 0, -12]), (1.6, Z)],
                                                                                                       "body:rot": [(0, Z), (0.4, tilt(6)), (1.6, Z)]}, layer="gesture")
strike_arms("zombie_villager.flail", "Zombie Villager Flailing Swat", T, event("attack", ALIVE), 0.7, F, [(0, [90]), (0.15, [150, 30, 0]), (0.3, [40, -10, 0], "in_quart"), (0.7, [90])],
            [(0, [90]), (0.3, [140, 30, 0]), (0.45, [40, -10, 0], "in_quart"), (0.7, [90])])
loop_state("zombie_villager.door_drag", "Zombie Villager Dragging Itself", CAT, T, WALKING + " && q.health < 0.3", 1.8, F, {
    "right_leg:rot": lambda u: leg('r', 20 * cwave(u)), "left_leg:rot": lambda u: leg('l', -6), "body:rot": lambda u: tilt(20, 0, 10 * max(0, wave(u))),
    "right_arm:rot": lambda u: arm('r', 90 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', 30, 20)}, pri=105, layer="base")

# ============================================================================ skeletons
for T, sp, label in (("minecraft:skeleton", "skeleton", "Skeleton"), ("minecraft:stray", "stray", "Stray"), ("minecraft:wither_skeleton", "wither_skeleton", "Wither Skeleton")):
    F = f(sp)
    wither = sp == "wither_skeleton"
    stray = sp == "stray"
    c = mob(sp + ".walk", label + (" Menacing Stride" if wither else (" Frostbitten Gait" if stray else " Rattling Walk")), CAT, T, 1.1 if not wither else 1.4,
            state(WALKING + CALM, exit_delay=0.15), layer="base", file=F, **driven(1.1 if not wither else 1.4))
    biped(c, stride=28 if not stray else 22, arm_swing=18 if not wither else 10, bob=0.5, twist=8 if not stray else 3, sway=1.5 if not stray else 4, lean=2 if not wither else -3,
          asym=0.0 if not stray else 0.35, knee_lift=0 if not wither else 12)
    c.bones.pop("head", None)
    life(sp + ".bone_rattle", label + " Bone Rattle", CAT, T, ALIVE, 0.25 if not wither else 0.35, F, {
        "right_arm:rot": lambda u, a=(1.2 if not wither else 0.6): [a * wave(u), 0, a * wave(u, 0.3)], "left_arm:rot": lambda u, a=(1.2 if not wither else 0.6): [a * wave(u, 0.5), 0, a * wave(u, 0.8)],
        "head:rot": lambda u: [0, 0, 0.6 * wave(u, 0.2)]} if not stray else {"right_arm:rot": lambda u: [1.6 * wave(u, 0, 2), 0, 0], "left_arm:rot": lambda u: [1.6 * wave(u, 0.5, 2), 0, 0],
                                                                         "body:rot": lambda u: [0, 0, 0.8 * wave(u, 0.25, 2)]})
T, F = "minecraft:skeleton", f("skeleton")
c = mob("skeleton.strafe_draw", "Skeleton Strafing Archer", CAT, T, 0.9, state(WALKING + HUNT + " && q.main_hand == 'bow'", exit_delay=0.15), layer="base", pri=101, file=F, **driven(0.9))
biped(c, stride=20, arm_swing=0, bob=0.4, twist=0, sway=3, lean=0, arms=False, side_sign="(q.strafe_speed >= 0 ? 1 : -1)")
c.bones.pop("head", None)
loop_state("skeleton.scan", "Skeleton Scanning For Targets", CAT, T, STILL + CALM, 4.0, F, {"head:rot": lambda u: [0, 50 * wave(u), 0], "body:rot": lambda u: tilt(0, 10 * wave(u, 0.05), 0)})
beat("skeleton.jaw_clack", "Skeleton Jaw Clack", CAT, T, event("vocalize", ALIVE), 0.6, F, {"head:rot": [(0, Z), (0.1, [-10, 0, 0]), (0.2, [4, 0, 0]), (0.3, [-10, 0, 0]), (0.4, [4, 0, 0]), (0.6, Z)]},
     layer="gesture")
loop_state("skeleton.sunburn_panic", "Skeleton Smouldering Flail", CAT, T, ALIVE + " && q.is_on_fire", 0.4, F, {
    "right_arm:rot": lambda u: arm('r', 130 + 40 * wave(u), 20), "left_arm:rot": lambda u: arm('l', 30 + 40 * wave(u, 0.5), 40), "head:rot": lambda u: [-20, 40 * wave(u, 0, 0.5), 0]}, pri=150,
    layer="action")
T, F = "minecraft:stray", f("stray")
life("stray.frost_breath", "Stray Frost Breath", CAT, T, ALIVE, 3.0, F, {"head:rot": lambda u: [-4 * spike(u, 0.3, 4), 0, 0]})
loop_state("stray.hunched_cold", "Stray Hunched Against The Cold", CAT, T, STILL, 3.0, F, {"body:rot": lambda u: tilt(12, 0, 0), "right_arm:rot": lambda u: arm('r', 20, -8),
                                                                                      "left_arm:rot": lambda u: arm('l', 20, -8), "head:rot": lambda u: [16, 0, 2 * wave(u, 0, 4)]})
T, F = "minecraft:wither_skeleton", f("wither_skeleton")
strike_arms("wither_skeleton.overhead_cleave", "Wither Skeleton Overhead Cleave", T, event("attack", ALIVE + " && q.main_hand == 'sword'"), 0.9, F,
            [(0, [20]), (0.35, [175, 10, 0], "out_quad"), (0.5, [20, -6, 0], "in_quart"), (0.9, [20])], body=[(0, Z), (0.35, tilt(-12, 0, 0)), (0.5, tilt(18, 0, 0)), (0.9, Z)],
            events=[(0.45, "whoosh", {"weight": "heavy"})])
strike_arms("wither_skeleton.backhand", "Wither Skeleton Backhand Slash", T, event("attack", ALIVE + " && q.main_hand == 'sword' && q.in_combat", weight=1), 0.7, F,
            [(0, [20]), (0.25, [80, -40, 40], "out_quad"), (0.38, [70, 60, -30], "in_quart"), (0.7, [20])], body=[(0, Z), (0.25, tilt(0, -30, 0)), (0.38, tilt(0, 30, 0)), (0.7, Z)])
loop_state("wither_skeleton.guard_stance", "Wither Skeleton Guard Stance", CAT, T, ALIVE + HUNT + " && q.ground_speed < 0.02", 2.0, F, {
    "right_arm:rot": lambda u: arm('r', 60, 10, -20), "left_arm:rot": lambda u: arm('l', 30, 20), "body:rot": lambda u: tilt(6, -14, 0), "right_leg:rot": lambda u: leg('r', -12),
    "left_leg:rot": lambda u: leg('l', 16)}, pri=120)
loop_state("wither_skeleton.nether_patrol", "Wither Skeleton Fortress Patrol Pause", CAT, T, STILL + CALM, 5.0, F, {"head:rot": lambda u: [8, 60 * wave(u), 0], "body:rot": lambda u: tilt(0, 20 * wave(u, 0.1), 0)})

# ============================================================================ creeper
T, F = "minecraft:creeper", f("creeper")
gait("creeper.creep", "Creeper Silent Creep", CAT, T, WALKING + CALM, 1.2, F, gait="trot", stride=26, duty=0.55, bob=0.2, pitch=0.6, roll=1.5, roll_phase=0.25, splay=6)
gait("creeper.stalk", "Creeper Closing In", CAT, T, WALKING + HUNT, 0.8, F, pri=101, gait="pace", stride=30, duty=0.5, bob=0.6, pitch=2, roll=2.5, snap=0.2)
loop_state("creeper.swell_tremble", "Creeper Swelling Tremble", CAT, T, ALIVE + " && q.is_charging", 0.15, F, {
    "head:rot": lambda u: [3 * wave(u), 3 * wave(u, 0.3), 3 * wave(u, 0.6)], "body:rot": lambda u: [0, 2 * wave(u, 0.5), 0], "mw_root:pos": lambda u: move(0.25 * wave(u), 0, 0.25 * wave(u, 0.25))},
    pri=200, layer="additive")
loop_state("creeper.peek", "Creeper Peeking Around", CAT, T, STILL + CALM, 5.0, F, {"head:rot": lambda u: [-6 + 4 * wave(u, 0.3), 70 * spike(u, 0.2, 2) - 70 * spike(u, 0.7, 2), 0]})
loop_state("creeper.charged_crackle", "Charged Creeper Crackling", CAT, T, ALIVE + " && q.is_powered", 0.4, F, {"head:rot": lambda u: [0, 0, 1.2 * spike(u, 0.1, 20)],
                                                                                                             "body:scl": lambda u: [1 + 0.02 * spike(u, 0.1, 20)] * 3}, layer="additive", pri=70)
beat("creeper.hiss_rear", "Creeper Rearing Hiss", CAT, T, event("aggro", ALIVE), 0.6, F, {
    "mw_center:rot": [(0, Z), (0.15, tilt(-8, 0, 0)), (0.6, Z)], "head:rot": [(0, Z), (0.15, [-14, 0, 0]), (0.6, Z)], "body:scl": [(0, [1, 1, 1]), (0.15, [1.05, 1.08, 1.05]), (0.6, [1, 1, 1])]},
    layer="gesture")
loop_state("creeper.defuse_retreat", "Creeper Defusing And Backing Off", CAT, T, WALKING + " && q.swell > 0.05 && !q.is_charging", 0.6, F, {
    "head:rot": lambda u: [10, 0, 0], "left_front_leg:rot": lambda u: [25 * cwave(u), 0, 0], "right_front_leg:rot": lambda u: [-25 * cwave(u), 0, 0], "mw_center:rot": lambda u: tilt(-4, 0, 0)}, pri=120)
life("creeper.leaf_rustle", "Creeper Rustling Foliage", CAT, T, ALIVE + " && q.feet_block == 'foliage'", 1.2, F, {"mw_center:rot": lambda u: tilt(0, 0, 1 * wave(u, 0, 3))})
beat("creeper.fuse_pop", "Creeper Final Swell", CAT, T, event("death", "q.swell > 0.9"), 0.3, F, {"body:scl": [(0, [1.2, 1.2, 1.2]), (0.15, [1.5, 1.4, 1.5], "in_expo"), (0.3, [1.5, 1.4, 1.5])]}, pri=300)

# ============================================================================ spiders
SPL = [f"{s}_{p}_leg" for s in ("right", "left") for p in ("hind", "middle_hind", "middle_front", "front")]
# alternating tetrapod: R1 L2 R3 L4 lift together, then the other set
SET_A = {"right_front_leg", "left_middle_front_leg", "right_middle_hind_leg", "left_hind_leg"}


def spider_walk(c, swing=24, lift=14, roll=2.0, wave_body=0.0):
    for b in SPL:
        ph = 0.0 if b in SET_A else 0.5
        side = 1 if b.startswith("right") else -1
        c.cycle(b, "rotation", lambda u, ph=ph, side=side: [0, swing * wave(u, ph) * side, lift * max(0, cwave(u, ph)) * side])
    c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, roll * wave(u, 0, 2)))
    if wave_body:
        c.cycle("body1", "rotation", lambda u: [0, wave_body * wave(u, 0.25), 0])


for T, sp, label, quick in (("minecraft:spider", "spider", "Spider", 1.0), ("minecraft:cave_spider", "cave_spider", "Cave Spider", 1.6)):
    F = f(sp)
    c = mob(sp + ".scuttle", label + " Scuttle", CAT, T, 0.6 / quick, state(WALKING + " && !q.is_climbing", exit_delay=0.1), layer="base", file=F, **driven(0.6 / quick, 2.0))
    spider_walk(c, swing=24 if quick == 1 else 30, lift=14 if quick == 1 else 8, roll=2.0 if quick == 1 else 4.0, wave_body=6 if quick == 1 else 0)
    c = mob(sp + ".wall_climb", label + (" Wall Climb" if quick == 1 else " Skittering Climb"), CAT, T, 0.5 / quick, state(ALIVE + " && q.is_climbing"), layer="base", pri=101, file=F)
    for b in SPL:
        ph = 0.0 if b in SET_A else 0.5
        side = 1 if b.startswith("right") else -1
        if quick == 1:
            c.cycle(b, "rotation", lambda u, ph=ph, side=side: [0, 10 * wave(u, ph) * side, (30 + 20 * max(0, cwave(u, ph))) * side])
        else:
            c.cycle(b, "rotation", lambda u, ph=ph, side=side: [6 * wave(u, ph, 2), 16 * wave(u, ph) * side, (22 + 10 * wave(u, ph, 2)) * side])
    c.cycle("body1", "rotation", (lambda u: [0, 0, 4 * wave(u)]) if quick == 1 else (lambda u: [5 * wave(u, 0, 2), 6 * wave(u), 0]))
    if quick == 1:
        beat(sp + ".pounce", label + " Pounce", CAT, T, event("jump", ALIVE + HUNT), 0.7, F, dict(
            {b + ":rot": [(0, Z), (0.1, [0, 0, (40 if b.startswith("right") else -40)]), (0.4, [0, (30 if "front" in b else -20) * (1 if b.startswith("right") else -1), 10]), (0.7, Z)] for b in SPL},
            **{"mw_center:rot": [(0, Z), (0.1, tilt(10, 0, 0)), (0.35, tilt(-14, 0, 0)), (0.7, Z)]}), pri=160)
    else:
        beat(sp + ".pounce", label + " Darting Lunge", CAT, T, event("jump", ALIVE + HUNT), 0.45, F, {
            "right_front_leg:rot": [(0, Z), (0.08, [0, 40, 50]), (0.25, [0, -20, 20]), (0.45, Z)], "left_front_leg:rot": [(0, Z), (0.08, [0, -40, -50]), (0.25, [0, 20, -20]), (0.45, Z)],
            "mw_center:pos": [(0, Z), (0.08, move(0, -0.5, 0)), (0.25, move(0, 0.5, 2)), (0.45, Z)]}, pri=160)
F, T = f("spider"), "minecraft:spider"
loop_state("spider.leg_tap", "Spider Tapping Its Forelegs", CAT, T, STILL + CALM, 1.6, F, {
    "right_front_leg:rot": lambda u: [0, 0, 20 * spike(u, 0, 4, 2) + 10], "left_front_leg:rot": lambda u: [0, 0, -20 * spike(u, 0.25, 4, 2) - 10]}, group="spider_idle", weight=2)
beat("spider.fang_bite", "Spider Fang Bite", CAT, T, event("melee_hit", ALIVE), 0.5, F, {
    "head:rot": [(0, Z), (0.1, [-20, 0, 0]), (0.2, [20, 0, 0], "in_quart"), (0.5, Z)], "right_front_leg:rot": [(0, Z), (0.1, [0, 20, 40]), (0.2, [0, -10, 10]), (0.5, Z)],
    "left_front_leg:rot": [(0, Z), (0.1, [0, -20, -40]), (0.2, [0, 10, -10]), (0.5, Z)], "mw_center:pos": [(0, Z), (0.2, move(0, 0, 2)), (0.5, Z)]}, pri=170)
beat("spider.hiss_threat", "Spider Threat Display", CAT, T, event("notice", ALIVE), 1.0, F, {
    "mw_center:rot": [(0, Z), (0.25, tilt(-25, 0, 0)), (0.75, tilt(-25, 0, 0)), (1.0, Z)], "right_front_leg:rot": [(0, Z), (0.25, [0, 30, 60]), (0.75, [0, 30, 60]), (1.0, Z)],
    "left_front_leg:rot": [(0, Z), (0.25, [0, -30, -60]), (0.75, [0, -30, -60]), (1.0, Z)], "right_middle_front_leg:rot": [(0, Z), (0.3, [0, 20, 40]), (1.0, Z)],
    "left_middle_front_leg:rot": [(0, Z), (0.3, [0, -20, -40]), (1.0, Z)]}, pri=150)
life("spider.abdomen_pulse", "Spider Abdomen Pulse", CAT, T, ALIVE, 2.2, F, {"body1:scl": lambda u: [1 + 0.03 * wave(u), 1 + 0.03 * wave(u), 1]})
loop_state("spider.web_lurk", "Spider Lurking Motionless", CAT, T, STILL + CALM + " && q.light < 7", 6.0, F, {
    "mw_center:pos": lambda u: move(0, -1.0, 0), **{b + ":rot": (lambda u, s=(1 if b.startswith("right") else -1): [0, 0, -14 * s]) for b in SPL}}, group="spider_idle", weight=3)
F, T = f("cave_spider"), "minecraft:cave_spider"
life("cave_spider.twitchy", "Cave Spider Twitchy Legs", CAT, T, ALIVE, 0.9, F, {b + ":rot": (lambda u, i=i: [0, 0, 6 * spike(u, i / 8.0, 12) * (1 if i < 4 else -1)]) for i, b in enumerate(SPL)})
beat("cave_spider.venom_strike", "Cave Spider Venom Strike", CAT, T, event("melee_hit", ALIVE), 0.35, F, {
    "head:rot": [(0, Z), (0.06, [-25, 0, 0]), (0.14, [25, 0, 0], "in_quart"), (0.35, Z)], "mw_center:pos": [(0, Z), (0.14, move(0, 0, 2.5)), (0.35, Z)]}, pri=170)
loop_state("cave_spider.swarm_jitter", "Cave Spider Swarm Jitter", CAT, T, STILL + HUNT, 0.4, F, {"mw_center:rot": lambda u: tilt(0, 14 * wave(u), 0), "mw_center:pos": lambda u: move(0.3 * wave(u, 0.2), 0, 0)}, pri=110)

# ============================================================================ enderman
T, F = "minecraft:enderman", f("enderman")
hwalk("enderman.glide_walk", "Enderman Long Gliding Stride", T, WALKING + " && !q.is_creepy", 1.8, F, stride=24, arm_swing=8, bob=0.3, twist=3, sway=1, lean=0, right_arm=None, left_arm=None)
hwalk("enderman.rage_stalk", "Enderman Enraged Stalk", T, WALKING + " && q.is_creepy", 0.9, F, pri=101, stride=34, arm_swing=0, bob=0.8, twist=10, sway=2, lean=12, right_arm=[20, 20, 0],
      left_arm=[20, 20, 0])
loop_state("enderman.stare_tremble", "Enderman Stare Tremble", CAT, T, ALIVE + " && q.is_creepy", 0.2, F, {
    "head:rot": lambda u: [1.5 * wave(u), 1.5 * wave(u, 0.3), 1.5 * wave(u, 0.6)], "right_arm:rot": lambda u: [2 * wave(u, 0.2), 0, 3], "left_arm:rot": lambda u: [2 * wave(u, 0.7), 0, -3]},
    layer="additive", pri=80)
loop_state("enderman.carry_block", "Enderman Cradling A Block", CAT, T, ALIVE + " && q.is_carrying && !q.is_creepy", 2.4, F, {
    "right_arm:rot": lambda u: arm('r', 40 + 3 * wave(u), -6), "left_arm:rot": lambda u: arm('l', 40 + 3 * wave(u), -6), "body:rot": lambda u: tilt(-4, 0, 0)}, pri=125)
beat("enderman.vanish", "Enderman Teleport Shimmer", CAT, T, event("teleport", ALIVE), 0.5, F, {
    "mw_root:scl": [(0, [1, 1, 1]), (0.1, [0.85, 1.15, 0.85], "out_expo"), (0.25, [1.1, 0.92, 1.1]), (0.5, [1, 1, 1])], "head:rot": [(0, Z), (0.1, [0, 0, 10]), (0.25, [0, 0, -10]), (0.5, Z)]},
    pri=220, layer="reaction", events=[(0.0, "particle", {"particle": "magic_glint", "count": "18", "at": "body", "spread": "0.8"})])
loop_state("enderman.rain_flinch", "Enderman Recoiling From Rain", CAT, T, ALIVE + " && q.is_raining && q.sky_exposed", 0.5, F, {
    "right_arm:rot": lambda u: arm('r', 150, -10 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', 150, -10 + 10 * wave(u, 0.5)), "body:rot": lambda u: tilt(14, 0, 4 * wave(u, 0.25)),
    "head:rot": lambda u: [30, 0, 0]}, pri=150, layer="action")
loop_state("enderman.idle_drift", "Enderman Absent Idle", CAT, T, STILL + " && !q.is_creepy && !q.is_carrying", 7.0, F, {
    "head:rot": lambda u: [10 * wave(u, 0.3), 40 * spike(u, 0.2, 2) - 30 * spike(u, 0.7, 2), 6 * wave(u)], "right_arm:rot": lambda u: [4 * wave(u), 0, 3],
    "left_arm:rot": lambda u: [4 * wave(u, 0.5), 0, -3]})
beat("enderman.scream_jaw", "Enderman Scream", CAT, T, event("aggro", ALIVE), 1.0, F, {
    "head:rot": [(0, Z), (0.15, [-30, 0, 0], "out_expo"), (0.7, [-25, 0, 6]), (1.0, Z)], "body:rot": [(0, Z), (0.15, tilt(-10)), (1.0, Z)],
    "right_arm:rot": [(0, Z), (0.2, arm('r', 0, 40)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.2, arm('l', 0, 40)), (1.0, Z)]}, pri=170)
strike_arms("enderman.lunge_strike", "Enderman Lunging Strike", T, event("attack", ALIVE), 0.6, F, [(0, [0]), (0.18, [120, 30, 0], "out_quad"), (0.3, [40, -10, 0], "in_quart"), (0.6, [0])],
            body=[(0, Z), (0.18, tilt(-6, 20, 0)), (0.3, tilt(14, -10, 0)), (0.6, Z)])
beat("enderman.block_pickup", "Enderman Lifting A Block", CAT, T, event("break_block", ALIVE), 1.2, F, {
    "body:rot": [(0, Z), (0.4, tilt(50)), (0.8, tilt(10)), (1.2, Z)], "right_arm:rot": [(0, Z), (0.4, arm('r', 80)), (1.2, arm('r', 40))],
    "left_arm:rot": [(0, Z), (0.4, arm('l', 80)), (1.2, arm('l', 40))]}, pri=150)

# ============================================================================ blaze & ghast
T, F = "minecraft:blaze", f("blaze")
RODS = ["part%d" % i for i in range(12)]
c = mob("blaze.hover_spin", "Blaze Hovering Rod Orbit", CAT, T, 4.0, state(ALIVE + " && !q.is_charging"), layer="additive", pri=60, file=F)
for i, b in enumerate(RODS):
    ring = i // 4
    c.cycle(b, "position", lambda u, i=i, ring=ring: move(0, (1.2 if ring != 1 else -1.2) * wave(u, i / 12.0, 2), 0))
c.cycle("mw_root", "position", lambda u: move(0, 1.0 * wave(u), 0))
c = mob("blaze.ignite_frenzy", "Blaze Igniting Frenzy", CAT, T, 0.5, state(ALIVE + " && q.is_charging"), layer="additive", pri=70, file=F)
for i, b in enumerate(RODS):
    c.cycle(b, "position", lambda u, i=i: move(0.6 * cwave(u, i / 12.0), 2.5 * wave(u, i / 12.0), 0.6 * wave(u, i / 12.0)))
c.cycle("head", "rotation", lambda u: [0, 0, 4 * wave(u, 0, 2)])
c.ev(0.0, "particle", particle="ember", count="3", at="body", spread="0.5")
beat("blaze.fireball_volley", "Blaze Fireball Volley", CAT, T, event("shoot:fireball", ALIVE), 1.2, F, {
    "head:rot": [(0, Z), (0.1, [-10, 0, 0]), (0.2, Z), (0.5, [-10, 0, 0]), (0.6, Z), (0.9, [-10, 0, 0]), (1.0, Z), (1.2, Z)],
    "mw_root:pos": [(0, Z), (0.1, move(0, 0, -0.6)), (0.3, Z), (0.5, move(0, 0, -0.6)), (0.7, Z), (0.9, move(0, 0, -0.6)), (1.2, Z)]}, layer="gesture")
loop_state("blaze.smoulder_idle", "Blaze Smouldering Idle", CAT, T, ALIVE + " && q.ground_speed < 0.02 && !q.is_charging && !q.is_aggressive", 3.0, F, {
    "head:rot": lambda u: [5 * wave(u, 0.2), 40 * wave(u), 0]}, layer="overlay", pri=105)
beat("blaze.rod_flare", "Blaze Rods Flare When Struck", CAT, T, event("hurt", ALIVE), 0.6, F, {
    rod + ":pos": [(0, Z), (0.08, move(1.5 * (1 if i % 2 else -1), 1, 1.5 * (1 if i % 3 else -1)), "out_expo"), (0.6, Z)] for i, rod in enumerate(RODS)}, pri=200, layer="reaction")
beat("blaze.breathe", "Blaze Crackling Breath", CAT, T, event("vocalize", ALIVE), 1.2, F, {"head:rot": [(0, Z), (0.3, [-12, 0, 0]), (0.6, [-10, 0, 6]), (1.2, Z)],
                                                                                 "mw_root:pos": [(0, Z), (0.3, move(0, 0.8, 0)), (1.2, Z)]}, layer="gesture")
loop_state("blaze.rain_fizzle", "Blaze Fizzling In Rain", CAT, T, ALIVE + " && (q.is_raining && q.sky_exposed || q.is_in_water)", 0.3, F, {
    "head:rot": lambda u: [0, 0, 6 * wave(u)], **{r + ":pos": (lambda u, i=i: move(0, 0.5 * wave(u, i / 6.0), 0)) for i, r in enumerate(RODS[:6])}}, pri=150, layer="action")

T, F = "minecraft:ghast", f("ghast")
TENT = ["tentacle%d" % i for i in range(9)]
EYE_CENTRE = (0, 16, 0)  # the guardian eye's box hangs 16 px below its pivot (see LibraryAudit SCALE_DRIFT)
c = mob("ghast.drift", "Ghast Mournful Drift", CAT, T, 5.0, state(ALIVE + " && !q.is_charging"), layer="additive", pri=60, file=F)
for i, b in enumerate(TENT):
    c.cycle(b, "rotation", lambda u, i=i: [10 * wave(u, i / 9.0) + 5, 0, 6 * wave(u, i / 4.5)])
c.cycle("mw_root", "position", lambda u: move(0, 2 * wave(u), 0))
c.cycle("mw_root", "rotation", lambda u: tilt(2 * wave(u, 0.25), 0, 2 * wave(u)))
c = mob("ghast.charge_shot", "Ghast Inhaling To Shoot", CAT, T, 0.8, state(ALIVE + " && q.is_charging"), layer="additive", pri=70, file=F, loop="hold")
c.cycle("body", "scale", lambda u: [1 + 0.06 * u, 1 + 0.06 * u, 1 + 0.06 * u])
for i, b in enumerate(TENT):
    c.cycle(b, "rotation", lambda u, i=i: [-25 * u, 0, 8 * wave(u, i / 9.0, 2)])
beat("ghast.recoil", "Ghast Fireball Recoil", CAT, T, event("shoot:fireball", ALIVE), 0.8, F, {"mw_root:pos": [(0, Z), (0.1, move(0, 0, -3), "out_expo"), (0.8, Z)],
                                                                                "body:scl": [(0, [1.06, 1.06, 1.06]), (0.1, [0.94, 0.94, 0.94]), (0.8, [1, 1, 1])]}, pri=170)
beat("ghast.wail", "Ghast Wail", CAT, T, event("vocalize", ALIVE), 2.4, F, dict({b + ":rot": [(0, Z), (0.6, [30, 0, (-1) ** i * 10]), (1.6, [25, 0, 0]), (2.4, Z)] for i, b in enumerate(TENT)},
                                                                          **{"mw_root:rot": [(0, Z), (0.6, tilt(-8, 0, 0)), (2.4, Z)]}), layer="gesture")
beat("ghast.pained_flinch", "Ghast Pained Flinch", CAT, T, event("hurt", ALIVE), 0.9, F, dict({b + ":rot": [(0, Z), (0.1, [-50, 0, 0], "out_expo"), (0.9, Z)] for b in TENT},
                                                                                     **{"body:scl": [(0, [1, 1, 1]), (0.1, [0.9, 1.1, 0.9]), (0.9, [1, 1, 1])]}), pri=200, layer="reaction")
loop_state("ghast.sleep_float", "Ghast Dozing Float", CAT, T, ALIVE + " && q.player_distance > 24", 8.0, F, {
    "mw_root:rot": lambda u: tilt(10 + 3 * wave(u), 0, 0), **{b + ":rot": (lambda u, i=i: [40 + 4 * wave(u, i / 9.0), 0, 0]) for i, b in enumerate(TENT)}}, pri=105)
life("ghast.tear_quiver", "Ghast Quivering Sob", CAT, T, ALIVE + " && q.player_distance <= 24 && !q.is_charging", 1.6, F, {"body:rot": lambda u: [0.8 * spike(u, 0.2, 6, 2), 0, 0]})

# ============================================================================ slime & magma cube
T, F = "minecraft:slime", f("slime")
loop_state("slime.jiggle", "Slime Jelly Jiggle", CAT, T, ALIVE + " && q.is_on_ground", 0.9, F, {"mw_root:scl": lambda u: [1 + 0.05 * wave(u), 1 - 0.05 * wave(u), 1 + 0.05 * wave(u, 0.1)]}, layer="additive", pri=60)
beat("slime.splat_land", "Slime Splat Landing", CAT, T, event("land", ALIVE), 0.5, F, {"mw_root:scl": [(0, [1, 1, 1]), (0.06, [1.35, 0.6, 1.35], "out_expo"), (0.2, [0.9, 1.15, 0.9]), (0.32, [1.05, 0.95, 1.05]), (0.5, [1, 1, 1])],
                                                                              "right_eye:pos": [(0, Z), (0.06, move(0, -1, 0)), (0.5, Z)], "left_eye:pos": [(0, Z), (0.06, move(0, -1, 0)), (0.5, Z)]}, pri=170,
     events=[(0.0, "particle", {"particle": "splash", "count": "6", "at": "feet", "spread": "0.4"})])
beat("slime.crouch_spring", "Slime Coiled Spring", CAT, T, event("jump", ALIVE), 0.4, F, {"mw_root:scl": [(0, [1.15, 0.85, 1.15]), (0.08, [0.8, 1.35, 0.8], "out_expo"), (0.4, [1, 1, 1])]}, pri=160)
loop_state("slime.eye_wander", "Slime Wandering Eyes", CAT, T, ALIVE, 3.0, F, {"right_eye:pos": lambda u: move(0.4 * wave(u), 0.3 * wave(u, 0.25), 0), "left_eye:pos": lambda u: move(0.4 * wave(u), 0.3 * wave(u, 0.25), 0),
                                                                          "mouth:pos": lambda u: move(0, -0.6 * spike(u, 0.6, 6), 0)}, layer="additive", pri=62)
beat("slime.gulp", "Slime Gulping Strike", CAT, T, event("melee_hit", ALIVE), 0.5, F, {"mw_root:scl": [(0, [1, 1, 1]), (0.1, [1.2, 1.1, 0.8]), (0.25, [0.9, 0.95, 1.2]), (0.5, [1, 1, 1])],
                                                                               "mouth:pos": [(0, Z), (0.1, move(0, -1.5, -0.5)), (0.25, Z)]}, pri=170)
loop_state("slime.dissolve_wobble", "Slime Weakened Wobble", CAT, T, ALIVE + " && q.health < 0.35", 0.5, F, {"mw_root:scl": lambda u: [1 + 0.1 * wave(u), 1 - 0.1 * wave(u, 0.25), 1 + 0.1 * wave(u, 0.5)]},
           layer="additive", pri=64)
T, F = "minecraft:magma_cube", f("magma_cube")
CUBES = ["cube%d" % i for i in range(8)]
beat("magma_cube.accordion_launch", "Magma Cube Accordion Launch", CAT, T, event("jump", ALIVE), 0.6, F, {
    cb + ":pos": [(0, move(0, -0.3 * i, 0)), (0.1, move(0, 1.2 * i, 0), "out_expo"), (0.4, move(0, 0.4 * i, 0)), (0.6, Z)] for i, cb in enumerate(CUBES)}, pri=160)
beat("magma_cube.slam", "Magma Cube Molten Slam", CAT, T, event("land", ALIVE), 0.5, F, {
    cb + ":pos": [(0, Z), (0.05, move(0, -0.25 * i, 0), "out_expo"), (0.25, move(0, 0.1 * i, 0)), (0.5, Z)] for i, cb in enumerate(CUBES)}, pri=170,
     events=[(0.0, "particle", {"particle": "ember", "count": "10", "at": "feet", "spread": "0.6"})])
loop_state("magma_cube.core_pulse", "Magma Cube Core Pulse", CAT, T, ALIVE, 1.4, F, {"inside_cube:scl": lambda u: [1 + 0.08 * wave(u)] * 3}, layer="additive", pri=60)
loop_state("magma_cube.coil_idle", "Magma Cube Coiling", CAT, T, ALIVE + " && q.is_on_ground && q.ground_speed < 0.01", 2.0, F, {
    cb + ":pos": (lambda u, i=i: move(0, -0.15 * i * (1 + wave(u)) * 0.5, 0)) for i, cb in enumerate(CUBES)}, pri=105)
beat("magma_cube.sear_strike", "Magma Cube Searing Strike", CAT, T, event("melee_hit", ALIVE), 0.4, F, {
    cb + ":rot": [(0, Z), (0.1, [0, 20 * (1 if i % 2 else -1), 0]), (0.4, Z)] for i, cb in enumerate(CUBES)}, pri=172)
loop_state("magma_cube.lava_bathe", "Magma Cube Bathing In Lava", CAT, T, ALIVE + " && q.is_in_lava", 3.0, F, {
    cb + ":rot": (lambda u, i=i: [0, 15 * wave(u, i / 8.0), 0]) for i, cb in enumerate(CUBES)}, pri=110)

# ============================================================================ guardians
for T, sp, label, elder in (("minecraft:guardian", "guardian", "Guardian", False), ("minecraft:elder_guardian", "elder_guardian", "Elder Guardian", True)):
    F = f(sp)
    SPK = ["spike%d" % i for i in range(12)]
    if not elder:
        c = mob(sp + ".tail_swim", label + " Tail Swim", CAT, T, 1.0, state(ALIVE + " && q.is_in_water && q.ground_speed >= 0.02"), layer="base", file=F)
        c.cycle("tail0", "rotation", lambda u: [0, 14 * wave(u), 0])
        c.cycle("tail1", "rotation", lambda u: [0, 24 * wave(u, 0.15), 0])
        c.cycle("tail2", "rotation", lambda u: [0, 32 * wave(u, 0.3), 0])
        c.cycle("mw_center", "rotation", lambda u: tilt(0, 0, 3 * wave(u, 0.25)))
        loop_state(sp + ".laser_lock", label + " Laser Lock", CAT, T, ALIVE + " && q.is_attacking", 0.5, F, {
            "eye:scl": lambda u: [1 + 0.12 * wave(u, 0, 2), 1 - 0.1 * wave(u, 0, 2), 1], "mw_center:rot": lambda u: tilt(0, 0, 0.8 * wave(u, 0, 4)), "tail2:rot": lambda u: [0, 8 * wave(u, 0, 3), 0]},
            pri=140, layer="overlay")
        beat(sp + ".spike_bristle", label + " Spike Bristle", CAT, T, event("hurt", ALIVE), 0.8, F, {s_ + ":scl": [(0, [1, 1, 1]), (0.1, [1, 1.6, 1], "out_expo"), (0.8, [1, 1, 1])] for s_ in SPK},
             pri=200, layer="reaction")
        life(sp + ".eye_dart", label + " Eye Darting", CAT, T, ALIVE + " && !q.is_attacking", 1.8, F, {"eye:pos": lambda u: move(0.6 * (1 if wave(u) > 0.3 else (-1 if wave(u) < -0.3 else 0)), 0.3 * wave(u, 0.3), 0)})
        loop_state(sp + ".beached_flop", label + " Beached Flop", CAT, T, ALIVE + " && !q.is_in_water", 0.6, F, {
            "mw_center:rot": lambda u: tilt(0, 0, 18 * wave(u)), "mw_center:pos": lambda u: move(0, 1.5 * max(0, wave(u, 0, 2)), 0), "tail2:rot": lambda u: [0, 40 * wave(u, 0.3), 0]}, pri=130)
    else:
        # the elder is a slow, pitching leviathan: undulation travels with a long lag and the body rises and falls with each stroke
        c = mob(sp + ".tail_swim", label + " Ancient Glide", CAT, T, 2.0, state(ALIVE + " && q.is_in_water && q.ground_speed >= 0.02"), layer="base", file=F)
        c.cycle("tail0", "rotation", lambda u: [4 * wave(u, 0.1), 8 * wave(u), 0])
        c.cycle("tail1", "rotation", lambda u: [6 * wave(u, 0.35), 14 * wave(u, 0.3), 0])
        c.cycle("tail2", "rotation", lambda u: [8 * wave(u, 0.6), 20 * wave(u, 0.55), 0])
        c.cycle("mw_center", "rotation", lambda u: tilt(4 * wave(u, 0.15), 0, 0))
        c.cycle("mw_center", "position", lambda u: move(0, 1.2 * wave(u, 0.4), 0))
        loop_state(sp + ".laser_lock", label + " Withering Gaze", CAT, T, ALIVE + " && q.is_attacking", 1.6, F, {
            "eye:scl": lambda u: [1 + 0.3 * min(1, u * 1.4), 1 + 0.3 * min(1, u * 1.4), 1],
            "eye:pos": lambda u: [0, -EYE_CENTRE[1] * 0.3 * min(1, u * 1.4), 0], "mw_center:rot": lambda u: tilt(-6 * min(1, u * 2), 0, 0)}, pri=140, layer="overlay",
            loop="hold")
        beat(sp + ".spike_bristle", label + " Rippling Spikes", CAT, T, event("hurt", ALIVE), 1.4, F, {
            s_ + ":scl": [(0, [1, 1, 1]), (0.05 + 0.07 * i, [1, 1.8, 1], "out_expo"), (0.5 + 0.07 * i, [1, 1, 1]), (1.4, [1, 1, 1])] for i, s_ in enumerate(SPK)}, pri=200, layer="reaction")
        life(sp + ".eye_dart", label + " Eye Slow Sweep", CAT, T, ALIVE + " && !q.is_attacking", 6.0, F, {"eye:pos": lambda u: move(0.8 * wave(u), 0.4 * wave(u, 0.25, 2), 0)})
        loop_state(sp + ".beached_flop", label + " Stranded Heave", CAT, T, ALIVE + " && !q.is_in_water", 2.4, F, {
            "mw_center:rot": lambda u: tilt(6 * wave(u, 0.25), 0, 8 * wave(u)), "tail0:rot": lambda u: [10 * wave(u, 0.5), 0, 0], "tail2:rot": lambda u: [0, 20 * wave(u, 0.3), 0]}, pri=130)
T, F = "minecraft:guardian", f("guardian")
loop_state("guardian.patrol_hover", "Guardian Patrol Hover", CAT, T, ALIVE + " && q.is_in_water && q.ground_speed < 0.02 && !q.is_attacking", 3.0, F, {
    "mw_center:pos": lambda u: move(0, 0.6 * wave(u), 0), "tail1:rot": lambda u: [0, 8 * wave(u, 0, 2), 0]}, pri=99, layer="base")
T, F = "minecraft:elder_guardian", f("elder_guardian")
GLARE = [(0, [1, 1, 1]), (0.4, [1.4, 1.4, 1]), (1.6, [1.4, 1.4, 1]), (2.0, [1, 1, 1])]
beat("elder_guardian.curse_glare", "Elder Guardian Curse Glare", CAT, T, event("vocalize", ALIVE), 2.0, F, {
    "eye:scl": GLARE, "eye:pos": anchored(GLARE, EYE_CENTRE), "mw_center:rot": [(0, Z), (0.4, tilt(-6, 0, 0)), (1.6, tilt(-6, 0, 0)), (2.0, Z)]}, pri=150)

# ============================================================================ phantom
T, F = "minecraft:phantom", f("phantom")
c = mob("phantom.glide", "Phantom Gliding Wingbeats", CAT, T, 1.6, state(ALIVE + " && q.vertical_speed > -0.3"), layer="base", file=F)
c.cycle("left_wing_base", "rotation", lambda u: [0, 0, 20 * wave(u)])
c.cycle("left_wing_tip", "rotation", lambda u: [0, 0, 25 * wave(u, 0.12)])
c.cycle("right_wing_base", "rotation", lambda u: [0, 0, -20 * wave(u)])
c.cycle("right_wing_tip", "rotation", lambda u: [0, 0, -25 * wave(u, 0.12)])
c.cycle("tail_base", "rotation", lambda u: [5 * wave(u, 0.3), 0, 0])
c.cycle("tail_tip", "rotation", lambda u: [8 * wave(u, 0.45), 0, 0])
c = mob("phantom.swoop", "Phantom Swooping Dive", CAT, T, 0.5, state(ALIVE + " && q.vertical_speed <= -0.3"), layer="base", pri=101, file=F)
c.cycle("left_wing_base", "rotation", lambda u: [0, 0, -30])
c.cycle("left_wing_tip", "rotation", lambda u: [0, 0, -20 + 4 * wave(u, 0, 3)])
c.cycle("right_wing_base", "rotation", lambda u: [0, 0, 30])
c.cycle("right_wing_tip", "rotation", lambda u: [0, 0, 20 - 4 * wave(u, 0, 3)])
c.cycle("tail_base", "rotation", lambda u: [-10, 0, 0])
c.cycle("head", "rotation", lambda u: [15, 0, 0])
life("phantom.circling_bank", "Phantom Circling Bank", CAT, T, ALIVE + " && math.abs(q.turn_rate) > 3", 2.0, F, {"mw_root:rot": lambda u: tilt(6 + 3 * wave(u), 4 * wave(u, 0.25), 25 + 5 * wave(u))}, pri=62)
beat("phantom.bite", "Phantom Bite", CAT, T, event("melee_hit", ALIVE), 0.5, F, {"head:rot": [(0, Z), (0.1, [-30, 0, 0]), (0.2, [20, 0, 0], "in_quart"), (0.5, Z)],
                                                                       "left_wing_base:rot": [(0, Z), (0.2, [0, 0, 50]), (0.5, Z)], "right_wing_base:rot": [(0, Z), (0.2, [0, 0, -50]), (0.5, Z)]}, pri=170)
beat("phantom.screech", "Phantom Screech", CAT, T, event("vocalize", ALIVE), 1.2, F, {"head:rot": [(0, Z), (0.3, [-30, 0, 0]), (0.9, [-25, 0, 6]), (1.2, Z)],
                                                                             "tail_tip:rot": [(0, Z), (0.3, [-20, 0, 0]), (1.2, Z)]}, layer="gesture")
loop_state("phantom.sun_scorch", "Phantom Scorching At Dawn", CAT, T, ALIVE + " && q.is_on_fire", 0.3, F, {
    "left_wing_base:rot": lambda u: [0, 0, 40 * wave(u)], "right_wing_base:rot": lambda u: [0, 0, -40 * wave(u)], "body:rot": lambda u: [0, 0, 10 * wave(u, 0.25)]}, pri=150, layer="action")
beat("phantom.wing_pump", "Phantom Climbing Wing Pump", CAT, T, event("jump"), 0.6, F, {
    "left_wing_base:rot": [(0, Z), (0.15, [0, 0, 50]), (0.35, [0, 0, -40]), (0.6, Z)], "right_wing_base:rot": [(0, Z), (0.15, [0, 0, -50]), (0.35, [0, 0, 40]), (0.6, Z)],
    "left_wing_tip:rot": [(0, Z), (0.2, [0, 0, 40]), (0.4, [0, 0, -30]), (0.6, Z)], "right_wing_tip:rot": [(0, Z), (0.2, [0, 0, -40]), (0.4, [0, 0, 30]), (0.6, Z)]}, layer="gesture")
beat("phantom.death_spiral", "Phantom Death Spiral", CAT, T, event("death"), 1.0, F, {"mw_root:rot": [(0, Z), (1.0, tilt(40, 0, 540), "in_quad")],
                                                                                 "left_wing_base:rot": [(0, Z), (1.0, [0, 0, -60])], "right_wing_base:rot": [(0, Z), (1.0, [0, 0, 60])]}, pri=300)

# ============================================================================ ravager
T, F = "minecraft:ravager", f("ravager")
gait("ravager.lumber", "Ravager Lumbering March", CAT, T, WALKING + " && q.ground_speed < 0.15", 1.4, F, gait="walk", stride=20, duty=0.66, bob=1.0, pitch=1.5, roll=3.5, yaw=2.5, front_scale=1.2)
gait("ravager.charge", "Ravager Charging Gallop", CAT, T, WALKING + " && q.ground_speed >= 0.15", 0.7, F, pri=101, gait="gallop", stride=34, duty=0.45, bob=2.6, pitch=5, roll=1.5, snap=0.15)
loop_state("ravager.roar", "Ravager Roar", CAT, T, ALIVE + " && q.is_roaring", 1.0, F, {
    "neck:rot": lambda u: [-25, 0, 6 * wave(u, 0, 3)], "mouth:rot": lambda u: [50, 0, 0], "head:rot": lambda u: [-10, 0, 0], "mw_center:rot": lambda u: tilt(-6, 0, 2 * wave(u, 0, 4))}, pri=170,
    layer="action")
loop_state("ravager.stunned", "Ravager Stunned And Reeling", CAT, T, ALIVE + " && q.is_stunned", 1.2, F, {
    "neck:rot": lambda u: [30, 20 * wave(u), 0], "head:rot": lambda u: [10, 0, 20 * wave(u, 0.25)], "mw_center:rot": lambda u: tilt(4, 0, 6 * wave(u)), "mouth:rot": lambda u: [20, 0, 0]}, pri=165,
    layer="action")
beat("ravager.horn_toss", "Ravager Horn Toss", CAT, T, event("melee_hit", ALIVE), 0.8, F, {
    "neck:rot": [(0, Z), (0.2, [30, 0, 0], "out_quad"), (0.35, [-30, 0, 0], "in_quart"), (0.8, Z)], "head:rot": [(0, Z), (0.2, [15, 0, 0]), (0.35, [-20, 0, 0]), (0.8, Z)],
    "mouth:rot": [(0, Z), (0.3, [30, 0, 0]), (0.8, Z)]}, pri=175, events=[(0.35, "whoosh", {"weight": "heavy"})])
loop_state("ravager.snort_idle", "Ravager Snorting Idle", CAT, T, STILL + " && !q.is_roaring && !q.is_stunned", 2.6, F, {
    "neck:rot": lambda u: [8 + 6 * spike(u, 0.3, 4), 14 * wave(u, 0, 0.5), 0], "mouth:rot": lambda u: [8 * spike(u, 0.3, 4), 0, 0]})
beat("ravager.stomp_challenge", "Ravager Challenge Stomp", CAT, T, event("notice", ALIVE), 1.4, F, {
    "right_front_leg:rot": [(0, Z), (0.3, [-40, 0, 0]), (0.45, [6, 0, 0], "in_quart"), (0.7, [-35, 0, 0]), (0.85, [6, 0, 0], "in_quart"), (1.4, Z)],
    "neck:rot": [(0, Z), (0.45, [15, 0, 0]), (1.4, Z)]}, pri=150, events=[(0.45, "stomp", {"strength": "0.7"}), (0.85, "stomp", {"strength": "0.7"})])
life("ravager.jaw_drool", "Ravager Slack Jaw", CAT, T, ALIVE + " && !q.is_roaring", 3.0, F, {"mouth:rot": lambda u: [5 + 3 * wave(u), 0, 0]})

# ============================================================================ hoglin & zoglin
for T, sp, label, rot in (("minecraft:hoglin", "hoglin", "Hoglin", False), ("minecraft:zoglin", "zoglin", "Zoglin", True)):
    F = f(sp)
    gait(sp + ".trot", label + (" Rotting Trot" if rot else " Bristling Trot"), CAT, T, WALKING + CALM, 1.0 if not rot else 1.2, F, gait="trot" if not rot else "amble", stride=26, duty=0.5,
         bob=1.0, pitch=2, roll=1.5 if not rot else 3.5, snap=0.0 if not rot else 0.3, yaw=3 if not rot else 0, lift=0 if not rot else 12, front_scale=1.25 if not rot else 1.0)
    gait(sp + ".rampage", label + " Rampage", CAT, T, WALKING + HUNT, 0.55, F, pri=101, gait="gallop" if not rot else "bound", stride=38, duty=0.4, bob=2.4, pitch=6, roll=1, yaw=0 if not rot else 4, snap=0.0 if not rot else 0.3, front_scale=1.0 if not rot else 1.3)
    beat(sp + ".gore_toss", label + " Gore Toss", CAT, T, event("melee_hit", ALIVE), 0.6 if not rot else 0.7, F, {
        "head:rot": [(0, Z), (0.15, [40, 0, 0], "out_quad"), (0.28, [-40, 0, 0 if not rot else 20], "in_quart"), (0.6 if not rot else 0.7, Z)],
        "mw_center:rot": [(0, Z), (0.15, tilt(6, 0, 0)), (0.28, tilt(-8, 0, 0)), (0.6 if not rot else 0.7, Z)]}, pri=175)
    life(sp + ".ear_flick", label + " Ear Flick", CAT, T, ALIVE, 2.0 if not rot else 3.6, F, {"left_ear:rot": lambda u: [0, 0, -20 * spike(u, 0.1, 8)], "right_ear:rot": lambda u, r_=rot: [0, 0, 20 * spike(u, 0.6 if not r_ else 0.15, 8)]})
F, T = f("hoglin"), "minecraft:hoglin"
loop_state("hoglin.root_crimson", "Hoglin Rooting For Fungus", CAT, T, STILL + CALM, 1.4, F, {"head:rot": lambda u: [40 + 10 * max(0, wave(u, 0, 3)), 16 * wave(u), 0]}, group="hoglin_idle", weight=3)
loop_state("hoglin.fungus_fear", "Hoglin Backing From Warped Fungus", CAT, T, ALIVE + " && q.trait_nervous > 0.7 && q.dimension == 'the_nether' && q.ground_speed > 0.05 && !q.is_aggressive", 0.8, F, {
    "head:rot": lambda u: [-20, 20 * wave(u), 0], "mw_center:rot": lambda u: tilt(-8, 0, 0)}, pri=110)
beat("hoglin.snort", "Hoglin Snort", CAT, T, event("vocalize", ALIVE), 0.7, F, {"head:rot": [(0, Z), (0.15, [-14, 0, 0]), (0.25, [8, 0, 0], "in_quart"), (0.7, Z)]}, layer="gesture",
     events=[(0.25, "breath", {"strength": "1"})])
loop_state("hoglin.zombify_shudder", "Hoglin Overworld Shudder", CAT, T, ALIVE + " && q.dimension != 'the_nether'", 0.25, F, {"mw_center:rot": lambda u: tilt(0, 0, 2 * wave(u)), "head:rot": lambda u: [0, 3 * wave(u, 0.3), 0]},
           layer="additive", pri=80)
F, T = f("zoglin"), "minecraft:zoglin"
loop_state("zoglin.twitch_idle", "Zoglin Rotting Twitch", CAT, T, STILL, 2.4, F, {"head:rot": lambda u: [30, 0, 25 * spike(u, 0.3, 12)], "mw_center:rot": lambda u: tilt(0, 0, 5 * spike(u, 0.7, 12))})

# ============================================================================ warden
T, F = "minecraft:warden", f("warden")
hwalk_w = mob("warden.heavy_walk", "Warden Ponderous Walk", CAT, T, 2.2, state(WALKING + " && q.attack_tick < 0.5", exit_delay=0.2), layer="base", file=F, **driven(2.2))
hwalk_w.cycle("right_leg", "rotation", lambda u: leg('r', 24 * cwave(u)))
hwalk_w.cycle("left_leg", "rotation", lambda u: leg('l', -24 * cwave(u)))
hwalk_w.cycle("right_arm", "rotation", lambda u: arm('r', -16 * cwave(u), 6))
hwalk_w.cycle("left_arm", "rotation", lambda u: arm('l', 16 * cwave(u), 6))
hwalk_w.cycle("body", "rotation", lambda u: tilt(6, 6 * cwave(u), 0))
hwalk_w.cycle("mw_root", "position", lambda u: move(0, -0.9 * (1 + cwave(u, 0, 2)) * 0.5, 0))
hwalk_w.cycle("mw_root", "rotation", lambda u: tilt(0, 0, 3 * wave(u)))
hwalk_w.ev(0.0, "stomp", strength="0.3")
hwalk_w.ev(1.1, "stomp", strength="0.3")
c = mob("warden.angry_stride", "Warden Furious Stride", CAT, T, 1.3, state(WALKING + " && q.attack_tick >= 0.5", exit_delay=0.2), layer="base", pri=101, file=F, **driven(1.3))
biped(c, stride=36, arm_swing=30, arm_out=10, bob=1.6, twist=12, sway=4, lean=14, foot_events=True)
c.bones.pop("head", None)
loop_state("warden.sniff", "Warden Sniffing The Air", CAT, T, ALIVE + " && q.is_sniffing", 1.0, F, {"head:rot": lambda u: [-20 + 6 * spike(u, 0, 3, 3), 25 * wave(u, 0, 0.5), 0],
                                                                                       "body:rot": lambda u: tilt(-10, 0, 0)}, pri=150, layer="additive")
loop_state("warden.tendril_quiver", "Warden Tendrils Quiver", CAT, T, ALIVE, 0.4, F, {
    "left_tendril:rot": lambda u: [8 * wave(u), 0, 0], "right_tendril:rot": lambda u: [8 * wave(u, 0.3), 0, 0]}, layer="additive", pri=60)
life("warden.heartbeat", "Warden Soul Heartbeat", CAT, T, ALIVE, 1.0, F, {"left_ribcage:scl": lambda u: [1 + 0.06 * spike(u, 0, 6) + 0.03 * spike(u, 0.18, 6)] * 3,
                                                                      "right_ribcage:scl": lambda u: [1 + 0.06 * spike(u, 0, 6) + 0.03 * spike(u, 0.18, 6)] * 3})
loop_state("warden.sonic_charge", "Warden Sonic Boom Charge", CAT, T, ALIVE + " && q.is_charging", 1.6, F, {
    "body:rot": lambda u: tilt(-25 * min(1, u * 1.5) + 40 * max(0, u - 0.7) / 0.3, 0, 0), "right_arm:rot": lambda u: arm('r', 0, 40 * min(1, u * 2)),
    "left_arm:rot": lambda u: arm('l', 0, 40 * min(1, u * 2)), "head:rot": lambda u: [-30 * min(1, u * 1.5), 0, 0], "left_ribcage:rot": lambda u: [0, -30 * min(1, u * 2), 0],
    "right_ribcage:rot": lambda u: [0, 30 * min(1, u * 2), 0]}, pri=200, layer="action", min_time=1.0, loop="hold")
beat("warden.smash", "Warden Overhead Smash", CAT, T, event("attack", ALIVE), 0.9, F, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', 170, 10), "out_quad"), (0.45, arm('r', 60), "in_quart"), (0.9, Z)], "left_arm:rot": [(0, Z), (0.3, arm('l', 170, 10), "out_quad"), (0.45, arm('l', 60), "in_quart"), (0.9, Z)],
    "body:rot": [(0, Z), (0.3, tilt(-14)), (0.45, tilt(22)), (0.9, Z)]}, pri=180, events=[(0.45, "stomp", {"strength": "1"}), (0.45, "shake", {"intensity": "0.5", "duration": "0.4"})])
beat("warden.roar_flex", "Warden Roar Ribcage Flex", CAT, T, event("aggro", ALIVE), 2.0, F, {
    "left_ribcage:rot": [(0, Z), (0.4, [0, -40, 0], "out_expo"), (1.6, [0, -40, 0]), (2.0, Z)], "right_ribcage:rot": [(0, Z), (0.4, [0, 40, 0], "out_expo"), (1.6, [0, 40, 0]), (2.0, Z)],
    "head:rot": [(0, Z), (0.4, [-35, 0, 0]), (1.6, [-30, 0, 0]), (2.0, Z)]}, pri=160, layer="gesture")
loop_state("warden.listen_still", "Warden Listening Still", CAT, T, STILL + " && !q.is_sniffing && q.attack_tick < 0.3", 5.0, F, {
    "head:rot": lambda u: [10, 30 * (1 if wave(u) > 0.5 else (-1 if wave(u) < -0.5 else 0)), 10 * wave(u)], "left_tendril:rot": lambda u: [-10, 0, 0], "right_tendril:rot": lambda u: [-10, 0, 0]})
loop_state("warden.emerge_struggle", "Warden Clawing Up From The Deep Dark", CAT, T, ALIVE + " && q.is_emerging", 1.0, F, {
    "right_arm:rot": lambda u: arm('r', 150 + 20 * wave(u), 20), "left_arm:rot": lambda u: arm('l', 150 + 20 * wave(u, 0.5), 20)}, layer="additive", pri=90)
loop_state("warden.burrow_heave", "Warden Burrowing Heave", CAT, T, ALIVE + " && q.is_digging", 1.0, F, {"body:rot": lambda u: tilt(30 + 10 * wave(u), 0, 6 * wave(u, 0.25))}, layer="additive", pri=90)
beat("warden.sense_vibration", "Warden Senses A Vibration", CAT, T, event("notice", ALIVE), 0.8, F, {
    "head:rot": [(0, Z), (0.1, [-10, "q.event_dir * 0.5", 0], "out_expo"), (0.8, [0, "q.event_dir * 0.5", 0])], "left_tendril:rot": [(0, Z), (0.1, [-30, 0, 0]), (0.8, Z)],
    "right_tendril:rot": [(0, Z), (0.1, [-30, 0, 0]), (0.8, Z)]}, pri=150, layer="gesture")

# ============================================================================ wither
T, F = "minecraft:wither", f("wither")
loop_state("wither.heads_scan", "Wither Heads Scanning", CAT, T, ALIVE + " && !q.invulnerable", 3.0, F, {
    "left_head:rot": lambda u: [10 * wave(u, 0.2), 40 * wave(u), 0], "right_head:rot": lambda u: [10 * wave(u, 0.6), -40 * wave(u, 0.35), 0]}, layer="additive", pri=60)
loop_state("wither.spawn_charge", "Wither Gathering Power", CAT, T, ALIVE + " && q.invulnerable", 1.0, F, {
    "ribcage:scl": lambda u: [1 + 0.08 * wave(u, 0, 2)] * 3, "center_head:rot": lambda u: [-20, 0, 6 * wave(u, 0, 4)], "left_head:rot": lambda u: [-20, -20, 10 * wave(u, 0.3, 4)],
    "right_head:rot": lambda u: [-20, 20, -10 * wave(u, 0.6, 4)], "mw_root:pos": lambda u: move(0.2 * wave(u, 0, 5), 0, 0)}, pri=200, layer="overlay")
loop_state("wither.armored_phase", "Wither Armored Hunch", CAT, T, ALIVE + " && q.is_powered", 2.0, F, {
    "shoulders:rot": lambda u: [12, 0, 0], "tail:rot": lambda u: [30 + 6 * wave(u), 0, 0], "ribcage:rot": lambda u: [14, 0, 0]}, layer="additive", pri=70)
life("wither.tail_coil", "Wither Spine Tail Coil", CAT, T, ALIVE, 2.4, F, {"tail:rot": lambda u: [10 * wave(u), 0, 14 * wave(u, 0.25)], "ribcage:rot": lambda u: [3 * wave(u, 0.1), 0, 0]})
beat("wither.skull_barrage", "Wither Skull Barrage", CAT, T, event("shoot:skull", ALIVE), 0.9, F, {
    "center_head:rot": [(0, Z), (0.1, [-12, 0, 0]), (0.2, [6, 0, 0]), (0.9, Z)], "left_head:rot": [(0, Z), (0.35, [-12, 0, 0]), (0.45, [6, 0, 0]), (0.9, Z)],
    "right_head:rot": [(0, Z), (0.6, [-12, 0, 0]), (0.7, [6, 0, 0]), (0.9, Z)]}, layer="gesture")
beat("wither.shriek", "Wither Shriek", CAT, T, event("vocalize", ALIVE), 1.6, F, {
    "center_head:rot": [(0, Z), (0.3, [-35, 0, 0]), (1.2, [-30, 0, 0]), (1.6, Z)], "left_head:rot": [(0, Z), (0.35, [-30, -25, 0]), (1.2, [-25, -25, 0]), (1.6, Z)],
    "right_head:rot": [(0, Z), (0.4, [-30, 25, 0]), (1.2, [-25, 25, 0]), (1.6, Z)], "shoulders:rot": [(0, Z), (0.3, [-10, 0, 0]), (1.6, Z)]}, pri=150, layer="gesture")
beat("wither.struck_recoil", "Wither Struck Recoil", CAT, T, event("hurt", ALIVE), 0.8, F, {"mw_root:rot": [(0, Z), (0.08, [-10, 0, "q.hurt_dir > 0 ? -6 : 6"], "out_expo"), (0.8, Z)],
                                                                                    "tail:rot": [(0, Z), (0.1, [40, 0, 0]), (0.8, Z)]}, pri=200, layer="reaction")
beat("wither.death_tremor", "Wither Death Tremor", CAT, T, event("death"), 2.0, F, {"mw_root:pos": [(0, Z)] + [(0.1 * i, move(0.5 * (-1) ** i, 0, 0.5 * (-1) ** (i // 2))) for i in range(1, 19)] + [(2.0, Z)],
                                                                             "ribcage:scl": [(0, [1, 1, 1]), (1.8, [1.25, 1.25, 1.25], "in_quad"), (2.0, [1.25, 1.25, 1.25])]}, pri=300)
loop_state("wither.hover_drift", "Wither Hovering Drift", CAT, T, ALIVE + " && !q.invulnerable && q.ground_speed < 0.03", 4.0, F, {"mw_root:pos": lambda u: move(0, 1.2 * wave(u), 0),
                                                                                                                         "mw_root:rot": lambda u: tilt(0, 0, 2 * wave(u, 0.25))}, pri=105)

# ============================================================================ shulker
T, F = "minecraft:shulker", f("shulker")
loop_state("shulker.lid_flutter", "Shulker Lid Flutter", CAT, T, ALIVE, 2.6, F, {"lid:pos": lambda u: move(0, 0.3 * spike(u, 0.2, 6), 0), "lid:rot": lambda u: [0, 4 * spike(u, 0.2, 6), 0]}, layer="additive", pri=60)
beat("shulker.snap_shut", "Shulker Snaps Shut", CAT, T, event("hurt", ALIVE), 0.6, F, {"lid:pos": [(0, Z), (0.05, move(0, -2, 0), "out_expo"), (0.6, Z)], "head:pos": [(0, Z), (0.05, move(0, -1.5, 0)), (0.6, Z)]},
     pri=200, layer="reaction")
beat("shulker.blink_out", "Shulker Teleport Blink", CAT, T, event("teleport", ALIVE), 0.5, F, {"mw_root:scl": [(0, [1, 1, 1]), (0.1, [0.7, 1.2, 0.7], "out_expo"), (0.3, [1.1, 0.9, 1.1]), (0.5, [1, 1, 1])]},
     pri=210, layer="reaction")
beat("shulker.bullet_spit", "Shulker Bullet Spit", CAT, T, event("shoot:bullet", ALIVE), 0.6, F, {"lid:pos": [(0, Z), (0.15, move(0, 3, 0), "out_quad"), (0.3, move(0, 2, 0)), (0.6, Z)],
                                                                                   "head:rot": [(0, Z), (0.15, [-14, 0, 0]), (0.6, Z)]}, layer="gesture")
loop_state("shulker.peek_wary", "Shulker Wary Peek", CAT, T, ALIVE + " && q.player_distance < 6", 2.0, F, {"head:rot": lambda u: [0, 40 * wave(u), 0], "head:pos": lambda u: move(0, 0.4 * wave(u, 0, 2), 0)},
           layer="additive", pri=64)
beat("shulker.dust_off", "Shulker Shell Shudder", CAT, T, event("vocalize", ALIVE), 0.8, F, {"base:rot": [(0, Z), (0.1, [0, 6, 0]), (0.2, [0, -6, 0]), (0.3, [0, 4, 0]), (0.8, Z)]}, layer="gesture")

# ============================================================================ silverfish & endermite
for T, sp, label, n, amp in (("minecraft:silverfish", "silverfish", "Silverfish", 7, 18), ("minecraft:endermite", "endermite", "Endermite", 4, 26)):
    F = f(sp)
    c = mob(sp + ".slither", label + " Slither", CAT, T, 0.5 if sp == "silverfish" else 0.35, state(WALKING), layer="base", file=F)
    for i in range(n):
        c.cycle("segment%d" % i, "rotation", lambda u, i=i: [0, amp * wave(u, i / float(n)), 0])
    if sp == "silverfish":
        loop_state(sp + ".antennae_feel", label + " Feeling About", CAT, T, STILL, 1.4, F, {"segment0:rot": lambda u: [8 * wave(u), 20 * wave(u, 0.25), 0], "segment1:rot": lambda u: [0, -8 * wave(u, 0.35), 0]})
        beat(sp + ".nip", label + " Nip", CAT, T, event("melee_hit", ALIVE), 0.3, F, {"segment0:rot": [(0, Z), (0.08, [-20, 0, 0]), (0.15, [20, 0, 0]), (0.3, Z)],
                                                                                    "mw_center:pos": [(0, Z), (0.15, move(0, 0, 1.5)), (0.3, Z)]}, pri=170)
    else:
        loop_state(sp + ".antennae_feel", label + " Restless Wriggle", CAT, T, STILL, 0.6, F, {"segment%d:rot" % i: (lambda u, i=i: [0, 14 * wave(u, i * 0.2, 2), 6 * wave(u, i * 0.1)]) for i in range(n)})
        beat(sp + ".nip", label + " Hopping Nip", CAT, T, event("melee_hit", ALIVE), 0.35, F, {"mw_center:pos": [(0, Z), (0.1, move(0, 1.2, 0.5), "out_quad"), (0.2, move(0, 0, 1.2)), (0.35, Z)],
                                                                                            "segment3:rot": [(0, Z), (0.1, [25, 0, 0]), (0.35, Z)]}, pri=170)
F, T = f("silverfish"), "minecraft:silverfish"
loop_state("silverfish.burrow", "Silverfish Burrowing Wiggle", CAT, T, ALIVE + " && q.is_aggressive && q.ground_speed < 0.01", 0.25, F, {"segment%d:rot" % i: (lambda u, i=i: [0, 0, 20 * wave(u, i / 7.0)]) for i in range(7)},
           pri=120)
F, T = f("endermite"), "minecraft:endermite"
life("endermite.void_jitter", "Endermite Void Jitter", CAT, T, ALIVE, 0.2, F, {"mw_center:pos": lambda u: move(0.15 * wave(u), 0, 0.15 * wave(u, 0.25))})

# ============================================================================ piglins
for T, sp, label in (("minecraft:piglin", "piglin", "Piglin"), ("minecraft:piglin_brute", "piglin_brute", "Piglin Brute"), ("minecraft:zombified_piglin", "zombified_piglin", "Zombified Piglin")):
    F = f(sp)
    if sp == "piglin":
        life(sp + ".ear_flop", label + " Ear Flop", CAT, T, ALIVE, 1.0, F, {"left_ear:rot": lambda u: [0, 0, -10 * wave(u)], "right_ear:rot": lambda u: [0, 0, 10 * wave(u, 0.2)]})
    elif sp == "piglin_brute":
        life(sp + ".ear_flop", label + " Scarred Ear Twitch", CAT, T, ALIVE, 2.6, F, {"left_ear:rot": lambda u: [6 * spike(u, 0.2, 12), 0, -14 * spike(u, 0.2, 12)], "right_ear:rot": lambda u: [0, 0, 4 * wave(u, 0, 0.5)]})
    else:
        life(sp + ".ear_flop", label + " Rotting Ear Droop", CAT, T, ALIVE, 1.8, F, {"left_ear:rot": lambda u: [0, 0, -20 * wave(u) - 20], "right_ear:rot": lambda u: [0, 0, 10 * wave(u, 0.2)]})
T, F = "minecraft:piglin", f("piglin")
hwalk("piglin.swagger", "Piglin Swaggering Walk", T, WALKING + CALM, 1.1, F, stride=26, arm_swing=26, arm_out=8, bob=0.7, twist=10, sway=3, lean=-4)
hwalk("piglin.war_charge", "Piglin War Charge", T, WALKING + HUNT + " && q.main_hand == 'sword'", 0.7, F, pri=101, stride=40, arm_swing=0, bob=1.4, twist=10, sway=1, lean=16,
      right_arm=[120, 10, 0], left_arm=[30, 20, 0])
loop_state("piglin.admire_gold", "Piglin Admiring Gold", CAT, T, ALIVE + " && q.is_admiring", 2.0, F, {
    "left_arm:rot": lambda u: arm('l', 70, 20, -40), "head:rot": lambda u: [30, -20 + 8 * wave(u), 10 * wave(u, 0.2)], "body:rot": lambda u: tilt(6, -10, 0)}, pri=150, layer="action")
loop_state("piglin.victory_dance", "Piglin Victory Dance", CAT, T, ALIVE + " && q.is_dancing", 0.6, F, {
    "mw_root:pos": lambda u: move(0, 1.2 * max(0, wave(u)), 0), "right_arm:rot": lambda u: arm('r', 160, 20 + 20 * wave(u)), "left_arm:rot": lambda u: arm('l', 160, 20 + 20 * wave(u, 0.5)),
    "body:rot": lambda u: tilt(0, 20 * wave(u, 0, 0.5), 0), "head:rot": lambda u: [-10 * wave(u), 0, 0]}, pri=150, layer="action")
loop_state("piglin.crossbow_crank", "Piglin Cranking Crossbow", CAT, T, ALIVE + " && q.arm_pose == 'crossbow_charge'", 0.6, F, {"body:rot": lambda u: tilt(4, 10 * wave(u), 0)}, layer="additive", pri=80)
beat("piglin.barter_toss", "Piglin Tossing A Barter", CAT, T, event("barter_toss", ALIVE), 0.8, F, {
    "left_arm:rot": [(0, arm('l', 70, 20)), (0.25, arm('l', 120, 10)), (0.4, arm('l', 40, 0), "in_quart"), (0.8, Z)], "head:rot": [(0, Z), (0.4, [-10, 0, 0]), (0.8, Z)]}, pri=160)
beat("piglin.gold_jealousy", "Piglin Gold Jealousy Snort", CAT, T, event("vocalize", ALIVE + " && q.is_aggressive"), 0.9, F, {
    "head:rot": [(0, Z), (0.15, [-20, 0, 0]), (0.3, [10, 0, 0]), (0.9, Z)], "body:rot": [(0, Z), (0.15, tilt(-8)), (0.9, Z)], "right_arm:rot": [(0, Z), (0.2, arm('r', 30, 40)), (0.9, Z)]}, layer="gesture")
loop_state("piglin.zombify_shake", "Piglin Overworld Convulsions", CAT, T, ALIVE + " && q.dimension != 'the_nether'", 0.3, F, {
    "head:rot": lambda u: [0, 0, 8 * spike(u, 0, 4)], "body:rot": lambda u: tilt(0, 0, 3 * wave(u))}, layer="additive", pri=85)
T, F = "minecraft:piglin_brute", f("piglin_brute")
hwalk("piglin_brute.patrol", "Piglin Brute Patrol March", T, WALKING, 1.2, F, stride=24, arm_swing=0, bob=0.9, twist=4, sway=2, lean=6, right_arm=[25, 14, 0], left_arm=[10, 18, 0], legs_out=4)
strike_arms("piglin_brute.axe_chop", "Piglin Brute Axe Chop", T, event("attack", ALIVE), 0.85, F, [(0, [25]), (0.35, [170, 0, 0], "out_quad"), (0.48, [20, 0, 0], "in_quart"), (0.85, [25])],
            [(0, [10]), (0.35, [140, 0, 0]), (0.48, [30, 0, 0]), (0.85, [10])], body=[(0, Z), (0.35, tilt(-12)), (0.48, tilt(20)), (0.85, Z)], events=[(0.45, "whoosh", {"weight": "heavy"})])
loop_state("piglin_brute.guard_bastion", "Piglin Brute Guarding The Bastion", CAT, T, STILL, 4.0, F, {
    "head:rot": lambda u: [0, 45 * wave(u), 0], "right_arm:rot": lambda u: arm('r', 30, 10, -20), "body:rot": lambda u: tilt(-4, 0, 0)})
beat("piglin_brute.war_cry", "Piglin Brute War Cry", CAT, T, event("aggro", ALIVE), 1.2, F, {"head:rot": [(0, Z), (0.25, [-30, 0, 0]), (0.9, [-26, 0, 0]), (1.2, Z)],
                                                                                 "right_arm:rot": [(0, Z), (0.3, arm('r', 170, 10)), (0.9, arm('r', 170, 10)), (1.2, Z)],
                                                                                 "left_arm:rot": [(0, Z), (0.3, arm('l', 20, 50)), (0.9, arm('l', 20, 50)), (1.2, Z)],
                                                                                 "body:rot": [(0, Z), (0.25, tilt(-14, 0, 0)), (0.9, tilt(-10, 0, 0)), (1.2, Z)]}, pri=160)
T, F = "minecraft:zombified_piglin", f("zombified_piglin")
hwalk("zombified_piglin.dead_walk", "Zombified Piglin Dead Walk", T, WALKING + CALM, 1.5, F, stride=20, arm_swing=6, bob=0.3, twist=4, sway=4, lean=6, right_arm=[20, 4, 0], left_arm=None, asym=0.5)
hwalk("zombified_piglin.vengeance", "Zombified Piglin Vengeful Horde Charge", T, WALKING + HUNT, 0.75, F, pri=101, stride=36, arm_swing=0, bob=1.2, twist=12, sway=3, lean=18,
      right_arm=[110, 6, 0], left_arm=[90, 20, 0])
loop_state("zombified_piglin.idle_lean", "Zombified Piglin Listless Lean", CAT, T, STILL + CALM, 5.0, F, {"body:rot": lambda u: tilt(10, 0, 8 + 2 * wave(u)), "head:rot": lambda u: [24, 0, 16]})
beat("zombified_piglin.grunt", "Zombified Piglin Wet Grunt", CAT, T, event("vocalize", ALIVE), 0.9, F, {"head:rot": [(0, Z), (0.2, [15, 0, -20]), (0.5, [5, 0, 10]), (0.9, Z)]}, layer="gesture")

# ============================================================================ vex
T, F = "minecraft:vex", f("vex")
loop_state("vex.hover", "Vex Malicious Hover", CAT, T, ALIVE + " && !q.is_charging", 1.2, F, {
    "root:pos": lambda u: move(0, 0.8 * wave(u), 0), "right_wing:rot": lambda u: [0, -30 - 20 * wave(u, 0, 3), 0], "left_wing:rot": lambda u: [0, 30 + 20 * wave(u, 0, 3), 0],
    "body:rot": lambda u: tilt(10, 0, 4 * wave(u, 0.25))}, layer="additive", pri=60)
loop_state("vex.charge_dive", "Vex Charging Dive", CAT, T, ALIVE + " && q.is_charging", 0.3, F, {
    "right_arm:rot": lambda u: arm('r', 170, 10), "body:rot": lambda u: tilt(40, 0, 0), "right_wing:rot": lambda u: [0, -60, 0], "left_wing:rot": lambda u: [0, 60, 0], "left_arm:rot": lambda u: arm('l', -20, 20)},
    pri=150, layer="action")
beat("vex.cackle", "Vex Cackle", CAT, T, event("vocalize", ALIVE), 0.8, F, {"head:rot": [(0, Z), (0.1, [-15, 0, 10]), (0.2, [-10, 0, -10]), (0.3, [-15, 0, 10]), (0.8, Z)],
                                                                    "body:rot": [(0, Z), (0.2, tilt(-8)), (0.8, Z)]}, layer="gesture")
beat("vex.slash", "Vex Spectral Slash", CAT, T, event("melee_hit", ALIVE), 0.5, F, {"right_arm:rot": [(0, arm('r', 170, 10)), (0.15, arm('r', 30, -30), "in_quart"), (0.5, Z)],
                                                                            "body:rot": [(0, tilt(40)), (0.15, tilt(10, 20, 0)), (0.5, Z)]}, pri=170)
loop_state("vex.circle_taunt", "Vex Circling Taunt", CAT, T, ALIVE + " && q.is_aggressive && !q.is_charging", 2.0, F, {"root:rot": lambda u: [0, 0, 20 * wave(u)], "head:rot": lambda u: [0, 0, -16 * wave(u)]},
           pri=105)
beat("vex.fade_death", "Vex Fading Away", CAT, T, event("death"), 0.8, F, {"root:scl": [(0, [1, 1, 1]), (0.8, [0.2, 1.6, 0.2], "in_quad")], "root:rot": [(0, Z), (0.8, [0, 360, 0])]}, pri=300)

# ============================================================================ witch
T, F = "minecraft:witch", f("witch")
loop_state("witch.brew_drink", "Witch Quaffing A Potion", CAT, T, ALIVE + " && q.is_using_item", 1.2, F, {"head:rot": lambda u: [-30, 0, 0], "body:rot": lambda u: tilt(-8, 0, 0),
                                                                                         "hat:rot": lambda u: [-10, 0, 0]}, pri=150, layer="action")
beat("witch.potion_hurl", "Witch Hurling A Potion", CAT, T, event("shoot:potion", ALIVE), 0.7, F, {"arms:rot": [(0, Z), (0.25, [-60, 0, 0], "out_quad"), (0.38, [30, 0, 0], "in_quart"), (0.7, Z)],
                                                                                    "body:rot": [(0, Z), (0.25, tilt(-10, 20, 0)), (0.38, tilt(10, -20, 0)), (0.7, Z)]}, pri=170)
beat("witch.cackle", "Witch Cackle", CAT, T, event("vocalize", ALIVE), 1.4, F, {
    "head:rot": [(0, Z), (0.2, [-25, 0, 0]), (0.35, [-15, 0, 0]), (0.5, [-25, 0, 0]), (0.65, [-15, 0, 0]), (0.8, [-25, 0, 0]), (1.4, Z)],
    "body:rot": [(0, Z), (0.2, tilt(-10)), (0.8, tilt(-10)), (1.4, Z)], "nose:rot": [(0, Z), (0.3, [10, 0, 0]), (1.4, Z)]}, layer="gesture")
life("witch.nose_twitch", "Witch Nose Twitch", CAT, T, ALIVE, 2.2, F, {"nose:rot": lambda u: [0, 0, 8 * spike(u, 0.3, 10)], "mole:rot": lambda u: [0, 0, 4 * spike(u, 0.3, 10)]})
c = mob("witch.hobble", "Witch Hobbling Gait", CAT, T, 1.3, state(WALKING, exit_delay=0.15), layer="base", file=F, **driven(1.3))
c.cycle("right_leg", "rotation", lambda u: leg('r', 22 * cwave(u)))
c.cycle("left_leg", "rotation", lambda u: leg('l', -16 * cwave(u) - 4))
c.cycle("body", "rotation", lambda u: tilt(10, 4 * cwave(u), 0))
c.cycle("mw_root", "rotation", lambda u: tilt(0, 0, 4 * max(0, wave(u, 0.1)) - 1))
c.cycle("hat2", "rotation", lambda u: [3 * wave(u, 0.2, 2), 0, 0])
c.cycle("hat3", "rotation", lambda u: [5 * wave(u, 0.35, 2), 0, 0])
c.cycle("hat4", "rotation", lambda u: [8 * wave(u, 0.5, 2), 0, 0])
loop_state("witch.cauldron_stir", "Witch Stirring An Invisible Brew", CAT, T, STILL + " && !q.is_aggressive", 2.4, F, {
    "arms:rot": lambda u: [-20 + 6 * wave(u), 0, 0], "arms:pos": lambda u: move(0.8 * cwave(u), 0, 0.8 * wave(u)), "body:rot": lambda u: tilt(14, 6 * wave(u), 0), "head:rot": lambda u: [24, 0, 0]})
loop_state("witch.hat_tilt_watch", "Witch Watching From Under The Brim", CAT, T, ALIVE + " && q.player_distance < 8 && q.ground_speed < 0.02", 3.0, F, {
    "head:rot": lambda u: [14, 0, 10 + 3 * wave(u)], "hat2:rot": lambda u: [-4, 0, 0]}, layer="additive", pri=64)

# ============================================================================ illagers
for T, sp, label in (("minecraft:pillager", "pillager", "Pillager"), ("minecraft:vindicator", "vindicator", "Vindicator"), ("minecraft:evoker", "evoker", "Evoker"),
                     ("minecraft:illusioner", "illusioner", "Illusioner")):
    F = f(sp)
    if sp == "pillager":
        loop_state(sp + ".raid_celebrate", label + " Raid Celebration", CAT, T, ALIVE + " && q.is_celebrating", 0.7, F, {
            "mw_root:pos": lambda u: move(0, 1.0 * max(0, wave(u)), 0), "right_arm:rot": lambda u: arm('r', 170, 20 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 60, 20 * wave(u, 0.6)),
            "head:rot": lambda u: [-15, 20 * wave(u, 0, 0.5), 0]}, pri=160, layer="action")
    elif sp == "vindicator":
        loop_state(sp + ".raid_celebrate", label + " Raid Celebration Stomp", CAT, T, ALIVE + " && q.is_celebrating", 0.7, F, {
            "mw_root:pos": lambda u: move(0, 1.5 * max(0, wave(u)), 0), "right_arm:rot": lambda u: arm('r', 170, 20 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 170, 20 * wave(u, 0.6)),
            "right_leg:rot": lambda u: leg('r', 30 * max(0, wave(u, 0.5))), "head:rot": lambda u: [-15, 20 * wave(u, 0, 0.5), 0]}, pri=160, layer="action")
    elif sp == "evoker":
        loop_state(sp + ".raid_celebrate", label + " Raid Celebration Sway", CAT, T, ALIVE + " && q.is_celebrating", 1.0, F, {
            "right_arm:rot": lambda u: arm('r', 120, 20 * wave(u, 0.3)), "left_arm:rot": lambda u: arm('l', 60, 20 * wave(u, 0.6)), "body:rot": lambda u: tilt(0, 0, 10 * wave(u)),
            "head:rot": lambda u: [-15, 20 * wave(u, 0, 0.5), 0]}, pri=160, layer="action")
    else:
        loop_state(sp + ".raid_celebrate", label + " Raid Celebration Spin", CAT, T, ALIVE + " && q.is_celebrating", 1.0, F, {
            "mw_root:rot": lambda u: [0, 360 * u, 0], "right_arm:rot": lambda u: arm('r', 90, 80), "left_arm:rot": lambda u: arm('l', 90, 80), "head:rot": lambda u: [-20, 0, 0]}, pri=160, layer="action")
T, F = "minecraft:pillager", f("pillager")
hwalk("pillager.patrol", "Pillager Patrol Walk", T, WALKING + CALM, 1.1, F, stride=26, arm_swing=0, bob=0.5, twist=5, sway=2, lean=2, right_arm=[20, 6, 0], left_arm=[25, 10, -20])
c = mob("pillager.aim_strafe", "Pillager Aiming Strafe", CAT, T, 1.0, state(WALKING + HUNT, exit_delay=0.15), layer="base", pri=101, file=F, **driven(1.0))
biped(c, stride=18, bob=0.6, twist=0, sway=2, lean=8, legs_out=6, knee_lift=12, arms=False, side_sign="(q.strafe_speed >= 0 ? 1 : -1)")
c.bones.pop("head", None)
loop_state("pillager.crossbow_reload", "Pillager Crossbow Reload", CAT, T, ALIVE + " && q.arm_pose == 'crossbow_charge'", 0.8, F, {"body:rot": lambda u: tilt(8, -10 + 6 * wave(u), 0)}, layer="additive", pri=80)
beat("pillager.mocking_laugh", "Pillager Mocking Laugh", CAT, T, event("vocalize", ALIVE), 1.0, F, {"head:rot": [(0, Z), (0.2, [-14, 0, 0]), (0.35, [-6, 0, 0]), (0.5, [-14, 0, 0]), (1.0, Z)],
                                                                                         "body:rot": [(0, Z), (0.2, tilt(-6)), (1.0, Z)]}, layer="gesture")
loop_state("pillager.watchtower_scan", "Pillager Watchtower Scan", CAT, T, STILL + CALM, 5.0, F, {"head:rot": lambda u: [-5, 50 * wave(u), 0], "body:rot": lambda u: tilt(0, 15 * wave(u, 0.08), 0)})
beat("pillager.recoil", "Pillager Crossbow Recoil", CAT, T, event("crossbow_fire", ALIVE), 0.5, F, {"body:rot": [(0, Z), (0.05, tilt(-8, 0, 0), "out_expo"), (0.5, Z)],
                                                                                          "head:rot": [(0, Z), (0.05, [-8, 0, 0]), (0.5, Z)]}, pri=170, layer="reaction")
T, F = "minecraft:vindicator", f("vindicator")
hwalk("vindicator.stomp_walk", "Vindicator Brutish Stomp", T, WALKING + CALM, 1.0, F, stride=28, arm_swing=0, bob=0.9, twist=4, sway=2.5, lean=6)
hwalk("vindicator.axe_rush", "Vindicator Axe Rush", T, WALKING + HUNT, 0.65, F, pri=101, stride=42, arm_swing=30, bob=1.5, twist=8, sway=1, lean=18, right_arm=[170, 10, 0], left_arm=None)
strike_arms("vindicator.cleave", "Vindicator Cleaving Chop", T, event("attack", ALIVE), 0.7, F, [(0, [150]), (0.15, [175, 0, 0]), (0.28, [10, 0, 0], "in_quart"), (0.7, [40])],
            body=[(0, Z), (0.15, tilt(-10)), (0.28, tilt(24)), (0.7, Z)], events=[(0.25, "whoosh", {"weight": "heavy"})])
beat("vindicator.johnny_rage", "Vindicator Unhinged Rage", CAT, T, event("aggro", ALIVE + " && q.trait_confidence > 0.6"), 1.2, F, {
    "head:rot": [(0, Z), (0.1, [-20, 0, 15]), (0.25, [-20, 0, -15]), (0.4, [-20, 0, 15]), (0.55, [-20, 0, -10]), (1.2, Z)], "right_arm:rot": [(0, Z), (0.2, arm('r', 175)), (1.0, arm('r', 175)), (1.2, Z)]},
     pri=170)
loop_state("vindicator.lurk", "Vindicator Mansion Lurk", CAT, T, STILL + CALM, 6.0, F, {"head:rot": lambda u: [12, 30 * wave(u), 0], "body:rot": lambda u: tilt(6, 0, 0)})
T, F = "minecraft:evoker", f("evoker")
loop_state("evoker.cast_fangs", "Evoker Summoning Fangs", CAT, T, ALIVE + " && q.is_casting && q.arm_pose == 'spellcasting'", 1.2, F, {
    "right_arm:rot": lambda u: arm('r', 100 + 20 * wave(u), 50), "left_arm:rot": lambda u: arm('l', 100 + 20 * wave(u, 0.5), 50), "body:rot": lambda u: tilt(-8, 0, 0), "head:rot": lambda u: [-20, 0, 0]},
    pri=150, layer="action")
loop_state("evoker.channel_vex", "Evoker Channelling Vexes", CAT, T, ALIVE + " && q.is_casting && q.arm_pose != 'spellcasting'", 1.6, F, {
    "right_arm:rot": lambda u: arm('r', 170, 30 + 10 * wave(u)), "left_arm:rot": lambda u: arm('l', 170, 30 + 10 * wave(u, 0.5)), "mw_root:pos": lambda u: move(0, 0.6 * wave(u), 0)}, pri=150, layer="action")
beat("evoker.sinister_hum", "Evoker Sinister Hum", CAT, T, event("vocalize", ALIVE), 1.4, F, {"head:rot": [(0, Z), (0.4, [10, -20, 0]), (1.0, [10, 20, 0]), (1.4, Z)]}, layer="gesture")
hwalk("evoker.robed_glide", "Evoker Robed Glide", T, WALKING, 1.6, F, stride=16, arm_swing=0, bob=0.15, twist=2, sway=1, lean=-2)
T, F = "minecraft:illusioner", f("illusioner")
loop_state("illusioner.mirror_cast", "Illusioner Mirror Image Cast", CAT, T, ALIVE + " && q.is_casting", 0.8, F, {
    "right_arm:rot": lambda u: arm('r', 120, 40 + 30 * wave(u)), "left_arm:rot": lambda u: arm('l', 120, 40 - 30 * wave(u)), "body:rot": lambda u: tilt(0, 30 * wave(u), 0)}, pri=150, layer="action")
loop_state("illusioner.bow_draw", "Illusioner Arcane Bow Draw", CAT, T, ALIVE + " && q.arm_pose == 'bow_and_arrow'", 1.0, F, {"body:rot": lambda u: tilt(0, -20, 0), "head:rot": lambda u: [-4, 18, 0]},
           layer="additive", pri=80)
beat("illusioner.blindness_flourish", "Illusioner Blinding Flourish", CAT, T, event("vocalize", ALIVE), 1.2, F, {
    "right_arm:rot": [(0, Z), (0.3, arm('r', 150, 60)), (0.6, arm('r', 60, 80)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.3, arm('l', 150, 60)), (0.6, arm('l', 60, 80)), (1.2, Z)]}, pri=150)

# ============================================================================ ender dragon (vanilla renderer draws it as one rigid hierarchy: virtual bones only)
T, F = "minecraft:ender_dragon", f("ender_dragon")
loop_state("ender_dragon.soar_sway", "Ender Dragon Soaring Sway", CAT, T, ALIVE + " && (q.phase == 'holding_pattern' || q.phase == 'hovering')", 4.0, F, {
    "mw_root:rot": lambda u: tilt(3 * wave(u, 0.25), 0, 8 * wave(u)), "mw_root:pos": lambda u: move(0, 4 * wave(u, 0.1), 0)}, layer="additive", pri=60)
loop_state("ender_dragon.strafe_bank", "Ender Dragon Strafing Bank", CAT, T, ALIVE + " && q.phase == 'strafe_player'", 1.6, F, {"mw_root:rot": lambda u: tilt(-6, 0, 20 + 4 * wave(u))}, layer="additive", pri=62)
loop_state("ender_dragon.charge_dive", "Ender Dragon Charging Dive", CAT, T, ALIVE + " && q.phase == 'charging_player'", 0.8, F, {"mw_root:rot": lambda u: tilt(14, 0, 3 * wave(u, 0, 3))},
           layer="additive", pri=64)
loop_state("ender_dragon.perch_breath", "Ender Dragon Perched Breath", CAT, T, ALIVE + " && q.phase == 'sitting_flaming'", 1.0, F, {"mw_root:pos": lambda u: move(0, -1.5 * max(0, wave(u)), 2 * max(0, wave(u)))},
           layer="additive", pri=66)
loop_state("ender_dragon.perch_scan", "Ender Dragon Scanning From Perch", CAT, T, ALIVE + " && q.phase == 'sitting_scanning'", 3.0, F, {"mw_root:rot": lambda u: tilt(0, 10 * wave(u), 0)}, layer="additive", pri=66)
loop_state("ender_dragon.perch_roar", "Ender Dragon Perched Roar", CAT, T, ALIVE + " && q.phase == 'sitting_attacking'", 1.2, F, {"mw_root:rot": lambda u: tilt(-10 * max(0, wave(u, 0, 0.5)), 0, 0),
                                                                                                                       "mw_root:pos": lambda u: move(0, 3 * max(0, wave(u, 0, 0.5)), 0)},
           layer="additive", pri=66)
loop_state("ender_dragon.landing_flare", "Ender Dragon Landing Flare", CAT, T, ALIVE + " && (q.phase == 'landing' || q.phase == 'landing_approach')", 1.4, F, {"mw_root:rot": lambda u: tilt(-12, 0, 4 * wave(u))},
           layer="additive", pri=64)
loop_state("ender_dragon.death_convulse", "Ender Dragon Death Convulsions", CAT, T, "q.phase == 'dying'", 0.5, F, {
    "mw_root:rot": lambda u: tilt(6 * wave(u), 4 * wave(u, 0.3), 10 * wave(u, 0.6)), "mw_root:pos": lambda u: move(0.8 * wave(u, 0.2), 0.8 * wave(u, 0.5), 0)}, layer="additive", pri=90)

# ============================================================================ extra behaviours
T, F = "minecraft:zombie", f("zombie")
loop_state("zombie.grasping_reach", "Zombie Grasping Reach", CAT, T, STILL + HUNT, 1.4, F, {
    "right_arm:rot": lambda u: arm('r', 95 + 10 * wave(u), 6 + 8 * wave(u, 0, 2)), "left_arm:rot": lambda u: arm('l', 90 + 10 * wave(u, 0.5), 6 + 8 * wave(u, 0.5, 2)),
    "body:rot": lambda u: tilt(14 + 4 * wave(u, 0, 2), 0, 0)}, pri=115)
T, F = "minecraft:skeleton", f("skeleton")
c = mob("skeleton.backpedal", "Skeleton Backpedalling To Range", CAT, T, 0.9, state(WALKING + HUNT + " && q.forward_speed < -0.02", exit_delay=0.15), layer="base", pri=102, file=F, **driven(0.9))
biped(c, stride=-20, arm_swing=0, bob=0.5, twist=0, sway=2, lean=-8, arms=False)
c.bones.pop("head", None)
T, F = "minecraft:creeper", f("creeper")
beat("creeper.landing_squat", "Creeper Landing Squat", CAT, T, event("land", ALIVE), 0.5, F, {"mw_center:pos": [(0, Z), (0.06, move(0, -1.5, 0), "out_expo"), (0.5, Z)],
                                                                                   "head:rot": [(0, Z), (0.06, [10, 0, 0]), (0.5, Z)], "body:scl": [(0, [1, 1, 1]), (0.06, [1.06, 0.92, 1.06]), (0.5, [1, 1, 1])]},
     layer="gesture")
T, F = "minecraft:enderman", f("enderman")
beat("enderman.arrive", "Enderman Arrival Unfold", CAT, T, event("teleport", ALIVE + " && q.is_creepy"), 0.9, F, {
    "body:rot": [(0, tilt(30)), (0.4, tilt(-6), "out_quad"), (0.9, Z)], "head:rot": [(0, [40, 0, 0]), (0.4, [-14, 0, 0]), (0.9, Z)],
    "right_arm:rot": [(0, arm('r', 0, 50)), (0.4, arm('r', 10, 10)), (0.9, Z)], "left_arm:rot": [(0, arm('l', 0, 50)), (0.4, arm('l', 10, 10)), (0.9, Z)]}, pri=225, layer="reaction")
T, F = "minecraft:ravager", f("ravager")
life("ravager.trample", "Ravager Trampling Through Foliage", CAT, T, WALKING + " && q.feet_block == 'foliage'", 0.7, F, {"neck:rot": lambda u: [10 + 8 * max(0, wave(u)), 10 * wave(u, 0.25), 0]})
T, F = "minecraft:witch", f("witch")
loop_state("witch.panicked_brew", "Witch Fumbling For A Healing Brew", CAT, T, ALIVE + " && q.is_using_item && q.health < 0.4", 0.6, F, {
    "head:rot": lambda u: [-35, 10 * wave(u), 0], "body:rot": lambda u: tilt(-6, 0, 4 * wave(u, 0.25)), "arms:rot": lambda u: [-30 + 10 * wave(u, 0, 2), 0, 0]}, pri=155, layer="action")
T, F = "minecraft:vindicator", f("vindicator")
loop_state("vindicator.door_hack", "Vindicator Hacking Down A Door", CAT, T, ALIVE + HUNT + " && q.ground_speed < 0.01 && q.is_swinging", 0.5, F, {
    "right_arm:rot": lambda u: arm('r', 120 + 50 * wave(u), 0), "body:rot": lambda u: tilt(10 * wave(u, 0.1), 0, 0)}, pri=145, layer="action")
T, F = "minecraft:piglin", f("piglin")
loop_state("piglin.hunt_hoglin", "Piglin Hunting Party Crouch", CAT, T, ALIVE + " && q.is_aggressive && q.main_hand == 'crossbow' && q.ground_speed < 0.02", 2.0, F, {
    "mw_root:pos": lambda u: move(0, -1.5, 0), "right_leg:rot": lambda u: leg('r', 25), "left_leg:rot": lambda u: leg('l', -15), "body:rot": lambda u: tilt(14, -10, 0)}, pri=118)

"""Player movement and locomotion (category: player_locomotion)."""
from core import Clip, state, event, arm, leg, tilt, move, biped, strike, shake, wave, cwave

CAT = "player_locomotion"
T = "@player"
CYCLE = 9.4248  # vanilla limb-swing units per stride cycle

ALIVE = "!q.is_dead && !q.is_sleeping && !q.is_riding && !q.is_swimming && !q.is_fall_flying"
GROUNDED = ALIVE + " && q.is_on_ground && !q.is_crawling && !q.is_climbing"
IDLE = GROUNDED + " && q.ground_speed < 0.02 && !q.is_sneaking"
WALKING = GROUNDED + " && q.ground_speed >= 0.02 && !q.is_sneaking"


def locomotion(cid, name, when, priority, cadence=1.0, length=1.0, **gait):
    c = Clip("player.locomotion." + cid, name, CAT, T, length=length, loop="loop", layer="base", priority=priority,
             trigger=state(when, exit_delay=0.12), blend_in=0.25, blend_out=0.25,
             time="q.limb_swing * %g" % round(length / (CYCLE * cadence), 5), weight="math.clamp(q.limb_swing_amount * 2.2, 0, 1)",
             file="player/locomotion")
    biped(c, **gait)
    return c


# --- walking: speed bands and gait character
locomotion("walk_casual", "Hands-Behind-Back Stroll", WALKING + " && q.ground_speed < 0.13", 200, cadence=0.9, stride=22, bob=0.5, twist=3, sway=1.5, head_bob=1.2,
           right_arm=(-28, -6, -30), left_arm=(-28, -6, -30))
locomotion("walk", "Walk", WALKING + " && !q.is_sprinting", 199, stride=30, arm_swing=26, bob=0.8, twist=5, sway=2.0, head_bob=1.8)
locomotion("walk_backward", "Walk Backward", WALKING + " && q.forward_speed < -0.02 && !q.is_sprinting", 230, cadence=0.85, stride=-22, arm_swing=12, bob=0.5, twist=2, sway=1.0, lean=-4, head_bob=1.0, arm_out=7)
SIDE = "(q.strafe_speed > 0 ? 1 : -1)"
locomotion("strafe", "Side Step", WALKING + " && math.abs(q.strafe_speed) > 0.03 && math.abs(q.forward_speed) < 0.04", 231, cadence=0.8, stride=12, arm_swing=8, bob=0.6,
           twist=8, sway=-5, legs_out=10, head_bob=1, side_sign=SIDE)
locomotion("diagonal", "Diagonal Walk", WALKING + " && math.abs(q.strafe_speed) > 0.03 && q.forward_speed > 0.04", 229, stride=26, arm_swing=20, bob=0.7, twist=6, sway=-3,
           head_bob=1.5, body_extra=lambda u: (0, 10, 0), side_sign=SIDE)
locomotion("walk_injured", "Injured Limp", WALKING + " && q.health < 0.3 && !q.is_sprinting", 240, cadence=0.75, stride=22, arm_swing=10, bob=1.6, twist=2, sway=4, lean=8, head_bob=3, asym=0.6, right_arm=(10, 14, 0))
locomotion("walk_heavy_armor", "Armoured March", WALKING + " && q.armor_weight > 0.6 && !q.is_sprinting", 235, cadence=0.92, stride=26, arm_swing=16, arm_out=10, bob=1.2, twist=3, sway=3.5, head_bob=1.0)
locomotion("walk_snow", "Snow Trudge", WALKING + " && q.surface == 'snow' && !q.is_sprinting", 236, cadence=0.8, stride=24, arm_swing=22, bob=1.4, twist=4, sway=2.5, lean=6, knee_lift=18)
locomotion("wade_shallow", "Shallow Wade", GROUNDED + " && q.ground_speed >= 0.02 && q.is_in_water && !q.is_underwater", 237, cadence=0.7, stride=20, arm_swing=6, arm_out=24, bob=1.0, twist=6, sway=2.5, lean=5, knee_lift=12)
locomotion("walk_ice", "Careful Ice Walk", WALKING + " && q.surface == 'glass' && !q.is_sprinting", 233, cadence=1.25, stride=12, arm_swing=4, arm_out=22, bob=0.3, twist=1, sway=4, lean=-3)
locomotion("walk_mud", "Heavy Mud Steps", WALKING + " && q.surface == 'mud' && !q.is_sprinting", 234, cadence=0.75, stride=24, arm_swing=18, bob=1.6, twist=5, sway=3, lean=7, knee_lift=22)
locomotion("walk_sand", "Sinking Sand Walk", WALKING + " && q.surface == 'sand' && !q.is_sprinting", 232, cadence=0.9, stride=26, arm_swing=22, bob=1.1, twist=5, sway=2.5, lean=4, knee_lift=8)
locomotion("walk_soul", "Soul Sand Drag", WALKING + " && q.surface == 'soul'", 238, cadence=0.6, stride=20, arm_swing=14, bob=1.8, twist=3, sway=2, lean=10, knee_lift=26, head_bob=3)
locomotion("walk_slime", "Bouncy Slime Steps", WALKING + " && q.surface == 'slime'", 238, cadence=1.1, stride=26, arm_swing=24, bob=0.5, bounce=2.5, twist=4, sway=2, head_bob=3)
locomotion("walk_rain", "Hunched Rain Walk", WALKING + " && q.is_raining && !q.is_sprinting", 222, stride=28, arm_swing=12, arm_out=2, bob=0.9, twist=3, sway=2, lean=12, head_hold=(18, 0, 0))
locomotion("walk_cold", "Cold Huddled Walk", WALKING + " && q.is_cold && !q.is_raining && !q.is_sprinting", 221, cadence=1.1, stride=24, arm_swing=0, bob=0.6, twist=2, sway=1.5, lean=8, right_arm=(34, -12, 30), left_arm=(34, -12, 30))
locomotion("walk_tired", "Weary Walk", WALKING + " && q.hunger > 0.7 && !q.is_sprinting", 223, cadence=0.85, stride=24, arm_swing=12, bob=1.4, twist=2, sway=3, lean=10, head_hold=(16, 0, 0), head_bob=3)
locomotion("walk_dark", "Wary Dark Walk", WALKING + " && q.light < 4 && !q.is_sprinting", 220, cadence=0.85, stride=22, arm_swing=8, arm_out=10, bob=0.5, twist=6, sway=1.5, lean=6, head_bob=1)
locomotion("walk_heat", "Heat-Stricken Walk", WALKING + " && q.dimension == 'the_nether' && !q.is_sprinting", 219, cadence=0.9, stride=26, arm_swing=16, bob=1.0, twist=3, sway=3.5, lean=6, arm_out=8)
locomotion("walk_happy", "Jaunty Walk", WALKING + " && q.mood > 0.55 && !q.is_sprinting", 215, cadence=1.05, stride=32, arm_swing=34, bob=0.6, bounce=1.4, twist=6, sway=2.5, head_bob=2.5)
locomotion("walk_sad", "Dejected Shuffle", WALKING + " && q.mood < -0.45 && !q.is_sprinting", 216, cadence=0.8, stride=18, arm_swing=8, bob=0.6, twist=2, sway=1.5, lean=9, head_hold=(22, 0, 0))
locomotion("walk_nervous", "Nervous Glancing Walk", WALKING + " && q.near_hostile && q.trait_nervous > 0.5 && !q.is_sprinting", 217, cadence=1.15, stride=24, arm_swing=12, arm_out=8, bob=0.5, twist=8, sway=1.5, lean=5,
           head_hold=None, body_extra=lambda u: (0, 6 * wave(u, 0, 1), 0))
locomotion("walk_confident", "Confident Swagger", WALKING + " && q.trait_confidence > 0.75 && !q.is_sprinting", 214, cadence=0.95, stride=34, arm_swing=22, arm_out=16, bob=0.4, twist=16, sway=4.5, lean=-7, head_bob=0.5, arm_phase=0.08)
locomotion("walk_uphill", "Uphill Climb", WALKING + " && q.vertical_speed > 0.15 && !q.is_sprinting", 224, cadence=0.85, stride=30, arm_swing=24, bob=1.1, twist=4, sway=2, lean=14, knee_lift=16)
locomotion("walk_downhill", "Downhill Brake Walk", WALKING + " && q.vertical_speed < -0.15 && !q.is_sprinting", 224, cadence=1.1, stride=22, arm_swing=14, arm_out=10, bob=0.9, twist=3, sway=2, lean=-8)
locomotion("walk_tall_grass", "Wading Through Grass", WALKING + " && q.surface == 'grass' && q.wind > 0.6 && !q.is_sprinting", 212, stride=28, arm_swing=10, arm_out=20, bob=0.9, twist=6, sway=2, knee_lift=12)

locomotion("walk_inspecting", "Inquisitive Amble", WALKING + " && q.ground_speed < 0.12 && q.trait_curiosity > 0.65 && !q.is_sprinting", 213, cadence=0.85,
           stride=20, arm_swing=6, bob=0.4, twist=10, sway=1.0, head_bob=0.5, right_arm=(-18, -4, -26), left_arm=(-18, -4, -26),
           body_extra=lambda u: (0, 14 * wave(u, 0.1, 1), 0))
locomotion("walk_sleepy", "Sleepy Shuffle", WALKING + " && q.time_of_day > 0.72 && q.time_of_day < 0.95 && q.exertion < 0.2 && !q.is_sprinting", 218, cadence=0.7,
           stride=16, arm_swing=6, bob=0.9, twist=1, sway=3.5, lean=7, head_hold=(26, 0, 6), knee_lift=-4)
locomotion("walk_freezing", "Frozen Stiff Steps", WALKING + " && q.freezing > 0.45", 239, cadence=1.3, stride=10, arm_swing=0, bob=0.2, twist=0, sway=1.0,
           right_arm=(40, -20, 40), left_arm=(40, -20, 40), head_hold=(18, 0, 0))
locomotion("walk_on_fire", "Burning Panic Run", GROUNDED + " && q.is_on_fire && q.ground_speed >= 0.02 && !q.is_in_water", 330, length=0.6, stride=50,
           arm_swing=20, bob=1.6, twist=12, sway=4, lean=8, right_arm=(160, 20, 0), left_arm=(160, 20, 0), head_bob=4)

# --- running
RUN = GROUNDED + " && q.is_sprinting && q.ground_speed > 0.08 && !q.is_sneaking"
locomotion("run", "Run", RUN, 300, length=0.8, stride=52, arm_swing=58, arm_out=6, bob=1.6, twist=9, sway=2.0, lean=10, head_bob=3.0, knee_lift=12)
locomotion("jog_tired", "Tired Jog", RUN + " && q.hunger > 0.7", 310, length=0.85, stride=40, arm_swing=36, bob=1.8, twist=6, sway=3, lean=14, head_hold=(14, 0, 0), knee_lift=6)
locomotion("sprint_fast", "Full Sprint", RUN + " && q.ground_speed > 0.34", 320, length=0.7, stride=66, arm_swing=80, arm_out=2, bob=1.2, twist=16, sway=1.0, lean=24, head_bob=1.0, knee_lift=4, arm_phase=0.06, root_pitch=4)
locomotion("sprint_heavy_armor", "Armoured Charge", RUN + " && q.armor_weight > 0.6", 315, length=0.85, stride=44, arm_swing=34, arm_out=12, bob=2.2, twist=6, sway=4, lean=12, knee_lift=10)
locomotion("sprint_injured", "Desperate Sprint", RUN + " && q.health < 0.3", 318, length=0.82, stride=46, arm_swing=50, bob=2.4, twist=10, sway=5, lean=16, asym=0.4, head_bob=4)
locomotion("run_snow", "Snow Bound Run", RUN + " && q.surface == 'snow'", 312, length=0.9, stride=46, arm_swing=46, bob=2.2, twist=8, sway=3, lean=14, knee_lift=30)
locomotion("run_sand", "Sand Dash", RUN + " && q.surface == 'sand'", 311, length=0.84, stride=40, arm_swing=34, arm_out=18, bob=2.6, bounce=1.0, twist=5, sway=6, lean=8, knee_lift=34, asym=0.15)
locomotion("run_shallow_water", "Splashing Run", GROUNDED + " && q.is_sprinting && q.is_in_water", 313, length=0.95, stride=42, arm_swing=26, arm_out=20, bob=2.0, twist=10, sway=3, lean=12, knee_lift=26)
locomotion("sprint_uphill", "Uphill Sprint", RUN + " && q.vertical_speed > 0.15", 314, length=0.82, stride=50, arm_swing=60, bob=1.7, twist=8, sway=2, lean=22, knee_lift=26)
locomotion("sprint_downhill", "Downhill Rush", RUN + " && q.vertical_speed < -0.15", 314, length=0.75, stride=58, arm_swing=40, arm_out=14, bob=1.4, twist=7, sway=2.5, lean=4)
locomotion("run_panic", "Panicked Flight", RUN + " && q.near_hostile && q.health < 0.5", 319, length=0.72, stride=60, arm_swing=80, arm_out=16, bob=2.0, twist=14, sway=4, lean=20, head_bob=5, arm_phase=0.1)
locomotion("run_happy", "Joyful Bounding Run", RUN + " && q.mood > 0.6", 305, length=0.8, stride=54, arm_swing=62, bob=1.2, bounce=2.0, twist=10, sway=2.5, lean=8)
locomotion("sprint_rain", "Shielded Rain Dash", RUN + " && q.is_raining", 309, length=0.8, stride=50, arm_swing=40, bob=1.6, twist=8, sway=2, lean=14,
           left_arm=(150, -20, 30), head_hold=(12, 0, 0))

# --- sneaking
SNEAK = ALIVE + " && q.is_sneaking && q.is_on_ground && !q.is_climbing"
c = Clip("player.locomotion.sneak_idle", "Crouched Idle", CAT, T, length=3.0, loop="loop", layer="base", priority=400,
         trigger=state(SNEAK + " && q.ground_speed < 0.01", group="sneak_idle", weight=4), blend_in=0.3, file="player/locomotion")
c.rot("head", (0, tilt(-6)), (1.5, tilt(-8, 6)), (3.0, tilt(-6)), lerp="smooth")
c.rot("right_arm", (0, arm('r', 14, 8)), (1.5, arm('r', 16, 9)), (3, arm('r', 14, 8)), lerp="smooth")
c.rot("left_arm", (0, arm('l', 18, 6)), (1.5, arm('l', 20, 7)), (3, arm('l', 18, 6)), lerp="smooth")
c.pos("mw_root", (0, move(0, -0.4)), (1.5, move(0, -0.7)), (3, move(0, -0.4)), lerp="smooth")
c = Clip("player.locomotion.sneak_peek", "Crouched Peek Around", CAT, T, length=2.6, loop="once", layer="base", priority=400,
         trigger=state(SNEAK + " && q.ground_speed < 0.01", group="sneak_idle", weight=1), blend_in=0.25, file="player/locomotion")
c.rot("head", (0, tilt(-6)), (0.5, tilt(-4, -38)), (1.2, tilt(-4, -40)), (1.6, tilt(-6, 32)), (2.2, tilt(-6, 34)), (2.6, tilt(-6)), lerp="smooth")
c.rot("body", (0, tilt(0)), (0.5, tilt(0, -10)), (1.6, tilt(0, 8)), (2.6, tilt(0)), lerp="smooth")
c.rot("right_arm", (0, arm('r', 14, 8)), (2.6, arm('r', 14, 8)))
locomotion("sneak_walk", "Stealth Creep", SNEAK + " && q.ground_speed >= 0.01", 401, cadence=0.8, stride=20, arm_swing=8, arm_out=8, bob=0.3, twist=3, sway=1.2, lean=4, head_bob=0.6, knee_lift=6)
locomotion("sneak_back", "Stealth Back Creep", SNEAK + " && q.forward_speed < -0.01", 402, cadence=0.75, stride=-16, arm_swing=6, arm_out=10, bob=0.3, twist=2, sway=1, lean=2)
locomotion("sneak_strafe", "Stealth Side Creep", SNEAK + " && math.abs(q.strafe_speed) > 0.015 && math.abs(q.forward_speed) < 0.02", 403, cadence=0.7, stride=10, arm_swing=4,
           arm_out=12, bob=0.3, twist=6, sway=-4, legs_out=8, side_sign=SIDE)

# --- crawling (1-block gaps)
CRAWL = ALIVE + " && q.is_crawling"
c = Clip("player.locomotion.crawl_idle", "Prone Rest", CAT, T, length=3.0, loop="loop", layer="base", priority=550,
         trigger=state(CRAWL + " && q.ground_speed < 0.01"), file="player/locomotion")
c.rot("right_arm", (0, arm('r', 150, 12)), (1.5, arm('r', 148, 14)), (3, arm('r', 150, 12)), lerp="smooth")
c.rot("left_arm", (0, arm('l', 150, 12)), (1.5, arm('l', 152, 10)), (3, arm('l', 150, 12)), lerp="smooth")
c.rot("head", (0, tilt(-20)), (1.5, tilt(-22, 5)), (3, tilt(-20)), lerp="smooth")
c = Clip("player.locomotion.crawl_forward", "Army Crawl", CAT, T, length=1.4, loop="loop", layer="base", priority=551,
         trigger=state(CRAWL + " && q.ground_speed >= 0.01"), time="q.limb_swing * %g" % round(1.4 / CYCLE, 5), file="player/locomotion")
c.cycle("right_arm", "rotation", lambda u: arm('r', 150 + 25 * cwave(u), 14 + 10 * wave(u)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 150 - 25 * cwave(u), 14 - 10 * wave(u)))
c.cycle("right_leg", "rotation", lambda u: leg('r', -10 * cwave(u, 0.5), 10 + 8 * wave(u, 0.5)))
c.cycle("left_leg", "rotation", lambda u: leg('l', 10 * cwave(u, 0.5), 10 - 8 * wave(u, 0.5)))
c.cycle("body", "rotation", lambda u: tilt(0, 6 * wave(u), 0))
c.cycle("head", "rotation", lambda u: tilt(-20, -4 * wave(u), 0))
c.ev(0.2, "foley", kind="cloth", volume=0.5).ev(0.9, "foley", kind="cloth", volume=0.5)
c = Clip("player.locomotion.crawl_back", "Backward Crawl", CAT, T, length=1.6, loop="loop", layer="base", priority=552,
         trigger=state(CRAWL + " && q.forward_speed < -0.005"), time="q.limb_swing * %g" % round(1.6 / CYCLE, 5), file="player/locomotion")
c.cycle("right_arm", "rotation", lambda u: arm('r', 140 - 18 * cwave(u), 20))
c.cycle("left_arm", "rotation", lambda u: arm('l', 140 + 18 * cwave(u), 20))
c.cycle("right_leg", "rotation", lambda u: leg('r', 8 * cwave(u), 6))
c.cycle("left_leg", "rotation", lambda u: leg('l', -8 * cwave(u), 6))
c.cycle("head", "rotation", lambda u: tilt(-28, 3 * wave(u), 0))


# ---------------------------------------------------------------- idles
def breathe_loop(c, bone, base, amp, phase=0.0, harmonic=1, ch="rotation"):
    c.cycle(bone, ch, lambda u: [b + a * wave(u, phase, harmonic) for b, a in zip(base, amp)])
    return c


def idle(cid, name, when, priority, length, group=None, weight=1, file="player/idle", **poses):
    """Looping idle: each pose kwarg is bone=(base_rot, amp_rot[, phase])."""
    c = Clip("player.idle." + cid, name, CAT, T, length=length, loop="loop", layer="base", priority=priority,
             trigger=state(when, group=group, weight=weight, min_time=length), blend_in=0.4, blend_out=0.4, file=file)
    for bone, spec in poses.items():
        base, amp = spec[0], spec[1]
        phase = spec[2] if len(spec) > 2 else 0.0
        if bone == "root_pos":
            breathe_loop(c, "mw_root", base, amp, phase, ch="position")
        else:
            breathe_loop(c, bone, base, amp, phase)
    return c


Z = (0, 0, 0)
idle("relaxed", "Relaxed Stance", IDLE, 100, 4.0, group="idle", weight=6,
     head=(tilt(2), (1.5, 2.5, 0), 0.1), body=(Z, (0.8, 0, 0.6)), right_arm=(arm('r', 0, 3), (1.5, 0, 1.2)), left_arm=(arm('l', 0, 3), (-1.5, 0, -1.2), 0.5),
     root_pos=(Z, (0, 0.25, 0)))
idle("alert", "Alert Stance", IDLE + " && q.near_hostile", 130, 2.4, group="idle_alert", weight=5,
     head=(tilt(-3), (1, 6, 0)), body=(tilt(3), (0.5, 3, 0)), right_arm=(arm('r', 12, 10), (2, 0, 2)), left_arm=(arm('l', 10, 10), (2, 0, 2), 0.5),
     right_leg=(leg('r', -4, 6), (1, 0, 0)), left_leg=(leg('l', 6, 6), (1, 0, 0)), root_pos=(move(0, -0.6), (0, 0.3, 0)))
idle("tired", "Exhausted Stance", IDLE + " && (q.hunger > 0.7 || q.exertion > 0.75)", 125, 2.0, group="idle_tired", weight=4,
     head=(tilt(18), (4, 0, 0)), body=(tilt(12), (3, 0, 0)), right_arm=(arm('r', -6, 6), (3, 0, 0)), left_arm=(arm('l', -6, 6), (3, 0, 0)),
     root_pos=(move(0, -0.8), (0, 0.5, 0)))
idle("cold", "Shivering Hug", IDLE + " && q.is_cold", 121, 0.6, group="idle_cold", weight=4,
     head=(tilt(10), (0, 0, 1.5)), body=(tilt(6), (0, 0, 1.4)), right_arm=(arm('r', 40, -14, 34), (0, 0, 3)), left_arm=(arm('l', 40, -14, 34), (0, 0, 3), 0.5),
     root_pos=(move(0, -0.3), (0.3, 0, 0)))
idle("rain", "Rain-Hunched Stance", IDLE + " && q.is_raining", 120, 3.0, group="idle_rain", weight=4,
     head=(tilt(20), (1.5, 2, 0)), body=(tilt(10), (1, 0, 0)), right_arm=(arm('r', 10, -4), (2, 0, 0)), left_arm=(arm('l', 10, -4), (2, 0, 0), 0.4))
idle("injured", "Wounded Stance", IDLE + " && q.health < 0.3", 128, 2.6, group="idle_injured", weight=5,
     head=(tilt(12, 0, 4), (3, 2, 0)), body=(tilt(8, 0, 6), (2, 0, 1)), right_arm=(arm('r', 30, -10, 20), (3, 0, 0)), left_arm=(arm('l', -2, 8), (2, 0, 0)),
     right_leg=(leg('r', 8, 4), (2, 0, 0)), left_leg=(leg('l', -4, 2), (1, 0, 0)), root_pos=(move(0, -0.7), (0, 0.4, 0)))
idle("heavy_armor", "Armoured Stance", IDLE + " && q.armor_weight > 0.6", 115, 4.5, group="idle_armor", weight=4,
     head=(tilt(-2), (1, 3, 0)), body=(tilt(-2), (0.6, 0, 0.5)), right_arm=(arm('r', 2, 9), (1, 0, 0.8)), left_arm=(arm('l', 2, 9), (1, 0, 0.8), 0.5),
     right_leg=(leg('r', 0, 4), (0, 0, 0)), left_leg=(leg('l', 0, 4), (0, 0, 0)))
idle("confident", "Proud Stance", IDLE + " && q.trait_confidence > 0.75", 110, 4.0, group="idle", weight=3,
     head=(tilt(-5), (1, 3, 0)), body=(tilt(-4), (0.8, 0, 0)), right_arm=(arm('r', -8, 16, 10), (1, 0, 1)), left_arm=(arm('l', -8, 16, 10), (1, 0, 1), 0.5),
     right_leg=(leg('r', 0, 6), Z), left_leg=(leg('l', 0, 6), Z))
idle("nervous", "Fidgety Stance", IDLE + " && q.trait_nervous > 0.72", 110, 1.6, group="idle", weight=3,
     head=(tilt(4), (2, 10, 1), 0.2), body=(tilt(3), (1, 3, 1)), right_arm=(arm('r', 16, -6, 20), (4, 2, 3)), left_arm=(arm('l', 16, -6, 20), (4, 2, 3), 0.3),
     root_pos=(Z, (0.3, 0.2, 0)))
idle("curious", "Curious Head-Tilt Stance", IDLE + " && q.trait_curiosity > 0.75", 110, 3.2, group="idle", weight=3,
     head=(tilt(4, 0, 10), (3, 8, 6)), body=(tilt(2), (0.6, 2, 0)), right_arm=(arm('r', 0, 4), (1.5, 0, 1)), left_arm=(arm('l', 0, 4), (1.5, 0, 1), 0.5))
idle("energetic", "Bouncing Stance", IDLE + " && q.trait_energy > 0.78", 110, 0.8, group="idle", weight=3,
     head=(tilt(0), (2, 0, 0)), right_arm=(arm('r', 4, 6), (5, 0, 2)), left_arm=(arm('l', 4, 6), (5, 0, 2), 0.5),
     right_leg=(leg('r', 0, 2), (4, 0, 0)), left_leg=(leg('l', 0, 2), (-4, 0, 0)), root_pos=(Z, (0, 0.6, 0)))
idle("night_watch", "Night Watch Stance", IDLE + " && q.is_night && q.light < 8", 112, 5.0, group="idle_night", weight=4,
     head=(tilt(-2), (2, 22, 0)), body=(tilt(2), (0.6, 6, 0)), right_arm=(arm('r', 6, 6), (1, 0, 0)), left_arm=(arm('l', 6, 6), (1, 0, 0)))
idle("heat", "Heat-Weary Stance", IDLE + " && q.dimension == 'the_nether'", 111, 2.2, group="idle_heat", weight=4,
     head=(tilt(8), (2, 0, 2)), body=(tilt(5), (1.5, 0, 1.0)), right_arm=(arm('r', -2, 14), (2, 0, 2)), left_arm=(arm('l', -2, 14), (2, 0, 2), 0.5),
     root_pos=(Z, (0, 0.45, 0)))
idle("wind_brace", "Braced Against Wind", IDLE + " && q.wind > 0.75", 118, 1.4, group="idle_wind", weight=4,
     head=(tilt(10, 0, 4), (2, 3, 2)), body=(tilt(8, 0, 6), (2, 0, 2)), right_arm=(arm('r', 26, -6, 20), (3, 0, 0)), left_arm=(arm('l', 4, 10), (5, 0, 4)),
     right_leg=(leg('r', -6, 8), Z), left_leg=(leg('l', 8, 8), Z))
idle("waiting_long", "Bored Waiting", IDLE + " && q.idle_time > 25", 105, 6.0, group="idle_bored", weight=4,
     head=(tilt(10, 0, 6), (4, 14, 4)), body=(tilt(4, 0, 4), (2, 3, 2)), right_arm=(arm('r', 26, -8, 30), (2, 0, 0)), left_arm=(arm('l', 26, -8, 30), (2, 0, 0)),
     right_leg=(leg('r', 0, 2), Z), left_leg=(leg('l', -6, 2, 10), Z))


def fidget(cid, name, when, length, weight=1, group="idle", priority=100, file="player/idle"):
    return Clip("player.idle." + cid, name, CAT, T, length=length, loop="once", layer="base", priority=priority,
                trigger=state(when, group=group, weight=weight), blend_in=0.3, blend_out=0.35, file=file)


c = fidget("look_left", "Glance Left", IDLE, 2.4)
c.rot("head", (0, Z), (0.5, tilt(-2, -55), "out_cubic"), (1.6, tilt(-2, -58)), (2.4, Z, "in_out_sine"))
c.rot("body", (0, Z), (0.6, tilt(0, -12), "out_cubic"), (1.6, tilt(0, -13)), (2.4, Z, "in_out_sine"))
c = fidget("look_right", "Glance Right Over Shoulder", IDLE, 2.8)
c.rot("head", (0, Z), (0.6, tilt(-4, 70), "out_cubic"), (1.9, tilt(-6, 72)), (2.8, Z, "in_out_sine"))
c.rot("body", (0, Z), (0.7, tilt(0, 22), "out_cubic"), (1.9, tilt(0, 24)), (2.8, Z, "in_out_sine"))
c.rot("right_leg", (0, Z), (0.7, leg('r', -6, 0, 18)), (2.8, Z))
c = fidget("stretch_arms", "Overhead Stretch", IDLE, 3.2)
c.rot("right_arm", (0, Z), (0.8, arm('r', 170, 10), "in_out_sine"), (1.6, arm('r', 176, 18)), (2.2, arm('r', 160, 30)), (3.2, Z, "in_out_sine"))
c.rot("left_arm", (0, Z), (0.8, arm('l', 170, 10), "in_out_sine"), (1.6, arm('l', 176, 18)), (2.2, arm('l', 160, 30)), (3.2, Z, "in_out_sine"))
c.rot("body", (0, Z), (1.0, tilt(-10)), (1.6, tilt(-12)), (3.2, Z))
c.rot("head", (0, Z), (1.0, tilt(-22)), (1.7, tilt(-24)), (3.2, Z))
c.pos("mw_root", (0, Z), (1.2, move(0, 0.6)), (3.2, Z))
c.ev(0.9, "foley", kind="armor", volume=0.6)
c = fidget("roll_shoulders", "Shoulder Roll", IDLE, 2.2)
for side in ('r', 'l'):
    c.rot(side == 'r' and "right_arm" or "left_arm", (0, Z), (0.5, arm(side, 0, 8)), (0.9, arm(side, -10, 4)), (1.3, arm(side, 6, 2)), (2.2, Z), lerp="smooth")
c.pos("right_arm", (0, Z), (0.5, move(0, 1)), (1.0, move(0, 0, -0.5)), (2.2, Z), lerp="smooth")
c.pos("left_arm", (0, Z), (0.5, move(0, 1)), (1.0, move(0, 0, -0.5)), (2.2, Z), lerp="smooth")
c.rot("head", (0, Z), (0.8, tilt(-6)), (2.2, Z))
c = fidget("neck_crack", "Neck Crack", IDLE, 2.0)
c.rot("head", (0, Z), (0.4, tilt(4, 0, 28), "in_out_cubic"), (0.55, tilt(6, 0, 34), "out_back"), (1.0, tilt(4, 0, -26), "in_out_cubic"), (1.15, tilt(6, 0, -32), "out_back"), (2.0, Z))
c.ev(0.55, "sound", sound="motionworks:emote.snap", volume=0.25, pitch=0.6)
c = fidget("check_hands", "Inspect Hands", IDLE, 3.0)
c.rot("right_arm", (0, Z), (0.6, arm('r', 60, -18, 30)), (1.6, arm('r', 62, -16, -40)), (2.3, arm('r', 58, -18, 30)), (3.0, Z), lerp="smooth")
c.rot("left_arm", (0, Z), (0.7, arm('l', 54, -16, 30)), (1.7, arm('l', 56, -14, -36)), (2.4, arm('l', 52, -16, 30)), (3.0, Z), lerp="smooth")
c.rot("head", (0, Z), (0.6, tilt(30)), (2.4, tilt(30, 6)), (3.0, Z), lerp="smooth")
c = fidget("shift_weight", "Weight Shift", IDLE, 2.6, weight=2)
c.rot("mw_root", (0, Z), (0.9, tilt(0, 0, 4), "in_out_sine"), (1.7, tilt(0, 0, 4)), (2.6, Z, "in_out_sine"))
c.rot("right_leg", (0, Z), (0.9, leg('r', 4, -3)), (1.7, leg('r', 4, -3)), (2.6, Z))
c.rot("left_leg", (0, Z), (0.9, leg('l', -2, 6, 8)), (1.7, leg('l', -2, 6, 8)), (2.6, Z))
c.rot("body", (0, Z), (0.9, tilt(0, 0, -3)), (1.7, tilt(0, 0, -3)), (2.6, Z))
c = fidget("scratch_head", "Head Scratch", IDLE, 2.6)
c.rot("right_arm", (0, Z), (0.5, arm('r', 150, -20, 40), "out_cubic"), (0.7, arm('r', 156, -16, 40)), (0.9, arm('r', 150, -20, 40)), (1.1, arm('r', 156, -16, 40)),
      (1.3, arm('r', 150, -20, 40)), (1.5, arm('r', 156, -16, 40)), (2.6, Z, "in_out_sine"))
c.rot("head", (0, Z), (0.5, tilt(8, 10, 8)), (1.6, tilt(8, 12, 10)), (2.6, Z))
c = fidget("tap_foot", "Impatient Foot Tap", IDLE + " && q.idle_time > 8", 2.4)
for i in range(4):
    t = 0.3 + i * 0.45
    c.key("left_leg", "rotation", t, leg('l', 14, 2, 10), "out_quad").key("left_leg", "rotation", t + 0.2, leg('l', 2, 2, 10), "in_quad")
    c.ev(t + 0.2, "footstep", foot="left", weight="0.4")
c.key("left_leg", "rotation", 0, Z).key("left_leg", "rotation", 2.4, Z)
c.rot("right_arm", (0, Z), (0.3, arm('r', 0, -20, 50)), (2.1, arm('r', 0, -20, 50)), (2.4, Z))
c.rot("left_arm", (0, Z), (0.3, arm('l', 0, -20, 50)), (2.1, arm('l', 0, -20, 50)), (2.4, Z))
c = fidget("look_up_sky", "Look Up At Sky", IDLE + " && q.light > 12", 3.4)
c.rot("head", (0, Z), (0.8, tilt(-55, 10), "in_out_sine"), (2.4, tilt(-58, -12), "in_out_sine"), (3.4, Z, "in_out_sine"))
c.rot("body", (0, Z), (0.8, tilt(-6)), (2.4, tilt(-7)), (3.4, Z))
c = fidget("brush_off", "Brush Off Dust", IDLE, 2.2)
c.rot("right_arm", (0, Z), (0.3, arm('r', 30, -24, 20)), (0.5, arm('r', 22, -10, 20), "out_quad"), (0.7, arm('r', 30, -24, 20)), (0.9, arm('r', 22, -10, 20), "out_quad"), (2.2, Z))
c.rot("left_arm", (0, Z), (1.0, arm('l', 32, -24, 20)), (1.2, arm('l', 24, -10, 20), "out_quad"), (1.4, arm('l', 32, -24, 20)), (2.2, Z))
c.rot("head", (0, Z), (0.3, tilt(30, -8)), (1.4, tilt(30, 8)), (2.2, Z))
c.ev(0.5, "particle", particle="dust_puff", count="2", at="center", spread="0.4").ev(1.2, "particle", particle="dust_puff", count="2", at="center", spread="0.4")
c = fidget("adjust_belt", "Adjust Belt", IDLE, 2.0)
c.rot("right_arm", (0, Z), (0.4, arm('r', 18, -20, 30)), (1.3, arm('r', 20, -22, 30)), (2.0, Z), lerp="smooth")
c.rot("left_arm", (0, Z), (0.4, arm('l', 18, -20, 30)), (1.3, arm('l', 20, -22, 30)), (2.0, Z), lerp="smooth")
c.pos("mw_root", (0, Z), (0.6, move(0, 0.5)), (0.8, move(0, -0.2)), (2.0, Z), lerp="smooth")
c.rot("head", (0, Z), (0.4, tilt(24)), (1.4, tilt(24)), (2.0, Z))
c.ev(0.7, "foley", kind="leather", volume=0.7)
c = fidget("sigh", "Deep Sigh", IDLE + " && q.mood < 0.1", 2.8)
c.rot("body", (0, Z), (1.0, tilt(-6), "in_out_sine"), (1.6, tilt(8), "out_quad"), (2.8, Z, "in_out_sine"))
c.rot("head", (0, Z), (1.0, tilt(-12)), (1.7, tilt(16)), (2.8, Z))
c.pos("mw_root", (0, Z), (1.0, move(0, 0.4)), (1.7, move(0, -0.5)), (2.8, Z))
c.rot("right_arm", (0, Z), (1.0, arm('r', -4, 6)), (1.7, arm('r', 2, 1)), (2.8, Z))
c.rot("left_arm", (0, Z), (1.0, arm('l', -4, 6)), (1.7, arm('l', 2, 1)), (2.8, Z))
c = fidget("yawn", "Yawn And Stretch", IDLE + " && q.is_night", 3.6, weight=2)
c.rot("head", (0, Z), (0.8, tilt(-30)), (2.0, tilt(-34)), (2.6, tilt(6)), (3.6, Z), lerp="smooth")
c.rot("right_arm", (0, Z), (0.9, arm('r', 130, 40)), (2.0, arm('r', 140, 50)), (3.6, Z), lerp="smooth")
c.rot("left_arm", (0, Z), (1.0, arm('l', 40, -20, 40)), (2.0, arm('l', 46, -22, 40)), (3.6, Z), lerp="smooth")
c.rot("body", (0, Z), (1.0, tilt(-8)), (2.0, tilt(-10)), (3.6, Z))
c = fidget("shiver", "Full-Body Shiver", IDLE + " && q.is_cold", 1.6, group="idle_cold", priority=121)
shake(c, "body", tilt(6), 2, 4, 9, 0.1, 1.4)
shake(c, "head", tilt(10), 2, 3, 9, 0.1, 1.4)
c.rot("right_arm", (0, arm('r', 40, -14, 34)), (1.6, arm('r', 40, -14, 34)))
c.rot("left_arm", (0, arm('l', 40, -14, 34)), (1.6, arm('l', 40, -14, 34)))
c = fidget("wipe_brow", "Wipe Brow", IDLE + " && (q.dimension == 'the_nether' || q.exertion > 0.5)", 2.2)
c.rot("right_arm", (0, Z), (0.5, arm('r', 140, -30, 60)), (0.8, arm('r', 136, -6, 60)), (1.1, arm('r', 132, 14, 60)), (2.2, Z), lerp="smooth")
c.rot("head", (0, Z), (0.5, tilt(-10)), (1.1, tilt(-6, 0, 6)), (2.2, Z))
c.rot("body", (0, Z), (0.6, tilt(-4)), (2.2, Z))
c = fidget("look_down_feet", "Check Footing", IDLE, 2.0)
c.rot("head", (0, Z), (0.5, tilt(48, -10)), (1.3, tilt(48, 12)), (2.0, Z), lerp="smooth")
c.rot("right_leg", (0, Z), (0.8, leg('r', 6, 2, 16)), (1.4, leg('r', 6, 2, -10)), (2.0, Z), lerp="smooth")
c = fidget("kick_pebble", "Kick A Pebble", IDLE + " && q.idle_time > 12", 1.8, group="idle_bored", priority=105)
strike(c, "right_leg", Z, leg('r', -24), leg('r', 40), leg('r', 30), 0.4, 0.55, 0.8, 1.8)
c.rot("mw_root", (0, Z), (0.4, tilt(-3, 0, 3)), (0.6, tilt(2, 0, 3)), (1.8, Z))
c.rot("right_arm", (0, Z), (0.55, arm('r', -20, 10)), (1.8, Z))
c.rot("left_arm", (0, Z), (0.55, arm('l', 20, 14)), (1.8, Z))
c.ev(0.55, "particle", particle="dust_puff", count="1", at="front", spread="0.2")
c = fidget("whistle_sway", "Whistling Sway", IDLE + " && q.mood > 0.4", 3.6, group="idle_bored", priority=105)
c.cycle("mw_root", "rotation", lambda u: tilt(0, 0, 3 * wave(u, 0, 2)))
c.cycle("head", "rotation", lambda u: tilt(-6, 0, 6 * wave(u, 0.1, 2)))
c.rot("right_arm", (0, arm('r', 6, -22, 40)), (3.6, arm('r', 6, -22, 40)))
c.rot("left_arm", (0, arm('l', 6, -22, 40)), (3.6, arm('l', 6, -22, 40)))
c.ev(0.4, "sound", sound="motionworks:emote.whistle", volume=0.4)
c = fidget("check_clock", "Check The Time", IDLE + " && q.main_hand == 'device'", 2.6, group="idle", priority=100, weight=2)
c.rot("right_arm", (0, Z), (0.5, arm('r', 70, -20, 20), "out_cubic"), (2.0, arm('r', 72, -20, 22)), (2.6, Z))
c.rot("head", (0, Z), (0.5, tilt(36, 6)), (2.0, tilt(38, 6)), (2.6, Z))

"""Player locomotion part 2: turning, starts/stops, airborne, landing, climbing, modifiers, carrying."""
from core import Clip, state, event, arm, leg, tilt, move, biped, strike, shake, wave, cwave
from player_locomotion import CAT, T, ALIVE, GROUNDED, IDLE, WALKING, CYCLE

Z = (0, 0, 0)
F = "player/transitions"


def one(cid, name, trig, length, priority=150, layer="action", mask=None, blend_in=0.1, blend_out=0.25, file=F, interrupt_after=0.5):
    return Clip("player.locomotion." + cid, name, CAT, T, length=length, loop="once", layer=layer, priority=priority, trigger=trig,
                blend_in=blend_in, blend_out=blend_out, mask=mask, file=file, interrupt_after=interrupt_after)


# --- turning in place: one direction-adaptive clip per turn size (sign follows q.turn_rate)
TURN = "(q.turn_rate > 0 ? 1 : -1)"
for cid, name, cond, big in (("turn_shuffle", "Shuffle Turn", "math.abs(q.turn_rate) > 3 && math.abs(q.turn_rate) < 14", False),
                             ("turn_pivot", "Pivot Turn", "math.abs(q.turn_rate) >= 14", True)):
    c = Clip("player.locomotion." + cid, name, CAT, T, length=0.6 if big else 0.8, loop="loop", layer="base", priority=150,
             trigger=state(IDLE + " && " + cond, exit_delay=0.25), blend_in=0.12, blend_out=0.3, file=F)
    amp = 26 if big else 14
    c.cycle("right_leg", "rotation", lambda u, amp=amp: [-amp * max(0, wave(u)), 0, 0])
    c.cycle("left_leg", "rotation", lambda u, amp=amp: [-amp * 0.7 * max(0, -wave(u)), 0, 0])
    for k in range(9):
        t = c.length * k / 8
        c.key("body", "rotation", t, [0, "%g * %s" % ((10 if big else 5) * (1 + 0.2 * wave(k / 8)), TURN), 0], lerp="smooth")
        c.key("head", "rotation", t, [0, "%g * %s" % ((16 if big else 8), TURN), 0], lerp="smooth")
    c.cycle("mw_root", "position", lambda u: move(0, 0.4 * abs(wave(u))))
    if big:
        # A pivot plants one foot and swings the other wide, arms counter-rotating for balance.
        c.cycle("right_leg", "rotation", lambda u: leg('r', 30 * max(0, wave(u)), 18 * max(0, wave(u)), 20))
        c.cycle("right_arm", "rotation", lambda u: arm('r', -20 * wave(u), 14))
        c.cycle("left_arm", "rotation", lambda u: arm('l', 20 * wave(u), 14))
        c.cycle("mw_root", "rotation", lambda u: tilt(4, 0, 5 * wave(u, 0.25)))
    c.ev(0.0, "footstep", foot="right", weight="0.5")

# --- starts, stops and direction changes (action layer, lower body + torso)
c = one("start_walk", "Walk Start Lean", event("start_moving", "!q.is_sprinting && q.is_on_ground && !q.is_sneaking"), 0.45, mask=["body", "head", "mw_root"])
c.rot("body", (0, Z), (0.15, tilt(8)), (0.45, Z, "in_out_sine"))
c.rot("mw_root", (0, Z), (0.12, tilt(3)), (0.45, Z))
c = one("start_sprint", "Sprint Burst", event("sprint_start", "q.is_on_ground"), 0.55, mask=["body", "head", "right_arm", "left_arm", "mw_root"])
c.rot("body", (0, Z), (0.12, tilt(22), "out_quad"), (0.55, tilt(10), "in_out_sine"))
c.rot("right_arm", (0, Z), (0.12, arm('r', -50, 6), "out_quad"), (0.55, arm('r', 10, 4)))
c.rot("left_arm", (0, Z), (0.12, arm('l', 60, 6), "out_quad"), (0.55, arm('l', -10, 4)))
c.pos("mw_root", (0, Z), (0.12, move(0, -1.2, 1)), (0.55, Z))
c.ev(0.05, "footstep", foot="right", weight="1.4")
c = one("stop_walk", "Walk Stop Settle", event("stop_moving", "q.is_on_ground && !q.is_sprinting && q.move_time > 0.4"), 0.5, priority=140)
c.rot("body", (0, tilt(4)), (0.15, tilt(-4)), (0.5, Z, "out_back"))
c.rot("right_leg", (0, leg('r', 14)), (0.2, leg('r', -2)), (0.5, Z))
c.rot("left_leg", (0, leg('l', -10)), (0.2, leg('l', 3)), (0.5, Z))
c.rot("right_arm", (0, arm('r', -12)), (0.25, arm('r', 6)), (0.5, Z))
c.rot("left_arm", (0, arm('l', 12)), (0.25, arm('l', -6)), (0.5, Z))
c.ev(0.15, "footstep", foot="left", weight="0.7")
c = one("stop_run_skid", "Running Skid Stop", event("sprint_stop", "q.is_on_ground && q.ground_speed > 0.12"), 0.7, priority=160)
c.rot("body", (0, tilt(14)), (0.18, tilt(-16), "out_quad"), (0.4, tilt(-6)), (0.7, Z, "in_out_sine"))
c.rot("right_leg", (0, leg('r', 30, 6)), (0.2, leg('r', 34, 10)), (0.7, Z))
c.rot("left_leg", (0, leg('l', -20, 6)), (0.2, leg('l', -14, 8)), (0.7, Z))
c.rot("right_arm", (0, arm('r', -40, 10)), (0.2, arm('r', 30, 30)), (0.7, Z))
c.rot("left_arm", (0, arm('l', 40, 10)), (0.2, arm('l', 20, 34)), (0.7, Z))
c.pos("mw_root", (0, Z), (0.2, move(0, -1.6)), (0.7, Z))
c.ev(0.1, "footstep", foot="right", weight="1.6").ev(0.2, "particle", particle="dust_puff", count="4", at="feet", spread="0.6")
c = one("stop_hard_brace", "Hard Stop Brace", event("stop_moving", "q.is_on_ground && q.is_sprinting"), 0.65, priority=161)
c.rot("mw_root", (0, Z), (0.1, tilt(-10), "out_expo"), (0.3, tilt(4)), (0.65, Z, "out_back"))
c.rot("right_arm", (0, Z), (0.12, arm('r', 20, 40)), (0.65, Z))
c.rot("left_arm", (0, Z), (0.12, arm('l', 20, 40)), (0.65, Z))
c.rot("right_leg", (0, Z), (0.12, leg('r', 24)), (0.65, Z))
c = one("pivot_180", "180 Degree Pivot", event("start_moving", "math.abs(q.turn_rate) > 30"), 0.5, priority=170)
c.rot("mw_root", (0, tilt(0, -40)), (0.25, tilt(4, 10), "out_cubic"), (0.5, Z))
c.rot("body", (0, tilt(0, -20)), (0.3, tilt(6, 4)), (0.5, Z))
c.rot("right_leg", (0, leg('r', 20, 10)), (0.25, leg('r', -10)), (0.5, Z))
c.ev(0.1, "footstep", foot="right", weight="1.2")
for cid, name, when, sign in (("accel_lean", "Acceleration Lean", "q.acceleration > 0.4 && q.is_on_ground", 1), ("decel_lean", "Deceleration Lean", "q.acceleration < -0.4 && q.is_on_ground", -1)):
    c = Clip("player.locomotion." + cid, name, CAT, T, length=0.4, loop="loop", layer="additive", priority=50,
             trigger=state(ALIVE + " && " + when, exit_delay=0.15), blend_in=0.12, blend_out=0.3, file=F)
    c.rot("mw_root", (0, tilt(5 * sign)), (0.2, tilt(6 * sign)), (0.4, tilt(5 * sign)), lerp="smooth")
    c.rot("head", (0, tilt(-3 * sign)), (0.4, tilt(-3 * sign)))

# --- jumping and airborne
AIR = ALIVE + " && !q.is_on_ground && !q.is_climbing && !q.is_in_water"
c = one("jump_standing", "Standing Jump", event("jump", "q.ground_speed < 0.05"), 0.5, priority=180)
c.rot("right_leg", (0, leg('r', 10)), (0.2, leg('r', 30)), (0.5, leg('r', 10)))
c.rot("left_leg", (0, leg('l', 10)), (0.2, leg('l', -6)), (0.5, leg('l', 14)))
c.rot("right_arm", (0, arm('r', -20, 6)), (0.15, arm('r', 60, 24)), (0.5, arm('r', 20, 20)))
c.rot("left_arm", (0, arm('l', -20, 6)), (0.15, arm('l', 60, 24)), (0.5, arm('l', 20, 20)))
c.rot("body", (0, tilt(10)), (0.15, tilt(-6)), (0.5, Z))
c.ev(0.0, "foley", kind="cloth", volume=0.5)
c = one("jump_running", "Running Leap", event("jump", "q.ground_speed >= 0.05 && !q.is_sprinting"), 0.55, priority=181)
c.rot("right_leg", (0, leg('r', -20)), (0.2, leg('r', 40)), (0.55, leg('r', 20)))
c.rot("left_leg", (0, leg('l', 20)), (0.2, leg('l', -30)), (0.55, leg('l', -10)))
c.rot("right_arm", (0, arm('r', 30)), (0.2, arm('r', -40, 10)), (0.55, arm('r', -10, 10)))
c.rot("left_arm", (0, arm('l', -30)), (0.2, arm('l', 50, 10)), (0.55, arm('l', 10, 10)))
c.rot("body", (0, tilt(6)), (0.2, tilt(-2)), (0.55, tilt(4)))
c = one("jump_sprint_leap", "Sprint Long Jump", event("jump", "q.is_sprinting"), 0.7, priority=182)
c.rot("right_leg", (0, leg('r', -30)), (0.25, leg('r', 56)), (0.7, leg('r', 30)))
c.rot("left_leg", (0, leg('l', 30)), (0.25, leg('l', -40)), (0.7, leg('l', -20)))
c.rot("right_arm", (0, arm('r', 40)), (0.25, arm('r', -80, 20)), (0.7, arm('r', -30, 20)))
c.rot("left_arm", (0, arm('l', -40)), (0.25, arm('l', 90, 24)), (0.7, arm('l', 30, 20)))
c.rot("body", (0, tilt(16)), (0.25, tilt(4)), (0.7, tilt(10)))
c.ev(0.0, "foley", kind="armor", volume=0.7)
c = one("jump_from_sneak", "Coiled Crouch Jump", event("jump", "q.is_sneaking"), 0.5, priority=183)
c.rot("right_leg", (0, leg('r', 30)), (0.18, leg('r', -10)), (0.5, leg('r', 20)))
c.rot("left_leg", (0, leg('l', 30)), (0.18, leg('l', -10)), (0.5, leg('l', 20)))
c.rot("body", (0, tilt(24)), (0.18, tilt(-4)), (0.5, tilt(6)))
c.rot("right_arm", (0, arm('r', -30, 10)), (0.18, arm('r', 100, 20)), (0.5, arm('r', 40, 20)))
c.rot("left_arm", (0, arm('l', -30, 10)), (0.18, arm('l', 100, 20)), (0.5, arm('l', 40, 20)))
c = one("jump_backward", "Backward Hop", event("jump", "q.forward_speed < -0.05"), 0.5, priority=184)
c.rot("mw_root", (0, tilt(-6)), (0.25, tilt(-10)), (0.5, tilt(-2)))
c.rot("right_leg", (0, leg('r', -14)), (0.25, leg('r', -24)), (0.5, leg('r', -6)))
c.rot("left_leg", (0, leg('l', -10)), (0.25, leg('l', -20)), (0.5, leg('l', -4)))
c.rot("right_arm", (0, arm('r', 20, 20)), (0.25, arm('r', 40, 30)), (0.5, arm('r', 10, 14)))
c.rot("left_arm", (0, arm('l', 20, 20)), (0.25, arm('l', 40, 30)), (0.5, arm('l', 10, 14)))
c = one("jump_sideways", "Sideways Hop", event("jump", "math.abs(q.strafe_speed) > 0.05 && math.abs(q.forward_speed) < 0.05"), 0.5, priority=184)
c.rot("mw_root", (0, tilt(0, 0, 6)), (0.25, tilt(0, 0, 10)), (0.5, tilt(0, 0, 3)))
c.rot("right_leg", (0, leg('r', 0, 16)), (0.25, leg('r', 0, 24)), (0.5, leg('r', 0, 6)))
c.rot("left_leg", (0, leg('l', 0, 6)), (0.25, leg('l', 0, 16)), (0.5, leg('l', 0, 4)))
c.rot("right_arm", (0, arm('r', 0, 30)), (0.25, arm('r', 0, 50)), (0.5, arm('r', 0, 20)))
c.rot("left_arm", (0, arm('l', 0, 30)), (0.25, arm('l', 0, 50)), (0.5, arm('l', 0, 20)))
c = one("step_up_hop", "Step-Up Hop", event("jump", "q.ground_speed > 0.05 && q.vertical_speed < 0.45 && q.vertical_speed > 0.2"), 0.35, priority=185)
c.rot("right_leg", (0, leg('r', 40)), (0.15, leg('r', 50)), (0.35, Z))
c.rot("left_leg", (0, leg('l', -10)), (0.35, Z))
c.rot("body", (0, tilt(10)), (0.35, Z))

for cid, name, cond, pri, arms_up, legs_spread, flail in (
        ("air_rise", "Airborne Rise", "q.vertical_speed > 0.05", 500, 25, 10, 0),
        ("air_apex", "Airborne Apex Tuck", "math.abs(q.vertical_speed) <= 0.05 && q.air_time > 0.2", 501, 40, 18, 0),
        ("fall_short", "Short Fall", "q.vertical_speed < -0.05 && q.fall_distance < 4", 502, 55, 14, 0),
        ("fall_long", "Flailing Fall", "q.fall_distance >= 4 && q.fall_distance < 12", 503, 90, 20, 30),
        ("fall_very_long", "Spread-Eagle Plummet", "q.fall_distance >= 12", 504, 120, 30, 12)):
    c = Clip("player.locomotion." + cid, name, CAT, T, length=0.8 if flail else 1.2, loop="loop", layer="base", priority=pri,
             trigger=state(AIR + " && " + cond + " && q.air_time > 0.1", exit_delay=0.05), blend_in=0.2, blend_out=0.12, file=F)
    c.cycle("right_arm", "rotation", lambda u, a=arms_up, f=flail: arm('r', a * 0.3 + f * wave(u), a * 0.7 + f * 0.5 * cwave(u)))
    c.cycle("left_arm", "rotation", lambda u, a=arms_up, f=flail: arm('l', a * 0.3 - f * wave(u, 0.3), a * 0.7 + f * 0.5 * cwave(u, 0.3)))
    c.cycle("right_leg", "rotation", lambda u, s=legs_spread, f=flail: leg('r', -8 + f * 0.6 * wave(u, 0.5), s * 0.5))
    c.cycle("left_leg", "rotation", lambda u, s=legs_spread, f=flail: leg('l', 6 - f * 0.6 * wave(u, 0.5), s * 0.5))
    c.cycle("head", "rotation", lambda u, f=flail: tilt(-10 if f else 10, f * 0.3 * wave(u), 0))
    c.cycle("body", "rotation", lambda u, f=flail: tilt(-4 if f else 4, 0, f * 0.15 * wave(u, 0.2)))

# --- landings (action layer, by fall height)
for cid, name, cond, crouch, arms_out, pri, length, heavy in (
        ("land_soft", "Soft Landing", "q.last_fall < 2.5", 10, 8, 190, 0.35, 0),
        ("land_medium", "Knees-Bent Landing", "q.last_fall >= 2.5 && q.last_fall < 5", 24, 24, 191, 0.55, 1),
        ("land_hard", "Hard Three-Point Landing", "q.last_fall >= 5", 44, 40, 192, 0.95, 2),
        ("land_sprint", "Sprint Landing Run-Out", "q.is_sprinting && q.last_fall < 5", 14, 12, 193, 0.4, 1)):
    c = one(cid, name, event("land", cond), length, priority=pri, blend_in=0.03)
    c.pos("mw_root", (0, move(0, -crouch * 0.12)), (length * 0.3, move(0, -crouch * 0.1)), (length, Z, "in_out_sine"))
    c.rot("body", (0, tilt(crouch * 0.8)), (length * 0.35, tilt(crouch * 0.6)), (length, Z, "in_out_sine"))
    c.rot("right_leg", (0, leg('r', crouch * 0.9, 6)), (length, Z, "in_out_sine"))
    c.rot("left_leg", (0, leg('l', crouch * 0.5, 6)), (length, Z, "in_out_sine"))
    c.rot("right_arm", (0, arm('r', -arms_out * 0.3 if heavy < 2 else 70, arms_out)), (length, Z, "in_out_sine"))
    c.rot("left_arm", (0, arm('l', arms_out * 0.4, arms_out)), (length, Z, "in_out_sine"))
    c.rot("head", (0, tilt(crouch * 0.4)), (length, Z))
    c.ev(0.0, "footstep", foot="left", weight=str(1 + heavy)).ev(0.02, "footstep", foot="right", weight=str(1 + heavy))
    c.ev(0.0, "sound", sound="motionworks:body.land_hard" if heavy == 2 else "motionworks:body.land_soft", volume=str(0.4 + 0.2 * heavy))
    if heavy == 2:
        c.ev(0.0, "particle", particle="dust_puff", count="6", at="feet", spread="1.0").ev(0.0, "shake", amount="0.25", radius="6")
c = one("land_roll", "Parkour Landing Roll", event("landing_roll"), 0.9, priority=195, blend_in=0.02, interrupt_after=0.85)
c.rot("mw_center", (0, Z), (0.15, tilt(60)), (0.45, tilt(250)), (0.7, tilt(355)), (0.9, tilt(360)))
c.pos("mw_center", (0, Z), (0.15, move(0, -6, 2)), (0.45, move(0, -8, 8)), (0.7, move(0, -4, 14)), (0.9, move(0, 0, 0)))
c.rot("right_leg", (0, leg('r', 60)), (0.45, leg('r', 90)), (0.9, Z))
c.rot("left_leg", (0, leg('l', 60)), (0.45, leg('l', 90)), (0.9, Z))
c.rot("right_arm", (0, arm('r', 60, 20)), (0.45, arm('r', 120, 10)), (0.9, Z))
c.rot("left_arm", (0, arm('l', 60, 20)), (0.45, arm('l', 120, 10)), (0.9, Z))
c.rot("head", (0, tilt(30)), (0.45, tilt(50)), (0.9, Z))
c.ev(0.1, "sound", sound="motionworks:body.roll", volume="0.7").ev(0.5, "particle", particle="dust_puff", count="5", at="feet", spread="0.8")

# --- climbing
CLIMB = ALIVE + " && q.is_climbing"
for cid, name, cond, dirn, reach, pri in (("ladder_up", "Ladder Climb Up", "q.vertical_speed > 0.02", 1, 150, 600),
                                          ("ladder_down", "Ladder Climb Down", "q.vertical_speed < -0.02", -1, 140, 601),
                                          ("ladder_hold", "Ladder Hold", "math.abs(q.vertical_speed) <= 0.02", 0, 145, 602)):
    c = Clip("player.locomotion." + cid, name, CAT, T, length=0.9 if dirn else 2.4, loop="loop", layer="base", priority=pri,
             trigger=state(CLIMB + " && " + cond + " && q.surface != 'leaves'", exit_delay=0.2), blend_in=0.2, file=F)
    amp = 22 if dirn else 3
    c.cycle("right_arm", "rotation", lambda u, a=amp, r_=reach: arm('r', r_ + a * wave(u), 4))
    c.cycle("left_arm", "rotation", lambda u, a=amp, r_=reach: arm('l', r_ - a * wave(u), 4))
    c.cycle("right_leg", "rotation", lambda u, a=amp: leg('r', 20 + 1.4 * a * wave(u, 0.25), 2))
    c.cycle("left_leg", "rotation", lambda u, a=amp: leg('l', 20 - 1.4 * a * wave(u, 0.25), 2))
    c.cycle("head", "rotation", lambda u, d=dirn: tilt(-12 if d >= 0 else 30, 0, 0))
    c.cycle("body", "rotation", lambda u, a=amp: tilt(-2, 0, 0.15 * a * wave(u)))
    if dirn:
        c.ev(0.0, "sound", sound="minecraft:block.ladder.step", volume="0.3").ev(0.45, "sound", sound="minecraft:block.ladder.step", volume="0.3")
for cid, name, cond, dirn, pri in (("vine_up", "Vine Scramble Up", "q.vertical_speed > 0.02", 1, 603), ("vine_down", "Vine Climb Down", "q.vertical_speed < -0.02", -1, 604),
                                   ("vine_hang", "Vine Hang", "math.abs(q.vertical_speed) <= 0.02", 0, 605)):
    c = Clip("player.locomotion." + cid, name, CAT, T, length=1.1 if dirn else 2.8, loop="loop", layer="base", priority=pri,
             trigger=state(CLIMB + " && " + cond + " && q.surface == 'leaves'", exit_delay=0.2), blend_in=0.2, file=F)
    amp = 30 if dirn else 4
    reach = 160 if dirn > 0 else (120 if dirn < 0 else 150)
    c.cycle("right_arm", "rotation", lambda u, a=amp, rc=reach, d=dirn: arm('r', rc + a * wave(u * (d or 1)), 18 + 8 * cwave(u)))
    c.cycle("left_arm", "rotation", lambda u, a=amp, rc=reach, d=dirn: arm('l', rc - a * wave(u * (d or 1)), 18 - 8 * cwave(u)))
    c.cycle("right_leg", "rotation", lambda u, a=amp, d=dirn: leg('r', (34 if d < 0 else 24) + a * wave(u * (d or 1), 0.2), 14))
    c.cycle("left_leg", "rotation", lambda u, a=amp, d=dirn: leg('l', (34 if d < 0 else 24) - a * wave(u * (d or 1), 0.2), 14))
    c.cycle("mw_root", "rotation", lambda u, a=amp: tilt(-3, 0, 0.12 * a * wave(u)))
    c.cycle("head", "rotation", lambda u, d=dirn: tilt(-28 if d > 0 else (35 if d < 0 else -10), 6 * wave(u) if d == 0 else 0, 0))
c = Clip("player.locomotion.scaffold_climb", "Scaffold Climb", CAT, T, length=0.8, loop="loop", layer="base", priority=606,
         trigger=state(ALIVE + " && !q.is_on_ground && q.vertical_speed > 0.1 && q.ground_speed < 0.02 && q.surface == 'wood' && q.air_time > 0.3", exit_delay=0.15), file=F)
c.cycle("right_arm", "rotation", lambda u: arm('r', 110 + 30 * max(0, wave(u)), 6))
c.cycle("left_arm", "rotation", lambda u: arm('l', 110 + 30 * max(0, -wave(u)), 6))
c.cycle("right_leg", "rotation", lambda u: leg('r', 50 * max(0, wave(u, 0.25))))
c.cycle("left_leg", "rotation", lambda u: leg('l', 50 * max(0, -wave(u, 0.25))))

# --- sliding
c = Clip("player.locomotion.slide_ice", "Ice Glide", CAT, T, length=1.6, loop="loop", layer="base", priority=245,
         trigger=state(GROUNDED + " && q.surface == 'glass' && q.ground_speed > 0.18", exit_delay=0.2), blend_in=0.3, file=F)
c.cycle("right_arm", "rotation", lambda u: arm('r', 10 + 6 * wave(u), 40 + 10 * wave(u, 0.3)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 10 - 6 * wave(u), 40 - 10 * wave(u, 0.3)))
c.cycle("right_leg", "rotation", lambda u: leg('r', -18, 6))
c.cycle("left_leg", "rotation", lambda u: leg('l', 22, 6))
c.cycle("mw_root", "rotation", lambda u: tilt(4, 0, 5 * wave(u)))
c.cycle("body", "rotation", lambda u: tilt(14, 0, 0))
c = Clip("player.locomotion.slide_slope", "Slope Slide", CAT, T, length=1.0, loop="loop", layer="base", priority=246,
         trigger=state(ALIVE + " && q.is_on_ground && q.vertical_speed < -0.25 && q.ground_speed > 0.15 && q.surface != 'glass'", exit_delay=0.15), file=F)
c.cycle("right_leg", "rotation", lambda u: leg('r', 40, 8))
c.cycle("left_leg", "rotation", lambda u: leg('l', -8, 8))
c.cycle("right_arm", "rotation", lambda u: arm('r', -10, 50 + 6 * wave(u, 0, 2)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 30, 40 + 6 * wave(u, 0.3, 2)))
c.cycle("mw_root", "rotation", lambda u: tilt(-14, 20, 3 * wave(u, 0, 2)))
c.ev(0.0, "particle", particle="dust_puff", count="2", at="feet", spread="0.4")

# --- additive modifiers on top of any locomotion
ADD = "player/modifiers"
for cid, name, when, rot_bone, keys in (
        ("breathing", "Breathing", ALIVE + " && !q.is_underwater", "body", None),
        ("breathing_heavy", "Heavy Breathing", ALIVE + " && q.exertion > 0.55 && !q.is_underwater", "body", None),
        ("lean_turn", "Lean Into Turns", ALIVE + " && q.ground_speed > 0.1", "mw_root", None),
        ("head_stabilize", "Head Stabilisation", ALIVE + " && q.ground_speed > 0.15", "head", None),
        ("wind_lean", "Lean Into Wind", ALIVE + " && q.wind > 0.65 && q.ground_speed > 0.02", "mw_root", None),
        ("armor_clank", "Armour Jostle", ALIVE + " && q.armor_weight > 0.4 && q.ground_speed > 0.05", "body", None),
        ("uphill_lean", "Climbing Lean", ALIVE + " && q.terrain_pitch > 10", "mw_root", None),
        ("downhill_lean", "Descending Lean", ALIVE + " && q.terrain_pitch < -10", "mw_root", None),
        ("cold_tremble", "Cold Tremor", ALIVE + " && q.freezing > 0.2", "body", None),
        ("fear_tremble", "Fear Tremor", ALIVE + " && q.near_hostile && q.health < 0.4", "head", None)):
    c = Clip("player.modifier." + cid, name, CAT, T, length=3.0, loop="loop", layer="additive", priority=10,
             trigger=state(when, exit_delay=0.3), blend_in=0.5, blend_out=0.6, file=ADD)
    if cid == "breathing":
        c.cycle("body", "scale", lambda u: [1 + 0.012 * wave(u), 1 + 0.008 * wave(u), 1 + 0.02 * wave(u)])
        c.cycle("head", "rotation", lambda u: tilt(-0.8 * wave(u)))
        c.cycle("right_arm", "rotation", lambda u: arm('r', 0, 0.8 * wave(u)))
        c.cycle("left_arm", "rotation", lambda u: arm('l', 0, 0.8 * wave(u)))
    elif cid == "breathing_heavy":
        c.length = 0.9
        c.cycle("body", "scale", lambda u: [1 + 0.03 * wave(u), 1 + 0.015 * wave(u), 1 + 0.05 * wave(u)])
        c.cycle("body", "rotation", lambda u: tilt(3 * wave(u)))
        c.cycle("head", "rotation", lambda u: tilt(-3 * wave(u)))
        c.cycle("right_arm", "position", lambda u: move(0, 0.4 * wave(u)))
        c.cycle("left_arm", "position", lambda u: move(0, 0.4 * wave(u)))
        c.ev(0.0, "breath")
    elif cid == "lean_turn":
        c.key("mw_root", "rotation", 0, [0, 0, "math.clamp(q.turn_rate * 0.5, -10, 10)"])
        c.key("body", "rotation", 0, [0, "math.clamp(q.turn_rate * 0.6, -12, 12)", 0])
    elif cid == "head_stabilize":
        c.key("head", "rotation", 0, ["math.clamp(-q.vertical_speed * 40, -8, 8)", 0, 0])
    elif cid == "wind_lean":
        c.length = 2.0
        c.cycle("mw_root", "rotation", lambda u: tilt(5 + 2 * wave(u, 0, 2), 0, 2 * wave(u)))
        c.cycle("head", "rotation", lambda u: tilt(6, 0, 0))
    elif cid == "armor_clank":
        c.length = 0.5
        c.cycle("right_arm", "rotation", lambda u: arm('r', 0, 2 + 2 * wave(u, 0, 2)))
        c.cycle("left_arm", "rotation", lambda u: arm('l', 0, 2 + 2 * wave(u, 0.5, 2)))
        c.cycle("body", "position", lambda u: move(0, 0.3 * wave(u, 0, 2)))
        c.ev(0.25, "foley", kind="armor", volume=0.3)
    elif cid == "uphill_lean":
        c.key("mw_root", "rotation", 0, ["math.clamp(q.terrain_pitch * 0.4, 0, 12)", 0, 0])
        c.key("head", "rotation", 0, ["math.clamp(-q.terrain_pitch * 0.3, -10, 0)", 0, 0])
    elif cid == "downhill_lean":
        c.key("mw_root", "rotation", 0, ["math.clamp(q.terrain_pitch * 0.3, -10, 0)", 0, 0])
        c.key("right_arm", "rotation", 0, arm('r', 0, 10))
        c.key("left_arm", "rotation", 0, arm('l', 0, 10))
    elif cid == "cold_tremble":
        c.length = 0.3
        c.cycle("body", "rotation", lambda u: tilt(0, 0, 1.2 * wave(u)))
        c.cycle("head", "rotation", lambda u: tilt(0, 1.0 * wave(u, 0.25), 0))
    elif cid == "fear_tremble":
        c.length = 0.25
        c.cycle("head", "rotation", lambda u: tilt(1.0 * wave(u), 1.5 * wave(u, 0.3), 0))
        c.cycle("right_arm", "rotation", lambda u: arm('r', 1.5 * wave(u), 0))
        c.cycle("left_arm", "rotation", lambda u: arm('l', 1.5 * wave(u, 0.5), 0))

# --- carrying equipment (overlay layer, masked to the arms). One clip per item: the hold pose is
# authored, and stride-coupled swing comes from the walk-cycle expressions so it fades out when standing.
CARRY = "player/carry"
OUT_OF_COMBAT = " && !q.in_combat && !q.is_using_item && !q.is_swinging"
SWING = "math.sin(q.limb_swing * 38.197) * q.limb_swing_amount"


def carry(item, name, rpose, lpose=None, swing=6.0, secondary=None, length=3.0):
    mask = ["right_arm", "left_arm"] if lpose else ["right_arm"]
    when = ALIVE + " && q.main_hand == '%s'" % item + OUT_OF_COMBAT
    c = Clip("player.carry." + item, name, CAT, T, length=length, loop="loop", layer="overlay", priority=100,
             trigger=state(when, exit_delay=0.15), blend_in=0.25, blend_out=0.25, mask=mask, file=CARRY)
    rx, ry, rz = arm('r', *rpose)
    c.key("right_arm", "rotation", 0, ["%g + %s * %g" % (rx, SWING, swing), ry, rz])
    if lpose:
        lx, ly, lz = arm('l', *lpose)
        c.key("left_arm", "rotation", 0, ["%g - %s * %g" % (lx, SWING, swing * 0.8), ly, lz])
    if secondary:
        secondary(c)
    return c


carry("sword", "Sword Lowered At Side", (-6, 10, -20), swing=10, secondary=lambda c: c.cycle("right_arm", "position", lambda u: move(0, 0.2 * wave(u))))
carry("axe", "Axe Rested On Shoulder", (150, -10, 40), swing=3, secondary=lambda c: c.cycle("head", "rotation", lambda u: tilt(0, 4 * wave(u), 3)))
carry("pickaxe", "Pickaxe Swinging At Side", (14, 6, -10), swing=14)
carry("shovel", "Shovel Dragged Behind", (-38, 8, 60), swing=4)
carry("hoe", "Hoe Used As Walking Staff", (24, 4, 30), swing=6)
carry("trident", "Trident Held Upright", (36, 8, -70), swing=3)
carry("bow", "Bow Held Low", (8, 14, -40), swing=8)
carry("crossbow", "Crossbow Across Body", (40, -30, 50), lpose=(36, -24, 40), swing=3)
carry("shield", "Shield Held Ready", (10, 20, -10), swing=6)
carry("torch", "Torch Raised High", (98, 14, -10), swing=4, secondary=lambda c: c.cycle("head", "rotation", lambda u: tilt(-4, 10 * wave(u), 0)))
carry("lantern", "Lantern Held Out", (34, 10, 0), swing=8, secondary=lambda c: c.cycle("right_arm", "rotation", lambda u: arm('r', 34, 10, 6 * wave(u, 0, 2))))
carry("map", "Map Held Open", (52, -12, 10), lpose=(50, -14, 10), swing=2, secondary=lambda c: c.cycle("head", "rotation", lambda u: tilt(34, 6 * wave(u), 0)))
carry("book", "Book Cradled", (46, -18, 20), lpose=(44, -16, 24), swing=2, secondary=lambda c: c.cycle("head", "rotation", lambda u: tilt(30, 0, 3 * wave(u))))
carry("food", "Snack In Hand", (34, 4, -10), swing=8)
carry("bucket", "Careful Bucket Carry", (6, 18, 0), swing=1.5, secondary=lambda c: c.cycle("right_arm", "position", lambda u: move(0, 0.4 * wave(u, 0, 2))))
carry("fishing_rod", "Fishing Rod Over Shoulder", (120, -14, -30), swing=4)
carry("block", "Block Hugged To Chest", (40, -6, 20), lpose=(38, -6, 20), swing=3)
carry("potion", "Potion Raised To Eye", (70, -6, 40), swing=3, secondary=lambda c: c.cycle("head", "rotation", lambda u: tilt(10, 8, 0)))
carry("device", "Compass Consulted", (58, -10, 20), swing=2, secondary=lambda c: c.cycle("head", "rotation", lambda u: tilt(28, 0, 0)))
carry("spyglass", "Spyglass Tapped On Palm", (30, -10, 0), lpose=(30, -20, 0), swing=5)
carry("horn", "Horn At Belt", (12, 4, 30), swing=8, secondary=lambda c: c.cycle("right_arm", "position", lambda u: move(0.3, 0, 0)))
carry("lead", "Coiled Lead Swinging", (24, 6, 0), swing=7, secondary=lambda c: c.cycle("right_arm", "rotation", lambda u: arm('r', 24, 6, 14 * wave(u, 0, 3))))
carry("throwable", "Tossing Throwable", (20, 4, 0), swing=4, secondary=lambda c: c.cycle("right_arm", "position", lambda u: move(0, max(0, wave(u, 0, 2)) * 1.5)), length=1.2)


def item_fidget(item, cid, name, length, weight=1):
    return Clip("player.idle.%s_%s" % (item, cid), name, CAT, T, length=length, loop="once", layer="overlay", priority=110,
                trigger=state(ALIVE + " && q.main_hand == '%s' && q.ground_speed < 0.02 && q.idle_time > 4" % item + OUT_OF_COMBAT,
                              group="item_fidget_" + item, weight=weight, exit_delay=0.3), blend_in=0.3, blend_out=0.35,
                mask=["right_arm", "left_arm", "head"], file=CARRY)


c = item_fidget("sword", "twirl", "Idle Sword Twirl", 2.0)
c.rot("right_arm", (0, arm('r', -6, 10, -20)), (0.4, arm('r', 40, 10, 40)), (0.8, arm('r', 40, 10, 400)), (1.2, arm('r', 40, 10, 760)), (2.0, arm('r', -6, 10, 700)), lerp="smooth")
c.rot("head", (0, Z), (0.5, tilt(20)), (1.4, tilt(22)), (2.0, Z))
c.ev(0.6, "whoosh", weight="light").ev(1.0, "whoosh", weight="light")
c = item_fidget("axe", "shoulder_shift", "Shift Axe To Other Shoulder", 2.6)
c.rot("right_arm", (0, arm('r', 150, -10, 40)), (0.6, arm('r', 100, -20, 10)), (2.0, arm('r', 100, -20, 10)), (2.6, arm('r', 150, -10, 40)), lerp="smooth")
c.rot("left_arm", (0, Z), (0.7, arm('l', 120, -10, 10)), (1.9, arm('l', 120, -10, 10)), (2.6, Z), lerp="smooth")
c.rot("head", (0, Z), (0.8, tilt(0, -20)), (1.8, tilt(0, -20)), (2.6, Z))
c = item_fidget("torch", "scan", "Torch Sweep Into Darkness", 3.2)
c.rot("right_arm", (0, arm('r', 98, 14, -10)), (1.0, arm('r', 100, 40, -10)), (2.0, arm('r', 100, -10, -10)), (3.2, arm('r', 98, 14, -10)), lerp="smooth")
c.rot("head", (0, Z), (1.0, tilt(-6, -30)), (2.0, tilt(-6, 30)), (3.2, Z), lerp="smooth")
c = item_fidget("map", "turn", "Rotate Map To Orient", 3.0)
c.rot("right_arm", (0, arm('r', 52, -12, 10)), (1.0, arm('r', 56, -4, 40)), (2.0, arm('r', 56, -4, 40)), (3.0, arm('r', 52, -12, 10)), lerp="smooth")
c.rot("left_arm", (0, arm('l', 50, -14, 10)), (1.0, arm('l', 46, -22, -20)), (2.0, arm('l', 46, -22, -20)), (3.0, arm('l', 50, -14, 10)), lerp="smooth")
c.rot("head", (0, tilt(34)), (1.0, tilt(36, 0, 14)), (2.0, tilt(36, 0, 14)), (3.0, tilt(34)), lerp="smooth")
c.ev(1.0, "sound", sound="motionworks:interact.page", volume="0.4")
c = item_fidget("food", "sniff", "Sniff The Food", 2.2)
c.rot("right_arm", (0, arm('r', 34, 4, -10)), (0.5, arm('r', 92, -24, 30), "out_cubic"), (1.6, arm('r', 94, -24, 30)), (2.2, arm('r', 34, 4, -10)))
c.rot("head", (0, Z), (0.5, tilt(14)), (0.9, tilt(10)), (1.2, tilt(14)), (2.2, Z))
c = item_fidget("bucket", "peek", "Peek Into Bucket", 2.4)
c.rot("right_arm", (0, arm('r', 6, 18, 0)), (0.6, arm('r', 40, -10, 0), "out_cubic"), (1.8, arm('r', 42, -10, 0)), (2.4, arm('r', 6, 18, 0)))
c.rot("head", (0, Z), (0.6, tilt(50, -10)), (1.8, tilt(52, -10)), (2.4, Z))
c = item_fidget("fishing_rod", "line_check", "Check The Line", 2.6)
c.rot("right_arm", (0, arm('r', 120, -14, -30)), (0.6, arm('r', 60, -10, -10)), (1.8, arm('r', 62, -10, -10)), (2.6, arm('r', 120, -14, -30)), lerp="smooth")
c.rot("left_arm", (0, Z), (0.8, arm('l', 50, -20, 30)), (1.6, arm('l', 54, -20, 30)), (2.6, Z), lerp="smooth")
c.rot("head", (0, Z), (0.8, tilt(26, -6)), (1.8, tilt(26, -6)), (2.6, Z))
c = item_fidget("crossbow", "bolt_check", "Check The Bolt", 2.4)
c.rot("right_arm", (0, arm('r', 40, -30, 50)), (0.6, arm('r', 70, -24, 30)), (1.8, arm('r', 72, -24, 30)), (2.4, arm('r', 40, -30, 50)), lerp="smooth")
c.rot("head", (0, Z), (0.6, tilt(30, -12)), (1.8, tilt(30, -12)), (2.4, Z))
c.ev(1.0, "sound", sound="motionworks:weapon.crossbow_crank", volume="0.25", pitch="1.4")
c = item_fidget("device", "tap", "Tap The Compass", 2.0)
c.rot("left_arm", (0, Z), (0.4, arm('l', 60, -30, 20)), (0.6, arm('l', 56, -30, 20)), (0.8, arm('l', 60, -30, 20)), (1.0, arm('l', 56, -30, 20)), (2.0, Z))
c.rot("head", (0, tilt(28)), (2.0, tilt(28)))
c = item_fidget("lantern", "raise_look", "Raise Lantern And Peer", 3.0)
c.rot("right_arm", (0, arm('r', 34, 10, 0)), (0.7, arm('r', 120, 20, 0), "out_cubic"), (2.2, arm('r', 122, 20, 0)), (3.0, arm('r', 34, 10, 0)))
c.rot("head", (0, Z), (0.7, tilt(-8, 20)), (1.6, tilt(-8, -16)), (2.2, tilt(-8, 0)), (3.0, Z), lerp="smooth")
c = item_fidget("spyglass", "quick_peek", "Quick Spyglass Peek", 2.4)
c.rot("right_arm", (0, arm('r', 30, -10, 0)), (0.4, arm('r', 92, -30, 0), "out_cubic"), (1.8, arm('r', 92, -30, 0)), (2.4, arm('r', 30, -10, 0)))
c.rot("head", (0, Z), (0.4, tilt(-6)), (1.0, tilt(-6, 14)), (1.8, tilt(-6, -10)), (2.4, Z), lerp="smooth")
c = item_fidget("book", "page_flip", "Flip A Page", 1.6)
c.rot("right_arm", (0, arm('r', 46, -18, 20)), (0.4, arm('r', 54, -30, -20)), (0.8, arm('r', 50, 0, 40)), (1.6, arm('r', 46, -18, 20)), lerp="smooth")
c.rot("head", (0, tilt(30)), (0.8, tilt(32, 6)), (1.6, tilt(30)))
c.ev(0.6, "sound", sound="motionworks:interact.page", volume="0.5")
c = item_fidget("horn", "polish", "Polish The Horn", 2.6)
c.rot("right_arm", (0, arm('r', 12, 4, 30)), (0.5, arm('r', 50, -10, 30)), (2.0, arm('r', 52, -10, 30)), (2.6, arm('r', 12, 4, 30)))
for i in range(5):
    c.key("left_arm", "rotation", 0.5 + i * 0.3, arm('l', 46 + (6 if i % 2 else 0), -24, 20))
c.key("left_arm", "rotation", 0, Z).key("left_arm", "rotation", 2.6, Z)
c = item_fidget("trident", "spin_plant", "Spin And Plant Trident", 2.4)
c.rot("right_arm", (0, arm('r', 36, 8, -70)), (0.5, arm('r', 60, 8, 200)), (1.0, arm('r', 60, 8, 470)), (1.4, arm('r', 30, 8, 650)), (2.4, arm('r', 36, 8, 650)))
c.ev(1.4, "sound", sound="minecraft:item.trident.hit_ground", volume="0.4")

# --- stairs, stance transitions and surface-specific landings
from player_locomotion import locomotion  # noqa: E402

locomotion("stairs_up", "Climbing Stairs", WALKING + " && q.vertical_speed > 0.04 && q.vertical_speed <= 0.15 && !q.is_sprinting", 226, cadence=0.8,
           stride=24, arm_swing=18, bob=1.4, twist=4, sway=1.5, lean=9, knee_lift=34, head_hold=(8, 0, 0))
locomotion("stairs_down", "Descending Stairs", WALKING + " && q.vertical_speed < -0.04 && q.vertical_speed >= -0.15 && !q.is_sprinting", 226, cadence=1.05,
           stride=18, arm_swing=10, arm_out=12, bob=1.8, twist=2, sway=1.0, lean=-4, head_hold=(22, 0, 0))
SNEAK = ALIVE + " && q.is_sneaking && q.is_on_ground && !q.is_climbing"
locomotion("sneak_injured", "Wounded Crouch Creep", SNEAK + " && q.ground_speed >= 0.01 && q.health < 0.3", 404, cadence=0.7, stride=16, arm_swing=4,
           bob=0.9, twist=1, sway=3, lean=10, asym=0.5, right_arm=(30, -12, 20))
c = one("sneak_enter", "Drop Into Crouch", event("sneak_start", "q.is_on_ground"), 0.35, priority=145, mask=["body", "head", "mw_root", "right_arm", "left_arm"])
c.pos("mw_root", (0, Z), (0.12, move(0, -1.2)), (0.35, move(0, -0.4), "out_back"))
c.rot("right_arm", (0, Z), (0.12, arm('r', 24, 14)), (0.35, arm('r', 14, 8)))
c.rot("left_arm", (0, Z), (0.12, arm('l', 26, 12)), (0.35, arm('l', 18, 6)))
c.ev(0.1, "foley", kind="cloth", volume=0.4)
c = one("sneak_exit", "Rise From Crouch", event("sneak_stop", "q.is_on_ground"), 0.4, priority=145, mask=["body", "head", "mw_root"])
c.pos("mw_root", (0, move(0, -0.6)), (0.2, move(0, 0.4)), (0.4, Z, "in_out_sine"))
c.rot("head", (0, tilt(8)), (0.2, tilt(-4)), (0.4, Z))
c = one("land_slime_bounce", "Slime Rebound", event("land", "q.surface == 'slime'"), 0.6, priority=196, blend_in=0.02)
c.pos("mw_root", (0, move(0, -2.5)), (0.1, move(0, -3.0), "out_quad"), (0.35, move(0, 1.0), "out_back"), (0.6, Z))
c.rot("right_arm", (0, arm('r', 0, 30)), (0.2, arm('r', 0, 70)), (0.6, Z))
c.rot("left_arm", (0, arm('l', 0, 30)), (0.2, arm('l', 0, 70)), (0.6, Z))
c.ev(0.0, "sound", sound="minecraft:block.slime_block.fall", volume="0.6")
c = one("land_ice_slip", "Ice Landing Slip", event("land", "q.surface == 'glass' && q.last_fall > 1.5"), 0.9, priority=197, blend_in=0.02)
c.rot("mw_root", (0, Z), (0.15, tilt(-8, 0, 10)), (0.35, tilt(6, 0, -8)), (0.6, tilt(-3, 0, 4)), (0.9, Z), lerp="smooth")
c.rot("right_arm", (0, Z), (0.15, arm('r', 30, 80)), (0.5, arm('r', 10, 50)), (0.9, Z), lerp="smooth")
c.rot("left_arm", (0, Z), (0.15, arm('l', -20, 70)), (0.5, arm('l', 10, 50)), (0.9, Z), lerp="smooth")
c.rot("right_leg", (0, Z), (0.2, leg('r', 30, 10)), (0.9, Z))
c = one("land_snow_sink", "Snow Plunge Landing", event("land", "q.surface == 'snow' && q.last_fall > 2"), 0.8, priority=197, blend_in=0.02)
c.pos("mw_root", (0, move(0, -3.0)), (0.3, move(0, -2.4)), (0.8, Z, "in_out_sine"))
c.rot("right_leg", (0, leg('r', 20)), (0.5, leg('r', 50)), (0.8, Z))
c.rot("left_leg", (0, leg('l', 20)), (0.6, leg('l', 10)), (0.8, Z))
c.rot("body", (0, tilt(14)), (0.8, Z))
c.ev(0.0, "particle", particle="snow_puff", count="8", at="feet", spread="1.0")
c = Clip("player.locomotion.fall_floating", "Feather-Fall Drift", CAT, T, length=2.4, loop="loop", layer="base", priority=505,
         trigger=state(AIR + " && q.vertical_speed < -0.01 && q.vertical_speed > -0.09 && q.air_time > 0.8", exit_delay=0.1), blend_in=0.5, file=F)
c.cycle("right_arm", "rotation", lambda u: arm('r', 10 + 8 * wave(u), 70 + 10 * wave(u, 0.2)))
c.cycle("left_arm", "rotation", lambda u: arm('l', 10 - 8 * wave(u), 70 + 10 * wave(u, 0.7)))
c.cycle("right_leg", "rotation", lambda u: leg('r', 6 + 6 * wave(u, 0.4), 6))
c.cycle("left_leg", "rotation", lambda u: leg('l', -4 - 6 * wave(u, 0.4), 6))
c.cycle("mw_root", "rotation", lambda u: tilt(2 * wave(u, 0, 2), 0, 4 * wave(u)))
c.cycle("head", "rotation", lambda u: tilt(-14, 10 * wave(u), 0))
c = Clip("player.locomotion.crouch_rest", "Sit On Heels", CAT, T, length=4.0, loop="loop", layer="base", priority=405,
         trigger=state(SNEAK + " && q.ground_speed < 0.01 && q.idle_time > 10", min_time=4), blend_in=0.6, file=F)
c.cycle("right_leg", "rotation", lambda u: leg('r', 70, 14))
c.cycle("left_leg", "rotation", lambda u: leg('l', 70, 14))
c.cycle("mw_root", "position", lambda u: move(0, -5.5 + 0.2 * wave(u)))
c.cycle("right_arm", "rotation", lambda u: arm('r', 50, -10, 20))
c.cycle("left_arm", "rotation", lambda u: arm('l', 50, -10, 20))
c.cycle("body", "rotation", lambda u: tilt(24 + wave(u), 0, 0))
c.cycle("head", "rotation", lambda u: tilt(-18, 8 * wave(u, 0, 1), 0))
c = one("trip_recover", "Stumble And Recover", event("land", "q.last_fall > 1.2 && q.last_fall < 3 && q.ground_speed > 0.15 && q.trait_energy > 0.8"), 0.8, priority=198, blend_in=0.03)
c.rot("mw_root", (0, Z), (0.15, tilt(18), "out_quad"), (0.4, tilt(-4)), (0.8, Z))
c.rot("right_arm", (0, Z), (0.15, arm('r', 80, 20)), (0.5, arm('r', -10, 10)), (0.8, Z))
c.rot("left_arm", (0, Z), (0.15, arm('l', 70, 30)), (0.5, arm('l', -10, 10)), (0.8, Z))
c.rot("right_leg", (0, Z), (0.2, leg('r', 40)), (0.45, leg('r', -10)), (0.8, Z))
c.ev(0.2, "footstep", foot="right", weight="1.4").ev(0.45, "footstep", foot="left", weight="1.0")

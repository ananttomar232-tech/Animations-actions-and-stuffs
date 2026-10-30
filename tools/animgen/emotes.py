"""Emotes, gestures and expressions (category: emotes).

Every emote is a manual clip with meta emote=true; the emote wheel pages them by emote_group
(gestures, celebrations, expressions, dances). They are played through the rate-limited EmotePacket
relay and stop on their own when the player walks off, gets hurt or mounts something.
"""
from core import Clip, manual, arm, leg, tilt, move, wave, cwave

CAT = "emotes"
P = "@player"
Z = (0, 0, 0)
STOP = "q.ground_speed > 0.06 || q.recent_hurt < 0.4 || q.is_riding || q.is_swimming || !q.is_on_ground"


def spike(u, phase, power=8, harmonic=1):
    return max(0.0, wave(u, phase, harmonic)) ** power


def emote(cid, name, group, L, tracks=None, fns=None, loop="once", pri=250, events=()):
    c = Clip("emote." + cid, name, CAT, P, length=L, loop=loop, layer="action", priority=pri, trigger=manual(stop_when=STOP, desc="Emote wheel / /mw emote"),
             blend_in=0.15, blend_out=0.25, file="emotes/" + group, interrupt_after=0.0)
    c.tag(emote="true", emote_group=group)
    for key, seq in (tracks or {}).items():
        bone, _, ch = key.partition(":")
        c.keys(bone, {"rot": "rotation", "pos": "position", "scl": "scale"}[ch], seq, lerp="smooth")
    for key, fn in (fns or {}).items():
        bone, _, ch = key.partition(":")
        c.cycle(bone, {"rot": "rotation", "pos": "position", "scl": "scale"}[ch], fn, samples=12)
    for e in events:
        c.ev(e[0], e[1], **e[2])
    return c


R, Lh = lambda *a: arm('r', *a), lambda *a: arm('l', *a)
RL, LL = lambda *a: leg('r', *a), lambda *a: leg('l', *a)

# ============================================================================ gestures
G = "gestures"
emote("wave", "Wave", G, 1.6, {"right_arm:rot": [(0, Z), (0.25, R(150, 15, -20)), (0.45, R(150, 40, -20)), (0.65, R(150, 15, -20)), (0.85, R(150, 40, -20)), (1.05, R(150, 15, -20)), (1.6, Z)],
                               "body:rot": [(0, Z), (0.3, tilt(0, 0, -5)), (1.1, tilt(0, 0, -5)), (1.6, Z)], "head:rot": [(0, Z), (0.3, [-6, 10, 6]), (1.2, [-6, 10, 6]), (1.6, Z)]})
emote("wave_both", "Big Two-Handed Wave", G, 1.8, {"right_arm:rot": [(0, Z), (0.3, R(170, 15)), (0.6, R(170, 45)), (0.9, R(170, 15)), (1.2, R(170, 45)), (1.8, Z)],
                                                    "left_arm:rot": [(0, Z), (0.3, Lh(170, 45)), (0.6, Lh(170, 15)), (0.9, Lh(170, 45)), (1.2, Lh(170, 15)), (1.8, Z)], "mw_root:pos": [(0, Z), (0.45, move(0, 1, 0)), (0.75, Z), (1.05, move(0, 1, 0)), (1.35, Z)]})
emote("beckon", "Come Here", G, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(80, 0, 40)), (0.5, R(100, 0, 40)), (0.7, R(80, 0, 40)), (0.9, R(100, 0, 40)), (1.6, Z)], "head:rot": [(0, Z), (0.3, [0, 0, 10]), (1.3, [0, 0, 10]), (1.6, Z)]})
emote("point_forward", "Point Ahead", G, 1.6, {"right_arm:rot": [(0, Z), (0.25, R(90, 0), "out_back"), (1.3, R(92, 0)), (1.6, Z)], "body:rot": [(0, Z), (0.25, tilt(-4, 10, 0)), (1.3, tilt(-4, 10, 0)), (1.6, Z)]})
emote("point_up", "Point Skyward", G, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(175, 5)), (1.3, R(175, 5)), (1.6, Z)], "head:rot": [(0, Z), (0.3, [-35, 0, 0]), (1.3, [-35, 0, 0]), (1.6, Z)]})
emote("point_down", "Point At The Ground", G, 1.4, {"right_arm:rot": [(0, Z), (0.25, R(30, 0, 0)), (0.35, R(20, 0, 0)), (0.45, R(30, 0, 0)), (1.1, R(30)), (1.4, Z)], "head:rot": [(0, Z), (0.3, [35, 0, 0]), (1.1, [35, 0, 0]), (1.4, Z)],
                                                    "body:rot": [(0, Z), (0.3, tilt(10)), (1.4, Z)]})
emote("thumbs_up", "Thumbs Up", G, 1.4, {"right_arm:rot": [(0, Z), (0.25, R(80, 10, -30), "out_back"), (1.1, R(82, 10, -30)), (1.4, Z)], "head:rot": [(0, Z), (0.3, [-6, 0, 6]), (1.4, Z)]})
emote("thumbs_down", "Thumbs Down", G, 1.4, {"right_arm:rot": [(0, Z), (0.3, R(60, 10, 150)), (0.5, R(50, 10, 150)), (1.1, R(55, 10, 150)), (1.4, Z)], "head:rot": [(0, Z), (0.4, [0, 0, -10]), (1.4, Z)]})
emote("salute", "Salute", G, 1.8, {"right_arm:rot": [(0, Z), (0.3, R(130, -20, 40), "out_quad"), (1.4, R(130, -20, 40)), (1.8, Z)], "body:rot": [(0, Z), (0.3, tilt(-4)), (1.4, tilt(-4)), (1.8, Z)],
                                   "right_leg:rot": [(0, Z), (0.3, RL(0, -2)), (1.8, Z)]})
emote("bow", "Formal Bow", G, 2.2, {"body:rot": [(0, Z), (0.6, tilt(45), "in_out_sine"), (1.4, tilt(45)), (2.2, Z)], "head:rot": [(0, Z), (0.6, [20, 0, 0]), (2.2, Z)],
                                    "right_arm:rot": [(0, Z), (0.6, R(60, -20, 40)), (1.4, R(60, -20, 40)), (2.2, Z)], "left_arm:rot": [(0, Z), (0.6, Lh(-40, 10)), (1.4, Lh(-40, 10)), (2.2, Z)]})
emote("curtsy", "Curtsy", G, 2.0, {"right_leg:rot": [(0, Z), (0.5, RL(-20, -10)), (1.3, RL(-20, -10)), (2.0, Z)], "left_leg:rot": [(0, Z), (0.5, LL(40)), (1.3, LL(40)), (2.0, Z)],
                                   "mw_root:pos": [(0, Z), (0.5, move(0, -2, 0)), (1.3, move(0, -2, 0)), (2.0, Z)], "right_arm:rot": [(0, Z), (0.5, R(10, 30)), (2.0, Z)], "left_arm:rot": [(0, Z), (0.5, Lh(10, 30)), (2.0, Z)],
                                   "body:rot": [(0, Z), (0.5, tilt(14)), (2.0, Z)]})
emote("nod_yes", "Nod Yes", G, 1.2, {"head:rot": [(0, Z), (0.2, [20, 0, 0]), (0.4, [-6, 0, 0]), (0.6, [20, 0, 0]), (0.8, [-6, 0, 0]), (1.2, Z)]})
emote("shake_no", "Shake No", G, 1.2, {"head:rot": [(0, Z), (0.2, [0, 30, 0]), (0.4, [0, -30, 0]), (0.6, [0, 30, 0]), (0.8, [0, -30, 0]), (1.2, Z)], "right_arm:rot": [(0, Z), (0.3, R(40, 20, 0)), (1.0, R(40, 20)), (1.2, Z)]})
emote("shrug", "Shrug", G, 1.4, {"right_arm:rot": [(0, Z), (0.3, R(30, 40, -60)), (1.0, R(30, 40, -60)), (1.4, Z)], "left_arm:rot": [(0, Z), (0.3, Lh(30, 40, -60)), (1.0, Lh(30, 40, -60)), (1.4, Z)],
                                 "head:rot": [(0, Z), (0.3, [0, 0, 16]), (1.0, [0, 0, 16]), (1.4, Z)], "mw_root:pos": [(0, Z), (0.3, move(0, 0.5, 0)), (1.0, move(0, 0.5, 0)), (1.4, Z)]})
emote("facepalm", "Facepalm", G, 2.0, {"right_arm:rot": [(0, Z), (0.35, R(140, -30, 40), "out_expo"), (1.6, R(138, -30, 40)), (2.0, Z)], "head:rot": [(0, Z), (0.35, [30, 0, 0]), (0.8, [30, 15, 0]), (1.2, [30, -15, 0]), (1.6, [30, 0, 0]), (2.0, Z)],
                                       "body:rot": [(0, Z), (0.35, tilt(14)), (1.6, tilt(14)), (2.0, Z)]})
emote("halt", "Halt!", G, 1.4, {"right_arm:rot": [(0, Z), (0.15, R(100, 0, -90), "out_expo"), (1.1, R(100, 0, -90)), (1.4, Z)], "body:rot": [(0, Z), (0.15, tilt(-6)), (1.1, tilt(-6)), (1.4, Z)],
                                "right_leg:rot": [(0, Z), (0.15, RL(-14)), (1.1, RL(-14)), (1.4, Z)]})
emote("shush", "Shush", G, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(140, -40, 50)), (1.3, R(140, -40, 50)), (1.6, Z)], "head:rot": [(0, Z), (0.3, [6, 0, 0]), (0.6, [6, 20, 0]), (0.9, [6, -20, 0]), (1.3, [6, 0, 0]), (1.6, Z)]})
emote("call_out", "Cup Hands And Call", G, 1.8, {"right_arm:rot": [(0, Z), (0.3, R(140, -40, 30)), (1.4, R(140, -40, 30)), (1.8, Z)], "left_arm:rot": [(0, Z), (0.3, Lh(140, -40, 30)), (1.4, Lh(140, -40, 30)), (1.8, Z)],
                                                 "body:rot": [(0, Z), (0.4, tilt(-10)), (0.8, tilt(10)), (1.4, tilt(-4)), (1.8, Z)], "head:rot": [(0, Z), (0.4, [-14, 0, 0]), (1.8, Z)]})
emote("crossed_arms", "Arms Crossed", G, 3.0, fns={"right_arm:rot": lambda u: R(60, -30, 40), "left_arm:rot": lambda u: Lh(55, -30, 40), "head:rot": lambda u: [-6, 10 * wave(u), 0],
                                                    "mw_root:rot": lambda u: tilt(0, 0, 2 * wave(u))}, loop="loop")
emote("hands_on_hips", "Hands On Hips", G, 3.0, fns={"right_arm:rot": lambda u: R(-10, 40, 50), "left_arm:rot": lambda u: Lh(-10, 40, 50), "body:rot": lambda u: tilt(-6, 0, 2 * wave(u)),
                                                      "head:rot": lambda u: [-4, 12 * wave(u, 0.2), 0]}, loop="loop")
emote("ponder", "Pondering, Hand On Chin", G, 3.0, fns={"right_arm:rot": lambda u: R(120, -30, 60), "left_arm:rot": lambda u: Lh(45, -30, 40), "head:rot": lambda u: [10, 10 * wave(u), 8 * spike(u, 0.6, 4)]},
      loop="loop")
emote("high_five", "Offer A High Five", G, 2.0, {"right_arm:rot": [(0, Z), (0.3, R(160, 20, 0), "out_back"), (1.0, R(160, 20)), (1.2, R(150, 20)), (2.0, Z)], "body:rot": [(0, Z), (0.3, tilt(-6, 10, 0)), (1.2, tilt(4, -10, 0)), (2.0, Z)]},
      events=[(1.15, "sound", {"sound": "motionworks:emote.clap", "volume": "0.6"})])
emote("fist_bump", "Offer A Fist Bump", G, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(85, 10)), (0.9, R(85, 10)), (1.0, R(75, 10)), (1.6, Z)], "body:rot": [(0, Z), (0.3, tilt(6, 15, 0)), (1.0, tilt(2, 15, 0)), (1.6, Z)]})
emote("handshake", "Offer A Handshake", G, 2.0, {"right_arm:rot": [(0, Z), (0.35, R(60, 4, 80)), (0.6, R(66, 4, 80)), (0.8, R(56, 4, 80)), (1.0, R(66, 4, 80)), (1.5, R(60, 4, 80)), (2.0, Z)],
                                                 "body:rot": [(0, Z), (0.35, tilt(10)), (1.5, tilt(10)), (2.0, Z)]})
emote("tip_hat", "Tip Of The Hat", G, 1.4, {"right_arm:rot": [(0, Z), (0.3, R(170, -10, 20)), (0.6, R(165, -10, 20)), (1.4, Z)], "head:rot": [(0, Z), (0.4, [20, 0, 0]), (0.9, [10, 0, 0]), (1.4, Z)],
                                            "hat:rot": [(0, Z), (0.4, [-15, 0, 0]), (0.8, Z)]})
emote("pray", "Hands Together", G, 3.0, fns={"right_arm:rot": lambda u: R(80, -40, 20), "left_arm:rot": lambda u: Lh(80, -40, 20), "head:rot": lambda u: [24 + 3 * wave(u), 0, 0], "body:rot": lambda u: tilt(6, 0, 0)},
      loop="loop")
emote("blow_kiss", "Blow A Kiss", G, 1.6, {"right_arm:rot": [(0, Z), (0.35, R(140, -40, 50)), (0.6, R(100, 30, 0), "out_expo"), (1.6, Z)], "head:rot": [(0, Z), (0.35, [10, 0, 0]), (0.6, [-10, 0, 8]), (1.6, Z)]})
emote("peace_sign", "Peace Sign", G, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(140, 30, -10)), (1.2, R(140, 30, -10)), (1.6, Z)], "head:rot": [(0, Z), (0.3, [0, 0, -14]), (1.2, [0, 0, -14]), (1.6, Z)],
                                           "body:rot": [(0, Z), (0.3, tilt(0, 0, -6)), (1.6, Z)]})
emote("rock_on", "Rock On", G, 1.6, {"right_arm:rot": [(0, Z), (0.2, R(170, 10)), (0.4, R(160, 10)), (0.6, R(170, 10)), (0.8, R(160, 10)), (1.6, Z)], "head:rot": [(0, Z), (0.2, [20, 0, 0]), (0.4, [-10, 0, 0]), (0.6, [20, 0, 0]), (0.8, [-10, 0, 0]), (1.6, Z)]})
emote("ok_sign", "All Good", G, 1.4, {"right_arm:rot": [(0, Z), (0.3, R(110, 20, -20)), (1.0, R(110, 20, -20)), (1.4, Z)], "head:rot": [(0, Z), (0.3, [6, 0, 6]), (0.6, [-6, 0, 6]), (1.4, Z)]})
emote("look_around", "Scan The Horizon", G, 3.0, {"right_arm:rot": [(0, Z), (0.4, R(150, -20, 40)), (2.6, R(150, -20, 40)), (3.0, Z)], "head:rot": [(0, Z), (0.8, [-10, 50, 0]), (1.8, [-10, -50, 0]), (2.6, [-10, 0, 0]), (3.0, Z)],
                                                  "body:rot": [(0, Z), (0.8, tilt(0, 15, 0)), (1.8, tilt(0, -15, 0)), (3.0, Z)]})
emote("check_wrist", "Check The Time", G, 1.8, {"left_arm:rot": [(0, Z), (0.35, Lh(80, -40, 0)), (1.4, Lh(80, -40, 0)), (1.8, Z)], "head:rot": [(0, Z), (0.35, [30, -20, 0]), (1.0, [30, -20, 0]), (1.4, [0, 0, 0]), (1.8, Z)]})
emote("follow_me", "Follow Me", G, 1.8, {"right_arm:rot": [(0, Z), (0.3, R(120, 0)), (0.7, R(90, -30, 0), "in_quad"), (1.0, R(120, 0)), (1.4, R(90, -30, 0)), (1.8, Z)], "body:rot": [(0, Z), (0.4, tilt(0, -20, 0)), (1.4, tilt(0, -20, 0)), (1.8, Z)],
                                         "head:rot": [(0, Z), (0.4, [0, 30, 0]), (1.4, [0, 30, 0]), (1.8, Z)]})
emote("over_there", "Over There", G, 1.8, {"left_arm:rot": [(0, Z), (0.3, Lh(100, 60, 0)), (1.4, Lh(100, 60, 0)), (1.8, Z)], "body:rot": [(0, Z), (0.3, tilt(0, -25, 0)), (1.4, tilt(0, -25, 0)), (1.8, Z)],
                                           "head:rot": [(0, Z), (0.3, [0, -40, 0]), (1.4, [0, -40, 0]), (1.8, Z)]})
emote("whistle", "Whistle For Attention", G, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(140, -40, 60)), (1.2, R(140, -40, 60)), (1.6, Z)], "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (1.2, [-10, 0, 0]), (1.6, Z)]},
      events=[(0.4, "sound", {"sound": "motionworks:emote.whistle", "volume": "0.8"})])
emote("snap_fingers", "Snap Fingers", G, 1.0, {"right_arm:rot": [(0, Z), (0.25, R(80, 20, -20)), (0.4, R(75, 20, -30), "out_expo"), (1.0, Z)], "head:rot": [(0, Z), (0.4, [-6, 0, 8]), (1.0, Z)]},
      events=[(0.4, "sound", {"sound": "motionworks:emote.snap", "volume": "0.8"})])
emote("bring_it", "Bring It On", G, 1.8, {"right_arm:rot": [(0, Z), (0.25, R(60, 20, -80)), (0.45, R(70, 10, -90)), (0.65, R(60, 20, -80)), (0.85, R(70, 10, -90)), (1.8, Z)],
                                          "left_arm:rot": [(0, Z), (0.25, Lh(60, 20, -80)), (0.45, Lh(70, 10, -90)), (0.65, Lh(60, 20, -80)), (0.85, Lh(70, 10, -90)), (1.8, Z)], "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (1.8, Z)]})

# ============================================================================ celebrations
C = "celebrations"
emote("cheer", "Cheer", C, 1.4, {"right_arm:rot": [(0, Z), (0.2, R(170, 25), "out_back"), (1.0, R(170, 30)), (1.4, Z)], "left_arm:rot": [(0, Z), (0.2, Lh(170, 25), "out_back"), (1.0, Lh(170, 30)), (1.4, Z)],
                                 "head:rot": [(0, Z), (0.2, [-25, 0, 0]), (1.0, [-25, 0, 0]), (1.4, Z)]})
emote("jump_cheer", "Jumping Cheer", C, 1.2, {"mw_root:pos": [(0, Z), (0.15, move(0, -1, 0)), (0.35, move(0, 4, 0), "out_quad"), (0.6, Z, "in_quad"), (1.2, Z)], "right_arm:rot": [(0, Z), (0.35, R(175, 30)), (0.8, R(160, 20)), (1.2, Z)],
                                              "left_arm:rot": [(0, Z), (0.35, Lh(175, 30)), (0.8, Lh(160, 20)), (1.2, Z)], "right_leg:rot": [(0, Z), (0.35, RL(30)), (0.6, Z)], "left_leg:rot": [(0, Z), (0.35, LL(30)), (0.6, Z)]})
emote("fist_pump", "Fist Pump", C, 1.2, {"right_arm:rot": [(0, Z), (0.2, R(120, 10)), (0.35, R(60, 10, 0), "in_quart"), (0.55, R(120, 10)), (0.7, R(60, 10), "in_quart"), (1.2, Z)], "body:rot": [(0, Z), (0.35, tilt(10)), (0.7, tilt(10)), (1.2, Z)]})
emote("double_pump", "Double Fist Pump", C, 1.4, {"right_arm:rot": [(0, Z), (0.2, R(150, 20)), (0.4, R(100, 30)), (0.6, R(150, 20)), (0.8, R(100, 30)), (1.4, Z)],
                                                  "left_arm:rot": [(0, Z), (0.2, Lh(150, 20)), (0.4, Lh(100, 30)), (0.6, Lh(150, 20)), (0.8, Lh(100, 30)), (1.4, Z)], "mw_root:pos": [(0, Z), (0.4, move(0, -1, 0)), (0.8, move(0, -1, 0)), (1.4, Z)]})
emote("victory_v", "Victory Pose", C, 2.0, {"right_arm:rot": [(0, Z), (0.3, R(160, 50)), (1.6, R(160, 50)), (2.0, Z)], "left_arm:rot": [(0, Z), (0.3, Lh(160, 50)), (1.6, Lh(160, 50)), (2.0, Z)],
                                            "right_leg:rot": [(0, Z), (0.3, RL(0, 12)), (1.6, RL(0, 12)), (2.0, Z)], "left_leg:rot": [(0, Z), (0.3, LL(0, 12)), (1.6, LL(0, 12)), (2.0, Z)], "head:rot": [(0, Z), (0.3, [-20, 0, 0]), (2.0, Z)]})
emote("spin", "Celebratory Spin", C, 1.2, {"mw_root:rot": [(0, Z), (1.0, [0, 360, 0], "in_out_sine"), (1.2, [0, 360, 0])], "right_arm:rot": [(0, Z), (0.5, R(90, 80)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.5, Lh(90, 80)), (1.2, Z)]})
emote("raise_the_roof", "Raise The Roof", C, 0.8, fns={"right_arm:rot": lambda u: R(150 + 20 * wave(u), 40, -80), "left_arm:rot": lambda u: Lh(150 + 20 * wave(u), 40, -80),
                                                        "mw_root:pos": lambda u: move(0, -0.8 * max(0, -wave(u)), 0), "head:rot": lambda u: [10 * wave(u), 0, 0]}, loop="loop")
emote("flex", "Double Bicep Flex", C, 2.0, {"right_arm:rot": [(0, Z), (0.35, R(90, 80, -80)), (0.6, R(95, 80, -95)), (0.85, R(90, 80, -80)), (1.6, R(95, 80, -95)), (2.0, Z)],
                                            "left_arm:rot": [(0, Z), (0.35, Lh(90, 80, -80)), (0.6, Lh(95, 80, -95)), (0.85, Lh(90, 80, -80)), (1.6, Lh(95, 80, -95)), (2.0, Z)], "body:rot": [(0, Z), (0.35, tilt(-6)), (2.0, Z)]})
emote("flex_one", "Show Off A Bicep", C, 1.8, {"right_arm:rot": [(0, Z), (0.3, R(90, 80, -90)), (1.4, R(92, 80, -95)), (1.8, Z)], "head:rot": [(0, Z), (0.4, [10, 40, 0]), (1.4, [10, 40, 0]), (1.8, Z)],
                                               "left_arm:rot": [(0, Z), (0.4, Lh(-10, 40, 50)), (1.4, Lh(-10, 40, 50)), (1.8, Z)]})
emote("crowd_bow", "Bow To The Crowd", C, 2.4, {"body:rot": [(0, Z), (0.5, tilt(50), "out_quad"), (1.0, tilt(50)), (1.5, Z)], "right_arm:rot": [(0, Z), (0.3, R(90, 60)), (0.5, R(60, -10, 40)), (1.5, R(160, 40)), (2.4, Z)],
                                                "left_arm:rot": [(0, Z), (0.3, Lh(90, 60)), (0.5, Lh(-30, 20)), (1.5, Lh(160, 40)), (2.4, Z)]})
emote("applaud", "Applause", C, 0.5, fns={"right_arm:rot": lambda u: R(70, -10 + 30 * max(0, wave(u)), 10), "left_arm:rot": lambda u: Lh(70, -10 + 30 * max(0, wave(u)), 10), "head:rot": lambda u: [-6, 0, 0]},
      loop="loop", events=[(0.25, "sound", {"sound": "motionworks:emote.clap", "volume": "0.5"})])
emote("champion", "Champion Stance", C, 2.4, {"right_arm:rot": [(0, Z), (0.4, R(175, 10)), (2.0, R(175, 10)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.4, Lh(-10, 40, 50)), (2.0, Lh(-10, 40, 50)), (2.4, Z)],
                                              "body:rot": [(0, Z), (0.4, tilt(-10, 0, -6)), (2.0, tilt(-10, 0, -6)), (2.4, Z)], "right_leg:rot": [(0, Z), (0.4, RL(-20, 10)), (2.0, RL(-20, 10)), (2.4, Z)]})
emote("backflip", "Backflip", C, 1.3, {"mw_root:pos": [(0, Z), (0.2, move(0, -2, 0)), (0.6, move(0, 8, 0), "out_quad"), (1.0, Z, "in_quad"), (1.3, Z)], "mw_root:rot": [(0, Z), (0.25, Z), (1.0, tilt(-360, 0, 0), "in_out_sine"), (1.3, tilt(-360, 0, 0))],
                                       "right_leg:rot": [(0, Z), (0.5, RL(110)), (0.85, RL(90)), (1.0, Z)], "left_leg:rot": [(0, Z), (0.5, LL(110)), (0.85, LL(90)), (1.0, Z)],
                                       "right_arm:rot": [(0, Z), (0.2, R(-40)), (0.5, R(170)), (1.0, R(60, 40)), (1.3, Z)], "left_arm:rot": [(0, Z), (0.2, Lh(-40)), (0.5, Lh(170)), (1.0, Lh(60, 40)), (1.3, Z)]})
emote("cartwheel", "Cartwheel", C, 1.4, {"mw_root:rot": [(0, Z), (1.2, tilt(0, 0, 360), "in_out_sine"), (1.4, tilt(0, 0, 360))], "mw_root:pos": [(0, Z), (0.6, move(0, 4, 0)), (1.2, Z)],
                                         "right_arm:rot": [(0, Z), (0.3, R(0, 170)), (0.9, R(0, 170)), (1.4, Z)], "left_arm:rot": [(0, Z), (0.3, Lh(0, 170)), (0.9, Lh(0, 170)), (1.4, Z)],
                                         "right_leg:rot": [(0, Z), (0.3, RL(0, 50)), (0.9, RL(0, 50)), (1.4, Z)], "left_leg:rot": [(0, Z), (0.3, LL(0, 50)), (0.9, LL(0, 50)), (1.4, Z)]})
emote("trophy_lift", "Lift The Trophy", C, 2.4, {"right_arm:rot": [(0, Z), (0.6, R(175, -10)), (1.8, R(175, -10)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.6, Lh(175, -10)), (1.8, Lh(175, -10)), (2.4, Z)],
                                                 "mw_root:pos": [(0, Z), (0.6, move(0, 1, 0)), (0.9, move(0, 1.5, 0)), (1.2, move(0, 1, 0)), (1.8, move(0, 1, 0)), (2.4, Z)], "head:rot": [(0, Z), (0.6, [-40, 0, 0]), (2.4, Z)]})
emote("dab", "Dab", C, 1.2, {"right_arm:rot": [(0, Z), (0.15, R(130, 70, 0), "out_expo"), (0.9, R(130, 70)), (1.2, Z)], "left_arm:rot": [(0, Z), (0.15, Lh(120, -40, 40), "out_expo"), (0.9, Lh(120, -40, 40)), (1.2, Z)],
                             "head:rot": [(0, Z), (0.15, [40, -30, 0]), (0.9, [40, -30, 0]), (1.2, Z)], "body:rot": [(0, Z), (0.15, tilt(10, -10, 0)), (0.9, tilt(10, -10, 0)), (1.2, Z)]})
emote("slam_dunk", "Slam Dunk", C, 1.4, {"mw_root:pos": [(0, Z), (0.25, move(0, -2, 0)), (0.55, move(0, 5, 0), "out_quad"), (0.9, Z, "in_quad"), (1.4, Z)], "right_arm:rot": [(0, Z), (0.55, R(180, 0)), (0.75, R(90, 0), "in_quart"), (1.4, Z)],
                                         "left_arm:rot": [(0, Z), (0.55, Lh(120, 20)), (1.4, Z)]})
emote("happy_hop", "Happy Hops", C, 0.5, fns={"mw_root:pos": lambda u: move(0, 2 * max(0, wave(u)), 0), "right_arm:rot": lambda u: R(30 + 20 * max(0, wave(u)), 30), "left_arm:rot": lambda u: Lh(30 + 20 * max(0, wave(u)), 30),
                                              "right_leg:rot": lambda u: RL(20 * max(0, wave(u))), "left_leg:rot": lambda u: LL(20 * max(0, wave(u)))}, loop="loop")
emote("confetti", "Throw Confetti", C, 1.6, {"right_arm:rot": [(0, R(20, -20, 30)), (0.4, R(30, -20, 30)), (0.6, R(170, 40), "out_expo"), (1.6, Z)], "left_arm:rot": [(0, Lh(20, -20, 30)), (0.4, Lh(30, -20, 30)), (0.6, Lh(170, 40), "out_expo"), (1.6, Z)],
                                             "head:rot": [(0, Z), (0.7, [-30, 0, 0]), (1.6, Z)]}, events=[(0.6, "particle", {"particle": "magic_glint", "count": "24", "at": "head", "spread": "1.2"})])
emote("knee_slide", "Knee Slide Celebration", C, 2.0, {"right_leg:rot": [(0, Z), (0.3, RL(90)), (1.6, RL(90)), (2.0, Z)], "left_leg:rot": [(0, Z), (0.3, LL(90)), (1.6, LL(90)), (2.0, Z)],
                                                       "mw_root:pos": [(0, Z), (0.3, move(0, -6, 2)), (1.0, move(0, -6, -2)), (1.6, move(0, -6, -2)), (2.0, Z)], "body:rot": [(0, Z), (0.5, tilt(-25)), (1.6, tilt(-25)), (2.0, Z)],
                                                       "right_arm:rot": [(0, Z), (0.5, R(150, 60)), (1.6, R(150, 60)), (2.0, Z)], "left_arm:rot": [(0, Z), (0.5, Lh(150, 60)), (1.6, Lh(150, 60)), (2.0, Z)]})
emote("chest_pound", "Chest Pound", C, 1.4, {"right_arm:rot": [(0, Z), (0.15, R(60, -30, 40)), (0.25, R(50, -20, 40)), (0.4, R(60, -30, 40)), (0.5, R(50, -20, 40)), (1.4, Z)],
                                             "left_arm:rot": [(0, Z), (0.2, Lh(60, -30, 40)), (0.3, Lh(50, -20, 40)), (0.45, Lh(60, -30, 40)), (0.55, Lh(50, -20, 40)), (1.4, Z)], "head:rot": [(0, Z), (0.6, [-30, 0, 0]), (1.4, Z)]})
emote("high_kick", "Victory High Kick", C, 1.0, {"right_leg:rot": [(0, Z), (0.25, RL(-110), "out_expo"), (0.5, RL(-90)), (1.0, Z)], "right_arm:rot": [(0, Z), (0.25, R(170, 30)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.25, Lh(30, 60)), (1.0, Z)],
                                                 "body:rot": [(0, Z), (0.25, tilt(-12)), (1.0, Z)]})
emote("lasso", "Lasso Twirl", C, 0.6, fns={"right_arm:rot": lambda u: [-170, 30 * cwave(u), 30 * wave(u)], "left_arm:rot": lambda u: Lh(-10, 40, 50), "mw_root:pos": lambda u: move(0, 0.4 * wave(u, 0, 2), 0)}, loop="loop")
emote("golf_clap", "Polite Golf Clap", C, 0.6, fns={"right_arm:rot": lambda u: R(40, -14 + 8 * max(0, wave(u)), 20), "left_arm:rot": lambda u: Lh(40, -14 + 8 * max(0, wave(u)), 20), "head:rot": lambda u: [6, 0, 8]}, loop="loop")
emote("arms_wide", "Arms Wide To The World", C, 2.2, {"right_arm:rot": [(0, Z), (0.5, R(80, 90)), (1.8, R(85, 95)), (2.2, Z)], "left_arm:rot": [(0, Z), (0.5, Lh(80, 90)), (1.8, Lh(85, 95)), (2.2, Z)],
                                                      "head:rot": [(0, Z), (0.5, [-30, 0, 0]), (1.8, [-30, 0, 0]), (2.2, Z)], "body:rot": [(0, Z), (0.5, tilt(-10)), (2.2, Z)]})
emote("sword_raise", "Raise A Blade In Triumph", C, 2.0, {"right_arm:rot": [(0, Z), (0.4, R(178, 0, 0), "out_back"), (1.6, R(178, 0)), (2.0, Z)], "body:rot": [(0, Z), (0.4, tilt(-8, 0, -4)), (2.0, Z)],
                                                          "head:rot": [(0, Z), (0.4, [-35, 0, 0]), (2.0, Z)], "left_leg:rot": [(0, Z), (0.4, LL(-15)), (1.6, LL(-15)), (2.0, Z)]})
emote("fist_shake", "Triumphant Fist Shake", C, 1.2, {"right_arm:rot": [(0, Z), (0.2, R(150, 20))] + [(0.2 + 0.1 * i, R(150 + 8 * (-1) ** i, 20)) for i in range(1, 8)] + [(1.2, Z)],
                                                      "head:rot": [(0, Z), (0.3, [-20, 0, 0]), (1.2, Z)]})
emote("countdown", "Count Down From Three", C, 2.4, {"right_arm:rot": [(0, Z), (0.3, R(120, 0)), (0.8, R(120, 0)), (0.9, R(110, 0)), (1.4, R(120, 0)), (1.5, R(110, 0)), (2.0, R(170, 20), "out_back"), (2.4, Z)],
                                                     "head:rot": [(0, Z), (0.8, [6, 0, 0]), (2.0, [-20, 0, 0]), (2.4, Z)]})
emote("drum_roll", "Drum Roll", C, 0.3, fns={"right_arm:rot": lambda u: R(50 + 12 * wave(u), 10), "left_arm:rot": lambda u: Lh(50 + 12 * wave(u, 0.5), 10), "head:rot": lambda u: [10, 0, 0]}, loop="loop")

# ============================================================================ expressions
E = "expressions"
emote("laugh", "Laugh", E, 1.6, {"body:rot": [(0, Z)] + [(0.15 * i, tilt(-8 if i % 2 else -2)) for i in range(1, 9)] + [(1.6, Z)], "head:rot": [(0, Z), (0.2, [-25, 0, 0]), (1.2, [-20, 0, 0]), (1.6, Z)],
                                 "right_arm:rot": [(0, Z), (0.3, R(30, -10, 40)), (1.2, R(30, -10, 40)), (1.6, Z)]})
emote("belly_laugh", "Belly Laugh", E, 2.0, {"body:rot": [(0, Z), (0.3, tilt(30)), (0.5, tilt(20)), (0.7, tilt(30)), (0.9, tilt(20)), (1.1, tilt(30)), (2.0, Z)], "right_arm:rot": [(0, Z), (0.3, R(40, -20, 40)), (1.4, R(40, -20, 40)), (2.0, Z)],
                                             "left_arm:rot": [(0, Z), (0.3, Lh(40, -20, 40)), (1.4, Lh(40, -20, 40)), (2.0, Z)], "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (2.0, Z)]})
emote("sob", "Sob", E, 2.4, {"right_arm:rot": [(0, Z), (0.4, R(140, -30, 40)), (2.0, R(140, -30, 40)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.4, Lh(140, -30, 40)), (2.0, Lh(140, -30, 40)), (2.4, Z)],
                             "head:rot": [(0, Z), (0.4, [30, 0, 0]), (2.4, Z)], "body:rot": [(0, Z)] + [(0.4 + 0.2 * i, tilt(16 + (4 if i % 2 else 0))) for i in range(8)] + [(2.4, Z)]})
emote("pout", "Pout", E, 3.0, fns={"right_arm:rot": lambda u: R(55, -30, 40), "left_arm:rot": lambda u: Lh(50, -30, 40), "head:rot": lambda u: [14, 30, 0], "body:rot": lambda u: tilt(0, 20, 0),
                                   "right_leg:rot": lambda u: RL(10 * spike(u, 0.5, 2))}, loop="loop")
emote("rage", "Furious Stomping", E, 1.6, {"right_leg:rot": [(0, Z), (0.2, RL(50)), (0.3, RL(-4), "in_quart"), (0.6, RL(50)), (0.7, RL(-4), "in_quart"), (1.6, Z)],
                                          "right_arm:rot": [(0, Z), (0.2, R(40, 20)), (0.3, R(10, 20)), (0.6, R(40, 20)), (0.7, R(10, 20)), (1.6, Z)], "left_arm:rot": [(0, Z), (0.2, Lh(40, 20)), (0.3, Lh(10, 20)), (0.6, Lh(40, 20)), (0.7, Lh(10, 20)), (1.6, Z)],
                                          "head:rot": [(0, Z), (0.2, [20, 0, 0]), (1.6, Z)]}, events=[(0.3, "footstep", {"foot": "right"}), (0.7, "footstep", {"foot": "right"})])
emote("gasp", "Gasp", E, 1.4, {"right_arm:rot": [(0, Z), (0.1, R(120, -20, 40), "out_expo"), (1.0, R(118, -20, 40)), (1.4, Z)], "head:rot": [(0, Z), (0.1, [-14, 0, 0]), (1.4, Z)], "body:rot": [(0, Z), (0.1, tilt(-10)), (1.4, Z)]})
emote("faint", "Faint", E, 2.6, {"mw_root:pos": [(0, Z), (0.8, move(0, -2, 0)), (1.4, move(0, -10, 0), "in_quad"), (2.6, move(0, -11, 0))], "mw_root:rot": [(0, Z), (0.8, tilt(-6)), (1.4, tilt(-85), "in_quad"), (2.6, tilt(-85))],
                                 "right_arm:rot": [(0, Z), (0.4, R(150, -30, 40)), (1.4, R(160, 60)), (2.6, R(170, 60))], "left_arm:rot": [(0, Z), (1.4, Lh(60, 60)), (2.6, Lh(70, 60))], "head:rot": [(0, Z), (0.6, [-20, 0, 10]), (2.6, [0, 0, 20])]})
emote("cower", "Cower In Fear", E, 0.4, fns={"right_arm:rot": lambda u: R(140, -10, 40), "left_arm:rot": lambda u: Lh(140, -10, 40), "mw_root:pos": lambda u: move(0.2 * wave(u), -2, 0), "body:rot": lambda u: tilt(30, 0, 1.5 * wave(u, 0.25)),
                                             "right_leg:rot": lambda u: RL(40), "left_leg:rot": lambda u: LL(40)}, loop="loop")
emote("shy_wave", "Shy Little Wave", E, 1.8, {"right_arm:rot": [(0, Z), (0.4, R(60, 10, 0)), (0.6, R(62, 20)), (0.8, R(60, 10)), (1.0, R(62, 20)), (1.8, Z)], "head:rot": [(0, Z), (0.4, [20, 0, 14]), (1.4, [20, 0, 14]), (1.8, Z)],
                                              "body:rot": [(0, Z), (0.4, tilt(4, 0, 4)), (1.8, Z)]})
emote("fidget", "Nervous Fidget", E, 1.2, fns={"right_arm:rot": lambda u: R(40, -20 + 10 * wave(u, 0, 2), 40), "left_arm:rot": lambda u: Lh(40, -20 + 10 * wave(u, 0.5, 2), 40), "head:rot": lambda u: [14, 20 * wave(u), 0],
                                               "mw_root:rot": lambda u: tilt(0, 0, 2 * wave(u, 0.25))}, loop="loop")
emote("disgust", "Disgusted", E, 1.6, {"head:rot": [(0, Z), (0.2, [-10, -30, 0], "out_expo"), (1.2, [-10, -35, 0]), (1.6, Z)], "body:rot": [(0, Z), (0.2, tilt(-8, -14, 0)), (1.2, tilt(-8, -14, 0)), (1.6, Z)],
                                       "right_arm:rot": [(0, Z), (0.2, R(70, 20, -60)), (1.2, R(70, 20, -60)), (1.6, Z)]})
emote("sniff", "Sniff The Air", E, 1.6, {"head:rot": [(0, Z), (0.3, [-20, 0, 0]), (0.45, [-16, 0, 0]), (0.6, [-20, 0, 0]), (0.75, [-16, 15, 0]), (0.9, [-20, 15, 0]), (1.6, Z)], "body:rot": [(0, Z), (0.3, tilt(-6)), (1.6, Z)]})
emote("evil_laugh", "Villainous Laugh", E, 2.2, {"right_arm:rot": [(0, Z), (0.4, R(80, -30, 60)), (1.8, R(80, -30, 60)), (2.2, Z)], "left_arm:rot": [(0, Z), (0.4, Lh(80, -30, 60)), (1.8, Lh(80, -30, 60)), (2.2, Z)],
                                                 "head:rot": [(0, Z), (0.6, [-30, 0, 0]), (0.8, [-20, 0, 0]), (1.0, [-30, 0, 0]), (1.2, [-20, 0, 0]), (1.4, [-35, 0, 0]), (2.2, Z)], "body:rot": [(0, Z), (0.6, tilt(-14)), (1.4, tilt(-18)), (2.2, Z)]})
emote("smug", "Smug", E, 2.4, {"head:rot": [(0, Z), (0.4, [-14, 0, 12]), (2.0, [-14, 0, 12]), (2.4, Z)], "right_arm:rot": [(0, Z), (0.4, R(-10, 40, 50)), (2.0, R(-10, 40, 50)), (2.4, Z)], "body:rot": [(0, Z), (0.4, tilt(-8, 0, 4)), (2.4, Z)]})
emote("slump", "Dejected Slump", E, 3.0, fns={"body:rot": lambda u: tilt(26, 0, 0), "head:rot": lambda u: [30 + 3 * wave(u), 0, 0], "right_arm:rot": lambda u: R(10, -4), "left_arm:rot": lambda u: Lh(10, -4),
                                              "mw_root:pos": lambda u: move(0, -0.8, 0)}, loop="loop")
emote("lovestruck", "Lovestruck", E, 2.4, {"right_arm:rot": [(0, Z), (0.4, R(60, -40, 30)), (2.0, R(60, -40, 30)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.4, Lh(60, -40, 30)), (2.0, Lh(60, -40, 30)), (2.4, Z)],
                                           "head:rot": [(0, Z), (0.6, [-10, 0, 14]), (1.2, [-10, 0, -14]), (1.8, [-10, 0, 14]), (2.4, Z)], "mw_root:pos": [(0, Z), (0.6, move(0, 0.6, 0)), (1.8, move(0, 0.6, 0)), (2.4, Z)]})
emote("dizzy", "Dizzy", E, 2.0, fns={"head:rot": lambda u: [10 * wave(u), 0, 15 * cwave(u)], "body:rot": lambda u: tilt(6 * wave(u, 0.25), 0, 8 * cwave(u, 0.25)), "right_arm:rot": lambda u: R(20, 40 + 10 * wave(u)),
                                     "left_arm:rot": lambda u: Lh(20, 40 + 10 * wave(u, 0.5))}, loop="loop")
emote("hiccup", "Hiccups", E, 1.4, {"mw_root:pos": [(0, Z), (0.3, move(0, 1.2, 0), "out_expo"), (0.45, Z), (1.0, Z), (1.1, move(0, 1.2, 0), "out_expo"), (1.25, Z), (1.4, Z)],
                                    "right_arm:rot": [(0, Z), (0.3, R(80, -20, 40)), (1.4, Z)], "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (0.45, Z), (1.1, [-10, 0, 0]), (1.25, Z)]})
emote("startled", "Startled Jump", E, 1.0, {"mw_root:pos": [(0, Z), (0.1, move(0, 3, 0), "out_expo"), (0.35, Z)], "right_arm:rot": [(0, Z), (0.1, R(100, 60)), (1.0, Z)], "left_arm:rot": [(0, Z), (0.1, Lh(100, 60)), (1.0, Z)],
                                            "right_leg:rot": [(0, Z), (0.1, RL(30)), (0.35, Z)]})
emote("relieved", "Wipe Of Relief", E, 1.8, {"right_arm:rot": [(0, Z), (0.4, R(150, -20, 50)), (0.6, R(150, 10, 50)), (0.8, R(130, 30, 50)), (1.8, Z)], "body:rot": [(0, Z), (0.8, tilt(-6)), (1.2, tilt(8)), (1.8, Z)],
                                             "head:rot": [(0, Z), (0.8, [-10, 0, 0]), (1.2, [12, 0, 0]), (1.8, Z)]}, events=[(1.0, "breath", {"strength": "0.6"})])
emote("frustrated", "Tearing Your Hair Out", E, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(170, -10, 30)), (0.5, R(160, -10, 30)), (0.7, R(170, -10, 30)), (1.6, Z)],
                                                      "left_arm:rot": [(0, Z), (0.3, Lh(170, -10, 30)), (0.5, Lh(160, -10, 30)), (0.7, Lh(170, -10, 30)), (1.6, Z)], "head:rot": [(0, Z), (0.3, [20, 0, 0]), (0.5, [20, 15, 0]), (0.7, [20, -15, 0]), (1.6, Z)]})
emote("daydream", "Daydreaming", E, 4.0, fns={"head:rot": lambda u: [-25 + 4 * wave(u), 15 * wave(u, 0, 0.5), 8 * wave(u)], "right_arm:rot": lambda u: R(120, -30, 60), "body:rot": lambda u: tilt(-4, 0, 3 * wave(u))},
      loop="loop")
emote("embarrassed", "Embarrassed", E, 2.0, {"right_arm:rot": [(0, Z), (0.3, R(160, -30, 40)), (1.6, R(160, -30, 40)), (2.0, Z)], "head:rot": [(0, Z), (0.3, [25, 25, 0]), (1.6, [25, 25, 0]), (2.0, Z)],
                                             "body:rot": [(0, Z), (0.3, tilt(6, 20, 0)), (2.0, Z)]})
emote("proud", "Proud Chest Out", E, 2.4, {"body:rot": [(0, Z), (0.5, tilt(-14)), (2.0, tilt(-14)), (2.4, Z)], "head:rot": [(0, Z), (0.5, [-20, 0, 0]), (2.0, [-20, 0, 0]), (2.4, Z)],
                                           "right_arm:rot": [(0, Z), (0.5, R(-20, 20)), (2.0, R(-20, 20)), (2.4, Z)], "left_arm:rot": [(0, Z), (0.5, Lh(-20, 20)), (2.0, Lh(-20, 20)), (2.4, Z)],
                                           "mw_root:pos": [(0, Z), (0.5, move(0, 0.8, 0)), (2.0, move(0, 0.8, 0)), (2.4, Z)]})
emote("confused", "Confused Head Tilt", E, 2.0, {"head:rot": [(0, Z), (0.4, [0, 0, 25]), (1.0, [0, 0, 25]), (1.3, [0, 0, -20]), (1.7, [0, 0, -20]), (2.0, Z)], "right_arm:rot": [(0, Z), (0.5, R(150, -20, 60)), (1.6, R(150, -20, 60)), (2.0, Z)]})
emote("sneeze", "Big Sneeze", E, 1.6, {"head:rot": [(0, Z), (0.6, [-30, 0, 0], "in_quad"), (0.7, [35, 0, 0], "out_expo"), (1.0, [20, 0, 0]), (1.6, Z)], "body:rot": [(0, Z), (0.6, tilt(-12)), (0.7, tilt(26)), (1.6, Z)],
                                       "right_arm:rot": [(0, Z), (0.6, R(110, -30, 40)), (0.8, R(120, -30, 40)), (1.6, Z)]})
emote("shiver_fright", "Trembling With Fright", E, 0.2, fns={"body:rot": lambda u: tilt(10, 0, 2 * wave(u)), "head:rot": lambda u: [14, 3 * wave(u, 0.3), 0], "right_arm:rot": lambda u: R(30, -10, 30), "left_arm:rot": lambda u: Lh(30, -10, 30)},
      loop="loop")
emote("bored", "Bored Out Of Your Mind", E, 3.6, fns={"head:rot": lambda u: [20 + 10 * spike(u, 0.5, 3), 0, 14], "right_arm:rot": lambda u: R(5 + 10 * wave(u, 0, 2), 6), "left_arm:rot": lambda u: Lh(5 + 10 * wave(u, 0.5, 2), 6),
                                                      "mw_root:rot": lambda u: tilt(0, 0, 4 * wave(u))}, loop="loop")
emote("think_hard", "Thinking Very Hard", E, 2.4, fns={"right_arm:rot": lambda u: R(150, -30, 60 + 10 * wave(u, 0, 2)), "head:rot": lambda u: [5, 0, 10 * wave(u, 0, 0.5)], "body:rot": lambda u: tilt(0, 10 * wave(u, 0, 0.5), 0)},
      loop="loop")
emote("mock_cry", "Mock Crying", E, 1.6, {"right_arm:rot": [(0, Z), (0.3, R(130, -10, 60))] + [(0.3 + 0.12 * i, R(130 + (8 if i % 2 else 0), -10, 60)) for i in range(1, 9)] + [(1.6, Z)],
                                          "left_arm:rot": [(0, Z), (0.3, Lh(130, -10, 60))] + [(0.3 + 0.12 * i, Lh(130 + (0 if i % 2 else 8), -10, 60)) for i in range(1, 9)] + [(1.6, Z)], "head:rot": [(0, Z), (0.3, [-10, 0, 0]), (1.6, Z)]})

# ============================================================================ dances (looping)
D = "dances"
emote("sway", "Gentle Sway", D, 2.0, fns={"body:rot": lambda u: tilt(0, 0, 6 * wave(u)), "mw_root:rot": lambda u: tilt(0, 0, 3 * wave(u)), "right_arm:rot": lambda u: R(10, 10 + 6 * wave(u)), "left_arm:rot": lambda u: Lh(10, 10 - 6 * wave(u)),
                                          "head:rot": lambda u: [0, 0, -4 * wave(u)]}, loop="loop")
emote("bop", "Head Bop", D, 0.5, fns={"head:rot": lambda u: [15 * max(0, wave(u)), 0, 0], "mw_root:pos": lambda u: move(0, -0.6 * max(0, wave(u)), 0), "right_arm:rot": lambda u: R(30, 10, 30), "left_arm:rot": lambda u: Lh(30, 10, 30)},
      loop="loop")
emote("robot", "The Robot", D, 2.0, tracks={"right_arm:rot": [(0, R(90, 0, 0)), (0.5, R(90, 0, 0)), (0.55, R(0, 80, 0)), (1.0, R(0, 80, 0)), (1.05, R(90, 0, -90)), (1.5, R(90, 0, -90)), (1.55, R(90, 0, 0)), (2.0, R(90, 0, 0))],
                                            "left_arm:rot": [(0, Lh(0, 80)), (0.5, Lh(0, 80)), (0.55, Lh(90, 0, 0)), (1.0, Lh(90, 0)), (1.05, Lh(90, 0, -90)), (1.5, Lh(90, 0, -90)), (1.55, Lh(0, 80)), (2.0, Lh(0, 80))],
                                            "head:rot": [(0, [0, 30, 0]), (0.5, [0, 30, 0]), (0.55, [0, -30, 0]), (1.0, [0, -30, 0]), (1.05, Z), (2.0, [0, 30, 0])]}, loop="loop")
emote("disco_point", "Disco Point", D, 1.0, fns={"right_arm:rot": lambda u: R(90 + 80 * max(0, wave(u)), 30 - 50 * max(0, wave(u))), "left_arm:rot": lambda u: Lh(-20, 40, 50), "mw_root:rot": lambda u: tilt(0, 0, 6 * wave(u)),
                                                 "right_leg:rot": lambda u: RL(0, 14 * max(0, wave(u)))}, loop="loop")
emote("twist", "The Twist", D, 0.6, fns={"body:rot": lambda u: tilt(6, 30 * wave(u), 0), "right_leg:rot": lambda u: RL(20, 0, -20 * wave(u)), "left_leg:rot": lambda u: LL(10, 0, -20 * wave(u)), "right_arm:rot": lambda u: R(60, 30, -30 * wave(u)),
                                         "left_arm:rot": lambda u: Lh(60, 30, 30 * wave(u)), "mw_root:pos": lambda u: move(0, -1 + 0.4 * wave(u, 0, 2), 0)}, loop="loop")
emote("moonwalk", "Backslide Glide", D, 1.2, fns={"right_leg:rot": lambda u: RL(-20 * max(0, wave(u)), 0), "left_leg:rot": lambda u: LL(-20 * max(0, wave(u, 0.5)), 0), "mw_root:pos": lambda u: move(0, 0.4 * abs(wave(u)), 0),
                                                  "right_arm:rot": lambda u: R(10 * wave(u), 10), "left_arm:rot": lambda u: Lh(-10 * wave(u), 10), "head:rot": lambda u: [10, 0, 0]}, loop="loop")
emote("floss", "Arm Swing Floss", D, 0.8, fns={"right_arm:rot": lambda u: [20 * wave(u, 0, 2), 0, 30 * wave(u)], "left_arm:rot": lambda u: [-20 * wave(u, 0, 2), 0, 30 * wave(u)], "mw_root:rot": lambda u: tilt(0, 0, -8 * wave(u)),
                                               "mw_root:pos": lambda u: move(0.8 * wave(u), 0, 0)}, loop="loop")
emote("stir_the_pot", "Stir The Pot", D, 1.0, fns={"right_arm:rot": lambda u: R(80 + 20 * cwave(u), 20 + 20 * wave(u), 40), "left_arm:rot": lambda u: Lh(80 + 20 * cwave(u, 0.5), 20 + 20 * wave(u, 0.5), 40),
                                                   "body:rot": lambda u: tilt(6, 15 * wave(u), 0), "mw_root:pos": lambda u: move(0, -0.8, 0)}, loop="loop")
emote("sprinkler", "The Sprinkler", D, 2.0, tracks={"left_arm:rot": [(0, Lh(130, -30, 60))] * 1 + [(2.0, Lh(130, -30, 60))], "right_arm:rot": [(0, R(90, 60))] + [(0.25 * i, R(90, 60 - 12 * i)) for i in range(1, 8)] + [(2.0, R(90, 60))],
                                                    "body:rot": [(0, tilt(0, 30, 0))] + [(0.25 * i, tilt(0, 30 - 8 * i, 0)) for i in range(1, 8)] + [(2.0, tilt(0, 30, 0))]}, loop="loop")
emote("running_man", "Running Man", D, 0.8, fns={"right_leg:rot": lambda u: RL(40 * max(0, wave(u)) - 10 * max(0, -wave(u))), "left_leg:rot": lambda u: LL(40 * max(0, wave(u, 0.5)) - 10 * max(0, -wave(u, 0.5))),
                                                 "right_arm:rot": lambda u: R(60 * max(0, wave(u, 0.5)), 10), "left_arm:rot": lambda u: Lh(60 * max(0, wave(u)), 10), "mw_root:pos": lambda u: move(0, 0.6 * abs(wave(u)), 0)}, loop="loop")
emote("jig", "Lively Jig", D, 0.6, fns={"right_leg:rot": lambda u: RL(-30 * max(0, wave(u)), 0), "left_leg:rot": lambda u: LL(-30 * max(0, wave(u, 0.5)), 0), "mw_root:pos": lambda u: move(0, 1.2 * abs(wave(u)), 0),
                                        "right_arm:rot": lambda u: R(-10, 40, 50), "left_arm:rot": lambda u: Lh(-10, 40, 50), "body:rot": lambda u: tilt(-4, 0, 0)}, loop="loop")
emote("chicken_dance", "Chicken Flap Dance", D, 0.6, fns={"right_arm:rot": lambda u: R(20, 30 + 30 * max(0, wave(u, 0, 2)), -60), "left_arm:rot": lambda u: Lh(20, 30 + 30 * max(0, wave(u, 0, 2)), -60),
                                                          "mw_root:pos": lambda u: move(0, -1.5, 0), "body:rot": lambda u: tilt(14, 0, 0), "head:rot": lambda u: [0, 0, 0], "head:pos": lambda u: move(0, 0, 0.6 * wave(u, 0, 2))}, loop="loop")
emote("salsa", "Salsa Step", D, 1.2, fns={"right_leg:rot": lambda u: RL(-20 * wave(u)), "left_leg:rot": lambda u: LL(20 * wave(u)), "mw_root:rot": lambda u: tilt(0, 10 * wave(u), 6 * wave(u, 0.25)),
                                          "right_arm:rot": lambda u: R(70, 50), "left_arm:rot": lambda u: Lh(90, 30, 0), "body:rot": lambda u: tilt(0, -10 * wave(u), 0)}, loop="loop")
emote("bounce", "Hip-Hop Bounce", D, 0.5, fns={"mw_root:pos": lambda u: move(0, -1.2 * max(0, -wave(u)), 0), "right_leg:rot": lambda u: RL(20 * max(0, -wave(u))), "left_leg:rot": lambda u: LL(20 * max(0, -wave(u))),
                                               "right_arm:rot": lambda u: R(30 + 20 * max(0, wave(u)), 30, 40), "left_arm:rot": lambda u: Lh(10, 20), "head:rot": lambda u: [10 * max(0, wave(u)), 0, 0]}, loop="loop")
emote("shuffle", "Shuffle", D, 0.6, fns={"right_leg:rot": lambda u: RL(10 * wave(u), 0, 0), "left_leg:rot": lambda u: LL(10 * wave(u, 0.5)), "mw_root:pos": lambda u: move(0.8 * wave(u, 0, 0.5), 0.4 * abs(wave(u)), 0),
                                         "right_arm:rot": lambda u: R(40, 30, -30), "left_arm:rot": lambda u: Lh(40, 30, -30)}, loop="loop")
emote("cossack", "Squat Kicks", D, 0.8, fns={"mw_root:pos": lambda u: move(0, -7, 0), "right_leg:rot": lambda u: RL(90 - 90 * max(0, wave(u))), "left_leg:rot": lambda u: LL(90 - 90 * max(0, wave(u, 0.5))),
                                             "right_arm:rot": lambda u: R(80, -40, 60), "left_arm:rot": lambda u: Lh(80, -40, 60)}, loop="loop")
emote("arm_wave", "Rolling Arm Wave", D, 1.2, fns={"right_arm:rot": lambda u: R(0, 90 + 20 * wave(u, 0.0)), "left_arm:rot": lambda u: Lh(0, 90 - 20 * wave(u, 0.25)), "head:rot": lambda u: [0, 0, 10 * wave(u, 0.15)],
                                                   "body:rot": lambda u: tilt(0, 0, 4 * wave(u, 0.1))}, loop="loop")
emote("headbang", "Headbang", D, 0.4, fns={"head:rot": lambda u: [-20 + 50 * max(0, wave(u)), 0, 0], "body:rot": lambda u: tilt(10 * max(0, wave(u)), 0, 0), "right_arm:rot": lambda u: R(30, 10), "left_arm:rot": lambda u: Lh(30, 10)}, loop="loop")
emote("slow_dance", "Slow Dance", D, 3.0, fns={"right_arm:rot": lambda u: R(70, 20, 20), "left_arm:rot": lambda u: Lh(90, -10, 20), "mw_root:rot": lambda u: [0, 360 * u, 0], "body:rot": lambda u: tilt(0, 0, 4 * wave(u, 0, 2))}, loop="loop")
emote("tap_dance", "Tap Dance", D, 0.5, fns={"right_leg:rot": lambda u: RL(-15 * spike(u, 0, 3, 2), 0, 10 * spike(u, 0, 3, 2)), "left_leg:rot": lambda u: LL(-15 * spike(u, 0.25, 3, 2)), "right_arm:rot": lambda u: R(-10, 30),
                                             "left_arm:rot": lambda u: Lh(-10, 30), "mw_root:pos": lambda u: move(0, 0.4 * spike(u, 0, 3, 2), 0)}, loop="loop",
      events=[(0.0, "footstep", {"foot": "right"}), (0.25, "footstep", {"foot": "left"})])
emote("vogue", "Vogue", D, 2.4, tracks={"right_arm:rot": [(0, R(170, 10)), (0.6, R(170, 10)), (0.65, R(120, -30, 60)), (1.2, R(120, -30, 60)), (1.25, R(90, 90)), (1.8, R(90, 90)), (1.85, R(150, -20, 60)), (2.4, R(170, 10))],
                                        "left_arm:rot": [(0, Lh(-10, 40, 50)), (0.6, Lh(-10, 40, 50)), (0.65, Lh(170, 10)), (1.2, Lh(170, 10)), (1.25, Lh(90, 90)), (1.8, Lh(90, 90)), (1.85, Lh(-10, 40, 50)), (2.4, Lh(-10, 40, 50))],
                                        "head:rot": [(0, [0, 20, 0]), (0.6, [0, 20, 0]), (0.65, [0, -20, 0]), (1.2, [0, -20, 0]), (1.25, Z), (1.8, Z), (1.85, [0, 20, 0]), (2.4, [0, 20, 0])]}, loop="loop")
emote("toprock", "Breakdance Toprock", D, 0.8, fns={"right_leg:rot": lambda u: RL(30 * max(0, wave(u)), 0, 0), "left_leg:rot": lambda u: LL(30 * max(0, wave(u, 0.5))), "body:rot": lambda u: tilt(10, 20 * wave(u), 0),
                                                    "right_arm:rot": lambda u: R(60, 20 + 30 * max(0, wave(u, 0.5)), 30), "left_arm:rot": lambda u: Lh(60, 20 + 30 * max(0, wave(u)), 30), "mw_root:pos": lambda u: move(0, -1, 0)}, loop="loop")
emote("pogo", "Pogo Jumps", D, 0.45, fns={"mw_root:pos": lambda u: move(0, 3 * max(0, wave(u)), 0), "right_arm:rot": lambda u: R(10, 6), "left_arm:rot": lambda u: Lh(10, 6), "head:rot": lambda u: [-10 * max(0, wave(u)), 0, 0]}, loop="loop")
emote("hand_jive", "Hand Jive", D, 1.0, tracks={"right_arm:rot": [(0, R(70, -10, 30)), (0.25, R(70, 10, 30)), (0.5, R(90, -20, 60)), (0.75, R(60, 10, 0)), (1.0, R(70, -10, 30))],
                                                "left_arm:rot": [(0, Lh(70, -10, 30)), (0.25, Lh(70, 10, 30)), (0.5, Lh(60, 10, 0)), (0.75, Lh(90, -20, 60)), (1.0, Lh(70, -10, 30))],
                                                "mw_root:pos": [(0, Z), (0.25, move(0, -0.5, 0)), (0.5, Z), (0.75, move(0, -0.5, 0)), (1.0, Z)]}, loop="loop")
emote("wiggle", "Silly Wiggle", D, 0.5, fns={"mw_root:rot": lambda u: tilt(0, 0, 10 * wave(u)), "body:rot": lambda u: tilt(0, 15 * wave(u, 0.25), 0), "right_arm:rot": lambda u: R(20, 60 + 20 * wave(u)), "left_arm:rot": lambda u: Lh(20, 60 - 20 * wave(u)),
                                             "head:rot": lambda u: [0, 0, -12 * wave(u)]}, loop="loop")
emote("conductor", "Conduct The Orchestra", D, 1.2, fns={"right_arm:rot": lambda u: R(110 + 30 * wave(u), 20 * cwave(u)), "left_arm:rot": lambda u: Lh(90 + 15 * wave(u, 0.5), 20), "head:rot": lambda u: [-10 + 8 * wave(u), 10 * wave(u, 0.25), 0],
                                                         "body:rot": lambda u: tilt(-4, 0, 3 * wave(u))}, loop="loop")

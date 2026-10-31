#!/usr/bin/env python3
"""Writes assets/motionworks/lang/en_us.json: UI strings, boss title cards and a subtitle for every sound event.

Run after generate_assets.py (it reads sounds.json); tools/animgen/test_toolkit.py verifies that
every translation key the Java code and the cinematic sequences use is present.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/motionworks")

UI = {
    "key.categories.motionworks": "MotionWorks",
    "key.motionworks.dodge": "Dodge",
    "key.motionworks.bash": "Shield Bash",
    "key.motionworks.emotes": "Emote Wheel",
    "key.motionworks.inspect": "Inspect Held Item",
    "key.motionworks.skip": "Skip Cinematic",
    "motionworks.emotes.title": "Emotes",
    "motionworks.emotes.hint": "Scroll to change page, click an emote to perform it",
    "motionworks.emotes.group.gestures": "Gestures",
    "motionworks.emotes.group.celebrations": "Celebrations",
    "motionworks.emotes.group.expressions": "Expressions",
    "motionworks.emotes.group.dances": "Dances",
    "motionworks.cinematic.skip": "Press %s to skip",
    "motionworks.cinematic.list": "Cinematics: %s",
    "motionworks.cinematic.playing": "Playing cinematic %s",
    "motionworks.cinematic.unknown": "Unknown cinematic: %s",
    "motionworks.cam.added": "Camera keyframe added (%s in path)",
    "motionworks.cam.cleared": "Camera path cleared%s",
    "motionworks.cam.preview": "Previewing the recorded camera path%s",
    "motionworks.cam.need_two": "Record at least two camera keyframes first%s",
    "motionworks.cam.saved": "Camera path saved to %s",
    "motionworks.cam.failed": "Could not complete the request: %s",
    "motionworks.command.animate": "Playing %s on %s entities",
    "motionworks.command.cinematic": "Playing cinematic %s for %s players",
    "motionworks.play.ok": "Playing %s",
    "motionworks.play.unknown": "Unknown clip: %s",
    "motionworks.play.not_bound": "%s cannot be played on this entity's rig",
    "motionworks.stats": "MotionWorks: %s",
    "motionworks.stats.errors": "%s animation files failed to load; check the log for details",
    "motionworks.list": "%s",
    "motionworks.export": "Animation registry exported to %s",
    "motionworks.trace.on": "Tracing animation triggers within %s blocks",
    "motionworks.trace.off": "Stopped tracing animation triggers",
    "motionworks.trace.entry": "[trace] %s \u25b8 %s",
}

BOSSES = {
    "wither": ("The Wither", "Destroyer of the living"),
    "ender_dragon": ("The Ender Dragon", "Sovereign of the End"),
    "warden": ("The Warden", "It hears your heartbeat"),
    "elder_guardian": ("Elder Guardian", "Keeper of the drowned monument"),
}

GROUP = {"footstep": "Footsteps", "foley": "Gear rustles", "weapon": "Weapon", "impact": "Impact", "body": "Body", "creature": "Creature", "water": "Water",
         "interact": "Interaction", "ambient": "Ambience", "cinematic": "Cinematic", "emote": "Emote"}


def subtitle(name):
    group, _, kind = name.partition(".")
    words = kind.replace("_", " ")
    if group == "footstep":
        return "Footsteps on %s" % words
    if group == "foley":
        return "%s gear rustles" % words.capitalize()
    if group == "impact":
        return "%s impact" % words.capitalize()
    if group == "weapon":
        return {"whoosh light": "Light swing whooshes", "whoosh medium": "Swing whooshes", "whoosh heavy": "Heavy swing whooshes", "draw blade": "Blade drawn",
                "sheathe blade": "Blade sheathed", "draw haft": "Weapon hefted", "bow creak": "Bowstring creaks", "crossbow crank": "Crossbow cranks",
                "shield raise": "Shield raised", "shield bash": "Shield bashes", "parry": "Blow parried"}.get(words, words.capitalize())
    if group == "body":
        return {"land soft": "Soft landing", "land hard": "Hard landing", "roll": "Combat roll", "fall": "Body falls", "dodge": "Quick dodge"}.get(words, words.capitalize())
    if group == "cinematic":
        return {"boom": "Deep boom", "riser": "Rising tension", "sting": "Musical sting", "whoosh": "Dramatic whoosh", "drone": "Ominous drone"}.get(words, words.capitalize())
    return "%s: %s" % (GROUP.get(group, group.capitalize()), words)


def main():
    lang = dict(UI)
    for key, (title, sub) in BOSSES.items():
        lang["motionworks.boss.%s.title" % key] = title
        lang["motionworks.boss.%s.subtitle" % key] = sub
    with open(os.path.join(ASSETS, "sounds.json"), encoding="utf-8") as fh:
        sounds = json.load(fh)
    for name, ev in sounds.items():
        lang[ev["subtitle"]] = subtitle(name)
    os.makedirs(os.path.join(ASSETS, "lang"), exist_ok=True)
    with open(os.path.join(ASSETS, "lang/en_us.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(sorted(lang.items())), fh, indent=1, ensure_ascii=False)
    print("lang entries:", len(lang))


if __name__ == "__main__":
    main()

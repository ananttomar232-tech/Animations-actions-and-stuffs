"""Clips that go into the ground on purpose. Everything else on a walking creature is kept above it at runtime by
GroundContact (client/rig/GroundContact.java); these opt out with meta "ground": "free". The in-game library audit
(/mw audit) lists every clip whose body dips below the feet, tagged LIFTED or FREE.
"""

FREE = {
    "sniffer.dig": "the sniffer buries its nose to dig, as in vanilla",
    "sniffer.dig_start": "the sniffer buries its nose to dig, as in vanilla",
    "sniffer.dig_finish": "the sniffer buries its nose to dig, as in vanilla",
    "sniffer.rise_after_dig": "starts with the nose still in the ground",
    "sniffer.scenting": "nose pressed to the ground",
    "cine.sniffer.discover_seed": "the sniffer digs up the seed",
    "zombie.rise_from_ground": "climbs out of the earth",
    "cine.warden.intro_emerge_roar": "the warden emerges from the ground, as in vanilla",
    "cine.warden.listen_then_leave": "the warden digs back into the ground, as in vanilla",
    "fox.snow_dive": "dives head first into snow, as vanilla's pounce",
    "fox.mouse_pounce": "dives head first into the ground, as vanilla's pounce",
    "fox.env_powder_snow_dive": "dives into powder snow",
    "player.env.powder_snow_sinking": "sinks into powder snow",
    "cine.player.climb_ledge_pull": "pulls up from below a ledge",
}


def apply(clips):
    known = {c.id for c in clips}
    unknown = sorted(set(FREE) - known)
    if unknown:
        raise ValueError("ground.FREE lists clips that do not exist: %s" % unknown)
    for c in clips:
        if c.id in FREE:
            c.meta["ground"] = "free"

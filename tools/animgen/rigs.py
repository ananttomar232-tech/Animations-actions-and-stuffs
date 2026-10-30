"""Bone vocabularies of every animated target, derived from the vanilla 1.20.1 layer definitions.

Each entry lists the part names the runtime rig discovery finds for that entity's model
(plus the virtual mw_root / mw_center bones). The validator rejects clips that reference
bones their target does not have, so this file is the contract between authoring and runtime.
"""

VIRTUAL = ["mw_root", "mw_center"]

HUMANOID = ["head", "hat", "body", "right_arm", "left_arm", "right_leg", "left_leg"]
PLAYER = HUMANOID + ["left_sleeve", "right_sleeve", "left_pants", "right_pants", "jacket", "ear", "cloak"]
PIGLIN = PLAYER + ["left_ear", "right_ear"]
VILLAGER = ["head", "hat", "hat_rim", "nose", "body", "jacket", "arms", "right_leg", "left_leg"]
WITCH = VILLAGER + ["hat2", "hat3", "hat4", "mole"]
ILLAGER = ["head", "hat", "nose", "body", "arms", "left_shoulder", "right_arm", "left_arm", "right_leg", "left_leg"]
ZOMBIE_VILLAGER = HUMANOID + ["hat_rim", "nose"]
QUAD = ["head", "body", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg"]
HORSE = ["body", "tail", "head_parts", "head", "mane", "upper_mouth", "left_ear", "right_ear", "left_hind_leg", "right_hind_leg",
         "left_front_leg", "right_front_leg"]
FP = ["fp_main", "fp_off", "fp_main_item", "fp_off_item", "fp_view"]

ENTITY_BONES = {
    # players and humanoid mobs
    "@player": PLAYER,
    "@first_person": FP,
    "minecraft:zombie": HUMANOID, "minecraft:husk": HUMANOID, "minecraft:drowned": HUMANOID, "minecraft:giant": HUMANOID,
    "minecraft:skeleton": HUMANOID, "minecraft:stray": HUMANOID, "minecraft:wither_skeleton": HUMANOID,
    "minecraft:piglin": PIGLIN, "minecraft:piglin_brute": PIGLIN, "minecraft:zombified_piglin": PIGLIN,
    "minecraft:enderman": HUMANOID,
    "minecraft:zombie_villager": ZOMBIE_VILLAGER,
    "minecraft:villager": VILLAGER, "minecraft:wandering_trader": VILLAGER, "minecraft:witch": WITCH,
    "minecraft:pillager": ILLAGER, "minecraft:vindicator": ILLAGER, "minecraft:evoker": ILLAGER, "minecraft:illusioner": ILLAGER,
    "minecraft:iron_golem": ["head", "body", "right_arm", "left_arm", "right_leg", "left_leg"],
    "minecraft:snow_golem": ["head", "upper_body", "lower_body", "right_arm", "left_arm"],
    "minecraft:vex": ["root", "head", "body", "right_arm", "left_arm", "right_wing", "left_wing"],
    "minecraft:allay": ["root", "head", "body", "right_arm", "left_arm", "right_wing", "left_wing"],
    # hostile non-humanoids
    "minecraft:creeper": QUAD,
    "minecraft:spider": ["head", "body0", "body1"] + [f"{s}_{p}_leg" for s in ("right", "left") for p in ("hind", "middle_hind", "middle_front", "front")],
    "minecraft:blaze": ["head"] + [f"part{i}" for i in range(12)],
    "minecraft:ghast": ["body"] + [f"tentacle{i}" for i in range(9)],
    "minecraft:slime": ["cube", "right_eye", "left_eye", "mouth"],
    "minecraft:magma_cube": [f"cube{i}" for i in range(8)] + ["inside_cube"],
    "minecraft:guardian": ["root", "head", "eye", "tail0", "tail1", "tail2"] + [f"spike{i}" for i in range(12)],
    "minecraft:phantom": ["root", "body", "head", "left_wing_base", "left_wing_tip", "right_wing_base", "right_wing_tip", "tail_base", "tail_tip"],
    "minecraft:ravager": ["root", "neck", "head", "mouth", "left_horn", "right_horn", "body", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg"],
    "minecraft:hoglin": ["head", "left_ear", "right_ear", "left_horn", "right_horn", "body", "mane", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg"],
    "minecraft:warden": ["root", "bone", "body", "head", "left_tendril", "right_tendril", "left_ribcage", "right_ribcage", "right_arm", "left_arm", "right_leg", "left_leg"],
    "minecraft:wither": ["shoulders", "ribcage", "tail", "center_head", "right_head", "left_head"],
    "minecraft:shulker": ["base", "lid", "head"],
    "minecraft:silverfish": [f"segment{i}" for i in range(7)] + [f"layer{i}" for i in range(3)],
    "minecraft:endermite": [f"segment{i}" for i in range(4)],
    "minecraft:ender_dragon": [],
    # passive
    "minecraft:cow": QUAD, "minecraft:mooshroom": QUAD, "minecraft:pig": QUAD, "minecraft:sheep": QUAD,
    "minecraft:polar_bear": QUAD, "minecraft:panda": QUAD,
    "minecraft:turtle": QUAD + ["egg_belly"],
    "minecraft:llama": QUAD + ["right_chest", "left_chest"], "minecraft:trader_llama": QUAD + ["right_chest", "left_chest"],
    "minecraft:goat": QUAD + ["left_horn", "right_horn", "nose"],
    "minecraft:horse": HORSE, "minecraft:donkey": HORSE + ["left_chest", "right_chest"], "minecraft:mule": HORSE + ["left_chest", "right_chest"],
    "minecraft:skeleton_horse": HORSE, "minecraft:zombie_horse": HORSE,
    "minecraft:camel": ["body", "hump", "tail", "head", "left_ear", "right_ear", "left_hind_leg", "right_hind_leg", "left_front_leg", "right_front_leg"],
    "minecraft:wolf": ["head", "real_head", "body", "upper_body", "tail", "real_tail", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg"],
    "minecraft:cat": ["head", "body", "tail1", "tail2", "left_hind_leg", "right_hind_leg", "left_front_leg", "right_front_leg"],
    "minecraft:ocelot": ["head", "body", "tail1", "tail2", "left_hind_leg", "right_hind_leg", "left_front_leg", "right_front_leg"],
    "minecraft:fox": ["head", "right_ear", "left_ear", "nose", "body", "tail", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg"],
    "minecraft:rabbit": ["head", "right_ear", "left_ear", "nose", "body", "tail", "left_haunch", "right_haunch", "left_hind_foot", "right_hind_foot",
                         "left_front_leg", "right_front_leg"],
    "minecraft:chicken": ["head", "beak", "red_thing", "body", "right_wing", "left_wing", "right_leg", "left_leg"],
    "minecraft:parrot": ["head", "head2", "beak1", "beak2", "feather", "body", "tail", "left_wing", "right_wing", "left_leg", "right_leg"],
    "minecraft:bee": ["bone", "body", "stinger", "left_antenna", "right_antenna", "right_wing", "left_wing", "front_legs", "middle_legs", "back_legs"],
    "minecraft:bat": ["head", "right_ear", "left_ear", "body", "right_wing", "right_wing_tip", "left_wing", "left_wing_tip"],
    "minecraft:axolotl": ["body", "head", "top_gills", "left_gills", "right_gills", "right_hind_leg", "left_hind_leg", "right_front_leg", "left_front_leg", "tail"],
    "minecraft:frog": ["root", "body", "head", "eyes", "right_eye", "left_eye", "croaking_body", "tongue", "left_arm", "left_hand", "right_arm",
                       "right_hand", "left_leg", "left_foot", "right_leg", "right_foot"],
    "minecraft:sniffer": ["bone", "body", "head", "left_ear", "right_ear", "nose", "lower_beak", "right_front_leg", "right_mid_leg",
                          "right_hind_leg", "left_front_leg", "left_mid_leg", "left_hind_leg"],
    "minecraft:dolphin": ["body", "back_fin", "left_fin", "right_fin", "tail", "tail_fin", "head", "nose"],
    "minecraft:squid": ["body"] + [f"tentacle{i}" for i in range(8)],
    "minecraft:glow_squid": ["body"] + [f"tentacle{i}" for i in range(8)],
    "minecraft:cod": ["body", "head", "nose", "right_fin", "left_fin", "tail_fin", "top_fin"],
    "minecraft:salmon": ["body_front", "body_back", "head", "top_front_fin", "top_back_fin", "back_fin", "right_fin", "left_fin"],
    "minecraft:tropical_fish": ["body", "tail", "right_fin", "left_fin", "top_fin"],
    "minecraft:pufferfish": ["body", "right_blue_fin", "left_blue_fin", "top_front_fin", "top_middle_fin", "top_back_fin", "right_front_fin",
                             "left_front_fin", "bottom_front_fin", "bottom_middle_fin", "bottom_back_fin", "right_back_fin", "left_back_fin"],
    "minecraft:tadpole": ["body", "tail"],
    "minecraft:strider": ["body", "right_leg", "left_leg", "right_bottom_bristle", "right_middle_bristle", "right_top_bristle",
                          "left_top_bristle", "left_middle_bristle", "left_bottom_bristle"],
}
for k in list(ENTITY_BONES):
    ENTITY_BONES[k] = VIRTUAL + ENTITY_BONES[k] if k != "@first_person" else ["mw_root", "mw_center"] + ENTITY_BONES[k]

GROUPS = {
    "@humanoid": ["@player", "minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:skeleton", "minecraft:stray",
                  "minecraft:wither_skeleton", "minecraft:piglin", "minecraft:piglin_brute", "minecraft:zombified_piglin",
                  "minecraft:enderman", "minecraft:zombie_villager", "minecraft:giant"],
    "@undead_humanoid": ["minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:zombie_villager", "minecraft:giant"],
    "@skeletal": ["minecraft:skeleton", "minecraft:stray", "minecraft:wither_skeleton"],
    "@piglins": ["minecraft:piglin", "minecraft:piglin_brute", "minecraft:zombified_piglin"],
    "@villagers": ["minecraft:villager", "minecraft:wandering_trader"],
    "@illagers": ["minecraft:pillager", "minecraft:vindicator", "minecraft:evoker", "minecraft:illusioner"],
    "@quadruped": ["minecraft:cow", "minecraft:mooshroom", "minecraft:pig", "minecraft:sheep", "minecraft:polar_bear", "minecraft:panda",
                   "minecraft:llama", "minecraft:trader_llama", "minecraft:goat", "minecraft:creeper", "minecraft:turtle"],
    "@equine": ["minecraft:horse", "minecraft:donkey", "minecraft:mule", "minecraft:skeleton_horse", "minecraft:zombie_horse"],
    "@fish": ["minecraft:cod", "minecraft:salmon", "minecraft:tropical_fish", "minecraft:pufferfish"],
    "@cephalopod": ["minecraft:squid", "minecraft:glow_squid"],
    "@living": [],
}


def bones_for(target):
    """Bones guaranteed to exist for a target (intersection over a group's members)."""
    if target in ENTITY_BONES:
        return set(ENTITY_BONES[target])
    members = GROUPS.get(target)
    if members is None:
        raise KeyError("unknown target " + target)
    if not members:
        return set(VIRTUAL)
    s = None
    for m in members:
        b = bones_for(m)
        s = b if s is None else s & b
    return s


# Which clip targets each entity uses (most specific first). Becomes assets/.../entities.json.
def families():
    fam = {}
    rig_of = {
        "@player": "player",
        "minecraft:zombie": "humanoid", "minecraft:husk": "humanoid", "minecraft:drowned": "humanoid", "minecraft:giant": "humanoid",
        "minecraft:skeleton": "humanoid", "minecraft:stray": "humanoid", "minecraft:wither_skeleton": "humanoid",
        "minecraft:piglin": "player", "minecraft:piglin_brute": "player", "minecraft:zombified_piglin": "player",
        "minecraft:enderman": "humanoid", "minecraft:zombie_villager": "humanoid",
        "minecraft:villager": "villager", "minecraft:wandering_trader": "villager", "minecraft:witch": "villager",
        "minecraft:pillager": "illager", "minecraft:vindicator": "illager", "minecraft:evoker": "illager", "minecraft:illusioner": "illager",
        "minecraft:iron_golem": "golem", "minecraft:snow_golem": "snow_golem",
        "minecraft:wolf": "wolf", "minecraft:cat": "feline", "minecraft:ocelot": "feline", "minecraft:fox": "fox",
        "minecraft:horse": "equine", "minecraft:donkey": "equine", "minecraft:mule": "equine", "minecraft:skeleton_horse": "equine",
        "minecraft:zombie_horse": "equine", "minecraft:camel": "camel",
    }
    for target in ENTITY_BONES:
        if target.startswith("@"):
            continue
        targets = [target]
        for g, members in GROUPS.items():
            if target in members:
                targets.append(g)
        targets.append("@living")
        fam[target] = {"rig": rig_of.get(target, "quadruped" if target in GROUPS["@quadruped"] else "generic"), "targets": targets}
    fam["minecraft:player"] = {"rig": "player", "targets": ["@player", "@humanoid", "@living"]}
    return fam

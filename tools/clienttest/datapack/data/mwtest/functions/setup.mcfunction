gamemode creative @s
tp @s ~ ~ ~ 0 10
summon minecraft:sheep ~2.5 ~ ~5
summon minecraft:villager ~-1.5 ~ ~6 {NoAI:1b,VillagerData:{profession:"minecraft:farmer",level:2,type:"minecraft:plains"}}
summon minecraft:wolf ~0.5 ~ ~4
summon minecraft:chicken ~1 ~ ~3
summon minecraft:zombie ~4 ~ ~9 {PersistenceRequired:1b}
summon minecraft:iron_golem ~-3 ~ ~11
# A half-block ramp rising toward +x, with a cow and a horse straddling its first step (terrain alignment)
execute align xyz run fill ~-10 ~ ~5 ~-5 ~3 ~13 minecraft:air
execute align xyz run fill ~-9 ~ ~6 ~-9 ~ ~12 minecraft:smooth_stone_slab
execute align xyz run fill ~-8 ~ ~6 ~-7 ~ ~12 minecraft:stone
execute align xyz run fill ~-7 ~1 ~6 ~-7 ~1 ~12 minecraft:smooth_stone_slab
execute align xyz run fill ~-6 ~ ~6 ~-6 ~1 ~12 minecraft:stone
execute align xyz run summon minecraft:cow ~-8 ~1 ~6.5 {NoAI:1b,Rotation:[-90f,0f]}
execute align xyz run summon minecraft:horse ~-8 ~1 ~9.5 {NoAI:1b,Rotation:[-90f,0f],Variant:2}
# An axolotl on dry ground for the play-dead check
execute align xyz run summon minecraft:axolotl ~-3 ~ ~3 {NoAI:1b,Rotation:[90f,0f]}
# Animated by body plan (the test resource pack removes their families), as a mob from another mod would be
summon minecraft:pig ~3.5 ~ ~7 {NoAI:1b}
summon minecraft:husk ~1.5 ~ ~6.5 {NoAI:1b,PersistenceRequired:1b}
summon minecraft:wandering_trader ~-3 ~ ~7 {NoAI:1b}
say mwtest scene ready

execute as @a run scoreboard players add @s mwt 1
execute as @a[scores={mwt=60}] at @s run function mwtest:setup
execute as @a[scores={mwt=180}] at @s run summon minecraft:tnt ~-8 ~ ~18 {Fuse:1}
execute as @a[scores={mwt=230}] at @s run summon minecraft:lightning_bolt ~30 ~ ~40
execute as @a[scores={mwt=280}] run motionworks cinematic @s "user:turntable"

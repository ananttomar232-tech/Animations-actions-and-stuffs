execute as @a run scoreboard players add @s mwt 1
execute as @a[scores={mwt=60}] at @s run function mwtest:setup
execute as @a[scores={mwt=180}] at @s run summon minecraft:tnt ~-8 ~ ~22 {Fuse:1}
execute as @a[scores={mwt=230}] at @s run summon minecraft:lightning_bolt ~30 ~ ~40
execute as @a[scores={mwt=270}] at @s align xyz run tp @s ~-7.7 ~1 ~11.5 -90 0
execute as @a[scores={mwt=280}] run motionworks cinematic @s "user:turntable"

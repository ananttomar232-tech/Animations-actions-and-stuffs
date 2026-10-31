# MotionWorks: Cinematic Animation Overhaul

A Forge mod for Minecraft 1.20.1 that replaces vanilla's procedural limb swinging with a data-driven skeletal
animation engine, and builds a cinematic camera, a living environment and new combat feel on top of it. It is
client-heavy but server-aware: the server sends the events the client cannot see (a mob's ambient sound, a
projectile launch, a parry), and every client animates them the same way.

Everything runs without shader packs. The optional foliage vertex shaders turn themselves off when Oculus or
Embeddium is installed.

## At a glance

| | |
|---|---|
| Animation clips | **2,518**, all trigger-bound, in 15 categories (table below) |
| Cinematic sequences | 27 authored, skippable, plus your own recorded with `/mw cam` |
| Entity coverage | 80 entity families on 13 rig profiles: players, every vanilla mob, villagers and illagers |
| Assets | 18 particle types, 60 sound events (109 generated OGG files), English translations |
| Tests | 40 JUnit tests, 6 in-game GameTests, 20 toolkit tests, and a headless client smoke test |

| Category | Clips | Required |
|---|---:|---:|
| Player locomotion | 180 | 180 |
| Player combat | 220 | 220 |
| Player interactions | 220 | 220 |
| First person | 231 | 180 |
| Passive mobs | 318 | 300 |
| Hostile mobs | 255 | 250 |
| Villagers and NPCs | 160 | 160 |
| Environmental interactions | 193 | 180 |
| Cinematic | 155 | 150 |
| Emotes | 122 | 120 |
| Mounts and riding | 101 | 100 |
| Swimming | 80 | 80 |
| Aerial | 80 | 80 |
| Damage reactions | 101 | 100 |
| Contextual transitions | 102 | 100 |

Every clip is listed with its id, name, category, target, trigger, duration, priority, model, controller and
status in [`docs/animation_registry.csv`](docs/animation_registry.csv) and
[`docs/ANIMATION_INVENTORY.md`](docs/ANIMATION_INVENTORY.md). The build fails if two clips are the same motion
under another speed, amplitude, mirror or phase (see *Uniqueness* below).

## What it does

**Animation engine** (`engine/`, no Minecraft dependencies). Clips are keyframed curves (linear, step, or
smooth auto-clamped Hermite that never overshoots an authored pose and loops seamlessly) or Molang-style
expressions over 171 context variables. Seven layers (base, overlay, action, gesture, then additive posture,
additive and reaction) blend as `final = lerp(vanilla, rest + override, weight) + additive`. Clips start from
state conditions, events (`"shoot:arrow"` also fires `"shoot"`) or manual play, with priorities, cooldowns,
chance, `stop_when` exits and deterministic per-entity variant selection, so every client picks the same
variant. Procedural layers add springs, life noise and expression drivers.

**Rigs** (`client/rig/`). Model parts are found by their layer-definition names, so rigs work on any vanilla
or modded model without obfuscated field names. Rig profiles add virtual bones (`mw_root` at the ground,
`mw_center` at the body centre), parent couplings (the torso pivots at the hips and carries head and arms),
followers (outer skin layers follow their limbs), and terrain alignment. Four-legged mobs pitch to the slope
under them. Each frame the applier restores whatever vanilla did not rewrite, so poses never accumulate.

**Players and first person.** Locomotion, combat (combos, charged swings, blocking, ranged weapons), every
interaction, swimming, flying, riding, damage and recovery. A separate first-person animator drives the hands
and held items, with weapon sway and inspect animations. It mirrors automatically for left-handed players.

**Mobs and villagers.** Every vanilla mob has idles, locomotion and reactions, including thunder, explosions,
fire and rain. Villagers and illagers get professions, trading, gossip and conversations: `SocialDirector`
forms groups only when members face each other with line of sight, and speaking turns are deterministic across
clients. Each entity has a stable personality derived from its UUID (energy, curiosity, nervousness,
sociability, confidence) and a mood from health, threats and weather. Clips use these in their conditions
and weights, so two cows of the same breed do not behave identically.

**Cinematics** (`client/cinematic/`). Data-driven sequences with 18 shot types (orbit, crane, dolly, track,
spline, pan, close-up, over-the-shoulder, reveal ...) and timeline events (actor animations, titles, dialogue, sound,
particles, fades, flashes, shake, letterbox, slow motion). They are always skippable unless an author opts
out, and end when you take damage unless the sequence opts out. Boss intros default to title cards that keep
the camera on the player; the full intro only takes the camera in creative, spectator or peaceful. `/mw cam` records camera paths into reusable sequences.

**Living environment.** A shared wind field (a pure function of synced world time, so every client sees the
same gusts) drives foliage, banners, particles and animation. Ambient effects include leaves, embers,
fireflies, pollen, dust motes and blown rain. Explosions leave smoke, a shockwave and debris. Lightning and
blasts are positional world events that nearby creatures react to by distance and direction.

**Combat feel** (server-authoritative, each with a config switch). Directional dodge with brief
invulnerability, shield parry with a stagger and counter window, shield bash, and landing rolls. Weapon trails
and impact particles are keyed to animation events.

**Faces and equipment.** An optional facial layer finds the eyes in the entity's own texture and animates
blinks, gaze and brows (and a mouth for players) using that texture's pixels. Unheld weapons, shields and
quivers ride on the back and hip.

## Requirements and installation

- Minecraft 1.20.1 with Forge 47.x (built against 47.4.28), Java 17.
- Install on the client. Install on the server as well for server-sent triggers (mob vocalisations, projectile
  launches, explosions and lightning reactions) and the combat mechanics. Vanilla clients can join a
  MotionWorks server, and a MotionWorks client works on vanilla servers with locally detectable animations.

Build from source:

```
./gradlew build            # mod jar in build/libs/
```

## Controls and commands

| Key (default) | Action |
|---|---|
| Left Alt | Dodge in the movement direction |
| V | Shield bash |
| B | Emote wheel (scroll to change page) |
| Y | Inspect the held item |
| Backspace | Skip a cinematic |

| Command | Where | Purpose |
|---|---|---|
| `/mw play <clip>`, `/mw emote <clip>` | client | Play a clip on yourself (emotes are sent to nearby players) |
| `/mw list [filter]`, `/mw stats`, `/mw debug`, `/mw export` | client | Browse the library, show load statistics, toggle the debug overlay, export the registry |
| `/mw cinematic play <id>`, `stop`, `list` | client | Preview cinematics locally |
| `/mw cam add`, `clear`, `preview`, `save <name>` | client | Record a camera path and save it as `user:<name>` |
| `/motionworks cinematic <players> <id> [anchor]`, `... stop` | server, op | Play a cinematic for players |
| `/motionworks animate <entities> <clip>` | server, op | Play a clip on entities for everyone nearby |
| `/motionworks trace on\|off` | server, op | Print every animation trigger the server sends within 48 blocks: which event names fire, so packs can bind clips to them |

## Configuration

`config/motionworks-client.toml` has sections `animation`, `firstPerson`, `camera`, `cinematics`,
`environment`, `particles`, `sound`, `faces`, `acting` and `sync`: global and per-system switches, intensity,
animation distance, camera shake strength, letterbox and HUD hiding, foliage and banner wind, particle budget,
footsteps, foley, weapon trails, faces, personality and conversations. `config/motionworks-common.toml` has
`sync` (trigger broadcasting), `combat` (dodge, parry window, shield bash, counter attacks, landing rolls)
and `social` (emotes). Every option documents itself in the file.

## Extending it

Clips, rig profiles, entity families and cinematics are resource-pack data under
`assets/<namespace>/motionworks/`. Bedrock/Blockbench animation JSON imports directly.

- [`docs/AUTHORING.md`](docs/AUTHORING.md): clip format, triggers, layers, rig profiles, events,
  cinematics and the authoring toolkit.
- [`docs/CONTEXT_VARIABLES.md`](docs/CONTEXT_VARIABLES.md): every `q.*` variable and the code that computes it
  (generated from the sources).
- [`docs/TESTING.md`](docs/TESTING.md): what is tested, how, and how to run each layer.

## Uniqueness

The library is authored in Python (`tools/animgen/`) and exported to JSON. Two validators compare every pair
of clips that animate the same bones: a fast amplitude-normalised screen in Python, and the authoritative
`MotionSignature` in Java (`ShippedLibraryTest`), which evaluates expressions too. Both normalise time and
amplitude and also compare phase-shifted and left/right-mirrored copies. A clip that is only another one
played faster, scaled, mirrored or offset fails the build.

## Known limitations

- The Ender Dragon is animated as a whole body (root motion and reactions), not per wing.
- Villager models have a single folded-arms part, so villager gestures move both arms together.
- Clips are authored right-handed. First person mirrors for left-handed players; third-person poses do not.
- The foliage vertex shaders are disabled when Oculus or Embeddium is present (they replace the same shaders).
  Everything else works with them.
- Client rendering has been verified headlessly under Xvfb with software OpenGL (see `docs/TESTING.md`). That
  covers boot, mixins, world join, scene animation and cinematics, but not a real GPU or other mods.

## License

MIT

# Authoring animations, rigs and cinematics

Everything MotionWorks animates is data. Resource packs (and other mods) can add or override clips, rig
profiles, entity families and cinematics without code.

| Path in a resource pack | Contents |
|---|---|
| `assets/<ns>/motionworks/animations/**/*.json` | Clips (MotionWorks format, or Bedrock/Blockbench animation JSON) |
| `assets/<ns>/motionworks/rigs/<id>.json` | Rig profiles |
| `assets/<ns>/motionworks/entities.json` | Which rig and clip targets each entity type uses |
| `assets/<ns>/motionworks/cinematics/<id>.json` | Cinematic sequences, played as `<ns>:<id>` |
| `config/motionworks/cinematics/<name>.json` | Your own sequences (from `/mw cam save`), played as `user:<name>` |

Reload with F3+T. `/mw stats` reports what loaded and how many files failed (the log says why).

## Clips

```json
{
  "clips": {
    "mypack.cow.sniff_ground": {
      "name": "Cow Sniffing The Ground",
      "category": "passive_mobs",
      "target": "minecraft:cow",
      "length": 2.4,
      "loop": "once",
      "layer": "gesture",
      "priority": 140,
      "blend_in": 0.2,
      "blend_out": 0.3,
      "trigger": {"type": "state", "when": "q.ground_speed < 0.01 && q.idle_time > 4", "cooldown": 20, "chance": 0.3},
      "bones": {
        "head": {"rotation": {"keys": {"0": [0, 0, 0], "0.6": [35, 10, 0], "1.8": [35, 10, 0], "2.4": [0, 0, 0]}, "lerp": "smooth"}},
        "mw_center": {"position": {"0": [0, 0, 0], "0.6": {"v": [0, 0, -1], "e": "out_back"}, "2.4": [0, 0, 0]}}
      },
      "events": [{"time": 0.7, "type": "particle", "particle": "dust_puff", "at": "mouth", "count": 3}]
    }
  }
}
```

| Field | Meaning |
|---|---|
| `target` | An entity type id (`minecraft:cow`) or a shared target (`@player`, `@humanoid`, `@living` ...) that entity families list |
| `rig` | Bone vocabulary the clip is written for, if it differs from the target |
| `length` | Seconds. Omit to use the last key |
| `loop` | `once` (fade out at the end), `hold` (keep the last pose until replaced) or `loop` |
| `layer` | `base`, `overlay`, `action`, `gesture` (overriding) or `posture`, `additive`, `reaction` (additive) |
| `priority` | Within a layer, the higher priority wins |
| `blend_in`, `blend_out` | Crossfade times in seconds |
| `additive` | Values are added to the pose instead of replacing it (implied on additive layers) |
| `mask` | Bone groups or bones the clip may touch (`["upper"]`) |
| `speed`, `time`, `weight` | Expressions: playback rate, a driver for clip time (phase-locked locomotion, e.g. `q.limb_swing * 0.25`), and a blend weight |
| `interruptible`, `interrupt_after` | Whether, and after which fraction, a higher-priority clip may cut in |
| `meta` | Free-form strings. The registry export reads `controller`, `model`, `status` and `testing`; emotes set `emote` and `emote_group` |

The pose is `final = lerp(vanilla, rest + override, weight) + additive`. Rotations are degrees, positions are
model pixels (y points down in model space), scale is a multiplier.

**Keys.** A channel is a constant vector, a map of time to vector, or `{"keys": {...}, "lerp": ..., "ease": ...}`
to set defaults. A key can be `{"v": [...], "e": "<easing>", "l": "<lerp>"}`, or `{"pre": [...], "post": [...]}`
for a jump. `lerp` is how the segment *ending* at that key is interpolated:

- `linear` (default)
- `step`
- `smooth`: auto-clamped cubic Hermite. It passes exactly through every key, never overshoots a hold or a
  peak, uses time-aware tangents through unevenly spaced keys, and wraps seamlessly across the seam of a
  looping clip whose first and last keys match. `catmullrom` and `spline` are accepted as synonyms.

Easings: `linear step snap` and `in_`/`out_`/`in_out_` + `sine quad cubic quart quint expo circ back elastic bounce`.

**Expressions** are Molang-style: `q.*` context variables (see [`CONTEXT_VARIABLES.md`](CONTEXT_VARIABLES.md)),
`math.sin`/`math.cos` in degrees, `math.clamp`, `math.abs`, `math.random` (seeded per entity), arithmetic,
comparisons, `&&`, `||`, `!`, `?:`, `??`, and string comparison against quoted names
(`q.main_hand == 'sword'`). Any number in a key can be an expression string.

**Bones** are the model's own part names (`head`, `right_arm`, `left_hind_leg`, `tail1` ...) plus two virtual
bones applied to the whole model: `mw_root` pivots at the ground and `mw_center` at the body centre (measured
from the model unless the rig sets `ground` and `center`). Bones the entity's model lacks are skipped, so one
humanoid clip drives players, zombies and piglins.

A part rotates and scales about its **pivot**. Some vanilla models place a part's box far from its pivot (a
slime's body hangs 17 px below it, a guardian's eye 15 px), so scaling that part slides its box away from its
neighbours. For whole-body squash and stretch, scale `mw_root`. To grow such a part in place, add a matching
position track; `mobkit.anchored(scale_keys, centre)` writes it. `/mw audit` reports any scale track that moves
a box off its pivot.

**Ground contact.** For a creature standing on the ground, anything but its legs that dips below the feet
lifts the whole model, so rolls and lying poses rest on the floor. A clip that goes underground on purpose
(a sniffer digging, a warden emerging) sets meta `"ground": "free"`; the shipped ones are listed with reasons
in `tools/animgen/ground.py`.

## Triggers

| `type` | Starts when | Fields |
|---|---|---|
| `state` | `when` holds; the best candidate per layer is chosen every selection tick | `when`, `group`, `weight`, `min_time`, `exit_delay` |
| `event` | the event fires and `when` holds | `event`, `when`, `cooldown`, `chance` |
| `manual` | played by a command, a cinematic or the emote wheel | `stop_when` |

All types accept `stop_when`. Clips in the same `group` are variants: one is picked by `weight` with a
deterministic per-entity seed, so every client picks the same one.

An event with an argument fires both forms: `"shoot"` with argument `"arrow"` reaches clips triggered by
`shoot` and by `shoot:arrow`. Common events:

- **Movement:** `jump`, `land`, `start_moving`, `stop_moving`, `sprint_start`, `sneak_start`, `climb_start`,
  `enter_water`, `submerge`, `surface`, `fly_start`, `glide_start`, `riptide_start`, `ledge_reached`
- **Combat:** `swing`, `attack`, `hit`, `miss`, `hurt:<kind>`, `hurt_front|back|left|right`, `guard_up`,
  `parry`, `parried`, `shield_bash`, `staggered`, `dodge:<dir>`, `counter`, `shoot:<projectile>`, `death`
- **Use:** `use_start`, `use_finish`, `eat_start`, `item_switch`, `place`, `break_block`, `dig_start`,
  `fish_cast`, `trade_open`, `trade_complete`, `inspect`
- **Server-sent:** `vocalize` (each ambient sound), `teleport`, `totem`, `spawn`, `respawn`, `boss_slain:<boss>`,
  `explosion_flinch`, `rider_on`
- **World:** `thunderclap:near|far`, `explosion:near|far`, `daybreak`, `nightfall`, `rain_start`

`event_dir` (degrees, the source's direction relative to the body) and `event_height` come with directional
events. The complete list is whatever `tools/animgen/build.py --check` accepts. On a server, `/motionworks
trace on` prints each trigger as it is sent near you, with its argument.

## Clip events

Timed `events` fire as the clip passes them: `footstep` (`foot`), `sound` (`sound`, `volume`, `pitch`, `var`),
`whoosh` (`weight`), `foley` (`kind`, `volume`), `particle` (`particle`, `at`, `count`, `spread`, `speed`),
`shake` (`amount`, `radius`), `impact` (`material`, `strength`), `stomp`, `trail` (`state`, `hand`) and
`breath`. Faint instances that are crossfading out are skipped, so nothing doubles up.

## Rig profiles

```json
{
  "extends": "quadruped",
  "groups": {"upper": ["head", "body"]},
  "followers": {"hat": "head"},
  "couplings": [{"parent": "body", "pivot": [0, 12, 0], "move_parent": true, "children": ["head", "right_arm", "left_arm"]}],
  "springs": [{"bone": "tail", "targets": ["q.ground_speed * -200", null, null], "stiffness": 60, "damping": 8, "limit": 40}],
  "life_noise": [{"bone": "head", "amplitude": 1.2, "frequency": 0.12, "scale": "q.ground_speed < 0.01 ? 1 : 0.2"}],
  "drivers": [{"bone": "mw_root", "group": "rotation", "exprs": ["math.clamp(-q.terrain_pitch * 0.9, -30, 30)", null, null], "half_life": 0.12}],
  "center": [0, 12, 0],
  "ground": [0, 24, 0]
}
```

- **followers** copy a leader part after posing (skin overlay layers follow their limbs).
- **couplings** make a part a virtual parent: rotating the torso about `pivot` carries the children with it,
  and `move_parent` moves the torso itself about that pivot.
- **springs** are damped secondary motion toward expression targets (degrees).
- **life_noise** adds small, continuous, per-entity noise so nothing is ever perfectly still.
- **drivers** set a channel from expressions with smoothing. The shipped four-legged rigs use them for
  terrain alignment.
- `center` and `ground` are the pivots of `mw_center` and `mw_root` in model pixels. Leave them out to use
  the centre and bottom centre of the model's rest geometry.
- `extends` inherits everything; lists you set replace the inherited ones.

`entities.json` maps entity types to a rig and the clip targets they use:
`{"minecraft:cow": {"rig": "quadruped", "targets": ["minecraft:cow", "@quadruped", "@living"]}}`.

## Cinematics

```json
{
  "name": "Sunset Ride",
  "anchor": "@self",
  "letterbox": true, "skippable": true, "hide_hud": true, "cancel_on_damage": true,
  "shots": [
    {"type": "establishing", "duration": 5},
    {"type": "orbit", "target": "@nearest:minecraft:horse", "duration": 6, "radius": 5, "height": 1.2,
     "from_angle": -40, "to_angle": 40, "transition": {"type": "blend", "duration": 1.0}}
  ],
  "events": [
    {"time": 0, "type": "fade", "from": 1, "to": 0, "duration": 1.5},
    {"time": 1, "type": "title", "title": "mypack.title", "subtitle": "mypack.subtitle", "duration": 3},
    {"time": 5, "type": "animate", "actor": "@self", "clip": "emote.wave"}
  ]
}
```

Shot types: `orbit`, `establishing`, `crane`, `dolly`, `push_in`, `pull_out`, `track`, `pan`, `tilt`, `spline`,
`pov`, `over_shoulder`, `low_angle`, `high_angle`, `wide`, `close_up`, `extreme_close_up`, `reveal`. Shots run
back to back unless one sets `at`. `target` frames another entity, and `ease` shapes the move.

Events: `fade` (`from`, `to`, `duration`, `color`), `title` and `dialogue` (translation keys: `title`,
`subtitle`, `speaker`, `text`), `sound`, `animate` (`actor`, `clip` or `event`), `particles`, `flash`,
`time_scale` (`value`, `duration`), `shake` (`amount`) and `letterbox` (`on`).

Actor selectors: `@self` (the player watching), `@anchor`, `@target`, `@nearest:<entity type>`.

## The authoring toolkit

The shipped library is written in Python (`tools/animgen/`). It's easier to review than raw JSON, and the
toolkit refuses to export anything invalid.

```
python3 tools/animgen/build.py --check   # validate only
python3 tools/animgen/build.py           # validate, then export JSON, the registry CSV and the inventory
python3 tools/animgen/test_toolkit.py    # toolkit tests
```

`core.py` has the `Clip` builder and gait generators (`quad_gait` with stride, bob, snap, splay and yaw
character controls). `mobkit.py` has helpers for state loops and event beats, and each category lives in its
own module. The validator rejects:

- unknown bones
- unknown `q.*` variables
- events the Java side never fires
- cinematic clips that no sequence performs
- unregistered sounds and particles
- category counts below their minimums
- any pair of clips that are the same motion after normalising speed and amplitude, phase-shifting or
  mirroring

Before validating, `snaps.py` eases any keyed segment that would move a limb further in one 60 fps frame than
reads as motion (90 degrees, 45 for the first-person camera, 6 px or 0.35 scale). It steps the segment's
easing down its family (`out_expo` to `out_quint` and so on), sampling curves exactly as the runtime does, so
a snap keeps its character but spans two or three frames.

`tools/assetgen/` generates the particle textures, the sound effects (synthesised with numpy, encoded to OGG),
`sounds.json`, the English translations and the GameTest structure.

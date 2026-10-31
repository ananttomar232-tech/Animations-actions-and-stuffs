# Testing

MotionWorks is tested in five layers, from pure data checks to the real client. Each runs offline once the
Gradle caches exist (one online `./gradlew build` first).

| Layer | Command | Runs in |
|---|---|---|
| Authoring validator | `python3 tools/animgen/build.py --check` | seconds |
| Toolkit tests (20) | `python3 tools/animgen/test_toolkit.py` | ~25 s |
| Java unit tests (40) | `./gradlew test` | ~1 min |
| In-game GameTests (6) | `./gradlew runGameTestServer` | ~1 min |
| Headless client smoke test | `tools/clienttest/run_client_smoke.sh` | ~4 min |

## Authoring validator

Run before exporting the library. It fails on unknown bones or `q.*` variables, events the Java code never
fires, missing sounds or particles, cinematic sequences that reference missing clips, cinematic clips no
sequence performs, categories below their minimums, and near-duplicate clips (speed, amplitude, mirror and
phase variants).

## Toolkit tests (`tools/animgen/test_toolkit.py`)

- **Gaits:** default controls reproduce the plain gait; character controls change the shape, not just the
  size; full-turn loops keep rotating forward.
- **Validators:** each one catches what it should (unknown bone, unknown variable, unfired event, scaled copy,
  mirrored copy) and accepts argument forms of real events.
- **Library:** every category meets its minimum, every clip passes every validator and has registry metadata,
  and emotes are tagged for the wheel.
- **Assets:**
  - every registered sound has an OGG file; every particle has a definition and textures
  - every translation key used by the code or the sequences exists
  - every entity family's rig exists, and rig profile expressions use only known variables
  - every mixin class exists, and `docs/CONTEXT_VARIABLES.md` matches the sources

## Java unit tests (`src/test`)

| Test | Covers |
|---|---|
| `ExprParserTest` | Precedence, constant folding, variables and aliases, string comparison, deterministic random, helpers, error reporting |
| `ChannelTest`, `InterpolationTest` | Keyframes, easing, jumps, expression channels; smooth interpolation: holds and peaks are never overshot, segments stay monotone, velocity is continuous through uneven keys, loops wrap seamlessly |
| `ControllerTest` | Deterministic idle pools, priority takeover with crossfade, state hysteresis, event selection and interruption, death pre-empting actions, additive stacking, loop events once per cycle, `stop_when`, time scale |
| `LoaderAndSignatureTest` | Bedrock import (axis flip, events) and duplicate detection |
| `ShippedLibraryTest` | Every shipped file loads with the runtime parser; no two shipped clips share a motion signature, expressions included |
| `PlayerRigPoseTest` | Bakes the real vanilla `PlayerModel` and plays all 1,119 player clips through the rig, reproducing exactly the fields vanilla's `setupAnim` rewrites each frame (taken from its bytecode). Shoulders, neck and hips must stay attached, and an ended clip must leave the vanilla pose untouched |
| `WorldEventArgsTest` | Positional world-event encoding, including under a decimal-comma locale |
| `SourceConventionsTest` | Singletons are the last static field (static initialisation order); every declared context variable is actually written |

## GameTests (`MotionWorksGameTests`)

`./gradlew runGameTestServer` starts a dedicated server with the mod and runs the tests in the game, then
exits non-zero if any fail. Each drives a real vanilla code path and checks, through `TriggerTrace`, that the
matching animation trigger was sent:

- the `Explosion` accessor mixin reads the blast radius
- `Mob.playAmbientSound` sends `vocalize` (the `MobMixin` hook)
- a launched arrow sends `shoot:arrow` for its skeleton
- lightning sends a positional `thunderclap` at the strike
- an explosion sends the `explosion` world event with its power, and `explosion_flinch` to mobs in range
- the `/motionworks` command tree is registered

Running them also proves the common mixins apply and that the server side loads without client classes.

## Headless client smoke test (`tools/clienttest/`)

Boots the real client under Xvfb with Mesa's software renderer and joins a copy of the GameTest world (created
by `runGameTestServer` if missing). A datapack then plays a scene:

- mobs, a villager and a golem; a half-block ramp with a cow and a horse straddling a step
- a distant TNT blast and a lightning strike
- a turntable cinematic (`turntable.json`) that frames the animals from the side and orbits the player, who
  bows partway through

The script saves screenshots and a contact sheet to `build/clienttest/`. It fails if the log lacks the
library and world-join markers, or contains a crash report, a mixin failure, an animation error, an event-bus
exception or a bad cinematic.

Needs `Xvfb`, Mesa (llvmpipe) and, for screenshots, ImageMagick. Tunables: `SHOTS`, `INTERVAL`, `WARMUP`,
`DISPLAY_NUM`. `./gradlew runClient -PquickPlay=<world>` joins a world directly for manual testing.

The first client runs found two bugs that every other layer missed, both now fixed and covered by tests:

- **A static initialisation-order crash on world join.** `FirstPersonAnimator` built its rig before `BONES`
  was set. `SourceConventionsTest` now guards this.
- **Players' torsos drifting away from their legs.** `PoseApplier` read last frame's output back as vanilla
  for fields vanilla never rewrites, and the hip coupling compounded every frame. `PlayerRigPoseTest`
  reproduces vanilla's per-frame writes to guard this.

## Not covered automatically

- Real GPUs and drivers. The smoke test uses software OpenGL at a few frames per second, so timing-sensitive
  visuals (trails, particles) are checked for errors, not for looks.
- Other mods, including shader packs, Oculus and Embeddium (the foliage shaders switch off for those).
- Two real clients on one server. Relayed triggers are covered on the server side by the GameTests.
- Performance with large mob counts.

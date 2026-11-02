# Testing

MotionWorks is tested in six layers, from pure data checks to a real Forge install. Each runs offline once the
Gradle caches exist (one online `./gradlew build` first).

| Layer | Command | Runs in |
|---|---|---|
| Authoring validator | `python3 tools/animgen/build.py --check` | seconds |
| Toolkit tests (27) | `python3 tools/animgen/test_toolkit.py` | ~25 s |
| Java unit tests (57) | `./gradlew test` | ~1 min |
| In-game GameTests (6) | `./gradlew runGameTestServer` | ~1 min |
| Headless client smoke test | `tools/clienttest/run_client_smoke.sh` | ~4 min |
| Production client test | `./gradlew build && tools/clienttest/run_production_client.sh` | ~3 min (plus a one-time Forge install) |

## Authoring validator

Run before exporting the library. It fails on unknown bones or `q.*` variables, events the Java code never
fires, missing sounds or particles, cinematic sequences that reference missing clips, cinematic clips no
sequence performs, categories below their minimums, and near-duplicate clips (speed, amplitude, mirror and
phase variants).

## Toolkit tests (`tools/animgen/test_toolkit.py`)

- **Gaits:** default controls reproduce the plain gait; character controls change the shape, not just the
  size; full-turn loops keep rotating forward.
- **Limb rotations:** `core.limb` (behind `arm` and `leg`) composes intuitive angles (swing forward, swing out
  from the midline, twist about the limb) into ModelPart's angles exactly: 2,000 random poses round-trip,
  hanging and purely forward limbs are unchanged, a raised hand with a negative `out` moves toward the midline on
  either side, and keys stay continuous (no Euler flips) through a pose passing overhead.
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
| `PlayerRigPoseTest` | Bakes the real vanilla `PlayerModel` and plays all 1,119 player clips through the rig, reproducing exactly the fields vanilla's `setupAnim` rewrites each frame (taken from its bytecode). Shoulders, neck and hips must stay attached, and an ended clip must leave the vanilla pose untouched. The Euler extraction must invert ModelPart's rotation order over 200,000 rotations, a head must turn with the torso without rolling over, and ground contact must lift a flipped body but not a kneel |
| `MotionQualityTest` | Every shipped clip sampled at 240 Hz under zero, realistic and random context values: no non-finite output, no jump at a loop seam, no limb moving more than one 60 fps frame can show (90 degrees, 45 for the first-person camera, 6 px, 0.35 scale), no one-shot ending where its blend-out cannot hide it |
| `RotationBlendTest` | Spins blend the short way round: against vanilla, between crossfading clips, and when an additive spin fades |
| `CombatStateTest` | Dodge, parry and counter windows from another world's game time are dropped, not honoured |
| `WorldEventArgsTest` | Positional world-event encoding, including under a decimal-comma locale |
| `BodyPlanTableTest` | The body-plan rules for mobs from other mods: every plan borrows a family and rig that exist, the first matching plan wins and needs all its traits, shapes come out right from vanilla part names (a horse's baby legs are not more legs, illagers carry both folded and separate arms), packs cannot name unknown shapes or traits |
| `AdaptiveRigTest` | A short-legged humanoid "from another mod" is classified as humanoid and its hips found; the fitted player rig turns its torso rigidly about those hips, not vanilla's, without changing the shared profile; `RenderHealth` notices another mod putting back an arm MotionWorks raised, but not a channel MotionWorks left alone |
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

The client also runs the **library audit** (`LibraryAudit`, the same check as `/mw audit`): for every entity
family it takes the model from the entity's real renderer and reports:

- clips that move nothing on it
- species clips naming bones it lacks
- scale tracks that slide a part's box off its pivot

It also lists bodies that dip below the feet (corrected at runtime by ground contact) and lifts off the
ground, for review. It checks the body-plan classifier on 13 vanilla models whose answer is known (a zombie must
come out humanoid and animated like a zombie, a vindicator illager, a horse equine, a spider an arthropod ...),
and lists every entity type without a family with its plan and how many borrowed bone tracks find a part.

A test resource pack removes the families of the pig, the husk and the wandering trader, so the scene also has
three mobs animated by body plan, as another mod's mobs would be. The log must show each one posed, like a cow, a
zombie and a villager. The render check (`RenderHealth`, the same data as `/mw doctor`) must report the
third-person hook healthy: nothing cancelled, every drawn entity type hooked.

The script saves screenshots and a contact sheet to `build/clienttest/`. It fails if the log lacks the
library, world-join and audit markers, or contains a crash report, a mixin failure, an animation error, an
event-bus exception, a bad cinematic or any audit issue.

`GALLERY=1` also renders every clip on its owner's real model at three moments into numbered contact sheets
(`build/clienttest/gallery/sheet_*.png` with `index.tsv`), about 2,270 clips in under a minute, for looking at
the whole library.

Needs `Xvfb`, Mesa (llvmpipe) and, for screenshots, ImageMagick. Tunables: `SHOTS`, `INTERVAL`, `WARMUP`,
`DISPLAY_NUM`. `./gradlew runClient -PquickPlay=<world>` joins a world directly for manual testing.

The client runs, the audit and the gallery found these bugs, which every other layer missed. All are now fixed
and covered by tests or the audit:

- **A static initialisation-order crash on world join.** `FirstPersonAnimator` built its rig before `BONES`
  was set. `SourceConventionsTest` now guards this.
- **Players' torsos drifting away from their legs.** `PoseApplier` read last frame's output back as vanilla
  for fields vanilla never rewrites, and the hip coupling compounded every frame. `PlayerRigPoseTest`
  reproduces vanilla's per-frame writes to guard this.
- **Heads twisting upside down when the torso turned.** JOML 1.10.5's `getEulerAnglesZYX` does not invert
  `rotationZYX`, ModelPart's rotation order, so the extraction is now done from the rotation matrix.
- **Rolls, flips and lying poses sinking into the floor** by up to two blocks: fixed by ground contact.
- **Small creatures pivoting around a point above them** (an axolotl playing dead floated a block up): fixed by
  measured pivots.
- **A slime's eyes floating off its squashing body, and the elder guardian's eye sliding off its face.**
  Fixed by scaling from the model root and holding the eye in place.
- **Two zombie villager clips animating a nose the model does not have.**
- **Arms going the wrong way on 27% of clips.** The authoring helper wrote "swing out" and "twist" straight into
  ModelPart's angles, which is only right for a hanging limb: on an arm raised forward "out" did nothing, and
  overhead it was reversed. Blowing into your hands held both arms straight out to the sides (the T-pose seen in
  a snowy world), shading your eyes pointed the hand away, a flex left the arm hanging. Found by filming normal
  third-person play in the production client with the debug overlay on; fixed in `core.limb`, which changed the
  limb direction of 671 clips by 15 degrees or more. Before/after renders of the most-changed clips confirm the
  new poses match their names.
- From the motion review:
  - spins whipping backwards during their blend-out
  - seven loops snapping back at their seam
  - 95 keyed segments moving a limb up to 160 degrees in one frame
  - 801 clips overshooting their authored poses (smooth interpolation)
- From code review:
  - combat windows leaking between singleplayer worlds (long invulnerability, free parries)
  - animators of killed mobs never released
  - remote players' stowed weapons outliving their entity ids

## Production client test (`tools/clienttest/run_production_client.sh`)

The development client remaps the mod while it loads. Players run the reobfuscated jar from `build/libs` in an
ordinary Forge install, where obfuscated names, the mixin refmap and the jar's manifest all matter. This test
installs that Forge version with its official installer (once, under `build/prodclient/mc`), builds the launch
command the vanilla launcher would use (`forge_launch.py`), and runs the shipped jar under Xvfb in the same scene,
with the same log checks (`checks.sh`) as the smoke test. It needs network access the first time.

Run against the jar that was published before this test existed, it showed third-person animation working in a
real install (the audit, the render check and screenshots of posed players and mobs). That ruled out a problem
in the jar itself and pointed at other mods, hence `/mw doctor`.

## Not covered automatically

- Real GPUs and drivers. The smoke test uses software OpenGL at a few frames per second, so timing-sensitive
  visuals (trails, particles) are checked for errors, not for looks.
- Other mods, including shader packs, Oculus and Embeddium (the foliage shaders switch off for those). The
  compatibility notes in the README come from reading other mods' rendering hooks and from `RenderHealth`, which
  watches for them at runtime. No third-party mod is run in these tests.
- Two real clients on one server. Relayed triggers are covered on the server side by the GameTests.
- Performance with large mob counts.

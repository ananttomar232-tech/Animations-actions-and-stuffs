#!/bin/bash
# Headless client smoke test: boots the real client under Xvfb (software OpenGL), joins a test world,
# plays a scripted scene (mobs, a distant explosion, lightning, a turntable cinematic around the player),
# captures screenshots and fails if the log shows a crash, a mixin failure or an animation error.
#
#   tools/clienttest/run_client_smoke.sh            # screenshots and contact sheet in build/clienttest/
#   SHOTS=30 INTERVAL=1 tools/clienttest/run_client_smoke.sh
#
# Needs Xvfb, Mesa (llvmpipe) and the Gradle caches of a previous online build; ImageMagick is optional
# (screenshots). The test world is copied from run/world, which ./gradlew runGameTestServer creates.
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
HERE="$ROOT/tools/clienttest"
OUT="$ROOT/build/clienttest"
SHOTS=${SHOTS:-24}
INTERVAL=${INTERVAL:-1}
WARMUP=${WARMUP:-6}
DISPLAY_NUM=${DISPLAY_NUM:-99}
cd "$ROOT"

if [ ! -f run/world/level.dat ]; then
    echo "No run/world yet: running the GameTest server once to create it"
    ./gradlew runGameTestServer --offline -q || { echo "FAIL: GameTest server run failed"; exit 1; }
fi

rm -rf run/saves/mwtest "$OUT" && mkdir -p run/saves "$OUT/shots" run/config/motionworks/cinematics
cp -r run/world run/saves/mwtest
rm -rf run/saves/mwtest/session.lock run/saves/mwtest/playerdata run/saves/mwtest/entities
mkdir -p run/saves/mwtest/datapacks && cp -r "$HERE/datapack" run/saves/mwtest/datapacks/mwtest
cp "$HERE/turntable.json" run/config/motionworks/cinematics/turntable.json
cp "$HERE/options.txt" run/options.txt

export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=":$DISPLAY_NUM"
Xvfb ":$DISPLAY_NUM" -screen 0 1280x720x24 -nolisten tcp >/dev/null 2>&1 &
XVFB=$!
trap 'kill $XVFB 2>/dev/null' EXIT
# GALLERY=1 also renders every clip into contact sheets under build/clienttest/gallery (takes a few minutes)
EXTRA=""
[ -n "${GALLERY:-}" ] && EXTRA="-PmwGallery=$OUT/gallery"
./gradlew runClient --offline -PquickPlay=mwtest -PmwAudit="$OUT/audit.txt" $EXTRA > "$OUT/client.log" 2>&1 &
GRADLE=$!

for _ in $(seq 1 300); do
    grep -q "joined the game" "$OUT/client.log" && break
    grep -q -e "---- Minecraft Crash Report ----" -e "BUILD FAILED" "$OUT/client.log" < /dev/null && break
    kill -0 $GRADLE 2>/dev/null || break
    sleep 2
done
if grep -q "joined the game" "$OUT/client.log"; then
    sleep "$WARMUP"
    for n in $(seq -w 1 "$SHOTS"); do
        sleep "$INTERVAL"
        command -v import >/dev/null && import -display ":$DISPLAY_NUM" -window root "$OUT/shots/shot_$n.png" 2>/dev/null
    done
fi
if [ -n "${GALLERY:-}" ]; then
    for _ in $(seq 1 450); do grep -q "MotionWorks gallery" "$OUT/client.log" && break; sleep 2; done
fi
pkill -f -- "--launchTarget, forgeclientuserdev|--launchTarget forgeclientuserdev" 2>/dev/null
pkill -f "cpw.mods.bootstraplauncher.BootstrapLauncher" 2>/dev/null
sleep 5
kill $GRADLE 2>/dev/null

if command -v montage >/dev/null && ls "$OUT"/shots/*.png >/dev/null 2>&1; then
    # The 854x480 game window sits centred on the 1280x720 virtual screen.
    for f in "$OUT"/shots/shot_*.png; do convert "$f" -crop 854x480+213+120 +repage "$f"; done
    montage "$OUT"/shots/shot_*.png -resize 50% -tile 6x -geometry +2+2 "$OUT/contact_sheet.png"
fi

fail=0
expect() { grep -q -e "$1" "$OUT/client.log" < /dev/null || { echo "FAIL: missing \"$1\""; fail=1; }; }
reject() { grep -q -e "$1" "$OUT/client.log" < /dev/null && { echo "FAIL: found \"$1\""; grep -m3 -e "$1" "$OUT/client.log"; fail=1; }; }
expect "MotionWorks loaded [0-9]* animation clips"
expect "MotionWorks loaded [0-9]* cinematic sequences"
expect "joined the game"
expect "mwtest scene ready"
expect "MotionWorks audit: [0-9]* clip bindings"
reject "---- Minecraft Crash Report ----"
reject "MotionWorks failed to animate"
reject "Mixin apply failed\|InvalidInjectionException\|InvalidMixinException"
reject "Exception caught during firing event"
reject "Bad cinematic\|Bad user cinematic\|failed to load"
reject "MotionWorks audit: [0-9]* clip bindings on [0-9]* models, [1-9][0-9]* issues"
grep -o "MotionWorks loaded [0-9]* animation clips.*" "$OUT/client.log" | head -1
[ $fail -eq 0 ] && echo "PASS: client smoke test (screenshots in build/clienttest/)" || echo "client log: $OUT/client.log"
exit $fail

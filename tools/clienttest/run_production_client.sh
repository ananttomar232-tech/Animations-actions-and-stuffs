#!/bin/bash
# Production client test: installs real Forge with its official installer (once, under build/prodclient/mc) and runs
# the shipped, reobfuscated jar from build/libs in an ordinary (non-development) client under Xvfb. It plays the same
# scene and runs the same log checks as run_client_smoke.sh. The development client remaps the mod at load time;
# this one runs it as players do, so it catches problems that only appear in a real install (obfuscated names,
# refmaps, mixin configuration, the jar's manifest).
#
#   ./gradlew build && tools/clienttest/run_production_client.sh
#
# Needs network access the first time (Forge installer, Minecraft libraries), Xvfb, Mesa, ImageMagick (optional),
# and the asset cache of a previous ./gradlew build (or ASSETS=<dir>).
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
HERE="$ROOT/tools/clienttest"
OUT="$ROOT/build/prodclient/out"
MC="$ROOT/build/prodclient/mc"
GAME="$ROOT/build/prodclient/game"
SHOTS=${SHOTS:-24}
DISPLAY_NUM=${DISPLAY_NUM:-98}
ASSETS=${ASSETS:-$HOME/.gradle/caches/forge_gradle/assets}
JAVA=${JAVA_HOME:-/usr/lib/jvm/java-17-openjdk-amd64}/bin/java
MCV=$(sed -n 's/^minecraft_version=//p' "$ROOT/gradle.properties")
FORGE=$(sed -n 's/^forge_version=//p' "$ROOT/gradle.properties")
PROFILE="$MCV-forge-$FORGE"
JAR=$(ls "$ROOT"/build/libs/motionworks-*.jar 2>/dev/null | grep -v sources | head -1)
[ -n "$JAR" ] || { echo "FAIL: no mod jar in build/libs (run ./gradlew build)"; exit 1; }
[ -f "$ROOT/run/world/level.dat" ] || { echo "FAIL: no run/world (run ./gradlew runGameTestServer once)"; exit 1; }

if [ ! -f "$MC/versions/$PROFILE/$PROFILE.json" ]; then
    mkdir -p "$MC" "$ROOT/build/prodclient/dl"
    INSTALLER="$ROOT/build/prodclient/dl/forge-$MCV-$FORGE-installer.jar"
    curl -sSfL -o "$INSTALLER" "https://maven.minecraftforge.net/net/minecraftforge/forge/$MCV-$FORGE/forge-$MCV-$FORGE-installer.jar" \
        || { echo "FAIL: could not download the Forge installer"; exit 1; }
    echo '{"profiles":{}}' > "$MC/launcher_profiles.json"
    # The installer writes its own log next to where it runs, so run it inside build/.
    (cd "$ROOT/build/prodclient" && "$JAVA" -jar "$INSTALLER" --installClient "$MC") > "$ROOT/build/prodclient/install.log" 2>&1 \
        || { echo "FAIL: Forge installer failed (build/prodclient/install.log)"; exit 1; }
fi

rm -rf "$OUT" "$GAME/mods" "$GAME/saves" "$GAME/config" "$GAME/logs" "$GAME/resourcepacks"
mkdir -p "$OUT/shots" "$GAME/mods" "$GAME/saves" "$GAME/config/motionworks/cinematics" "$GAME/resourcepacks"
cp "$JAR" "$GAME/mods/"
cp -r "$ROOT/run/world" "$GAME/saves/mwtest"
rm -rf "$GAME/saves/mwtest/session.lock" "$GAME/saves/mwtest/playerdata" "$GAME/saves/mwtest/entities"
mkdir -p "$GAME/saves/mwtest/datapacks" && cp -r "$HERE/datapack" "$GAME/saves/mwtest/datapacks/mwtest"
cp -r "$HERE/resourcepack" "$GAME/resourcepacks/mwtest"
cp "$HERE/turntable.json" "$GAME/config/motionworks/cinematics/turntable.json"
cp "$HERE/options.txt" "$GAME/options.txt"

python3 "$HERE/forge_launch.py" "$MC" "$PROFILE" "$GAME" "$ASSETS" "-Dmotionworks.audit=$OUT/audit.txt" > "$OUT/args.txt" \
    || { echo "FAIL: could not build the launch command"; exit 1; }
mapfile -t ARGS < "$OUT/args.txt"

export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=":$DISPLAY_NUM"
Xvfb ":$DISPLAY_NUM" -screen 0 1280x720x24 -nolisten tcp >/dev/null 2>&1 &
XVFB=$!
(cd "$GAME" && exec "$JAVA" "${ARGS[@]}" --quickPlaySingleplayer mwtest) > "$OUT/client.log" 2>&1 &
CLIENT=$!
trap 'kill $CLIENT $XVFB 2>/dev/null' EXIT

for _ in $(seq 1 300); do
    grep -q "joined the game" "$OUT/client.log" && break
    grep -q -e "---- Minecraft Crash Report ----" "$OUT/client.log" < /dev/null && break
    kill -0 $CLIENT 2>/dev/null || break
    sleep 2
done
if grep -q "joined the game" "$OUT/client.log"; then
    sleep 6
    for n in $(seq -w 1 "$SHOTS"); do
        sleep 1
        command -v import >/dev/null && import -display ":$DISPLAY_NUM" -window root -crop 854x480+213+120 +repage "$OUT/shots/shot_$n.png" 2>/dev/null
    done
fi
kill $CLIENT 2>/dev/null
sleep 4
kill -9 $CLIENT 2>/dev/null
command -v montage >/dev/null && ls "$OUT"/shots/*.png >/dev/null 2>&1 \
    && montage "$OUT"/shots/shot_*.png -resize 50% -tile 6x -geometry +2+2 "$OUT/contact_sheet.png"

source "$HERE/checks.sh"
check_log "$OUT/client.log"
grep -o "MotionWorks loaded [0-9]* animation clips.*" "$OUT/client.log" | head -1
[ $fail -eq 0 ] && echo "PASS: production client test with $(basename "$JAR") on Forge $FORGE (build/prodclient/out/)" \
    || echo "client log: $OUT/client.log"
exit $fail

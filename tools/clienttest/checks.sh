# Log checks shared by the client smoke tests (development and production clients).
# Usage: source checks.sh; check_log <client log>; then $fail is 0 when every check passed.
check_log() {
    local LOG="$1"
    fail=0
    expect() { grep -q -e "$1" "$LOG" < /dev/null || { echo "FAIL: missing \"$1\""; fail=1; }; }
    reject() { grep -q -e "$1" "$LOG" < /dev/null && { echo "FAIL: found \"$1\""; grep -m3 -e "$1" "$LOG"; fail=1; }; }
    expect "MotionWorks loaded [0-9]* animation clips"
    expect "MotionWorks loaded [0-9]* cinematic sequences"
    expect "joined the game"
    expect "mwtest scene ready"
    expect "MotionWorks audit: [0-9]* clip bindings"
    expect "MotionWorks render check: third-person hook healthy"
    # Mobs without a family (the resource pack removes these three) are animated by body plan, fitted to their model
    expect "MotionWorks body plan: minecraft:pig: body plan quadruped .*animated like minecraft:cow, posed [1-9]"
    expect "MotionWorks body plan: minecraft:husk: body plan humanoid .*animated like minecraft:zombie, posed [1-9]"
    expect "MotionWorks body plan: minecraft:wandering_trader: body plan villager .*animated like minecraft:villager, posed [1-9]"
    reject "---- Minecraft Crash Report ----"
    reject "MotionWorks failed to animate"
    reject "WARN.*MotionWorks render check"
    reject "Mixin apply failed\|InvalidInjectionException\|InvalidMixinException"
    reject "Exception caught during firing event"
    reject "Bad cinematic\|Bad user cinematic\|failed to load"
    reject "MotionWorks audit: [0-9]* clip bindings on [0-9]* models, [1-9][0-9]* issues"
}

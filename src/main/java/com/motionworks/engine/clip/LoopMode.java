package com.motionworks.engine.clip;

public enum LoopMode {
    /** Play once, fade out at the end, then the instance is released. */
    ONCE,
    /** Play once and hold the final pose until replaced. */
    HOLD,
    /** Wrap around forever. */
    LOOP,
    /** Play forward then backward forever. */
    PING_PONG;

    public static LoopMode parse(Object o) {
        if (o instanceof Boolean b) return b ? LOOP : ONCE;
        if (o == null) return ONCE;
        return switch (o.toString().toLowerCase(java.util.Locale.ROOT)) {
            case "true", "loop" -> LOOP;
            case "hold", "hold_on_last_frame" -> HOLD;
            case "ping_pong", "pingpong" -> PING_PONG;
            default -> ONCE;
        };
    }
}

package com.motionworks.engine.clip;

/** How a channel interpolates into a keyframe from the previous one. */
public enum Interp {
    LINEAR,
    /** Catmull-Rom spline through neighbouring keys (Bedrock "catmullrom"). */
    SMOOTH,
    /** Hold the previous value until this key is reached. */
    STEP;

    public static Interp parse(String s) {
        if (s == null) return LINEAR;
        return switch (s.toLowerCase(java.util.Locale.ROOT)) {
            case "smooth", "catmullrom", "catmull_rom", "spline" -> SMOOTH;
            case "step", "hold", "constant" -> STEP;
            default -> LINEAR;
        };
    }
}

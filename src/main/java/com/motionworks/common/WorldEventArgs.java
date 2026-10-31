package com.motionworks.common;

import java.util.Locale;

/**
 * Wire format of positional world events (AnimationEventPacket with entity id -1): "x,y,z" or
 * "x,y,z,magnitude". Always written with Locale.ROOT; a locale with a decimal comma would split
 * each coordinate in two.
 */
public final class WorldEventArgs {
    private WorldEventArgs() {}

    public static String encode(double x, double y, double z) {
        return String.format(Locale.ROOT, "%.1f,%.1f,%.1f", x, y, z);
    }

    public static String encode(double x, double y, double z, float magnitude) {
        return String.format(Locale.ROOT, "%.1f,%.1f,%.1f,%.1f", x, y, z, magnitude);
    }

    /** {x, y, z, magnitude} with magnitude 1 when absent, or null when the argument is malformed or not finite. */
    public static double[] decode(String arg) {
        String[] parts = arg.split(",");
        if (parts.length != 3 && parts.length != 4) return null;
        double[] out = {0, 0, 0, 1};
        try {
            for (int i = 0; i < parts.length; i++) {
                out[i] = Double.parseDouble(parts[i]);
                if (!Double.isFinite(out[i])) return null;
            }
        } catch (NumberFormatException e) {
            return null;
        }
        return out;
    }
}

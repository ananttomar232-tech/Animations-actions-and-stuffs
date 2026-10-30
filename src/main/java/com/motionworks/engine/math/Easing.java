package com.motionworks.engine.math;

import java.util.Locale;

/**
 * Easing curves applied to the normalised time of a keyframe segment. Names follow the common
 * easings.net vocabulary so curves authored in Blockbench/GeckoLib map one to one.
 */
public enum Easing {
    LINEAR {
        @Override public float apply(float t) { return t; }
    },
    STEP {
        @Override public float apply(float t) { return t < 1f ? 0f : 1f; }
    },
    IN_SINE {
        @Override public float apply(float t) { return 1f - (float) Math.cos(t * Math.PI / 2); }
    },
    OUT_SINE {
        @Override public float apply(float t) { return (float) Math.sin(t * Math.PI / 2); }
    },
    IN_OUT_SINE {
        @Override public float apply(float t) { return -((float) Math.cos(Math.PI * t) - 1f) / 2f; }
    },
    IN_QUAD {
        @Override public float apply(float t) { return t * t; }
    },
    OUT_QUAD {
        @Override public float apply(float t) { return 1f - (1f - t) * (1f - t); }
    },
    IN_OUT_QUAD {
        @Override public float apply(float t) { return t < 0.5f ? 2f * t * t : 1f - (float) Math.pow(-2f * t + 2f, 2) / 2f; }
    },
    IN_CUBIC {
        @Override public float apply(float t) { return t * t * t; }
    },
    OUT_CUBIC {
        @Override public float apply(float t) { return 1f - (float) Math.pow(1f - t, 3); }
    },
    IN_OUT_CUBIC {
        @Override public float apply(float t) { return t < 0.5f ? 4f * t * t * t : 1f - (float) Math.pow(-2f * t + 2f, 3) / 2f; }
    },
    IN_QUART {
        @Override public float apply(float t) { return t * t * t * t; }
    },
    OUT_QUART {
        @Override public float apply(float t) { return 1f - (float) Math.pow(1f - t, 4); }
    },
    IN_OUT_QUART {
        @Override public float apply(float t) { return t < 0.5f ? 8f * t * t * t * t : 1f - (float) Math.pow(-2f * t + 2f, 4) / 2f; }
    },
    IN_QUINT {
        @Override public float apply(float t) { return t * t * t * t * t; }
    },
    OUT_QUINT {
        @Override public float apply(float t) { return 1f - (float) Math.pow(1f - t, 5); }
    },
    IN_OUT_QUINT {
        @Override public float apply(float t) { return t < 0.5f ? 16f * t * t * t * t * t : 1f - (float) Math.pow(-2f * t + 2f, 5) / 2f; }
    },
    IN_EXPO {
        @Override public float apply(float t) { return t == 0f ? 0f : (float) Math.pow(2, 10 * t - 10); }
    },
    OUT_EXPO {
        @Override public float apply(float t) { return t == 1f ? 1f : 1f - (float) Math.pow(2, -10 * t); }
    },
    IN_OUT_EXPO {
        @Override public float apply(float t) {
            if (t == 0f || t == 1f) return t;
            return t < 0.5f ? (float) Math.pow(2, 20 * t - 10) / 2f : (2f - (float) Math.pow(2, -20 * t + 10)) / 2f;
        }
    },
    IN_CIRC {
        @Override public float apply(float t) { return 1f - (float) Math.sqrt(1f - t * t); }
    },
    OUT_CIRC {
        @Override public float apply(float t) { return (float) Math.sqrt(1f - (t - 1f) * (t - 1f)); }
    },
    IN_OUT_CIRC {
        @Override public float apply(float t) {
            return t < 0.5f ? (1f - (float) Math.sqrt(1f - 4f * t * t)) / 2f
                    : ((float) Math.sqrt(1f - (float) Math.pow(-2f * t + 2f, 2)) + 1f) / 2f;
        }
    },
    IN_BACK {
        @Override public float apply(float t) { return C3 * t * t * t - C1 * t * t; }
    },
    OUT_BACK {
        @Override public float apply(float t) { float u = t - 1f; return 1f + C3 * u * u * u + C1 * u * u; }
    },
    IN_OUT_BACK {
        @Override public float apply(float t) {
            return t < 0.5f ? ((float) Math.pow(2f * t, 2) * ((C2 + 1f) * 2f * t - C2)) / 2f
                    : ((float) Math.pow(2f * t - 2f, 2) * ((C2 + 1f) * (t * 2f - 2f) + C2) + 2f) / 2f;
        }
    },
    IN_ELASTIC {
        @Override public float apply(float t) {
            if (t == 0f || t == 1f) return t;
            return -(float) Math.pow(2, 10 * t - 10) * (float) Math.sin((t * 10 - 10.75) * C4);
        }
    },
    OUT_ELASTIC {
        @Override public float apply(float t) {
            if (t == 0f || t == 1f) return t;
            return (float) Math.pow(2, -10 * t) * (float) Math.sin((t * 10 - 0.75) * C4) + 1f;
        }
    },
    IN_OUT_ELASTIC {
        @Override public float apply(float t) {
            if (t == 0f || t == 1f) return t;
            return t < 0.5f ? -((float) Math.pow(2, 20 * t - 10) * (float) Math.sin((20 * t - 11.125) * C5)) / 2f
                    : ((float) Math.pow(2, -20 * t + 10) * (float) Math.sin((20 * t - 11.125) * C5)) / 2f + 1f;
        }
    },
    IN_BOUNCE {
        @Override public float apply(float t) { return 1f - bounceOut(1f - t); }
    },
    OUT_BOUNCE {
        @Override public float apply(float t) { return bounceOut(t); }
    },
    IN_OUT_BOUNCE {
        @Override public float apply(float t) {
            return t < 0.5f ? (1f - bounceOut(1f - 2f * t)) / 2f : (1f + bounceOut(2f * t - 1f)) / 2f;
        }
    },
    /** Snappy anticipation-friendly curve: slow start, very fast middle, soft landing. */
    SNAP {
        @Override public float apply(float t) { return IN_OUT_EXPO.apply(t) * 0.7f + IN_OUT_CUBIC.apply(t) * 0.3f; }
    };

    private static final float C1 = 1.70158f;
    private static final float C2 = C1 * 1.525f;
    private static final float C3 = C1 + 1f;
    private static final double C4 = (2 * Math.PI) / 3;
    private static final double C5 = (2 * Math.PI) / 4.5;

    public abstract float apply(float t);

    private static float bounceOut(float t) {
        final float n1 = 7.5625f;
        final float d1 = 2.75f;
        if (t < 1f / d1) return n1 * t * t;
        if (t < 2f / d1) { t -= 1.5f / d1; return n1 * t * t + 0.75f; }
        if (t < 2.5f / d1) { t -= 2.25f / d1; return n1 * t * t + 0.9375f; }
        t -= 2.625f / d1;
        return n1 * t * t + 0.984375f;
    }

    /** Parses names such as {@code "easeInOutSine"}, {@code "in_out_sine"} or {@code "linear"}. */
    public static Easing parse(String name) {
        if (name == null || name.isEmpty()) return LINEAR;
        String n = name.trim();
        if (n.startsWith("ease")) n = n.substring(4);
        n = n.replaceAll("([a-z])([A-Z])", "$1_$2").replace('-', '_').toUpperCase(Locale.ROOT);
        if (n.startsWith("_")) n = n.substring(1);
        try {
            return valueOf(n);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Unknown easing '" + name + "'");
        }
    }
}

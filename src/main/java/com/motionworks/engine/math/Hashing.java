package com.motionworks.engine.math;

/**
 * Deterministic hashing used for every "random" animation decision. Because all inputs (entity
 * UUID, synced game time, event counters) are identical on every client, every client makes the
 * same choice without any network traffic.
 */
public final class Hashing {
    private Hashing() {}

    public static long mix(long z) {
        z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
        z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
        return z ^ (z >>> 31);
    }

    public static long combine(long a, long b) {
        return mix(a * 0x9E3779B97F4A7C15L + b);
    }

    public static long combine(long a, long b, long c) {
        return combine(combine(a, b), c);
    }

    /** Uniform float in [0, 1). */
    public static float unit(long h) {
        return (mix(h) >>> 40) / (float) (1L << 24);
    }

    public static long ofString(String s) {
        long h = 1125899906842597L;
        for (int i = 0; i < s.length(); i++) h = 31 * h + s.charAt(i);
        return mix(h);
    }

    /** Smooth 1-D value noise in [-1, 1], continuous in {@code x}. */
    public static float noise1(long seed, float x) {
        long i = (long) Math.floor(x);
        float f = x - i;
        float a = unit(combine(seed, i)) * 2f - 1f;
        float b = unit(combine(seed, i + 1)) * 2f - 1f;
        float u = f * f * (3f - 2f * f);
        return a + (b - a) * u;
    }
}

package com.motionworks.engine.math;

/** Small scalar helpers shared by the engine. All angles are radians unless stated otherwise. */
public final class MathUtil {
    public static final float PI = (float) Math.PI;
    public static final float TAU = PI * 2f;
    public static final float DEG_TO_RAD = PI / 180f;
    public static final float RAD_TO_DEG = 180f / PI;

    private MathUtil() {}

    public static float lerp(float a, float b, float t) {
        return a + (b - a) * t;
    }

    public static float clamp(float v, float lo, float hi) {
        return v < lo ? lo : (v > hi ? hi : v);
    }

    public static float clamp01(float v) {
        return v < 0f ? 0f : (v > 1f ? 1f : v);
    }

    /** Wraps an angle into [-PI, PI). */
    public static float wrapRadians(float a) {
        a %= TAU;
        if (a >= PI) a -= TAU;
        if (a < -PI) a += TAU;
        return a;
    }

    /** Wraps an angle into [-180, 180). */
    public static float wrapDegrees(float a) {
        a %= 360f;
        if (a >= 180f) a -= 360f;
        if (a < -180f) a += 360f;
        return a;
    }

    /** Shortest-path angular interpolation in radians. */
    public static float lerpAngle(float a, float b, float t) {
        return a + wrapRadians(b - a) * t;
    }

    /** Frame-rate independent exponential approach: returns the blend factor for a given half-life. */
    public static float approachFactor(float halfLifeSeconds, float dt) {
        if (halfLifeSeconds <= 0f) return 1f;
        return 1f - (float) Math.pow(0.5, dt / halfLifeSeconds);
    }

    /** Catmull-Rom spline through p1..p2 with neighbours p0 and p3. */
    public static float catmullRom(float p0, float p1, float p2, float p3, float t) {
        float t2 = t * t;
        float t3 = t2 * t;
        return 0.5f * ((2f * p1) + (-p0 + p2) * t + (2f * p0 - 5f * p1 + 4f * p2 - p3) * t2 + (-p0 + 3f * p1 - 3f * p2 + p3) * t3);
    }

    /** Cubic Hermite between p1 and p2 with end tangents m1, m2 already scaled to the segment. */
    public static float hermite(float p1, float p2, float m1, float m2, float t) {
        float t2 = t * t;
        float t3 = t2 * t;
        return (2f * t3 - 3f * t2 + 1f) * p1 + (t3 - 2f * t2 + t) * m1 + (-2f * t3 + 3f * t2) * p2 + (t3 - t2) * m2;
    }

    /**
     * Auto-clamped slope at a key between a segment of duration h0 with slope d0 and one of duration h1 with
     * slope d1 (Fritsch-Butland, as in pchip): zero at holds and local extrema, otherwise a weighted harmonic
     * mean that keeps each segment monotone, so the curve never passes an authored value.
     */
    public static float clampedSlope(float d0, float d1, float h0, float h1) {
        if (d0 * d1 <= 0f) return 0f;
        float w1 = 2f * h1 + h0;
        float w2 = h1 + 2f * h0;
        return (w1 + w2) / (w1 / d0 + w2 / d1);
    }

    public static float smoothstep(float e0, float e1, float x) {
        float t = clamp01((x - e0) / (e1 - e0));
        return t * t * (3f - 2f * t);
    }

    public static float hermiteBlend(float t) {
        return t * t * (3f - 2f * t);
    }

    public static float sinDeg(float deg) {
        return (float) Math.sin(deg * DEG_TO_RAD);
    }

    public static float cosDeg(float deg) {
        return (float) Math.cos(deg * DEG_TO_RAD);
    }
}

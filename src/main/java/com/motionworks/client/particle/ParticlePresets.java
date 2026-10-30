package com.motionworks.client.particle;

import java.util.HashMap;
import java.util.Map;

/** Behaviour presets for every MotionWorks particle type. */
public final class ParticlePresets {
    /**
     * @param life       lifetime in ticks (randomised +/-25%)
     * @param size       quad size in blocks
     * @param grow       relative size change over life (negative shrinks)
     * @param fadeStart  normalised life at which fade-out begins
     * @param wind       how strongly the global wind pushes the particle
     * @param flutter    lateral wobble (leaves, snow)
     * @param spin       max roll speed in radians per tick
     */
    public record Preset(int life, float size, float gravity, float friction, boolean collide, float grow, float fadeStart,
                         float wind, float flutter, float spin, boolean emissive, boolean animated, float[] color, float colorJitter) {}

    private static final Map<String, Preset> PRESETS = new HashMap<>();

    static {
        PRESETS.put("spark", new Preset(12, 0.06f, 0.9f, 0.92f, true, -0.7f, 0.4f, 0f, 0f, 0f, true, false, rgba(1f, 0.85f, 0.5f, 1f), 0.15f));
        PRESETS.put("dust_puff", new Preset(26, 0.28f, -0.01f, 0.86f, false, 1.4f, 0.3f, 0.3f, 0f, 0.05f, false, false, rgba(0.62f, 0.55f, 0.45f, 0.55f), 0.1f));
        PRESETS.put("snow_puff", new Preset(22, 0.24f, 0.02f, 0.85f, false, 1.0f, 0.3f, 0.4f, 0.4f, 0.05f, false, false, rgba(0.95f, 0.97f, 1f, 0.7f), 0.03f));
        PRESETS.put("splash", new Preset(16, 0.09f, 1.0f, 0.95f, true, -0.3f, 0.6f, 0f, 0f, 0f, false, false, rgba(0.75f, 0.85f, 1f, 0.85f), 0.05f));
        PRESETS.put("ripple", new Preset(24, 0.4f, 0f, 1f, false, 2.2f, 0.2f, 0f, 0f, 0f, false, true, rgba(0.85f, 0.92f, 1f, 0.5f), 0f));
        PRESETS.put("ember", new Preset(50, 0.05f, -0.04f, 0.96f, false, -0.5f, 0.5f, 0.6f, 0.5f, 0f, true, false, rgba(1f, 0.55f, 0.2f, 1f), 0.2f));
        PRESETS.put("leaf", new Preset(140, 0.12f, 0.06f, 0.97f, true, 0f, 0.85f, 1.2f, 1.2f, 0.12f, false, false, rgba(0.45f, 0.62f, 0.25f, 1f), 0.25f));
        PRESETS.put("wind_streak", new Preset(18, 0.5f, 0f, 1f, false, 0.4f, 0.4f, 3f, 0f, 0f, false, true, rgba(1f, 1f, 1f, 0.22f), 0f));
        PRESETS.put("impact_ring", new Preset(8, 0.35f, 0f, 1f, false, 2.5f, 0.1f, 0f, 0f, 0f, true, true, rgba(1f, 0.95f, 0.85f, 0.75f), 0f));
        PRESETS.put("smoke_wisp", new Preset(70, 0.35f, -0.02f, 0.94f, false, 1.6f, 0.25f, 0.8f, 0.2f, 0.03f, false, false, rgba(0.35f, 0.35f, 0.38f, 0.45f), 0.1f));
        PRESETS.put("magic_glint", new Preset(24, 0.09f, -0.01f, 0.9f, false, -0.8f, 0.5f, 0f, 0.3f, 0.2f, true, true, rgba(0.75f, 0.6f, 1f, 1f), 0.2f));
        PRESETS.put("firefly", new Preset(120, 0.07f, 0f, 0.92f, false, 0f, 0.8f, 0.1f, 1.5f, 0f, true, false, rgba(0.85f, 1f, 0.45f, 1f), 0.1f));
        PRESETS.put("pollen", new Preset(160, 0.035f, -0.002f, 0.98f, false, 0f, 0.8f, 0.8f, 0.8f, 0f, false, false, rgba(1f, 0.95f, 0.6f, 0.8f), 0.1f));
        PRESETS.put("rain_streak", new Preset(10, 0.18f, 1.6f, 1f, true, 0f, 0.7f, 1.5f, 0f, 0f, false, false, rgba(0.7f, 0.78f, 0.9f, 0.5f), 0.05f));
        PRESETS.put("mote", new Preset(200, 0.03f, -0.0005f, 0.99f, false, 0f, 0.8f, 0.15f, 0.6f, 0f, true, false, rgba(1f, 0.97f, 0.88f, 0.6f), 0.1f));
        PRESETS.put("shockwave", new Preset(12, 0.8f, 0f, 1f, false, 4f, 0.1f, 0f, 0f, 0f, false, true, rgba(0.9f, 0.85f, 0.75f, 0.5f), 0f));
        PRESETS.put("breath", new Preset(30, 0.12f, -0.005f, 0.9f, false, 2f, 0.2f, 0.5f, 0.1f, 0.02f, false, false, rgba(0.9f, 0.93f, 1f, 0.35f), 0f));
        PRESETS.put("bubble_trail", new Preset(30, 0.05f, -0.06f, 0.9f, false, 0.2f, 0.7f, 0f, 0.6f, 0f, false, false, rgba(0.8f, 0.9f, 1f, 0.8f), 0f));
    }

    private ParticlePresets() {}

    private static float[] rgba(float r, float g, float b, float a) {
        return new float[] {r, g, b, a};
    }

    public static Preset get(String name) {
        return PRESETS.get(name);
    }

    /** Number of sprite frames per particle texture set (must match textures/particle). */
    public static int frames(String name) {
        Preset p = PRESETS.get(name);
        return p != null && p.animated() ? 6 : 3;
    }
}

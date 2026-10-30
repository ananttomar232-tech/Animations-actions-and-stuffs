package com.motionworks.engine.clip;

import java.util.Map;

/**
 * A timed side effect fired when playback crosses {@link #time}. The engine is agnostic about
 * what types mean; the Minecraft layer maps them to sounds, particles, camera shake, footsteps...
 */
public record ClipEvent(float time, String type, Map<String, String> data) {
    public String get(String key, String fallback) {
        String v = data.get(key);
        return v == null ? fallback : v;
    }

    public float getFloat(String key, float fallback) {
        String v = data.get(key);
        if (v == null) return fallback;
        try {
            return Float.parseFloat(v);
        } catch (NumberFormatException e) {
            return fallback;
        }
    }
}

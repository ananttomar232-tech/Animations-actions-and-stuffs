package com.motionworks.engine.runtime;

import com.motionworks.engine.math.MathUtil;

import java.util.Arrays;

/**
 * Result of evaluating a controller. For every bone and channel group (rotation, position,
 * scale) it stores an override value relative to the rest pose plus the weight with which that
 * override replaces the vanilla pose, and an additive offset applied afterwards:
 *
 * <pre>final = lerp(vanilla, rest + override, overrideWeight) + additive</pre>
 *
 * Scale overrides are multipliers (1 = rest); additive scale is a delta.
 */
public final class PoseBuffer {
    public final int bones;
    public final float[] override;
    public final float[] overrideWeight;
    public final float[] additive;

    public PoseBuffer(int bones) {
        this.bones = bones;
        this.override = new float[bones * 9];
        this.overrideWeight = new float[bones * 3];
        this.additive = new float[bones * 9];
    }

    public void reset() {
        Arrays.fill(override, 0f);
        Arrays.fill(overrideWeight, 0f);
        Arrays.fill(additive, 0f);
        for (int b = 0; b < bones; b++) {
            override[b * 9 + 6] = 1f;
            override[b * 9 + 7] = 1f;
            override[b * 9 + 8] = 1f;
        }
    }

    /** Layers an override on top of what previous layers produced, with coverage {@code c}. */
    public void blendOverride(int bone, int group, float x, float y, float z, float c) {
        if (c <= 0f) return;
        if (c > 1f) c = 1f;
        int w = bone * 3 + group;
        int o = bone * 9 + group * 3;
        float prevW = overrideWeight[w];
        if (group == 0 && prevW > 0f) {
            // Rotations blend along the shortest path: 720 degrees fading into 0 must not spin back twice.
            x = override[o] + MathUtil.wrapRadians(x - override[o]);
            y = override[o + 1] + MathUtil.wrapRadians(y - override[o + 1]);
            z = override[o + 2] + MathUtil.wrapRadians(z - override[o + 2]);
        }
        float newW = prevW * (1f - c) + c;
        float kPrev = prevW * (1f - c) / newW;
        float kNew = c / newW;
        override[o] = override[o] * kPrev + x * kNew;
        override[o + 1] = override[o + 1] * kPrev + y * kNew;
        override[o + 2] = override[o + 2] * kPrev + z * kNew;
        overrideWeight[w] = newW;
        // An override with full coverage also masks additive motion authored by lower layers.
        if (c >= 1f) {
            additive[o] = 0f;
            additive[o + 1] = 0f;
            additive[o + 2] = 0f;
        } else {
            float keep = 1f - c;
            additive[o] *= keep;
            additive[o + 1] *= keep;
            additive[o + 2] *= keep;
        }
    }

    public void addAdditive(int bone, int group, float x, float y, float z) {
        int o = bone * 9 + group * 3;
        additive[o] += x;
        additive[o + 1] += y;
        additive[o + 2] += z;
    }

    public boolean isTouched(int bone) {
        int w = bone * 3;
        if (overrideWeight[w] > 0f || overrideWeight[w + 1] > 0f || overrideWeight[w + 2] > 0f) return true;
        int o = bone * 9;
        for (int i = 0; i < 9; i++) if (additive[o + i] != 0f) return true;
        return false;
    }

    /**
     * Resolves a final channel value given the value vanilla produced and the rest value. Rotations move from
     * vanilla along the shortest path (an Euler angle and the same angle plus a whole turn are the same pose).
     */
    public float resolve(int bone, int component, float vanilla, float rest) {
        int group = component / 3;
        float w = overrideWeight[bone * 3 + group];
        float target = group == 2 ? override[bone * 9 + component] : rest + override[bone * 9 + component];
        float delta = group == 0 ? MathUtil.wrapRadians(target - vanilla) : target - vanilla;
        return vanilla + delta * w + additive[bone * 9 + component];
    }

    public void copyFrom(PoseBuffer other) {
        System.arraycopy(other.override, 0, override, 0, override.length);
        System.arraycopy(other.overrideWeight, 0, overrideWeight, 0, overrideWeight.length);
        System.arraycopy(other.additive, 0, additive, 0, additive.length);
    }
}

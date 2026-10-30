package com.motionworks.engine.expr;

/**
 * Evaluation scope for expressions. Entity-wide values live in {@link #values}; the clip
 * currently being sampled supplies its local time through the dedicated fields.
 */
public final class Scope {
    public float[] values = new float[64];
    public float animTime;
    public float animProgress;
    public float animLoop;
    public float deltaTime;
    /** Deterministic seed of the owning entity, used by {@code math.random}. */
    public long seed;

    public float get(int id) {
        if (id < Vars.LOCAL_LIMIT) {
            if (id == Vars.ANIM_TIME) return animTime;
            if (id == Vars.ANIM_PROGRESS) return animProgress;
            if (id == Vars.ANIM_LOOP) return animLoop;
            if (id == Vars.DELTA_TIME) return deltaTime;
        }
        return id < values.length ? values[id] : 0f;
    }

    public void set(int id, float v) {
        if (id >= values.length) {
            float[] grown = new float[Math.max(id + 16, values.length * 2)];
            System.arraycopy(values, 0, grown, 0, values.length);
            values = grown;
        }
        values[id] = v;
    }

    public void set(String name, float v) {
        set(Vars.id(name), v);
    }

    public void setBool(int id, boolean v) {
        set(id, v ? 1f : 0f);
    }

    public void setString(int id, String v) {
        set(id, StringIds.id(v));
    }
}

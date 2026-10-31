package com.motionworks.engine.clip;

import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.math.MathUtil;

import java.util.Arrays;
import java.util.Comparator;

/** A keyframed 3-component curve driving one transform channel of one bone. */
public final class Channel {
    public final ChannelTarget target;
    private final Keyframe[] keys;
    private final boolean constant;
    private static final Scope NO_SCOPE = new Scope();
    /** The curve is one period of a loop: smooth tangents wrap across the seam between last and first key. */
    private final boolean cyclic;

    public Channel(ChannelTarget target, Keyframe[] keys) {
        this(target, keys, false);
    }

    private Channel(ChannelTarget target, Keyframe[] keys, boolean cyclic) {
        if (keys.length == 0) throw new IllegalArgumentException("Channel needs at least one keyframe");
        this.target = target;
        this.keys = keys.clone();
        Arrays.sort(this.keys, Comparator.comparingDouble(Keyframe::time));
        boolean c = true;
        for (Keyframe k : this.keys) c &= k.isConstant();
        this.constant = c;
        this.cyclic = cyclic;
    }

    /**
     * This curve as one period of a loop of the given length, when it spans exactly 0..length and its
     * first and last keys hold the same constant values; otherwise this curve unchanged.
     */
    public Channel cyclicOver(float length) {
        Keyframe first = keys[0], last = keys[keys.length - 1];
        if (keys.length < 3 || first.time() > 1e-4f || Math.abs(last.time() - length) > 1e-4f) return this;
        for (int c = 0; c < 3; c++) {
            if (!first.post()[c].isConstant() || !last.pre()[c].isConstant()) return this;
            if (Math.abs(first.post()[c].eval(NO_SCOPE) - last.pre()[c].eval(NO_SCOPE)) > 1e-4f) return this;
        }
        return new Channel(target, keys, true);
    }

    public boolean isCyclic() {
        return cyclic;
    }

    public Keyframe[] keys() {
        return keys.clone();
    }

    public int keyCount() {
        return keys.length;
    }

    public float startTime() {
        return keys[0].time();
    }

    public float endTime() {
        return keys[keys.length - 1].time();
    }

    public boolean isConstant() {
        return constant;
    }

    /** Samples the curve at {@code t} seconds, writing three floats to {@code out[off..off+2]}. */
    public void sample(float t, Scope scope, float[] out, int off) {
        Keyframe[] k = keys;
        if (k.length == 1 || t <= k[0].time()) {
            Keyframe f = k[0];
            write(t <= f.time() && k.length > 1 ? f.pre() : f.post(), scope, out, off);
            return;
        }
        int last = k.length - 1;
        if (t >= k[last].time()) {
            write(k[last].post(), scope, out, off);
            return;
        }
        int i = segment(t);
        Keyframe a = k[i];
        Keyframe b = k[i + 1];
        float span = b.time() - a.time();
        float u = span <= 0f ? 1f : (t - a.time()) / span;
        if (b.interp() == Interp.STEP) {
            write(a.post(), scope, out, off);
            return;
        }
        u = b.easing().apply(MathUtil.clamp01(u));
        if (b.interp() == Interp.SMOOTH) {
            // Auto-clamped Hermite: time-aware tangents that are flat at holds, extrema, jump keys and the
            // ends of non-looping curves, so motion eases through every authored pose without overshooting it.
            Keyframe p = i > 0 ? k[i - 1] : cyclic ? k[last - 1] : null;
            float hp = i > 0 ? a.time() - p.time() : cyclic ? k[last].time() - p.time() : 0f;
            Keyframe n = i + 2 <= last ? k[i + 2] : cyclic ? k[1] : null;
            float hn = i + 2 <= last ? n.time() - b.time() : cyclic ? k[1].time() - k[0].time() : 0f;
            boolean flatA = p == null || hp <= 0f || a.pre() != a.post();
            boolean flatB = n == null || hn <= 0f || b.pre() != b.post();
            for (int c = 0; c < 3; c++) {
                float v1 = a.post()[c].eval(scope);
                float v2 = b.pre()[c].eval(scope);
                float d = span <= 0f ? 0f : (v2 - v1) / span;
                float m1 = flatA ? 0f : MathUtil.clampedSlope((v1 - p.post()[c].eval(scope)) / hp, d, hp, span);
                float m2 = flatB ? 0f : MathUtil.clampedSlope(d, (n.pre()[c].eval(scope) - v2) / hn, span, hn);
                out[off + c] = MathUtil.hermite(v1, v2, m1 * span, m2 * span, u);
            }
            return;
        }
        for (int c = 0; c < 3; c++) {
            out[off + c] = MathUtil.lerp(a.post()[c].eval(scope), b.pre()[c].eval(scope), u);
        }
    }

    private int segment(float t) {
        int lo = 0, hi = keys.length - 2;
        while (lo < hi) {
            int mid = (lo + hi + 1) >>> 1;
            if (keys[mid].time() <= t) lo = mid;
            else hi = mid - 1;
        }
        return lo;
    }

    private static void write(com.motionworks.engine.expr.Expr[] v, Scope s, float[] out, int off) {
        out[off] = v[0].eval(s);
        out[off + 1] = v[1].eval(s);
        out[off + 2] = v[2].eval(s);
    }
}

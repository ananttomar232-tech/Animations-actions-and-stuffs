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

    public Channel(ChannelTarget target, Keyframe[] keys) {
        if (keys.length == 0) throw new IllegalArgumentException("Channel needs at least one keyframe");
        this.target = target;
        this.keys = keys.clone();
        Arrays.sort(this.keys, Comparator.comparingDouble(Keyframe::time));
        boolean c = true;
        for (Keyframe k : this.keys) c &= k.isConstant();
        this.constant = c;
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
            Keyframe p = i > 0 ? k[i - 1] : a;
            Keyframe n = i + 2 <= last ? k[i + 2] : b;
            for (int c = 0; c < 3; c++) {
                float p0 = (p == a ? a.post() : p.post())[c].eval(scope);
                float p1 = a.post()[c].eval(scope);
                float p2 = b.pre()[c].eval(scope);
                float p3 = (n == b ? b.pre() : n.pre())[c].eval(scope);
                out[off + c] = MathUtil.catmullRom(p0, p1, p2, p3, u);
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

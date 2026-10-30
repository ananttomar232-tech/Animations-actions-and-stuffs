package com.motionworks.engine.procedural;

import com.motionworks.engine.expr.Expr;
import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.math.MathUtil;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.PoseBuffer;

/**
 * Very low amplitude, smooth, deterministic noise on a bone so characters are never perfectly
 * still. Amplitude is scaled by an expression (typically lower while sleeping, higher when nervous).
 */
public final class LifeNoise implements ProceduralModifier {
    private final int bone;
    private final float amplitudeDeg;
    private final float frequency;
    private final Expr scale;
    private final long salt;

    public LifeNoise(int bone, float amplitudeDeg, float frequency, Expr scale, long salt) {
        this.bone = bone;
        this.amplitudeDeg = amplitudeDeg;
        this.frequency = frequency;
        this.scale = scale;
        this.salt = salt;
    }

    @Override
    public void apply(AnimationController c, PoseBuffer pose, float dt) {
        if (bone < 0) return;
        float k = scale.eval(c.scope());
        if (k <= 0f) return;
        float t = c.time() * frequency;
        long s = Hashing.combine(c.seed(), salt);
        float a = amplitudeDeg * k * MathUtil.DEG_TO_RAD;
        pose.addAdditive(bone, 0,
                Hashing.noise1(s, t) * a,
                Hashing.noise1(s + 1, t * 0.83f) * a,
                Hashing.noise1(s + 2, t * 1.17f) * a * 0.5f);
    }
}

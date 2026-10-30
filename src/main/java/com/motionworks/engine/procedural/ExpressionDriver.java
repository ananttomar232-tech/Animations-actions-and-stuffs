package com.motionworks.engine.procedural;

import com.motionworks.engine.expr.Expr;
import com.motionworks.engine.math.MathUtil;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.PoseBuffer;

/**
 * Drives a bone channel directly from expressions with exponential smoothing. Used for things
 * like terrain alignment (body pitch from q.terrain_pitch) or torso twist from head yaw.
 */
public final class ExpressionDriver implements ProceduralModifier {
    private final int bone;
    private final int group;
    private final Expr[] exprs;
    private final float halfLife;
    private final float[] value = new float[3];
    private final float unit;

    /** @param group 0 rotation (degrees in expressions), 1 position (pixels) */
    public ExpressionDriver(int bone, int group, Expr[] exprs, float halfLifeSeconds) {
        this.bone = bone;
        this.group = group;
        this.exprs = exprs;
        this.halfLife = halfLifeSeconds;
        this.unit = group == 0 ? MathUtil.DEG_TO_RAD : 1f;
    }

    @Override
    public void apply(AnimationController c, PoseBuffer pose, float dt) {
        if (bone < 0) return;
        float k = MathUtil.approachFactor(halfLife, dt);
        for (int i = 0; i < 3; i++) {
            if (exprs[i] == null) continue;
            value[i] += (exprs[i].eval(c.scope()) - value[i]) * k;
        }
        pose.addAdditive(bone, group, value[0] * unit, value[1] * unit, value[2] * unit);
    }
}

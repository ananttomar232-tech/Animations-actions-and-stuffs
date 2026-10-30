package com.motionworks.engine.procedural;

import com.motionworks.engine.expr.Expr;
import com.motionworks.engine.math.MathUtil;
import com.motionworks.engine.runtime.AnimationController;
import com.motionworks.engine.runtime.PoseBuffer;

/**
 * Secondary motion: a critically-tunable damped spring per rotation axis that chases a target
 * angle computed from context expressions (for example the negated body turn rate for a tail, or
 * vertical speed for ears). Its output is added to the bone, so authored clips keep working and
 * the spring adds lag, overshoot and settle on top.
 */
public final class SpringBone implements ProceduralModifier {
    private final int bone;
    private final Expr[] targets;
    private final float stiffness;
    private final float damping;
    private final float limitDeg;
    private final float[] angle = new float[3];
    private final float[] velocity = new float[3];

    /**
     * @param targets   per-axis target expressions in degrees (null entries are ignored)
     * @param stiffness spring constant (1/s^2); 60-200 is typical
     * @param damping   damping ratio; 1 = critically damped, below 1 overshoots
     */
    public SpringBone(int bone, Expr[] targets, float stiffness, float damping, float limitDeg) {
        this.bone = bone;
        this.targets = targets;
        this.stiffness = stiffness;
        this.damping = damping;
        this.limitDeg = limitDeg;
    }

    @Override
    public void apply(AnimationController c, PoseBuffer pose, float dt) {
        if (bone < 0) return;
        float c2 = 2f * damping * (float) Math.sqrt(stiffness);
        int steps = Math.max(1, (int) Math.ceil(dt / 0.01f));
        float h = dt / steps;
        for (int axis = 0; axis < 3; axis++) {
            if (targets[axis] == null) continue;
            float target = MathUtil.clamp(targets[axis].eval(c.scope()), -limitDeg, limitDeg);
            for (int i = 0; i < steps; i++) {
                float acc = stiffness * (target - angle[axis]) - c2 * velocity[axis];
                velocity[axis] += acc * h;
                angle[axis] += velocity[axis] * h;
            }
            angle[axis] = MathUtil.clamp(angle[axis], -limitDeg, limitDeg);
        }
        pose.addAdditive(bone, 0, angle[0] * MathUtil.DEG_TO_RAD, angle[1] * MathUtil.DEG_TO_RAD, angle[2] * MathUtil.DEG_TO_RAD);
    }

    public float angle(int axis) {
        return angle[axis];
    }
}

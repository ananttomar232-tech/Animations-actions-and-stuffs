package com.motionworks.engine.clip;

import com.motionworks.engine.expr.Expr;
import com.motionworks.engine.math.Easing;

/**
 * A keyframe with separate "pre" (arriving) and "post" (leaving) values so authored motion can
 * contain deliberate snaps, matching the Bedrock animation format.
 */
public record Keyframe(float time, Expr[] pre, Expr[] post, Easing easing, Interp interp) {
    public Keyframe {
        if (pre.length != 3 || post.length != 3) throw new IllegalArgumentException("Keyframe values must be 3-component");
    }

    public static Keyframe of(float time, Expr[] value, Easing easing, Interp interp) {
        return new Keyframe(time, value, value, easing, interp);
    }

    public boolean isConstant() {
        for (int i = 0; i < 3; i++) if (!pre[i].isConstant() || !post[i].isConstant()) return false;
        return true;
    }
}

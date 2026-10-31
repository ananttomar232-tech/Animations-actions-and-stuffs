package com.motionworks.engine.runtime;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.clip.ChannelTarget;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.expr.Vars;
import com.motionworks.engine.math.MathUtil;

import java.util.List;

/** Poses one clip on its own at full weight, exactly as an animation layer would: for audits and tools. */
public final class ClipSampler {
    private ClipSampler() {}

    public static PoseBuffer sampleSolo(Rig rig, AnimationClip clip, float t, Scope scope) {
        PoseBuffer pose = new PoseBuffer(rig.size());
        pose.reset();
        scope.set(Vars.ANIM_TIME, t);
        scope.set(Vars.ANIM_PROGRESS, clip.length() > 0f ? t / clip.length() : 0f);
        int[] binding = rig.bind(clip);
        boolean[] mask = rig.mask(clip);
        List<BoneTrack> tracks = clip.tracks();
        float[] v = new float[3];
        for (int i = 0; i < tracks.size(); i++) {
            int bone = binding[i];
            if (bone < 0 || (mask != null && !mask[bone])) continue;
            for (ChannelTarget target : ChannelTarget.values()) {
                Channel ch = tracks.get(i).channel(target);
                if (ch == null) continue;
                ch.sample(t, scope, v, 0);
                if (target == ChannelTarget.ROTATION) {
                    for (int k = 0; k < 3; k++) v[k] *= MathUtil.DEG_TO_RAD;
                }
                if (clip.additive()) {
                    if (target == ChannelTarget.ROTATION) {
                        for (int k = 0; k < 3; k++) v[k] = MathUtil.wrapRadians(v[k]);
                    } else if (target == ChannelTarget.SCALE) {
                        for (int k = 0; k < 3; k++) v[k] -= 1f;
                    }
                    pose.addAdditive(bone, target.group(), v[0], v[1], v[2]);
                } else {
                    pose.blendOverride(bone, target.group(), v[0], v[1], v[2], 1f);
                }
            }
        }
        return pose;
    }
}

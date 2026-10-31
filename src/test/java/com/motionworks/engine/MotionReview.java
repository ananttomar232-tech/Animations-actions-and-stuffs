package com.motionworks.engine;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.clip.ChannelTarget;
import com.motionworks.engine.clip.LoopMode;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.expr.Vars;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * Samples every clip's curves the way playback does and measures motion defects that are visible in game:
 * non-finite output, a jump at the loop seam, a limb moving further in one 60 fps frame than reads as motion,
 * and a one-shot clip ending so far from rest that its blend-out cannot hide the snap.
 */
final class MotionReview {
    static final float HZ = 120f;

    record Finding(String clip, String kind, String detail, float amount) {}

    private MotionReview() {}

    /** A grounded, healthy, walking player with typical event data: values every clip should handle. */
    static Scope realistic() {
        Scope s = new Scope();
        Map<String, Float> v = Map.ofEntries(Map.entry("q.is_on_ground", 1f), Map.entry("q.health", 20f), Map.entry("q.max_health", 20f),
                Map.entry("q.recent_hurt", 100f), Map.entry("q.ground_speed", 0.13f), Map.entry("q.forward_speed", 0.13f),
                Map.entry("q.limb_swing", 12.3f), Map.entry("q.limb_swing_amount", 0.8f), Map.entry("q.moving", 1f),
                Map.entry("q.head_yaw", 20f), Map.entry("q.head_pitch", -10f), Map.entry("q.event_dir", 45f), Map.entry("q.event_height", 0.5f),
                Map.entry("q.use_time", 0.6f), Map.entry("q.hurt_dir", -60f), Map.entry("q.terrain_pitch", 12f), Map.entry("q.turn_rate", 40f),
                Map.entry("q.strafe_speed", 0.05f), Map.entry("q.light", 15f), Map.entry("q.mood", 0.5f), Map.entry("q.wind", 0.4f));
        v.forEach(s::set);
        return s;
    }

    /** Every variable set to a random value in [-50, 50]: probes expressions that break outside their usual range. */
    static Scope random(long seed) {
        Scope s = new Scope();
        Random r = new Random(seed);
        for (int i = 0; i < Vars.count(); i++) s.set(i, (r.nextFloat() - 0.5f) * 100f);
        return s;
    }

    static float[] sample(Channel ch, float t, Scope s, float length) {
        float[] out = new float[3];
        s.set(Vars.ANIM_TIME, t);
        s.set(Vars.ANIM_PROGRESS, length > 0 ? t / length : 0f);
        ch.sample(t, s, out, 0);
        return out;
    }

    /** Largest per-component change between two samples 1/60 s apart, scanned at 240 Hz. */
    static float frameJump(Channel ch, Scope s, float len) {
        float worst = 0f, step = 1f / 240f, frame = 1f / 60f;
        for (float t = 0f; t + frame <= len + 1e-6f; t += step) {
            float[] a = sample(ch, t, s, len), b = sample(ch, t + frame, s, len);
            for (int k = 0; k < 3; k++) worst = Math.max(worst, Math.abs(b[k] - a[k]));
        }
        return worst;
    }

    static List<Finding> review(AnimationClip c, Scope s, String scopeName) {
        List<Finding> out = new ArrayList<>();
        float len = Math.max(c.length(), 1e-3f);
        int n = Math.max(2, Math.round(len * HZ));
        float dt = len / n;
        for (BoneTrack t : c.tracks()) {
            for (ChannelTarget ct : ChannelTarget.values()) {
                Channel ch = t.channel(ct);
                if (ch == null) continue;
                String where = t.bone() + "." + ct.name().toLowerCase();
                boolean rot = ct == ChannelTarget.ROTATION;
                float[] first = sample(ch, 0f, s, len);
                boolean bad = false;
                for (int i = 1; i <= n; i++) {
                    for (float x : sample(ch, i * dt, s, len)) if (!Float.isFinite(x)) bad = true;
                }
                if (bad) out.add(new Finding(c.id(), "non_finite:" + scopeName, where, 1));
                if (!scopeName.equals("random")) {
                    // What a 60 fps viewer sees: the largest change between consecutive frames. Past these limits a
                    // limb appears to teleport rather than move fast (the first-person camera gets a tighter limit).
                    float jump = frameJump(ch, s, len);
                    float limit = rot ? (t.bone().equals("fp_view") ? 45f : 90f) : (ct == ChannelTarget.POSITION ? 6f : 0.35f);
                    if (jump > limit) out.add(new Finding(c.id(), "frame_jump", where, jump));
                    if (c.loop() == LoopMode.LOOP && c.timeDriver() == null) {
                        float[] end = sample(ch, len - 1e-4f, s, len);
                        float gap = 0;
                        for (int k = 0; k < 3; k++) {
                            float d = Math.abs(end[k] - first[k]);
                            // Whole turns are seamless (a spin that ends at 360 degrees looks like 0).
                            if (rot) d = Math.min(d % 360f, 360f - d % 360f);
                            gap = Math.max(gap, d);
                        }
                        float tol = rot ? 2f : (ct == ChannelTarget.POSITION ? 0.3f : 0.02f);
                        if (gap > tol) out.add(new Finding(c.id(), "loop_seam", where, gap));
                    }
                    if (c.loop() == LoopMode.ONCE && !c.additive()) {
                        float[] end = sample(ch, len, s, len);
                        float rest = ct == ChannelTarget.SCALE ? 1f : 0f;
                        float endPose = 0;
                        for (int k = 0; k < 3; k++) {
                            // Rotations blend along the shortest path, so a spin ending at 720 degrees ends at rest.
                            endPose = Math.max(endPose, Math.abs(rot ? com.motionworks.engine.math.MathUtil.wrapDegrees(end[k]) : end[k] - rest));
                        }
                        // Blending out over b seconds moves at roughly pose / b; flag what no blend can hide. (Start poses
                        // are not checked: release, parry and impact clips deliberately continue from a held pose.)
                        if (rot && endPose / Math.max(c.blendOut(), 1e-3f) > 3000f) out.add(new Finding(c.id(), "end_pop", where, endPose));
                    }
                }
            }
        }
        return out;
    }
}

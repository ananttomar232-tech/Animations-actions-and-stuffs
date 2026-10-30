package com.motionworks.engine.analysis;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;
import com.motionworks.engine.clip.Channel;
import com.motionworks.engine.clip.ChannelTarget;
import com.motionworks.engine.clip.LoopMode;
import com.motionworks.engine.expr.Scope;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

/**
 * Samples a clip's motion over normalised time into a vector so clips can be compared. Because
 * time is normalised, playback-speed variants produce the same signature; because vectors are
 * also compared after amplitude normalisation, mirrored and phase-shifted copies, the checker
 * catches every kind of "variation" the registry must not count as a new animation.
 */
public final class MotionSignature {
    public static final int SAMPLES = 24;

    public final AnimationClip clip;
    /** Sorted list of animated channel keys, e.g. "right_arm/rotation". */
    public final List<String> channels;
    final float[] data;
    final float norm;

    private MotionSignature(AnimationClip clip, List<String> channels, float[] data) {
        this.clip = clip;
        this.channels = channels;
        this.data = data;
        double n = 0;
        for (float v : data) n += v * v;
        this.norm = (float) Math.sqrt(n);
    }

    public static MotionSignature of(AnimationClip clip) {
        return of(clip, false);
    }

    /** @param mirrored swap left/right bones and negate lateral components */
    public static MotionSignature of(AnimationClip clip, boolean mirrored) {
        Map<String, BoneTrack> tracks = new HashMap<>();
        for (BoneTrack t : clip.tracks()) tracks.put(mirrored ? mirror(t.bone()) : t.bone(), t);
        TreeSet<String> keys = new TreeSet<>();
        for (Map.Entry<String, BoneTrack> e : tracks.entrySet()) {
            for (ChannelTarget ct : ChannelTarget.values()) {
                if (e.getValue().channel(ct) != null) keys.add(e.getKey() + "/" + ct.name().toLowerCase());
            }
        }
        List<String> channels = new ArrayList<>(keys);
        float[] data = new float[channels.size() * 3 * SAMPLES];
        Scope scope = new Scope();
        float[] tmp = new float[3];
        float len = Math.max(clip.length(), 1e-3f);
        for (int s = 0; s < SAMPLES; s++) {
            float t = clip.loop() == LoopMode.LOOP ? len * s / SAMPLES : len * s / (SAMPLES - 1);
            scope.animTime = t;
            scope.animProgress = t / len;
            for (int c = 0; c < channels.size(); c++) {
                String key = channels.get(c);
                int slash = key.indexOf('/');
                BoneTrack track = tracks.get(key.substring(0, slash));
                ChannelTarget ct = ChannelTarget.valueOf(key.substring(slash + 1).toUpperCase());
                Channel ch = track.channel(ct);
                ch.sample(t, scope, tmp, 0);
                float k = ct == ChannelTarget.ROTATION ? 1f : (ct == ChannelTarget.POSITION ? 4f : 60f);
                for (int i = 0; i < 3; i++) {
                    float v = ct == ChannelTarget.SCALE ? tmp[i] - 1f : tmp[i];
                    if (mirrored && ct != ChannelTarget.SCALE && i > 0 && ct == ChannelTarget.ROTATION) v = -v;
                    if (mirrored && ct == ChannelTarget.POSITION && i == 0) v = -v;
                    data[(s * channels.size() + c) * 3 + i] = v * k;
                }
            }
        }
        return new MotionSignature(clip, channels, data);
    }

    static String mirror(String bone) {
        if (bone.contains("left")) return bone.replace("left", "right");
        if (bone.contains("right")) return bone.replace("right", "left");
        return bone;
    }

    public float magnitude() {
        return norm;
    }

    /**
     * Similarity in [0,1] between two signatures with identical channel sets; 1 means the same
     * motion up to uniform amplitude scaling (and, for loops, a phase shift).
     */
    public float similarity(MotionSignature o) {
        if (!channels.equals(o.channels)) return 0f;
        if (norm < 1e-3f || o.norm < 1e-3f) return norm < 1e-3f && o.norm < 1e-3f ? 1f : 0f;
        int stride = channels.size() * 3;
        int shifts = clip.loop() == LoopMode.LOOP && o.clip.loop() == LoopMode.LOOP ? SAMPLES : 1;
        float best = 0f;
        for (int shift = 0; shift < shifts; shift++) {
            double dot = 0;
            for (int s = 0; s < SAMPLES; s++) {
                int so = ((s + shift) % SAMPLES) * stride;
                int sa = s * stride;
                for (int i = 0; i < stride; i++) dot += (double) data[sa + i] * o.data[so + i];
            }
            best = Math.max(best, (float) (dot / (norm * (double) o.norm)));
        }
        return best;
    }

    /** RMS distance after optimal alignment, in signature units (degrees for rotation). */
    public float distance(MotionSignature o) {
        if (!channels.equals(o.channels)) return Float.POSITIVE_INFINITY;
        double sum = 0;
        for (int i = 0; i < data.length; i++) {
            double d = data[i] - o.data[i];
            sum += d * d;
        }
        return (float) Math.sqrt(sum / Math.max(1, data.length));
    }

    public record Duplicate(AnimationClip a, AnimationClip b, String kind, float score) {}

    /**
     * Finds clip pairs that are not genuinely distinct: identical channel sets with motion that is
     * the same up to speed, amplitude, phase or mirroring. Clips are bucketed by channel set first
     * so the search stays fast for thousands of clips.
     *
     * @param threshold similarity at or above which two clips are flagged (0.995 is strict)
     */
    public static List<Duplicate> findDuplicates(Collection<AnimationClip> clips, float threshold) {
        Map<List<String>, List<MotionSignature>> buckets = new HashMap<>();
        List<MotionSignature> all = new ArrayList<>();
        for (AnimationClip c : clips) {
            MotionSignature sig = of(c);
            all.add(sig);
            buckets.computeIfAbsent(sig.channels, k -> new ArrayList<>()).add(sig);
        }
        List<Duplicate> out = new ArrayList<>();
        java.util.Set<String> seen = new java.util.HashSet<>();
        for (List<MotionSignature> bucket : buckets.values()) {
            for (int i = 0; i < bucket.size(); i++) {
                for (int j = i + 1; j < bucket.size(); j++) {
                    MotionSignature a = bucket.get(i), b = bucket.get(j);
                    float sim = a.similarity(b);
                    if (sim >= threshold && seen.add(pairKey(a.clip, b.clip))) {
                        out.add(new Duplicate(a.clip, b.clip, "same-motion(speed/amplitude/phase)", sim));
                    }
                }
            }
        }
        for (MotionSignature a : all) {
            MotionSignature m = of(a.clip, true);
            List<MotionSignature> bucket = buckets.get(m.channels);
            if (bucket == null) continue;
            for (MotionSignature b : bucket) {
                if (b.clip == a.clip) continue;
                float sim = m.similarity(b);
                if (sim >= threshold && seen.add(pairKey(a.clip, b.clip))) out.add(new Duplicate(a.clip, b.clip, "mirrored", sim));
            }
        }
        return out;
    }

    private static String pairKey(AnimationClip a, AnimationClip b) {
        return a.id().compareTo(b.id()) < 0 ? a.id() + "|" + b.id() : b.id() + "|" + a.id();
    }
}

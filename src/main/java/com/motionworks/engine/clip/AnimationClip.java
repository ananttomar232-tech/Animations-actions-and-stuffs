package com.motionworks.engine.clip;

import com.motionworks.engine.expr.Expr;

import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * An immutable, authored animation sequence plus the metadata the registry tracks for it.
 *
 * @param id            unique id such as {@code player.combat.sword_slash_rising}
 * @param category      registry category (player_locomotion, hostile_mobs ...)
 * @param target        entity type id or rig group the clip is written for
 * @param rig           rig vocabulary used by the bone names (humanoid, quadruped, wolf ...)
 * @param layer         controller layer the clip plays on (base, overlay, action, additive, reaction, face, first_person)
 * @param additive      when true channel values are added on top instead of overriding
 * @param mask          optional bone mask; entries starting with '@' reference rig bone groups
 * @param speed         playback-rate expression (1 = authored speed)
 * @param timeDriver    optional expression that directly drives clip time in seconds (phase-locked locomotion)
 * @param weight        per-frame weight expression
 * @param interruptAfter normalised time after which equal-priority actions may interrupt
 */
public record AnimationClip(
        String id,
        String name,
        String category,
        String target,
        String rig,
        float length,
        LoopMode loop,
        String layer,
        int priority,
        float blendIn,
        float blendOut,
        boolean additive,
        Set<String> mask,
        Expr speed,
        Expr timeDriver,
        Expr weight,
        Trigger trigger,
        List<BoneTrack> tracks,
        List<ClipEvent> events,
        boolean interruptible,
        float interruptAfter,
        Map<String, String> meta) {

    public String meta(String key, String fallback) {
        String v = meta.get(key);
        return v == null ? fallback : v;
    }

    public int keyCount() {
        int n = 0;
        for (BoneTrack t : tracks) n += t.keyCount();
        return n;
    }

    public BoneTrack track(String bone) {
        for (BoneTrack t : tracks) if (t.bone().equals(bone)) return t;
        return null;
    }
}

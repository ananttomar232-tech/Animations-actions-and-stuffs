package com.motionworks.engine.io;

import com.motionworks.engine.clip.AnimationClip;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/** The animation registry: every loaded clip by id, with lookups by target and category. */
public final class ClipLibrary {
    private final Map<String, AnimationClip> clips = new LinkedHashMap<>();
    private final Map<String, List<AnimationClip>> byTarget = new LinkedHashMap<>();

    public synchronized void clear() {
        clips.clear();
        byTarget.clear();
    }

    /** Adds clips, replacing any existing clip with the same id (later packs override earlier ones). */
    public synchronized void addAll(Collection<AnimationClip> list) {
        for (AnimationClip c : list) {
            AnimationClip old = clips.put(c.id(), c);
            if (old != null) byTarget.getOrDefault(old.target(), new ArrayList<>()).remove(old);
            byTarget.computeIfAbsent(c.target(), k -> new ArrayList<>()).add(c);
        }
    }

    public synchronized AnimationClip get(String id) {
        return clips.get(id);
    }

    public synchronized Collection<AnimationClip> all() {
        return Collections.unmodifiableCollection(new ArrayList<>(clips.values()));
    }

    public synchronized int size() {
        return clips.size();
    }

    /** Clips written for any of the given targets (entity ids or '@group' names), in load order. */
    public synchronized List<AnimationClip> forTargets(Collection<String> targets) {
        List<AnimationClip> out = new ArrayList<>();
        for (String t : targets) {
            List<AnimationClip> l = byTarget.get(t);
            if (l != null) out.addAll(l);
        }
        return out;
    }

    public synchronized Map<String, Integer> countByCategory() {
        Map<String, Integer> m = new TreeMap<>();
        for (AnimationClip c : clips.values()) m.merge(c.category(), 1, Integer::sum);
        return m;
    }

    public synchronized Map<String, Integer> countByTarget() {
        Map<String, Integer> m = new TreeMap<>();
        for (AnimationClip c : clips.values()) m.merge(c.target(), 1, Integer::sum);
        return m;
    }
}

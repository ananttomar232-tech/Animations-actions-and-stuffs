package com.motionworks.engine.runtime;

import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.clip.BoneTrack;

import java.util.Collection;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * The bone vocabulary of one concrete model. Clips reference bones by name and are bound to a
 * rig lazily; bones a clip mentions but the rig lacks are skipped, which lets one humanoid clip
 * drive players, zombies and piglins alike.
 */
public final class Rig {
    public final String id;
    private final String[] bones;
    private final int[] parents;
    private final Map<String, Integer> index = new HashMap<>();
    private final Map<String, int[]> groups = new HashMap<>();
    private final Map<AnimationClip, int[]> bindings = new IdentityHashMap<>();
    private final Map<AnimationClip, boolean[]> masks = new IdentityHashMap<>();

    public Rig(String id, List<String> boneNames, int[] parents, Map<String, ? extends Collection<String>> boneGroups) {
        this.id = id;
        this.bones = boneNames.toArray(new String[0]);
        this.parents = parents == null ? filled(bones.length) : parents.clone();
        for (int i = 0; i < bones.length; i++) index.putIfAbsent(bones[i], i);
        if (boneGroups != null) {
            boneGroups.forEach((g, names) -> groups.put(g, names.stream().mapToInt(this::indexOf).filter(i -> i >= 0).toArray()));
        }
    }

    private static int[] filled(int n) {
        int[] p = new int[n];
        java.util.Arrays.fill(p, -1);
        return p;
    }

    public int size() {
        return bones.length;
    }

    public String bone(int i) {
        return bones[i];
    }

    public int parent(int i) {
        return parents[i];
    }

    public int indexOf(String name) {
        Integer i = index.get(name);
        return i == null ? -1 : i;
    }

    public boolean has(String name) {
        return index.containsKey(name);
    }

    public int[] group(String name) {
        int[] g = groups.get(name);
        return g == null ? new int[0] : g;
    }

    public Set<String> groupNames() {
        return groups.keySet();
    }

    /** Per-track bone indices for {@code clip}; -1 for bones this rig does not have. */
    public synchronized int[] bind(AnimationClip clip) {
        return bindings.computeIfAbsent(clip, c -> {
            List<BoneTrack> tracks = c.tracks();
            int[] out = new int[tracks.size()];
            for (int i = 0; i < out.length; i++) out[i] = indexOf(tracks.get(i).bone());
            return out;
        });
    }

    /** Bone mask for {@code clip} or null when the clip is unmasked. */
    public synchronized boolean[] mask(AnimationClip clip) {
        if (clip.mask() == null || clip.mask().isEmpty()) return null;
        return masks.computeIfAbsent(clip, c -> {
            boolean[] m = new boolean[bones.length];
            for (String entry : c.mask()) {
                if (entry.startsWith("@")) {
                    for (int i : group(entry.substring(1))) m[i] = true;
                } else {
                    int i = indexOf(entry);
                    if (i >= 0) m[i] = true;
                }
            }
            return m;
        });
    }

}

package com.motionworks.client.rig;

import com.motionworks.MotionWorks;
import com.motionworks.engine.runtime.Rig;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelPart;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.WeakHashMap;

/**
 * Discovers the parts of any entity model without depending on obfuscated field names: parts
 * are found by type (fields holding ModelPart or ModelPart[]) or through the root of hierarchical
 * models, then named through {@link ModelPartIndex}.
 */
public final class RigFactory {
    private static final Map<EntityModel<?>, Map<RigProfile, ModelRig>> CACHE = Collections.synchronizedMap(new WeakHashMap<>());

    private RigFactory() {}

    public static ModelRig get(EntityModel<?> model, RigProfile profile) {
        Map<RigProfile, ModelRig> byProfile = CACHE.computeIfAbsent(model, m -> new IdentityHashMap<>());
        synchronized (byProfile) {
            return byProfile.computeIfAbsent(profile, p -> build(model, p));
        }
    }

    /** Undoes the last frame's writes on every rig bound to this model (see {@link PoseApplier#restore}). */
    public static void restore(EntityModel<?> model) {
        Map<RigProfile, ModelRig> byProfile = CACHE.get(model);
        if (byProfile == null) return;
        synchronized (byProfile) {
            for (ModelRig mr : byProfile.values()) PoseApplier.restore(mr);
        }
    }

    public static void clear() {
        CACHE.clear();
    }

    static ModelRig build(EntityModel<?> model, RigProfile profile) {
        LinkedHashMap<String, ModelPart> found = new LinkedHashMap<>();
        Set<ModelPart> seen = Collections.newSetFromMap(new IdentityHashMap<>());
        if (model instanceof HierarchicalModel<?> h) {
            ModelPart root = h.root();
            walk(root, found, seen);
        }
        for (Class<?> c = model.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            for (Field f : c.getDeclaredFields()) {
                if (Modifier.isStatic(f.getModifiers())) continue;
                try {
                    if (f.getType() == ModelPart.class) {
                        f.setAccessible(true);
                        ModelPart p = (ModelPart) f.get(model);
                        if (p != null) {
                            add(p, found, seen);
                            walk(p, found, seen);
                        }
                    } else if (f.getType() == ModelPart[].class) {
                        f.setAccessible(true);
                        ModelPart[] arr = (ModelPart[]) f.get(model);
                        if (arr != null) for (ModelPart p : arr) {
                            if (p != null) {
                                add(p, found, seen);
                                walk(p, found, seen);
                            }
                        }
                    }
                } catch (ReflectiveOperationException | RuntimeException e) {
                    MotionWorks.LOGGER.debug("Skipping field {} of {}: {}", f.getName(), c.getName(), e.toString());
                }
            }
        }
        List<String> names = new ArrayList<>();
        List<ModelPart> parts = new ArrayList<>();
        names.add(ModelRig.ROOT);
        parts.add(null);
        names.add(ModelRig.CENTER);
        parts.add(null);
        for (Map.Entry<String, ModelPart> e : found.entrySet()) {
            names.add(e.getKey());
            parts.add(e.getValue());
        }
        Map<String, List<String>> groups = new LinkedHashMap<>(profile.groups);
        autoGroups(names, groups);
        Rig rig = new Rig(profile.id + "@" + model.getClass().getSimpleName(), names, null, groups);

        List<int[]> followers = new ArrayList<>();
        profile.followers.forEach((follower, leader) -> {
            int f = rig.indexOf(follower), l = rig.indexOf(leader);
            if (f >= 2 && l >= 2) followers.add(new int[] {f, l});
        });
        List<int[]> couplings = new ArrayList<>();
        List<float[]> pivots = new ArrayList<>();
        List<Boolean> moves = new ArrayList<>();
        for (RigProfile.Coupling c : profile.couplings) {
            int parent = rig.indexOf(c.parent());
            if (parent < 2) continue;
            int[] entry = new int[c.children().size() + 1];
            entry[0] = parent;
            int n = 1;
            for (String child : c.children()) {
                int ci = rig.indexOf(child);
                if (ci >= 2) entry[n++] = ci;
            }
            couplings.add(java.util.Arrays.copyOf(entry, n));
            pivots.add(c.pivot());
            moves.add(c.moveParent());
        }
        boolean[] mv = new boolean[moves.size()];
        for (int i = 0; i < mv.length; i++) mv[i] = moves.get(i);
        return new ModelRig(rig, profile, parts.toArray(new ModelPart[0]), followers.toArray(new int[0][]),
                couplings.toArray(new int[0][]), pivots.toArray(new float[0][]), mv);
    }

    private static void add(ModelPart p, Map<String, ModelPart> found, Set<ModelPart> seen) {
        if (!seen.add(p)) return;
        ModelPartIndex.Info info = ModelPartIndex.get(p);
        String name = info != null ? info.name() : "part_" + found.size();
        if (found.containsKey(name)) {
            name = info != null ? info.path().replace('/', '.') : name + "_" + found.size();
        }
        if (!found.containsKey(name)) found.put(name, p);
    }

    private static void walk(ModelPart part, Map<String, ModelPart> found, Set<ModelPart> seen) {
        for (Map.Entry<String, ModelPart> e : ModelPartIndex.children(part).entrySet()) {
            ModelPart child = e.getValue();
            if (seen.contains(child)) continue;
            seen.add(child);
            String name = e.getKey();
            if (found.containsKey(name)) {
                ModelPartIndex.Info info = ModelPartIndex.get(child);
                name = info != null ? info.path().replace('/', '.') : name + "_" + found.size();
            }
            found.putIfAbsent(name, child);
            walk(child, found, seen);
        }
    }

    /** Groups every rig gets for free, derived from conventional vanilla part names. */
    private static void autoGroups(List<String> names, Map<String, List<String>> groups) {
        Map<String, Set<String>> auto = new LinkedHashMap<>();
        for (String n : names) {
            if (n.startsWith("mw_")) continue;
            put(auto, "all", n);
            if (n.contains("leg") || n.contains("foot") || n.contains("haunch")) put(auto, "legs", n);
            if (n.contains("arm") || n.contains("hand") || n.contains("sleeve")) put(auto, "arms", n);
            if (n.contains("wing")) put(auto, "wings", n);
            if (n.contains("tail")) put(auto, "tail", n);
            if (n.contains("head") || n.contains("ear") || n.contains("nose") || n.contains("hat") || n.contains("jaw") || n.contains("mouth") || n.contains("beak") || n.contains("horn")) put(auto, "head", n);
            if (n.startsWith("left")) put(auto, "left", n);
            if (n.startsWith("right")) put(auto, "right", n);
            if (n.contains("fin")) put(auto, "fins", n);
            if (n.contains("tentacle")) put(auto, "tentacles", n);
        }
        Set<String> upper = new LinkedHashSet<>();
        for (String n : names) {
            if (n.startsWith("mw_")) continue;
            boolean lower = n.contains("leg") || n.contains("foot") || n.contains("pants") || n.contains("haunch");
            if (!lower) upper.add(n);
        }
        auto.put("upper_body", upper);
        auto.forEach((k, v) -> groups.putIfAbsent(k, new ArrayList<>(v)));
    }

    private static void put(Map<String, Set<String>> m, String k, String v) {
        m.computeIfAbsent(k, x -> new LinkedHashSet<>()).add(v);
    }
}

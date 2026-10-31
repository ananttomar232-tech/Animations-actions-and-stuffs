package com.motionworks.client.rig;

import com.motionworks.mixin.client.ModelPartAccessor;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.Collections;
import java.util.Map;
import java.util.WeakHashMap;

/**
 * Maps baked {@link ModelPart} instances back to the names they were given in their layer
 * definition. Those names are plain strings in vanilla code, so unlike field names they are the
 * same in development and production, which makes name-based rigs robust and mod-friendly.
 */
public final class ModelPartIndex {
    public record Info(String name, String path, ModelLayerLocation layer) {}

    private static final Map<ModelPart, Info> INFO = Collections.synchronizedMap(new WeakHashMap<>());

    private ModelPartIndex() {}

    public static void index(ModelLayerLocation layer, ModelPart root) {
        if (root == null) return;
        INFO.put(root, new Info("root", "root", layer));
        walk(layer, root, "");
    }

    private static void walk(ModelLayerLocation layer, ModelPart part, String path) {
        for (Map.Entry<String, ModelPart> e : children(part).entrySet()) {
            String p = path.isEmpty() ? e.getKey() : path + "/" + e.getKey();
            INFO.put(e.getValue(), new Info(e.getKey(), p, layer));
            walk(layer, e.getValue(), p);
        }
    }

    public static Info get(ModelPart part) {
        return INFO.get(part);
    }

    /**
     * A part's named children. Normally read through the mixin accessor; where mixins are not applied
     * (unit tests) the map is found by type, as ModelPart holds exactly one Map field.
     */
    @SuppressWarnings("unchecked")
    public static Map<String, ModelPart> children(ModelPart part) {
        if ((Object) part instanceof ModelPartAccessor a) return a.motionworks$children();
        if (childrenField == null) {
            for (Field f : ModelPart.class.getDeclaredFields()) {
                if (f.getType() == Map.class && !Modifier.isStatic(f.getModifiers())) {
                    f.setAccessible(true);
                    childrenField = f;
                }
            }
        }
        try {
            return childrenField == null ? Map.of() : (Map<String, ModelPart>) childrenField.get(part);
        } catch (IllegalAccessException e) {
            return Map.of();
        }
    }

    private static Field childrenField;
}

package com.motionworks.client.rig;

import com.mojang.blaze3d.vertex.PoseStack;
import com.motionworks.engine.runtime.PoseBuffer;
import net.minecraft.client.model.geom.ModelPart;
import org.joml.Matrix4f;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Set;

/**
 * Keeps animated bodies out of the ground. A Minecraft leg is one block with no knee, so lowering the body and
 * letting the feet pass into the ground is how a kneel or a crouch reads; a torso, head or arm in the ground is
 * a glitch (a roll, a cartwheel, a pose lying down). Measured on the posed model: when anything but the legs
 * dips below where vanilla's pose had its lowest point, the model is lifted by exactly that much.
 */
public final class GroundContact {
    private GroundContact() {}

    /** Lowest visible point in model pixels (model space points down), with the root bones of {@code pose} applied. */
    public static float lowest(ModelRig mr, PoseBuffer pose, float strength, boolean includeLegs) {
        PoseStack stack = new PoseStack();
        if (pose != null) PoseApplier.applyRoot(mr, pose, stack, strength);
        Lowest visitor = new Lowest(includeLegs);
        ModelPart[] top = mr.topLevel();
        boolean[] legs = mr.topIsLeg();
        for (int i = 0; i < top.length; i++) {
            if (!top[i].visible || (!includeLegs && legs[i])) continue;
            top[i].visit(stack, visitor);
        }
        return visitor.low;
    }

    /** How far (in model pixels) the posed model must rise so nothing but its legs is below {@code ground}. */
    public static float lift(ModelRig mr, PoseBuffer pose, float strength, float ground) {
        float body = lowest(mr, pose, strength, false);
        return body == -Float.MAX_VALUE ? 0f : Math.max(0f, body - ground);
    }

    static boolean isLeg(String name) {
        String leaf = name.substring(name.lastIndexOf('/') + 1);
        return leaf.contains("leg") || leaf.contains("foot") || leaf.contains("pants");
    }

    static ModelPart[] topLevel(ModelPart[] parts) {
        Set<ModelPart> children = Collections.newSetFromMap(new IdentityHashMap<>());
        for (ModelPart part : parts) if (part != null) children.addAll(ModelPartIndex.children(part).values());
        List<ModelPart> out = new ArrayList<>();
        for (ModelPart part : parts) if (part != null && !children.contains(part)) out.add(part);
        return out.toArray(new ModelPart[0]);
    }

    private static final class Lowest implements ModelPart.Visitor {
        final boolean includeLegs;
        final Vector3f p = new Vector3f();
        float low = -Float.MAX_VALUE;

        Lowest(boolean includeLegs) {
            this.includeLegs = includeLegs;
        }

        @Override
        public void visit(PoseStack.Pose pose, String path, int index, ModelPart.Cube cube) {
            // visit() names nested children in the path (a top-level part's own cubes arrive with an empty one)
            if (!includeLegs && !path.isEmpty() && isLeg(path)) return;
            Matrix4f m = pose.pose();
            for (int c = 0; c < 8; c++) {
                p.set(((c & 1) == 0 ? cube.minX : cube.maxX) / 16f, ((c & 2) == 0 ? cube.minY : cube.maxY) / 16f,
                        ((c & 4) == 0 ? cube.minZ : cube.maxZ) / 16f);
                m.transformPosition(p);
                low = Math.max(low, p.y * 16f);
            }
        }
    }
}

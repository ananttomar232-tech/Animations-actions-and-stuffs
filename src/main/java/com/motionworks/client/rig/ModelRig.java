package com.motionworks.client.rig;

import com.motionworks.engine.runtime.Rig;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;

/**
 * A {@link Rig} bound to the concrete {@link ModelPart}s of one model instance. Index 0 and 1 are
 * virtual bones: {@code mw_root} rotates the whole model about the ground point and
 * {@code mw_center} about the body centre; both are applied to the pose stack.
 */
public final class ModelRig {
    public static final String ROOT = "mw_root";
    public static final String CENTER = "mw_center";

    public final Rig rig;
    public final RigProfile profile;
    public final ModelPart[] parts;
    public final float[] rest;
    final float[] vanilla;
    /** What the last apply wrote, and the vanilla values it replaced; see {@link PoseApplier#restore}. */
    final float[] written;
    final float[] replaced;
    boolean hasOutput;
    final int[][] followers;
    final int[][] couplings;
    final float[][] couplingPivots;
    final boolean[] couplingMovesParent;

    ModelRig(Rig rig, RigProfile profile, ModelPart[] parts, int[][] followers, int[][] couplings, float[][] couplingPivots, boolean[] movesParent) {
        this.rig = rig;
        this.profile = profile;
        this.parts = parts;
        this.rest = new float[parts.length * 9];
        this.vanilla = new float[parts.length * 9];
        this.written = new float[parts.length * 9];
        this.replaced = new float[parts.length * 9];
        for (int i = 0; i < parts.length; i++) {
            ModelPart p = parts[i];
            int o = i * 9;
            rest[o + 6] = rest[o + 7] = rest[o + 8] = 1f;
            if (p == null) continue;
            PartPose pose = p.getInitialPose();
            rest[o] = pose.xRot;
            rest[o + 1] = pose.yRot;
            rest[o + 2] = pose.zRot;
            rest[o + 3] = pose.x;
            rest[o + 4] = pose.y;
            rest[o + 5] = pose.z;
        }
        this.followers = followers;
        this.couplings = couplings;
        this.couplingPivots = couplingPivots;
        this.couplingMovesParent = movesParent;
        float[][] measured = profile.center == null || profile.ground == null ? restBounds() : null;
        this.center = profile.center != null ? profile.center : measured[0];
        this.ground = profile.ground != null ? profile.ground : measured[1];
    }

    /** Pivot of mw_center (body centre) and mw_root (ground) in model pixels. */
    final float[] center;
    final float[] ground;

    /**
     * Centre and bottom centre of the model's visible geometry in its rest pose. A rotation about a pivot that is
     * not inside the body (the old fixed defaults sat above a chicken or a fish) swings it through the air.
     */
    private float[][] restBounds() {
        PartPose[] saved = new PartPose[parts.length];
        for (int i = 0; i < parts.length; i++) {
            if (parts[i] == null) continue;
            saved[i] = parts[i].storePose();
            parts[i].loadPose(parts[i].getInitialPose());
        }
        float[] min = {Float.MAX_VALUE, Float.MAX_VALUE, Float.MAX_VALUE}, max = {-Float.MAX_VALUE, -Float.MAX_VALUE, -Float.MAX_VALUE};
        org.joml.Vector3f p = new org.joml.Vector3f();
        com.mojang.blaze3d.vertex.PoseStack stack = new com.mojang.blaze3d.vertex.PoseStack();
        for (ModelPart part : GroundContact.topLevel(parts)) {
            if (!part.visible) continue;
            part.visit(stack, (pose, path, index, cube) -> {
                for (int c = 0; c < 8; c++) {
                    p.set(((c & 1) == 0 ? cube.minX : cube.maxX) / 16f, ((c & 2) == 0 ? cube.minY : cube.maxY) / 16f, ((c & 4) == 0 ? cube.minZ : cube.maxZ) / 16f);
                    pose.pose().transformPosition(p);
                    min[0] = Math.min(min[0], p.x * 16f);
                    min[1] = Math.min(min[1], p.y * 16f);
                    min[2] = Math.min(min[2], p.z * 16f);
                    max[0] = Math.max(max[0], p.x * 16f);
                    max[1] = Math.max(max[1], p.y * 16f);
                    max[2] = Math.max(max[2], p.z * 16f);
                }
            });
        }
        for (int i = 0; i < parts.length; i++) if (parts[i] != null) parts[i].loadPose(saved[i]);
        if (min[0] > max[0]) return new float[][] {{0f, 12f, 0f}, {0f, 24f, 0f}};
        float cz = (min[2] + max[2]) / 2f;
        return new float[][] {{0f, (min[1] + max[1]) / 2f, cz}, {0f, max[1], cz}};
    }

    private ModelPart[] topLevel;
    private boolean[] topIsLeg;

    /** Parts that are not children of another bound part, which is where a model's geometry starts. */
    ModelPart[] topLevel() {
        if (topLevel == null) {
            ModelPart[] top = GroundContact.topLevel(parts);
            boolean[] legs = new boolean[top.length];
            for (int i = 0; i < top.length; i++) {
                ModelPartIndex.Info info = ModelPartIndex.get(top[i]);
                legs[i] = info != null && GroundContact.isLeg(info.name());
            }
            topIsLeg = legs;
            topLevel = top;
        }
        return topLevel;
    }

    boolean[] topIsLeg() {
        topLevel();
        return topIsLeg;
    }

    public ModelPart part(String name) {
        int i = rig.indexOf(name);
        return i < 0 ? null : parts[i];
    }
}

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
    }

    public ModelPart part(String name) {
        int i = rig.indexOf(name);
        return i < 0 ? null : parts[i];
    }
}

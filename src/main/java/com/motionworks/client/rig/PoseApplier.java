package com.motionworks.client.rig;

import com.mojang.blaze3d.vertex.PoseStack;
import com.motionworks.engine.runtime.PoseBuffer;
import net.minecraft.client.model.geom.ModelPart;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Writes an evaluated {@link PoseBuffer} onto model parts after vanilla's setupAnim, then
 * resolves virtual couplings and followers, and applies the virtual root bones to the pose stack.
 */
public final class PoseApplier {
    private static final Quaternionf QA = new Quaternionf();
    private static final Quaternionf QB = new Quaternionf();
    private static final Quaternionf QD = new Quaternionf();
    private static final Vector3f V = new Vector3f();

    private PoseApplier() {}

    public static void apply(ModelRig mr, PoseBuffer pose, float strength) {
        restore(mr);
        ModelPart[] parts = mr.parts;
        float[] van = mr.vanilla;
        for (int b = 2; b < parts.length; b++) {
            ModelPart p = parts[b];
            if (p == null) continue;
            for (int c = 0; c < 9; c++) van[b * 9 + c] = get(p, c);
        }
        float[] rest = mr.rest;
        for (int b = 2; b < parts.length; b++) {
            if (!pose.isTouched(b)) continue;
            ModelPart p = parts[b];
            int o = b * 9;
            p.xRot = mix(van[o], pose.resolve(b, 0, van[o], rest[o]), strength);
            p.yRot = mix(van[o + 1], pose.resolve(b, 1, van[o + 1], rest[o + 1]), strength);
            p.zRot = mix(van[o + 2], pose.resolve(b, 2, van[o + 2], rest[o + 2]), strength);
            p.x = mix(van[o + 3], pose.resolve(b, 3, van[o + 3], rest[o + 3]), strength);
            p.y = mix(van[o + 4], pose.resolve(b, 4, van[o + 4], rest[o + 4]), strength);
            p.z = mix(van[o + 5], pose.resolve(b, 5, van[o + 5], rest[o + 5]), strength);
            p.xScale = Math.max(0.01f, mix(van[o + 6], pose.resolve(b, 6, van[o + 6], 1f), strength));
            p.yScale = Math.max(0.01f, mix(van[o + 7], pose.resolve(b, 7, van[o + 7], 1f), strength));
            p.zScale = Math.max(0.01f, mix(van[o + 8], pose.resolve(b, 8, van[o + 8], 1f), strength));
        }
        for (int c = 0; c < mr.couplings.length; c++) couple(mr, c);
        for (int[] f : mr.followers) parts[f[0]].copyFrom(parts[f[1]]);
        for (int b = 2; b < parts.length; b++) {
            ModelPart p = parts[b];
            if (p == null) continue;
            for (int c = 0; c < 9; c++) mr.written[b * 9 + c] = get(p, c);
        }
        System.arraycopy(van, 0, mr.replaced, 0, van.length);
        mr.hasOutput = true;
    }

    /**
     * Puts back the vanilla value of every channel that still holds what the last apply wrote. Vanilla
     * models only set the fields they animate (HumanoidModel never writes body x/z/zRot or any scale), so
     * without this the previous frame's output would be read back as vanilla and compound frame after
     * frame. Models are shared by every entity of a type, so this also runs for renders MotionWorks does
     * not animate. A channel vanilla rewrote to exactly the value we wrote is indistinguishable and is
     * restored to last frame's vanilla value instead, which is the same value for any steady pose.
     */
    public static void restore(ModelRig mr) {
        if (!mr.hasOutput) return;
        mr.hasOutput = false;
        ModelPart[] parts = mr.parts;
        for (int b = 2; b < parts.length; b++) {
            ModelPart p = parts[b];
            if (p == null) continue;
            for (int c = 0; c < 9; c++) {
                int o = b * 9 + c;
                if (get(p, c) == mr.written[o]) set(p, c, mr.replaced[o]);
            }
        }
    }

    private static float get(ModelPart p, int c) {
        return switch (c) {
            case 0 -> p.xRot;
            case 1 -> p.yRot;
            case 2 -> p.zRot;
            case 3 -> p.x;
            case 4 -> p.y;
            case 5 -> p.z;
            case 6 -> p.xScale;
            case 7 -> p.yScale;
            default -> p.zScale;
        };
    }

    private static void set(ModelPart p, int c, float v) {
        switch (c) {
            case 0 -> p.xRot = v;
            case 1 -> p.yRot = v;
            case 2 -> p.zRot = v;
            case 3 -> p.x = v;
            case 4 -> p.y = v;
            case 5 -> p.z = v;
            case 6 -> p.xScale = v;
            case 7 -> p.yScale = v;
            default -> p.zScale = v;
        }
    }

    private static float mix(float a, float b, float t) {
        return t >= 1f ? b : a + (b - a) * t;
    }

    /** Propagates the parent's animated delta (not vanilla's own motion) to its virtual children. */
    private static void couple(ModelRig mr, int c) {
        int[] entry = mr.couplings[c];
        int parent = entry[0];
        ModelPart p = mr.parts[parent];
        float[] van = mr.vanilla;
        int o = parent * 9;
        float dRx = p.xRot - van[o], dRy = p.yRot - van[o + 1], dRz = p.zRot - van[o + 2];
        float dPx = p.x - van[o + 3], dPy = p.y - van[o + 4], dPz = p.z - van[o + 5];
        boolean rotated = Math.abs(dRx) + Math.abs(dRy) + Math.abs(dRz) > 1e-5f;
        boolean moved = Math.abs(dPx) + Math.abs(dPy) + Math.abs(dPz) > 1e-5f;
        if (!rotated && !moved) return;
        QA.rotationZYX(p.zRot, p.yRot, p.xRot);
        QB.rotationZYX(van[o + 2], van[o + 1], van[o]).conjugate();
        QD.set(QA).mul(QB);
        float[] piv = mr.couplingPivots[c];
        float px = piv != null ? piv[0] : van[o + 3];
        float py = piv != null ? piv[1] : van[o + 4];
        float pz = piv != null ? piv[2] : van[o + 5];
        if (mr.couplingMovesParent[c] && rotated && piv != null) {
            V.set(van[o + 3] - px, van[o + 4] - py, van[o + 5] - pz);
            QD.transform(V);
            p.x = px + V.x + dPx;
            p.y = py + V.y + dPy;
            p.z = pz + V.z + dPz;
        }
        for (int i = 1; i < entry.length; i++) {
            ModelPart ch = mr.parts[entry[i]];
            if (rotated) {
                V.set(ch.x - px, ch.y - py, ch.z - pz);
                QD.transform(V);
                ch.x = px + V.x + dPx;
                ch.y = py + V.y + dPy;
                ch.z = pz + V.z + dPz;
                QA.rotationZYX(ch.zRot, ch.yRot, ch.xRot);
                QB.set(QD).mul(QA);
                QB.getEulerAnglesZYX(V);
                ch.xRot = V.x;
                ch.yRot = V.y;
                ch.zRot = V.z;
            } else {
                ch.x += dPx;
                ch.y += dPy;
                ch.z += dPz;
            }
        }
    }

    /** Applies mw_root (ground pivot) and mw_center (body-centre pivot) to the pose stack. */
    public static void applyRoot(ModelRig mr, PoseBuffer pose, PoseStack stack, float strength) {
        for (int b = 0; b < 2; b++) {
            if (!pose.isTouched(b)) continue;
            float[] pivot = b == 0 ? mr.ground : mr.center;
            float rx = pose.resolve(b, 0, 0f, 0f) * strength;
            float ry = pose.resolve(b, 1, 0f, 0f) * strength;
            float rz = pose.resolve(b, 2, 0f, 0f) * strength;
            float tx = pose.resolve(b, 3, 0f, 0f) * strength / 16f;
            float ty = pose.resolve(b, 4, 0f, 0f) * strength / 16f;
            float tz = pose.resolve(b, 5, 0f, 0f) * strength / 16f;
            float sx = 1f + (pose.resolve(b, 6, 1f, 1f) - 1f) * strength;
            float sy = 1f + (pose.resolve(b, 7, 1f, 1f) - 1f) * strength;
            float sz = 1f + (pose.resolve(b, 8, 1f, 1f) - 1f) * strength;
            stack.translate(tx, ty, tz);
            stack.translate(pivot[0] / 16f, pivot[1] / 16f, pivot[2] / 16f);
            if (rx != 0f || ry != 0f || rz != 0f) stack.mulPose(new Quaternionf().rotationZYX(rz, ry, rx));
            if (sx != 1f || sy != 1f || sz != 1f) stack.scale(sx, sy, sz);
            stack.translate(-pivot[0] / 16f, -pivot[1] / 16f, -pivot[2] / 16f);
        }
    }
}

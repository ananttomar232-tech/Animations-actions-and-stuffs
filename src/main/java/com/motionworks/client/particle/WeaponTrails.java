package com.motionworks.client.particle;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.motionworks.common.ItemCategories;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * Ribbon trails behind swung weapons. Animation events start and stop a trail; the
 * {@link TrailLayer} samples the posed weapon base and tip in world space each frame, and the
 * ribbon is drawn additively after particles, fading with sample age.
 */
public final class WeaponTrails {
    private static final long LIFETIME_MS = 220;

    private record Sample(Vec3 base, Vec3 tip, long time) {}

    private static final class Trail {
        final Deque<Sample> samples = new ArrayDeque<>();
        boolean active;
        float width;
        float r, g, b;
        boolean offhand;
    }

    private static final Map<Integer, Trail> TRAILS = new HashMap<>();
    private static final Matrix4f INV_VIEW = new Matrix4f();

    /** Captures the inverse view rotation for the frame so posed points can be lifted to world space. */
    public static void setViewMatrix(Matrix4f view) {
        INV_VIEW.set(view).invert();
    }

    private WeaponTrails() {}

    public static void start(LivingEntity e, String hand, float width) {
        Trail t = TRAILS.computeIfAbsent(e.getId(), k -> new Trail());
        t.active = true;
        t.width = width;
        t.offhand = "off".equals(hand);
        String cat = ItemCategories.of(t.offhand ? e.getOffhandItem() : e.getMainHandItem());
        switch (cat) {
            case "axe" -> { t.r = 1f; t.g = 0.8f; t.b = 0.55f; }
            case "trident" -> { t.r = 0.5f; t.g = 0.95f; t.b = 1f; }
            case "empty" -> { t.r = 0.9f; t.g = 0.9f; t.b = 0.9f; t.width *= 0.5f; }
            default -> { t.r = 0.82f; t.g = 0.9f; t.b = 1f; }
        }
    }

    public static void stop(LivingEntity e) {
        Trail t = TRAILS.get(e.getId());
        if (t != null) t.active = false;
    }

    public static boolean isActive(LivingEntity e) {
        Trail t = TRAILS.get(e.getId());
        return t != null && t.active;
    }

    public static boolean usesOffhand(LivingEntity e) {
        Trail t = TRAILS.get(e.getId());
        return t != null && t.offhand;
    }

    /** Records a sample from model space (camera-relative pose) into world space. */
    public static void sample(LivingEntity e, Matrix4f pose, Vec3 camera) {
        Trail t = TRAILS.get(e.getId());
        if (t == null || !t.active) return;
        org.joml.Vector4f base = INV_VIEW.transform(pose.transform(new org.joml.Vector4f(0f, 0.55f, -0.15f, 1f)));
        org.joml.Vector4f tip = INV_VIEW.transform(pose.transform(new org.joml.Vector4f(0f, 0.6f, -0.15f - 0.75f * t.width, 1f)));
        t.samples.addLast(new Sample(new Vec3(base.x(), base.y(), base.z()).add(camera), new Vec3(tip.x(), tip.y(), tip.z()).add(camera), Util.getMillis()));
        while (t.samples.size() > 24) t.samples.removeFirst();
    }

    public static void render(PoseStack stack, Vec3 camera) {
        if (TRAILS.isEmpty()) return;
        long now = Util.getMillis();
        MultiBufferSource.BufferSource buffers = Minecraft.getInstance().renderBuffers().bufferSource();
        VertexConsumer vc = buffers.getBuffer(RenderType.lightning());
        Matrix4f m = stack.last().pose();
        Iterator<Map.Entry<Integer, Trail>> it = TRAILS.entrySet().iterator();
        while (it.hasNext()) {
            Trail t = it.next().getValue();
            t.samples.removeIf(s -> now - s.time > LIFETIME_MS);
            if (t.samples.isEmpty()) {
                if (!t.active) it.remove();
                continue;
            }
            Sample prev = null;
            for (Sample s : t.samples) {
                if (prev != null) {
                    float a0 = 1f - (now - prev.time) / (float) LIFETIME_MS;
                    float a1 = 1f - (now - s.time) / (float) LIFETIME_MS;
                    quad(vc, m, camera, prev, s, a0 * 0.45f, a1 * 0.45f, t);
                }
                prev = s;
            }
        }
        buffers.endBatch(RenderType.lightning());
    }

    private static void quad(VertexConsumer vc, Matrix4f m, Vec3 cam, Sample a, Sample b, float aa, float ab, Trail t) {
        vertex(vc, m, a.base.subtract(cam), t, aa * 0.2f);
        vertex(vc, m, a.tip.subtract(cam), t, aa);
        vertex(vc, m, b.tip.subtract(cam), t, ab);
        vertex(vc, m, b.base.subtract(cam), t, ab * 0.2f);
    }

    private static void vertex(VertexConsumer vc, Matrix4f m, Vec3 p, Trail t, float alpha) {
        vc.vertex(m, (float) p.x, (float) p.y, (float) p.z).color(t.r, t.g, t.b, Math.max(0f, alpha)).endVertex();
    }
}

package com.motionworks.client.rig;

import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.Lighting;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexSorting;
import com.mojang.math.Axis;
import com.motionworks.MotionWorks;
import com.motionworks.client.anim.AnimationLibrary;
import com.motionworks.engine.clip.AnimationClip;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.runtime.ClipSampler;
import com.motionworks.engine.runtime.PoseBuffer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Matrix4f;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Renders every clip on the model of the entity that owns it (species clips on their species, shared clips on
 * the first family that plays them) at three moments, into numbered contact sheets plus an index: a way to look
 * at the whole library. Ground contact is applied as at runtime. Run once in a world with
 * {@code -Dmotionworks.gallery=<directory>}.
 */
public final class PoseGallery {
    private static final int CELL = 96, FRAMES = 3, COLS = 5, ROWS = 10;
    private static final float[] TIMES = {0.2f, 0.5f, 0.8f};
    private static boolean done;

    private PoseGallery() {}

    public static void autoRun() {
        String dir = System.getProperty("motionworks.gallery");
        Minecraft mc = Minecraft.getInstance();
        if (done || dir == null || dir.isEmpty() || mc.player == null || mc.player.tickCount < 60) return;
        done = true;
        try {
            int n = render(Path.of(dir));
            MotionWorks.LOGGER.info("MotionWorks gallery: {} clips rendered to {}", n, dir);
        } catch (Exception e) {
            MotionWorks.LOGGER.error("MotionWorks gallery failed", e);
        }
    }

    private record Owner(String entity, AnimationLibrary.EntityFamily family) {}

    static int render(Path dir) throws IOException {
        Minecraft mc = Minecraft.getInstance();
        AnimationLibrary lib = AnimationLibrary.INSTANCE;
        Files.createDirectories(dir);
        // Each clip once, on its own species when it has one, else on the first family that plays it.
        Map<AnimationClip, Owner> owners = new LinkedHashMap<>();
        for (Map.Entry<String, AnimationLibrary.EntityFamily> e : lib.families().entrySet()) {
            for (AnimationClip c : lib.clips().forTargets(e.getValue().targets())) {
                Owner o = new Owner(e.getKey(), e.getValue());
                if (c.target().equals(e.getKey()) || !owners.containsKey(c)) owners.put(c, o);
            }
        }
        TextureTarget target = new TextureTarget(CELL, CELL, true, Minecraft.ON_OSX);
        List<String> index = new ArrayList<>();
        NativeImage sheet = null;
        int n = 0, page = 0;
        Map<String, Prepared> prepared = new LinkedHashMap<>();
        try {
            for (Map.Entry<AnimationClip, Owner> e : owners.entrySet()) {
                Prepared p = prepared.computeIfAbsent(e.getValue().entity(), id -> prepare(id, e.getValue().family()));
                if (p == null) continue;
                int slot = n % (COLS * ROWS);
                if (slot == 0) {
                    if (sheet != null) write(sheet, dir, page++);
                    sheet = new NativeImage(COLS * FRAMES * CELL, ROWS * CELL, true);
                    sheet.fillRect(0, 0, sheet.getWidth(), sheet.getHeight(), 0xFFFFFFFF);
                }
                int x0 = (slot % COLS) * FRAMES * CELL, y0 = (slot / COLS) * CELL;
                for (int f = 0; f < FRAMES; f++) {
                    NativeImage shot = shoot(target, p, e.getKey(), e.getKey().length() * TIMES[f]);
                    copy(shot, sheet, x0 + f * CELL, y0);
                    shot.close();
                }
                Digits.draw(sheet, x0 + 2, y0 + 2, n);
                index.add(n + "\t" + e.getKey().id() + "\t" + e.getValue().entity() + "\tsheet " + page);
                n++;
            }
            if (sheet != null) write(sheet, dir, page);
        } finally {
            if (sheet != null) sheet.close();
            target.destroyBuffers();
            mc.getMainRenderTarget().bindWrite(true);
            for (Prepared p : prepared.values()) if (p != null) p.rest.restore();
        }
        Files.write(dir.resolve("index.tsv"), index);
        return n;
    }

    private record Prepared(LivingEntity entity, EntityModel<?> model, ModelRig rig, ResourceLocation texture, LibraryAudit.Pose rest, float ground,
                            boolean grounded) {}

    @SuppressWarnings({"unchecked", "rawtypes"})
    private static Prepared prepare(String id, AnimationLibrary.EntityFamily family) {
        Minecraft mc = Minecraft.getInstance();
        Entity entity = id.equals("minecraft:player") ? mc.player : create(id);
        if (!(entity instanceof LivingEntity living)) return null;
        EntityRenderer renderer = mc.getEntityRenderDispatcher().getRenderer(entity);
        if (!(renderer instanceof LivingEntityRenderer<?, ?> lr)) return null;
        EntityModel<?> model = lr.getModel();
        ModelRig mr = RigFactory.get(model, AnimationLibrary.INSTANCE.rig(family.rig()));
        LibraryAudit.Pose rest = LibraryAudit.Pose.capture(model, living, mr);
        return new Prepared(living, model, mr, renderer.getTextureLocation(entity), rest, GroundContact.lowest(mr, null, 1f, true),
                LibraryAudit.standsOnGround(living));
    }

    private static Entity create(String id) {
        EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(id));
        return type == null ? null : type.create(Minecraft.getInstance().level);
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    private static NativeImage shoot(TextureTarget target, Prepared p, AnimationClip clip, float t) {
        Minecraft mc = Minecraft.getInstance();
        p.rest.restore();
        PoseBuffer pose = ClipSampler.sampleSolo(p.rig.rig, clip, t, groundedScope());
        PoseApplier.apply(p.rig, pose, 1f);
        float lift = p.grounded && !"free".equals(clip.meta("ground", "")) ? GroundContact.lift(p.rig, pose, 1f, p.ground) : 0f;

        target.setClearColor(0.78f, 0.84f, 0.9f, 1f);
        target.clear(Minecraft.ON_OSX);
        target.bindWrite(true);
        // Frame the model's own rest geometry (a hitbox can sit well away from it, as a bat's does).
        float[] b = p.rig.bounds;
        float centreY = 1.501f - (b[1] + b[4]) / 32f;
        float size = Math.max(p.entity.getBbHeight(), p.entity.getBbWidth());
        float extent = size * 0.62f + 0.12f;
        RenderSystem.backupProjectionMatrix();
        RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(-extent, extent, -extent, extent, -50f, 50f), VertexSorting.ORTHOGRAPHIC_Z);
        PoseStack view = RenderSystem.getModelViewStack();
        view.pushPose();
        view.setIdentity();
        RenderSystem.applyModelViewMatrix();
        PoseStack ps = new PoseStack();
        ps.translate(0f, -centreY, 0f);
        ps.mulPose(Axis.XP.rotationDegrees(12f));
        ps.mulPose(Axis.YP.rotationDegrees(215f));
        ps.scale(-1f, -1f, 1f);
        ps.translate(0f, -1.501f, 0f);
        if (lift > 0f) ps.translate(0f, -lift / 16f, 0f);
        PoseApplier.applyRoot(p.rig, pose, ps, 1f);
        Lighting.setupForEntityInInventory();
        MultiBufferSource.BufferSource buffers = mc.renderBuffers().bufferSource();
        ((EntityModel) p.model).renderToBuffer(ps, buffers.getBuffer(RenderType.entityCutoutNoCull(p.texture)), LightTexture.FULL_BRIGHT,
                OverlayTexture.NO_OVERLAY, 1f, 1f, 1f, 1f);
        buffers.endBatch();
        view.popPose();
        RenderSystem.applyModelViewMatrix();
        RenderSystem.restoreProjectionMatrix();
        Lighting.setupFor3DItems();
        return Screenshot.takeScreenshot(target);
    }

    private static Scope groundedScope() {
        Scope s = new Scope();
        s.setBool(com.motionworks.common.CtxVars.ON_GROUND, true);
        return s;
    }

    private static void copy(NativeImage from, NativeImage to, int x, int y) {
        for (int j = 0; j < Math.min(CELL, from.getHeight()); j++) {
            for (int i = 0; i < Math.min(CELL, from.getWidth()); i++) to.setPixelRGBA(x + i, y + j, from.getPixelRGBA(i, j));
        }
    }

    private static void write(NativeImage sheet, Path dir, int page) throws IOException {
        sheet.writeToFile(dir.resolve(String.format("sheet_%03d.png", page)));
    }

    /** A 3x5 pixel digit font, drawn at double size, for numbering cells. */
    private static final class Digits {
        private static final String[] GLYPHS = {"111101101101111", "010110010010111", "111001111100111", "111001111001111", "101101111001001",
                "111100111001111", "111100111101111", "111001001001001", "111101111101111", "111101111001111"};

        static void draw(NativeImage img, int x, int y, int value) {
            String s = Integer.toString(value);
            img.fillRect(x, y, s.length() * 8 + 2, 12, 0xFFFFFFFF);
            for (int d = 0; d < s.length(); d++) {
                String g = GLYPHS[s.charAt(d) - '0'];
                for (int k = 0; k < 15; k++) {
                    if (g.charAt(k) == '1') img.fillRect(x + 1 + d * 8 + (k % 3) * 2, y + 1 + (k / 3) * 2, 2, 2, 0xFF000000);
                }
            }
        }
    }
}

package com.motionworks.client.face;

import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.anim.EntityAnimator;
import com.motionworks.common.CtxVars;
import com.motionworks.config.MWConfig;
import com.motionworks.engine.expr.Scope;
import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.math.MathUtil;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HeadedModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Optional facial rig drawn as thin overlays on the front of the head. Vanilla models have no
 * facial geometry, so the rig reads the entity's own texture: it finds the eyes (white sclera
 * next to a coloured iris), and paints eyelids, a moving iris, brows and (for players) a mouth
 * using pixels sampled from that same texture, which keeps it consistent with any skin or
 * resource pack. Textures without detectable eyes are left untouched.
 *
 * <p>Expressions blend from context: sleep, pain, fear, anger, happiness, sadness, suspicion,
 * curiosity, concentration, excitement, surprise, discomfort and neutral, plus blinking,
 * gaze toward nearby players and speech mouth movement.
 */
public final class FaceLayer<T extends LivingEntity, M extends EntityModel<T> & HeadedModel> extends RenderLayer<T, M> {
    public enum Kind { PLAYER, VILLAGER, ILLAGER }

    /** Eye geometry in face-pixel coordinates (origin top-left of the front face). */
    record FaceMap(int faceW, int faceH, int u0, int v0, int eyeRow, int leftWhite, int leftIris, int rightIris, int rightWhite, boolean hasBrow) {}

    private static final Map<ResourceLocation, Optional<FaceMap>> MAPS = new HashMap<>();
    private static final Map<Integer, float[]> STATE = new HashMap<>();
    private final Kind kind;

    public FaceLayer(RenderLayerParent<T, M> parent, Kind kind) {
        super(parent);
        this.kind = kind;
    }

    public static Kind kindFor(EntityType<?> type) {
        if (type == EntityType.VILLAGER || type == EntityType.WANDERING_TRADER || type == EntityType.WITCH || type == EntityType.ZOMBIE_VILLAGER) return Kind.VILLAGER;
        if (type == EntityType.PILLAGER || type == EntityType.VINDICATOR || type == EntityType.EVOKER || type == EntityType.ILLUSIONER) return Kind.ILLAGER;
        return null;
    }

    public static void clearCache() {
        MAPS.clear();
    }

    @Override
    @SuppressWarnings("unchecked")
    public void render(PoseStack stack, MultiBufferSource buffers, int light, T entity, float limbSwing, float limbAmount,
                       float partialTicks, float age, float headYaw, float headPitch) {
        if (!enabled() || entity.isInvisible()) return;
        ResourceLocation tex = getTextureLocation(entity);
        Optional<FaceMap> map = MAPS.computeIfAbsent(tex, t -> detect(t, kind));
        if (map.isEmpty()) return;
        FaceMap f = map.get();
        EntityAnimator anim = AnimatorManager.find(entity.getId());
        float[] s = expression(entity, anim == null ? null : anim.scope(), partialTicks);

        ModelPart head = getParentModel().getHead();
        if (!head.visible) return;
        stack.pushPose();
        head.translateAndRotate(stack);
        VertexConsumer vc = buffers.getBuffer(RenderType.entityCutoutNoCull(tex));
        int overlay = LivingEntityRenderer.getOverlayCoords(entity, 0f);
        float halfW = f.faceW / 2f;
        // Front face sits at z = -depth/2 = -4 px; heads are 8 px deep for every supported model.
        float top = kind == Kind.PLAYER ? -8f : -10f;
        float z = -4.003f;
        float lid = s[0], gazeX = s[1], browLift = s[2], browTilt = s[3], mouth = s[4];

        int[][] eyes = {{f.leftWhite, f.leftIris}, {f.rightWhite, f.rightIris}};
        for (int side = 0; side < 2; side++) {
            int white = eyes[side][0], iris = eyes[side][1];
            int x0 = Math.min(white, iris);
            float px0 = x0 - halfW;
            float py0 = top + f.eyeRow;
            // Sclera across both eye pixels, then the iris at its gaze offset.
            quad(vc, stack, px0, py0, px0 + 2, py0 + 1, z, f, white, f.eyeRow, light, overlay);
            float ix = iris - halfW + Mth.clamp(gazeX * (side == 0 ? 1 : 1), -0.6f, 0.6f);
            ix = Mth.clamp(ix, px0, px0 + 1);
            quad(vc, stack, ix, py0, ix + 1, py0 + 1, z - 0.002f, f, iris, f.eyeRow, light, overlay);
            if (lid > 0.02f) {
                // Eyelid painted with the skin pixel just below the eye.
                quad(vc, stack, px0, py0, px0 + 2, py0 + Math.min(1f, lid), z - 0.004f, f, white, Math.min(f.faceH - 1, f.eyeRow + 1), light, overlay);
            }
            if (f.hasBrow && (Math.abs(browLift) > 0.05f || Math.abs(browTilt) > 0.05f)) {
                // Paint skin over the authored brow, then draw it displaced.
                int skinRow = Math.max(0, f.eyeRow - 2);
                quad(vc, stack, px0 - 1, py0 - 1, px0 + 3, py0, z - 0.005f, f, side == 0 ? f.leftWhite : f.rightWhite, skinRow, light, overlay);
                float by = py0 - 1f - browLift;
                float inner = side == 0 ? px0 + 2 : px0;
                float outer = side == 0 ? px0 - 1 : px0 + 3;
                skewedBrow(vc, stack, outer, inner, by, browTilt, z - 0.006f, f, side == 0 ? f.leftWhite : f.rightWhite, light, overlay);
            }
        }
        if (kind == Kind.PLAYER && mouth > 0.05f && f.faceH >= 8) {
            float my = top + 6f;
            quad(vc, stack, -1.5f, my, 1.5f, my + Math.min(1.5f, mouth * 1.5f), z - 0.004f, f, (int) halfW, 7, light, overlay);
        }
        stack.popPose();
    }

    private boolean enabled() {
        return switch (kind) {
            case PLAYER -> MWConfig.CLIENT.playerFaces.get();
            case VILLAGER -> MWConfig.CLIENT.villagerFaces.get();
            case ILLAGER -> MWConfig.CLIENT.illagerFaces.get();
        };
    }

    /**
     * Expression parameters [lid, gazeX, browLift, browTilt, mouth] eased toward targets.
     * Positive brow tilt lowers the inner ends (anger), negative lowers the outer ends (sadness).
     */
    private static float[] expression(LivingEntity e, Scope s, float partial) {
        if (STATE.size() > 512) STATE.clear();
        float[] st = STATE.computeIfAbsent(e.getId(), k -> new float[5]);
        float lid = 0f, browLift = 0f, browTilt = 0f, mouth = 0f;
        float time = (e.tickCount + partial) / 20f;
        long seed = e.getUUID().getLeastSignificantBits();
        if (s != null) {
            boolean asleep = s.get(CtxVars.SLEEPING) != 0f || e.isDeadOrDying();
            float hurt = s.get(CtxVars.RECENT_HURT);
            float mood = s.get(CtxVars.MOOD);
            float nervous = s.get(CtxVars.TRAIT_NERVOUS);
            if (asleep) lid = 1f;
            else if (hurt < 0.5f) { lid = 0.75f; browTilt = 0.6f; }
            else if (s.get(CtxVars.NEAR_HOSTILE) != 0f && nervous > 0.45f) { lid = 0f; browLift = 0.6f; browTilt = -0.2f; }
            else if (s.get(CtxVars.AGGRESSIVE) != 0f || s.get(CtxVars.IN_COMBAT) != 0f) { lid = 0.35f; browTilt = 0.7f; }
            else if (s.get(CtxVars.TRADING) != 0f || s.get(CtxVars.CELEBRATING) != 0f) { lid = 0.3f; browLift = 0.3f; }
            else if (s.get(CtxVars.MINING) != 0f || "bow".equals(useAnimName(s))) { lid = 0.3f; browTilt = 0.25f; }
            else if (mood < -0.4f) { lid = 0.3f; browTilt = -0.6f; }
            else if (s.get(CtxVars.FREEZING) > 0.3f || s.get(CtxVars.ON_FIRE) != 0f) { lid = 0.5f; browTilt = 0.4f; browLift = 0.2f; }
            else if (s.get(CtxVars.INTERESTED) != 0f || s.get(CtxVars.TRAIT_CURIOSITY) > 0.75f && s.get(CtxVars.PLAYER_DISTANCE) < 4f) { browLift = 0.5f; }
            else if (s.get(CtxVars.HEALTH) < 0.3f) { lid = 0.4f; browTilt = -0.3f; }
            if (s.get(CtxVars.SPEAKING) != 0f) mouth = 0.5f + 0.5f * Mth.sin(time * 13f + Mth.sin(time * 5f) * 2f);
            else if ("eat".equals(useAnimName(s)) || "drink".equals(useAnimName(s))) mouth = 0.5f + 0.5f * Mth.sin(time * 16f);
            else if (hurt < 0.25f) mouth = 0.8f;
        }
        // Deterministic blinks every 2-6 s, 0.15 s long; nervous characters blink more.
        float interval = 2f + Hashing.unit(seed) * 4f;
        float phase = (time + Hashing.unit(seed + 1) * interval) % interval;
        if (phase < 0.15f) lid = Math.max(lid, 1f - Math.abs(phase - 0.075f) / 0.075f * 0.3f);
        float gaze = gazeTarget(e, partial) + Hashing.noise1(seed + 2, time * 0.7f) * 0.25f;
        float k = MathUtil.approachFactor(0.06f, 1f / 60f);
        float[] target = {lid, gaze, browLift, browTilt, mouth};
        for (int i = 0; i < 5; i++) st[i] += (target[i] - st[i]) * (i == 0 && target[0] > st[0] ? 0.6f : k);
        return st;
    }

    private static String useAnimName(Scope s) {
        int id = (int) s.get(CtxVars.USE_ANIM);
        if (id == com.motionworks.engine.expr.StringIds.id("bow")) return "bow";
        if (id == com.motionworks.engine.expr.StringIds.id("eat")) return "eat";
        if (id == com.motionworks.engine.expr.StringIds.id("drink")) return "drink";
        return "";
    }

    /** Horizontal iris offset (pixels) toward the nearest player in front of the face. */
    private static float gazeTarget(LivingEntity e, float partial) {
        Player target = e.level().getNearestPlayer(e, 8);
        if (target == null || target == e) return 0f;
        double dx = target.getX() - e.getX(), dz = target.getZ() - e.getZ();
        float yawTo = (float) (Math.toDegrees(Math.atan2(dz, dx)) - 90.0);
        float rel = Mth.wrapDegrees(yawTo - Mth.rotLerp(partial, e.yHeadRotO, e.yHeadRot));
        if (Math.abs(rel) > 80f) return 0f;
        return Mth.clamp(rel / 50f, -1f, 1f) * -0.6f;
    }

    private static void quad(VertexConsumer vc, PoseStack stack, float x0, float y0, float x1, float y1, float z, FaceMap f,
                             int texX, int texY, int light, int overlay) {
        float tw = 64f, th = 64f;
        float u0 = (f.u0 + texX + 0.1f) / tw, u1 = (f.u0 + texX + 0.9f) / tw;
        float v0 = (f.v0 + texY + 0.1f) / th, v1 = (f.v0 + texY + 0.9f) / th;
        PoseStack.Pose pose = stack.last();
        Matrix4f m = pose.pose();
        Matrix3f n = pose.normal();
        float s = 1f / 16f;
        vertex(vc, m, n, x0 * s, y0 * s, z * s, u0, v0, light, overlay);
        vertex(vc, m, n, x0 * s, y1 * s, z * s, u0, v1, light, overlay);
        vertex(vc, m, n, x1 * s, y1 * s, z * s, u1, v1, light, overlay);
        vertex(vc, m, n, x1 * s, y0 * s, z * s, u1, v0, light, overlay);
    }

    private static void skewedBrow(VertexConsumer vc, PoseStack stack, float outer, float inner, float y, float tilt, float z, FaceMap f,
                                   int texX, int light, int overlay) {
        float s = 1f / 16f;
        int browRow = Math.max(0, f.eyeRow - 1);
        float u0 = (f.u0 + texX + 0.1f) / 64f, u1 = (f.u0 + texX + 0.9f) / 64f;
        float v0 = (f.v0 + browRow + 0.1f) / 64f, v1 = (f.v0 + browRow + 0.9f) / 64f;
        float yi = y + tilt * 0.5f, yo = y - tilt * 0.5f;
        PoseStack.Pose pose = stack.last();
        vertex(vc, pose.pose(), pose.normal(), outer * s, yo * s, z * s, u0, v0, light, overlay);
        vertex(vc, pose.pose(), pose.normal(), outer * s, (yo + 1) * s, z * s, u0, v1, light, overlay);
        vertex(vc, pose.pose(), pose.normal(), inner * s, (yi + 1) * s, z * s, u1, v1, light, overlay);
        vertex(vc, pose.pose(), pose.normal(), inner * s, yi * s, z * s, u1, v0, light, overlay);
    }

    private static void vertex(VertexConsumer vc, Matrix4f m, Matrix3f n, float x, float y, float z, float u, float v, int light, int overlay) {
        vc.vertex(m, x, y, z).color(1f, 1f, 1f, 1f).uv(u, v).overlayCoords(overlay == 0 ? OverlayTexture.NO_OVERLAY : overlay)
                .uv2(light).normal(n, 0f, 0f, -1f).endVertex();
    }

    /** Finds sclera/iris pixels on the front face of the head texture. */
    static Optional<FaceMap> detect(ResourceLocation tex, Kind kind) {
        int faceW = 8, faceH = kind == Kind.PLAYER ? 8 : 10;
        // Both the 8x8x8 player head and the 8x10x8 villager/illager head start their front face at (8, 8).
        int u0 = 8, v0 = 8;
        try {
            Optional<Resource> res = Minecraft.getInstance().getResourceManager().getResource(tex);
            NativeImage img;
            if (res.isPresent()) {
                try (InputStream in = res.get().open()) {
                    img = NativeImage.read(in);
                }
            } else {
                return Optional.empty();
            }
            try (img) {
                if (img.getWidth() != 64) return Optional.empty();
                int preferred = kind == Kind.PLAYER ? MWConfig.CLIENT.playerEyeRow.get() : 6;
                for (int pass = 0; pass < 2; pass++) {
                    for (int row = 0; row < faceH; row++) {
                        if (pass == 0 && row != preferred) continue;
                        int lw = -1, rw = -1;
                        for (int x = 0; x < faceW / 2; x++) if (isWhite(img.getPixelRGBA(u0 + x, v0 + row))) lw = x;
                        for (int x = faceW - 1; x >= faceW / 2; x--) if (isWhite(img.getPixelRGBA(u0 + x, v0 + row))) rw = x;
                        if (lw < 0 || rw < 0) continue;
                        int li = lw + 1, ri = rw - 1;
                        if (li >= faceW / 2 || ri < faceW / 2 || isWhite(img.getPixelRGBA(u0 + li, v0 + row)) || isWhite(img.getPixelRGBA(u0 + ri, v0 + row))) continue;
                        boolean brow = row > 0 && luminance(img.getPixelRGBA(u0 + li, v0 + row - 1)) < luminance(img.getPixelRGBA(u0 + li, v0 + Math.min(faceH - 1, row + 1))) * 0.6f;
                        return Optional.of(new FaceMap(faceW, faceH, u0, v0, row, lw, li, ri, rw, brow));
                    }
                }
            }
        } catch (Exception ignored) {
            // Unreadable or dynamic texture: no face rig.
        }
        return Optional.empty();
    }

    private static boolean isWhite(int abgr) {
        int a = (abgr >>> 24) & 255, b = (abgr >> 16) & 255, g = (abgr >> 8) & 255, r = abgr & 255;
        return a > 200 && r > 205 && g > 205 && b > 205;
    }

    private static float luminance(int abgr) {
        int b = (abgr >> 16) & 255, g = (abgr >> 8) & 255, r = abgr & 255;
        return 0.3f * r + 0.59f * g + 0.11f * b;
    }
}

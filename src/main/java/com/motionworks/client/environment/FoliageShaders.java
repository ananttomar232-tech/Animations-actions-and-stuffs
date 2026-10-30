package com.motionworks.client.environment;

import com.motionworks.MotionWorks;
import com.motionworks.config.MWConfig;
import com.mojang.blaze3d.shaders.Uniform;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.client.renderer.block.BlockModelShaper;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.event.ModelEvent;
import net.minecraftforge.client.model.BakedModelWrapper;
import net.minecraftforge.client.model.data.ModelData;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Living foliage without a shader pack.
 *
 * <p>At bake time, the models of plants, leaves, vines, hanging lanterns and water plants are
 * wrapped so their quads carry a sway code in the (otherwise unused) vertex-colour alpha. Forge's
 * block renderer preserves per-vertex alpha, and MotionWorks' {@code rendertype_cutout} vertex
 * shaders decode it and displace vertices with the shared wind field, gusts and nearby
 * moving entities. Untagged geometry is untouched, so doors, rails and torches never wobble.
 *
 * <p>Displacement for leaves, hanging chains and stalks is a pure function of world position,
 * so neighbouring blocks move together without cracks; free-standing plants bend from an
 * anchored base. Tagging is skipped automatically when a shader-pack or alternative chunk
 * renderer is present.
 */
public final class FoliageShaders {
    /** Sway profiles; must match the vertex shaders. */
    static final int PLANT = 0, FIELD = 1, LANTERN = 2, UNDERWATER = 3, FLOATING = 4;

    private static final int PUSHERS = 4;
    private static boolean compatible = true;

    private FoliageShaders() {}

    public static boolean enabled() {
        return compatible && MWConfig.CLIENT.foliageWind.get();
    }

    public static void detectCompatibility() {
        boolean conflict = ModList.get().isLoaded("oculus") || ModList.get().isLoaded("embeddium") || ModList.get().isLoaded("rubidium")
                || ModList.get().isLoaded("sodium");
        try {
            Class.forName("net.optifine.Config", false, FoliageShaders.class.getClassLoader());
            conflict = true;
        } catch (ClassNotFoundException ignored) {
            // no OptiFine
        }
        compatible = !conflict;
        if (conflict) MotionWorks.LOGGER.info("MotionWorks living foliage disabled: shader pack or alternative chunk renderer detected");
    }

    // ------------------------------------------------------------------ bake-time tagging

    public static void onModifyBakingResult(ModelEvent.ModifyBakingResult event) {
        if (!enabled()) return;
        Map<ResourceLocation, BakedModel> models = event.getModels();
        int wrapped = 0;
        for (Block block : ForgeRegistries.BLOCKS) {
            for (BlockState state : block.getStateDefinition().getPossibleStates()) {
                int profile = profile(state);
                if (profile < 0) continue;
                ResourceLocation loc = BlockModelShaper.stateToModelLocation(state);
                BakedModel model = models.get(loc);
                if (model == null || model instanceof SwayModel) continue;
                models.put(loc, new SwayModel(model, profile, amplitude(state, profile), half(state)));
                wrapped++;
            }
        }
        MotionWorks.LOGGER.info("MotionWorks tagged {} block-state models for living foliage", wrapped);
    }

    static int profile(BlockState s) {
        Block b = s.getBlock();
        if (s.is(BlockTags.LEAVES)) return FIELD;
        if (b instanceof LanternBlock) return s.getValue(LanternBlock.HANGING) ? LANTERN : -1;
        if (b instanceof WaterlilyBlock) return FLOATING;
        if (b instanceof SeagrassBlock || b instanceof TallSeagrassBlock || b instanceof KelpBlock || b instanceof KelpPlantBlock) return UNDERWATER;
        if (b instanceof VineBlock || b instanceof WeepingVinesBlock || b instanceof WeepingVinesPlantBlock || b instanceof CaveVinesBlock
                || b instanceof CaveVinesPlantBlock || b instanceof HangingRootsBlock || b instanceof TwistingVinesBlock
                || b instanceof TwistingVinesPlantBlock || b instanceof SporeBlossomBlock) return FIELD;
        if (b instanceof SugarCaneBlock || b instanceof BambooStalkBlock) return FIELD;
        if (b instanceof BushBlock || b instanceof SweetBerryBushBlock) return PLANT;
        return -1;
    }

    static float amplitude(BlockState s, int profile) {
        Block b = s.getBlock();
        if (profile != FIELD) return 1f;
        if (s.is(BlockTags.LEAVES)) return 0.5f;
        if (b instanceof VineBlock) return 0.35f;
        if (b instanceof SugarCaneBlock || b instanceof BambooStalkBlock) return 0.3f;
        return 1f;
    }

    /** 0 for single-block plants, 1 for the lower and 2 for the upper half of double plants. */
    static int half(BlockState s) {
        if (!s.hasProperty(BlockStateProperties.DOUBLE_BLOCK_HALF)) return 0;
        return s.getValue(BlockStateProperties.DOUBLE_BLOCK_HALF) == DoubleBlockHalf.UPPER ? 2 : 1;
    }

    static final class SwayModel extends BakedModelWrapper<BakedModel> {
        private final int profile;
        private final float amplitude;
        private final int half;
        private final Map<BakedQuad, BakedQuad> cache = new ConcurrentHashMap<>();

        SwayModel(BakedModel original, int profile, float amplitude, int half) {
            super(original);
            this.profile = profile;
            this.amplitude = amplitude;
            this.half = half;
        }

        @Override
        public List<BakedQuad> getQuads(BlockState state, Direction side, RandomSource rand) {
            return tag(super.getQuads(state, side, rand));
        }

        @Override
        public List<BakedQuad> getQuads(BlockState state, Direction side, RandomSource rand, ModelData data, RenderType renderType) {
            return tag(super.getQuads(state, side, rand, data, renderType));
        }

        private List<BakedQuad> tag(List<BakedQuad> quads) {
            if (quads.isEmpty()) return quads;
            List<BakedQuad> out = new ArrayList<>(quads.size());
            for (BakedQuad q : quads) out.add(cache.computeIfAbsent(q, this::tagQuad));
            return out;
        }

        private BakedQuad tagQuad(BakedQuad q) {
            int[] data = q.getVertices().clone();
            int stride = data.length / 4;
            for (int v = 0; v < 4; v++) {
                int base = v * stride;
                float y = Float.intBitsToFloat(data[base + 1]);
                float h = Math.max(0f, Math.min(1f, y));
                float weight = switch (profile) {
                    // Double plants bend over their combined two-block height, anchored at the ground.
                    case PLANT -> half == 0 ? h : (half == 1 ? h * 0.5f : 0.5f + h * 0.5f);
                    case LANTERN -> 1f - h;
                    default -> amplitude;
                };
                int code = profile * 32 + Math.round(weight * 31f);
                int alpha = 254 - code;
                int color = data[base + 3];
                data[base + 3] = (color & 0x00FFFFFF) | (alpha << 24);
            }
            return new BakedQuad(data, q.getTintIndex(), q.getDirection(), q.getSprite(), q.isShade(), q.hasAmbientOcclusion());
        }
    }

    // ------------------------------------------------------------------ per-frame uniforms

    public static void updateUniforms(float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;
        boolean on = enabled();
        float strength = on ? WindSystem.strength() : 0f;
        double[] w = WindSystem.vector();
        Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        float time = (float) (((mc.level.getGameTime() % 72000L) + partialTick) / 20.0);
        float[][] pushers = new float[PUSHERS][4];
        if (on) {
            int n = 0;
            for (Entity e : mc.level.entitiesForRendering()) {
                if (n >= PUSHERS) break;
                if (!(e instanceof LivingEntity le) || e.distanceToSqr(cam) > 24 * 24) continue;
                Vec3 v = e.getDeltaMovement();
                if (v.x * v.x + v.z * v.z < 0.0004 && !(le == mc.player)) continue;
                Vec3 p = e.getPosition(partialTick).subtract(cam);
                pushers[n][0] = (float) p.x;
                pushers[n][1] = (float) p.y;
                pushers[n][2] = (float) p.z;
                pushers[n][3] = Math.max(0.8f, e.getBbWidth() * 1.4f);
                n++;
            }
        }
        for (ShaderInstance sh : new ShaderInstance[] {GameRenderer.getRendertypeCutoutShader(), GameRenderer.getRendertypeCutoutMippedShader()}) {
            if (sh == null) continue;
            set4(sh, "MwWind", (float) w[0], (float) w[1], strength, on ? WindSystem.gust() : 0f);
            Uniform t = sh.getUniform("MwTime");
            if (t != null) t.set(time);
            Uniform c = sh.getUniform("MwCam");
            if (c != null) c.set((float) (cam.x % 256.0), (float) cam.y, (float) (cam.z % 256.0));
            for (int i = 0; i < PUSHERS; i++) set4(sh, "MwPush" + i, pushers[i][0], pushers[i][1], pushers[i][2], pushers[i][3]);
        }
    }

    private static void set4(ShaderInstance sh, String name, float a, float b, float c, float d) {
        Uniform u = sh.getUniform(name);
        if (u != null) u.set(a, b, c, d);
    }
}

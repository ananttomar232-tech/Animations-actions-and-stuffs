package com.motionworks.client.environment;

import com.motionworks.client.particle.Effects;
import com.motionworks.config.MWConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FlowerBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * Environmental storytelling around the camera: leaves torn loose by gusts, wind-blown rain and
 * drifting snow, dust motes in still interiors, fireflies over night meadows, pollen over flowers
 * and embers rising from fire. Spawn rates follow the shared wind and weather.
 */
public final class AmbientEffects {
    private static final RandomSource RANDOM = RandomSource.create();

    private AmbientEffects() {}

    public static void tick() {
        Minecraft mc = Minecraft.getInstance();
        ClientLevel level = mc.level;
        if (level == null || mc.player == null || mc.isPaused()) return;
        Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        BlockPos origin = BlockPos.containing(cam);
        float wind = WindSystem.strength();
        double[] w = WindSystem.vector();
        Vec3 windV = new Vec3(w[0], 0, w[1]).scale(0.08);
        if (MWConfig.CLIENT.weatherEffects.get()) {
            // Leaves shed by wind and gusts.
            int leafTries = 2 + Math.round(wind * 6 + WindSystem.gust() * 8);
            for (int i = 0; i < leafTries; i++) {
                BlockPos p = origin.offset(RANDOM.nextInt(25) - 12, RANDOM.nextInt(13) - 4, RANDOM.nextInt(25) - 12);
                BlockState st = level.getBlockState(p);
                if (st.is(BlockTags.LEAVES) && level.getBlockState(p.below()).isAir() && RANDOM.nextFloat() < 0.15f + wind * 0.4f) {
                    Effects.burst("leaf", Vec3.atBottomCenterOf(p).add(0, -0.05, 0), 1, 0.8, 0.02, windV);
                }
            }
            float rain = level.getRainLevel(1f);
            if (rain > 0.2f && level.canSeeSky(origin)) {
                Biome biome = level.getBiome(origin).value();
                boolean snowy = biome.coldEnoughToSnow(origin);
                int n = Math.round(rain * (snowy ? 4 : 6) * (0.5f + wind));
                for (int i = 0; i < n; i++) {
                    double x = cam.x + RANDOM.nextGaussian() * 6, z = cam.z + RANDOM.nextGaussian() * 6;
                    int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, (int) Math.floor(x), (int) Math.floor(z));
                    double y = Math.max(top + 0.2, cam.y + RANDOM.nextDouble() * 4 - 1);
                    if (snowy) Effects.burst("snow_puff", new Vec3(x, Math.min(y, top + 0.6), z), 1, 0.4, 0.01, windV.scale(1.5));
                    else if (wind > 0.35f) Effects.burst("rain_streak", new Vec3(x, y + 3, z), 1, 0.3, 0.0, windV.scale(2.5).add(0, -0.6, 0));
                }
            }
            if (wind > 0.55f && cam.y > 90 && RANDOM.nextFloat() < wind * 0.6f) {
                Effects.burst("wind_streak", cam.add(RANDOM.nextGaussian() * 5, RANDOM.nextGaussian() * 2, RANDOM.nextGaussian() * 5), 1, 0.2, 0, windV.scale(3));
            }
        }
        if (!MWConfig.CLIENT.ambientParticles.get()) return;
        long dayTime = level.getDayTime() % 24000L;
        boolean night = dayTime > 13000 && dayTime < 23000;
        for (int i = 0; i < 4; i++) {
            BlockPos p = origin.offset(RANDOM.nextInt(17) - 8, RANDOM.nextInt(7) - 2, RANDOM.nextInt(17) - 8);
            BlockState st = level.getBlockState(p);
            Vec3 at = Vec3.atCenterOf(p);
            if (st.is(Blocks.LAVA) || st.is(Blocks.FIRE) || st.is(Blocks.CAMPFIRE) || st.is(Blocks.SOUL_FIRE)) {
                if (level.getBlockState(p.above()).isAir() && RANDOM.nextFloat() < 0.5f) Effects.burst("ember", at.add(0, 0.6, 0), 1, 0.4, 0.02, new Vec3(0, 0.05, 0));
            } else if (st.getBlock() instanceof FlowerBlock || st.is(Blocks.TALL_GRASS) || st.is(Blocks.GRASS)) {
                if (night && level.canSeeSky(p) && !level.isRaining() && RANDOM.nextFloat() < 0.18f) Effects.burst("firefly", at.add(0, 0.8, 0), 1, 1.5, 0.01, Vec3.ZERO);
                else if (!night && st.getBlock() instanceof FlowerBlock && RANDOM.nextFloat() < 0.12f) Effects.burst("pollen", at.add(0, 0.5, 0), 1, 0.6, 0.005, windV.scale(0.3));
            } else if (st.isAir() && !level.canSeeSky(p) && level.getMaxLocalRawBrightness(p) >= 9 && RANDOM.nextFloat() < 0.04f) {
                Effects.burst("mote", at, 1, 1.0, 0.002, Vec3.ZERO);
            }
        }
    }

    /** Lingering smoke and falling debris after an explosion seen by this client. */
    public static void explosionAftermath(Vec3 pos, float power) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || !MWConfig.CLIENT.ambientParticles.get()) return;
        Effects.burst("smoke_wisp", pos, Math.round(6 + power * 4), power * 1.2, 0.03, new Vec3(0, 0.03, 0));
        Effects.shockwave(mc.level, pos, Math.min(2f, power / 2f));
        for (int i = 0; i < Math.round(power * 3); i++) {
            BlockPos p = BlockPos.containing(pos.add(RANDOM.nextGaussian() * power, -1, RANDOM.nextGaussian() * power));
            Effects.blockDebris(mc.level, p, Vec3.atCenterOf(p).add(0, 1, 0), 2);
        }
        if (mc.player != null) {
            double d = mc.player.position().distanceTo(pos);
            if (d < power * 8) com.motionworks.client.camera.CameraEffects.addTrauma((float) (0.6 * (1 - d / (power * 8))));
        }
    }
}

package com.motionworks.client.environment;

import com.motionworks.config.MWConfig;
import com.motionworks.engine.math.Hashing;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.BannerBlock;
import net.minecraft.world.level.block.WallBannerBlock;
import net.minecraft.world.level.block.entity.BannerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Wind response of block-entity scenery (banners) rendered by vanilla renderers. */
public final class EnvironmentAnimation {
    private EnvironmentAnimation() {}

    public static void bannerWind(BannerBlockEntity banner, ModelPart flag, float partialTicks) {
        if (!MWConfig.CLIENT.bannerWind.get() || banner.getLevel() == null) return;
        BlockPos pos = banner.getBlockPos();
        BlockState state = banner.getBlockState();
        float facingYaw;
        if (state.getBlock() instanceof WallBannerBlock) facingYaw = state.getValue(WallBannerBlock.FACING).toYRot();
        else if (state.getBlock() instanceof BannerBlock) facingYaw = state.getValue(BannerBlock.ROTATION) * 22.5f;
        else return;
        float sheltered = banner.getLevel().canSeeSky(pos.above()) ? 1f : 0.2f;
        float strength = WindSystem.strength() * sheltered;
        double[] w = WindSystem.vector();
        // Wind across the cloth (perpendicular to its face) lifts it hardest.
        float nx = -Mth.sin(facingYaw * Mth.DEG_TO_RAD), nz = Mth.cos(facingYaw * Mth.DEG_TO_RAD);
        float across = strength <= 0.001f ? 0f : (float) Math.abs((w[0] * nx + w[1] * nz) / strength);
        float push = strength * (0.35f + 0.65f * across);
        double t = (banner.getLevel().getGameTime() + partialTicks) / 20.0 + (Hashing.unit(pos.asLong()) * 10.0);
        float flutter = (float) (Math.sin(t * (2.5 + 7.0 * strength)) * 0.03 * (0.3 + strength)
                + Math.sin(t * 11.3 + 1.7) * 0.012 * strength
                + Math.max(0f, WindSystem.gust()) * 0.05 * Math.sin(t * 17.0));
        float idle = (float) (Math.cos(t * Math.PI * 2 / 5.0) * 0.01);
        flag.xRot = Mth.clamp(-0.015f + idle - push * 0.32f + flutter, -0.42f, 0.02f) * Mth.PI;
    }
}

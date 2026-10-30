package com.motionworks.client.particle;

import com.motionworks.config.MWConfig;
import com.motionworks.registry.MWParticles;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/** High-level effect recipes shared by animation events, combat and the environment. */
public final class Effects {
    private static final RandomSource RANDOM = RandomSource.create();

    private Effects() {}

    public static void burst(String type, Vec3 at, int count, double spread, double speed, Vec3 bias) {
        SimpleParticleType t = MWParticles.get(type);
        if (t == null) return;
        burst(t, at, count, spread, speed, bias);
    }

    public static void burst(ParticleOptions t, Vec3 at, int count, double spread, double speed, Vec3 bias) {
        Level level = Minecraft.getInstance().level;
        if (level == null || count <= 0 || !ParticleBudget.take(count)) return;
        for (int i = 0; i < count; i++) {
            double ox = (RANDOM.nextDouble() - 0.5) * spread;
            double oy = (RANDOM.nextDouble() - 0.5) * spread * 0.5;
            double oz = (RANDOM.nextDouble() - 0.5) * spread;
            double vx = (RANDOM.nextDouble() - 0.5) * speed + bias.x;
            double vy = RANDOM.nextDouble() * speed * 0.6 + bias.y;
            double vz = (RANDOM.nextDouble() - 0.5) * speed + bias.z;
            level.addParticle(t, at.x + ox, at.y + oy, at.z + oz, vx, vy, vz);
        }
    }

    /** Footstep puff matched to the surface. */
    public static void footstep(String surface, Vec3 at, float weight) {
        if (!MWConfig.CLIENT.footstepParticles.get()) return;
        Level level = Minecraft.getInstance().level;
        if (level == null) return;
        int n = Math.max(1, Math.round(2 * weight));
        switch (surface) {
            case "sand", "gravel", "dirt", "soul", "mud" -> burst("dust_puff", at, n, 0.3, 0.03, Vec3.ZERO);
            case "snow" -> burst("snow_puff", at, n + 1, 0.3, 0.04, new Vec3(0, 0.02, 0));
            case "water" -> {
                burst("splash", at, n + 2, 0.25, 0.12, new Vec3(0, 0.12, 0));
                burst("ripple", at.add(0, 0.05, 0), 1, 0.0, 0.0, Vec3.ZERO);
            }
            case "leaves", "grass", "moss" -> {
                if (weight > 1.5f) blockDebris(level, BlockPos.containing(at.x, at.y - 0.1, at.z), at, 2);
            }
            default -> {
                if (weight > 1.5f) burst("dust_puff", at, 1, 0.2, 0.02, Vec3.ZERO);
            }
        }
        if (weight > 1.5f && level.isRainingAt(BlockPos.containing(at))) burst("splash", at, 3, 0.3, 0.1, new Vec3(0, 0.1, 0));
    }

    public static void blockDebris(Level level, BlockPos pos, Vec3 at, int count) {
        BlockState st = level.getBlockState(pos);
        if (st.isAir()) return;
        burst(new BlockParticleOption(ParticleTypes.BLOCK, st), at, count, 0.4, 0.15, new Vec3(0, 0.1, 0));
    }

    /** Weapon impact: sparks on metal/armour, debris otherwise, plus a brief ring. */
    public static void impact(Vec3 at, String material, float strength) {
        if (!MWConfig.CLIENT.impactParticles.get()) return;
        int n = Math.round(4 + 6 * strength);
        if ("metal".equals(material)) burst("spark", at, n, 0.15, 0.35, Vec3.ZERO);
        else burst("dust_puff", at, Math.max(1, n / 3), 0.25, 0.05, Vec3.ZERO);
        if (strength > 0.6f) burst("impact_ring", at, 1, 0, 0, Vec3.ZERO);
    }

    /** Heavy landing or large-creature stomp. */
    public static void shockwave(Level level, Vec3 at, float strength) {
        burst("shockwave", at.add(0, 0.05, 0), 1, 0, 0, Vec3.ZERO);
        burst("dust_puff", at, Math.round(4 + strength * 6), 1.4 * strength, 0.08, Vec3.ZERO);
        blockDebris(level, BlockPos.containing(at.x, at.y - 0.2, at.z), at, Math.round(3 * strength));
    }
}

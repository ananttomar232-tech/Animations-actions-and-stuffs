package com.motionworks.client.environment;

import com.motionworks.config.MWConfig;
import com.motionworks.engine.math.Hashing;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;

/**
 * Global wind model shared by foliage, banners, particles, cloth springs and animation context.
 * It is a pure function of synced world time and weather, so every client sees the same gusts.
 */
public final class WindSystem {
    private static final long SEED = 0x6d77_77696e64L;
    private static float strength;
    private static float gust;
    private static float angle;
    private static final double[] VECTOR = new double[2];

    private WindSystem() {}

    /** Recomputes the wind for the current frame. */
    public static void update(float partialTick) {
        ClientLevel level = Minecraft.getInstance().level;
        if (level == null) {
            strength = 0f;
            return;
        }
        double t = (level.getGameTime() + partialTick) / 20.0;
        float rain = level.getRainLevel(partialTick);
        float thunder = level.getThunderLevel(partialTick);
        float base = 0.22f + rain * 0.3f + thunder * 0.4f;
        float slow = Hashing.noise1(SEED, (float) (t / 45.0)) * 0.5f + 0.5f;
        float g = Hashing.noise1(SEED + 7, (float) (t / 6.0));
        gust = Math.max(0f, g - 0.35f) * (1.4f + thunder);
        strength = (float) ((base * (0.65 + 0.35 * slow) + gust * 0.35f) * MWConfig.CLIENT.windStrength.get());
        angle = Hashing.noise1(SEED + 3, (float) (t / 300.0)) * (float) Math.PI * 1.5f + 0.6f;
        VECTOR[0] = Math.cos(angle) * strength;
        VECTOR[1] = Math.sin(angle) * strength;
    }

    public static float strength() {
        return strength;
    }

    public static float gust() {
        return gust;
    }

    public static float angle() {
        return angle;
    }

    /** World-space horizontal wind vector (x, z) scaled by strength. */
    public static double[] vector() {
        return VECTOR;
    }

    /** Local strength: sheltered spots (no sky access) feel far less wind, heights feel more. */
    public static float strengthAt(Entity e) {
        if (e.level() == null) return strength;
        BlockPos p = e.blockPosition();
        float shelter = e.level().canSeeSky(p.above()) ? 1f : 0.15f;
        float altitude = 1f + Math.max(0f, (p.getY() - 70) / 120f);
        return strength * shelter * Math.min(altitude, 1.8f);
    }
}

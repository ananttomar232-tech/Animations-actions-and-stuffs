package com.motionworks.client.particle;

import com.motionworks.config.MWConfig;
import net.minecraft.Util;

/** Token bucket limiting how many MotionWorks particles may spawn per second. */
public final class ParticleBudget {
    private static float tokens = 100f;
    private static long last = Util.getMillis();

    private ParticleBudget() {}

    public static boolean take(int n) {
        long now = Util.getMillis();
        float rate = MWConfig.CLIENT.maxParticlesPerSecond.get();
        tokens = Math.min(rate, tokens + (now - last) / 1000f * rate);
        last = now;
        if (tokens < n) return false;
        tokens -= n;
        return true;
    }
}

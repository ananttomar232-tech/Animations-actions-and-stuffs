package com.motionworks.client.camera;

import com.motionworks.config.MWConfig;
import com.motionworks.engine.math.Hashing;
import com.motionworks.engine.math.MathUtil;
import net.minecraft.Util;

/**
 * Additive camera motion: trauma-based shake (smooth noise, quadratic falloff), landing dip and
 * damage tilt, each a small spring so motion settles naturally.
 */
public final class CameraEffects {
    private static float trauma;
    private static float dip;
    private static float dipVel;
    private static float tilt;
    private static float tiltVel;
    private static float pitchKick;
    private static float pitchVel;
    private static long lastNanos = Util.getNanos();
    private static float time;
    private static float yaw, pitch, roll, yOffset;

    private CameraEffects() {}

    public static void addTrauma(float amount) {
        if (!MWConfig.CLIENT.cameraEffects.get()) return;
        trauma = MathUtil.clamp01(trauma + amount * MWConfig.CLIENT.cameraShake.get().floatValue());
    }

    /** Downward kick in blocks when landing; springs back. */
    public static void landing(float fall) {
        if (!MWConfig.CLIENT.cameraEffects.get() || !MWConfig.CLIENT.landingDip.get()) return;
        dipVel -= MathUtil.clamp(fall * 0.25f, 0.2f, 3.2f);
        if (fall > 6f) addTrauma(Math.min(0.5f, fall / 30f));
    }

    /** Roll toward the side the hit came from (relative yaw in degrees). */
    public static void hurt(float relativeYaw, float amount) {
        if (!MWConfig.CLIENT.cameraEffects.get() || !MWConfig.CLIENT.damageTilt.get()) return;
        float side = MathUtil.sinDeg(relativeYaw);
        float front = MathUtil.cosDeg(relativeYaw);
        tiltVel += side * MathUtil.clamp(amount * 6f, 8f, 40f);
        pitchVel += front * MathUtil.clamp(amount * 4f, 6f, 25f);
        addTrauma(MathUtil.clamp(amount / 20f, 0.05f, 0.35f));
    }

    /** Small forward pitch kick for weapon impacts felt by the local player. */
    public static void impactKick(float strength) {
        if (!MWConfig.CLIENT.cameraEffects.get()) return;
        pitchVel += 10f * strength;
        addTrauma(0.06f * strength);
    }

    public static void update() {
        long now = Util.getNanos();
        float dt = MathUtil.clamp((now - lastNanos) / 1e9f, 0f, 0.1f);
        lastNanos = now;
        time += dt;
        trauma = Math.max(0f, trauma - dt * 1.1f);
        float shake = trauma * trauma * 6f;
        yaw = Hashing.noise1(11, time * 18f) * shake;
        pitch = Hashing.noise1(23, time * 18f) * shake;
        roll = Hashing.noise1(37, time * 14f) * shake * 0.7f;

        float[] d = spring(dip, dipVel, 90f, 0.75f, dt);
        dip = d[0];
        dipVel = d[1];
        float[] t = spring(tilt, tiltVel, 60f, 0.55f, dt);
        tilt = t[0];
        tiltVel = t[1];
        float[] p = spring(pitchKick, pitchVel, 70f, 0.6f, dt);
        pitchKick = p[0];
        pitchVel = p[1];
        yOffset = dip * 0.08f;
    }

    private static float[] spring(float x, float v, float k, float zeta, float dt) {
        float c = 2f * zeta * (float) Math.sqrt(k);
        int steps = Math.max(1, (int) Math.ceil(dt / 0.008f));
        float h = dt / steps;
        for (int i = 0; i < steps; i++) {
            v += (-k * x - c * v) * h;
            x += v * h;
        }
        return new float[] {x, v};
    }

    public static float yaw() {
        return yaw;
    }

    public static float pitch() {
        return pitch + pitchKick * 0.1f;
    }

    public static float roll() {
        return roll + tilt * 0.1f;
    }

    public static float yOffset() {
        return yOffset;
    }
}

package com.motionworks.client.particle;

import com.motionworks.client.environment.WindSystem;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.util.Mth;

/** Data-driven sprite particle; all behaviour comes from its {@link ParticlePresets.Preset}. */
public final class MWParticle extends TextureSheetParticle {
    private final ParticlePresets.Preset preset;
    private final SpriteSet sprites;
    private final float baseSize;
    private final float spin;

    MWParticle(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, ParticlePresets.Preset p, SpriteSet sprites) {
        super(level, x, y, z, 0, 0, 0);
        this.preset = p;
        this.sprites = sprites;
        this.xd = vx;
        this.yd = vy;
        this.zd = vz;
        this.gravity = p.gravity();
        this.friction = p.friction();
        this.hasPhysics = p.collide();
        this.lifetime = (int) (p.life() * (0.75f + random.nextFloat() * 0.5f));
        this.baseSize = p.size() * (0.8f + random.nextFloat() * 0.4f);
        this.quadSize = baseSize;
        this.spin = (random.nextFloat() - 0.5f) * p.spin();
        this.roll = random.nextFloat() * Mth.TWO_PI * (p.spin() > 0f ? 1f : 0f);
        this.oRoll = roll;
        float[] c = p.color();
        float jitter = 1f - random.nextFloat() * p.colorJitter();
        setColor(c[0] * jitter, c[1] * jitter, c[2] * jitter);
        setAlpha(c[3]);
        if (p.animated()) setSpriteFromAge(sprites);
        else pickSprite(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        if (removed) return;
        if (preset.animated()) setSpriteFromAge(sprites);
        float life = age / (float) Math.max(1, lifetime);
        this.oRoll = roll;
        this.roll += spin;
        this.quadSize = baseSize * (preset.grow() >= 0f ? 1f + preset.grow() * life : 1f + preset.grow() * life);
        float fadeIn = Math.min(1f, life * 6f);
        float fadeOut = 1f - Math.max(0f, (life - preset.fadeStart()) / Math.max(0.01f, 1f - preset.fadeStart()));
        setAlpha(preset.color()[3] * fadeIn * fadeOut);
        if (preset.wind() > 0f) {
            double[] w = WindSystem.vector();
            xd += w[0] * preset.wind() * 0.01;
            zd += w[1] * preset.wind() * 0.01;
        }
        if (preset.flutter() > 0f) {
            xd += Mth.sin((float) ((age + x) * 0.4)) * preset.flutter() * 0.004;
            zd += Mth.cos((float) ((age + z) * 0.37)) * preset.flutter() * 0.004;
        }
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
    }

    @Override
    protected int getLightColor(float partialTick) {
        if (preset.emissive()) return 0xF000F0;
        return super.getLightColor(partialTick);
    }

    public record Provider(ParticlePresets.Preset preset, SpriteSet sprites) implements net.minecraft.client.particle.ParticleProvider<net.minecraft.core.particles.SimpleParticleType> {
        @Override
        public net.minecraft.client.particle.Particle createParticle(net.minecraft.core.particles.SimpleParticleType type, ClientLevel level,
                                                                      double x, double y, double z, double vx, double vy, double vz) {
            return new MWParticle(level, x, y, z, vx, vy, vz, preset, sprites);
        }
    }
}

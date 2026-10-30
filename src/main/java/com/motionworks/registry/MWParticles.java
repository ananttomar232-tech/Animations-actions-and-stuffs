package com.motionworks.registry;

import com.motionworks.MotionWorks;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.LinkedHashMap;
import java.util.Map;

public final class MWParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, MotionWorks.MOD_ID);
    public static final Map<String, RegistryObject<SimpleParticleType>> BY_NAME = new LinkedHashMap<>();

    /** Particle names; each has a behaviour preset in ParticlePresets and sprites in textures/particle. */
    public static final String[] NAMES = {
            "spark", "dust_puff", "snow_puff", "splash", "ripple", "ember", "leaf", "wind_streak", "impact_ring",
            "smoke_wisp", "magic_glint", "firefly", "pollen", "rain_streak", "mote", "shockwave", "breath", "bubble_trail"
    };

    static {
        for (String n : NAMES) BY_NAME.put(n, PARTICLES.register(n, () -> new SimpleParticleType(false)));
    }

    private MWParticles() {}

    public static void register(IEventBus bus) {
        PARTICLES.register(bus);
    }

    public static SimpleParticleType get(String name) {
        RegistryObject<SimpleParticleType> r = BY_NAME.get(name);
        return r != null && r.isPresent() ? r.get() : null;
    }
}

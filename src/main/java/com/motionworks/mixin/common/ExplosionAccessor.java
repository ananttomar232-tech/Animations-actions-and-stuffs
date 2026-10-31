package com.motionworks.mixin.common;

import net.minecraft.world.level.Explosion;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Explosion keeps its power private in 1.20.1; the aftermath effects scale with it. */
@Mixin(Explosion.class)
public interface ExplosionAccessor {
    @Accessor("radius")
    float motionworks$radius();
}

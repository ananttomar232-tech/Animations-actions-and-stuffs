package com.motionworks.mixin.client;

import com.motionworks.client.anim.DamageReactions;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Client-side damage events carry the damage type and source, enough for directional reactions. */
@Mixin(LivingEntity.class)
public abstract class LivingEntityClientMixin {
    @Inject(method = "handleDamageEvent", at = @At("HEAD"))
    private void motionworks$damage(DamageSource source, CallbackInfo ci) {
        LivingEntity self = (LivingEntity) (Object) this;
        if (self.level().isClientSide) DamageReactions.onDamage(self, source);
    }
}

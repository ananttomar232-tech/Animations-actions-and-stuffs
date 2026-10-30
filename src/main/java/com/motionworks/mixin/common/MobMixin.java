package com.motionworks.mixin.common;

import com.motionworks.server.ServerTriggers;
import net.minecraft.world.entity.Mob;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Ambient sounds only play on the server; this turns each one into a "vocalize" animation event. */
@Mixin(Mob.class)
public abstract class MobMixin {
    @Inject(method = "playAmbientSound", at = @At("HEAD"))
    private void motionworks$vocalize(CallbackInfo ci) {
        ServerTriggers.onAmbientSound((Mob) (Object) this);
    }
}

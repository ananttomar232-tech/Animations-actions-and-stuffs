package com.motionworks.mixin.client;

import com.motionworks.client.anim.MiningTracker;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Vanilla tells every client who is breaking which block; that drives remote mining animation. */
@Mixin(LevelRenderer.class)
public abstract class LevelRendererMixin {
    @Inject(method = "destroyBlockProgress", at = @At("HEAD"))
    private void motionworks$progress(int breakerId, BlockPos pos, int progress, CallbackInfo ci) {
        MiningTracker.onProgress(breakerId, pos, progress);
    }
}

package com.motionworks.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.motionworks.client.anim.AnimatorManager;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EnderDragonRenderer;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * The dragon model recomputes its parts inside renderToBuffer, so only whole-body (root and
 * centre) motion can be layered on; that is applied to the pose stack here.
 */
@Mixin(EnderDragonRenderer.class)
public abstract class EnderDragonRendererMixin {
    @Shadow
    @Final
    private EnderDragonRenderer.DragonModel model;

    @Inject(method = "render(Lnet/minecraft/world/entity/boss/enderdragon/EnderDragon;FFLcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;I)V",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/client/renderer/entity/EnderDragonRenderer$DragonModel;prepareMobModel(Lnet/minecraft/world/entity/boss/enderdragon/EnderDragon;FFF)V", shift = At.Shift.AFTER))
    private void motionworks$applyRoot(EnderDragon dragon, float yaw, float partialTicks, PoseStack stack, MultiBufferSource buffers, int light, CallbackInfo ci) {
        AnimatorManager.apply(dragon, this.model, partialTicks, stack);
    }
}

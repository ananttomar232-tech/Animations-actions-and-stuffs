package com.motionworks.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.motionworks.client.anim.AnimatorManager;
import com.motionworks.client.rig.RenderHealth;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * The single integration point for entity animation: right after vanilla's setupAnim has posed
 * the model, MotionWorks layers its evaluated pose on top. Armour, held items, capes and other
 * layers render afterwards and therefore follow the animated parts.
 */
@Mixin(LivingEntityRenderer.class)
public abstract class LivingEntityRendererMixin<T extends LivingEntity, M extends EntityModel<T>> {
    @Shadow
    protected M model;

    @Inject(method = "render(Lnet/minecraft/world/entity/LivingEntity;FFLcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;I)V",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/client/model/EntityModel;setupAnim(Lnet/minecraft/world/entity/Entity;FFFFF)V", shift = At.Shift.AFTER))
    private void motionworks$applyAnimation(T entity, float yaw, float partialTicks, PoseStack stack, MultiBufferSource buffers, int light, CallbackInfo ci) {
        AnimatorManager.apply(entity, this.model, partialTicks, stack);
    }

    // Diagnostics (RenderHealth): did another mod change the pose between the hook and the draw, or during it?
    // Optional, so a mod that rewrites this call cannot stop the game from starting.
    @Inject(method = "render(Lnet/minecraft/world/entity/LivingEntity;FFLcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;I)V",
            at = @At(value = "INVOKE", target = RENDER_TO_BUFFER), require = 0)
    private void motionworks$beforeDraw(T entity, float yaw, float partialTicks, PoseStack stack, MultiBufferSource buffers, int light, CallbackInfo ci) {
        RenderHealth.beforeDraw(entity, this.model);
    }

    @Inject(method = "render(Lnet/minecraft/world/entity/LivingEntity;FFLcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;I)V",
            at = @At(value = "INVOKE", target = RENDER_TO_BUFFER, shift = At.Shift.AFTER), require = 0)
    private void motionworks$afterDraw(T entity, float yaw, float partialTicks, PoseStack stack, MultiBufferSource buffers, int light, CallbackInfo ci) {
        RenderHealth.afterDraw(entity, this.model);
    }

    private static final String RENDER_TO_BUFFER =
            "Lnet/minecraft/client/model/EntityModel;renderToBuffer(Lcom/mojang/blaze3d/vertex/PoseStack;Lcom/mojang/blaze3d/vertex/VertexConsumer;IIFFFF)V";
}

package com.motionworks.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.motionworks.client.firstperson.FirstPersonAnimator;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Wraps first-person hand and item rendering with the first-person animator's transforms. */
@Mixin(ItemInHandRenderer.class)
public abstract class ItemInHandRendererMixin {
    @Inject(method = "renderHandsWithItems", at = @At("HEAD"))
    private void motionworks$frame(float partialTicks, PoseStack stack, MultiBufferSource.BufferSource buffers, net.minecraft.client.player.LocalPlayer player, int light, CallbackInfo ci) {
        FirstPersonAnimator.INSTANCE.frame(0f);
    }

    @Inject(method = "renderArmWithItem", at = @At("HEAD"))
    private void motionworks$pushHand(AbstractClientPlayer player, float partialTicks, float pitch, InteractionHand hand, float swing, ItemStack stack,
                                      float equip, PoseStack pose, MultiBufferSource buffers, int light, CallbackInfo ci) {
        pose.pushPose();
        boolean main = hand == InteractionHand.MAIN_HAND;
        HumanoidArm side = main ? player.getMainArm() : player.getMainArm().getOpposite();
        FirstPersonAnimator.INSTANCE.applyHand(main, side, pose);
        FirstPersonAnimator.INSTANCE.setRenderingFirstPersonItem(true);
    }

    @Inject(method = "renderArmWithItem", at = @At("RETURN"))
    private void motionworks$popHand(AbstractClientPlayer player, float partialTicks, float pitch, InteractionHand hand, float swing, ItemStack stack,
                                     float equip, PoseStack pose, MultiBufferSource buffers, int light, CallbackInfo ci) {
        FirstPersonAnimator.INSTANCE.setRenderingFirstPersonItem(false);
        pose.popPose();
    }

    @Inject(method = "renderItem", at = @At("HEAD"))
    private void motionworks$pushItem(LivingEntity entity, ItemStack stack, ItemDisplayContext ctx, boolean leftHand, PoseStack pose,
                                      MultiBufferSource buffers, int light, CallbackInfo ci) {
        if (!ctx.firstPerson() || !FirstPersonAnimator.INSTANCE.isRenderingFirstPersonItem()) return;
        pose.pushPose();
        HumanoidArm side = leftHand ? HumanoidArm.LEFT : HumanoidArm.RIGHT;
        boolean main = entity.getMainArm() == side;
        FirstPersonAnimator.INSTANCE.applyItem(main, side, pose);
    }

    @Inject(method = "renderItem", at = @At("RETURN"))
    private void motionworks$popItem(LivingEntity entity, ItemStack stack, ItemDisplayContext ctx, boolean leftHand, PoseStack pose,
                                     MultiBufferSource buffers, int light, CallbackInfo ci) {
        if (!ctx.firstPerson() || !FirstPersonAnimator.INSTANCE.isRenderingFirstPersonItem()) return;
        pose.popPose();
    }

    /** Authored first-person attacks replace vanilla's generic swing instead of stacking on it. */
    @Redirect(method = "renderArmWithItem", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/renderer/ItemInHandRenderer;applyItemArmAttackTransform(Lcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/world/entity/HumanoidArm;F)V"))
    private void motionworks$maybeSkipVanillaSwing(ItemInHandRenderer self, PoseStack pose, HumanoidArm arm, float swing) {
        if (FirstPersonAnimator.INSTANCE.overridesVanillaSwing()) return;
        ((ItemInHandRendererInvoker) self).motionworks$applyItemArmAttackTransform(pose, arm, swing);
    }
}

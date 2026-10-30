package com.motionworks.client.particle;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;

/** Samples the animated hand transform for {@link WeaponTrails}; draws nothing itself. */
public final class TrailLayer<T extends LivingEntity, M extends EntityModel<T> & ArmedModel> extends RenderLayer<T, M> {
    public TrailLayer(RenderLayerParent<T, M> parent) {
        super(parent);
    }

    @Override
    public void render(PoseStack stack, MultiBufferSource buffers, int light, T entity, float limbSwing, float limbAmount,
                       float partialTicks, float age, float headYaw, float headPitch) {
        if (!WeaponTrails.isActive(entity)) return;
        boolean off = WeaponTrails.usesOffhand(entity);
        HumanoidArm arm = off ? entity.getMainArm().getOpposite() : entity.getMainArm();
        stack.pushPose();
        getParentModel().translateToHand(arm, stack);
        WeaponTrails.sample(entity, stack.last().pose(), Minecraft.getInstance().gameRenderer.getMainCamera().getPosition());
        stack.popPose();
    }
}

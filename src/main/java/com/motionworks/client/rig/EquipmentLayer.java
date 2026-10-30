package com.motionworks.client.rig;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.motionworks.client.particle.WeaponTrails;
import com.motionworks.config.MWConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

/**
 * Shows stowed equipment on the body: the best unheld weapon on the back or hip, a shield on the
 * back and a quiver when the player carries arrows for a bow. Stowed items ride on the animated
 * body part so they move with every lean, roll and stride. Remote players' loadouts come from the
 * server via {@link StowedEquipment}.
 */
public final class EquipmentLayer extends RenderLayer<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> {
    public EquipmentLayer(RenderLayerParent<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> parent) {
        super(parent);
    }

    @Override
    public void render(PoseStack stack, MultiBufferSource buffers, int light, AbstractClientPlayer player, float limbSwing, float limbAmount,
                       float partialTicks, float age, float headYaw, float headPitch) {
        if (!MWConfig.CLIENT.equipmentDisplay.get() || player.isInvisible() || player.isSleeping()) return;
        com.motionworks.common.Loadouts.Loadout l = StowedEquipment.of(player);
        if (l == null) return;
        var body = getParentModel().body;
        var renderer = Minecraft.getInstance().getItemRenderer();
        boolean chestArmor = !player.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.CHEST).isEmpty();
        float depth = chestArmor ? 0.19f : 0.155f;
        if (!l.back().isEmpty()) {
            stack.pushPose();
            body.translateAndRotate(stack);
            boolean blade = l.backIsBlade();
            stack.translate(0f, blade ? 0.32f : 0.3f, depth);
            stack.mulPose(Axis.ZP.rotationDegrees(blade ? 135f : 45f));
            stack.mulPose(Axis.YP.rotationDegrees(180f));
            stack.scale(0.8f, 0.8f, 0.8f);
            renderer.renderStatic(player, l.back(), ItemDisplayContext.FIXED, false, stack, buffers, player.level(), light, OverlayTexture.NO_OVERLAY, player.getId());
            stack.popPose();
        }
        if (!l.hip().isEmpty() && !WeaponTrails.isActive(player)) {
            stack.pushPose();
            body.translateAndRotate(stack);
            stack.translate(-0.27f, 0.68f, 0.02f);
            stack.mulPose(Axis.YP.rotationDegrees(90f));
            stack.mulPose(Axis.ZP.rotationDegrees(-110f));
            stack.scale(0.55f, 0.55f, 0.55f);
            renderer.renderStatic(player, l.hip(), ItemDisplayContext.FIXED, false, stack, buffers, player.level(), light, OverlayTexture.NO_OVERLAY, player.getId() + 1);
            stack.popPose();
        }
        if (l.shield()) {
            stack.pushPose();
            body.translateAndRotate(stack);
            stack.translate(0f, 0.35f, depth + 0.07f);
            stack.mulPose(Axis.YP.rotationDegrees(180f));
            stack.scale(0.65f, 0.65f, 0.65f);
            renderer.renderStatic(player, new ItemStack(net.minecraft.world.item.Items.SHIELD), ItemDisplayContext.FIXED, false, stack, buffers, player.level(), light, OverlayTexture.NO_OVERLAY, player.getId() + 2);
            stack.popPose();
        }
        if (l.quiver()) {
            stack.pushPose();
            body.translateAndRotate(stack);
            stack.translate(0.18f, 0.25f, depth);
            stack.mulPose(Axis.ZP.rotationDegrees(-20f));
            stack.scale(0.6f, 0.6f, 0.6f);
            renderer.renderStatic(player, new ItemStack(net.minecraft.world.item.Items.ARROW), ItemDisplayContext.FIXED, false, stack, buffers, player.level(), light, OverlayTexture.NO_OVERLAY, player.getId() + 3);
            stack.translate(0.06f, 0.06f, 0.02f);
            renderer.renderStatic(player, new ItemStack(net.minecraft.world.item.Items.ARROW), ItemDisplayContext.FIXED, false, stack, buffers, player.level(), light, OverlayTexture.NO_OVERLAY, player.getId() + 4);
            stack.popPose();
        }
    }
}

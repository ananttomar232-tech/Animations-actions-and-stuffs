package com.motionworks.mixin.client;

import com.motionworks.client.anim.AnimatorManager;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.network.protocol.game.ClientboundEntityEventPacket;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Exposes vanilla entity events (golem/ravager/hoglin attacks, sheep grazing, wolf shaking,
 * taming hearts...) to animations as {@code entity_event_<id>}.
 */
@Mixin(ClientPacketListener.class)
public abstract class ClientPacketListenerMixin {
    @Inject(method = "handleEntityEvent", at = @At("TAIL"))
    private void motionworks$entityEvent(ClientboundEntityEventPacket packet, CallbackInfo ci) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || !mc.isSameThread()) return;
        Entity e = packet.getEntity(mc.level);
        if (e != null) AnimatorManager.fire(e.getId(), "entity_event_" + packet.getEventId(), "", 0f);
    }
}

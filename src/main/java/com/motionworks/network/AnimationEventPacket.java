package com.motionworks.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Server-detected gameplay event for an entity (interaction, combat, emote...). */
public record AnimationEventPacket(int entityId, String event, String arg, float dir, float height) {
    public AnimationEventPacket(int entityId, String event, String arg, float dir) {
        this(entityId, event, arg, dir, 0f);
    }

    public static void encode(AnimationEventPacket p, FriendlyByteBuf buf) {
        buf.writeVarInt(p.entityId);
        buf.writeUtf(p.event, 96);
        buf.writeUtf(p.arg, 128);
        buf.writeFloat(p.dir);
        buf.writeFloat(p.height);
    }

    public static AnimationEventPacket decode(FriendlyByteBuf buf) {
        return new AnimationEventPacket(buf.readVarInt(), buf.readUtf(96), buf.readUtf(128), buf.readFloat(), buf.readFloat());
    }

    public static void handle(AnimationEventPacket p, Supplier<NetworkEvent.Context> ctx) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.motionworks.client.ClientPacketHandlers.animationEvent(p));
        ctx.get().setPacketHandled(true);
    }
}

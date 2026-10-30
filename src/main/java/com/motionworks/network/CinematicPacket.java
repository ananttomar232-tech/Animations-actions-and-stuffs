package com.motionworks.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Asks a client to play (or stop, when id is empty) a cinematic anchored on an entity. */
public record CinematicPacket(String id, int anchorId) {
    public static void encode(CinematicPacket p, FriendlyByteBuf buf) {
        buf.writeUtf(p.id, 128);
        buf.writeVarInt(p.anchorId);
    }

    public static CinematicPacket decode(FriendlyByteBuf buf) {
        return new CinematicPacket(buf.readUtf(128), buf.readVarInt());
    }

    public static void handle(CinematicPacket p, Supplier<NetworkEvent.Context> ctx) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.motionworks.client.ClientPacketHandlers.cinematic(p));
        ctx.get().setPacketHandled(true);
    }
}

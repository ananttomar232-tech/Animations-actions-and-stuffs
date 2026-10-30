package com.motionworks.network;

import com.motionworks.server.CombatMechanics;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Dodge (with input direction) or shield bash requested by a client; resolved on the server. */
public record CombatActionPacket(Action action, float forward, float strafe) {
    public enum Action { DODGE, BASH }

    public static void encode(CombatActionPacket p, FriendlyByteBuf buf) {
        buf.writeEnum(p.action);
        buf.writeFloat(p.forward);
        buf.writeFloat(p.strafe);
    }

    public static CombatActionPacket decode(FriendlyByteBuf buf) {
        return new CombatActionPacket(buf.readEnum(Action.class), buf.readFloat(), buf.readFloat());
    }

    public static void handle(CombatActionPacket p, Supplier<NetworkEvent.Context> ctx) {
        ServerPlayer sender = ctx.get().getSender();
        ctx.get().setPacketHandled(true);
        if (sender == null) return;
        float f = Float.isFinite(p.forward) ? Math.max(-1f, Math.min(1f, p.forward)) : 0f;
        float s = Float.isFinite(p.strafe) ? Math.max(-1f, Math.min(1f, p.strafe)) : 0f;
        switch (p.action) {
            case DODGE -> CombatMechanics.dodge(sender, f, s);
            case BASH -> CombatMechanics.bash(sender);
        }
    }
}

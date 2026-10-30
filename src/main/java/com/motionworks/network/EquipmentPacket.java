package com.motionworks.network;

import com.motionworks.common.Loadouts;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** A remote player's stowed equipment (hotbar is not otherwise visible to other clients). */
public record EquipmentPacket(int entityId, Loadouts.Loadout loadout) {
    public static void encode(EquipmentPacket p, FriendlyByteBuf buf) {
        buf.writeVarInt(p.entityId);
        p.loadout.write(buf);
    }

    public static EquipmentPacket decode(FriendlyByteBuf buf) {
        return new EquipmentPacket(buf.readVarInt(), Loadouts.Loadout.read(buf));
    }

    public static void handle(EquipmentPacket p, Supplier<NetworkEvent.Context> ctx) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> com.motionworks.client.rig.StowedEquipment.setRemote(p.entityId(), p.loadout()));
        ctx.get().setPacketHandled(true);
    }
}

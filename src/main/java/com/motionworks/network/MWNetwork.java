package com.motionworks.network;

import com.motionworks.MotionWorks;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

/**
 * Network channel. Both sides accept a missing remote, so the mod also works client-only (local
 * detection) and server-only (vanilla clients are simply never sent MotionWorks packets).
 */
public final class MWNetwork {
    public static final String VERSION = "1";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(MotionWorks.MOD_ID, "main"), () -> VERSION,
            NetworkRegistry.acceptMissingOr(VERSION), NetworkRegistry.acceptMissingOr(VERSION));

    private MWNetwork() {}

    public static void register() {
        int id = 0;
        CHANNEL.messageBuilder(AnimationEventPacket.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(AnimationEventPacket::encode).decoder(AnimationEventPacket::decode)
                .consumerMainThread(AnimationEventPacket::handle).add();
        CHANNEL.messageBuilder(CinematicPacket.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(CinematicPacket::encode).decoder(CinematicPacket::decode)
                .consumerMainThread(CinematicPacket::handle).add();
        CHANNEL.messageBuilder(EmotePacket.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(EmotePacket::encode).decoder(EmotePacket::decode)
                .consumerMainThread(EmotePacket::handle).add();
        CHANNEL.messageBuilder(EquipmentPacket.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(EquipmentPacket::encode).decoder(EquipmentPacket::decode)
                .consumerMainThread(EquipmentPacket::handle).add();
        CHANNEL.messageBuilder(CombatActionPacket.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(CombatActionPacket::encode).decoder(CombatActionPacket::decode)
                .consumerMainThread(CombatActionPacket::handle).add();
    }

    /** Sends to every tracking player that has MotionWorks installed (optionally including the entity itself). */
    public static void toTrackers(Entity entity, Object msg, boolean includeSelf) {
        if (entity.level().isClientSide || entity.level().getServer() == null) return;
        for (ServerPlayer p : entity.level().getServer().getPlayerList().getPlayers()) {
            if (p.level() != entity.level()) continue;
            boolean self = p == entity;
            if (self && !includeSelf) continue;
            if (!self && p.distanceToSqr(entity) > 96 * 96) continue;
            if (!CHANNEL.isRemotePresent(p.connection.connection)) continue;
            CHANNEL.send(PacketDistributor.PLAYER.with(() -> p), msg);
        }
    }

    public static void toPlayer(ServerPlayer p, Object msg) {
        if (CHANNEL.isRemotePresent(p.connection.connection)) CHANNEL.send(PacketDistributor.PLAYER.with(() -> p), msg);
    }
}

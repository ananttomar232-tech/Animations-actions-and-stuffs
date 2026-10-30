package com.motionworks.network;

import com.motionworks.config.MWConfig;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/** A player requests an emote clip; the server rate-limits and relays it to nearby players. */
public record EmotePacket(String clipId) {
    private static final Map<UUID, Long> LAST = new ConcurrentHashMap<>();
    /** Purely cosmetic client actions other players may see. */
    private static final java.util.Set<String> RELAYED_EVENTS = java.util.Set.of("inspect", "draw_weapon", "sheathe_weapon");

    public static void encode(EmotePacket p, FriendlyByteBuf buf) {
        buf.writeUtf(p.clipId, 128);
    }

    public static EmotePacket decode(FriendlyByteBuf buf) {
        return new EmotePacket(buf.readUtf(128));
    }

    public static void handle(EmotePacket p, Supplier<NetworkEvent.Context> ctx) {
        ServerPlayer sender = ctx.get().getSender();
        ctx.get().setPacketHandled(true);
        if (sender == null || !MWConfig.SERVER.emotes.get()) return;
        if (!p.clipId.matches("[a-z0-9_.:\\-]{1,96}")) return;
        long now = sender.level().getGameTime();
        Long last = LAST.get(sender.getUUID());
        if (last != null && now - last < 10) return;
        LAST.put(sender.getUUID(), now);
        if (p.clipId.startsWith("event:")) {
            String event = p.clipId.substring(6);
            if (RELAYED_EVENTS.contains(event)) MWNetwork.toTrackers(sender, new AnimationEventPacket(sender.getId(), event, "", 0f), false);
            return;
        }
        MWNetwork.toTrackers(sender, new AnimationEventPacket(sender.getId(), "play_clip", p.clipId, 0f), false);
    }
}

package com.motionworks.server;

import com.motionworks.MotionWorks;
import com.motionworks.common.Loadouts;
import com.motionworks.network.EquipmentPacket;
import com.motionworks.network.MWNetwork;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/** Sends stowed-equipment changes to players who can see them. */
@Mod.EventBusSubscriber(modid = MotionWorks.MOD_ID)
public final class EquipmentSync {
    private static final Map<UUID, Integer> LAST = new ConcurrentHashMap<>();

    private EquipmentSync() {}

    @SubscribeEvent
    public static void onTick(TickEvent.PlayerTickEvent e) {
        if (e.phase != TickEvent.Phase.END || !(e.player instanceof ServerPlayer p) || p.tickCount % 10 != 0) return;
        Loadouts.Loadout l = Loadouts.compute(p);
        Integer prev = LAST.put(p.getUUID(), l.signature());
        if (prev == null || prev != l.signature()) MWNetwork.toTrackers(p, new EquipmentPacket(p.getId(), l), false);
    }

    @SubscribeEvent
    public static void onStartTracking(PlayerEvent.StartTracking e) {
        if (e.getTarget() instanceof ServerPlayer target && e.getEntity() instanceof ServerPlayer viewer) {
            MWNetwork.toPlayer(viewer, new EquipmentPacket(target.getId(), Loadouts.compute(target)));
        }
    }

    @SubscribeEvent
    public static void onLogout(PlayerEvent.PlayerLoggedOutEvent e) {
        LAST.remove(e.getEntity().getUUID());
    }
}

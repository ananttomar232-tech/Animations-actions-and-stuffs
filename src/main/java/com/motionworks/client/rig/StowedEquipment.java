package com.motionworks.client.rig;

import com.motionworks.common.Loadouts;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.player.Player;

/** Which items a player carries stowed. Local player: computed; others: synced from the server. */
public final class StowedEquipment {

    private static final Int2ObjectMap<Loadouts.Loadout> REMOTE = new Int2ObjectOpenHashMap<>();

    private StowedEquipment() {}

    public static void setRemote(int entityId, Loadouts.Loadout l) {
        REMOTE.put(entityId, l);
    }

    public static Loadouts.Loadout of(Player p) {
        if (p == Minecraft.getInstance().player) return Loadouts.compute(p);
        return REMOTE.get(p.getId());
    }

}

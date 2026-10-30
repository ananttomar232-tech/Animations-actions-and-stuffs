package com.motionworks.common;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** Stowed-equipment rules shared by client and server so both agree on what is worn where. */
public final class Loadouts {
    public record Loadout(ItemStack back, boolean backIsBlade, ItemStack hip, boolean shield, boolean quiver) {
        public void write(FriendlyByteBuf buf) {
            buf.writeItem(back);
            buf.writeBoolean(backIsBlade);
            buf.writeItem(hip);
            buf.writeBoolean(shield);
            buf.writeBoolean(quiver);
        }

        public static Loadout read(FriendlyByteBuf buf) {
            return new Loadout(buf.readItem(), buf.readBoolean(), buf.readItem(), buf.readBoolean(), buf.readBoolean());
        }

        public int signature() {
            return java.util.Objects.hash(back.getItem(), backIsBlade, hip.getItem(), shield, quiver);
        }
    }

    private Loadouts() {}

    public static Loadout compute(Player p) {
        Inventory inv = p.getInventory();
        ItemStack held = p.getMainHandItem();
        ItemStack off = p.getOffhandItem();
        ItemStack bestBack = ItemStack.EMPTY;
        int bestScore = 0;
        ItemStack hip = ItemStack.EMPTY;
        boolean shield = false, bow = false, arrows = false;
        for (int i = 0; i < Inventory.getSelectionSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.isEmpty() || s == held) continue;
            String c = ItemCategories.of(s);
            int score = switch (c) {
                case "sword" -> 5;
                case "axe" -> 4;
                case "trident" -> 4;
                case "bow", "crossbow" -> 3;
                default -> 0;
            };
            if (score > bestScore) {
                bestScore = score;
                bestBack = s;
            }
            if ("pickaxe".equals(c) || "shovel".equals(c)) if (hip.isEmpty()) hip = s;
            if ("shield".equals(c) && off.getItem() != Items.SHIELD) shield = true;
            if ("bow".equals(c) || "crossbow".equals(c) || "bow".equals(ItemCategories.of(held)) || "crossbow".equals(ItemCategories.of(held))) bow = true;
        }
        for (ItemStack s : inv.items) if (s.is(Items.ARROW) || s.is(Items.SPECTRAL_ARROW) || s.is(Items.TIPPED_ARROW)) arrows = true;
        String backCat = ItemCategories.of(bestBack);
        return new Loadout(bestBack.copy(), "sword".equals(backCat), hip.copy(), shield, bow && arrows);
    }
}
